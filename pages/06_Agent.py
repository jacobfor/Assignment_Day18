import os
import requests
import streamlit as st
from typing import Type
from langchain.chat_models import ChatOpenAI
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from langchain.utilities import DuckDuckGoSearchAPIWrapper, WikipediaAPIWrapper
from bs4 import BeautifulSoup

# OpenAI API 키를 사용자가 입력할 수 있도록 설정
st.sidebar.title("OpenAI API Key 설정")
api_key = st.sidebar.text_input("Enter your OpenAI API key:", type="password")

# OpenAI API 키가 없으면 실행 중지
if not api_key:
    st.warning("OpenAI API 키를 입력하세요.")
    st.stop()

# OpenAI API 키 설정
os.environ["OPENAI_API_KEY"] = api_key

# OpenAI 언어 모델 초기화
llm = ChatOpenAI(temperature=0.1, model_name="gpt-3.5-turbo-1106", openai_api_key=api_key)

# Wikipedia 검색 도구
class WikipediaSearchToolArgsSchema(BaseModel):
    query: str = Field(description="Wikipedia에 대한 검색 쿼리. 예: '양자 물리학'")

class WikipediaSearchTool(BaseTool):
    name = "WikipediaSearch"
    description = "주어진 쿼리와 관련된 정보를 Wikipedia에서 검색합니다."
    
    args_schema: Type[WikipediaSearchToolArgsSchema] = WikipediaSearchToolArgsSchema

    def _run(self, query):
        wiki = WikipediaAPIWrapper()
        return wiki.run(query)

# DuckDuckGo 검색 도구
class DuckDuckGoSearchToolArgsSchema(BaseModel):
    query: str = Field(description="DuckDuckGo에서 검색할 쿼리입니다.")

class DuckDuckGoSearchTool(BaseTool):
    name = "DuckDuckGoSearch"
    description = "DuckDuckGo에서 정보를 검색합니다."
    
    args_schema: Type[DuckDuckGoSearchToolArgsSchema] = DuckDuckGoSearchToolArgsSchema

    def _run(self, query):
        ddg = DuckDuckGoSearchAPIWrapper()
        return ddg.run(query)

# 웹 스크래핑 도구
class WebScrapeArgsSchema(BaseModel):
    url: str = Field(description="텍스트를 스크랩할 웹사이트의 URL입니다.")

class WebScrapeTool(BaseTool):
    name = "WebScrape"
    description = "주어진 URL에서 텍스트를 스크랩하고 추출합니다."
    
    args_schema: Type[WebScrapeArgsSchema] = WebScrapeArgsSchema

    def _run(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        content = '\n'.join([p.get_text() for p in paragraphs])
        return content

# 연구 결과를 .txt 파일에 저장하는 도구
class SaveToTextFileArgsSchema(BaseModel):
    content: str = Field(description="저장할 내용.")
    filename: str = Field(default="research_output.txt", description="연구 결과를 저장할 파일 이름.")

class SaveToTextFileTool(BaseTool):
    name = "SaveToTextFile"
    description = ".txt 파일에 연구 결과를 저장합니다."
    
    args_schema: Type[SaveToTextFileArgsSchema] = SaveToTextFileArgsSchema

    def _run(self, content, filename):
        with open(filename, 'w') as f:
            f.write(content)
        return f"연구 내용이 {filename}에 저장되었습니다."

# Streamlit으로 대화형 인터페이스 구현
st.title("OpenAI Investor Assistant")

# 사용자로부터 프롬프트 입력 받기
user_input = st.text_input("Enter your question:")

# 도구 리스트 정의
tools = [WikipediaSearchTool(), DuckDuckGoSearchTool(), WebScrapeTool(), SaveToTextFileTool()]

# 사용자의 질문에 대한 응답 생성
if user_input:
    response = llm({"role": "user", "content": user_input})
    
    # 대화 기록 출력
    st.write("### Assistant Response:")
    st.write(response)

    # 로그를 파일에 저장하기 위한 옵션
    if st.button("Save response to file"):
        filename = "response.txt"
        with open(filename, "w") as file:
            file.write(response)
        st.success(f"Response saved to {filename}")
