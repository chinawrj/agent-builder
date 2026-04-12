# Skill 开发指南

本文档定义了 Agent Builder 中 Skill 的编写规范、自测标准和贡献流程。

## SKILL.md 标准结构

每个 Skill 放在 `skills/<skill-name>/SKILL.md`，必须包含以下章节：

```markdown
# Skill: <名称>

## 用途
描述 Skill 的适用场景。必须包含：
- **何时使用** - 触发条件列表
- **何时不使用** - 排除条件

## 前置条件
列出所有必需的工具、环境、依赖。

## 操作步骤
具体的操作指令，包含可直接复制执行的代码/命令。
- 使用 `{{VARIABLE}}` 模板变量标记需要替换的部分
- 每个步骤应该是原子性的（可独立执行或验证）

## Self-Test（自检）               ← 必须
验证 Skill 指令在当前环境下是否有效的测试。

### 自检步骤
可直接执行的测试命令，每条输出 SELF_TEST_PASS 或 SELF_TEST_FAIL。

### 预期结果
测试项与预期输出的对照表。

### Blind Test（盲测）              ← 必须
模拟 AI Agent 首次使用此 Skill 的测试场景。
包含：测试 Prompt + 验收标准。

## 成功标准
可勾选的核查清单（checkbox list）。
```

## Self-Test 规范

### 设计原则

1. **可自动执行** - 测试命令可以被 AI Agent 或脚本直接运行
2. **输出标准化** - 每项测试输出 `SELF_TEST_PASS: <name>` 或 `SELF_TEST_FAIL: <name>`
3. **无副作用** - 测试不应修改系统状态；创建的临时资源必须清理
4. **快速执行** - 单个 Skill 的自检应在 30 秒内完成
5. **分层测试** - 先验证前置条件，再测试核心功能

### Self-Test 分类

| 类型 | 目的 | 执行时机 |
|------|------|---------|
| **前置条件检查** | 验证工具/依赖是否可用 | 首次使用 Skill 时 |
| **指令正确性** | 验证 Skill 中的命令可执行 | Skill 更新后 |
| **输出格式** | 验证输出符合预期格式 | Skill 更新后 |

### Self-Test 模板

```bash
#!/bin/bash
# self-test for <skill-name>
# 运行: bash skills/<skill-name>/self-test.sh

PASS=0
FAIL=0

test_case() {
    local name=$1
    shift
    if "$@" &>/dev/null; then
        echo "SELF_TEST_PASS: $name"
        PASS=$((PASS + 1))
    else
        echo "SELF_TEST_FAIL: $name"
        FAIL=$((FAIL + 1))
    fi
}

# --- 测试用例 ---
test_case "tool_exists" command -v <tool>
test_case "config_valid" test -f <config-file>

# --- 汇总 ---
echo ""
echo "Results: $PASS passed, $FAIL failed"
exit $FAIL
```

## Blind Test 规范

### 什么是 Blind Test

Blind Test 模拟一个**全新的 AI Agent**（没有上下文、没有记忆）首次阅读此 Skill 后能否独立完成任务。

目的：
- 验证 Skill 描述是否足够清晰和完整
- 发现遗漏的步骤或隐含假设
- 确保 Skill 可被不同的 AI 模型正确理解

### Blind Test 结构

```markdown
### Blind Test（盲测）

**场景描述:**
一句话描述测试场景的背景。

**测试 Prompt:**
直接给 AI Agent 的完整指令，不包含额外上下文。

**验收标准:**
- [ ] 标准1: Agent 的具体行为/输出要求
- [ ] 标准2: ...
- [ ] 标准3: ...

**常见失败模式:**
- 失败模式1: Agent 跳过了 XX 步骤 → 需要在 Skill 中强调
- 失败模式2: Agent 使用了错误的工具 → 需要明确排除
```

### 执行方式

1. **手动盲测**: 开一个新的 AI 对话，只提供 SKILL.md 内容和测试 Prompt
2. **自动盲测**: 通过 builder 引擎调用（规划中）

## 新增 Skill 流程

1. 在 `skills/` 下创建目录：`skills/<skill-name>/`
2. 编写 `SKILL.md`，遵循上述结构
3. 编写 Self-Test（可内嵌在 SKILL.md 中，也可单独 `self-test.sh`）
4. 在 `builder/config.py` 的 `SKILL_CATALOG` 中注册
5. 执行 Self-Test 确认通过
6. 找一个同事/AI 做 Blind Test
7. 提交 PR

## 模板变量约定

| 变量 | 用途 | 示例 |
|------|------|------|
| `{{PROJECT_NAME}}` | 项目名称 | `esp32-cam` |
| `{{PROJECT_DESCRIPTION}}` | 项目描述 | `ESP32 摄像头项目` |
| `{{TARGET_HARDWARE}}` | 目标硬件 | `esp32`, `esp32s3` |
| `{{DEVICE_IP}}` | 设备 IP 地址 | `192.168.1.100` |
| `{{SERIAL_PORT}}` | 串口路径 | `/dev/ttyUSB0` |
| `{{SKILLS_LIST}}` | 选中的 skills 列表 | Markdown 列表 |
| `{{ACCEPTANCE_CRITERIA}}` | 验收标准 | Checkbox 列表 |
| `{{FEATURES}}` | 功能列表 | Markdown 列表 |
| `{{MILESTONES}}` | 里程碑 | Markdown 标题+描述 |
| `{{BUILDER_VERSION}}` | Builder 版本号 | `0.2.0` |
