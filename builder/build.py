#!/usr/bin/env python3
"""Agent Builder CLI - 从 skill 库生成项目专属 AI agent 文件"""

import argparse
import os
import shutil
import sys

from .config import ProjectConfig, SKILL_CATALOG, recommend_skills


BUILDER_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_DIR = os.path.join(BUILDER_ROOT, "skills")
TEMPLATES_DIR = os.path.join(BUILDER_ROOT, "templates")


def copy_skills(skill_names: list[str], output_dir: str):
    """复制选中的 skills 到输出目录"""
    skills_out = os.path.join(output_dir, "skills")
    os.makedirs(skills_out, exist_ok=True)

    for name in skill_names:
        src = os.path.join(SKILLS_DIR, name)
        dst = os.path.join(skills_out, name)
        if os.path.isdir(src):
            shutil.copytree(src, dst, dirs_exist_ok=True)
            print(f"  ✓ {name}")
        else:
            print(f"  ✗ {name} (not found)")


def render_template(template_name: str, variables: dict) -> str:
    """简单的模板渲染（{{variable}} 替换）"""
    template_path = os.path.join(TEMPLATES_DIR, template_name)
    with open(template_path) as f:
        content = f.read()

    for key, value in variables.items():
        if isinstance(value, list):
            value = "\n".join(f"- {item}" for item in value)
        content = content.replace(f"{{{{{key}}}}}", str(value))

    return content


def generate_project(config: ProjectConfig, output_dir: str):
    """生成完整的 agent 项目"""
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    print(f"生成 Agent 项目: {config.name}")
    print(f"输出目录: {output_dir}")
    print()

    # 1. 复制 Skills
    print("[1/4] 复制 Skills...")
    if not config.skills:
        config.skills = recommend_skills(config)
    copy_skills(config.skills, output_dir)
    print()

    # 2. 生成工作流 Agent
    print("[2/4] 生成工作流 Agent...")
    agents_dir = os.path.join(output_dir, "agents")
    os.makedirs(agents_dir, exist_ok=True)

    variables = {
        "PROJECT_NAME": config.name,
        "PROJECT_DESCRIPTION": config.description,
        "TARGET_HARDWARE": config.target_hardware,
        "SKILLS_LIST": "\n".join(
            f"- `{s}`: {SKILL_CATALOG.get(s, {}).get('description', s)}"
            for s in config.skills
        ),
        "ACCEPTANCE_CRITERIA": "\n".join(
            f"- [ ] {c}" for c in config.acceptance_criteria
        ),
        "FEATURES": "\n".join(f"- {f}" for f in config.features),
        "MILESTONES": "\n".join(
            f"### Milestone {i+1}: {m.get('name', 'TBD')}\n{m.get('description', '')}"
            for i, m in enumerate(config.milestones)
        ),
    }

    agent_content = render_template("workflow-agent.agent.md", variables)
    agent_path = os.path.join(agents_dir, "dev-workflow.agent.md")
    with open(agent_path, "w") as f:
        f.write(agent_content)
    print(f"  ✓ {agent_path}")
    print()

    # 3. 生成需求文档
    print("[3/4] 生成需求文档...")
    req_content = render_template("requirements.md", variables)
    req_path = os.path.join(output_dir, "requirements.md")
    with open(req_path, "w") as f:
        f.write(req_content)
    print(f"  ✓ {req_path}")
    print()

    # 4. 生成每日计划模板
    print("[4/4] 生成每日计划模板...")
    plan_content = render_template("daily-plan.md", variables)
    plan_path = os.path.join(output_dir, "daily-plan.md")
    with open(plan_path, "w") as f:
        f.write(plan_content)
    print(f"  ✓ {plan_path}")
    print()

    print("=" * 50)
    print(f"Agent 项目已生成到: {output_dir}")
    print(f"包含 {len(config.skills)} 个 skills")


def main():
    parser = argparse.ArgumentParser(description="Agent Builder - 生成项目专属 AI agent")
    parser.add_argument("--config", required=True, help="项目配置 YAML 文件路径")
    parser.add_argument("--output", required=True, help="输出目录路径")
    args = parser.parse_args()

    config = ProjectConfig.from_yaml(args.config)
    generate_project(config, args.output)


if __name__ == "__main__":
    main()
