# Stylus & Tablet Plugin

> Support for advanced stylus and tablet inputs such as pressure, stylus and tablet buttons, and pen angles.

| 属性 | 值 |
|---|---|
| 中文名 | 手写笔输入 |
| 分类 | Input Devices |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `StylusInput` (Editor), `StylusInputDebugWidget` (EditorNoCommandlet), `StylusInputMac` (EditorNoCommandlet), `StylusInputRealTimeStylus` (EditorNoCommandlet), `StylusInputWintab` (EditorNoCommandlet) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-06-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/StylusInput) | |

## 用途

StylusInput 插件为 UE5 编辑器提供对数位板/手写笔（Wacom、Surface Pen 等）高级输入的支持。标准的鼠标/触摸输入无法获取压感、笔倾斜角度、气缸按钮等数据，而这些对于数字绘画、雕刻、手写批注等专业工作流至关重要。

该插件采用平台抽象架构：
- **核心模块 `StylusInput`**：定义统一的接口（`IStylusInputInstance`、`IStylusInputEventHandler`、`FStylusInputPacket`），并管理接口注册与实例生命周期。
- **平台实现模块**：分别对接不同平台的数位板 API——Windows 上通过 `Wintab`（传统驱动）和 `RealTimeStylus`（Windows Ink）两种接口，macOS 上通过原生 NSEvent API。
- **调试模块**：提供可视化调试 widget，用于验证数位板硬件输入是否正确识别。

这种设计允许上层代码只依赖核心模块，运行时自动选择当前平台可用的最佳接口。

## 使用场景

- 你在编辑器中实现**数字绘画/纹理绘制工具**，需要读取笔的压力来控制笔刷大小/透明度
- 你正在开发一个**手写批注/标注系统**，需要获取笔的倾斜角度和旋转信息
- 你需要区分**笔尖触碰、悬浮、反转（橡皮擦端）**等不同交互状态
- 你在为编辑器工具集成**数位板快捷按钮**映射
- 你需要在 Windows 上同时支持 **Wintab 驱动和 Windows Ink**（RealTimeStylus），以兼容不同品牌的数位板

## 蓝图用法

该插件**不暴露任何蓝图节点**。所有 API 均为纯 C++ 接口（`IStylusInputInstance`、`IStylusInputEventHandler` 等），没有 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)` 标记。如需在蓝图中使用，需自行编写 C++ 包装层桥接到蓝图。

## C++ 用法

### 头文件引入

```cpp
#include "StylusInput.h"
#include "StylusInputPacket.h"
#include "StylusInputTabletContext.h"
```

### 基本用法

以下展示如何创建实例并监听手写笔输入事件。核心流程为：创建实例 → 注册事件处理器 → 在回调中处理数据 → 不再需要时释放实例。

```cpp
// 来源: Public/StylusInput.h, Public/StylusInputPacket.h

#include "StylusInput.h"
#include "StylusInputPacket.h"
#include "StylusInputTabletContext.h"

using namespace UE::StylusInput;

// 1. 定义事件处理器
class FMyStylusHandler : public IStylusInputEventHandler
{
public:
    virtual FString GetName() override { return TEXT("MyStylusHandler"); }

    virtual void OnPacket(const FStylusInputPacket& Packet, IStylusInputInstance* Instance) override
    {
        // 根据包类型判断交互状态
        if (Packet.Type == EPacketType::OnDigitizer)
        {
            // 笔尖正在触碰绘制面
            float Pressure = Packet.NormalPressure;  // 压感值
            float X = Packet.X;                       // X 坐标（窗口坐标空间）
            float Y = Packet.Y;                       // Y 坐标（窗口坐标空间）
            float TiltX = Packet.XTiltOrientation;    // X 轴倾斜角
            float TiltY = Packet.YTiltOrientation;    // Y 轴倾斜角
        }
        else if (Packet.Type == EPacketType::AboveDigitizer)
        {
            // 笔在绘制面上方悬浮（proximity）
        }
        else if (Packet.Type == EPacketType::StylusDown)
        {
            // 笔尖刚触碰到绘制面
        }
        else if (Packet.Type == EPacketType::StylusUp)
        {
            // 笔尖刚离开绘制面
        }

        // 检查笔的状态标志
        bool bTouching = (Packet.PenStatus & EPenStatus::CursorIsTouching) != EPenStatus::None;
        bool bInverted = (Packet.PenStatus & EPenStatus::CursorIsInverted) != EPenStatus::None;  // 橡皮擦端
        bool bBarrelButton = (Packet.PenStatus & EPenStatus::BarrelButtonPressed) != EPenStatus::None;
    }
};

// 2. 在窗口初始化后创建实例
void SetupStylusInput(SWindow& MyWindow)
{
    IStylusInputInstance* StylusInstance = CreateInstance(MyWindow);
    if (StylusInstance && StylusInstance->WasInitializedSuccessfully())
    {
        // 在游戏线程上接收事件（推荐用于更新 UI/编辑器状态）
        static FMyStylusHandler Handler;
        StylusInstance->AddEventHandler(&Handler, EEventHandlerThread::OnGameThread);
    }
}

