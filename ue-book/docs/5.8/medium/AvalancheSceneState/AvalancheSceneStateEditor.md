# Motion Design Scene State Integration

> （无描述）

| 属性 | 值 |
|---|---|
| 中文名 | 运动设计场景状态集成 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `AvalancheSceneState` (Runtime), `AvalancheSceneStateBlueprint` (UncookedOnly), `AvalancheSceneStateEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/AvalancheSceneState) | |

## 用途

该插件是 **Avalanche（运动设计/Motion Design）** 系统与 **Scene State（场景状态）** 系统之间的桥梁。它解决的核心问题是：**如何在运动设计工作流中，利用场景状态系统来定义、管理和执行复杂的场景状态序列与任务。**

简单来说，它允许用户：
1.  在 Avalanche 编辑器中直接创建和管理 `AAvaSceneStateActor` 和 `USceneStateBlueprint`。
2.  将远程控制（Remote Control）映射到场景状态系统的输入值，从而实现外部设备或界面驱动场景状态的变化。
3.  在场景状态任务中集成运动设计特有的逻辑，例如控制广播图形、虚拟场景元素的切换等。

它通过一个专门的 `AvalancheSceneStateEditor` 模块，将场景状态系统的管理界面无缝集成到了运动设计（Avalanche）的编辑器扩展中，使得虚拟制作人员可以在一个统一的工作流中完成从图形设计到场景状态编程的全过程。

## 使用场景

-   **你在使用 UE5 的运动设计（Motion Design/Avalanche）功能制作广播图形、虚拟演播室或动态视觉元素** → 你可以用这个插件来为这些图形定义不同的“状态”（例如：开场、主播采访、全屏图表），并通过场景状态蓝图来编排它们的出现、变化和消失序列。
-   **你需要通过外部设备（如 Stream Deck、MIDI 控制器）或自定义 UI 来实时控制虚拟场景中的元素** → 你可以将远程控制映射到此插件提供的任务上，从而用物理按钮或滑块来触发预设的场景状态过渡。
-   **你希望将复杂的、分步骤的场景变化逻辑（例如：灯光调整、镜头切换、动画播放、材质参数变化）打包成可复用的“任务”** → 你可以利用场景状态蓝图来编写这些任务，并在此插件的集成编辑器中管理它们。

## 蓝图用法

该插件的核心功能主要集成在编辑器中，但运行时蓝图节点围绕着场景状态任务和远程控制映射展开。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| （推测）与 `FAvaSceneStateRCTaskInstance` 相关的节点 | 用于定义和执行与远程控制（RC）值同步的场景状态任务实例。可能涉及获取/设置控制器映射和属性包值。 | `UAvaSceneStateRCTask` (推测) |

*注意：具体蓝图节点需查阅 `AvalancheSceneStateBlueprint` 模块中的 `UCLASS` 和 `UFUNCTION` 定义。由于提供的源码分析主要聚焦于编辑器模块的细节定制，运行时蓝图节点的精确列表未能直接展示。*

### 使用示例（蓝图描述）

1.  在 **Avalanche 编辑器** 的工具栏中，找到由 `FAvaSceneStateExtension` 添加的“场景状态”选项。
2.  选择“创建场景状态 Actor”或“新建场景状态蓝图”，这将调用 `FindOrSpawnSceneStateActor` 和 `CreateSceneStateBlueprint` 逻辑。
3.  打开创建的 `USceneStateBlueprint`，在其中定义状态（State）和任务（Task）。
4.  使用 `FAvaSceneStateRCTaskDetails` 定制的细节面板，为任务添加 **控制器映射（Controller Mapping）**。这里你可以将一个远程控制预设的控制器（如一个浮点数）关联到任务的输入。
5.  `FAvaSceneStateRCValuesDetails` 会确保控制器映射数组与值属性包（Property Bag）保持同步，你可以在细节面板中直接编辑这些值。

## C++ 用法

插件的公共 API 主要体现在编辑器扩展和细节定制上。

### 头文件引入

```cpp
// 用于扩展运动设计编辑器
#include "AvaSceneStateExtension.h"

