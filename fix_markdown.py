import os

with open('research_paper.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for i in range(len(lines)):
    line = lines[i]
    if line.startswith('* ') or line.startswith('1. '):
        if i > 0 and lines[i-1].strip() != '' and not lines[i-1].startswith('* ') and not lines[i-1].startswith(tuple([f"{j}. " for j in range(1, 10)])):
            new_lines.append('\n')
    new_lines.append(line)

with open('research_paper.md', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Markdown lists fixed.")
