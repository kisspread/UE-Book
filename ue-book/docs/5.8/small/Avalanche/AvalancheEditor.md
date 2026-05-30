# Motion Design

> Compositing, designer and broadcasting tool.

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器工具、资产、详细设置） |
| 模块 | `Avalanche` (Runtime), `AvalancheAttribute` (Runtime), `AvalancheAttributeEditor` (Runtime), `AvalancheCamera` (Runtime), `AvalancheComponentVisualizers` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheEditorCore` (Runtime), `AvalancheEffectors` (Runtime), `AvalancheEffectorsEditor` (Runtime), `AvalancheFunctionalTest` (Runtime), `AvalancheInteractiveTools` (Runtime), `AvalancheInteractiveToolsRuntime` (Runtime), `AvalancheLevelViewport` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheMRQEditor` (Runtime), `AvalancheMask` (Runtime), `AvalancheMaskEditor` (Runtime), `AvalancheMaterial` (Runtime), `AvalancheMedia` (Runtime), `AvalancheMediaEditor` (Runtime), `AvalancheModifiers` (Runtime), `AvalancheModifiersEditor` (Runtime), `AvalancheOutliner` (Runtime), `AvalanchePropertyAnimator` (Runtime), `AvalanchePropertyAnimatorEditor` (Runtime), `AvalancheRemoteControl` (Runtime), `AvalancheRemoteControlEditor` (Runtime), `AvalancheSVGEditor` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheSceneRigEditor` (Runtime), `AvalancheSceneTree` (Runtime), `AvalancheSequence` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheShapes` (Runtime), `AvalancheShapesEditor` (Runtime), `AvalancheTag` (Runtime), `AvalancheTagEditor` (Runtime), `AvalancheText` (Runtime), `AvalancheTextEditor` (Runtime), `AvalancheTransition` (Runtime), `AvalancheTransitionEditor` (Runtime), `AvalancheViewport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Motion Design 插件是一套面向虚拟制片和实时图形设计的综合性工具套件。它不仅仅是一个简单的组件，而是一个完整的编辑器扩展，旨在将 Unreal Engine 转变为一个专业的动态图形、合成和广播内容创作平台。该插件解决的核心问题是为设计师和广播工程师提供一个高度集成的工作流，用于实时创建、编辑和播出复杂的动态视觉内容（如节目包装、虚拟布景、实时字幕、动态图表等），所有操作都在 UE 的 3D 环境中完成。

## 使用场景

- 你在为电视台或直播活动设计实时播出的虚拟布景、节目开场、片尾和过场动画。
- 你需要创建复杂的参数化动态图形（如克隆体、特效器、形状动画），并实时调整其属性。
- 你需要一个集中式的场景管理和大纲视图来处理大量动态设计元素，而非传统的 Actor 列表。
- 你需要将设计资产与远程控制、序列器、材质设计器等工具无缝集成，实现高效的内容管线。
- 你需要利用 Movie Render Queue (MRQ) 渲染高质量的最终输出，同时保留实时预览能力。

## 蓝图用法

该插件主要通过其提供的编辑器界面和命令来操作，但其核心子模块也暴露了部分蓝图接口。以下是基于源码分析的主要功能点：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get` | 获取编辑器设置的单例 | `UAvaEditorSettings` |
| `OpenEditorSettingsWindow` | 打开 Motion Design 编辑器设置窗口 | `UAvaEditorSettings` |
| `SetPlanePivot` | 根据 UV 坐标设置选择的平面枢轴点 | `FAvaSelectionProviderExtension` |
| `SetDepthPivot` | 设置选择的深度枢轴点 | `FAvaSelectionProviderExtension` |

### 使用示例（蓝图描述）

1.  **获取和修改编辑器设置**：通过 `UAvaEditorSettings::Get()` 节点获取设置单例，然后可以读取或设置如 `CameraDistance`、`bAutoActivateMotionDesignViewport` 等属性来定制工作流行为。
2.  **程序化控制枢轴点**：使用 `FAvaSelectionProviderExtension` 中的 `SetPlanePivot` 或 `SetDepthPivot` 节点，传入一个在 -1 到 1 范围内的 `FVector2D` 值，可以精确控制选中对象组的枢轴点位置，这对于动画和布局至关重要。

## C++ 用法

Motion Design 插件的功能主要通过其庞大的 C++ 模块体系实现。`AvalancheEditor` 模块是核心，包含了编辑器的主模块和各种功能扩展。

### 头文件引入

```cpp
// 引入编辑器主模块头文件
#include "AvaEditorModule.h"

// 引入编辑器设置
#include "AvaEditorSettings.h"

// 引入编辑器命令
#include "AvaEditorCommands.h"
```

