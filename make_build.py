import json
import os
import glob
from datetime import datetime

def generate_html():
    # 1. JSON 파일 찾기 (KO, EN 모두 로드)
    ko_files = glob.glob('*kokr*.json')
    en_files = glob.glob('*enus*.json')
    
    if not ko_files or not en_files:
        print("오류: 'kokr' 또는 'enus' JSON 파일을 찾을 수 없습니다.")
        return
        
    ko_path = max(ko_files, key=os.path.getmtime)
    en_path = max(en_files, key=os.path.getmtime)
    
    # 2. 데이터 로드 및 통합
    with open(ko_path, 'r', encoding='utf-8') as f:
        data_ko = json.load(f)
    with open(en_path, 'r', encoding='utf-8') as f:
        data_en = json.load(f)

    # 영웅 목록 생성 (한글/영문 모두 포함하여 검색 최적화)
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

    # 파일명 및 시간 설정
    now = datetime.now()
    timestamp = now.strftime("%y%m%d_%H%M")
    output_file = f"index_{timestamp}.html"
    img_cdn_base = "https://raw.githubusercontent.com/SIN0NIS/images/main/abilitytalents/"

    # 3. 데이터가 포함된 메인 콘텐츠 HTML (index_YYMMDD_HHMM.html)
    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, shrink-to-fit=no">
    <title>히오스 빌드 메이커</title>
    <script src="https://html2canvas.hertzen.com/dist/html2canvas.min.js"></script>
    <style>
        :root {{ --p: #a333ff; --bg: #0b0b0d; --card: #16161a; --blue: #00d4ff; --gold: #ffd700; --green: #00ff00; --fs: 11px; }}
        body {{ margin: 0; background: var(--bg); color: white; font-family: sans-serif; display: flex; flex-direction: column; height: 100vh; overflow: hidden; width: 100%; font-size: var(--fs); }}
        
        #top-link {{ background: #000; padding: 4px 10px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #333; }}
        #top-link a {{ color: #888; text-decoration: none; font-size: 10px; }}
        
        .lang-btn {{ background: #333; color: #fff; border: 1px solid var(--p); padding: 2px 8px; border-radius: 4px; cursor: pointer; font-size: 10px; font-weight: bold; }}
        .lang-btn:hover {{ background: var(--p); }}

        #header {{ padding: 10px; background: #1a1a1e; border-bottom: 1px solid #333; flex-shrink: 0; z-index: 2000; }}
        .search-group {{ display: flex; flex-direction: column; gap: 8px; }}
        .search-box {{ flex: 1; padding: 12px; background: #222; color: white; border: 1px solid var(--p); border-radius: 6px; font-size: 14px; outline: none; }}
        
        #hero-list-dropdown {{ position: absolute; left: 10px; right: 10px; max-height: 250px; background: #2a2a2a; overflow-y: auto; z-index: 3000; border-radius: 4px; display: none; border: 1px solid var(--p); }}
        .hero-item {{ padding: 12px; border-bottom: 1px solid #333; cursor: pointer; }}
        
        #capture-area {{ flex: 1; display: flex; flex-direction: column; overflow-y: auto; padding-bottom: 250px; background: #0b0b0d; width: 100%; box-sizing: border-box; }}
        #hero-stat-container {{ background: #1a1a20; margin: 8px; padding: 12px; border-radius: 8px; border: 1px solid #333; display: none; }}
        
        .stat-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px; margin-bottom: 12px; }}
        .stat-item {{ background: #111; padding: 6px; border-radius: 4px; display: flex; flex-direction: column; gap: 2px; }}
        .stat-value {{ color: #fff; font-weight: bold; font-size: 1.2em; }}
        .stat-label {{ color: #888; font-size: 0.85em; display: flex; justify-content: space-between; }}
        
        .slider-container {{ position: relative; width: 100%; margin: 10px 0 25px 0; padding: 0 10px; box-sizing: border-box; }}
        #level-slider {{ width: 100%; margin: 0; cursor: pointer; }}
        .slider-ticks {{ position: relative; display: flex; justify-content: space-between; margin-top: 8px; width: 100%; }}
        .tick {{ position: absolute; transform: translateX(-50%); font-size: 9px; color: #666; display: flex; flex-direction: column; align-items: center; }}
        .tick::before {{ content: ''; width: 1px; height: 5px; background: #444; margin-bottom: 3px; }}
        .tick.highlight {{ color: var(--gold); font-weight: bold; }}
        .tick.highlight::before {{ background: var(--gold); height: 7px; }}

        .ability-list {{ border-top: 1px solid #444; padding-top: 8px; display: flex; flex-direction: column; gap: 8px; }}
        .ability-item {{ display: flex; gap: 8px; align-items: flex-start; background: #111; padding: 6px; border-radius: 6px; }}
        .ability-icon {{ width: 34px; height: 34px; border: 1px solid #444; border-radius: 4px; flex-shrink: 0; }}
        .ability-text {{ flex: 1; line-height: 1.4; }}
        .ability-name {{ font-weight: bold; color: var(--blue); font-size: 1.05em; }}

        .tier-row {{ display: flex; align-items: center; background: var(--card); padding: 6px 8px; border-radius: 6px; border-left: 4px solid var(--p); gap: 8px; margin: 4px 8px; }}
        .tier-label {{ color: var(--blue); font-weight: bold; width: 35px; flex-shrink: 0; }}
        .t-icon {{ width: 38px; height: 38px; border: 1px solid #444; cursor: pointer; border-radius: 5px; background: #000; }}
        .t-icon.selected {{ border-color: var(--gold); box-shadow: 0 0 6px var(--gold); }}
        .t-info-display {{ flex: 1; padding-left: 8px; border-left: 1px solid #444; display: flex; align-items: center; min-height: 38px; }}
        
        #footer {{ position: fixed; bottom: 0; width: 100%; background: rgba(10,10,12,0.98); border-top: 2px solid var(--p); padding: 12px; box-sizing: border-box; display: flex; flex-direction: column; gap: 12px; z-index: 1500; }}
        .font-control {{ display: flex; align-items: center; gap: 10px; background: #222; padding: 4px 15px; border-radius: 20px; }}
        .font-control input {{ flex: 1; accent-color: var(--p); }}
        .summary-img {{ width: 44px; height: 44px; border-radius: 4px; border: 1px solid var(--gold); }}
        
        .cap-row {{ display: flex; align-items: flex-start; gap: 15px; border-bottom: 1px solid #333; padding: 15px 0; }}
        .cap-lv {{ color: var(--blue); font-size: 20px; font-weight: bold; width: 50px; flex-shrink: 0; }}
        .cap-img {{ width: 60px; height: 60px; border: 2px solid var(--gold); border-radius: 8px; flex-shrink: 0; }}
        .cap-content {{ flex: 1; }}
        .cap-tname {{ color: white; font-size: 18px; font-weight: bold; margin-bottom: 4px; }}
        .cap-tdesc {{ color: #bbb; font-size: 14px; line-height: 1.4; }}
    </style>
</head>
<body>
    <div id="top-link">
        <a href="https://github.com/SIN0NIS/hots_talent_build_auto_git" target="_blank">GitHub: SIN0NIS/hots_talent_build_auto_git</a>
        <button class="lang-btn" onclick="toggleLanguage()">KO / EN</button>
    </div>

    <div id="header">
        <div class="search-group">
            <div style="display:flex; gap:8px;">
                <input type="text" id="hero-search" class="search-box" placeholder="Search Hero or Build Code..." onclick="showList()" oninput="handleSearch(this.value)">
                <button onclick="loadFromCode()" style="padding:0 15px; background:var(--p); color:white; border:none; border-radius:6px; font-weight:bold;">로드</button>
            </div>
        </div>
        <div id="hero-list-dropdown"></div>
    </div>

    <div id="capture-area">
        <div id="welcome-area" style="padding:40px; text-align:center; color:#666;">영웅을 선택하거나 빌드 코드를 붙여넣으세요.</div>
        <div id="hero-stat-container">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                <div id="hero-info-title" style="font-size:22px; font-weight:bold; color:var(--p);"></div>
                <div id="hero-role-badge" style="color:var(--blue); border:1px solid var(--blue); padding:2px 8px; border-radius:4px; font-size:12px;"></div>
            </div>
            <div style="background:#25252b; padding:12px; border-radius:8px; margin-bottom:12px;">
                <div class="slider-container">
                    <input type="range" id="level-slider" min="1" max="30" value="1" step="1" oninput="updateLevel(this.value)">
                    <div class="slider-ticks">
                        <span class="tick highlight" style="left: 0%;">1</span>
                        <span class="tick highlight" style="left: 10.34%;">4</span>
                        <span class="tick highlight" style="left: 20.68%;">7</span>
                        <span class="tick highlight" style="left: 31.03%;">10</span>
                        <span class="tick highlight" style="left: 41.37%;">13</span>
                        <span class="tick highlight" style="left: 51.72%;">16</span>
                        <span class="tick highlight" style="left: 65.51%;">20</span>
                        <span class="tick highlight" style="left: 100%;">30</span>
                    </div>
                </div>
                <div style="display:flex; justify-content:space-between; margin-top:12px;">
                    <span id="level-display" style="font-weight:bold; color:var(--gold); font-size:14px;">LV 1</span>
                    <span id="level-growth-total" style="color:var(--green); font-size:12px;">(+0.00%)</span>
                </div>
            </div>
            <div class="stat-grid" id="stat-grid"></div>
            <div id="ability-container" class="ability-list"></div>
        </div>
        <div id="main-content"></div>
    </div>

    <div id="footer">
        <div id="selected-summary" style="display:flex; justify-content:center; gap:6px;"></div>
        <div class="font-control">
            <span style="font-size:10px; color:#aaa;">가</span>
            <input type="range" min="9" max="20" value="11" oninput="updateFontSize(this.value)">
            <span style="font-size:20px; color:#fff;">가</span>
        </div>
        <div style="display:flex; gap:10px; width:100%;">
            <div id="build-code" onclick="copyCode()" style="flex:2.5; font-size:14px; font-weight:bold; color:var(--gold); background:#111; padding:12px; border-radius:6px; border:1px dashed var(--gold); text-align:center; white-space:nowrap; overflow:hidden; cursor:pointer;">[영웅 선택]</div>
            <button onclick="takeScreenshot()" style="flex:1; background:var(--p); color:white; border:none; padding:10px; border-radius:6px; font-weight:bold; font-size:15px; cursor:pointer;">📸 저장</button>
        </div>
    </div>

    <script>
        const dataKO = {json.dumps(data_ko, ensure_ascii=False)};
        const dataEN = {json.dumps(data_en, ensure_ascii=False)};
        const heroList = {json.dumps(hero_list, ensure_ascii=False)};
        const imgBase = "{img_cdn_base}";
        
        let currentLang = 'ko'; 
        let currentHeroId = null; 
        let currentLevel = 1; 
        let selectedTalents = []; 

        function toggleLanguage() {{
            currentLang = (currentLang === 'ko') ? 'en' : 'ko';
            alert("Language changed: " + (currentLang === 'ko' ? "Korean" : "English"));
            if(currentHeroId) {{
                selectHero(currentHeroId, selectedTalents);
            }}
            handleSearch(document.getElementById("hero-search").value);
        }}

        function getActiveData() {{ return currentLang === 'ko' ? dataKO : dataEN; }}
        function updateFontSize(v) {{ document.documentElement.style.setProperty('--fs', v + 'px'); }}

        function getChosung(str) {{
            const cho = ["ㄱ","ㄲ","ㄴ","ㄷ","ㄸ","ㄹ","ㅁ","ㅂ","ㅃ","ㅅ","ㅆ","ㅇ","ㅈ","ㅉ","ㅊ","ㅋ","ㅌ","ㅍ","ㅎ"];
            let res = ""; for(let i=0; i<str.length; i++) {{
                let c = str.charCodeAt(i) - 44032;
                if(c>-1 && c<11172) res += cho[Math.floor(c/588)];
                else res += str.charAt(i);
            }} return res;
        }}

        function handleSearch(v) {{
            const s = v.toLowerCase().replace(/\s/g, "");
            const choInput = getChosung(s);
            const fil = heroList.filter(h => {{
                const n_ko = h.name_ko.toLowerCase().replace(/\s/g, "");
                const n_en = h.name_en.toLowerCase().replace(/\s/g, "");
                return n_ko.includes(s) || n_en.includes(s) || getChosung(n_ko).includes(choInput);
            }});
            renderList(fil);
        }}

        function renderList(l) {{
            document.getElementById("hero-list-dropdown").innerHTML = l.map(h => 
                `<div class="hero-item" onclick="selectHero('${{h.id}}')">${{currentLang === 'ko' ? h.name_ko : h.name_en}}</div>`
            ).join("");
        }}

        function processTooltip(t, lv) {{
            if(!t) return "";
            let p = t.replace(/<[^>]*>?/gm, "");
            p = p.replace(/(\d+(?:\.\d+)?)\s*~~(0\.\d+)~~/g, (m, b, s) => {{
                const v = parseFloat(b) * Math.pow(1 + parseFloat(s), lv - 1);
                return "<strong>" + v.toFixed(1) + "</strong>(+" + (parseFloat(s)*100).toFixed(1) + "%)";
            }});
            return p.replace(/~~(0\.\d+)~~/g, (m, s) => "(+" + (parseFloat(s)*100).toFixed(1) + "%)");
        }}

        function selectHero(id, codeArray = null) {{
            currentHeroId = id;
            const hData = getActiveData()[id];
            document.getElementById("welcome-area").style.display = "none";
            document.getElementById("hero-list-dropdown").style.display = "none";
            document.getElementById("hero-info-title").innerText = hData.name;
            document.getElementById("hero-role-badge").innerText = hData.expandedRole || "Hero";
            document.getElementById("hero-stat-container").style.display = "block";

            const lvs = Object.keys(hData.talents).filter(l => hData.talents[l].length > 0).sort((a,b) => parseInt(a.replace(/\D/g,"")) - parseInt(b.replace(/\D/g,"")));
            
            if(!codeArray || codeArray.length === 0) {{
                selectedTalents = new Array(lvs.length).fill(0);
            }} else {{
                selectedTalents = codeArray;
            }}

            let h = '';
            lvs.forEach((l, i) => {{
                h += `<div class="tier-row"><div class="tier-label">${{l.replace(/\D/g,"")}}</div><div style="display:flex;gap:4px;">`;
                hData.talents[l].forEach((t, ti) => {{
                    const isSelected = selectedTalents[i] == (ti+1) ? "selected" : "";
                    h += `<img src="${{imgBase}}${{t.icon}}" class="t-icon t-row-${{i}} t-node-${{i}}-${{ti+1}} ${{isSelected}}" onclick="toggleTalent(${{i}}, ${{ti+1}}, this)">`;
                }});
                h += `</div><div class="t-info-display" id="desc-${{i}}">...</div></div>`;
            }});
            document.getElementById("main-content").innerHTML = h;
            
            renderAbilities(); renderStats();
            selectedTalents.forEach((tn, ti) => {{ if(tn > 0) updateTalentTooltip(ti); }});
            updateUI();
        }}

        function toggleTalent(ti, tn, el) {{
            const box = document.getElementById("desc-"+ti);
            if(selectedTalents[ti] == tn) {{
                selectedTalents[ti] = 0; el.classList.remove("selected"); box.innerHTML = "...";
            }} else {{
                selectedTalents[ti] = tn; document.querySelectorAll(".t-row-"+ti).forEach(img => img.classList.remove("selected"));
                el.classList.add("selected"); updateTalentTooltip(ti);
            }}
            updateUI();
        }}

        function updateTalentTooltip(ti) {{
            const tn = selectedTalents[ti]; if(tn == 0) return;
            const hData = getActiveData()[currentHeroId];
            const lvs = Object.keys(hData.talents).filter(l => hData.talents[l].length > 0).sort((a,b) => parseInt(a.replace(/\D/g,"")) - parseInt(b.replace(/\D/g,"")));
            const t = hData.talents[lvs[ti]][tn-1];
            document.getElementById("desc-"+ti).innerHTML = `<div style="width:100%"><b style="color:#fff;">${{t.name}}</b><br><span style="font-size:0.95em; color:#ccc;">${{processTooltip(t.fullTooltip, currentLevel)}}</span></div>`;
        }}

        function updateLevel(lv) {{
            currentLevel = parseInt(lv);
            document.getElementById("level-display").innerText = "LV " + currentLevel;
            document.getElementById("level-growth-total").innerText = "(+" + ((Math.pow(1.04, currentLevel - 1) - 1) * 100).toFixed(2) + "%)";
            if(currentHeroId) {{ renderStats(); renderAbilities(); selectedTalents.forEach((tn, ti) => {{ if(tn > 0) updateTalentTooltip(ti); }}); }}
        }}

        function renderStats() {{
            const h = getActiveData()[currentHeroId];
            const calc = (b, s, lv) => (b * Math.pow(1 + (s || 0.04), lv - 1)).toFixed(0);
            let sArr = [{{l: currentLang==='ko'?'체력':'Health', v:calc(h.life.amount, h.life.scale, currentLevel), g: h.life.scale}}];
            const w = (h.weapons && h.weapons[0]) ? h.weapons[0] : {{damage:0, range:0, period:1, damageScale:0.04}};
            sArr.push({{l: currentLang==='ko'?'공격력':'Attack', v:calc(w.damage, w.damageScale, currentLevel), g: w.damageScale}});
            
            document.getElementById("stat-grid").innerHTML = sArr.map(s => `
                <div class="stat-item">
                    <div class="stat-label"><span>${{s.l}}</span>${{s.g > 0 ? `<span style="color:var(--green);">+${{(s.g*100).toFixed(1)}}%</span>` : ""}}</div>
                    <b class="stat-value">${{s.v}}</b>
                </div>`).join("");
        }}

        function renderAbilities() {{
            const h = getActiveData()[currentHeroId];
            let html = "";
            const processList = (list) => {{
                if(!list) return;
                list.forEach(skill => {{
                    html += `<div class="ability-item"><img src="${{imgBase}}${{skill.icon}}" class="ability-icon"><div class="ability-text">
                        <span class="ability-name"><span style="color:var(--gold)">[${{skill.abilityType}}]</span> ${{skill.name}}</span>
                        <div style="font-size:0.95em; color:#bbb;">${{processTooltip(skill.fullTooltip || skill.description, currentLevel)}}</div></div></div>`;
                }});
            }};
            ["basic", "trait", "mount", "activable"].forEach(k => processList(h.abilities[k]));
            document.getElementById("ability-container").innerHTML = html;
        }}

        function updateUI() {{
            const hData = getActiveData()[currentHeroId];
            if(!hData) return;
            const lvs = Object.keys(hData.talents).filter(l => hData.talents[l].length > 0).sort((a,b) => parseInt(a.replace(/\D/g,"")) - parseInt(b.replace(/\D/g,"")));
            const sum = selectedTalents.map((tn, ti) => tn == 0 ? `<div style="width:44px;height:44px;border:1px dashed #333;"></div>` : `<img src="${{imgBase}}${{hData.talents[lvs[ti]][tn-1].icon}}" class="summary-img">`).join("");
            document.getElementById("selected-summary").innerHTML = sum;
            document.getElementById("build-code").innerText = `[T${{selectedTalents.join("")}},${{hData.hyperlinkId}}]`;
        }}

        function loadFromCode() {{
            const val = document.getElementById("hero-search").value;
            const m = val.match(/\[T(\d+),(.+?)\]/);
            if(!m) return alert("Invalid Code");
            const entry = Object.entries(dataKO).find(([id, d]) => d.hyperlinkId === m[2]);
            if(entry) selectHero(entry[0], m[1].split(""));
        }}

        function showList() {{ handleSearch(""); document.getElementById("hero-list-dropdown").style.display = "block"; }}
        function copyCode() {{ navigator.clipboard.writeText(document.getElementById("build-code").innerText); alert("Copied!"); }}

        function takeScreenshot() {{
            if (!currentHeroId) return;
            const tempDiv = document.createElement('div');
            tempDiv.style.cssText = "position:absolute; left:-9999px; top:0; width:500px; background:#0b0b0d; padding:25px; border:2px solid #a333ff; color:white;";
            const hData = getActiveData()[currentHeroId];
            let innerHTML = `<div style="text-align:center; margin-bottom:20px;"><div style="font-size:32px; font-weight:bold; color:#a333ff;">${{hData.name}}</div></div>`;
            const lvs = Object.keys(hData.talents).filter(l => hData.talents[l].length > 0).sort((a,b) => parseInt(a.replace(/\D/g,"")) - parseInt(b.replace(/\D/g,"")));
            selectedTalents.forEach((tn, ti) => {{
                if (tn > 0) {{
                    const t = hData.talents[lvs[ti]][tn-1];
                    innerHTML += `<div class="cap-row"><div class="cap-lv">${{lvs[ti].replace(/\D/g,"")}}Lv</div><img src="${{imgBase}}${{t.icon}}" class="cap-img"><div class="cap-content"><div class="cap-tname">${{t.name}}</div><div class="cap-tdesc">${{processTooltip(t.fullTooltip, currentLevel)}}</div></div></div>`;
                }}
            }});
            tempDiv.innerHTML = innerHTML;
            document.body.appendChild(tempDiv);
            html2canvas(tempDiv, {{ useCORS:true, backgroundColor:"#0b0b0d" }}).then(canvas => {{
                const link = document.createElement('a');
                link.download = `${{hData.name}}_build.png`;
                link.href = canvas.toDataURL();
                link.click();
                document.body.removeChild(tempDiv);
            }});
        }}
    </script>
</body>
</html>"""

    # 4. 모바일/PC 최적화된 래퍼 HTML (hots_talent_build.html)
    main_page = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, shrink-to-fit=no">
    <title>히오스 빌드 메이커</title>
    <style>
        html, body {{ margin: 0; padding: 0; width: 100%; height: 100%; background-color: #0b0b0d; overflow: hidden; }}
        iframe {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none; display: block; }}
        @supports (-webkit-touch-callout: none) {{ html, body {{ height: -webkit-fill-available; }} }}
    </style>
</head>
<body>
    <iframe src="{output_file}" allow="clipboard-write" allowfullscreen></iframe>
</body>
</html>"""

    # 5. 파일 저장
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    with open('hots_talent_build.html', 'w', encoding='utf-8') as f:
        f.write(main_page)
        
    print(f"--- 생성 완료 ---")
    print(f"데이터 포함 파일: {output_file}")
    print(f"메인 래퍼 파일: hots_talent_build.html")

if __name__ == "__main__":
    generate_html()
