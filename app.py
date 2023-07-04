import streamlit as st
from Model import model

def main():
    st.title("Chatbot")
    
    user_input = st.text_input("User Input")
    
    if st.button("Send"):
        response = model(user_input)
        st.text(response)
