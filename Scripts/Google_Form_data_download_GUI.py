import pandas as pd
import streamlit as st
import requests
from io import StringIO
from io import BytesIO
from datetime import datetime
import gspread
import json
from sqlalchemy import create_engine
from google.oauth2 import service_account

# Display the PNG image in the top center of the Streamlit sidebar
image_path = 'https://twetkfnfqdtsozephdse.supabase.co/storage/v1/object/sign/stemcheck/VS-logo.png?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1cmwiOiJzdGVtY2hlY2svVlMtbG9nby5wbmciLCJpYXQiOjE3MjE5NzA3ODUsImV4cCI6MTc1MzUwNjc4NX0.purLZOGk272W80A4OlvnavqVB9u-yExhzpmI3dZrjdM&t=2024-07-26T05%3A13%3A02.704Z'
st.markdown(
    f'<div style="text-align:center"><img src="{image_path}" width="150"></div>',
    unsafe_allow_html=True
)

# Display the title of the Google Form
st.markdown(
    "<h1 style='color: black; font-weight: bold;'>Google Form Data Download GUI</h1>",
    unsafe_allow_html=True
)

# Radio button to select the form
Form_name = st.radio('Choose the Google Form GUI you want to access data', ('Mentor Recruitment', 'Career Recruitment'))

# Define your AWS RDS database connection settings
username = st.secrets['DB_USERNAME']
password = st.secrets['DB_PASSWORD']
host = st.secrets['DB_ENDPOINT']
port = st.secrets['DB_PORT']
database_name = st.secrets['DB_NAME']
Career_sheet_url = st.secrets['SH_CARLINK']
Mentor_sheet_url = st.secrets['SH_MENLINK']

# Create the connection string for the AWS RDS MySQL database
connection_string = f"mysql+mysqlconnector://{username}:{password}@{host}:{port}/{database_name}"
engine = create_engine(connection_string)

# Button to download data
if st.button("Download"):
    # Determine the correct table and sheet based on the selected form
    if Form_name == 'Career Recruitment':
        sql_query = "SELECT * FROM Career_Recruitment"
        sheet_key = st.secrets['SH_CARID']
        sheet_url = Career_sheet_url
        LinkedIn_column = 'Enter your LinkedIn profile link here'
    elif Form_name == 'Mentor Recruitment':
        sql_query = "SELECT * FROM Mentor_Recruitment"
        sheet_key = st.secrets['SH_MENID']
        sheet_url = Mentor_sheet_url
        LinkedIn_column = 'ID'

    # Read data from the database
    df = pd.read_sql(sql_query, con=engine)
    df1 = pd.DataFrame(df)

    # Fetch service account credentials from Supabase storage
    supabase_credentials_url = "https://twetkfnfqdtsozephdse.supabase.co/storage/v1/object/sign/stemcheck/studied-indexer-431906-h1-e3634918ab42.json?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1cmwiOiJzdGVtY2hlY2svc3R1ZGllZC1pbmRleGVyLTQzMTkwNi1oMS1lMzYzNDkxOGFiNDIuanNvbiIsImlhdCI6MTcyNjkwMzEzNywiZXhwIjoxNzU4NDM5MTM3fQ.d-YWFIIV3ue7eUwUIemVHKrxVSgsdy3Dm34bCfkKBPE&t=2024-09-21T07%3A18%3A57.318Z"
    response = requests.get(supabase_credentials_url)

    if response.status_code == 200:
        # Decode the response content
        service_account_info = response.json()

        # Create credentials and authorize client
        creds = service_account.Credentials.from_service_account_info(
            service_account_info, scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        client = gspread.authorize(creds)

        # Open the correct Google Sheet
        sheet = client.open_by_key(sheet_key).sheet1

        # Get existing records from the sheet
        existing_records = sheet.get_all_values()

        # Extract the header from the first row
        existing_headers = existing_records[0]

        # Convert existing records to DataFrame (skip headers)
        existing_df = pd.DataFrame(existing_records[1:], columns=existing_headers)

        if LinkedIn_column not in df1.columns:
            st.error(f"{LinkedIn_column} column is missing in the new data.")
        else:
            # Extract the unique identifier column from the existing records
            existing_ids = existing_df[LinkedIn_column].tolist() if LinkedIn_column in existing_df.columns else []

            # Filter rows where the unique identifier is not in existing records
            new_entries = df1[~df1[LinkedIn_column].isin(existing_ids)]

            if not new_entries.empty:
                # Append only new rows to the sheet
                rows_to_append = new_entries.values.tolist()
                for row in rows_to_append:
                    sheet.append_row(row)
                st.success(f"{len(rows_to_append)} new entries added to the sheet.")
            else:
                st.info("No new entries to add.")

        # Sort the DataFrame in descending order and add serial numbers
        df2 = df1[::-1].reset_index(drop=True)
        df2.insert(0, "Sr No", range(len(df2), 0, -1))

        # Display the updated DataFrame in Streamlit
        st.write("Recent Entries")
        st.write(df2)
        st.write(f"[Open Google Sheet]({sheet_url})")
