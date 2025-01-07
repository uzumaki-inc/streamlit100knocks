import json
import os
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_unstructured import UnstructuredLoader

from docx import Document
from docx.shared import RGBColor

from langchain.document_loaders import TextLoader
from langchain.schema import Document as LangDocument
from langchain.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

# OpenAIの環境変数を読み込み
from common.util import load_environment
load_environment()


def load_style_guide(file_path: str):
    """
    スタイルガイドをテキストファイルからロードし、LangDocument形式に変換する。
    :param file_path: スタイルガイドのテキストファイルパス
    :return: LangDocumentのリスト
    """
    loader = TextLoader(file_path)
    documents = loader.load()

    # ルールごとに分割してLangDocument形式に変換
    rules = documents[0].page_content.split("\nルール:")
    # print(rules)
    return [LangDocument(page_content=rule.strip()) for rule in rules if rule.strip()]


def create_vectorstore(docs, embeddings_model: str = "text-embedding-3-small"):
    """
    LangDocumentリストをChromaベクトルストアに登録する。
    :param docs: LangDocument形式のリスト
    :param embeddings_model: Embeddingsモデル名
    :return: Chromaベクトルストア
    """
    embeddings = OpenAIEmbeddings(model=embeddings_model)

    if os.getenv("ENV") != "production":
        # Development environment - use SQLite persistence
        persist_directory = "./chroma_store"
        try:
            vectorstore = Chroma(
                persist_directory=persist_directory,
                embedding_function=embeddings
            )
            print("既存のベクトルストアをロードしました。")
            return vectorstore
        except Exception as e:
            print(f"新しいベクトルストアを作成します: {e}")
            vectorstore = Chroma.from_documents(
                docs,
                embeddings,
                persist_directory=persist_directory
            )
            return vectorstore
    else:
        # Production environment - in-memory storage
        vectorstore = Chroma.from_documents(
            docs,
            embeddings,
            persist_directory=None  # This makes it run in-memory
        )
        return vectorstore



def get_style_guide_rules(retriever):
    """
    スタイルガイドのルールを取得する。
    """
    # クエリを検索
    query = "日立のスタイルガイドはありますか？"

    context_docs = retriever.invoke(query)
    rules = "\n\n".join([doc.page_content for doc in context_docs])
    print("クエリ実行結果")
    print(rules)

    return rules

def get_retriever():
    print("retriever取得")
    # スタイルガイドのファイルパス
    file_path = "./knocks/knock_3/style_guide.txt"

    # スタイルガイドをロード
    docs = load_style_guide(file_path)

    db = create_vectorstore(docs)
    retriever = db.as_retriever()
    get_style_guide_rules(retriever)

    return retriever


# WordファイルをHTMLに変換する関数
def word_to_html(file_path):
    doc = Document(file_path)
    html_content = ""

    for paragraph in doc.paragraphs:
        paragraph_html = ""

        for run in paragraph.runs:
            text = run.text
            style = ""

            # 太字チェック
            if run.bold:
                style += "font-weight:bold;"

            # 文字色チェック
            if run.font.color and run.font.color.rgb:
                color = run.font.color.rgb
                style += f"color:#{color};"

            # スタイルを適用してHTMLに変換
            paragraph_html += f"<span style='{style}'>{text}</span>"

        # 段落ごとに改行を追加
        html_content += f"<p>{paragraph_html}</p>"

    return html_content

# Wordファイルの内容を読み込む関数
def read_word_file(file_path):
    doc = Document(file_path)
    content = [paragraph.text for paragraph in doc.paragraphs]
    return "\n".join(content)

def load_word_file_with_langchain(file_path: str) -> str:
    """
    LangChainのUnstructuredLoaderを使用してWordファイルからテキストを抽出する。
    """
    loader = UnstructuredLoader(file_path)
    documents = loader.load()
    return "\n".join([doc.page_content for doc in documents])

def correct_text_with_llm(text: str, retriever) -> list:
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0
    )

    rules = get_style_guide_rules(retriever)

    prompt = PromptTemplate(
        input_variables=["text", "rules"],
        template="""
        以下のチェック対象テキストの校正結果をJSON形式で出力してください。

        スタイルガイド:
        {rules}

        チェック対象テキスト:
        {text}

        必ず以下の形式のJSONで出力してください:
        {{
          "corrections": [
            {{
              "original": "修正前の表現",
              "corrected": "修正後の表現",
              "reason": "修正理由",
              "line_number": 行番号
            }}
          ]
        }}
        """
    )

    formatted_prompt = prompt.format(text=text, rules=rules)
    print(formatted_prompt)
    response = llm.invoke(formatted_prompt)
    print("invoke結果")
    print(response.content)

    try:
        # 出力結果が```json```で囲まれている場合、それを取り除く
        cleaned_output = (response.content).strip("```json").strip("```").strip()
        result = json.loads(cleaned_output)
        print("invoke結果")
        print(result)
        return result.get("corrections", [])
    except json.JSONDecodeError:
        return []

def add_corrections_to_word(input_file: str, corrections: list, output_file: str):
    """
    Wordファイルに修正箇所を擬似コメントとして追加し、修正版を保存する。
    修正内容は対象段落の末尾に太字・赤色テキストとして追加される。
    """
    doc = Document(input_file)
    paragraphs = doc.paragraphs


    for correction in corrections:
        print("修正内容")
        print(correction)
        line_number =  int(str(correction["line_number"])) - 1  # 行番号を0ベースに変換
        original = correction["original"]
        corrected = correction["corrected"]
        reason = correction["reason"]

        # 指定された行番号の段落に修正案を追加
        if 0 <= line_number < len(paragraphs):
            paragraph = paragraphs[line_number]
            if original in paragraph.text:  # originalが含まれている場合のみ
                # 修正案を末尾に追加
                comment_text = f" [修正案: '{corrected}' 理由: {reason}]"
                run = paragraph.add_run(comment_text)
                run.bold = True  # 太字
                run.font.color.rgb = RGBColor(255, 0, 0)  # 赤色

    # Wordファイルを保存
    doc.save(output_file)
    print(f"修正版Wordファイルが {output_file} に保存されました。")

def process_word_file(input_file: str, output_file: str, retriever):
    """
    Wordファイルを読み込み、修正をコメントとして追加し、新しいWordファイルを保存する。
    """
    print("LangChainでWordファイルを読み込んでいます...")
    text = load_word_file_with_langchain(input_file)

    print("誤字脱字の修正を実行しています...")
    corrections = correct_text_with_llm(text, retriever)

    print("Wordファイルにコメントを追加しています...")
    add_corrections_to_word(input_file, corrections, output_file)

# 実行例
if __name__ == "__main__":
    input_word_file = "knocks/knock_2/input.docx"  # 入力Wordファイル
    output_word_file = "knocks/knock_2/output.docx"  # 出力Wordファイル

    process_word_file(input_word_file, output_word_file)
