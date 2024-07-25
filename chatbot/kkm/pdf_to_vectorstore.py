from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
import os
import re


def load_remove_list(file_path: str) -> list:
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file.readlines()]


def load_all_pdfs_from_directory(data_path: str, remove_list: list):
    all_documents = []

    for filename in os.listdir(data_path):
        if filename.endswith(".pdf"):
            file_path = os.path.join(data_path, filename)
            loader = PyPDFLoader(file_path)
            document = loader.load()
            prepend_str = f'\"출처: {filename} \n \"'
            for doc in document:
                for pattern in remove_list:
                    doc.page_content = doc.page_content.replace(pattern, '')
                doc.page_content = prepend_str + doc.page_content.replace('\n', ' ')
                doc.page_content = doc.page_content.replace('  ', ' ')
            all_documents.extend(document)

    return all_documents


directory = "./data"  #PDF 파일 경로
remove_list_path = "./remove_list.txt"  #PDF 전처리(불필요 문자 제거) 리스트
os.environ["OPENAI_API_KEY"] = ""  #openai 키 입력

remove_list = load_remove_list(remove_list_path)
documents = load_all_pdfs_from_directory(data_path=directory, remove_list=remove_list)

embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(documents, embeddings)
vectorstore.save_local('./db/faiss')


