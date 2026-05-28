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

此插件为虚幻编辑器提供了标准化的接口，用于接收来自数位板和压感笔的高级输入数据。它解决了不同操作系统（Windows 的 Wintab/RealTimeStylus API、macOS 的 NSEvent）和硬件（Wacom 等）之间的底层差异，为编辑器工具（如数字雕刻、绘画）提供统一的压感、倾斜角度、笔身按钮等输入。该插件**仅适用于编辑器**，无法在运行时（Runtime）使用。

## 使用场景

- 你在使用带有压感功能的数位笔在编辑器中绘制纹理或蓝图。
- 你需要在自定义编辑器工具中，根据压感笔的倾斜角度或压力来调整笔刷效果。
- 你在开发一个编辑器扩展，需要精确控制通过压感笔输入的轨迹。

## 蓝图用法

由于该插件主要是底层 C++ 接口，用于编辑器内部集成，因此直接暴露给蓝图的公开函数（BlueprintCallable）非常有限。其主要使用场景是作为其他编辑器功能（如 Paint、Sculpt）的输入源。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| 无直接公开蓝图节点 | 该插件主要提供 C++ 接口，供其他插件或模块调用。其提供的调试小部件（`StylusInputDebugWidget`）可在编辑器内用于监控输入。 | - |

### 使用示例（蓝图描述）

在编辑器中，你可以通过 `Window -> Developer Tools -> Output Log` 或通过添加 `Stylus Input Debug Widget` 面板来查看插件是否正常工作以及输入数据流。不建议直接在游戏逻辑蓝图中使用此插件。

## C++ 用法

该插件的核心在于实现和响应 `IStylusInputEventHandler` 接口以接收压感数据，或创建 `IStylusInputInstance` 实例来管理一个窗口的数位板输入。

### 头文件引入

```cpp
#include "StylusInput/IStylusInputEventHandler.h"
#include "StylusInput/IStylusInputInstance.h"
```

### 基本用法

处理数位板事件，例如绘制线段。此代码片段展示了如何创建一个简单的事件处理器来记录笔尖位置和压力。

```cpp
// 来自 StylusInput 模块的测试或示例代码
#include "IStylusInputEventHandler.h"
#include "IStylusInputInstance.h"

class FMyTabletHandler : public UE::StylusInput::IStylusInputEventHandler
{
public:
    virtual void OnPacket(const UE::StylusInput::IStylusInputInstance& Instance, const UE::StylusInput::IStylusInputPacket& Packet) override
    {
        // 从数据包中获取标准化的坐标和压力
        const FVector2D Position = Packet.GetPosition();
        const float Pressure = Packet.GetNormalPressure();
        UE_LOG(LogTemp, Log, TEXT("Stylus Pos: (%f, %f), Pressure: %f"), Position.X, Position.Y, Pressure);
    }

    virtual void OnStylusButtonDown(const UE::StylusInput::IStylusInputInstance& Instance, const UE::StylusInput::IStylusInputStylusButton& Button) override
    {
        UE_LOG(LogTemp, Log, TEXT("Stylus Button Down: %s"), *Button.GetName());
    }

    // ... 实现其他必要的虚函数，如 OnStylusButtonUp, OnTabletAdded 等。
};

// 要使用它，你需要获取一个窗口对应的 IStylusInputInstance
// 通常由编辑器框架管理，例如在自定义的 SCompoundWidget 中：
void SMyDrawingWidget::Construct(const FArguments& InArgs)
{
    // ... 构造逻辑
    if (IStylusInputInstance* StylusInstance = /* 从全局或模块获取 */)
    {
        MyHandler = MakeShared<FMyTabletHandler>();
        StylusInstance->AddEventHandler(MyHandler.Get(), EEventHandlerThread::GameThread);
    }
}
```

### 进阶用法

直接创建并管理一个数位板输入实例，用于自定义的编辑器窗口。这需要调用底层的 `IStylusInputInterface`。

