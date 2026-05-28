# Stylus & Tablet Plugin

> Support for advanced stylus and tablet inputs such as pressure, stylus and tablet buttons, and pen angles.

| 属性 | 值 |
|---|---|
| 中文名 | 手写笔输入插件 |
| 分类 | Input Devices |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `StylusInput` (Editor), `StylusInputDebugWidget` (EditorNoCommandlet), `StylusInputMac` (EditorNoCommandlet), `StylusInputRealTimeStylus` (EditorNoCommandlet), `StylusInputWintab` (EditorNoCommandlet) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-06-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/StylusInput) | |

## 用途

这个插件为 UE5 编辑器提供专业数位板/手写笔的高级输入支持。它解决了 UE5 原生输入系统无法获取手写笔压力、倾斜角度、笔身按钮等专业绘图设备数据的问题。

插件采用平台抽象架构，通过统一接口屏蔽底层 API 差异：
- **Windows**：同时支持 RealTimeStylus API（微软官方）和 Wintab（Wacom 等厂商广泛使用）
- **macOS**：通过 NSEvent 处理 Apple Pencil / 数位板输入

此外，插件提供了内置的调试工具（Debug Widget），方便开发者在编辑器中实时可视化手写笔的各项数据。

**注意**：这是一个 **EditorOnly** 插件，仅在编辑器中生效，不会被打包到最终游戏运行时。

## 使用场景

- 你正在开发美术工具或编辑器扩展，需要读取手写笔压力来控制画笔粗细
- 你在实现自定义的 2D/3D 绘图功能，需要获取笔尖倾斜角度
- 你需要同时支持 Wacom 和 Windows Ink 两种 Windows 数位板协议
- 你需要在 macOS 上使用 Apple Pencil 或数位板进行创作
- 你需要调试手写笔输入，观察实时数据流

## 蓝图用法

此插件主要面向 C++ 编辑器扩展开发，当前提供的公开 Blueprint API 较少。核心功能通过 C++ 接口暴露。

### 核心接口

| 接口/类 | 说明 | 所在模块 |
|---|---|---|
| `IStylusInputInstance` | 手写笔输入实例，主入口接口 | `StylusInput` |
| `IStylusInputEventHandler` | 事件处理接口，用于接收笔数据 | `StylusInput` |
| `FStylusInputPacket` | 笔数据包（压力、坐标、角度等） | `StylusInput` |
| `IStylusInputTabletContext` | 数位板上下文信息 | `StylusInput` |
| `IStylusInputStylusInfo` | 手写笔设备信息 | `StylusInput` |

## C++ 用法

### 头文件引入

```cpp
#include "StylusInput.h"
#include "StylusInputPacket.h"
```

### 基本用法：实现事件处理器

从 Debug Widget 模块的 `FDebugEventHandlerAsynchronous` 和 `FDebugEventHandlerOnGameThread` 可以看到标准用法。

```cpp
// 来源: Source/StylusInputDebugWidget/Private/StylusInputDebugWidget.h

// 1. 实现 IStylusInputEventHandler 接口
class FMyStylusHandler : public IStylusInputEventHandler
{
public:
    virtual FString GetName() override { return "MyStylusHandler"; }

    // 接收笔数据包（可能在非游戏线程调用）
    virtual void OnPacket(const FStylusInputPacket& Packet, IStylusInputInstance* Instance) override
    {
        // 处理压力、坐标等数据
        // 注意：此回调可能不在游戏线程！
    }

    // 接收调试事件
    virtual void OnDebugEvent(const FString& Message, IStylusInputInstance* Instance) override
    {
        UE_LOG(LogTemp, Log, TEXT("Stylus Debug: %s"), *Message);
    }
};
```

### 进阶用法：异步事件处理

Debug Widget 提供了两种线程模型，可根据需求选择：

```cpp
// 来源: Source/StylusInputDebugWidget/Private/StylusInputDebugWidget.h

// 方式一：直接在回调线程处理（适合线程安全的轻量操作）
// 使用 FDebugEventHandlerOnGameThread 模式

// 方式二：队列化处理，在 Tick 中消费（适合需要线程安全的操作）
class FMyAsyncHandler : public IStylusInputEventHandler, public FTickableEditorObject
{
public:
    virtual void OnPacket(const FStylusInputPacket& Packet, IStylusInputInstance* Instance) override
    {
        // 将数据入队（线程安全的 SPSC 队列）
        PacketQueue.Enqueue(Packet);
    }

    virtual void Tick(float DeltaTime) override
    {
        // 在游戏线程安全地消费数据
        FStylusInputPacket Packet;
        while (PacketQueue.Dequeue(Packet))
        {
            // 处理数据...
        }
    }

    virtual TStatId GetStatId() const override
    {
        RETURN_QUICK_DECLARE_CYCLE_STAT(MyStylusHandler, STATGROUP_Tickables);
    }

private:
    TSpscQueue<FStylusInputPacket> PacketQueue;
};
```

## 模块架构

此插件由 5 个模块组成，采用平台分层架构：

| 模块 | 平台 | 加载阶段 | 职责 |
|---|---|---|---|
| `StylusInput` | 全平台 | Default | 核心抽象层，定义接口和数据结构 |
| `StylusInputDebugWidget` | 全平台 | PostEngineInit | 调试可视化工具 |
| `StylusInputMac` | macOS | PostDefault | macOS 平台实现（NSEvent） |
| `StylusInputRealTimeStylus` | Win64 | PostDefault | Windows RealTimeStylus API 实现 |
| `StylusInputWintab` | Win64 | PostDefault | Windows Wintab API 实现 |

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Slate` / `SlateCore` | 调试 Widget 的 UI 渲染 |

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-19 | `9693e160` | StylusInput: Fix NSEvent up/down | 修复 macOS 上笔抬起/落下事件处理问题 |
| 2026-05-19 | `36a0dc9c` | StylusInput: Fix issue with multiple Wintab instances | 修复多个 Wintab 实例同时存在的冲突问题 |
| 2026-05-13 | `041d4d75` | StylusInput: Fix coordinates issue with Wintab when main screen is not on left/top | 修复主屏幕非左上角时 Wintab 坐标偏移问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新的 UE_LOGF 格式 |
| 2026-01-28 | `5f766aee` | Fixed modules that does not support portable toolchain | 修复可移植工具链兼容性问题 |

### 维护评价

- **状态**：活跃维护中
- **近期活动**：2026 年 5 月有多次实质性 bug 修复，说明 Epic 仍在积极维护
- **已知限制**：
  - 仍然是 **Beta 状态**（`IsBetaVersion=true`）
  - **默认未启用**（`EnabledByDefault=false`），需要手动在 Plugins 面板中启用
  - 仅限 Editor 使用，不支持运行时打包
  - Windows 平台存在两种 API（RealTimeStylus 和 Wintab），用户需根据设备选择
- **推荐度**：如果你需要在 UE5 编辑器中使用手写笔的高级输入功能，这是唯一官方支持的方案，推荐使用。但需注意 Beta 状态，生产环境使用时做好兼容性测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/StylusInput)