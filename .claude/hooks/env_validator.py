#!/usr/bin/env python3
"""
Claude Code 환경변수 보안 검증 훅
.env 파일 변경 시 보안 검증 및 필수 환경변수 체크
"""

import json
import sys
import os
import re
from datetime import datetime
from pathlib import Path


def log_message(message, level="INFO"):
  """
  로그 메시지를 파일에 기록
  """
  log_file = Path.home() / '.claude' / 'env-validator.log'
  log_file.parent.mkdir(parents=True, exist_ok=True)

  timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  log_line = f"[{timestamp}] [{level}] {message}\n"

  try:
    with open(log_file, 'a', encoding='utf-8') as f:
      f.write(log_line)
  except Exception:
    pass


def read_env_file(file_path):
  """
  .env 파일을 읽어서 파싱
  """
  env_vars = {}
  try:
    with open(file_path, 'r', encoding='utf-8') as f:
      for line_num, line in enumerate(f, 1):
        line = line.strip()
        # 빈 줄이나 주석은 건너뛰기
        if not line or line.startswith('#'):
          continue

        if '=' in line:
          key, value = line.split('=', 1)
          env_vars[key.strip()] = {
            'value': value.strip(),
            'line': line_num
          }
  except Exception as e:
    log_message(f"파일 읽기 에러: {e}", "ERROR")
    return None

  return env_vars


def check_required_variables(env_vars, file_name):
  """
  필수 환경변수 체크
  """
  issues = []

  # 파일별 필수 환경변수 정의
  required_vars = {
    '.env': [
      'DATABASE_URL',
      'SECRET_KEY',
      'ENV'
    ],
    '.env.example': [
      'DATABASE_URL',
      'SECRET_KEY',
      'ENV'
    ]
  }

  required = required_vars.get(file_name, [])

  for var in required:
    if var not in env_vars:
      issues.append({
        'type': 'missing',
        'severity': 'error',
        'variable': var,
        'message': f"필수 환경변수 '{var}'가 누락되었습니다"
      })

  return issues


def check_secret_key_strength(value):
  """
  SECRET_KEY 강도 검증
  """
  issues = []

  # 최소 길이 체크 (32자)
  if len(value) < 32:
    issues.append({
      'type': 'weak_secret',
      'severity': 'error',
      'message': f"SECRET_KEY가 너무 짧습니다 (현재: {len(value)}자, 최소: 32자)"
    })

  # 예시 값 체크
  example_patterns = [
    'your-secret-key',
    'change-this',
    'changeme',
    'please-change',
    '123456',
    'secret',
    'password'
  ]

  value_lower = value.lower()
  for pattern in example_patterns:
    if pattern in value_lower:
      issues.append({
        'type': 'example_value',
        'severity': 'warning',
        'message': f"SECRET_KEY가 예시 값으로 보입니다: '{pattern}' 패턴 발견"
      })
      break

  # 복잡도 체크 (영문, 숫자, 특수문자 포함 권장)
  has_upper = bool(re.search(r'[A-Z]', value))
  has_lower = bool(re.search(r'[a-z]', value))
  has_digit = bool(re.search(r'[0-9]', value))
  has_special = bool(re.search(r'[^A-Za-z0-9]', value))

  complexity_score = sum([has_upper, has_lower, has_digit, has_special])

  if complexity_score < 3 and len(value) < 40:
    issues.append({
      'type': 'weak_complexity',
      'severity': 'warning',
      'message': "SECRET_KEY의 복잡도가 낮습니다 (대문자, 소문자, 숫자, 특수문자 조합 권장)"
    })

  return issues


def check_database_url(value):
  """
  DATABASE_URL 검증
  """
  issues = []

  # 예시 값 체크
  if 'password' in value.lower() and not ':' in value:
    issues.append({
      'type': 'example_value',
      'severity': 'warning',
      'message': "DATABASE_URL이 예시 값으로 보입니다"
    })

  # localhost 프로덕션 경고
  if 'localhost' in value or '127.0.0.1' in value:
    issues.append({
      'type': 'localhost_in_prod',
      'severity': 'info',
      'message': "DATABASE_URL이 localhost를 사용 중입니다 (개발 환경 확인)"
    })

  # 평문 비밀번호 패턴 감지 (간단한 비밀번호)
  simple_passwords = ['password', '123456', 'admin', 'root', 'test']
  for pwd in simple_passwords:
    if f':{pwd}@' in value.lower():
      issues.append({
        'type': 'weak_password',
        'severity': 'error',
        'message': f"DATABASE_URL에 취약한 비밀번호 '{pwd}'가 포함되어 있습니다"
      })
      break

  return issues


def check_hardcoded_secrets(env_vars):
  """
  민감정보 하드코딩 체크
  """
  issues = []

  sensitive_patterns = {
    'API_KEY': r'^[A-Za-z0-9]{20,}$',
    'SECRET': r'.+',
    'PASSWORD': r'.+',
    'TOKEN': r'.+',
    'PRIVATE_KEY': r'.+',
  }

  for var_name, var_info in env_vars.items():
    value = var_info['value']

    # 빈 값 체크
    if not value or value in ['""', "''", '""', "''"] :
      issues.append({
        'type': 'empty_value',
        'severity': 'warning',
        'variable': var_name,
        'line': var_info['line'],
        'message': f"환경변수 '{var_name}'의 값이 비어있습니다 (line {var_info['line']})"
      })
      continue

    # 민감한 키워드 포함 여부 체크
    for keyword in sensitive_patterns.keys():
      if keyword in var_name.upper():
        # 예시 값 패턴 체크
        if 'your-' in value.lower() or 'change' in value.lower() or 'example' in value.lower():
          issues.append({
            'type': 'example_value',
            'severity': 'warning',
            'variable': var_name,
            'line': var_info['line'],
            'message': f"'{var_name}'이 예시 값으로 보입니다 (line {var_info['line']})"
          })

  return issues


