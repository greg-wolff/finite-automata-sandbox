"""Render sanity-check images of the exported parts: python preview.py"""
import os
import numpy as np
import trimesh
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

import sys
SIZE = sys.argv[1] if len(sys.argv) > 1 else "puck"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", SIZE)
parts = {n: trimesh.load(os.path.join(OUT, n + ".stl")) for n in ("top", "bottom", "deck")}
colors = {"top": "#e9e6df", "bottom": "#cfcac0", "deck": "#e07a3f"}
for n, m in parts.items():
    print(n, "watertight", m.is_watertight, "faces", len(m.faces))


def shaded(ax, mesh, color, light=(0.4, -0.5, 0.8)):
    l = np.array(light) / np.linalg.norm(light)
    shade = 0.45 + 0.55 * np.clip(mesh.face_normals @ l, 0, 1)
    rgb = np.array(matplotlib.colors.to_rgb(color))
    pc = Poly3DCollection(mesh.triangles, facecolors=shade[:, None] * rgb[None, :], edgecolors="none")
    ax.add_collection3d(pc)


def view(ax, elev, azim, lim=50):
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_zlim(-lim, lim)
    ax.set_box_aspect((1, 1, 1)); ax.view_init(elev, azim); ax.set_axis_off()


fig = plt.figure(figsize=(16, 8))
ax = fig.add_subplot(241, projection="3d")
for n in ("bottom", "top"):
    shaded(ax, parts[n], colors[n])
view(ax, 28, -35); ax.set_title("assembled, camera side")
ax = fig.add_subplot(242, projection="3d")
for n in ("bottom", "top"):
    shaded(ax, parts[n], colors[n])
view(ax, 28, 140); ax.set_title("assembled, speaker side")
ax = fig.add_subplot(243, projection="3d")
for n, dz in (("bottom", -22), ("deck", 0), ("top", 26)):
    m = parts[n].copy(); m.apply_translation((0, 0, dz)); shaded(ax, m, colors[n])
view(ax, 22, -50, 55); ax.set_title("exploded")
ax = fig.add_subplot(244, projection="3d")
shaded(ax, parts["deck"], colors["deck"]); view(ax, 55, -60, 48); ax.set_title("deck")
ax = fig.add_subplot(245, projection="3d")
m = parts["top"].copy(); m.apply_transform(trimesh.transformations.rotation_matrix(np.pi, (1, 0, 0)))
shaded(ax, m, colors["top"]); view(ax, 50, -60, 48); ax.set_title("top shell, inside")
ax = fig.add_subplot(246, projection="3d")
shaded(ax, parts["bottom"], colors["bottom"]); view(ax, 50, -60, 48); ax.set_title("bottom shell, inside")


def section(ax, origin, normal, u, v, title):
    for n, m in parts.items():
        s = m.section(plane_origin=origin, plane_normal=normal)
        if s is None:
            continue
        for seg in s.discrete:
            ax.plot(seg @ np.array(u), seg @ np.array(v), color=colors[n] if n == "deck" else "#333", lw=1.2)
    ax.set_aspect("equal"); ax.set_title(title); ax.grid(alpha=0.3)


ax = fig.add_subplot(247)
section(ax, (0, 0.01, 0), (0, 1, 0), (1, 0, 0), (0, 0, 1), "section through camera (right) and speaker (left)")
a = np.radians(60.0)
ax = fig.add_subplot(248)
section(ax, (0, 0, 0), (-np.sin(a), np.cos(a), 0), (np.cos(a), np.sin(a), 0), (0, 0, 1), "section at 60 deg (USB plug zone)")
pass
fig.tight_layout()
fig.savefig(os.path.join(OUT, "preview.png"), dpi=110)
