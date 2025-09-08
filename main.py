import streamlit as st
import pandas as pd
import argparse
import os

from usingTenSEAL_FHE import fetch_data, setup_tenseal
from checkFile import load_numeric_columns, build_ckks_context, encrypt_columns, multiply_and_decrypt

st.set_page_config(page_title="HELIX: Homomorphic Encryption for Logic, Insight and eXploration", layout="wide")
st.title("HELIX: Homomorphic Encryption for Logic, Insight and eXploration")

#Upload textbox with button Upload
uploaded_file = st.file_uploader("Upload Document in CSV format", type=["csv"])

#Read and process the uploaded document
if uploaded_file:
    st.info("Uploaded the file")
    df = pd.read_csv(uploaded_file)
    # Display the first few rows
    st.write("### Preview of DataFrame")
    st.dataframe(df.head())
    #extract float values only
    df_amount_precision = df[['Amount','Precision']]
    vector = fetch_data(df_amount_precision)
    setup_tenseal(vector)
