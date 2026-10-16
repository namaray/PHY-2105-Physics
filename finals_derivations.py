"""Build finals-derivations.html — every 'show that' from the past finals, most-asked first.

Run: python3 finals_derivations.py
Frequencies come from the 13 final papers in finals/ (221 is a midterm and has none);
three extra derivations come from the slides/notes and have not been asked yet.
"""
from finals_build import (M, FIG, RING_EXPLAIN, d253_8a, d261_5b, d253_8b, d261_1b, d261_4b, d253_9b, d261_4a,
                          d253_9a, d261_5a)
from visual_cheatsheet import f_def, p_system, p_grad, p_equal

TRIM = {"203": "Fall 2020", "211": "Spring 2021", "212": "Summer 2021", "213A": "Fall 2021 (A)", "213B": "Fall 2021 (B)",
        "231": "Spring 2023", "232": "Summer 2023", "233": "Fall 2023", "243": "Fall 2024", "251": "Spring 2025",
        "252": "Summer 2025", "253": "Fall 2025", "261": "Spring 2026"}
N_PAPERS = len(TRIM)


def step(label, html):
    return f'<div class="step"><span class="step-label">{label}</span>{html}</div>'


def result(tex, extra=""):
    return (f'<div class="result"><span class="result-label">Result</span>'
            f'<div class="math-block" style="margin-bottom:0;">\\[ {tex} \\]</div>{extra}</div>')


def tip(html):
    return f'<div class="tip"><strong>✍️ In the exam</strong> {html}</div>'


def asked(papers, phr):
    chips = "".join(f'<span class="chip" title="{TRIM[p]}">{p}</span>' for p in papers)
    quotes = "".join(f"<li>{q}</li>" for q in phr)
    return (f'<div class="asked"><div><strong>Asked in {len(papers)} of {N_PAPERS} papers:</strong> {chips}</div>'
            f'<div class="phr"><strong>How it was worded:</strong><ul>{quotes}</ul></div></div>')


# ------------------------------------------------------------------ the derivations, most-asked first
D = []

D.append(dict(id="d1", title="Electric field on the axis of a dipole", short=r"E = \dfrac{1}{2\pi\varepsilon_0}\dfrac{p}{z^3}",
    papers=["203", "212", "213A", "213B", "231", "232", "251", "253"],
    phr=["Find out the electric field due to an electric dipole. (203, 213A)",
         "Derive expression for electric field due to a dipole. Modify the expression when z ≫ d. (212, 213B)",
         "Show that the electric field on the axis of an electric dipole is E = qd / 2πε₀z³. (251, 253)",
         "Show that E = 2kp / z³ (232)"],
    fig=FIG(d253_8a()),
    body=step("Set up", "<p>Put the dipole on the z-axis with its centre at the origin: +q at z = +d/2 and −q at z = −d/2. P is on the axis a distance z from the centre.</p>") +
         step("Field of each charge at P", "<p>+q is closer (distance z − d/2) and pushes away from itself, along +z. −q is farther (z + d/2) and pulls toward itself, along −z:</p>" +
              M(r"E_{(+)} = \frac{1}{4\pi\varepsilon_0}\frac{q}{(z - \frac d2)^2},\qquad E_{(-)} = \frac{1}{4\pi\varepsilon_0}\frac{q}{(z + \frac d2)^2}")) +
         step("Superpose (they point opposite ways)", M(r"E = E_{(+)} - E_{(-)} = \frac{q}{4\pi\varepsilon_0}\left[\frac{1}{(z - \frac d2)^2} - \frac{1}{(z + \frac d2)^2}\right]")) +
         step("Common denominator", M(r"E = \frac{q}{4\pi\varepsilon_0}\,\frac{(z + \frac d2)^2 - (z - \frac d2)^2}{(z^2 - \frac{d^2}{4})^2} = \frac{q}{4\pi\varepsilon_0}\,\frac{2zd}{(z^2 - \frac{d^2}{4})^2}")) +
         step("Far away (z ≫ d)", r"<p>\(d^2/4\) is negligible next to \(z^2\), so \((z^2 - d^2/4)^2 \approx z^4\):</p>" +
              M(r"E \approx \frac{q}{4\pi\varepsilon_0}\frac{2zd}{z^4} = \frac{1}{2\pi\varepsilon_0}\frac{qd}{z^3}")) +
         result(r"E = \frac{1}{2\pi\varepsilon_0}\frac{p}{z^3} = \frac{2kp}{z^3},\qquad p = qd",
                "<p style='margin-top:.6rem;font-size:.92rem'>Direction: along the axis, the same way as \\(\\vec p\\) (from − to +). It falls off as 1/z³ — faster than a point charge's 1/z² because the two fields nearly cancel.</p>") +
         tip("Draw the diagram first (it carries marks). If the question says \"modify when z ≫ d\", show the exact line <em>and</em> the approximation. "
             "An alternative last step: factor out z² and use (1 ± x)⁻² ≈ 1 ∓ 2x — both are accepted.")))

