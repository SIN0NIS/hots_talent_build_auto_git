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

    # 수정 시간 순으로 가장 최신 파일 선택
    json_path = max(json_files, key=os.path.getmtime)
    
    # 2. 파일명 및 시간 설정
    now = datetime.now()
    timestamp = now.strftime("%y%m%d_%H%M")
    output_file = f"index_{timestamp}.html"
    img_cdn_base = "https://raw.githubusercontent.com/SIN0NIS/images/main/abilitytalents/"

    print(f"사용 데이터: {json_path}")
    print(f"생성 파일: {output_file}")

    # 3. 데이터 로드
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    hero_list = sorted([{"id": k, "name": v['name'], "hId": v.get('hyperlinkId', k)} for k, v in data.items() if 'name' in v], key=lambda x: x['name'])

    # 4. HTML 템플릿 작성
    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>히오스 빌드 메이커 Pro</title>
    <script src="https://html2canvas.hertzen.com/dist/html2canvas.min.js"></script>
    <style>
        :root {{ --p: #a333ff; --bg: #0b0b0d; --card: #16161a; --blue: #00d4ff; --gold: #ffd700; --green: #00ff00; }}
        body {{ margin: 0; background: var(--bg); color: white; font-family: sans-serif; display: flex; flex-direction: column; height: 100vh; overflow: hidden; }}
        #header {{ padding: 10px; background: #1a1a1e; border-bottom: 1px solid #333; flex-shrink: 0; position: relative; z-index: 2000; }}
        
        .search-group {{ display: flex; flex-direction: column; gap: 8px; }}
        .comment-input {{ width: 100%; padding: 8px; background: #111; color: var(--green); border: 1px solid #444; border-radius: 4px; font-size: 12px; outline: none; }}
        .search-box {{ flex: 1; padding: 12px; background: #222; color: white; border: 1px solid var(--p); border-radius: 6px; font-size: 14px; outline: none; }}
        
        #hero-list-dropdown {{ position: absolute; width: calc(100% - 20px); max-height: 300px; background: #2a2a2a; overflow-y: auto; z-index: 3000; border-radius: 4px; display: none; border: 1px solid var(--p); margin-top: 5px; }}
        .hero-item {{ padding: 12px; border-bottom: 1px solid #333; cursor: pointer; }}
        .hero-item:hover {{ background: var(--p); }}
        
        #capture-area {{ flex: 1; display: flex; flex-direction: column; overflow-y: auto; padding-bottom: 220px; background: #0b0b0d; position: relative; }}
        
        /* 초기 화면 코멘트 영역 */
        #welcome-area {{ flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 40px; text-align: center; color: #666; }}
        #comment-display {{ color: var(--green); font-size: 18px; font-weight: bold; margin-bottom: 15px; white-space: pre-wrap; }}
        
        #hero-stat-container {{ background: #1a1a20; margin: 10px; padding: 15px; border-radius: 8px; border: 1px solid #333; display: none; }}
        .stat-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 15px; }}
        .stat-item {{ background: #111; padding: 8px; border-radius: 4px; font-size: 12px; }}
        
        .ability-list {{ border-top: 1px solid #333; padding-top: 10px; display: flex; flex-direction: column; gap: 10px; }}
        .ability-item {{ display: flex; gap: 10px; align-items: flex-start; background: #111; padding: 8px; border-radius: 6px; }}
        .ability-icon {{ width: 34px; height: 34px; border-radius: 4px; flex-shrink: 0; }}
        
        .tier-row {{ display: flex; align-items: center; background: var(--card); padding: 8px 10px; border-radius: 6px; border-left: 5px solid var(--p); gap: 10px; min-height: 65px; margin: 3px 5px; }}
        .tier-label {{ color: var(--blue); font-weight: bold; width: 35px; flex-shrink: 0; font-size: 12px; text-align: center; }}
        .t-icon {{ width: 40px; height: 40px; border: 1px solid #444; cursor: pointer; border-radius: 5px; background: #000; }}
        .t-icon.selected {{ border-color: var(--gold); box-shadow: 0 0 10px var(--gold); transform: scale(1.1); z-index: 10; }}
        
        #footer {{ position: fixed; bottom: 0; width: 100%; background: rgba(0,0,0,0.95); border-top: 2px solid var(--p); padding: 10px; box-sizing: border-box; display: flex; flex-direction: column; align-items: center; gap: 8px; backdrop-filter: blur(10px); z-index: 1500; }}
        .summary-img {{ width: 45px; height: 45px; border-radius: 3px; border: 1px solid var(--gold); }}
    </style>
</head>
<body>
    <div id="header">
        <div class="search-group">
            <input type="text" id="comment-input" class="comment-input" placeholder="코멘트를 입력하세요..." oninput="syncComment(this.value)" value="SINONIS입니다">
            <div style="display:flex; gap:8px;">
                <input type="text" id="hero-search" class="search-box" placeholder="영웅 검색..." onclick="showList()" oninput="handleSearch(this.value)">
                <button onclick="loadFromCode()" style="padding:0 15px; background:var(--p); color:white; border:none; border-radius:6px; font-weight:bold;">로드</button>
            </div>
        </div>
        <div id="hero-list-dropdown"></div>
    </div>

    <div id="capture-area">
        <div id="welcome-area">
            <div id="comment-display">SINONIS입니다</div>
            <div style="font-size:12px;">영웅을 선택하여 빌드 제작을 시작하세요.</div>
        </div>

        <div id="hero-stat-container">
            <div id="hero-title-area" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <div id="hero-info-title" style="font-size:20px; font-weight:bold; color:var(--p);"></div>
                <div id="hero-role-badge" style="font-size:11px; color:var(--blue); border:1px solid var(--blue); padding:2px 6px; border-radius:4px;"></div>
            </div>
            <div class="stat-grid" id="stat-grid"></div>
            <div id="ability-container" class="ability-list"></div>
        </div>
        <div id="main-content"></div>
    </div>

    <div id="footer">
        <div id="selected-summary" style="display:flex; gap:6px; min-height:40px;"></div>
        <div style="display:flex; gap:10px; width:98%;">
            <div id="build-code" onclick="copyCode()" style="flex:3; font-size:14px; color:var(--gold); background:#1a1a1a; padding:10px; border-radius:6px; border:1px dashed var(--gold); text-align:center;">[영웅을 선택하세요]</div>
            <button onclick="takeScreenshot()" style="flex:1; background:var(--p); color:white; border:none; border-radius:6px; font-weight:bold;">📸 저장</button>
        </div>
        <div style="font-size:9px; color:#444; margin-top:5px;">제작자: SINONIS | 데이터: {json_path}</div>
    </div>

    <script>
        const hotsData = {json.dumps(data, ensure_ascii=False)};
        const heroList = {json.dumps(hero_list, ensure_ascii=False)};
        const imgBase = "{img_cdn_base}";
        let currentHeroData = null; let currentLevel = 1; let selectedTalents = []; let currentTalentNodes = [];

        function syncComment(val) {{
            document.getElementById("comment-display").innerText = val;
        }}

        function selectHero(id, code = null) {{
            document.getElementById("welcome-area").style.display = "none";
            document.getElementById("hero-list-dropdown").style.display = "none";
            currentHeroData = hotsData[id];
            
            document.getElementById("hero-search").value = currentHeroData.name;
            document.getElementById("hero-info-title").innerText = currentHeroData.name;
            document.getElementById("hero-role-badge").innerText = currentHeroData.expandedRole || "미분류";
            document.getElementById("hero-stat-container").style.display = "block";
            
            renderAbilities();
            renderTalents();
            renderStats();
            updateUI();
        }}

        function renderAbilities() {{
            const container = document.getElementById("ability-container");
            const abs = currentHeroData.abilities;
            const targetTypes = ["Q", "W", "E", "Trait", "Z", "Active"];
            let html = "";
            const allAbilities = [...(abs.basic || []), ...(abs.trait || []), ...(abs.mount || []), ...(abs.activable || [])];
            
            targetTypes.forEach(type => {{
                allAbilities.filter(a => a.abilityType === type).forEach(skill => {{
                    let label = type === "Trait" ? "D" : type;
                    html += `<div class="ability-item">
                        <img src="${{imgBase}}${{skill.icon}}" class="ability-icon">
                        <div class="ability-text">
                            <span class="ability-name"><span style="color:var(--gold)">[${{label}}]</span> ${{skill.name}}</span>
                            <div>${{skill.description || ""}}</div>
                        </div>
                    </div>`;
                }});
            }});
            container.innerHTML = html;
        }}

        function renderTalents() {{
            const lvs = Object.keys(currentHeroData.talents).filter(l => currentHeroData.talents[l].length > 0).sort((a,b) => parseInt(a) - parseInt(b));
            selectedTalents = new Array(lvs.length).fill(0); currentTalentNodes = [];
            let h = '';
            lvs.forEach((l, i) => {{
                currentTalentNodes.push(currentHeroData.talents[l]);
                h += `<div class="tier-row"><div class="tier-label">${{l.replace(/\D/g,"")}}LV</div><div style="display:flex;gap:8px;">`;
                currentHeroData.talents[l].forEach((t, ti) => {{
                    h += `<img src="${{imgBase}}${{t.icon}}" class="t-icon t-row-${{i}} t-node-${{i}}-${{ti+1}}" onclick="toggleTalent(${{i}}, ${{ti+1}}, this)">`;
                }});
                h += `</div><div class="t-info-display" id="desc-${{i}}">특성을 선택하세요.</div></div>`;
            }});
            document.getElementById("main-content").innerHTML = h;
        }}

        function toggleTalent(ti, tn, el) {{
            const box = document.getElementById("desc-"+ti);
            if(selectedTalents[ti] === tn) {{
                selectedTalents[ti] = 0; el.classList.remove("selected");
                box.innerHTML = "특성을 선택하세요.";
            }} else {{
                selectedTalents[ti] = tn;
                document.querySelectorAll(".t-row-"+ti).forEach(img => img.classList.remove("selected"));
                el.classList.add("selected");
                const t = currentTalentNodes[ti][tn-1];
                box.innerHTML = `<b style="color:#fff;">${{t.name}}</b><br>${{t.description || ""}}`;
            }}
            updateUI();
        }}

        function renderStats() {{
            const h = currentHeroData; const l = h.life;
            const sArr = [{{l:"체력", v:l.amount}}, {{l:"재생", v:l.regenRate}}, {{l:"공격력", v:h.weapons[0].damage}}, {{l:"범위", v:h.radius}}];
            document.getElementById("stat-grid").innerHTML = sArr.map(s => `<div class="stat-item"><span style="color:#888;">${{s.l}}</span><br><b class="stat-value">${{s.v}}</b></div>`).join("");
        }}

        function updateUI() {{
            const sum = selectedTalents.map((tn, ti) => tn === 0 ? `<div style="width:17px;height:17px;border:1px dashed #333;border-radius:3px;"></div>` : `<img src="${{imgBase}}${{currentTalentNodes[ti][tn-1].icon}}" class="summary-img">`).join("");
            document.getElementById("selected-summary").innerHTML = sum;
            document.getElementById("build-code").innerText = currentHeroData ? `[T${{selectedTalents.join("")}},${{currentHeroData.hyperlinkId}}]` : "[영웅을 선택하세요]";
        }}

        function handleSearch(v) {{
            const fil = heroList.filter(h => h.name.includes(v));
            renderList(fil); document.getElementById("hero-list-dropdown").style.display = "block";
        }}
        function renderList(l) {{ document.getElementById("hero-list-dropdown").innerHTML = l.map(h => `<div class="hero-item" onclick="selectHero('${{h.id}}')">${{h.name}}</div>`).join(""); }}
        function showList() {{ handleSearch(""); }}
        function copyCode() {{ navigator.clipboard.writeText(document.getElementById("build-code").innerText); alert("코드 복사 완료"); }}
        
        function takeScreenshot() {{
            const heroName = currentHeroData ? currentHeroData.name : "미선택";
            const dateStr = new Date().toISOString().slice(2,10).replace(/-/g,"");
            const timeStr = new Date().toTimeString().slice(0,5).replace(":","");
            const fileName = `빌드_${{heroName}}_${{dateStr}}_${{timeStr}}.png`;

            html2canvas(document.getElementById("capture-area"), {{useCORS:true, backgroundColor:"#0b0b0d"}}).then(c => {{
                const l = document.createElement('a');
                l.download = fileName;
                l.href = c.toDataURL();
                l.click();
            }});
        }}
    </script>
</body>
</html>"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    with open('hots_talent_build.html', 'w', encoding='utf-8') as f:
        f.write(f'<!DOCTYPE html><html><body style="margin:0;"><iframe src="{output_file}" style="width:100%; height:100vh; border:none;"></iframe></body></html>')

if __name__ == "__main__":
    generate_html()
