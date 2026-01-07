#!/usr/bin/env python3
"""
Claude Code 코드 품질 자동 체크 훅
Python 파일 변경 시 black(포맷팅) + ruff(린팅) 자동 실행
"""

import json
import sys
import os
import subprocess
from datetime import datetime
from pathlib import Path


def log_message(message, level="INFO"):
  """
  로그 메시지를 파일에 기록
  """
  log_file = Path.home() / '.claude' / 'code-quality.log'
  log_file.parent.mkdir(parents=True, exist_ok=True)

  timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  log_line = f"[{timestamp}] [{level}] {message}\n"

  try:
    with open(log_file, 'a', encoding='utf-8') as f:
      f.write(log_line)
  except Exception:
    pass


def run_command(command, cwd=None):
  """
  명령어 실행 및 결과 반환
  """
  try:
    result = subprocess.run(
      command,
      shell=True,
      cwd=cwd,
      capture_output=True,
      text=True,
      timeout=30
    )
    return result.returncode, result.stdout, result.stderr
  except subprocess.TimeoutExpired:
    return -1, "", "명령어 실행 타임아웃 (30초)"
  except Exception as e:
    return -1, "", str(e)


def check_tool_installed(tool_name):
  """
  도구가 설치되어 있는지 확인
  """
  returncode, stdout, stderr = run_command(f"{tool_name} --version")
  return returncode == 0


def run_black(file_path, project_dir):
  """
  Black 포맷터 실행
  """
  log_message(f"Black 실행: {file_path}")

  # black 설치 확인
  if not check_tool_installed("black"):
    log_message("Black이 설치되지 않았습니다. pip install black 실행 필요", "WARNING")
    return True, "Black 미설치"

  # black 실행 (자동 수정)
  returncode, stdout, stderr = run_command(
    f'black "{file_path}"',
    cwd=project_dir
  )

  if returncode == 0:
    if "reformatted" in stdout:
      log_message(f"Black 포맷팅 완료: {file_path}", "INFO")
      return True, "포맷팅 완료"
    else:
      log_message(f"Black 포맷팅 불필요: {file_path}", "INFO")
      return True, "포맷팅 불필요"
  else:
    log_message(f"Black 실행 실패: {stderr}", "ERROR")
    return False, stderr


def run_ruff(file_path, project_dir):
  """
  Ruff 린터 실행
  """
  log_message(f"Ruff 실행: {file_path}")

  # ruff 설치 확인
  if not check_tool_installed("ruff"):
    log_message("Ruff가 설치되지 않았습니다. pip install ruff 실행 필요", "WARNING")
    return True, "Ruff 미설치"

  # ruff check 실행 (자동 수정 시도)
  returncode, stdout, stderr = run_command(
    f'ruff check "{file_path}" --fix',
    cwd=project_dir
  )

  if returncode == 0:
    log_message(f"Ruff 린팅 통과: {file_path}", "INFO")
    return True, "린팅 통과"
  else:
    # 에러가 있지만 계속 진행
    log_message(f"Ruff 린팅 문제 발견: {stdout}", "WARNING")
    return True, stdout


def process_python_file(file_path, project_dir):
  """
  Python 파일에 대해 코드 품질 체크 실행
  """
  results = []

  # 1. Black 포맷팅
  success, message = run_black(file_path, project_dir)
  results.append(f"📝 Black: {message}")

  # 2. Ruff 린팅
  success, message = run_ruff(file_path, project_dir)
  results.append(f"🔍 Ruff: {message}")

  return results


def should_process_file(file_path):
  """
  파일을 처리해야 하는지 판단
  """
  # Python 파일만 처리
  if not file_path.endswith('.py'):
    return False

  # 제외할 파일/디렉토리 패턴
  exclude_patterns = [
    'venv/', '.venv/', 'env/', '__pycache__/',
    'alembic/versions/',  # 마이그레이션 파일 제외
    '.claude/hooks/',  # 훅 스크립트 자체 제외
  ]

  for pattern in exclude_patterns:
    if pattern in file_path.replace('\\', '/'):
      return False

  return True


def main():
  """
  메인 실행 함수
  """
  try:
    # stdin에서 JSON 데이터 읽기
    input_data = json.load(sys.stdin)

    hook_event_name = input_data.get('hook_event_name', '')
    tool_name = input_data.get('tool_name', '')

    # Write, Edit 이벤트만 처리
    if hook_event_name != 'Notification':
      sys.exit(0)

    if tool_name not in ['Write', 'Edit']:
      sys.exit(0)

    # 파일 경로 가져오기
    tool_input = input_data.get('tool_input', {})
    file_path = tool_input.get('file_path', '')

    if not file_path:
      sys.exit(0)

    # 처리 대상 파일인지 확인
    if not should_process_file(file_path):
      log_message(f"처리 제외 파일: {file_path}", "INFO")
      sys.exit(0)

    # 프로젝트 디렉토리
    project_dir = os.getenv('CLAUDE_PROJECT_DIR', '')

    # 상대 경로로 변환
    display_path = file_path
    if project_dir and file_path.startswith(project_dir):
      display_path = file_path[len(project_dir):].lstrip('\\/')

    log_message(f"코드 품질 체크 시작: {display_path}", "INFO")

    # Python 파일 처리
    results = process_python_file(file_path, project_dir)

    # 결과 로그 기록
    for result in results:
      log_message(result, "INFO")

    log_message(f"코드 품질 체크 완료: {display_path}", "INFO")

    # 정상 종료
    sys.exit(0)

  except json.JSONDecodeError as e:
    log_message(f"JSON 파싱 에러: {e}", "ERROR")
    sys.exit(1)
  except Exception as e:
    log_message(f"예상치 못한 에러: {str(e)}", "ERROR")
    import traceback
    log_message(traceback.format_exc(), "ERROR")
    sys.exit(1)


if __name__ == '__main__':
  main()
