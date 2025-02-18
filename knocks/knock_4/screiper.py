from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import json
import re
import pandas as pd

from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from bs4 import BeautifulSoup

from typing import Dict, Optional

import os

# OpenAIの環境変数を読み込み
from common.util import load_environment
load_environment()

def fetch_json_data_with_webdriver(key: str, limit: int = 10) -> Optional[Dict]:
    if not key:
        return None

    """
    Fetch JSONP data from PRtimes API using Selenium on Google Colab and print the JSON to the console.
    """
    url = f"https://prtimes.jp/api/search_release.php?callback=addReleaseList&type=topics&v={key}&limit={limit}&page=1"

    # ChromeDriverのオプション設定
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # ヘッドレスモード（ブラウザ画面を表示しない）
    chrome_options.add_argument("--disable-gpu")  # GPUを無効化
    chrome_options.add_argument("--no-sandbox")  # サンドボックスを無効化
    chrome_options.add_argument("--disable-dev-shm-usage")  # 共有メモリ関連の問題を防止

    # ChromeDriverのパスを指定
    # 下記のパスはmacOSの場合のパス
    service = Service("/opt/homebrew/bin/chromedriver")  # ChromeDriverのパス
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(url)
        print(f"Accessing URL: {url}")
        # Get page source and extract JSON
        page_source = driver.page_source

        # Remove HTML tags to extract the JSON content
        # match = re.search(r"<pre.*?>(.*)</pre>", page_source, re.DOTALL)
        match = re.search(r"addReleaseList\((\{.*\})\)", page_source, re.DOTALL)
        if not match:
            print("Invalid response format")
            return

        json_data_str = match.group(1)
        json_data = json.loads(json_data_str)
        print("Fetched JSON Data:")
        return json_data

    except Exception as e:
        print(f"Error occurred: {e}")

    finally:
        driver.quit()

# HTMLから要約を作成する関数
def create_summary(html_text, max_length=500):
    """
    LangChainとOpenAIを使用して、HTMLコンテンツを要約する関数。

    Args:
        html_text (str): HTMLテキスト。
        max_length (int): 要約の最大長。

    Returns:
        str: 要約されたテキスト。
    """
    # BeautifulSoupを使ってHTMLからテキストを抽出
    soup = BeautifulSoup(html_text, "html.parser")
    extracted_text = soup.get_text(separator="\n").strip()

    # 環境変数ENVに基づいてモデルを切り替え
    if os.getenv("ENV") == "production":
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
        )
    else:
        llm = ChatOllama(
            model="llama3.2",
            base_url="http://localhost:11434"
        )

    # プロンプトのテンプレート
    prompt_template = PromptTemplate(
        input_variables=["text", "length"],
        template=(
            "以下の文章を {length} 文字程度に要約してください:\n\n"
            "{text}\n\n"
            "要約:"
        ),
    )
    prompt = prompt_template.format(text=extracted_text, length=max_length)

    # 要約を生成
    response = llm.invoke(prompt)
    # print(response.cotent)
    return response.content



def extract_text_from_html(html_str):
    """
    HTML文字列からタグを除去し、生テキストを返す
    """
    soup = BeautifulSoup(html_str, 'html.parser')
    return soup.get_text(separator='\n').strip()


def normalize_url(url):
    """
    相対URLを正規化（例: PR TIMESサイト想定）
    """
    base = "https://prtimes.jp"
    if url.startswith('http'):
        return url
    else:
        return base + url

def format_articles(json_data):
    """
    JSONP形式のデータから記事データを抽出・整形するメソッド。
    title, summary, 本文, 詳細URL, 画像URL, 更新日時などをまとめる。
    """
    data = json_data

    articles = data.get('articles', [])
    # print(len(articles))

    formatted = []
    for article in articles:
        title = article.get('title', '')
        print(f"要約中: {title}")
        detail_url = normalize_url(article.get('url', ''))
        provider_name = article.get('provider', {}).get('name', '')
        updated_at = article.get('updated_at', {}).get('origin', '')

        raw_html = article.get('text', '')
        text_content = extract_text_from_html(raw_html)
        # summary = create_summary(raw_html, max_length=120)
        summary = create_summary(text_content, max_length=120)

        # 画像URLがある場合は正規化
        image_file = article.get('images', {}).get('original', {}).get('file', '')
        image_url = normalize_url(image_file) if image_file else ''

        # 整形結果をまとめる
        formatted.append({
            "title": title,
            "detail_url": detail_url,
            "provider": provider_name,
            "updated_at": updated_at,
            "summary": summary,
            "text": text_content,
            "image_url": image_url
        })

    return formatted


def print_articles_as_markdown_table(articles):
    """
    記事リストをMarkdownテーブル形式で出力する関数
    """
    # ヘッダー行
    print("| title | URL | provider | updated_at | summary |")
    print("|---|---|---|---|---|")

    # データ行
    for r in articles:
        title = r["title"].replace("|", "｜")
        detail_url = r["detail_url"].replace("|", "｜")
        provider = r["provider"].replace("|", "｜")
        updated_at = r["updated_at"].replace("|", "｜")
        summary = r["summary"].replace("|", "｜")

        print(f"| {title} | {detail_url} | {provider} | {updated_at} | {summary} |")

def articles_to_data_frame(articles):
    # JSONデータをDataFrameに変換
    df = pd.DataFrame(articles)

    # URL列をハイパーリンクとして整形
    df["detail_url"] = df["detail_url"].apply(lambda x: f'<a href="{x}" target="_blank">link</a>')

    # updated_at列を日付形式に変換し、MM/DD hh:mm形式でフォーマット
    df["updated_at"] = pd.to_datetime(df["updated_at"]).dt.strftime("%m/%d %H:%M")

    # 必要な列だけを選択
    columns_to_keep = ["title", "summary", "provider", "detail_url", "updated_at"]
    df = df[columns_to_keep]

    return df

# 実行例
# このスクリプトが直接実行された場合の処理
if __name__ == "__main__":
    json_data = fetch_json_data_with_webdriver("生成AI", limit=2)
    result = format_articles(json_data)
    print_articles_as_markdown_table(result)