def check_gitignore(project_dir, env_file_name):
  """
  .env 파일이 .gitignore에 포함되어 있는지 확인
  """
  gitignore_path = Path(project_dir) / '.gitignore'

  if not gitignore_path.exists():
    return [{
      'type': 'no_gitignore',
      'severity': 'warning',
      'message': ".gitignore 파일이 존재하지 않습니다"
    }]

  try:
    with open(gitignore_path, 'r', encoding='utf-8') as f:
      gitignore_content = f.read()

    # .env 파일이 gitignore에 포함되어 있는지 확인
    if '.env' not in gitignore_content and env_file_name == '.env':
      return [{
        'type': 'not_in_gitignore',
        'severity': 'error',
        'message': f"'{env_file_name}' 파일이 .gitignore에 포함되어 있지 않습니다! 보안 위험!"
      }]
  except Exception as e:
    log_message(f".gitignore 확인 실패: {e}", "ERROR")

  return []


def validate_env_file(file_path, project_dir):
  """
  .env 파일 전체 검증
  """
  all_issues = []

  # 파일명 추출
  file_name = Path(file_path).name

  log_message(f"환경변수 검증 시작: {file_name}", "INFO")

  # 1. .env 파일 읽기
  env_vars = read_env_file(file_path)
  if env_vars is None:
    return [{'type': 'file_error', 'severity': 'error', 'message': '파일을 읽을 수 없습니다'}]

  # 2. 필수 변수 체크
  missing_issues = check_required_variables(env_vars, file_name)
  all_issues.extend(missing_issues)

  # 3. SECRET_KEY 강도 체크
  if 'SECRET_KEY' in env_vars:
    secret_issues = check_secret_key_strength(env_vars['SECRET_KEY']['value'])
    for issue in secret_issues:
      issue['variable'] = 'SECRET_KEY'
      issue['line'] = env_vars['SECRET_KEY']['line']
    all_issues.extend(secret_issues)

  # 4. DATABASE_URL 체크
  if 'DATABASE_URL' in env_vars:
    db_issues = check_database_url(env_vars['DATABASE_URL']['value'])
    for issue in db_issues:
      issue['variable'] = 'DATABASE_URL'
      issue['line'] = env_vars['DATABASE_URL']['line']
    all_issues.extend(db_issues)

  # 5. 하드코딩된 민감정보 체크
  hardcoded_issues = check_hardcoded_secrets(env_vars)
  all_issues.extend(hardcoded_issues)

  # 6. .gitignore 체크 (.env 파일만, .env.example은 제외)
  if file_name == '.env':
    gitignore_issues = check_gitignore(project_dir, file_name)
    all_issues.extend(gitignore_issues)

  return all_issues


def format_validation_report(issues, file_path):
  """
  검증 결과를 포맷팅된 리포트로 출력
  """
  if not issues:
    log_message("✅ 환경변수 검증 통과", "INFO")
    return

  # 심각도별 분류
  errors = [i for i in issues if i.get('severity') == 'error']
  warnings = [i for i in issues if i.get('severity') == 'warning']
  infos = [i for i in issues if i.get('severity') == 'info']

  report = f"\n{'='*60}\n"
  report += f"🔒 환경변수 보안 검증 결과: {Path(file_path).name}\n"
  report += f"{'='*60}\n\n"

  if errors:
    report += f"❌ 에러 ({len(errors)}개):\n"
    for i, issue in enumerate(errors, 1):
      var = issue.get('variable', '')
      line = issue.get('line', '')
      loc = f" [{var}:L{line}]" if var and line else f" [{var}]" if var else ""
      report += f"  {i}. {issue['message']}{loc}\n"
    report += "\n"

  if warnings:
    report += f"⚠️  경고 ({len(warnings)}개):\n"
    for i, issue in enumerate(warnings, 1):
      var = issue.get('variable', '')
      line = issue.get('line', '')
      loc = f" [{var}:L{line}]" if var and line else f" [{var}]" if var else ""
      report += f"  {i}. {issue['message']}{loc}\n"
    report += "\n"

  if infos:
    report += f"ℹ️  정보 ({len(infos)}개):\n"
    for i, issue in enumerate(infos, 1):
      var = issue.get('variable', '')
      line = issue.get('line', '')
      loc = f" [{var}:L{line}]" if var and line else f" [{var}]" if var else ""
      report += f"  {i}. {issue['message']}{loc}\n"
    report += "\n"

  report += f"{'='*60}\n"

  log_message(report, "INFO")

  # 에러가 있으면 stderr에도 출력 (선택적)
  if errors:
    print(report, file=sys.stderr)


def should_process_file(file_path):
  """
  파일을 처리해야 하는지 판단
  """
  file_name = Path(file_path).name

  # .env로 시작하는 파일만 처리
  return file_name.startswith('.env')


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
      sys.exit(0)

    # 프로젝트 디렉토리
    project_dir = os.getenv('CLAUDE_PROJECT_DIR', '')
    if not project_dir:
      project_dir = str(Path(file_path).parent)

    # 검증 실행
    issues = validate_env_file(file_path, project_dir)

    # 결과 리포트
    format_validation_report(issues, file_path)

    # 정상 종료 (에러가 있어도 훅은 통과)
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
