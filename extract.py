import re

with open("quiz2-problems.html", "r") as f:
    content = f.read()

# Find all formula-card divs
cards = re.finditer(r'<div class="formula-card">.*?<h4>Example\s+(\d+)\b.*?<p><strong>Problem:</strong>(.*?)</p>', content, re.DOTALL)
for match in cards:
    print(f"Example {match.group(1)}: {match.group(2)[:100].strip()}")
