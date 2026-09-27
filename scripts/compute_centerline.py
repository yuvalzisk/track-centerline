import csv
import math
import runpy
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent

# Reuse our existing data loading for this first prototype.
data = runpy.run_path(str(ROOT / "scripts" / "inspect_track.py"))
left = data["points"]["left"]
right = data["points"]["right"]

if len(left) != len(right) or len(left) < 3:
    raise ValueError("Need equal point counts and at least 3 pairs.")

centerline = []
pair_distances = []

for l_point, r_point in zip(left, right):
    middle_x = (l_point[0] + r_point[0]) / 2
    middle_y = (l_point[1] + r_point[1]) / 2

    centerline.append((middle_x, middle_y))
    pair_distances.append(math.dist(l_point, r_point))

output_dir = ROOT / "output"
output_dir.mkdir(exist_ok=True)

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
    closed = pts + [pts[0]]
    xs, ys = zip(*closed)
    ax.plot(xs, ys, color=color, label=label, linewidth=1.5)

# Show the assumed pairing across the road.
for l_point, r_point in zip(left, right):
    ax.plot(
        [l_point[0], r_point[0]],
        [l_point[1], r_point[1]],
        color="gray",
        linewidth=0.6,
        alpha=0.5,
    )

ax.set_aspect("equal", adjustable="box")
ax.set_xlabel("X (dataset units)")
ax.set_ylabel("Y (dataset units)")
ax.set_title("Centerline with point-pair connections")
ax.legend()
ax.grid(True, alpha=0.3)

fig.savefig(output_dir / "centerline.png", dpi=160, bbox_inches="tight")
plt.close(fig)

print(f"\nCenterline points: {len(centerline)}")
print(f"Pair distance min: {min(pair_distances):.2f}")
print(f"Pair distance mean: {sum(pair_distances) / len(pair_distances):.2f}")
print(f"Pair distance max: {max(pair_distances):.2f}")
print("Saved: output/centerline.csv and output/centerline.png")
