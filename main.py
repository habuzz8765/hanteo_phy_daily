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
from selenium.common.exceptions import TimeoutException, NoSuchElementException

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
        wait = WebDriverWait(driver, 15)

        # 100위까지 '더보기' 버튼 클릭 반복
        click_count = 0
        while click_count < 5:
            try:
                # '더보기' 버튼이 나타날 때까지 대기
                more_button = wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(., '더보기')]")))
                
                # 버튼 위치로 스크롤 후 강제 클릭
                driver.execute_script("arguments[0].scrollIntoView(true);", more_button)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", more_button)
                
                print(f"➕ {click_count + 1}번째 '더보기' 클릭 성공")
                click_count += 1
                time.sleep(4) 
            except (TimeoutException, NoSuchElementException):
                print("🏁 모든 데이터를 불러왔거나 버튼이 없습니다.")
                break

        # 전체 데이터 추출
        print("🔍 데이터 추출 시작...")
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
            print(f"📤 {len(final_data)}개의 데이터를 시트로 전송합니다!")
            res = requests.post(webapp_url, json=final_data)
            print(f"📡 서버 응답: {res.text}")
        else:
            print("❌ 수집 실패")

    finally:
        driver.quit()

if __name__ == "__main__":
    run_scraper()
