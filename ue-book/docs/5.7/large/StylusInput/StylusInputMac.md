# StylusInputMac

> macOS NSEvent 后端模块

## 概述

`StylusInputMac` 是 StylusInput 的 macOS 后端实现，基于 **NSEvent** 和 **IOKit HID** API。此模块于 2025 年 9 月新增，为 macOS 上的 Apple Pencil（通过 Sidecar）和 Wacom 数位板提供支持。

## 技术细节

### 平台限制

- **仅限 Mac**
- **仅限编辑器**（EditorNoCommandlet）
- 加载阶段：PostDefault

### 双层事件系统

macOS 后端使用两个层次的事件捕获：

1. **NSEvent**（应用层）：通过 `NSApplication` 的事件回调捕获 tablet 事件（`tabletPoint`、`tabletProximity` 等）
2. **IOKit HID**（设备层）：通过 `IOHIDManager` 获取设备级别的信息，用于区分不同的物理设备和获取设备 ID

```
macOS 事件系统
    → NSEvent (tabletPoint, tabletProximity)
        → FNSEventHandler::HandleNSEvent()
            → 转换为 FStylusInputPacket
                → IStylusInputEventHandler::OnPacket()

IOKit HID
    → IOHIDManager 回调
        → FNSEventHandler::HandleHIDEvent()
            → 获取设备 ID
```

### 与 Windows 的差异

macOS 上没有类似 Windows "Tablet Context" 的概念。`FMacInstance` 将系统中所有已知的数位板设备存储为 tablet context，并通过设备 ID 区分事件来源。

### 源文件

| 文件 | 说明 |
|---|---|
| `MacInterface.h/cpp` | `IStylusInputInterface` 实现，接口名称为 `"NSEvent"` |
| `MacInstance.h/cpp` | `IStylusInputInstance` 实现 |
| `NSEventHandler.h/cpp` | NSEvent 和 IOKit HID 事件处理 |
| `MacTabletContext.h/cpp` | 数位板上下文（基于系统设备列表） |
| `MacStats.h` | 性能统计 |
| `StylusInputMacModule.cpp` | 模块注册 |

### 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 基础库 |
| `Slate` | SWindow 引用 |
| `SlateCore` | Slate 核心 |
| `StylusInput` | 核心接口定义 |

### 系统框架依赖

| Framework | 用途 |
|---|---|
| `IOKit` | HID 设备管理，获取设备 ID |
| `CoreFoundation` | macOS 核心类型 |
| `Foundation` | NSEvent 等 Objective-C API |

### 注意事项

- 使用 Objective-C++ 混编（`.mm` 文件）
- IOKit HID 用于获取精确的设备标识符，NSEvent 本身不直接提供
- `FCocoaWindow` 是 macOS 特有的窗口类型
- 支持 Apple Pencil（通过 Sidecar 或 Universal Control）

## 源码

[源码目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/StylusInput/Source/StylusInputMac)
