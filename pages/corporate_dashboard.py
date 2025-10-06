import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(page_title="Corporate Analytics", layout="wide")

# --- Styling and Data Fetching ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
    
    .stApp {
        background-image: url("https://analytics.smartsalem.tech/smartsuite/bg-login.688761c8fcdbbeb1.jpg");
        background-size: cover;
        background-attachment: fixed;
    }
    h1, h2, h3, h4, .stMarkdown, .stMetric label, .stMetric div {
        color: white !important;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.6);
        font-family: 'Roboto', sans-serif !important;
    }
    div[data-testid="stMetric"] {
        background-color: rgba(0, 0, 0, 0.3) !important;
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 20px !important;
        border-radius: 10px !important;
        text-align: center !important;
    }
    .section-divider {
        border-top: 2px solid #00899D;
        margin: 40px 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def style_chart(fig, title):
    """Applies consistent styling to charts."""
    fig.update_layout(
        title={'text': title, 'y':0.9, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'},
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0.2)',
        font_color='white',
        font_family='Roboto',
        legend_title_font_color='white'
    )
    return fig

# --- Check for data ---
if 'corp_df' not in st.session_state or st.session_state.corp_df is None:
    st.error("⚠️ No data available. Please upload a file on the main page first.")
    if st.button("Back to Home Page"):
        st.switch_page("corporate_app.py")
    st.stop()

master_df = st.session_state.corp_df

# --- Main Service Filter (Wellness/Governmental) ---
st.markdown("<h3>Filter by Service Type</h3>", unsafe_allow_html=True)
service_filter = st.radio(
    "Select Service Type:",
    ("Wellness", "Governmental"),
    horizontal=True,
    label_visibility="collapsed"
)

if service_filter == "Wellness":
    df = master_df[master_df['ServiceType'] == 'Private Services'].copy()
    st.success("Displaying data for Wellness (Private) services")
else:
    df = master_df[master_df['ServiceType'] != 'Private Services'].copy()
    st.info("Displaying data for Governmental services")

if df.empty:
    st.warning("No data available for this service type in the uploaded file.")
    st.stop()

# --- Calculate Age ---
df['Age'] = df['TransactionDate'].dt.year - df['DOB'].dt.year

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.title("📊 Comprehensive Analytics Dashboard")

# --- Overview ---
st.markdown("<h3>Overview</h3>", unsafe_allow_html=True)
total_revenue = df['ServicePaidAmount'].sum()
total_transactions = len(df)
avg_transaction_value = df['ServicePaidAmount'].mean()

col1, col2, col3 = st.columns(3)
col1.metric("Total Revenue (AED)", f"{total_revenue:,.0f}")
col2.metric("Total Transactions", f"{total_transactions:,.0f}")
col3.metric("Avg. Transaction Value (AED)", f"{avg_transaction_value:,.0f}")

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# --- Revenue and Service Analytics ---
st.markdown("<h3>Revenue and Service Analytics</h3>", unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    st.markdown("<h5>Top 10 Services by Revenue</h5>", unsafe_allow_html=True)
    top_services_revenue = df.groupby('ServiceName')['ServicePaidAmount'].sum().nlargest(10)
    fig_top_services = px.bar(top_services_revenue, y=top_services_revenue.index, x='ServicePaidAmount', orientation='h', labels={'y': 'Service Name', 'ServicePaidAmount': 'Total Revenue'})
    fig_top_services.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(style_chart(fig_top_services, "Top 10 Services by Revenue"), use_container_width=True)

with col2:
    st.markdown("<h5>Revenue Distribution by Center</h5>", unsafe_allow_html=True)
    revenue_by_center = df.groupby('CenterName')['ServicePaidAmount'].sum()
    fig_rev_center = px.pie(values=revenue_by_center.values, names=revenue_by_center.index)
    st.plotly_chart(style_chart(fig_rev_center, "Revenue Distribution by Center"), use_container_width=True)

# --- Demographic Analytics ---
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown("<h3>Customer Demographics</h3>", unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    st.markdown("<h5>Transaction Distribution by Gender</h5>", unsafe_allow_html=True)
    gender_counts = df['Gender'].value_counts()
    fig_gender = px.pie(values=gender_counts.values, names=gender_counts.index)
    st.plotly_chart(style_chart(fig_gender, "Transaction Distribution by Gender"), use_container_width=True)

with col2:
    st.markdown("<h5>Top 10 Nationalities</h5>", unsafe_allow_html=True)
    top_nationalities = df['Nationality'].value_counts().nlargest(10)
    fig_nat = px.bar(top_nationalities, x=top_nationalities.index, y=top_nationalities.values, labels={'x': 'Nationality', 'y': 'Number of Transactions'})
    st.plotly_chart(style_chart(fig_nat, "Top 10 Nationalities"), use_container_width=True)

st.markdown("<h5>Transaction Distribution by Age Group</h5>", unsafe_allow_html=True)
bins = [0, 18, 30, 40, 50, 60, 100]
labels = ['<18', '18-29', '30-39', '40-49', '50-59', '60+']
df['Age Group'] = pd.cut(df['Age'], bins=bins, labels=labels, right=False)
age_group_counts = df['Age Group'].value_counts().sort_index()
fig_age = px.bar(age_group_counts, x=age_group_counts.index, y=age_group_counts.values, labels={'x': 'Age Group', 'y': 'Number of Transactions'})
st.plotly_chart(style_chart(fig_age, "Transaction Distribution by Age Group"), use_container_width=True)

# --- Time Analytics ---
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown("<h3>Time-Based Analytics</h3>", unsafe_allow_html=True)

st.markdown("<h5>Transactions and Revenue Over Time</h5>", unsafe_allow_html=True)
df_time = df.set_index('TransactionDate').resample('D').agg({'ServicePaidAmount': 'sum', 'ServiceName': 'count'}).rename(columns={'ServiceName': 'Transactions'}).reset_index()
fig_time = px.line(df_time, x='TransactionDate', y=['ServicePaidAmount', 'Transactions'], labels={'TransactionDate': 'Date'}, title="Daily Transactions and Revenue")
fig_time.update_layout(yaxis_title="Value / Count")
st.plotly_chart(style_chart(fig_time, "Transactions and Revenue Over Time"), use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown("<h5>Transactions by Day of Week</h5>", unsafe_allow_html=True)
    df['DayOfWeek'] = df['TransactionDate'].dt.day_name()
    day_order = ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    day_counts = df['DayOfWeek'].value_counts().reindex(day_order)
    fig_day = px.bar(day_counts, x=day_counts.index, y=day_counts.values, labels={'x': 'Day of Week', 'y': 'Number of Transactions'})
    st.plotly_chart(style_chart(fig_day, "Transactions by Day of Week"), use_container_width=True)

with col2:
    st.markdown("<h5>Transactions by Hour of Day</h5>", unsafe_allow_html=True)
    df['Hour'] = pd.to_datetime(df['TransactionTime'], format='%H:%M:%S', errors='coerce').dt.hour
    hour_counts = df['Hour'].value_counts().sort_index()
    fig_hour = px.bar(hour_counts, x=hour_counts.index, y=hour_counts.values, labels={'x': 'Hour of Day', 'y': 'Number of Transactions'})
    st.plotly_chart(style_chart(fig_hour, "Transactions by Hour of Day"), use_container_width=True)

