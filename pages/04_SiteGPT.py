import requests
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.faiss import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import streamlit as st

# Sidebar input for OpenAI API key
with st.sidebar:
    openai_api_key = st.text_input("Enter your OpenAI API Key", type="password")
    if not openai_api_key:
        st.warning("Please enter your OpenAI API Key to proceed.")
        st.stop()

# Initialize the OpenAI LLM model using the user's API key
llm = ChatOpenAI(
    temperature=0.1,
    openai_api_key=openai_api_key
)

# Define the prompt template for answering questions based on context
answers_prompt = ChatPromptTemplate.from_template(
    """
    Using ONLY the following context answer the user's question. If you can't just say you don't know, don't make anything up.
                                                  
    Then, give a score to the answer between 0 and 5.

    If the answer answers the user question the score should be high, else it should be low.

    Make sure to always include the answer's score even if it's 0.

    Context: {context}
                                                  
    Examples:
                                                  
    Question: How far away is the moon?
    Answer: The moon is 384,400 km away.
    Score: 5
                                                  
    Question: How far away is the sun?
    Answer: I don't know
    Score: 0
                                                  
    Your turn!

    Question: {question}
"""
)

# Function to get answers based on the documents
def get_answers(docs, question):
    answers_chain = answers_prompt | llm
    answers = []
    for doc in docs:
        result = answers_chain.invoke(
            {"question": question, "context": doc.page_content}
        )
        answers.append(result.content)
    st.write(answers)

# Function to scrape and return the page content
def scrape_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Clean the page by removing headers, footers, or irrelevant content
        header = soup.find('header')
        footer = soup.find('footer')
        if header:
            header.decompose()
        if footer:
            footer.decompose()
        
        return soup.get_text(separator=' ').strip()
    except Exception as e:
        st.error(f"Error scraping {url}: {e}")
        return ""

# Function to process scraped content into FAISS retriever
def process_content_into_retriever(pages_content):
    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=1000,
        chunk_overlap=200,
    )
    docs = splitter.create_documents(pages_content)
    vector_store = FAISS.from_documents(docs, OpenAIEmbeddings(openai_api_key=openai_api_key))
    return vector_store.as_retriever()

# Set up the Streamlit page config
st.set_page_config(
    page_title="Cloudflare Documentation GPT",
    page_icon="🖥️",
)

# Display the page title and description
st.markdown(
    """
    # Cloudflare Documentation GPT
            
    Ask questions about the content of Cloudflare's documentation:
    - AI Gateway
    - Cloudflare Vectorize
    - Workers AI
"""
)

# Define the product URLs
product_urls = {
    "AI Gateway": "https://developers.cloudflare.com/ai-gateway/",
    "Cloudflare Vectorize": "https://developers.cloudflare.com/vectorize/",
    "Workers AI": "https://developers.cloudflare.com/workers-ai/"
}

# Scrape content from each product page
pages_content = []
for product, url in product_urls.items():
    st.info(f"Scraping content for {product}...")
    page_content = scrape_page(url)
    if page_content:
        pages_content.append(page_content)

# Process the scraped content into a retriever for querying
if pages_content:
    retriever = process_content_into_retriever(pages_content)
    
    # Allow the user to ask questions about the documentation
    query = st.text_input("Ask a question about the Cloudflare documentation content.")
    
    if query and retriever:
        docs = retriever.get_relevant_documents(query)
        get_answers(docs, query)
