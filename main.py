import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

def run_scraper():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    # 1. 셀레늄으로 한터차트 접속
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    try:
        print("🚀 한터차트 웹사이트 접속 중...")
        driver.get("https://www.hanteochart.com/chart/album/daily")
        time.sleep(10) # 페이지 로딩 대기

        # 2. 텍스트 추출 및 간단 정제 (Buzz님의 이전 성공 로직 활용)
        raw_text = driver.find_element(By.TAG_NAME, "body").text
        lines = raw_text.split('\n')
        
        chart_list = []
        start_index = next((i + 1 for i, line in enumerate(lines) if "음반 지수" in line), 0)
        data_rows = lines[start_index:]
        
        idx = 0
        while idx < len(data_rows) - 4:
            if data_rows[idx].isdigit():
                chart_list.append([
                    data_rows[idx], data_rows[idx+1], data_rows[idx+2], 
                    data_rows[idx+3], data_rows[idx+4], time.strftime('%Y-%m-%d %H:%M:%S')
                ])
                idx += 5
            else:
                idx += 1

        # 3. 구글 시트 웹앱으로 전송
        webapp_url = os.environ.get('WEBAPP_URL')
        if chart_list and webapp_url:
            res = requests.post(webapp_url, json=chart_list[:100])
            print(f"📡 전송 결과: {res.text}")
        else:
            print("❌ 수집된 데이터가 없거나 URL 설정 오류")

    finally:
        driver.quit()

if __name__ == "__main__":
    run_scraper()