```cpp
#include "StylusInput/IStylusInputInterface.h"
#include "StylusInput/StylusInputModule.h"

// 假设我们有一个 SWindow
TSharedRef<SWindow> MyWindow = SNew(SWindow) /* ... */;
// ... 将窗口加入 Slate 应用 ...

// 获取平台特定的 StylusInput 接口
IStylusInputInterface* StylusInterface = FStylusInputModule::Get().GetPlatformInterface();
if (StylusInterface)
{
    // 为这个窗口创建输入实例
    IStylusInputInstance* Instance = StylusInterface->CreateInstance(MyWindow->GetNativeWindow().ToSharedRef().Get());
    if (Instance)
    {
        // 添加事件处理器
        Instance->AddEventHandler(MyHandler.Get(), EEventHandlerThread::GameThread);

        // 获取该窗口相关的所有数位板上下文（硬件设备）
        TSharedPtr<IStylusInputTabletContext> Context = Instance->GetTabletContext(/* TabletContextID */);
        if (Context.IsValid())
        {
            // 可以查询设备名称、支持的属性（压力、倾斜）等
            UE_LOG(LogTemp, Log, TEXT("Tablet: %s"), *Context->GetName());
        }
    }
}

// 当窗口关闭时，记得释放实例
if (StylusInterface && Instance)
{
    StylusInterface->ReleaseInstance(Instance);
}
```

## Demo 示例

以下是一个最小的编辑器自定义面板示例，它监听并显示数位板输入数据。

### StylusInputDemoPanel.h
```cpp
#pragma once
#include "Widgets/SCompoundWidget.h"
#include "StylusInput/IStylusInputEventHandler.h"

class SStylusInputDemoPanel : public SCompoundWidget, public UE::StylusInput::IStylusInputEventHandler
{
public:
    SLATE_BEGIN_ARGS(SStylusInputDemoPanel) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);
    virtual ~SStylusInputDemoPanel();

    // IStylusInputEventHandler Interface
    virtual void OnPacket(const UE::StylusInput::IStylusInputInstance& Instance, const UE::StylusInput::IStylusInputPacket& Packet) override;
    virtual void OnTabletContextAdded(const UE::StylusInput::IStylusInputInstance& Instance, const UE::StylusInput::IStylusInputTabletContext& Context) override;
    virtual void OnTabletContextRemoved(const UE::StylusInput::IStylusInputInstance& Instance, const UE::StylusInput::IStylusInputTabletContext& Context) override;
    virtual void OnStylusButtonDown(const UE::StylusInput::IStylusInputInstance& Instance, const UE::StylusInput::IStylusInputStylusButton& Button) override;
    virtual void OnStylusButtonUp(const UE::StylusInput::IStylusInputInstance& Instance, const UE::StylusInput::IStylusInputStylusButton& Button) override;
    // ... 其他必要虚函数的默认实现 ...

private:
    TSharedPtr<STextBlock> InfoText;
    UE::StylusInput::IStylusInputInstance* StylusInstance = nullptr;
};
```

