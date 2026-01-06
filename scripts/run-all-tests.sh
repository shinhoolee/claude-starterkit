#!/bin/bash

# Dual Test Runner - Express & FastAPI 통합 테스트 스크립트
# 이 스크립트는 dual-test-runner 에이전트의 참고 구현입니다

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# 결과 변수
EXPRESS_PASSED=0
EXPRESS_FAILED=0
EXPRESS_SKIPPED=0
EXPRESS_TIME=0

FASTAPI_PASSED=0
FASTAPI_FAILED=0
FASTAPI_SKIPPED=0
FASTAPI_TIME=0

echo -e "${BLUE}${BOLD}🧪 듀얼 스택 테스트 실행 시작...${NC}\n"

# 1. Express 테스트 실행
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}${BOLD}📦 Express (Node.js) 테스트${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

if [ -f "package.json" ]; then
  echo "프레임워크: Jest/Mocha"

  # Express 테스트 실행 (병렬)
  EXPRESS_START=$(date +%s)

  if npm test 2>&1 | tee /tmp/express-test.log; then
    EXPRESS_EXIT=0
  else
    EXPRESS_EXIT=$?
  fi

  EXPRESS_END=$(date +%s)
  EXPRESS_TIME=$((EXPRESS_END - EXPRESS_START))

  # 결과 파싱 (Jest 출력 형식)
  # 실제로는 Jest JSON reporter를 사용하면 더 정확함
  EXPRESS_PASSED=$(grep -o "passed" /tmp/express-test.log | wc -l || echo "0")
  EXPRESS_FAILED=$(grep -o "failed" /tmp/express-test.log | wc -l || echo "0")

  echo -e "\n실행 시간: ${EXPRESS_TIME}초\n"
  echo "결과:"
  echo -e "  ${GREEN}✅ 통과: ${EXPRESS_PASSED}${NC}"
  echo -e "  ${RED}❌ 실패: ${EXPRESS_FAILED}${NC}"

  if [ $EXPRESS_EXIT -ne 0 ]; then
    echo -e "\n${YELLOW}실패한 테스트 상세 정보는 로그를 확인하세요.${NC}"
  fi
else
  echo -e "${YELLOW}⚠️  Express 프로젝트를 찾을 수 없습니다.${NC}\n"
fi

echo ""

# 2. FastAPI 테스트 실행
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}${BOLD}🐍 FastAPI (Python) 테스트${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

if [ -d "app" ] && [ -f "pyproject.toml" ]; then
  echo "프레임워크: pytest"

  # FastAPI 테스트 실행 (병렬)
  FASTAPI_START=$(date +%s)

  if poetry run pytest -v --tb=short 2>&1 | tee /tmp/fastapi-test.log; then
    FASTAPI_EXIT=0
  else
    FASTAPI_EXIT=$?
  fi

  FASTAPI_END=$(date +%s)
  FASTAPI_TIME=$((FASTAPI_END - FASTAPI_START))

  # 결과 파싱 (pytest 출력)
  FASTAPI_PASSED=$(grep -o "passed" /tmp/fastapi-test.log | wc -l || echo "0")
  FASTAPI_FAILED=$(grep -o "failed" /tmp/fastapi-test.log | wc -l || echo "0")

  echo -e "\n실행 시간: ${FASTAPI_TIME}초\n"
  echo "결과:"
  echo -e "  ${GREEN}✅ 통과: ${FASTAPI_PASSED}${NC}"
  echo -e "  ${RED}❌ 실패: ${FASTAPI_FAILED}${NC}"

  if [ $FASTAPI_EXIT -ne 0 ]; then
    echo -e "\n${YELLOW}실패한 테스트 상세 정보는 로그를 확인하세요.${NC}"
  fi
else
  echo -e "${YELLOW}⚠️  FastAPI 프로젝트를 찾을 수 없습니다.${NC}\n"
fi

echo ""

# 3. 통합 요약
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}${BOLD}📊 통합 요약${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

TOTAL_PASSED=$((EXPRESS_PASSED + FASTAPI_PASSED))
TOTAL_FAILED=$((EXPRESS_FAILED + FASTAPI_FAILED))
TOTAL_TESTS=$((TOTAL_PASSED + TOTAL_FAILED))
MAX_TIME=$((EXPRESS_TIME > FASTAPI_TIME ? EXPRESS_TIME : FASTAPI_TIME))

if [ $TOTAL_TESTS -gt 0 ]; then
  SUCCESS_RATE=$(awk "BEGIN {printf \"%.1f\", ($TOTAL_PASSED/$TOTAL_TESTS)*100}")
else
  SUCCESS_RATE="0.0"
fi

echo "총 테스트: ${TOTAL_TESTS}개"
echo -e "  ${GREEN}✅ 통과: ${TOTAL_PASSED} (${SUCCESS_RATE}%)${NC}"
echo -e "  ${RED}❌ 실패: ${TOTAL_FAILED}${NC}"
echo ""
echo "총 실행 시간: ${MAX_TIME}초 (병렬 실행)"

echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

# 종료 코드 결정
if [ $TOTAL_FAILED -gt 0 ]; then
  echo -e "${RED}${BOLD}❌ 테스트 실패${NC}"
  exit 1
else
  echo -e "${GREEN}${BOLD}✅ 모든 테스트 통과!${NC}"
  exit 0
fi
