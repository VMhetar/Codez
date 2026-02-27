import streamlit as st
import requests

st.title('AI agent')

instruction = st.text_input('Enter change request: ')

if st.button("Generate PR"):
    response = requests.post(
        "http://localhost:8000/run_agent",
        json={"instruction":instruction}
    )
    st.write(response.json())