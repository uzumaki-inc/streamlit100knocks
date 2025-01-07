import os
from dotenv import load_dotenv

def load_environment():
    """
    環境変数をロードするメソッド。
    - ENV=production が設定されていれば、本番環境として `.env` ファイルを無視。
    - それ以外の場合は `.env` ファイルを読み込む。
    """
    if os.getenv("ENV") != "production":  # 本番環境でない場合
        load_dotenv()
        print("Loaded .env file for local development")
    else:
        print("Running in production environment")

    # 環境変数が設定されていない場合にエラーを投げる（必要に応じて追加）
    required_vars = [
        "OPENAI_API_KEY",
        "STREAMLIT_USERNAME",
        "STREAMLIT_EMAIL",
        "STREAMLIT_PASSWORD"
    ]

    for var in required_vars:
        if not os.getenv(var):
            raise EnvironmentError(f"{var}が設定されていません。")
