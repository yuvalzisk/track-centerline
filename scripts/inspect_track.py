import csv
import math
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "BrandsHatchLayout.csv"

points = {"left": [], "right": []}
invalid_rows = []
total = 0

with DATA_FILE.open(newline="", encoding="utf-8-sig") as file:
    reader = csv.DictReader(file)

    for line_number, row in enumerate(reader, start=2):
        total += 1
        side = (row.get("side") or "").strip().lower()

        try:
            x = float(row["x"])
            y = float(row["y"])
        except (ValueError, TypeError):
            invalid_rows.append(line_number)
            continue

        if side not in points or not (math.isfinite(x) and math.isfinite(y)):
            invalid_rows.append(line_number)
            continue

        points[side].append((x, y))

print(f"Data rows: {total}")
print(f"Left points: {len(points['left'])}")
print(f"Right points: {len(points['right'])}")
print(f"Skipped rows: {invalid_rows}")

fig, ax = plt.subplots(figsize=(10, 8))

for side, color in [("left", "royalblue"), ("right", "darkorange")]:
    if points[side]:
        xs, ys = zip(*points[side])
        ax.scatter(xs, ys, s=12, color=color, label=side)

ax.set_aspect("equal", adjustable="box")
ax.set_xlabel("X (dataset units)")
ax.set_ylabel("Y (dataset units)")
ax.set_title("Track boundary points")
ax.legend()
ax.grid(True, alpha=0.3)

output_file = ROOT / "output" / "track_points.png"
output_file.parent.mkdir(exist_ok=True)
fig.savefig(output_file, dpi=160, bbox_inches="tight")
plt.close(fig)

print(f"Plot saved to: {output_file}")
