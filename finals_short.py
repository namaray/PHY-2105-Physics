"""Build finals-derivations-short.html — the exam version: every derivation in a few lines.

Run: python3 finals_short.py
"""
from finals_build import d253_8a, d261_5b, d253_8b, d261_4b, d253_9b, d261_4a, d253_9a, d261_5a
from visual_cheatsheet import f_def, p_system, p_grad

# (id, title, how often, use-line, [math lines], result, conditions, diagram)
DERIVS = [
    ("s1", "Dipole field on the axis", "8/13", r"E = \frac{kq}{r^2},\ \ p = qd",
     [r"E = \frac{kq}{(z - \frac d2)^2} - \frac{kq}{(z + \frac d2)^2}",
      r"= kq\,\frac{2zd}{(z^2 - \frac{d^2}{4})^2}",
      r"\approx kq\,\frac{2zd}{z^4} = \frac{2kqd}{z^3}\qquad (z \gg d)"],
     r"E = \frac{1}{2\pi\varepsilon_0}\frac{p}{z^3}", "Along the axis, same direction as p.", d253_8a),
    ("s2", "Dipole potential", "7/13", r"V = \frac{kq}{r}",
     [r"V = \frac{kq}{r_+} - \frac{kq}{r_-} = kq\,\frac{r_- - r_+}{r_-\,r_+}",
      r"r_- - r_+ \approx d\cos\theta,\qquad r_-\,r_+ \approx r^2\qquad (r \gg d)",
      r"V = \frac{kqd\cos\theta}{r^2}"],
     r"V = \frac{1}{4\pi\varepsilon_0}\frac{p\cos\theta}{r^2}", "Axis (θ = 0): kp/r². Bisector (θ = 90°): 0.", d261_5b),
    ("s3", "Torque on a dipole", "5/13", r"F = qE,\ \ \tau = F\times\text{lever arm}",
     [r"\text{forces } +qE \text{ and } -qE\ \Rightarrow\ F_{net} = 0",
      r"\text{lever arm of each} = \tfrac d2\sin\theta",
      r"\tau = 2\,(qE)\,\tfrac d2\sin\theta = qEd\sin\theta = pE\sin\theta"],
     r"\vec\tau = \vec p\times\vec E", "Max pE at 90°. Zero at 0° and 180°.", d253_8b),
    ("s4", "Dipole potential energy", "5/13", r"\tau = pE\sin\theta,\ \ \Delta U = -W",
     [r"W = \int_{\theta_0}^{\theta}(-pE\sin\theta)\,d\theta = pE(\cos\theta - \cos\theta_0)",
      r"U - U_0 = -W = -pE(\cos\theta - \cos\theta_0)",
      r"\theta_0 = 90^\circ,\ U_0 = 0\ \Rightarrow\ U = -pE\cos\theta"],
     r"U = -pE\cos\theta = -\vec p\cdot\vec E", "Max +pE at 180°. Zero at 90°. Min −pE at 0°.", d261_4b),
    ("s5", "Potential of a point charge", "5/13", r"V_f - V_i = -\int\vec E\cdot d\vec s,\ \ E = \frac{kq}{r^2}",
     [r"0 - V = -\int_R^{\infty}\frac{kq}{r^2}\,dr",
      r"= -kq\left[-\frac1r\right]_R^{\infty} = -\frac{kq}{R}",
      r"\text{group: } V = \sum\frac{kq_i}{r_i}"],
     r"V = \frac{1}{4\pi\varepsilon_0}\frac{q}{r}", "Same sign as q. Zero at infinity.", d253_9b),
    ("s6", "Field of a charged ring", "4/13", r"dE = \frac{k\,dq}{r^2},\ \ r^2 = z^2 + R^2,\ \ \cos\theta = \frac zr",
     [r"\text{sideways parts cancel (symmetry)} \Rightarrow \text{keep } dE\cos\theta",
      r"dE\cos\theta = \frac{k\,dq}{z^2+R^2}\cdot\frac{z}{\sqrt{z^2+R^2}} = \frac{kz\,dq}{(z^2+R^2)^{3/2}}",
      r"E = \frac{kz}{(z^2+R^2)^{3/2}}\int dq"],
     r"E = \frac{1}{4\pi\varepsilon_0}\frac{qz}{(z^2+R^2)^{3/2}}", "z = 0: E = 0. z ≫ R: E ≈ kq/z².", d261_4a),
    ("s7", "V from the field", "3/13", r"dW = \vec F\cdot d\vec s,\ \ F = q_0E,\ \ \Delta V = -\frac{W}{q_0}",
     [r"dW = q_0\,\vec E\cdot d\vec s",
      r"W = q_0\int_i^f\vec E\cdot d\vec s",
      r"V_f - V_i = -\frac{W}{q_0}\qquad(\text{definition of } \Delta V)",
      r"= -\frac{q_0\int_i^f\vec E\cdot d\vec s}{q_0}\qquad(\text{put in } W;\ q_0 \text{ cancels})"],
     r"V_f - V_i = -\int_i^f\vec E\cdot d\vec s", "Uniform field: ΔV = −Ed.", d253_9a),
    ("s8", "Potential of a rod (length L)", "3/13", r"dV = \frac{k\,dq}{r},\ \ dq = \lambda\,dx,\ \ r = \sqrt{x^2+d^2}",
     [r"V = k\lambda\int_0^L\frac{dx}{\sqrt{x^2+d^2}}",
      r"= k\lambda\Big[\ln\big(x + \sqrt{x^2+d^2}\big)\Big]_0^L"],
     r"V = \frac{\lambda}{4\pi\varepsilon_0}\ln\left[\frac{L + \sqrt{L^2+d^2}}{d}\right]", "Bottom limit gives ln d; ln a − ln b = ln(a/b).", d261_5a),
    ("s9", "Field of a point charge", "1/13", r"F = \frac{kqq_0}{r^2},\ \ E = \frac{F}{q_0}",
     [r"\vec E = \frac{1}{q_0}\cdot\frac{kqq_0}{r^2}\,\hat r"],
     r"\vec E = \frac{1}{4\pi\varepsilon_0}\frac{q}{r^2}\,\hat r", "Away from +q, toward −q.", f_def),
    ("s10", "Energy of a system of charges", "slides", r"W = qV,\ \ V = \frac{kq}{r}",
     [r"\text{bring } q_1:\ W = 0;\quad \text{bring } q_2:\ W = \frac{kq_1q_2}{r_{12}}",
      r"\text{bring } q_3:\ W = \frac{kq_1q_3}{r_{13}} + \frac{kq_2q_3}{r_{23}}"],
     r"U = \sum_{\text{pairs}}\frac{kq_iq_j}{r_{ij}}", "One term per pair; keep the signs.", p_system),
    ("s11", "Field from potential", "slides", r"dW = q_0E\cos\theta\,ds,\ \ dW = -q_0\,dV",
     [r"q_0E\cos\theta\,ds = -q_0\,dV"],
     r"E_s = -\frac{dV}{ds}", "E points where V falls fastest.", p_grad),
    ("s12", "Potential of any continuous charge", "slides", r"dV = \frac{k\,dq}{r}",
     [r"V = \int dV"],
     r"V = \frac{1}{4\pi\varepsilon_0}\int\frac{dq}{r}", "dq = λ ds (line), σ dA (surface), ρ dV (volume).", None),
]


