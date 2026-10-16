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


HOW = ('<div class="how"><strong>🧮 How to get the components</strong> Put the force (or field) on a right triangle. '
       'If θ is its angle with the <em>horizontal</em>:<div class="fx">\\[ F_x = F\\cos\\theta,\\qquad F_y = F\\sin\\theta \\]</div>'
       'Then give each part a sign from the way it points: <strong>right / up = +</strong>, <strong>left / down = −</strong>. '
       'cos θ and sin θ come straight from the geometry: cos θ = (horizontal side) / (hypotenuse), sin θ = (vertical side) / (hypotenuse).</div>')


def comp_fig(phi, F_lab, x_lab, y_lab, th_lab, side=()):
    """A vector at angle phi (degrees from +x) split into its horizontal and vertical parts."""
    d = D(420, 214 + 17 * len(side), "Splitting a vector into components")
    c, s_ = cos(radians(phi)), sin(radians(phi))
    L = 150
    ox = 280 if c < 0 else 140
    oy = 180 if s_ > 0 else 30
    tx, ty = ox + L * c, oy - L * s_
    d.arrow(ox, oy, tx, oy, "pink", 2, 8, dash="6,4")
    d.arrow(tx, oy, tx, ty, "pink", 2, 8, dash="6,4")
    d.arrow(ox, oy, tx, ty, "vec", 2.8, 10)
    th = degrees(atan2(abs(s_), abs(c)))
    a0 = 180 if c < 0 else 0
    a1 = 180 - th if (c < 0 and s_ > 0) else (180 + th if (c < 0 and s_ < 0) else (th if s_ > 0 else -th))
    d.arc(ox, oy, 34, a0, a1)
    d.text(ox + (10 if c < 0 else -10), oy + (-4 if s_ > 0 else 14), th_lab, "gold", 10.5, "start" if c < 0 else "end", True)
    d.text((ox + tx) / 2, oy + (16 if s_ > 0 else -8), x_lab, "pink", 10.5, "middle", True)
    d.text(tx + (-8 if c < 0 else 8), (oy + ty) / 2, y_lab, "pink", 10.5, "end" if c < 0 else "start", True)
    d.text((ox + tx) / 2 + (18 if c < 0 else -18), (oy + ty) / 2 + (-10 if s_ > 0 else 14), F_lab, "vec", 11, "start" if c < 0 else "end", True)
    for j, t in enumerate(side):
        d.text(210, 222 + 17 * j, t, "txt", 10.5, "middle", j == 0)
    return d.svg()


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


def d_ring_pair():
    d = D(400, 250, "Two opposite pieces of the ring: sideways parts cancel, axial parts add")
    c, P, R = (60, 125), (200, 125), 85
    d.p.append(f'<ellipse cx="{c[0]}" cy="{c[1]}" rx="16" ry="{R}" style="stroke:var(--d-pos);stroke-width:3;fill:none;opacity:0.6"/>')
    d.line(c[0], c[1], 390, c[1], "ln", 1, "4,4")
    L = 70
    for piece, tag in (((c[0], c[1] - R), "top"), ((c[0], c[1] + R), "bottom")):
        d.circle(*piece, 6, None, fill="pos")
        d.text(piece[0] + 12, piece[1] + (4 if tag == "top" else 10), f"dq ({tag})", "pos", 10, "start", True)
        d.line(*piece, *P, "mut", 1, "3,3")
        u = unit(*piece, *P)
        e = (P[0] + u[0] * L, P[1] + u[1] * L)
        d.arrow(*P, *e, "vec", 2.4, 8)
        d.line(e[0], P[1], *e, "pink", 1.8, "4,3")
        below = e[1] > P[1]
        d.text(e[0] + 6, e[1] + (12 if below else -4), f"dE from {tag} piece", "vec", 9.5, "start", True)
        d.text(e[0] + 6, (P[1] + e[1]) / 2 + 4, "dE sin θ", "pink", 9.5, "start", True)
    ax = 2 * L * u[0]
    d.arrow(P[0], P[1], P[0] + ax, P[1], "net", 3, 9)
    d.text(P[0] + ax + 6, P[1] + 4, "E", "net", 12, "start", True)
    d.dot(*P); d.text(P[0] - 6, P[1] - 8, "P", "txt", 11, "end", True)
    d.text(200, 240, "pink: equal and opposite → cancel   ·   green: the axial parts add up", "mut", 9.5)
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


RING_EXPLAIN = (
    '<div class="how"><strong>🧠 The idea before the maths</strong>'
    '<p><strong>Why not just kq/r²?</strong> That formula is for charge sitting at <em>one point</em>. The ring\'s charge is spread around a circle, so there is no single distance to use.</p>'
    '<p style="margin-top:.5rem"><strong>The plan — chop, find, add:</strong></p><ol class="rules">'
    '<li><strong>Chop</strong> the ring into tiny pieces dq. Each piece is small enough to be a point charge.</li>'
    '<li><strong>Every piece is the same distance</strong> from P: go z along the axis and R out to the ring, so by Pythagoras \\( r = \\sqrt{z^2 + R^2} \\).</li>'
    '<li><strong>One piece</strong> gives \\( dE = k\\,dq/r^2 \\), pointing away from that piece — a <em>slanted</em> arrow.</li>'
    '<li><strong>Split</strong> each slanted arrow into an <em>axial</em> part \\( dE\\cos\\theta \\) (along the axis) and a <em>sideways</em> part \\( dE\\sin\\theta \\).</li>'
    '<li><strong>Symmetry:</strong> the piece directly opposite makes a mirror-image arrow. Same axial part, opposite sideways part. So every sideways part is cancelled by its partner '
    '— <em>only the axial parts survive</em>, and they all point the same way, so they simply add.</li>'
    '<li><strong>Add</strong> the axial parts of all the pieces. Because z and R are the same for every piece, they come out of the sum, and the dq\'s add up to the total charge q.</li></ol>'
    '<p style="margin-top:.5rem"><strong>Where (z² + R²)<sup>3/2</sup> comes from:</strong> one factor 1/r² from Coulomb\'s law, times cos θ = z/r from the triangle, gives z/r³ — and r³ = (z² + R²)<sup>3/2</sup>.</p>'
    '</div>' + FIG(d_ring_pair(), "The top and bottom pieces: their sideways (pink) parts cancel, their axial (green) parts add."))

