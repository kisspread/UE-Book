# Stylus & Tablet Plugin

> Support for advanced stylus and tablet inputs such as pressure, stylus and tablet buttons, and pen angles.

| 属性 | 值 |
|---|---|
| 中文名 | 数位板输入 |
| 分类 | Input Devices |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `StylusInput` (Editor), `StylusInputDebugWidget` (EditorNoCommandlet), `StylusInputMac` (EditorNoCommandlet), `StylusInputRealTimeStylus` (EditorNoCommandlet), `StylusInputWintab` (EditorNoCommandlet) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-06-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/StylusInput) | |

## 用途

UE5 内置的输入系统只处理标准鼠标/键盘/手柄事件，无法获取数位板（Wacom、Huion 等）的高级特性——压力感应、笔倾斜角度、笔身旋转、笔身按钮等。StylusInput 插件填补了这一空缺，为编辑器环境下的数位板输入提供统一抽象层。

插件采用**多后端架构**，通过 `IStylusInputInterface` 接口抽象底层实现：

- **Windows**：同时支持两种 API
  - **RealTimeStylus**（微软 Ink API）：通过 COM 接口 `IRealTimeStylus` 获取高精度数据包，支持同步/异步两种插件模式
  - **Wintab**：兼容传统 Wintab 驱动，覆盖不支持 RealTimeStylus 的旧设备
- **macOS**：通过原生 `NSEvent` 获取 Apple Pencil / 数位板事件

插件自动选择当前平台可用的最佳后端，为上层提供统一的 `IStylusInputInstance` 和 `IStylusInputEventHandler` 接口。所有数位板属性（压力、倾斜、旋转、坐标范围等）统一用 `EPacketPropertyType` 枚举描述，包含 20+ 种属性类型。

**重要**：此插件**默认未启用**且处于 **Beta** 状态，需要在项目设置中手动启用。

## 使用场景

- 你在编辑器中制作 2D 绘画/雕刻工具，需要获取笔压来控制笔刷大小或透明度
- 你开发了一个编辑器内绘画插件，需要根据笔的倾斜角度模拟真实画笔效果
- 你需要读取数位板上多个按钮的状态来映射不同工具
- 你需要在编辑器工具中支持 Wacom/Huion/XP-Pen 等数位板的完整功能
- 你需要在 Mac 上用 Apple Pencil 进行编辑器内的手绘输入

## 蓝图用法

本插件为纯 C++ API，没有暴露 `BlueprintCallable` 节点。所有功能通过 C++ 接口访问。

如需在蓝图中使用数位板输入，需要编写 C++ 薄封装层将事件转发到蓝图可调用的函数或委托。

## C++ 用法

### 头文件引入

```cpp
#include "StylusInput.h"
#include "StylusInputInterface.h"
```

### 核心接口

插件的核心抽象在 `IStylusInputInterface` 和相关接口中：

| 接口 | 说明 |
|---|---|
| `IStylusInputInterface` | 后端工厂接口，每个平台实现一份 |
| `IStylusInputInstance` | 绑定到一个窗口的输入实例 |
| `IStylusInputEventHandler` | 事件处理器，用户实现此接口来接收事件 |
| `IStylusInputTabletContext` | 数位板设备上下文（设备信息、输入范围、支持的属性） |
| `IStylusInputStylusInfo` | 笔信息（ID、名称、按钮列表） |
| `IStylusInputStylusButton` | 笔按钮信息 |

### 基本用法

创建数位板输入实例并注册事件处理器：