D.append(dict(id="d2", title="Electric potential of a dipole", short=r"V = \dfrac{1}{4\pi\varepsilon_0}\dfrac{p\cos\theta}{r^2}",
    papers=["211", "213A", "213B", "231", "251", "252", "261"],
    phr=["Find out the electric potential due to an electric dipole. Rewrite the case if the electric charge is continuous. (211)",
         "Find the electrical potential for a dipole. (213B)",
         "Show that, at a distance r from an electric dipole with dipole moment p = qd, V = (1/4πε₀) p cos θ / r². Draw proper diagram. (231, 251, 252, 261)"],
    fig=FIG(d261_5b()),
    body=step("Superpose the two potentials", r"<p>Potential is a scalar, so just add: +q at distance \(r_{(+)}\), −q at \(r_{(-)}\).</p>" +
              M(r"V = \frac{1}{4\pi\varepsilon_0}\left(\frac{q}{r_{(+)}} - \frac{q}{r_{(-)}}\right) = \frac{q}{4\pi\varepsilon_0}\,\frac{r_{(-)} - r_{(+)}}{r_{(-)}\,r_{(+)}}")) +
         step("Far away (r ≫ d)", "<p>The two lines to P are almost parallel. The extra distance to −q is the projection of d on that line, and the product is about r²:</p>" +
              M(r"r_{(-)} - r_{(+)} \approx d\cos\theta,\qquad r_{(-)}\,r_{(+)} \approx r^2")) +
         step("Substitute and use p = qd", M(r"V = \frac{q}{4\pi\varepsilon_0}\frac{d\cos\theta}{r^2}")) +
         result(r"V = \frac{1}{4\pi\varepsilon_0}\frac{p\cos\theta}{r^2}",
                "<p style='margin-top:.6rem;font-size:.92rem'>θ is measured from the dipole axis. On the axis (θ = 0): V = kp/r². On the perpendicular bisector (θ = 90°): V = 0. Behind (θ = 180°): V = −kp/r².</p>") +
         step("If the charge is continuous (211)", r"<p>Split the charge into elements \(dq\), each a point charge, and add up the scalars:</p>" +
              M(r"dV = \frac{1}{4\pi\varepsilon_0}\frac{dq}{r}\ \Longrightarrow\ V = \frac{1}{4\pi\varepsilon_0}\int\frac{dq}{r}")) +
         tip("State the approximation r ≫ d out loud and mark d cos θ on your diagram — that projection is the key step the marker looks for.")))

