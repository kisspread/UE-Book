# Stylus & Tablet Plugin

> Support for advanced stylus and tablet inputs such as pressure, stylus and tablet buttons, and pen angles.

| 属性 | 值 |
|---|---|
| 分类 | Input Devices |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `StylusInput` (Editor), `StylusInputDebugWidget` (EditorNoCommandlet), `StylusInputMac` (EditorNoCommandlet), `StylusInputRealTimeStylus` (EditorNoCommandlet), `StylusInputWintab` (EditorNoCommandlet) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-05-17 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/StylusInput) | |

## 用途

StylusInput 为 Unreal Editor 提供数位板/手写笔（stylus）输入支持。它抽象了多个平台特定的数位板 API（Windows 上的 RealTimeStylus COM API 和 Wintab API，macOS 上的 NSEvent），提供统一的 C++ 接口来读取笔压力、倾斜角度、旋转、按钮状态等高级手写笔数据。

这个 plugin **仅限编辑器使用**（所有模块都是 Editor 或 EditorNoCommandlet 类型），主要面向开发编辑器内绘画工具、笔刷工具等需要读取手写笔压力和倾斜数据的场景。它不适用于运行时游戏输入——运行时游戏应使用 Enhanced Input 或其他输入系统。

### 为什么存在？

UE 的标准输入系统（Enhanced Input 等）不直接支持数位板的高级属性（压力、倾斜、旋转）。StylusInput 填补了这个空白，为编辑器工具开发者提供了统一的手写笔数据访问接口。

## 使用场景

- 你在编辑器中开发一个 3D 雕刻/绘画工具，需要读取笔压力来控制笔刷强度
- 你需要检测手写笔的倾斜角度来实现自然的笔触效果
- 你想在编辑器中创建一个数位板测试/调试工具
- 你需要区分不同的手写笔按钮（桶形按钮、笔尖按钮等）

## 模块架构

本插件采用**接口注册**架构。核心模块定义抽象接口，平台模块注册具体实现。

```
StylusInput (核心模块)
├── IStylusInputInterface     ← 平台 API 抽象
├── IStylusInputInstance      ← 每窗口实例
├── IStylusInputEventHandler  ← 事件回调
├── FStylusInputPacket        ← 数据包（压力、倾斜等）
└── IStylusInputTabletContext ← 数位板设备信息

StylusInputRealTimeStylus (Win64)  ← Microsoft RealTimeStylus COM API
StylusInputWintab (Win64)          ← Wintab API（兼容旧设备）
StylusInputMac (Mac)               ← macOS NSEvent API
StylusInputDebugWidget             ← 调试/可视化控件
```

### 接口优先级

在 Windows 上，`RealTimeStylus` 接口会被优先注册为默认接口（源码中有 HACK 注释说明这是临时方案）。如果 RealTimeStylus 不可用，系统会回退到 Wintab。

| 接口名称 | 平台 | API | 说明 |
|---|---|---|---|
| `RealTimeStylus` | Win64 | Microsoft COM RealTimeStylus | 默认首选，支持更现代的数位板 |
| `Wintab` | Win64 | Wintab API | 兼容旧款数位板（如老款 Wacom） |
| `NSEvent` | Mac | macOS NSEvent | macOS 原生支持 |

子模块详细文档：

- [StylusInputRealTimeStylus](StylusInputRealTimeStylus.md) — Windows RealTimeStylus 后端
- [StylusInputWintab](StylusInputWintab.md) — Windows Wintab 后端
- [StylusInputMac](StylusInputMac.md) — macOS 后端
- [StylusInputDebugWidget](StylusInputDebugWidget.md) — 调试控件

## C++ 用法

### 头文件引入

```cpp
#include "StylusInput.h"              // CreateInstance / ReleaseInstance
#include "StylusInputInterface.h"     // GetAvailableInterfaces / RegisterInterface
#include "StylusInputPacket.h"        // FStylusInputPacket, EPenStatus, EPacketType
#include "StylusInputTabletContext.h" // IStylusInputTabletContext, IStylusInputStylusInfo
```

### 基本用法