```cpp
#include "StylusInput.h"
#include "StylusInputInterface.h"

// 获取平台默认的数位板接口
IStylusInputInterface* StylusInterface = IStylusInputInterface::GetDefault();
if (!StylusInterface || !StylusInterface->IsValid())
{
    UE_LOG(LogTemp, Warning, TEXT("No stylus input interface available"));
    return;
}

// 为目标窗口创建输入实例
TSharedPtr<SWindow> TargetWindow = /* 获取目标窗口 */;
IStylusInputInstance* StylusInstance = StylusInterface->CreateInstance(*TargetWindow);
if (!StylusInstance || !StylusInstance->WasInitializedSuccessfully())
{
    UE_LOG(LogTemp, Warning, TEXT("Failed to create stylus instance"));
    return;
}

// 创建并注册事件处理器
class FMyStylusHandler : public IStylusInputEventHandler
{
public:
    virtual void OnStylusDown(const FStylusInputPacket& Packet) override
    {
        // 笔尖触碰数位板
        float Pressure = Packet.GetFloat(EPacketPropertyType::NormalPressure);
        float X = Packet.GetFloat(EPacketPropertyType::X);
        float Y = Packet.GetFloat(EPacketPropertyType::Y);
        UE_LOG(LogTemp, Log, TEXT("Stylus Down at (%.1f, %.1f) pressure=%.3f"), X, Y, Pressure);
    }

    virtual void OnStylusUp(const FStylusInputPacket& Packet) override
    {
        UE_LOG(LogTemp, Log, TEXT("Stylus Up"));
    }

    virtual void OnPackets(const FStylusInputPacket* Packets, int32 Count) override
    {
        // 连续绘制时的数据包流
        for (int32 i = 0; i < Count; ++i)
        {
            float Pressure = Packets[i].GetFloat(EPacketPropertyType::NormalPressure);
            float X = Packets[i].GetFloat(EPacketPropertyType::X);
            float Y = Packets[i].GetFloat(EPacketPropertyType::Y);
            // 使用数据绘制...
        }
    }
};

FMyStylusHandler* Handler = new FMyStylusHandler();
StylusInstance->AddEventHandler(Handler, EEventHandlerThread::GameThread);
```

（基于 `FRealTimeStylusInstance` 的 `AddEventHandler` 实现和 `EPacketPropertyType` 枚举推断）

### 进阶用法

读取数位板设备信息和笔倾斜角度：

```cpp
// 查询当前连接的数位板上下文
const TSharedPtr<IStylusInputTabletContext> TabletContext = StylusInstance->GetTabletContext(TabletContextID);
if (TabletContext.IsValid())
{
    UE_LOG(LogTemp, Log, TEXT("Tablet: %s"), *TabletContext->GetName());
    UE_LOG(LogTemp, Log, TEXT("Input rect: %s"), *TabletContext->GetInputRectangle().ToString());

    // 检查硬件能力
    ETabletHardwareCapabilities Capabilities = TabletContext->GetHardwareCapabilities();
    bool bSupportsPressure = EnumHasAllFlags(TabletContext->GetSupportedProperties(),
                                              ETabletSupportedProperties::NormalPressure);
}

// 查询笔信息
const TSharedPtr<IStylusInputStylusInfo> StylusInfo = StylusInstance->GetStylusInfo(StylusID);
if (StylusInfo.IsValid())
{
    UE_LOG(LogTemp, Log, TEXT("Stylus: %s with %d buttons"), *StylusInfo->GetName(), StylusInfo->GetNumButtons());
    for (int32 i = 0; i < StylusInfo->GetNumButtons(); ++i)
    {
        const IStylusInputStylusButton* Button = StylusInfo->GetButton(i);
        UE_LOG(LogTemp, Log, TEXT("  Button %d: %s"), i, *Button->GetName());
    }
}

// 在事件处理器中获取笔倾斜角度
virtual void OnPackets(const FStylusInputPacket* Packets, int32 Count) override
{
    for (int32 i = 0; i < Count; ++i)
    {
        // 笔的 X/Y 倾斜角（0 = 垂直于板面）
        float XTilt = Packets[i].GetFloat(EPacketPropertyType::XTiltOrientation);
        float YTilt = Packets[i].GetFloat(EPacketPropertyType::YTiltOrientation);

        // 方位角和高度角
        float Azimuth = Packets[i].GetFloat(EPacketPropertyType::AzimuthOrientation);
        float Altitude = Packets[i].GetFloat(EPacketPropertyType::AltitudeOrientation);

        // 笔身扭转
        float Twist = Packets[i].GetFloat(EPacketPropertyType::TwistOrientation);

        // 根据倾斜角度计算笔刷形状...
    }
}

// 监控输入性能
float PacketsPerSecond = StylusInstance->GetPacketsPerSecond(EEventHandlerThread::GameThread);
UE_LOG(LogTemp, Log, TEXT("Input rate: %.1f packets/sec"), PacketsPerSecond);
```

（基于 `EPacketPropertyType` 枚举的完整属性列表和 `IStylusInputTabletContext`/`IStylusInputStylusInfo` 接口推断）

