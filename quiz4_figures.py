"""Generate the Quiz-4 SVG diagrams (run: python3 quiz4_figures.py).

Every arrow is computed from charge positions with Coulomb's law, so the
pictures cannot drift from the verified numerical answers.
"""
from math import hypot, atan2, cos, sin, radians, degrees, sqrt, pi
import os, sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "quiz4-figures"
BG, AX, TXT, MUTED = "#161a26", "#6b7280", "#e5e7eb", "#9ca3af"
POS, NEG, VEC, NET, PT = "#ef4444", "#3b82f6", "#fbbf24", "#4ade80", "#f9fafb"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;")


class Canvas:
    def __init__(self, box, width=540, pad=(48, 48, 48, 70), height=None):
        self.xmin, self.xmax, self.ymin, self.ymax = box
        self.pl, self.pr, self.pt, self.pb = pad
        self.W = width
        self.sx = (width - self.pl - self.pr) / (self.xmax - self.xmin)
        if height:          # graphs: independent axis scales
            self.H = height
            self.sy = (height - self.pt - self.pb) / (self.ymax - self.ymin)
        else:               # geometry: equal scales so angles are true
            self.sy = self.sx
            self.H = int(self.pt + self.pb + (self.ymax - self.ymin) * self.sy)
        self.parts = []

    def X(self, x): return self.pl + (x - self.xmin) * self.sx
    def Y(self, y): return self.pt + (self.ymax - y) * self.sy
    def add(self, t): self.parts.append(t)

    def text(self, x, y, t, fill=TXT, size=13, anchor="middle", weight="normal"):
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" fill="{fill}" font-size="{size}" '
                 f'text-anchor="{anchor}" font-weight="{weight}" font-family="Inter,Arial,sans-serif">{esc(t)}</text>')

    def line(self, x1, y1, x2, y2, stroke=AX, w=1.5, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{w}"{d}/>')

    def arrow(self, x1, y1, x2, y2, color, w=3, head=11):
        L = hypot(x2 - x1, y2 - y1)
        if L < 2:
            return
        ux, uy = (x2 - x1) / L, (y2 - y1) / L
        bx, by = x2 - ux * head, y2 - uy * head
        self.line(x1, y1, bx, by, color, w)
        px, py = -uy * head * 0.5, ux * head * 0.5
        self.add(f'<polygon points="{x2:.1f},{y2:.1f} {bx+px:.1f},{by+py:.1f} {bx-px:.1f},{by-py:.1f}" fill="{color}"/>')

    def axes(self, xl="x", yl="y"):
        if self.xmin < 0 < self.xmax:
            self.line(self.X(0), self.Y(self.ymin), self.X(0), self.Y(self.ymax), AX, 1.3)
            self.text(self.X(0) + 10, self.Y(self.ymax) + 12, yl, MUTED, 12, "start")
        if self.ymin < 0 < self.ymax:
            self.line(self.X(self.xmin), self.Y(0), self.X(self.xmax), self.Y(0), AX, 1.3)
            self.text(self.X(self.xmax) - 4, self.Y(0) - 7, xl, MUTED, 12, "end")

    def charge(self, x, y, q, label, away=(0, 1), r=11):
        cx, cy = self.X(x), self.Y(y)
        col = POS if q > 0 else NEG
        self.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{col}"/>')
        self.text(cx, cy + 5, "+" if q > 0 else "−", "#fff", 15)
        if label:
            ax, ay = away
            n = hypot(ax, ay) or 1
            ax, ay = ax / n, ay / n
            lx, ly = cx + ax * 26, cy - ay * 26 + 4
            anc = "start" if ax > 0.35 else ("end" if ax < -0.35 else "middle")
            self.text(lx, ly, label, TXT, 12.5, anc)

    def svg(self, aria):
        body = "\n".join(self.parts)
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.W} {self.H}" role="img" aria-label="{esc(aria)}">\n'
                f'<rect width="{self.W}" height="{self.H}" rx="12" fill="{BG}"/>\n{body}\n</svg>\n')


