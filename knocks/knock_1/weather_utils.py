import requests
from typing import TypedDict, List, Dict, Optional

from langchain_ollama import ChatOllama
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser


# TypedDictを定義
class Forecast(TypedDict):
    dateLabel: str
    telop: str
    date: str
    image: Dict[str, str]

class WeatherData(TypedDict):
    forecasts: List[Forecast]


def get_weather_data(city_code)-> Optional[WeatherData]:
    """
    都市コードをもとに天気データを取得する関数
    """
    API_URL = f"https://weather.tsukumijima.net/api/forecast/city/{city_code}"
    try:
        response = requests.get(API_URL)
        response.raise_for_status()  # ステータスコードがエラーの場合例外を発生
        data = response.json()
        return data
    except Exception:
        return None

def initialize_llm(llm_type):
    """
    指定されたLLMタイプに基づいてLLMを初期化する関数

    Parameters:
        llm_type (str): 使用するLLMの種類 ("ollama" または "openai")

    Returns:
        object: 初期化されたLLMインスタンス
    """
    if llm_type == "ollama":
        return ChatOllama(
            model="llama3.2",
            base_url="http://localhost:11434"
        )
    elif llm_type == "openai":
        return ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7
        )
    else:
        raise ValueError(f"Unsupported LLM type: {llm_type}")

poem_prompt = ChatPromptTemplate.from_template("""
あなたは天気をモチーフにした詩を生成する詩人です。

天気は「{input}」です。
日本語でこの天気からインスピレーションを得た短いポエムを書いてください。
""")

def generate_poem(weather_description: str, llm_type: str = "ollama") -> str:
    llm = initialize_llm(llm_type)
    poem_chain = poem_prompt | llm | StrOutputParser()
    return poem_chain.invoke({"input": weather_description})
