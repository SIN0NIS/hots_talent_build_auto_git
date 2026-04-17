import json
import os
import glob
from datetime import datetime

def generate_html():
    # 1. JSON 파일 찾기
    ko_files = glob.glob('*kokr*.json')
    en_files = glob.glob('*enus*.json')
    
    if not ko_files or not en_files:
        print("오류: 데이터 JSON 파일을 찾을 수 없습니다.")
        return
        
    ko_path = max(ko_files, key=os.path.getmtime)
    en_path = max(en_files, key=os.path.getmtime)
    
    # 2. 데이터 로드
    with open(ko_path, 'r', encoding='utf-8') as f:
        data_ko = json.load(f)
    with open(en_path, 'r', encoding='utf-8') as f:
        data_en = json.load(f)

    hero_list = []
    for h_id, v_ko in data_ko.items():
        if 'name' in v_ko:
            v_en = data_en.get(h_id, {})
            hero_list.append({
                "id": h_id,
                "name_ko": v_ko['name'],
                "name_en": v_en.get('name', h_id),
                "hId": v_ko.get('hyperlinkId', h_id)
            })
    
    hero_list = sorted(hero_list, key=lambda x: x['name_ko'])

    now = datetime.now()
    timestamp = now.strftime("%y%m%d_%H%M")
    output_file = f"index_{timestamp}.html"
    img_cdn_base = "https://raw.githubusercontent.com/SIN0NIS/images/main/abilitytalents/"

    # 3. 메인 콘텐츠 HTML (상단 깃허브 링크 추가)
    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, shrink-to-fit=no">
    <title>히오스 빌드 메이커</title>
    <script src="https://html2canvas.hertzen.com/dist/html2canvas.min.js"></script>
    <style>
        :root {{ --p: #a333ff; --bg: #0b0b0d; --card: #16161a; --blue: #00d4ff; --gold: #ffd700; --green: #00ff00; --fs: 14px; }}
        body {{ margin: 0; background: var(--bg); color: white; font-family: sans-serif; display: flex; flex-direction: column; height: 100vh; overflow: hidden; width: 100%; font-size: var(--fs); }}
        
        /* 상단 링크 스타일 */
        #top-bar {{ background: #000; padding: 6px 12px; border-bottom: 1px solid #333; text-align: center; z-index: 2100; }}
        #top-bar a {{ color: #888; text-decoration: none; font-size: 11px; font-family: monospace; transition: color 0.2s; }}
        #top-bar a:hover {{ color: var(--p); }}

        #header {{ padding: 10px; background: #1a1a1e; border-bottom: 1px solid #333; flex-shrink: 0; z-index: 2000; }}
        .search-box {{ width: 100%; padding: 12px; background: #222; color: white; border: 1px solid var(--p); border-radius: 6px; font-size: 16px; outline: none; box-sizing: border-box; }}
        #hero-list-dropdown {{ position: absolute; left: 10px; right: 10px; max-height: 250px; background: #2a2a2a; overflow-y: auto; z-index: 3000; border-radius: 4px; display: none; border: 1px solid var(--p); }}
        .hero-item {{ padding: 12px; border-bottom: 1px solid #333; cursor: pointer; }}
        #capture-area {{ flex: 1; display: flex; flex-direction: column; overflow-y: auto; padding-bottom: 280px; background: #0b0b0d; width: 100%; box-sizing: border-box; }}
        #hero-stat-container {{ background: #1a1a20; margin: 8px; padding: 12px; border-radius: 8px; border: 1px solid #333; display: none; }}
        .stat-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px; margin-bottom: 12px; }}
        .stat-item {{ background: #111; padding: 6px; border-radius: 4px; display: flex; flex-direction: column; gap: 2px; }}
        .stat-value {{ color: #fff; font-weight: bold; font-size: 1.25em; }}
        .stat-label {{ color: #888; font-size: 0.85em; display: flex; justify-content: space-between; align-items: center; }}
        .growth-tag {{ color: var(--green); font-size: 0.9em; }}
        .ability-list {{ border-top: 1px solid #444; padding-top: 8px; display: flex; flex-direction: column; gap: 8px; }}
        .ability-item {{ display: flex; gap: 8px; align-items: flex-start; background: #111; padding: 6px; border-radius: 6px; }}
        .ability-icon {{ width: 34px; height: 34px; border: 1px solid #444; border-radius: 4px; flex-shrink: 0; }}
        .tier-row {{ display: flex; align-items: center; background: var(--card); padding: 6px 8px; border-radius: 6px; border-left: 4px solid var(--p); gap: 8px; margin: 4px 8px; }}
        .t-icon {{ width: 38px; height: 38px; border: 1px solid #444; cursor: pointer; border-radius: 5px; background: #000; }}
        .t-icon.selected {{ border-color: var(--gold); box-shadow: 0 0 6px var(--gold); }}
        
        #footer {{ position: fixed; bottom: 0; width: 100%; background: rgba(10,10,12,0.98); border-top: 2px solid var(--p); padding: 12px; box-sizing: border-box; display: flex; flex-direction: column; gap: 8px; z-index: 1500; }}
        #selected-summary {{ display: flex; justify-content: center; gap: 4px; margin-bottom: 4px; }}
        .summary-icon {{ width: 32px; height: 32px; border: 1px solid #444; border-radius: 4px; background: #000; }}
        .summary-icon.filled {{ border-color: var(--gold); }}
        #build-code-box {{ background: #111; border: 1px dashed var(--gold); color: var(--gold); padding: 8px; border-radius: 4px; font-family: monospace; font-size: 13px; text-align: center; cursor: pointer; }}
        
        .option-group {{ display: flex; gap: 12px; align-items: center; background: #222; padding: 6px 12px; border-radius: 6px; }}
        .btn-group {{ display: flex; gap: 8px; width: 100%; }}
        .footer-btn {{ flex: 1; background: var(--p); color: white; border: none; padding: 12px; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 15px; }}
        .cap-row {{ display: flex; align-items: flex-start; gap: 15px; border-bottom: 1px solid #333; padding: 15px 0; }}
        .cap-lv {{ color: var(--blue); font-size: 14px; font-weight: bold; width: 45px; flex-shrink: 0; }}
        .cap-img {{ width: 60px; height: 60px; border: 2px solid var(--gold); border-radius: 8px; flex-shrink: 0; }}
    </style>
</head>
<body>
    <div id="top-bar">
        <a href="https://github.com/SIN0NIS/hots_talent_build_auto_git" target="_blank">🔗 GitHub: SIN0NIS/hots_talent_build_auto_git</a>
    </div>

    <div id="header">
        <input type="text" id="hero-search" class="search-box" placeholder="영웅 초성 또는 이름 검색..." onclick="showList()" oninput="handleSearch(this.value)">
        <div id="hero-list-dropdown"></div>
    </div>
    <div id="capture-area">
        <div id="welcome-area" style="padding:40px; text-align:center; color:#666;">영웅을 선택하세요.</div>
        <div id="hero-stat-container">
            <h2 id="hero-info-title" style="margin:0; font-size: 24px;"></h2>
            <div id="level-display" style="color:var(--gold); font-weight:bold; margin: 10px 0;">LV 1</div>
            <input type="range" id="level-slider" min="1" max="30" value="1" step="1" style="width:100%;" oninput="updateLevel(this.value)">
            <div class="stat-grid" id="stat-grid"></div>
            <div id="ability-container" class="ability-list"></div>
        </div>
        <div id="main-content"></div>
    </div>
    <div id="footer">
        <div id="selected-summary"></div>
        <div id="build-code-box" onclick="copyBuildCode()">특성을 선택하면 빌드 코드가 생성됩니다.</div>
        <div class="option-group">
            <span style="font-size:12px; color:#aaa;">이름 <input type="color" id="name-color" value="#a333ff"></span>
            <span style="font-size:12px; color:#aaa;">테두리 <input type="color" id="border-color" value="#a333ff"></span>
            <input type="range" min="12" max="20" value="14" oninput="updateFontSize(this.value)">
        </div>
        <div class="btn-group">
            <button class="footer-btn" onclick="takeScreenshot('save')">📸 저장</button>
            <button class="footer-btn" style="background:#27ae60;" onclick="takeScreenshot('copy')">📋 이미지 복사</button>
        </div>
    </div>
    <script>
        const dataKO = {json.dumps(data_ko, ensure_ascii=False)};
        const heroList = {json.dumps(hero_list, ensure_ascii=False)};
        const imgBase = "{img_cdn_base}";
        let currentHeroId = null, currentLevel = 1, selectedTalents = [];

        function getChosung(str) {{
            const cho = ["ㄱ","ㄲ","ㄴ","ㄷ","ㄸ","ㄹ","ㅁ","ㅂ","ㅃ","ㅅ","ㅆ","ㅇ","ㅈ","ㅉ","ㅊ","ㅋ","ㅌ","ㅍ","ㅎ"];
            let res = ""; for(let i=0; i<str.length; i++) {{
                let c = str.charCodeAt(i) - 44032;
                if(c >= 0 && c < 11172) res += cho[Math.floor(c/588)];
                else res += str.charAt(i);
            }} return res;
        }}
        function handleSearch(v) {{
            const s = v.toLowerCase().replace(/\\s/g, ""), choInput = getChosung(s);
            const fil = heroList.filter(h => {{
                const n_ko = h.name_ko.toLowerCase().replace(/\\s/g, "");
                return n_ko.includes(s) || getChosung(n_ko).includes(choInput);
            }}); renderList(fil);
        }}
        function renderList(l) {{ document.getElementById("hero-list-dropdown").innerHTML = l.map(h => `<div class="hero-item" onclick="selectHero('${{h.id}}')">${{h.name_ko}}</div>`).join(""); }}
        function showList() {{ document.getElementById("hero-list-dropdown").style.display = "block"; }}
        function updateFontSize(v) {{ document.documentElement.style.setProperty('--fs', v + 'px'); }}

        function processTooltip(t, lv) {{
            if(!t) return ""; let p = t.replace(/<[^>]*>?/gm, "").replace(/\\n/g, "<br>");
            p = p.replace(/(\\d+(?:\\.\\d+)?)\\s*~~(0\\.\\d+)~~/g, (m, b, s) => {{
                const v = parseFloat(b) * Math.pow(1 + parseFloat(s), lv - 1);
                return "<strong>" + v.toFixed(1) + "</strong>(+" + (parseFloat(s)*100).toFixed(1) + "%)";
            }}); return p.replace(/~~(0\\.\\d+)~~/g, (m, s) => "(+" + (parseFloat(s)*100).toFixed(1) + "%)");
        }}

        function selectHero(id) {{
            currentHeroId = id; const hData = dataKO[id];
            document.getElementById("welcome-area").style.display = "none"; document.getElementById("hero-list-dropdown").style.display = "none";
            document.getElementById("hero-info-title").innerText = hData.name; document.getElementById("hero-stat-container").style.display = "block";
            const lvs = Object.keys(hData.talents).filter(l => hData.talents[l].length > 0).sort((a,b) => parseInt(a.replace(/\\D/g,"")) - parseInt(b.replace(/\\D/g,"")));
            selectedTalents = new Array(lvs.length).fill(0);
            let h = ''; lvs.forEach((lv, i) => {{
                h += `<div class="tier-row"><div style="width:35px; color:var(--blue); font-weight:bold;">${{lv.replace(/\\D/g,"")}}</div><div style="display:flex;gap:4px;">`;
                hData.talents[lv].forEach((t, ti) => {{ h += `<img src="${{imgBase}}${{t.icon}}" class="t-icon t-row-${{i}}" onclick="toggleTalent(${{i}}, ${{ti+1}}, this)">`; }});
                h += `</div><div class="t-info-display" id="desc-${{i}}" style="font-size:0.9em; color:#aaa;">특성을 선택하세요.</div></div>`;
            }});
            document.getElementById("main-content").innerHTML = h; 
            renderStats(); renderAbilities(); updateBuildUI();
        }}

        function toggleTalent(ti, tn, el) {{
            const box = document.getElementById("desc-"+ti);
            if(selectedTalents[ti] == tn) {{ selectedTalents[ti] = 0; el.classList.remove("selected"); box.innerHTML = "특성을 선택하세요."; }}
            else {{
                selectedTalents[ti] = tn; document.querySelectorAll(".t-row-"+ti).forEach(img => img.classList.remove("selected"));
                el.classList.add("selected"); const hData = dataKO[currentHeroId];
                const lvs = Object.keys(hData.talents).filter(l => hData.talents[l].length > 0).sort((a,b) => parseInt(a.replace(/\\D/g,"")) - parseInt(b.replace(/\\D/g,"")));
                const t = hData.talents[lvs[ti]][tn-1];
                box.innerHTML = `<b style="color:#fff; font-size:1.1em;">${{t.name}}</b><div style="color:#ccc; margin-top:2px;">${{processTooltip(t.fullTooltip, currentLevel)}}</div>`;
            }}
            updateBuildUI();
        }}

        function updateBuildUI() {{
            if(!currentHeroId) return;
            const hData = dataKO[currentHeroId];
            const lvs = Object.keys(hData.talents).filter(l => hData.talents[l].length > 0).sort((a,b) => parseInt(a.replace(/\\D/g,"")) - parseInt(b.replace(/\\D/g,"")));
            let summaryHTML = "";
            selectedTalents.forEach((tn, ti) => {{
                if(tn > 0) {{
                    const t = hData.talents[lvs[ti]][tn-1];
                    summaryHTML += `<img src="${{imgBase}}${{t.icon}}" class="summary-icon filled">`;
                }} else {{ summaryHTML += `<div class="summary-icon"></div>`; }}
            }});
            document.getElementById("selected-summary").innerHTML = summaryHTML;
            const code = `[T${{selectedTalents.join("")}},${{hData.hyperlinkId}}]`;
            document.getElementById("build-code-box").innerText = code;
        }}

        function copyBuildCode() {{
            const code = document.getElementById("build-code-box").innerText;
            navigator.clipboard.writeText(code).then(() => alert("빌드 코드가 복사되었습니다: " + code));
        }}

        function updateLevel(lv) {{ currentLevel = parseInt(lv); document.getElementById("level-display").innerText = "LV " + currentLevel; if(currentHeroId) {{ renderStats(); renderAbilities(); }} }}

        function renderStats() {{
            const h = dataKO[currentHeroId]; const calc = (b, s, lv) => (b * Math.pow(1 + (s || 0), lv - 1)).toFixed(0);
            const getGT = (s) => s > 0 ? `(+${{(s*100).toFixed(1)}}%)` : "";
            const energyMap = {{ "Mana": "마나", "Energy": "기력", "Fury": "분노", "Rage": "광기", "Essence": "정수", "Soul": "영혼", "Focus": "집중", "Brew": "취기" }};
            let sArr = []; sArr.push({{l: '생명력', v: calc(h.life.amount, h.life.scale, currentLevel), g: getGT(h.life.scale)}});
            if(h.shield) sArr.push({{l: '보호막', v: calc(h.shield.amount, h.shield.scale, currentLevel), g: getGT(h.shield.scale)}});
            if(h.energy && h.energy.type !== "None") {{
                let eName = energyMap[h.energy.type] || h.energy.type;
                let eScale = (h.energy.type === "Mana") ? 0.04 : 0;
                sArr.push({{l: eName, v: calc(h.energy.amount, eScale, currentLevel), g: getGT(eScale)}});
            }}
            const w = (h.weapons && h.weapons[0]) ? h.weapons[0] : {{damage:0, period:1, damageScale:0.04, range:0}};
            const dmg = parseFloat(calc(w.damage, w.damageScale, currentLevel)), dps = (dmg / w.period).toFixed(1);
            sArr.push({{ l: '공격력', v: dmg + ` (DPS: ${{dps}})`, g: getGT(w.damageScale) }});
            sArr.push({{l: '공격 주기', v: w.period.toFixed(2) + "s", g: ""}}, {{l: '사거리', v: w.range.toFixed(1), g: ""}}, {{l: '피격 반지름', v: h.radius.toFixed(2), g: ""}});
            document.getElementById("stat-grid").innerHTML = sArr.map(s => `<div class="stat-item"><div class="stat-label"><span>${{s.l}}</span> <span class="growth-tag">${{s.g}}</span></div><b class="stat-value">${{s.v}}</b></div>`).join("");
        }}

        function renderAbilities() {{
            const h = dataKO[currentHeroId]; let html = "";
            const processList = (list) => {{ if(!list) return; list.forEach(skill => {{ html += `<div class="ability-item"><img src="${{imgBase}}${{skill.icon}}" class="ability-icon"><div style="flex:1"><b style="color:var(--blue)">[${{skill.abilityType}}] ${{skill.name}}</b><div style="color:#bbb; font-size:0.95em; margin-top:2px;">${{processTooltip(skill.fullTooltip || skill.description, currentLevel)}}</div></div></div>`; }}); }};
            ["basic", "heroic", "trait", "mount", "activable"].forEach(k => processList(h.abilities[k]));
            document.getElementById("ability-container").innerHTML = html;
        }}

        async function takeScreenshot(mode) {{
            if (!currentHeroId) return;
            const nameColor = document.getElementById("name-color").value, borderColor = document.getElementById("border-color").value;
            const tempDiv = document.createElement('div');
            tempDiv.style.cssText = `position:absolute; left:-9999px; top:0; width:500px; background:#0b0b0d; padding:25px; border:3px solid ${{borderColor}}; color:white; border-radius:12px;`;
            const hData = dataKO[currentHeroId];
            let innerHTML = `<div style="text-align:center; margin-bottom:25px;"><div style="font-size:36px; font-weight:bold; color:${{nameColor}};">${{hData.name}}</div></div>`;
            const lvs = Object.keys(hData.talents).filter(l => hData.talents[l].length > 0).sort((a,b) => parseInt(a.replace(/\\D/g,"")) - parseInt(b.replace(/\\D/g,"")));
            selectedTalents.forEach((tn, ti) => {{ if (tn > 0) {{ const t = hData.talents[lvs[ti]][tn-1]; innerHTML += `<div class=\"cap-row\"><div class=\"cap-lv\">${{lvs[ti].replace(/\\D/g,"")}}Lv</div><img src=\"${{imgBase}}${{t.icon}}\" class=\"cap-img\"><div style=\"flex:1; padding-left:15px;\"><div style=\"font-size:18px; font-weight:bold;\">${{t.name}}</div><div style=\"color:#bbb; font-size:14px;\">${{processTooltip(t.fullTooltip, currentLevel)}}</div></div></div>`; }} }});
            tempDiv.innerHTML = innerHTML; document.body.appendChild(tempDiv);
            try {{
                const canvas = await html2canvas(tempDiv, {{ useCORS:true, backgroundColor:"#0b0b0d", scale: 2 }});
                if (mode === 'save') {{
                    const link = document.createElement('a'); link.download = `${{hData.name}}_build.png`; link.href = canvas.toDataURL(); link.click();
                }} else {{
                    canvas.toBlob(async blob => {{
                        try {{
                            if (navigator.clipboard && window.ClipboardItem) {{
                                const item = new ClipboardItem({{ "image/png": blob }});
                                await navigator.clipboard.write([item]);
                                alert("이미지가 클립보드에 복사되었습니다!");
                            }} else {{ throw new Error(); }}
                        }} catch (err) {{
                            alert("보안 문제로 이미지 직접 복사가 차단되었습니다. [📸 저장] 버튼을 이용해 주세요.");
                        }}
                    }}, "image/png");
                }}
            }} catch (err) {{ alert("이미지 생성 오류"); }} finally {{ document.body.removeChild(tempDiv); }}
        }}
    </script>
</body>
</html>"""

    # 4. 파일 저장
    with open(output_file, 'w', encoding='utf-8') as f: f.write(html_content)
    with open('hots_talent_build.html', 'w', encoding='utf-8') as f: f.write(html_content)
    print(f"--- 완료 ---")

if __name__ == "__main__":
    generate_html()
