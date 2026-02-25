import re

with open('Weapon_Analysis_Report.json', 'r', encoding='utf-8-sig') as f:
    data = f.read()

with open('index.html', 'r', encoding='utf-8') as h:
    html = h.read()

# Replace the array with the new JSON data safely without matching other javascript ]
html = re.sub(r'(const weaponData = )\[.*?\n?\s*\];', r'\g<1>' + data + ';', html, flags=re.DOTALL)

with open('index.html', 'w', encoding='utf-8') as h:
    h.write(html)

print("Updated index.html safely")
