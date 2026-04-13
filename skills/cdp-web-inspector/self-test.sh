#!/bin/bash
# self-test for cdp-web-inspector
# 运行: bash skills/cdp-web-inspector/self-test.sh

PASS=0
FAIL=0
SKIP=0

test_pass() { echo "SELF_TEST_PASS: $1"; PASS=$((PASS + 1)); }
test_fail() { echo "SELF_TEST_FAIL: $1"; FAIL=$((FAIL + 1)); }
skip_case() { echo "SELF_TEST_SKIP: $1 ($2)"; SKIP=$((SKIP + 1)); }

# --- Test 1: patchright 可导入 ---
if python3 -c "from patchright.sync_api import sync_playwright" 2>/dev/null; then
  test_pass "patchright_import"
else
  skip_case "patchright_import" "pip install patchright"
  echo ""; echo "Results: $PASS passed, $FAIL failed, $SKIP skipped"; exit $FAIL
fi

# --- Test 2: chromium 驱动存在 ---
if ls ~/Library/Caches/ms-playwright/chromium-* &>/dev/null || \
   ls ~/.cache/ms-playwright/chromium-* &>/dev/null; then
  test_pass "chromium_driver"
else
  skip_case "chromium_driver" "patchright install chromium"
fi

# --- Test 3: headless 浏览器启动 + 页面操作 ---
if python3 -c "
from patchright.sync_api import sync_playwright
import tempfile
pw = sync_playwright().start()
ctx = pw.chromium.launch_persistent_context(
    user_data_dir=tempfile.mkdtemp(),
    channel='chrome',
    headless=True,
    no_viewport=True,
)
page = ctx.pages[0] if ctx.pages else ctx.new_page()
page.goto('data:text/html,<h1 id=\"t\">hello</h1><p class=\"x\">world</p>')
assert page.locator('h1').text_content() == 'hello'
assert page.locator('p.x').text_content() == 'world'
ctx.close()
pw.stop()
" 2>/dev/null; then
  test_pass "browser_launch_and_query"
else
  test_fail "browser_launch_and_query"
fi

# --- Test 4: JavaScript evaluate ---
if python3 -c "
from patchright.sync_api import sync_playwright
import tempfile
pw = sync_playwright().start()
ctx = pw.chromium.launch_persistent_context(
    user_data_dir=tempfile.mkdtemp(),
    channel='chrome',
    headless=True,
    no_viewport=True,
)
page = ctx.pages[0] if ctx.pages else ctx.new_page()
page.goto('data:text/html,<title>Test Page</title>')
title = page.evaluate('document.title')
assert title == 'Test Page', f'Expected Test Page, got {title}'
ctx.close()
pw.stop()
" 2>/dev/null; then
  test_pass "js_evaluate"
else
  test_fail "js_evaluate"
fi

# --- 汇总 ---
echo ""
echo "Results: $PASS passed, $FAIL failed, $SKIP skipped"
exit $FAIL
