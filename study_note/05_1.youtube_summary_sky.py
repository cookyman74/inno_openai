from youtube_transcript_api import YouTubeTranscriptApi
import openai

video_id='orDKvo8h71o'

captions = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko', 'en'])
texts = [caption['text'] for caption in captions]

max_length = 1000
current_length = 0
groups = []
current_group = []

for text in texts:
    if current_length + len(text) > max_length:
        groups.append(current_group)
        current_group = [text]
        current_length = len(text)
    else:
        current_group.append(text)
        current_length += len(text)

if current_group:
    groups.append(current_group)

for group in groups:
    text = " ".join(group)
    prompt = f"주제를 분석하고 주요 정보를 요약하세요: {text}"

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    print("요약:", response['choices'][0]['message']['content'].strip())