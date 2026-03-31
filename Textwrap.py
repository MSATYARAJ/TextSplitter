
import streamlit as st
import pandas as pd
import textwrap
import io
from xlsxwriter import Workbook

# --- Page Configuration ---
st.set_page_config(page_title="Text Splitter Pro", page_icon="✂️", layout="wide")

# --- Initialize Reset Key ---
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0

def clear_all_data():
    """Increments the key to force a reset of all widgets."""
    st.session_state.uploader_key += 1
    # st.rerun() ensures the app reflects the change immediately
    st.rerun()

# --- Custom Styling ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 4px; height: 3em; font-weight: bold; }
    .stDownloadButton>button { width: 100%; background-color: #28a745; color: white; }
    /* Style for the Clear Button */
    div[data-testid="stSidebar"] .stButton>button { background-color: #dc3545; color: white; border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- App Header ---
st.title("✂️ Professional Text Column Splitter")
st.markdown("Split long descriptions into new columns without breaking words.")
st.divider()

# --- Sidebar (Settings & Clear) ---
with st.sidebar:
    st.header("⚙️ Configuration")
    max_length = st.number_input("Max Characters per Column", min_value=1, value=50)
    
    st.markdown("---")
    st.subheader("🧹 App Control")
    # Using the clear function as a callback for a clean reset
    st.button("Clear All Data", on_click=clear_all_data, help="Reset the uploader and clear current results.")

# --- Main Interface ---
col_upload, col_preview = st.columns([1, 2], gap="large")

with col_upload:
    st.subheader("1. Upload File")
    # The key=st.session_state.uploader_key allows us to clear the file manually
    uploaded_file = st.file_uploader(
        "Choose a CSV or Excel file", 
        type=["csv", "xlsx"], 
        key=f"file_uploader_{st.session_state.uploader_key}"
    )

if uploaded_file:
    # Read the file
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    
    with col_upload:
        column_to_split = st.selectbox("Select column to process:", df.columns)
        process_ready = st.button("Generate New Columns", type="primary")

    with col_preview:
        st.subheader("2. Data Preview")
        
        if process_ready:
            # Splitting Logic
            with st.spinner("Processing..."):
                def split_to_chunks(text, m_len):
                    return textwrap.wrap(str(text), width=m_len,break_long_words = False) if pd.notna(text) else []
                
                chunks = df[column_to_split].apply(lambda x: split_to_chunks(x, max_length))
                new_cols = pd.DataFrame(chunks.tolist())
                new_cols.columns = [f"Part_{i+1}" for i in range(new_cols.shape[1])]
                df_final = pd.concat([df, new_cols], axis=1)
            
            st.success("Successfully processed!")
            st.dataframe(df_final.head(20), use_container_width=True)

            # Export Section
            st.divider()
            d1, d2 = st.columns(2)
            
            # Excel Buffer
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_final.to_excel(writer, index=False)
            
            d1.download_button("📥 Download Excel", data=buffer.getvalue(), file_name="split_results.xlsx")
            d2.download_button("📥 Download CSV", data=df_final.to_csv(index=False).encode('utf-8'), file_name="split_results.csv")
        else:
            st.info("Select a column and click 'Generate' to see results.")
            st.dataframe(df.head(10), use_container_width=True)
else:
    with col_preview:
        st.info("Upload a file on the left to begin.")
