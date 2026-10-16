"""Build the solved past-final pages (final-261.html, final-253.html, final-252.html).

Run: python3 finals_build.py [261|253|252|all]
Questions are shown as screenshots cropped from the papers (finals-figures/q<paper>-<part>.png);
solutions are Given -> Formula -> Steps -> Answer with inline SVG diagrams that follow the
site's light/dark theme.
"""
import sys
from math import hypot, cos, sin, radians, degrees, atan2, sqrt

from quiz4_figures import trace
from visual_cheatsheet import D, unit, esc

K = 8.99e9
E_CH = 1.6e-19

# ------------------------------------------------------------------ page helpers
def M(t):
    """Display maths; long lines break at ',\\qquad', ',\\quad' and ' // ' markers."""
    for sep in (r",\qquad ", r"\qquad ", r",\quad ", " // "):
        t = t.replace(sep, r" \\ ")
    if r" \\ " in t:
        t = r"\begin{gathered} " + t + r" \end{gathered}"
    return f'<div class="math-block">\\[ {t} \\]</div>'


A = lambda t: f'<div class="ans"><strong>Answer:</strong> {t}</div>'
FL = lambda t: f'<div class="flag">{t}</div>'
WHY = lambda t: f'<div class="why"><strong>🧭 Why?</strong> {t}</div>'
FIG = lambda svg, cap="": f'<figure class="dgf">{svg}' + (f'<figcaption>{cap}</figcaption>' if cap else "") + "</figure>"


def G(*items):
    return '<div class="given"><strong>Given</strong><ul>' + "".join(f"<li>{i}</li>" for i in items) + "</ul></div>"


def F(*rows):
    out = '<div class="fbox"><strong>📐 Formula</strong>'
    for tex, note in rows:
        out += f'<div class="fx">\\[ {tex} \\]</div>' + (f"<p>{note}</p>" if note else "")
    return out + "</div>"


def ST(n, t):
    return f'<p class="step"><b class="n">Step {n}.</b> {t}</p>'


KK = r"\(k = \dfrac{1}{4\pi\varepsilon_0} = 8.99\times10^{9}\ \text{N·m}^2/\text{C}^2\)"
EE = r"\(e = 1.6\times10^{-19}\) C"
COUL = (r"F = \frac{k|q_1q_2|}{r^2}", "Coulomb's law — size of the force. Like charges repel, unlike attract.")
FIELD = (r"E = \frac{k|q|}{r^2}", "field of a point charge — <strong>away</strong> from +, <strong>toward</strong> −")


def card(paper, part, title, marks, body, kind=""):
    badge = {"derive": '<span class="badge badge-proof">Show that</span>',
             "short": '<span class="badge badge-short">Short</span>'}.get(kind, '<span class="badge badge-math">Math</span>')
    return (f'<div class="formula-card" id="q{part}"><h4>Q{title} {badge} <span class="mk">{marks} marks</span></h4>'
            f'<img class="qimg" src="finals-figures/q{paper}-{part}.png" alt="Question {title} as printed in the {paper} paper">'
            f'<details open><summary>📝 Solution</summary>{body}</details></div>\n')


# ------------------------------------------------------------------ diagram helpers
class W:
    """World→screen mapping inside a D canvas (world y points up)."""

    def __init__(s, d, ox, oy, sc):
        s.d, s.ox, s.oy, s.sc = d, ox, oy, sc

    def X(s, x): return s.ox + x * s.sc
    def Y(s, y): return s.oy - y * s.sc
    def P(s, p): return s.X(p[0]), s.Y(p[1])


def contributions(charges, P, qP=1.0):
    """Coulomb vectors on a charge qP at P (k = 1). charges: [(x, y, q)]; returns world vectors."""
    out = []
    for x, y, q in charges:
        dx, dy = P[0] - x, P[1] - y
        r = hypot(dx, dy)
        f = q * qP / r ** 2
        out.append((f * dx / r, f * dy / r))
    return out


def vectors(w, charges, P, qP=1.0, labels=None, net_label="", px=70, net_cap=2.0, offsets=None, lab_net=None,
            show_net=True):
    """Draw each contribution (amber) and the net (green) at P."""
    d = w.d
    vs = contributions(charges, P, qP)
    big = max(hypot(*v) for v in vs) or 1
    sc = px / big
    net = (sum(v[0] for v in vs), sum(v[1] for v in vs))
    if hypot(*net) * sc > px * net_cap:
        sc = px * net_cap / hypot(*net)
    Px, Py = w.P(P)
    for i, (vx, vy) in enumerate(vs):
        m = hypot(vx, vy)
        if m < 1e-12:
            continue
        ux, uy = vx / m, -vy / m
        off = (offsets or {}).get(i, 0)
        ox, oy = -uy * off, ux * off
        ex, ey = Px + ox + ux * m * sc, Py + oy + uy * m * sc
        d.arrow(Px + ox, Py + oy, ex, ey, "vec", 2.4, 8)
        if labels and labels[i]:
            d.text(ex + ux * 12 + ox * 0.6, ey + uy * 12 + 4 + oy * 0.6, labels[i], "vec", 11, "middle", True)
    m = hypot(*net)
    if show_net and m > 1e-9 * big:
        ux, uy = net[0] / m, -net[1] / m
        ex, ey = Px + ux * m * sc, Py + uy * m * sc
        d.arrow(Px, Py, ex, ey, "net", 3, 10)
        if net_label:
            lx, ly = lab_net if lab_net else (ex + ux * 16, ey + uy * 16 + 4)
            d.text(lx, ly, net_label, "net", 11.5, "middle", True)
    return vs, net


