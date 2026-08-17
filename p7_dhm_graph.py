#!/usr/bin/env python3
"""
Practice Sheet-2, Problem 7: displacement vs. time for a DHM at
omega/gamma = 10, 0.5 and 0.03.

Draws all three regimes from the same initial condition so they can be
compared, and marks the features you need to reproduce with a pen.

Standard library only -- writes an SVG, no matplotlib needed.
Run:  python3 p7_dhm_graph.py
"""

from math import exp, cos, sin, sqrt

# ---------------------------------------------------------------- physics --
# Hold the natural frequency fixed and let the ratio set the damping, so the
# three curves differ only in how hard they are damped.
OMEGA = 1.0                      # rad/s
RATIOS = [10.0, 0.5, 0.03]       # omega/gamma from the problem
A0 = 1.0                         # start pulled aside by A0, released from rest


def displacement(ratio):
    """Return x(t) for this omega/gamma, with x(0)=A0 and v(0)=0."""
    gamma = OMEGA / ratio

    if gamma < OMEGA:                                   # underdamped
        wd = sqrt(OMEGA**2 - gamma**2)
        return lambda t: A0 * exp(-gamma * t) * (
            cos(wd * t) + (gamma / wd) * sin(wd * t))

    if gamma == OMEGA:                                  # critically damped
        return lambda t: A0 * (1 + gamma * t) * exp(-gamma * t)

    s = sqrt(gamma**2 - OMEGA**2)                       # overdamped
    r1, r2 = -gamma + s, -gamma - s                     # r1 is the slow root
    return lambda t: A0 * (r2 * exp(r1 * t) - r1 * exp(r2 * t)) / (r2 - r1)


def envelope(ratio):
    """The e^{-gamma t} decay envelope (only meaningful when underdamped)."""
    gamma = OMEGA / ratio
    return lambda t: A0 * exp(-gamma * t)


def slow_time_constant(ratio):
    """Time constant that actually governs the return to equilibrium."""
    gamma = OMEGA / ratio
    if gamma <= OMEGA:
        return 1.0 / gamma                              # envelope decay
    s = sqrt(gamma**2 - OMEGA**2)
    return 1.0 / (gamma - s)                            # slow root dominates


# ------------------------------------------------------------------- style --
STYLE = {
    10.0: dict(color="#c0392b", dash="",         label="&#969;/&#947; = 10 &#8212; underdamped"),
    0.5:  dict(color="#1f6feb", dash="9,5",      label="&#969;/&#947; = 0.5 &#8212; overdamped"),
    0.03: dict(color="#178f52", dash="2.5,4",    label="&#969;/&#947; = 0.03 &#8212; heavily overdamped"),
}

W, H = 900, 1000
PANELS = [
    dict(key="a", x0=95, y0=100, w=740, h=330, tmax=20,  tstep=2,
         title="Panel A &#8212; the first 20 s"),
    dict(key="b", x0=95, y0=560, w=740, h=330, tmax=250, tstep=25,
         title="Panel B &#8212; same curves out to 250 s"),
]
YMIN, YMAX = -0.88, 1.08
SAMPLES = 1400


