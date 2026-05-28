# Stylus & Tablet Plugin

> Support for advanced stylus and tablet inputs such as pressure, stylus and tablet buttons, and pen angles.

| 属性 | 值 |
|---|---|
| 中文名 | 数位板输入插件 |
| 分类 | Input Devices |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `StylusInput` (Editor), `StylusInputDebugWidget` (EditorNoCommandlet), `StylusInputMac` (EditorNoCommandlet), `StylusInputRealTimeStylus` (EditorNoCommandlet), `StylusInputWintab` (EditorNoCommandlet) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-06-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/StylusInput) | |

## 用途

这个插件为 UE 编辑器提供了对专业数位板（Wacom 等）和触控笔的高级输入支持。它解决了编辑器中无法读取笔压、笔倾斜角度、数位板按钮等专业输入数据的问题。

插件采用了**平台抽象架构**，核心模块定义统一的接口（`IStylusInputInterface`、`IStylusInputInstance`、`IStylusInputTabletContext` 等），然后通过三个平台后端模块分别实现：

- **StylusInputWintab**（Windows）：使用 Wintab API，这是 Windows 上最广泛支持的数位板驱动接口
- **StylusInputRealTimeStylus**（Windows）：使用微软的 RealTimeStylus API，作为 Windows 上的备选方案
- **StylusInputMac**（macOS）：使用 Apple 原生平板输入 API

此外还包含一个 **StylusInputDebugWidget** 模块，提供调试可视化界面，方便开发者实时查看数位板输入数据。

**注意**：此插件默认未启用（`EnabledByDefault: false`），且处于 Beta 状态。需要在编辑器设置中手动启用。

## 使用场景

- 你正在开发数字雕刻/绘画工具插件，需要读取笔压来控制笔刷大小 → 使用此插件获取 `FStylusInputPacket` 中的压力数据
- 你需要在编辑器工具中检测触控笔的倾斜角度，用于模拟真实笔触效果 → 订阅 `IStylusInputEventHandler` 获取 Orientation 数据
- 你在开发自定义编辑器面板，需要区分触控笔的笔尖和橡皮擦端 → 使用 `CursorIsInverted()` 检测反向笔触
- 你需要调试数位板输入数据，确认驱动是否正确工作 → 启用 `StylusInputDebugWidget` 模块查看实时数据

## 蓝图用法

此插件主要面向 C++ 开发者，提供底层数位板输入接口。核心 API 均为 C++ 虚接口（`IStylusInputInterface`、`IStylusInputInstance` 等），不直接暴露蓝图节点。

`StylusInputDebugWidget` 模块可能提供编辑器内调试 UI，但其设计目的为开发调试而非蓝图集成。

如需在蓝图中使用数位板输入，需自行编写 C++ 包装层，将 `IStylusInputEventHandler` 的回调数据桥接到蓝图事件。

## C++ 用法

### 头文件引入

```cpp
// 核心 API
#include "StylusInput.h"
#include "StylusInputInterface.h"
#include "StylusInputPacket.h"
#include "StylusInputTabletContext.h"
```

### 核心概念

插件的架构分为以下层次：

```
IStylusInputInterface          ← 平台接口（Wintab/RealTimeStylus/Mac）
  └─ IStylusInputInstance      ← 每个窗口的输入实例
       ├─ IStylusInputTabletContext   ← 数位板设备信息
       │    └─ IStylusInputStylusInfo ← 触控笔信息
       │         └─ IStylusInputStylusButton ← 笔按钮
       └─ IStylusInputEventHandler    ← 输入事件接收器
            └─ FStylusInputPacket     ← 单次输入数据包
```

### 基本用法：获取数位板输入

创建窗口级实例并注册事件处理器来接收输入数据：

