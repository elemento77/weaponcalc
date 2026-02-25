const fs = require('fs');
const data = JSON.parse(fs.readFileSync('Weapon_Analysis_Report.json', 'utf8').replace(/^\uFEFF/, ''));

data.sort((a, b) => a.Name.localeCompare(b.Name));

let md = '# Weapon Analysis Report\n\n';
const cats = ['Swords', 'Maces', 'Fencing', 'Bows', 'Throwing'];

cats.forEach(cat => {
    let catWeapons = data.filter(w => w.Skill === cat);
    if (!catWeapons.length) return;

    md += `## ${cat}\n\n`;

    ['OneHanded', 'TwoHanded'].forEach(layer => {
        let layerWeapons = catWeapons.filter(w => w.Layer === layer);
        if (!layerWeapons.length) return;

        md += `### ${layer}\n\n`;
        md += '| Weapon | Old Damage | AoS Damage | Sphere Speed | Old Speed | Swing (100 Dex) |\n';
        md += '| :--- | :--- | :--- | :--- | :--- | :--- |\n';

        layerWeapons.forEach(w => {
            let oldDmg = `${w.OldMin}-${w.OldMax}`;
            let aosDmg = `${w.AosMin}-${w.AosMax}`;
            let swing = `${w.SwingSeconds.toFixed(2)}s`.replace('.', ',');
            md += `| ${w.Name} | ${oldDmg} | ${aosDmg} | ${w.SphereSpeed} | ${w.OldSpeed} | ${swing} |\n`;
        });
        md += '\n';
    });
});

fs.writeFileSync('Weapon_Analysis_Report.md', md, 'utf8');
console.log('Done!');
