"""Generate the Quiz-5 (electric potential) SVG diagrams.

Run: python3 quiz5_figures.py
Reuses the canvas and plotting helpers from quiz4_figures.py. Equipotentials
are true contours of V (marching squares on a grid); field lines are traced
numerically, so both follow directly from Coulomb's law.
"""
import os
from math import hypot, cos, sin, pi, sqrt

import quiz4_figures as q4
from quiz4_figures import Canvas, trace, plot, vector_diagram, VEC, NET, TXT, MUTED

OUT = "quiz5-figures"
q4.OUT = OUT
GOLD = "#f59e0b"


def potential(charges, x, y):
    v = 0.0
    for q, (cx, cy) in charges:
        r = hypot(x - cx, y - cy)
        v += q / max(r, 1e-6)
    return v


def contour_segments(f, box, levels, nx=221, ny=171):   # odd counts: no grid line sits exactly on a symmetry axis
    """Marching squares: return {level: [(x1,y1,x2,y2), ...]}."""
    x0, x1, y0, y1 = box
    dx, dy = (x1 - x0) / nx, (y1 - y0) / ny
    grid = [[f(x0 + i * dx, y0 + j * dy) for i in range(nx + 1)] for j in range(ny + 1)]
    out = {L: [] for L in levels}

    def interp(pa, pb, va, vb, L):
        t = (L - va) / (vb - va)
        return pa[0] + t * (pb[0] - pa[0]), pa[1] + t * (pb[1] - pa[1])

    for j in range(ny):
        for i in range(nx):
            p = [(x0 + i * dx, y0 + j * dy), (x0 + (i + 1) * dx, y0 + j * dy),
                 (x0 + (i + 1) * dx, y0 + (j + 1) * dy), (x0 + i * dx, y0 + (j + 1) * dy)]
            v = [grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]]
            if max(abs(t) for t in v) > 40:      # skip cells right on top of a charge
                continue
            for L in levels:
                pts = []
                for a, b in ((0, 1), (1, 2), (2, 3), (3, 0)):
                    if (v[a] - L) * (v[b] - L) < 0:
                        pts.append(interp(p[a], p[b], v[a], v[b], L))
                if len(pts) == 2:
                    out[L].append((*pts[0], *pts[1]))
                elif len(pts) == 4:
                    out[L].append((*pts[0], *pts[1]))
                    out[L].append((*pts[2], *pts[3]))
    return out


def equipotential_figure(name, charges, box, title, notes, levels, n_lines=14, width=340, uniform=False):
    c = Canvas(box, width, pad=(14, 14, 34, 52))
    clip = f"clip{name}"
    c.add(f'<clipPath id="{clip}"><rect x="{c.pl}" y="{c.pt}" width="{c.W-c.pl-c.pr}" height="{c.H-c.pt-c.pb}"/></clipPath>')
    c.add(f'<g clip-path="url(#{clip})">')
    if uniform:
        # field points down (from + plate to - plate); equipotentials are horizontal
        for k in range(1, 9):
            x = box[0] + (box[1] - box[0]) * k / 9
            c.arrow(c.X(x), c.Y(box[3] - 0.15), c.X(x), c.Y(box[2] + 0.15), "#818cf8", 1.6, 8)
        for k in range(1, 6):
            y = box[2] + (box[3] - box[2]) * k / 6
            c.line(c.X(box[0]), c.Y(y), c.X(box[1]), c.Y(y), GOLD, 1.6, "6,4")
        c.text(c.X(box[1]) - 6, c.Y(box[3]) + 16, "high V", GOLD, 11.5, "end")
        c.text(c.X(box[1]) - 6, c.Y(box[2]) - 8, "low V", GOLD, 11.5, "end")
    else:
        segs = contour_segments(lambda x, y: potential(charges, x, y), box, levels)
        for L, ss in segs.items():
            d = " ".join(f"M{c.X(a):.1f},{c.Y(b):.1f}L{c.X(p):.1f},{c.Y(q):.1f}" for a, b, p, q in ss)
            if d:
                c.add(f'<path d="{d}" stroke="{GOLD}" stroke-width="1.5" fill="none"/>')
        sources = [(q, p) for q, p in charges if q > 0]
        sign = 1
        if not sources:
            sources = [(-q, p) for q, p in charges]
            sign = -1
        for q, (cx, cy) in sources:
            k = int(round(n_lines * abs(q) / max(abs(qq) for qq, _ in charges)))
            for j in range(k):
                t = 2 * pi * (j + 0.5) / k
                pts = trace(charges, (cx + 0.09 * cos(t), cy + 0.09 * sin(t)), sign, box)
                dd = "M " + " L ".join(f"{c.X(px):.1f},{c.Y(py):.1f}" for px, py in pts)
                c.add(f'<path d="{dd}" fill="none" stroke="#818cf8" stroke-width="1.2" opacity="0.85"/>')
    c.add("</g>")
    for q, (cx, cy) in charges:
        c.charge(cx, cy, q, "", r=10)
    c.text(c.W / 2, 22, title, TXT, 14, "middle", "bold")
    for j, t in enumerate(notes):
        c.text(c.W / 2, c.H - c.pb + 20 + j * 16, t, MUTED, 11.5)
    q4.save(name, c.svg(title))


