import os
import openai
import streamlit as st

# OpenAI API 키를 사용자가 입력할 수 있도록 설정
st.sidebar.title("OpenAI API Key 설정")
api_key = st.sidebar.text_input("Enter your OpenAI API key:", type="password")

# OpenAI API 키가 없으면 실행 중지
if not api_key:
    st.warning("OpenAI API 키를 입력하세요.")
    st.stop()

# OpenAI API 키 설정
openai.api_key = api_key

# Streamlit으로 대화형 인터페이스 구현
st.title("OpenAI Assistant Interface")

# 사용자로부터 프롬프트 입력 받기
user_input = st.text_input("Enter your question:")

# 대화 기록 저장을 위한 리스트
chat_history = []

# 사용자의 질문에 대한 응답 생성
if user_input:
    # ChatCompletion API와 상호작용
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  
        messages=[
            {"role": "system", "content": "You are an assistant that helps with various research tasks like Wikipedia search, DuckDuckGo search, and web scraping."},
            {"role": "user", "content": user_input}
        ]
    )
    
    # Assistant의 응답 가져오기
    assistant_response = response['choices'][0]['message']['content']
    
    # 대화 기록 추가
    chat_history.append({"user": user_input, "assistant": assistant_response})
    
    # 대화 기록 출력
    st.write("### Conversation:")
    for entry in chat_history:
        st.write(f"**User:** {entry['user']}")
        st.write(f"**Assistant:** {entry['assistant']}")
    
    # 응답을 파일로 저장하는 버튼
    if st.button("Save response to file"):
        filename = "assistant_response.txt"
        with open(filename, "w") as file:
            file.write(assistant_response)
        st.success(f"Response saved to {filename}")