```cpp
// 引入核心头文件
#include "StylusInput.h"
#include "StylusInputInterface.h"
#include "StylusInputPacket.h"

// 定义事件处理器（实现 IStylusInputEventHandler 接口）
class FMyStylusHandler : public UE::StylusInput::IStylusInputEventHandler
{
public:
    virtual void OnPacket(const UE::StylusInput::FStylusInputPacket& Packet) override
    {
        // 读取笔压（0.0 ~ 1.0 归一化值）
        float Pressure = Packet.NormalPressure;
        
        // 读取笔尖位置（窗口相对坐标）
        float X = Packet.X;
        float Y = Packet.Y;
        
        // 读取倾斜角度
        // Packet.Orientation 包含 Azimuth、Altitude 等方向数据
        
        // 读取笔按钮状态
        // Packet.Buttons 位掩码表示各按钮是否按下
    }
};
```

### 进阶用法：查询数位板和触控笔信息

```cpp
// 获取已注册的数位板上下文信息
const TSharedPtr<IStylusInputTabletContext> TabletContext = 
    Instance->GetTabletContext(TabletContextID);

if (TabletContext.IsValid())
{
    // 获取数位板名称
    FString Name = TabletContext->GetName();
    
    // 获取输入区域范围
    FIntRect InputRect = TabletContext->GetInputRectangle();
    
    // 查询硬件能力（支持哪些属性）
    ETabletHardwareCapabilities Caps = TabletContext->GetHardwareCapabilities();
    
    // 查询支持的属性（压力、倾斜等）
    ETabletSupportedProperties Props = TabletContext->GetSupportedProperties();
}

// 获取触控笔信息
const TSharedPtr<IStylusInputStylusInfo> StylusInfo = 
    Instance->GetStylusInfo(StylusID);

if (StylusInfo.IsValid())
{
    // 获取触控笔名称
    FString StylusName = StylusInfo->GetName();
    
    // 获取笔按钮数量和信息
    int32 NumButtons = StylusInfo->GetNumButtons();
    for (int32 i = 0; i < NumButtons; ++i)
    {
        const IStylusInputStylusButton* Button = StylusInfo->GetButton(i);
        // Button->GetName() - 按钮名称
        // Button->GetID()   - 按钮标识
    }
}

// 获取每秒数据包速率（性能监控）
float PacketsPerSec = Instance->GetPacketsPerSecond(EEventHandlerThread::Game);
```

### 进阶用法：Wintab 平台细节

在 Windows Wintab 后端中，支持以下光标类型（来自 `ECursorType`）：

| 光标类型 | 值 | 说明 |
|---|---|---|
| `GeneralStylus` | `0x0802` | 标准触控笔 |
| `Airbrush` | `0x0902` | 喷枪工具 |
| `ArtPen` | `0x0804` | 美术笔 |
| `FourDMouse` | `0x0004` | 4D 鼠标 |
| `FiveButtonPuck` | `0x0006` | 五按钮定位器 |

Wintab 数据包包含以下属性（通过 `PACKETDATA` 宏定义）：

- `PK_STATUS` — 笔状态
- `PK_TIME` — 时间戳
- `PK_SERIAL_NUMBER` — 数据包序列号（用于检测丢包）
- `PK_CURSOR` — 光标标识
- `PK_BUTTONS` — 按钮状态
- `PK_X`, `PK_Y`, `PK_Z` — 三维坐标
- `PK_NORMAL_PRESSURE` — 垂直压力
- `PK_TANGENT_PRESSURE` — 切向压力
- `PK_ORIENTATION` — 笔倾斜方向
- `PK_ROTATION` — 笔旋转角度

## Demo 示例

以下展示如何创建一个最小的事件处理器来接收数位板输入：

```cpp
// MyStylusHandler.h
#pragma once

#include "StylusInputInterface.h"

class FMyStylusHandler : public UE::StylusInput::IStylusInputEventHandler
{
public:
    FMyStylusHandler() = default;
    virtual ~FMyStylusHandler() = default;

    // IStylusInputEventHandler 接口
    virtual void OnPacket(const UE::StylusInput::FStylusInputPacket& Packet) override;
    virtual void OnStylusInRange(const UE::StylusInput::FStylusInputStylusState& State) override;
    virtual void OnStylusOutOfRange(const UE::StylusInput::FStylusInputStylusState& State) override;

    float GetCurrentPressure() const { return CurrentPressure; }
    bool IsStylusActive() const { return bStylusInRange; }

private:
    float CurrentPressure = 0.0f;
    bool bStylusInRange = false;
};
```

