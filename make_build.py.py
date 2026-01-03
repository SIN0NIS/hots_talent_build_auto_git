import json
import os
import glob
from datetime import datetime

# 1. 가장 최신 kokr.json 파일 찾기
json_files = glob.glob('herodata_*_kokr.json')
if not json_files:
    print("JSON 파일을 찾을 수 없습니다.")
    exit()
latest_json = max(json_files, key=os.path.getmtime)

# 2. 파일명 및 시간 설정
now = datetime.now()
timestamp = now.strftime("%y%m%d_%H%M")
output_html = f"index_{timestamp}.html"

# 3. HTML 생성 로직 (기존 코드 통합)
def generate():
    with open(latest_json, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # ... (여기에 이전에 사용하던 HTML 생성 로직이 들어갑니다) ...
    # 요약: full_html 변수에 전체 HTML 코드가 완성되었다고 가정
    
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(full_html) # 실제 HTML 내용 기록
    
    # 4. hots_talent_build.html (메인 페이지) 자동 업데이트
    main_page_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>히오스 빌드 메이커 - 통합</title>
    <style>body, html {{ margin: 0; padding: 0; height: 100%; overflow: hidden; }} iframe {{ width: 100%; height: 100%; border: none; }}</style>
</head>
<body>
    <iframe src="{output_html}"></iframe>
</body>
</html>"""
    
    with open('hots_talent_build.html', 'w', encoding='utf-8') as f:
        f.write(main_page_content)

if __name__ == "__main__":
    generate()