### 基本用法

以下示例展示了如何在 C++ 中注册编辑器命令和响应用户操作。此代码模式常用于扩展编辑器的功能菜单和快捷键。

**示例：注册和使用编辑器命令**
```cpp
// 文件路径: Source/AvalancheEditor/Private/AvaEditorCommands.h (概念示例)

// 1. 命令类定义 (通常已在插件内实现)
class FAvaEditorCommands : public TCommands<FAvaEditorCommands>
{
public:
    FAvaEditorCommands()
        : TCommands<FAvaEditorCommands>(
            TEXT("AvaEditor"),
            FText::FromString(TEXT("Motion Design Editor")),
            NAME_None,
            FAppStyle::GetAppStyleSetName())
    {}

    // 注册所有命令
    virtual void RegisterCommands() override
    {
        UI_COMMAND(SwitchViewports, "Switch Viewports", "Switches between 2D and 3D viewport", EUserInterfaceActionType::Button, FInputChord());
        UI_COMMAND(GroupActors, "Group", "Groups the Selected Actors via a Null Actor", EUserInterfaceActionType::Button, FInputChord(EModifierKey::Control, EKeys::G));
        // ... 注册更多命令
    }

    // 命令声明
    TSharedPtr<FUICommandInfo> SwitchViewports;
    TSharedPtr<FUICommandInfo> GroupActors;
};

// 2. 在编辑器激活时绑定命令到操作 (通常在 FAvaEditorModule 或扩展中)
void FAvaEditorModule::StartupModule()
{
    // ... 其他初始化代码
    
    // 注册编辑器命令
    FAvaEditorCommands::Register();
    
    // 获取命令列表并绑定到具体的函数
    TSharedPtr<FUICommandList> CommandList = ...; // 从编辑器或视图获取
    CommandList->MapAction(
        FAvaEditorCommands::Get().SwitchViewports,
        FExecuteAction::CreateRaw(this, &FAvaLevelViewportExtension::OnSwitchViewports),
        FCanExecuteAction());
        
    CommandList->MapAction(
        FAvaEditorCommands::Get().GroupActors,
        FExecuteAction::CreateRaw(this, &FAvaOutlinerExtension::GroupSelection),
        FCanExecuteAction());
}

// 3. 实现命令绑定的具体函数
void FAvaLevelViewportExtension::OnSwitchViewports()
{
    // 实现切换 2D/3D 视口的逻辑
    SetMotionDesignViewportType();
    // ...
}
```

### 进阶用法

插件通过“扩展”(Extension)机制来组织功能。要创建一个自定义功能，通常需要继承自 `FAvaEditorExtension` 并重写相关方法。

**示例：创建一个简单的编辑器扩展**
```cpp
// 假设我们要添加一个自定义的工具栏按钮和功能
// 文件: MyCustomAvaExtension.h

#pragma once
#include "IAvaEditorExtension.h"

class FMyCustomAvaExtension : public FAvaEditorExtension
{
public:
    UE_AVA_INHERITS(FMyCustomAvaExtension, FAvaEditorExtension);

    // 当扩展被激活时调用
    virtual void Activate() override
    {
        // 在这里可以绑定命令、注册 UI 等
        Super::Activate();
    }

    // 当扩展被停用时调用，用于清理
    virtual void Deactivate() override
    {
        Super::Deactivate();
    }

    // 用于向编辑器工具栏添加菜单项
    virtual void ExtendToolbarMenu(UToolMenu& InMenu) override
    {
        // 向工具栏添加一个新部分
        FToolMenuSection& Section = InMenu.AddSection("MyCustomSection", FText::FromString("My Tools"));
        Section.AddMenuEntry(
            "MyCustomAction",
            FText::FromString("Do Something Custom"),
            FText::FromString("Performs a custom action"),
            FSlateIcon(),
            FUIAction(FExecuteAction::CreateRaw(this, &FMyCustomAvaExtension::OnMyCustomAction))
        );
    }

private:
    void OnMyCustomAction()
    {
        // 实现自定义操作的具体逻辑
        UE_LOG(LogTemp, Log, TEXT("Custom Motion Design Action Executed!"));
    }
};
```

## Demo 示例

以下是一个最小化的示例，展示了如何创建一个继承自 Motion Design 编辑器扩展的简单 C++ 类，并添加一个日志输出功能。