def pot_diagram(name, charges, box, *, P=None, plabel=("P", 12, -10, "start"), outline=(), dashed=(),
                dist=(), notes=(), title="", width=460, extra=None):
    """Geometry sketch for a potential problem.

    charges: [(q, (x, y), label, away)], P: point where V is wanted,
    outline: solid polylines (e.g. the square), dashed: extra dashed segments,
    dist: [(i, text, frac, dx, dy)] distance label on the line from charge i to P,
          or [((x1,y1), (x2,y2), text, dx, dy)] for a free segment label.
    """
    c = Canvas(box, width, pad=(40, 40, 46 if title else 24, 24 + 18 * len(notes)))
    for pts in outline:
        c.add('<polyline points="' + " ".join(f"{c.X(x):.1f},{c.Y(y):.1f}" for x, y in pts) +
              f'" fill="none" stroke="{MUTED}" stroke-width="1.6"/>')
    for (x1, y1), (x2, y2) in dashed:
        c.line(c.X(x1), c.Y(y1), c.X(x2), c.Y(y2), "#4b5563", 1.2, "5,4")
    if P is not None:
        for q, pos, *_ in charges:
            c.line(c.X(pos[0]), c.Y(pos[1]), c.X(P[0]), c.Y(P[1]), "#6b7280", 1.3, "5,4")
    for d in dist:
        if isinstance(d[0], int):
            i, t, f, dx, dy = d
            (x1, y1), (x2, y2) = charges[i][1], P
        else:
            (x1, y1), (x2, y2), t, dx, dy = d
            f = 0.5
        mx, my = c.X(x1) + (c.X(x2) - c.X(x1)) * f, c.Y(y1) + (c.Y(y2) - c.Y(y1)) * f
        c.text(mx + dx, my + dy, t, GOLD, 12, "middle", "bold")
    if extra:
        extra(c)
    for q, pos, lab, away in charges:
        c.charge(pos[0], pos[1], q, lab, away)
    if P is not None:
        c.add(f'<circle cx="{c.X(P[0]):.1f}" cy="{c.Y(P[1]):.1f}" r="5" fill="#f9fafb"/>')
        c.text(c.X(P[0]) + plabel[1], c.Y(P[1]) + plabel[2], plabel[0], "#f9fafb", 13, plabel[3], "bold")
    if title:
        c.text(c.W / 2, 26, title, TXT, 14, "middle", "bold")
    for j, t in enumerate(notes):
        c.text(c.W / 2, c.H - c.pb + 20 + j * 18, t, MUTED, 12)
    q4.save(name, c.svg(title or name))


