from opensearchpy import OpenSearch
import openai
from dotenv import load_dotenv
import os
import json

load_dotenv()

# OpenSearch 클라이언트 초기화
client = OpenSearch(
    hosts=[{'host': '192.168.110.211', 'port': 9200}],
    http_compress=True,  # enables gzip compression for request bodies
)

# 로그 검색 쿼리
index_name = "telegraf-*"
query = {
    "query": {
        "bool": {
            "must": [
                {
                    "range": {
                        "@timestamp": {
                            "gte": "now-3d",  # 이벤트 발생 전후 1시간 범위 로그 검색
                            "lte": "now"
                        }
                    }
                },
                {"match_phrase": {"fields.message": "error"}}
            ]
        }
    }
}

# 검색 실행
response = client.search(index=index_name, body=query)
print("00000",response)

# 검색 결과
logs = response["hits"]["hits"]
print("hhhhh",logs)

# 로그 간략화 함수
def simplify_log(log):
    fields = log["_source"].get("fields", {})
    return {
        "timestamp": log["_source"].get("@timestamp", "N/A"),
        "message": fields.get("message", "No message provided"),
        "severity": log["_source"].get("severity", "unknown"),
    }

# 간략화된 로그 리스트 생성
simplified_logs = [simplify_log(log) for log in logs]
print(simplified_logs)

# OpenAI API 키 설정
openai_api_key = os.getenv('OPENAI_API_KEY')

# 간략화된 로그를 질의로 변환
log_texts = "\n".join([f"{log['timestamp']} [{log['severity']}] {log['message']}" for log in simplified_logs])
print(log_texts)

# OpenAI 모델에 질의
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a system log analyzer."},
        {"role": "user", "content": f"The following are logs from the server 'master.mini-pc.com'. Identify any anomalies and found the cause. Please answer in Korean.:\n{log_texts}"}
    ],
    temperature=0.0,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
)

# 결과 출력
anomalies = response.choices[0].message['content'].strip()
print(anomalies)
