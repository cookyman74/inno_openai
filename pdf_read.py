import openai
from PyPDF2 import PdfReader


def read_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text


def split_text(text, max_tokens=1500):
    sentences = text.split('. ')
    chunks = []
    current_chunk = ""
    current_tokens = 0
    for sentence in sentences:
        sentence_tokens = len(sentence.split())
        if current_tokens + sentence_tokens > max_tokens:
            chunks.append(current_chunk)
            current_chunk = sentence + ". "
            current_tokens = sentence_tokens
        else:
            current_chunk += sentence + ". "
            current_tokens += sentence_tokens
    chunks.append(current_chunk)
    return chunks


def ask_gpt(text_chunk, question, api_key):
    openai.api_key = api_key
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "당신은 도움이 되는 조수입니다. 가능한 한 자세하게 답변해 주세요."},
            {"role": "user", "content": f"문맥: {text_chunk}\n\n질문: {question}"}
        ]
    )
    return response.choices[0].message['content']


def main(pdf_path, question, api_key):
    text = read_pdf(pdf_path)
    chunks = split_text(text)
    answers = []
    for chunk in chunks:
        answer = ask_gpt(chunk, question, api_key)
        answers.append(answer)
    full_answer = " ".join(answers)
    print(full_answer)


pdf_path = "./pdf파일"
question = "질문"
api_key = ""

main(pdf_path, question, api_key)