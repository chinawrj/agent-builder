# Skill: ESP32 串口工具

## 用途

管理 ESP32 设备的串口通信，包括日志监控、数据解析、异常检测。

**何时使用：**
- 需要监控 ESP32 设备的串口输出
- 需要解析串口日志中的关键信息
- 需要检测运行时错误（panic, assert, watchdog）
- 需要通过串口发送命令到设备

**何时不使用：**
- 不涉及串口通信的项目
- 仅需要 Web 接口交互的场景

## 前置条件

- ESP-IDF 已安装并配置环境变量
- USB 串口驱动已安装（CP2102/CH340）
- 设备已通过 USB 连接

## 操作步骤

### 1. 识别串口设备

```bash
# macOS
ls /dev/tty.usb* /dev/cu.usb* 2>/dev/null

# Linux
ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null

# 通常结果：/dev/ttyUSB0 或 /dev/cu.usbserial-xxx
```

### 2. 启动串口监控

```bash
# 方式一：使用 idf.py monitor（推荐）
idf.py -p /dev/ttyUSB0 monitor

# 方式二：使用 minicom
minicom -D /dev/ttyUSB0 -b 115200

# 方式三：使用 screen
screen /dev/ttyUSB0 115200
```

### 3. 日志捕获与分析

在 tmux 环境中，可以自动捕获和分析日志：

```bash
# 捕获 monitor 窗口的最新输出
tmux capture-pane -t {{PROJECT_NAME}}:monitor -p | tail -50

# 检查是否有错误
tmux capture-pane -t {{PROJECT_NAME}}:monitor -p | grep -iE "(error|panic|assert|abort|watchdog)"

# 检查 WiFi 连接状态
tmux capture-pane -t {{PROJECT_NAME}}:monitor -p | grep -iE "(wifi|connected|ip addr|got ip)"

# 检查 HTTP 服务器状态
tmux capture-pane -t {{PROJECT_NAME}}:monitor -p | grep -iE "(httpd|server|listening|port)"
```

### 4. 常见日志模式识别

| 日志模式 | 含义 | 处理方式 |
|---------|------|---------|
| `Guru Meditation Error` | CPU 异常（panic） | 检查 backtrace，定位崩溃代码 |
| `Task watchdog got triggered` | 任务看门狗超时 | 检查是否有死循环或阻塞 |
| `Wi-Fi connected` | WiFi 已连接 | 正常，记录 IP 地址 |
| `httpd_start: Started` | HTTP 服务已启动 | 检查端口号 |
| `cam_hal: cam_dma_config` | 摄像头初始化 | 检查分辨率和帧率 |
| `ENOMEM` / `alloc failed` | 内存不足 | 降低分辨率或减少缓冲区 |

### 5. 串口数据提取脚本

```python
import serial
import re
import time

def monitor_serial(port="/dev/ttyUSB0", baudrate=115200, timeout=30):
    """监控串口输出，提取关键信息"""
    results = {
        "ip_address": None,
        "errors": [],
        "wifi_connected": False,
        "http_started": False,
    }

    ser = serial.Serial(port, baudrate, timeout=1)
    start = time.time()

    while time.time() - start < timeout:
        line = ser.readline().decode("utf-8", errors="ignore").strip()
        if not line:
            continue

        # 提取 IP 地址
        ip_match = re.search(r"got ip:(\d+\.\d+\.\d+\.\d+)", line)
        if ip_match:
            results["ip_address"] = ip_match.group(1)

        # 检查 WiFi 连接
        if "wifi connected" in line.lower() or "sta_connected" in line.lower():
            results["wifi_connected"] = True

        # 检查 HTTP 服务
        if "httpd" in line.lower() and "start" in line.lower():
            results["http_started"] = True

        # 收集错误
        if re.search(r"error|panic|assert|abort", line, re.IGNORECASE):
            results["errors"].append(line)

    ser.close()
    return results
```

## 成功标准

- [ ] 能正确识别并连接串口设备
- [ ] 串口日志实时输出可见
- [ ] 能自动检测常见错误模式
- [ ] 能提取关键信息（IP 地址、服务状态等）
