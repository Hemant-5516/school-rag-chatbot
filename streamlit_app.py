import streamlit as st
from app.rag_chain import answer_question

st.set_page_config(page_title="RAG Chatbot", layout="centered")
st.title("RAG Chatbot for MySQL Database")

st.write("Ask any question about your school database!")

if 'messages' not in st.session_state:
    st.session_state['messages'] = []

user_input = st.text_input("You:", "", key="input")

if st.button("Send") and user_input:
    st.session_state['messages'].append(("user", user_input))
    with st.spinner("Thinking..."):
        response = answer_question(user_input)
    st.session_state['messages'].append(("bot", response))

for sender, msg in st.session_state['messages']:
    if sender == "user":
        st.markdown(f"**You:** {msg}")
    else:
        st.markdown(f"**Bot:** {msg}") 