# ================================================================== PAPER 261
def d261_1a():
    d = D(320, 360, "Field lines of +5q and −10q, null point below the positive charge")
    w = W(d, 160, 140, 58)
    ch = [(5, (0, 0)), (-10, (0, 1))]
    box = (-2.7, 2.7, -3.8, 2.4)
    inside = lambda x, y: -2.75 < x < 2.75 and -3.75 < y < 2.35
    for k in range(10):                                   # out of +5q
        a = 2 * 3.14159265 * (k + 0.5) / 10
        pts = [p for p in trace(ch, (0.08 * cos(a), 0.08 * sin(a)), 1, box, h=0.02) if inside(*p)]
        if len(pts) > 2:
            d.poly([w.P(p) for p in pts], "fld", 1.2, close=False)
            m = len(pts) // 3
            d.arrow(*w.P(pts[m]), *w.P(pts[m + 1]), "fld", 1, 6)
    for k in range(20):                                   # into −10q from far away
        a = 2 * 3.14159265 * (k + 0.25) / 20
        pts = trace(ch, (0.08 * cos(a), 1 + 0.08 * sin(a)), -1, box, h=0.02)
        if hypot(*pts[-1]) < 0.15:                        # this one came from +5q: already drawn
            continue
        pts = [p for p in pts if inside(*p)]
        if len(pts) > 2:
            d.poly([w.P(p) for p in pts], "fld", 1.2, close=False)
            m = len(pts) // 2
            d.arrow(*w.P(pts[m + 1]), *w.P(pts[m]), "fld", 1, 6)
    yn = -1 / (sqrt(2) - 1)
    d.dot(*w.P((0, yn)), "net", 5)
    d.arrow(w.X(0) + 14, w.Y(yn), w.X(0) + 14, w.Y(yn) + 26, "vec", 2, 7)
    d.arrow(w.X(0) - 14, w.Y(yn), w.X(0) - 14, w.Y(yn) - 26, "vec", 2, 7)
    d.text(w.X(0) + 22, w.Y(yn) + 4, "E = 0 here", "net", 11, "start", True)
    d.text(w.X(0) + 22, w.Y(yn) + 18, "y = −2.41 r", "net", 10.5, "start")
    d.charge(*w.P((0, 0)), 1, r=11); d.charge(*w.P((0, 1)), -1, r=14)
    d.text(w.X(0) + 18, w.Y(0) + 4, "+5q", "txt", 11, "start", True)
    d.text(w.X(0) + 20, w.Y(1) + 4, "−10q", "txt", 11, "start", True)
    d.dim(w.X(0) - 34, w.Y(0), w.X(0) - 34, w.Y(1), "r", tdx=-10, tdy=4)
    return d.svg()


def d261_1b():
    d = D(390, 150, "Dipole at 0, 90 and 180 degrees in a field along +x")
    for i, (th, t1, t2) in enumerate(((0, "θ = 0°", "τ = 0"), (90, "θ = 90°", "τ = pE (max)"), (180, "θ = 180°", "τ = 0"))):
        cx, cy = 65 + i * 130, 70
        d.field(cx - 58, cx + 58, 22, 118, "right", 3, 0.25)
        L = 34
        px, py = cx + L * cos(radians(th)), cy - L * sin(radians(th))
        nx, ny = cx - L * cos(radians(th)), cy + L * sin(radians(th))
        d.line(nx, ny, px, py, "ln", 3)
        d.arrow(px, py, px + 22, py, "vec", 2, 6); d.arrow(nx, ny, nx - 22, ny, "vec", 2, 6)
        d.charge(nx, ny, -1, r=7); d.charge(px, py, 1, r=7)
        d.text(cx, 134, t1, "txt", 10.5, bold=True)
        d.text(cx, 147, t2, "net" if th == 90 else "mut", 10, bold=th == 90)
    d.text(380, 14, "E →", "fld", 10, "end", True)
    return d.svg()


def d261_1c():
    d = D(320, 150, "Doubling the distance quarters the force")
    for row, (sep, L, lab) in enumerate(((80, 60, "F"), (160, 15, "F/4"))):
        y = 40 + row * 70
        x1, x2 = 160 - sep / 2, 160 + sep / 2
        d.charge(x1, y, 1, r=9); d.charge(x2, y, 1, r=9)
        d.arrow(x1 - 10, y, x1 - 10 - L, y); d.arrow(x2 + 10, y, x2 + 10 + L, y)
        d.text(x2 + 14 + L, y - 8, lab, "vec", 11, "start", True)
        d.dim(x1, y, x2, y, "r" if row == 0 else "2r", off=18, tdy=14)
    return d.svg()


def d261_2a():
    d = D(330, 285, "Forces on A in the right-angle triangle")
    w = W(d, 170, 252, 46)
    A, B, C = (0, 4), (0, 0), (2, 0)
    d.poly([w.P(A), w.P(B), w.P(C)], "ln", 1.4)
    d.poly([(w.X(0), w.Y(0.3)), (w.X(0.3), w.Y(0.3)), (w.X(0.3), w.Y(0))], "ln", 1, close=False)
    d.dim(*w.P(B), *w.P(C), "2 m", off=16, tdy=14)
    d.dim(*w.P(B), *w.P(A), "4 m", off=-16, tdx=-14, tdy=4)
    d.text(w.X(1.2) + 14, w.Y(2), "√20 m", "gold", 10.5, "start", True)
    vs, net = vectors(w, [(0, 0, -1), (2, 0, 1)], A, 1, None, "F = 2.57×10⁻⁸ N", px=75,
                      lab_net=(w.X(0) - 78, w.Y(4) + 62))
    d.text(w.X(0) + 8, w.Y(4) + 70, "F_B (attract)", "vec", 10.5, "start", True)
    d.text(w.X(0) - 40, w.Y(4) - 40, "F_C (repel)", "vec", 10.5, "end", True)
    nx, ny = net
    d.line(w.X(0), w.Y(4), w.X(0) - 60, w.Y(4), "mut", 1, "3,3")
    d.arc(w.X(0), w.Y(4), 34, 180, 180 + degrees(atan2(-ny, -nx)) * 1)
    d.text(w.X(0) - 44, w.Y(4) + 16, "38.5°", "gold", 10, "end", True)
    for p, q, n in ((A, 1, "A (+)"), (B, -1, "B (−)"), (C, 1, "C (+)")):
        d.charge(*w.P(p), q, r=9)
        d.text(w.P(p)[0] + 14, w.P(p)[1] - 8, n, "txt", 10.5, "start", True)
    return d.svg()


