import streamlit as st
import pandas as pd
import json

st.set_page_config(
    page_title="AWS Stock Pipeline",
    layout="wide"
)

st.title("📈 Real-Time Stock & Sensor Data Pipeline")
st.markdown("AWS-based real-time streaming and anomaly detection dashboard")

# Load JSON data
try:
    with open("output.json", "r") as f:
        data = json.load(f)

    st.subheader("Raw JSON Data")
    st.json(data)

    # Convert to DataFrame
    if isinstance(data, dict):
        df = pd.DataFrame([data])
    else:
        df = pd.DataFrame(data)

    st.subheader("Incoming Data")
    st.dataframe(df)

    # Metrics
    st.subheader("Dataset Info")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Rows", df.shape[0])

    with col2:
        st.metric("Columns", df.shape[1])

    # Auto chart numeric columns
    numeric_cols = df.select_dtypes(include=["number"]).columns

    if len(numeric_cols) > 0:
        st.subheader("📊 Numeric Trends")
        st.line_chart(df[numeric_cols])

    # Detect anomalies if column exists
    if "anomaly" in df.columns:
        anomalies = df[df["anomaly"] == True]

        st.subheader("⚠️ Detected Anomalies")

        if len(anomalies) > 0:
            st.dataframe(anomalies)
        else:
            st.success("No anomalies detected")

except Exception as e:
    st.error(f"Error loading data: {e}")