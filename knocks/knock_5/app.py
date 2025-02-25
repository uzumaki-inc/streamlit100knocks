import streamlit as st
from sentens_maker import create_agent, create_prompt, MeetingResponse
import json

def main():
    st.title("英語ミーティングフレーズジェネレーター")

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
