
import streamlit as st
from streamlit.components.v1 import html
import tempfile
import os
from reviewer import process_word_file,word_to_html

# StreamlitのUI部分
st.title("Wordファイル校正アプリ ver.1")
st.write("Wordファイルをドラッグアンドドロップでアップロードして内容を確認します。")

# ファイルアップロード
uploaded_file = st.file_uploader("Wordファイルをアップロードしてください", type=["docx"])

# ファイルがアップロードされた場合
if uploaded_file is not None:
    st.success("ファイルがアップロードされました！")
    st.write(f"ファイル名: {uploaded_file.name}")

    # 一時ファイルにアップロードしたファイルを保存
    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = os.path.join(temp_dir, "input.docx")
        output_path = os.path.join(temp_dir, "output.docx")

        st.subheader("入力ファイルの内容:")
        # アップロードしたファイルを保存
        with open(input_path, "wb") as f:
            f.write(uploaded_file.getvalue())

            processed_html = word_to_html(input_path)

            # HTMLをStreamlit上に表示
            html(f"""
            <div style="border: 1px solid #ddd; padding: 10px; border-radius: 5px; background-color: #f9f9f9; max-height: 300px; overflow-y: scroll;">
                {processed_html}
            </div>
            """, height=300)
        # process_word_fileを呼び出す
        st.info("ファイルを処理しています。少々お待ちください...")
        process_word_file(input_path, output_path)

        # 処理後のWordファイルを読み込んでプレビュー表示
        st.subheader("修正後のファイルの内容:")
        processed_html = word_to_html(output_path)

        # HTMLをStreamlit上に表示
        html(f"""
        <div style="border: 1px solid #ddd; padding: 10px; border-radius: 5px; background-color: #f9f9f9; max-height: 400px; overflow-y: scroll;">
            {processed_html}
        </div>
        """, height=400)

        # 処理結果をダウンロード可能にする
        with open(output_path, "rb") as f:
            processed_file = f.read()

        st.success("ファイルの処理が完了しました！")
        st.download_button(
            label="修正済みファイルをダウンロード",
            data=processed_file,
            file_name="output_reviewed.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

# ファイルがアップロードされていない場合
else:
    st.info("ここにWordファイルをドラッグアンドドロップするか、ファイルを選択してください。")
