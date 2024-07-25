from langchain_community.vectorstores import Chroma
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import Ollama
from langchain_core.embeddings import Embeddings
from langchain_openai import ChatOpenAI
import os


os.environ['OPENAI_API_KEY'] = ''



class MyEF(Embeddings):
    def __init__(self, ef):
        self.ef = ef
    def embed_documents(self,texts):
        return self.ef(texts)
    def embed_query(self, query):
        return self.ef([query])[0]


openai_ef = embedding_functions.OpenAIEmbeddingFunction(
   api_key=os.getenv('OPENAI_API_KEY'),
   model_name='text-embedding-3-small'
)


client = chromadb.PersistentClient(path='data/chroma')
db = Chroma(client=client, collection_name='langchain_docs2', embedding_function=MyEF(openai_ef))
retriever = db.as_retriever()


'''
query = 'langchain의 RecursiveCharacterTextSplitter 클래스의 주요 기능 알려줘.'
k = 6
documents = db.similarity_search(query, k)
document_str = ''
for doc in documents:
    document_str += doc.page_content
# print(documents.page_content)
'''


def format_docs(docs):
    return "\n".join(doc.page_content for doc in docs)


ollama_llm = Ollama(model='llama3')
openai_llm = ChatOpenAI(model='gpt-3.5-turbo', temperature=0)


prompt = PromptTemplate.from_template(
    "You are a langchain expert and coding teacher. Use the following pieces of retrieved context to teach the answer to the question. "
    "Please answer in detail. If you don't know the answer, just say that you don't know. Please answer in Korean. "
    "Question: {question} "
    "Context: {context}"
)

rag_chain = (
    {'context': retriever | format_docs, 'question': RunnablePassthrough()}
    | prompt
    | openai_llm
    | StrOutputParser()
)


question1 = 'langchain을 이용해서 rag시스템 구축하는 방법 알려줘.'
question2 = 'langchain을 이용해서 벡터 DB에 document 저장하는 방법 알려줘.'
question3 = 'langchain v0.2 버전에서의 RecursiveCharacterTextSplitter 클래스의 주요 기능 알려줘.'
question4 = 'langchain프레임워크에서 Indexing 기능에 대해 설명해줘'
question5 = 'langchain 프레임워크에서 HTMLSectionSplitter에 대해 설명하고 예제 코드 알려줘'


answer = rag_chain.invoke(
    question5
)

print(answer)


# langchain v0.2 -> 2024년 5월 20일 release
