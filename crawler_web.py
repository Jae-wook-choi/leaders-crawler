import streamlit as st
import pandas as pd
import time
from io import BytesIO
from playwright.sync_api import sync_playwright

def scrape_news(start_page, end_page):
    news_data = []
    base_url = "https://finance.naver.com/news/mainnews.naver?page="

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        for page_num in range(start_page, end_page + 1):
            url = base_url + str(page_num)
            page.goto(url)

            try:
                page.wait_for_selector(".newsList", timeout=5000)
            except:
                continue

            news_elements = page.query_selector_all(".newsList a[target='_blank']")
            for news in news_elements:
                title = news.inner_text().strip()
                link = news.get_attribute("href")
                if title and link:
                    news_data.append({"제목": title, "URL": link})

            time.sleep(1)

        browser.close()

    return pd.DataFrame(news_data)

# --- Streamlit UI ---
st.set_page_config(page_title="네이버 뉴스 크롤러", layout="centered")
st.title("\U0001F4F0 네이버 뉴스 크롤러")

start_page = st.number_input("시작 페이지", min_value=1, max_value=100, value=1)
end_page = st.number_input("종료 페이지", min_value=1, max_value=100, value=3)

if st.button("크롤링 시작"):
    with st.spinner("크롤링 중..."):
        df = scrape_news(start_page, end_page)

        if not df.empty:
            st.success(f"{len(df)}개의 뉴스 기사가 수집되었습니다!")
            st.dataframe(df)

            # 엑셀 다운로드
            output = BytesIO()
            df.to_excel(output, index=False, engine='openpyxl')
            st.download_button(
                label="\U0001F4E5 엑셀 다운로드",
                data=output.getvalue(),
                file_name="news_result.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("수집된 데이터가 없습니다.")