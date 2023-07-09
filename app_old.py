import streamlit as st
from Model import model
from langchain.memory import ConversationBufferWindowMemory

# https://discuss.streamlit.io/t/1-st-button-delete-result-of-2-nd-button/33280/2
if 'log' not in st.session_state:
    st.session_state.log = []

if 'buffer_memory' not in st.session_state:
            st.session_state.buffer_memory=ConversationBufferWindowMemory(k=3,return_messages=True)


st.title("Chatbot")

user_input = st.text_input("Ask here:")

if st.button("Send"):
    response = model(user_input, memory = st.session_state.buffer_memory)
    styled_user_input = f'<p style="color:green; text-align:right;">{user_input}</p>'

    # Some conditional or callback function process will add to the log
    st.session_state.log.append(styled_user_input)
    st.session_state.log.append(response)
    memory = st.session_state.buffer_memory
    memory.save_context({"input": user_input}, {"output": response})
    st.session_state.buffer_memory = memory
    

    for i, msg in enumerate(st.session_state.log):
        if i%2 == 0:
            st.markdown(msg, unsafe_allow_html=True)
        else:
            st.text(msg)

if st.button("Clear chat"):
    st.session_state.log = []
    st.session_state.buffer_memory = ConversationBufferWindowMemory(k=3,return_messages=True)
