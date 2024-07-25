import os

from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.llms import Ollama
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI


os.environ['OPENAI_API_KEY'] = ''

ollama_llm = Ollama(model='llama3', temperature=0)
openai_llm = ChatOpenAI(model='gpt-3.5-turbo', temperature=0)

prompt = PromptTemplate.from_template(
    "You are a langchain expert and coding teacher."
    "Please answer in detail. If you don't know the answer, just say that you don't know. Please answer in Korean. "
    "Question: {question} "
)

llm_chain = ( 
    {'question': RunnablePassthrough()}
    | prompt
    | openai_llm
    | StrOutputParser()
)


question1 = 'langchain을 이용해서 rag시스템 구축하는 방법 알려줘.'
question2 = 'langchain을 이용해서 벡터 DB에 document 저장하는 방법 알려줘.'
question3 = 'langchain v0.2 버전에서의 RecursiveCharacterTextSplitter 클래스의 주요 기능 알려줘.'

question4 = 'langchain프레임워크에서 Indexing 기능에 대해 설명해줘'
question5 = 'langchain 프레임워크에서 HTMLSectionSplitter에 대해 설명하고 예제 코드 알려줘'


print(llm_chain.invoke(question5))


# GPT-4o -> 2023년 10월 까지의 데이터
# GPT-3.5-turbo -> 2021년 9월 까지의 데이터