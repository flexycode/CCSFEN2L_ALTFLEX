import streamlit as st

st.set_page_config(page_title="AltFlex Dashboard", layout="wide")

st.title("AltFlex: AI & Digital Forensics Framework")

st.sidebar.header("Navigation")
st.sidebar.info("Select a module to view analysis.")

st.markdown("""
## Welcome to AltFlex
This dashboard visualizes forensic analysis and anomaly detection results.
""")
