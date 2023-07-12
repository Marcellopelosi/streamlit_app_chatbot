import streamlit as st
from Model import answer

# https://discuss.streamlit.io/t/1-st-button-delete-result-of-2-nd-button/33280/2
if 'log' not in st.session_state:
    st.session_state.log = []

st.title("Chatbot")

user_input = st.text_input("Ask here:")

if st.button("Send"):
    response = answer(user_input)
    styled_user_input = f'<p style="color:green; text-align:right;">{user_input}</p>'

    # Some conditional or callback function process will add to the log
    st.session_state.log.append(styled_user_input)
    st.session_state.log.append(response)

    for i, msg in enumerate(st.session_state.log):
        if i%2 == 0:
            st.markdown(msg, unsafe_allow_html=True)
        else:
            st.text(msg)

if st.button("Clear chat"):
    st.session_state.log = []