// 用于自定义细节视图
#include "AvaSceneStateRCTaskDetails.h"
#include "AvaSceneStateRCValuesDetails.h"
```

### 基本用法：扩展工具栏菜单

`FAvaSceneStateExtension` 展示了如何为运动设计编辑器添加自定义工具栏菜单。

```cpp
// 来源：Private/AvaSceneStateExtension.h
// 在你的编辑器模块 StartupModule 中注册扩展
void FYourEditorModule::StartupModule()
{
    // 假设您有获取 AvaEditor 的方法
    if (FAvaEditor* AvaEditor = GetAvaEditor())
    {
        // 创建并注册场景状态扩展
        TSharedRef<FAvaSceneStateExtension> Extension = MakeShared<FAvaSceneStateExtension>();
        AvaEditor->AddExtension(Extension);
    }
}

// 在 FAvaSceneStateExtension 的实现中（如 .cpp 文件）
void FAvaSceneStateExtension::ExtendToolbarMenu(UToolMenu& InMenu)
{
    // 添加一个包含“场景状态”选项的菜单段
    FToolMenuSection& Section = InMenu.AddSection("SceneStateSection", LOCTEXT("SceneStateSection", "Scene State"));
    Section.AddSubMenu(
        "SceneStateSubMenu",
        LOCTEXT("SceneStateSubMenu", "Scene State"),
        LOCTEXT("SceneStateSubMenuToolTip", "Options for Scene State"),
        FNewToolMenuDelegate::CreateSP(this, &FAvaSceneStateExtension::GenerateSceneStateOptions)
    );
}

void FAvaSceneStateExtension::GenerateSceneStateOptions(UToolMenu* InMenu)
{
    FToolMenuSection& Section = InMenu->AddSection("SceneStateOptions");
    // 添加创建 Actor、打开蓝图、删除 Actor 等菜单项
    Section.AddMenuEntry(
        "CreateSceneStateActor",
        LOCTEXT("CreateSceneStateActor", "Create Scene State Actor"),
        LOCTEXT("CreateSceneStateActorToolTip", "Spawns a Scene State Actor in the level"),
        FSlateIcon(),
        FUIAction(FExecuteAction::CreateSP(this, &FAvaSceneStateExtension::FindOrSpawnSceneStateActor))
    );
    // ... 其他菜单项 ...
}
```

### 进阶用法：自定义细节面板

插件使用 `IPropertyTypeCustomization` 和 `IDetailCustomNodeBuilder` 来深度自定义场景状态任务在细节面板中的显示。

```cpp
// 来源：Private/DetailsView/AvaSceneStateRCTaskDetails.h
// 注册细节自定义（通常在模块 StartupModule 中）
void FAvaSceneStateEditorModule::RegisterCustomizations()
{
    FPropertyEditorModule& PropertyModule = FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");
    // 假设 FAvaSceneStateRCTaskInstance 是你要定制的 UStruct
    PropertyModule.RegisterCustomPropertyTypeLayout(
        FAvaSceneStateRCTaskInstance::StaticStruct()->GetFName(),
        FOnGetPropertyTypeCustomizationInstance::CreateStatic(&FAvaSceneStateRCTaskDetails::MakeInstance)
    );
    CustomizedTypes.Add(FAvaSceneStateRCTaskInstance::StaticStruct()->GetFName());
}

// FAvaSceneStateRCTaskDetails 的 CustomizeChildren 可能会创建 FAvaSceneStateRCValuesDetails 来构建控制器映射和值的复杂UI
void FAvaSceneStateRCTaskDetails::CustomizeChildren(TSharedRef<IPropertyHandle> InPropertyHandle, IDetailChildrenBuilder& InChildBuilder, ...)
{
    // ... 获取对映射和值属性的句柄 ...
    TSharedRef<FAvaSceneStateRCValuesDetails> ValuesBuilder = MakeShared<FAvaSceneStateRCValuesDetails>(StructHandle, ValuesId, PropUtils);
    ValuesBuilder->Initialize();
    InChildBuilder.AddCustomBuilder(ValuesBuilder);
}
```

## Demo 示例

一个最小化的示例，展示如何创建一个编辑器模块，该模块在启动时添加一个场景状态扩展，并在关闭时清理。

**MySceneStateExtensionModule.h**
```cpp
#pragma once
#include "Modules/ModuleManager.h"

class FMySceneStateExtensionModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    TSharedPtr<class FAvaSceneStateExtension> SceneStateExtension;
};
```

**MySceneStateExtensionModule.cpp**
```cpp
#include "MySceneStateExtensionModule.h"
#include "AvaSceneStateExtension.h"
// 假设这是访问 Avalanche 编辑器的头文件
// #include "AvalancheEditorModule.h" 

#define LOCTEXT_NAMESPACE "FMySceneStateExtensionModule"

void FMySceneStateExtensionModule::StartupModule()
{
    // 获取 Avalanche 编辑器模块 (仅为示例，实际获取方式取决于 Avalanche 的API)
    // FAvalancheEditorModule& AvaEditorModule = FModuleManager::Get().LoadModuleChecked<FAvalancheEditorModule>("AvalancheEditor");
    // FAvaEditor* AvaEditor = AvaEditorModule.GetEditor();
    
    // 创建并注册我们的场景状态扩展
    if (/* AvaEditor */ true) // 替换为实际检查
    {
        SceneStateExtension = MakeShared<FAvaSceneStateExtension>();
        // AvaEditor->AddExtension(SceneStateExtension.ToSharedRef());
    }
}

void FMySceneStateExtensionModule::ShutdownModule()
{
    // 清理扩展
    if (SceneStateExtension.IsValid())
    {
        // 调用扩展的清理方法，确保其从编辑器中移除
        SceneStateExtension->Cleanup();
        SceneStateExtension.Reset();
    }
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMySceneStateExtensionModule, MySceneStateExtensionModule)
```

## 模块依赖

使用该插件，你的模块需要依赖以下独特的模块（省略了 Core, Engine 等常见依赖）：

| 模块 | 用途 |
|---|---|
| `Avalanche` | 运动设计（Motion Design）编辑器和运行时核心功能 |
| `SceneState` | 场景状态系统的核心运行时和编辑器功能 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF，属于引擎级代码规范更新。 |
| 2026-02-22 | `977f0c20` | Motion Design Scene State: added an extra 'utility task' metadata + updating from deprecated api | 为场景状态任务添加了额外的“实用任务”元数据，并更新了已弃用的API调用。 |
| 2026-02-16 | `22f3bb17` | Motion Design Scene State: changed schema to only check for task type metadata in the task itself, n | 修改了场景状态图表的规则（Schema），现在只检查任务自身的类型元数据，简化了逻辑。 |
| 2026-02-15 | `5c9f991d` | Motion Design Scene State: made some schema functions editor-only, and added metadata to tasks to ea | 将部分图表函数改为仅编辑器可用，并为任务添加元数据以实现更便捷的查找和筛选。 |
| 2026-02-03 | `d2e06058` | Motion Design Scene State: added schema to set the rules of which tasks are allowed. | 添加了场景状态图表（Schema），用于定义哪些类型的任务在场景状态蓝图中是被允许的。 |

### 维护评价

该插件**正处于活跃开发阶段**。
-   **创建时间**：约 1 年前（2025年8月），是一个相对较新的插件。
-   **最近更新频率**：近期（2026年2-4月）有多次功能性更新，主要集中在场景状态任务的元数据管理、API更新和图表规则优化上，表明开发者正在完善其核心功能。
-   **实验性**：`.uplugin` 中 `IsBetaVersion=true`，且 `Installed=false`（默认未启用），确认其仍处于 **Beta 测试阶段**。
-   **推荐度**：**适合在实验性或原型项目中尝试使用**。由于它是 Beta 版本，API 和功能在未来版本中可能会有较大变动。对于生产环境，建议密切关注其版本更新和稳定化进展。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/AvalancheSceneState)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/AvalancheSceneState/Tests)（如果存在）