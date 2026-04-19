---
name: builder-validation
category: meta
description: "验证 builder 生成的项目是否完整、正确"
tags: [builder, validation, meta, testing]
---

# Builder Validation

## 用途

**元技能（Meta Skill）**：用于验证 agent-builder 自身生成的项目是否包含所有必需的章节和文件。

此 Skill 不会被复制到生成的项目中，仅在 agent-builder 仓库内使用。

### 何时使用
- 修改了 `templates/` 下的模板文件后
- 修改了 `builder/build.py` 的生成逻辑后
- 新增了必需章节到模板中后

### 何时不使用
- 此 Skill 不适用于生成的项目

## 验证清单

Builder 生成的项目必须通过以下验证：

### 文件完整性
- [ ] `agents/dev-workflow.agent.md` 存在
- [ ] `requirements.md` 存在
- [ ] `daily-plan.md` 存在
- [ ] `docs/skill-feedback.md` 存在
- [ ] `skills/` 目录包含选中的 skills

### Agent 必需章节
- [ ] Python 环境（`.venv/` 规则）
- [ ] 代码质量要求（行数限制、警告限制）
- [ ] 重构策略（自适应触发条件）
- [ ] 测试要求（每日测试通过）
- [ ] 硬件假设（默认硬件可用）
- [ ] 禁止事项（常见错误清单）
- [ ] Skill 反馈（反馈循环机制）

### 模板变量
- [ ] 所有 `{{VARIABLE}}` 已替换，无遗留占位符

## Self-Test

```bash
bash skills/builder-validation/self-test.sh
```

验证项目：
1. `builder_executable` — builder CLI 可执行
2. `build_e2e` — 完整构建 + 验证通过
3. `agent_required_sections` — Agent 包含所有必需章节
4. `no_unreplaced_variables` — 无未替换的模板变量
5. `required_files_exist` — 必需文件全部生成
6. `skills_copied` — Skills 目录包含 skills
7. `detect_missing_sections` — 能检测缺失章节（负面测试）

## Blind Test

### Prompt
> 我修改了 workflow-agent 模板，删除了「禁止事项」章节。运行 builder 生成一个新项目，验证是否能检测到缺失。

### 验收标准
- [ ] Builder 输出 `[7/7] 验证生成结果...`
- [ ] 缺失章节被标记为 `✗ Agent 缺失章节: 禁止事项`
- [ ] Builder 以非零退出码退出
- [ ] 输出包含 `⚠ 验证结果: X 通过, Y 失败`
