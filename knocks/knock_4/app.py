
import streamlit as st
from screiper import fetch_json_data_with_webdriver, format_articles, articles_to_data_frame

# StreamlitのUI部分
st.title("PR Timesサマリー")
st.write("PR Timesの特定のキーワードにヒットする記事を要約してリストアップします")

# キーワード入力
key = st.text_input("キーワードを入力してください", "")

# 記事数入力
limit = st.number_input("取得する記事数を入力してください", min_value=1, max_value=100, value=2)

# 実行ボタン
if st.button("実行"):
    # 空のプレースホルダーを作成
    status_label = st.empty()
    # データ取得中のラベルを表示
    status_label.text("データ取得中...")

    # メソッドを実行
    json_data = fetch_json_data_with_webdriver(key, limit)

    status_label.text("データ要約中...")
    articles = format_articles(json_data)
    df = articles_to_data_frame(articles)

    # 結果を表示
    status_label.subheader("結果:")
    # HTMLを有効にしてテーブルを表示
    st.markdown(
        df.to_html(escape=False, index=False),  # escape=FalseでHTMLを有効化
        unsafe_allow_html=True
    )
