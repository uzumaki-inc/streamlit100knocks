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


def read_phrases_csv() -> List[Dict]:
    """
    phrases.csvを読み込んでデータを返す
    """
    df = pd.read_csv("./phrases.csv")
    selected_columns = ['Phrase', 'Translation']
    df_selected = df[selected_columns]

    return df_selected.to_dict('records')


def get_random_phrases(phrases, num_phrases = 3) -> List[Dict]:
    """
    フレーズリストからランダムに指定数を抽出する

    Args:
        num_phrases (int): 抽出するフレーズの数

    Returns:
        List[Dict]: ランダムに選択されたフレーズのリスト
    """
    phrases = read_phrases_csv()
    return random.sample(phrases, min(num_phrases, len(phrases)))

def create_prompt():
    template = """
    こんにちは、あなたは日本語のフレーズを生成するツールです。
    下記のURLからコンテンツを抽出して、Markdown形式で返してください。

    URL: {url}
    """

    prompt = ChatPromptTemplate.from_template(template)
    return prompt

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
    if not validators.url(url):
        raise ValueError("Invalid URL format")

    # MarkItDownを使用してMarkdownに変換
    markitdown = MarkItDown()
    result = markitdown.convert(url)
    print(result)
    return result.text_content

tools = [extract_content_from_url]
model = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
        ).bind_tools(tools)
prompt = create_prompt()
chain = prompt | model

if __name__ == "__main__":
    # データを取得して表示
    # phrases = read_phrases_csv()
    # phrases_selected = get_random_phrases(phrases, 2)
    # print(phrases_selected)

    #  # Example URL
    # test_url = "https://konyu.hatenablog.com/entry/2024/12/07/000000"

    # markdown_content = extract_content_from_url(test_url)
    # print(f"=== Content from {test_url} ===")
    # print(markdown_content)


    res = chain.invoke({"url": "https://konyu.hatenablog.com/entry/2024/12/07/000000"})
    tool_call = res.tool_calls[0]
    method_name = tool_call["name"]
    method = getattr(sys.modules[__name__], method_name)
    result = method.invoke(tool_call["args"])
    print(result)
    print(res)


