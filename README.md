# Agent Builder

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
├── README.md
├── .github/
│   └── copilot-instructions.md     # 仓库级 AI 指令
├── agents/
│   └── builder.agent.md            # Builder 主 Agent 定义
├── skills/                          # 可复用 Skill 库
│   ├── tmux-multi-shell/           # tmux 多终端管理
│   ├── cdp-web-inspector/          # CDP 浏览器检查工具
│   ├── esp32-serial-tools/         # ESP32 串口工具
│   ├── esp32-build-flash/          # ESP32 编译烧录
│   ├── daily-iteration/            # 每日迭代工作流
│   ├── automated-testing/          # 自动化测试框架
│   ├── code-refactoring/           # 代码重构策略
│   └── web-page-inspector/         # Web 页面检查与数据抓取
├── templates/                       # 生成模板
│   ├── workflow-agent.agent.md     # 工作流 Agent 模板
│   ├── requirements.md             # 需求文档模板
│   └── daily-plan.md              # 每日计划模板
├── builder/                         # 构建引擎
│   ├── __init__.py
│   ├── build.py                    # CLI 入口
│   └── config.py                   # 项目配置 schema
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

## Skills 清单

| Skill | 描述 |
|-------|------|
| `tmux-multi-shell` | tmux 多窗口管理（编译/烧录/串口监控） |
| `cdp-web-inspector` | Chrome DevTools Protocol 浏览器自动化 |
| `esp32-serial-tools` | ESP32 串口通信与日志监控 |
| `esp32-build-flash` | ESP-IDF 编译与烧录工作流 |
| `daily-iteration` | 每日迭代计划与执行 |
| `automated-testing` | 自动化测试（串口验证 + Web UI 验证） |
| `code-refactoring` | 周期性代码重构策略 |
| `web-page-inspector` | Web 页面内容检查与数据提取 |

## License

MIT
