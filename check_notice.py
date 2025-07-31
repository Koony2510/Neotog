from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from datetime import datetime
import requests
import os
import time

# 오늘 날짜를 'YYYY.MM.DD' 형식으로 자동 설정
target_date = datetime.today().strftime('%Y.%m.%d')

# GitHub 사용자 지정
github_assignees = ["Koony2510"]     # ⚠️ 실제 GitHub 사용자명
github_mentions = ["Koony2510"]  # ⚠️ 실제 GitHub 사용자명

# 크롬 옵션 설정
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

try:
    url = "https://www.betman.co.kr/main/mainPage/customercenter/notice.do?notiCd=4&searchVal=%EC%B6%95%EA%B5%AC&iPage=1"
    driver.get(url)
    time.sleep(3)

    table = driver.find_element(By.ID, "lv_noti")
    rows = table.find_elements(By.TAG_NAME, "tr")

    found = False
    issue_title = ""

    for idx, row in enumerate(rows):
        tds = row.find_elements(By.TAG_NAME, "td")
        if len(tds) < 4:
            continue

        category = tds[1].text.strip()
        title = tds[2].text.strip()
        date = tds[3].text.strip()

        print(f"[{idx}] 구분: '{category}', 제목: '{title}', 날짜: '{date}'")

        if category == "토토" and "축구" in title and "이월" in title and date == target_date:
            print(f"\n✅ 조건에 맞는 공지 발견: '{title}' ({date})\n")
            found = True
            issue_title = title
            break

    if found:
        # GitHub 이슈 생성
        github_repo = os.getenv("GITHUB_REPOSITORY")
        github_token = os.getenv("GITHUB_TOKEN")

        if github_repo and github_token:
            api_url = f"https://api.github.com/repos/{github_repo}/issues"
            headers = {
                "Authorization": f"Bearer {github_token}",
                "Accept": "application/vnd.github+json"
            }

            # 멘션 포함한 본문 만들기
            mention_text = " ".join([f"@{user}" for user in github_mentions])
            body_text = f"{mention_text}\n\n{issue_title}"

            payload = {
                "title": issue_title,
                "body": body_text,
                "assignees": github_assignees
            }

            response = requests.post(api_url, headers=headers, json=payload)
            if response.status_code == 201:
                print("📌 GitHub 이슈가 성공적으로 생성되었습니다.")
            else:
                print(f"⚠️ GitHub 이슈 생성 실패: {response.status_code} - {response.text}")
        else:
            print("⚠️ GITHUB_REPOSITORY 또는 GITHUB_TOKEN 환경변수가 설정되어 있지 않습니다.")

    else:
        print(f"\n🔍 {target_date}에 해당하는 공지를 찾지 못했습니다.\n")

finally:
    driver.quit()