D.append(dict(id="d3", title="Torque on a dipole: τ = p × E", short=r"\vec\tau = \vec p\times\vec E,\ \ \tau = pE\sin\theta",
    papers=["203", "213A", "232", "243", "253"],
    phr=["Establish a relation between torque τ, electric dipole moment p and electric field E. (203, 213A)",
         "If two charges behave like a dipole, show that the moment of force is τ = p × E. Calculate the angles for maximum and minimum torque. (232)",
         "Show that the torque experienced by a dipole in the electric field is given by the cross product. Draw and discuss the condition for maximum torque. (243, 253)"],
    fig=FIG(d253_8b()) + FIG(d261_1b(), "Torque is zero at 0° and 180°, maximum at 90°."),
    body=step("Forces", r"<p>In a uniform field \(\vec E\), the +q end feels \(+q\vec E\) and the −q end feels \(-q\vec E\). Equal and opposite → <strong>no net force</strong>.</p>") +
         step("Lever arms", r"<p>Take moments about the centre. Each force acts at distance d/2, and its perpendicular lever arm is \((d/2)\sin\theta\), θ being the angle between \(\vec p\) and \(\vec E\). Both turn the dipole the same way, so they add:</p>" +
              M(r"\tau = F\frac d2\sin\theta + F\frac d2\sin\theta = (qE)\,d\sin\theta")) +
         step("Use p = qd", M(r"\tau = pE\sin\theta")) +
         step("Vector form", r"<p>The torque is perpendicular to the plane of \(\vec p\) and \(\vec E\) and turns \(\vec p\) toward \(\vec E\) — exactly the right-hand rule for a cross product:</p>") +
         result(r"\vec\tau = \vec p\times\vec E,\qquad |\tau| = pE\sin\theta",
                "<p style='margin-top:.6rem;font-size:.92rem'><strong>Maximum</strong> τ = pE at θ = 90° (p ⊥ E). <strong>Zero</strong> at θ = 0° (stable) and θ = 180° (unstable).</p>") +
         tip("Two diagrams win the marks: the dipole with both forces and the lever arm, and the three orientations (0°, 90°, 180°).")))

D.append(dict(id="d4", title="Potential energy of a dipole: U = −p · E", short=r"U = -\vec p\cdot\vec E = -pE\cos\theta",
    papers=["231", "233", "251", "252", "261"],
    phr=["Show that a potential energy U is associated with the orientation of the dipole moment in the field, U = −p·E. (231, 233, 252, 261)",
         "Calculate the condition for maximum and zero potential energy. (233, 252, 261)",
         "Show that U = −p·E. Draw the diagram and discuss the conditions of maximum potential energy. (251)"],
    fig=FIG(d261_4b()),
    body=step("Torque tries to reduce θ", M(r"\tau = -pE\sin\theta") +
              "<p>(The minus sign: the torque acts to <em>decrease</em> the angle between p and E.)</p>") +
         step("Work done by the field as θ₀ → θ", M(r"W = \int_{\theta_0}^{\theta}\tau\,d\theta = \int_{\theta_0}^{\theta}(-pE\sin\theta)\,d\theta = pE\left(\cos\theta - \cos\theta_0\right)")) +
         step("Potential energy", r"<p>\(\Delta U = -W\). Choose the zero of energy at \(\theta_0 = 90^\circ\) (\(\cos 90^\circ = 0\)):</p>" +
              M(r"U(\theta) - U(90^\circ) = -pE\cos\theta + pE\cos90^\circ\ \Longrightarrow\ U = -pE\cos\theta")) +
         result(r"U = -pE\cos\theta = -\vec p\cdot\vec E",
                "<p style='margin-top:.6rem;font-size:.92rem'><strong>Maximum</strong> +pE at θ = 180° (antiparallel, unstable). <strong>Zero</strong> at θ = 90°. <strong>Minimum</strong> −pE at θ = 0° (aligned, stable). "
                "Work by an external agent to turn it: W = U<sub>f</sub> − U<sub>i</sub>.</p>") +
         tip("Say why θ₀ = 90° is chosen (it makes U = 0 there). Sketch the U–θ curve; it answers the 'conditions' part at a glance.")))

