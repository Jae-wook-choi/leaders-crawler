import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st

def scrape_news(start_page: int, end_page: int) -> pd.DataFrame:
    base_url = "https://finance.naver.com/news/mainnews.naver?page="
    news_list = []

    for page_num in range(start_page, end_page + 1):
        url = base_url + str(page_num)
        response = requests.get(url)
        response.encoding = 'euc-kr'  # 네이버 뉴스 페이지 인코딩
        soup = BeautifulSoup(response.text, 'html.parser')

        for item in soup.select("ul.mainNewsList li"):
            a_tag = item.find("a")
            date_tag = item.select_one("span.wdate")

            if a_tag and date_tag:
                title = a_tag.text.strip()
                link = "https://finance.naver.com" + a_tag.get("href")
                date = date_tag.text.strip()

                news_list.append({
                    "title": title,
                    "link": link,
                    "date": date
                })

    return pd.DataFrame(news_list)

st.set_page_config(page_title="뉴스 크롤러", layout="wide")
st.title("📈 금융 뉴스 크롤러")

start_page = st.number_input("시작 페이지", min_value=1, max_value=100, value=1)
end_page = st.number_input("끝 페이지", min_value=1, max_value=100, value=1)

if st.button("크롤링 시작"):
    with st.spinner("크롤링 중입니다..."):
        df = scrape_news(start_page, end_page)
        if not df.empty:
            st.success(f"{len(df)}개의 뉴스 기사를 수집했습니다.")
            st.dataframe(df)
        else:
            st.warning("뉴스 기사가 없습니다. 다른 페이지 범위를 시도해보세요.")