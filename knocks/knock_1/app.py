import os
import streamlit as st
from weather_utils import get_weather_data, generate_poem, Forecast
from typing import List

# OpenAIの環境変数を読み込み
from common.util import load_environment
load_environment()

# 都道府県の都市コード辞書
CITY_CODES = {
    "札幌": "016010",
    "東京": "130010",
    "大阪": "270000",
    "福岡": "400010",
    "沖縄": "471010",
}

# UI部分
st.title("天気感覚ポエム")
st.write("このアプリは、選択した都道府県の天気を検索し、天気に基づいてポエムを生成します。")

# 都道府県を選択
selected_prefecture = st.selectbox("都道府県を選択してください", CITY_CODES.keys())
city_code = CITY_CODES[selected_prefecture]

# 天気データを取得
st.write("### 天気予報")
weather_data = get_weather_data(city_code)

if weather_data is None:
    st.error("天気データの取得に失敗しました。")
else:
    forecasts: List[Forecast] = weather_data.get("forecasts", [])
    forecast_options = {f["dateLabel"]: f for f in forecasts}

    # 日付を選択
    select_day = st.selectbox("日付を選択", forecast_options.keys())
    selected_weather = forecast_options[select_day]
    weather_description = selected_weather["telop"]

    # 天気予報の表示
    st.write(f"### {select_day}の天気予報：")
    st.write(f"- 日付：{selected_weather['date']}")
    st.write(f"- 気象：{weather_description}")
    st.image(selected_weather["image"]["url"], caption=selected_weather["image"]["title"])

    # 天気に基づくポエム生成
    st.write("### 天気感覚のポエム：")
    if os.getenv("ENV") == "production":
        poem = generate_poem(weather_description, llm_type="openai")
    else:
        poem = generate_poem(weather_description, llm_type="ollama")

    st.write(poem)