D.append(dict(id="d5", title="Potential of a point charge (and of a group of charges)", short=r"V = \dfrac{1}{4\pi\varepsilon_0}\dfrac{q}{r},\ \ V = \sum\dfrac{kq_i}{r_i}",
    papers=["203", "213B", "231", "232", "253"],
    phr=["Find out the electric potential due to a group of point charges. (203)",
         "Find the electrical potential for a point charge. (213B)",
         "Show that the electric potential due to a single charged particle at a distance r is V = (1/4πε₀) q/r. Write down the formula for a group of point charges. (231, 253)",
         "Find out the electric potential due to a single charge. Modify your derived equation for n number of charges. (232)"],
    fig=FIG(d253_9b()) + FIG(p_equal(), "For a group, add the potentials as plain numbers (with signs)."),
    body=step("Start from the field", M(r"V_f - V_i = -\int_i^f \vec E\cdot d\vec s")) +
         step("Choose the path", r"<p>Move a test charge from P (distance R) straight out to infinity along a radial line, so \(\vec E\cdot d\vec s = E\,dr\) with \(E = \dfrac{1}{4\pi\varepsilon_0}\dfrac{q}{r^2}\).</p>") +
         step("Integrate, with V(∞) = 0", M(r"0 - V = -\frac{q}{4\pi\varepsilon_0}\int_R^\infty\frac{dr}{r^2} = -\frac{q}{4\pi\varepsilon_0}\left[-\frac1r\right]_R^\infty = -\frac{q}{4\pi\varepsilon_0 R}")) +
         result(r"V = \frac{1}{4\pi\varepsilon_0}\frac{q}{r}",
                "<p style='margin-top:.6rem;font-size:.92rem'>V has the same sign as q, and is zero at infinity.</p>") +
         step("Group of n point charges", "<p>Potential is a scalar, so the potentials of the individual charges simply add (superposition) — no components:</p>" +
              M(r"V = \sum_{i=1}^{n} V_i = \frac{1}{4\pi\varepsilon_0}\sum_{i=1}^{n}\frac{q_i}{r_i}")) +
         tip("Keep the sign of each q in the group sum. If asked to 'modify for n charges', the one-line superposition step is the whole answer.")))

D.append(dict(id="d6", title="Electric field of a charged ring (on its axis)", short=r"E = \dfrac{1}{4\pi\varepsilon_0}\dfrac{qz}{(z^2 + R^2)^{3/2}}",
    papers=["213B", "243", "252", "261"],
    phr=["Derive expression for electric field for a charged ring. Modify the expression when z ≫ R and z = 0. (213B)",
         "Show that the electric field due to a charged ring at large distance is … (243)",
         "Show that the electric field at a point due to a uniformly distributed infinite line charge or ring charge is E = qz / 4πε₀(z² + R²)^{3/2}. (252, 261)"],
    fig=RING_EXPLAIN + FIG(d261_4a()),
    body=step("Element of the ring", r"<p>Split the ring (radius R, charge q, \(\lambda = q/2\pi R\)) into elements \(ds\) with \(dq = \lambda\,ds\). Each is a point charge a distance \(r = \sqrt{z^2 + R^2}\) from P:</p>" +
              M(r"dE = \frac{1}{4\pi\varepsilon_0}\frac{\lambda\,ds}{z^2 + R^2}")) +
         step("Symmetry", r"<p>The element directly opposite gives an equal \(dE\) whose sideways part points the other way. All sideways (\(dE\sin\theta\)) parts cancel; only the axial parts \(dE\cos\theta\) add, with</p>" +
              M(r"\cos\theta = \frac zr = \frac{z}{(z^2 + R^2)^{1/2}}")) +
         step("Add round the ring", M(r"E = \oint dE\cos\theta = \frac{1}{4\pi\varepsilon_0}\frac{z\lambda}{(z^2 + R^2)^{3/2}}\oint ds = \frac{1}{4\pi\varepsilon_0}\frac{z\lambda(2\pi R)}{(z^2 + R^2)^{3/2}}") +
              r"<p>and \(\lambda(2\pi R) = q\).</p>") +
         result(r"E = \frac{1}{4\pi\varepsilon_0}\frac{qz}{(z^2 + R^2)^{3/2}}") +
         step("Limits", M(r"z = 0:\ \ E = 0 // (\text{every element is cancelled by the opposite one})") +
              M(r"z \gg R:\ \ (z^2 + R^2)^{3/2} \approx z^3\ // \Rightarrow\ E \approx \frac{1}{4\pi\varepsilon_0}\frac{q}{z^2} // (\text{looks like a point charge})")) +
         tip("The symmetry sentence (sideways parts cancel) is worth marks on its own — write it explicitly. Note the papers' wording \"infinite line charge or ring charge\": the formula is the <em>ring</em> one.")))

