# Agent Builder

[English](README.md)

一个用于构建项目开发 Agent 的元项目（Meta-project）。

Agent Builder 本身不包含任何实际代码项目。它是一个 **skill 库 + agent 生成器**，通过与用户对话收集需求，然后生成一套完整的 AI agent 项目文件，帮助 AI 自主开发用户的目标项目。

## 核心概念

```
┌─────────────────────────────────────────────────────────┐
│                    Agent Builder                         │
│                                                         │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Skills   │  │ Interview    │  │ Builder Engine   │  │
│  │ Library  │──│ Agent        │──│ (generator)      │  │
│  └──────────┘  └──────────────┘  └──────────────────┘  │
│       │               │                   │             │
└───────┼───────────────┼───────────────────┼─────────────┘
        │               │                   │
        ▼               ▼                   ▼
  可复用技能       用户需求收集        生成目标 Agent 项目
  (tmux, CDP,     (对话式确认         (workflow agent +
   ESP32, ...)     目标/指标)          skills + 需求文档)
```

## 目录结构

```
agent-builder/
├── README.md                        # English README
├── README_zh.md                     # 中文 README
├── .github/
│   └── copilot-instructions.md     # 仓库级 AI 指令
├── agents/
│   ├── builder.agent.md            # Builder 主 Agent 定义
│   ├── iterator.agent.md           # 功能迭代 Agent
│   └── skill-tester.agent.md       # Skill 测试 Agent
├── skills/                          # 可复用 Skill 库
│   ├── tmux-multi-shell/           # tmux 多终端管理
│   ├── cdp-web-inspector/          # CDP 浏览器检查工具
│   ├── esp32-serial-tools/         # ESP32 串口工具
│   ├── esp32-build-flash/          # ESP32 编译烧录
│   ├── daily-iteration/            # 每日迭代工作流
│   ├── automated-testing/          # 自动化测试框架
│   ├── code-refactoring/           # 代码重构策略
│   ├── web-page-inspector/         # Web 页面检查与数据抓取
│   ├── environment-setup/          # 开发环境检查与配置
│   └── project-scaffolding/        # 项目脚手架生成
├── templates/                       # 生成模板
│   ├── workflow-agent.agent.md     # 工作流 Agent 模板
│   ├── requirements.md             # 需求文档模板
│   └── daily-plan.md              # 每日计划模板
├── builder/                         # 构建引擎
│   ├── __init__.py                 # 公共 API 导出
│   ├── build.py                    # CLI 入口
│   └── config.py                   # 项目配置 schema
├── docs/
│   └── SKILL_DEVELOPMENT.md        # Skill 开发指南
├── prompts/
│   └── gather-requirements.prompt.md
└── examples/
    └── esp32-cam/                  # 示例：ESP-CAM 项目输出
```

## 使用方式

### 交互模式（推荐）

在 VS Code 中打开此项目，使用 `@builder` agent 与 AI 对话：

```
@builder 我想做一个 ESP-CAM 项目，需要通过浏览器实时查看摄像头画面，
并显示温度/湿度传感器数据
```

Builder Agent 会：
1. 确认项目目标、技术栈、验收指标
2. 选择适用的 skills
3. 在指定目录生成完整的 agent 项目

### CLI 模式

```bash
# 列出所有可用 skills
python -m builder.build --list-skills

# 预览生成内容（不写入文件）
python -m builder.build \
  --config examples/esp32-cam/project-config.yaml \
  --output /path/to/output --dry-run

# 正式生成
python -m builder.build \
  --config examples/esp32-cam/project-config.yaml \
  --output /path/to/target-project/.copilot
```

## 生成内容

Builder 生成的 agent 项目包含：

| 文件 | 用途 |
|------|------|
| `workflow-agent.agent.md` | 工作流 Agent，驱动每日迭代开发 |
| `requirements.md` | 项目需求与验收指标 |
| `daily-plan.md` | 每日工作计划模板 |
| `skills/` | 根据需求选择的 skill 文件 |

## Agents

| Agent | 用途 | 调用方式 |
|-------|------|----------|
| `builder` | 通过对话收集需求，生成项目 agent 文件 | `@builder` |
| `iterator` | 审查项目现状，发现改进点，实施迭代优化 | `@iterator` |
| `skill-tester` | 批量执行 Self-Test / Blind Test，生成测试报告 | `@skill-tester` |

## Skills 清单

每个 Skill 都包含 **Self-Test（自检）** 和 **Blind Test（盲测）**，确保质量和可用性。

| Skill | 描述 | 分类 |
|-------|------|------|
| `tmux-multi-shell` | tmux 多窗口管理（编译/烧录/串口监控） | dev-tools |
| `cdp-web-inspector` | Chrome DevTools Protocol 浏览器自动化 | web-tools |
| `esp32-serial-tools` | ESP32 串口通信与日志监控 | hardware |
| `esp32-build-flash` | ESP-IDF 编译与烧录工作流 | hardware |
| `daily-iteration` | 每日迭代计划与执行 | workflow |
| `automated-testing` | 自动化测试（串口验证 + Web UI 验证） | quality |
| `code-refactoring` | 周期性代码重构策略 | quality |
| `web-page-inspector` | Web 页面内容检查与数据提取 | web-tools |
| `environment-setup` | 开发环境检查与配置（工具链、驱动、依赖） | dev-tools |
| `project-scaffolding` | 项目脚手架生成（目录结构、CMake、HTML 模板） | workflow |

## Skill 质量保证

每个 Skill 必须包含两层测试：

- **Self-Test**: 可自动执行的验证，输出 `SELF_TEST_PASS` / `SELF_TEST_FAIL`
- **Blind Test**: 模拟 AI 首次使用的场景测试（Prompt + 验收标准）

详见 [`docs/SKILL_DEVELOPMENT.md`](docs/SKILL_DEVELOPMENT.md)。

## License

MIT