def efield(charges, P):
    """Field (k=1) at P from charges [(q,(x,y)),...] -> list of vectors."""
    out = []
    for q, (x, y) in charges:
        dx, dy = P[0] - x, P[1] - y
        r = hypot(dx, dy)
        out.append((q * dx / r ** 3, q * dy / r ** 3))
    return out


def lbl_at(c, tipx, tipy, ux, uy, t, color, size=12.5, bold=False):
    lx, ly = tipx + ux * 16, tipy + uy * 16 + 4
    anc = "start" if ux > 0.35 else ("end" if ux < -0.35 else "middle")
    c.text(lx, ly, t, color, size, anc, "bold" if bold else "normal")


def vector_diagram(name, charges, P, box, *, groups=None, arrow_px=95, point_label="P",
                   net_label="E_net", notes=(), aria="", width=540, dist_labels=None, axes=True,
                   plabel=(-12, -12, "end"), dist_frac=0.5, net_lpos=None):
    """charges: list of dict(q, pos, label). groups: list of (indices, label)."""
    c = Canvas(box, width)
    if axes:
        c.axes()
    Px, Py = c.X(P[0]), c.Y(P[1])
    for i, ch in enumerate(charges):
        c.line(c.X(ch["pos"][0]), c.Y(ch["pos"][1]), Px, Py, "#4b5563", 1.2, "5,4")
        if dist_labels and dist_labels.get(i):
            mx = c.X(ch["pos"][0]) + (Px - c.X(ch["pos"][0])) * dist_frac
            my = c.Y(ch["pos"][1]) + (Py - c.Y(ch["pos"][1])) * dist_frac
            c.text(mx + 8, my - 6, dist_labels[i], MUTED, 11.5, "start")
    vecs = efield([(ch["q"], ch["pos"]) for ch in charges], P)
    if groups is None:
        groups = [([i], ch.get("elabel", f"E{i+1}")) for i, ch in enumerate(charges)]
    gv = []
    for g in groups:
        idx, lab = g[0], g[1]
        off = g[2] if len(g) > 2 else 0
        vx = sum(vecs[i][0] for i in idx)
        vy = sum(vecs[i][1] for i in idx)
        gv.append((vx, vy, lab, off))
    net = (sum(v[0] for v in vecs), sum(v[1] for v in vecs))
    mags = [hypot(v[0], v[1]) for v in gv] + [hypot(*net)]
    big = max(m for m in mags if m > 1e-12)
    sc = arrow_px / max(hypot(v[0], v[1]) for v in gv if hypot(v[0], v[1]) > 1e-9 * big)
    if hypot(*net) * sc > arrow_px * 1.9:
        sc = arrow_px * 1.9 / hypot(*net)
    for vx, vy, lab, off in gv:
        m = hypot(vx, vy)
        if m < 1e-9 * big:
            continue
        ux, uy = vx / m, -vy / m
        ox, oy = -uy * off, ux * off          # sideways shift keeps collinear arrows visible
        tx, ty = Px + ox + ux * m * sc, Py + oy + uy * m * sc
        c.arrow(Px + ox, Py + oy, tx, ty, VEC, 3)
        if lab:
            lbl_at(c, tx, ty, ux, uy, lab, VEC)
    m = hypot(*net)
    if m > 1e-9 * big and net_label:
        ux, uy = net[0] / m, -net[1] / m
        tx, ty = Px + ux * m * sc, Py + uy * m * sc
        c.arrow(Px, Py, tx, ty, NET, 4, 13)
        if net_lpos:
            c.text(Px + net_lpos[0], Py + net_lpos[1], net_label, NET, 13, net_lpos[2], "bold")
        else:
            lbl_at(c, tx, ty, ux, uy, net_label, NET, 13, True)
    for ch in charges:
        dx, dy = ch["pos"][0] - P[0], ch["pos"][1] - P[1]
        c.charge(ch["pos"][0], ch["pos"][1], ch["q"], ch.get("label", ""), ch.get("away", (dx, dy)))
    c.add(f'<circle cx="{Px:.1f}" cy="{Py:.1f}" r="5" fill="{PT}"/>')
    if point_label:
        c.text(Px + plabel[0], Py + plabel[1], point_label, PT, 13, plabel[2], "bold")
    y0 = c.H - c.pb + 26
    for j, n in enumerate(notes):
        c.text(c.W / 2, y0 + j * 18, n, MUTED, 12)
    save(name, c.svg(aria or name))