D.append(dict(id="d7", title="Potential difference from the field: V_f − V_i = −∫ E · ds", short=r"V_f - V_i = -\int_i^f\vec E\cdot d\vec s",
    papers=["233", "251", "253"],
    phr=["Show that the electric potential difference between two points i and f is V_f − V_i = −∫ E·ds = −Ed. (233)",
         "Draw proper diagram and show that V_f − V_i = −∫ E·ds. (251, 253)"],
    fig=FIG(d253_9a()),
    body=step("Work on a test charge", r"<p>A positive test charge \(q_0\) moves through \(d\vec s\) in a field \(\vec E\). The field's force is \(q_0\vec E\), so</p>" +
              M(r"dW = \vec F\cdot d\vec s = q_0\,\vec E\cdot d\vec s")) +
         step("Whole path", M(r"W = q_0\int_i^f\vec E\cdot d\vec s")) +
         step("Potential difference = −work per unit charge", M(r"V_f - V_i = -\frac{W}{q_0}")) +
         result(r"V_f - V_i = -\int_i^f\vec E\cdot d\vec s") +
         step("Uniform field (233 asks for this too)", r"<p>Move a distance d along a uniform \(\vec E\): \(\vec E\cdot d\vec s = E\,ds\), and E comes out of the integral:</p>" +
              M(r"V_f - V_i = -E\int_i^f ds = -Ed")) +
         tip("Mention that the result is path-independent (the electrostatic force is conservative), and that V decreases along the direction of E.")))

D.append(dict(id="d8", title="Potential of a line of charge (rod of length L)", short=r"V = \dfrac{\lambda}{4\pi\varepsilon_0}\ln\left[\dfrac{L + (L^2 + d^2)^{1/2}}{d}\right]",
    papers=["212", "213B", "261"],
    phr=["Find the electrical potential due to a line of charges. (212)",
         "Find out electric potential at a point P, distance r from a charged wire of length L. (213B)",
         "Show that the electric potential V due to a continuous charge distribution of length L is … (261)"],
    fig=FIG(d261_5a()),
    body=step("Set up", r"<p>A thin rod of length L along the x-axis from 0 to L carries uniform charge density λ. P is a distance d from the left end, on the perpendicular through that end.</p>") +
         step("Element", r"<p>The element \(dx\) at x carries \(dq = \lambda\,dx\) and is \(r = \sqrt{x^2 + d^2}\) from P:</p>" +
              M(r"dV = \frac{1}{4\pi\varepsilon_0}\frac{\lambda\,dx}{\sqrt{x^2 + d^2}}")) +
         step("Integrate along the rod", r"<p>Using \(\displaystyle\int\frac{dx}{\sqrt{x^2+d^2}} = \ln\left(x + \sqrt{x^2+d^2}\right)\):</p>" +
              M(r"V = \frac{\lambda}{4\pi\varepsilon_0}\Big[\ln\big(x + \sqrt{x^2+d^2}\big)\Big]_0^L // = \frac{\lambda}{4\pi\varepsilon_0}\Big[\ln\big(L + \sqrt{L^2+d^2}\big) - \ln d\Big]")) +
         result(r"V = \frac{\lambda}{4\pi\varepsilon_0}\ln\left[\frac{L + (L^2+d^2)^{1/2}}{d}\right]") +
         tip("No components are needed — potential is a scalar. Quote the standard integral; you aren't expected to derive it.")))

