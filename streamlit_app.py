import streamlit as st
import pandas as pd

# Title of the app
st.title("Freight Rate Discrepancy Checker")

# Load the Excel file
@st.cache_data
def load_data():
    # Ensure the file path matches your repository structure
    df = pd.read_excel("zzEcopax - Q3 Analysis.xlsx", engine="openpyxl")
    return df

# Display the Excel file's contents
st.write("Reading data from 'zzEcopax - Q3 Analysis.xlsx':")
data = load_data()

# Show the first few rows of the Excel file
st.write(data.head())

# Optionally, allow the user to select a column to view specific data
if st.checkbox('Show column details'):
    column = st.selectbox('Select a column', data.columns)
    st.write(data[column])
