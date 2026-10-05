"""Generate the Assignment-2 (Coulomb's law + electric field) SVG diagrams.

Run: python3 assignment2_figures.py
Force arrows are computed from Coulomb's law (k = 1 units), so their
directions always match the worked answers.
"""
import os
from math import hypot, sqrt

import quiz4_figures as q4
from quiz4_figures import Canvas, vector_diagram, lbl_at, VEC, NET, TXT, MUTED, PT

OUT = "assignment2-figures"
q4.OUT = OUT
GOLD = "#f59e0b"


def force_diagram(name, charges, target, box, *, arrow_px=90, notes=(), title="", net_label="F_net",
                  net_lpos=None, dist=(), outline=(), axes=False, width=500, show_net=True):
    """Coulomb forces on `target` from every charge in `charges`.

    charges/target: dict(q, pos, label, away, flabel, off). `off` shifts an arrow sideways (px)
    so collinear forces stay visible. dist: [(p1, p2, text, dx, dy)].
    """
    c = Canvas(box, width, pad=(40, 40, 46 if title else 24, 30 + 18 * len(notes)))
    if axes:
        c.axes()
    for pts in outline:
        c.add('<polyline points="' + " ".join(f"{c.X(x):.1f},{c.Y(y):.1f}" for x, y in pts) +
              f'" fill="none" stroke="{MUTED}" stroke-width="1.5"/>')
    tx, ty = target["pos"]
    for ch in charges:
        c.line(c.X(ch["pos"][0]), c.Y(ch["pos"][1]), c.X(tx), c.Y(ty), "#4b5563", 1.2, "5,4")
    for (x1, y1), (x2, y2), t, dx, dy in dist:
        c.text((c.X(x1) + c.X(x2)) / 2 + dx, (c.Y(y1) + c.Y(y2)) / 2 + dy, t, GOLD, 12, "middle", "bold")
    forces = []
    for ch in charges:
        dx, dy = tx - ch["pos"][0], ty - ch["pos"][1]
        r = hypot(dx, dy)
        s = target["q"] * ch["q"] / r ** 3
        forces.append((s * dx, s * dy, ch.get("flabel", ""), ch.get("off", 0)))
    sc = arrow_px / max(hypot(f[0], f[1]) for f in forces)
    net = (sum(f[0] for f in forces), sum(f[1] for f in forces))
    if hypot(*net) * sc > arrow_px * 1.9:
        sc = arrow_px * 1.9 / hypot(*net)
    Px, Py = c.X(tx), c.Y(ty)
    for fx, fy, lab, off in forces:
        m = hypot(fx, fy)
        ux, uy = fx / m, -fy / m
        ox, oy = -uy * off, ux * off
        ex, ey = Px + ox + ux * m * sc, Py + oy + uy * m * sc
        c.arrow(Px + ox, Py + oy, ex, ey, VEC, 3)
        if lab:
            lbl_at(c, ex, ey, ux, uy, lab, VEC)
    m = hypot(*net)
    if show_net and m > 1e-9:
        ux, uy = net[0] / m, -net[1] / m
        ex, ey = Px + ux * m * sc, Py + uy * m * sc
        c.arrow(Px, Py, ex, ey, NET, 4, 13)
        if net_lpos:
            c.text(Px + net_lpos[0], Py + net_lpos[1], net_label, NET, 13, net_lpos[2], "bold")
        else:
            lbl_at(c, ex, ey, ux, uy, net_label, NET, 13, True)
    for ch in charges + [target]:
        c.charge(ch["pos"][0], ch["pos"][1], ch["q"], ch.get("label", ""), ch.get("away", (0, 1)))
    if title:
        c.text(c.W / 2, 26, title, TXT, 14, "middle", "bold")
    for j, t in enumerate(notes):
        c.text(c.W / 2, c.H - c.pb + 22 + j * 18, t, MUTED, 12)
    q4.save(name, c.svg(title or name))


def line_forces(name, charges, target, xr, rows, title, notes=(), dist=()):
    """1-D layout: charges on a line, then one row per force arrow under the target.

    rows: [(length_px (signed, + = right), color, label)]."""
    c = Canvas((xr[0], xr[1], -0.1, 0.1), 520, pad=(30, 30, 76, 40 + 40 * len(rows) + 18 * len(notes)))
    c.line(c.X(xr[0] + 0.05 * (xr[1] - xr[0])), c.Y(0), c.X(xr[1] - 0.05 * (xr[1] - xr[0])), c.Y(0), MUTED, 1.3)
    for x1, x2, t in dist:
        c.text((c.X(x1) + c.X(x2)) / 2, c.Y(0) - 12, t, GOLD, 12, "middle", "bold")
    tx = c.X(target[0])
    c.line(tx, c.Y(0), tx, c.Y(0) + 30 + 40 * len(rows), "#4b5563", 1, "3,3")
    for j, (L, col, lab) in enumerate(rows):
        y = c.Y(0) + 52 + 40 * j
        c.arrow(tx, y, tx + L, y, col, 3.2 if j < len(rows) - 1 else 4, 11)
        c.text(tx + L / 2, y - 8, lab, col, 12.5, "middle", "bold")
    for x, q, lab in charges + [target]:
        c.charge(x, 0, q, lab, (0, 1))
    c.text(c.W / 2, 26, title, TXT, 14, "middle", "bold")
    for j, t in enumerate(notes):
        c.text(c.W / 2, c.H - 18 * len(notes) + 4 + j * 18, t, MUTED, 12)
    q4.save(name, c.svg(title))


