# Agent Builder - Copilot Instructions

## 项目定位

这是一个 **agent 构建器** 项目，用于生成其他项目所需的 AI agent 文件。
本项目不包含实际的代码项目，只包含 skills 库、模板和构建逻辑。

## 工作规则

1. **不要修改 skills/ 下的文件内容**，除非用户明确要求改进某个 skill
2. **不要在本项目中创建实际的代码项目**（如 ESP32 固件代码）
3. 生成的 agent 项目应输出到 `examples/` 或用户指定的外部目录
4. 所有 skill 文件必须遵循 `SKILL.md` 格式规范
5. Agent 文件必须遵循 `.agent.md` 格式规范

## Skill 编写规范

每个 Skill 文件 (`SKILL.md`) 必须包含：
- 清晰的用途描述（何时使用、何时不使用）
- 前置条件和依赖
- 具体的操作步骤
- 可验证的成功标准

## 模板变量

生成模板使用 `{{variable}}` 占位符，由 builder 引擎替换：
- `{{PROJECT_NAME}}` - 项目名称
- `{{PROJECT_DESCRIPTION}}` - 项目描述
- `{{TARGET_HARDWARE}}` - 目标硬件平台
- `{{SKILLS_LIST}}` - 选中的 skills 列表
- `{{ACCEPTANCE_CRITERIA}}` - 验收标准