```cpp
// MyStylusHandler.cpp
#include "MyStylusHandler.h"

void FMyStylusHandler::OnPacket(const UE::StylusInput::FStylusInputPacket& Packet)
{
    CurrentPressure = Packet.NormalPressure;
    
    UE_LOG(LogTemp, Log, TEXT("Stylus Packet - Pos: (%.1f, %.1f), Pressure: %.3f"),
        Packet.X, Packet.Y, Packet.NormalPressure);
}

void FMyStylusHandler::OnStylusInRange(const UE::StylusInput::FStylusInputStylusState& State)
{
    bStylusInRange = true;
    UE_LOG(LogTemp, Log, TEXT("Stylus entered range"));
}

void FMyStylusHandler::OnStylusOutOfRange(const UE::StylusInput::FStylusInputStylusState& State)
{
    bStylusInRange = false;
    CurrentPressure = 0.0f;
    UE_LOG(LogTemp, Log, TEXT("Stylus left range"));
}
```

使用时，通过 `IStylusInputInstance::AddEventHandler` 注册处理器：

```cpp
// 在某个拥有 SWindow 的编辑器面板中
TSharedRef<SWindow> MyWindow = /* 获取或创建窗口 */;

// 通过 StylusInput 模块获取接口实例
IStylusInputInterface& StylusInterface = /* 获取接口 */;
IStylusInputInstance* Instance = StylusInterface.CreateInstance(MyWindow.Get());

FMyStylusHandler* Handler = new FMyStylusHandler();
Instance->AddEventHandler(Handler, EEventHandlerThread::Game);
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `StylusInput` | 核心数位板输入 API 和接口定义 |
| `StylusInputDebugWidget` | 数位板输入数据的调试可视化控件 |
| `StylusInputMac` | macOS 平台的数位板输入后端实现 |
| `StylusInputRealTimeStylus` | Windows RealTimeStylus API 后端 |
| `StylusInputWintab` | Windows Wintab API 后端 |

无特殊依赖（仅标准 Core/Engine/Slate 等）。平台后端模块仅在对应平台加载。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-19 | `9693e160` | StylusInput: Fix NSEvent up/down | 修复 macOS 上 NSEvent 笔按下/抬起事件问题 |
| 2026-05-19 | `36a0dc9c` | StylusInput: Fix issue with multiple Wintab instances | 修复多 Wintab 实例共存时的问题 |
| 2026-05-13 | `041d4d75` | StylusInput: Fix coordinates issue with Wintab when main screen is not on left/top | 修复主屏幕不在左上角时 Wintab 坐标偏移问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到 UE_LOGF 新格式 |
| 2026-01-28 | `5f766aee` | Fixed modules that does not support portable toolchain | 修复模块不支持可移植工具链的编译问题 |

### 维护评价

此插件**维护活跃**。虽然创建于 2019 年（约 7 年前），但近期（2026 年）有多次实质性更新，涵盖：

- **Bug 修复**：修复了 macOS 上笔事件、Windows 上多实例问题和坐标偏移等多个实际问题
- **平台兼容性**：修复了跨平台编译问题
- **代码维护**：迁移日志宏到新版 API

从更新记录看，Epic 仍在积极维护此插件的 Windows（Wintab + RealTimeStylus）和 macOS 后端。不过它仍标记为 **Beta** 且**默认未启用**，说明 API 可能尚未完全稳定，未来版本可能有接口变化。适合在受控环境中使用，但不建议在生产关键路径中深度依赖。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/StylusInput)
- [官方文档](https://docs.unrealengine.com)（此插件无独立文档页）