def build_problem_figures():
    # PPS-5 #1: the arrangement the question asks you to draw
    L = 0.10
    sq = [(0, L), (L, L), (L, 0), (0, 0), (0, L)]
    pot_diagram("pps-01", [(2, (0, L), "A: +2q", (-1, 1)), (4, (L, L), "B: +4q", (1, 1)),
                           (2, (L, 0), "C: +2q", (1, -1)), (-2, (0, 0), "D: −2q", (-1, -1))],
                (-0.035, 0.135, -0.03, 0.13), P=(L / 2, L / 2), plabel=("O", 14, 5, "start"), outline=[sq],
                dist=[(((0, L), (L, L), "10 cm", 0, -10)), (((L, L), (L, 0), "10 cm", 30, 4)),
                      (0, "r = 7.07 cm", 0.5, 44, -12)],
                title="Charges at the corners of the square",
                notes=["O is where the diagonals cross: r = side/√2 = 7.07 cm from every corner."])

    # PPS-5 #2
    def p2(c):
        c.arrow(c.X(0.205), c.Y(0), c.X(0.1), c.Y(0), GOLD, 2.4, 10)
        c.text(c.X(0.208), c.Y(0) + 4, "from ∞", GOLD, 12, "start")
        c.text(c.X(0.16), c.Y(0) - 12, "q₀ = 2×10⁻⁹ C", GOLD, 12)
    pot_diagram("pps-02", [(1, (0, 0), "q = 4×10⁻⁷ C", (0, 1))], (-0.04, 0.26, -0.05, 0.05),
                P=(0.09, 0), plabel=("P", 0, 22, "middle"), dist=[(0, "r = 0.09 m", 0.5, 0, -10)], extra=p2,
                title="Bringing q₀ in from infinity to P",
                notes=["V at P depends only on q and r; the work is W = q₀V."])

    # PPS-5 #4
    pot_diagram("pps-04", [(-1, (-0.1, 0), "−q", (-1, -0.3)), (-1, (0.1, 0), "−q", (1, -0.3))],
                (-0.15, 0.15, -0.04, 0.14), P=(0, 0.1), plabel=("P", 0, -14, "middle"),
                outline=[[(-0.1, 0), (0.1, 0)], [(0, 0), (0, 0.1)]],
                dist=[((-0.1, 0), (0, 0), "10 cm", 0, 18), ((0, 0), (0.1, 0), "10 cm", 0, 18),
                      ((0, 0), (0, 0.1), "10 cm", 26, 4), (0, "r = 14.1 cm", 0.5, -44, -4)],
                title="Two equal negative charges",
                notes=["Each charge is r = √(0.10² + 0.10²) = 0.141 m from P."])

    # PPS-5 #5
    pot_diagram("pps-05", [(1, (0, 0), "q = ?", (0, 1))], (-0.12, 0.78, -0.08, 0.08),
                P=(0.6, 0), plabel=("P: E = 5.0 N/C", 0, 24, "middle"), dist=[(0, "r = 60 cm", 0.5, 0, -10)],
                title="Point charge and the field point",
                notes=["Same r in E = kq/r² and V = kq/r, so V = E·r."])

    # PPS-5 #7: ammonia dipole, point on the axis
    def p7(c):
        c.arrow(c.X(-0.25), c.Y(0) + 26, c.X(0.25), c.Y(0) + 26, NET, 2.4, 10)
        c.text(c.X(0), c.Y(0) + 44, "p (from − to +)", NET, 12)
    pot_diagram("pps-07", [(-1, (-0.3, 0), "−q", (0, 1)), (1, (0.3, 0), "+q", (0, 1))],
                (-0.6, 3.4, -0.5, 0.45), P=(3.0, 0), plabel=("P", 0, -14, "middle"),
                dist=[((0, 0), (3.0, 0), "r = 52.0 nm (from the centre)", 0, -10)], extra=p7,
                title="Point on the dipole axis (θ = 0°)",
                notes=["r ≫ d, so the dipole formula V = kp cosθ / r² applies."])

    # Slide P4 / PPS-5 #8: before and at closest approach
    def p8(c):
        y1, y2 = 0.55, -0.6
        c.text(c.X(-2.1), c.Y(y1) - 24, "Far apart: U ≈ 0, all energy kinetic", MUTED, 12, "start")
        c.arrow(c.X(-1.7), c.Y(y1), c.X(-1.05), c.Y(y1), GOLD, 2.4, 10)
        c.arrow(c.X(1.7), c.Y(y1), c.X(1.05), c.Y(y1), GOLD, 2.4, 10)
        c.text(c.X(-1.35), c.Y(y1) - 10, "v", GOLD, 13, "middle", "bold")
        c.text(c.X(1.35), c.Y(y1) - 10, "v", GOLD, 13, "middle", "bold")
        c.text(c.X(-2.1), c.Y(y2) - 24, "Closest approach: both stop, all energy potential", MUTED, 12, "start")
        c.line(c.X(-0.45), c.Y(y2) + 22, c.X(0.45), c.Y(y2) + 22, GOLD, 1.4)
        c.text(c.X(0), c.Y(y2) + 38, "r_min", GOLD, 13, "middle", "bold")
    pot_diagram("pps-08", [(1, (-2.0, 0.55), "proton (m, +e)", (0, -1)), (2, (2.0, 0.55), "alpha (4m, +2e)", (0, -1)),
                           (1, (-0.45, -0.6), "", (0, 1)), (2, (0.45, -0.6), "", (0, 1))],
                (-2.6, 2.6, -1.1, 1.05), extra=p8, title="Proton and alpha particle, head on",
                notes=["Slide method: ½mv² + ½(4m)v² = k(e)(2e)/r_min."])

    # PPS-5 #10 (and slide P3 uses the same layout)
    pot_diagram("pps-10", [(-1, (0, 1), "−1.0 μC at (0, 1)", (1, 0.4)), (3, (3, 0), "+3.0 μC at (3, 0)", (0, 1))],
                (-0.9, 3.8, -0.6, 1.5), P=(0, 0), plabel=("O", -10, 20, "end"),
                outline=[[(-0.6, 0), (3.6, 0)], [(0, -0.4), (0, 1.35)]],
                dist=[(0, "1 m", 0.5, -20, 4), (1, "3 m", 0.5, 0, -10)],
                title="Charges on the axes, V wanted at the origin",
                notes=["The +3 μC charge is 3× bigger but 3× further away."])

    # PPS-5 #16: right angle at q1 (stated assumption)
    a = 0.5
    pot_diagram("pps-16", [(1, (0, 0), "q₁ = 1 μC", (-1, -1)), (-2, (a, 0), "q₂ = −2 μC", (1, -1)),
                           (3, (0, a), "q₃ = 3 μC", (-1, 1))],
                (-0.25, 0.75, -0.17, 0.65), outline=[[(0, 0), (a, 0), (0, a), (0, 0)]],
                dist=[((0, 0), (a, 0), "r₁₂ = 0.5 m", 0, 20), ((0, 0), (0, a), "r₁₃ = 0.5 m", -48, 4),
                      ((a, 0), (0, a), "r₂₃ = 0.707 m", 52, -6)],
                extra=lambda c: c.add(f'<polyline points="{c.X(0.05):.1f},{c.Y(0):.1f} {c.X(0.05):.1f},{c.Y(0.05):.1f} {c.X(0):.1f},{c.Y(0.05):.1f}" fill="none" stroke="{MUTED}" stroke-width="1.3"/>'),
                title="Isosceles right triangle (right angle at q₁)",
                notes=["Three charges → three pairs: 1-2, 1-3, 2-3."])

    # PPS-5 #17: distances from the centre
    pot_diagram("pps-17", [(2, (-1, 0.5), "+2q₁", (-1, 1)), (4, (0, 0.5), "+4q₂", (0, 1)), (-3, (1, 0.5), "−3q₁", (1, 1)),
                           (-1, (-1, -0.5), "−q₁", (-1, -1)), (4, (0, -0.5), "+4q₂", (0, -1)), (2, (1, -0.5), "+2q₁", (1, -1))],
                (-1.5, 1.5, -0.95, 0.95), P=(0, 0), plabel=("C", 12, 18, "start"),
                outline=[[(-1, 0.5), (1, 0.5), (1, -0.5), (-1, -0.5), (-1, 0.5)]],
                dist=[(1, "a/2", 0.5, 16, 4), (2, "(√5/2)a", 0.45, 30, -2)],
                title="Rectangle 2a × a, centre C",
                notes=["Middle charges: a/2 from C.  Corners: √(a² + (a/2)²) = (√5/2)a from C."])

    # Slide P3: field vectors (vector problem) next to the scalar potential
    vector_diagram("slide-p3", [dict(q=-1, pos=(0, 1), label="−1.0 μC at (0, 1)", away=(1, 0.3)),
                                dict(q=1, pos=(1, 0), label="+1.0 μC at (1, 0)", away=(0.4, 1))],
                   (0, 0), (-1.35, 1.6, -0.55, 1.35), point_label="origin", plabel=(10, 22, "start"),
                   groups=[([0], "E₋"), ([1], "E₊")], arrow_px=70,
                   net_label="E = 1.27×10⁴ N/C at 135°", net_lpos=(-44, -22, "end"),
                   notes=["E needs vectors: 9000 N/C each, at 90° → √2 × 9000 = 1.27×10⁴ N/C.",
                          "V is a scalar: +9000 V − 9000 V = 0."],
                   aria="Slide problem 3 field vectors at the origin")