D.append(dict(id="d9", title="Electric field of a point charge (from Coulomb's law)", short=r"\vec E = \dfrac{1}{4\pi\varepsilon_0}\dfrac{q}{r^2}\,\hat r",
    papers=["232"],
    phr=["Derive the equation of electric field at a certain distance from a point charge. Write the vector form of your derived equation. (232)"],
    fig=FIG(f_def()),
    body=step("Coulomb's law on a test charge", r"<p>Place a small positive test charge \(q_0\) a distance r from q:</p>" +
              M(r"\vec F = \frac{1}{4\pi\varepsilon_0}\frac{q\,q_0}{r^2}\,\hat r")) +
         step("Definition of the field", M(r"\vec E = \frac{\vec F}{q_0}")) +
         result(r"\vec E = \frac{1}{4\pi\varepsilon_0}\frac{q}{r^2}\,\hat r,\qquad E = \frac{k|q|}{r^2}",
                "<p style='margin-top:.6rem;font-size:.92rem'>\\(\\hat r\\) points from q to the field point: away from a positive q, toward a negative q. For several charges, \\(\\vec E = \\sum\\vec E_i\\) (vector sum).</p>") +
         tip("Short but easy marks: Coulomb's law → divide by q₀ → vector form with r̂ → direction rule.")))

FROM_NOTES = []
FROM_NOTES.append(dict(id="n1", title="Potential energy of a system of point charges", short=r"U = \dfrac{1}{4\pi\varepsilon_0}\dfrac{q_1q_2}{r},\ \ U = \sum_{pairs}\dfrac{kq_iq_j}{r_{ij}}",
    fig=FIG(p_system()),
    body=step("Assemble the charges from infinity", r"<p>Bring \(q_1\) in first — no field yet, no work. Then bring \(q_2\) from infinity to a distance r from \(q_1\). The external agent's work is \(q_2\) times the potential of \(q_1\) there:</p>" +
              M(r"W = q_2V_1 = q_2\,\frac{1}{4\pi\varepsilon_0}\frac{q_1}{r}")) +
         step("That work is stored as U", M(r"U = W = \frac{1}{4\pi\varepsilon_0}\frac{q_1q_2}{r}")) +
         step("More charges", "<p>Each new charge does work against every charge already there, so add one term per <em>pair</em>:</p>" +
              M(r"U = \frac{1}{4\pi\varepsilon_0}\left(\frac{q_1q_2}{r_{12}} + \frac{q_1q_3}{r_{13}} + \frac{q_2q_3}{r_{23}}\right)")) +
         result(r"U = \sum_{\text{pairs}}\frac{1}{4\pi\varepsilon_0}\frac{q_iq_j}{r_{ij}}",
                "<p style='margin-top:.6rem;font-size:.92rem'>Like charges → U &gt; 0 (work was needed to push them together); unlike → U &lt; 0 (the system is bound).</p>")))

FROM_NOTES.append(dict(id="n2", title="Field from potential (potential gradient)", short=r"E_s = -\dfrac{dV}{ds}",
    fig=FIG(p_grad()),
    body=step("Move between two close equipotentials", r"<p>A test charge \(q_0\) moves \(ds\) at angle θ to \(\vec E\). The field's work, written two ways:</p>" +
              M(r"dW = q_0E\cos\theta\,ds\qquad\text{and}\qquad dW = -q_0\,dV")) +
         step("Equate", M(r"q_0E\cos\theta\,ds = -q_0\,dV\ \Longrightarrow\ E\cos\theta = -\frac{dV}{ds}")) +
         result(r"E_s = -\frac{dV}{ds}",
                "<p style='margin-top:.6rem;font-size:.92rem'>The component of E in any direction is minus the rate of change of V in that direction; E points the way V falls fastest. "
                "(The quizzes excluded gradient <em>applications</em>; the result itself is in the slides.)</p>")))

