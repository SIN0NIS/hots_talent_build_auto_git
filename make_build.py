import json
import os
import glob
from datetime import datetime

def generate_html():
    # 1. 최신 kokr.json 파일 탐색
    json_files = glob.glob('*kokr*.json')
    if not json_files:
        print("JSON 파일을 찾을 수 없습니다.")
        return
    json_path = max(json_files, key=os.path.getmtime)
    
    now = datetime.now()
    timestamp = now.strftime("%y%m%d_%H%M")
    output_file = f"index_{timestamp}.html"
    img_cdn_base = "https://raw.githubusercontent.com/SIN0NIS/images/main/abilitytalents/"

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    hero_list = sorted([{"id": k, "name": v['name'], "hId": v.get('hyperlinkId', k)} for k, v in data.items() if 'name' in v], key=lambda x: x['name'])

    # 2. HTML 템플릿 (스킬 레이아웃 및 아이콘 크기 수정)
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
        #header {{ padding: 10px; background: #1a1a1e; border-bottom: 1px solid #333; flex-shrink: 0; position: relative; }}
        .search-group {{ display: flex; gap: 8px; }}
        .search-box {{ flex: 1; padding: 12px; background: #222; color: white; border: 1px solid var(--p); border-radius: 6px; font-size: 14px; outline: none; }}
        
        #capture-area {{ flex: 1; display: flex; flex-direction: column; overflow-y: auto; padding-bottom: 180px; }}
        
        /* 캐릭터 스펙 및 스킬 영역 */
        #hero-stat-container {{ background: #1a1a20; margin: 10px; padding: 15px; border-radius: 8px; border: 1px solid #333; display: none; }}
        .stat-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 15px; }}
        .stat-item {{ background: #111; padding: 8px; border-radius: 4px; font-size: 11px; }}
        
        /* 기본 스킬 레이아웃 */
        .ability-section {{ border-top: 1px solid #333; padding-top: 10px; }}
        .ability-card {{ display: flex; gap: 10px; background: #111; padding: 8px; border-radius: 6px; margin-bottom: 6px; align-items: flex-start; }}
        .ability-img-box {{ position: relative; flex-shrink: 0; }}
        .ability-img {{ width: 34px; height: 34px; border-radius: 4px; border: 1px solid #444; }}
        .ability-key {{ position: absolute; bottom: -2px; right: -2px; background: rgba(0,0,0,0.8); color: var(--gold); font-size: 10px; padding: 1px 4px; border-radius: 3px; font-weight: bold; border: 0.5px solid var(--gold); }}
        .ability-info {{ flex: 1; font-size: 11px; }}
        .ability-name {{ font-weight: bold; color: var(--blue); margin-bottom: 2px; display: block; }}
        
        /* 특성 줄 레이아웃 */
        .tier-row {{ display: flex; align-items: center; background: var(--card); padding: 8px 10px; border-radius: 6px; border-left: 5px solid var(--p); gap: 10px; margin: 3px 5px; }}
        .tier-label {{ color: var(--blue); font-weight: bold; width: 35px; flex-shrink: 0; font-size: 12px; }}
        .t-icon {{ width: 40px; height: 40px; border: 1px solid #444; border-radius: 5px; cursor: pointer; }}
        .t-icon.selected {{ border-color: var(--gold); box-shadow: 0 0 8px var(--gold); transform: scale(1.05); }}
        
        /* 하단 바 아이콘 크기 절반 수정 (기존 약 40px -> 22px) */
        #footer {{ position: fixed; bottom: 0; width: 100%; background: rgba(0,0,0,0.95); border-top: 2px solid var(--p); padding: 8px; box-sizing: border-box; display: flex; flex-direction: column; align-items: center; gap: 6px; z-index: 2000; }}
        .summary-img {{ width: 22px; height: 22px; border-radius: 3px; border: 1px solid var(--gold); }}
        .summary-placeholder {{ width: 22px; height: 22px; border: 1px dashed #444; border-radius: 3px; }}
        #build-code {{ font-size: 12px; color: var(--gold); background: #1a1a1a; padding: 6px; border-radius: 4px; width: 95%; text-align: center; border: 1px dashed #444; }}
    </style>
</head>
<body>
    <div id="header">
        <div class="search-group">
            <input type="text" id="hero-search" class="search-box" placeholder="영웅 검색..." onclick="showList()" oninput="handleSearch(this.value)">
            <div id="hero-list-dropdown" style="position:absolute; top:50px; left:10px; right:10px; background:#222; z-index:3000; display:none; max-height:200px; overflow-y:auto; border:1px solid var(--p);"></div>
        </div>
    </div>
    <div id="capture-area">
        <div id="hero-stat-container">
            <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
                <span id="hero-info-title" style="font-size:18px; font-weight:bold;"></span>
                <span id="hero-role-badge" style="color:var(--blue); font-size:12px;"></span>
            </div>
            <div class="stat-grid" id="stat-grid"></div>
            
            <div class="ability-section" id="ability-list"></div>
        </div>
        <div id="main-content"></div>
    </div>
    <div id="footer">
        <div id="selected-summary" style="display:flex; gap:4px;"></div>
        <div id="build-code" onclick="copyCode()">[영웅을 선택하세요]</div>
        <button onclick="takeScreenshot()" style="width:95%; background:var(--p); color:white; border:none; padding:8px; border-radius:4px; font-weight:bold;">📸 이미지 저장</button>
    </div>

    <script>
        const hotsData = {json.dumps(data, ensure_ascii=False)};
        const heroList = {json.dumps(hero_list, ensure_ascii=False)};
        const imgBase = "{img_cdn_base}";
        let currentHeroData = null; let selectedTalents = [];

        function selectHero(id) {{
            currentHeroData = hotsData[id];
            document.getElementById("hero-list-dropdown").style.display = "none";
            document.getElementById("hero-search").value = currentHeroData.name;
            document.getElementById("hero-stat-container").style.display = "block";
            document.getElementById("hero-info-title").innerText = currentHeroData.name;
            document.getElementById("hero-role-badge").innerText = currentHeroData.expandedRole || "";
            
            renderStats();
            renderAbilities(); // 스킬 렌더링 호출
            renderTalents();
            updateUI();
        }}

        function renderAbilities() {{
            const abArea = document.getElementById("ability-list");
            let h = '<div style="font-size:12px; font-weight:bold; color:var(--gold); margin-bottom:8px;">기본 기술 및 고유 능력</div>';
            
            // basic 스킬과 trait(고유 능력) 합치기
            const basics = currentHeroData.abilities.basic || [];
            const traits = currentHeroData.abilities.trait || [];
            const allAbilities = [...basics, ...traits];

            allAbilities.forEach(a => {{
                // 특성 찍어야 생기는 스킬은 제외
                if(a.abilityType === "Active") return; 
                
                const key = a.abilityType === "Trait" ? "D" : (a.abilityType || "ETC");
                h += `
                <div class="ability-card">
                    <div class="ability-img-box">
                        <img src="${{imgBase}}${{a.icon}}" class="ability-img">
                        <div class="ability-key">${{key}}</div>
                    </div>
                    <div class="ability-info">
                        <span class="ability-name">${{a.name}}</span>
                        <div style="color:#aaa; line-height:1.3;">${{a.description || ""}}</div>
                    </div>
                </div>`;
            }});
            abArea.innerHTML = h;
        }}

        function renderStats() {{
            const h = currentHeroData; const l = h.life;
            const sArr = [
                {{l: "체력", v: l.amount}},
                {{l: "재생", v: l.regenRate}},
                {{l: "자원", v: (h.energy ? h.energy.amount : 0)}},
                {{l: "사거리", v: (h.weapons ? h.weapons[0].range : 0)}}
            ];
            document.getElementById("stat-grid").innerHTML = sArr.map(s => `
                <div class="stat-item"><span style="color:#888;">${{s.l}}</span><br><b>${{s.v}}</b></div>
            `).join("");
        }}

        function renderTalents() {{
            const tiers = Object.keys(currentHeroData.talents).sort((a,b)=>parseInt(a)-parseInt(b));
            selectedTalents = new Array(tiers.length).fill(0);
            let h = "";
            tiers.forEach((t, i) => {{
                h += `<div class="tier-row"><div class="tier-label">${{t}}</div><div style="display:flex; gap:8px;">`;
                currentHeroData.talents[t].forEach((tal, ti) => {{
                    h += `<img src="${{imgBase}}${{tal.icon}}" class="t-icon t-row-${{i}}" onclick="toggleTalent(${{i}}, ${{ti+1}}, this, '${{tal.icon}}')">`;
                }});
                h += `</div></div>`;
            }});
            document.getElementById("main-content").innerHTML = h;
        }}

        function toggleTalent(ti, tn, el, icon) {{
            if(selectedTalents[ti] === tn) selectedTalents[ti] = 0;
            else selectedTalents[ti] = {{tn, icon}};
            
            document.querySelectorAll(".t-row-"+ti).forEach(img => img.classList.remove("selected"));
            if(selectedTalents[ti]) el.classList.add("selected");
            updateUI();
        }}

        function updateUI() {{
            const summary = selectedTalents.map(t => t === 0 ? `<div class="summary-placeholder"></div>` : `<img src="${{imgBase}}${{t.icon}}" class="summary-img">`).join("");
            document.getElementById("selected-summary").innerHTML = summary;
            const code = selectedTalents.map(t => t === 0 ? "0" : t.tn).join("");
            document.getElementById("build-code").innerText = currentHeroData ? `[T${{code}},${{currentHeroData.hyperlinkId}}]` : "";
        }}

        function handleSearch(v) {{
            const fil = heroList.filter(h => h.name.includes(v));
            const drop = document.getElementById("hero-list-dropdown");
            drop.style.display = "block";
            drop.innerHTML = fil.map(h => `<div style="padding:10px; border-bottom:1px solid #333;" onclick="selectHero('${{h.id}}')">${{h.name}}</div>`).join("");
        }}
        function showList() {{ handleSearch(""); }}
        function copyCode() {{ navigator.clipboard.writeText(document.getElementById("build-code").innerText); alert("코드 복사됨"); }}
        function takeScreenshot() {{
            html2canvas(document.getElementById("capture-area"), {{useCORS:true, backgroundColor:"#0b0b0d"}}).then(c => {{
                const l = document.createElement('a'); l.download="build.png"; l.href=c.toDataURL(); l.click();
            }});
        }}
    </script>
</body>
</html>"""

    # 3. 파일 저장 및 메인 업데이트
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    with open('hots_talent_build.html', 'w', encoding='utf-8') as f:
        f.write(f'<!DOCTYPE html><html><body style="margin:0;"><iframe src="{output_file}" style="width:100%; height:100vh; border:none;"></iframe></body></html>')

if __name__ == "__main__":
    generate_html()