def save(name, s):
    with open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8") as f:
        f.write(s)


# ------------------------------------------------------------------ vectors
def build_vectors():
    d = 1.0
    at = lambda deg, r=d: (r * cos(radians(deg)), r * sin(radians(deg)))
    vector_diagram("v-slide-p1", [
        dict(q=2, pos=at(150), label="q1 = +2Q"),
        dict(q=-2, pos=at(-30), label="q2 = −2Q"),
        dict(q=-4, pos=at(30), label="q3 = −4Q")],
        (0, 0), (-1.25, 2.05, -0.95, 0.95),
        groups=[([0, 1], "E1 + E2"), ([2], "E3")], point_label="origin", plabel=(-10, 22, "end"),
        arrow_px=72, net_lpos=(131, -8, "start"),
        net_label="E = 6.93 kQ/d²",
        notes=["E1 and E2 point the same way (both along −30°), so they add first.",
               "The y-parts of (E1+E2) and E3 cancel; the x-parts double."],
        aria="Slide problem 1 field vectors at the origin")

    vector_diagram("v-p01", [
        dict(q=1, pos=(-0.05, 0), label="+q"), dict(q=1, pos=(0.05, 0), label="+q")],
        (0, 0.0866), (-0.085, 0.085, -0.02, 0.19), point_label="third corner",
        net_label="E = 1.87×10⁶ N/C",
        notes=["Each field 1.08×10⁶ N/C, pointing away from its (positive) charge.",
               "Horizontal parts cancel; resultant runs up the perpendicular bisector."],
        aria="P1 triangle field vectors", dist_labels={0: "10 cm", 1: "10 cm"})

    vector_diagram("v-p03", [
        dict(q=-1, pos=(-0.1, 0), label="−q"), dict(q=-1, pos=(0.1, 0), label="−q")],
        (0, 0.1), (-0.15, 0.15, -0.09, 0.16), plabel=(14, -8, "start"),
        net_label="E = 6.36×10⁷ N/C",
        notes=["Negative charges: each field points TOWARD its charge.",
               "x-parts cancel; net field points straight down (−y)."],
        aria="P3 field vectors at P")

    a = 0.05
    vector_diagram("v-p05", [
        dict(q=10, pos=(0, a), label="q1 = +10 nC", away=(-1, 1)),
        dict(q=-20, pos=(a, a), label="q2 = −20 nC", away=(1, 1)),
        dict(q=20, pos=(a, 0), label="q3 = +20 nC", away=(1, -1)),
        dict(q=-10, pos=(0, 0), label="q4 = −10 nC", away=(-1, -1))],
        (a / 2, a / 2), (-0.03, 0.08, -0.024, 0.074),
        groups=[([0, 2], "q1 + q3"), ([1, 3], "q2 + q4")], point_label="centre",
        net_label="E = (1.02×10⁵ N/C) ĵ",
        notes=["Pair the diagonals: each diagonal leaves a net 0.72×10⁵ N/C.",
               "Those two leftovers are at 90°; their x-parts cancel, y-parts add."],
        aria="P5 square field vectors at the centre", axes=False)

    r6 = 0.1 / sqrt(2)          # square drawn on its corner so the B-to-D diagonal is horizontal
    vector_diagram("v-p06", [
        dict(q=2, pos=(0, r6), label="A: +2q", away=(0, 1)),
        dict(q=4, pos=(r6, 0), label="B: +4q", away=(1, 0)),
        dict(q=2, pos=(0, -r6), label="C: +2q", away=(0, -1)),
        dict(q=-2, pos=(-r6, 0), label="D: \u22122q", away=(-1, 0))],
        (0, 0), (-0.105, 0.105, -0.09, 0.09), arrow_px=62, plabel=(12, 22, "start"),
        groups=[([0, 2], ""), ([1], "from B", -24), ([3], "from D", -46)], point_label="O",
        net_label="E = 6.15\u00d710\u2075 N/C", net_lpos=(-46, -14, "middle"),
        notes=["A and C are equal and opposite across their diagonal \u2192 they cancel.",
               "B pushes away and D pulls toward, so both point from B to D and add."],
        aria="P6 square field vectors", axes=False)

    vector_diagram("v-p07", [
        dict(q=-1, pos=(-3, 0), label="−q (x = −3 m)"),
        dict(q=1, pos=(3, 0), label="+q (x = +3 m)")],
        (0, 4), (-4.2, 4.2, -1.2, 5.6), plabel=(14, -10, "start"), dist_frac=0.3,
        net_label="E = 2.07×10⁻¹⁰ N/C", dist_labels={0: "5 m", 1: "5 m"},
        notes=["Both fields have equal size (same |q|, same 5 m distance).",
               "Their y-parts cancel; x-parts both point −x."],
        aria="P7 field vectors at P")

    vector_diagram("v-p09", [
        dict(q=-1, pos=(0, 2), label="−1 μC at (0,2)"),
        dict(q=1, pos=(1, 0), label="+1 μC at (1,0)", away=(1, -0.6))],
        (0, 0), (-1.9, 1.9, -0.7, 2.5), point_label="origin", plabel=(10, 22, "start"),
        groups=[([0], "E from −1 μC"), ([1], "E from +1 μC")],
        net_label="E = 9.27×10³ N/C",
        notes=["The +1 μC is 1 m away (field 8990 N/C); the −1 μC is 2 m away (2248 N/C).",
               "Net points 14.0° above the −x axis."],
        aria="P9 field vectors at origin")

    vector_diagram("v-p12", [
        dict(q=10, pos=(0, 0), label="q1 = +10 nC", away=(-1, -0.4)),
        dict(q=15, pos=(4, 0), label="q2 = +15 nC", away=(1, -0.5))],
        (0, 3), (-2.6, 5.8, -0.9, 5.4), point_label="(0, 3)", plabel=(14, 6, "start"),
        groups=[([0], "E1 = 9.99"), ([1], "E2 = 5.39")],
        net_label="E = 13.9 N/C at 108°",
        dist_labels={0: "3 m", 1: "5 m"},
        notes=["3-4-5 triangle: E2 has components (−0.8, +0.6) × 5.39 N/C."],
        aria="P12 field vectors")

    a = 1.0
    vector_diagram("v-p13", [
        dict(q=1, pos=(0, a), label="1: +e"), dict(q=1, pos=(a, 0), label="2: +e"),
        dict(q=2, pos=(0, 0), label="3: +2e", away=(-1, -1))],
        (a / 2, a / 2), (-0.35, 1.45, -0.3, 1.3),
        groups=[([0], "E1"), ([1], "E2"), ([2], "")], plabel=(-12, 18, "end"),
        net_label="E = E3 = 160 N/C at 45°",
        notes=["E1 and E2: equal size, exactly opposite → cancel.",
               "Only E3 survives; it points away from particle 3 at 45°."],
        aria="P13 field vectors")

    r = 1.0
    arc = [(-1, 0, "e"), (1, 30, "p"), (1, 80, "p"), (-1, 130, "e"), (1, 160, "p")]
    vector_diagram("v-p15", [
        dict(q=q, pos=(r * cos(radians(t)), r * sin(radians(t))),
             label=f"{n} ({t}°)", elabel="") for q, t, n in arc],
        (0, 0), (-1.55, 1.55, -1.25, 1.35), point_label="centre", arrow_px=70, plabel=(-14, -12, "end"),
        groups=[([i], "") for i in range(5)],
        net_label="3.93×10⁻⁶ N/C at −76.4°",
        notes=["Each charge gives the same 3.60×10⁻⁶ N/C: protons push away, electrons pull toward.",
               "Charge angles from +x: e 0°, p 30°, p 80°, e 130°, p 160°."],
        aria="P15 arc field vectors")

    vector_diagram("v-p16a", [
        dict(q=15, pos=(-4, 0), label="A: +15 nC"), dict(q=15, pos=(4, 0), label="B: +15 nC")],
        (0, 3), (-5.3, 5.3, -1.3, 5.2), net_label="6.47 N/C (+y)",
        dist_labels={0: "5", 1: "5"}, notes=["Figure-1: like charges → x-parts cancel, y-parts add."],
        aria="P16 figure 1")
    vector_diagram("v-p16b", [
        dict(q=-15, pos=(-4, 0), label="A: −15 nC"), dict(q=15, pos=(4, 0), label="B: +15 nC")],
        (0, 3), (-5.3, 5.3, -1.3, 5.2), net_label="8.63 N/C (−x)",
        dist_labels={0: "5", 1: "5"}, notes=["Figure-2: unlike charges → y-parts cancel, x-parts add (toward A)."],
        aria="P16 figure 2")

    rr = 0.005
    vector_diagram("v-p20", [
        dict(q=3.2, pos=(-rr * cos(radians(30)), rr * sin(radians(30))), label="q1 = 3.2×10⁻¹⁹ C", away=(-1, 1)),
        dict(q=5.6, pos=(rr * cos(radians(30)), rr * sin(radians(30))), label="q2 = 5.6×10⁻¹⁹ C", away=(1, 1))],
        (0, 0), (-0.0078, 0.0078, -0.0068, 0.0052), point_label="O",
        net_label="1.75×10⁻⁴ N/C at 245°",
        notes=["Both positive: fields point away, i.e. down-right and down-left.",
               "q2 is bigger, so the net tilts toward −x."],
        aria="P20 field vectors")

    L = 1.0
    vector_diagram("v-p29", [
        dict(q=1, pos=(-L / 2, L / 2), label="+q", away=(-1, 1)),
        dict(q=-2, pos=(L / 2, L / 2), label="−2q", away=(1, 1)),
        dict(q=-1, pos=(-L / 2, -L / 2), label="−q", away=(-1, -1)),
        dict(q=2, pos=(L / 2, -L / 2), label="+2q", away=(1, -1))],
        (0, 0), (-0.95, 0.95, -0.85, 0.95), point_label="centre", axes=False, plabel=(14, 22, "start"),
        net_label="2.83 kq/L² (up)",
        notes=["Each diagonal joins LIKE charges, so their fields oppose, leaving 2kq/L² each.",
               "Those leftovers are 90° apart: x-parts cancel, y-parts add → 2√2 kq/L² up."],
        aria="P29 square")

    s = 0.1
    vector_diagram("v-p31", [
        dict(q=4, pos=(s, 0), label="4 μC", away=(1, -0.5)),
        dict(q=8, pos=(s, s), label="8 μC", away=(1, 1)),
        dict(q=12, pos=(0, s), label="12 μC", away=(-1, 1))],
        (0, 0), (-0.13, 0.15, -0.15, 0.14), point_label="4th corner", arrow_px=135, plabel=(12, -12, "start"),
        net_label="1.47×10⁷ N/C",
        notes=["All positive: every field points away from the square.",
               "The 12 μC charge dominates, so the net leans steeply along −y."],
        aria="P31 fourth corner")

    vector_diagram("v-p32", [
        dict(q=2, pos=at(120), label="q1 = +2Q"),
        dict(q=-2, pos=at(-60), label="q2 = −2Q"),
        dict(q=4, pos=at(60), label="q3 = +4Q")],
        (0, 0), (-1.2, 1.55, -1.15, 1.1), point_label="A", plabel=(-12, -8, "end"),
        groups=[([0, 1], "E1 + E2"), ([2], "E3")],
        net_label="E = 6.93 kQ/d² (down)",
        notes=["Same structure as slide Problem-1, rotated: E1 and E2 are parallel.",
               "Two equal 4kQ/d² vectors 60° apart → √3 × 4 = 6.93."],
        aria="P32 field vectors")


