import streamlit as st
from sentens_maker import create_agent, create_prompt, MeetingResponse, read_phrases_csv
import json
import pandas as pd

def main():
    st.title("英語ミーティングフレーズジェネレーター")
    # 初期化
    if 'show_phrases' not in st.session_state:
        st.session_state.show_phrases = False

    # フレーズCSVファイル表示機能を追加
    st.markdown("### フレーズ一覧")

    # ボタンのテキストを現在の状態に基づいて設定
    button_text = "フレーズ一覧を閉じる" if st.session_state.show_phrases else "フレーズ一覧を表示"

    # ボタンクリックのハンドラ - セッション状態を変更して再実行
    if st.button(button_text, key="toggle_phrases"):
        st.session_state.show_phrases = not st.session_state.show_phrases
        st.rerun()  # ボタンラベルを更新するために再実行

    # セッション状態に基づいてデータフレームを表示
    if st.session_state.show_phrases:
        try:
            phrases_data = read_phrases_csv()
            st.dataframe(
                phrases_data,
                column_config={
                    "Phrase": "英語フレーズ",
                    "Translation": "日本語訳",
                },
                use_container_width=True,
                height=400
            )
        except Exception as e:
            st.error(f"フレーズファイルの読み込みに失敗しました: {str(e)}")
    url = st.text_input(
        "題材のURLを指定して下さい",
        placeholder="https://example.com"
    )

    if st.button("フレーズを生成", type="primary"):
        if url:
            with st.spinner("英語フレーズを生成中..."):
                try:
                    # 既存の実装を使用
                    agent = create_agent()
                    inputs = {"messages": [("system", create_prompt(url, 3))]}
                    res = agent.invoke(inputs)

                    # 文字列からJSONへ変換
                    content = res['messages'][-1].content
                    print("#### CONTENT DATA ####")
                    print(content)

                    # JSONからPydanticモデルへ変換
                    meeting_response = MeetingResponse.model_validate_json(content)

                    # 結果の表示
                    for i, phrase in enumerate(meeting_response.phrases, 1):
                        with st.expander(f"フレーズ {i}: {phrase.phrase}", expanded=True):
                            cols = st.columns(2)
                            with cols[0]:
                                st.markdown("##### 英語フレーズ")
                                st.info(phrase.phrase)
                            with cols[1]:
                                st.markdown("##### 日本語訳")
                                st.info(phrase.translation)

                            st.markdown("##### 例文")
                            st.success(phrase.sentence)
                            st.markdown("##### 英文説明")
                            st.info(phrase.explanation)


                except Exception as e:
                    st.error(f"エラーが発生しました: {str(e)}")
        else:
            st.warning("URLを入力してください")

    with st.sidebar:
        st.markdown("### 使い方")
        st.markdown("""
        1. 分析したいWebページのURLを入力
        2. 「フレーズを生成」ボタンをクリック
        3. AIが内容を分析して英語フレーズを生成
        4. 生成されたフレーズと例文を確認
        """)

if __name__ == "__main__":
    main()