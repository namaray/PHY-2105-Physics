import re
import os
import subprocess

template_start = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quiz-2 Solved Problems — PHY-2105</title>
    <link rel="stylesheet" href="styles.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=Outfit:wght@400;700&display=swap" rel="stylesheet">
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    <style>
        .math-block { background: rgba(255, 255, 255, 0.05); padding: 1.5rem; border-radius: 10px; border-left: 4px solid var(--accent-color); margin: 1.5rem 0; font-size: 1.15rem; overflow-x: auto; text-align: center; }
        .math-inline { font-style: italic; background: rgba(255, 255, 255, 0.08); padding: 0.1rem 0.4rem; border-radius: 4px; }
        .formula-card { background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 1.2rem 1.5rem; margin: 1rem 0; transition: all 0.3s ease; }
        .formula-card:hover { border-color: var(--accent-color); background: rgba(255, 255, 255, 0.06); }
        .formula-card h4 { color: var(--accent-color); margin-bottom: 0.5rem; font-size: 1rem; }
        .badge { display: inline-block; padding: 0.2rem 0.7rem; border-radius: 20px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }
        .badge-math { background: rgba(99, 102, 241, 0.2); color: #818cf8; }
        .notes-section { margin-bottom: 3rem; }
        .notes-container { max-width: 800px; margin: 0 auto; padding: 2rem; }
        .nav-bar { display: flex; justify-content: space-between; padding: 1rem 0; margin-bottom: 2rem; border-bottom: 1px solid rgba(255,255,255,0.1); }
        .nav-bar a { color: var(--accent-color); text-decoration: none; font-weight: 600; }
        .nav-bar a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container notes-container">
        <nav class="nav-bar">
            <a href="index.html" class="back-btn">
                <span>←</span> Back to Prep Guide
            </a>
        </nav>

        <header class="notes-header">
            <h1 style="text-align: center; margin-bottom: 2rem; font-family: 'Outfit', sans-serif;">🎯 Quiz-2 Solved Problems</h1>
        </header>
"""

template_end = """
    </div>
</body>
</html>
"""

def get_text(pdf):
    try:
        return subprocess.check_output(["pdftotext", pdf, "-"]).decode('utf-8', errors='ignore')
    except:
        return ""

files = [
    "Supplementary File_ Summer 2026_ PHY-105_B-20260731T105704Z-1-001/Supplementary File_ Summer 2026_ PHY-105_B/Subsidiary file-1 (Waves and Oscillation)_updated.pdf",
    "Waves and Oscillation_b.pdf",
    "Damped Harmonic Motion_DHM_b.pdf",
    "Practice problem sheet_2_PHY 2105_Summer 2026.pdf"
]

all_problems = []
for f in files:
    text = get_text(f)
    # Find things like "1. The equation..."
    matches = re.finditer(r'(?m)^(\d+)\.\s+(.*?)(?=^\d+\.\s+|\Z)', text, re.DOTALL)
    for m in matches:
        num = m.group(1)
        prob = m.group(2).strip()
        if len(prob) > 10:
            all_problems.append(prob)

with open("quiz2-problems.html", "w", encoding='utf-8') as f:
    f.write(template_start)
    
    f.write('        <section class="notes-section">\n')
    f.write('            <h2>SECTION 1: Quiz 2 Problems</h2>\n')
    
    for i, prob in enumerate(all_problems[:54]):
        prob_clean = prob.replace('\n', ' ').strip()
        f.write('        <div class="formula-card">\n')
        f.write(f'            <h4>Example {i+1} <span class="badge badge-math">Math</span></h4>\n')
        f.write(f'            <p><strong>Problem:</strong> {prob_clean}</p>\n')
        f.write('            <details>\n')
        f.write('                <summary style="cursor: pointer; color: var(--accent-color); font-weight: 600; padding: 0.5rem 0;">📝 Show Solution</summary>\n')
        f.write('                <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1);">\n')
        f.write('                <p><strong>Solution to be derived / Problem text/values to be verified from graph/lecture notes.</strong></p>\n')
        f.write('                <p>Formula: \\( ... \\)</p>\n')
        f.write('                <p>Substitution: \\( ... \\)</p>\n')
        f.write('                </div>\n')
        f.write('            </details>\n')
        f.write('        </div>\n')

    f.write('        </section>\n')
    f.write(template_end)
