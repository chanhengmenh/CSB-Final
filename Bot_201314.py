import streamlit as st
from streamlit_chat import message
from functionality import api_calling, save_chat_history, load_chat_history, dynamic_response_tuning

# Streamlit App Title
st.title("💬 Bot-201314")

# Initialize session state for chat history if not already present
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! How can I assist you today?"}]

# Display chat history in Streamlit with unique keys
for i, chat in enumerate(st.session_state.messages):
    message(chat["content"], is_user=(chat["role"] == "user"), key=f"message_{i}")

# Input box for the user to ask questions
if prompt := st.chat_input("Type your message..."):
    with st.spinner("Thinking..."):
        response = api_calling(prompt)  # Call the function from functionality.py

    # Append user input and bot response to the chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.messages.append({"role": "assistant", "content": response})

    # Display chat messages
    message(prompt, is_user=True, key=f"message_user_{len(st.session_state.messages)-2}")
    message(response, is_user=False, key=f"message_assistant_{len(st.session_state.messages)-1}")

# Call additional functionalities
save_chat_history()  # Save chat history button
load_chat_history()  # Load chat history button
dynamic_response_tuning()  # Sidebar for file uploads and tuning




