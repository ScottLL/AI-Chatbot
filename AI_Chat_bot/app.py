from fastapi import FastAPI, UploadFile, File
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceInstructEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.llms import HuggingFaceHub
from typing import List
import uvicorn
import os

app = FastAPI()

conversation = None  # Initialize conversation as a global variable

@app.on_event("startup")
async def startup_event():
    load_dotenv()
    os.environ["OPENAI_API_KEY"] = "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"  # Replace with your actual OpenAI API key

@app.post("/upload/")
async def upload_files(files: List[UploadFile]):
    global conversation  # Declare conversation as global so we can modify it

    # get pdf text
    raw_text = get_pdf_text(files)

    # get the text chunks
    text_chunks = get_text_chunks(raw_text)

    # create vector store
    vectorstore = get_vectorstore(text_chunks)

    # create conversation chain
    conversation = get_conversation_chain(vectorstore)

    return {"detail": "Files processed successfully"}

@app.post("/ask/")
async def ask_question(question: str):
    global conversation  # Declare conversation as global so we can access it

    if conversation is None:
        return {"error": "No documents uploaded yet"}

    response = conversation({'question': question})
    chat_history = response['chat_history']

    return {"chat_history": chat_history}

def get_pdf_text(files):
    text = ""
    for file in files:
        pdf_reader = PdfReader(file.file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore

def get_conversation_chain(vectorstore):
    llm = ChatOpenAI()
    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
