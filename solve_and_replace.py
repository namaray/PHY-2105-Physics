import re
import math

file_path = '/home/angkon/Courses/Physics/quiz2-problems.html'
with open(file_path, 'r') as f:
    content = f.read()

# I will use multi_replace_file_content to do this properly from Python?
# I'll just write a script that does the replacement directly. Wait, the prompt says:
# "Use the multi_replace_file_content tool to replace the ENTIRE..."
# So I *MUST* use the tool, not a Python script to do the replacement!
