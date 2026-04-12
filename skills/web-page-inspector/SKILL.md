# Skill: Web 页面检查与数据提取

## 用途

通过浏览器访问设备 Web 页面，检查页面结构、提取显示的数据、验证实时流媒体。

**何时使用：**
- 需要检查设备 Web 界面是否正常渲染
- 需要提取传感器数据、统计信息等
- 需要验证实时视频/音频流状态
- 需要获取页面上动态更新的内容

**何时不使用：**
- 设备没有 Web 界面
- 只需要 REST API 交互（直接用 curl）

## 前置条件

- CDP 浏览器工具已启动（见 `cdp-web-inspector` skill）
- 设备 Web 服务已运行
- 已知设备 IP 地址

## 操作步骤

### 1. 页面结构探索

```python
from patchright.sync_api import sync_playwright

def inspect_page(device_ip):
    """探索目标页面的 DOM 结构"""
    pw = sync_playwright().start()
    browser = pw.chromium.connect_over_cdp("http://localhost:9222")
    page = browser.contexts[0].new_page()

    page.goto(f"http://{device_ip}/")
    page.wait_for_load_state("networkidle")

    # 获取页面基本信息
    info = {
        "title": page.title(),
        "url": page.url,
    }

    # 获取所有可见文本
    info["text_content"] = page.locator("body").text_content()

    # 获取所有图片元素
    images = page.locator("img").all()
    info["images"] = [
        {"src": img.get_attribute("src"), "id": img.get_attribute("id")}
        for img in images
    ]

    # 获取所有表格数据
    tables = page.locator("table").all()
    info["tables"] = []
    for table in tables:
        rows = table.locator("tr").all()
        table_data = []
        for row in rows:
            cells = row.locator("td, th").all()
            table_data.append([cell.text_content() for cell in cells])
        info["tables"].append(table_data)

    page.close()
    pw.stop()
    return info
```

### 2. 传感器数据提取

```python
def extract_sensor_data(page):
    """从页面提取传感器数据"""
    data = {}

    # 策略1：通过 ID 查找
    selectors = {
        "temperature": "#temperature, [data-sensor='temperature'], .temp-value",
        "humidity": "#humidity, [data-sensor='humidity'], .humidity-value",
        "pressure": "#pressure, [data-sensor='pressure'], .pressure-value",
    }

    for name, selector in selectors.items():
        el = page.locator(selector)
        if el.count() > 0 and el.first.is_visible():
            data[name] = el.first.text_content().strip()

    # 策略2：通过 JavaScript 提取
    js_data = page.evaluate("""() => {
        const result = {};
        // 查找包含数字和单位的元素
        document.querySelectorAll('[class*="sensor"], [class*="data"], [class*="value"]')
            .forEach(el => {
                const text = el.textContent.trim();
                const id = el.id || el.className;
                if (text && /\\d/.test(text)) {
                    result[id] = text;
                }
            });
        return result;
    }""")
    data["js_extracted"] = js_data

    return data
```

### 3. 视频流检测

```python
def check_video_stream(page):
    """检测视频流是否正常工作"""
    result = {
        "has_stream": False,
        "stream_type": None,
        "stream_url": None,
        "is_loading": False,
    }

    # 检查 <img> 标签的 MJPEG 流
    mjpeg = page.locator("img[src*='stream'], img[src*='mjpeg'], img[src*=':81']")
    if mjpeg.count() > 0 and mjpeg.first.is_visible():
        result["has_stream"] = True
        result["stream_type"] = "MJPEG"
        result["stream_url"] = mjpeg.first.get_attribute("src")

    # 检查 <video> 标签
    video = page.locator("video")
    if video.count() > 0 and video.first.is_visible():
        result["has_stream"] = True
        result["stream_type"] = "VIDEO"
        result["stream_url"] = video.first.get_attribute("src")

    # 检查 canvas (WebRTC 等)
    canvas = page.locator("canvas#stream, canvas.video-canvas")
    if canvas.count() > 0 and canvas.first.is_visible():
        result["has_stream"] = True
        result["stream_type"] = "CANVAS"

    # 验证流是否在加载（通过图片尺寸变化）
    if result["has_stream"] and result["stream_type"] == "MJPEG":
        size1 = page.evaluate("""(sel) => {
            const img = document.querySelector(sel);
            return img ? {w: img.naturalWidth, h: img.naturalHeight} : null;
        }""", mjpeg.first.evaluate("el => el.tagName + (el.id ? '#'+el.id : '')"))
        result["is_loading"] = size1 is not None and size1.get("w", 0) > 0

    return result
```

### 4. 周期性数据采集

```python
import time
import json

def collect_data_over_time(page, interval=5, duration=60):
    """周期性采集页面数据"""
    samples = []
    start = time.time()

    while time.time() - start < duration:
        sample = {
            "timestamp": time.time(),
            "data": extract_sensor_data(page),
            "stream": check_video_stream(page),
        }
        samples.append(sample)
        print(f"[{len(samples)}] {json.dumps(sample['data'], ensure_ascii=False)}")
        time.sleep(interval)

    return samples
```

### 5. 页面截图与报告

```python
def generate_page_report(page, output_dir="reports"):
    """生成页面检查报告"""
    import os
    os.makedirs(output_dir, exist_ok=True)

    # 全页截图
    page.screenshot(path=f"{output_dir}/full-page.png", full_page=True)

    # 特定区域截图
    stream_el = page.locator("img#stream, video#stream").first
    if stream_el.is_visible():
        stream_el.screenshot(path=f"{output_dir}/stream.png")

    # 生成文本报告
    sensor_data = extract_sensor_data(page)
    stream_status = check_video_stream(page)

    report = f"""# 页面检查报告

## 基本信息
- URL: {page.url}
- 标题: {page.title()}
- 时间: {time.strftime('%Y-%m-%d %H:%M:%S')}

## 传感器数据
{json.dumps(sensor_data, indent=2, ensure_ascii=False)}

## 视频流状态
{json.dumps(stream_status, indent=2, ensure_ascii=False)}

## 截图
- 全页: full-page.png
- 视频流: stream.png
"""
    with open(f"{output_dir}/report.md", "w") as f:
        f.write(report)

    return report
```

## 成功标准

- [ ] 能正确访问设备 Web 页面
- [ ] 能从页面提取传感器数据
- [ ] 能检测视频流状态
- [ ] 能周期性采集数据
- [ ] 能生成包含截图的检查报告