def build():
    os.makedirs(OUT, exist_ok=True)
    B = (-1.6, 1.6, -1.3, 1.3)
    equipotential_figure("eq-point", [(1, (0, 0))], B, "Point charge",
                         ["Equipotentials (gold): circles", "Field lines (blue): radial, crossing them at 90°"],
                         levels=[1.0, 1.5, 2.2, 3.4])
    equipotential_figure("eq-uniform", [], (-1.6, 1.6, -1.3, 1.3), "Uniform field",
                         ["Equipotentials (gold): parallel planes", "V falls in the direction of E"], levels=[], uniform=True)
    B2 = (-2.2, 2.2, -1.6, 1.6)
    equipotential_figure("eq-dipole", [(1, (-0.7, 0)), (-1, (0.7, 0))], B2, "Electric dipole",
                         ["The perpendicular bisector is the V = 0 surface", "(E is not zero there)"],
                         levels=[-2.4, -1.4, -0.8, -0.35, 0.0, 0.35, 0.8, 1.4, 2.4])
    equipotential_figure("eq-two-positive", [(1, (-0.7, 0)), (1, (0.7, 0))], B2, "Two equal positive charges",
                         ["At the midpoint E = 0 but V ≠ 0", "(V there = 2kq/r)"],
                         levels=[1.6, 2.0, 2.6, 3.3, 4.2])

    plot("g-V-and-E-vs-r", (0, 4.2, 0, 1.6),
         [(lambda r: 1 / r, 0.63, 4.2, NET, "V ∝ 1/r", (2.85, 0.45), None),
          (lambda r: 1 / r ** 2, 0.79, 4.2, VEC, "E ∝ 1/r²", (2.85, 0.2), "7,5")],
         "distance r (units of r₀)", "V and E (units of their values at r₀)",
         [(1, "r₀"), (2, "2r₀"), (3, "3r₀"), (4, "4r₀")], [(0.5, "0.5"), (1, "1"), (1.5, "1.5")],
         callouts=[(2, 0.5, "V/2", 2.15, 0.95, NET), (2, 0.25, "E/4", 2.15, 0.76, VEC)],
         notes=["Double the distance: potential halves, field drops to a quarter.",
                "For a negative charge draw the V curve below the axis (V < 0)."],
         title="Point charge: potential vs field")

    a = 1.0
    inv = lambda u: 1 / max(abs(u), 1e-9)
    fd = lambda x: inv(x + a) - inv(x - a)        # dipole
    fl = lambda x: inv(x + a) + inv(x - a)        # two like charges
    pieces = [(-3, -a - 1e-3), (-a + 1e-3, a - 1e-3), (a + 1e-3, 3)]   # break the curve at each charge
    plot("g-V-on-axis", (-3, 3, -3.2, 3.2),
         [(fd, lo, hi, NET, "dipole (+q left, −q right)" if lo == -3 else "", (-2.9, -2.55), None) for lo, hi in pieces] +
         [(fl, lo, hi, "#f472b6", "two equal +q" if lo == -3 else "", (-2.9, 2.9), "7,5") for lo, hi in pieces],
         "position x along the line joining the charges (units of a)", "V (units of kq/a)",
         [(-1, "−a"), (0, "0"), (1, "+a")], [(-2, "−2"), (0, "0"), (2, "+2")],
         marks=[(0, 0, "dipole: V = 0, E ≠ 0", "end", -10, 24), (0, 2, "like charges: V = 2, E = 0", "start", 10, 24)],
         notes=["The midpoint shows the key contrast: zero potential does not mean zero field,",
                "and zero field does not mean zero potential."],
         title="Potential along the line through two charges")
    plot("g-U-vs-r", (0, 4.2, -3, 3),
         [(lambda r: 1 / r, 0.34, 4.2, "#f472b6", "like charges: U = +kq₁q₂/r", (1.55, 1.25), None),
          (lambda r: -1 / r, 0.34, 4.2, NET, "unlike charges: U = −kq₁q₂/r", (1.55, -1.45), None)],
         "separation r", "U (units of kq₁q₂/r₀)",
         [(0.5, "r_min"), (1, "r₀"), (2, "2r₀"), (3, "3r₀"), (4, "4r₀")], [(-2, "−2"), (0, "0"), (2, "+2")],
         hlines=[(2, GOLD)],
         callouts=[(0.5, 2, "turning point: K = U", 0.95, 2.45, GOLD)],
         notes=["Like charges repel: U grows as they approach. A pair arriving with total K",
                "stops where U = K (gold line) — that is r_min in PPS-5 #8 and #9."],
         title="Potential energy of two charges vs separation")

    plot("g-V-uniform", (0, 1.25, 0, 1.25),
         [(lambda x: 1 - x, 0, 1, NET, "V = V₀ − Ex", (0.5, 0.62), None),
          (lambda x: 0.5, 0, 1, VEC, "E = constant", (0.68, 0.42), "7,5")],
         "distance x along the field (units of d)", "V (units of V₀),  E",
         [(0, "0"), (0.5, "d/2"), (1, "d")], [(0.5, "0.5"), (1, "V₀")],
         marks=[(0.25, 0.75, "slope = −E", "start", 12, -6)],
         notes=["In a uniform field V falls linearly along E: ΔV = −Ed.",
                "A straight V line means a constant E; a steeper line means a stronger field."],
         title="Uniform field: V and E vs distance")
    build_problem_figures()
    print("\n".join(sorted(f for f in os.listdir(OUT) if f.endswith(".svg"))))


if __name__ == "__main__":
    build()
