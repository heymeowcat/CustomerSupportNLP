import streamlit as st
import requests

FLASK_API_URL = "http://127.0.0.1:5000/chat"

st.title("Troubleshooting Bot")

if 'conversation' not in st.session_state:
    st.session_state.conversation = []

def send_message_to_bot(message):
    response = requests.post(FLASK_API_URL, json={'message': message})
    if response.status_code == 200:
        return response.json()['response']
    else:
        return "Something went wrong. Please try again."

def display_chat():
    st.write("### Chat History:")
    for message in st.session_state.conversation:
        st.write(f"**You**: {message['user']}")
        st.write(f"**Bot**: {message['bot']}")


user_input = st.text_input("Ask your troubleshooting question:")


if st.button("Send"):
    if user_input:
        bot_response = send_message_to_bot(user_input)
        st.session_state.conversation.append({'user': user_input, 'bot': bot_response})
        user_input = "" 

display_chat()
