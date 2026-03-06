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
        time.sleep(10)

        # 100위까지 '더보기' 버튼 클릭 반복
        for i in range(1, 6):
            print(f"🔄 {i}번째 '더보기' 버튼 정밀 탐색 중...")
            
            try:
                # 1. 텍스트뿐만 아니라 버튼의 형태(XPath)를 여러 가지 방식으로 찾습니다.
                # '더보기' 글자 포함 혹은 화살표 아이콘이 있는 버튼을 모두 타겟팅합니다.
                wait = WebDriverWait(driver, 15)
                more_button = wait.until(EC.presence_of_element_located((
                    By.XPATH, "//button[contains(., '더보기')] | //div[contains(@class, 'more')]//button"
                )))

                # 2. 버튼이 화면 중앙에 오도록 스크롤합니다.
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", more_button)
                time.sleep(2)

                # 3. 일반 클릭이 안 될 경우를 대비해 JavaScript로 강제 클릭을 시도합니다.
                driver.execute_script("arguments[0].click();", more_button)
                
                print(f"✅ {i}번째 클릭 성공! (다음 데이터를 기다립니다)")
                time.sleep(6) # 데이터가 길게 늘어나는 시간을 충분히 확보
            except:
                print(f"⚠️ {i}번째에서 버튼을 찾지 못했습니다. 현재 화면까지 수집합니다.")
                break

        # 전체 데이터 추출
        print("🔍 최종 데이터 수집 시작...")
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
            print(f"📤 총 {len(chart_list)}개 중 {len(final_data)}개를 시트로 전송!")
            res = requests.post(webapp_url, json=final_data)
            print(f"📡 서버 응답: {res.text}")
        else:
            print("❌ 데이터 수집 실패")

    finally:
        driver.quit()

if __name__ == "__main__":
    run_scraper()
