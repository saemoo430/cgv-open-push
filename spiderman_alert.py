import os
import requests

TARGET_DATE = "20260808"

TARGET_MOVIE_NO = "30001192"

TARGET_FORMATS = {
    "아이맥스",
    "4DX"
}

SITE_NO = "0089"  # 센텀시티

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

url = (
    "https://cgv.co.kr/api/v1/booking/searchMovScnInfo"
    f"?coCd=A420"
    f"&siteNo={SITE_NO}"
    f"&scnYmd={TARGET_DATE}"
    f"&rtctlScopCd=08"
)

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(
    url,
    headers=headers,
    timeout=20
)

response.raise_for_status()

data = response.json().get("data", [])

found = []

for item in data:

    if item.get("movNo") != TARGET_MOVIE_NO:
        continue

    if item.get("tcscnsGradNm") not in TARGET_FORMATS:
        continue

    found.append(
        f'{item["tcscnsGradNm"]} '
        f'{item["scnsrtTm"][:2]}:{item["scnsrtTm"][2:]}'
    )

if found:

    message = (
        "🎬 스파이더맨 브랜드 뉴 데이 예매 오픈!\n\n"
        f"날짜 : {TARGET_DATE}\n"
        "극장 : CGV 센텀시티\n\n"
        + "\n".join(found)
    )

    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": message
        },
        timeout=10
    )

    print("ALERT SENT")

else:

    print("NOT OPEN")
