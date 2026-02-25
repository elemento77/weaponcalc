import os
import re

file_path = 'c:\\Users\\menti\\Desktop\\novo-shard\\WeaponCalc\\newweapons.md'
weapons_dir = 'c:\\Users\\menti\\Desktop\\novo-shard\\Projects\\UOContent\\Items\\Weapons'

# 1. Parse weapons
weapons = {}
with open(file_path, 'r', encoding='utf-8') as f:
    for line in f:
        m = re.match(r'\|\s*\*\*.*?\*\*\s*\|\s*([^\|]+?)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|', line)
        if m:
            w_name = m.group(1).strip()
            min_d = int(m.group(2))
            max_d = int(m.group(3))
            spd = int(m.group(4))
            weapons[w_name] = (min_d, max_d, spd)

print(f"Loaded {len(weapons)} weapons from markdown.")

# 2. Iterate over files
files_updated = 0
for root, dirs, files in os.walk(weapons_dir):
    for fn in files:
        if not fn.endswith('.cs'):
            continue
        
        w_name = fn[:-3]
        if w_name in weapons:
            min_d, max_d, spd = weapons[w_name]
            fpath = os.path.join(root, fn)
            
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()

            new_content = content
            
            # Update OldMinDamage
            new_content = re.sub(r'(public override int OldMinDamage\s*=>\s*)\d+;', rf'\g<1>{min_d};', new_content)
            
            # Update OldMaxDamage
            new_content = re.sub(r'(public override int OldMaxDamage\s*=>\s*)\d+;', rf'\g<1>{max_d};', new_content)
            
            # Speed updating logic
            if spd > 100:
                # Update SphereSpeed
                if 'public override int SphereSpeed' in new_content:
                    new_content = re.sub(r'(public override int SphereSpeed\s*=>\s*)\d+;', rf'\g<1>{spd};', new_content)
                else:
                    # Add SphereSpeed after OldSpeed
                    new_content = re.sub(r'(public override int OldSpeed\s*=>\s*\d+;)', rf'\1\n        public override int SphereSpeed => {spd};', new_content)
            else:
                # Update OldSpeed
                if 'public override int OldSpeed' in new_content:
                    new_content = re.sub(r'(public override int OldSpeed\s*=>\s*)\d+;', rf'\g<1>{spd};', new_content)

            if new_content != content:
                with open(fpath, 'w', encoding='utf-8-sig') as f:
                    f.write(new_content)
                print(f"Updated {w_name}")
                files_updated += 1
            else:
                print(f"No changes for {w_name} (check if properties exist)")
                
print(f"Total files updated: {files_updated}")
