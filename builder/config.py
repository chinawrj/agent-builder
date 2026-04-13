"""项目配置 Schema"""

import os
from dataclasses import dataclass, field

# Agent Builder 版本
VERSION = "0.2.0"

REQUIRED_FIELDS = {"name", "description", "target_hardware"}


@dataclass
class ProjectConfig:
    """项目配置"""

    # 基本信息
    name: str = ""
    description: str = ""
    target_hardware: str = ""  # esp32, esp32s3, raspberry-pi, etc.

    # 开发环境
    framework: str = ""  # esp-idf, arduino, platformio
    dev_os: str = ""  # macos, linux, windows

    # 功能需求
    features: list[str] = field(default_factory=list)

    # 选中的 skills
    skills: list[str] = field(default_factory=list)

    # 验收标准
    acceptance_criteria: list[str] = field(default_factory=list)

    # 里程碑
    milestones: list[dict] = field(default_factory=list)

    # 输出目录
    output_dir: str = ""

    def validate(self):
        """验证配置完整性"""
        missing = {f for f in REQUIRED_FIELDS if not getattr(self, f, "")}
        if missing:
            raise ValueError(f"缺少必填字段: {', '.join(sorted(missing))}")

        # 验证 skills 是否在目录中
        if self.skills:
            unknown = set(self.skills) - set(SKILL_CATALOG.keys())
            if unknown:
                raise ValueError(f"未知的 skill: {', '.join(sorted(unknown))}")

        # 验证 milestones 格式
        for i, m in enumerate(self.milestones):
            if not isinstance(m, dict):
                raise ValueError(f"里程碑 {i+1} 格式错误，应为 dict")

    @classmethod
    def from_yaml(cls, path: str) -> "ProjectConfig":
        """从 YAML 文件加载配置"""
        import yaml

        if not os.path.isfile(path):
            raise FileNotFoundError(f"配置文件不存在: {path}")

        with open(path) as f:
            data = yaml.safe_load(f)

        if not data or not isinstance(data, dict):
            raise ValueError(f"配置文件为空或格式错误: {path}")

        # 过滤掉不属于 ProjectConfig 的字段
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in valid_fields}

        config = cls(**filtered)
        config.validate()
        return config

    def to_yaml(self, path: str):
        """保存配置到 YAML 文件"""
        import yaml
        from dataclasses import asdict

        with open(path, "w") as f:
            yaml.dump(asdict(self), f, default_flow_style=False, allow_unicode=True)


# 可用 skills 及其分类
SKILL_CATALOG = {
    "tmux-multi-shell": {
        "category": "dev-tools",
        "description": "tmux 多终端管理（编译/烧录/串口监控）",
        "tags": ["terminal", "multi-window", "embedded"],
    },
    "cdp-web-inspector": {
        "category": "web-tools",
        "description": "Chrome DevTools Protocol 浏览器自动化",
        "tags": ["browser", "cdp", "patchright", "web-ui"],
    },
    "esp32-serial-tools": {
        "category": "hardware",
        "description": "ESP32 串口通信与日志监控",
        "tags": ["serial", "uart", "esp32", "embedded"],
    },
    "esp32-build-flash": {
        "category": "hardware",
        "description": "ESP-IDF 编译与烧录工作流",
        "tags": ["build", "flash", "esp-idf", "esp32"],
    },
    "daily-iteration": {
        "category": "workflow",
        "description": "每日迭代计划与执行",
        "tags": ["planning", "agile", "iteration"],
    },
    "automated-testing": {
        "category": "quality",
        "description": "自动化测试（串口验证 + Web UI 验证）",
        "tags": ["testing", "automation", "e2e"],
    },
    "code-refactoring": {
        "category": "quality",
        "description": "周期性代码重构策略",
        "tags": ["refactoring", "code-quality", "maintenance"],
    },
    "web-page-inspector": {
        "category": "web-tools",
        "description": "Web 页面内容检查与数据提取",
        "tags": ["web", "scraping", "inspection"],
    },
    "environment-setup": {
        "category": "dev-tools",
        "description": "开发环境检查与配置（工具链、驱动、依赖）",
        "tags": ["setup", "environment", "verification"],
    },
    "project-scaffolding": {
        "category": "workflow",
        "description": "项目脚手架生成（目录结构、CMake、HTML 模板）",
        "tags": ["scaffold", "template", "init"],
    },
    "board-pinout-reference": {
        "category": "hardware",
        "description": "开发板引脚定义(Pinout)与核心模组资源速查",
        "tags": ["pinout", "hardware", "esp32", "reference", "datasheet"],
    },
}


def recommend_skills(config: ProjectConfig) -> list[str]:
    """根据项目配置推荐 skills"""
    recommended = ["environment-setup"]  # 环境检查总是需要

    # 嵌入式项目基础 skills
    if config.target_hardware.startswith("esp32"):
        recommended.extend([
            "tmux-multi-shell", "esp32-build-flash", "esp32-serial-tools",
            "project-scaffolding",
        ])

    # Web UI 相关
    has_web = any(
        kw in " ".join(config.features).lower()
        for kw in ["web", "browser", "http", "视频", "video", "stream", "页面"]
    )
    if has_web:
        recommended.extend(["cdp-web-inspector", "web-page-inspector"])

    # 工作流 skills（几乎总是需要）
    recommended.extend(["daily-iteration", "automated-testing", "code-refactoring"])

    # 去重并保持顺序
    seen = set()
    result = []
    for s in recommended:
        if s not in seen:
            seen.add(s)
            result.append(s)

    return result