def d261_2b():
    d = D(420, 215, "Forces on the test charge at x = 8 m")
    X = lambda x: 20 + x * 36
    y0 = 46
    d.line(X(0), y0, X(8.4), y0, "ln", 1.2)
    for x in range(0, 9):
        d.line(X(x), y0 - 3, X(x), y0 + 3, "ln", 1); d.text(X(x), y0 + 15, str(x), "mut", 9)
    for x, q, lab in ((1, 1, "+5 μC"), (2, -1, "−40 μC"), (5, 1, "+9 μC"), (8, 1, "q₀ +1 μC")):
        d.charge(X(x), y0, q, r=8 if x != 8 else 6)
        d.text(X(x), y0 - 14, lab, "txt", 9.5, bold=True)
    tx = X(8)
    rows = [(9.17e-4, "F₁ = 0.92 mN (repel →)"), (-9.99e-3, "F₂ = 9.99 mN (attract ←)"), (8.99e-3, "F₃ = 8.99 mN (repel →)")]
    s = 92 / 9.99e-3
    for j, (f, t) in enumerate(rows):
        y = 94 + 32 * j
        d.arrow(tx, y, tx + f * s, y, "vec", 2.4, 7)
        d.text(tx + f * s / 2 if abs(f * s) > 40 else tx + (f * s + 60) / 2, y - 7, t, "vec", 9.5, "middle", True)
    d.arrow(tx, 192, tx - 14, 192, "net", 3, 8)
    d.text(tx - 20, 196, "net 8.2×10⁻⁵ N, toward −x (tiny)", "net", 10, "end", True)
    d.line(tx, y0 + 8, tx, 198, "mut", 1, "3,3")
    return d.svg()


def d261_2c():
    d = D(320, 262, "Forces on q0 at the origin")
    w = W(d, 160, 140, 42)
    r = 2
    p1, p2 = (-r * cos(radians(45)), r * sin(radians(45))), (r * cos(radians(45)), r * sin(radians(45)))
    d.line(w.X(-3), w.Y(0), w.X(3), w.Y(0), "ln", 1); d.line(w.X(0), w.Y(-1.8), w.X(0), w.Y(2.4), "ln", 1)
    for p in (p1, p2):
        d.line(*w.P(p), *w.P((0, 0)), "mut", 1, "4,4")
    d.arc(w.X(0), w.Y(0), 30, 90, 135); d.arc(w.X(0), w.Y(0), 30, 45, 90)
    d.text(w.X(0) - 12, w.Y(0) - 34, "45°", "gold", 9.5, "end", True); d.text(w.X(0) + 12, w.Y(0) - 34, "45°", "gold", 9.5, "start", True)
    vectors(w, [(p1[0], p1[1], 10), (p2[0], p2[1], 20)], (0, 0), 1, ["F₁", "F₂"], "F = 5.03×10⁻⁸ N", px=70,
            lab_net=(w.X(0) - 86, w.Y(0) + 96))
    d.charge(*w.P(p1), 1, r=12); d.charge(*w.P(p2), 1, r=14)
    d.text(w.X(p1[0]) - 18, w.Y(p1[1]) - 14, "q₁ = 10 nC", "txt", 10, "middle", True)
    d.text(w.X(p2[0]) + 18, w.Y(p2[1]) - 16, "q₂ = 20 nC", "txt", 10, "middle", True)
    d.charge(*w.P((0, 0)), 1, r=6)
    return d.svg()


def d261_3a():
    d = D(360, 150, "Dipole parallel and perpendicular to E")
    for i, (th, t1, t2) in enumerate(((0, "p ∥ E", "U = −pE (lowest)"), (90, "p ⊥ E", "U = 0"))):
        cx = 90 + i * 180
        d.field(cx - 80, cx + 80, 22, 112, "right", 3, 0.25)
        L = 32
        px, py = cx + L * cos(radians(th)), 67 - L * sin(radians(th))
        nx, ny = cx - L * cos(radians(th)), 67 + L * sin(radians(th))
        d.line(nx, ny, px, py, "ln", 3)
        d.charge(nx, ny, -1, r=8); d.charge(px, py, 1, r=8)
        d.arrow(cx + 14 * sin(radians(th)) - 16 * cos(radians(th)), 67 + 14 * cos(radians(th)) + 16 * sin(radians(th)),
                cx + 14 * sin(radians(th)) + 16 * cos(radians(th)), 67 + 14 * cos(radians(th)) - 16 * sin(radians(th)), "net", 2, 6)
        d.text(cx, 130, t1, "txt", 11, bold=True); d.text(cx, 145, t2, "net", 10.5, bold=True)
    d.text(352, 14, "E →", "fld", 10, "end", True)
    return d.svg()


def d261_3b():
    d = D(420, 230, "Field at P for both charge choices")
    for i, (qa, title, lab) in enumerate(((-1, "(i) both charges −8 C", "E = 3.18×10⁹ N/C ↓"),
                                         (1, "(ii) A = +8 C, B = −8 C", "E = 3.18×10⁹ N/C →"))):
        w = W(d, 105 + i * 210, 190, 19)
        d.line(w.X(-5), w.Y(0), w.X(5), w.Y(0), "ln", 1); d.line(w.X(0), w.Y(0), w.X(0), w.Y(5.6), "ln", 1)
        for x in (-4, 4):
            d.line(*w.P((x, 0)), *w.P((0, 4)), "mut", 1, "3,3")
        vectors(w, [(-4, 0, qa), (4, 0, -1)], (0, 4), 1, ["E_A", "E_B"], "", px=46)
        d.charge(*w.P((-4, 0)), qa, r=9); d.charge(*w.P((4, 0)), -1, r=9)
        d.text(w.X(-4), w.Y(0) + 22, "A", "txt", 10, bold=True); d.text(w.X(4), w.Y(0) + 22, "B", "txt", 10, bold=True)
        d.dot(*w.P((0, 4))); d.text(w.X(0) - 8, w.Y(4) - 6, "P", "txt", 10.5, "end", True)
        d.text(w.X(0), 16, title, "txt", 10.5, bold=True)
        d.text(w.X(0), 224, lab, "net", 10.5, bold=True)
    return d.svg()


def d261_3c():
    d = D(320, 192, "Every charge on the arc is the same distance from the centre")
    c, R = (160, 160), 120
    d.arc(*c, R, 0, 180, "ln", 1.4)
    d.line(c[0] - R - 10, c[1], c[0] + R + 10, c[1], "ln", 1)
    for ang, q, n in ((0, -1, "e"), (30, 1, "p"), (80, 1, "p"), (130, -1, "e"), (160, 1, "p")):
        x, y = c[0] + R * cos(radians(ang)), c[1] - R * sin(radians(ang))
        d.line(*c, x, y, "mut", 1, "4,4")
        d.charge(x, y, q, r=8)
    d.dot(*c, "txt", 4)
    d.text(c[0], c[1] + 22, "all five at r = 4.00 cm  ·  3 p + 2 e → net charge +e", "net", 10.5, bold=True)
    return d.svg()


