# Remote Control Protocol Widgets

> A Remote Control module that provides editor widgets for protocol bindings.

| 属性 | 值 |
|---|---|
| 中文名 | 远程控制协议小部件 |
| 分类 | Messaging |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器控件样式、视图模型、Slate控件） |
| 模块 | `RemoteControlProtocolWidgets` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-06-07 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/RemoteControl/Source/RemoteControlProtocolWidgets) | |

## 用途

`RemoteControlProtocolWidgets` 是 **Remote Control API** 插件的一个子模块，专门负责为协议绑定提供编辑器 UI 控件。其主要功能是：

1.  **可视化协议映射配置**：为用户暴露的 Actor 属性、函数等实体（Entity）提供一个可交互的界面，用于配置它们与外部协议（如 MIDI, OSC, DMX, DMX, sACN, Art-Net 等）的绑定关系。
2.  **管理输入/输出范围映射**：定义协议输入值（如 MIDI 0-127）如何映射到输出值（如灯光亮度 0.0-1.0，旋转角度 0-360）。用户可以通过 UI 添加、删除和编辑这些范围映射。
3.  **提供通道遮罩**：对于支持多通道（如颜色 RGBA、向量 XYZ）的属性，提供控件来选择哪些通道参与协议映射。
4.  **集成到编辑器面板**：这些控件被集成到 Remote Control Panel 中，为艺术家和技术美术人员提供了一个直观的、所见即所得的界面来设置复杂的虚拟制片控制界面。

简而言之，这个模块是 Remote Control 系统在编辑器中的“控制台”和“设置面板”，解决了如何让用户通过图形界面配置引擎与外部设备交互的核心问题。

## 使用场景

-   **虚拟制片**：在虚拟制片环境中，通过触摸屏、MIDI 控制器或自定义应用程序远程控制场景中的灯光参数、摄像机设置、材质属性等。
-   **实时演出控制**：在音乐演出或艺术装置中，使用 OSC 协议实时控制引擎中的粒子效果、音效或视觉元素。
-   **参数快速调试**：在编辑器中，通过协议输入模拟来自外部设备的信号，快速测试和调试蓝图逻辑或材质参数，而无需连接物理设备。
-   **构建自定义控制界面**：利用 Remote Control 的 Web API 和这个模块提供的配置，构建基于浏览器的定制化控制面板。

## 蓝图用法

本模块主要提供 C++ 和 Slate 控件接口，其功能通常通过 Remote Control Panel 面板间接使用，而不是直接暴露给蓝图。核心的协议绑定和映射逻辑由 `FProtocolBindingViewModel` 和 `FProtocolRangeViewModel` 等视图模型类管理。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddProtocolBinding` | 为指定实体添加一个新的协议绑定 | `IRemoteControlProtocolWidgetsModule` |
| `GenerateDetailsForEntity` | 为给定的 Preset 和 FieldId 创建一个详细信息控件 | `IRemoteControlProtocolWidgetsModule` |
| `GetProtocolBindingList` | 获取当前协议绑定列表的公共接口 | `IRemoteControlProtocolWidgetsModule` |
| `OnProtocolBindingAddedOrRemoved` | 当协议绑定被添加或移除时触发的委托 | `IRemoteControlProtocolWidgetsModule` |

**使用示例（蓝图描述）**

蓝图中通常不直接操作这些控件节点。用户交互流程如下：
1.  在 **Remote Control Panel** 面板中，选中一个已暴露的属性或函数（对应一个 `FProtocolEntityViewModel`）。
2.  点击 **“+”** 按钮，通过 `IRemoteControlProtocolWidgetsModule::AddProtocolBinding` 选择一种协议类型。
3.  面板中会生成对应的 `SRCProtocolBinding` 控件，其中包含 `SRCProtocolRangeList` 和 `SRCProtocolRange` 控件。
4.  用户通过 `SRCProtocolRange` 中的属性视图 (`SPropertyView`) 设置输入/输出值，通过 `SRCProtocolMaskTriplet` 设置通道遮罩。
5.  所有操作通过视图模型 (`FProtocolBindingViewModel` -> `FProtocolRangeViewModel`) 反映到底层的 `URemoteControlPreset` 数据资产中。

## C++ 用法

### 头文件引入

```cpp
#include "RemoteControlProtocolWidgetsModule.h"
#include "IRemoteControlProtocolWidgetsModule.h"
```

### 基本用法

获取模块实例并为其绑定一个新协议。
（示例逻辑，实际使用需结合 Remote Control 框架）

```cpp
// 引入模块接口
#include "IRemoteControlProtocolWidgetsModule.h"

// 假设你已经有一个有效的 URemoteControlPreset 和已暴露的实体 ID
URemoteControlPreset* MyPreset = ...;
FGuid EntityId = ...;

// 获取 Remote Control Protocol Widgets 模块
IRemoteControlProtocolWidgetsModule& ProtocolWidgetsModule = IRemoteControlProtocolWidgetsModule::Get();

// 为实体添加一个 MIDI 协议的绑定
FName ProtocolName = TEXT("MIDI"); // 协议名称需与已注册的协议模块匹配
ProtocolWidgetsModule.AddProtocolBinding(ProtocolName);

