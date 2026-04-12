"""项目配置 Schema"""

from dataclasses import dataclass, field


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

    @classmethod
    def from_yaml(cls, path: str) -> "ProjectConfig":
        """从 YAML 文件加载配置"""
        import yaml

        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data)

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
}


def recommend_skills(config: ProjectConfig) -> list[str]:
    """根据项目配置推荐 skills"""
    recommended = []

    # 嵌入式项目基础 skills
    if config.target_hardware.startswith("esp32"):
        recommended.extend(["tmux-multi-shell", "esp32-build-flash", "esp32-serial-tools"])

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
