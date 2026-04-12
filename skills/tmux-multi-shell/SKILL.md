# Skill: tmux 多终端管理

## 用途

管理 tmux 会话，为嵌入式开发创建多窗口工作环境。典型布局包括：编译窗口、烧录窗口、串口监控窗口、代码编辑窗口。

**何时使用：**
- 需要同时运行多个终端任务（编译 + 烧录 + 串口监控）
- 需要持久化终端会话
- 需要在不同任务间快速切换

**何时不使用：**
- 单终端任务足够的情况
- 非命令行环境

## 前置条件

- `tmux` 已安装（macOS: `brew install tmux`, Linux: `apt install tmux`）
- 终端支持 tmux

## 操作步骤

### 1. 创建项目会话

```bash
# 创建新会话，命名为项目名
tmux new-session -d -s {{PROJECT_NAME}}

# 重命名第一个窗口为 "编辑"
tmux rename-window -t {{PROJECT_NAME}}:0 'edit'

# 创建编译窗口
tmux new-window -t {{PROJECT_NAME}} -n 'build'

# 创建烧录窗口
tmux new-window -t {{PROJECT_NAME}} -n 'flash'

# 创建串口监控窗口
tmux new-window -t {{PROJECT_NAME}} -n 'monitor'
```

### 2. 标准窗口布局

| 窗口编号 | 名称 | 用途 |
|---------|------|------|
| 0 | edit | 代码编辑/git 操作 |
| 1 | build | 编译构建 |
| 2 | flash | 烧录固件 |
| 3 | monitor | 串口日志监控 |

### 3. 发送命令到指定窗口

```bash
# 在 build 窗口执行编译
tmux send-keys -t {{PROJECT_NAME}}:build 'idf.py build' C-m

# 在 flash 窗口执行烧录
tmux send-keys -t {{PROJECT_NAME}}:flash 'idf.py -p /dev/ttyUSB0 flash' C-m

# 在 monitor 窗口启动串口监控
tmux send-keys -t {{PROJECT_NAME}}:monitor 'idf.py -p /dev/ttyUSB0 monitor' C-m
```

### 4. 查看窗口输出

```bash
# 捕获指定窗口的输出（最后 100 行）
tmux capture-pane -t {{PROJECT_NAME}}:build -p | tail -100

# 检查编译是否成功
tmux capture-pane -t {{PROJECT_NAME}}:build -p | grep -E "(error|warning|SUCCESS)"
```

### 5. 会话管理

```bash
# 列出所有会话
tmux list-sessions

# 附加到会话
tmux attach-session -t {{PROJECT_NAME}}

# 关闭会话
tmux kill-session -t {{PROJECT_NAME}}
```

## 成功标准

- [ ] tmux 会话已创建，包含所有必要窗口
- [ ] 每个窗口可独立发送和执行命令
- [ ] 可以通过 `capture-pane` 获取任意窗口的输出
- [ ] 会话在终端断开后仍然存活
