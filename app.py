import streamlit as st
from Model import model


st.title("Chatbot")

user_input = st.text_input("Ask here:")

if st.button("Send"):
    response = model(user_input)
    styled_user_input = f'<p style="color:green; text-align:right;">{user_input}</p>'
    st.markdown(styled_user_input, unsafe_allow_html=True)
    st.text(response)
