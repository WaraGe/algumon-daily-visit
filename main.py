import os
import json
from playwright.sync_api import sync_playwright

TARGET_URL = "https://www.algumon.com/n/deal"

def normalize_cookies(raw_cookies):
    valid_same_site = {"Strict", "Lax", "None"}
    cleaned = []
    for c in raw_cookies:
        cookie = {
            "name": c["name"],
            "value": c["value"],
            "domain": c.get("domain", "www.algumon.com"),
            "path": c.get("path", "/"),
            "secure": c.get("secure", True),
            "httpOnly": c.get("httpOnly", False),
        }
        same_site = str(c.get("sameSite", "")).capitalize()
        if same_site in valid_same_site:
            cookie["sameSite"] = same_site
        if "expirationDate" in c and c["expirationDate"]:
            cookie["expires"] = int(c["expirationDate"])
        cleaned.append(cookie)
    return cleaned

def run():
    cookies_raw = os.environ.get("SITE_COOKIES")
    if not cookies_raw:
        raise ValueError("SITE_COOKIES 환경변수가 비어 있습니다.")

    cookies = normalize_cookies(json.loads(cookies_raw))

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        )
        context.add_cookies(cookies)
        page = context.new_page()

        page.goto(TARGET_URL, wait_until="networkidle")
        page.wait_for_timeout(3000)

        content = page.content()
        if "로그아웃" in content or "logout" in content.lower():
            print("✅ 알구몬 로그인 상태 접속 성공!")
        else:
            raise RuntimeError("❌ 로그인이 풀려 있습니다. SITE_COOKIES를 갱신해 주세요.")

        browser.close()

if __name__ == "__main__":
    run()
