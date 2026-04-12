#!/usr/bin/env python3
"""Agent Builder CLI - 从 skill 库生成项目专属 AI agent 文件"""

import argparse
import os
import re
import shutil
import sys

from .config import ProjectConfig, SKILL_CATALOG, VERSION, recommend_skills


BUILDER_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_DIR = os.path.join(BUILDER_ROOT, "skills")
TEMPLATES_DIR = os.path.join(BUILDER_ROOT, "templates")


def copy_skills(skill_names: list[str], output_dir: str, dry_run: bool = False):
    """复制选中的 skills 到输出目录"""
    skills_out = os.path.join(output_dir, "skills")
    missing = []

    for name in skill_names:
        src = os.path.join(SKILLS_DIR, name)
        skill_md = os.path.join(src, "SKILL.md")
        if not os.path.isdir(src) or not os.path.isfile(skill_md):
            missing.append(name)
            continue

        if not dry_run:
            dst = os.path.join(skills_out, name)
            os.makedirs(skills_out, exist_ok=True)
            shutil.copytree(src, dst, dirs_exist_ok=True)
        print(f"  ✓ {name}")

    if missing:
        raise FileNotFoundError(f"以下 skill 不存在或缺少 SKILL.md: {', '.join(missing)}")


def render_template(template_name: str, variables: dict) -> str:
    """简单的模板渲染（{{variable}} 替换）"""
    template_path = os.path.join(TEMPLATES_DIR, template_name)
    if not os.path.isfile(template_path):
        raise FileNotFoundError(f"模板文件不存在: {template_path}")

    with open(template_path) as f:
        content = f.read()

    for key, value in variables.items():
        if isinstance(value, list):
            value = "\n".join(f"- {item}" for item in value)
        content = content.replace(f"{{{{{key}}}}}", str(value))

    # 检查是否有未替换的变量
    unreplaced = re.findall(r"\{\{(\w+)\}\}", content)
    if unreplaced:
        print(f"  ⚠ 模板 {template_name} 中有未替换的变量: {', '.join(unreplaced)}", file=sys.stderr)

    return content


def _format_milestones(milestones: list[dict]) -> str:
    """格式化里程碑列表为 Markdown"""
    if not milestones:
        return "*(暂未定义里程碑)*"
    parts = []
    for i, m in enumerate(milestones, 1):
        name = (m.get("name") or f"M{i}").strip()
        desc = (m.get("description") or "").strip()
        parts.append(f"### Milestone {i}: {name}\n\n{desc}")
    return "\n\n".join(parts)


def build_variables(config: ProjectConfig) -> dict:
    """从配置构建模板变量字典"""
    return {
        "PROJECT_NAME": config.name,
        "PROJECT_DESCRIPTION": config.description,
        "TARGET_HARDWARE": config.target_hardware,
        "SKILLS_LIST": "\n".join(
            f"- `{s}`: {SKILL_CATALOG.get(s, {}).get('description', s)}"
            for s in config.skills
        ),
        "ACCEPTANCE_CRITERIA": "\n".join(
            f"- [ ] {c}" for c in config.acceptance_criteria
        ) or "*(暂未定义验收标准)*",
        "FEATURES": "\n".join(f"- {f}" for f in config.features) or "*(暂未定义功能)*",
        "MILESTONES": _format_milestones(config.milestones),
        "BUILDER_VERSION": VERSION,
    }


def generate_project(config: ProjectConfig, output_dir: str, dry_run: bool = False):
    """生成完整的 agent 项目"""
    output_dir = os.path.abspath(output_dir)
    mode = "[DRY RUN] " if dry_run else ""

    print(f"{mode}生成 Agent 项目: {config.name}")
    print(f"{mode}输出目录: {output_dir}")
    print()

    if not dry_run:
        os.makedirs(output_dir, exist_ok=True)

    # 1. 复制 Skills
    print("[1/4] 复制 Skills...")
    if not config.skills:
        config.skills = recommend_skills(config)
        print(f"  (自动推荐 {len(config.skills)} 个 skills)")
    copy_skills(config.skills, output_dir, dry_run=dry_run)
    print()

    # 2. 构建模板变量
    variables = build_variables(config)

    # 3. 生成工作流 Agent
    print("[2/4] 生成工作流 Agent...")
    agent_content = render_template("workflow-agent.agent.md", variables)
    agent_path = os.path.join(output_dir, "agents", "dev-workflow.agent.md")
    if not dry_run:
        os.makedirs(os.path.dirname(agent_path), exist_ok=True)
        with open(agent_path, "w") as f:
            f.write(agent_content)
    print(f"  ✓ agents/dev-workflow.agent.md")
    print()

    # 4. 生成需求文档
    print("[3/4] 生成需求文档...")
    req_content = render_template("requirements.md", variables)
    req_path = os.path.join(output_dir, "requirements.md")
    if not dry_run:
        with open(req_path, "w") as f:
            f.write(req_content)
    print(f"  ✓ requirements.md")
    print()

    # 5. 生成每日计划模板
    print("[4/4] 生成每日计划模板...")
    plan_content = render_template("daily-plan.md", variables)
    plan_path = os.path.join(output_dir, "daily-plan.md")
    if not dry_run:
        with open(plan_path, "w") as f:
            f.write(plan_content)
    print(f"  ✓ daily-plan.md")
    print()

    print("=" * 50)
    print(f"{mode}Agent 项目已生成到: {output_dir}")
    print(f"包含 {len(config.skills)} 个 skills | builder v{VERSION}")


def list_skills():
    """列出所有可用 skills"""
    print(f"Agent Builder v{VERSION} - 可用 Skills")
    print("=" * 60)

    categories = {}
    for name, info in SKILL_CATALOG.items():
        cat = info["category"]
        categories.setdefault(cat, []).append((name, info))

    for cat in sorted(categories):
        print(f"\n[{cat}]")
        for name, info in sorted(categories[cat]):
            skill_dir = os.path.join(SKILLS_DIR, name)
            exists = "✓" if os.path.isdir(skill_dir) else "✗"
            print(f"  {exists} {name:<24} {info['description']}")
            if info.get("tags"):
                print(f"    tags: {', '.join(info['tags'])}")


def main():
    parser = argparse.ArgumentParser(
        description=f"Agent Builder v{VERSION} - 生成项目专属 AI agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""示例:
  python -m builder.build --list-skills
  python -m builder.build --config project.yaml --output ./output
  python -m builder.build --config project.yaml --output ./output --dry-run
""",
    )
    parser.add_argument("--config", help="项目配置 YAML 文件路径")
    parser.add_argument("--output", help="输出目录路径")
    parser.add_argument("--dry-run", action="store_true", help="预览生成内容，不实际写入文件")
    parser.add_argument("--list-skills", action="store_true", help="列出所有可用 skills")
    parser.add_argument("--version", action="version", version=f"agent-builder {VERSION}")
    args = parser.parse_args()

    try:
        if args.list_skills:
            list_skills()
            return

        if not args.config or not args.output:
            parser.error("--config 和 --output 为必填项（除非使用 --list-skills）")

        config = ProjectConfig.from_yaml(args.config)
        generate_project(config, args.output, dry_run=args.dry_run)

    except FileNotFoundError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"配置无效: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"未知错误: {e}", file=sys.stderr)
        sys.exit(3)

    config = ProjectConfig.from_yaml(args.config)
    generate_project(config, args.output)


if __name__ == "__main__":
    main()
