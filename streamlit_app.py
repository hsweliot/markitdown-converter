import io
import tempfile
import zipfile
from pathlib import Path

import streamlit as st
from markitdown import MarkItDown

st.set_page_config(
    page_title="MarkItDown Converter",
    page_icon="📄",
    layout="wide",
)

converter = MarkItDown()

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1100px;
        }
        .hero {
            padding: 1.2rem 1.4rem;
            border-radius: 18px;
            border: 1px solid rgba(255,255,255,0.08);
            background: linear-gradient(135deg, rgba(60,60,60,0.22), rgba(20,20,20,0.12));
            margin-bottom: 1.2rem;
        }
        .hero h1 {
            margin: 0;
            font-size: 2.2rem;
        }
        .hero p {
            margin: 0.35rem 0 0 0;
            opacity: 0.8;
        }
        .card {
            padding: 1rem 1.1rem;
            border-radius: 16px;
            border: 1px solid rgba(255,255,255,0.08);
            background: rgba(255,255,255,0.03);
            margin-bottom: 1rem;
        }
        .small-label {
            font-size: 0.85rem;
            opacity: 0.72;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 0.35rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>📄 MarkItDown Converter</h1>
        <p>Upload one or more files, convert them to Markdown, and download a ZIP.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns([1.05, 1], gap="large")

with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="small-label">Upload</div>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "Choose files",
        type=None,
        accept_multiple_files=True,
        help="You can upload multiple files at once. Supported examples: PDF, DOCX, PPTX, XLSX, CSV, HTML, XML, JSON, images, and more.",
        label_visibility="collapsed",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    if uploaded_files:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="small-label">Files selected</div>', unsafe_allow_html=True)
        for f in uploaded_files:
            file_type = f.type or "Unknown"
            st.write(f"• **{f.name}** — {file_type} — {f.size / 1024:.1f} KB")
        st.markdown("</div>", unsafe_allow_html=True)

        convert_clicked = st.button("Convert to Markdown", use_container_width=True)

        if convert_clicked:
            results = []
            errors = []

            with st.spinner("Converting files..."):
                for uploaded_file in uploaded_files:
                    suffix = Path(uploaded_file.name).suffix

                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                        tmp.write(uploaded_file.getbuffer())
                        input_path = tmp.name

                    try:
                        result = converter.convert(input_path)
                        markdown_text = result.text_content or ""
                        output_name = f"{Path(uploaded_file.name).stem}.md"
                        results.append((output_name, markdown_text))
                    except Exception as e:
                        errors.append(f"{uploaded_file.name}: {e}")

            st.session_state["converted_results"] = results
            st.session_state["conversion_errors"] = errors

            if results:
                st.success(f"Converted {len(results)} file(s) successfully.")
            if errors:
                st.warning("Some files failed to convert.")

with right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="small-label">Output</div>', unsafe_allow_html=True)

    results = st.session_state.get("converted_results", [])

    if results:
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for filename, markdown_text in results:
                zf.writestr(filename, markdown_text)

        zip_buffer.seek(0)

        st.download_button(
            label="⬇️ Download ZIP of Markdown files",
            data=zip_buffer,
            file_name="markdown_exports.zip",
            mime="application/zip",
            use_container_width=True,
        )

        st.subheader("Preview")
        selected_names = [name for name, _ in results]
        selected_file = st.selectbox("Pick a file to preview", selected_names)

        preview_text = next(text for name, text in results if name == selected_file)
        st.text_area("Markdown preview", preview_text, height=500)

    else:
        st.info("Upload files and click **Convert to Markdown** to see the preview here.")
        st.markdown(
            """
            **Good for:**  
            PDF, DOCX, PPTX, XLSX, CSV, HTML, XML, JSON, images, and other supported formats.
            """
        )

    errors = st.session_state.get("conversion_errors", [])
    if errors:
        st.markdown("### Conversion errors")
        for err in errors:
            st.error(err)

    st.markdown("</div>", unsafe_allow_html=True)
