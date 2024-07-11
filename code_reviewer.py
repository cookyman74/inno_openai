import os
from openai import OpenAI
from dotenv import load_dotenv
from git import Repo
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
load_dotenv()

# OpenAI 클라이언트 초기화
client = OpenAI()

def get_staged_diff():
    """스테이지에 추가된 파일의 diff를 가져옵니다."""
    try:
        repo = Repo(os.getcwd())
        diff = repo.git.diff('--cached')
        return diff
    except Exception as e:
        logging.error(f"Git diff를 가져오는 중 오류가 발생했습니다: {e}")
        raise

def review_code(diff):
    """OpenAI API를 사용하여 코드 리뷰를 받습니다."""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 간결하고 효과적인 코드 리뷰어입니다. 버그와 개선이 필요한 부분에 대해서만 짧고 명확하게 한국어로 피드백을 제공합니다."},
                {"role": "user", "content": f"다음 코드 변경사항을 검토하고, 버그나 개선이 필요한 부분만 간단히 지적해주세요:\n\n{diff}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"OpenAI API 호출 중 오류가 발생했습니다: {e}")
        raise

def suggest_commit_message(diff):
    """OpenAI API를 사용하여 커밋 메시지를 추천받습니다."""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 명확하고 정보력 있는 git 커밋 메시지 작성자입니다. 코드 변경사항을 정확히 파악하고, 추가된 기능이나 수정된 내용을 간결하게 설명하는 커밋 메시지를 한국어로 작성합니다."},
                {"role": "user", "content": f"다음 코드 변경사항을 분석하고, 추가된 코드의 핵심 기능이나 중요한 수정사항을 잘 나타내는 간결한 커밋 메시지를 작성해주세요:\n\n{diff}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"OpenAI API 호출 중 오류가 발생했습니다: {e}")
        raise

def main():
    try:
        diff = get_staged_diff()
        if not diff:
            logging.info("스테이지에 추가된 변경사항이 없습니다.")
            return

        logging.info("코드 리뷰 중...\n")
        review = review_code(diff)
        logging.info("코드 리뷰 결과:")
        print(review + "\n\n")

        logging.info("커밋 메시지 추천 중...\n")
        commit_message = suggest_commit_message(diff)
        logging.info("추천된 커밋 메시지:")
        print(commit_message + "\n\n")

        user_input = input("\n이 커밋 메시지를 사용하시겠습니까?... (y/n): ")
        if user_input.lower() == 'y':
            repo = Repo(os.getcwd())
            repo.index.commit(commit_message)
            logging.info("커밋이 완료되었습니다.")
        else:
            logging.info("커밋이 취소되었습니다.")
    except Exception as e:
        logging.error(f"메인 프로세스 중 오류가 발생했습니다: {e}")


if __name__ == "__main__":
    main()