FROM_NOTES.append(dict(id="n3", title="Potential of any continuous charge distribution", short=r"V = \dfrac{1}{4\pi\varepsilon_0}\displaystyle\int\dfrac{dq}{r}",
    fig="",
    body=step("Treat each element as a point charge", M(r"dV = \frac{1}{4\pi\varepsilon_0}\frac{dq}{r}")) +
         step("Add (integrate) the scalars", M(r"V = \frac{1}{4\pi\varepsilon_0}\int\frac{dq}{r}") +
              r"<p>with \(dq = \lambda\,ds\) (line), \(\sigma\,dA\) (surface) or \(\rho\,dV\) (volume). Example: a ring of charge q, every element at \(r = \sqrt{z^2+R^2}\), gives \(V = \dfrac{1}{4\pi\varepsilon_0}\dfrac{q}{\sqrt{z^2+R^2}}\); the rod of length L is worked in derivation 8.</p>") +
         result(r"V = \frac{1}{4\pi\varepsilon_0}\int\frac{dq}{r}")))


def section(n, d, from_notes=False):
    badge = ('<span class="badge badge-notes">From the slides</span>' if from_notes else
             f'<span class="badge badge-freq">{len(d["papers"])}/{N_PAPERS} papers</span>')
    head = f'<section class="notes-section" id="{d["id"]}"><h2>{n}. {d["title"]} {badge}</h2>'
    meta = "" if from_notes else asked(d["papers"], d["phr"])
    return head + meta + f'<div class="formula-card">{d["fig"]}{d["body"]}</div></section>\n'


