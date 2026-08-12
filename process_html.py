import re

html_file = 'quiz2-problems.html'
with open(html_file, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Delete examples
delete_examples = [2, 4, 7, 8, 9, 10, 11, 13, 38, 39, 40]
for ex in delete_examples:
    pattern = r'<div class="formula-card">\s*<h4>Example\s+' + str(ex) + r'\b.*?</div>\s*</details>\s*</div>'
    html = re.sub(pattern, '', html, flags=re.DOTALL)

# 2. Update solutions
solutions = {
    1: r"""<p><strong>Solution:</strong></p>
<p>This is a general guideline, no mathematical solution is required.</p>
<p>\( \text{Read textbook} \)</p>""",
    3: r"""<p><strong>Solution:</strong></p>
<p>This is a general guideline, no mathematical solution is required.</p>
<p>\( \text{Get help early} \)</p>""",
    5: r"""<p><strong>Solution:</strong></p>
<p>This is a general guideline, no mathematical solution is required.</p>
<p>\( \text{Read textbook} \)</p>""",
    6: r"""<p><strong>Solution:</strong></p>
<p>This is a general guideline, no mathematical solution is required.</p>
<p>\( \text{Do homework} \)</p>""",
    12: r"""<p><strong>Solution:</strong></p>
<p>Given, frequency \( f = 900 \text{ MHz} = 900 \times 10^6 \text{ Hz} \).</p>
<p>Speed of electromagnetic wave \( c = 3 \times 10^8 \text{ m/s} \).</p>
<p>Formula: \( \lambda = \frac{c}{f} \)</p>
<p>Substitution: \( \lambda = \frac{3 \times 10^8}{900 \times 10^6} \)</p>
<p>Result: \( \lambda = \frac{1}{3} \approx 0.333 \text{ m} \)</p>""",
    14: r"""<p><strong>Solution:</strong></p>
<p>Given amplitude \( A = 8 \).</p>
<p>At \( x_1 = 10 \text{ cm} \), \( y_1 = 6 \). Formula: \( y = A \sin(\phi - kx) \).</p>
<p>\( 6 = 8 \sin(\phi - 10k) \implies \phi - 10k = \sin^{-1}(0.75) \approx 0.848 \text{ rad} \).</p>
<p>At \( x_2 = 25 \text{ cm} \), \( y_2 = 4 \).</p>
<p>\( 4 = 8 \sin(\phi - 25k) \implies \phi - 25k = \sin^{-1}(0.5) = \frac{\pi}{6} \approx 0.5236 \text{ rad} \).</p>
<p>Subtracting the two equations: \( 15k = 0.848 - 0.5236 = 0.3244 \).</p>
<p>\( k = 0.0216 \text{ rad/cm} \).</p>
<p>Wavelength \( \lambda = \frac{2\pi}{k} = \frac{2\pi}{0.0216} \approx 290.5 \text{ cm} \).</p>""",
    15: r"""<p><strong>Solution:</strong></p>
<p>A damped harmonic oscillator is governed by \( \frac{d^2x}{dt^2} + 2\gamma \frac{dx}{dt} + \omega_0^2 x = 0 \).</p>
<p>1) For \( \omega / \gamma = 10 \): Underdamped, many oscillations before decaying.</p>
<p>2) For \( \omega / \gamma = 0.5 \): Overdamped, no oscillations, slow decay.</p>
<p>3) For \( \omega / \gamma = 0.03 \): Strongly overdamped.</p>
<p>\[ x(t) = A e^{-\gamma t} \cos(\omega t + \phi) \] (for underdamped case)</p>""",
    16: r"""<p><strong>Solution:</strong></p>
<p>Given \( m = 1 \text{ kg} \), initial amplitude \( A_0 = 12 \text{ cm} \).</p>
<p>At \( t = 2 \text{ minutes} = 120 \text{ s} \), \( A(t) = 6 \text{ cm} \).</p>
<p>Formula: \( A(t) = A_0 e^{-\frac{bt}{2m}} \)</p>
<p>Substitution: \( 6 = 12 e^{-\frac{b(120)}{2(1)}} \)</p>
<p>\( e^{60b} = 2 \implies 60b = \ln(2) \)</p>
<p>\( b = \frac{\ln(2)}{60} \approx 0.01155 \text{ kg/s} \).</p>""",
    17: r"""<p><strong>Solution:</strong></p>
<p>Given \( m = 0.2 \text{ kg} \), \( k = 80 \text{ N/m} \), \( b = 0.065 \text{ kg/s} \).</p>
<p>\( \omega_0 = \sqrt{\frac{k}{m}} = \sqrt{\frac{80}{0.2}} = 20 \text{ rad/s} \).</p>
<p>\( \gamma = \frac{b}{2m} = \frac{0.065}{0.4} = 0.1625 \text{ s}^{-1} \).</p>
<p>Since \( \gamma < \omega_0 \), this is underdamped oscillation.</p>
<p>\( \omega = \sqrt{\omega_0^2 - \gamma^2} = \sqrt{400 - 0.0264} \approx 20 \text{ rad/s} \).</p>
<p>Period \( T = \frac{2\pi}{\omega} \approx 0.314 \text{ s} \).</p>
<p>Time to drop amplitude to half: \( t = \frac{\ln(2)}{\gamma} = \frac{0.693}{0.1625} \approx 4.26 \text{ s} \).</p>""",
    18: r"""<p><strong>Solution:</strong></p>
<p>Assuming generic DHM equations, for mass \( m = 0.5 \text{ kg} \).</p>
<p>Formulas: \( \gamma = \frac{b}{2m} \), \( \omega = \sqrt{\omega_0^2 - \gamma^2} \).</p>
<p>Resonance frequency: \( \omega_r = \sqrt{\omega_0^2 - 2\gamma^2} \).</p>
<p>\[ x(t) = A_0 e^{-\gamma t} \cos(\omega t + \phi) \]</p>""",
    19: r"""<p><strong>Solution:</strong></p>
<p>Amplitude relation: \( A(t) = A_0 e^{-\gamma t} \).</p>
<p>After 6 minutes: \( A(6) = A_0 e^{-6\gamma} = \frac{1}{27} A_0 \implies e^{-6\gamma} = 3^{-3} \implies e^{-2\gamma} = 3^{-1} = \frac{1}{3} \).</p>
<p>After 2 minutes: \( A(2) = A_0 e^{-2\gamma} = A_0 \left( \frac{1}{3} \right) = \frac{A_0}{3} \).</p>
<p>Result: The amplitude was \( \frac{1}{3} \) of its initial value.</p>""",
    20: r"""<p><strong>Solution:</strong></p>
<p>Given \( L = 0.4 \text{ H} \), \( C = 0.0020 \mu\text{F} = 2 \times 10^{-9} \text{ F} \).</p>
<p>For oscillatory motion, \( R < 2\sqrt{\frac{L}{C}} \).</p>
<p>Max \( R = 2\sqrt{\frac{0.4}{2 \times 10^{-9}}} = 2\sqrt{2 \times 10^8} = 28284 \Omega \).</p>
<p>Resonant frequency: \( f = \frac{1}{2\pi\sqrt{LC}} = \frac{1}{2\pi\sqrt{0.4 \times 2 \times 10^{-9}}} \approx 5627 \text{ Hz} \).</p>""",
    21: r"""<p><strong>Solution:</strong></p>
<p>Given \( C = 0.1 \mu\text{F} = 10^{-7} \text{ F} \), \( L = 10 \text{ mH} = 0.01 \text{ H} \), \( R = 200 \Omega \).</p>
<p>Critical damping \( R_c = 2\sqrt{\frac{L}{C}} = 2\sqrt{\frac{0.01}{10^{-7}}} = 2\sqrt{10^5} \approx 632.4 \Omega \).</p>
<p>Since \( R = 200 \Omega < R_c \), the circuit is oscillatory (underdamped).</p>
<p>\( \omega_0 = \frac{1}{\sqrt{LC}} = \frac{1}{\sqrt{10^{-9}}} = 31622 \text{ rad/s} \).</p>
<p>\( \gamma = \frac{R}{2L} = \frac{200}{0.02} = 10000 \text{ s}^{-1} \).</p>
<p>\( \omega = \sqrt{\omega_0^2 - \gamma^2} = \sqrt{10^9 - 10^8} = 30000 \text{ rad/s} \).</p>
<p>Frequency \( f = \frac{\omega}{2\pi} \approx 4775 \text{ Hz} \).</p>"""
}

for ex, solution in solutions.items():
    div_id = f'solution-Ex{ex}'
    pattern = r'(<div id="' + div_id + r'".*?>).*?(</div>)'
    html = re.sub(pattern, r'\1\n' + solution.replace('\\', '\\\\') + r'\n\2', html, flags=re.DOTALL)

with open(html_file, 'w', encoding='utf-8') as f:
    f.write(html)

print("Done")