### Windows 后端选择

在 Win64 上，插件提供两个可选后端：

| 后端 | 模块 | API | 说明 |
|---|---|---|---|
| RealTimeStylus | `StylusInputRealTimeStylus` | Microsoft Ink/COM | 现代 API，精度高，支持更多属性 |
| Wintab | `StylusInputWintab` | Wintab32 DLL | 传统驱动接口，兼容性更广 |

插件会在运行时自动探测并选择可用的后端。如果两者都可用，优先使用 RealTimeStylus。

## Demo 示例

一个最小的编辑器工具数位板输入监听示例：

```cpp
// StylusDemoTool.h
#pragma once

#include "StylusInput.h"
#include "StylusInputInterface.h"

class FStylusDemoTool : public IStylusInputEventHandler
{
public:
    FStylusDemoTool();
    ~FStylusDemoTool();

    void Initialize(TSharedPtr<SWindow> InWindow);
    void Shutdown();

    // IStylusInputEventHandler
    virtual void OnStylusDown(const FStylusInputPacket& Packet) override;
    virtual void OnStylusUp(const FStylusInputPacket& Packet) override;
    virtual void OnPackets(const FStylusInputPacket* Packets, int32 Count) override;
    virtual void OnTabletAdded(const TSharedPtr<IStylusInputTabletContext>& Context) override;
    virtual void OnTabletRemoved(uint32 TabletContextID) override;

private:
    IStylusInputInstance* StylusInstance = nullptr;
    bool bIsDrawing = false;
};
```

```cpp
// StylusDemoTool.cpp
#include "StylusDemoTool.h"

FStylusDemoTool::FStylusDemoTool()
{
}

FStylusDemoTool::~FStylusDemoTool()
{
    Shutdown();
}

void FStylusDemoTool::Initialize(TSharedPtr<SWindow> InWindow)
{
    IStylusInputInterface* StylusInterface = IStylusInputInterface::GetDefault();
    if (!StylusInterface || !StylusInterface->IsValid())
    {
        UE_LOG(LogTemp, Warning, TEXT("No stylus input interface available on this platform"));
        return;
    }

    StylusInstance = StylusInterface->CreateInstance(*InWindow);
    if (StylusInstance && StylusInstance->WasInitializedSuccessfully())
    {
        StylusInstance->AddEventHandler(this, EEventHandlerThread::GameThread);
        UE_LOG(LogTemp, Log, TEXT("Stylus demo tool initialized with interface: %s"),
               *StylusInstance->GetInterfaceName().ToString());
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to initialize stylus instance"));
    }
}

void FStylusDemoTool::Shutdown()
{
    if (StylusInstance)
    {
        StylusInstance->RemoveEventHandler(this);
        // Interface owns the instance lifetime
        StylusInstance = nullptr;
    }
}

void FStylusDemoTool::OnStylusDown(const FStylusInputPacket& Packet)
{
    bIsDrawing = true;
    float X = Packet.GetFloat(EPacketPropertyType::X);
    float Y = Packet.GetFloat(EPacketPropertyType::Y);
    float Pressure = Packet.GetFloat(EPacketPropertyType::NormalPressure);
    UE_LOG(LogTemp, Log, TEXT("=== Stylus Down === (%.1f, %.1f) P=%.2f"), X, Y, Pressure);
}

void FStylusDemoTool::OnStylusUp(const FStylusInputPacket& Packet)
{
    bIsDrawing = false;
    UE_LOG(LogTemp, Log, TEXT("=== Stylus Up ==="));
}

void FStylusDemoTool::OnPackets(const FStylusInputPacket* Packets, int32 Count)
{
    if (!bIsDrawing)
    {
        return;
    }

    for (int32 i = 0; i < Count; ++i)
    {
        float X = Packets[i].GetFloat(EPacketPropertyType::X);
        float Y = Packets[i].GetFloat(EPacketPropertyType::Y);
        float Pressure = Packets[i].GetFloat(EPacketPropertyType::NormalPressure);

        // 在此处处理绘制逻辑
        // 例如：根据 Pressure 调整笔刷大小，根据 X/Y 在画布上绘制点
    }
}

void FStylusDemoTool::OnTabletAdded(const TSharedPtr<IStylusInputTabletContext>& Context)
{
    UE_LOG(LogTemp, Log, TEXT("Tablet added: %s"), *Context->GetName());
    UE_LOG(LogTemp, Log, TEXT("  Input rect: %s"), *Context->GetInputRectangle().ToString());
    UE_LOG(LogTemp, Log, TEXT("  Supported properties: 0x%X"),
           static_cast<uint32>(Context->GetSupportedProperties()));
}

void FStylusDemoTool::OnTabletRemoved(uint32 TabletContextID)
{
    UE_LOG(LogTemp, Log, TEXT("Tablet removed: context %u"), TabletContextID);
}
```