def build():
    src = open("final-261.html", encoding="utf-8").read()
    head = src[:src.index("    </style>")].replace("Final 261 Solutions — PHY-2105", "Finals Derivation Sheet — PHY-2105")
    css = r"""
        .excluded-box { background: rgba(239,68,68,0.08); border:1px solid rgba(239,68,68,0.28); border-radius:12px; padding:1.1rem 1.4rem; margin:1.2rem 0; }
        .excluded-box h4 { color:#ef4444; margin-bottom:0.4rem; }
        .badge-freq { background: rgba(239,68,68,0.16); color:#f87171; }
        .badge-notes { background: rgba(99,102,241,0.18); color:#818cf8; }
        [data-theme="light"] .badge-freq { color:#b91c1c; } [data-theme="light"] .badge-notes { color:#4338ca; }
        .step { margin: 0.9rem 0; padding-left: 1rem; border-left: 2px solid var(--border-color); }
        .step-label { color: var(--accent-color); font-weight: 600; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.4px; display:block; margin-bottom:0.3rem; }
        .result { background: rgba(34,197,94,0.10); border:1px solid rgba(34,197,94,0.3); border-radius:10px; padding:0.8rem 1.2rem; margin-top:1rem; }
        .result-label { color:#4ade80; font-weight:700; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.5px; }
        [data-theme="light"] .result-label { color:#15803d; }
        .tip { background: rgba(245,158,11,0.08); border:1px solid rgba(245,158,11,0.3); border-radius:10px; padding:0.6rem 1rem; margin-top:1rem; font-size:0.92rem; }
        .tip strong:first-child { color:#f59e0b; } [data-theme="light"] .tip strong:first-child { color:#b45309; }
        .asked { font-size:0.9rem; margin:0.4rem 0 0.8rem; }
        .asked .phr { color: var(--text-secondary); margin-top:0.4rem; } .asked .phr ul { margin:0.2rem 0 0 1.2rem; }
        .chip { display:inline-block; padding:0.1rem 0.5rem; margin:0.1rem; border-radius:6px; font-size:0.78rem; font-weight:600; background: var(--surface-color); border:1px solid var(--border-color); }
        table.rank { width:100%; border-collapse:collapse; font-size:0.92rem; margin:0.6rem 0; }
        table.rank th, table.rank td { padding:0.45rem 0.6rem; border-bottom:1px solid var(--border-color); text-align:left; vertical-align:middle; }
        table.rank th { color: var(--accent-color); }
        table.rank a { color: var(--text-primary); text-decoration:none; font-weight:600; } table.rank a:hover { color: var(--accent-color); }
        .bar { height:8px; border-radius:4px; background: linear-gradient(90deg,#ef4444,#f59e0b); display:inline-block; vertical-align:middle; }
        h2 .badge { vertical-align: middle; margin-left: 0.3rem; }
        @media (max-width: 700px) { .math-block { font-size: 0.86rem !important; } }
    </style>
</head>"""
    nav = ('<nav class="nav-bar"><a href="index.html" class="back-btn">← Back to Home</a><a href="finals-cheatsheet.html">Cheat Sheet</a>'
           '<a href="visual-cheatsheet.html">Visual Sheet</a><a href="final-261.html">Final 261</a><a href="final-253.html">Final 253</a>'
           '<a href="final-252.html">Final 252</a></nav>')
    rows = ""
    for i, d in enumerate(D, 1):
        n = len(d["papers"])
        last = max(d["papers"], key=lambda p: int(p[:3]))
        rows += (f'<tr><td>{i}</td><td><a href="#{d["id"]}">{d["title"]}</a><div style="font-size:.85rem">\\( {d["short"]} \\)</div></td>'
                 f'<td><span class="bar" style="width:{n * 12}px"></span> {n}</td><td>{last} <span style="color:var(--text-secondary);font-size:.82rem">({TRIM[last]})</span></td></tr>')
    for j, d in enumerate(FROM_NOTES, len(D) + 1):
        rows += (f'<tr><td>{j}</td><td><a href="#{d["id"]}">{d["title"]}</a><div style="font-size:.85rem">\\( {d["short"]} \\)</div></td>'
                 f'<td colspan="2" style="color:var(--text-secondary)">not asked yet — in the slides</td></tr>')
    intro = f"""
        <div class="warning-box">
            <h4>📌 How this sheet was made</h4>
            <p>I went through all {N_PAPERS} final papers in the folder (Fall 2020 → Spring 2026; 221 is a midterm with no derivations) and
            counted every "show that / derive / find out / establish" question on the current syllabus — Coulomb's law, electric field and
            electric potential. They are ordered <strong>most-asked first</strong>. The last three come from the slides and notes and haven't been asked yet.</p>
            <p style="margin-top:.6rem">Recent papers put the derivations in the last two questions (choose one), each with two 4-mark parts,
            and almost always pick from the <strong>dipole</strong> family (1–4) plus one potential derivation (5, 7 or 8) or the ring (6).</p>
        </div>
        <div class="excluded-box">
            <h4>🚫 Asked in older papers, but not on this trimester's syllabus</h4>
            <p>Gauss's law (flux through a cylinder, Coulomb's law from Gauss's law — 213A, 243), drift velocity and current density (203, 211),
            capacitors in series/parallel and AC power (211). These belonged to older course outlines that went beyond the three chapters you were taught.</p>
        </div>
        <div class="formula-card toc"><strong>Ranking</strong>
            <table class="rank"><tr><th>#</th><th>Derivation</th><th>Papers</th><th>Last asked</th></tr>{rows}</table></div>
"""
    body = ['<body><div class="container notes-container">', nav,
            '<header class="notes-header"><h1>🧾 Finals Derivation Sheet</h1>'
            '<p class="subtitle">PHY-2105 • Coulomb\'s Law · Electric Field · Electric Potential — every "show that", most-asked first</p></header>', intro,
            '<h2 class="part-header">Asked in past finals</h2>']
    body += [section(i, d) for i, d in enumerate(D, 1)]
    body.append('<h2 class="part-header">From the slides — not asked yet</h2>')
    body += [section(j, d, True) for j, d in enumerate(FROM_NOTES, len(D) + 1)]
    body.append('<footer><p>Made for PHY-2105 • Summer 2026</p></footer></div></body></html>')
    open("finals-derivations.html", "w", encoding="utf-8").write(head + css + "\n" + "".join(body))
    print(f"finals-derivations.html: {len(D)} asked + {len(FROM_NOTES)} from notes")


if __name__ == "__main__":
    build()
