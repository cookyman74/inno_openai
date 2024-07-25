import os
import chainlit as cl
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate


os.environ["OPENAI_API_KEY"] = ""  #openai 키 입력

embeddings = OpenAIEmbeddings()
db = FAISS.load_local('./db/faiss', embeddings, allow_dangerous_deserialization=True)
retriever = db.as_retriever(search_kwargs={"k": 3})

prompt = PromptTemplate(
    template="당신은 회사 규정에 대한 사용자의 질문을 돕는 지능형 비서입니다. "
             "하나씩 하나씩 생각하고 나서 대답해. "
             "친절하게 대답해. "
             "너가 참고한 문서에 적힌 출처도 찾아서 답변의 맨 마지막에 같이 알려줘. "
             "한국말로 대답해. "
             "답변을 찾을 수 없다면 \"죄송합니다, 관련 정보를 찾을 수 없습니다. 더 열심히 하겠습니다!\"라고 대답해."
             "Question: {subject}",
    input_variables=["subject"],
)


# Chainlit UI
@cl.on_chat_start
async def on_chat_start():
    model = ChatOpenAI(streaming=True,
                       temperature=0.0,
                       model_name='gpt-3.5-turbo',
                       )

    qa = RetrievalQA.from_chain_type(
        llm=model,
        chain_type="stuff",
        retriever=retriever)

    cl.user_session.set("qa", qa)


@cl.on_message
async def on_message(message: cl.Message):
    qa = cl.user_session.get("qa")
    formatted_prompt = prompt.format(subject=message.content)
    response = qa({"query": formatted_prompt})

    msg = cl.Message(content="")
    await msg.stream_token(response['result'])
    await msg.send()


@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="사내 규정 챗봇",
            message="안녕!",
            icon="/public/idea.svg",
            )
    ]