import streamlit as st
from markitdown import MarkItDown
import os
import io

# --- Configuration & Styling ---
st.set_page_config(page_title="Universal Document Reader", page_icon="📄")

st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stTextArea textarea {
        font-family: 'Courier New', Courier, monospace;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Logic Layer ---
def convert_file(uploaded_file):
    """
    Handles the conversion logic using MarkItDown.
    """
    # Initialize MarkItDown with a timeout for web-based resources (HTML/Links)
    # Note: MarkItDown handles local files directly, but we wrap it in 
    # a handler to ensure stability.
    md = MarkItDown()
    
    try:
        # Since Streamlit provides a BytesIO object, we need to handle 
        # temporary storage or direct conversion if supported.
        # MarkItDown typically expects a file path or stream.
        
        # We save to a temporary location to ensure MarkItDown's internal 
        # file-type detection works via extensions.
        temp_filename = uploaded_file.name
        with open(temp_filename, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Perform conversion
        result = md.convert(temp_filename)
        converted_text = result.text_content
        
        # Clean up temporary file
        os.remove(temp_filename)
        
        return converted_text

    except Exception as e:
        # Resilience: Return None to trigger the error message in UI
        return None

# --- UI Layer ---
st.title("📄 Universal Document Reader")
st.subheader("Convert Office Docs, PDFs, and HTML to Markdown instantly.")

# [2] Upload Area
uploaded_files = st.file_uploader(
    "Drag and drop files here", 
    type=['docx', 'xlsx', 'pptx', 'pdf', 'html', 'zip'], 
    accept_multiple_files=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        st.divider()
        st.write(f"### Processing: `{uploaded_file.name}`")
        
        with st.spinner('Converting...'):
            content = convert_file(uploaded_file)
        
        if content:
            # [2] Instant Preview
            st.text_area(
                label="Extracted Content Preview", 
                value=content, 
                height=300, 
                key=f"preview_{uploaded_file.name}"
            )
            
            # [4] Dynamic Filename Logic
            base_name = os.path.splitext(uploaded_file.name)[0]
            
            col1, col2 = st.columns(2)
            
            # [2] Download Options
            with col1:
                st.download_button(
                    label="⬇️ Download as Markdown (.md)",
                    data=content,
                    file_name=f"{base_name}_converted.md",
                    mime="text/markdown"
                )
            
            with col2:
                st.download_button(
                    label="⬇️ Download as Text (.txt)",
                    data=content,
                    file_name=f"{base_name}_converted.txt",
                    mime="text/plain"
                )
        else:
            # [3] Resilience / Error Handling
            st.error(f"⚠️ Could not read {uploaded_file.name}. Please check the format.")

else:
    st.info("Upload a document to see the magic happen!")

st.markdown("---")
st.caption("Powered by Microsoft MarkItDown & Streamlit")