def d261_4a():
    d = D(360, 220, "Ring of charge: field on the axis")
    c, P, R = (60, 110), (236, 110), 80
    d.p.append(f'<ellipse cx="{c[0]}" cy="{c[1]}" rx="16" ry="{R}" style="stroke:var(--d-pos);stroke-width:3;fill:none"/>')
    d.line(c[0], c[1], 350, c[1], "ln", 1, "4,4")
    top, bot = (c[0], c[1] - R), (c[0], c[1] + R)
    d.circle(*top, 5, None, fill="pos"); d.text(top[0] - 10, top[1] - 6, "ds", "pos", 10.5, "end", True)
    d.circle(*bot, 4, None, fill="pos", op=0.6)
    d.line(*top, *P, "gold", 1.4); d.line(*bot, *P, "mut", 1, "3,3")
    d.text((top[0] + P[0]) / 2, (top[1] + P[1]) / 2 - 8, "r = √(z² + R²)", "gold", 10.5, bold=True)
    u = unit(*top, *P)
    L = 56
    e = (P[0] + u[0] * L, P[1] + u[1] * L)
    d.arrow(*P, *e, "vec", 2.4, 8); d.text(e[0] + 6, e[1] + 4, "dE", "vec", 11, "start", True)
    d.arrow(*P, e[0], P[1], "net", 2.4, 8); d.text(e[0] + 4, P[1] - 6, "dE cos θ", "net", 10.5, "start", True)
    d.line(e[0], P[1], *e, "pink", 1.4, "4,3"); d.text(e[0] + 4, (P[1] + e[1]) / 2 + 4, "dE sin θ", "pink", 10, "start")
    ub = unit(*bot, *P)
    d.arrow(*P, P[0] + ub[0] * L, P[1] + ub[1] * L, "vec", 1.6, 7, op=0.55)
    d.text(300, 196, "opposite element:", "mut", 9.5)
    d.text(300, 209, "sideways parts cancel", "mut", 9.5)
    d.arc(*P, 26, 180 - degrees(atan2(P[1] - top[1], P[0] - top[0])), 180)
    d.text(P[0] - 32, P[1] - 8, "θ", "gold", 11, "end", True)
    d.dim(c[0], c[1] + 6, P[0], P[1] + 6, "z", off=0, tdy=16)
    d.dim(c[0] - 24, c[1], c[0] - 24, c[1] - R, "R", c="txt", tdx=-10, tdy=4)
    d.dot(*P); d.text(P[0], P[1] + 32, "P", "txt", 11, bold=True)
    return d.svg()


def d261_4b():
    d = D(360, 200, "Dipole potential energy against angle")
    X = lambda t: 40 + t / 180 * 290
    Y = lambda u: 92 - u * 60
    d.line(40, 92, 340, 92, "ln", 1, "3,3")
    d.axes(40, 175, 350, 18, "θ", "U")
    d.curve(lambda t: -cos(radians(t)), 0, 180, X, Y, "net", 2.4)
    for t, lab, col, dy in ((0, "θ = 0°: U = −pE (minimum, stable)", "net", 16), (90, "θ = 90°: U = 0", "gold", 20),
                            (180, "θ = 180°: U = +pE (maximum)", "pink", -10)):
        d.dot(X(t), Y(-cos(radians(t))), col, 4.5)
        d.text(X(t) + (8 if t < 180 else -8), Y(-cos(radians(t))) + dy, lab, col, 10.5, "start" if t < 180 else "end", True)
    for t in (0, 90, 180):
        d.text(X(t), 190, f"{t}°", "mut", 10)
    return d.svg()


def d261_5a():
    d = D(360, 200, "Line of charge of length L, point P at distance d from one end")
    x0, y0, s = 40, 160, 260
    d.line(x0, y0, x0 + s, y0, "pos", 5, op=0.55)
    d.text(x0 + s, y0 + 18, "L", "txt", 11, "end", True)
    P = (x0, 40)
    d.dot(*P); d.text(P[0] - 8, P[1] + 4, "P", "txt", 11, "end", True)
    d.dim(x0 - 16, y0, x0 - 16, P[1], "d", c="txt", tdx=-10, tdy=4)
    ex = x0 + 160
    d.line(ex - 9, y0, ex + 9, y0, "pos", 8)
    d.text(ex, y0 + 20, "dq = λ dx", "pos", 10.5, bold=True)
    d.dim(x0, y0 + 30, ex, y0 + 30, "x", off=0, tdy=-4)
    d.line(ex, y0, *P, "gold", 1.4)
    d.text((ex + P[0]) / 2 + 12, (y0 + P[1]) / 2 - 6, "r = √(x² + d²)", "gold", 10.5, "start", True)
    d.text(240, 30, "dV = k dq / r", "net", 11, bold=True)
    return d.svg()


def d261_5b():
    d = D(360, 230, "Dipole potential geometry")
    c = (90, 130)
    a = 34
    pp, pn = (c[0], c[1] - a), (c[0], c[1] + a)
    P = (300, 40)
    for p, col in ((pp, "pos"), (pn, "neg")):
        d.line(*p, *P, "gold" if p == pp else "fld", 1.3)
    d.line(*c, *P, "ln", 1, "4,4")
    d.line(c[0], c[1] - 80, c[0], c[1] + 70, "mut", 1, "3,3")
    th = degrees(atan2(P[0] - c[0], c[1] - P[1]))
    d.arc(*c, 52, 90 - th, 90)
    d.text(c[0] + 26, c[1] - 52, "θ", "gold", 11, "start", True)
    u = unit(*pn, *P)
    t = (pp[0] - pn[0]) * u[0] + (pp[1] - pn[1]) * u[1]
    foot = (pn[0] + u[0] * t, pn[1] + u[1] * t)
    d.line(*pp, *foot, "pink", 1.4, "3,3")
    d.line(*pn, *foot, "pink", 2.4)
    d.text(foot[0] + 4, foot[1] + 18, "r₋ − r₊ ≈ d cos θ", "pink", 10.5, "start", True)
    d.charge(*pp, 1, r=9); d.charge(*pn, -1, r=9)
    d.dim(c[0] - 26, pp[1], c[0] - 26, pn[1], "d", c="txt", tdx=-10, tdy=4)
    d.dot(*P); d.text(P[0] + 8, P[1] + 4, "P", "txt", 11, "start", True)
    d.text(200, 64, "r₊", "gold", 11, bold=True); d.text(236, 116, "r₋", "fld", 11, bold=True)
    d.text(176, 100, "r", "txt", 11, bold=True)
    return d.svg()


