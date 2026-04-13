# VS Code Copilot File Placement Rules

## Correct Paths (MUST follow)

| File Type | Correct Path | WRONG Path |
|-----------|-------------|------------|
| `*.agent.md` | `.github/agents/` | ~~`.github/`~~, ~~`agents/`~~ |
| `copilot-instructions.md` | `.github/` | |
| `*.instructions.md` | `.github/instructions/` | |
| `*.prompt.md` | `.github/prompts/` | |
| `SKILL.md` | `.github/skills/<name>/` | |
| Hooks (`*.json`) | `.github/hooks/` | |

## Lesson Learned
- 2026-04-13: Generated project placed `.agent.md` in `.github/` instead of `.github/agents/`. Agent was not discoverable by VS Code.
