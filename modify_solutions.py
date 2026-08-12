import re

html_path = '/home/angkon/Courses/Physics/quiz2-problems.html'
with open(html_path, 'r') as f:
    content = f.read()

solutions = {
    "P25": r"""<div id="solution-P25" style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1);">
<p><strong>Solution:</strong></p>
<p>Given: \( f = 500 \) Hz, \( v = 350 \) m/s.</p>
<p>Wavelength \( \lambda = \frac{v}{f} = \frac{350}{500} = 0.7 \) m.</p>
<p>(i) Phase difference \( \Delta \phi = \frac{2\pi}{\lambda} \Delta x \). For \( \Delta \phi = \frac{\pi}{3} \):<br>
\( \frac{\pi}{3} = \frac{2\pi}{0.7} \Delta x \implies \Delta x = \frac{0.7}{6} \approx 0.117 \) m.</p>
<p>(ii) Assuming the problem means times \( \Delta t = 1.00 \) ms apart:<br>
Phase difference \( \Delta \phi = \omega \Delta t = 2\pi f \Delta t = 2\pi (500) (1 \times 10^{-3}) = \pi \) rad.</p>
</div>""",

    "P26": r"""<div id="solution-P26" style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1);">
<p><strong>Solution:</strong></p>
<p>Given: \( f = 50 \) Hz, \( v_{wave} = 250 \) m/s, \( A = 25 \) cm \( = 0.25 \) m.</p>
<p>Maximum speed of the particle is given by \( v_{max} = A\omega \).</p>
<p>\( \omega = 2\pi f = 2\pi (50) = 100\pi \) rad/s.</p>
<p>\( v_{max} = 0.25 \times 100\pi = 25\pi \approx 78.54 \) m/s.</p>
</div>""",

    "P27": r"""<div id="solution-P27" style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1);">
<p><strong>Solution:</strong></p>
<p><em>(Note: The equation is missing from the problem description. Below are the generic steps based on a standard DHM equation \( x(t) = A e^{-bt/2m} \cos(\omega' t + \phi) \)).</em></p>
<p>Given \( m = 0.3 \) kg.</p>
<p>(i) Damping coefficient \( b \): Determine the exponential decay constant \( \gamma = \frac{b}{2m} \) from the equation, then \( b = 2m\gamma \).</p>
<p>(ii) Natural frequency \( \omega_0 \): Using the damped angular frequency \( \omega' \) from the cosine term, \( \omega_0 = \sqrt{\omega'^2 + \gamma^2} \). Natural frequency \( f_0 = \frac{\omega_0}{2\pi} \).</p>
<p>(iii) Force constant \( k \): Using \( \omega_0^2 = \frac{k}{m} \), we have \( k = m \omega_0^2 \).</p>
<p>(iv) Damping factor at \( t = 2 \) ms: Evaluate the exponential term \( e^{-\gamma t} \) at \( t = 0.002 \) s.</p>
</div>""",

    "P28": r"""<div id="solution-P28" style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1);">
<p><strong>Solution:</strong></p>
<p>Given: \( x_m = 20 \) cm \( = 0.2 \) m, \( m = 0.68 \) kg, \( k = 65000 \) dynes/cm \( = 65 \) N/m, \( b = 70 \) gm/s \( = 0.07 \) kg/s.</p>
<p>(i) Damping angular frequency \( \omega' \):<br>
\( \gamma = \frac{b}{2m} = \frac{0.07}{2 \times 0.68} \approx 0.0515 \) s\(^{-1}\).<br>
\( \omega_0 = \sqrt{\frac{k}{m}} = \sqrt{\frac{65}{0.68}} \approx 9.777 \) rad/s.<br>
\( \omega' = \sqrt{\omega_0^2 - \gamma^2} \approx \sqrt{95.588 - 0.00265} \approx 9.777 \) rad/s.</p>
<p>(ii) Damping frequency \( f' = \frac{\omega'}{2\pi} \approx 1.556 \) Hz.</p>
<p>(iii) Damping period \( T' = \frac{1}{f'} \approx 0.643 \) s.</p>
<p>(iv) Natural frequency \( f_0 = \frac{\omega_0}{2\pi} \approx 1.556 \) Hz.</p>
<p>(v) Damping factor \( \gamma = 0.0515 \) s\(^{-1}\).</p>
<p>(vi) Damping amplitude function \( A(t) = A_0 e^{-\gamma t} = 0.2 e^{-0.0515 t} \).</p>
<p>(vii) Life time \( \tau = \frac{1}{\gamma} = \frac{2m}{b} \approx 19.43 \) s.</p>
<p>(viii) Displacement equation \( x(t) = 0.2 e^{-0.0515 t} \cos(9.777 t) \) (assuming phase \( \phi = 0 \)).</p>
<p>(ix) Displacement at \( t=1 \): \( x(1) \approx 0.2 e^{-0.0515} \cos(9.777) \approx -0.174 \) m.</p>
<p>(x)-(xiii) Using the derivatives \( v(t), a(t) \) and substituting the respective \( t \) values. Cycle time uses \( t = nT' \).</p>
</div>""",

    "P29": r"""<div id="solution-P29" style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1);">
<p><strong>Solution:</strong></p>
<p><em>(Note: Since the graph is not visible, generic steps to extract parameters and solve are provided).</em></p>
<p>Given: \( m = 0.05 \) kg, \( b = 0.05 \) kg/s. \( \gamma = \frac{b}{2m} = 0.5 \) s\(^{-1}\).</p>
<p>Steps to extract from graph: Read initial amplitude \( A_0 \) and damped period \( T' \) (time between peaks).</p>
<p>(i) \( \omega' = \frac{2\pi}{T'} \).</p>
<p>(ii) \( f' = \frac{1}{T'} \).</p>
<p>(iii) Damping energy \( E(t) = \frac{1}{2} k A_0^2 e^{-2\gamma t} \) at \( t=0.5 \).</p>
<p>(iv) Damping time period \( T' \) directly from graph.</p>
<p>(v) Spring constant \( k \): Using \( \omega_0^2 = \omega'^2 + \gamma^2 \) and \( k = m\omega_0^2 \).</p>
<p>(vi) Damping factor \( \gamma = 0.5 \) s\(^{-1}\).</p>
<p>(vii) Damping term \( e^{-\gamma t} \) at \( t=0.2 \).</p>
<p>(viii) Relaxation time \( \tau = \frac{1}{\gamma} = 2 \) s.</p>
<p>(ix)-(xvi) Compute \( x(t), v(t), a(t) \), and energy expressions substituting derived \( k \), \( \omega' \), and \( A_0 \).</p>
</div>""",

    "P30": r"""<div id="solution-P30" style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1);">
<p><strong>Solution:</strong></p>
<p><em>(Generic procedure as the graph is missing.)</em></p>
<p>Given: \( m = 0.05 \) kg, \( b = 0.05 \) kg/s. \( \gamma = 0.5 \) s\(^{-1}\).</p>
<p>1. Extract \( A_0 \) (initial max displacement) and \( T' \) (time between successive peaks) from the graph.</p>
<p>2. Calculate \( \omega' = \frac{2\pi}{T'} \), \( \omega_0 = \sqrt{\omega'^2 + \gamma^2} \), and \( k = m\omega_0^2 \).</p>
<p>3. Construct \( x(t) = A_0 e^{-0.5t} \cos(\omega' t) \).</p>
<p>(i) \( E(0.5) \approx E_0 e^{-2(0.5)(0.5)} = E_0 e^{-0.5} \), where \( E_0 = \frac{1}{2} k A_0^2 \).</p>
<p>(ii) Evaluate \( x(1) \).</p>
<p>(iii) Evaluate \( v(2) = x'(2) \) and \( a(3) = x''(3) \).</p>
<p>(iv) \( K(4) = \frac{1}{2} m v(4)^2 \).</p>
<p>(v) \( U(5) = \frac{1}{2} k x(5)^2 \).</p>
<p>(vi) Total energy \( E(6) \approx E_0 e^{-2(0.5)(6)} \).</p>
</div>""",

    "P31": r"""<div id="solution-P31" style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1);">
<p><strong>Solution:</strong></p>
<p><em>(Generic procedure as the graph is missing.)</em></p>
<p>Given: \( m = 0.05 \) kg, \( b = 0.05 \) kg/s, \( \gamma = 0.5 \) s\(^{-1}\).</p>
<p>1. Read initial amplitude \( A_0 \) and damped period \( T' \) from the graph.</p>
<p>2. Damped amplitude formula: \( A(t) = A_0 e^{-\gamma t} \).</p>
<p>3. Energy formula: \( E(t) = \frac{1}{2} k A(t)^2 = E_0 e^{-2\gamma t} \).</p>
<p>(i) \( E(0.5) = E_0 e^{-0.5} \).</p>
<p>(ii)-(v) Same substitution steps as P30.</p>
<p>(vi) Damping amplitude at \( t = 6 \) s: \( A(6) = A_0 e^{-0.5 \times 6} = A_0 e^{-3} \).</p>
</div>""",

    "P32": r"""<div id="solution-P32" style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1);">
<p><strong>Solution:</strong></p>
<p><em>(Generic procedure as the graph is missing.)</em></p>
<p>Given: \( m = 0.25 \) kg.</p>
<p>From the graph, read:<br>
- Initial amplitude \( A_0 \).<br>
- Damped period \( T' \).<br>
- Amplitude at a later time \( A(t) \) to find \( \gamma \).</p>
<p>Calculate \( \gamma = -\frac{1}{t} \ln\left(\frac{A(t)}{A_0}\right) \).</p>
<p>(i) Damping amplitude at \( t=2 \): \( A(2) = A_0 e^{-2\gamma} \).</p>
<p>(ii) Displacement at \( t=3 \): \( x(3) = A_0 e^{-3\gamma} \cos(3\omega' + \phi) \).</p>
<p>(iii) \( \omega' = \frac{2\pi}{T'} \).</p>
<p>(iv) \( E(4) = E_0 e^{-8\gamma} \).</p>
<p>(v)-(vi) Evaluate derivatives \( v(t), a(t) \) for envelopes.</p>
<p>(vii) Life time \( \tau = \frac{1}{\gamma} \).</p>
<p>(viii) Damping coefficient \( b = 2m\gamma \).</p>
<p>(ix)-(x) Envelope equations \( y = \pm A_0 e^{-\gamma t} \).</p>
</div>""",

    "P33": r"""<div id="solution-P33" style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1);">
<p><strong>Solution:</strong></p>
<p><em>(Generic procedure as the graph is missing.)</em></p>
<p>Given: \( m = 1 \) kg, \( b = 1 \) kg/s. \( \gamma = \frac{b}{2m} = 0.5 \) s\(^{-1}\).</p>
<p>From graph, read \( A_0 \) and \( T' \).</p>
<p>(i) Equation: \( x(t) = A_0 e^{-0.5 t} \cos(\omega' t) \) where \( \omega' = \frac{2\pi}{T'} \).</p>
<p>(ii) \( A(1.25) = A_0 e^{-0.5 \times 1.25} \).</p>
<p>(iii) \( x(3) = A_0 e^{-1.5} \cos(3\omega') \).</p>
<p>(iv) \( \omega' = \frac{2\pi}{T'} \).</p>
<p>(v) \( E(3.25) = E_0 e^{-3.25} \).</p>
<p>(vi)-(vii) Maximums are bounded by the envelopes \( A\omega' \) and \( A\omega'^2 \) approximately for light damping.</p>
<p>(vii) Life time \( \tau = \frac{1}{\gamma} = 2 \) s.</p>
<p>(viii) Damping envelope at \( t=2.5 \): \( \pm A_0 e^{-1.25} \).</p>
</div>""",

    "P34": r"""<div id="solution-P34" style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1);">
<p><strong>Solution:</strong></p>
<p>Given: \( m = 1 \) kg, \( b = 1 \) kg/s. \( \gamma = \frac{b}{2m} = 0.5 \) s\(^{-1}\).</p>
<p>Assume \( \omega' \) and \( A_0 \) are extracted from context/graphs missing here.</p>
<p>(i) \( x(t) = A_0 e^{-0.5t} \cos(\omega' t) \).</p>
<p>(ii) At \( t=1 \) s:<br>
- Damping amplitude \( A(1) = A_0 e^{-0.5} \).<br>
- Damping displacement \( x(1) = A_0 e^{-0.5} \cos(\omega') \).<br>
- Damping frequency \( f' = \frac{\omega'}{2\pi} \).<br>
- Damping energy \( E(1) = E_0 e^{-1} \).</p>
<p>(iii) Relaxation time (life time) \( \tau = \frac{1}{\gamma} = 2 \) s.</p>
</div>""",

    "P35": r"""<div id="solution-P35" style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1);">
<p><strong>Solution:</strong></p>
<p><em>(Generic procedure as the velocity equation/graph is missing.)</em></p>
<p>Given: \( m = 0.5 \) kg, \( \alpha \) (or \( \gamma \)) \( = 0.5 \) s\(^{-1}\).</p>
<p>If velocity \( v(t) \) is given, say \( v(t) = V_0 e^{-0.5t} \sin(\omega' t) \):</p>
<p>(i) The displacement equation can be found by integrating \( v(t) \) with respect to time, or simply by knowing that \( x(t) \approx -\frac{V_0}{\omega'} e^{-0.5t} \cos(\omega' t) \) for small damping.</p>
<p>(ii) Substitute \( t = 3 \) s into the derived displacement equation \( x(3) \).</p>
</div>""",

    "P36": r"""<div id="solution-P36" style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1);">
<p><strong>Solution:</strong></p>
<p><em>(Generic procedure as the graph is missing.)</em></p>
<p>Given: \( m = 1.2 \) kg, \( k = 65 \) N/m.</p>
<p>From the graph, identify the time period \( T' \) and successive amplitudes \( A_1 \) and \( A_2 \).</p>
<p>(i) Find logarithmic decrement \( \delta = \ln(A_1 / A_2) \). Then \( \gamma = \frac{\delta}{T'} \). Finally, \( b = 2m\gamma \).</p>
<p>(ii) Life time \( \tau = \frac{1}{\gamma} \).</p>
<p>(iii) Equation of displacement \( x(t) = A_0 e^{-\gamma t} \cos(\omega' t) \) where \( \omega' = \frac{2\pi}{T'} \).</p>
<p>(iv) Substitute \( t = 2.5 \) s into the displacement equation to find \( x(2.5) \).</p>
</div>"""
}

# Use lambda in sub to avoid escape parsing issues in the replacement string
for pid, replacement in solutions.items():
    pattern = re.compile(rf'<div id="solution-{pid}".*?</div>', re.DOTALL)
    content = pattern.sub(lambda m, r=replacement: r, content)

with open(html_path, 'w') as f:
    f.write(content)

print("Replaced all solution blocks.")