**文件：MyCustomMotionDesignExtension.h**
```cpp
// MyCustomMotionDesignExtension.h
#pragma once

#include "CoreMinimal.h"
#include "IAvaEditorExtension.h"

class FMyCustomMotionDesignExtension : public FAvaEditorExtension
{
public:
    UE_AVA_INHERITS(FMyCustomMotionDesignExtension, FAvaEditorExtension);

    virtual ~FMyCustomMotionDesignExtension() override = default;

    // 编辑器扩展激活时调用
    virtual void Activate() override
    {
        UE_LOG(LogTemp, Log, TEXT("MyCustomMotionDesignExtension: Activated!"));
        // 在此处进行初始化，如注册命令、绑定事件等
    }

    // 编辑器扩展停用时调用
    virtual void Deactivate() override
    {
        UE_LOG(LogTemp, Log, TEXT("MyCustomMotionDesignExtension: Deactivated!"));
        // 在此处进行清理，如解绑事件、释放资源等
    }

    // (可选) 用于向编辑器添加 UI 元素
    virtual void ExtendToolbarMenu(UToolMenu& InMenu) override
    {
        FToolMenuSection& Section = InMenu.AddSection("MyCustomTools", FText::FromString("My Custom Tools"));
        Section.AddMenuEntry(
            "LogHello",
            FText::FromString("Say Hello"),
            FText::FromString("Logs a hello message"),
            FSlateIcon(),
            FUIAction(FExecuteAction::CreateStatic(&FMyCustomMotionDesignExtension::SayHello))
        );
    }

private:
    static void SayHello()
    {
        UE_LOG(LogTemp, Warning, TEXT("Hello from Motion Design Extension!"));
    }
};
```

## 模块依赖

Motion Design 插件本身包含大量模块，但作为用户使用该插件时，你的项目模块通常只需要依赖其核心接口模块。同时，由于该插件集成了多个 Epic 的其他插件，因此具备以下独特依赖：

| 模块 | 用途 |
|---|---|
| `AvalancheEditor` | Motion Design 编辑器主模块 |
| `AvalancheOutliner` | 自定义大纲视图功能 |
| `AvalancheSequencer` | 自定义序列器集成功能 |
| `AvalancheViewport` | 自定义视口管理 |
| `AdvancedRenamer` | 高级重命名工具 |
| `CustomDetailsView` | 自定义详细信息视图 |
| `DynamicMaterial` | 动态材质系统 |
| `GeometryCache` | 几何体缓存 |
| `GeometryScripting` | 几何脚本 |
| `MediaCompositing` | 媒体合成 |
| `MediaIOFramework` | 媒体IO框架 |
| `MeshModelingToolsetExp` | 网格建模工具集（实验） |
| `RemoteControl` | 远程控制 |
| `SVGImporter` | SVG 导入器 |
| `Text3D` | 3D文本 |
| `ActorModifierCore` | Actor修改器核心 |

**说明**：要使用 Motion Design 的完整功能，你的项目通常需要启用上述插件。对于仅使用其部分运行时功能的场景，依赖可能会少一些。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own group | 将动态设计标签页（场景设置、大纲）移至关卡编辑器独立分组，优化布局 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 当使用节目单页面设置时，为影片渲染队列添加了分析数据收集功能 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and added | 向节目控制工具栏添加了页面加载选项（全部、下一个、已选），并增加了相关功能 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 添加了项目设置，可强制禁用3D文本和形状的碰撞检测 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated with a viewport client | 重构了视口关联/解除关联时的客户端通知机制，优化了代码复用 |

### 维护评价

Motion Design 插件是 Unreal Engine 虚拟制片工具链中的一个核心组件，处于**积极维护和快速迭代**的状态。

-   **创建时间**：2025年5月，是一个相对较新的大型插件。
-   **近期活跃度**：从最近的提交历史看（截至2026年5月），每周甚至每天都有功能更新、优化和 Bug 修复。这表明 Epic Games 的开发团队正在持续投入资源。
-   **功能范围**：插件规模庞大（43个模块，2000+文件），涵盖了从基本编辑器、大纲、序列器到材质设计、远程控制、媒体合成等高级功能，生态完整。
-   **状态判断**：**推荐使用**。该插件是 Epic 官方主推的虚拟制片工具之一，随着 UE 版本更新而持续发展。它是为专业广播和动态图形设计需求量身打造的，虽然功能复杂，但提供了开箱即用的完整解决方案。
-   **注意事项**：由于功能强大且集成深入，学习曲线可能较陡。使用前建议确保项目已启用其所有列出的依赖插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/virtual-production-in-unreal-engine/) (假设链接，请根据实际情况替换为 Motion Design 专属文档)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheFunctionalTest) (插件内包含功能测试模块)