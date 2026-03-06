import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def run_scraper():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        print("🚀 한터차트 접속 중...")
        driver.get("https://www.hanteochart.com/chart/album/daily")
        
        # 100위까지 '더보기' 버튼 클릭 반복 (최대 6번)
        for i in range(1, 7):
            print(f"🔄 {i}번째 '더보기' 버튼 탐색 중...")
            
            # 1. 화면을 버튼이 있을 법한 위치까지 아래로 충분히 내립니다.
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3) 

            try:
                # 2. 버튼이 보일 때까지 최대 15초간 기다립니다.
                wait = WebDriverWait(driver, 15)
                more_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., '더보기')]")))
                
                # 3. 버튼을 클릭합니다.
                driver.execute_script("arguments[0].click();", more_button)
                print(f"✅ {i}번째 클릭 성공!")
                time.sleep(5) # 데이터가 로딩될 시간을 충분히 줍니다.
            except:
                print(f"⚠️ {i}번째 클릭 실패 (버튼을 찾을 수 없음). 수집을 시도합니다.")
                break

        # 전체 데이터 추출
        print("🔍 최종 데이터 추출 시작...")
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
            final_data = chart_list[:100]
            print(f"📤 총 {len(chart_list)}개 중 상위 {len(final_data)}개를 전송합니다.")
            res = requests.post(webapp_url, json=final_data)
            print(f"📡 서버 응답: {res.text}")
        else:
            print(f"❌ 데이터 부족 (현재 수집량: {len(chart_list)})")

    finally:
        driver.quit()

if __name__ == "__main__":
    run_scraper()
