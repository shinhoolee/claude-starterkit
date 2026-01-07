#!/usr/bin/env python3
"""
Claude Code Slack 알림 훅
권한 요청(Edit, Write) 및 작업 완료 시 Slack으로 알림을 전송합니다.
"""

import json
import sys
import os
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import traceback
from pathlib import Path


def load_env_file():
  """
  .env 파일에서 환경변수 로드
  """
  env_file = Path(os.getenv('CLAUDE_PROJECT_DIR', '')) / '.env'
  env_vars = {}

  if env_file.exists():
    try:
      with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
          line = line.strip()
          if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            env_vars[key.strip()] = value.strip()
    except Exception as e:
      log_error(f".env 파일 로드 실패: {e}")

  return env_vars


def get_webhook_url():
  """
  Slack Webhook URL 가져오기
  우선순위: 환경변수 > .env 파일
  """
  # 환경변수에서 먼저 확인
  webhook_url = os.getenv('SLACK_WEBHOOK_URL')

  # 환경변수에 없으면 .env 파일에서 로드
  if not webhook_url:
    env_vars = load_env_file()
    webhook_url = env_vars.get('SLACK_WEBHOOK_URL')

  return webhook_url


def log_error(message):
  """
  에러 로그를 파일에 기록
  """
  log_file = Path.home() / '.claude' / 'slack-notify.log'
  log_file.parent.mkdir(parents=True, exist_ok=True)

  timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  log_message = f"[{timestamp}] {message}\n"

  try:
    with open(log_file, 'a', encoding='utf-8') as f:
      f.write(log_message)
  except Exception:
    pass  # 로그 기록 실패는 무시


def format_notification_message(data):
  """
  Notification 훅 메시지 포맷팅
  Edit, Write 도구만 처리
  """
  tool_name = data.get('tool_name', 'Unknown')

  # Edit, Write 도구만 알림 전송
  if tool_name not in ['Edit', 'Write']:
    return None

  tool_input = data.get('tool_input', {})
  file_path = tool_input.get('file_path', 'N/A')
  notification_type = data.get('notification_type', 'permission_prompt')

  # 프로젝트 디렉토리 상대 경로로 변환
  project_dir = os.getenv('CLAUDE_PROJECT_DIR', '')
  if project_dir and file_path.startswith(project_dir):
    file_path = file_path[len(project_dir):].lstrip('\\/')

  timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

  # 도구별 아이콘
  icon = '📝' if tool_name == 'Edit' else '📄'
  action = '파일 수정' if tool_name == 'Edit' else '파일 생성'

  message = f"""{icon} *권한 요청: {action}*
📋 도구: `{tool_name}`
📁 파일: `{file_path}`
⏰ 시간: {timestamp}
🔔 타입: {notification_type}"""

  # 파일 내용 미리보기 (선택적, 너무 길면 생략)
  if tool_name == 'Write':
    content = tool_input.get('content', '')
    if content and len(content) < 200:
      message += f"\n💬 내용 미리보기: ```{content[:100]}...```"

  return message


def format_stop_message(data):
  """
  Stop 훅 메시지 포맷팅
  """
  session_id = data.get('session_id', 'Unknown')
  cwd = data.get('cwd', 'N/A')
  timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

  # 프로젝트명 추출
  project_name = Path(cwd).name if cwd != 'N/A' else 'Unknown'

  message = f"""✅ *작업 완료*
🆔 세션: `{session_id[:8]}...`
📂 프로젝트: `{project_name}`
📍 경로: `{cwd}`
⏰ 완료 시간: {timestamp}"""

  return message


def send_slack_notification(webhook_url, message):
  """
  Slack 웹훅으로 알림 전송
  """
  payload = {
    'text': message,
    'mrkdwn': True
  }

  try:
    # JSON 데이터를 바이트로 인코딩
    data = json.dumps(payload).encode('utf-8')

    # HTTP POST 요청
    request = Request(
      webhook_url,
      data=data,
      headers={'Content-Type': 'application/json'},
      method='POST'
    )

    # 타임아웃 5초
    with urlopen(request, timeout=5) as response:
      if response.status == 200:
        return True
      else:
        log_error(f"Slack 응답 에러: HTTP {response.status}")
        return False

  except HTTPError as e:
    log_error(f"Slack HTTP 에러: {e.code} - {e.reason}")
    return False
  except URLError as e:
    log_error(f"Slack URL 에러: {e.reason}")
    return False
  except Exception as e:
    log_error(f"Slack 전송 에러: {str(e)}\n{traceback.format_exc()}")
    return False


def main():
  """
  메인 실행 함수
  """
  try:
    # stdin에서 JSON 데이터 읽기
    input_data = json.load(sys.stdin)

    # Webhook URL 가져오기
    webhook_url = get_webhook_url()
    if not webhook_url or webhook_url.startswith('https://hooks.slack.com/services/YOUR'):
      log_error("SLACK_WEBHOOK_URL이 설정되지 않았습니다. .env 파일을 확인하세요.")
      sys.exit(0)  # 에러지만 훅은 통과

    # 훅 이벤트 타입 확인
    hook_event_name = input_data.get('hook_event_name', '')

    message = None

    if hook_event_name == 'Notification':
      # Notification 훅: Edit, Write 도구만 처리
      message = format_notification_message(input_data)

    elif hook_event_name == 'Stop':
      # Stop 훅: 작업 완료 알림
      message = format_stop_message(input_data)

    # 메시지가 있으면 Slack으로 전송
    if message:
      success = send_slack_notification(webhook_url, message)
      if success:
        # 성공 로그 (선택적)
        pass
      else:
        log_error(f"알림 전송 실패: {hook_event_name}")

    # 정상 종료 (exit 0)
    sys.exit(0)

  except json.JSONDecodeError as e:
    log_error(f"JSON 파싱 에러: {e}")
    sys.exit(1)
  except Exception as e:
    log_error(f"예상치 못한 에러: {str(e)}\n{traceback.format_exc()}")
    sys.exit(1)


if __name__ == '__main__':
  main()
