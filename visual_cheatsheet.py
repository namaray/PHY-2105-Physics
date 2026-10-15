"""Build visual-cheatsheet.html — every finals formula next to a diagram.

Run: python3 visual_cheatsheet.py
The diagrams are inline SVG coloured through CSS variables, so they follow
the site's light/dark theme without any image filters.
"""
from math import hypot, cos, sin, radians, sqrt, atan2, degrees

from quiz4_figures import trace

VAR = {k: f"var(--d-{k})" for k in ("pos", "neg", "vec", "net", "ln", "txt", "mut", "fld", "gold", "pink")}


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class D:
    """A tiny SVG canvas in screen coordinates (y down)."""

    def __init__(s, w=240, h=150, label=""):
        s.w, s.h, s.label, s.p = w, h, label, []

    def _st(s, c, w=None, fill=None, dash=None, op=None):
        st = f"stroke:{VAR[c]}" if c else "stroke:none"
        if w:
            st += f";stroke-width:{w}"
        st += f";fill:{VAR[fill] if fill in VAR else (fill or 'none')}"
        if dash:
            st += f";stroke-dasharray:{dash}"
        if op is not None:
            st += f";opacity:{op}"
        return st

    def line(s, x1, y1, x2, y2, c="ln", w=1.4, dash=None, op=None):
        s.p.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" style="{s._st(c, w, dash=dash, op=op)};stroke-linecap:round"/>')

    def arrow(s, x1, y1, x2, y2, c="vec", w=2.2, head=7.5, dash=None, op=None):
        L = hypot(x2 - x1, y2 - y1)
        if L < 1:
            return
        ux, uy = (x2 - x1) / L, (y2 - y1) / L
        hd = min(head, L * 0.6)
        bx, by = x2 - ux * hd, y2 - uy * hd
        s.line(x1, y1, bx, by, c, w, dash, op)
        pts = f"{x2:.1f},{y2:.1f} {bx - uy * hd * .5:.1f},{by + ux * hd * .5:.1f} {bx + uy * hd * .5:.1f},{by - ux * hd * .5:.1f}"
        s.p.append(f'<polygon points="{pts}" style="fill:{VAR[c]};stroke:none{";opacity:" + str(op) if op is not None else ""}"/>')

    def text(s, x, y, t, c="txt", size=10.5, anchor="middle", bold=False, italic=False, halo=False):
        extra = (";font-weight:600" if bold else "") + (";font-style:italic" if italic else "")
        if halo:
            extra += ";paint-order:stroke;stroke:var(--bg-color);stroke-width:4px;stroke-linejoin:round"
        s.p.append(f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" style="fill:{VAR[c]};font-size:{size}px{extra}">{esc(t)}</text>')

    def charge(s, x, y, q, lab=None, r=10, dy=None, size=10):
        s.p.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" style="fill:{VAR["pos" if q > 0 else "neg"]};stroke:none"/>')
        s.p.append(f'<text x="{x:.1f}" y="{y + r * 0.42:.1f}" text-anchor="middle" style="fill:#fff;font-size:{r * 1.35:.1f}px;font-weight:700">{"+" if q > 0 else "−"}</text>')
        if lab:
            s.text(x, y + (dy if dy is not None else r + 12), lab, "txt", size)

    def circle(s, x, y, r, c="ln", w=1.3, fill=None, dash=None, op=None):
        s.p.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" style="{s._st(c, w, fill, dash, op)}"/>')

    def dot(s, x, y, c="txt", r=3):
        s.circle(x, y, r, None, fill=c)

    def path(s, d, c="ln", w=1.4, fill=None, dash=None, op=None):
        s.p.append(f'<path d="{d}" style="{s._st(c, w, fill, dash, op)};stroke-linejoin:round"/>')

    def poly(s, pts, c="ln", w=1.4, fill=None, dash=None, op=None, close=True):
        d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + (" Z" if close else "")
        s.path(d, c, w, fill, dash, op)

    def rect(s, x, y, w, h, c="ln", fill=None, op=None, rx=0, sw=1.3):
        s.p.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" style="{s._st(c, sw, fill, op=op)}"/>')

    def arc(s, cx, cy, r, a0, a1, c="gold", w=1.3, arrow_end=False):
        """Arc from angle a0 to a1 (degrees, maths convention: counter-clockwise, y up)."""
        p0 = (cx + r * cos(radians(a0)), cy - r * sin(radians(a0)))
        p1 = (cx + r * cos(radians(a1)), cy - r * sin(radians(a1)))
        large = 1 if abs(a1 - a0) > 180 else 0
        sweep = 0 if a1 > a0 else 1
        s.path(f"M{p0[0]:.1f},{p0[1]:.1f} A{r},{r} 0 {large} {sweep} {p1[0]:.1f},{p1[1]:.1f}", c, w)
        if arrow_end:
            sgn = 1 if a1 > a0 else -1
            t = radians(a1)
            tx, ty = -sin(t) * sgn, -cos(t) * sgn          # screen tangent in the direction of travel
            s.arrow(p1[0] - tx * 6, p1[1] - ty * 6, p1[0] + tx * 2, p1[1] + ty * 2, c, w, 7)

    def dim(s, x1, y1, x2, y2, t, c="gold", off=0, size=10.5, tdx=0, tdy=-4):
        """Dimension line with end ticks and a label at the middle."""
        L = hypot(x2 - x1, y2 - y1)
        nx, ny = -(y2 - y1) / L, (x2 - x1) / L
        x1, y1, x2, y2 = x1 + nx * off, y1 + ny * off, x2 + nx * off, y2 + ny * off
        s.line(x1, y1, x2, y2, c, 1.1)
        for x, y in ((x1, y1), (x2, y2)):
            s.line(x - nx * 4, y - ny * 4, x + nx * 4, y + ny * 4, c, 1.1)
        s.text((x1 + x2) / 2 + tdx, (y1 + y2) / 2 + tdy, t, c, size, bold=True)

    def axes(s, x0, y0, x1, y1, xl="", yl=""):
        s.arrow(x0, y0, x1, y0, "ln", 1.3, 6)
        s.arrow(x0, y0, x0, y1, "ln", 1.3, 6)
        if xl:
            s.text(x1, y0 + 13, xl, "mut", 10, "end")
        if yl:
            s.text(x0 + 5, y1 + 4, yl, "mut", 10, "start")

    def field(s, x0, x1, y0, y1, direction="right", n=4, op=0.45):
        """Faint uniform-field arrows filling a box."""
        if direction in ("right", "left"):
            for k in range(n):
                y = y0 + (y1 - y0) * (k + 0.5) / n
                a, b = (x0, x1) if direction == "right" else (x1, x0)
                s.arrow(a, y, b, y, "fld", 1.2, 6, op=op)
        else:
            for k in range(n):
                x = x0 + (x1 - x0) * (k + 0.5) / n
                a, b = (y0, y1) if direction == "down" else (y1, y0)
                s.arrow(x, a, x, b, "fld", 1.2, 6, op=op)

    def curve(s, f, x0, x1, X, Y, c="net", w=2, dash=None, n=120, clip=None):
        pts = []
        for i in range(n + 1):
            x = x0 + (x1 - x0) * i / n
            y = f(x)
            if clip and not (clip[0] <= y <= clip[1]):
                continue
            pts.append((X(x), Y(y)))
        s.poly(pts, c, w, dash=dash, close=False)

    def svg(s):
        return (f'<svg class="dg" viewBox="0 0 {s.w} {s.h}" role="img" aria-label="{esc(s.label)}">'
                + "".join(s.p) + "</svg>")


def unit(x1, y1, x2, y2):
    L = hypot(x2 - x1, y2 - y1)
    return (x2 - x1) / L, (y2 - y1) / L


# =====================================================================  Coulomb
def c_coulomb():
    d = D(label="Like charges repel, unlike attract")
    d.charge(80, 45, 1); d.charge(160, 45, 1)
    d.arrow(68, 45, 34, 45); d.arrow(172, 45, 206, 45)
    d.dim(80, 45, 160, 45, "r", off=-20)
    d.text(120, 74, "like charges → repel", "mut", 10)
    d.charge(80, 108, 1); d.charge(160, 108, -1)
    d.arrow(92, 108, 117, 108); d.arrow(148, 108, 123, 108)
    d.text(120, 138, "unlike charges → attract", "mut", 10)
    return d.svg()


def c_vector():
    d = D(label="Unit vector from source to the charge acted on")
    x1, y1, x2, y2 = 50, 108, 165, 55
    ux, uy = unit(x1, y1, x2, y2)
    d.line(x1, y1, x2, y2, "ln", 1.1, "4,4")
    d.charge(x1, y1, 1, "q₁ (source)")
    d.charge(x2, y2, 1, "q₂", dy=-16)
    d.arrow(x1 + ux * 13, y1 + uy * 13, x1 + ux * 42, y1 + uy * 42, "gold", 2)
    d.text(x1 + ux * 30 + 10, y1 + uy * 30 + 14, "r̂₁₂", "gold", 11, bold=True)
    d.arrow(x2 + ux * 12, y2 + uy * 12, x2 + ux * 58, y2 + uy * 58)
    d.text(x2 + ux * 45 + 4, y2 + uy * 45 + 16, "F₁₂", "vec", 11, bold=True)
    return d.svg()


def c_super():
    d = D(label="Forces add head to tail")
    tx, ty = 110, 115
    f1, f2 = (-60, -38), (78, -22)
    n = (f1[0] + f2[0], f1[1] + f2[1])
    d.line(tx + f1[0], ty + f1[1], tx + n[0], ty + n[1], "mut", 1, "3,3")
    d.line(tx + f2[0], ty + f2[1], tx + n[0], ty + n[1], "mut", 1, "3,3")
    d.arrow(tx, ty, tx + f1[0], ty + f1[1]); d.arrow(tx, ty, tx + f2[0], ty + f2[1])
    d.arrow(tx, ty, tx + n[0], ty + n[1], "net", 2.8, 9)
    d.text(tx + f1[0] - 6, ty + f1[1] - 4, "F₁", "vec", 11, "end", True)
    d.text(tx + f2[0] + 4, ty + f2[1] + 12, "F₂", "vec", 11, "start", True)
    d.text(tx + n[0] + 6, ty + n[1] - 2, "F_net", "net", 11, "start", True)
    d.charge(tx, ty, 1, r=9)
    return d.svg()


def c_components():
    d = D(label="Components and the angle of the resultant")
    ox, oy, fx, fy = 50, 122, 160, 48
    d.axes(ox - 20, oy, 225, 18, "x", "y")
    d.arrow(ox, oy, fx, oy, "pink", 1.6, 7, dash="5,3")
    d.arrow(fx, oy, fx, fy, "pink", 1.6, 7, dash="5,3")
    d.arrow(ox, oy, fx, fy, "net", 2.6, 9)
    d.arc(ox, oy, 28, 0, degrees(atan2(oy - fy, fx - ox)))
    d.text(ox + 34, oy - 7, "θ", "gold", 11, "start", True)
    d.text((ox + fx) / 2, oy + 13, "Fx = F cos θ", "pink", 10)
    d.text(fx + 5, (oy + fy) / 2, "Fy", "pink", 10, "start")
    d.text(92, 72, "F", "net", 12, bold=True)
    return d.svg()


def c_quant():
    d = D(label="Charge comes in whole electrons")
    d.path("M30,75 C30,35 110,30 120,55 C130,30 175,45 160,85 C150,120 60,125 30,75 Z", "ln", 1.4, fill="mut", op=0.18)
    for i, (x, y) in enumerate([(55, 70), (80, 55), (105, 80), (130, 62), (80, 95), (140, 92)]):
        d.charge(x, y, -1, r=7)
    d.text(95, 132, "n = 6 extra electrons", "mut", 10)
    d.arrow(170, 75, 195, 75, "ln", 1.4, 6)
    d.text(215, 72, "q = ne", "txt", 12, bold=True)
    d.text(215, 88, "= 6e", "mut", 10)
    return d.svg()


def c_sample():
    d = D(label="From grams to coulombs")
    boxes = [(10, "mass m"), (62, "moles"), (114, "atoms"), (166, "charge q")]
    for x, t in boxes:
        d.rect(x, 52, 60 if x == 166 else 46, 30, "ln", fill="mut", op=0.12, rx=6)
        d.text(x + (30 if x == 166 else 23), 71, t, "txt", 9.5, bold=True)
    for (x, t) in [(56, "÷ M"), (108, "× N_A"), (160, "× Ze")]:
        d.arrow(x, 67, x + 6, 67, "ln", 1.2, 5)
        d.text(x + 3, 46, t, "gold", 9.5, bold=True)
    d.circle(70, 115, 6, None, fill="pos")
    d.circle(70, 115, 17, "ln", 1, dash="2,2")
    for a in (20, 140, 260):
        d.circle(70 + 17 * cos(radians(a)), 115 - 17 * sin(radians(a)), 3, None, fill="neg")
    d.text(96, 119, "one atom: Z electrons", "mut", 9.5, "start")
    return d.svg()


def c_spheres():
    d = D(label="Use centre-to-centre distance for spheres")
    d.circle(60, 70, 26, "ln", 1.4, fill="pos", op=0.25); d.circle(180, 70, 26, "ln", 1.4, fill="pos", op=0.25)
    d.dot(60, 70); d.dot(180, 70)
    d.dim(86, 70, 154, 70, "r (gap)", off=0, tdy=-6)
    d.line(60, 70, 60 - 26 * cos(radians(50)), 70 - 26 * sin(radians(50)), "txt", 1)
    d.text(36, 58, "R", "txt", 10, bold=True)
    d.dim(60, 112, 180, 112, "r + 2R  (use this)", c="net", tdy=14)
    return d.svg()


def c_gravity():
    d = D(label="Electric force dwarfs gravity")
    d.charge(85, 70, -1, "e"); d.charge(155, 70, -1, "e")
    d.arrow(73, 70, 18, 70, "vec", 3); d.arrow(167, 70, 222, 70, "vec", 3)
    d.text(45, 60, "F_e", "vec", 11, bold=True); d.text(195, 60, "F_e", "vec", 11, bold=True)
    d.arrow(96, 64, 101, 64, "net", 1.4, 4); d.arrow(144, 64, 139, 64, "net", 1.4, 4)
    d.text(120, 52, "F_g (tiny)", "net", 9.5)
    d.text(120, 120, "F_e / F_g ≈ 4×10⁴² — r cancels", "mut", 10)
    return d.svg()


def c_newton():
    d = D(label="Acceleration points along the net force")
    d.rect(70, 55, 46, 40, "ln", fill="mut", op=0.15, rx=6)
    d.text(93, 80, "m", "txt", 13, bold=True)
    d.arrow(118, 68, 190, 68, "vec", 2.6); d.text(196, 72, "F", "vec", 12, "start", True)
    d.arrow(118, 86, 165, 86, "net", 2.2); d.text(171, 90, "a", "net", 12, "start", True)
    d.text(120, 125, "same direction; bigger m → smaller a", "mut", 10)
    return d.svg()


def c_current():
    d = D(label="Charge is the area under the current graph")
    X = lambda t: 34 + t * 36
    Y = lambda i: 120 - i * 26
    pts = [(0, 0), (1, 3), (3, 3), (5, 0)]
    d.poly([(X(0), Y(0))] + [(X(t), Y(i)) for t, i in pts] + [(X(5), Y(0))], None, fill="net", op=0.25)
    d.poly([(X(t), Y(i)) for t, i in pts], "net", 2, close=False)
    d.axes(34, 120, 225, 25, "t", "i")
    d.text(X(2.4), Y(1.3), "Q = ∫ i dt", "txt", 11, bold=True)
    d.text(X(2.4), Y(1.3) + 14, "(area)", "mut", 9.5)
    d.text(X(3.1), 22, "I = dq/dt: rate of charge flow", "gold", 9.5)
    return d.svg()


def c_voltage():
    d = D(label="Voltage is work per unit charge")
    d.rect(36, 30, 8, 90, None, fill="pos"); d.rect(196, 30, 8, 90, None, fill="neg")
    d.text(40, 24, "+ (high V)", "pos", 9.5); d.text(200, 24, "− (low V)", "neg", 9.5)
    d.field(52, 188, 40, 112, "right", 3, 0.3)
    d.charge(150, 75, 1, r=8)
    d.arrow(138, 75, 78, 75, "pink", 2.2)
    d.text(108, 66, "push dq: work dW", "pink", 9.5)
    d.text(120, 140, "V = dW/dq   (J/C = volt)", "txt", 10.5, bold=True)
    return d.svg()


def c_power():
    d = D(label="Energy is the area under the power graph")
    X = lambda t: 34 + t * 36
    Y = lambda p: 120 - p * 26
    f = lambda t: 1.2 + 1.6 * sin(t * 0.9) ** 2
    pts = [(X(t / 10), Y(f(t / 10))) for t in range(0, 51)]
    d.poly([(X(0), Y(0))] + pts + [(X(5), Y(0))], None, fill="gold", op=0.25)
    d.poly(pts, "gold", 2, close=False)
    d.axes(34, 120, 225, 25, "t", "P")
    d.text(X(2.5), Y(0.7), "W = ∫ P dt", "txt", 11, bold=True)
    d.text(X(2.5), 18, "P = VI = dW/dt", "mut", 10)
    return d.svg()


# =====================================================================  Field
def f_def():
    d = D(label="Field is force per unit positive test charge")
    d.charge(45, 75, 1, "source q", r=12)
    d.line(57, 75, 140, 75, "ln", 1, "4,4")
    d.charge(150, 75, 1, "test q₀", r=7)
    d.arrow(158, 75, 210, 75, "vec", 2.4)
    d.text(184, 66, "F", "vec", 11, bold=True)
    d.text(120, 130, "E = F / q₀ — points like the force on +q₀", "mut", 9.5)
    return d.svg()


def f_point():
    d = D(label="Field points away from + and toward −")
    for cx, q in ((65, 1), (175, -1)):
        for k in range(8):
            a = radians(k * 45 + 22.5)
            r0, r1 = (16, 44) if q > 0 else (46, 18)
            d.arrow(cx + r0 * cos(a), 72 - r0 * sin(a), cx + r1 * cos(a), 72 - r1 * sin(a), "fld", 1.6, 6)
        d.charge(cx, 72, q, r=11)
    d.text(65, 136, "away from +", "mut", 10); d.text(175, 136, "toward −", "mut", 10)
    return d.svg()


def f_force():
    d = D(label="Force on a charge in a field")
    d.field(10, 230, 20, 128, "right", 4, 0.3)
    d.text(222, 16, "E →", "fld", 10, "end", True)
    d.charge(90, 50, 1, r=9); d.arrow(100, 50, 150, 50, "vec", 2.6); d.text(156, 54, "F = qE", "vec", 10, "start", True)
    d.charge(140, 105, -1, r=9); d.arrow(130, 105, 80, 105, "vec", 2.6); d.text(74, 109, "F opposite", "vec", 10, "end", True)
    d.text(140, 128, "electron", "mut", 9)
    return d.svg()


def f_super():
    d = D(label="Fields add as vectors at a point")
    P, q1, q2 = (125, 60), (45, 125), (205, 125)
    e1 = unit(*q1, *P)                       # away from +
    e2 = unit(*P, *q2)                       # toward −
    L1, L2 = 46, 40
    v1 = (e1[0] * L1, e1[1] * L1); v2 = (e2[0] * L2, e2[1] * L2); n = (v1[0] + v2[0], v1[1] + v2[1])
    for q in (q1, q2):
        d.line(q[0], q[1], *P, "ln", 1, "4,4")
    d.arrow(*P, P[0] + v1[0], P[1] + v1[1]); d.arrow(*P, P[0] + v2[0], P[1] + v2[1])
    d.arrow(*P, P[0] + n[0], P[1] + n[1], "net", 2.8, 9)
    d.text(P[0] + v1[0] + 4, P[1] + v1[1] - 2, "E₁", "vec", 11, "start", True)
    d.text(P[0] + v2[0] + 2, P[1] + v2[1] + 12, "E₂", "vec", 11, "start", True)
    d.text(P[0] + n[0] + 6, P[1] + n[1] + 4, "E", "net", 12, "start", True)
    d.dot(*P); d.text(P[0] - 8, P[1] - 4, "P", "txt", 11, "end", True)
    d.charge(*q1, 1); d.charge(*q2, -1)
    return d.svg()


def f_angle():
    d = D(label="Two equal vectors at angle phi")
    o, L, phi = (120, 132), 62, 70
    a1, a2 = 90 + phi / 2, 90 - phi / 2
    p1 = (o[0] + L * cos(radians(a1)), o[1] - L * sin(radians(a1)))
    p2 = (o[0] + L * cos(radians(a2)), o[1] - L * sin(radians(a2)))
    R = 2 * L * cos(radians(phi / 2))
    d.line(*p1, o[0], o[1] - R, "mut", 1, "3,3"); d.line(*p2, o[0], o[1] - R, "mut", 1, "3,3")
    d.arrow(*o, *p1); d.arrow(*o, *p2)
    d.arrow(*o, o[0], o[1] - R, "net", 2.8, 9)
    d.arc(*o, 24, a2, a1)
    d.text(o[0] + 13, o[1] - 28, "φ", "gold", 11, bold=True)
    d.text(p1[0] - 6, p1[1] + 2, "E", "vec", 11, "end", True); d.text(p2[0] + 6, p2[1] + 2, "E", "vec", 11, "start", True)
    d.text(o[0] + 8, o[1] - R + 6, "2E cos(φ/2)", "net", 10.5, "start", True)
    return d.svg()


def f_null():
    d = D(label="Null point sits nearer the smaller charge")
    x1, x2 = 35, 205
    xn = x1 + (x2 - x1) * 2 / 3
    d.line(x1, 72, x2, 72, "ln", 1)
    d.charge(x1, 72, 1, "4q", r=13); d.charge(x2, 72, 1, "q", r=8)
    d.dot(xn, 72, "net", 4)
    d.text(xn, 60, "E = 0", "net", 10.5, bold=True)
    d.arrow(xn, 88, xn + 24, 88, "vec", 1.6, 6); d.arrow(xn, 88, xn - 24, 88, "vec", 1.6, 6)
    d.dim(x1, 72, xn, 72, "x", off=-40)
    d.dim(xn, 72, x2, 72, "d − x", off=-40)
    d.text(120, 128, "like charges: between them, near the smaller", "mut", 9.5)
    return d.svg()


def f_accel():
    d = D(label="Charge between plates follows a parabola")
    d.rect(40, 20, 150, 6, None, fill="pos"); d.rect(40, 124, 150, 6, None, fill="neg")
    d.field(48, 182, 30, 120, "down", 5, 0.3)
    k = 0.00156                                     # 35 px of deflection over the 150 px plates
    pts = [(40 + t, 75 - k * t * t) for t in range(0, 151, 5)]
    d.poly([(20, 75)] + pts, "net", 2.2, close=False)
    x, y = pts[-1]
    d.line(x, y, x + 40, y - 2 * k * 150 * 40, "net", 2.2, "4,3")
    d.charge(20, 75, -1, r=7)
    d.arrow(100, 100, 100, 77, "pink", 2, 7); d.text(105, 92, "F (toward + plate)", "pink", 9.5, "start")
    d.text(115, 145, "a = |q|E/m  (electron → toward + plate)", "mut", 9)
    return d.svg()


def f_line():
    d = D(label="Element of a line charge")
    d.line(20, 118, 220, 118, "pos", 4, op=0.5)
    d.line(70, 118, 92, 118, "pos", 6)
    d.text(81, 136, "ds  (dq = λ ds)", "pos", 10, bold=True)
    P = (160, 40)
    d.line(81, 118, *P, "ln", 1, "4,4")
    d.text(115, 74, "r", "gold", 11, bold=True)
    u = unit(81, 118, *P)
    d.arrow(*P, P[0] + u[0] * 40, P[1] + u[1] * 40)
    d.text(P[0] + u[0] * 40 + 6, P[1] + u[1] * 40 + 4, "dE", "vec", 10.5, "start", True)
    d.dot(*P); d.text(P[0] - 8, P[1] + 2, "P", "txt", 11, "end", True)
    return d.svg()


def f_ring():
    d = D(label="Ring: sideways parts cancel on the axis")
    c, P = (55, 75), (180, 75)
    d.p.append(f'<ellipse cx="{c[0]}" cy="{c[1]}" rx="12" ry="45" style="stroke:{VAR["pos"]};stroke-width:3;fill:none"/>')
    d.line(c[0], c[1], 230, c[1], "ln", 1, "4,4")
    top, bot = (c[0], c[1] - 45), (c[0], c[1] + 45)
    for e in (top, bot):
        d.line(*e, *P, "mut", 1, "3,3")
        u = unit(*e, *P)
        d.arrow(*P, P[0] + u[0] * 36, P[1] + u[1] * 36, "vec", 1.8, 6)
    d.arrow(*P, P[0] + 46, P[1], "net", 2.8, 9)
    d.text(P[0] + 48, P[1] - 6, "E", "net", 11, "start", True)
    d.dim(c[0], c[1], P[0], P[1], "z", off=-58)
    d.dim(c[0], c[1], c[0], c[1] - 45, "R", c="txt", tdx=-24, tdy=4)
    d.dot(*P)
    return d.svg()


def f_dipole_p():
    d = D(label="Dipole moment points from minus to plus")
    d.charge(65, 85, -1, "−q", r=11); d.charge(175, 85, 1, "+q", r=11)
    d.line(76, 85, 164, 85, "ln", 1.2)
    d.arrow(85, 50, 155, 50, "net", 2.8, 9)
    d.text(120, 42, "p = qd  (− → +)", "net", 11, bold=True)
    d.dim(65, 85, 175, 85, "d", off=30, tdy=14)
    return d.svg()


def f_dipole_E():
    d = D(label="On the axis E points along p")
    d.charge(45, 75, -1, r=8); d.charge(75, 75, 1, r=8)
    d.arrow(48, 52, 72, 52, "net", 1.8, 6); d.text(60, 46, "p", "net", 10, bold=True)
    d.line(83, 75, 230, 75, "ln", 1, "4,4")
    d.dot(185, 75)
    d.arrow(185, 75, 225, 75, "vec", 2.6); d.text(205, 66, "E", "vec", 11, bold=True)
    d.dim(60, 75, 185, 75, "z", off=-38, tdy=14)
    d.text(120, 128, "E = 2kp/z³ — falls off as 1/z³", "mut", 10)
    return d.svg()


def f_torque():
    d = D(label="Torque turns the dipole toward the field")
    d.field(10, 230, 20, 132, "right", 4, 0.25)
    c, th, L = (120, 78), 40, 48
    px, py = c[0] + L * cos(radians(th)), c[1] - L * sin(radians(th))
    nx, ny = c[0] - L * cos(radians(th)), c[1] + L * sin(radians(th))
    d.line(nx, ny, px, py, "ln", 3)
    d.arrow(px + 9, py, px + 40, py, "vec", 2.2); d.text(px + 42, py + 4, "qE", "vec", 10, "start", True)
    d.arrow(nx - 9, ny, nx - 40, ny, "vec", 2.2); d.text(nx - 42, ny + 4, "qE", "vec", 10, "end", True)
    d.line(c[0], c[1], c[0] + 60, c[1], "mut", 1, "3,3")
    d.arc(*c, 26, 0, th); d.text(c[0] + 30, c[1] - 8, "θ", "gold", 11, "start", True)
    d.arc(*c, 18, th + 30, th - 40, "pink", 1.8, arrow_end=True)
    d.text(c[0] - 4, c[1] - 26, "τ", "pink", 12, "end", True)
    d.charge(nx, ny, -1, r=8); d.charge(px, py, 1, r=8)
    d.text(120, 146, "net force 0, torque pE sin θ", "mut", 9.5)
    return d.svg()


def f_U():
    d = D(label="Dipole potential energy against angle")
    X = lambda t: 34 + t / 180 * 185
    Y = lambda u: 70 - u * 40
    d.line(34, 70, 222, 70, "ln", 1, "3,3")
    d.axes(34, 132, 228, 18, "θ", "U")
    d.curve(lambda t: -cos(radians(t)), 0, 180, X, Y, "net", 2.2)
    d.dot(X(0), Y(-1), "net", 4); d.dot(X(180), Y(1), "pink", 4)
    d.text(X(0) + 6, Y(-1) + 14, "0°: −pE (stable)", "net", 9.5, "start")
    d.text(X(180) - 4, Y(1) - 8, "180°: +pE (unstable)", "pink", 9.5, "end")
    d.text(X(90) + 10, 84, "90°: U = 0", "mut", 9, "start")
    return d.svg()


def f_work():
    d = D(label="Work by the agent is the rise in U")
    X = lambda t: 34 + t / 180 * 185
    Y = lambda u: 75 - u * 45
    d.axes(34, 132, 228, 18, "θ", "U")
    d.curve(lambda t: -cos(radians(t)), 0, 180, X, Y, "mut", 1.6)
    t0, t1 = 20, 120
    d.dot(X(t0), Y(-cos(radians(t0))), "vec", 4); d.dot(X(t1), Y(-cos(radians(t1))), "vec", 4)
    d.line(X(t0), Y(-cos(radians(t0))), X(t1) + 8, Y(-cos(radians(t0))), "ln", 1, "3,3")
    d.arrow(X(t1) + 8, Y(-cos(radians(t0))), X(t1) + 8, Y(-cos(radians(t1))), "pink", 2.2)
    d.text(X(t1) + 12, 78, "W_agent", "pink", 10, "start", True)
    d.text(X(t1) + 12, 91, "= U_f − U_i", "pink", 10, "start")
    d.text(X(t0), Y(-cos(radians(t0))) + 15, "θ_i", "vec", 10, bold=True)
    d.text(X(t1) - 4, Y(-cos(radians(t1))) - 8, "θ_f", "vec", 10, "end", True)
    return d.svg()


def f_cross():
    d = D(label="Cross product is perpendicular to both vectors")
    o = (95, 105)
    d.path(f"M{o[0] - 40},{o[1] + 20} L{o[0] + 70},{o[1] + 20} L{o[0] + 110},{o[1] - 15} L{o[0]},{o[1] - 15} Z", "mut", 1, fill="mut", op=0.12)
    d.arrow(*o, o[0] + 85, o[1] + 5, "vec", 2.4); d.text(o[0] + 88, o[1] + 14, "a", "vec", 11, "start", True)
    d.arrow(*o, o[0] + 30, o[1] - 22, "net", 2.4); d.text(o[0] + 34, o[1] - 24, "b", "net", 11, "start", True)
    d.arrow(*o, o[0], o[1] - 82, "pink", 2.6); d.text(o[0] + 6, o[1] - 76, "a × b", "pink", 11, "start", True)
    d.text(120, 144, "⊥ to both · size ab sin θ · right-hand rule", "mut", 9)
    return d.svg()


def f_lines():
    d = D(label="Field lines of a dipole")
    box = (-1.6, 1.6, -1.0, 1.0)
    ch = [(1, (-0.55, 0)), (-1, (0.55, 0))]
    X = lambda x: 120 + x * 68
    Y = lambda y: 72 - y * 68
    for k in range(12):
        a = 2 * 3.14159 * (k + 0.5) / 12
        pts = trace(ch, (-0.55 + 0.08 * cos(a), 0.08 * sin(a)), 1, box, h=0.03)
        pts = [(X(x), Y(y)) for x, y in pts if -1.8 < x < 1.8 and -1.2 < y < 1.2]
        if len(pts) > 1:
            d.poly(pts, "fld", 1.2, close=False)
            m = pts[len(pts) // 2], pts[len(pts) // 2 + 1]
            d.arrow(*m[0], *m[1], "fld", 1, 6)
    d.charge(X(-0.55), Y(0), 1, r=9); d.charge(X(0.55), Y(0), -1, r=9)
    d.text(120, 146, "start on +, end on −, never cross", "mut", 9.5, halo=True)
    return d.svg()


# =====================================================================  Potential
def p_dU():
    d = D(label="Field does positive work so U falls")
    d.rect(20, 18, 110, 5, None, fill="pos"); d.rect(20, 127, 110, 5, None, fill="neg")
    d.field(26, 124, 26, 122, "down", 3, 0.3)
    d.charge(75, 40, 1, r=8); d.arrow(75, 50, 75, 105, "pink", 2.2); d.charge(75, 112, 1, r=8)
    d.text(84, 80, "field does +W", "pink", 9.5, "start")
    for x, h, t in ((165, 80, "U_i"), (205, 30, "U_f")):
        d.rect(x - 12, 120 - h, 24, h, None, fill="gold", op=0.8)
        d.text(x, 134, t, "txt", 10)
    d.text(185, 26, "ΔU = −W", "txt", 11, bold=True)
    return d.svg()


def p_V():
    d = D(label="Potential belongs to the point, not the test charge")
    d.charge(35, 80, 1, "Q", r=12)
    d.line(47, 80, 120, 80, "ln", 1, "4,4")
    d.dot(125, 80, "txt", 4); d.text(125, 68, "P", "txt", 11, bold=True)
    d.text(145, 52, "put q here → U", "txt", 10, "start")
    d.text(145, 72, "put 2q here → 2U", "txt", 10, "start")
    d.text(145, 100, "V = U/q", "net", 12, "start", True)
    d.text(145, 116, "same either way", "mut", 9.5, "start")
    return d.svg()


def p_dV():
    d = D(label="Moving along the field lowers V")
    for x, t in ((60, "V_i (high)"), (180, "V_f (low)")):
        d.line(x, 20, x, 120, "gold", 1.4, "5,4"); d.text(x, 136, t, "gold", 10, bold=True)
    d.field(20, 225, 30, 112, "right", 3, 0.3)
    d.charge(60, 70, 1, r=8); d.arrow(70, 70, 168, 70, "pink", 2.2); d.charge(180, 70, 1, r=8)
    d.text(120, 62, "W by field", "pink", 9.5)
    d.text(120, 14, "ΔV = ΔU/q = −W/q", "txt", 10.5, bold=True)
    return d.svg()


def p_Wext():
    d = D(label="Work to bring a charge in from infinity")
    d.charge(40, 80, 1, "Q", r=12)
    d.dot(110, 80, "txt", 4); d.text(110, 68, "P (potential V)", "txt", 9.5)
    d.path("M225,40 C200,45 160,110 118,84", "pink", 1.6, dash="5,4")
    d.arrow(130, 90, 118, 84, "pink", 1.6, 7)
    d.text(220, 32, "from ∞", "pink", 10, "end", True)
    d.charge(222, 42, 1, r=6)
    d.text(165, 125, "W_ext = qV (any path)", "txt", 10.5, bold=True)
    return d.svg()


def p_int():
    d = D(label="Potential difference is minus the line integral of E")
    d.field(10, 230, 18, 130, "right", 4, 0.25)
    pts = [(30 + 18 * k, 112 - 60 * sin(k / 9 * 3.1416) ** 1 * 1.0) for k in range(10)]
    d.poly(pts, "pink", 1.8, close=False)
    for a, b in zip(pts[1:8:3], pts[2:9:3]):
        d.arrow(*a, *b, "pink", 2, 6)
    d.text(pts[0][0] - 4, pts[0][1] + 12, "i", "txt", 11, bold=True)
    d.text(pts[-1][0] + 4, pts[-1][1] + 12, "f", "txt", 11, bold=True)
    d.text(170, 70, "ds", "pink", 10.5, "start", True)
    d.text(220, 14, "E →", "fld", 10, "end", True)
    d.text(175, 140, "add up E · ds along the path", "mut", 9.5)
    return d.svg()


def p_Ed():
    d = D(label="Uniform field: V falls linearly")
    d.rect(30, 18, 120, 6, None, fill="pos"); d.rect(30, 124, 120, 6, None, fill="neg")
    d.field(38, 142, 28, 120, "down", 4, 0.3)
    for k in range(1, 4):
        y = 21 + k * 106 / 4
        d.line(30, y, 150, y, "gold", 1.1, "5,4")
    d.text(155, 25, "V (high)", "pos", 10, "start", True)
    d.text(155, 130, "V − Ed", "neg", 10, "start", True)
    d.dim(205, 21, 205, 127, "d", c="txt", tdx=10, tdy=4)
    d.text(90, 145, "E points to lower V", "mut", 9.5)
    return d.svg()


def p_point():
    d = D(label="Potential of a point charge falls as 1 over r")
    X = lambda r: 30 + r * 48
    Y = lambda v: 75 - v * 30
    d.line(30, 75, 228, 75, "ln", 1.2)
    d.arrow(30, 140, 30, 12, "ln", 1.2, 6)
    d.text(226, 88, "r", "mut", 10, "end"); d.text(36, 16, "V", "mut", 10, "start")
    d.curve(lambda r: 1 / r, 0.5, 4, X, Y, "pos", 2.2)
    d.curve(lambda r: -1 / r, 0.5, 4, X, Y, "neg", 2.2, dash="5,4")
    d.text(X(1.6), Y(1 / 1.6) - 6, "+q: V > 0", "pos", 10, "start", True)
    d.text(X(1.6), Y(-1 / 1.6) + 14, "−q: V < 0", "neg", 10, "start", True)
    return d.svg()


def p_group():
    d = D(label="Potentials add as plain numbers")
    P = (120, 70)
    qs = [((40, 30), 1, "+V₁"), ((205, 45), -1, "−V₂"), ((70, 130), 1, "+V₃")]
    for (x, y), q, t in qs:
        d.line(x, y, *P, "ln", 1, "4,4")
        d.charge(x, y, q, r=9)
        d.text((x + P[0]) / 2 + 6, (y + P[1]) / 2 - 4, t, "pos" if q > 0 else "neg", 10, "start", True)
    d.dot(*P, "txt", 4); d.text(P[0] + 8, P[1] + 16, "V = V₁ − V₂ + V₃", "txt", 10, "start", True)
    d.text(165, 140, "no arrows, no angles", "mut", 9.5)
    return d.svg()


def p_equal():
    d = D(label="Equal distances: add the charges first")
    c, a = (100, 75), 54
    pts = [(c[0] - a, c[1] - a), (c[0] + a, c[1] - a), (c[0] + a, c[1] + a), (c[0] - a, c[1] + a)]
    d.poly(pts, "mut", 1.2)
    for (x, y), q in zip(pts, (2, 4, 2, -2)):
        d.line(x, y, *c, "ln", 1, "4,4")
        d.charge(x, y, q, r=9)
    d.dot(*c, "txt", 4)
    d.text(c[0] + 10, c[1] - 30, "r", "gold", 11, bold=True)
    d.text(168, 60, "all r = a/√2", "gold", 10, "start", True)
    d.text(168, 80, "V = kΣq / r", "txt", 10.5, "start", True)
    return d.svg()


def p_Er():
    d = D(label="For a point charge V equals E times r")
    d.charge(45, 80, 1, "q", r=11)
    d.dim(45, 80, 165, 80, "r", off=-28)
    d.dot(165, 80, "txt", 4)
    d.arrow(165, 80, 210, 80, "net", 2.4); d.text(205, 72, "E = kq/r²", "net", 9.5, "end")
    d.text(165, 105, "V = kq/r", "gold", 10.5, bold=True)
    d.text(120, 135, "divide: V = E·r", "txt", 11, bold=True)
    return d.svg()


def p_dipole():
    d = D(label="Dipole potential depends on angle")
    c = (75, 85)
    d.charge(c[0] - 18, c[1], -1, r=8); d.charge(c[0] + 18, c[1], 1, r=8)
    d.line(c[0], 20, c[0], 140, "gold", 1.2, "5,4"); d.text(c[0] - 4, 18, "V = 0", "gold", 9.5, "end", True)
    th, r = 35, 120
    P = (c[0] + r * cos(radians(th)), c[1] - r * sin(radians(th)))
    d.line(*c, *P, "ln", 1, "4,4"); d.line(*c, c[0] + 140, c[1], "mut", 1, "3,3")
    d.arc(*c, 34, 0, th); d.text(c[0] + 40, c[1] - 10, "θ", "gold", 11, "start", True)
    d.dot(*P, "txt", 4); d.text(P[0] - 6, P[1] - 6, "P", "txt", 11, "end", True)
    d.text(c[0] + 62, c[1] - 52, "r", "txt", 10.5, bold=True)
    d.text(160, 130, "V = kp cos θ / r²", "txt", 10.5, bold=True)
    return d.svg()


def p_cont():
    d = D(label="Continuous charge: add k dq over r")
    c, R = (120, 80), 55
    d.arc(*c, R, 20, 160, "pos", 4)
    a = radians(120)
    e = (c[0] + R * cos(a), c[1] - R * sin(a))
    d.circle(*e, 5, None, fill="pos")
    d.text(e[0] - 10, e[1] - 6, "dq", "pos", 10.5, "end", True)
    d.line(*e, *c, "ln", 1, "4,4"); d.text((e[0] + c[0]) / 2 - 8, (e[1] + c[1]) / 2 + 4, "r", "gold", 11, "end", True)
    d.dot(*c, "txt", 4); d.text(c[0], c[1] + 16, "P", "txt", 11, bold=True)
    d.text(120, 140, "every dq at the same r → V = kQ/r", "mut", 9.5)
    return d.svg()


def p_grad():
    d = D(label="E points down the potential slope")
    X = lambda s: 30 + s * 45
    Y = lambda v: 120 - v * 26
    f = lambda s: 3.4 - 0.18 * s * s
    d.axes(30, 120, 228, 15, "s", "V")
    d.curve(f, 0, 4, X, Y, "gold", 2.2)
    s0 = 2.4
    m = -0.36 * s0
    d.line(X(s0 - 1), Y(f(s0) - m), X(s0 + 1), Y(f(s0) + m), "pink", 1.6, "5,3")
    d.dot(X(s0), Y(f(s0)), "pink", 4)
    d.text(X(s0) + 8, Y(f(s0)) - 12, "slope dV/ds", "pink", 10, "start", True)
    d.arrow(X(s0), Y(f(s0)) + 22, X(s0) + 48, Y(f(s0)) + 22, "net", 2.4)
    d.text(X(s0) + 52, Y(f(s0)) + 26, "E", "net", 11, "start", True)
    d.text(110, 145, "E_s = −dV/ds: E points where V falls", "mut", 9)
    return d.svg()


def p_pair():
    d = D(label="Pair energy against separation")
    X = lambda r: 30 + r * 48
    Y = lambda u: 75 - u * 30
    d.line(30, 75, 228, 75, "ln", 1.2); d.arrow(30, 140, 30, 12, "ln", 1.2, 6)
    d.text(226, 88, "r", "mut", 10, "end"); d.text(36, 16, "U", "mut", 10, "start")
    d.curve(lambda r: 1 / r, 0.5, 4, X, Y, "pink", 2.2)
    d.curve(lambda r: -1 / r, 0.5, 4, X, Y, "net", 2.2)
    d.text(X(1.5), Y(1 / 1.5) - 6, "like: U > 0", "pink", 10, "start", True)
    d.text(X(1.5), Y(-1 / 1.5) + 14, "unlike: U < 0", "net", 10, "start", True)
    return d.svg()


def p_system():
    d = D(label="System energy: one term per pair")
    A, B, C = (40, 125), (200, 125), (120, 25)
    for (p, q, t, dx, dy) in ((A, B, "q₁q₂/r₁₂", 0, 16), (A, C, "q₁q₃/r₁₃", -34, 0), (B, C, "q₂q₃/r₂₃", 36, 0)):
        d.line(*p, *q, "gold", 1.6)
        d.text((p[0] + q[0]) / 2 + dx, (p[1] + q[1]) / 2 + dy, t, "gold", 9.5, bold=True)
    d.charge(*A, 1, r=10); d.charge(*B, -1, r=10); d.charge(*C, 1, r=10)
    d.text(A[0], A[1] - 16, "q₁", "txt", 10); d.text(B[0], B[1] - 16, "q₂", "txt", 10); d.text(C[0] + 16, C[1] + 4, "q₃", "txt", 10, "start")
    d.text(120, 98, "3 charges → 3 pairs", "mut", 9.5)
    return d.svg()


def p_closest():
    d = D(label="Kinetic energy turns into potential energy")
    d.charge(30, 60, 1, r=8); d.arrow(40, 60, 75, 60, "vec", 2.2); d.text(57, 52, "v", "vec", 10, bold=True)
    d.charge(205, 60, 1, "nucleus", r=12, dy=-18)
    d.path("M40,72 L150,72", "pink", 1, dash="2,3")
    d.charge(150, 60, 1, r=8); d.text(150, 42, "stops", "pink", 9.5, bold=True)
    d.dim(150, 60, 205, 60, "r_min", off=28, tdy=14)
    for x, h, t, c in ((70, 34, "K", "vec"), (100, 4, "U", "pink")):
        d.rect(x - 9, 140 - h, 18, h, None, fill=c, op=0.85)
    d.arrow(115, 120, 140, 120, "ln", 1.2, 5)
    for x, h, t, c in ((160, 2, "K", "vec"), (190, 36, "U", "pink")):
        d.rect(x - 9, 140 - h, 18, h, None, fill=c, op=0.85)
    d.text(85, 150, "far: K", "mut", 9); d.text(175, 150, "closest: all U", "mut", 9)
    return d.svg()


def p_eV():
    d = D(label="Electron-volt")
    d.rect(40, 25, 6, 100, None, fill="pos"); d.rect(190, 25, 6, 100, None, fill="neg")
    d.text(43, 18, "1 V", "pos", 10, bold=True); d.text(193, 18, "0 V", "neg", 10, bold=True)
    d.charge(175, 75, -1, "e", r=8)
    d.arrow(164, 75, 62, 75, "net", 2.4)
    d.text(115, 66, "gains energy", "net", 10, bold=True)
    d.text(118, 142, "e × 1 V = 1 eV = 1.6×10⁻¹⁹ J", "txt", 10, bold=True)
    return d.svg()


def p_cons():
    d = D(label="Total energy stays the same")
    base = 118
    for x0, K, U, t in ((40, 20, 60, "before"), (140, 55, 25, "after")):
        d.rect(x0, base - K, 24, K, None, fill="vec", op=0.85); d.text(x0 + 12, base + 12, "K", "txt", 10)
        d.rect(x0 + 30, base - U, 24, U, None, fill="pink", op=0.85); d.text(x0 + 42, base + 12, "U", "txt", 10)
        d.text(x0 + 27, 146, t, "mut", 9.5)
        d.line(x0 - 4, base - 80, x0 + 58, base - 80, "net", 1.4, "4,3")
    d.text(120, 30, "K + U = same total", "net", 10.5, bold=True)
    return d.svg()


def p_equip():
    d = D(label="Equipotentials are perpendicular to field lines")
    c = (120, 75)
    for r in (22, 38, 58):
        d.circle(*c, r, "gold", 1.4, dash="5,4")
    for k in range(8):
        a = radians(k * 45 + 22.5)
        d.arrow(c[0] + 12 * cos(a), c[1] - 12 * sin(a), c[0] + 70 * cos(a), c[1] - 70 * sin(a), "fld", 1.4, 6)
    d.charge(*c, 1, r=10)
    d.text(200, 140, "⊥ everywhere", "mut", 9.5)
    return d.svg()


# =====================================================================  Geometry
def g_square():
    d = D(label="Square: corner to centre")
    c, a = (90, 75), 55
    d.poly([(c[0] - a, c[1] - a), (c[0] + a, c[1] - a), (c[0] + a, c[1] + a), (c[0] - a, c[1] + a)], "ln", 1.4)
    d.line(c[0] - a, c[1] - a, c[0] + a, c[1] + a, "mut", 1, "4,4"); d.line(c[0] + a, c[1] - a, c[0] - a, c[1] + a, "mut", 1, "4,4")
    d.dim(c[0] - a, c[1] - a, *c, "a/√2", c="gold", off=-12, tdx=14, tdy=-6)
    d.dim(c[0] - a, c[1] + a, c[0] + a, c[1] + a, "a", c="txt", tdy=14)
    d.text(178, 70, "diagonal a√2", "mut", 10, "start")
    return d.svg()


def g_rect():
    d = D(label="Rectangle 2a by a: corner to centre")
    c = (110, 75)
    d.poly([(30, 35), (190, 35), (190, 115), (30, 115)], "ln", 1.4)
    d.line(30, 35, *c, "gold", 1.4, "4,3"); d.line(110, 35, *c, "net", 1.4, "4,3")
    d.dot(*c)
    d.text(86, 50, "(√5/2)a", "gold", 10, bold=True)
    d.text(116, 56, "a/2", "net", 10, "start", True)
    d.dim(30, 115, 190, 115, "2a", c="txt", tdy=14)
    d.dim(190, 35, 190, 115, "a", c="txt", tdx=10, tdy=4)
    return d.svg()


def g_equil():
    d = D(label="Equilateral triangle")
    A, B = (50, 128), (190, 128)
    C = (120, 128 - 140 * sqrt(3) / 2)
    G = (120, 128 - 140 * sqrt(3) / 6)
    d.poly([A, B, C], "ln", 1.4)
    d.line(*C, 120, 128, "gold", 1.2, "4,3"); d.text(126, 80, "h = (√3/2)a", "gold", 9.5, "start", True)
    d.line(*A, *G, "net", 1.2, "4,3"); d.dot(*G, "net")
    d.text(76, 104, "a/√3", "net", 9.5, bold=True)
    d.dim(*A, *B, "a", c="txt", tdy=14)
    return d.svg()


def g_right():
    d = D(label="Isosceles right triangle")
    A, B, C = (50, 125), (160, 125), (50, 15)
    M = ((B[0] + C[0]) / 2, (B[1] + C[1]) / 2)
    d.poly([A, B, C], "ln", 1.4)
    d.poly([(50, 115), (60, 115), (60, 125)], "ln", 1, close=False)
    d.text(112, 64, "a√2", "gold", 10.5, "start", True)
    d.dot(*M, "net"); d.line(*A, *M, "net", 1.2, "4,3")
    d.text(M[0] - 8, M[1] - 2, "M", "net", 10, "end", True)
    d.text(150, 95, "M is a/√2 from", "net", 9.5, "start", True)
    d.text(150, 108, "all 3 corners", "net", 9.5, "start", True)
    d.text(105, 140, "a", "txt", 10.5, bold=True); d.text(38, 72, "a", "txt", 10.5, bold=True)
    return d.svg()


def g_bisector():
    d = D(label="Point on the perpendicular bisector")
    q1, q2, P = (40, 120), (200, 120), (120, 40)
    d.line(*q1, *q2, "ln", 1); d.line(120, 120, *P, "mut", 1, "4,4")
    d.line(*q1, *P, "gold", 1.4); d.line(*q2, *P, "gold", 1.4)
    d.charge(*q1, 1, r=8); d.charge(*q2, -1, r=8); d.dot(*P)
    d.text(66, 72, "r = √(d² + y²)", "gold", 9.5, "end", True)
    d.text(126, 85, "y", "txt", 10.5, "start", True)
    d.text(80, 135, "d", "txt", 10.5, bold=True); d.text(160, 135, "d", "txt", 10.5, bold=True)
    d.arc(*q1, 26, 0, degrees(atan2(80, 80)))
    d.text(70, 113, "θ", "gold", 10.5, bold=True)
    d.text(160, 30, "cos θ = d/r", "mut", 9.5, "start"); d.text(160, 44, "sin θ = y/r", "mut", 9.5, "start")
    return d.svg()


def g_triangles():
    d = D(label="Handy right triangles")
    for (x0, a, b, la, lb, lc) in ((25, 72, 54, "4", "3", "5"), (140, 40, 80, "1", "2", "√5")):
        A, B, C = (x0, 125), (x0 + a, 125), (x0, 125 - b)
        d.poly([A, B, C], "ln", 1.4)
        d.text(x0 + a / 2, 140, la, "txt", 11, bold=True)
        d.text(x0 - 8, 125 - b / 2 + 4, lb, "txt", 11, "end", True)
        d.text(x0 + a / 2 + 8, 125 - b / 2 - 4, lc, "gold", 11, "start", True)
    return d.svg()


# =====================================================================  page
SECTIONS = [
    ("c1", "1. Charge & Coulomb's Law", "coulombs-law.html", [
        ("Coulomb's law", r"F = \frac{k|q_1q_2|}{r^2}", c_coulomb, "Size from the formula; direction from the signs."),
        ("Vector form", r"\vec F_{12} = \frac{kq_1q_2}{r^2}\,\hat r_{12}", c_vector, "r̂ points from the source to the charge acted on."),
        ("Superposition", r"\vec F_{net} = \vec F_1 + \vec F_2 + \cdots", c_super, "Add forces as vectors — tip to tail."),
        ("Components & resultant", r"F = \sqrt{F_x^2+F_y^2},\ \ \theta = \tan^{-1}\frac{F_y}{F_x}", c_components, "Check the quadrant from the signs of Fx, Fy."),
        ("Quantization", r"q = ne", c_quant, "Charge comes in whole multiples of e."),
        ("Charge in a sample", r"q = \frac{m}{M}N_A\,Z\,e", c_sample, "Grams → moles → atoms → electrons → coulombs."),
        ("Charged spheres", r"F = \frac{kq_1q_2}{(r+2R)^2}", c_spheres, "If r is the gap, add both radii."),
        ("Electric vs gravity", r"\frac{F_e}{F_g} = \frac{kq_1q_2}{Gm_1m_2}", c_gravity, "The r² cancels — the ratio is distance-free."),
        ("Newton's 2nd law", r"a = \frac{F}{m}", c_newton, "\"Acceleration as they separate\"."),
        ("Current", r"I = \frac{dq}{dt},\quad Q = \int i\,dt", c_current, "Charge = area under the i–t graph."),
        ("Voltage", r"V = \frac{dW}{dq}", c_voltage, "Energy per coulomb."),
        ("Power", r"P = VI = \frac{dW}{dt},\quad W = \int P\,dt", c_power, "Energy = area under the P–t graph."),
    ]),
    ("c2", "2. Electric Field", "electric-fields.html", [
        ("Definition", r"\vec E = \frac{\vec F}{q_0}", f_def, "N/C. Direction = force on a positive test charge."),
        ("Point charge", r"E = \frac{k|q|}{r^2}", f_point, "Away from +, toward −."),
        ("Force from a field", r"\vec F = q\vec E", f_force, "Negative charges feel a force opposite to E."),
        ("Superposition", r"\vec E = \sum \vec E_i", f_super, "Each field from its own charge, then vector-add."),
        ("Two equal fields at angle φ", r"E_{net} = 2E\cos\frac{\varphi}{2}", f_angle, "60° → √3E, 90° → √2E, 120° → E."),
        ("Null point", r"\frac{q_1}{x^2} = \frac{q_2}{(d-x)^2}", f_null, "Square-root both sides; no quadratic."),
        ("Charge in a uniform field", r"a = \frac{|q|E}{m}", f_accel, "Constant sideways force → parabola."),
        ("Line-charge element", r"dq = \lambda\,ds,\quad dE = \frac{k\,dq}{r^2}", f_line, "Treat each element as a point charge."),
        ("Charged ring (axis)", r"E = \frac{kqz}{(z^2+R^2)^{3/2}}", f_ring, "Zero at the centre; → kq/z² far away."),
        ("Dipole moment", r"p = qd", f_dipole_p, "Points from − to +. Unit C·m."),
        ("Dipole field (axis, far)", r"E = \frac{1}{2\pi\varepsilon_0}\frac{p}{z^3} = \frac{2kp}{z^3}", f_dipole_E, "Bisector: kp/r³, opposite to p."),
        ("Torque on a dipole", r"\tau = pE\sin\theta,\quad \vec\tau = \vec p\times\vec E", f_torque, "Max pE at 90°, zero at 0° and 180°."),
        ("Dipole potential energy", r"U = -pE\cos\theta = -\vec p\cdot\vec E", f_U, "Lowest when aligned (stable)."),
        ("Work rotating a dipole", r"W_{agent} = U_f - U_i = -W_{field}", f_work, "0°→180° costs 2pE."),
        ("Cross product", r"\vec a\times\vec b = \begin{vmatrix}\hat i&\hat j&\hat k\\a_x&a_y&a_z\\b_x&b_y&b_z\end{vmatrix}", f_cross, "Don't drop the minus on the ĵ term."),
        ("Field-line rules", r"\text{line density} \propto E", f_lines, "Tangent = direction of E; lines never cross."),
    ]),
    ("c3", "3. Electric Potential", "electric-potential.html", [
    ("Potential energy change", r"\Delta U = U_f - U_i = -W", p_dU, "Field does + work → U falls."),
    ("Potential", r"V = \frac{U}{q}", p_V, "Volt = J/C. A property of the point."),
    ("Potential difference", r"\Delta V = \frac{\Delta U}{q} = -\frac{W}{q}", p_dV, "Keep the sign of q (electron: q = −e)."),
    ("Work to bring q from ∞", r"W_{ext} = qV", p_Wext, "Path doesn't matter."),
    ("From the field", r"V_f - V_i = -\int_i^f \vec E\cdot d\vec s", p_int, "V falls along E."),
    ("Uniform field", r"\Delta V = -Ed", p_Ed, "Equipotentials: evenly spaced planes."),
    ("Point charge", r"V = \frac{kq}{r}", p_point, "1/r, not 1/r² — and keeps the sign."),
    ("Group of charges", r"V = \sum \frac{kq_i}{r_i}", p_group, "Scalars: add with signs."),
    ("Equal distances", r"V = \frac{k\sum q_i}{r}", p_equal, "Square centre, arc centre, ring axis."),
    ("Point-charge shortcut", r"V = Er", p_Er, "From E = kq/r² and V = kq/r."),
    ("Dipole potential (far)", r"V = \frac{kp\cos\theta}{r^2}", p_dipole, "Zero everywhere on the bisector."),
    ("Continuous charge", r"V = \int \frac{k\,dq}{r}", p_cont, "Still a scalar sum."),
    ("Gradient", r"E_s = -\frac{dV}{ds}", p_grad, "E points where V falls fastest."),
    ("Pair energy", r"U = \frac{kq_1q_2}{r}", p_pair, "Like +, unlike −."),
    ("System energy", r"U = \sum_{pairs}\frac{kq_iq_j}{r_{ij}}", p_system, "3 charges → 3 pairs; 4 → 6."),
    ("Closest approach", r"K_{initial} = \frac{kq_1q_2}{r_{min}}", p_closest, "Two movers: add both K's (slide method)."),
    ("Electron-volt", r"1\ \text{eV} = 1.6\times10^{-19}\ \text{J}", p_eV, "ΔU in eV = (q/e) × ΔV."),
    ("Energy conservation", r"K_i + U_i = K_f + U_f", p_cons, "Speed from a drop: ½mv² = |qΔV|."),
    ("Equipotentials", r"\Delta V = 0 \Rightarrow W = 0", p_equip, "Always ⊥ to field lines; no work along them."),
    ]),
]

GEOMETRY = [
    ("Square", r"r = \frac{a}{\sqrt2}", g_square, "Corner to centre."),
    ("Rectangle 2a × a", r"r = \frac{\sqrt5}{2}a", g_rect, "Corner to centre; middle of long side: a/2."),
    ("Equilateral triangle", r"h = \frac{\sqrt3}{2}a,\quad r_G = \frac{a}{\sqrt3}", g_equil, "Vertex to centroid."),
    ("Isosceles right triangle", r"\text{hyp} = a\sqrt2", g_right, "Midpoint of hypotenuse is a/√2 from all corners."),
    ("Point on the bisector", r"r = \sqrt{d^2+y^2}", g_bisector, "Resolve with cos θ = d/r, sin θ = y/r."),
    ("Handy triangles", r"3\text{-}4\text{-}5,\quad 1\text{-}2\text{-}\sqrt5", g_triangles, "Exact cosines without a calculator."),
]


def card(title, tex, fn, note):
    return (f'<div class="vc"><h4>{esc(title)}</h4><div class="fx">\\[ {tex} \\]</div>'
            f'{fn()}<p>{esc(note)}</p></div>')


def build():
    head = open("finals-cheatsheet.html", encoding="utf-8").read()
    head = head[:head.index("<style>")].replace("Finals Cheat Sheet — PHY-2105", "Visual Formula Sheet — PHY-2105")
    css = r"""<style>
        :root { --d-pos:#ef4444; --d-neg:#3b82f6; --d-vec:#fbbf24; --d-net:#4ade80; --d-ln:#9ca3af; --d-txt:#e5e7eb;
                --d-mut:#9ca3af; --d-fld:#a5b4fc; --d-gold:#f59e0b; --d-pink:#f472b6; }
        [data-theme="light"] { --d-pos:#dc2626; --d-neg:#2563eb; --d-vec:#d97706; --d-net:#16a34a; --d-ln:#6b7280; --d-txt:#1f2937;
                --d-mut:#6b7280; --d-fld:#6366f1; --d-gold:#b45309; --d-pink:#db2777; }
        .notes-container { max-width: 1120px; margin: 0 auto; padding: 2rem; }
        .nav-bar { display:flex; flex-wrap:wrap; gap:1rem; justify-content:space-between; padding:1rem 0; margin-bottom:2rem; border-bottom:1px solid var(--border-color); }
        .nav-bar a { color: var(--accent-color); text-decoration:none; font-weight:600; }
        .vgrid { display:grid; grid-template-columns: repeat(3, 1fr); gap:0.9rem; }
        @media (max-width: 960px) { .vgrid { grid-template-columns: 1fr 1fr; } }
        @media (max-width: 620px) { .vgrid { grid-template-columns: 1fr; } .notes-container { padding: 1rem; } }
        .vc { background: var(--surface-color); border:1px solid var(--border-color); border-radius:12px; padding:0.8rem 0.9rem; display:flex; flex-direction:column; break-inside: avoid; }
        .vc h4 { color: var(--accent-color); font-size:0.92rem; margin-bottom:0.1rem; }
        .vc .fx { text-align:center; font-size:0.98rem; overflow-x:auto; overflow-y:hidden; min-height:2.8rem; }
        .vc svg.dg { width:100%; height:auto; display:block; margin:0.2rem 0; font-family: Inter, system-ui, sans-serif; }
        .vc p { font-size:0.82rem; color: var(--text-secondary); margin-top:auto; }
        .chap { border-left:4px solid; padding-left:0.8rem; margin:2.4rem 0 1rem; font-family:'Outfit',sans-serif; }
        .chap.c1 { border-color:#f472b6; } .chap.c2 { border-color:#38bdf8; } .chap.c3 { border-color:#fbbf24; } .chap.c4 { border-color:#4ade80; }
        .chap small { color: var(--text-secondary); font-weight:400; font-size:0.85rem; }
        .chap small a { color: var(--accent-color); }
        .intro { background: var(--surface-color); border:1px solid var(--border-color); border-radius:12px; padding:0.9rem 1.1rem; font-size:0.92rem; color: var(--text-secondary); }
        .intro a { color: var(--accent-color); }
        .key { display:flex; flex-wrap:wrap; gap:0.9rem; margin-top:0.5rem; font-size:0.82rem; }
        .key i { display:inline-block; width:16px; height:4px; border-radius:2px; vertical-align:middle; margin-right:0.3rem; }
        @media print {
            :root, [data-theme] { --d-pos:#dc2626; --d-neg:#2563eb; --d-vec:#d97706; --d-net:#16a34a; --d-ln:#555; --d-txt:#111; --d-mut:#555; --d-fld:#4f46e5; --d-gold:#b45309; --d-pink:#db2777; }
            body { background:#fff !important; color:#000 !important; }
            .background-elements, .nav-bar, .theme-toggle, .intro { display:none !important; }
            .vc { background:#fff !important; border:1px solid #999 !important; }
            .vgrid { grid-template-columns: repeat(3, 1fr); }
        }
    </style>
</head>
<body>
    <div class="background-elements"><div class="glow-orb orb-1"></div><div class="glow-orb orb-2"></div></div>
    <div class="container notes-container">
        <nav class="nav-bar">
            <a href="index.html" class="back-btn"><span>←</span> Back to Home</a>
            <a href="finals-cheatsheet.html">Text Cheat Sheet</a>
            <a href="simulations.html">Simulations</a>
        </nav>
        <header class="notes-header">
            <h1>🖼️ Visual Formula Sheet</h1>
            <p class="subtitle">PHY-2105 Finals • every formula with a picture of what it means</p>
        </header>
        <div class="intro">The same formulas as the <a href="finals-cheatsheet.html">text cheat sheet</a>, each drawn as a diagram.
            Want to move things around? Try the <a href="simulations.html">simulations</a>. Prints on white paper (Ctrl+P).
            <div class="key">
                <span><i style="background:var(--d-pos)"></i>positive</span><span><i style="background:var(--d-neg)"></i>negative</span>
                <span><i style="background:var(--d-vec)"></i>force / field</span><span><i style="background:var(--d-net)"></i>net / result</span>
                <span><i style="background:var(--d-fld)"></i>field lines</span><span><i style="background:var(--d-gold)"></i>distances, angles, V</span>
                <span><i style="background:var(--d-pink)"></i>motion / work / components</span>
            </div>
        </div>
"""
    body = []
    for cls, title, link, cards in SECTIONS:
        body.append(f'<h2 class="chap {cls}">{title} <small>— notes: <a href="{link}">{link}</a></small></h2><div class="vgrid">')
        body += [card(*c) for c in cards]
        body.append("</div>")
    body.append('<h2 class="chap c4">4. Geometry Shortcuts</h2><div class="vgrid">')
    body += [card(*c) for c in GEOMETRY]
    body.append("</div>")
    tail = """
        <footer><p>Made for PHY-2105 • Summer 2026</p></footer>
    </div>
</body>
</html>
"""
    open("visual-cheatsheet.html", "w", encoding="utf-8").write(head + css + "\n".join(body) + tail)
    n = sum(len(s[3]) for s in SECTIONS) + len(GEOMETRY)
    print(f"visual-cheatsheet.html: {n} formula cards")


if __name__ == "__main__":
    build()
