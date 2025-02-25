import random
import pandas as pd
from typing import List, Dict
import validators
from markitdown import MarkItDown

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from pydantic import BaseModel, Field

class EnglishPhrase(BaseModel):
    phrase: str = Field(..., description="使用する英語フレーズ")
    translation: str = Field(..., description="フレーズの日本語訳")
    sentence: str = Field(..., description="作成された英文")
    explanation: str = Field(..., description="英文の文法説明")

class MeetingResponse(BaseModel):
    phrases: List[EnglishPhrase] = Field(..., description="ミーティングで使用する英語フレーズのリスト")

def read_phrases_csv() -> List[Dict]:
    """
    phrases.csvを読み込んで、phrasesのデータを返す
    """
    df = pd.read_csv("./phrases.csv")
    selected_columns = ['Phrase', 'Translation']
    df_selected = df[selected_columns]

    return df_selected.to_dict('records')

# モジュールレベルでキャッシュ変数を定義
phrases = None

@tool
def get_random_phrases(num_phrases = 3) -> List[Dict]:
    """
    [[使いたい英語のフレーズ]]をランダムに指定数を抽出する

    Args:
        num_phrases (int): 抽出するフレーズの数

    Returns:
        List[Dict]: ランダムに選択されたフレーズのリスト
    """
    print("@@@@ get_random_phrases called @@@@")

    global phrases
    if phrases is None:
        print("phrases is None, reading phrases.csv!!!!")
        phrases = read_phrases_csv()

    return random.sample(phrases, min(num_phrases, len(phrases)))

def create_prompt(url: str, num: int) -> str:
    template = """
        あなたは英語を日本人に教えるプロフェッショナルです。
        私は、ある[[サイトのURL]]の内容について、グローバルなメンバーと英語でミーティングを行います。
        その[[サイトのURL]]の内容に沿って、ミーティングでの英語の発言を[[使いたい英語のフレーズ]]を使って{num}個作って下さい。

        要件:
        - [[使いたい英語のフレーズ]]は、get_random_phrases({num})で取得して下さい
        - phraseに[[使いたい英語のフレーズ]]を入れて下さい
        - translationに[[使いたい英語のフレーズ]]の日本語訳を入れて下さい
        - sentenceに[[使いたい英語のフレーズ]]を使った英文を入れて下さい
          - 英文はミーティングは、社内ミーティングとし若干インフォーマルな口語にして下さい
        - explanationにsentenceの英文の説明をして下さい。日本語訳を "日本語訳「日本語訳の説明」"と「」で囲んで下さい。次に\nを追加して文法の説明を大学進学向けの英語の授業のように説明して下さい。その後\nを追加して、サイトのURL内容のどこを参考にしたかを明確にして下さい


        [[サイトのURL]]
        -----
        {url}


        出力は必ず以下のJSON形式で行ってください。またJSON以外の文字列を出力を絶対にしないこと。```jsonなどの装飾も不要です。
        -----
        {{
            "phrases": [
                {{
                    "phrase": "英語フレーズ",
                    "translation": "日本語訳",
                    "sentence": 英文",
                    "explanation": "英文の説明"
                }}
            ]
        }}
    """

    return template.format(url=url, num=num)

@tool
def extract_content_from_url(url: str) -> str:
    """
    URLからコンテンツを抽出してMarkdownに変換する

    Args:
        url (str): 解析対象のURL

    Returns:
        str: Markdownに変換されたコンテンツ

    Raises:
        ValueError: URLの形式が不正な場合
        ConnectionError: URLへのアクセスに失敗した場合
    """
    print("@@@@ extract_content_from_url called @@@@")

    if not validators.url(url):
        raise ValueError("Invalid URL format")

    # MarkItDownを使用してMarkdownに変換
    markitdown = MarkItDown()
    result = markitdown.convert(url)
    return result.text_content


def create_agent():
    tools = [extract_content_from_url, get_random_phrases]
    model = ChatOpenAI(model="gpt-4o", temperature=0.5)
    agent = create_react_agent(model=model, tools=tools, response_format=MeetingResponse)
    return agent


from pydantic import ValidationError

if __name__ == "__main__":
    # データを取得して表示
    # phrases_selected = get_random_phrases.invoke({"num_phrases": 2})
    # print(phrases_selected)

    # Example URL
    # test_url = "https://konyu.hatenablog.com/entry/2024/12/07/000000"
    # markdown_content = extract_content_from_url(test_url)
    # print(f"=== Content from {test_url} ===")
    # print(markdown_content)

    url = "https://konyu.hatenablog.com/entry/2024/12/07/000000"
    inputs = { "messages": [("system", create_prompt(url, 3))]}
    agent = create_agent()

    # for state in agent.stream(inputs, stream_mode="values"):
    #     message = state["messages"][-1]
    #     message.pretty_print()

    res = agent.invoke(inputs)
    # 文字列からJSONへ変換
    content = res['messages'][-1].content
    print("#### CONTENT ####")
    print(content)
