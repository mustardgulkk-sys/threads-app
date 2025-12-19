import json
import anthropic
import requests
import random

def handler(event, context):
    # 폰에서 입력할 추가 지시사항을 받는 부분
    params = event.get('queryStringParameters', {})
    extra_prompt = params.get('extra', '') if params else ''

    # --- [사용자 정보 입력 구간] ---
    CLAUDE_KEY = "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"
    THREADS_TOKEN = "THAAUKlPxroIVBUVJuYVRxNHFDalI2MnVCQUxSdUZAtb1JJb00tc1d1ZAmVKbm5hekZAudDF0SjhfaFV6Y1NRaVdzTVhTZAEJiTmR1OGN0VHVEWnhDZA1Bib1ozOS0wOGs2VTVaNWY3WFJCLWVxNVFhVHRtVURyT0tGVG5HSXZA1V0FIcmx3RzFiOTdBQmVXS3YxZAjgZD"
    THREADS_USER_ID = "26171896552412179" #

    client = anthropic.Anthropic(api_key=CLAUDE_KEY)

    try:
        # 1. 상황 설정 및 글 생성
        scenarios = ["이별 후 전 애인 염탐", "직장 상사 갈등", "친구의 스토킹", "관심 확인"]
        selected_scenario = random.choice(scenarios)
        
        system_prompt = f"""
        너는 스레드 리퍼럴 마케팅 고수야. 반말로 작성해.
        기본 상황: {selected_scenario}
        추가 요청: {extra_prompt} 
        분량: 100~150자 내외.
        마지막엔 인스타그램 방문자 추적기 사용 후기를 자연스럽게 넣어.
        비속어는 최대한 피하고 욕설은 아예 금지!
        
        """
        
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=300,
            system=system_prompt,
            messages=[{"role": "user", "content": "글 써줘."}]
        )
        content = message.content[0].text

        # 2. 스레드 게시 (1단계: 컨테이너 생성)
        container_url = f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads"
        res1 = requests.post(container_url, params={
            'text': content, 'media_type': 'TEXT', 'access_token': THREADS_TOKEN
        })
        container_id = res1.json().get('id')

        # 3. 스레드 게시 (2단계: 최종 게시)
        publish_url = f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads_publish"
        requests.post(publish_url, params={
            'creation_id': container_id, 'access_token': THREADS_TOKEN
        })

        return {
            "statusCode": 200,
            "body": json.dumps({"message": f"✅ 게시 성공!\n내용: {content[:30]}..."})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": f"❌ 오류 발생: {str(e)}"})
        }