### StylusInputDemoPanel.cpp
```cpp
#include "StylusInputDemoPanel.h"
#include "StylusInput/StylusInputModule.h"
#include "Widgets/Text/STextBlock.h"

void SStylusInputDemoPanel::Construct(const FArguments& InArgs)
{
    ChildSlot
    [
        SAssignNew(InfoText, STextBlock)
        .Text(FText::FromString(TEXT("Connect a pressure-sensitive tablet...")))
    ];

    // 尝试获取当前平台的数位板输入接口
    if (IStylusInputInterface* Interface = FStylusInputModule::Get().GetPlatformInterface())
    {
        // 注意：实际中需要获取一个有效的窗口句柄来创建实例。这里假设我们能从 Slate 获取。
        // StylusInstance = Interface->CreateInstance(/* Window */);
        if (StylusInstance)
        {
            StylusInstance->AddEventHandler(this, EEventHandlerThread::GameThread);
        }
    }
}

SStylusInputDemoPanel::~SStylusInputDemoPanel()
{
    if (StylusInstance)
    {
        StylusInstance->RemoveEventHandler(this);
        // 注意：通常实例的生命周期由创建它的接口管理，这里简化了释放逻辑。
    }
}

void SStylusInputDemoPanel::OnPacket(const UE::StylusInput::IStylusInputInstance& Instance, const UE::StylusInput::IStylusInputPacket& Packet)
{
    if (InfoText.IsValid())
    {
        const FVector2D Pos = Packet.GetPosition();
        const float Pressure = Packet.GetNormalPressure();
        const FText Info = FText::Format(
            NSLOCTEXT("StylusDemo", "PacketInfo", "X: {0}, Y: {1}, Pressure: {2}"),
            FText::AsNumber(Pos.X), FText::AsNumber(Pos.Y), FText::AsNumber(Pressure));
        InfoText->SetText(Info);
    }
}

void SStylusInputDemoPanel::OnTabletContextAdded(const UE::StylusInput::IStylusInputInstance& Instance, const UE::StylusInput::IStylusInputTabletContext& Context)
{
    UE_LOG(LogTemp, Log, TEXT("Tablet Added: %s (ID: %u)"), *Context.GetName(), Context.GetID());
}

void SStylusInputDemoPanel::OnTabletContextRemoved(const UE::StylusInput::IStylusInputInstance& Instance, const UE::StylusInput::IStylusInputTabletContext& Context)
{
    UE_LOG(LogTemp, Log, TEXT("Tablet Removed: %s (ID: %u)"), *Context.GetName(), Context.GetID());
}

void SStylusInputDemoPanel::OnStylusButtonDown(const UE::StylusInput::IStylusInputInstance& Instance, const UE::StylusInput::IStylusInputStylusButton& Button)
{
    UE_LOG(LogTemp, Log, TEXT("Button Down: %s"), *Button.GetName());
}

void SStylusInputDemoPanel::OnStylusButtonUp(const UE::StylusInput::IStylusInputInstance& Instance, const UE::StylusInput::IStylusInputStylusButton& Button)
{
    UE_LOG(LogTemp, Log, TEXT("Button Up: %s"), *Button.GetName());
}
```

## 模块依赖

根据构建文件，该插件的模块主要依赖于以下非标准核心模块：

| 模块 | 用途 |
|---|---|
| `Slate` | 用于创建调试小部件（`StylusInputDebugWidget`）和处理窗口句柄。 |
| `ApplicationCore` | 访问平台窗口（`SWindow`）和应用程序层。 |
| `InputCore` | 提供基础输入类型定义。 |
| `Core` | 提供基础工具类、平台抽象和内存管理。 |
| `CoreUObject` | 对象系统和反射支持。 |
| `Engine` | 编辑器和引擎核心功能。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-19 | `9693e160` | StylusInput: Fix NSEvent up/down | 修复 macOS 上 NSEvent 笔尖抬起/按下状态判断错误的问题。 |
| 2026-05-19 | `36a0dc9c` | StylusInput: Fix issue with multiple Wintab instances | 修复 Windows 上同时使用多个 Wintab 设备实例时出现的问题。 |
| 2026-05-13 | `041d4d75` | StylusInput: Fix coordinates issue with Wintab when main screen is not on left/top | 修复当主显示器不在左上角时，Wintab 驱动下坐标转换错误的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将插件中的 `UE_LOG` 调用迁移到更现代的 `UE_LOGF`。 |
| 2026-01-28 | `5f766aee` | Fixed modules that does not support portable toolchain | 修复了不支持可移植工具链的模块，确保跨平台编译兼容性。 |

### 维护评价

**活跃维护**。尽管该插件已有7年历史，且标记为实验性（`IsBetaVersion=true`），但近期（2026年5月）仍有活跃的提交，主要针对 macOS 和 Windows 平台进行了重要的 bug 修复，解决了输入状态、多设备支持和多显示器坐标转换等关键问题。这表明 Epic 仍在维护此插件以支持编辑器核心功能。

**推荐使用**：如果你正在开发依赖数位板高级输入（压力、倾斜）的编辑器工具，这个插件是**唯一官方支持**的解决方案。需要注意其**实验性**标签，意味着 API 可能还不完全稳定。由于它**默认禁用**，你需要在 `.uproject` 文件中手动启用 `StylusInput` 插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/StylusInput)
- 官方文档：无（.uplugin 中 DocsURL 为空）