def paper_261():
    P = "261"
    out = []
    out.append(card(P, "1a", "1 (a)", 2, G(r"\(+5q\) at the origin, \(-10q\) on the +y axis at distance \(r\)") +
        F((r"E = \frac{k|q|}{r^2}", "field of each charge; the test charge feels no force where the two fields are equal and opposite"),) +
        WHY("Look at each region in turn:<ul class='rules'>"
            "<li><strong>Between them:</strong> the field of +5q points away from it (up, toward −10q) and the field of −10q points toward it (also up). "
            "Same direction → they add, never cancel.</li>"
            "<li><strong>Above −10q:</strong> the fields are opposite, but this point is nearer the <em>bigger</em> charge, so its field always wins.</li>"
            "<li><strong>Below +5q:</strong> opposite directions (+5q pushes down, −10q pulls up) and the smaller charge is nearer — the sizes can match. "
            "For unlike charges the null point is always <em>outside</em>, on the side of the <em>smaller</em> charge.</li></ul>") +
        ST(1, r"Put the null point a distance \(x\) below the origin. Then it is \(x\) from +5q and \(r + x\) from −10q:") +
        M(r"\frac{k(5q)}{x^2} = \frac{k(10q)}{(r+x)^2}\ \Longrightarrow\ \frac{r+x}{x} = \sqrt2\ \Longrightarrow\ x = \frac{r}{\sqrt2 - 1} = 2.41\,r") +
        FIG(d261_1a(), "Twice as many lines end on −10q as leave +5q; the extra lines come in from far away. The null point (green) is below +5q.") +
        A(r"Below the positive charge, on the y-axis at \(y = -2.41r\) (i.e. \(2.41r\) below the +5q charge). Not between them, not above them."), "short"))

    out.append(card(P, "1b", "1 (b)", 2, F((r"\tau = pE\sin\theta", "θ = angle between the dipole moment p and the field E"),) +
        ST(1, r"\(\sin\theta\) is largest (= 1) at \(\theta = 90^\circ\), and zero at \(0^\circ\) and \(180^\circ\).") +
        M(r"\tau_{max} = pE\ \ (\theta = 90^\circ),\qquad \tau = 0\ \ (\theta = 0^\circ \text{ or } 180^\circ)") +
        WHY("The forces +qE and −qE are always equal and opposite. At 90° they sit on two different lines a full distance d apart → biggest twist. "
            "At 0° or 180° they act along the same line (the dipole axis) → no twist at all.") +
        FIG(d261_1b()) +
        A(r"Maximum torque \(pE\) when \(\vec p \perp \vec E\) (dipole along the y-axis); zero torque when \(\vec p\) is parallel (0°, stable) or antiparallel (180°, unstable) to \(\vec E\)."), "short"))

    out.append(card(P, "1c", "1 (c)", 2, F(COUL,) +
        ST(1, r"Replace \(r\) by \(2r\):") + M(r"F' = \frac{kq_1q_2}{(2r)^2} = \frac14\,\frac{kq_1q_2}{r^2} = \frac{F}{4}") +
        FIG(d261_1c()) +
        A("The force drops to one quarter of its original value (a 75% decrease) — inverse-square law: double r → ¼ F."), "short"))

    out.append(card(P, "2a", "2 (a)", 4,
        G(r"\(|q| = 10\) nC \(= 1.0\times10^{-8}\) C each; A and C positive, B negative",
          "height AB = 4 m, base BC = 2 m, right angle at B", r"Axes: B at (0, 0), A at (0, 4), C at (2, 0)", KK) +
        F(COUL, (r"F_x = \sum F_{ix},\quad F_y = \sum F_{iy},\quad F = \sqrt{F_x^2 + F_y^2}", "add the two forces as vectors")) +
        ST(1, "Distances from A:") + M(r"r_{AB} = 4\ \text{m},\qquad r_{AC} = \sqrt{2^2 + 4^2} = \sqrt{20} = 4.47\ \text{m}") +
        ST(2, "Sizes:") + M(r"F_B = \frac{(8.99\times10^9)(10^{-8})^2}{4^2} = 5.62\times10^{-8}\ \text{N},\qquad F_C = \frac{(8.99\times10^9)(10^{-8})^2}{20} = 4.50\times10^{-8}\ \text{N}") +
        WHY("<strong>B is negative, A positive → attraction:</strong> A is pulled straight down toward B. "
            "<strong>C and A are both positive → repulsion:</strong> A is pushed away from C, along the line C→A, i.e. up and to the left.") +
        ST(3, r"Components (C→A direction is \((-2, 4)/\sqrt{20} = (-0.447, 0.894)\)):") +
        M(r"\vec F_B = (0,\ -5.62)\times10^{-8},\qquad \vec F_C = (-2.01,\ +4.02)\times10^{-8}\ \text{N}") +
        M(r"F_x = -2.01\times10^{-8}\ \text{N},\qquad F_y = -5.62 + 4.02 = -1.60\times10^{-8}\ \text{N}") +
        ST(4, "Resultant:") + M(r"F = \sqrt{(2.01)^2 + (1.60)^2}\times10^{-8} = 2.57\times10^{-8}\ \text{N},\qquad \theta = \tan^{-1}\frac{1.60}{2.01} = 38.5^\circ") +
        FIG(d261_2a()) +
        FL("The paper doesn't say where the right angle is. \"4 m height and 2 m base BC\" puts it at B, with AB vertical — that's used here; state it in your answer.") +
        A(r"\(F = 2.57\times10^{-8}\) N, pointing down and to the left, 38.5° below the −x direction (218.5° from +x)."), "math"))

    out.append(card(P, "2b", "2 (b)", 4,
        G(r"\(q_1 = +5\ \mu\)C at 1 m, \(q_2 = -40\ \mu\)C at 2 m, \(q_3 = +9\ \mu\)C at 5 m", r"\(q_0 = +1\ \mu\)C at \(x = 8\) m", KK) +
        F(COUL, (r"F_{net} = \sum F_i\ \text{(signs along x)}", "everything is on one line: take +x as positive")) +
        ST(1, "Distances to q₀: 7 m, 6 m and 3 m.") +
        M(r"F_1 = \frac{(8.99\times10^9)(5\times10^{-6})(10^{-6})}{7^2} = 9.17\times10^{-4}\ \text{N}") +
        M(r"F_2 = \frac{(8.99\times10^9)(40\times10^{-6})(10^{-6})}{6^2} = 9.99\times10^{-3}\ \text{N}") +
        M(r"F_3 = \frac{(8.99\times10^9)(9\times10^{-6})(10^{-6})}{3^2} = 8.99\times10^{-3}\ \text{N}") +
        WHY("All three charges are to the <strong>left</strong> of q₀. q₁ and q₃ are positive → they push q₀ away → <strong>+x</strong>. "
            "q₂ is negative → it pulls q₀ toward itself → <strong>−x</strong>.") +
        ST(2, "Add with signs:") + M(r"F = 9.17\times10^{-4} + 8.99\times10^{-3} - 9.99\times10^{-3} = -8.15\times10^{-5}\ \text{N}") +
        FIG(d261_2b(), "Arrow lengths to scale; the net is so small it barely shows.") +
        A(r"(i) \(8.15\times10^{-5}\) N; (ii) along −x (toward the origin) — the pull of q₂ just beats the two pushes."), "math"))

    out.append(card(P, "2c", "2 (c)", 4,
        G(r"\(q_1 = 10\) nC, \(q_2 = 20\) nC (taken as positive), each \(r = 2\) m from the origin, 45° either side of the +y axis",
          r"\(q_0 = +1\) nC at the origin", KK) +
        F(COUL, (r"F = \sqrt{F_1^2 + F_2^2}\ \ (\text{forces at }90^\circ)", "q₁ is at 135°, q₂ at 45° — 90° apart, so their forces on q₀ are perpendicular")) +
        M(r"F_1 = \frac{(8.99\times10^9)(10\times10^{-9})(10^{-9})}{2^2} = 2.25\times10^{-8}\ \text{N},\qquad F_2 = \frac{(8.99\times10^9)(20\times10^{-9})(10^{-9})}{2^2} = 4.50\times10^{-8}\ \text{N}") +
        WHY("Both charges are positive, like q₀, so both push it <em>away</em>: q₁ (upper-left) pushes q₀ down-right, along 315°; "
            "q₂ (upper-right) pushes it down-left, along 225°.") +
        ST(1, "Components:") +
        M(r"F_x = 2.25\cos45^\circ - 4.50\cos45^\circ = -1.59\times10^{-8}\ \text{N} // F_y = -(2.25 + 4.50)\sin45^\circ = -4.77\times10^{-8}\ \text{N}") +
        ST(2, "Resultant:") + M(r"F = \sqrt{1.59^2 + 4.77^2}\times10^{-8} = 5.03\times10^{-8}\ \text{N},\qquad \theta = \tan^{-1}\frac{4.77}{1.59} = 71.6^\circ") +
        FIG(d261_2c()) +
        FL("The paper gives no signs for q₁ and q₂; they're taken as positive (as written, \"10 nC\" and \"20 nC\").") +
        A(r"\(F = 5.03\times10^{-8}\) N, pointing down and to the left, 71.6° below the −x axis (251.6° from +x)."), "math"))

    out.append(card(P, "3a", "3 (a)", 4,
        G(r"charges \(\pm5e\), \(d = 0.4\) nm \(= 4\times10^{-10}\) m", r"\(E = 8\times10^{-9}\) N/C", EE) +
        F((r"p = qd", "dipole moment"), (r"U = -pE\cos\theta", "θ between p and E")) +
        ST(1, "Dipole moment:") + M(r"p = (5)(1.6\times10^{-19})(4\times10^{-10}) = 3.2\times10^{-28}\ \text{C·m}") +
        ST(2, "(i) Parallel, θ = 0°:") + M(r"U = -pE\cos0^\circ = -(3.2\times10^{-28})(8\times10^{-9}) = -2.56\times10^{-36}\ \text{J}") +
        ST(3, "(ii) Perpendicular, θ = 90°:") + M(r"U = -pE\cos90^\circ = 0") +
        FIG(d261_3a()) +
        A(r"(i) \(|U| = 2.56\times10^{-36}\) J (U = −2.56×10⁻³⁶ J, the minimum); (ii) \(U = 0\)."), "math"))

    out.append(card(P, "3b", "3 (b)", 6,
        G(r"Both charges are \(-q\) with \(q = -8\) C in the paper; read as <strong>−8 C each</strong> (see note)",
          r"A at \((-4, 0)\), B at \((4, 0)\), P at \((0, 4)\) m", KK) +
        F(FIELD, (r"\vec E = \vec E_A + \vec E_B", "add as vectors")) +
        ST(1, "Each charge is the same distance from P:") +
        M(r"r = \sqrt{4^2 + 4^2} = 4\sqrt2 = 5.66\ \text{m},\qquad E = \frac{(8.99\times10^9)(8)}{32} = 2.25\times10^{9}\ \text{N/C each}") +
        "<h4 style='margin-top:1rem'>(i) Both −8 C</h4>" +
        WHY("Negative charges: each field points <strong>toward</strong> its charge. From P, A is down-left and B is down-right (both at 45°). "
            "The sideways parts cancel; the downward parts add.") +
        M(r"E = 2(2.25\times10^9)\cos45^\circ = 3.18\times10^{9}\ \text{N/C, along } -y") +
        "<h4 style='margin-top:1rem'>(ii) A replaced by +8 C</h4>" +
        WHY("Now A is positive: its field points <strong>away</strong> from A → up-right. B (still negative) gives down-right. "
            "The up and down parts cancel; the rightward parts add.") +
        M(r"E = 2(2.25\times10^9)\cos45^\circ = 3.18\times10^{9}\ \text{N/C, along } +x") +
        FIG(d261_3b()) +
        FL("The figure labels both charges \"−q\" and gives q = −8 C, which would make them +8 C — but then part (ii), replacing one with +8 C, would change nothing. "
           "So the intended reading is that both charges are −8 C. Say so in your answer.") +
        A(r"(i) \(3.18\times10^9\) N/C straight down (−y, toward the origin). (ii) \(3.18\times10^9\) N/C along +x."), "math"))

    out.append(card(P, "3c", "3 (c)", 4,
        G("3 protons (+e) and 2 electrons (−e) on the arc", r"radius \(r = 4.00\) cm \(= 0.0400\) m", KK + ", " + EE) +
        F((r"V = \sum\frac{kq_i}{r_i}", "potential is a scalar: add with signs; the angles don't matter")) +
        ST(1, "Every charge is the same distance r from the centre, so add the charges first:") +
        M(r"\sum q = 3(+e) + 2(-e) = +e") +
        ST(2, "") + M(r"V = \frac{ke}{r} = \frac{(8.99\times10^9)(1.6\times10^{-19})}{0.0400} = 3.60\times10^{-8}\ \text{V}") +
        WHY("θ₁…θ₄ are a distraction for <em>potential</em>: V has no direction, and every charge is at the same r. (They'd matter for the electric <em>field</em>.)") +
        FIG(d261_3c()) +
        A(r"\(V = +3.60\times10^{-8}\) V."), "math"))

    out.append(card(P, "4a", "4 (a)", 4,
        '<p>The formula given is the field of a <strong>ring</strong> of radius R and charge q at a point P on its axis, a distance z from the centre.</p>' +
        ST(1, r"Split the ring into small elements of length \(ds\), each carrying \(dq = \lambda\,ds\) with \(\lambda = q/2\pi R\). Treat each as a point charge:") +
        M(r"dE = \frac{1}{4\pi\varepsilon_0}\frac{dq}{r^2} = \frac{1}{4\pi\varepsilon_0}\frac{\lambda\,ds}{z^2 + R^2}") +
        ST(2, r"Symmetry: the element directly opposite gives a \(d\vec E\) with the same axial part and an equal but opposite sideways part. "
              r"So all the sideways (\(dE\sin\theta\)) parts cancel and only the axial parts \(dE\cos\theta\) survive, with") +
        M(r"\cos\theta = \frac{z}{r} = \frac{z}{(z^2 + R^2)^{1/2}}") +
        ST(3, "Add up the axial parts around the whole ring (z and R are the same for every element):") +
        M(r"E = \oint dE\cos\theta = \frac{1}{4\pi\varepsilon_0}\frac{z\,\lambda}{(z^2+R^2)^{3/2}}\oint ds = \frac{1}{4\pi\varepsilon_0}\frac{z\,\lambda\,(2\pi R)}{(z^2+R^2)^{3/2}}") +
        ST(4, r"Since \(\lambda(2\pi R) = q\):") +
        M(r"E = \frac{1}{4\pi\varepsilon_0}\frac{qz}{(z^2 + R^2)^{3/2}}") +
        FIG(d261_4a(), "Each element's field splits into an axial part (kept) and a sideways part (cancelled by the opposite element).") +
        A(r"\(E = \dfrac{1}{4\pi\varepsilon_0}\dfrac{qz}{(z^2+R^2)^{3/2}}\), directed along the axis (away from the ring for q > 0). Checks: E = 0 at the centre (z = 0); E → kq/z² far away."), "derive"))

    out.append(card(P, "4b", "4 (b)", 4,
        ST(1, r"A dipole at angle θ to \(\vec E\) feels a torque that tries to <em>decrease</em> θ:") +
        M(r"\tau = -pE\sin\theta") +
        ST(2, r"Work done by the field as the dipole turns from \(\theta_0\) to θ:") +
        M(r"W = \int_{\theta_0}^{\theta}\tau\,d\theta = \int_{\theta_0}^{\theta}(-pE\sin\theta)\,d\theta = pE(\cos\theta - \cos\theta_0)") +
        ST(3, r"Potential energy change \(\Delta U = -W\). Choose the reference \(U = 0\) at \(\theta_0 = 90^\circ\) (\(\cos90^\circ = 0\)):") +
        M(r"U(\theta) - 0 = -pE\cos\theta + pE\cos90^\circ\ \Longrightarrow\ U = -pE\cos\theta = -\vec p\cdot\vec E") +
        ST(4, "Conditions:") +
        M(r"U_{max} = +pE\ \ \text{at } \theta = 180^\circ,\qquad U = 0\ \ \text{at } \theta = 90^\circ,\qquad U_{min} = -pE\ \ \text{at } \theta = 0^\circ") +
        FIG(d261_4b()) +
        A(r"\(U = -\vec p\cdot\vec E\). Maximum (+pE) when p is antiparallel to E (180°, unstable); zero when p ⊥ E (90°); minimum (−pE) when aligned (0°, stable)."), "derive"))

    out.append(card(P, "5a", "5 (a)", 4,
        '<p>Thin rod of length L with uniform charge density λ along the x-axis from 0 to L; P is a distance d from the left end, on the perpendicular through that end.</p>' +
        ST(1, r"Element \(dx\) at position x carries \(dq = \lambda\,dx\) and is a distance \(r = \sqrt{x^2 + d^2}\) from P:") +
        M(r"dV = \frac{1}{4\pi\varepsilon_0}\frac{dq}{r} = \frac{1}{4\pi\varepsilon_0}\frac{\lambda\,dx}{\sqrt{x^2 + d^2}}") +
        ST(2, "Potential is a scalar — just add (integrate) along the rod:") +
        M(r"V = \frac{\lambda}{4\pi\varepsilon_0}\int_0^L\frac{dx}{\sqrt{x^2 + d^2}}") +
        ST(3, r"Standard integral \(\int \frac{dx}{\sqrt{x^2+d^2}} = \ln\left(x + \sqrt{x^2 + d^2}\right)\):") +
        M(r"V = \frac{\lambda}{4\pi\varepsilon_0}\Big[\ln\big(x + \sqrt{x^2+d^2}\big)\Big]_0^L // = \frac{\lambda}{4\pi\varepsilon_0}\Big[\ln\big(L + \sqrt{L^2+d^2}\big) - \ln d\Big]") +
        M(r"V = \frac{\lambda}{4\pi\varepsilon_0}\ln\left[\frac{L + (L^2 + d^2)^{1/2}}{d}\right]") +
        FIG(d261_5a()) +
        A(r"\(V = \dfrac{\lambda}{4\pi\varepsilon_0}\ln\left[\dfrac{L + (L^2+d^2)^{1/2}}{d}\right]\) — no vector components needed, because potential is a scalar."), "derive"))

    out.append(card(P, "5b", "5 (b)", 4,
        ST(1, r"Superpose the potentials of \(+q\) and \(-q\), at distances \(r_{(+)}\) and \(r_{(-)}\) from P:") +
        M(r"V = \frac{1}{4\pi\varepsilon_0}\left(\frac{q}{r_{(+)}} - \frac{q}{r_{(-)}}\right) = \frac{q}{4\pi\varepsilon_0}\,\frac{r_{(-)} - r_{(+)}}{r_{(-)}\,r_{(+)}}") +
        ST(2, r"Far away (\(r \gg d\)) the two lines to P are almost parallel. Then") +
        M(r"r_{(-)} - r_{(+)} \approx d\cos\theta,\qquad r_{(-)}\,r_{(+)} \approx r^2") +
        ST(3, r"Substitute, and use \(p = qd\):") +
        M(r"V = \frac{q}{4\pi\varepsilon_0}\frac{d\cos\theta}{r^2} = \frac{1}{4\pi\varepsilon_0}\frac{p\cos\theta}{r^2}") +
        FIG(d261_5b(), "The extra distance to −q is the projection of d on the line to P: d cos θ.") +
        A(r"\(V = \dfrac{1}{4\pi\varepsilon_0}\dfrac{p\cos\theta}{r^2}\). On the axis (θ = 0) V = kp/r²; on the bisector (θ = 90°) V = 0."), "derive"))
    meta = dict(title="Final Exam — Spring 2026 (261)", sub="PHY-2105 • Full marks 40 • 2 hours • Q1–Q3 compulsory, then Q4 or Q5",
                toc=[("1a", "1a"), ("1b", "1b"), ("1c", "1c"), ("2a", "2a"), ("2b", "2b"), ("2c", "2c"), ("3a", "3a"), ("3b", "3b"),
                     ("3c", "3c"), ("4a", "4a"), ("4b", "4b"), ("5a", "5a"), ("5b", "5b")])
    return meta, out


