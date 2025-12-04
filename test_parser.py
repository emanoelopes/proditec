from bs4 import BeautifulSoup, NavigableString
import json

html_content = """
<div class="MuiTableContainer-root">
    Nome
    Ambientação
    Atividade síncrona: A RcS e as figuras do aprender
    Claudemir Filho
    <td><input value="10" class="jss1"></td>
    <td><input value="8" class="jss1"></td>
    <td><input value="" class="jss1"></td>
    <td><input value="10" class="jss1"></td>
    <td><input value="9" class="jss1"></td>
    Cláudia Santos
    <td><input value="7" class="jss1"></td>
    <td><input value="6" class="jss1"></td>
    <td><input value="5" class="jss1"></td>
    <td><input value="4" class="jss1"></td>
    <td><input value="3" class="jss1"></td>
</div>
"""

soup = BeautifulSoup(html_content, 'html.parser')
container = soup.find('div', class_='MuiTableContainer-root')

students_data = []
current_student = None
grades = []

# Iterate through children to find text nodes (names) and TDs (grades)
# Iterate through children to find text nodes (names) and TDs (grades)
for child in container.contents:
    if isinstance(child, NavigableString):
        # Split by newline to handle cases where multiple text items are in one node
        lines = str(child).split('\n')
        for line in lines:
            text = line.strip()
            if not text: continue
            print(f"Found text line: '{text}'")
            # Heuristic: Name is longer than 3 chars, not a header, not a number
            if len(text) > 3 and "Atividade" not in text and "Nome" not in text and not text.replace('.', '', 1).isdigit():
                print(f"  -> Identified as Name: {text}")
                if current_student:
                    print(f"  -> Saving previous student: {current_student} with grades {grades}")
                    students_data.append({'name': current_student, 'grades': grades})
                current_student = text
                grades = []
    elif child.name == 'td':
        print("Found TD")
        input_tag = child.find('input')
        if input_tag:
            val = input_tag.get('value', '')
            print(f"  -> Grade: {val}")
            grades.append(val)

# Add last student
if current_student:
    students_data.append({'name': current_student, 'grades': grades})

print(json.dumps(students_data, indent=2, ensure_ascii=False))
