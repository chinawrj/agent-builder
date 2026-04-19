#!/bin/bash
# 探测包含指定模块的 Python 解释器
# 用法: source skills/_common/detect-python.sh
#       PYTHON=$(detect_python "patchright.sync_api")

detect_python() {
  local module="${1:-patchright.sync_api}"

  # 1. 项目本地 .venv（优先）
  local project_root="$PWD"
  # 向上查找包含 .venv 的项目根目录
  local dir="$PWD"
  for i in 1 2 3 4; do
    if [ -x "$dir/.venv/bin/python3" ] && "$dir/.venv/bin/python3" -c "import $module" 2>/dev/null; then
      echo "$dir/.venv/bin/python3"
      return 0
    fi
    dir=$(dirname "$dir")
  done

  # 2. 当前 python3（可能已在 venv 中 activate）
  if python3 -c "import $module" 2>/dev/null; then
    echo "python3"
    return 0
  fi

  # 3. 环境变量指定
  if [ -n "$PATCHRIGHT_PYTHON" ] && "$PATCHRIGHT_PYTHON" -c "import $module" 2>/dev/null; then
    echo "$PATCHRIGHT_PYTHON"
    return 0
  fi

  # 4. 其他常见路径（fallback）
  local search_paths=(
    "$HOME/patchright-env/bin/python3"
    "$HOME/.venv/bin/python3"
    "$HOME/venv/bin/python3"
  )

  for p in "${search_paths[@]}"; do
    if [ -x "$p" ] && "$p" -c "import $module" 2>/dev/null; then
      echo "$p"
      return 0
    fi
  done

  return 1
}
