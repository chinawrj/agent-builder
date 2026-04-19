#!/usr/bin/env python3
"""Agent Builder CLI - 从 skill 库生成项目专属 AI agent 文件"""

import argparse
import os
import re
import shutil
import sys

from .config import ProjectConfig, SKILL_CATALOG, MCP_SERVER_CATALOG, VERSION, recommend_skills, recommend_mcp_servers


BUILDER_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_DIR = os.path.join(BUILDER_ROOT, "skills")
TEMPLATES_DIR = os.path.join(BUILDER_ROOT, "templates")

# 生成结果必须包含的章节（agent 文件验证清单）
REQUIRED_AGENT_SECTIONS = [
    ("Python 环境", "python.*venv|Python Environment|Python 环境"),
    ("代码质量要求", "Code Quality Requirements|代码质量要求"),
    ("重构策略", "Code Refactoring Strategy|重构策略"),
    ("测试要求", "Test Requirements|测试要求"),
    ("硬件假设", "Hardware Assumptions|硬件假设"),
    ("禁止事项", "Things to Avoid|禁止事项"),
    ("Skill 反馈", "Skill Feedback|Skill 反馈"),
]


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



def generate_mcp_config(mcp_names: list[str], output_dir: str, dry_run: bool = False):
    """生成 .vscode/mcp.json 配置文件"""
    import json

    if not mcp_names:
        return

    mcp_servers = {}
    for name in mcp_names:
        info = MCP_SERVER_CATALOG.get(name)
        if not info:
            print(f"  ⚠ 未知 MCP server: {name}")
            continue
        mcp_servers[info["mcp_key"]] = {"url": info["url"]}

    config = {"mcpServers": mcp_servers}

    if not dry_run:
        vscode_dir = os.path.join(output_dir, ".vscode")
        os.makedirs(vscode_dir, exist_ok=True)
        mcp_path = os.path.join(vscode_dir, "mcp.json")
        with open(mcp_path, "w") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
            f.write("\n")

    for name in mcp_names:
        info = MCP_SERVER_CATALOG.get(name, {})
        print(f"  ✓ {info.get('mcp_key', name)} → {info.get('url', '?')}")


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
        "MCP_SERVERS_LIST": "\n".join(
            f"- `{s}`: {MCP_SERVER_CATALOG.get(s, {}).get('description', s)}"
            for s in config.mcp_servers
        ) or "*(无 MCP servers)*",
        "BUILDER_VERSION": VERSION,
    }


def validate_generated_agent(agent_path: str) -> tuple[list[str], list[str]]:
    """验证生成的 agent 文件是否包含所有必需章节。
    
    Returns:
        (passed, failed) — 通过和缺失的章节名列表
    """
    if not os.path.isfile(agent_path):
        return [], [name for name, _ in REQUIRED_AGENT_SECTIONS]

    with open(agent_path) as f:
        content = f.read()

    passed = []
    failed = []
    for section_name, pattern in REQUIRED_AGENT_SECTIONS:
        if re.search(pattern, content, re.IGNORECASE):
            passed.append(section_name)
        else:
            failed.append(section_name)
    return passed, failed


