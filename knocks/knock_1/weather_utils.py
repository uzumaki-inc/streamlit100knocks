import requests
from langchain_ollama import ChatOllama
from langchain_community.chat_models import ChatOpenAI
from typing import TypedDict, List, Dict, Optional

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

def create_prompt(weather_description):
    """
    天気の説明からプロンプトを生成する関数

    Parameters:
        weather_description (str): 天気の説明

    Returns:
        str: LLMへのプロンプト
    """
    return f"天気は「{weather_description}」です。日本語でこの天気からインスピレーションを得た短いポエムを書いてください。"

def generate_poem(weather_description, llm_type="ollama"):
    """
    天気からポエムを生成する関数

    Parameters:
        weather_description (str): 天気の説明
        llm_type (str): 使用するLLMの種類 ("ollama" または "openai")

    Returns:
        str: 生成されたポエムまたはエラーメッセージ
    """
    try:
        # LLMの初期化
        llm = initialize_llm(llm_type)

        # プロンプトの生成
        prompt = create_prompt(weather_description)

        # LLMを使用してポエム生成
        response = llm.invoke(prompt)

        # レスポンスの内容をチェック
        if hasattr(response, "content"):
            return response.content
        else:
            return "No content available in the response."
    except Exception as e:
        return f"ポエムを生成するのに失敗しました：{e}"