// 3. 不再需要时释放
void CleanupStylusInput(IStylusInputInstance* StylusInstance)
{
    if (StylusInstance)
    {
        StylusInstance->RemoveEventHandler(&Handler);
        ReleaseInstance(StylusInstance);
    }
}
```

### 进阶用法

查询数位板硬件信息，以及指定使用特定平台接口。

```cpp
// 来源: Public/StylusInput.h, Public/StylusInputTabletContext.h, Public/StylusInputInterface.h

using namespace UE::StylusInput;

// 查询当前可用的平台接口
TArray<FName> AvailableInterfaces = GetAvailableInterfaces();
for (const FName& Name : AvailableInterfaces)
{
    UE_LOG(LogTemp, Log, TEXT("Available stylus interface: %s"), *Name.ToString());
}

// 指定使用某个特定接口（如强制使用 Wintab）
IStylusInputInstance* Instance = CreateInstance(Window, FName("Wintab"), /*bRequestedInterfaceOnly=*/true);
if (!Instance)
{
    // Wintab 不可用，回退到默认
    Instance = CreateInstance(Window);
}

// 在事件回调中查询数位板和笔的详细信息
void OnPacket(const FStylusInputPacket& Packet, IStylusInputInstance* Instance) override
{
    // 获取数位板上下文信息
    TSharedPtr<IStylusInputTabletContext> TabletCtx = Instance->GetTabletContext(Packet.TabletContextID);
    if (TabletCtx.IsValid())
    {
        FString TabletName = TabletCtx->GetName();              // 数位板名称（如 "Wacom Intuos Pro"）
        FIntRect InputRect = TabletCtx->GetInputRectangle();    // 数位板物理输入区域（设备坐标）

        // 检查硬件能力
        ETabletHardwareCapabilities Caps = TabletCtx->GetHardwareCapabilities();
        bool bIntegrated = (Caps & ETabletHardwareCapabilities::Integrated) != ETabletHardwareCapabilities::None;
        bool bCursorMustTouch = (Caps & ETabletHardwareCapabilities::CursorMustTouch) != ETabletHardwareCapabilities::None;

        // 检查支持的属性（只有声明支持的属性才提供有效值）
        ETabletSupportedProperties SupportedProps = TabletCtx->GetSupportedProperties();
        bool bHasPressure = (SupportedProps & ETabletSupportedProperties::NormalPressure) != ETabletSupportedProperties::None;
        bool bHasTilt = (SupportedProps & ETabletSupportedProperties::XTiltOrientation) != ETabletSupportedProperties::None;
    }

    // 获取笔的信息
    TSharedPtr<IStylusInputStylusInfo> StylusInfo = Instance->GetStylusInfo(Packet.CursorID);
    if (StylusInfo.IsValid())
    {
        FString StylusName = StylusInfo->GetName();         // 笔的名称
        uint32 NumButtons = StylusInfo->GetNumButtons();    // 按钮数量

        for (uint32 i = 0; i < NumButtons; ++i)
        {
            const IStylusInputStylusButton* Button = StylusInfo->GetButton(i);
            if (Button)
            {
                FString ButtonID = Button->GetID();     // 按钮 GUID
                FString ButtonName = Button->GetName(); // 按钮名称
            }
        }
    }

    // 诊断信息：每秒处理的包数量
    float PPS = Instance->GetPacketsPerSecond(EEventHandlerThread::OnGameThread);
    UE_LOG(LogTemp, Log, TEXT("Packets/sec: %.1f"), PPS);
}
```

使用异步线程模式获取更高频率的输入数据（适用于实时笔迹渲染等延迟敏感场景）：

```cpp
// 异步线程接收事件（注意：回调不在游戏线程上，需要自行处理线程同步）
class FAsyncStylusHandler : public IStylusInputEventHandler
{
    FCriticalSection Mutex;
    TArray<FStylusInputPacket> PendingPackets;

public:
    virtual FString GetName() override { return TEXT("AsyncStylusHandler"); }

    virtual void OnPacket(const FStylusInputPacket& Packet, IStylusInputInstance* Instance) override
    {
        FScopeLock Lock(&Mutex);
        PendingPackets.Add(Packet);
    }

    // 在游戏线程上消费
    void ConsumePackets(TArray<FStylusInputPacket>& OutPackets)
    {
        FScopeLock Lock(&Mutex);
        OutPackets = MoveTemp(PendingPackets);
        PendingPackets.Reset();
    }
};

// 注册异步处理器
Instance->AddEventHandler(&AsyncHandler, EEventHandlerThread::Asynchronous);
```

## Demo 示例

一个完整的最小可编译示例：创建数位板输入实例，在控制台输出压力和坐标信息。

**MyStylusComponent.h**

```cpp
#pragma once