# --------------------------------------------------------------- field lines
def trace(charges, start, sign, box, h=0.02, nmax=900):
    pts = [start]
    x, y = start
    for _ in range(nmax):
        ex = ey = 0.0
        for q, (cx, cy) in charges:
            dx, dy = x - cx, y - cy
            r3 = (dx * dx + dy * dy) ** 1.5 + 1e-12
            ex += q * dx / r3
            ey += q * dy / r3
        m = hypot(ex, ey)
        if m == 0:
            break
        x += sign * h * ex / m
        y += sign * h * ey / m
        pts.append((x, y))
        if not (box[0] - 0.3 < x < box[1] + 0.3 and box[2] - 0.3 < y < box[3] + 0.3):
            break
        if any(q * sign < 0 and hypot(x - cx, y - cy) < 0.09 for q, (cx, cy) in charges):
            break
    return pts


def field_lines(name, charges, box, title, notes, n=16, width=300):
    c = Canvas(box, width, pad=(14, 14, 34, 50))
    clip = f"clip{name}"
    c.add(f'<clipPath id="{clip}"><rect x="{c.pl}" y="{c.pt}" width="{c.W-c.pl-c.pr}" height="{c.H-c.pt-c.pb}"/></clipPath>')
    c.add(f'<g clip-path="url(#{clip})">')
    sources = [(q, p) for q, p in charges if q > 0]
    sign = 1
    if not sources:                       # lone negative: trace backwards from it
        sources = [(-q, p) for q, p in charges]
        sign = -1
    for q, (cx, cy) in sources:
        k = int(round(n * abs(q) / max(abs(qq) for qq, _ in charges)))
        for j in range(k):
            t = 2 * pi * (j + 0.5) / k
            st = (cx + 0.09 * cos(t), cy + 0.09 * sin(t))
            pts = trace(charges, st, sign, box)
            d = "M " + " L ".join(f"{c.X(px):.1f},{c.Y(py):.1f}" for px, py in pts)
            c.add(f'<path d="{d}" fill="none" stroke="#818cf8" stroke-width="1.3" opacity="0.9"/>')
            mid = len(pts) // 3 if len(pts) > 6 else 0
            if mid and mid + 1 < len(pts):
                (x1, y1), (x2, y2) = pts[mid], pts[mid + 1]
                if sign < 0:
                    (x1, y1), (x2, y2) = (x2, y2), (x1, y1)
                X1, Y1, X2, Y2 = c.X(x1), c.Y(y1), c.X(x2), c.Y(y2)
                L = hypot(X2 - X1, Y2 - Y1) or 1
                ux, uy = (X2 - X1) / L, (Y2 - Y1) / L
                hx, hy = X1 + ux * 7, Y1 + uy * 7
                px, py = -uy * 4.5, ux * 4.5
                c.add(f'<polygon points="{hx:.1f},{hy:.1f} {X1-ux*2+px:.1f},{Y1-uy*2+py:.1f} {X1-ux*2-px:.1f},{Y1-uy*2-py:.1f}" fill="{VEC}"/>')
    c.add("</g>")
    for q, (cx, cy) in charges:
        c.charge(cx, cy, q, "", r=10)
    c.text(c.W / 2, 22, title, TXT, 14, "middle", "bold")
    for j, t in enumerate(notes):
        c.text(c.W / 2, c.H - c.pb + 20 + j * 16, t, MUTED, 11.5)
    save(name, c.svg(title))