def validate_generated_files(output_dir: str) -> tuple[int, int]:
    """验证生成的所有文件完整性。
    
    Returns:
        (total_pass, total_fail) 计数
    """
    total_pass = 0
    total_fail = 0

    # 检查必需文件存在
    required_files = [
        "agents/dev-workflow.agent.md",
        "requirements.md",
        "daily-plan.md",
        "docs/skill-feedback.md",
    ]
    for rel_path in required_files:
        full_path = os.path.join(output_dir, rel_path)
        if os.path.isfile(full_path):
            print(f"  ✓ 文件存在: {rel_path}")
            total_pass += 1
        else:
            print(f"  ✗ 文件缺失: {rel_path}")
            total_fail += 1

    # 检查 skills 目录
    skills_dir = os.path.join(output_dir, "skills")
    if os.path.isdir(skills_dir):
        skill_count = len([d for d in os.listdir(skills_dir)
                          if os.path.isdir(os.path.join(skills_dir, d)) and not d.startswith("_")])
        if skill_count > 0:
            print(f"  ✓ Skills 目录: {skill_count} 个 skills")
            total_pass += 1
        else:
            print(f"  ✗ Skills 目录为空")
            total_fail += 1
    else:
        print(f"  ✗ Skills 目录不存在")
        total_fail += 1

    # 验证 agent 文件必需章节
    agent_path = os.path.join(output_dir, "agents", "dev-workflow.agent.md")
    passed, failed = validate_generated_agent(agent_path)
    for name in passed:
        print(f"  ✓ Agent 章节: {name}")
        total_pass += 1
    for name in failed:
        print(f"  ✗ Agent 缺失章节: {name}")
        total_fail += 1

    # 检查未替换的模板变量
    for rel_path in required_files:
        full_path = os.path.join(output_dir, rel_path)
        if os.path.isfile(full_path):
            with open(full_path) as f:
                content = f.read()
            unreplaced = re.findall(r"\{\{(\w+)\}\}", content)
            if unreplaced:
                print(f"  ✗ {rel_path} 含未替换变量: {', '.join(unreplaced)}")
                total_fail += 1

    return total_pass, total_fail


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
    print("[1/7] 复制 Skills...")
    if not config.skills:
        config.skills = recommend_skills(config)
        print(f"  (自动推荐 {len(config.skills)} 个 skills)")
    copy_skills(config.skills, output_dir, dry_run=dry_run)
    print()

    # 2. 生成 MCP 配置
    print("[2/7] 生成 MCP 配置...")
    if not config.mcp_servers:
        config.mcp_servers = recommend_mcp_servers(config)
        if config.mcp_servers:
            print(f"  (自动推荐 {len(config.mcp_servers)} 个 MCP servers)")
    if config.mcp_servers:
        generate_mcp_config(config.mcp_servers, output_dir, dry_run=dry_run)
    else:
        print("  (无 MCP servers)")
    print()

    # 3. 构建模板变量
    variables = build_variables(config)

    # 3. 生成工作流 Agent
    print("[3/7] 生成工作流 Agent...")
    agent_content = render_template("workflow-agent.agent.md", variables)
    agent_path = os.path.join(output_dir, "agents", "dev-workflow.agent.md")
    if not dry_run:
        os.makedirs(os.path.dirname(agent_path), exist_ok=True)
        with open(agent_path, "w") as f:
            f.write(agent_content)
    print(f"  ✓ agents/dev-workflow.agent.md")
    print()

    # 4. 生成需求文档
    print("[4/7] 生成需求文档...")
    req_content = render_template("requirements.md", variables)
    req_path = os.path.join(output_dir, "requirements.md")
    if not dry_run:
        with open(req_path, "w") as f:
            f.write(req_content)
    print(f"  ✓ requirements.md")
    print()

    # 5. 生成每日计划模板
    print("[5/7] 生成每日计划模板...")
    plan_content = render_template("daily-plan.md", variables)
    plan_path = os.path.join(output_dir, "daily-plan.md")
    if not dry_run:
        with open(plan_path, "w") as f:
            f.write(plan_content)
    print(f"  ✓ daily-plan.md")
    print()

    # 6. 生成 Skill 反馈文件
    print("[6/7] 生成 Skill 反馈文件...")
    feedback_content = render_template("skill-feedback.md", variables)
    feedback_path = os.path.join(output_dir, "docs", "skill-feedback.md")
    if not dry_run:
        os.makedirs(os.path.dirname(feedback_path), exist_ok=True)
        with open(feedback_path, "w") as f:
            f.write(feedback_content)
    print(f"  ✓ docs/skill-feedback.md")
    print()

    # 7. 验证生成结果
    print("[7/7] 验证生成结果...")
    if not dry_run:
        v_pass, v_fail = validate_generated_files(output_dir)
        print()
        if v_fail > 0:
            print(f"  ⚠ 验证结果: {v_pass} 通过, {v_fail} 失败")
            print(f"  请检查模板或配置是否完整！")
        else:
            print(f"  ✅ 验证全部通过 ({v_pass} 项)")
    else:
        print("  (dry-run 模式跳过验证)")
    print()

    print("=" * 50)
    print(f"{mode}Agent 项目已生成到: {output_dir}")
    print(f"包含 {len(config.skills)} 个 skills | builder v{VERSION}")

    if not dry_run and v_fail > 0:
        return False
    return True


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



def list_mcp_servers():
    """列出所有可用 MCP servers"""
    print(f"Agent Builder v{VERSION} - 可用 MCP Servers")
    print("=" * 60)

    categories = {}
    for name, info in MCP_SERVER_CATALOG.items():
        cat = info["category"]
        categories.setdefault(cat, []).append((name, info))

    for cat in sorted(categories):
        print(f"\n[{cat}]")
        for name, info in sorted(categories[cat]):
            print(f"  {name:<28} {info['description']}")
            print(f"    url: {info['url']}")
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
    parser.add_argument("--list-mcp", action="store_true", help="列出所有可用 MCP servers")
    parser.add_argument("--version", action="version", version=f"agent-builder {VERSION}")
    args = parser.parse_args()

    try:
        if args.list_skills:
            list_skills()
            return

        if args.list_mcp:
            list_mcp_servers()
            return

        if not args.config or not args.output:
            parser.error("--config 和 --output 为必填项（除非使用 --list-skills）")

        config = ProjectConfig.from_yaml(args.config)
        success = generate_project(config, args.output, dry_run=args.dry_run)
        if not success:
            print("\n⚠ 生成完成但验证未全部通过，请检查上方输出!", file=sys.stderr)
            sys.exit(4)

    except FileNotFoundError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"配置无效: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"未知错误: {e}", file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()
