import re

with open("quiz2-problems.html", "r") as f:
    content = f.read()

solve_list = [1, 3, 5, 6, 12, 14, 15, 16, 17, 18, 19, 20, 21]

cards = re.finditer(r'<div class="formula-card">.*?<h4>Example\s+(\d+)\b.*?<p><strong>Problem:</strong>(.*?)</p>', content, re.DOTALL)
for match in cards:
    ex_num = int(match.group(1))
    if ex_num in solve_list:
        print(f"--- Example {ex_num} ---")
        print(match.group(2).strip())
