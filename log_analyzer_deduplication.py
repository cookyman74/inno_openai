from opensearchpy import OpenSearch
import openai
from collections import Counter


# OpenAI API 키 설정
openai.api_key = ''


def simplify_log(log):
    fields = log["_source"].get("fields", {})
    tags = log["_source"].get("_tags", [])
    return {
        "timestamp": log["_source"].get("@timestamp", "N/A"),
        "message": fields.get("message", "No message provided"),
        "host": tags[0].get("host", "UNKNOWN"),
    }


def refine_logs(log_list):
    log_counter = Counter(log['message'] for log in log_list)

    # 정제된 로그 리스트 생성
    refined_logs = []
    for log in log_list:
        message = log['message']
        count = log_counter[message]
        refined_log = log.copy()
        refined_log['count'] = count
        if count > 1:
            if not any(d['message'] == message for d in refined_logs):
                refined_logs.append(refined_log)
        else:
            refined_logs.append(refined_log)

    return refined_logs


def get_log_analysis_response(log):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a system log analyzer."},
            {"role": "user", "content": f"The following are logs from the server 'master.mini-pc.com'. "
                                        f"Identify any anomalies and found the cause and simple solutions. "
                                        f"Please answer in Korean.:\n{log}"}
        ],
        temperature=0.0,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    return response.choices[0].message['content'].strip()

# OpenSearch 클라이언트 초기화
client = OpenSearch(
    hosts=[{'host': '192.168.110.211', 'port': 9200}],
    http_compress=True,  # enables gzip compression for request bodies
)

# 로그 검색 쿼리
index_name = "telegraf-*"
query = {
    "size": 100,
    "query": {
        "bool": {
            "must": [
                {
                    "range": {
                        "@timestamp": {
                            "gte": "now-3d",
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
# print("00000",response)

# 검색 결과
logs = response["hits"]["hits"]
# print("hhhhh",logs)

# 간략화된 로그 리스트 생성
simplified_logs = [simplify_log(log) for log in logs]
# for log in simplified_logs:
#     print(log)
#     print()

refined_log_data = refine_logs(simplified_logs)

# print("정제된 로그 리스트:")
# for log in refined_log_data:
#     print(log)

# 간략화된 로그를 질의로 변환
log_texts = "\n".join([f"This log has happened {log['count']}times in total, {log['timestamp']}"
                       f" [{log['host']}] {log['message']}" for log in refined_log_data])

print("#####################\n")
print(f'검색한 로그 수: {len(simplified_logs)}\n')
print(f'중복 처리된 로그 수: {len(refined_log_data)}\n')
print("#####################\n")

# OpenAI 모델에 질의 & 결과 출력
response = get_log_analysis_response(log=log_texts)
print(response)
