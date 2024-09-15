import streamlit as st
import openai
from openai import OpenAI
import time

# Function to create the assistant
def create_assistant():
    assistant = client.beta.assistants.create(
        name="Wikipedia Search Assistant",
        description="You are an assistant that searches Wikipedia and provides relevant information.",
        model="gpt-4-1106-preview",
        tools=[{"type": "file_search"}]  # Updated to use a supported tool type
    )
    return assistant.id

# Function to initialize OpenAI client with user API key
def initialize_openai(api_key):
    openai.api_key = api_key
    return OpenAI()

# Function to search Wikipedia using the assistant
def search_wikipedia(assistant_id, query):
    thread = client.beta.threads.create()
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=query
    )
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id
    )
    
    # Polling for the assistant's response
    run_status = get_run(run.id, thread.id)
    while run_status.status != 'completed':
        time.sleep(1)
        run_status = get_run(run.id, thread.id)
    
    return get_messages(thread.id)

# Function to get the result of a run
def get_run(run_id, thread_id):
    return client.beta.threads.runs.retrieve(
        run_id=run_id,
        thread_id=thread_id,
    )

# Function to get all messages in a thread
def get_messages(thread_id):
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    messages = list(messages)
    messages.reverse()  # Ensures most recent messages are displayed last
    return messages

# Streamlit UI
st.title("Wikipedia Search Assistant")

# 사용자로부터 OpenAI API 키 입력 받기
if "api_key_check" not in st.session_state:
    st.session_state["api_key_check"] = False

api_key = st.sidebar.text_input("Enter your OpenAI API Key:", type="password")

# API 키가 입력되지 않았을 때 렌더링 중단
if not api_key and not st.session_state["api_key_check"]:
    st.warning("Please enter your OpenAI API key in the sidebar.")
    st.stop()

# API 키가 입력된 경우
if api_key:
    st.session_state["api_key_check"] = True
    client = initialize_openai(api_key)
    assistant_id = create_assistant()

    query = st.text_input("Enter your Wikipedia search query:")
    
    if st.button("Search"):
        if query:
            with st.spinner("Searching..."):
                messages = search_wikipedia(assistant_id, query)
                st.write("### Conversation History:")
                for message in messages:
                    st.write(f"**{message.role}:** {message.content[0].text.value}")
        else:
            st.error("Please enter a search query.")
