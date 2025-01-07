import os
from util import load_environment

import streamlit_authenticator as stauth
import yaml
from typing import List, Dict

def get_user_data_from_env():
    """環境変数からユーザー情報を取得"""
    return [{
        "username": os.getenv("STREAMLIT_USERNAME"),
        "email": os.getenv("STREAMLIT_EMAIL"),
        "password": os.getenv("STREAMLIT_PASSWORD")
    }]


def generate_yaml_credentials(users: List[Dict[str, str]]) -> str:
    """
    ユーザー情報を受け取り、指定した形式のYAMLに変換する。

    Args:
        users (List[Dict[str, str]]): 各ユーザーの情報を含む辞書のリスト。
            必須キー:
                - username: ユーザー名
                - email: ユーザーのメールアドレス
                - password: 平文のパスワード

    Returns:
        str: YAML形式の文字列。
    """


    # ユーザー情報にハッシュ化されたパスワードを追加
    for user in users:
        user["hashed_password"] = stauth.Hasher.hash(user["password"])

    # YAML構造を作成
    yaml_structure = {
        "credentials": {
            "usernames": {
                user["username"]: {
                    "email": user["email"],
                    "name": user["username"],
                    "password": user["hashed_password"],
                }
                for user in users
            }
        }
    }

    # YAML文字列に変換
    return yaml.dump(yaml_structure, default_flow_style=False, sort_keys=False)

# 使用例
if __name__ == "__main__":
     # 環境変数をロード
    load_environment()

    # 環境変数からユーザー情報を取得
    user_data = get_user_data_from_env()

    # # ユーザー情報を定義
    # user_data = [
    #     {"username": "demo", "email": "konyu@example.com", "password": "P@ssword"},
    # ]
    # # YAMLを生成
    yaml_output = generate_yaml_credentials(user_data)

    # 出力を表示
    print("Generated YAML: common/config.yaml のcredentialsを上書きしてください" )
    print(yaml_output)
