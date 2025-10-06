import streamlit as st
import pandas as pd
from style_utils import load_css, load_footer

# --- Initialize Session State ---
if 'corp_df' not in st.session_state:
    st.session_state.corp_df = None

# --- Page Configuration ---
st.set_page_config(page_title="Corporate Analytics Upload", layout="centered")
load_css()

st.title("📊 Online Analytics Dashboard")
st.markdown("Upload the new report file here to start the analysis. ✨")

# --- File Uploader ---
uploaded_file = st.file_uploader("Upload Corporate Excel File", type=["xlsx", "xls"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        
        # --- Check for required columns ---
        required_columns = [
            'CenterName', 'TransactionDate', 'TransactionTime', 'ServiceType', 
            'Gender', 'Nationality', 'DOB', 'ServiceName', 'ServicePaidAmount'
        ]
        
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            st.error(f"The uploaded file is missing the following columns: {', '.join(missing_cols)}")
        else:
            # --- Select and clean data ---
            analytics_df = df[required_columns].copy()

            # --- Convert data types ---
            analytics_df['TransactionDate'] = pd.to_datetime(analytics_df['TransactionDate'], errors='coerce')
            analytics_df['DOB'] = pd.to_datetime(analytics_df['DOB'], errors='coerce')
            analytics_df['ServicePaidAmount'] = pd.to_numeric(analytics_df['ServicePaidAmount'], errors='coerce')

            # Drop rows with null values in essential columns
            analytics_df.dropna(subset=['TransactionDate', 'ServicePaidAmount', 'DOB'], inplace=True)

            # Store the dataframe in the session state
            st.session_state.corp_df = analytics_df
            
            st.success("✅ File processed successfully!")

            if st.button("🚀 View Analytics Dashboard", use_container_width=True, type="primary"):
                st.switch_page("pages/corporate_dashboard.py")

    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")
        st.exception(e)

# --- Footer ---
load_footer()

