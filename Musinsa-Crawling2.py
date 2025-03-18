import os
import requests
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# 디렉토리 생성 함수
def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# 이미지 다운로드 함수
def download_image(url, folder, count):
    try:
        response = requests.get(url, stream=True, timeout=10)  # timeout 추가
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            ext = img.format.lower()  # 이미지 포맷 자동 감지 (JPEG, PNG 등)
            filename = os.path.join(folder, f'image_{count}.{ext}')
            img.save(filename)
            return True
        else:
            print(f"이미지 다운로드 실패: {url} (응답 코드: {response.status_code})")
    except Exception as e:
        print(f"이미지 다운로드 중 오류 발생: {e}")
    return False

# 크롬 옵션 설정 (헤드리스 모드)
chrome_options = Options()
chrome_options.add_argument("--headless")  # 브라우저 창을 띄우지 않음
chrome_options.add_argument("--enable-gpu")  # GPU 활성화
chrome_options.add_argument("--window-size=1920x1080")  # 창 크기 설정
chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # 봇 감지 회피

# 크롬 드라이버 설정
service = Service()  # 자동으로 chromedriver 실행
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.implicitly_wait(5)  # 암묵적 대기 추가

# 카테고리 URL 및 저장할 폴더 설정
categories = {
    '맨투맨': ('https://www.musinsa.com/categories/item/001005', 'images/tops/mtm/'),
    '후드티': ('https://www.musinsa.com/categories/item/001004', 'images/tops/hoody/'),
    '셔츠': ('https://www.musinsa.com/categories/item/001002', 'images/tops/shirts/'),
    '긴소매': ('https://www.musinsa.com/categories/item/001010', 'images/tops/long-sleeve/'),
    '반팔': ('https://www.musinsa.com/categories/item/001001', 'images/tops/t-shirts/'),
    '데님': ('https://www.musinsa.com/categories/item/003002', 'images/bottom/jeans/'),
    '트레이닝': ('https://www.musinsa.com/categories/item/003004', 'images/bottom/sporty/'),
    '코튼': ('https://www.musinsa.com/categories/item/003007', 'images/bottom/cotton/'),
    '슬렉스': ('https://www.musinsa.com/categories/item/003008', 'images/bottom/slacks/'),
    '스커트': ('https://www.musinsa.com/categories/item/100004', 'images/bottom/skirt/')
}

# 각 카테고리별 크롤링
for category_name, (url, folder) in categories.items():
    create_directory(folder)  # 저장할 폴더 생성
    driver.get(url)  # URL 접속
    count = 0
    image_set = set()  # 중복 이미지 방지

    while count < 1000:  # 최대 1000장 다운로드
        for i in range(1, 11):
            for j in range(1, 4):
                if count >= 1000:
                    break  # 1000장 이상이면 종료
                
                try:
                    print(f'{category_name} - {i}, {j}')
                    
                    # 이미지 선택자
                    image_selector = f'//*[@id="commonLayoutContents"]/div[4]/div/div/div/div[{i}]/div/div[{j}]/div[1]/div/a/div/img'
                    
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, image_selector)))
                    
                    image_box = driver.find_element(By.XPATH, image_selector)
                    driver.execute_script("arguments[0].scrollIntoView();", image_box)  # 스크롤 이동
                    
                    src = image_box.get_attribute('src')
                    
                    if src and src not in image_set:
                        image_set.add(src)  # 다운로드한 이미지 URL 저장
                        count += 1
                        download_image(src, folder, count)
                    else:
                        print("이미지 URL이 중복되거나 찾을 수 없습니다.")

                except Exception as e:
                    print(f'이미지 수집 오류: {e}')

        # 페이지 스크롤하여 더 많은 이미지 로드
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)  # 페이지 로드 대기

# 드라이버 종료
driver.quit()
print("크롤링 완료.")