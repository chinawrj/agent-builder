# {{PROJECT_NAME}} - 项目需求文档

## 项目概述

**项目名称**: {{PROJECT_NAME}}
**描述**: {{PROJECT_DESCRIPTION}}
**目标硬件**: {{TARGET_HARDWARE}}

## 功能需求

{{FEATURES}}

## 验收标准

{{ACCEPTANCE_CRITERIA}}

## 里程碑

{{MILESTONES}}

## 技术栈

- 硬件平台: {{TARGET_HARDWARE}}
- 开发工具: tmux, ESP-IDF, CDP 浏览器工具
- 测试工具: 串口自动化测试, Web UI 自动化测试

## AI Agent Skills

以下 skills 将用于项目开发：

{{SKILLS_LIST}}

## 非功能需求

- 设备应在 WiFi 断开后自动重连
- Web 页面应在 3 秒内加载完成
- 视频流延迟不超过 2 秒
- 传感器数据刷新间隔不超过 5 秒
- 系统连续运行 24 小时无崩溃

## 约束条件

- Flash 空间限制: 4MB（根据硬件型号调整）
- RAM 限制: 520KB SRAM + 4MB PSRAM（如有）
- WiFi 仅支持 2.4GHz