def build_field_lines():
    B = (-1.6, 1.6, -1.3, 1.3)
    field_lines("fl-positive", [(1, (0, 0))], B, "Single positive charge",
                ["Lines start on + and go out radially"])
    field_lines("fl-negative", [(-1, (0, 0))], B, "Single negative charge",
                ["Lines come in radially and end on −"])
    B2 = (-2.2, 2.2, -1.6, 1.6)
    field_lines("fl-two-positive", [(1, (-0.7, 0)), (1, (0.7, 0))], B2, "Two equal positive charges",
                ["Lines repel; E = 0 at the midpoint", "(no line passes through it)"], n=14, width=340)
    field_lines("fl-dipole", [(1, (-0.7, 0)), (-1, (0.7, 0))], B2, "Electric dipole (+q, −q)",
                ["Every line from + ends on −", "Dense between the charges = strong E"], n=14, width=340)


# ------------------------------------------------------------------- graphs
def plot(name, box, curves, xlabel, ylabel, xticks, yticks, marks=(), notes=(), title="", width=540,
         hlines=(), callouts=()):
    c = Canvas(box, width, pad=(62, 24, 42, 104), height=400)
    for xv, _ in xticks:
        c.line(c.X(xv), c.Y(box[2]), c.X(xv), c.Y(box[3]), "rgba(255,255,255,0.08)", 1)
    for yv, _ in yticks:
        c.line(c.X(box[0]), c.Y(yv), c.X(box[1]), c.Y(yv), "rgba(255,255,255,0.08)", 1)
    for yv, col in hlines:
        c.line(c.X(box[0]), c.Y(yv), c.X(box[1]), c.Y(yv), col, 1.2, "5,4")
    y0 = 0 if box[2] < 0 < box[3] else box[2]
    c.line(c.X(box[0]), c.Y(y0), c.X(box[1]), c.Y(y0), TXT, 1.8)
    c.line(c.X(box[0]), c.Y(box[2]), c.X(box[0]), c.Y(box[3]), TXT, 1.8)
    for xv, t in xticks:
        c.text(c.X(xv), c.Y(box[2]) + 18, t, MUTED, 12)
    for yv, t in yticks:
        c.text(c.X(box[0]) - 8, c.Y(yv) + 4, t, MUTED, 12, "end")
    c.text((c.X(box[0]) + c.X(box[1])) / 2, c.Y(box[2]) + 40, xlabel, TXT, 13)
    yc = (c.Y(box[2]) + c.Y(box[3])) / 2
    c.add(f'<text x="18" y="{yc:.1f}" fill="{TXT}" font-size="13" text-anchor="middle" '
          f'transform="rotate(-90 18 {yc:.1f})" font-family="Inter,Arial,sans-serif">{esc(ylabel)}</text>')
    for fn, x0, x1, col, lab, lpos, dash in curves:
        pts, n = [], 240
        for i in range(n + 1):
            x = x0 + (x1 - x0) * i / n
            y = fn(x)
            if box[2] - 0.5 < y < box[3] + 0.5:
                pts.append(f"{c.X(x):.1f},{c.Y(min(max(y, box[2]), box[3])):.1f}")
        dd = f' stroke-dasharray="{dash}"' if dash else ""
        c.add(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{col}" stroke-width="3"{dd}/>')
        if lab:
            c.text(c.X(lpos[0]), c.Y(lpos[1]), lab, col, 12.5, "start", "bold")
    for x, y, t, anc, dx, dy in marks:
        c.add(f'<circle cx="{c.X(x):.1f}" cy="{c.Y(y):.1f}" r="5" fill="{NET}"/>')
        c.text(c.X(x) + dx, c.Y(y) + dy, t, NET, 12, anc)
    for x, y, t, lx, ly, col in callouts:
        c.line(c.X(x), c.Y(y), c.X(lx), c.Y(ly) + 4, col, 1.1)
        c.add(f'<circle cx="{c.X(x):.1f}" cy="{c.Y(y):.1f}" r="5" fill="{col}"/>')
        c.text(c.X(lx) + 4, c.Y(ly), t, col, 12.5, "start", "bold")
    if title:
        c.text(c.W / 2, 24, title, TXT, 14, "middle", "bold")
    for j, t in enumerate(notes):
        c.text(c.W / 2, c.H - c.pb + 66 + j * 17, t, MUTED, 12)
    save(name, c.svg(title or name))


def build_graphs():
    plot("g-E-vs-r", (0, 4.2, 0, 1.6),
         [(lambda r: 1 / r ** 2, 0.78, 4.2, VEC, "point charge: E ∝ 1/r²", (2.75, 0.5), None),
          (lambda r: 1 / r ** 3, 0.85, 4.2, "#f472b6", "dipole (far): E ∝ 1/r³", (2.75, 0.33), "7,5")],
         "distance r (units of r₀)", "field E (units of E₀)",
         [(1, "r₀"), (2, "2r₀"), (3, "3r₀"), (4, "4r₀")],
         [(0.5, "0.5"), (1, "E₀"), (1.5, "1.5")],
         callouts=[(1, 1, "(r₀, E₀)", 1.35, 1.25, NET),
                   (2, 0.25, "E₀/4", 2.1, 0.95, VEC),
                   (2, 0.125, "E₀/8", 2.1, 0.75, "#f472b6")],
         notes=["Double the distance: point-charge field falls to 1/4, dipole field to 1/8.",
                "Both approach zero but never reach it."],
         title="Field strength vs distance")

    R = 1.0
    ring = lambda z: z / (z * z + R * R) ** 1.5
    zmax = R / sqrt(2)
    plot("g-ring", (0, 4.2, 0, 0.5),
         [(ring, 0, 4.2, VEC, "ring: E = kqz / (z²+R²)^(3/2)", (1.0, 0.465), None),
          (lambda z: 1 / z ** 2, 1.6, 4.2, "#f472b6", "point charge: kq/z²", (2.75, 0.25), "7,5")],
         "distance z along the axis (units of R)", "E (units of kq/R²)",
         [(0, "0"), (zmax, "R/√2"), (2, "2R"), (3, "3R"), (4, "4R")],
         [(0.1, "0.1"), (0.2, "0.2"), (0.3, "0.3"), (0.4, "0.4")],
         marks=[(0, 0, "E = 0 at centre", "start", 10, -10), (zmax, ring(zmax), "max 0.385 kq/R²", "start", 10, -8)],
         notes=["Zero at the centre (every element is cancelled by the one opposite).",
                "Far away (z ≫ R) the ring looks like a point charge."],
         title="Field on the axis of a charged ring")

    plot("g-dipole-U-tau", (0, 360, -1.25, 1.25),
         [(lambda t: -cos(radians(t)), 0, 360, NET, "U = −pE cosθ", (272, 0.62), None),
          (lambda t: sin(radians(t)), 0, 360, VEC, "τ = pE sinθ (dashed)", (272, 0.36), "7,5")],
         "angle θ between p and E (degrees)", "U and τ (units of pE)",
         [(0, "0"), (90, "90"), (180, "180"), (270, "270"), (360, "360")],
         [(-1, "−1"), (0, "0"), (1, "+1")],
         marks=[(0, -1, "stable: U = −pE", "start", 10, 18), (180, 1, "unstable: U = +pE", "start", 12, 16),
                (90, 1, "τ max", "end", -10, 16)],
         notes=["τ is largest at 90° and zero when aligned (0°) or anti-aligned (180°).",
                "Work by an external agent = U_f − U_i; turning from 0° to 180° costs 2pE."],
         title="Dipole in a uniform field: potential energy and torque")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    build_vectors()
    build_field_lines()
    build_graphs()
    print("\n".join(sorted(f for f in os.listdir(OUT) if f.endswith(".svg"))))
