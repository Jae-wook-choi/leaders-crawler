import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
import time

def scrape_news(start_page, end_page):
    news_data = []
    base_url = "https://finance.naver.com/news/mainnews.naver?page="

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    for page_num in range(start_page, end_page + 1):
        url = base_url + str(page_num)
        print(f"▶ 페이지 요청 중: {url}")
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"❌ 요청 실패: {e}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        news_items = soup.select(".newsList a[target='_blank']")

        for item in news_items:
            title = item.get_text(strip=True)
            link = item.get("href")
            if title and link:
                full_url = link if link.startswith("http") else f"https://finance.naver.com{link}"
                news_data.append({"제목": title, "URL": full_url})

        print(f"✅ 페이지 {page_num} 완료 - {len(news_items)}건 수집")
        time.sleep(1.5)

    return pd.DataFrame(news_data)

# Streamlit 인터페이스
st.title("📈 네이버 금융 뉴스 크롤러")
start_page = st.number_input("시작 페이지", value=1)
end_page = st.number_input("종료 페이지", value=3)

if st.button("크롤링 시작"):
    with st.spinner("뉴스 수집 중..."):
        df = scrape_news(start_page, end_page)
        if not df.empty:
            st.success(f"{len(df)}개의 기사를 수집했습니다!")
            st.dataframe(df)
            df.to_excel("news.xlsx", index=False)
            with open("news.xlsx", "rb") as f:
                st.download_button("엑셀 다운로드", f, file_name="news.xlsx")
        else:
            st.warning("기사를 찾을 수 없습니다.")