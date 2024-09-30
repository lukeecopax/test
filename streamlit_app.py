import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader
from pdf2image import convert_from_path
import base64
import io
import pyfiglet
import openai

# Hardcoded OpenAI API Key (replace with your key)
openai.api_key = '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'

# Title of the app
st.title("Freight Rate Discrepancy Checker")

# Cache the loading of Excel file to prevent reloading every time the script runs
@st.cache_data
def load_excel(file):
    return pd.read_excel(file, sheet_name='Bid data', skiprows=5)

# Convert PDF first page to Base64 image for processing
def pdf_first_page_to_base64(pdf_file):
    images = convert_from_path(pdf_file, dpi=300, first_page=1, last_page=1)
    pil_image = images[0]
    buffered = io.BytesIO()
    pil_image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str

# Normalize extracted data
def normalize_extracted_data(extracted_data):
    # Implement the normalization logic here
    # Similar to your notebook's normalization function
    return extracted_data

# Function to process the PDF and extract data using OpenAI
def process_pdf(pdf_file, model="gpt-4"):
    base64_image = pdf_first_page_to_base64(pdf_file)
    
    response = openai.Completion.create(
        model=model,
        prompt=f"Extract relevant details from the attached image: {base64_image}",
        temperature=0.0,
        max_tokens=150
    )
    
    assistant_reply = response.choices[0].text
    extracted_data = parse_assistant_reply(assistant_reply)
    return normalize_extracted_data(extracted_data)

# Main function to process and compare data
def main():
    # Upload Excel file
    excel_file = st.file_uploader("Upload the 'zzEcopax - Q3 Analysis.xlsx' file", type=["xlsx"])
    
    # Upload PDF files
    pdf_files = st.file_uploader("Upload Invoice PDF files", type=["pdf"], accept_multiple_files=True)

    if excel_file and pdf_files:
        # Load the Excel data
        df_excel = load_excel(excel_file)
        df_excel = df_excel[['Broker Name', 'Origin City(S)', 'Destination City', 'Destination State', 'R2 Rate', 'Assign to']]
        df_excel = df_excel.applymap(lambda x: x.lower() if isinstance(x, str) else x)
        
        # Initialize summary
        total_processed = 0
        matched_rates = 0
        discrepancy_rates = 0
        
        for pdf_file in pdf_files:
            st.write(f"Processing {pdf_file.name}...")
            
            # Process the PDF
            normalized_data = process_pdf(pdf_file)

            # Perform your comparison logic with the Excel file
            broker_name = normalized_data.get('Broker Name')
            origin_city = normalized_data.get('Origin City(S)')
            destination_city = normalized_data.get('Destination City')
            destination_state = normalized_data.get('Destination State')
            
            # Filter Excel data for matches
            matching_rows = df_excel[
                (df_excel['Broker Name'] == broker_name) &
                (df_excel['Origin City(S)'] == origin_city) &
                (df_excel['Destination City'] == destination_city) &
                (df_excel['Destination State'] == destination_state)
            ]
            
            if not matching_rows.empty:
                r2_rate = matching_rows.iloc[0]['R2 Rate']
                rate_difference = float(normalized_data['Rate']) - r2_rate
                if rate_difference == 0:
                    matched_rates += 1
                else:
                    discrepancy_rates += 1
            total_processed += 1

        # Summary output
        st.write(f"Total PDFs processed: {total_processed}")
        st.write(f"Matched rates: {matched_rates}")
        st.write(f"Discrepancies: {discrepancy_rates}")

if __name__ == "__main__":
    main()