# ------------------------------------------------------------------ page shell
STYLE = r"""
        :root { --d-pos:#ef4444; --d-neg:#3b82f6; --d-vec:#fbbf24; --d-net:#4ade80; --d-ln:#9ca3af; --d-txt:#e5e7eb;
                --d-mut:#9ca3af; --d-fld:#a5b4fc; --d-gold:#f59e0b; --d-pink:#f472b6; }
        [data-theme="light"] { --d-pos:#dc2626; --d-neg:#2563eb; --d-vec:#d97706; --d-net:#16a34a; --d-ln:#6b7280; --d-txt:#1f2937;
                --d-mut:#6b7280; --d-fld:#6366f1; --d-gold:#b45309; --d-pink:#db2777; }
        .qimg { display:block; width:100%; max-width:760px; margin:0.6rem auto 0.4rem; border-radius:8px; border:1px solid var(--border-color); background:#fff; }
        [data-theme="dark"] .qimg { filter: brightness(0.93); }
        .paper-head { max-width:620px; }
        figure.dgf { margin:1rem auto; text-align:center; }
        figure.dgf svg.dg { width:100%; max-width:520px; height:auto; font-family: Inter, system-ui, sans-serif; }
        figure.dgf figcaption { font-size:0.85rem; color:var(--text-secondary); margin-top:0.3rem; }
        .mk { float:right; font-size:0.8rem; color:var(--text-secondary); font-weight:600; }
        .rules { margin:0.4rem 0 0 1.2rem; } .rules li { margin:0.25rem 0; }
        .why { background: rgba(56,189,248,0.08); border:1px solid rgba(56,189,248,0.35); border-radius:10px; padding:0.6rem 1.1rem; margin:0.8rem 0; font-size:0.94rem; }
        .why strong:first-child { color:#38bdf8; }
        [data-theme="light"] .why strong:first-child { color:#0369a1; }
    </style>
</head>"""