// 或者，为该实体生成一个可嵌入的控件
EExposedFieldType FieldType = EExposedFieldType::Property; // 假设是属性
TSharedRef<SWidget> DetailsWidget = ProtocolWidgetsModule.GenerateDetailsForEntity(MyPreset, EntityId, FieldType);
// 现在可以将 DetailsWidget 添加到你的自定义 Slate 面板中
```

### 进阶用法

直接使用视图模型来管理和响应协议绑定状态。
（概念示例，需依赖 `RemoteControl` 和 `RemoteControlProtocol` 模块）

```cpp
#include "ViewModels/ProtocolEntityViewModel.h"
#include "ViewModels/ProtocolBindingViewModel.h"

// 创建或获取实体的视图模型
TSharedRef<FProtocolEntityViewModel> EntityVM = FProtocolEntityViewModel::Create(MyPreset, EntityId);

// 监听绑定添加事件
EntityVM->OnBindingAdded().AddLambda([](TSharedRef<FProtocolBindingViewModel> BindingVM)
{
    UE_LOG(LogTemp, Log, TEXT("Added binding for protocol: %s"), *BindingVM->GetProtocolName().ToString());
    // 可以进一步获取范围映射视图模型
    const auto& Ranges = BindingVM->GetRanges();
    for (const auto& RangeVM : Ranges)
    {
        // 处理每个范围映射
    }
});

// 添加一个绑定
TSharedPtr<FProtocolBindingViewModel> NewBindingVM = EntityVM->AddBinding(FName(TEXT("OSC")));
if (NewBindingVM.IsValid())
{
    // 为这个绑定添加默认的范围映射
    NewBindingVM->AddDefaultRangeMappings();
}
```

## Demo 示例

以下示例展示如何在自定义的 Slate 控件中集成协议绑定列表。
```cpp
// MyCustomProtocolPanel.h
#pragma once
#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"
#include "IRCProtocolBindingList.h"

class URemoteControlPreset;

class SMyCustomProtocolPanel : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyCustomProtocolPanel) {}
    SLATE_ARGUMENT(URemoteControlPreset*, Preset)
    SLATE_ARGUMENT(FGuid, EntityId)
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);

private:
    /** 用于承载协议绑定列表的控件 */
    TSharedPtr<IRCProtocolBindingList> ProtocolBindingList;
};
```

```cpp
// MyCustomProtocolPanel.cpp
#include "MyCustomProtocolPanel.h"
#include "IRemoteControlProtocolWidgetsModule.h"
#include "RemoteControlPreset.h"

void SMyCustomProtocolPanel::Construct(const FArguments& InArgs)
{
    // 通过模块接口获取协议绑定列表控件
    IRemoteControlProtocolWidgetsModule& Module = IRemoteControlProtocolWidgetsModule::Get();
    // 重置（或初始化）列表，通常与特定 Preset 关联
    Module.ResetProtocolBindingList();
    ProtocolBindingList = Module.GetProtocolBindingList();

    ChildSlot
    [
        SNew(SVerticalBox)
        + SVerticalBox::Slot()
        .AutoHeight()
        [
            SNew(STextBlock)
            .Text(FText::FromString(TEXT("Protocol Bindings")))
        ]
        + SVerticalBox::Slot()
        .FillHeight(1.0f)
        [
            // 这里通常不会直接嵌入 IRCProtocolBindingList，
            // 因为它代表一个接口。实际使用中，RemoteControlPanel
            // 会内部管理这个列表控件。此示例仅展示获取过程。
            SNew(STextBlock)
            .Text(FText::FromString(TEXT("Protocol binding list would be displayed here.")))
        ]
    ];
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RemoteControl` | 核心远程控制逻辑，提供 Preset、Field 等基础类型。 |
| `RemoteControlCommon` | 远程控制公共类型和工具。 |
| `RemoteControlProtocol` | 协议接口定义和基础实现（如 MIDI, OSC）。 |
| `RemoteControlLogic` | 远程控制逻辑，处理属性访问和函数调用。 |
| `EditorFramework` | 编辑器框架支持。 |
| `PropertyEditor` | 属性编辑器和细节面板自定义。 |

**说明**：此模块高度依赖 `RemoteControl` 插件家族中的其他运行时模块，用于获取数据模型和协议逻辑。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `1716f2e0` | Remote Control: added missing ApplyColorWheelDelta and ApplyColorGradingWheelDelta to the built-in a | 为内置的远程控制功能补充了颜色轮盘增量应用功能。 |
| 2026-05-20 | `d724bb52` | Remote Control: fixed uninitialized ObjectClass in FRCRemoteFunctionCallParams, sometimes causing a | 修复了远程函数调用参数中对象类未初始化可能导致的问题。 |
| 2026-05-20 | `12d5ae7f` | Remote Control: added allow list for remote function calls, and specifying built-in functions to all | 新增了远程函数调用的白名单功能，并允许指定哪些内置函数可用于所有对象。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量截断为浮点数可能产生的警告代码。 |

### 维护评价

**活跃维护**。

-   **创建时间**：模块创建于2019年，是Remote Control系统的早期组件。
-   **近期更新**：在2026年5月有多次实质性的功能增强和Bug修复提交，表明该模块仍在持续开发和改进中。
-   **功能完整性**：作为Remote Control UI的核心，其功能随着协议支持的扩展而不断完善。
-   **建议**：该模块是Remote Control插件正常工作的重要组成部分，对于需要在编辑器中配置协议控制的项目，推荐启用并使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/RemoteControl/Source/RemoteControlProtocolWidgets)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/RemoteControl/Tests) （位于插件根目录的 Tests 文件夹内）