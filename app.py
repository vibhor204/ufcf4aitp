import streamlit as st
from markitdown import MarkItDown
import os
import tempfile
import pandas as pd

# --- Page Configuration ---
st.set_page_config(page_title="Universal Document Reader", page_icon="📝", layout="wide")

def get_file_size(file_bytes):
    """Returns size in MB formatted to 2 decimal places."""
    size_mb = len(file_bytes) / (1024 * 1024)
    return size_mb

def convert_to_markdown(uploaded_file):
    md = MarkItDown()
    file_ext = os.path.splitext(uploaded_file.name)[1].lower()
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
        tmp_file.write(uploaded_file.getbuffer())
        tmp_file_path = tmp_file.name

    try:
        result = md.convert(tmp_file_path)
        return result.text_content
    except Exception as e:
        return f"ERROR: {str(e)}"
    finally:
        if os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)

# --- User Interface ---
st.title("🚀 Universal Document-to-Text Converter")
st.markdown("Convert Office docs, PDFs, and HTML into clean Markdown with size analytics.")

uploaded_files = st.file_uploader(
    "Upload your documents (Multiple allowed)", 
    type=['docx', 'xlsx', 'pptx', 'pdf', 'html', 'zip'], 
    accept_multiple_files=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        with st.expander(f"📄 {uploaded_file.name}", expanded=True):
            with st.spinner(f"Processing..."):
                # Get Original Size
                original_bytes = uploaded_file.getvalue()
                orig_size = get_file_size(original_bytes)
                
                # Convert
                converted_text = convert_to_markdown(uploaded_file)
            
            if converted_text.startswith("ERROR:"):
                st.error(f"⚠️ Could not read **{uploaded_file.name}**.")
            else:
                # Setup Tabs
                tab1, tab2 = st.tabs(["📄 Content Preview", "📊 File Size Comparison"])
                
                with tab1:
                    st.text_area("Markdown Preview", value=converted_text, height=300, key=f"text_{uploaded_file.name}")
                    
                    # Download Logic
                    base_filename = os.path.splitext(uploaded_file.name)[0]
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button("Download .md", converted_text, f"{base_filename}.md", "text/markdown")
                    with col2:
                        st.download_button("Download .txt", converted_text, f"{base_filename}.txt", "text/plain")

                with tab2:
                    # Calculate Converted Size
                    conv_bytes = converted_text.encode('utf-8')
                    conv_size = get_file_size(conv_bytes)
                    
                    # Calculate Reduction Percentage
                    reduction = ((orig_size - conv_size) / orig_size) * 100 if orig_size > 0 else 0
                    
                    # Create Comparison Table
                    stats_data = {
                        "File State": ["Original File", "Converted Text"],
                        "Size (MB)": [f"{orig_size:.2f} MB", f"{conv_size:.2f} MB"]
                    }
                    df_stats = pd.DataFrame(stats_data)
                    st.table(df_stats)
                    
                    # Highlighting the efficiency
                    st.success(f"💡 **Efficiency Note:** The text version is **{reduction:.1f}% smaller** than the original.")

else:
    st.info("Ready for input. Drag your files above to begin.")

st.divider()
st.caption("Built with Microsoft MarkItDown | Streamlit 2026 Edition")