（基于 `IStylusInputEventHandler`、`IStylusInputInterface`、`IStylusInputInstance` 的接口模式和 `EPacketPropertyType` 推断的完整示例）

## 可用的数位板属性

`EPacketPropertyType` 枚举定义了所有可查询的数据包属性（源码位于 `RealTimeStylusTabletContext.h`）：

| 属性 | 说明 |
|---|---|
| `X` / `Y` | 笔尖在数位板坐标系中的位置 |
| `Z` | 笔尖与板面的距离 |
| `NormalPressure` | 笔尖垂直压力（影响笔画粗细） |
| `TangentPressure` | 笔尖沿板面的压力 |
| `ButtonPressure` | 压力感应按钮的压力值 |
| `XTiltOrientation` / `YTiltOrientation` | 笔的 X/Y 倾斜角（0°=垂直） |
| `AzimuthOrientation` | 笔绕 Z 轴的方位角 |
| `AltitudeOrientation` | 笔轴与板面的夹角（0°=平行, 90°=垂直） |
| `TwistOrientation` | 笔绕自身轴的扭转角度 |
| `PitchRotation` / `RollRotation` / `YawRotation` | 3D 数位器的旋转属性 |
| `Width` / `Height` | 触控数位器的接触面积 |
| `FingerContactConfidence` | 手指接触的置信度 |
| `PacketStatus` | 状态标志（触碰/倒置/笔身按钮） |
| `TimerTick` | 数据包生成时间戳（毫秒） |
| `SerialNumber` | 数据包唯一标识符 |

## 模块架构

```
StylusInput (Editor)                    ← 核心抽象层，平台无关接口
├── StylusInputDebugWidget              ← 调试可视化 UI
├── StylusInputMac (Mac only)           ← macOS NSEvent 后端
├── StylusInputRealTimeStylus (Win64)   ← Windows COM/Ink 后端
└── StylusInputWintab (Win64)           ← Windows Wintab 驱动后端
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Slate` | 窗口系统（`SWindow` 绑定） |
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | |

`StylusInputRealTimeStylus` 和 `StylusInputWintab` 模块通过动态加载 Windows 系统 DLL（`RTSCom.dll`、`wintab32.dll`）访问数位板 API，不需要额外的 UE 模块依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-19 | `9693e160` | StylusInput: Fix NSEvent up/down | 修复 Mac 端 NSEvent 笔抬起/按下事件 |
| 2026-05-19 | `36a0dc9c` | StylusInput: Fix issue with multiple Wintab instances | 修复多个 Wintab 实例共存时的问题 |
| 2026-05-13 | `041d4d75` | StylusInput: Fix coordinates issue with Wintab when main screen is not on left/top | 修复主显示器不在左上角时 Wintab 坐标偏移 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到新格式 |
| 2026-01-28 | `5f766aee` | Fixed modules that does not support portable toolchain | 修复可移植工具链兼容性 |

### 维护评价

**维护状态：活跃维护 ✅**

- 插件创建于 2019 年（约 7 年前），是 UE4 4.23 时期引入的功能
- 2026 年仍有持续的 bug 修复和平台兼容性改进，最近一次更新距今不到一个月
- 近期更新集中在修复实际使用中的坐标计算和多实例问题，说明有用户在实际使用
- 仍然是 **Beta** 状态且**默认未启用**，说明 Epic 认为 API 可能还有变动
- Mac 和 Windows 双平台都有近期修复，说明跨平台支持仍在推进
- **推荐使用**：如果你的编辑器工具需要数位板输入，这是唯一官方支持的方案。虽然标记为 Beta，但已稳定运行多年且持续维护。注意需要手动启用 `EnabledByDefault=false`。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/StylusInput)
- 官方文档（无）