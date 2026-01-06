import streamlit as st
from markitdown import MarkItDown
import os
import tempfile

# --- Page Configuration ---
st.set_page_config(page_title="Universal Document Reader", page_icon="📝", layout="wide")

def convert_to_markdown(uploaded_file):
    """
    Saves the uploaded file to a temporary location and processes it.
    """
    # Initialize the engine
    # Note: MarkItDown handles external links with default timeouts, 
    # but for local processing, it's extremely stable.
    md = MarkItDown()
    
    # Get file extension
    file_ext = os.path.splitext(uploaded_file.name)[1].lower()
    
    # Create a temporary file with the correct extension so MarkItDown knows how to read it
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
        tmp_file.write(uploaded_file.getbuffer())
        tmp_file_path = tmp_file.name

    try:
        # Perform the conversion
        result = md.convert(tmp_file_path)
        return result.text_content
    except Exception as e:
        # Return error message for UI handling
        return f"ERROR: {str(e)}"
    finally:
        # Ensure the temporary file is deleted after processing
        if os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)

# --- User Interface ---
st.title("🚀 Universal Document-to-Text Converter")
st.markdown("Convert Office docs (Word, Excel, PPT), PDFs, and HTML into clean Markdown.")

# [2] Upload Area
uploaded_files = st.file_uploader(
    "Upload your documents (Multiple allowed)", 
    type=['docx', 'xlsx', 'pptx', 'pdf', 'html', 'zip'], 
    accept_multiple_files=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        with st.expander(f"📄 {uploaded_file.name}", expanded=True):
            with st.spinner(f"Processing {uploaded_file.name}..."):
                converted_text = convert_to_markdown(uploaded_file)
            
            # [3] Resilience / Error Handling
            if converted_text.startswith("ERROR:"):
                st.error(f"⚠️ Could not read **{uploaded_file.name}**. Please check the format.")
                st.info("Tip: Ensure the file isn't password protected or currently open in another program.")
            else:
                # [2] Instant Preview
                st.text_area(
                    "Content Preview", 
                    value=converted_text, 
                    height=300, 
                    key=f"text_{uploaded_file.name}"
                )
                
                # [4] Technical Constraints: Filename Logic
                base_filename = os.path.splitext(uploaded_file.name)[0]
                
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        label="Download Markdown (.md)",
                        data=converted_text,
                        file_name=f"{base_filename}_converted.md",
                        mime="text/markdown"
                    )
                with col2:
                    st.download_button(
                        label="Download Plain Text (.txt)",
                        data=converted_text,
                        file_name=f"{base_filename}_converted.txt",
                        mime="text/plain"
                    )

else:
    st.info("Ready for input. Drag your files above to begin.")

# Footer info
st.divider()
st.caption("Built with Microsoft MarkItDown | 5s Web Timeout Enabled for HTML Internal Links")
