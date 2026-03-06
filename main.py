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
        time.sleep(10) # 첫 화면 로딩 대기 시간 대폭 증대

        # 100위까지 '더보기' 버튼 클릭 반복 (최대 6번)
        for i in range(1, 7):
            print(f"🔄 {i}번째 '더보기' 버튼 탐색 시도 중...")
            
            success = False
            for retry in range(3): # 버튼을 찾기 위해 3번 재시도
                # 화면을 조금씩 아래로 내려 버튼 노출 유도
                driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight * {0.3 * (retry + 1)});")
                time.sleep(3)

                try:
                    # 버튼이 클릭 가능한 상태가 될 때까지 20초간 끈질기게 대기
                    wait = WebDriverWait(driver, 20)
                    more_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., '더보기')]")))
                    
                    # 버튼 클릭
                    driver.execute_script("arguments[0].click();", more_button)
                    print(f"✅ {i}번째 클릭 성공!")
                    time.sleep(7) # 데이터 로딩 시간 충분히 확보
                    success = True
                    break
                except:
                    print(f"🔍 {i}번째 {retry+1}번 시도: 아직 버튼을 찾는 중...")

            if not success:
                print(f"🏁 {i}번째 시도 끝에 버튼이 더 이상 없는 것으로 판단되어 수집을 시작합니다.")
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
            print(f"📤 총 {len(chart_list)}개 데이터 수집 완료! 상위 {len(final_data)}개를 전송합니다.")
            res = requests.post(webapp_url, json=final_data)
            print(f"📡 서버 응답: {res.text}")
        else:
            print(f"❌ 데이터 수집 부족 (현재 수집량: {len(chart_list)})")

    finally:
        driver.quit()

if __name__ == "__main__":
    run_scraper()
