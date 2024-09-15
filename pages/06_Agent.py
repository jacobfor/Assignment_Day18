import requests
import streamlit as st
import os

# OpenAI API 키를 사용자가 입력할 수 있도록 설정
st.sidebar.title("OpenAI API Key 설정")
api_key = st.sidebar.text_input("Enter your OpenAI API key:", type="password")

# OpenAI API 키가 없으면 실행 중지
if not api_key:
    st.warning("OpenAI API 키를 입력하세요.")
    st.stop()

# OpenAI API 키 설정
openai_api_key = api_key
headers = {
    "Authorization": f"Bearer {openai_api_key}",
    "Content-Type": "application/json"
}

# OpenAI Assistant ID 설정 (OpenAI 플랫폼에서 얻은 Assistant ID 입력)
assistant_id = "asst_MI7opfY5pXGMsTWj1o8mcHVP"

# 스레드 생성 함수
def create_thread():
    url = f"https://api.openai.com/v1/assistants/{assistant_id}/threads"
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        thread_data = response.json()
        thread_id = thread_data['id']
        return thread_id
    else:
        st.error(f"Failed to create thread: {response.status_code} - {response.text}")
        return None

# 스레드 실행 함수
def run_thread(thread_id, user_input):
    url = f"https://api.openai.com/v1/assistants/{assistant_id}/threads/{thread_id}/runs"
    payload = {
        "messages": [
            {"role": "system", "content": "You are an assistant that helps with various research tasks."},
            {"role": "user", "content": user_input}
        ]
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        run_data = response.json()
        return run_data['choices'][0]['message']['content']
    else:
        st.error(f"Failed to run thread: {response.status_code} - {response.text}")
        return None

# Streamlit으로 대화형 인터페이스 구현
st.title("OpenAI Thread-based Assistant Interface")

# 사용자로부터 프롬프트 입력 받기
user_input = st.text_input("Enter your question:")

# 스레드 관리
thread_id = st.session_state.get('thread_id', None)

if user_input:
    # 스레드가 없으면 새 스레드 생성
    if not thread_id:
        thread_id = create_thread()
        st.session_state['thread_id'] = thread_id

    # 스레드가 생성되면 사용자 입력을 실행
    if thread_id:
        assistant_response = run_thread(thread_id, user_input)
        if assistant_response:
            st.write(f"Assistant: {assistant_response}")

    # 응답을 파일에 저장하는 옵션 제공
    if st.button("Save response to file"):
        filename = "assistant_response.txt"
        with open(filename, "w") as file:
            file.write(assistant_response)
        st.success(f"Response saved to {filename}")
