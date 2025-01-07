import streamlit as st
import os
import sys

from common.auth import init_authenticator

# 認証初期化
yaml_path = "common/config.yaml"
authenticator = init_authenticator(yaml_path)

# 認証処理
authenticator.login()
if st.session_state["authentication_status"]:
    # ログイン成功
    with st.sidebar:
        st.markdown(f'## Welcome *{st.session_state["name"]}*')
        authenticator.logout('Logout', 'sidebar')

elif st.session_state["authentication_status"] is False:
    # ログイン失敗
    st.error('Username/password is incorrect')
    st.stop()  # 処理を中断

elif st.session_state["authentication_status"] is None:
    # デフォルト
    st.warning('Please enter your username and password')
    st.stop()  # 処理を中断


# ノックディレクトリの設定
knocks_dir = "knocks"

# ノック一覧を取得
knock_list = [d for d in os.listdir(knocks_dir) if os.path.isdir(os.path.join(knocks_dir, d))]

def get_display_name(knock_name):
    """サブディレクトリの Readme.txt があればその1行目を取得、なければディレクトリ名を返す"""
    readme_path = os.path.join(knocks_dir, knock_name, "readme.txt")
    if os.path.exists(readme_path):
        try:
            with open(readme_path, "r", encoding="utf-8") as f:
                first_line = f.readline().strip()
            if first_line:  # 1行目が空でない場合
                return first_line
        except Exception as e:
            st.error(f"エラー: {knock_name}/readme.txt の読み込みに失敗しました: {e}")
    return knock_name  # デフォルトでディレクトリ名を返す

# ノック選択肢の表示名を生成
knock_options = [""] + knock_list  # 最初に空の選択肢を追加
knock_display_names = ["ノックを選択してください"] + [get_display_name(knock) for knock in knock_list]

# サイドバーにノック一覧を表示
st.sidebar.title("生成AI100本ノック")
selected_knock_display = st.sidebar.selectbox(
    "挑戦するノックを選んでください",
    knock_display_names
)

# 選択されたノックに対応するディレクトリ名を取得
selected_knock = (
    knock_list[knock_display_names.index(selected_knock_display) - 1]
    if selected_knock_display != "ノックを選択してください"
    else ""
)

# メインエリアに選択したノックを展開
if selected_knock == "":
    st.title("生成AI100本ノックへようこそ！")
    st.write("左のサイドバーからデモを選んで下さい")
else:
    knock_file_path = os.path.join(knocks_dir, selected_knock, "app.py")  # 例: knocks/knock1/app.py
    knock_dir_path = os.path.join(knocks_dir, selected_knock)

    if os.path.exists(knock_file_path):
        # ノックスクリプトを動的に実行
        try:
            # インポートしたいモジュールがあるディレクトリを sys.path に追加
            if knock_dir_path not in sys.path:
                sys.path.insert(0, knock_dir_path)
            with open(knock_file_path, "r", encoding="utf-8") as f:
                script_content = f.read()
            exec(script_content, globals())  # スクリプトを実行
        except Exception as e:
            st.error(f"ノック {selected_knock} の実行中にエラーが発生しました: {e}")
    else:
        st.error(f"{selected_knock}/app.py が見つかりません！")
