# DMX Protocol

> DMX Protocols implementation（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | DMX协议 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `DMXProtocol` (Runtime), `DMXProtocolArtNet` (Runtime), `DMXProtocolSACN` (Runtime), `DMXProtocolEditor` (Editor), `DMXProtocolBlueprintGraph` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXProtocol) | |

## 用途

这个插件提供了在 UE5 虚拟制作环境中与 DMX 设备进行通信的基础框架。它不仅定义了用于数据收发的核心协议接口，还具体实现了 ArtNet 和 sACN 这两种在影视灯光和特效控制领域广泛使用的行业标准协议。该插件的核心价值在于为 UE5 提供了一套标准化、可扩展的 DMX 通信层，使得开发者能够将物理世界的灯光、特效控制器与 UE5 的数字场景无缝连接，是构建虚拟制片（Virtual Production）、扩展现实（XR）和实时灯光控制流程的关键基础设施。

## 使用场景

- **虚拟制片（Virtual Production）**：在 LED 墙或绿幕前拍摄时，使用实体 DMX 控制器（如 GrandMA2、ETC）实时调整虚拟场景中的灯光颜色、强度和效果，确保物理灯光与数字背景匹配。
- **XR 拍摄环境**：在混合现实摄影棚中，通过 DMX 信号控制安装在 XR 舞台上的实际灯光设备，使其与 UE5 场景中的虚拟光源同步。
- **实时灯光秀预演**：在 UE5 中为音乐会、戏剧或活动设计复杂的灯光序列和 cue，然后通过 DMX 输出到真实的灯光控台或设备进行排练和最终执行。
- **交互式装置艺术**：创建由 UE5 驱动的交互艺术装置，通过 DMX 协议控制数百个 LED 灯泡、激光器或马达。

## 蓝图用法

本插件的 DMXProtocolEditor 模块主要提供编辑器侧的细节自定义（Details Customization）UI 控件，以便在编辑器属性面板中更友好地配置 DMX 输入输出端口。这些控件通常不直接暴露为蓝图节点，而是通过属性自定义框架集成。

### 核心控件（编辑器用）

以下 Slate 控件用于构建 DMX 端口配置的用户界面，它们主要被 C++ 的 `IPropertyTypeCustomization` 类内部使用。

| 控件 | 说明 | 所在文件 |
|---|---|---|
| `SDMXPortSelector` | 一个下拉框，允许从所有已配置的 DMX 输入/输出端口中进行选择。 | `Public/Widgets/SDMXPortSelector.h` |
| `SDMXProtocolNameComboBox` | 用于选择 DMX 协议（如 ArtNet, sACN）的下拉框。 | `Private/DetailsCustomizations/Widgets/SDMXProtocolNameComboBox.h` |
| `SDMXCommunicationTypeComboBox` | 用于选择通信类型（如 Broadcast, Multicast）的下拉框。 | `Private/DetailsCustomizations/Widgets/SDMXCommunicationTypeComboBox.h` |
| `SDMXIPAddressEditWidget` | 用于输入和选择 IP 地址的控件，可列出本机网络适配器地址。 | `Private/DetailsCustomizations/Widgets/SDMXIPAddressEditWidget.h` |
| `SDMXDelayEditWidget` | 用于设置发送延迟的控件，支持以秒或基于特定帧率的帧数进行设置。 | `Private/DetailsCustomizations/Widgets/SDMXDelayEditWidget.h` |

**说明**：这些控件通常与 `FDMXInputPortConfigCustomization` 和 `FDMXOutputPortConfigCustomization` 等自定义类一起工作，自动出现在项目设置或 Actor 细节面板中的 DMX 端口配置属性上，无需蓝图直接调用。

## C++ 用法

本插件的核心运行时 API（如 `DMXProtocol`、`DMXProtocolArtNet`、`DMXProtocolSACN` 模块）负责底层协议实现，其使用涉及创建和管理端口、注册子系统等，通常由 DMX 插件的上层模块（如 DMXEngine）封装。Editor 模块的用法主要体现在自定义细节面板。

### 头文件引入

要使用 Editor 模块的自定义功能，需包含：
```cpp
#include "DMXProtocolEditorModule.h"
```

### 基本用法（编辑器属性自定义）

要为你的自定义结构体（如 DMX 端口配置）注册属性自定义，可以在 Editor 模块的 `StartupModule` 中完成。以下是一个注册 `FDMXOutputPortConfig` 属性自定义的示例思路：

```cpp
// 在 DMXProtocolEditor 模块的 StartupModule 中
#include "PropertyEditorModule.h"
#include "DMXOutputPortConfigCustomization.h"

void FDMXProtocolEditorModule::StartupModule()
{
    // ... 其他初始化
    RegisterDetailsCustomizations();
}

void FDMXProtocolEditorModule::RegisterDetailsCustomizations()
{
    FPropertyEditorModule& PropertyModule = FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");

    // 为 FDMXOutputPortConfig 结构体注册自定义
    PropertyModule.RegisterCustomPropertyTypeLayout(
        FDMXOutputPortConfig::StaticStruct()->GetFName(),
        FOnGetPropertyTypeCustomizationInstance::CreateStatic(&FDMXOutputPortConfigCustomization::MakeInstance)
    );
}
```

**来源**：推断自 `Private/DetailsCustomizations/DMXOutputPortConfigCustomization.h` 和 `Public/DMXProtocolEditorModule.h` 的类结构。