def make_panel(p):
    """Build the SVG fragment for one panel."""
    x0, y0, w, h = p["x0"], p["y0"], p["w"], p["h"]

    def px(t):
        return x0 + w * t / p["tmax"]

    def py(x):
        return y0 + h * (YMAX - x) / (YMAX - YMIN)

    out = []
    add = out.append

    add(f'<text x="{x0}" y="{y0 - 26}" class="title">{p["title"]}</text>')

    # grid
    t = 0.0
    while t <= p["tmax"] + 1e-9:
        add(f'<line x1="{px(t):.1f}" y1="{y0}" x2="{px(t):.1f}" y2="{y0 + h}" class="grid"/>')
        add(f'<text x="{px(t):.1f}" y="{y0 + h + 20}" class="tick">{t:g}</text>')
        t += p["tstep"]
    for x in (-0.5, 0.0, 0.5, 1.0):
        add(f'<line x1="{x0}" y1="{py(x):.1f}" x2="{x0 + w}" y2="{py(x):.1f}" class="grid"/>')
        add(f'<text x="{x0 - 12}" y="{py(x) + 4:.1f}" class="tick" text-anchor="end">{x:g}</text>')

    # axes
    add(f'<line x1="{x0}" y1="{py(0):.1f}" x2="{x0 + w + 14}" y2="{py(0):.1f}" class="axis"/>')
    add(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0 + h}" class="axis"/>')
    add(f'<text x="{x0 + w + 18}" y="{py(0) + 22:.1f}" class="axlabel">t (s)</text>')
    add(f'<text x="{x0 - 62}" y="{y0 + h / 2:.1f}" class="axlabel" '
        f'transform="rotate(-90 {x0 - 62} {y0 + h / 2:.1f})">x(t)</text>')

    # everything below is confined to the plot box
    clip = f'clip-{p["key"]}'
    add(f'<clipPath id="{clip}"><rect x="{x0}" y="{y0}" width="{w}" height="{h}"/></clipPath>')
    add(f'<g clip-path="url(#{clip})">')

    # curves
    for ratio in RATIOS:
        f = displacement(ratio)
        st = STYLE[ratio]
        pts = []
        for i in range(SAMPLES + 1):
            t = p["tmax"] * i / SAMPLES
            pts.append(f'{px(t):.2f},{py(f(t)):.2f}')
        dash = f' stroke-dasharray="{st["dash"]}"' if st["dash"] else ''
        add(f'<polyline points="{" ".join(pts)}" fill="none" '
            f'stroke="{st["color"]}" stroke-width="2.4"{dash}/>')

    # decay envelope, underdamped case only
    env = envelope(10.0)
    for sign in (1, -1):
        pts = []
        for i in range(SAMPLES + 1):
            t = p["tmax"] * i / SAMPLES
            pts.append(f'{px(t):.2f},{py(sign * env(t)):.2f}')
        add(f'<polyline points="{" ".join(pts)}" fill="none" stroke="#c0392b" '
            f'stroke-width="1.3" stroke-dasharray="5,5" opacity="0.75"/>')

    add('</g>')
    return out, px, py


def build_svg():
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="Helvetica, Arial, sans-serif">',
        '<style>'
        '.grid{stroke:#d8d8d8;stroke-width:1}'
        '.axis{stroke:#111;stroke-width:1.8}'
        '.tick{font-size:13px;fill:#444;text-anchor:middle}'
        '.axlabel{font-size:15px;fill:#111;text-anchor:middle;font-style:italic}'
        '.title{font-size:17px;fill:#111;font-weight:bold}'
        '.head{font-size:21px;fill:#111;font-weight:bold}'
        '.note{font-size:13.5px;fill:#333}'
        '.leg{font-size:14px;fill:#111}'
        '</style>',
        f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
        f'<text x="{W/2}" y="34" class="head" text-anchor="middle">'
        f'P7 &#8212; DHM displacement vs. time for &#969;/&#947; = 10, 0.5, 0.03</text>',
    ]

    for p in PANELS:
        frag, px, py = make_panel(p)
        out += frag

        if p["tmax"] == 20:      # annotate the short-time panel
            out.append(f'<text x="{px(11.2):.0f}" y="{py(0.47):.0f}" class="note" '
                       f'fill="#c0392b">envelope &#177;e^(&#8722;&#947;t)</text>')
            out.append(f'<text x="{px(6.4):.0f}" y="{py(-0.72):.0f}" class="note" '
                       f'fill="#c0392b">crosses the axis &#8594; it oscillates</text>')
            # the two overdamped remarks go in the clear band below the panel,
            # where they cannot land on top of a curve
            cap = p["y0"] + p["h"] + 52
            out.append(f'<text x="{p["x0"]}" y="{cap}" class="note">'
                       f'<tspan fill="#1f6feb">&#969;/&#947; = 0.5</tspan> and '
                       f'<tspan fill="#178f52">&#969;/&#947; = 0.03</tspan> never cross the axis '
                       f'&#8212; that is what overdamped looks like. At t = 20 s the '
                       f'<tspan fill="#178f52">green</tspan> curve has barely left its start.</text>')
        else:
            out.append(f'<text x="{px(70):.0f}" y="{py(0.72):.0f}" class="note" '
                       f'fill="#178f52">the heavily overdamped case needs '
                       f'~{slow_time_constant(0.03):.0f} s to relax</text>')

    # legend
    ly = 958
    lx = 95
    for ratio in RATIOS:
        st = STYLE[ratio]
        dash = f' stroke-dasharray="{st["dash"]}"' if st["dash"] else ''
        out.append(f'<line x1="{lx}" y1="{ly - 5}" x2="{lx + 34}" y2="{ly - 5}" '
                   f'stroke="{st["color"]}" stroke-width="2.6"{dash}/>')
        out.append(f'<text x="{lx + 42}" y="{ly}" class="leg">{st["label"]}</text>')
        lx += 268

    out.append('</svg>')
    return '\n'.join(out)


