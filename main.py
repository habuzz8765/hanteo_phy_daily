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
    # 실제 브라우저처럼 보이기 위한 유저 에이전트 추가
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
                # '더보기' 버튼이 화면에 나타날 때까지 대기
                more_button = wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(., '더보기')]")))
                
                # 버튼 위치로 스크롤 후 강제 클릭
                driver.execute_script("arguments[0].scrollIntoView(true);", more_button)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", more_button)
                
                print(f"➕ {click_count + 1}번째 '더보기' 클릭 성공 (현재 약 {20 + (click_count+1)*20}위 로딩 중)")
                click_count += 1
                time.sleep(4) # 데이터 로딩 대기 시간 증대
            except (TimeoutException, NoSuchElementException):
