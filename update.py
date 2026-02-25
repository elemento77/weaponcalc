import json

data_path = 'c:\\Users\\menti\\Desktop\\novo-shard\\WeaponCalc\\Weapon_Analysis_Report.json'
with open(data_path, 'r', encoding='utf-8-sig') as f:
    weapons = json.load(f)

weapons.sort(key=lambda w: w['Name'])
md_content = '# Weapon Analysis Report\n\n'
categories = ['Swords', 'Maces', 'Fencing', 'Bows', 'Throwing']

for cat in categories:
    cat_weapons = [w for w in weapons if w['Skill'] == cat]
    if not cat_weapons: continue
    
    md_content += f'## {cat}\n\n'
    
    for layer in ['OneHanded', 'TwoHanded']:
        layer_weapons = [w for w in cat_weapons if w['Layer'] == layer]
        if not layer_weapons: continue
            
        md_content += f'### {layer}\n\n'
        md_content += '| Weapon | Old Damage | AoS Damage | Sphere Speed | Old Speed | Swing (100 Dex) |\n'
        md_content += '| :--- | :--- | :--- | :--- | :--- | :--- |\n'
        
        for w in layer_weapons:
            old_dmg = f"{w['OldMin']}-{w['OldMax']}"
            aos_dmg = f"{w['AosMin']}-{w['AosMax']}"
            swing = f"{w['SwingSeconds']:.2f}s".replace('.', ',')
            md_content += f"| {w['Name']} | {old_dmg} | {aos_dmg} | {w['SphereSpeed']} | {w['OldSpeed']} | {swing} |\n"
            
        md_content += '\n'

with open('c:\\Users\\menti\\Desktop\\novo-shard\\WeaponCalc\\Weapon_Analysis_Report.md', 'w', encoding='utf-8') as f:
    f.write(md_content)
