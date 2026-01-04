⚡ 히오스 빌드 메이커 Pro (HOTS Talent Build Maker)
이 프로젝트는 **Heroes of the Storm (히오스)**의 영웅 데이터를 바탕으로 자신만의 특성 빌드를 만들고, 이미지로 저장하며, 빌드 코드를 공유할 수 있는 웹 도구입니다. GitHub Actions를 통해 최신 데이터를 바탕으로 자동 업데이트됩니다.

✨ 주요 기능
🔍 스마트 검색: 영웅 이름 검색은 물론, 'ㄴㅂ'와 같은 초성 검색을 완벽 지원합니다.

📈 실시간 스탯 계산: 레벨 슬라이더(1~30)를 조절하면 체력, 마나, 공격력 등이 성장치(+4.00%)에 맞춰 실시간으로 계산됩니다. (마나 외 특수 자원은 고정 수치 유지)

🛠️ 특성 로드 및 공유: 빌드 코드를 복사하거나 입력하여 다른 사람의 특성을 즉시 불러올 수 있습니다. 로드 시 모든 특성이 자동으로 찍힙니다.

📸 스마트 스크린샷: 날짜와 영웅 이름이 포함된 파일명(빌드_영웅명_날짜.png)으로 빌드 화면을 즉시 저장합니다.

📱 모바일 최적화: 스마트폰 환경에서도 축소 없이 꽉 찬 화면으로 쾌적하게 사용할 수 있습니다.

💬 커스텀 코멘트: 자신만의 메시지나 깃허브 링크를 메인 화면에 띄울 수 있습니다.

🚀 사용 방법 

하단 주소로 들어갑니다.
https://sin0nis.github.io/hots_talent_build_auto_git/hots_talent_build.html

상단 검색창에 영웅 이름을 입력하거나 초성을 입력해 영웅을 선택하세요.

레벨 슬라이더를 움직여 특정 레벨의 스탯을 확인하세요. (특성 구간 강조 표시 포함)

원하는 특성을 클릭하여 빌드를 완성하세요.

하단의 [복사] 버튼으로 빌드 코드를 공유하거나, [📸 저장] 버튼으로 이미지를 다운로드하세요.


⚡ HOTS Talent Build Maker Pro
This project is a powerful web tool for creating, sharing, and saving talent builds for Heroes of the Storm (HOTS). It utilizes GitHub Actions to automatically generate and update the builder using the latest game data.

✨ Key Features
🔍 Smart Search: Supports searching by hero names and Korean Chosung (Consonants) for faster navigation.

📈 Real-time Stat Scaling: Adjust the level slider (1–30) to see HP, Mana, and Attack Damage scale dynamically (+4.00% per level). Special resources stay fixed as per game logic.

🛠️ Build Loading & Sharing: Easily share your builds using build codes. Loading a code automatically selects the hero and toggles all corresponding talents.

📸 Smart Screenshots: Save your build as an image with an automated filename including the hero name and current date (Build_HeroName_Date.png).

📱 Mobile Optimized: Fully responsive design ensures a seamless experience on smartphones without unwanted zooming or layout breaking.

💬 Custom Comments: Display your own messages or social links directly on the main dashboard.

🚀 How to Use

Link: https://sin0nis.github.io/hots_talent_build_auto_git/hots_talent_build.html

Use the search bar at the top to find and select a hero (supports consonants for Korean users).

Move the level slider to check stats at different milestones (talent levels are highlighted).

Click on the talent icons to complete your build.

Click [Copy] to share the build code or [📸 Save] to download the build as a PNG image.

🛠️ Technical Info
Language: Python (HTML Generator), JavaScript (Frontend Logic)

Data Source: Custom kokr.json extracted from game files.

Automation: GitHub Actions (Workflows) for automated static site generation.
