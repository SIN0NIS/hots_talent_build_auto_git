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

    # 3. 데이터 로드
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    hero_list = sorted([{"id": k, "name": v['name'], "hId": v.get('hyperlinkId', k)} for k, v in data.items() if 'name' in v], key=lambda x: x['name'])

    # 4. 자바스크립트 정규식 변수 처리
    js_regex_space = r"/\s/g"
    js_regex_digit = r"/\D/g"
    js_regex_non_digit = r"/\d/g"
    js_regex_tooltip = r"/<[^>]*>?/gm"
    js_regex_scaling = r"/(\d+(?:\.\d+)?)\s*~~(0\.\d+)~~/g"
    js_regex_simple_scaling = r"/~~(0\.\d+)~~/g"
    js_regex_build_code = r"/\[T(\d+),(.+?)\]/"

    # 5. HTML 템플릿 작성
    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, shrink-to-fit=no">
    <title>히오스 특성</title>
    <script src="https://html2canvas.hertzen.com/dist/html2canvas.min.js"></script>
    <style>
        :root {{ --p: #a333ff; --bg: #0b0b0d; --card: #16161a; --blue: #00d4ff; --gold: #ffd700; --green: #00ff00; }}
        body {{ margin: 0; background: var(--bg); color: white; font-family: sans-serif; display: flex; flex-direction: column; height: 100vh; overflow: hidden; width: 100%; }}
        #header {{ padding: 10px; background: #1a1a1e; border-bottom: 1px solid #333; flex-shrink: 0; position: relative; z-index: 2000; }}
        .search-group {{ display: flex; flex-direction: column; gap: 8px; }}
        .search-box {{ flex: 1; padding: 12px; background: #222; color: white; border: 1px solid var(--p); border-radius: 6px; font-size: 14px; outline: none; }}
        .comment-input {{ width: 100%; padding: 8px; background: #111; color: var(--blue); border: 1px solid #444; border-radius: 4px; font-size: 11px; text-decoration: underline; box-sizing: border-box; }}
        
        #hero-list-dropdown {{ position: absolute; left: 10px; right: 10px; max-height: 250px; background: #2a2a2a; overflow-y: auto; z-index: 3000; border-radius: 4px; display: none; border: 1px solid var(--p); margin-top: 5px; }}
        .hero-item {{ padding: 12px; border-bottom: 1px solid #333; cursor: pointer; }}
        
        #capture-area {{ flex: 1; display: flex; flex-direction: column; overflow-y: auto; padding-bottom: 220px; background: #0b0b0d; width: 100%; box-sizing: border-box; }}
        #welcome-area {{ padding: 40px 20px; text-align: center; }}
        #comment-display {{ color: var(--green); font-size: 16px; font-weight: bold; margin-bottom: 10px; white-space: pre-wrap; }}
        
        #hero-stat-container {{ background: #1a1a20; margin: 8px; padding: 12px; border-radius: 8px; border: 1px solid #333; display: none; }}
        
        #level-control-wrapper {{ position: relative; width: 100%; padding-bottom: 20px; }}
        .slider-ticks {{ position: absolute; top: 18px; left: 0; width: 100%; display: flex; justify-content: space-between; padding: 0 10px; box-sizing: border-box; pointer-events: none; }}
        .tick {{ width: 2px; height: 6px; background: #333; }}
        .tick.highlight {{ background: var(--p); width: 3px; height: 10px; box-shadow: 0 0 5px var(--p); }}
        .tick-label {{ position: absolute; top: 12px; font-size: 8px; color: #666; transform: translateX(-50%); }}
        
        .stat-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px; margin-bottom: 12px; }}
        .stat-item {{ background: #111; padding: 6px; border-radius: 4px; font-size: 11px; display: flex; flex-direction: column; gap: 2px; }}
        .stat-value {{ color: #fff; font-weight: bold; font-size: 12px; }}
        
        .ability-list {{ border-top: 1px solid #333; padding-top: 8px; display: flex; flex-direction: column; gap: 8px; }}
        .ability-item {{ display: flex; gap: 8px; align-items: flex-start; background: #111; padding: 6px; border-radius: 6px; }}
        .ability-icon {{ width: 30px; height: 30px; border: 1px solid #444; border-radius: 4px; flex-shrink: 0; }}
        .ability-text {{ flex: 1; font-size: 10px; color: #ccc; line-height: 1.3; }}
        .ability-name {{ font-weight: bold; color: var(--blue); font-size: 11px; display: block; margin-bottom: 2px; }}

        .tier-row {{ display: flex; align-items: center; background: var(--card); padding: 6px 8px; border-radius: 6px; border-left: 4px solid var(--p); gap: 8px; min-height: 55px; margin: 3px 5px; box-sizing: border-box; }}
        .tier-label {{ color: var(--blue); font-weight: bold; width: 35px; flex-shrink: 0; font-size: 11px; text-align: center; }}
        .t-icon {{ width: 36px; height: 36px; border: 1px solid #444; cursor: pointer; border-radius: 5px; background: #000; flex-shrink: 0; }}
        .t-icon.selected {{ border-color: var(--gold); box-shadow: 0 0 6px var(--gold); transform: scale(1.05); z-index: 10; }}
        .t-info-display {{ flex: 1; font-size: 10px; color: #ccc; padding-left: 8px; border-left: 1px solid #444; min-height: 36px; display: flex; align-items: center; }}
        
        #footer {{ position: fixed; bottom: 0; width: 100%; background: rgba(0,0,0,0.95); border-top: 2px solid var(--p); padding: 10px; box-sizing: border-box; display: flex; flex-direction: column; align-items: center; gap: 6px; backdrop-filter: blur(10px); z-index: 1500; }}
        .summary-img {{ width: 45px; height: 45px; border-radius: 3px; border: 1px solid var(--gold); }}

        /* 캡처용 임시 스타일 (JS에서 사용) */
        .cap-row {{ display: flex; align-items: flex-start; gap: 15px; border-bottom: 1px solid #333; padding: 15px 0; }}
        .cap-lv {{ color: var(--blue); font-size: 20px; font-weight: bold; width: 50px; flex-shrink: 0; }}
        .cap-img {{ width: 60px; height: 60px; border: 2px solid var(--gold); border-radius: 8px; flex-shrink: 0; }}
        .cap-content {{ flex: 1; }}
        .cap-tname {{ color: white; font-size: 18px; font-weight: bold; margin-bottom: 4px; }}
        .cap-tdesc {{ color: #bbb; font-size: 14px; line-height: 1.4; }}
    </style>
</head>
<body>
    <div id="header">
        <div class="search-group">
            <input type="text" id="comment-input" class="comment-input" value="https://github.com/SIN0NIS/hots_talent_build_auto_git" readonly onclick="window.open(this.value, '_blank')">
            <div style="display:flex; gap:8px;">
                <input type="text" id="hero-search" class="search-box" placeholder="영웅 검색 또는 코드 입력..." onclick="showList()" oninput="handleSearch(this.value)">
                <button onclick="loadFromCode()" style="padding:0 15px; background:var(--p); color:white; border:none; border-radius:6px; font-weight:bold; font-size:13px;">로드</button>
            </div>
        </div>
        <div id="hero-list-dropdown"></div>
    </div>
    <div id="capture-area">
        <div id="welcome-area">
            <div id="comment-display">히오스 빌드 사이트 입니다.</div>
        </div>
        <div id="hero-stat-container">
            <div id="hero-title-area" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <div id="hero-info-title" style="font-size:18px; font-weight:bold; color:var(--p);"></div>
                <div id="hero-role-badge" style="font-size:10px; color:var(--blue); border:1px solid var(--blue); padding:1px 4px; border-radius:4px;"></div>
            </div>
            
            <div id="level-control" style="background:#25252b; padding:12px 10px 5px 10px; border-radius:6px; margin-bottom:10px;">
                <div id="level-control-wrapper">
                    <input type="range" id="level-slider" min="1" max="30" value="1" style="width:100%; accent-color:var(--p);" oninput="updateLevel(this.value)">
                    <div class="slider-ticks" id="slider-ticks"></div>
                </div>
                <div style="display:flex; justify-content:space-between; margin-top:4px;">
                    <span id="level-display" style="font-weight:bold; color:var(--gold); font-size:13px;">LV 1</span>
                    <span id="level-growth-total" style="font-size:9px; color:var(--green);">(+0.00%)</span>
                </div>
            </div>

            <div class="stat-grid" id="stat-grid"></div>
            <div id="ability-container" class="ability-list"></div>
        </div>
        <div id="main-content"></div>
    </div>
    <div id="footer">
        <div id="selected-summary" style="display:flex; gap:4px; min-height:45px;"></div>
        <div style="display:flex; gap:8px; width:100%;">
            <div id="build-code" onclick="copyCode()" style="flex:3; font-size:11px; color:var(--gold); background:#1a1a1a; padding:8px; border-radius:6px; border:1px dashed var(--gold); text-align:center;">[영웅 선택]</div>
            <button onclick="takeScreenshot()" style="flex:1.2; background:var(--p); color:white; border:none; border-radius:6px; font-weight:bold; font-size:13px;">📸 저장</button>
        </div>
    </div>
    <script>
        const hotsData = {json.dumps(data, ensure_ascii=False)};
        const heroList = {json.dumps(hero_list, ensure_ascii=False)};
        const imgBase = "{img_cdn_base}";
        let currentHeroData = null; let currentLevel = 1; let selectedTalents = []; let currentTalentNodes = [];

        const energyMap = {{
            "Mana": "마나", "Scrap": "고철", "Fury": "분노", "Rage": "광기",
            "Energy": "기력", "Brew": "취기", "Essence": "정수", "Focus": "집중",
            "Despair": "절망", "Soul": "영혼"
        }};

        function getChosung(str) {{
            const cho = ["ㄱ","ㄲ","ㄴ","ㄷ","ㄸ","ㄹ","ㅁ","ㅂ","ㅃ","ㅅ","ㅆ","ㅇ","ㅈ","ㅉ","ㅊ","ㅋ","ㅌ","ㅍ","ㅎ"];
            let res = ""; 
            for(let i=0; i<str.length; i++) {{
                let c = str.charCodeAt(i) - 44032;
                if(c>-1 && c<11172) res += cho[Math.floor(c/588)];
                else res += str.charAt(i);
            }} 
            return res;
        }}

        function createSliderTicks() {{
            const container = document.getElementById("slider-ticks");
            const highlightLevels = [1, 4, 7, 10, 13, 16, 20, 30];
            let html = "";
            for(let i=1; i<=30; i++) {{
                const isHighlight = highlightLevels.includes(i);
                html += `<div class="tick ${{isHighlight ? 'highlight' : ''}}">${{isHighlight ? `<span class="tick-label">${{i}}</span>` : ''}}</div>`;
            }}
            container.innerHTML = html;
        }}

        function handleSearch(v) {{
            const s = v.replace({js_regex_space}, "").toLowerCase();
            const choInput = getChosung(s);
            const fil = heroList.filter(h => {{
                const n = h.name.replace({js_regex_space}, "").toLowerCase();
                const choHero = getChosung(n);
                return n.includes(s) || choHero.includes(choInput);
            }});
            renderList(fil); document.getElementById("hero-list-dropdown").style.display = "block";
        }}
        
        function processTooltip(t, lv) {{
            if(!t) return ""; let p = t.replace({js_regex_tooltip}, "");
            p = p.replace({js_regex_scaling}, (m, b, s) => {{
                const v = parseFloat(b) * Math.pow(1 + parseFloat(s), lv - 1);
                return "<strong>" + v.toFixed(1) + "</strong>(+" + (parseFloat(s)*100).toFixed(2) + "%)";
            }});
            return p.replace({js_regex_simple_scaling}, (m, s) => "(+" + (parseFloat(s)*100).toFixed(2) + "%)");
        }}

        function selectHero(id, codeArray = null) {{
            document.getElementById("welcome-area").style.display = "none";
            document.getElementById("hero-list-dropdown").style.display = "none";
            document.getElementById("hero-search").value = "";
            currentHeroData = hotsData[id];
            document.getElementById("hero-info-title").innerText = currentHeroData.name;
            document.getElementById("hero-role-badge").innerText = currentHeroData.expandedRole || "미분류";
            document.getElementById("hero-stat-container").style.display = "block";
            createSliderTicks();
            const lvs = Object.keys(currentHeroData.talents).filter(l => currentHeroData.talents[l].length > 0).sort((a,b) => parseInt(a.replace({js_regex_digit},"")) - parseInt(b.replace({js_regex_digit},"")));
            selectedTalents = new Array(lvs.length).fill(0); currentTalentNodes = [];
            let h = ''; lvs.forEach((l, i) => {{
                currentTalentNodes.push(currentHeroData.talents[l]);
                h += `<div class="tier-row"><div class="tier-label">${{l.replace({js_regex_digit},"")}}Lv</div><div style="display:flex;gap:4px;">`;
                currentHeroData.talents[l].forEach((t, ti) => {{
                    h += `<img src="${{imgBase}}${{t.icon}}" class="t-icon t-row-${{i}} t-node-${{i}}-${{ti+1}}" onclick="toggleTalent(${{i}}, ${{ti+1}}, this)">`;
                }});
                h += `</div><div class="t-info-display" id="desc-${{i}}">선택...</div></div>`;
            }});
            document.getElementById("main-content").innerHTML = h;
            renderAbilities(); renderStats(); 
            if(codeArray) {{
                codeArray.forEach((val, idx) => {{
                    const talentNum = parseInt(val);
                    if(talentNum > 0) {{
                        const targetImg = document.querySelector(`.t-node-${{idx}}-${{talentNum}}`);
                        if(targetImg) toggleTalent(idx, talentNum, targetImg);
                    }}
                }});
            }}
            updateUI();
        }}

        function toggleTalent(ti, tn, el) {{
            const box = document.getElementById("desc-"+ti);
            if(selectedTalents[ti] === tn) {{ selectedTalents[ti] = 0; el.classList.remove("selected"); box.innerHTML = "선택..."; }}
            else {{
                selectedTalents[ti] = tn; document.querySelectorAll(".t-row-"+ti).forEach(img => img.classList.remove("selected"));
                el.classList.add("selected"); updateTalentTooltip(ti);
            }}
            updateUI();
        }}

        function updateTalentTooltip(ti) {{
            const tn = selectedTalents[ti]; if(tn === 0) return;
            const box = document.getElementById("desc-"+ti); const t = currentTalentNodes[ti][tn-1];
            box.innerHTML = `<div style="width:100%"><b style="color:#fff;font-size:11px;">${{t.name}}</b><br><span style="font-size:10px;">${{processTooltip(t.fullTooltip, currentLevel)}}</span></div>`;
        }}

        function updateLevel(lv) {{
            currentLevel = parseInt(lv); document.getElementById("level-display").innerText = "LV " + currentLevel;
            document.getElementById("level-growth-total").innerText = "(+" + ((Math.pow(1.04, currentLevel - 1) - 1) * 100).toFixed(2) + "%)";
            if(currentHeroData) {{ renderStats(); renderAbilities(); selectedTalents.forEach((tn, ti) => {{ if(tn > 0) updateTalentTooltip(ti); }}); }}
        }}

        function renderStats() {{
            const h = currentHeroData; const l = h.life; const e = h.energy || {{ amount: 0, scale: 0, type: "None" }};
            const w = (h.weapons && h.weapons[0]) ? h.weapons[0] : {{damage:0, range:0, period:1, damageScale:0.04}};
            const calc = (b, s, lv) => (b * Math.pow(1 + (s || 0), lv - 1)).toFixed(0);
            const energyLabel = energyMap[e.type] || e.type;
            const sArr = [
                {{l:"체력", v:calc(l.amount, l.scale, currentLevel), g: l.scale}}, 
                {{l:e.type==="Mana" ? "마나" : energyLabel, v:e.amount > 0 ? (e.type==="Mana" ? calc(e.amount, 0.04, currentLevel) : e.amount) : "없음", g: e.type==="Mana" ? 0.04 : 0}},
                {{l:"공격력", v:calc(w.damage, w.damageScale, currentLevel), g: w.damageScale}}, 
                {{l:"공격주기", v:w.period.toFixed(2) + "s", g: 0}},
                {{l:"공격사거리", v:w.range.toFixed(1), g: 0}}, 
                {{l:"피격크기", v:h.radius.toFixed(2), g: 0}}
            ];
            document.getElementById("stat-grid").innerHTML = sArr.map(s => `
                <div class="stat-item">
                    <span style="color:#888;">${{s.l}} ${{s.g > 0 ? `(<span style="color:var(--green)">+${{(s.g*100).toFixed(2)}}%</span>)` : ""}}</span>
                    <b class="stat-value">${{s.v}}</b>
                </div>`).join("");
        }}

        function renderAbilities() {{
            const container = document.getElementById("ability-container");
            const abs = currentHeroData.abilities;
            const all = [...(abs.basic || []), ...(abs.trait || []), ...(abs.mount || []), ...(abs.activable || [])];
            let html = "";
            ["Q", "W", "E", "Trait", "Z", "Active"].forEach(type => {{
                all.filter(a => a.abilityType === type).forEach(skill => {{
                    html += `<div class="ability-item"><img src="${{imgBase}}${{skill.icon}}" class="ability-icon"><div class="ability-text">
                        <span class="ability-name"><span style="color:var(--gold)">[${{type === "Trait" ? "D" : type}}]</span> ${{skill.name}}</span>
                        <div>${{processTooltip(skill.fullTooltip || skill.description, currentLevel)}}</div></div></div>`;
                }});
            }});
            container.innerHTML = html;
        }}

        function updateUI() {{
            const sum = selectedTalents.map((tn, ti) => tn === 0 ? `<div style="width:45px;height:45px;border:1px dashed #333;border-radius:3px;"></div>` : `<img src="${{imgBase}}${{currentTalentNodes[ti][tn-1].icon}}" class="summary-img">`).join("");
            document.getElementById("selected-summary").innerHTML = sum;
            document.getElementById("build-code").innerText = currentHeroData ? `[T${{selectedTalents.join("")}},${{currentHeroData.hyperlinkId}}]` : "영웅 선택";
        }}

        function loadFromCode() {{
            const val = document.getElementById("hero-search").value;
            const m = val.match({js_regex_build_code});
            if(!m) return alert("형식 오류");
            const entry = Object.entries(hotsData).find(([id, d]) => d.hyperlinkId === m[2]);
            if(entry) selectHero(entry[0], m[1].split(""));
        }}

        function renderList(l) {{ document.getElementById("hero-list-dropdown").innerHTML = l.map(h => `<div class="hero-item" onclick="selectHero('${{h.id}}')">${{h.name}}</div>`).join(""); }}
        function showList() {{ handleSearch(""); }}
        function copyCode() {{ navigator.clipboard.writeText(document.getElementById("build-code").innerText); alert("복사 완료!"); }}

        // 특성 중심 고화질 캡처 기능
        function takeScreenshot() {{
            if (!currentHeroData) return alert("영웅을 선택해주세요.");
            
            // 1. 임시 캡처용 컨테이너 생성
            const tempDiv = document.createElement('div');
            tempDiv.style.cssText = "position:absolute; left:-9999px; top:0; width:500px; background:#0b0b0d; padding:25px; border:2px solid #a333ff; color:white; font-family:sans-serif;";
            
            let innerHTML = `
                <div style="text-align:center; margin-bottom:20px; border-bottom:1px solid #444; padding-bottom:15px;">
                    <div style="font-size:32px; font-weight:bold; color:#a333ff; margin-bottom:5px;">${{currentHeroData.name}}</div>
                    <div style="font-size:16px; color:#00d4ff;">${{currentHeroData.expandedRole || 'Heroes of the Storm'}} Build</div>
                </div>
            `;

            let hasSelection = false;
            const lvKeys = Object.keys(currentHeroData.talents).filter(l => currentHeroData.talents[l].length > 0).sort((a,b) => parseInt(a.replace({js_regex_digit},"")) - parseInt(b.replace({js_regex_digit},"")));

            selectedTalents.forEach((tn, ti) => {{
                if (tn > 0) {{
                    hasSelection = true;
                    const t = currentTalentNodes[ti][tn-1];
                    const lvLabel = lvKeys[ti].replace({js_regex_digit},"") + "Lv";
                    innerHTML += `
                        <div class="cap-row">
                            <div class="cap-lv">${{lvLabel}}</div>
                            <img src="${{imgBase}}${{t.icon}}" class="cap-img">
                            <div class="cap-content">
                                <div class="cap-tname">${{t.name}}</div>
                                <div class="cap-tdesc">${{processTooltip(t.fullTooltip, currentLevel)}}</div>
                            </div>
                        </div>
                    `;
                }}
            }});

            if (!hasSelection) return alert("선택된 특성이 없습니다.");

            innerHTML += `<div style="margin-top:20px; text-align:right; font-size:12px; color:#555;">Generated by hots_talent_build_auto_git </div>`;
            tempDiv.innerHTML = innerHTML;
            document.body.appendChild(tempDiv);

            html2canvas(tempDiv, {{ useCORS:true, backgroundColor:"#0b0b0d", scale:2 }}).then(canvas => {{
                const link = document.createElement('a');
                link.download = `${{currentHeroData.name}}_build.png`;
                link.href = canvas.toDataURL();
                link.click();
                document.body.removeChild(tempDiv);
            }});
        }}
    </script>
</body>
</html>"""

    main_page = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, shrink-to-fit=no">
    <title>히오스 빌드 메이커 - 통합</title>
    <style>
        body, html {{ margin: 0; padding: 0; height: 100%; width: 100%; overflow: hidden; background: #0b0b0d; }}
        iframe {{ width: 100%; height: 100%; border: none; display: block; }}
    </style>
</head>
<body>
    <iframe src="{output_file}"></iframe>
</body>
</html>"""

    with open(output_file, 'w', encoding='utf-8') as f: f.write(html_content)
    with open('hots_talent_build.html', 'w', encoding='utf-8') as f: f.write(main_page)

if __name__ == "__main__":
    generate_html()

