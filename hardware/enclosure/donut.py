"""Parametric donut enclosure for the party-game device (v0 prototype shell).

Three printed parts, all support-free:
  top     upper half-torus  - print seam face down
  bottom  lower half-torus  - print seam face down (flat foot ends up on top)
  deck    C-shaped plate that keys the halves together and carries speaker + amp

Layout (seam is z = 0, camera faces +X, angles run counter-clockwise seen from above):
  0 deg         camera eye, looking CAM_ELEV degrees up. The XIAO ESP32S3 Sense is
                foam-taped to a tilted shelf behind it, camera still seated on the board.
  20..85 deg    the USB-C plug lies inside the tube (the board's port faces along the ring)
  125 deg       cable exit slot - the device has a captive power cable, like a smart speaker
  180 deg       speaker under a grille, firing up

Run:  python donut.py [--size puck|party]     writes out/<size>/*.stl and *.step
Units are millimetres.
"""
import argparse
import math
import os
from build123d import (Align, Axis, Box, Circle, Cone, Cylinder, Location, Plane, Polygon, Pos,
                       Rot, Torus, export_step, export_stl, extrude, revolve)

SIZES = {
    # R = centre-line radius, r = tube radius, SPK = speaker (diameter, depth)
    "puck": dict(R=31.0, r=17.0, SPK_D=28.0),    # 96 x 33 mm, 28 mm speaker
    "party": dict(R=36.0, r=24.0, SPK_D=40.0),   # 120 x 47 mm, 40 mm x 20 mm speaker
}
ap = argparse.ArgumentParser()
ap.add_argument("--size", choices=SIZES, default="puck")
args = ap.parse_args()
R, r, SPK_D = (SIZES[args.size][k] for k in ("R", "r", "SPK_D"))

WALL = 2.4
FOOT = 1.2          # slice taken off the underside to make a flat foot
DECK_T = 3.0        # deck thickness, half sits in each shell
RABBET = 1.2        # radial depth of the step the deck sits in
FIT = 0.15          # clearance per side between printed parts

BOSS_ANGLES = (100, 222, 325)
BOSS_D = 7.0
SCREW_CLEAR = 3.4   # M3 clearance
SCREW_PILOT = 2.7   # M3 threading straight into plastic (use 4.0 for heat-set inserts)
HEAD_D, HEAD_H = 6.2, 3.2      # counterbore for M3 socket-head screws

CAM_ELEV = 30.0     # camera looks this many degrees above horizontal
CAM_BORE = 9.0      # hole in front of the lens, flared outward
CAM_BODY = 9.5      # square relief the camera module nests in
STACK_H = 15.0      # XIAO ESP32S3 Sense: back of main PCB to top of camera
BOARD_L, BOARD_W = 21.0, 17.8  # long axis lies along the ring, USB-C towards +angle
MIC_D, MIC_OFFSET = 1.5, 8.0   # two sound holes either side of the lens

DECK_GAP = (-24.0, 92.0)       # deck is cut away where the board and USB plug sit
CABLE_ANGLE, CABLE_D = 125.0, 4.2
SPK_ANGLE = 180.0
GRILLE_HOLE, GRILLE_PITCH = 1.8, 3.4

rc = r - WALL                  # cavity radius
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", args.size)
MIN = (Align.CENTER, Align.CENTER, Align.MIN)


def ring(profile):
    """Revolve a tube-section sketch (x = radial offset from R, y = z) round Z."""
    return revolve(Plane.XZ * Pos(R, 0) * profile, Axis.Z)


def polar(angle, radius=None, z=0.0):
    a = math.radians(angle)
    radius = R if radius is None else radius
    return Pos(radius * math.cos(a), radius * math.sin(a), z)


def cavity(sign):
    """Cavity section for one half. The roof is a 45 degree arch with a short flat
    bridge, so each half prints seam-down with no supports."""
    k = rc * math.sqrt(2)
    top = rc if sign > 0 else r - FOOT - WALL
    house = Polygon((-rc, 0), (rc, 0), (rc, k - rc), (k - top, top),
                    (-(k - top), top), (-rc, k - rc), align=None)
    h = DECK_T / 2 + FIT
    step = Polygon((-rc - RABBET, 0), (rc + RABBET, 0), (rc + RABBET, h),
                   (rc, h + RABBET), (-rc, h + RABBET), (-rc - RABBET, h), align=None)
    sec = (Circle(rc) & house) + step
    if sign < 0:
        sec = sec.mirror(Plane.XZ)
    return ring(sec)


def half_space(sign, size=300):
    return Pos(0, 0, sign * size / 2) * Box(size, size, size)


def tube_frame():
    """Frame at the tube centre under the camera: local Z = lens axis (outward, up),
    local Y = along the ring, local X = down and outward."""
    return Location((R, 0, 0), (0, 90 - CAM_ELEV, 0))


