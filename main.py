import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

def run_scraper():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
    # 화면 크기를 고정하여 좌표의 정확도를 높입니다.
    chrome_options.add_argument('--window-size=1920,1080')
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        print("🚀 한터차트 접속 중...")
        driver.get("https://www.hanteochart.com/chart/album/daily")
        time.sleep(10)

        # 100위까지 도달하기 위해 반복 수행
        for i in range(1, 6):
            print(f"🔄 {i}번째 데이터 확장 시도 중 (화면 하단 강제 클릭)...")
            
            # 1. 화면의 맨 아래로 이동
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

            # 2. 버튼의 텍스트가 아닌 '위치'를 타겟팅하여 클릭 (ActionChains 활용)
            # 화면 중앙 하단부를 클릭하여 '더보기' 버튼을 강제로 누릅니다.
            try:
                actions = ActionChains(driver)
                # 바디 전체를 기준으로 하단 중앙 지점을 클릭하도록 명령
                body = driver.find_element(By.TAG_NAME, 'body')
                actions.move_to_element(body).move_by_offset(0, 450).click().perform()
                
                print(f"✅ {i}번째 클릭 명령 전송 완료")
                time.sleep(7) # 로딩 대기
            except Exception as e:
                print(f"⚠️ 클릭 시도 중 알 수 없는 상태 발생: {str(e)}")
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
            print(f"📤 총 {len(chart_list)}개 데이터 수집! {len(final_data)}개를 시트로 전송합니다.")
            res = requests.post(webapp_url, json=final_data)
            print(f"📡 서버 응답: {res.text}")
        else:
            print(f"❌ 데이터 수집 부족 (수집량: {len(chart_list)})")

    finally:
        driver.quit()

if __name__ == "__main__":
    run_scraper()
