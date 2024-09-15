import streamlit as st
import openai
import time

# Function to initialize OpenAI client with user API key
def initialize_openai(api_key):
    openai.api_key = api_key  # Set the API key using openai module

# Function to search Wikipedia using ChatCompletion
def search_wikipedia(query):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # gpt-4를 원하면 "gpt-4"로 변경
            messages=[
                {"role": "system", "content": "You are a helpful assistant that searches Wikipedia and provides relevant information."},
                {"role": "user", "content": f"Search Wikipedia for information about {query}."}
            ]
        )
        return response['choices'][0]['message']['content']
    except openai.error.OpenAIError as e:
        return f"Error: {str(e)}"

# Streamlit UI
st.title("Wikipedia Search Assistant")

# 세션 상태에서 API 키가 입력되었는지 확인
if "api_key_check" not in st.session_state:
    st.session_state["api_key_check"] = False
    st.session_state["api_key"] = ""

# 사이드바에서 사용자로부터 OpenAI API 키 입력 받기
api_key = st.sidebar.text_input("Enter your OpenAI API Key:", type="password")

# API 키가 입력되지 않으면 경고하고 렌더링 중단
if not api_key and not st.session_state["api_key_check"]:
    st.warning("Please enter your OpenAI API key in the sidebar.")
    st.stop()

# API 키가 입력되었을 경우 세션에 저장하고, 클라이언트 초기화
if api_key:
    st.session_state["api_key_check"] = True
    st.session_state["api_key"] = api_key
    initialize_openai(api_key)

# Wikipedia 검색 쿼리 입력 받기
query = st.text_input("Enter your Wikipedia search query:")

# 검색 버튼 클릭 시 Wikipedia 검색 수행
if st.button("Search"):
    if query:
        with st.spinner("Searching..."):
            response = search_wikipedia(query)
            st.write("### Conversation History:")
            st.write(f"**user:** {query}")
            st.write(f"**assistant:** {response}")
    else:
        st.error("Please enter a search query.")