### 进阶用法（创建自定义端口选择器）

如果你需要在自己的编辑器工具中嵌入一个 DMX 端口选择器（例如一个独立的窗口或自定义的资产编辑器），你可以直接实例化 `SDMXPortSelector` 控件。

```cpp
// 在你的 Slate 窗口或面板构造函数中
TSharedRef<SDMXPortSelector> PortSelector = SNew(SDMXPortSelector)
    .Mode(EDMXPortSelectorMode::SelectFromAvailableOutputs) // 只显示输出端口
    .InitialSelection(MySavedPortGuid) // 初始选择
    .OnPortSelected(FSimpleDelegate::CreateSP(this, &SMyPanel::HandlePortSelected));

// 添加到你的布局中
MyVerticalBox->AddSlot()
    .Padding(2.0f)
    [
        PortSelector
    ];
```

**来源**：`Public/Widgets/SDMXPortSelector.h` 中的 `SLATE_BEGIN_ARGS` 和公共方法。

## Demo 示例

本插件作为基础设施，没有包含独立的可运行 Demo 场景。一个完整的 DMX 使用示例通常需要结合 DMX 插件套件中的其他部分，如 DMXEngine 和 DMXFixture。一个最小化的集成示例结构如下：

**DMXPortManager.h (示例)**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "DMXProtocolEditorModule.h" // 引入编辑器模块头

class UMyDMXPortManager : public UObject
{
    GENERATED_BODY()

public:
    UMyDMXPortManager();
    ~UMyDMXPortManager();

    /** 初始化，注册自定义等 */
    void Initialize();
};
```

**DMXPortManager.cpp (示例)**
```cpp
#include "DMXPortManager.h"
#include "DMXOutputPortConfigCustomization.h"
#include "PropertyEditorModule.h"

UMyDMXPortManager::UMyDMXPortManager()
{
}

UMyDMXPortManager::~UMyDMXPortManager()
{
    // 反注册（通常在模块ShutdownModule中完成更合适）
}

void UMyDMXPortManager::Initialize()
{
    // 确保编辑器模块已加载
    FDMXProtocolEditorModule& DMXEditorModule = FModuleManager::LoadModuleChecked<FDMXProtocolEditorModule>("DMXProtocolEditor");

    // 在此可以调用 DMXEditorModule 中注册的自定义细节
    // 实际的注册/注销逻辑在模块的 Startup/Shutdown 中处理
    UE_LOG(LogTemp, Log, TEXT("MyDMXPortManager initialized. DMX Protocol Editor module is available."));
}
```

**说明**：此示例展示了如何在你的代码中依赖并加载 DMXProtocolEditor 模块。要真正发送和接收 DMX 数据，你需要使用 `DMXProtocol` 或 `DMXProtocolArtNet` 等运行时模块的 API，这通常涉及 `IDMXProtocol` 接口和端口管理器类。

## 模块依赖

使用本插件时，你的模块需要依赖的具体模块取决于功能需求：

| 模块 | 用途 |
|---|---|
| `DMXProtocolEditor` | 如果你需要在自己的编辑器扩展或属性自定义中使用 DMX 端口选择器等控件，则需要依赖此模块。 |
| `DMXProtocol` | 依赖核心 DMX 协议接口和类型定义。这是所有 DMX 功能的基石。 |
| `DMXProtocolArtNet` | 依赖 ArtNet 协议的具体实现，用于通过 ArtNet 网络发送/接收 DMX 数据。 |
| `DMXProtocolSACN` | 依赖 sACN (E1.31) 协议的具体实现，用于通过 sACN 网络发送/接收 DMX 数据。 |
| `DMXProtocolBlueprintGraph` | 如果你需要扩展或使用 DMX 相关的蓝图节点，则需要依赖此模块（类型为 UncookedOnly）。 |

**说明**：`DMXProtocol`、`DMXProtocolArtNet`、`DMXProtocolSACN` 是运行时核心，`DMXProtocolEditor` 仅在编辑器环境下使用。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧版 UE_LOG 日志宏迁移到新的 UE_LOGF 格式。 |
| 2026-04-08 | `86879cf0` | Fix unreachable code warnings | 修复了代码中不可达部分的编译器警告。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 在修复了错误的查找替换后，进行了第二次提交。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回滚了编号为 CL51314860 的变更。 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 将引擎初始化后的核心委托访问方式从静态成员改为通过 Get 函数获取，以修复可能的注册问题。 |

### 维护评价

- **创建时间**：2020年9月，已有约6年历史。
- **活跃程度**：**活跃维护中**。最近一次更新在2026年4月，且近期有连续的更新，内容以代码质量改进（修复警告）和框架适配（委托接口迁移）为主，表明该插件仍在随着引擎的发展而持续维护和更新。
- **稳定性**：作为 Epic Games 官方维护的虚拟制作核心组件之一，代码质量和稳定性有保障。从 commit 历史看，近期的改动多为修复和适配，未见重大功能重构或废弃标记。
- **推荐度**：**强烈推荐**。这是 UE5 虚拟制作工具链中经过长期验证的官方标准组件，如果你的项目涉及任何形式的实体灯光控制或 DMX 设备集成，应优先使用此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXProtocol)
- [官方文档]() （.uplugin 中未提供）
- [测试用例]() （提供的文件列表中未包含测试文件路径）