def build_panel_a_only():
    """Panel A alone, sized for embedding in the solutions page."""
    w, h = 780, 480
    panel = dict(key="embed", x0=80, y0=56, w=630, h=310, tmax=20, tstep=2,
                 title="Displacement vs. time (t = 0-20 s)")

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" font-family="Helvetica, Arial, sans-serif">',
        '<style>'
        '.grid{stroke:#d8d8d8;stroke-width:1}'
        '.axis{stroke:#111;stroke-width:1.8}'
        '.tick{font-size:13px;fill:#444;text-anchor:middle}'
        '.axlabel{font-size:15px;fill:#111;text-anchor:middle;font-style:italic}'
        '.title{font-size:16px;fill:#111;font-weight:bold}'
        '.note{font-size:13px;fill:#333}'
        '.leg{font-size:13.5px;fill:#111}'
        '</style>',
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>',
    ]

    frag, px, py = make_panel(panel)
    out += frag
    out.append(f'<text x="{px(11.2):.0f}" y="{py(0.47):.0f}" class="note" '
               f'fill="#c0392b">envelope &#177;e^(&#8722;&#947;t)</text>')
    out.append(f'<text x="{px(6.4):.0f}" y="{py(-0.78):.0f}" class="note" '
               f'fill="#c0392b">crosses the axis &#8594; oscillates</text>')

    ly = h - 14
    lx = panel["x0"]
    for ratio in RATIOS:
        st = STYLE[ratio]
        dash = f' stroke-dasharray="{st["dash"]}"' if st["dash"] else ''
        out.append(f'<line x1="{lx}" y1="{ly - 5}" x2="{lx + 30}" y2="{ly - 5}" '
                   f'stroke="{st["color"]}" stroke-width="2.4"{dash}/>')
        out.append(f'<text x="{lx + 36}" y="{ly}" class="leg">{st["label"]}</text>')
        lx += 230

    out.append('</svg>')
    return '\n'.join(out)


def print_key_numbers():
    print(f"natural frequency omega = {OMEGA:g} rad/s, released from rest at x = {A0:g}\n")
    header = f"{'omega/gamma':>12} {'gamma':>8} {'regime':>20} {'period':>10} {'relax time':>11}"
    print(header)
    print("-" * len(header))
    for r in RATIOS:
        gamma = OMEGA / r
        if gamma < OMEGA:
            wd = sqrt(OMEGA**2 - gamma**2)
            regime, period = "underdamped", f"{2 * 3.141592653589793 / wd:.2f} s"
        else:
            regime, period = "overdamped", "none"
        print(f"{r:>12g} {gamma:>8.3f} {regime:>20} {period:>10} "
              f"{slow_time_constant(r):>9.1f} s")


if __name__ == "__main__":
    out = "p7-damping-regimes.svg"
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(build_svg())
    print_key_numbers()
    print(f"\nwrote {out}")

    embed_out = "quiz2-graphs/graph-p7.svg"
    with open(embed_out, "w", encoding="utf-8") as fh:
        fh.write(build_panel_a_only())
    print(f"wrote {embed_out}")
