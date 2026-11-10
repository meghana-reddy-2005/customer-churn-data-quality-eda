import os
import pandas as pd
import plotly.express as px
import streamlit as st

# 1. Page Config
st.set_page_config(page_title="Business KPI Dashboard", page_icon="📊", layout="wide")

# 2. Dynamic Data Loader
@st.cache_data
def load_data():
    src_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(src_dir)
    data_dir = os.path.join(project_root, "data")
    
    possible_names = ["customer_churn.csv", "Customer_Churn.csv", "dataset.csv"]
    file_path = None

    if os.path.exists(data_dir):
        files_in_data = os.listdir(data_dir)
        for name in possible_names:
            if name in files_in_data:
                file_path = os.path.join(data_dir, name)
                break
        if not file_path:
            csv_files = [f for f in files_in_data if f.endswith(".csv")]
            if csv_files:
                file_path = os.path.join(data_dir, csv_files[0])

    if not file_path or not os.path.exists(file_path):
        st.error("❌ Could not locate dataset in `data/` folder.")
        st.stop()

    df = pd.read_csv(file_path)

    for col in ["TotalCharges", "MonthlyCharges", "tenure"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df

df = load_data()

# 3. UI Header
st.title("📊 Customer Churn & Revenue Risk Dashboard")
st.markdown("Decision-ready metrics for retention analysis and segment performance.")

# 4. Filters (Contract, Tenure, Payment Method)
st.sidebar.header("Filter Segment")

contract_options = list(df["Contract"].unique()) if "Contract" in df.columns else []
contract_filter = st.sidebar.multiselect("Contract Type", options=contract_options, default=contract_options)

payment_options = list(df["PaymentMethod"].unique()) if "PaymentMethod" in df.columns else []
payment_filter = st.sidebar.multiselect("Payment Method", options=payment_options, default=payment_options)

if "tenure" in df.columns:
    min_t, max_t = int(df["tenure"].min()), int(df["tenure"].max())
    tenure_range = st.sidebar.slider("Tenure (Months)", min_value=min_t, max_value=max_t, value=(min_t, max_t))
else:
    tenure_range = (0, 0)

filtered_df = df.copy()
if contract_filter:
    filtered_df = filtered_df[filtered_df["Contract"].isin(contract_filter)]
if payment_filter:
    filtered_df = filtered_df[filtered_df["PaymentMethod"].isin(payment_filter)]
if "tenure" in df.columns:
    filtered_df = filtered_df[filtered_df["tenure"].between(tenure_range[0], tenure_range[1])]

# 5. KPI Calculations
total_customers = len(filtered_df)
churn_col = "Churn" if "Churn" in df.columns else None

if churn_col:
    churned_df = filtered_df[filtered_df[churn_col] == "Yes"]
    churned_count = len(churned_df)
    churn_rate = (churned_count / total_customers * 100) if total_customers > 0 else 0.0
    retention_rate = 100.0 - churn_rate
    rev_at_risk = churned_df["MonthlyCharges"].sum() if "MonthlyCharges" in churned_df.columns else 0.0
else:
    churn_rate, retention_rate, rev_at_risk = 0.0, 100.0, 0.0

avg_tenure = filtered_df["tenure"].mean() if ("tenure" in filtered_df.columns and total_customers > 0) else 0.0

# Display Cards
c1, c2, c3, c4 = st.columns(4)
c1.metric("Churn Rate", f"{churn_rate:.1f}%")
c2.metric("Retention Rate", f"{retention_rate:.1f}%")
c3.metric("Revenue at Risk", f"${rev_at_risk:,.2f}")
c4.metric("Avg Tenure", f"{avg_tenure:.1f} mos")

st.divider()

# 6. Charts
col_l, col_r = st.columns(2)

with col_l:
    st.subheader("Churn Count by Contract Type")
    if "Contract" in filtered_df.columns and churn_col:
        c_churn = filtered_df.groupby(["Contract", churn_col]).size().reset_index(name="Count")
        fig1 = px.bar(
            c_churn, x="Contract", y="Count", color=churn_col, barmode="group",
            color_discrete_map={"Yes": "#D95F02", "No": "#7570B3"},
            labels={"Count": "Number of Customers"}
        )
        st.plotly_chart(fig1, use_container_width="stretch")

with col_r:
    st.subheader("Revenue at Risk by Payment Method")
    if "PaymentMethod" in filtered_df.columns and churn_col and "MonthlyCharges" in filtered_df.columns:
        p_risk = filtered_df[filtered_df[churn_col] == "Yes"].groupby("PaymentMethod")["MonthlyCharges"].sum().reset_index()
        fig2 = px.pie(p_risk, names="PaymentMethod", values="MonthlyCharges", hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig2, use_container_width="stretch")

if "tenure" in filtered_df.columns and churn_col:
    st.subheader("Tenure Distribution by Churn Status")
    fig3 = px.box(filtered_df, x=churn_col, y="tenure", color=churn_col, color_discrete_map={"Yes": "#D95F02", "No": "#7570B3"})
    st.plotly_chart(fig3, use_container_width="stretch")