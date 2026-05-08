import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="AWS Stock Pipeline", layout="wide")

st.title("📈 Real-Time Stock & Sensor Data Pipeline")

st.markdown("AWS-based real-time streaming and anomaly detection dashboard")

# Load sample output
with open("output.json", "r") as f:
    data = json.load(f)

# Handle single JSON object
if isinstance(data, dict):
    df = pd.DataFrame([data])
else:
    df = pd.DataFrame(data)
st.subheader("Incoming Data")
st.dataframe(df)

# Show metrics
if "price" in df.columns:
    st.line_chart(df["price"])

if "anomaly" in df.columns:
    anomalies = df[df["anomaly"] == True]
    st.subheader("⚠️ Detected Anomalies")
    st.dataframe(anomalies)
