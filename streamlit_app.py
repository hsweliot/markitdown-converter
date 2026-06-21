import tempfile
from pathlib import Path

import streamlit as st
from markitdown import MarkItDown

st.set_page_config(
    page_title="MarkItDown Converter",
    page_icon="📄"
)

converter = MarkItDown()

st.title("📄 MarkItDown Converter")
st.write("Upload a file and convert it to Markdown.")

uploaded_file = st.file_uploader("Choose a file")

if uploaded_file is not None:
    suffix = Path(uploaded_file.name).suffix

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getbuffer())
        input_path = tmp.name

    try:
        result = converter.convert(input_path)
        markdown_text = result.text_content or ""

        output_filename = f"{Path(uploaded_file.name).stem}.md"

        st.success("Conversion completed!")

        st.download_button(
            label="⬇️ Download Markdown",
            data=markdown_text,
            file_name=output_filename,
            mime="text/markdown"
        )

        st.text_area(
            "Markdown Preview",
            markdown_text,
            height=400
        )

    except Exception as e:
        st.error(f"Conversion failed: {e}")
