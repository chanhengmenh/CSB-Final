import pandas as pd
import PyPDF2
import json
from io import StringIO
from docx import Document
import streamlit as st
import requests

# DeepInfra API Key and Model Configuration
DEEPINFRA_API_KEY = "Lf1O4AUrODmQ1ihQ3KmmPBiL6HDLt45t"
MODEL_NAME = "meta-llama/Meta-Llama-3.1-405B-Instruct"

# Function to format the conversation for the API request
def format_conversation():
    """
    Formats the conversation history into a clear, readable format for context.
    Includes user-provided context for a more personalized experience.
    """
    conversation = ""

    # Add any saved user context (preferences, definitions, etc.)
    if "user_context" in st.session_state:
        for key, value in st.session_state["user_context"].items():
            conversation += f"User Context - {key}: {value}\n"

    # Add the conversation history
    for message in st.session_state.messages:
        if message["role"] == "user":
            conversation += f"User: {message['content']}\n"
        elif message["role"] == "assistant":
            conversation += f"Bot: {message['content']}\n"
        else:
            conversation += f"System: {message['content']}\n"

    return conversation.strip()



def api_calling(prompt):
    """
    Sends a prompt to the API and returns a contextual response.
    """
    # Increase max_tokens for longer responses
    temperature = st.session_state.get('temperature', 1)  # Adjust as needed
    max_tokens = 1028

    headers = {
        "Authorization": f"Bearer {DEEPINFRA_API_KEY}",
        "Content-Type": "application/json"
    }

    system_message = """
    You are a helpful assistant capable of answering user questions in detail.
    Provide comprehensive, clear, and well-structured responses based on user input and any available context.
    """

    # Format the full input prompt
    conversation_history = format_conversation()
    formatted_input = f"{system_message}\n\n{conversation_history}\n\nUser: {prompt}\nBot:"

    data = {
        "input": formatted_input,
        "stop": ["User:", "Bot:"],
        "parameters": {
            "temperature": temperature,  
            "max_tokens": max_tokens,  
            "top_p": 0.9,              
            "frequency_penalty": 0.3,   
            "presence_penalty": 0.5     
        },
    }

    try:
        response = requests.post(
            f"https://api.deepinfra.com/v1/inference/{MODEL_NAME}",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        output = response.json()
        response_text = output["results"][0]["generated_text"].strip()
        return response_text
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"



# Save chat history to a file
def save_chat_history():
    if st.button("Save Chat History", key="save_chat_button"):
        with open("chat_history.txt", "w") as file:
            for message in st.session_state.messages:
                file.write(f"{message['role'].capitalize()}: {message['content']}\n")
        st.success("Chat history saved!")

# Load chat history from a file
def load_chat_history():
    if st.button("Load Chat History", key="load_chat_button"):
        try:
            with open("chat_history.txt", "r") as file:
                st.session_state.messages = [
                    {"role": line.split(":")[0].strip().lower(), "content": ":".join(line.split(":")[1:]).strip()}
                    for line in file.readlines()
                ]
            st.success("Chat history loaded!")
        except FileNotFoundError:
            st.error("No saved chat history found.")



def dynamic_response_tuning():
    st.sidebar.title("Response Tuning")

    # Allow multiple file uploads (up to 5 files)
    uploaded_files = st.sidebar.file_uploader(
        "Upload your files here!",
        type=["csv", "txt", "pdf", "docx", "json", "xlsx", "py", "java", "cpp", "c", "js", "html", "css"],
        accept_multiple_files=True,
        key="file_uploader"
    )

    # Check if more than 5 files are uploaded
    if len(uploaded_files) > 5:
        st.sidebar.warning("You can only upload up to 5 files.")

    # If files are uploaded, process them and store their content in session state
    if uploaded_files:
        if "file_contents" not in st.session_state:
            st.session_state["file_contents"] = {}  # Initialize if not already initialized

        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            file_content = process_uploaded_file(uploaded_file)

            if file_content:
                st.session_state["file_contents"][file_name] = file_content
                st.sidebar.success(f"File '{file_name}' uploaded and processed successfully!")
            else:
                st.sidebar.error(f"Failed to process the file '{file_name}'.")
    else:
        st.sidebar.warning("No files uploaded yet.")




def process_uploaded_file(uploaded_file):
    """
    Processes the uploaded file based on its type and extracts relevant content.
    """
    try:
        file_type = uploaded_file.name.split(".")[-1].lower()

        if file_type == "csv":
            df = pd.read_csv(uploaded_file)
            return df.to_string()
        
        elif file_type == "xlsx":
            df = pd.read_excel(uploaded_file)
            return df.to_string()
        
        elif file_type == "txt":
            return uploaded_file.read().decode("utf-8")
        
        elif file_type == "pdf":
            reader = PyPDF2.PdfReader(uploaded_file)
            text = "".join([page.extract_text() for page in reader.pages])
            return text
        
        elif file_type == "docx":
            doc = Document(uploaded_file)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        
        elif file_type == "json":
            data = json.load(uploaded_file)
            return json.dumps(data, indent=2)
        
        elif file_type in {"py", "java", "cpp", "c", "js", "html", "css"}:
            return uploaded_file.read().decode("utf-8")
        
        else:
            return None
    except Exception as e:
        return f"Error processing file: {e}"
