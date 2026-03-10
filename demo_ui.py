import streamlit as st
import pandas as pd

st.title("Amazon Review Sentiment Analyzer")

uploaded_file = st.file_uploader(
    "Upload CSV file",
    type=["csv"]
)

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)

    st.success("File uploaded successfully!")

    st.write("Total Rows:", len(df))
    st.write("Total Columns:", len(df.columns))

    st.subheader("Preview Data")

    num_rows = st.slider("Select rows to preview", 5, 100, 10)

    st.dataframe(df.head(num_rows))