import os
import sys
import random
import pandas as pd
from typing import List, Dict
import validators
from markitdown import MarkItDown

from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.prebuilt import create_react_agent

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

def create_prompt(url: str) -> str:
    template = """
        あなたは英語を日本人に教えるプロフェッショナルです。
        私は、ある[[サイトのURL]]の内容についてグローバルなメンバーと英語でミーティングを行います。
        その[[サイトのURL]]の内容に沿って、ミーティングでの英語の発言を下記に示す[[使いたい英語のフレーズ]]を2つを使って作って下さい。
        [[使いたい英語のフレーズ]]は、get_random_phrases(2)で取得して下さい。

        要件:
        - ミーティングは、社内ミーティングをイメージ、若干インフォーマルな口語にして下さい
        - 英語の発言の説明も日本語でして下さい
        - 英語の説明は、大学進学向けの英語の授業のように説明して下さい



        [[サイトのURL]]
        -----
        {url}

        [[出力例]]:
        -----
        使った英語のフレーズ: When it comes to
        日本語訳: 〜と言えば

        英文:
        When it comes to something, I bought a new pen.

        英語の説明:
        サイトのXXXXXという箇所から、ペンを買ったことを説明しています。
    """

    return template.format(url=url)

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

tools = [extract_content_from_url, get_random_phrases]
model = ChatOpenAI(
            model="gpt-4o",
            temperature=0,
        ).bind_tools(tools)
agent = create_react_agent(model=model, tools=tools)#, prompt=prompt)

# chain = prompt | model

if __name__ == "__main__":
    # データを取得して表示
    # phrases_selected = get_random_phrases.invoke({"num_phrases": 2})
    # print(phrases_selected)

    #  # Example URL
    # test_url = "https://konyu.hatenablog.com/entry/2024/12/07/000000"
    # markdown_content = extract_content_from_url(test_url)
    # print(f"=== Content from {test_url} ===")
    # print(markdown_content)

    # inputs = { "messages": [
    #     ("user", "Please extract and analyze content in Japanese from https://konyu.hatenablog.com/entry/2024/12/07/000000")
    # ]}
    url = "https://konyu.hatenablog.com/entry/2024/12/07/000000"
    prompt_text = create_prompt(url)
    inputs = { "messages": [
        ("user", prompt_text)
    ]}


    for state in agent.stream(inputs, stream_mode="values"):
        message = state["messages"][-1]
        message.pretty_print()
    # res = agent.invoke(inputs)
    # print(res['messages'][-1].content)