def make_top():
    outer = Torus(R, r) & half_space(+1)
    body = outer - cavity(+1)
    for a in BOSS_ANGLES:
        body += (polar(a, z=DECK_T / 2 + FIT) * Cylinder(BOSS_D / 2, r, align=MIN)) & outer
    f = tube_frame()
    # tilted shelf the dev board is taped to (leans 30 degrees, prints without support)
    back = rc + 0.5 - STACK_H
    shelf = f * Pos(-r, 0, back - 2.0) * Box(2 * r + BOARD_W / 2 + 2, BOARD_L + 3, 2.0, align=(Align.MIN, Align.CENTER, Align.MIN))
    body += shelf & outer
    # camera eye: nest for the module, bore, outward flare
    body -= f * Pos(0, 0, rc - 1) * Box(CAM_BODY, CAM_BODY, 1.8, align=MIN)
    body -= f * Pos(0, 0, rc - 1) * Cylinder(CAM_BORE / 2, WALL + 3, align=MIN)
    body -= f * Pos(0, 0, rc + 0.8) * Cone(CAM_BORE / 2, CAM_BORE / 2 + 2.4, 2.4, align=MIN)
    for s in (-1, 1):
        body -= f * Pos(0, s * MIC_OFFSET, rc - 1) * Cylinder(MIC_D / 2, WALL + 3, align=MIN)
    for a in BOSS_ANGLES:
        body -= polar(a) * Cylinder(SCREW_PILOT / 2, min(11, r - 5), align=MIN)
    # speaker grille: hex grid of vertical holes
    gr = SPK_D / 2 - 2.5
    n = int(gr / GRILLE_PITCH) + 2
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            x = GRILLE_PITCH * (i + j / 2)
            y = GRILLE_PITCH * j * math.sqrt(3) / 2
            if math.hypot(x, y) <= gr:
                body -= Rot(0, 0, SPK_ANGLE) * Pos(R + x, y, 0) * Cylinder(GRILLE_HOLE / 2, 3 * r)
    # light window: thin the wall facing the centre hole so an LED strip glows through
    k = r - 0.8
    win = (Circle(k) - Circle(rc)) & Polygon((-k - 1, 3.5), (-0.6 * rc, 3.5), (-0.6 * rc, 8), (-k - 1, k), align=None)
    body -= ring(win)
    # cable exit: U-slot open to the seam, closed underneath by the deck rim
    h = DECK_T / 2 + CABLE_D + 0.3
    body -= Rot(0, 0, CABLE_ANGLE) * Pos(R + r - 5, 0, 0) * Box(10, CABLE_D + 0.4, h, align=MIN)
    return body


def make_bottom():
    outer = (Torus(R, r) & half_space(-1)) - Pos(0, 0, -r - 50 + FOOT) * Box(300, 300, 100)
    body = outer - cavity(-1)
    for a in BOSS_ANGLES:
        body += (polar(a, z=-r) * Cylinder(BOSS_D / 2, r - DECK_T / 2 - FIT, align=MIN)) & outer
        body -= polar(a, z=-r) * Cylinder(SCREW_CLEAR / 2, r, align=MIN)
        body -= polar(a, z=-r + FOOT) * Cylinder(HEAD_D / 2, HEAD_H, align=MIN)
    return body


def make_deck():
    ri, ro = R - rc - RABBET + FIT, R + rc + RABBET - FIT
    deck = extrude(Circle(ro) - Circle(ri), DECK_T / 2, both=True)
    # open the front sector for the board and the USB plug
    a0, a1 = (math.radians(a) for a in DECK_GAP)
    n = 12
    pts = [(0, 0)] + [(2 * ro * math.cos(a0 + (a1 - a0) * i / n), 2 * ro * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]
    deck -= extrude(Polygon(*pts, align=None), DECK_T, both=True)
    for a in BOSS_ANGLES:
        deck -= polar(a) * Cylinder(SCREW_CLEAR / 2, 10)
    # speaker: rim rests in a shallow recess, basket and magnet hang through
    deck -= polar(SPK_ANGLE, z=DECK_T / 2 - 1.2) * Cylinder(SPK_D / 2 + 0.2, 5, align=MIN)
    deck -= polar(SPK_ANGLE) * Cylinder(SPK_D / 2 - 2.0, 10)
    # wire pass-throughs and zip-tie slots for cable strain relief
    for a in (145, 215, 270):
        deck -= polar(a, R - rc + 5) * Rot(0, 0, a) * Box(4, 8, 10)
    for da in (-7, 7):
        deck -= polar(CABLE_ANGLE + da, R + rc - 5) * Rot(0, 0, CABLE_ANGLE + da) * Box(4.5, 2.0, 10)
    return deck


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, part in {"top": make_top(), "bottom": make_bottom(), "deck": make_deck()}.items():
        export_stl(part, os.path.join(OUT, f"{name}.stl"), tolerance=0.04, angular_tolerance=0.15)
        export_step(part, os.path.join(OUT, f"{name}.step"))
        bb = part.bounding_box()
        print(f"{args.size} {name:7s} {part.volume/1000:6.1f} cm3  bbox "
              f"{bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f}  solids {len(part.solids())}")