```cpp
using namespace UE::StylusInput;

// 1. 定义事件处理器
class FMyEventHandler : public IStylusInputEventHandler
{
public:
    virtual FString GetName() override { return TEXT("MyEventHandler"); }

    virtual void OnPacket(const FStylusInputPacket& Packet, IStylusInputInstance* Instance) override
    {
        // 获取数位板上下文信息
        TSharedPtr<IStylusInputTabletContext> Context = Instance->GetTabletContext(Packet.TabletContextID);
        if (Context.IsValid())
        {
            // 检查是否支持压力
            bool bHasPressure = EnumHasAnyFlags(Context->GetSupportedProperties(), ETabletSupportedProperties::NormalPressure);
        }

        // 读取压力值（0.0 ~ 1.0+，取决于设备）
        float Pressure = Packet.NormalPressure;

        // 读取倾斜角度
        float XTilt = Packet.XTiltOrientation;
        float YTilt = Packet.YTiltOrientation;

        // 检查笔的状态
        bool bIsDrawing = EnumHasAnyFlags(Packet.PenStatus, EPenStatus::CursorIsTouching);
        bool bIsEraser  = EnumHasAnyFlags(Packet.PenStatus, EPenStatus::CursorIsInverted);
        bool bBarrelBtn = EnumHasAnyFlags(Packet.PenStatus, EPenStatus::BarrelButtonPressed);

        // 获取手写笔信息
        TSharedPtr<IStylusInputStylusInfo> Stylus = Instance->GetStylusInfo(Packet.CursorID);
    }
};

// 2. 创建实例并注册事件处理器
IStylusInputInstance* Instance = CreateInstance(*MySWindow);
if (Instance)
{
    FMyEventHandler* Handler = new FMyEventHandler();
    // 在游戏线程上接收事件
    Instance->AddEventHandler(Handler, EEventHandlerThread::OnGameThread);
    // 或在异步线程上接收（更高性能，但需要注意线程安全）
    // Instance->AddEventHandler(Handler, EEventHandlerThread::Asynchronous);
}

// 3. 清理
Instance->RemoveEventHandler(Handler);
ReleaseInstance(Instance);
```

### 指定接口

```cpp
// 只使用 Wintab 接口
IStylusInputInstance* Instance = CreateInstance(*MyWindow, FName("Wintab"), /*bRequestedInterfaceOnly=*/true);

// 查询可用接口
TArray<FName> Interfaces = GetAvailableInterfaces();
// 可能返回: {"RealTimeStylus", "Wintab"}
```

### 数据结构参考

#### FStylusInputPacket 字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `TabletContextID` | `uint32` | 数位板上下文 ID |
| `CursorID` | `uint32` | 手写笔/光标 ID |
| `Type` | `EPacketType` | 交互类型（OnDigitizer / AboveDigitizer / StylusDown / StylusUp） |
| `PenStatus` | `EPenStatus` | 笔状态标志位（触摸/反转/桶形按钮） |
| `X`, `Y`, `Z` | `float` | 坐标（Z 为笔尖到板面距离） |
| `NormalPressure` | `float` | 笔尖垂直压力 |
| `TangentPressure` | `float` | 笔尖切面压力 |
| `XTiltOrientation`, `YTiltOrientation` | `float` | X/Y 轴倾斜角度 |
| `AzimuthOrientation`, `AltitudeOrientation` | `float` | 方位角/仰角 |
| `TwistOrientation` | `float` | 笔身旋转 |
| `PitchRotation`, `RollRotation`, `YawRotation` | `float` | 3D 旋转（需要 3D 数位化仪） |
| `Width`, `Height` | `float` | 触摸面积（触摸数位化仪） |
| `FingerContactConfidence` | `float` | 手指触摸置信度 |
| `DeviceContactID` | `int32` | 设备接触 ID（区分多指） |

#### EPenStatus 标志

| 标志 | 值 | 说明 |
|---|---|---|
| `None` | `0x00` | 无标志 |
| `CursorIsTouching` | `0x01` | 笔尖正在接触板面 |
| `CursorIsInverted` | `0x02` | 笔倒置（橡皮擦端朝下） |
| `BarrelButtonPressed` | `0x08` | 桶形按钮按下 |

#### EPacketType