#include "StylusInput.h"
#include "StylusInputPacket.h"
#include "CoreMinimal.h"

class FMyStylusEventHandler : public UE::StylusInput::IStylusInputEventHandler
{
public:
    virtual FString GetName() override;
    virtual void OnPacket(const UE::StylusInput::FStylusInputPacket& Packet,
                          UE::StylusInput::IStylusInputInstance* Instance) override;
};

/**
 * 简单的数位板输入管理器，演示基本的创建、监听、清理流程。
 */
class FMyStylusManager
{
public:
    void Initialize(SWindow& Window);
    void Shutdown();

private:
    UE::StylusInput::IStylusInputInstance* Instance = nullptr;
    FMyStylusEventHandler Handler;
};
```

**MyStylusComponent.cpp**

```cpp
#include "MyStylusComponent.h"

using namespace UE::StylusInput;

FString FMyStylusEventHandler::GetName()
{
    return TEXT("MyStylusEventHandler");
}

void FMyStylusEventHandler::OnPacket(const FStylusInputPacket& Packet, IStylusInputInstance* Instance)
{
    if (Packet.Type == EPacketType::OnDigitizer)
    {
        UE_LOG(LogTemp, Log, TEXT("Stylus [%u] at (%.1f, %.1f), Pressure: %.3f, Tilt: (%.1f, %.1f)"),
            Packet.CursorID, Packet.X, Packet.Y, Packet.NormalPressure,
            Packet.XTiltOrientation, Packet.YTiltOrientation);
    }

    if ((Packet.PenStatus & EPenStatus::BarrelButtonPressed) != EPenStatus::None)
    {
        UE_LOG(LogTemp, Log, TEXT("Barrel button pressed!"));
    }

    if ((Packet.PenStatus & EPenStatus::CursorIsInverted) != EPenStatus::None)
    {
        UE_LOG(LogTemp, Log, TEXT("Eraser end detected"));
    }
}

void FMyStylusManager::Initialize(SWindow& Window)
{
    Instance = CreateInstance(Window);
    if (Instance && Instance->WasInitializedSuccessfully())
    {
        Instance->AddEventHandler(&Handler, EEventHandlerThread::OnGameThread);
        UE_LOG(LogTemp, Log, TEXT("Stylus input initialized with interface: %s"),
            *Instance->GetInterfaceName().ToString());
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Failed to initialize stylus input. Available interfaces:"));
        for (const FName& Name : GetAvailableInterfaces())
        {
            UE_LOG(LogTemp, Warning, TEXT("  - %s"), *Name.ToString());
        }
    }
}

void FMyStylusManager::Shutdown()
{
    if (Instance)
    {
        Instance->RemoveEventHandler(&Handler);
        ReleaseInstance(Instance);
        Instance = nullptr;
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Slate 等） | 该插件的公共头文件仅依赖 Core、CoreUObject、Slate 等基础模块；平台实现模块的内部依赖由插件自身管理 |

> **注意**：要使用此插件，你需要在项目的 `.uproject` 或 `.Build.cs` 中启用 `StylusInput` 插件。由于 `EnabledByDefault=false`，必须手动启用。平台实现模块（`StylusInputWintab`、`StylusInputRealTimeStylus`、`StylusInputMac`）会自动在对应平台上加载，无需额外配置。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-19 | `9693e160` | StylusInput: Fix NSEvent up/down | 修复 macOS 上笔尖抬起/落下事件的处理错误 |
| 2026-05-19 | `36a0dc9c` | StylusInput: Fix issue with multiple Wintab instances | 修复多个 Wintab 实例共存时的问题 |
| 2026-05-13 | `041d4d75` | StylusInput: Fix coordinates issue with Wintab when main screen is not on left/top | 修复主屏幕不在左上角时 Wintab 坐标计算错误 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移至 UE_LOGF 新格式 |
| 2026-01-28 | `5f766aee` | Fixed modules that does not support portable toolchain | 修复不支持可移植工具链的模块编译问题 |

### 维护评价

- **创建时间**：2019 年（UE 4.23 时代），已存在约 7 年
- **近期活跃度**：2026 年 1-5 月有多次实质性 bug 修复（坐标计算、多实例、macOS 事件），说明仍在积极维护
- **实验性状态**：`IsBetaVersion=true` 且 `EnabledByDefault=false`，表明 Epic 仍将此视为实验性功能
- **平台覆盖**：Windows（Wintab + Windows Ink）和 macOS 均有实现，覆盖主流平台
- **已知限制**：
  - 仍标记为 Beta，API 可能在未来版本中变化
  - 需要手动启用插件
  - 仅限编辑器环境（Editor 模块类型），不支持打包后的运行时应用
- **推荐程度**：**推荐在编辑器工具中使用**。虽然标记为 Beta，但代码质量较高，接口设计清晰，近期维护活跃。如果你的编辑器工具需要数位板输入，这是官方唯一的原生支持方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/StylusInput)
- [官方文档]()（无）