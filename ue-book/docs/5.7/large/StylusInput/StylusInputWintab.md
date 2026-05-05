# StylusInputWintab

> Windows Wintab API 后端模块

## 概述

`StylusInputWintab` 是 StylusInput 的 Windows 后端实现，基于 **Wintab API**。Wintab 是一个历史悠久的数位板接口标准，由 Wacom 主导开发，广泛支持各种旧款数位板设备。

相比 RealTimeStylus，Wintab 兼容性更好（支持更老的硬件），但功能上可能不如 RealTimeStylus 丰富。当 RealTimeStylus 不可用时，系统会回退到 Wintab。

## 技术细节

### 平台限制

- **仅限 Win64**
- **仅限编辑器**（EditorNoCommandlet）
- 加载阶段：PostDefault

### 消息驱动架构

与 RealTimeStylus 的 COM 插件模式不同，Wintab 后端通过 **Windows 消息处理** 工作：

1. `FWintabInstance` 注册一个 `FWintabMessageHandler`（实现 `IWindowsMessageHandler`）
2. 消息处理器拦截 Windows 消息（如 `WT_PACKET`、`WT_CSRCHANGE` 等）
3. 调用 Wintab API 函数读取数据包
4. 将 Wintab 数据转换为 `FStylusInputPacket`

### 数据流

```
Windows 消息循环
    → WT_PACKET / WT_CSRCHANGE / WT_PROXIMITY 等消息
        → FWintabMessageHandler::ProcessMessage()
            → Wintab API (WTQueuePacketsEx, WTPacket 等)
                → FStylusInputPacket
                    → IStylusInputEventHandler::OnPacket()
```

### 关键特性

- **游标变化检测**：`FWintabMessageHandler` 追踪 `CurrentStylusID`，在游标变化时通知事件处理器
- **数位板上下文管理**：支持动态添加/移除数位板设备
- **坐标映射**：将 Wintab 设备坐标转换为窗口坐标
- **包统计**：追踪每秒处理的数据包数量

### 源文件

| 文件 | 说明 |
|---|---|
| `WintabInterface.h/cpp` | `IStylusInputInterface` 实现 |
| `WintabInstance.h/cpp` | `IStylusInputInstance` 实现 |
| `WintabMessageHandler.h/cpp` | Windows 消息处理，Wintab 事件转换 |
| `WintabAPI.h/cpp` | Wintab DLL 动态加载和函数绑定 |
| `WintabTabletContext.h` | 数位板上下文实现 |
| `WintabStylus.h` | 手写笔信息实现 |
| `WintabStats.h` | 性能统计 |

### 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 基础库 |
| `Slate` | SWindow 引用 |
| `SlateCore` | Slate 核心 |
| `StylusInput` | 核心接口定义 |
| `Wintab` | UE 内置的 Wintab SDK 封装模块 |

### 注意事项

- 事件处理器在游戏线程上调用（通过 Windows 消息循环）
- 支持多个事件处理器
- Wintab DLL（`wintab32.dll`）通过动态加载，如果不存在则接口不可用
- 数位板上下文在实例创建时初始化，支持运行时热插拔检测

## 源码

[源码目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/StylusInput/Source/StylusInputWintab)
