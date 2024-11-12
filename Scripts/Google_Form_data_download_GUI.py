import pandas as pd
import streamlit as st
import requests
from io import StringIO  # Import StringIO directly from the io module
from io import BytesIO
from datetime import datetime
import gspread
import json
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy import create_engine, text
from openpyxl.workbook import Workbook


# Display the PNG image in the top centre of the Streamlit sidebar with custom dimensions
image_path = 'https://twetkfnfqdtsozephdse.supabase.co/storage/v1/object/sign/stemcheck/VS-logo.png?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1cmwiOiJzdGVtY2hlY2svVlMtbG9nby5wbmciLCJpYXQiOjE3MjE5NzA3ODUsImV4cCI6MTc1MzUwNjc4NX0.purLZOGk272W80A4OlvnavqVB9u-yExhzpmI3dZrjdM&t=2024-07-26T05%3A13%3A02.704Z'
st.markdown(
    f'<div style="text-align:center"><img src="{image_path}" width="150"></div>',
    unsafe_allow_html=True
)
#Display the title of the Google form
st.markdown(
    "<h1 style='color: black; font-weight: bold;'>Google Form Data Download GUI</h1>", 
    unsafe_allow_html=True
)

Form_name=st.radio('Choose the Google form GUI you want to access data',('Mentor Recruitment','Career Recruitment'))

combined_button_text = "Download"

# Define your AWS RDS database connection settings
username = st.secrets['DB_USERNAME']
password = st.secrets['DB_PASSWORD']
host = st.secrets['DB_ENDPOINT']
port = st.secrets['DB_PORT']  # Replace with your MySQL port if different
database_name = st.secrets['DB_NAME']


# Create the connection string for the AWS RDS MySQL database using the create_engine function
connection_string = f"mysql+mysqlconnector://{username}:{password}@{host}:{port}/{database_name}"
engine = create_engine(connection_string)

# Button to download data
if st.button(combined_button_text):
    if Form_name == 'Career Recruitment':
        # SQL query to retrieve data for Career Recruitment
        sql_query = "SELECT * FROM Career_Recruitment"
        
        # Read data into a DataFrame
        df = pd.read_sql(sql_query, con=engine)
        
        # Display the DataFrame in the Streamlit app
        st.write(df)
        
        # Save the data to a Google sheet.
        df.to_excel(r"C:\Users\User\Downloads\Career_rec.xlsx")
        st.success("Career Recruitment data saved successfully in Career ")

    elif Form_name == 'Mentor Recruitment':
        # SQL query to retrieve data for Mentor Recruitment
        sql_query = "SELECT * FROM Mentor_Recruitment"
        
        # Read data into a DataFrame
        df = pd.read_sql(sql_query, con=engine)
        
        # Display the DataFrame in the Streamlit app
        st.write(df)
        
        # Save the data to a google sheet.
        df.to_excel(r"C:\Users\User\Downloads\Mentor data file.xlsx")
        st.success("Mentor Recruitment data saved successfully in Mentor data file.")