| 值 | 说明 |
|---|---|
| `Invalid` | 无效包 |
| `OnDigitizer` | 笔尖接触板面时生成 |
| `AboveDigitizer` | 笔在板面上方悬停时生成 |
| `StylusDown` | 笔尖开始接触板面 |
| `StylusUp` | 笔尖离开板面 |

## 蓝图用法

本插件**没有 Blueprint 接口**。所有 API 都是纯 C++ 接口（`UE::StylusInput` 命名空间中的抽象类），没有 `UCLASS`、`UFUNCTION` 或 `UPROPERTY` 标记。如需在蓝图中使用手写笔数据，需要自行编写 C++ 包装层并暴露为 BlueprintCallable 函数。

## Demo 示例

### 最小可编译示例

**MyStylusTool.h**
```cpp
#pragma once
#include "StylusInput.h"
#include "StylusInputPacket.h"

class FMyStylusTool : public UE::StylusInput::IStylusInputEventHandler
{
public:
    void Init(SWindow& Window);
    void Shutdown();

    // IStylusInputEventHandler
    virtual FString GetName() override { return TEXT("MyStylusTool"); }
    virtual void OnPacket(const UE::StylusInput::FStylusInputPacket& Packet,
                          UE::StylusInput::IStylusInputInstance* Instance) override;

private:
    UE::StylusInput::IStylusInputInstance* Instance = nullptr;
};
```

**MyStylusTool.cpp**
```cpp
#include "MyStylusTool.h"

void FMyStylusTool::Init(SWindow& Window)
{
    using namespace UE::StylusInput;
    Instance = CreateInstance(Window);
    if (Instance)
    {
        Instance->AddEventHandler(this, EEventHandlerThread::OnGameThread);
    }
}

void FMyStylusTool::Shutdown()
{
    using namespace UE::StylusInput;
    if (Instance)
    {
        Instance->RemoveEventHandler(this);
        ReleaseInstance(Instance);
        Instance = nullptr;
    }
}

void FMyStylusTool::OnPacket(const UE::StylusInput::FStylusInputPacket& Packet,
                              UE::StylusInput::IStylusInputInstance* Instance)
{
    if (EnumHasAnyFlags(Packet.PenStatus, UE::StylusInput::EPenStatus::CursorIsTouching))
    {
        // 笔正在绘画 — 使用 Packet.NormalPressure、Packet.X、Packet.Y 等
    }
}
```

**Build.cs 依赖**
```csharp
PublicDependencyModuleNames.AddRange(new string[] { "StylusInput" });
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 基础库 |
| `CoreUObject` | UObject 系统 |
| `Slate` | UI 框架（SWindow） |
| `SlateCore` | Slate 核心（私有依赖） |
| `Engine` | 引擎核心 |
| `UnrealEd` | 编辑器框架 |
| `EditorSubsystem` | 编辑器子系统 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-10-03 | `7a4aec64e2a7` | Fix debug widget not receiving packets after widget gets attached to a different window | 修复调试控件在窗口切换后丢失数据包的 bug |
| 2025-09-04 | `0e89243095e9` | Minor fixes for Mac Stylus | macOS 平台修复 |
| 2025-09-04 | `d742bf592b0d` | StylusInput: MacOS support | **新增 macOS 支持**（NSEvent 后端） |

### 维护评价

- **创建时间**：2019 年 5 月，约 7 年历史
- **最近更新**：2025 年 10 月，非常活跃
- **重大变化**：2025 年 9 月新增了 macOS 支持，说明 Epic 仍在积极扩展此插件
- **Beta 状态**：`.uplugin` 标记 `IsBetaVersion=true`，表明仍被视为实验性功能
- **默认关闭**：`EnabledByDefault=false`，需要手动在编辑器设置中启用
- **已知限制**：
  - 纯 Editor 插件，不支持运行时
  - Windows 上 RealTimeStylus 被硬编码为默认接口（源码中标记为 HACK）
  - 没有 Blueprint 接口
  - 没有官方文档（DocsURL 为空）

**评价**：虽然标记为 Beta，但实际上已被 Epic 持续维护了 7 年，且最近还新增了 macOS 支持。推荐在编辑器工具开发中使用，但需要注意它仍然是实验性 API，接口可能在未来的 UE 版本中发生变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/StylusInput)
- 官方文档（无）
