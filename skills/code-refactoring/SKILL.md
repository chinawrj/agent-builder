# Skill: 代码重构策略

## 用途

定义周期性代码重构的策略和流程，确保在持续开发中保持代码质量。

**何时使用：**
- 每 5 个迭代日进行一次计划重构
- 发现代码异味（code smell）时
- 功能完成后的清理阶段
- 代码复杂度超过阈值时

**何时不使用：**
- 项目初期原型阶段（先让功能跑起来）
- 紧急 bug 修复中
- 代码质量已经很好的模块

## 前置条件

- 所有当前测试通过（重构前必须有绿灯）
- Git 工作区干净（无未提交的改动）
- 已明确重构目标

## 操作步骤

### 1. 重构触发条件

每次重构前评估以下指标：

| 指标 | 阈值 | 检测方法 |
|------|------|---------|
| 函数行数 | > 50 行 | `wc -l` |
| 文件行数 | > 500 行 | `wc -l` |
| 重复代码 | > 3 处 | `grep` 搜索 |
| TODO/FIXME | > 5 个 | `grep -rn "TODO\|FIXME"` |
| 嵌套层级 | > 4 层 | 代码审查 |
| 全局变量 | > 10 个 | `grep` 搜索 |

### 2. 重构检查清单

```markdown
## 重构清单 - Day N

### 代码检查
- [ ] 查找超长函数并拆分
- [ ] 提取重复代码为公共函数
- [ ] 消除魔术数字，定义常量
- [ ] 检查命名一致性
- [ ] 清理无用的 #include / import
- [ ] 处理所有 TODO/FIXME

### 架构检查
- [ ] 模块间依赖是否合理
- [ ] 接口是否清晰（输入/输出明确）
- [ ] 错误处理是否一致
- [ ] 内存管理是否正确（嵌入式重点）

### 文档检查
- [ ] README 是否与代码同步
- [ ] 关键函数是否有注释
- [ ] 配置说明是否完整
```

### 3. 安全重构流程

```bash
# Step 1: 确保测试通过
idf.py build && python test_serial.py && echo "绿灯 ✅"

# Step 2: 创建重构分支
git checkout -b refactor/day-N-cleanup

# Step 3: 执行重构（小步提交）
# ... 代码修改 ...
git add -A && git commit -m "refactor: 提取 WiFi 初始化为独立模块"

# ... 更多修改 ...
git add -A && git commit -m "refactor: 消除 main.c 中的魔术数字"

# Step 4: 重构后验证
idf.py build && python test_serial.py && echo "重构后仍然绿灯 ✅"

# Step 5: 合并
git checkout main && git merge refactor/day-N-cleanup
```

### 4. ESP32/嵌入式特定重构

#### 内存优化
```c
// Before: 栈上分配大缓冲区
void handle_request() {
    char buf[4096];  // 可能导致栈溢出
    // ...
}

// After: 使用堆分配或静态分配
static char s_buf[4096];  // 或使用 malloc/free
void handle_request() {
    // 使用 s_buf
}
```

#### 模块化
```
// Before: 所有代码在 main.c
main.c (800 lines)

// After: 按功能拆分
main.c          (50 lines)  - 入口和初始化调度
wifi_manager.c  (150 lines) - WiFi 管理
http_server.c   (200 lines) - HTTP 服务
camera_ctrl.c   (150 lines) - 摄像头控制
sensor_reader.c (100 lines) - 传感器读取
```

#### 错误处理统一
```c
// 定义统一的错误处理宏
#define CHECK_ESP_ERR(x, tag) do { \
    esp_err_t err = (x); \
    if (err != ESP_OK) { \
        ESP_LOGE(tag, "%s failed: %s", #x, esp_err_to_name(err)); \
        return err; \
    } \
} while(0)
```

### 5. 重构报告

每次重构后生成报告：

```markdown
## 重构报告 - Day N

### 变更摘要
- 拆分文件: main.c → 5 个模块文件
- 消除重复: 3 处重复代码提取为公共函数
- 清理: 移除 8 个 TODO，2 个未使用变量

### 代码指标变化
| 指标 | 重构前 | 重构后 |
|------|--------|--------|
| 最大函数行数 | 120 | 45 |
| 文件数 | 2 | 6 |
| TODO 数量 | 12 | 4 |

### 测试结果
- 编译: ✅ 通过
- 串口测试: ✅ 5/5 通过
- Web UI 测试: ✅ 4/4 通过
```

## 成功标准

- [ ] 重构前后所有测试保持通过
- [ ] 代码指标有明显改善
- [ ] Git 历史清晰，每次重构小步提交
- [ ] 重构报告已生成
