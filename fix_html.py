import re

# Read the broken index.html
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# We need to inject the missing JS exactly where it belongs
missing_code = """
        const formatDamage = (min, max) => `
        <span class="val-min">${min}</span><span class="val-dash">-</span><span class="val-max">${max}</span>
    `;

        const getHeaders = (tableId) => `
        <thead>
            <tr>
                <th onclick="sortTable('${tableId}', 0, 'string')">Weapon Name</th>
                <th onclick="sortTable('${tableId}', 1, 'num')">Old Min Dmg</th>
                <th onclick="sortTable('${tableId}', 2, 'num')">Old Max Dmg</th>
                <th onclick="sortTable('${tableId}', 3, 'num')" style="color:#ffcccc">Novo Sphere Min</th>
                <th onclick="sortTable('${tableId}', 4, 'num')" style="color:#ffcccc">Novo Sphere Max</th>
                <th onclick="sortTable('${tableId}', 5, 'num')">Sphere Speed</th>
                <th onclick="sortTable('${tableId}', 6, 'num')">Old Speed</th>
                <th onclick="sortTable('${tableId}', 7, 'float')">Swing (100 Dex)</th>
                <th onclick="sortTable('${tableId}', 8, 'float')" style="color:#ffcccc">Novo Swing</th>
            </tr>
        </thead>
        <tbody></tbody>
    `;

        const getArtifactHeaders = (tableId) => `
        <thead>
            <tr>
                <th onclick="sortTable('${tableId}', 0, 'string')">Identifier</th>
                <th>Status</th>
                <th onclick="sortTable('${tableId}', 2, 'float')">Swing (100 Dex)</th>
            </tr>
        </thead>
        <tbody></tbody>
    `;

        const getBalancerHeaders = (tableId) => `
        <thead>
            <tr>
                <th onclick="sortTable('${tableId}', 0, 'string')">Weapon Name</th>
                <th onclick="sortTable('${tableId}', 1, 'string')">Category</th>
                <th onclick="sortTable('${tableId}', 2, 'string')">Layer</th>
                <th onclick="sortTable('${tableId}', 3, 'float')">Swing (s)</th>
                <th onclick="sortTable('${tableId}', 4, 'num')">Current Old Min</th>
                <th onclick="sortTable('${tableId}', 5, 'num')" style="color:#ffcccc;">Proposed Min</th>
                <th onclick="sortTable('${tableId}', 6, 'num')">Difference</th>
            </tr>
        </thead>
        <tbody></tbody>
    `;

        function calculateBaseSwing(speed, dexRaw) {
            if (speed <= 0) return 0;
            let speedInSeconds = (speed / 100.0) * 0.65;
            let bonusDex = Math.max(-50, Math.min(25, dexRaw - 100));
            if (bonusDex > 0) speedInSeconds -= speedInSeconds * bonusDex * 0.008;
            else if (bonusDex < 0) speedInSeconds -= speedInSeconds * bonusDex * 0.004;
            return Math.max(0.25, speedInSeconds);
        }

        function renderDash() {
            ['swords-1h', 'swords-2h', 'fencing-1h', 'fencing-2h', 'maces-1h', 'maces-2h', 'bows-1h', 'bows-2h', 'throwing-1h', 'throwing-2h'].forEach(id => {
                const el = document.getElementById(`t-${id}`);
                if (el) el.innerHTML = getHeaders(`t-${id}`);
            });
            const artEl = document.getElementById('t-artifacts');
            if (artEl) artEl.innerHTML = getArtifactHeaders('t-artifacts');

            const balEl = document.getElementById('t-balancer');
            if (balEl) balEl.innerHTML = getBalancerHeaders('t-balancer');

            const counts = {
                'swords-1h': 0, 'swords-2h': 0,
                'fencing-1h': 0, 'fencing-2h': 0,
                'maces-1h': 0, 'maces-2h': 0,
                'bows-1h': 0, 'bows-2h': 0,
                'throwing-1h': 0, 'throwing-2h': 0,
                'artifacts': 0
            };

            weaponData.forEach(w => {
                const isZero = w.OldMax === 0 && w.AosMax === 0 && w.OldMin === 0 && w.AosMin === 0;

                let targetTbody;
                let rowHtml = "";

                if (isZero) {
                    const t = document.querySelector('#t-artifacts tbody');
                    if (t) {
                        targetTbody = t;
                        counts['artifacts']++;
                        rowHtml = `
                        <tr onclick="fillCalculator(${w.SphereSpeed}, '${w.Name.replace(/'/g, "\\'")}')">
                            <td>${w.Name}</td>
                            <td class="stat-zero">Requires Base Weapon</td>
                            <td data-val="${w.SwingSeconds}"><span class="stat-speed">${w.SwingSeconds.toFixed(2)}s</span></td>
                        </tr>
                    `;
                    }
                } else {
                    let cat = w.Skill.toLowerCase();
                    if (!['swords', 'fencing', 'maces', 'bows', 'throwing'].includes(cat)) cat = 'swords';

                    let hands = w.Layer.toLowerCase() === 'twohanded' ? '2h' : '1h';
                    const key = `${cat}-${hands}`;

                    const t = document.querySelector(`#t-${key} tbody`);
                    if (t) {
                        targetTbody = t;
                        counts[key]++;
                        let l_min = w.AosMin;
                        let l_max = w.AosMax;
                        let l_speed = w.SphereSpeed;
                        let l_swing = w.SwingSeconds;
                        let cls = "";

                        let tunedData = localStorage.getItem('weapon_tune_' + w.Name);
                        if (tunedData) {
                            try {
                                let parse = JSON.parse(tunedData);
                                l_min = parse.minDmg;
                                l_max = parse.maxDmg;
                                l_speed = parse.speed;
                                let currDex = parseFloat(document.getElementById('calcDex').value) || 100;
                                l_swing = calculateBaseSwing(l_speed, currDex);
                                cls = "calc-new-stat";
                            } catch (e) { }
                        }

                        rowHtml = `
                        <tr id="row-${w.Name.replace(/[^a-zA-Z0-9]/g, '-')}" onclick="fillCalculator(${w.SphereSpeed}, '${w.Name.replace(/'/g, "\\'")}', ${w.AosMin}, ${w.AosMax}, this, ${w.OldMin}, ${w.OldMax})">
                            <td>${w.Name}</td>
                            <td data-val="${w.OldMin}">${w.OldMin}</td>
                            <td data-val="${w.OldMax}">${w.OldMax}</td>
                            <td data-val="${l_min}" class="cell-newmin ${cls}">${l_min}</td>
                            <td data-val="${l_max}" class="cell-newmax ${cls}">${l_max}</td>
                            <td data-val="${l_speed}" class="cell-speed ${cls}"><span class="stat-sphere">${l_speed}</span></td>
                            <td data-val="${w.OldSpeed}">${w.OldSpeed}</td>
                            <td data-val="${w.SwingSeconds}"><span class="stat-speed">${w.SwingSeconds.toFixed(2)}s</span></td>
                            <td data-val="${l_swing}" class="cell-newswing ${cls}">${l_swing.toFixed(2)}s</td>
                        </tr>
                    `;
                    
                        // Balancer Logic with dynamic UI inputs
                        const engineBase = parseInt(document.getElementById('balBaseline')?.value || 15);
                        const engine2H = parseInt(document.getElementById('bal2HBonus')?.value || 2);
                        const engineFastThresh = parseFloat(document.getElementById('balFastThreshold')?.value || 2.15);
                        const engineFastPen = parseInt(document.getElementById('balFastPenalty')?.value || -2);

                        let proposedMin = engineBase;
                        if(w.Layer.toLowerCase() === 'twohanded') proposedMin += engine2H;
                        if(l_swing <= engineFastThresh) proposedMin += engineFastPen;
                        
                        let diff = proposedMin - w.OldMin;
                        let diffStr = diff > 0 ? `+${diff}` : (diff === 0 ? "0" : diff.toString());
                        let diffColor = diff > 0 ? '#69f0ae' : (diff < 0 ? '#ff5252' : '#9e9e9e');

                        const balTbody = document.querySelector('#t-balancer tbody');
                        if (balTbody) {
                            balTbody.insertAdjacentHTML('beforeend', `
                                <tr>
                                    <td>${w.Name}</td>
                                    <td>${w.Skill}</td>
                                    <td>${w.Layer}</td>
                                    <td data-val="${l_swing}"><span class="stat-speed">${l_swing.toFixed(2)}s</span></td>
                                    <td data-val="${w.OldMin}">${w.OldMin}</td>
                                    <td data-val="${proposedMin}" style="color:#ffcccc; font-weight:700;">${proposedMin}</td>
                                    <td data-val="${diff}" style="color:${diffColor}; font-weight:700;">${diffStr}</td>
                                </tr>
                            `);
                        }
                    }
                }

                if (targetTbody) targetTbody.insertAdjacentHTML('beforeend', rowHtml);
            });

            Object.keys(counts).forEach(k => {
                const badge = document.getElementById(`c-${k}`);
                if (badge) badge.innerText = counts[k];
            });
        }

        function sortTable(tableId, colIndex, type) {
            const table = document.getElementById(tableId);
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            
            // Toggle sort direction
            let dir = table.getAttribute(`data-sort-dir-${colIndex}`) || 'desc';
            dir = dir === 'asc' ? 'desc' : 'asc';
            table.setAttribute(`data-sort-dir-${colIndex}`, dir);

            rows.sort((a, b) => {
                let cellA = a.children[colIndex];
                let cellB = b.children[colIndex];
                let valA = cellA.getAttribute('data-val') !== null ? cellA.getAttribute('data-val') : cellA.innerText;
                let valB = cellB.getAttribute('data-val') !== null ? cellB.getAttribute('data-val') : cellB.innerText;

                if (type === 'num') {
                    valA = parseInt(valA) || 0;
                    valB = parseInt(valB) || 0;
                } else if (type === 'float') {
                    valA = parseFloat(valA) || 0;
                    valB = parseFloat(valB) || 0;
                } else {
                    valA = valA.toString().toLowerCase();
                    valB = valB.toString().toLowerCase();
                }

                if (valA < valB) return dir === 'asc' ? -1 : 1;
                if (valA > valB) return dir === 'asc' ? 1 : -1;
                return 0;
            });

            rows.forEach(row => tbody.appendChild(row));
            
            // Visual feedback for sorted column
            table.querySelectorAll('th').forEach(th => th.classList.remove('sorted-asc', 'sorted-desc'));
            table.querySelectorAll('th')[colIndex].classList.add(dir === 'asc' ? 'sorted-asc' : 'sorted-desc');
        }

        function filterTables() {
            const input = document.getElementById('searchInput');
            const filter = input.value.toUpperCase();
            const tables = document.querySelectorAll('table');

            tables.forEach(table => {
                const tr = table.getElementsByTagName('tr');
                for (let i = 1; i < tr.length; i++) {
                    let td = tr[i].getElementsByTagName('td')[0];\n"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# We replace the portion starting from `;` under `const weaponData = [...]` until `let td = tr[i].getElementsByTagName('td')[0];`
# Because `update_html.py` deleted EVERYTHING up to `if (td) {` including `let td = ...`!
new_content = re.sub(r'(const weaponData = \[.*?\]\s*;)\s*if \(td\) \{', r'\1\n' + missing_code + r'                    if (td) {', content, flags=re.DOTALL)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Repair completed!!")
