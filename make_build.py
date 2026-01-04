import json
import os
import glob
from datetime import datetime

def generate_html():
    # 1. 최신 kokr.json 파일 찾기
    json_files = glob.glob('*kokr*.json')
    if not json_files:
        print("오류: 'kokr'이 포함된 JSON 파일을 찾을 수 없습니다.")
        return
    json_path = max(json_files, key=os.path.getmtime)
    
    # 2. 파일명 및 시간 설정
    now = datetime.now()
    timestamp = now.strftime("%y%m%d_%H%M")
    output_file = f"index_{timestamp}.html"
    img_cdn_base = "https://raw.githubusercontent.com/SIN0NIS/images/main/abilitytalents/"

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    hero_list = sorted([{"id": k, "name": v['name'], "hId": v.get('hyperlinkId', k)} for k, v in data.items() if 'name' in v], key=lambda x: x['name'])

    # 4. HTML 템플릿 작성
    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, shrink-to-fit=no">
    <title>히오스 빌드 메이커 Pro</title>
    <script src="https://html2canvas.hertzen.com/dist/html2canvas.min.js"></script>
    <style>
        :root {{ --p: #a333ff; --bg: #0b0b0d; --card: #16161a; --blue: #00d4ff; --gold: #ffd700; --green: #00ff00; }}
        body {{ margin: 0; background: var(--bg); color: white; font-family: sans-serif; display: flex; flex-direction: column; height: 100vh; overflow: hidden; width: 100%; }}
        #header {{ padding: 10px; background: #1a1a1e; border-bottom: 1px solid #333; flex-shrink: 0; position: relative; z-index: 2000; }}
        .search-group {{ display: flex; flex-direction: column; gap: 8px; }}
        .search-box {{ flex: 1; padding: 12px; background: #222; color: white; border: 1px solid var(--p); border-radius: 6px; font-size: 14px; outline: none; }}
        .comment-input {{ width: 100%; padding: 8px; background: #111; color: var(--blue); border: 1px solid #444; border-radius: 4px; font-size: 11px; text-decoration: underline; box-sizing: border-box; }}
        
        #capture-area {{ flex: 1; display: flex; flex-direction: column; overflow-y: auto; padding-bottom: 220px; background: #0b0b0d; }}
        #welcome-area {{ padding: 40px 20px; text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: center; }}
        #comment-display {{ color: var(--green); font-size: 18px; font-weight: bold; margin-bottom: 10px; white-space: pre-wrap; }}
        
        #hero-stat-container {{ background: #1a1a20; margin: 10px; padding: 15px; border-radius: 8px; border: 1px solid #333; display: none; }}
        
        /* 레벨 슬라이더 컨테이너 및 강조 표시 */
        #level-control-wrapper {{ position: relative; width: 100%; padding-bottom: 20px; }}
        .slider-ticks {{ position: absolute; top: 18px; left: 0; width: 100%; display: flex; justify-content: space-between; padding: 0 10px; box-sizing: border-box; pointer-events: none; }}
        .tick {{ width: 4px; height: 4px; background: #444; border-radius: 50%; }}
        .tick.highlight {{ background: var(--p); box-shadow: 0 0 5px var(--p); height: 6px; width: 6px; margin-top: -1px; }}
        .tick-label {{ position: absolute; top: 8px; font-size: 9px; color: #666; transform: translateX(-50%); }}
        
        .stat-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 15px; }}
        .stat-item {{ background: #111; padding: 8px; border-radius: 4px; font-size: 12px; display: flex; flex-direction: column; gap: 2px; }}
        .stat-value {{ color: #fff; font-weight: bold; font-size: 13px; }}
        
        .ability-list {{ border-top: 1px solid #333; padding-top: 10px; display: flex; flex-direction: column; gap: 10px; }}
        .ability-item {{ display: flex; gap: 10px; align-items: flex-start; background: #111; padding: 8px; border-radius: 6px; }}
        .ability-icon {{ width: 34px; height: 34px; border: 1px solid #444; border-radius: 4px; flex-shrink: 0; }}
        .ability-text {{ flex: 1; font-size: 11px; color: #ccc; line-height: 1.4; }}
        
        .tier-row {{ display: flex; align-items: center; background: var(--card); padding: 8px 10px; border-radius: 6px; border-left: 5px solid var(--p); gap: 10px; min-height: 65px; margin: 3px 5px; }}
        .tier-label {{ color: var(--blue); font-weight: bold; width: 35px; flex-shrink: 0; font-size: 12px; text-align: center; }}
        .t-icon {{ width: 40px; height: 40px; border: 1px solid #444; cursor: pointer; border-radius: 5px; background: #000; }}
        .t-icon.selected {{ border-color: var(--gold); box-shadow: 0 0 10px var(--gold); transform: scale(1.1); z-index: 10; }}
        
        #footer {{ position: fixed; bottom: 0; width: 100%; background: rgba(0,0,0,0.95); border-top: 2px solid var(--p); padding: 10px; box-sizing: border-box; display: flex; flex-direction: column; align-items: center; gap: 8px; backdrop-filter: blur(10px); z-index: 1500; }}
        .summary-img {{ width: 17px; height: 17px; border-radius: 3px; border: 1px solid var(--gold); }}
    </style>
</head>
<body>
    <div id="header">
        <div class="search-group">
            <input type="text" id="comment-input" class="comment-input" value="https://github.com/SIN0NIS/hots_talent_build_auto_git" readonly onclick="window.open(this.value, '_blank')">
            <div style="display:flex; gap:8px;">
                <input type="text" id="hero-search" class="search-box" placeholder="영웅 검색..." onclick="showList()" oninput="handleSearch(this.value)">
                <button onclick="loadFromCode()" style="padding:0 15px; background:var(--p); color:white; border:none; border-radius:6px; font-weight:bold;">로드</button>
            </div>
        </div>
        <div id="hero-list-dropdown"></div>
    </div>
    <div id="capture-area">
        <div id="welcome-area">
            <div id="comment-display">히오스 빌드 사이트 입니다.</div>
            <div style="font-size:16px; color:#555;">영웅을 선택하면 정보가 나타납니다.</div>
        </div>
        <div id="hero-stat-container">
            <div id="hero-title-area" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <div id="hero-info-title" style="font-size:20px; font-weight:bold; color:var(--p);">영웅 이름</div>
                <div id="hero-role-badge" style="font-size:11px; color:var(--blue); border:1px solid var(--blue); padding:2px 6px; border-radius:4px;">역할군</div>
            </div>
            
            <div id="level-control" style="background:#25252b; padding:15px 10px 5px 10px; border-radius:6px; margin-bottom:12px;">
                <div id="level-control-wrapper">
                    <input type="range" id="level-slider" min="1" max="30" value="1" style="width:100%; accent-color:var(--p); cursor:pointer;" oninput="updateLevel(this.value)">
                    <div class="slider-ticks" id="slider-ticks"></div>
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:5px;">
                    <span id="level-display" style="font-weight:bold; color:var(--gold);">LV 1</span>
                    <span id="level-growth-total" style="font-size:10px; color:var(--green);">(+0.00%)</span>
                </div>
            </div>

            <div class="stat-grid" id="stat-grid"></div>
            <div id="ability-container" class="ability-list"></div>
        </div>
        <div id="main-content"></div>
    </div>
    <div id="footer">
        <div id="selected-summary" style="display:flex; gap:4px;"></div>
        <div style="display:flex; gap:10px; width:98%;">
            <div id="build-code" onclick="copyCode()" style="flex:3; font-size:12px; color:var(--gold); background:#1a1a1a; padding:10px; border-radius:6px; border:1px dashed var(--gold); text-align:center;">[영웅을 선택하세요]</div>
            <button onclick="takeScreenshot()" style="flex:1; background:var(--p); color:white; border:none; border-radius:6px; font-weight:bold;">📸 저장</button>
        </div>
    </div>
    <script>
        const hotsData = {json.dumps(data, ensure_ascii=False)};
        const heroList = {json.dumps(hero_list, ensure_ascii=False)};
        const imgBase = "{img_cdn_base}";
        let currentHeroData = null; let currentLevel = 1; let selectedTalents = []; let currentTalentNodes = [];

        // 슬라이더 눈금 생성 (1~30레벨 중 특성 구간 1,4,7,10,13,16,20 강조)
        function createSliderTicks() {{
            const container = document.getElementById("slider-ticks");
            const highlightLevels = [1, 4, 7, 10, 13, 16, 20, 30];
            let html = "";
            for(let i=1; i<=30; i++) {{
                const isHighlight = highlightLevels.includes(i);
                html += `<div class="tick ${{isHighlight ? 'highlight' : ''}}">
                    ${{isHighlight ? `<span class="tick-label">${{i}}</span>` : ''}}
                </div>`;
            }}
            container.innerHTML = html;
        }}

        function getChosung(str) {{
            const cho = ["ㄱ","ㄲ","ㄴ","ㄷ","ㄸ","ㄹ","ㅁ","ㅂ","ㅃ","ㅅ","ㅆ","ㅇ","ㅈ","ㅉ","ㅊ","ㅋ","ㅌ","ㅍ","ㅎ"];
            let res = ""; for(let i=0; i<str.length; i++) {{
                let c = str.charCodeAt(i) - 44032; if(c>-1 && c<11172) res += cho[Math.floor(c/588)]; else res += str.charAt(i);
            }} return res;
        }}
        function handleSearch(v) {{
            const s = v.replace(/\s/g, "").toLowerCase(); const cho = getChosung(s);
            const fil = heroList.filter(h => {{ const n = h.name.replace(/\s/g, "").toLowerCase(); return n.includes(s) || getChosung(n).includes(cho); }});
            renderList(fil); document.getElementById("hero-list-dropdown").style.display = "block";
        }}
        function processTooltip(t, lv) {{
            if(!t) return ""; let p = t.replace(/<[^>]*>?/gm, "");
            p = p.replace(/(\d+(?:\.\d+)?)\s*~~(0\.\d+)~~/g, (m, b, s) => {{
                const v = parseFloat(b) * Math.pow(1 + parseFloat(s), lv - 1);
                return "<strong>" + v.toFixed(1) + "</strong>";
            }});
            return p;
        }}
        function selectHero(id, code = null) {{
            document.getElementById("welcome-area").style.display = "none";
            document.getElementById("hero-list-dropdown").style.display = "none";
            currentHeroData = hotsData[id];
            document.getElementById("hero-search").value = currentHeroData.name;
            document.getElementById("hero-info-title").innerText = currentHeroData.name;
            document.getElementById("hero-role-badge").innerText = currentHeroData.expandedRole || "미분류";
            document.getElementById("hero-stat-container").style.display = "block";
            
            createSliderTicks(); // 영웅 선택 시 눈금 생성
            renderAbilities();
            const lvs = Object.keys(currentHeroData.talents).filter(l => currentHeroData.talents[l].length > 0).sort((a,b) => parseInt(a.replace(/\D/g,"")) - parseInt(b.replace(/\D/g,"")));
            selectedTalents = new Array(lvs.length).fill(0); currentTalentNodes = [];
            let h = ''; lvs.forEach((l, i) => {{
                let n = l.replace(/\D/g,""); if(currentHeroData.hyperlinkId === "Chromie") n = ["1","2","5","8","11","14","18"][i];
                currentTalentNodes.push(currentHeroData.talents[l]);
                h += `<div class="tier-row"><div class="tier-label">${{n}}LV</div><div style="display:flex;gap:8px;">`;
                currentHeroData.talents[l].forEach((t, ti) => {{
                    h += `<img src="${{imgBase}}${{t.icon}}" class="t-icon t-row-${{i}} t-node-${{i}}-${{ti+1}}" onclick="toggleTalent(${{i}}, ${{ti+1}}, this)">`;
                }});
                h += `</div><div class="t-info-display" id="desc-${{i}}">선택하세요.</div></div>`;
            }});
            document.getElementById("main-content").innerHTML = h;
            renderStats(); updateUI();
        }}
        function renderAbilities() {{
            const container = document.getElementById("ability-container");
            const abs = currentHeroData.abilities;
            const all = [...(abs.basic || []), ...(abs.trait || []), ...(abs.mount || []), ...(abs.activable || [])];
            let html = "";
            ["Q", "W", "E", "Trait", "Z", "Active"].forEach(type => {{
                all.filter(a => a.abilityType === type).forEach(skill => {{
                    html += `<div class="ability-item"><img src="${{imgBase}}${{skill.icon}}" class="ability-icon"><div class="ability-text">
                        <span style="font-weight:bold;color:var(--blue)">[${{type === "Trait" ? "D" : type}}] ${{skill.name}}</span>
                        <div style="font-size:10px; color:#aaa;">${{processTooltip(skill.fullTooltip || skill.description, currentLevel)}}</div></div></div>`;
                }});
            }});
            container.innerHTML = html;
        }}
        function toggleTalent(ti, tn, el) {{
            const box = document.getElementById("desc-"+ti);
            if(selectedTalents[ti] === tn) {{ selectedTalents[ti] = 0; el.classList.remove("selected"); box.innerHTML = "선택하세요."; }}
            else {{
                selectedTalents[ti] = tn; document.querySelectorAll(".t-row-"+ti).forEach(img => img.classList.remove("selected"));
                el.classList.add("selected"); const t = currentTalentNodes[ti][tn-1];
                box.innerHTML = `<b style="color:#fff;">${{t.name}}</b><br>${{processTooltip(t.fullTooltip, currentLevel)}}`;
            }}
            updateUI();
        }}
        function updateLevel(lv) {{
            currentLevel = parseInt(lv); document.getElementById("level-display").innerText = "LV " + currentLevel;
            document.getElementById("level-growth-total").innerText = "(+" + ((Math.pow(1.04, currentLevel - 1) - 1) * 100).toFixed(2) + "%)";
            if(currentHeroData) {{ renderStats(); renderAbilities(); selectedTalents.forEach((tn, ti) => {{ if(tn > 0) toggleTalent(ti, tn, document.querySelector(`.t-node-${{ti}}-${{tn}}`)); }}); }}
        }}
        function renderStats() {{
            const h = currentHeroData; const l = h.life; const w = (h.weapons && h.weapons[0]) ? h.weapons[0] : {{damage:0, range:0, period:1, damageScale:0.04}};
            const c = (b, s, lv) => (b * Math.pow(1 + (s || 0.04), lv - 1)).toFixed(0);
            const sArr = [{{l:"체력", v:c(l.amount, l.scale, currentLevel)}}, {{l:"공격", v:c(w.damage, w.damageScale, currentLevel)}}, {{l:"거리", v:w.range}}, {{l:"피격", v:h.radius}}];
            document.getElementById("stat-grid").innerHTML = sArr.map(s => `<div class="stat-item"><span style="color:#888;">${{s.l}}</span><b class="stat-value">${{s.v}}</b></div>`).join("");
        }}
        function updateUI() {{
            const sum = selectedTalents.map((tn, ti) => tn === 0 ? `<div style="width:17px;height:17px;border:1px dashed #333;border-radius:3px;"></div>` : `<img src="${{imgBase}}${{currentTalentNodes[ti][tn-1].icon}}" class="summary-img">`).join("");
            document.getElementById("selected-summary").innerHTML = sum;
            document.getElementById("build-code").innerText = currentHeroData ? `[T${{selectedTalents.join("")}},${{currentHeroData.hyperlinkId}}]` : "영웅 선택";
        }}
        function renderList(l) {{ document.getElementById("hero-list-dropdown").innerHTML = l.map(h => `<div class="hero-item" onclick="selectHero('${{h.id}}')">${{h.name}}</div>`).join(""); }}
        function showList() {{ handleSearch(""); }}
        function copyCode() {{ navigator.clipboard.writeText(document.getElementById("build-code").innerText); alert("복사 완료"); }}
        function takeScreenshot() {{
            const name = currentHeroData ? currentHeroData.name : "미선택";
            html2canvas(document.getElementById("capture-area"), {{useCORS:true, backgroundColor:"#0b0b0d"}}).then(c => {{
                const l = document.createElement('a'); l.download = `빌드_${{name}}.png`; l.href = c.toDataURL(); l.click();
            }});
        }}
    </script>
</body>
</html>"""

    main_page = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>히오스 빌드 메이커 - 통합</title>
    <style>body, html {{ margin: 0; padding: 0; height: 100%; width: 100%; overflow: hidden; background: #0b0b0d; }} iframe {{ width: 100%; height: 100%; border: none; display: block; }}</style>
</head>
<body><iframe src="{output_file}"></iframe></body>
</html>"""

    with open(output_file, 'w', encoding='utf-8') as f: f.write(html_content)
    with open('hots_talent_build.html', 'w', encoding='utf-8') as f: f.write(main_page)

if __name__ == "__main__":
    generate_html()