def build(paper, fn):
    src = open("assignment2.html", encoding="utf-8").read()
    head = src[:src.index("    </style>")].replace("Assignment-2 Solutions — PHY-2105", f"Final {paper} Solutions — PHY-2105")
    meta, cards = fn()
    others = " ".join(f'<a href="final-{p}.html">Final {p}</a>' for p in ("261", "253", "252") if p != paper)
    nav = ('<nav class="nav-bar"><a href="index.html" class="back-btn">← Back to Home</a>'
           f'<a href="finals-cheatsheet.html">Cheat Sheet</a><a href="visual-cheatsheet.html">Visual Sheet</a>{others}'
           f'<a href="finals/Physics - Final Questions/PHY2105_Final_{paper}.pdf" target="_blank">Paper PDF</a></nav>')
    toc = ('<div class="formula-card toc"><strong>Jump to</strong><div class="toc-grid">' +
           "".join(f'<a href="#q{a}">{b}</a>' for a, b in meta["toc"]) + "</div>"
           '<p class="layout-note" style="margin-top:.6rem">Each question is shown exactly as printed (cropped from the paper), followed by '
           '<strong>Given</strong> → <strong>📐 Formula</strong> → <strong>Steps</strong> → <strong>Answer</strong>, with diagrams. '
           'Blue <strong>🧭 Why?</strong> boxes explain directions; red boxes flag ambiguities in the paper.</p></div>')
    body = ['<body><div class="container notes-container">', nav,
            f'<header class="notes-header"><h1>📄 {meta["title"]}</h1><p class="subtitle">{meta["sub"]}</p></header>',
            f'<img class="qimg paper-head" src="finals-figures/q{paper}-head.png" alt="Paper header and instructions">', toc] + cards
    body.append('<footer><p>Made for PHY-2105 • Summer 2026</p></footer></div></body></html>')
    open(f"final-{paper}.html", "w", encoding="utf-8").write(head + STYLE + "\n" + "".join(body))
    print(f"final-{paper}.html: {len(cards)} parts")


PAPERS = {"261": paper_261}

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    for p, fn in PAPERS.items():
        if which in ("all", p):
            build(p, fn)
