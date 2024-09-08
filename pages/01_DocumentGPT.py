from langchain.prompts import PromptTemplate
from langchain.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings, CacheBackedEmbeddings
from langchain.vectorstores.faiss import FAISS
from langchain.chains import RetrievalQA, StuffDocumentsChain, LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.storage import LocalFileStore
import streamlit as st
import faiss
import os

# Streamlit page configuration
st.set_page_config(
    page_title="DocumentGPT RAG",
    page_icon="📜",
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Sidebar UI Components
with st.sidebar:
    openai_api_key = st.text_input("Enter your OpenAI API Key:")
    file = st.file_uploader("Upload a .txt .pdf or .docx file", type=["pdf", "txt", "docx"])
    st.markdown("[GitHub Repository](https://github.com/your-repo)")

# Set up the language model with the user's API key
llm = ChatOpenAI(api_key=openai_api_key)

# Set up cache directory
cache_dir = LocalFileStore("./.cache/")

# Embed and index documents from uploaded file
@st.cache_data(show_spinner="Embedding file...")
def setup_chain(file):
    file_path = f"./.cache/files/{file.name}"
    with open(file_path, "wb") as f:
        f.write(file.getvalue())
    splitter = CharacterTextSplitter.from_tiktoken_encoder(
        separator="\n",
        chunk_size=600,
        chunk_overlap=100,
    )
    loader = UnstructuredFileLoader(file_path)
    docs = loader.load_and_split(text_splitter=splitter)
    embeddings = OpenAIEmbeddings()
    cached_embeddings = CacheBackedEmbeddings.from_bytes_store(embeddings, cache_dir)
    vectorstore = FAISS.from_documents(docs, cached_embeddings)
    faiss.write_index(vectorstore.index, f"./.cache/faiss_index_{file.name}")
    retriever = vectorstore.as_retriever()
    memory = ConversationBufferMemory()
    prompt_template = PromptTemplate(
        input_variables=["context"],
        template="Using the context below, answer the following question: {context}"
    )
    llm_chain = LLMChain(llm=llm, prompt=prompt_template)
    combine_documents_chain = StuffDocumentsChain(llm_chain=llm_chain)
    return RetrievalQA(combine_documents_chain=combine_documents_chain, retriever=retriever, memory=memory)

# UI interaction for handling messages
def send_message(message, role, save=True):
    with st.chat_message(role):
        st.markdown(message)
    if save:
        st.session_state["messages"].append({"message": message, "role": role})


def paint_history():
    for message in st.session_state["messages"]:
        send_message(message["message"], message["role"], save=False)

# Main application logic
if file and openai_api_key:
    chain = setup_chain(file)
    send_message("I'm ready! Ask away!", "ai", save=False)
    paint_history()
    message = st.chat_input("Ask anything about your file...")
    if message:
        send_message(message, "human")
        response = chain.run(message)
        send_message(f"Answer: {response}", "ai")
else:
    st.write("Please upload a file and enter your OpenAI API Key.")
