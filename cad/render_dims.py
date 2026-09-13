"""Dimensioned reference diagram: top view + cross-section."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

OUTER_R = 130.0
WALL_THICK = 7.0
FLOOR_THICK = 4.0
WALL_HEIGHT = 28.0
WALL_ARC_DEG = 250.0
MOUTH_DEG = 360 - WALL_ARC_DEG
INNER_R = OUTER_R - WALL_THICK
DRAIN_R = 5.0
DRAIN_RADIAL_POS = OUTER_R - WALL_THICK - 15.0

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 6.5))

# ---------------- Top view ----------------
theta_wall = np.linspace(np.radians(MOUTH_DEG / 2), np.radians(360 - MOUTH_DEG / 2), 200)
outer_x, outer_y = OUTER_R * np.cos(theta_wall), OUTER_R * np.sin(theta_wall)
inner_x, inner_y = INNER_R * np.cos(theta_wall), INNER_R * np.sin(theta_wall)

full_theta = np.linspace(0, 2 * np.pi, 200)
ax1.plot(OUTER_R * np.cos(full_theta), OUTER_R * np.sin(full_theta), color="0.6", lw=1, ls="--")
ax1.plot(outer_x, outer_y, color="k", lw=2)
ax1.plot(inner_x, inner_y, color="k", lw=1.2)
# mouth end caps
ax1.plot([inner_x[0], outer_x[0]], [inner_y[0], outer_y[0]], color="k", lw=2)
ax1.plot([inner_x[-1], outer_x[-1]], [inner_y[-1], outer_y[-1]], color="k", lw=2)

# drain holes
back_angle = 180
spread = 40
for i in range(3):
    ang = np.radians(back_angle - spread / 2 + spread * i / 2)
    hx, hy = DRAIN_RADIAL_POS * np.cos(ang), DRAIN_RADIAL_POS * np.sin(ang)
    ax1.add_patch(patches.Circle((hx, hy), DRAIN_R, fill=False, color="tab:blue"))

# mouth arrow / label
ax1.annotate("open mouth\n(Goku walks up, no wall)", xy=(OUTER_R * 0.9, 0), xytext=(OUTER_R * 1.25, 60),
             arrowprops=dict(arrowstyle="->"), ha="center", fontsize=9)
ax1.annotate(f"{MOUTH_DEG:.0f}° opening", xy=(OUTER_R * 0.5, 0), fontsize=9, ha="center")
ax1.annotate("drain / rinse holes", xy=(-DRAIN_RADIAL_POS, 20), xytext=(-OUTER_R * 1.5, 90),
             arrowprops=dict(arrowstyle="->"), fontsize=9)

ax1.set_xlim(-OUTER_R * 1.6, OUTER_R * 1.6)
ax1.set_ylim(-OUTER_R * 1.3, OUTER_R * 1.3)
ax1.set_aspect("equal")
ax1.set_title(f"Top view — {OUTER_R*2:.0f}mm diameter")
ax1.axis("off")

# diameter dimension line
ax1.annotate("", xy=(-OUTER_R, -OUTER_R * 1.15), xytext=(OUTER_R, -OUTER_R * 1.15),
             arrowprops=dict(arrowstyle="<->"))
ax1.text(0, -OUTER_R * 1.25, f"{OUTER_R*2:.0f} mm", ha="center", fontsize=10)

# ---------------- Cross-section (through the back wall) ----------------
TOTAL_H = FLOOR_THICK + WALL_HEIGHT
xs_floor = [-OUTER_R, OUTER_R, OUTER_R, -OUTER_R]
ys_floor = [0, 0, FLOOR_THICK, FLOOR_THICK]
ax2.fill(xs_floor, ys_floor, color="0.85", edgecolor="k", lw=1.5)

# back wall segment (both sides visible in a diametral cross-section since arc >180°)
wall_x = [-OUTER_R, -INNER_R, -INNER_R, -OUTER_R]
wall_y = [FLOOR_THICK, FLOOR_THICK, TOTAL_H, TOTAL_H]
ax2.fill(wall_x, wall_y, color="0.7", edgecolor="k", lw=1.5)
wall_x2 = [INNER_R, OUTER_R, OUTER_R, INNER_R]
ax2.fill(wall_x2, wall_y, color="0.7", edgecolor="k", lw=1.5)

ax2.set_xlim(-OUTER_R * 1.3, OUTER_R * 1.3)
ax2.set_ylim(-10, TOTAL_H + 40)
ax2.set_aspect("equal")
ax2.axis("off")
ax2.set_title("Cross-section (through back wall)")

# height dim
ax2.annotate("", xy=(OUTER_R * 1.12, 0), xytext=(OUTER_R * 1.12, TOTAL_H), arrowprops=dict(arrowstyle="<->"))
ax2.text(OUTER_R * 1.18, TOTAL_H / 2, f"{TOTAL_H:.0f} mm total\n({WALL_HEIGHT:.0f}mm wall\n+ {FLOOR_THICK:.0f}mm floor)",
         va="center", fontsize=8)

# wall thickness dim
ax2.annotate("", xy=(INNER_R, TOTAL_H + 8), xytext=(OUTER_R, TOTAL_H + 8), arrowprops=dict(arrowstyle="<->"))
ax2.text((INNER_R + OUTER_R) / 2, TOTAL_H + 14, f"{WALL_THICK:.0f}mm", ha="center", fontsize=8)

ax2.text(0, FLOOR_THICK / 2, "no wall here\n(this is the open mouth,\nseen face-on)", ha="center", va="center", fontsize=8, style="italic")

fig.suptitle("Goku's Feeding Platform — reference dimensions", fontsize=13)
fig.tight_layout()
fig.savefig("/Users/josetorres/Code/Goku-Feeder/output/dimensions.png", dpi=160)
print("wrote dimensions.png")
