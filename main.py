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
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

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
        wait = WebDriverWait(driver, 20) # 대기 시간을 20초로 늘림

        # 100위까지 '더보기' 버튼 클릭 반복
        # 버튼이 화면에서 사라지거나 최대 6번 클릭할 때까지 수행
        for i in range(1, 7):
            try:
                # 버튼이 보일 때까지 대기 및 스크롤
                more_button = wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(., '더보기')]")))
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", more_button)
                time.sleep(2)
                
                # JavaScript를 이용한 강제 클릭 (방해 요소 무시)
                driver.execute_script("arguments[0].click();", more_button)
                print(f"➕ {i}번째 '더보기' 클릭 성공 (데이터 로딩 대기 중...)")
                
                # 데이터가 충분히 로딩되도록 클릭 후 5초간 대기
                time.sleep(5)
            except (TimeoutException, NoSuchElementException):
                print(f"🏁 {i}번째 시도: '더보기' 버튼이 더 이상 없거나 로딩이 완료되었습니다.")
                break
            except Exception as e:
                print(f"⚠️ 클릭 중 오류 발생: {str(e)}")
                break

        # 전체 데이터 추출
        print("🔍 100위 데이터 추출 시작...")
        raw_text = driver.find_element(By.TAG_NAME, "body").text
        lines = raw_text.split('\n')
        
        chart_list = []
        # '음반 지수' 텍스트 이후부터 데이터 시작
        start_index = next((i + 1 for i, line in enumerate(lines) if "음반 지수" in line), 0)
        data_rows = lines[start_index:]
        
        idx = 0
        while idx < len(data_rows) - 4:
            if data_rows[idx].isdigit():
                chart_list.append([
                    data_rows[idx],    # 순위
                    data_rows[idx+1],  # 앨범명
                    data_rows[idx+2],  # 아티스트
                    data_rows[idx+3],  # 판매량
                    data_rows[idx+4],  # 음반지수
                    time.strftime('%Y-%m-%d %H:%M:%S') # 수집시간
                ])
                idx += 5
            else:
                idx += 1

        webapp_url = os.environ.get('WEBAPP_URL')
        if chart_list and webapp_url:
            final_data = chart_list[:100] # 정확히 100개만 전송
            print(f"📤 총 {len(final_data)}개의 데이터를 시트로 보냅니다!")
            res = requests.post(webapp_url, json=final_data)
            print(f"📡 서버 응답: {res.text}")
        else:
            print(f"❌ 데이터 부족 (현재 수집량: {len(chart_list)}) 또는 URL 설정 오류")

    finally:
        driver.quit()

if __name__ == "__main__":
    run_scraper()
