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
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    try:
        print("🚀 한터차트 접속 및 100위까지 로딩 시작...")
        driver.get("https://www.hanteochart.com/chart/album/daily")
        time.sleep(5) 

        # [추가된 부분] 100위까지 로딩하기 위해 화면을 끝까지 3번 내립니다.
        for _ in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3) # 로딩 대기

        # 데이터 추출 로직
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

        webapp_url = os.environ.get('WEBAPP_URL')
        if chart_list and webapp_url:
            # 100개까지만 잘라서 전송
            final_data = chart_list[:100]
            print(f"📤 {len(final_data)}개의 데이터를 시트로 보냅니다...")
            res = requests.post(webapp_url, json=final_data)
            print(f"📡 전송 결과: {res.text}")

    finally:
        driver.quit()

if __name__ == "__main__":
    run_scraper()
