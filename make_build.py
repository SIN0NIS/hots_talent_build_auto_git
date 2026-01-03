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
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>히오스 빌드 메이커 Pro</title>
    <script src="https://html2canvas.hertzen.com/dist/html2canvas.min.js"></script>
    <style>
        :root {{ --p: #a333ff; --bg: #0b0b0d; --card: #16161a; --blue: #00d4ff; --gold: #ffd700; --green: #00ff00; }}
        body {{ margin: 0; background: var(--bg); color: white; font-family: sans-serif; display: flex; flex-direction: column; height: 100vh; overflow: hidden; }}
        #header {{ padding: 10px; background: #1a1a1e; border-bottom: 1px solid #333; flex-shrink: 0; position: relative; z-index: 2000; }}
        .search-group {{ display: flex; flex-direction: column; gap: 8px; }}
        .search-box {{ flex: 1; padding: 12px; background: #222; color: white; border: 1px solid var(--p); border-radius: 6px; font-size: 14px; outline: none; }}
        .comment-input {{ width: 100%; padding: 8px; background: #111; color: var(--green); border: 1px solid #444; border-radius: 4px; font-size: 12px; }}
        
        #hero-list-dropdown {{ position: absolute; width: calc(100% - 20px); max-height: 300px; background: #2a2a2a; overflow-y: auto; z-index: 3000; border-radius: 4px; display: none; border: 1px solid var(--p); margin-top: 5px; }}
        .hero-item {{ padding: 12px; border-bottom: 1px solid #333; cursor: pointer; }}
        .hero-item:hover {{ background: var(--p); }}
        
        #capture-area {{ flex: 1; display: flex; flex-direction: column; overflow-y: auto; padding-bottom: 220px; background: #0b0b0d; }}
        #welcome-area {{ padding: 60px 20px; text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: center; }}
        #comment-display {{ color: var(--green); font-size: 18px; font-weight: bold; margin-bottom: 10px; white-space: pre-wrap; }}
        
        #hero-stat-container {{ background: #1a1a20; margin: 10px; padding: 15px; border-radius: 8px; border: 1px solid #333; display: none; }}
        .stat-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 15px; }}
        .stat-item {{ background: #111; padding: 8px; border-radius: 4px; font-size: 12px; display: flex; flex-direction: column; gap: 2px; }}
        .stat-value {{ color: #fff; font-weight: bold; font-size: 13px; }}
        
        .ability-list {{ border-top: 1px solid #333; padding-top: 10px; display: flex; flex-direction: column; gap: 10px; }}
        .ability-item {{ display: flex; gap: 10px; align-items: flex-start; background: #111; padding: 8px; border-radius: 6px; }}
        .ability-icon {{ width: 34px; height: 34px; border: 1px solid #444; border-radius: 4px; flex-shrink: 0; }}
        .ability-text {{ flex: 1; font-size: 11px; color: #ccc; line-height: 1.4; }}
        .ability-name {{ font-weight: bold; color: var(--blue); display: block; margin-bottom: 2px; }}

        .tier-row {{ display: flex; align-items: center; background: var(--card); padding: 8px 10px; border-radius: 6px; border-left: 5px solid var(--p); gap: 10px; min-height: 65px; margin: 3px 5px; }}
        .tier-label {{ color: var(--blue); font-weight: bold; width: 35px; flex-shrink: 0; font-size: 12px; text-align: center; }}
        .t-icon {{ width: 40px; height: 40px; border: 1px solid #444; cursor: pointer; border-radius: 5px; background: #000; }}
        .t-icon.selected {{ border-color: var(--gold); box-shadow: 0 0 10px var(--gold); transform: scale(1.1); z-index: 10; }}
        .t-info-display {{ flex: 1; font-size: 11px; color: #ccc; line-height: 1.4; padding-left: 10px; border-left: 1px solid #444; height: 46px; overflow-y: auto; }}
        
        #footer {{ position: fixed; bottom: 0; width: 100%; background: rgba(0,0,0,0.95); border-top: 2px solid var(--p); padding: 10px; box-sizing: border-box; display: flex; flex-direction: column; align-items: center; gap: 8px; backdrop-filter: blur(10px); z-index: 1500; }}
        .summary-img {{ width: 45px; height: 45px; border-radius: 3px; border: 1px solid var(--gold); }}
    </style>
</head>
<body>
    <div id="header">
        <div class="search-group">
           	<div style="position: relative;">
		    <input type="text" id="comment-input" class="comment-input" 
	    		value="https://github.com/SIN0NIS/hots_talent_build_auto_git" 
	    		readonly 
	    		style="cursor: pointer; color: var(--blue); text-decoration: underline;" 
	    		onclick="window.open(this.value, '_blank')">
        	</div>
            <div style="display:flex; gap:8px;">
                <input type="text" id="hero-search" class="search-box" placeholder="영웅 검색 또는 코드 입력..." onclick="showList()" oninput="handleSearch(this.value)">
                <button onclick="loadFromCode()" style="padding:0 15px; background:var(--p); color:white; border:none; border-radius:6px; font-weight:bold;">로드</button>
            </div>
        </div>
        <div id="hero-list-dropdown"></div>
    </div>
    <div id="capture-area">
        <div id="welcome-area">
            <div id="comment-display">히오스 빌드 사이트 입니다. 상단 주소 참고해주세요. </div>
            <div style="font-size:20px; color:#555;">영웅을 선택하면 상세 정보가 나타납니다.</div>
        </div>
        <div id="hero-stat-container">
            <div id="hero-title-area" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <div id="hero-info-title" style="font-size:20px; font-weight:bold; color:var(--p);">영웅 이름</div>
                <div id="hero-role-badge" style="font-size:11px; color:var(--blue); border:1px solid var(--blue); padding:2px 6px; border-radius:4px;">역할군</div>
            </div>
            <div id="level-control" style="background:#25252b; padding:10px; border-radius:6px; margin-bottom:12px; display:flex; align-items:center; gap:15px;">
                <input type="range" id="level-slider" min="1" max="30" value="1" style="flex:1; accent-color:var(--p);" oninput="updateLevel(this.value)">
                <div style="display:flex; flex-direction:column; align-items:center; min-width:95px;">
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
        <div id="selected-summary" style="display:flex; gap:6px; min-height:40px;"></div>
        <div style="display:flex; gap:10px; width:98%;">
            <div id="build-code" onclick="copyCode()" style="flex:3; font-size:14px; color:var(--gold); background:#1a1a1a; padding:10px; border-radius:6px; border:1px dashed var(--gold); text-align:center;">[영웅을 선택하세요]</div>
            <button onclick="takeScreenshot()" style="flex:1; background:var(--p); color:white; border:none; border-radius:6px; font-weight:bold;">📸 저장</button>
        </div>
    </div>
    <script>
        const hotsData = {json.dumps(data, ensure_ascii=False)};
        const heroList = {json.dumps(hero_list, ensure_ascii=False)};
        const imgBase = "{img_cdn_base}";
        let currentHeroData = null; let currentLevel = 1; let selectedTalents = []; let currentTalentNodes = [];

        function updateComment(val) {{ document.getElementById("comment-display").innerText = val; }}
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
                return "<strong>" + v.toFixed(1) + "</strong>(+" + (parseFloat(s)*100).toFixed(2) + "%)";
            }});
            return p.replace(/~~(0\.\d+)~~/g, (m, s) => "(+" + (parseFloat(s)*100).toFixed(2) + "%)");
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
            const lvs = Object.keys(currentHeroData.talents).filter(l => currentHeroData.talents[l].length > 0).sort((a,b) => parseInt(a.replace(/\D/g,"")) - parseInt(b.replace(/\D/g,"")));
            selectedTalents = new Array(lvs.length).fill(0); currentTalentNodes = [];
            let h = ''; lvs.forEach((l, i) => {{
                let n = l.replace(/\D/g,""); if(currentHeroData.hyperlinkId === "Chromie") n = ["1","2","5","8","11","14","18"][i];
                currentTalentNodes.push(currentHeroData.talents[l]);
                h += `<div class="tier-row"><div class="tier-label">${{n}}LV</div><div style="display:flex;gap:8px;">`;
                currentHeroData.talents[l].forEach((t, ti) => {{
                    h += `<img src="${{imgBase}}${{t.icon}}" class="t-icon t-row-${{i}} t-node-${{i}}-${{ti+1}}" onclick="toggleTalent(${{i}}, ${{ti+1}}, this)">`;
                }});
                h += `</div><div class="t-info-display" id="desc-${{i}}">특성을 선택하세요.</div></div>`;
            }});
            document.getElementById("main-content").innerHTML = h;
            renderStats(); updateUI();
        }}
        function renderAbilities() {{
            const container = document.getElementById("ability-container");
            const abs = currentHeroData.abilities;
            const targetTypes = ["Q", "W", "E", "Trait", "Z", "Active"];
            let html = "";
            const all = [...(abs.basic || []), ...(abs.trait || []), ...(abs.mount || []), ...(abs.activable || [])];
            targetTypes.forEach(type => {{
                all.filter(a => a.abilityType === type).forEach(skill => {{
                    const label = type === "Trait" ? "D" : type;
                    html += `<div class="ability-item"><img src="${{imgBase}}${{skill.icon}}" class="ability-icon"><div class="ability-text">
                        <span class="ability-name"><span style="color:var(--gold)">[${{label}}]</span> ${{skill.name}}</span>
                        <div>${{processTooltip(skill.fullTooltip || skill.description, currentLevel)}}</div></div></div>`;
                }});
            }});
            container.innerHTML = html;
        }}
        function toggleTalent(ti, tn, el) {{
            const box = document.getElementById("desc-"+ti);
            if(selectedTalents[ti] === tn) {{ selectedTalents[ti] = 0; el.classList.remove("selected"); box.innerHTML = "특성을 선택하세요."; }}
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
            const h = currentHeroData; 
            const l = h.life; 
            const e = h.energy || {{ amount: 0, scale: 0 }};
            const w = (h.weapons && h.weapons[0]) ? h.weapons[0] : {{damage:0, range:0, period:1, damageScale:0.04}};
            const c = (b, s, lv) => (b * Math.pow(1 + (s || 0.04), lv - 1)).toFixed(1);
            const sArr = [
                {{l:"체력", v:c(l.amount, l.scale, currentLevel), s:l.scale}}, 
                {{l:"마나", v:e.amount > 0 ? c(e.amount, e.scale, currentLevel) : "없음", s:e.amount > 0 ? e.scale : 0}},
                {{l:"공격력", v:c(w.damage, w.damageScale, currentLevel), s:w.damageScale}}, 
                {{l:"공격사거리", v:w.range.toFixed(1), s:0}}, 
                {{l:"공격주기", v:w.period.toFixed(2) + "s", s:0}},
                {{l:"피격크기", v:h.radius.toFixed(2), s:0}}
            ];
            document.getElementById("stat-grid").innerHTML = sArr.map(s => `<div class="stat-item"><span style="color:#888;">${{s.l}} ${{s.s > 0 ? `<span style="color:var(--green);font-size:10px;">(+${{(s.s*100).toFixed(0)}}%)</span>` : ""}}</span><b class="stat-value">${{s.v}}</b></div>`).join("");
          0 }}

        
        function updateUI() {{
            const sum = selectedTalents.map((tn, ti) => tn === 0 ? `<div style="width:17px;height:17px;border:1px dashed #333;border-radius:3px;"></div>` : `<img src="${{imgBase}}${{currentTalentNodes[ti][tn-1].icon}}" class="summary-img">`).join("");
            document.getElementById("selected-summary").innerHTML = sum;
            document.getElementById("build-code").innerText = currentHeroData ? `[T${{selectedTalents.join("")}},${{currentHeroData.hyperlinkId}}]` : "[영웅을 선택하세요]";
        }}
        function renderList(l) {{ document.getElementById("hero-list-dropdown").innerHTML = l.map(h => `<div class="hero-item" onclick="selectHero('${{h.id}}')">${{h.name}}</div>`).join(""); }}
        function showList() {{ handleSearch(""); }}
        function copyCode() {{ navigator.clipboard.writeText(document.getElementById("build-code").innerText); alert("복사 완료"); }}
        function takeScreenshot() {{
            const name = currentHeroData ? currentHeroData.name : "미선택";
            const time = new Date().toISOString().slice(2,16).replace(/[-T:]/g,"");
            html2canvas(document.getElementById("capture-area"), {{useCORS:true, backgroundColor:"#0b0b0d"}}).then(c => {{
                const l = document.createElement('a'); l.download = `빌드_${{name}}_${{time}}.png`; l.href = c.toDataURL(); l.click();
            }});
        }}
    </script>
</body>
</html>"""

    with open(output_file, 'w', encoding='utf-8') as f: f.write(html_content)
    with open('hots_talent_build.html', 'w', encoding='utf-8') as f:
        f.write(f'<!DOCTYPE html><html><body style="margin:0;"><iframe src="{output_file}" style="width:100%; height:100vh; border:none;"></iframe></body></html>')

if __name__ == "__main__":
    generate_html()



