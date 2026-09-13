"""
Goku's Feeding Platform - parametric model (FreeCAD 1.0, Part workbench)

Concept: a low "horseshoe" corral sitting on top of the substrate.
- A solid floor disc keeps the 250g of chopped endive off the coco-coir/mulch.
- An arced wall (not a full ring) contains greens that Goku pushes around,
  but leaves a wide open "mouth" so he can walk right up and reach in with
  no wall or ramp to climb - a sulcata this size (~19cm carapace) shouldn't
  have to step over anything to start eating.
- Floor sits only FLOOR_THICK above ground, so even outside the mouth the
  step is trivial.
- Fillets round every edge so nothing catches on soft neck/leg skin or a
  printed seam.

Run with:
  /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd feeder.py
"""

import os
import math
import FreeCAD as App
import Part
from FreeCAD import Base

# ---------------------------------------------------------------------------
# Parameters (all in mm) - tune these and re-run to rescale as Goku grows
# ---------------------------------------------------------------------------
OUTER_R = 130.0          # outer radius of the whole platform -> 260mm diameter
WALL_THICK = 7.0         # radial thickness of the corral wall
FLOOR_THICK = 4.0        # thickness of the base disc
WALL_HEIGHT = 28.0       # height of the corral wall above the floor
WALL_ARC_DEG = 250.0     # how much of the circle the wall covers
                         # (remaining 360-250=110 deg is the open "mouth")
FILLET_RADIUS = 2.0      # edge break-safety radius on the finished part
FLOOR_EDGE_CHAMFER = 1.0 # small chamfer on the outer bottom edge (print-friendly foot)

DRAIN_HOLE_R = 5.0
DRAIN_HOLE_COUNT = 3
DRAIN_HOLE_RADIAL_POS = OUTER_R - WALL_THICK - 15.0  # inboard of the wall, near the back

INNER_R = OUTER_R - WALL_THICK
TOTAL_HEIGHT = FLOOR_THICK + WALL_HEIGHT

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output")
os.makedirs(OUT_DIR, exist_ok=True)

doc = App.newDocument("GokuFeeder")

# ---------------------------------------------------------------------------
# 1. Floor disc
# ---------------------------------------------------------------------------
floor = Part.makeCylinder(OUTER_R, FLOOR_THICK, Base.Vector(0, 0, 0), Base.Vector(0, 0, 1))

# ---------------------------------------------------------------------------
# 2. Corral wall: full ring, then cut away the "mouth" sector
# ---------------------------------------------------------------------------
outer_wall = Part.makeCylinder(OUTER_R, WALL_HEIGHT, Base.Vector(0, 0, FLOOR_THICK), Base.Vector(0, 0, 1))
inner_cut = Part.makeCylinder(INNER_R, WALL_HEIGHT + 4.0, Base.Vector(0, 0, FLOOR_THICK - 2.0), Base.Vector(0, 0, 1))
ring = outer_wall.cut(inner_cut)

mouth_deg = 360.0 - WALL_ARC_DEG
mouth_sector = Part.makeCylinder(
    OUTER_R + 20.0, WALL_HEIGHT + 20.0,
    Base.Vector(0, 0, FLOOR_THICK - 10.0), Base.Vector(0, 0, 1),
    mouth_deg,
)
# Center the mouth on the +X axis (angle 0), matching where Goku approaches from
mouth_sector.rotate(Base.Vector(0, 0, 0), Base.Vector(0, 0, 1), -mouth_deg / 2.0)

horseshoe_wall = ring.cut(mouth_sector)

# ---------------------------------------------------------------------------
# 3. Fuse floor + wall
# ---------------------------------------------------------------------------
platform = floor.fuse(horseshoe_wall)
platform = platform.removeSplitter()

# ---------------------------------------------------------------------------
# 4. Drainage / rinse-out holes through the floor, tucked near the back wall
# ---------------------------------------------------------------------------
back_angle_deg = 180.0  # opposite the mouth
spread_deg = 40.0
for i in range(DRAIN_HOLE_COUNT):
    if DRAIN_HOLE_COUNT == 1:
        ang = back_angle_deg
    else:
        ang = back_angle_deg - spread_deg / 2.0 + spread_deg * i / (DRAIN_HOLE_COUNT - 1)
    rad = math.radians(ang)
    x = DRAIN_HOLE_RADIAL_POS * math.cos(rad)
    y = DRAIN_HOLE_RADIAL_POS * math.sin(rad)
    hole = Part.makeCylinder(DRAIN_HOLE_R, FLOOR_THICK + 4.0, Base.Vector(x, y, -2.0), Base.Vector(0, 0, 1))
    platform = platform.cut(hole)

platform = platform.removeSplitter()

# ---------------------------------------------------------------------------
# 5. Chamfer the outer bottom edge (print-friendly + a defined contact foot)
# ---------------------------------------------------------------------------
try:
    bottom_outer_edges = []
    for e in platform.Edges:
        bb = e.BoundBox
        if bb.ZMin < 0.05 and bb.ZMax < 0.05:
            # roughly circular edge at z=0 with radius close to OUTER_R
            mid = e.CenterOfMass
            r = math.hypot(mid.x, mid.y)
            if r > OUTER_R - 1.0:
                bottom_outer_edges.append(e)
    if bottom_outer_edges:
        platform = platform.makeChamfer(FLOOR_EDGE_CHAMFER, bottom_outer_edges)
except Exception as exc:
    print("Chamfer skipped:", exc)

# ---------------------------------------------------------------------------
# 6. Break every remaining sharp edge with a small fillet (safety + comfort)
# ---------------------------------------------------------------------------
try:
    platform_filleted = platform.makeFillet(FILLET_RADIUS, platform.Edges)
    platform = platform_filleted
except Exception as exc:
    print("Global fillet failed, trying a smaller radius:", exc)
    try:
        platform = platform.makeFillet(0.8, platform.Edges)
    except Exception as exc2:
        print("Fillet skipped entirely, exporting sharp-edged geometry:", exc2)

# ---------------------------------------------------------------------------
# 7. Export
# ---------------------------------------------------------------------------
obj = doc.addObject("Part::Feature", "GokuFeeder")
obj.Shape = platform
doc.recompute()

stl_path = os.path.join(OUT_DIR, "goku_feeder.stl")
step_path = os.path.join(OUT_DIR, "goku_feeder.step")

# Explicit, print-appropriate tessellation (0.1mm) instead of the default
# ultra-fine deflection, which otherwise blows up to a 100MB+ STL because of
# all the small fillet surfaces.
import Mesh
verts, facets = platform.tessellate(0.1)
triangles = [[verts[i0], verts[i1], verts[i2]] for (i0, i1, i2) in facets]
mesh = Mesh.Mesh(triangles)
mesh.write(stl_path)

Part.export([obj], step_path)

print("Exported:")
print(" ", stl_path)
print(" ", step_path)
print("Bounding box:", platform.BoundBox)
print(f"Outer diameter: {OUTER_R*2:.1f} mm, total height: {TOTAL_HEIGHT:.1f} mm")