def build():
    os.makedirs(OUT, exist_ok=True)

    # Q1 (i): null point between two like charges
    c = Canvas((-0.08, 0.58, -0.12, 0.12), 520, pad=(30, 30, 46, 48))
    c.line(c.X(0), c.Y(0), c.X(0.5), c.Y(0), MUTED, 1.4)
    xn = 2 / 7
    c.add(f'<circle cx="{c.X(xn):.1f}" cy="{c.Y(0):.1f}" r="5" fill="{PT}"/>')
    c.text(c.X(xn), c.Y(0) - 14, "null point", PT, 12.5, "middle", "bold")
    c.arrow(c.X(xn), c.Y(0) + 22, c.X(xn) + 55, c.Y(0) + 22, VEC, 2.6, 10)
    c.arrow(c.X(xn), c.Y(0) + 22, c.X(xn) - 55, c.Y(0) + 22, VEC, 2.6, 10)
    c.text(c.X(xn) + 60, c.Y(0) + 26, "from 16 nC", VEC, 11.5, "start")
    c.text(c.X(xn) - 60, c.Y(0) + 26, "from 9 nC", VEC, 11.5, "end")
    c.text((c.X(0) + c.X(xn)) / 2, c.Y(0) - 34, "x = 28.6 cm", GOLD, 12.5, "middle", "bold")
    c.text((c.X(xn) + c.X(0.5)) / 2, c.Y(0) - 34, "50 − x = 21.4 cm", GOLD, 12.5, "middle", "bold")
    c.charge(0, 0, 1, "+16 nC", (0, -1))
    c.charge(0.5, 0, 1, "+9 nC", (0, -1))
    c.text(c.W / 2, 26, "Q1 (i): where a test charge feels no force", TXT, 14, "middle", "bold")
    c.text(c.W / 2, c.H - 22, "Only between like charges do the two pushes point opposite ways.", MUTED, 12)
    q4.save("a2-q1-null", c.svg("Q1 null point"))

    # Q1 (ii): forces on +2 nC at the midpoint (lengths to scale: 4.60, 2.59, 2.01 μN)
    u = 30
    line_forces("a2-q1-mid", [(0, 16, "+16 nC"), (0.5, 9, "+9 nC")], (0.25, 2, "+2 nC"), (-0.06, 0.56),
                [(4.60 * u, VEC, "F₁₆ = 4.60 μN"),
                 (-2.59 * u, VEC, "F₉ = 2.59 μN"),
                 (2.01 * u, NET, "Net F = 2.01 μN")],
                "Q1 (ii): forces on +2 nC at the midpoint", dist=[(0, 0.25, "25 cm"), (0.25, 0.5, "25 cm")],
                notes=["Both charges repel the +2 nC: 16 nC pushes it right, 9 nC pushes it left.",
                       "The bigger 16 nC push wins → net force toward the +9 nC charge."])

    # Q2: force on B (positive) from A and C (negative)
    h = 3 * sqrt(3) / 2
    force_diagram("a2-q2", [dict(q=-1, pos=(0, 0), label="A: −10 μC", away=(-1, -0.6), flabel="F_BA"),
                            dict(q=-1, pos=(3, 0), label="C: −10 μC", away=(1, -0.6), flabel="F_BC")],
                  dict(q=1, pos=(1.5, h), label="B: +10 μC", away=(0, 1)), (-0.9, 3.9, -0.7, 3.25),
                  arrow_px=85, net_label="F = 0.173 N (−ĵ)", net_lpos=(14, 150, "start"),
                  outline=[[(0, 0), (3, 0), (1.5, h), (0, 0)]],
                  dist=[((0, 0), (3, 0), "3 m", 0, 20)], axes=False,
                  title="Q2: force direction diagram at B",
                  notes=["Unlike charges attract: B is pulled toward A and toward C.",
                         "Sideways parts cancel; the downward parts add."])

    # Q4: forces on q2 (lengths to scale: 0.674, 1.94, 1.27 μN)
    u = 70
    line_forces("a2-q4", [(0, 25, "q₁ = +25 nC"), (3, 18, "q₃ = +18 nC")], (2, -12, "q₂ = −12 nC"), (-0.5, 3.5),
                [(-0.674 * u, VEC, "F₁₂ = 0.674 μN"),
                 (1.94 * u, VEC, "F₃₂ = 1.94 μN"),
                 (1.27 * u, NET, "Net F = 1.27 μN")],
                "Q4: forces on q₂", dist=[(0, 2, "2 m"), (2, 3, "1 m")],
                notes=["q₂ is negative, so both positive charges ATTRACT it.",
                       "q₁ pulls left, q₃ pulls right — the closer q₃ wins → net force +x."])

    # Q6: arrangement + forces on +q at the centre (figure: q4 at origin, q1 top-left)
    a = 0.10
    force_diagram("a2-q6", [dict(q=2, pos=(0, a), label="q₁ = +2q", away=(-1, 1), flabel="F₁"),
                            dict(q=4, pos=(a, a), label="q₂ = +4q", away=(1, 1), flabel="F₂", off=14),
                            dict(q=2, pos=(a, 0), label="q₃ = +2q", away=(1, -1), flabel="F₃"),
                            dict(q=-2, pos=(0, 0), label="q₄ = −2q", away=(-1, -1), flabel="F₄", off=-14)],
                  dict(q=1, pos=(a / 2, a / 2), label="", away=(0, 1)), (-0.04, 0.14, -0.035, 0.135),
                  arrow_px=66, net_label="F = 9.71×10⁻⁵ N toward q₄", net_lpos=(26, 86, "start"),
                  outline=[[(0, 0), (0, a), (a, a), (a, 0), (0, 0)]],
                  dist=[((0, a), (a, a), "10 cm", 0, -12), ((0, 0), (a, 0), "a = 10 cm", 0, 22)],
                  title="Q6: arrangement and forces on +q at the centre",
                  notes=["q₁ and q₃ push equally in opposite directions → cancel.",
                         "q₂ pushes toward q₄; q₄ pulls toward itself → they add."])

    # Q7 (i) and (ii): fields at P
    vector_diagram("a2-q7a", [dict(q=-1, pos=(-4, 0), label="−q = −4 C", away=(0, -1)),
                              dict(q=1, pos=(4, 0), label="+q = +4 C", away=(0, -1))],
                   (0, 4), (-6.2, 6.2, -1.4, 6.6), plabel=(12, -10, "start"), arrow_px=75,
                   groups=[([0], "toward −q"), ([1], "away from +q")],
                   net_label="E = 1.59×10⁹ N/C (−x)", net_lpos=(-114, 4, "end"),
                   notes=["Both fields: 1.12×10⁹ N/C (same |q|, same r = 4√2 m).",
                          "y-parts cancel; x-parts both point −x."],
                   aria="Q7 (i) field vectors at P")
    vector_diagram("a2-q7b", [dict(q=1, pos=(-4, 0), label="+4 C", away=(0, -1)),
                              dict(q=4, pos=(0, 0), label="+4q = +16 C", away=(1, -1)),
                              dict(q=1, pos=(4, 0), label="+4 C", away=(0, -1))],
                   (0, 4), (-6.2, 6.2, -1.4, 7.6), plabel=(12, 14, "start"), arrow_px=55,
                   groups=[([0, 2], ""), ([1], "", 18)],
                   net_label="E = 1.06×10¹⁰ N/C (+y)", net_lpos=(16, -96, "start"),
                   notes=["Short arrow: the two side charges (1.59×10⁹ N/C, +y).",
                          "Long arrow: +16 C at O (8.99×10⁹ N/C, +y). All add along +y."],
                   aria="Q7 (ii) field vectors at P")

    # Q9: electron on the dipole axis
    c = Canvas((-1.0, 7.4, -1.0, 1.0), 560, pad=(30, 30, 46, 48))
    c.line(c.X(-0.8), c.Y(0), c.X(6.2), c.Y(0), MUTED, 1.2, "5,4")
    c.arrow(c.X(-0.35), c.Y(0) + 30, c.X(0.35), c.Y(0) + 30, NET, 2.4, 10)
    c.text(c.X(0), c.Y(0) + 48, "p", NET, 13, "middle", "bold")
    c.text((c.X(0) + c.X(5)) / 2, c.Y(0) - 14, "z = 5 nm", GOLD, 12.5, "middle", "bold")
    c.arrow(c.X(5), c.Y(0) - 30, c.X(5) + 70, c.Y(0) - 30, VEC, 3, 11)
    c.text(c.X(5) + 74, c.Y(0) - 26, "E (along p)", VEC, 12, "start", "bold")
    c.arrow(c.X(5), c.Y(0) + 30, c.X(5) - 70, c.Y(0) + 30, "#f472b6", 3, 11)
    c.text(c.X(5) - 74, c.Y(0) + 34, "F on electron", "#f472b6", 12, "end", "bold")
    c.charge(-0.3, 0, -1, "", r=9)
    c.charge(0.3, 0, 1, "", r=9)
    c.charge(5, 0, -1, "", r=8)
    c.text(c.W / 2, 26, "Q9: electron on the dipole axis", TXT, 14, "middle", "bold")
    c.text(c.W / 2, c.H - 22, "On the axis E points along p; the electron's force is opposite to E.", MUTED, 12)
    q4.save("a2-q9", c.svg("Q9 dipole axis"))
    print("\n".join(sorted(os.listdir(OUT))))


if __name__ == "__main__":
    build()
