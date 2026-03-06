import requests
import time
import os

def run_scraper():
    # 1. 한터차트 API 호출 (데이터 수집)
    api_url = "https://api.hanteochart.com/v1/chart/album/daily"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://www.hanteochart.com/",
        "Origin": "https://www.hanteochart.com"
    }
    
    try:
        print("🚀 한터차트 데이터 수집 중...")
        response = requests.get(api_url, headers=headers, timeout=20)
        
        # 응답이 정상인지 확인
        if response.status_code != 200:
            print(f"❌ API 호출 실패: {response.status_code}")
            return

        items = response.json().get('data', {}).get('list', [])
        
        # 2. 데이터 가공 (순위, 앨범명, 아티스트, 판매량, 음반지수, 수집일시)
        chart_list = []
        for item in items[:100]:
            chart_list.append([
                item.get('ranking'), 
                item.get('album_nm'), 
                item.get('artist_nm'),
                item.get('step_data'), 
                item.get('data_val'), 
                time.strftime('%Y-%m-%d %H:%M:%S')
            ])

        # 3. 구글 시트 웹앱으로 데이터 전송
        # 깃허브 Secrets에 저장한 WEBAPP_URL을 불러옵니다.
        webapp_url = os.environ.get('WEBAPP_URL')
        
        if not webapp_url:
            print("❌ WEBAPP_URL 설정이 되어있지 않습니다.")
            return

        print("📤 구글 시트로 데이터를 전송합니다...")
        res = requests.post(webapp_url, json=chart_list)
        print(f"📡 서버 응답: {res.text}")

    except Exception as e:
        print(f"🚨 오류 발생: {e}")

if __name__ == "__main__":
    run_scraper()
