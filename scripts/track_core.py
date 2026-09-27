import csv
import math
from pathlib import Path


def load_track(csv_path):
    points = {"left": [], "right": []}
    skipped = []

    with Path(csv_path).open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames != ["x", "y", "side"]:
            raise ValueError("Expected CSV columns: x,y,side")

        for line_number, row in enumerate(reader, start=2):
            side = (row.get("side") or "").strip().lower()

            try:
                x = float(row["x"])
                y = float(row["y"])
            except (ValueError, TypeError):
                skipped.append(line_number)
                continue

            if side not in points or not (
                math.isfinite(x) and math.isfinite(y)
            ):
                skipped.append(line_number)
                continue

            points[side].append((x, y))

    return points["left"], points["right"], skipped


def compute_centerline(left, right):
    # Assumes both boundaries are ordered and paired by index.
    if len(left) != len(right) or len(left) < 3:
        raise ValueError("Need equal point counts and at least 3 pairs.")

    centerline = []

    for (lx, ly), (rx, ry) in zip(left, right):
        centerline.append(((lx + rx) / 2, (ly + ry) / 2))

    return centerline


def save_results(left, right, centerline, output_dir):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with (output_dir / "centerline.csv").open("w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["x", "y"])
        writer.writerows(centerline)

    fig, ax = plt.subplots(figsize=(10, 8))

    for label, pts, color in [
        ("Left boundary", left, "royalblue"),
        ("Right boundary", right, "darkorange"),
        ("Estimated centerline", centerline, "green"),
    ]:
        closed = list(pts) + [pts[0]]
        xs, ys = zip(*closed)
        ax.plot(xs, ys, color=color, label=label, linewidth=1.5)

    for (lx, ly), (rx, ry) in zip(left, right):
        ax.plot(
            [lx, rx], [ly, ry],
            color="gray", linewidth=0.6, alpha=0.5,
        )

    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("X (dataset units)")
    ax.set_ylabel("Y (dataset units)")
    ax.set_title("Centerline with point-pair connections")
    ax.legend()
    ax.grid(True, alpha=0.3)

    fig.savefig(
        output_dir / "centerline.png",
        dpi=160,
        bbox_inches="tight",
    )
    plt.close(fig)
