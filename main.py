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
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        print("🚀 한터차트 접속 및 데이터 확장 시작...")
        driver.get("https://www.hanteochart.com/chart/album/daily")
        time.sleep(10)

        for i in range(1, 6):
            print(f"🔄 {i}번째 데이터 확장 시도 중...")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

            # [핵심] 텍스트나 태그에 상관없이 '더보기' 아이콘이나 버튼 근처의 모든 요소를 찾아 클릭 시도
            # 특히 'more'나 'btn' 단어가 포함된 클래스를 집중 공략합니다.
            try:
                # 1. '더보기' 혹은 화살표가 포함된 모든 요소를 찾음
                elements = driver.find_elements(By.XPATH, "//*[contains(text(), '더보기')] | //*[contains(@class, 'more')] | //*[contains(@class, 'btn')]")
                
                # 2. 화면 하단에 위치한 요소들만 골라내어 클릭 신호를 보냄
                clicked = False
                for el in reversed(elements):
                    if el.is_displayed():
                        driver.execute_script("arguments[0].click();", el)
                        clicked = True
                        break # 하나라도 클릭 신호가 갔으면 대기 단계로
                
                if clicked:
                    print(f"✅ {i}번째 클릭 신호 전송 완료")
                    time.sleep(8) # 로딩 시간을 넉넉히 줍니다.
            except:
                continue

        # 데이터 추출 로직 (이전과 동일)
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
            print(f"📤 총 {len(chart_list)}개 데이터 수집! 상위 {len(final_data)}개를 전송합니다.")
            res = requests.post(webapp_url, json=final_data)
            print(f"📡 서버 응답: {res.text}")
        else:
            print(f"❌ 데이터 수집 부족 (수집량: {len(chart_list)})")

    finally:
        driver.quit()

if __name__ == "__main__":
    run_scraper()
