# Agent Builder

[中文版](README_zh.md)

A meta-project for building AI development agents.

Agent Builder contains no actual project code. It is a **skill library + agent generator** that collects requirements through conversation, then generates a complete set of AI agent project files to help AI autonomously develop the user's target project.

## Core Concept

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
  Reusable Skills   Requirement        Generate Target
  (tmux, CDP,       Collection         Agent Project
   ESP32, ...)      (interactive)      (workflow agent +
                                        skills + docs)
```

## Directory Structure

```
agent-builder/
├── README.md                        # English README
├── README_zh.md                     # Chinese README
├── .github/
│   ├── copilot-instructions.md     # Repo-level AI instructions
│   └── agents/
│       ├── builder.agent.md        # Builder main agent
│       ├── iterator.agent.md       # Feature iteration agent
│       └── skill-tester.agent.md   # Skill testing agent
├── skills/                          # Reusable skill library
│   ├── tmux-multi-shell/           # tmux multi-terminal management
│   ├── cdp-web-inspector/          # CDP browser inspection tools
│   ├── esp32-serial-tools/         # ESP32 serial tools
│   ├── esp32-build-flash/          # ESP32 build & flash
│   ├── daily-iteration/            # Daily iteration workflow
│   ├── automated-testing/          # Automated testing framework
│   ├── code-refactoring/           # Code refactoring strategies
│   ├── web-page-inspector/         # Web page inspection & scraping
│   ├── environment-setup/          # Dev environment setup & check
│   └── project-scaffolding/        # Project scaffolding generator
├── templates/                       # Generation templates
│   ├── workflow-agent.agent.md     # Workflow agent template
│   ├── requirements.md             # Requirements doc template
│   └── daily-plan.md              # Daily plan template
├── builder/                         # Builder engine
│   ├── __init__.py                 # Public API exports
│   ├── build.py                    # CLI entry point
│   └── config.py                   # Project config schema
├── docs/
│   └── SKILL_DEVELOPMENT.md        # Skill development guide
├── prompts/
│   └── gather-requirements.prompt.md
└── examples/
    └── esp32-cam/                  # Example: ESP-CAM project output
```

## Usage

### Interactive Mode (Recommended)

Open this project in VS Code and chat with the `@builder` agent:

```
@builder I want to build an ESP-CAM project that streams live camera
feed to a browser and displays temperature/humidity sensor data
```

The Builder Agent will:
1. Confirm project goals, tech stack, and acceptance criteria
2. Select applicable skills
3. Generate a complete agent project in the specified directory

### CLI Mode

```bash
# List all available skills
python -m builder.build --list-skills

# Preview generated content (dry run, no files written)
python -m builder.build \
  --config examples/esp32-cam/project-config.yaml \
  --output /path/to/output --dry-run

# Generate for real
python -m builder.build \
  --config examples/esp32-cam/project-config.yaml \
  --output /path/to/target-project/.copilot
```

## Generated Output

The builder generates an agent project containing:

| File | Purpose |
|------|---------|
| `workflow-agent.agent.md` | Workflow agent that drives daily iterative development |
| `requirements.md` | Project requirements and acceptance criteria |
| `daily-plan.md` | Daily work plan template |
| `skills/` | Selected skill files based on requirements |

## Agents

| Agent | Purpose | Invocation |
|-------|---------|------------|
| `builder` | Collect requirements via conversation, generate agent files | `@builder` |
| `iterator` | Review project status, discover improvements, implement iterations | `@iterator` |
| `skill-tester` | Batch execute Self-Test / Blind Test, generate test reports | `@skill-tester` |

## Skills Catalog

Every skill includes **Self-Test** and **Blind Test** to ensure quality and usability.

| Skill | Description | Category |
|-------|-------------|----------|
| `tmux-multi-shell` | tmux multi-window management (build/flash/serial monitor) | dev-tools |
| `cdp-web-inspector` | Chrome DevTools Protocol browser automation | web-tools |
| `esp32-serial-tools` | ESP32 serial communication & log monitoring | hardware |
| `esp32-build-flash` | ESP-IDF build & flash workflow | hardware |
| `daily-iteration` | Daily iteration planning & execution | workflow |
| `automated-testing` | Automated testing (serial validation + Web UI verification) | quality |
| `code-refactoring` | Periodic code refactoring strategies | quality |
| `web-page-inspector` | Web page content inspection & data extraction | web-tools |
| `environment-setup` | Dev environment check & configuration (toolchains, drivers, deps) | dev-tools |
| `project-scaffolding` | Project scaffolding (directory structure, CMake, HTML templates) | workflow |

## Skill Quality Assurance

Every skill must include two layers of testing:

- **Self-Test**: Automatically executable validation, outputs `SELF_TEST_PASS` / `SELF_TEST_FAIL`
- **Blind Test**: Simulated first-use scenario test (Prompt + acceptance criteria)

See [`docs/SKILL_DEVELOPMENT.md`](docs/SKILL_DEVELOPMENT.md) for details.

## License

MIT