U_EXPLAIN = (
    '<div class="how"><strong>🧠 The idea before the maths</strong>'
    '<p><strong>What U means:</strong> energy the dipole stores just because of <em>which way it points</em>. Think of a ball on a hill: '
    'pointing <strong>along</strong> E is the bottom of the hill (lowest energy, it stays put); pointing <strong>against</strong> E is the top (highest energy, the slightest nudge flips it).</p>'
    '<p style="margin-top:.5rem"><strong>Why it changes with angle:</strong> the field twists the dipole toward E with torque pE sin θ. '
    'Turning it away from E means fighting that twist — you do work, and that work is stored as potential energy (like lifting a ball).</p>'
    '<p style="margin-top:.5rem"><strong>Where the cos comes from:</strong> work = torque added up over the angle turned (an integral), and '
    '\\( \\int\\sin\\theta\\,d\\theta = -\\cos\\theta \\). That is the only reason the answer has −cos θ in it.</p>'
    '<p style="margin-top:.5rem"><strong>Why zero at 90°:</strong> like choosing "ground level" for height, the zero of energy is a choice. '
    '90° is picked because cos 90° = 0, so the formula comes out with no extra constant.</p>'
    '<table class="tbl" style="margin-top:.6rem"><tr><th>θ</th><th>U = −pE cos θ</th><th>meaning</th></tr>'
    '<tr><td>0° (along E)</td><td>−pE</td><td>lowest — stable, bottom of the hill</td></tr>'
    '<tr><td>90°</td><td>0</td><td>the reference point</td></tr>'
    '<tr><td>180° (against E)</td><td>+pE</td><td>highest — unstable, top of the hill</td></tr></table>'
    '<p style="margin-top:.5rem"><strong>The "= −p·E" part is the same thing in vector shorthand:</strong> a dot product is defined as '
    '\\( \\vec a\\cdot\\vec b = ab\\cos\\theta \\), so \\( \\vec p\\cdot\\vec E = pE\\cos\\theta \\). Use the vector form when p and E are given in '
    'î, ĵ components: multiply matching parts and add, e.g. \\( \\vec p\\cdot\\vec E = p_xE_x + p_yE_y \\).</p>'
    '<p style="margin-top:.5rem"><strong>The minus sign</strong> makes "aligned" the low-energy position. Without it, aligned would be the high-energy one — backwards.</p>'
    '</div>')

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
        ST(3, "Split each force into its horizontal (x) and vertical (y) parts.") + HOW +
        "<p class='sub'><strong>F_B</strong> points straight down, so all of it is vertical and none is horizontal:</p>" +
        M(r"F_{Bx} = 0,\qquad F_{By} = -5.62\times10^{-8}\ \text{N} // (\text{down} \Rightarrow -)") +
        "<p class='sub'><strong>F_C</strong> points along the line from C to A. Going from C to A you move <strong>2 m left</strong> and <strong>4 m up</strong>, "
        "over a length of √20 m. That right triangle gives the cos and sin of the angle θ the force makes with the horizontal:</p>" +
        M(r"\cos\theta = \frac{\text{horizontal}}{\text{hypotenuse}} = \frac{2}{\sqrt{20}} = 0.447,\qquad \sin\theta = \frac{\text{vertical}}{\text{hypotenuse}} = \frac{4}{\sqrt{20}} = 0.894\qquad (\theta = 63.4^\circ)") +
        M(r"F_{Cx} = -F_C\cos\theta = -(4.50\times10^{-8})(0.447) = -2.01\times10^{-8}\ \text{N} // (\text{left} \Rightarrow -)") +
        M(r"F_{Cy} = +F_C\sin\theta = +(4.50\times10^{-8})(0.894) = +4.02\times10^{-8}\ \text{N} // (\text{up} \Rightarrow +)") +
        FIG(comp_fig(116.57, "F_C = 4.50×10⁻⁸ N", "F_Cx = −2.01×10⁻⁸", "F_Cy = +4.02×10⁻⁸", "θ = 63.4°",
                     ("Triangle C → A:", "2 m left, 4 m up, √20 m long", "cos θ = 2/√20 = 0.447", "sin θ = 4/√20 = 0.894")),
            "F_C split into a horizontal part (left) and a vertical part (up).") +
        ST(4, "Add the parts of both forces:") +
        M(r"F_x = F_{Bx} + F_{Cx} // = 0 + (-2.01\times10^{-8}) = -2.01\times10^{-8}\ \text{N}") +
        M(r"F_y = F_{By} + F_{Cy} // = -5.62\times10^{-8} + 4.02\times10^{-8} = -1.60\times10^{-8}\ \text{N}") +
        ST(5, "Resultant:") + M(r"F = \sqrt{(2.01)^2 + (1.60)^2}\times10^{-8} = 2.57\times10^{-8}\ \text{N},\qquad \theta = \tan^{-1}\frac{1.60}{2.01} = 38.5^\circ") +
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
        F(COUL, (r"F = \sqrt{F_1^2 + F_2^2} // (\text{forces at }90^\circ)", "q₁ is at 135°, q₂ at 45° — 90° apart, so their forces on q₀ are perpendicular")) +
        M(r"F_1 = \frac{(8.99\times10^9)(10\times10^{-9})(10^{-9})}{2^2} = 2.25\times10^{-8}\ \text{N},\qquad F_2 = \frac{(8.99\times10^9)(20\times10^{-9})(10^{-9})}{2^2} = 4.50\times10^{-8}\ \text{N}") +
        WHY("Both charges are positive, like q₀, so both push it <em>away</em>: q₁ (upper-left) pushes q₀ down-right, along 315°; "
            "q₂ (upper-right) pushes it down-left, along 225°.") +
        ST(1, "Components. Each force is 45° from the vertical, so also 45° from the horizontal: cos 45° = sin 45° = 0.707.") + HOW +
        M(r"F_{1x} = +F_1\cos45^\circ = +(2.25\times10^{-8})(0.707) = +1.59\times10^{-8}\ \text{N} // (\text{right})") +
        M(r"F_{1y} = -F_1\sin45^\circ = -(2.25\times10^{-8})(0.707) = -1.59\times10^{-8}\ \text{N} // (\text{down})") +
        M(r"F_{2x} = -F_2\cos45^\circ = -(4.50\times10^{-8})(0.707) = -3.18\times10^{-8}\ \text{N} // (\text{left})") +
        M(r"F_{2y} = -F_2\sin45^\circ = -(4.50\times10^{-8})(0.707) = -3.18\times10^{-8}\ \text{N} // (\text{down})") +
        FIG(comp_fig(225, "F₂ = 4.50×10⁻⁸ N", "F₂x = −3.18×10⁻⁸", "F₂y = −3.18×10⁻⁸", "45°",
                     ("q₂ is up-right, so it pushes", "q₀ down-left, 45° below −x.", "cos 45° = sin 45° = 0.707")), "F₂ split into its parts (F₁ works the same way, to the right).") +
        M(r"F_x = 1.59 - 3.18 = -1.59\times10^{-8}\ \text{N},\qquad F_y = -1.59 - 3.18 = -4.77\times10^{-8}\ \text{N}") +
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
        HOW + "<p class='sub'>From P to A is 4 m left and 4 m down (length 4√2 m), so cos θ = sin θ = 4/(4√2) = 0.707 (θ = 45°). Each field has parts of size (2.25×10⁹)(0.707) = 1.59×10⁹ N/C.</p>" +
        M(r"\vec E_A = (-1.59,\ -1.59)\times10^9 // (\text{left, down}),\qquad \vec E_B = (+1.59,\ -1.59)\times10^9 // (\text{right, down})") +
        M(r"E_x = -1.59 + 1.59 = 0,\qquad E_y = -1.59 - 1.59 = -3.18\times10^{9}\ \text{N/C}") +
        M(r"E = 3.18\times10^{9}\ \text{N/C, along } -y") +
        "<h4 style='margin-top:1rem'>(ii) A replaced by +8 C</h4>" +
        WHY("Now A is positive: its field points <strong>away</strong> from A → up-right. B (still negative) gives down-right. "
            "The up and down parts cancel; the rightward parts add.") +
        M(r"\vec E_A = (+1.59,\ +1.59)\times10^9 // (\text{right, up}),\qquad \vec E_B = (+1.59,\ -1.59)\times10^9 // (\text{right, down})") +
        M(r"E_x = 1.59 + 1.59 = 3.18\times10^{9}\ \text{N/C},\qquad E_y = 1.59 - 1.59 = 0") +
        M(r"E = 3.18\times10^{9}\ \text{N/C, along } +x") +
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
        '<p>The formula given is the field of a <strong>ring</strong> of radius R and charge q at a point P on its axis, a distance z from the centre.</p>' + RING_EXPLAIN +
        ST(1, r"Split the ring into small elements of length \(ds\), each carrying \(dq = \lambda\,ds\) with \(\lambda = q/2\pi R\). Treat each as a point charge:") +
        M(r"dE = \frac{1}{4\pi\varepsilon_0}\frac{dq}{r^2} = \frac{1}{4\pi\varepsilon_0}\frac{\lambda\,ds}{z^2 + R^2}") +
        ST(2, r"Symmetry: the element directly opposite gives a \(d\vec E\) with the same axial part and an equal but opposite sideways part. "
              r"So all the sideways (\(dE\sin\theta\)) parts cancel and only the axial parts \(dE\cos\theta\) survive, with") +
        M(r"\cos\theta = \frac{z}{r} = \frac{z}{(z^2 + R^2)^{1/2}}") +
        ST(3, "Put Steps 1 and 2 together, then add up round the ring.") +
        r"<p><strong>(a) Axial part of one piece</strong> = (its field from Step 1) × (cos θ from Step 2). This is where z comes in — it is the adjacent side of the triangle in cos θ = z/r:</p>" +
        M(r"dE\cos\theta = \underbrace{\frac{1}{4\pi\varepsilon_0}\frac{\lambda\,ds}{z^2 + R^2}}_{dE\ \text{(Step 1)}}\times\underbrace{\frac{z}{(z^2 + R^2)^{1/2}}}_{\cos\theta\ \text{(Step 2)}}") +
        r"<p><strong>(b) Combine the powers</strong> of \((z^2+R^2)\): \(\ (z^2+R^2)^{1}\times(z^2+R^2)^{1/2} = (z^2+R^2)^{3/2}\):</p>" +
        M(r"dE\cos\theta = \frac{1}{4\pi\varepsilon_0}\frac{z\,\lambda\,ds}{(z^2 + R^2)^{3/2}}") +
        r"<p><strong>(c) Add this up for every piece</strong> round the ring (∮ means “sum all the way round”). Only \(ds\) changes from piece to piece — z, R and λ are the same for all of them — so everything except ds comes outside the sum:</p>" +
        M(r"E = \oint dE\cos\theta = \frac{1}{4\pi\varepsilon_0}\frac{z\,\lambda}{(z^2 + R^2)^{3/2}}\oint ds") +
        r"<p><strong>(d)</strong> All the little lengths ds added together make the whole circumference: \(\oint ds = 2\pi R\).</p>" +
        M(r"E = \frac{1}{4\pi\varepsilon_0}\frac{z\,\lambda\,(2\pi R)}{(z^2 + R^2)^{3/2}}") +
        ST(4, r"Since \(\lambda(2\pi R) = q\) (charge per length × length of the ring = total charge):") +
        M(r"E = \frac{1}{4\pi\varepsilon_0}\frac{qz}{(z^2 + R^2)^{3/2}}") +
        ST(5, "Check it makes sense:") +
        M(r"z = 0:\ E = 0 // (\text{at the centre every piece is cancelled by the opposite one})") +
        M(r"z \gg R:\ (z^2 + R^2)^{3/2} \approx z^3\ \Rightarrow\ E \approx \frac{1}{4\pi\varepsilon_0}\frac{q}{z^2} // (\text{from far away the ring looks like a point charge})") +
        '<img class="svg-fig" src="quiz4-figures/g-ring.svg" alt="Ring field along its axis"><p class="fig-cap">E along the axis: zero at the centre, a maximum near z ≈ 0.7R, then falling like a point charge.</p>' +
        FIG(d261_4a(), "Each element's field splits into an axial part (kept) and a sideways part (cancelled by the opposite element).") +
        A(r"\(E = \dfrac{1}{4\pi\varepsilon_0}\dfrac{qz}{(z^2+R^2)^{3/2}}\), directed along the axis (away from the ring for q > 0). Checks: E = 0 at the centre (z = 0); E → kq/z² far away."), "derive"))

    out.append(card(P, "4b", "4 (b)", 4, U_EXPLAIN +
        ST(1, r"A dipole at angle θ to \(\vec E\) feels a torque that tries to <em>decrease</em> θ:") +
        M(r"\tau = -pE\sin\theta") +
        ST(2, r"Work done by the field as the dipole turns from \(\theta_0\) to θ:") +
        M(r"W = \int_{\theta_0}^{\theta}\tau\,d\theta = \int_{\theta_0}^{\theta}(-pE\sin\theta)\,d\theta = pE(\cos\theta - \cos\theta_0)") +
        ST(3, r"Potential energy change: \(\Delta U = -W\). Choose the reference \(U = 0\) at \(\theta_0 = 90^\circ\) — the angle where the energy is zero:") +
        M(r"U(\theta) - U(90^\circ) = -W = -pE\,(\cos\theta - \cos90^\circ)") +
        ST(4, r"Both reference terms vanish: \(U(90^\circ) = 0\) (that's how we chose it) and \(\cos90^\circ = 0\):") +
        M(r"U(\theta) - 0 = -pE\,(\cos\theta - 0)\ \Longrightarrow\ U = -pE\cos\theta") +
        ST(5, r"Write it as a dot product. For any two vectors, \(\vec a\cdot\vec b = ab\cos\theta\) (θ = angle between them). With \(\vec a = \vec p\) and \(\vec b = \vec E\), \(pE\cos\theta\) is exactly \(\vec p\cdot\vec E\):") +
        M(r"U = -pE\cos\theta = -\vec p\cdot\vec E") +
        ST(6, "Conditions:") +
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


# ================================================================== PAPER 253
def d253_1b():
    d = D(320, 210, "Moving along an equipotential takes no work")
    c = (160, 110)
    for k in range(10):
        a = radians(k * 36 + 18)
        d.arrow(c[0] + 14 * cos(a), c[1] - 14 * sin(a), c[0] + 98 * cos(a), c[1] - 98 * sin(a), "fld", 1.2, 6, op=0.7)
    d.circle(*c, 62, "gold", 2, dash="6,4")
    d.charge(*c, 1, r=11)
    A, B = (c[0] + 62 * cos(radians(150)), c[1] - 62 * sin(radians(150))), (c[0] + 62 * cos(radians(40)), c[1] - 62 * sin(radians(40)))
    d.arc(*c, 62, 150, 40, "pink", 3, arrow_end=True)
    d.dot(*A, "txt", 5); d.dot(*B, "txt", 5)
    d.text(A[0] - 10, A[1] - 6, "A (V)", "txt", 11, "end", True); d.text(B[0] + 10, B[1] - 6, "B (V)", "txt", 11, "start", True)
    d.text(c[0], 200, "ΔV = 0 → W = qΔV = 0, whatever the path", "net", 10.5, bold=True)
    return d.svg()


def d253_1c():
    d = D(320, 150, "Counting electrons on a charged ball")
    d.circle(90, 72, 48, "ln", 1.4, fill="neg", op=0.15)
    for x, y in ((70, 50), (105, 45), (60, 80), (95, 75), (120, 95), (80, 105), (115, 62)):
        d.charge(x, y, -1, r=6)
    d.text(90, 140, "q = −3.2×10⁻¹⁵ C", "txt", 10.5, bold=True)
    d.arrow(150, 72, 180, 72, "ln", 1.4, 6)
    d.text(250, 66, "N = q / e", "net", 12, bold=True)
    d.text(250, 84, "= 2.0×10⁴ extra electrons", "mut", 10)
    return d.svg()


def d_double():
    return d261_1c()


def d253_2():
    d = D(380, 175, "Forces on +1 μC at the midpoint")
    d.line(40, 50, 340, 50, "ln", 1.2)
    d.charge(60, 50, 1, r=11); d.charge(320, 50, -1, r=13); d.charge(190, 50, 1, r=7)
    d.text(60, 28, "+5 μC", "txt", 10.5, bold=True); d.text(320, 28, "−10 μC", "txt", 10.5, bold=True); d.text(190, 28, "+1 μC", "txt", 10.5, bold=True)
    d.dim(60, 50, 190, 50, "5 cm", off=16, tdy=14); d.dim(190, 50, 320, 50, "5 cm", off=16, tdy=14)
    for j, (L, c, t) in enumerate(((50, "vec", "F₁ = 18.0 N (pushed away from +5 μC)"), (100, "vec", "F₂ = 36.0 N (pulled toward −10 μC)"),
                                  (150, "net", "F = 53.9 N → toward −10 μC"))):
        y = 102 + 24 * j
        d.arrow(190, y, 190 + L, y, c, 2.6 if c == "vec" else 3.2, 8)
        d.text(184, y + 4, t, c, 9.5, "end", True)
    return d.svg()


def d253_3():
    d = D(340, 240, "Forces on q0 at P")
    w = W(d, 230, 150, 50)
    q1, q2 = (-2, 0), (-1, sqrt(3))
    d.line(*w.P(q1), *w.P((0, 0)), "ln", 1.4); d.line(*w.P(q2), *w.P((0, 0)), "ln", 1.4)
    d.arc(w.X(0), w.Y(0), 26, 120, 180); d.text(w.X(0) - 34, w.Y(0) - 14, "60°", "gold", 10, "end", True)
    d.text(w.X(-1), w.Y(0) + 16, "d = 2 m", "gold", 10, bold=True); d.text(w.X(-0.5) - 26, w.Y(0.87) - 4, "d", "gold", 10, bold=True)
    vectors(w, [(q1[0], q1[1], 5), (q2[0], q2[1], 10)], (0, 0), 1, ["F₁", "F₂"], "F = 29.7 N", px=60, lab_net=(w.X(0) + 30, w.Y(0) + 76))
    d.line(w.X(0), w.Y(0), w.X(1.8), w.Y(0), "mut", 1, "3,3")
    d.arc(w.X(0), w.Y(0), 38, -40.9, 0); d.text(w.X(0) + 44, w.Y(0) + 18, "40.9°", "gold", 10, "start", True)
    d.charge(*w.P(q1), 1, r=11); d.charge(*w.P(q2), 1, r=13); d.charge(*w.P((0, 0)), 1, r=6)
    d.text(w.X(q1[0]), w.Y(q1[1]) + 24, "q₁ = 5 C", "txt", 10, bold=True); d.text(w.X(q2[0]) - 18, w.Y(q2[1]) - 14, "q₂ = 10 C", "txt", 10, bold=True)
    d.text(w.X(0) + 6, w.Y(0) - 10, "q₀ (P)", "txt", 10, "start", True)
    return d.svg()


def d253_4():
    d = D(340, 240, "Field at P from -10 C and +5 C")
    w = W(d, 170, 200, 34)
    d.line(w.X(-4.4), w.Y(0), w.X(4.4), w.Y(0), "ln", 1); d.line(w.X(0), w.Y(0), w.X(0), w.Y(5.3), "ln", 1)
    for x in (-3, 3):
        d.line(*w.P((x, 0)), *w.P((0, 4)), "mut", 1, "3,3")
    d.text(w.X(-1.5) - 16, w.Y(2) - 2, "5 m", "gold", 10, "end", True); d.text(w.X(1.5) + 16, w.Y(2) - 2, "5 m", "gold", 10, "start", True)
    vectors(w, [(-3, 0, -10), (3, 0, 5)], (0, 4), 1, ["E₁", "E₂"], "E = 3.54×10⁹ N/C", px=70, lab_net=(w.X(0) - 118, w.Y(4) + 10))
    d.charge(*w.P((-3, 0)), -1, r=12); d.charge(*w.P((3, 0)), 1, r=9)
    d.text(w.X(-3), w.Y(0) + 26, "q₁ = −10 C", "txt", 10, bold=True); d.text(w.X(3), w.Y(0) + 26, "q₂ = +5 C", "txt", 10, bold=True)
    d.dot(*w.P((0, 4))); d.text(w.X(0) + 8, w.Y(4) - 8, "P (0, 4)", "txt", 10.5, "start", True)
    return d.svg()


def d253_5():
    d = D(320, 210, "Dipole moment and field in the xy-plane; torque out of the page")
    o = (90, 170)
    ap, aE = degrees(atan2(2, 5)), degrees(atan2(6000, 5000))
    d.axes(o[0] - 20, o[1], 300, 20, "x", "y")
    for ang, L, c, t in ((ap, 150, "net", "p = (5, 2)×10⁻³⁰"), (aE, 150, "vec", "E = (5000, 6000)")):
        e = (o[0] + L * cos(radians(ang)), o[1] - L * sin(radians(ang)))
        d.arrow(*o, *e, c, 2.6, 9); d.text(e[0] + 6, e[1] + (12 if c == "net" else -2), t, c, 10.5, "start", True)
    d.arc(*o, 60, ap, aE, "gold", 1.4); d.text(o[0] + 66, o[1] - 50, "θ = 28.4°", "gold", 10.5, "start", True)
    d.circle(o[0], o[1], 9, "pink", 1.8); d.dot(o[0], o[1], "pink", 2.5)
    d.text(o[0] + 16, o[1] + 26, "τ: out of the page (+k̂)", "pink", 10, "start", True)
    d.arc(*o, 100, ap + 4, aE - 4, "pink", 1.6, arrow_end=True)
    return d.svg()


def d253_6():
    d = D(320, 240, "Distances from P to the four charges")
    P = (130, 130)
    s = 62
    dirs = [(115, 1, s, "+q", "d"), (25, -1, s, "−q", "d"), (25, -1, 2 * s, "−q", "2d"), (-65, 1, s, "+q", "d")]
    for ang, q, r, lab, dl in dirs:
        x, y = P[0] + r * cos(radians(ang)), P[1] - r * sin(radians(ang))
        d.line(*P, x, y, "mut", 1, "4,4")
        d.charge(x, y, q, r=9)
        d.text(x + 14, y - 8, lab, "txt", 10, "start", True)
        if dl == "2d":
            d.text(P[0] + 1.5 * s * cos(radians(25)) + 4, P[1] - 1.5 * s * sin(radians(25)) + 16, "d", "gold", 10, bold=True)
        else:
            d.text(P[0] + r / 2 * cos(radians(ang)) + 10, P[1] - r / 2 * sin(radians(ang)) + 4, dl, "gold", 10, bold=True)
    d.dot(*P, "txt", 4); d.text(P[0] - 10, P[1] + 4, "P", "txt", 11, "end", True)
    d.text(160, 232, "V = kq(1/d − 1/d − 1/2d + 1/d) = kq/2d", "net", 10.5, bold=True)
    return d.svg()


def d253_7():
    d = D(300, 252, "P is the midpoint of the hypotenuse")
    w = W(d, 60, 200, 150)
    A, B, C = (0, 1), (1, 0), (0, 0)
    M_ = (0.5, 0.5)
    d.poly([w.P(A), w.P(B), w.P(C)], "ln", 1.4)
    for p in (A, B, C):
        d.line(*w.P(p), *w.P(M_), "gold", 1.4, "4,3")
    d.text(w.X(0.25) - 6, w.Y(0.75) - 4, "a/√2", "gold", 10, "end", True)
    d.charge(*w.P(A), 1, r=10); d.charge(*w.P(B), 1, r=10); d.charge(*w.P(C), 1, r=10)
    d.text(w.X(0) + 16, w.Y(1) + 4, "q₁ = +2e", "txt", 10, "start", True)
    d.text(w.X(1) + 14, w.Y(0) + 4, "q₂ = +2e", "txt", 10, "start", True)
    d.text(w.X(0) + 16, w.Y(0) - 10, "q₃ = +3e", "txt", 10, "start", True)
    d.dot(*w.P(M_)); d.text(w.X(0.5) + 8, w.Y(0.5) - 6, "P", "txt", 11, "start", True)
    d.dim(*w.P(C), *w.P(B), "a = 5 μm", off=26, tdy=14)
    return d.svg()


def d253_8a():
    d = D(360, 170, "Dipole on the z axis: fields of + and − at P")
    y = 90
    zx = lambda z: 46 + z * 52
    d.line(20, y, 350, y, "ln", 1, "4,4")
    d.charge(zx(-0.5), y, -1, r=9); d.charge(zx(0.5), y, 1, r=9)
    d.dot(zx(0), y, "txt", 3)
    d.dim(zx(-0.5), y, zx(0.5), y, "d", off=22, tdy=14)
    d.dot(zx(4.2), y, "txt", 4); d.text(zx(4.2), y + 22, "P", "txt", 11, bold=True)
    d.dim(zx(0), y, zx(4.2), y, "z", off=-36)
    d.arrow(zx(4.2), y - 14, zx(4.2) + 60, y - 14, "pos", 2.4, 8); d.text(zx(4.2) - 6, y - 18, "E₊ = kq/(z − d/2)²", "pos", 10, "end", True)
    d.arrow(zx(4.2), y + 14, zx(4.2) - 44, y + 14, "neg", 2.4, 8); d.text(zx(4.2) - 50, y + 18, "E₋ = kq/(z + d/2)²", "neg", 10, "end", True)
    d.text(180, 160, "E₊ is slightly bigger (closer) → net along +z", "net", 10, bold=True)
    return d.svg()


def d253_8b():
    d = D(340, 210, "Torque on a dipole: lever arm d/2 sin θ")
    d.field(10, 330, 20, 190, "right", 4, 0.25)
    c, th, L = (170, 105), 40, 70
    px, py = c[0] + L * cos(radians(th)), c[1] - L * sin(radians(th))
    nx, ny = c[0] - L * cos(radians(th)), c[1] + L * sin(radians(th))
    d.line(nx, ny, px, py, "ln", 3)
    d.arrow(px + 9, py, px + 60, py, "vec", 2.4); d.text(px + 62, py + 4, "F = qE", "vec", 10.5, "start", True)
    d.arrow(nx - 9, ny, nx - 60, ny, "vec", 2.4); d.text(nx - 62, ny + 4, "F = qE", "vec", 10.5, "end", True)
    d.line(c[0], c[1], c[0] + 100, c[1], "mut", 1, "3,3")
    d.arc(*c, 30, 0, th); d.text(c[0] + 36, c[1] - 10, "θ", "gold", 11, "start", True)
    d.line(c[0], c[1], c[0], py, "pink", 1.4, "3,3"); d.line(c[0], py, px, py, "mut", 1, "2,2")
    d.text(c[0] - 6, (c[1] + py) / 2 + 4, "(d/2) sin θ", "pink", 10, "end", True)
    d.charge(nx, ny, -1, r=9); d.charge(px, py, 1, r=9)
    d.text(170, 202, "τ = 2 · qE · (d/2) sin θ = pE sin θ", "net", 10.5, bold=True)
    return d.svg()


def d253_9a():
    d = D(340, 190, "Moving a test charge from i to f through a field")
    d.field(10, 330, 20, 170, "right", 4, 0.3)
    pts = [(40 + 26 * k, 150 - 95 * max(0.0, sin(k / 10 * 3.14159265)) ** 0.9) for k in range(11)]
    d.poly(pts, "pink", 2, close=False)
    k = 4
    d.arrow(*pts[k], *pts[k + 1], "pink", 2.4, 8); d.text(pts[k][0] - 6, pts[k][1] - 8, "ds", "pink", 11, "end", True)
    d.arrow(pts[k + 1][0], pts[k + 1][1], pts[k + 1][0] + 46, pts[k + 1][1], "vec", 2.2, 7)
    d.text(pts[k + 1][0] + 50, pts[k + 1][1] + 4, "F = q₀E", "vec", 10.5, "start", True)
    d.charge(*pts[k + 1], 1, r=6)
    d.text(pts[0][0] - 4, pts[0][1] + 16, "i", "txt", 12, bold=True); d.text(pts[-1][0] + 4, pts[-1][1] + 16, "f", "txt", 12, bold=True)
    d.text(320, 16, "E →", "fld", 10, "end", True)
    d.text(240, 184, "dW = q₀ E · ds", "net", 10.5, bold=True)
    return d.svg()


def d253_9b():
    d = D(340, 150, "Bringing the test charge in from infinity along a radial line")
    d.charge(40, 75, 1, r=13); d.text(40, 104, "q", "txt", 11, bold=True)
    d.line(53, 75, 330, 75, "ln", 1, "4,4")
    d.dot(150, 75, "txt", 4); d.text(150, 100, "P (r = R)", "txt", 10.5, bold=True)
    for x in (200, 260):
        d.arrow(x, 58, x + 34, 58, "vec", 1.8, 6)
    d.text(232, 48, "E = kq/r² (radial)", "vec", 10, bold=True)
    d.text(320, 100, "→ ∞ (V = 0)", "mut", 10, "end", True)
    d.dim(40, 75, 150, 75, "R", off=34, tdy=14)
    return d.svg()


def paper_253():
    P = "253"
    out = []
    out.append(card(P, "1a", "1 (a)", 2, F(COUL,) +
        ST(1, r"With \(r \to 2r\):") + M(r"F' = \frac{kq^2}{(2r)^2} = \frac{1}{4}\cdot\frac{kq^2}{r^2} = \frac{F}{4}") +
        WHY("Coulomb's law is an <strong>inverse-square</strong> law: the force depends on 1/r², so doubling r divides the force by 2² = 4. "
            "The charges are still alike, so the force stays repulsive — only its size changes.") +
        FIG(d_double()) +
        A("The force becomes one quarter of its original value (still repulsive)."), "short"))
    out.append(card(P, "1b", "1 (b)", 2, F((r"W = q\,\Delta V = q(V_B - V_A)", "work done to move q (slowly) from A to B"),) +
        ST(1, r"\(V_A = V_B = V\), so") + M(r"W = q(V - V) = 0") +
        WHY("A and B lie on the same <strong>equipotential surface</strong>. The field is perpendicular to an equipotential, so moving along it the force has no component along the motion — "
            "and the work depends only on the end points, so <em>any</em> path from A to B gives zero.") +
        FIG(d253_1b()) +
        A("Zero work, because ΔV = 0 between points at the same potential (W = qΔV)."), "short"))
    out.append(card(P, "1c", "1 (c)", 2, G(r"\(q = -3.2\times10^{-15}\) C", r"\(e = -1.6\times10^{-19}\) C (electron)") +
        F((r"q = Ne\ \Longrightarrow\ N = \frac{q}{e}", "quantization of charge")) +
        M(r"N = \frac{-3.2\times10^{-15}}{-1.6\times10^{-19}} = 2.0\times10^{4}") +
        FIG(d253_1c()) +
        A(r"\(2.0\times10^4\) (twenty thousand) excess electrons."), "short"))
    out.append(card(P, "2", "2", 4,
        G(r"\(q_1 = +5\ \mu\)C, \(q_2 = -10\ \mu\)C, 10 cm apart", r"\(q_0 = +1\ \mu\)C at the midpoint → 5 cm = 0.05 m from each", KK) +
        F(COUL, (r"F = F_1 + F_2 // (\text{same direction})", "")) +
        M(r"F_1 = \frac{(8.99\times10^9)(5\times10^{-6})(1\times10^{-6})}{(0.05)^2} = 18.0\ \text{N}") +
        M(r"F_2 = \frac{(8.99\times10^9)(10\times10^{-6})(1\times10^{-6})}{(0.05)^2} = 36.0\ \text{N}") +
        WHY("q₀ is positive. +5 μC <strong>repels</strong> it → pushes it away from +5 μC, toward −10 μC. −10 μC <strong>attracts</strong> it → pulls it toward −10 μC. "
            "Both forces point the same way, so they <em>add</em>. (Between unlike charges forces never cancel.)") +
        M(r"F = 18.0 + 36.0 = 53.9\ \text{N}") +
        FIG(d253_2()) +
        A("53.9 N, directed from the +5 μC charge toward the −10 μC charge."), "math"))
    out.append(card(P, "3", "3", 5,
        G(r"\(q_1 = 5\) C at distance \(d = 2\) m to the left of P; \(q_2 = 10\) C at distance \(d\) from P, 60° above that line",
          r"\(q_0 = 1\) nC at P; charges taken as positive", "Axes: P at the origin, +x to the right", KK) +
        F(COUL, (r"F_x = \sum F\cos\theta,\quad F_y = \sum F\sin\theta,\quad F = \sqrt{F_x^2 + F_y^2}", "")) +
        M(r"F_1 = \frac{(8.99\times10^9)(5)(10^{-9})}{2^2} = 11.24\ \text{N},\qquad F_2 = \frac{(8.99\times10^9)(10)(10^{-9})}{2^2} = 22.48\ \text{N}") +
        WHY("All positive → both forces are repulsions, pointing <em>away</em> from each source. q₁ is directly left of P → F₁ points along <strong>+x</strong>. "
            "q₂ is up-left at 60° → F₂ points down-right, 60° below +x.") +
        ST(1, "(i) Components.") + HOW +
        "<p class='sub'><strong>F₁</strong> lies along +x, so it is all horizontal:</p>" +
        M(r"F_{1x} = +11.24\ \text{N},\qquad F_{1y} = 0") +
        "<p class='sub'><strong>F₂</strong> points 60° below +x (straight away from q₂, which sits 60° above the line to q₁):</p>" +
        M(r"F_{2x} = +F_2\cos60^\circ = +(22.48)(0.5) = +11.24\ \text{N} // (\text{right})") +
        M(r"F_{2y} = -F_2\sin60^\circ = -(22.48)(0.866) = -19.46\ \text{N} // (\text{down})") +
        FIG(comp_fig(-60, "F₂ = 22.48 N", "F₂x = +11.24 N", "F₂y = −19.46 N", "60°",
                     ("cos 60° = 0.5", "sin 60° = 0.866")), "F₂ split into its parts.") +
        M(r"F_x = F_{1x} + F_{2x} = 11.24 + 11.24 = 22.48\ \text{N},\qquad F_y = 0 + (-19.46) = -19.46\ \text{N}") +
        ST(2, "(ii) Resultant:") +
        M(r"F = \sqrt{22.48^2 + 19.46^2} = 29.7\ \text{N},\qquad \theta = \tan^{-1}\frac{19.46}{22.48} = 40.9^\circ\ \text{below } +x") +
        FIG(d253_3()) +
        A(r"(i) \(F_x = +22.5\) N, \(F_y = -19.5\) N. (ii) \(F = 29.7\) N at 40.9° below the +x axis (319.1°)."), "math"))
    out.append(card(P, "4", "4", 5,
        G(r"\(q_1 = -10\) C at \(x = -3\) m, \(q_2 = +5\) C at \(x = +3\) m", "P at (0, 4) m", KK) +
        F(FIELD, (r"\vec E = \vec E_1 + \vec E_2", "")) +
        ST(1, r"Distances: \(r = \sqrt{3^2 + 4^2} = 5\) m for both.") +
        M(r"E_1 = \frac{(8.99\times10^9)(10)}{25} = 3.60\times10^{9}\ \text{N/C},\qquad E_2 = \frac{(8.99\times10^9)(5)}{25} = 1.80\times10^{9}\ \text{N/C}") +
        WHY("q₁ is negative → E₁ points <strong>toward</strong> q₁: down-left, along (−0.6, −0.8). "
            "q₂ is positive → E₂ points <strong>away</strong> from q₂: up-left, along (−0.6, +0.8). Both lean left; their vertical parts partly cancel.") +
        HOW + "<p class='sub'>From P to either charge is 3 m sideways and 4 m down, length 5 m, so cos θ = 3/5 = 0.6 and sin θ = 4/5 = 0.8 (θ = 53.1° from the horizontal).</p>" +
        M(r"E_{1x} = -E_1\cos\theta = -(3.60\times10^9)(0.6) = -2.16\times10^{9} // (\text{left})") +
        M(r"E_{1y} = -E_1\sin\theta = -(3.60\times10^9)(0.8) = -2.88\times10^{9} // (\text{down})") +
        M(r"E_{2x} = -E_2\cos\theta = -(1.80\times10^9)(0.6) = -1.08\times10^{9} // (\text{left})") +
        M(r"E_{2y} = +E_2\sin\theta = +(1.80\times10^9)(0.8) = +1.44\times10^{9} // (\text{up})") +
        FIG(comp_fig(233.13, "E₁ = 3.60×10⁹ N/C", "E₁x = −2.16×10⁹", "E₁y = −2.88×10⁹", "53.1°",
                     ("P → q₁: 3 m left, 4 m down, 5 m", "cos θ = 3/5 = 0.6", "sin θ = 4/5 = 0.8")), "E₁ split into its parts (E₂ is the same idea, pointing up-left).") +
        M(r"E_x = -2.16 - 1.08 = -3.24\times10^{9},\qquad E_y = -2.88 + 1.44 = -1.44\times10^{9}\ \text{N/C}") +
        M(r"E = \sqrt{3.24^2 + 1.44^2}\times10^9 = 3.54\times10^{9}\ \text{N/C},\qquad \theta = \tan^{-1}\frac{1.44}{3.24} = 24.0^\circ") +
        FIG(d253_4()) +
        A(r"(i) \(3.54\times10^9\) N/C; (ii) 24.0° below the −x axis (204° from +x), i.e. down and to the left."), "math"))
    out.append(card(P, "5", "5", 6,
        G(r"\(\vec p = (5\hat i + 2\hat j)\times10^{-30}\) C·m", r"\(\vec E = (5000\hat i + 6000\hat j)\) N/C") +
        F((r"\vec\tau = \vec p\times\vec E", "torque"), (r"U = -\vec p\cdot\vec E", "potential energy")) +
        ST(1, "(i) Both vectors lie in the xy-plane, so only the k̂ part survives:") +
        M(r"\vec\tau = (p_xE_y - p_yE_x)\,\hat k // = [(5)(6000) - (2)(5000)]\times10^{-30}\,\hat k = 2.0\times10^{-26}\,\hat k\ \text{N·m}") +
        WHY("+k̂ is out of the page: the torque turns p counter-clockwise, toward E (p is at 21.8°, E at 50.2°, so p has to rotate up by 28.4° to line up).") +
        ST(2, "(ii)") + M(r"U = -[(5)(5000) + (2)(6000)]\times10^{-30} = -3.7\times10^{-26}\ \text{J}") +
        FIG(d253_5()) +
        A(r"(i) \(\vec\tau = (2.0\times10^{-26}\ \text{N·m})\,\hat k\) — magnitude \(2.0\times10^{-26}\) N·m, along +z (out of the page). (ii) \(U = -3.7\times10^{-26}\) J."), "math"))
    out.append(card(P, "6", "6", 3,
        G(r"\(q = 6\) nC, \(d = 2\) m", "from the figure: +q at d, −q at d, −q at 2d, +q at d", KK) +
        F((r"V = \sum\frac{kq_i}{r_i}", "scalar sum — signs matter, directions don't")) +
        M(r"V = kq\left(\frac1d - \frac1d - \frac1{2d} + \frac1d\right) = \frac{kq}{2d} // = \frac{(8.99\times10^9)(6\times10^{-9})}{2(2)} = 13.5\ \text{V}") +
        FIG(d253_6()) +
        A(r"\(V = 13.5\) V."), "math"))
    out.append(card(P, "7", "7", 3,
        G(r"\(q_1 = q_2 = +2e\), \(q_3 = +3e\)", r"\(a = 5\ \mu\)m", "P is the midpoint of the hypotenuse (foot of the perpendicular from particle 3)", KK + ", " + EE) +
        F((r"V = \sum\frac{kq_i}{r_i}", ""), (r"r = \frac{a}{\sqrt2}", "the midpoint of the hypotenuse is equidistant from all three corners")) +
        M(r"r = \frac{5\times10^{-6}}{\sqrt2} = 3.54\times10^{-6}\ \text{m}") +
        M(r"V = \frac{k(2e + 2e + 3e)}{r} // = \frac{(8.99\times10^9)(7)(1.6\times10^{-19})}{3.54\times10^{-6}} = 2.85\times10^{-3}\ \text{V}") +
        FIG(d253_7()) +
        A(r"\(V = 2.85\times10^{-3}\) V."), "math"))
    out.append(card(P, "8a", "8 (a)", 4,
        '<p>Put the dipole on the z-axis with its centre at the origin: +q at z = +d/2, −q at z = −d/2. P is on the axis at distance z.</p>' +
        ST(1, "Fields at P (both along the axis; + pushes away, − pulls toward):") +
        M(r"E = E_{(+)} - E_{(-)} = \frac{1}{4\pi\varepsilon_0}\frac{q}{(z - \frac d2)^2} - \frac{1}{4\pi\varepsilon_0}\frac{q}{(z + \frac d2)^2}") +
        ST(2, r"Factor out \(z^2\):") +
        M(r"E = \frac{q}{4\pi\varepsilon_0 z^2}\left[\left(1 - \frac{d}{2z}\right)^{-2} - \left(1 + \frac{d}{2z}\right)^{-2}\right]") +
        ST(3, r"For \(z \gg d\), use \((1 \pm x)^{-2} \approx 1 \mp 2x\):") +
        M(r"E \approx \frac{q}{4\pi\varepsilon_0 z^2}\left[\left(1 + \frac dz\right) - \left(1 - \frac dz\right)\right] = \frac{q}{4\pi\varepsilon_0 z^2}\cdot\frac{2d}{z}") +
        M(r"E = \frac{1}{2\pi\varepsilon_0}\frac{qd}{z^3} = \frac{1}{2\pi\varepsilon_0}\frac{p}{z^3}") +
        FIG(d253_8a()) +
        A(r"\(E = \dfrac{1}{2\pi\varepsilon_0}\dfrac{qd}{z^3}\), along the dipole axis (in the direction of \(\vec p\)); it falls off as 1/z³."), "derive"))
    out.append(card(P, "8b", "8 (b)", 4,
        ST(1, r"In a uniform field the forces on the ends are \(+q\vec E\) and \(-q\vec E\): equal and opposite, so the net force is zero.") +
        ST(2, r"Each force has a lever arm \((d/2)\sin\theta\) about the centre, and both turn the dipole the same way:") +
        M(r"\tau = F\frac d2\sin\theta + F\frac d2\sin\theta = qE\,d\sin\theta = pE\sin\theta") +
        ST(3, r"The torque is perpendicular to the plane of \(\vec p\) and \(\vec E\) and turns \(\vec p\) toward \(\vec E\) — exactly the cross product:") +
        M(r"\vec\tau = \vec p\times\vec E") +
        ST(4, "Conditions:") + M(r"\tau_{max} = pE\ \ (\theta = 90^\circ),\qquad \tau = 0\ \ (\theta = 0^\circ \text{ or } 180^\circ)") +
        FIG(d253_8b()) +
        A(r"\(\vec\tau = \vec p\times\vec E\), \(|\tau| = pE\sin\theta\): maximum pE when p ⊥ E; zero when p is parallel or antiparallel to E."), "derive"))
    out.append(card(P, "9a", "9 (a)", 4,
        ST(1, r"A positive test charge \(q_0\) moves through \(d\vec s\) in a field \(\vec E\). The field's force is \(q_0\vec E\), so the work done on it is") +
        M(r"dW = \vec F\cdot d\vec s = q_0\vec E\cdot d\vec s") +
        ST(2, "Add up the work along the whole path from i to f:") +
        M(r"W = q_0\int_i^f \vec E\cdot d\vec s") +
        ST(3, r"The potential difference is the work per unit charge with a minus sign, \(V_f - V_i = -W/q_0\):") +
        M(r"V_f - V_i = -\int_i^f \vec E\cdot d\vec s") +
        FIG(d253_9a()) +
        A(r"\(V_f - V_i = -\displaystyle\int_i^f \vec E\cdot d\vec s\). Moving along \(\vec E\) makes the integral positive, so V decreases in the direction of the field."), "derive"))
    out.append(card(P, "9b", "9 (b)", 4,
        ST(1, r"Start from \(V_f - V_i = -\int_i^f \vec E\cdot d\vec s\). Take the test charge from P (distance R) straight out to infinity, along the field line:") +
        M(r"\vec E\cdot d\vec s = E\,dr,\qquad E = \frac{1}{4\pi\varepsilon_0}\frac{q}{r^2}") +
        ST(2, r"Set \(V_f = V(\infty) = 0\) and \(V_i = V\):") +
        M(r"0 - V = -\frac{q}{4\pi\varepsilon_0}\int_R^\infty\frac{dr}{r^2} = -\frac{q}{4\pi\varepsilon_0}\left[-\frac1r\right]_R^\infty = -\frac{q}{4\pi\varepsilon_0}\frac1R") +
        ST(3, r"So, renaming R as r:") + M(r"V = \frac{1}{4\pi\varepsilon_0}\frac{q}{r}") +
        FIG(d253_9b()) +
        A(r"\(V = \dfrac{1}{4\pi\varepsilon_0}\dfrac qr\) — positive for a positive charge, negative for a negative one, and zero at infinity."), "derive"))
    meta = dict(title="Final Exam — Fall 2025 (253)", sub="PHY-2105 • Full marks 40 • 2 hours • Q1–Q7 compulsory, then Q8 or Q9",
                toc=[(x, x) for x in ("1a", "1b", "1c", "2", "3", "4", "5", "6", "7", "8a", "8b", "9a", "9b")])
    return meta, out


# ================================================================== PAPER 252
def reuse(paper_fn, part):
    """Solution body of an identical question already solved on another paper."""
    _, cards = paper_fn()
    tag = '<details open><summary>📝 Solution</summary>'
    for c in cards:
        if f'id="q{part}"' in c:
            return c[c.index(tag) + len(tag):c.rindex("</details>")]
    raise KeyError(part)


def d252_1a():
    d = D(360, 170, "Between unlike charges both fields point the same way")
    y = 70
    d.line(30, y, 330, y, "ln", 1)
    d.charge(70, y, 1, r=12); d.charge(290, y, -1, r=12)
    d.text(70, y + 28, "+q", "txt", 11, bold=True); d.text(290, y + 28, "−q", "txt", 11, bold=True)
    x = 120
    d.dot(x, y, "txt", 4); d.text(x, y + 20, "a point between", "mut", 9.5)
    d.arrow(x, y - 14, x + 45, y - 14, "pos", 2.4, 8); d.text(x + 50, y - 10, "E₊ (away from +)", "pos", 9.5, "start", True)
    d.arrow(x, y - 32, x + 60, y - 32, "neg", 2.4, 8); d.text(x + 65, y - 28, "E₋ (toward −)", "neg", 9.5, "start", True)
    d.text(180, 120, "same direction → they add → E ≠ 0 anywhere between", "net", 10.5, bold=True)
    d.text(180, 140, "(a null point can exist only outside, beyond the smaller charge)", "mut", 9.5)
    return d.svg()


def d252_1b():
    d = D(380, 190, "Water dipoles flipping in the oscillating field of a microwave oven")
    for i, (dirn, th) in enumerate((("right", 0), ("left", 180))):
        cx = 95 + i * 190
        d.field(cx - 80, cx + 80, 22, 132, dirn, 3, 0.3)
        d.text(cx + (70 if dirn == "right" else -70), 16, "E →" if dirn == "right" else "← E", "fld", 10, "end" if dirn == "right" else "start", True)
        ox, oy = cx - 18 * cos(radians(th)), 78
        for a in (52.5, -52.5):
            ang = radians(th + a)
            hx, hy = ox + 28 * cos(ang), oy - 28 * sin(ang)
            d.line(ox, oy, hx, hy, "ln", 2)
            d.charge(hx, hy, 1, r=8)
        d.charge(ox, oy, -1, r=14)
        d.text(ox - 24 * cos(radians(th)), oy + 4, "O", "txt", 10.5, "middle", True)
        d.arrow(ox - 4 * cos(radians(th)), oy + 34, ox + 32 * cos(radians(th)), oy + 34, "net", 2, 7)
        d.text(ox + 14 * cos(radians(th)), oy + 50, "p lines up with E", "net", 9.5, bold=True)
    d.arrow(160, 78, 220, 78, "pink", 1.6, 7); d.arrow(220, 92, 160, 92, "pink", 1.6, 7)
    d.text(190, 176, "E reverses ~5×10⁹ times a second → dipoles keep flipping → friction → heat", "txt", 9.5, bold=True)
    return d.svg()


def d252_2a():
    d = D(320, 150, "Ball after electrons are pulled out")
    d.circle(90, 72, 48, "ln", 1.4, fill="pos", op=0.15)
    for x, y in ((70, 50), (105, 45), (60, 80), (95, 75), (120, 95), (80, 105), (115, 62)):
        d.charge(x, y, 1, r=6)
    d.text(90, 140, "q = +3.2×10⁻¹⁵ C", "txt", 10.5, bold=True)
    d.arrow(140, 50, 180, 30, "neg", 1.6, 6); d.charge(188, 26, -1, r=6)
    d.text(250, 72, "N = q / e", "net", 12, bold=True)
    d.text(250, 90, "= 2.0×10⁴ electrons removed", "mut", 10)
    return d.svg()


def d252_2b():
    d = D(420, 200, "Forces on q1 at the origin")
    X = lambda x: 130 + x * 28
    y0 = 46
    d.line(X(-0.5), y0, X(9.6), y0, "ln", 1.2)
    for x in range(0, 10):
        d.line(X(x), y0 - 3, X(x), y0 + 3, "ln", 1); d.text(X(x), y0 + 15, str(x), "mut", 9)
    for x, q, lab in ((0, 1, "q₁ +20 μC"), (4, -1, "q₂ −10 μC"), (9, 1, "q₃ +40 μC")):
        d.charge(X(x), y0, q, r=9)
        d.text(X(x), y0 - 15, lab, "txt", 9.5, bold=True)
    tx = X(0)
    rows = [(0.1124, "F₂ = 0.112 N (attracted toward q₂ →)"), (-0.0888, "F₃ = 0.0888 N (repelled by q₃ ←)")]
    s = 110 / 0.1124
    d.line(tx, y0 + 10, tx, 182, "mut", 1, "3,3")
    s = 90 / 0.1124
    for j, (f, t) in enumerate(rows):
        y = 100 + 34 * j
        d.arrow(tx, y, tx + f * s, y, "vec", 2.4, 7)
        d.text(tx + f * s / 2 + (60 if f > 0 else 40), y - 8, t, "vec", 9.5, "middle", True)
    d.arrow(tx, 172, tx + 0.0236 * s, 172, "net", 3, 8)
    d.text(tx + 0.0236 * s + 8, 176, "net 0.0236 N → (+x)", "net", 10, "start", True)
    return d.svg()


def d252_2c():
    d = D(320, 280, "Forces on q0 at the origin")
    w = W(d, 170, 130, 26)
    d.line(w.X(-4.8), w.Y(0), w.X(4.8), w.Y(0), "ln", 1); d.line(w.X(0), w.Y(-4.8), w.X(0), w.Y(4.6), "ln", 1)
    ch = [(-4, 0, 1), (0, 4, 2), (0, -4, -8)]
    vectors(w, ch, (0, 0), 1, None, "F = 2.82×10⁻⁸ N", px=86, offsets={1: -14, 2: 14}, lab_net=(w.X(0) + 72, w.Y(0) + 70))
    d.text(w.X(0) + 18, w.Y(0) - 8, "F₁", "vec", 10.5, "start", True)
    d.text(w.X(0) - 20, w.Y(0) + 34, "F₂", "vec", 10.5, "end", True)
    d.text(w.X(0) - 20, w.Y(0) + 86, "F₃", "vec", 10.5, "end", True)
    for (x, y, q), lab, pos in zip(ch, ("q₁ = +Q", "q₂ = +2Q", "q₃ = −8Q"), ((0, 26, "middle"), (16, 4, "start"), (-16, 4, "end"))):
        d.charge(*w.P((x, y)), 1 if q > 0 else -1, r=10)
        d.text(w.X(x) + pos[0], w.Y(y) + pos[1], lab, "txt", 10, pos[2], True)
    d.charge(*w.P((0, 0)), 1, r=6)
    d.text(w.X(-2), w.Y(0) - 8, "d", "gold", 10, bold=True); d.text(w.X(0) + 10, w.Y(2), "d", "gold", 10, "start", True)
    return d.svg()


def d252_3a():
    d = D(360, 150, "Torque on the dipole: parallel and perpendicular")
    for i, (th, t1, t2) in enumerate(((0, "p ∥ E", "τ = 0"), (90, "p ⊥ E", "τ = pE (maximum)"))):
        cx = 90 + i * 180
        d.field(cx - 80, cx + 80, 22, 112, "right", 3, 0.25)
        L = 30
        px, py = cx + L * cos(radians(th)), 67 - L * sin(radians(th))
        nx, ny = cx - L * cos(radians(th)), 67 + L * sin(radians(th))
        d.line(nx, ny, px, py, "ln", 3)
        d.arrow(px + 8, py, px + 34, py, "vec", 2, 6); d.arrow(nx - 8, ny, nx - 34, ny, "vec", 2, 6)
        d.charge(nx, ny, -1, r=8); d.charge(px, py, 1, r=8)
        if th == 90:
            d.arc(cx, 67, 18, 140, 40, "pink", 1.8, arrow_end=True)
        d.text(cx, 130, t1, "txt", 11, bold=True); d.text(cx, 145, t2, "net", 10.5, bold=True)
    d.text(352, 14, "E →", "fld", 10, "end", True)
    return d.svg()


def d252_3b():
    d = D(360, 180, "Dipole along z, field along x: perpendicular")
    o = (120, 120)
    d.arrow(*o, 300, 120, "vec", 2.6, 9); d.text(304, 124, "E = 24 î", "vec", 10.5, "start", True)
    d.arrow(*o, 120, 24, "net", 2.6, 9); d.text(128, 30, "p = 5.98×10⁻²⁸ k̂", "net", 10.5, "start", True)
    d.poly([(o[0], o[1] - 14), (o[0] + 14, o[1] - 14), (o[0] + 14, o[1])], "ln", 1, close=False)
    d.text(o[0] + 20, o[1] - 20, "90°", "gold", 10.5, "start", True)
    d.text(180, 160, "U = −p·E = −pE cos 90° = 0", "txt", 10.5, bold=True)
    d.text(40, 60, "z", "mut", 10); d.text(300, 140, "x", "mut", 10)
    return d.svg()


def d252_3c():
    d = D(330, 330, "Square: fields at the centre")
    w = W(d, 165, 160, 3900)
    a = 0.04
    h = a / 2
    corners = [(-h, h, 2, "+2q"), (h, h, 4, "+4q"), (h, -h, -2, "−2q"), (-h, -h, -3, "−3q")]
    d.poly([w.P((x, y)) for x, y, _, _ in corners], "ln", 1.4)
    for x, y, _, _ in corners:
        d.line(*w.P((x, y)), *w.P((0, 0)), "mut", 1, "4,4")
    vectors(w, [(x, y, q) for x, y, q, _ in corners], (0, 0), 1, ["E₁", "E₂", "E₃", "E₄"], "E = 1.81×10⁵ N/C", px=46,
            offsets={0: 8, 2: -8, 1: -8, 3: 8}, lab_net=(w.X(0) + 4, w.Y(-h) + 46))
    for x, y, q, lab in corners:
        d.charge(*w.P((x, y)), 1 if q > 0 else -1, r=11)
        d.text(w.X(x) + (16 if x > 0 else -16), w.Y(y) + (-14 if y > 0 else 22), lab, "txt", 10.5, "start" if x > 0 else "end", True)
    d.dim(*w.P((-h, h)), *w.P((h, h)), "4 cm", off=-22, tdy=-4)
    return d.svg()


def d252_4a():
    d = D(320, 230, "Two charges and the point P")
    w = W(d, 160, 190, 38)
    d.line(w.X(-2.5), w.Y(0), w.X(2.5), w.Y(0), "ln", 1); d.line(w.X(0), w.Y(0), w.X(0), w.Y(4.6), "ln", 1)
    for x in (-1, 1):
        d.line(*w.P((x, 0)), *w.P((0, 4)), "gold", 1.3, "4,3")
    d.text(w.X(-0.5) - 8, w.Y(2), "√17 m", "gold", 10, "end", True); d.text(w.X(0.5) + 8, w.Y(2), "√17 m", "gold", 10, "start", True)
    d.charge(*w.P((-1, 0)), -1, r=10); d.charge(*w.P((1, 0)), -1, r=10)
    d.text(w.X(-1), w.Y(0) + 24, "A: −q", "txt", 10, bold=True); d.text(w.X(1), w.Y(0) + 24, "B: −q", "txt", 10, bold=True)
    d.dot(*w.P((0, 4))); d.text(w.X(0) + 8, w.Y(4) - 6, "P (0, 4)", "txt", 10.5, "start", True)
    d.text(160, 14, "(ii) put Q = +q at A → V_A + V_B = 0", "net", 10, bold=True)
    return d.svg()


def d252_4b():
    d = D(300, 220, "Four charges on a circle")
    c, R = (150, 110), 80
    d.circle(*c, R, "ln", 1.2)
    for ang, q, lab in ((90, 1, "+20 nC"), (0, -1, "−30 nC"), (270, 1, "+30 nC"), (180, -1, "−20 nC")):
        x, y = c[0] + R * cos(radians(ang)), c[1] - R * sin(radians(ang))
        d.line(*c, x, y, "mut", 1, "4,4")
        d.charge(x, y, q, r=10)
        d.text(x + (16 if ang == 0 else -16 if ang == 180 else 14), y + (4 if ang in (0, 180) else (-12 if ang == 90 else 22)), lab, "txt", 10,
               "start" if ang in (0, 90, 270) else "end", True)
    d.dot(*c, "txt", 4)
    d.text(c[0] + 30, c[1] - 12, "r = 2 m", "gold", 10, "start", True)
    return d.svg()


def d252_4c():
    d = D(360, 120, "Point on the axis of the ammonia dipole")
    d.charge(50, 60, -1, r=8); d.charge(80, 60, 1, r=8)
    d.arrow(52, 84, 78, 84, "net", 1.8, 6); d.text(65, 100, "p", "net", 10, bold=True)
    d.line(90, 60, 340, 60, "ln", 1, "4,4")
    d.dot(300, 60, "txt", 4); d.text(300, 82, "P (θ = 0)", "txt", 10.5, bold=True)
    d.dim(65, 60, 300, 60, "r = 60.0 nm", off=-28)
    d.text(200, 108, "V = kp cos 0° / r² = kp / r²", "net", 10.5, bold=True)
    return d.svg()


def d252_6a():
    d = D(340, 210, "Rectangle: distances from the centre")
    w = W(d, 170, 105, 75)
    pts = [(-2, 0.5 * 2, 2, "+2q₁"), (0, 1, 4, "+4q₂"), (2, 1, -3, "−3q₁"), (-2, -1, -1, "−q₁"), (0, -1, 4, "+4q₂"), (2, -1, 2, "+2q₁")]
    d.poly([w.P((-2, 1)), w.P((2, 1)), w.P((2, -1)), w.P((-2, -1))], "ln", 1.2, dash="5,4")
    for x, y, q, lab in pts:
        d.line(*w.P((x, y)), *w.P((0, 0)), "mut", 1, "3,3")
        d.charge(*w.P((x, y)), 1 if q > 0 else -1, r=9)
        d.text(w.X(x), w.Y(y) + (-14 if y > 0 else 24), lab, "txt", 10, bold=True)
    d.dot(*w.P((0, 0)), "txt", 4)
    d.text(w.X(0) + 8, w.Y(0.5), "a/2", "net", 10, "start", True)
    d.text(w.X(1) + 6, w.Y(0.5) - 6, "(√5/2)a", "gold", 10, "start", True)
    return d.svg()


def paper_252():
    P = "252"
    out = []
    out.append(card(P, "1a", "1 (a)", 2, F((r"E = \frac{k|q|}{r^2}", "field of each charge: away from +, toward −"),) +
        WHY("Take any point between +q and −q. The field of +q points <strong>away</strong> from +q — toward −q. "
            "The field of −q points <strong>toward</strong> −q — also toward −q. Both point the same way, so they add; their sum can never be zero there.") +
        FIG(d252_1a()) +
        A("No. Between two opposite charges the two fields always point the same way (from + toward −), so E ≠ 0 at every point between them. "
          "A zero-field point can exist only on the axis <em>outside</em> the pair, beyond the charge of smaller magnitude (and nowhere if the magnitudes are equal)."), "short"))
    out.append(card(P, "1b", "1 (b)", 2,
        F((r"\vec\tau = \vec p\times\vec E,\qquad U = -\vec p\cdot\vec E", "torque and energy of a dipole in a field")) +
        ST(1, "A water molecule is a permanent dipole: its electrons crowd toward the oxygen, so the O side is negative and the H side positive (bond angle ~105°).") +
        ST(2, "The oven fills the food with an electric field that reverses direction about 2.45 billion times a second (it oscillates).") +
        ST(3, "Each time the field changes, it exerts a torque τ = pE sin θ that turns every water dipole toward the new field direction — so the molecules keep flipping back and forth.") +
        ST(4, "The rotating molecules jostle their neighbours and keep breaking and re-forming hydrogen bonds. That energy is shared out as random molecular motion — i.e. thermal energy — so the temperature rises.") +
        FIG(d252_1b()) +
        A("The microwave's rapidly reversing field keeps exerting torques on the water dipoles, making them rotate back and forth; the energy of this agitation turns into heat (random motion), warming the sandwich."), "short"))
    out.append(card(P, "1c", "1 (c)", 2, F((r"\tau = pE\sin\theta", ""),) +
        M(r"\tau = 0\ \ \text{when}\ \sin\theta = 0,\ \text{i.e. } \theta = 0^\circ \text{ or } 180^\circ") +
        WHY("At 0° and 180° the forces +qE and −qE act along the same line (the dipole axis), so they cancel without twisting. "
            "0° is stable (U = −pE, a nudge brings it back); 180° is unstable (U = +pE, a nudge flips it).") +
        FIG(d261_1b()) +
        A("When the dipole moment is parallel (θ = 0°) or antiparallel (θ = 180°) to the field."), "short"))
    out.append(card(P, "2a", "2 (a)", 2, G(r"\(q = +3.2\times10^{-15}\) C", EE) +
        F((r"N = \frac{q}{e}", "each electron removed leaves +e behind")) +
        M(r"N = \frac{3.2\times10^{-15}}{1.6\times10^{-19}} = 2.0\times10^{4}") +
        FIG(d252_2a()) +
        A(r"\(2.0\times10^4\) electrons were pulled out."), "math"))
    out.append(card(P, "2b", "2 (b)", 3,
        G(r"\(q_1 = +20\ \mu\)C at 0, \(q_2 = -10\ \mu\)C at 4 m, \(q_3 = +40\ \mu\)C at 9 m", KK) +
        F(COUL, (r"F = \sum F_i\ \text{(signs along x)}", "")) +
        M(r"F_{12} = \frac{(8.99\times10^9)(20\times10^{-6})(10\times10^{-6})}{4^2} = 0.112\ \text{N}") +
        M(r"F_{13} = \frac{(8.99\times10^9)(20\times10^{-6})(40\times10^{-6})}{9^2} = 0.0888\ \text{N}") +
        WHY("q₂ is negative → it <strong>attracts</strong> q₁ toward itself → +x. q₃ is positive like q₁ → it <strong>repels</strong> q₁ away from itself → −x.") +
        M(r"F = +0.112 - 0.0888 = +0.0236\ \text{N}") +
        FIG(d252_2b()) +
        A(r"(i) \(2.36\times10^{-2}\) N; (ii) along +x (toward q₂) — the closer attraction beats the farther repulsion."), "math"))
    out.append(card(P, "2c", "2 (c)", 3,
        G(r"\(q_1 = +Q\) at \((-d, 0)\), \(q_2 = +2Q\) at \((0, d)\), \(q_3 = -8Q\) at \((0, -d)\)", r"\(Q = 5\) nC, \(d = 4\) m, \(q_0 = +1\) nC at O", KK) +
        F(COUL, (r"F = \sqrt{F_x^2 + F_y^2}", "")) +
        M(r"F_1 = \frac{k(5\times10^{-9})(10^{-9})}{16} = 2.81\times10^{-9},\quad F_2 = 2F_1 = 5.62\times10^{-9},\quad F_3 = 8F_1 = 2.25\times10^{-8}\ \text{N}") +
        WHY("q₁ (+, on the left) repels q₀ → pushes it <strong>right</strong> (+x). q₂ (+, above) repels → pushes it <strong>down</strong>. "
            "q₃ (−, below) attracts → pulls it <strong>down</strong> too. So F₂ and F₃ add.") +
        "<p class='sub'>Each force lies along an axis, so one component is the whole force and the other is zero:</p>" +
        M(r"\vec F_1 = (+2.81\times10^{-9},\ 0),\quad \vec F_2 = (0,\ -5.62\times10^{-9}),\quad \vec F_3 = (0,\ -2.25\times10^{-8})\ \text{N}") +
        M(r"F_x = +2.81\times10^{-9}\ \text{N},\qquad F_y = -(5.62 + 22.5)\times10^{-9} = -2.81\times10^{-8}\ \text{N}") +
        M(r"F = \sqrt{(0.281)^2 + (2.81)^2}\times10^{-8} = 2.82\times10^{-8}\ \text{N},\qquad \theta = \tan^{-1}\frac{2.81}{0.281} = 84.3^\circ") +
        FIG(d252_2c()) +
        A(r"(i) \(F = 2.82\times10^{-8}\) N; (ii) 84.3° below the +x axis (275.7°) — almost straight down, slightly to the right."), "math"))
    out.append(card(P, "3a", "3 (a)", 3,
        G(r"\(\pm5e\), \(d = 0.4\) nm", r"\(E = 8\times10^{-9}\) N/C", EE) +
        F((r"p = qd", ""), (r"\tau = pE\sin\theta", "")) +
        M(r"p = (5)(1.6\times10^{-19})(4\times10^{-10}) = 3.2\times10^{-28}\ \text{C·m}") +
        ST(1, "(i) Parallel, θ = 0°:") + M(r"\tau = pE\sin0^\circ = 0") +
        ST(2, "(ii) Perpendicular, θ = 90°:") + M(r"\tau = pE = (3.2\times10^{-28})(8\times10^{-9}) = 2.56\times10^{-36}\ \text{N·m}") +
        FIG(d252_3a()) +
        A(r"(i) 0; (ii) \(2.56\times10^{-36}\) N·m (the maximum possible torque)."), "math"))
    out.append(card(P, "3b", "3 (b)", 3,
        G(r"\(p = 5.98\times10^{-30}\) C·m", "NH₄OH: 1 N (7 protons), 5 H (1 each), 1 O (8) → 20 protons (and 20 electrons)",
          r"(ii) \(\vec p = 5.98\times10^{-28}\,\hat k\) C·m, \(\vec E = 24\,\hat i\) N/C", EE) +
        F((r"d = \frac{p}{Ne}", "slide method: total charge Ne of one sign, separated by d"), (r"U = -\vec p\cdot\vec E", "")) +
        ST(1, "(i)") + M(r"d = \frac{5.98\times10^{-30}}{(20)(1.6\times10^{-19})} = 1.87\times10^{-12}\ \text{m}") +
        ST(2, "(ii) p is along k̂ and E along î, which are perpendicular:") + M(r"U = -(5.98\times10^{-28}\,\hat k)\cdot(24\,\hat i) = -(5.98\times10^{-28})(24)(\hat k\cdot\hat i) = 0") +
        FIG(d252_3b()) +
        FL("Part (ii) gives p = 5.98×10⁻²⁸ (not ×10⁻³⁰ as in the first line). It doesn't matter here: the dot product is zero for any size of p.") +
        A(r"(i) \(d = 1.87\times10^{-12}\) m; (ii) \(U = 0\) (p ⊥ E)."), "math"))
    out.append(card(P, "3c", "3 (c)", 3,
        G(r"Corners in order around the square: +2q, +4q, −2q, −3q; side \(a = 4\) cm", r"\(q = 2\) nC", KK) +
        F(FIELD, (r"r = \frac{a}{\sqrt2}", "corner to centre")) +
        ST(1, r"\(r = 0.04/\sqrt2 = 0.0283\) m, so one \(q\) at a corner gives") +
        M(r"E_0 = \frac{kq}{r^2} = \frac{(8.99\times10^9)(2\times10^{-9})}{(0.0283)^2} = 2.25\times10^{4}\ \text{N/C}") +
        WHY("Positive corners push the field away, negative corners pull it in. +2q (top-left) and −2q (bottom-right) both give a field pointing toward the bottom-right corner: "
            "2E₀ + 2E₀ = 4E₀. +4q (top-right) and −3q (bottom-left) both point toward the bottom-left corner: 4E₀ + 3E₀ = 7E₀. "
            "The two diagonals are at 90°.") +
        M(r"E = \sqrt{(4E_0)^2 + (7E_0)^2} = \sqrt{65}\,E_0 = 1.81\times10^{5}\ \text{N/C}") +
        "<p class='sub'>The same answer with x and y components (both diagonals are 45° from the horizontal, cos 45° = sin 45° = 0.707):</p>" + HOW +
        M(r"4E_0 = 8.99\times10^4\ \text{(down-right)} // x:\ (+8.99\times10^4)(0.707) = +6.36\times10^4 // y:\ -(8.99\times10^4)(0.707) = -6.36\times10^4") +
        M(r"7E_0 = 1.57\times10^5\ \text{(down-left)} // x:\ -(1.57\times10^5)(0.707) = -1.11\times10^5 // y:\ -(1.57\times10^5)(0.707) = -1.11\times10^5") +
        M(r"E_x = 6.36\times10^4 - 1.11\times10^5 = -4.77\times10^{4},\qquad E_y = -6.36\times10^4 - 1.11\times10^5 = -1.75\times10^{5}\ \text{N/C}") +
        M(r"E = \sqrt{(4.77\times10^4)^2 + (1.75\times10^5)^2} = 1.81\times10^{5}\ \text{N/C}") +
        M(r"\text{angle from the } -2q\text{ diagonal} = \tan^{-1}\frac{7}{4} = 60.3^\circ // \Rightarrow\ 254.7^\circ \text{ from } +x") +
        FIG(d252_3c(), "(i) The arrangement, with the four fields at the centre (to scale) and their sum.") +
        FL("The paper doesn't fix which corner holds which charge. They are placed in the order given, going round the square — state this.") +
        A(r"(ii) \(E = 1.81\times10^5\) N/C, pointing down and to the left at 254.7° from +x (15.3° to the left of straight down), toward the side between the −2q and −3q corners."), "math"))
    out.append(card(P, "4a", "4 (a)", 3,
        G(r"Charges \(-q\) with \(q = 2\times10^{-5}\) C at A \((-1, 0)\) and B \((1, 0)\)", "P at (0, 4) m", KK) +
        F((r"V = \sum\frac{kq_i}{r_i}", "scalar sum")) +
        ST(1, r"Distance from each charge: \(r = \sqrt{1^2 + 4^2} = \sqrt{17} = 4.12\) m.") +
        ST(2, "(i)") + M(r"V = 2\cdot\frac{k(-2\times10^{-5})}{\sqrt{17}} = -8.72\times10^{4}\ \text{V}\ \Rightarrow\ |V| = 8.72\times10^{4}\ \text{V}") +
        ST(3, "(ii) For V = 0 the new charge must cancel B's contribution. Both are at the same distance, so") +
        M(r"\frac{kQ}{\sqrt{17}} + \frac{k(-q)}{\sqrt{17}} = 0\ \Longrightarrow\ Q = +q = +2\times10^{-5}\ \text{C}") +
        FIG(d252_4a()) +
        A(r"(i) \(|V| = 8.72\times10^4\) V (V itself is negative); (ii) \(Q = +2\times10^{-5}\) C."), "math"))
    out.append(card(P, "4b", "4 (b)", 3,
        G("20, −30, 30, −20 nC, all on a circle of radius r = 2 m", KK) +
        F((r"V = \frac{k\sum q_i}{r}", "all at the same distance from the centre → add the charges")) +
        M(r"\sum q = 20 - 30 + 30 - 20 = 0\ \Longrightarrow\ V = \frac{k(0)}{2} = 0") +
        FIG(d252_4b()) +
        A("V = 0 at the centre."), "math"))
    out.append(card(P, "4c", "4 (c)", 3,
        G(r"\(p = 3\) D \(= 3(3.4\times10^{-30}) = 1.02\times10^{-29}\) C·m", r"\(r = 60.0\) nm on the axis (θ = 0)", KK) +
        F((r"V = \frac{kp\cos\theta}{r^2}", "dipole potential far away")) +
        M(r"V = \frac{(8.99\times10^9)(1.02\times10^{-29})}{(60.0\times10^{-9})^2} = 2.55\times10^{-5}\ \text{V}") +
        FIG(d252_4c()) +
        A(r"\(V = 2.55\times10^{-5}\) V."), "math"))
    out.append(card(P, "5a", "5 (a)", 4, "<p class='note'>Same derivation as Final 261 Q4 (a).</p>" + reuse(paper_261, "4a"), "derive"))
    out.append(card(P, "5b", "5 (b)", 4, "<p class='note'>Same derivation as Final 261 Q4 (b).</p>" + reuse(paper_261, "4b"), "derive"))
    out.append(card(P, "6a", "6 (a)", 4,
        G(r"Corners: \(+2q_1,\ -3q_1,\ -q_1,\ +2q_1\); middles of the long sides: \(+4q_2\) each", r"\(q_1 = q\), \(q_2 = 2q\); rectangle \(2a\times a\)") +
        F((r"V = \sum\frac{kq_i}{r_i}", "")) +
        ST(1, r"Corners are all \(\sqrt{a^2 + (a/2)^2} = \tfrac{\sqrt5}{2}a\) from the centre, and their charges add to") +
        M(r"2q_1 - 3q_1 - q_1 + 2q_1 = 0\ \Longrightarrow\ V_{corners} = 0") +
        ST(2, r"The two middle charges are \(a/2\) away:") +
        M(r"V = 2\cdot\frac{k(4q_2)}{a/2} = \frac{16kq_2}{a} = \frac{16k(2q)}{a} = \frac{32kq}{a} = \frac{8q}{\pi\varepsilon_0 a}") +
        FIG(d252_6a()) +
        A(r"\(V = \dfrac{32kq}{a} = \dfrac{8q}{\pi\varepsilon_0\,a}\) (only the two \(+4q_2\) charges contribute)."), "math"))
    out.append(card(P, "6b", "6 (b)", 4, "<p class='note'>Same derivation as Final 261 Q5 (b).</p>" + reuse(paper_261, "5b"), "derive"))
    meta = dict(title="Final Exam — Summer 2025 (252)", sub="PHY-2105 • Full marks 40 • 2 hours • Q1–Q4 compulsory, then Q5 or Q6",
                toc=[(x, x) for x in ("1a", "1b", "1c", "2a", "2b", "2c", "3a", "3b", "3c", "4a", "4b", "4c", "5a", "5b", "6a", "6b")])
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
        .how { background: rgba(168,85,247,0.08); border:1px solid rgba(168,85,247,0.35); border-radius:10px; padding:0.6rem 1.1rem; margin:0.8rem 0; font-size:0.93rem; }
        .how > strong:first-child { color:#c084fc; display:block; margin-bottom:0.2rem; }
        [data-theme="light"] .how > strong:first-child { color:#7e22ce; }
        .how .fx { text-align:center; }
        p.sub { margin-top:0.7rem; }
        @media (max-width: 700px) { .math-block, .fx { font-size: 0.86rem !important; } }
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


PAPERS = {"261": paper_261, "253": paper_253, "252": paper_252}

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    for p, fn in PAPERS.items():
        if which in ("all", p):
            build(p, fn)
