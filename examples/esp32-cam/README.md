# ESP32-CAM 示例

这是一个使用 Agent Builder 生成的示例项目。

## 项目描述

通过浏览器实时查看 ESP32-CAM 摄像头画面，并显示虚拟温湿度传感器数据。

## 使用方式

### 1. 生成 Agent 项目文件

```bash
cd agent-builder
python -m builder.build \
  --config examples/esp32-cam/project-config.yaml \
  --output examples/esp32-cam/output
```

### 2. 将生成的文件复制到实际项目

```bash
cp -r examples/esp32-cam/output/.copilot /path/to/your-esp32-cam-project/
```

### 3. 在 VS Code 中使用 Agent 开发

打开你的 ESP32-CAM 项目，使用 `@dev-workflow` agent 开始每日迭代开发。

## 项目里程碑

| 里程碑 | 内容 | 状态 |
|--------|------|------|
| M1 | 基础框架（WiFi + HTTP） | 未开始 |
| M2 | 摄像头 MJPEG 流 | 未开始 |
| M3 | 虚拟传感器数据展示 | 未开始 |
| M4 | 测试优化与文档 | 未开始 |