def card(n, d):
    id_, title, freq, use, lines, res, cond, fig = d
    badge = f'<span class="freq">{freq}{" papers" if "/" in freq else ""}</span>'
    maths = "".join(f'<div class="ln">\\( \\displaystyle {l} \\)</div>' for l in lines)
    pic = f'<div class="pic">{fig()}<p>Draw this</p></div>' if fig else ""
    return (f'<div class="dc" id="{id_}"><h3>{n}. {title} {badge}</h3>'
            f'<div class="body"><div class="txt"><p class="use"><b>Use:</b> \\( \\displaystyle {use} \\)</p>{maths}'
            f'<div class="res">\\( \\displaystyle {res} \\)</div><p class="cond">{cond}</p></div>{pic}</div></div>\n')


def build():
    src = open("final-261.html", encoding="utf-8").read()
    head = src[:src.index("    </style>")].replace("Final 261 Solutions — PHY-2105", "Derivations — Exam Version — PHY-2105")
    css = r"""
        .dc { background: var(--surface-color); border:1px solid var(--border-color); border-radius:12px; padding:0.9rem 1.1rem; margin:1rem 0; break-inside: avoid; }
        .dc h3 { color: var(--accent-color); font-size:1.08rem; margin-bottom:0.5rem; }
        .freq { font-size:0.72rem; font-weight:700; padding:0.15rem 0.55rem; border-radius:20px; background: rgba(239,68,68,0.15); color:#f87171; vertical-align:middle; margin-left:0.3rem; }
        [data-theme="light"] .freq { color:#b91c1c; }
        .body { display:grid; grid-template-columns: 1fr 260px; gap:1rem; align-items:start; }
        @media (max-width: 760px) { .body { grid-template-columns: 1fr; } }
        .use { font-size:0.92rem; color: var(--text-secondary); margin-bottom:0.3rem; }
        .ln { padding:0.35rem 0 0.35rem 0.7rem; border-left:3px solid var(--accent-color); margin:0.15rem 0; overflow-x:auto; overflow-y:hidden; }
        .res { background: rgba(34,197,94,0.12); border:1px solid rgba(34,197,94,0.35); border-radius:8px; padding:0.5rem 0.8rem; margin-top:0.6rem; overflow-x:auto; overflow-y:hidden; font-size:1.05rem; }
        .cond { font-size:0.88rem; color: var(--text-secondary); margin-top:0.4rem; }
        .pic { max-width:300px; margin:0 auto; width:100%; }
        .pic svg.dg { width:100%; height:auto; font-family: Inter, system-ui, sans-serif; }
        .pic p { text-align:center; font-size:0.78rem; color: var(--text-secondary); }
        .legend { font-size:0.9rem; color: var(--text-secondary); }
        @media print { .nav-bar, .theme-toggle, .background-elements { display:none !important; } .dc { border:1px solid #999; } }
    </style>
</head>"""
    nav = ('<nav class="nav-bar"><a href="index.html" class="back-btn">← Back to Home</a>'
           '<a href="finals-derivations.html">Full derivations (step by step)</a><a href="finals-cheatsheet.html">Cheat Sheet</a></nav>')
    body = ['<body><div class="container notes-container">', nav,
            '<header class="notes-header"><h1>⚡ Derivations — Exam Version</h1>'
            '<p class="subtitle">PHY-2105 Finals • each derivation in a few lines, most-asked first</p></header>',
            '<p class="legend">Write exactly this in the exam: draw the diagram, write the <b>Use</b> line, then the lines below it, then box the result. '
            'The red badge says how many of the 13 past finals asked it. Stuck on a line? The <a href="finals-derivations.html">full version</a> explains every step.</p>']
    body += [card(i, d) for i, d in enumerate(DERIVS, 1)]
    body.append('<footer><p>Made for PHY-2105 • Summer 2026</p></footer></div></body></html>')
    open("finals-derivations-short.html", "w", encoding="utf-8").write(head + css + "\n" + "".join(body))
    print(f"finals-derivations-short.html: {len(DERIVS)} derivations")


if __name__ == "__main__":
    build()
