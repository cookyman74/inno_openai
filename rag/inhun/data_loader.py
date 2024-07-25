import os
from pathlib import Path
import chromadb
import chromadb.utils.embedding_functions as embedding_functions

from langchain_community.document_loaders import NotebookLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


openai_ef = embedding_functions.OpenAIEmbeddingFunction(
   api_key='',
   model_name='text-embedding-3-small'
)
client = chromadb.PersistentClient(path='data/chroma')

# langchain_docs에는 chunk_size=2000
# langchain_docs2에는 chunk_size=6000
try:
    collection = client.create_collection(name='langchain_docs2', embedding_function=openai_ef, metadata={'hnsw:space': 'cosine'})
except:
    collection = client.get_collection(name='langchain_docs2', embedding_function=openai_ef)


def get_docs_paths():
    path_list = []
    
    for path in Path('docs').rglob('*.ipynb'):
        path_list.append(path)

    return path_list


def load_langchain_docs(path_list):
    docs_list = []

    for path in path_list:
        loader = NotebookLoader(
            path='docs/tutorials/rag.ipynb',
            remove_newline=True
        )
        docs = loader.load()
        docs_list.append(docs)


    return docs_list
    
 
def split_docs(docs_list):
    splits_list = []
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=6000, chunk_overlap=500)
    for doc in docs_list:
        splits = text_splitter.split_documents(doc)
        splits_list.append(splits)
    
    return splits_list


def save_to_db(splits_list):
    for idx, splits in enumerate(splits_list):
        if idx % 10 == 0:
            print(idx)

        try:
            collection.add(documents=splits[0].page_content, ids=[str(idx)])
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(e)
            continue











if __name__ == '__main__':
    path_list = get_docs_paths()
    docs_list = load_langchain_docs(path_list)
    splits_list = split_docs(docs_list)
    save_to_db(splits_list)
    # print(docs_list)

