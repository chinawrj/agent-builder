#!/bin/bash
# self-test for builder-validation
# 运行: bash skills/builder-validation/self-test.sh
#
# 验证 builder 生成的项目是否包含所有必需章节和文件

set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BUILDER_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

PASS=0
FAIL=0

test_pass() { echo "SELF_TEST_PASS: $1"; PASS=$((PASS + 1)); }
test_fail() { echo "SELF_TEST_FAIL: $1"; FAIL=$((FAIL + 1)); }

# --- Test 1: Builder 可执行 ---
if python3 -m builder.build --version 2>/dev/null | grep -q "agent-builder"; then
  test_pass "builder_executable"
else
  test_fail "builder_executable"
fi

# --- Test 2: 完整构建 + 验证通过 ---
TMP=$(mktemp -d)
CONFIG="$BUILDER_ROOT/examples/esp32-cam/project-config.yaml"
if [ ! -f "$CONFIG" ]; then
  test_fail "build_e2e (config not found)"
else
  OUTPUT=$(cd "$BUILDER_ROOT" && python3 -m builder.build --config "$CONFIG" --output "$TMP/out" 2>&1)
  if echo "$OUTPUT" | grep -q "验证全部通过"; then
    test_pass "build_e2e"
  else
    test_fail "build_e2e"
    echo "  Output: $(echo "$OUTPUT" | tail -5)"
  fi
fi

# --- Test 3: Agent 包含所有必需章节 ---
AGENT_FILE="$TMP/out/agents/dev-workflow.agent.md"
if [ -f "$AGENT_FILE" ]; then
  ALL_FOUND=true
  for section in "Python" "代码质量要求|Code Quality" "重构策略|Code Refactoring" "测试要求|Test Requirements" "硬件假设|Hardware Assumptions" "禁止事项|Things to Avoid" "Skill 反馈|Skill Feedback"; do
    if ! grep -qiE "$section" "$AGENT_FILE"; then
      ALL_FOUND=false
      echo "  Missing section: $section"
      break
    fi
  done
  if $ALL_FOUND; then
    test_pass "agent_required_sections"
  else
    test_fail "agent_required_sections"
  fi
else
  test_fail "agent_required_sections (file missing)"
fi

# --- Test 4: 无未替换的模板变量 ---
if [ -f "$AGENT_FILE" ]; then
  UNREPLACED=$(grep -oE '\{\{[A-Z_]+\}\}' "$AGENT_FILE" || true)
  if [ -z "$UNREPLACED" ]; then
    test_pass "no_unreplaced_variables"
  else
    test_fail "no_unreplaced_variables ($UNREPLACED)"
  fi
else
  test_fail "no_unreplaced_variables (file missing)"
fi

# --- Test 5: 必需文件全部生成 ---
ALL_FILES=true
for f in "agents/dev-workflow.agent.md" "requirements.md" "daily-plan.md" "docs/skill-feedback.md"; do
  if [ ! -f "$TMP/out/$f" ]; then
    ALL_FILES=false
    break
  fi
done
if $ALL_FILES; then
  test_pass "required_files_exist"
else
  test_fail "required_files_exist"
fi

# --- Test 6: Skills 目录包含 skills ---
SKILL_COUNT=$(find "$TMP/out/skills" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')
if [ "$SKILL_COUNT" -gt 0 ]; then
  test_pass "skills_copied ($SKILL_COUNT skills)"
else
  test_fail "skills_copied"
fi

# --- Test 7: validate_generated_agent 检测缺失章节 ---
if [ -f "$AGENT_FILE" ]; then
  BROKEN=$(mktemp -d)
  mkdir -p "$BROKEN/agents"
  sed '/禁止事项/d' "$AGENT_FILE" > "$BROKEN/agents/dev-workflow.agent.md"
  RESULT=$(cd "$BUILDER_ROOT" && python3 -c "
from builder.build import validate_generated_agent
p, f = validate_generated_agent('$BROKEN/agents/dev-workflow.agent.md')
for name in f:
    print('missing: ' + name)
" 2>&1)
  if echo "$RESULT" | grep -q "missing:"; then
    test_pass "detect_missing_sections"
  else
    test_fail "detect_missing_sections"
    echo "  Output: $RESULT"
  fi
  rm -rf "$BROKEN"
else
  test_fail "detect_missing_sections (file missing)"
fi

# --- 清理 ---
rm -rf "$TMP"

# --- 汇总 ---
echo ""
echo "Results: $PASS passed, $FAIL failed"
exit $FAIL
