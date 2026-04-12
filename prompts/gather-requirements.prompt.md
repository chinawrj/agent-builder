---
description: "与用户对话收集项目需求，用于生成 AI agent 项目"
---

# 收集项目需求

你正在帮助用户定义一个新项目的需求。请按以下步骤有序地收集信息。

## 必须收集的信息

### 1. 基本信息（必填）
- 项目名称是什么？
- 用一句话描述项目做什么？

### 2. 硬件/平台（必填）
- 目标硬件是什么？(ESP32, ESP32-S3, Raspberry Pi, etc.)
- 使用什么开发框架？(ESP-IDF, Arduino, PlatformIO, etc.)
- 开发机操作系统？(macOS, Linux, Windows)

### 3. 功能需求（必填）
- 核心功能有哪些？请逐条列出。
- 是否需要 Web 界面？
- 是否需要实时数据显示？
- 是否需要视频/音频流？

### 4. 验收标准（必填）
- 每个功能怎么算"完成"？
- 有没有性能指标要求？

### 5. 可选信息
- 项目大概的开发周期？
- 有没有参考项目或文档？
- 有没有特殊硬件要求？(外接传感器类型等)

## 对话策略

1. 先问基本信息，再深入细节
2. 每次最多问 2-3 个问题，不要一次性轰炸
3. 用户回答模糊时，给出具体选项帮助选择
4. 收集完所有信息后，生成完整的配置摘要让用户确认
5. 确认后调用 builder 生成项目

## 输出格式

收集完成后，生成 YAML 配置：

```yaml
name: "项目名"
description: "项目描述"
target_hardware: "esp32"
framework: "esp-idf"
dev_os: "macos"
features:
  - "功能1"
  - "功能2"
skills:
  - "skill1"
  - "skill2"
acceptance_criteria:
  - "标准1"
  - "标准2"
milestones:
  - name: "里程碑1"
    description: "描述"
output_dir: "./output"
```
