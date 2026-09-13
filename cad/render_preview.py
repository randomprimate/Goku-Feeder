"""Quick preview renders of goku_feeder.stl (top view + isometric) using matplotlib."""
import struct
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

STL_PATH = "/Users/josetorres/Code/Goku-Feeder/output/goku_feeder.stl"
OUT_TOP = "/Users/josetorres/Code/Goku-Feeder/output/preview_top.png"
OUT_ISO = "/Users/josetorres/Code/Goku-Feeder/output/preview_iso.png"


def read_binary_stl(path):
    with open(path, "rb") as f:
        header = f.read(80)
        count = struct.unpack("<I", f.read(4))[0]
        tris = np.zeros((count, 3, 3), dtype=np.float32)
        for i in range(count):
            f.read(12)  # normal
            for j in range(3):
                tris[i, j] = struct.unpack("<3f", f.read(12))
            f.read(2)  # attribute byte count
    return tris


tris = read_binary_stl(STL_PATH)
print("triangle count:", len(tris))

all_pts = tris.reshape(-1, 3)
mins = all_pts.min(axis=0)
maxs = all_pts.max(axis=0)
print("bbox min", mins, "max", maxs)


def make_fig(elev, azim, out_path, title):
    fig = plt.figure(figsize=(7, 7))
    ax = fig.add_subplot(111, projection="3d")
    coll = Poly3DCollection(tris, facecolor=(0.75, 0.78, 0.82, 1.0), edgecolor=(0.25, 0.25, 0.25), linewidths=0.05)
    ax.add_collection3d(coll)
    ax.set_xlim(mins[0], maxs[0])
    ax.set_ylim(mins[1], maxs[1])
    ax.set_zlim(mins[2], maxs[2] * 3)
    ax.set_box_aspect((maxs[0] - mins[0], maxs[1] - mins[1], (maxs[2] - mins[2]) * 3))
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


make_fig(90, -90, OUT_TOP, "Top view")
make_fig(28, -60, OUT_ISO, "Isometric view")
print("wrote", OUT_TOP, OUT_ISO)
