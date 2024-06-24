from dotenv import load_dotenv

import openai
from openai import OpenAI
from youtube_transcript_api import YouTubeTranscriptApi


def get_video_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko', 'en'])
        transcript_text = " ".join([entry['text'] for entry in transcript])
        return transcript_text
    except Exception as e:
        print(f"Error retrieving transcript: {e}")
        return None


def summarize_text(client, text):
    try:
        # https://platform.openai.com/docs/models/gpt-3-5-turbo
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {
                    'role': 'system',
                    'content': '다음과 같이 영상의 자막 {text}을 한국어로 요약해줘. 내용은 풍성하게 포함하고, 유머나 잡담은 최대한 제외해줘.'
                },
                {
                    'role': 'user',
                    'content': f'{text}'
                }
            ],
            # max_tokens=500,
            temperature=0.5,
        )
        summary = response.choices[0].message
        return summary
    except Exception as e:
        print(f"Error summarizing text: {e}")
        return None


def main(video_id):
    client = OpenAI()

    transcript_text = get_video_transcript(video_id)
    if transcript_text:
        point = 0
        while point < len(transcript_text):
            summary = summarize_text(client, transcript_text[point:point+4000])
            print(f'summary: {summary.content}')
            point += 4000

    else:
        print("No transcript available.")


if __name__ == "__main__":
    load_dotenv()
    video_id = "Z-ekdCF5Dvg"

    main(video_id)
