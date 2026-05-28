# Unreal Animation Framework (UAF)

> Framework for defining functional data flow for animation systems

| 属性 | 值 |
|---|---|
| 中文名 | 动画状态框架 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、图表、测试资源） |
| 模块 | `UAF` (Runtime), `UAFEditor` (Runtime), `UAFTestData` (Runtime), `UAFUncookedOnly` (Runtime), `UAFTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-26 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAF) | |

## 用途

UAF (Unreal Animation Framework) 是一个**实验性的、数据驱动的动画系统框架**。它远不止是一个简单的状态机，而是一套完整的、基于图表的工具链，用于定义动画状态、变量、事件以及它们之间的复杂数据流关系。

它解决的核心问题是：让动画师和技术美术能够以**数据驱动和可视化**的方式，而非纯粹依赖代码，来定义复杂的动画逻辑和状态转换。它内置了基于 RigVM 的图表编辑器、强大的变量系统、资产浏览器、以及与内容浏览器的深度集成，旨在为大型、复杂的动画系统提供结构化的构建块和工作流程。

## 使用场景

*   **构建复杂的动画状态机与状态图**：当你的角色动画系统包含数十个状态（Idle、Walk、Run、Attack、Stagger、Death等）以及复杂的转换逻辑时，UAF 的图表编辑器提供了比蓝图状态机更专业和高效的编辑环境。
*   **定义可复用的动画逻辑与变量系统**：你需要为不同角色或武器定义可共享的动画参数（如“攻击强度”、“速度”、“是否在空中”）。UAF 的变量和函数系统允许你创建可在多个资产间引用和重用的共享变量和逻辑函数。
*   **实现动画逻辑与渲染/物理的解耦**：你希望动画逻辑能独立于具体的角色蓝图和组件。UAF 的 “System” 和 “Module” 概念允许你将动画逻辑封装成独立的、可组合的数据资产。
*   **需要可视化调试与数据流分析**：动画系统出错时，你需要清晰地看到变量的值、状态的流向和事件的触发。UAF 编辑器与 Unreal 的 Rewind Debugger 和 Insights 追踪系统深度集成，支持可视化调试。
*   **动画驱动程序开发**：作为引擎或大型项目的核心开发者，你需要一个标准化的、可扩展的框架来构建下一代动画驱动解决方案。

## 蓝图用法

UAF 主要通过其编辑器界面（基于 Workspace 和图表）进行操作，提供的直接蓝图节点较少。其“用法”更多体现在资产（UAF System/Module）的创建和配置上。

### 核心编辑器交互

| 功能 | 说明 | 所在类/上下文 |
|---|---|---|
| `SVariablePickerCombo` | 变量选择器下拉框。在图表中编辑节点（如设置变量值）时，弹出此窗口选择要操作的变量及其来源。 | `UE::UAF::Editor::SVariablePickerCombo` |
| `SVariablePicker` | 变量选择器核心列表。`SVariablePickerCombo` 的内部实现，展示所有可用的变量（本地、共享、引用），支持搜索和类型过滤。 | `UE::UAF::Editor::SVariablePicker` |
| `SRigVMFunctionPicker` | RigVM 函数选择器。用于在图表中选择要调用的 RigVM 函数，支持按资产过滤和新建函数。 | `UE::UAF::Editor::SRigVMFunctionPicker` |
| `SActionMenu` | 图表右键操作菜单。当在 UAF 图表编辑器中右键时弹出，提供添加节点（RigVM Unit, 变量, 函数, 注释）的菜单项。 | `UE::UAF::Editor::SActionMenu` |
| `SUAFBrowser` | UAF 专用资产浏览器。一个集成在 UAF 编辑器中的侧边栏，用于搜索、预览和创建 UAF 相关资产（如 System、Module、变量集、标签等）。 | `UE::UAF::Editor::SUAFBrowser` |

### 使用示例（蓝图描述）
1.  **创建一个变量**：
    1.  在 UAF 编辑器的内容区域（或通过 UAF Browser），右键选择 “Animation Framework” -> “New Variable”。
    2.  在弹出的对话框中，输入变量名，选择数据类型（如 `Float`, `Bool`）。
    3.  创建后，变量会出现在 Outliner 的 “Variables” 面板中。
2.  **在图表中使用变量**：
    1.  在图表中右键，选择 “Variables” -> “Get” 或 “Set”。
    2.  此时会弹出 `SVariablePickerCombo`。
    3.  在下拉列表中搜索或浏览找到你刚创建的变量，选择它。
    4.  一个获取或设置该变量的节点就会被添加到图表中。
3.  **调用一个函数**：
    1.  在图表中右键，选择 “Functions”。
    2.  从 `SRigVMFunctionPicker` 列表中，选择一个已存在的函数或点击 “New Function…” 创建新函数。
    3.  函数调用节点将被添加到图表，其输入输出引脚可以连接其他节点。

## C++ 用法

### 头文件引入

```cpp
// 访问UAF编辑器模块接口
#include "IAnimNextEditorModule.h"

// 使用变量选择器相关类型
#include "Variables/VariablePickerArgs.h"
#include "Variables/SVariablePickerCombo.h"

// 使用函数选择器
#include "Common/SRigVMFunctionPicker.h"

// 使用资产预览相关接口
#include "Common/AssetPreview/IUAFAssetPreview.h"
```

### 基本用法
(源自 `Private/Variables/SVariablePicker.h` 和 `Public/Variables/SVariablePickerCombo.h`)

```cpp
// 1. 定义一个变量选择器的参数配置
UE::UAF::Editor::FVariablePickerArgs PickerArgs;

// 设置筛选条件：只显示公共变量
PickerArgs.FlagInclusionFilter = EAnimNextExportedVariableFlags::Public;

// 设置选择变量后的回调
PickerArgs.OnVariablePicked = UE::UAF::Editor::FOnVariablePicked::CreateLambda(
    [](const FAnimNextSoftVariableReference& Ref, const FAnimNextParamType& Type) {
        // 用户选择了一个变量，Ref和Type包含了变量的引用和类型信息
        UE_LOG(LogTemp, Log, TEXT("Picked variable: %s"), *Ref.GetVariableName().ToString());
    }
);

// 2. 创建并使用一个带下拉框的变量选择器控件
TSharedRef<UE::UAF::Editor::SVariablePickerCombo> PickerCombo =
    SNew(UE::UAF::Editor::SVariablePickerCombo)
    .PickerArgs(PickerArgs)
    .VariableName(FText::FromString(TEXT("MyVariable")));

// 将PickerCombo添加到你的Slate UI中...
// MyContainer->AddSlot() [ PickerCombo ];
```

### 进阶用法
(源自 `Private/Common/AssetPreview/IUAFAssetViewportPreview.h` 和测试模式推断)

```cpp
// 1. 实现一个自定义的、带3D视口的资产预览器
class FMyAssetPreview : public UE::UAF::Editor::IUAFAssetViewportPreview
{
public:
    // 实现关键的预览场景定制函数
    virtual void OnCustomizePreviewScene(
        FAdvancedPreviewScene& InPreviewScene,
        FEditorViewportClient& InEditorViewportClient) override
    {
        // 在这里设置预览场景的背景、灯光、以及预览的网格体/动画
        InPreviewScene.SetEnvironmentVisibility(false);
        InPreviewScene.AddComponent(
            CreatePreviewMeshComponent(),
            FTransform::Identity
        );
    }

    // 指定此预览器支持的资产类型
    virtual const UStruct* GetAssetPreviewType() const override
    {
        return UMyCustomAsset::StaticClass();
    }

private:
    UMeshComponent* CreatePreviewMeshComponent() { /* ... */ }
};

// 2. 在编辑器启动时注册这个预览工厂
class FMyEditorModule : public IModuleInterface
{
    virtual void StartupModule() override
    {
        UE::UAF::Editor::FUAFAssetPreviewFactory Factory;
        Factory.CreateAssetPreviewWidget = [](TSharedPtr<FAssetEditorToolkit> Toolkit, const FAssetData& AssetData) {
            return MakeShared<FMyAssetPreview>();
        };
        Factory.GetPreviewType = [] { return UMyCustomAsset::StaticClass(); };

        // 使用 UAF 的子系统来注册工厂
        UUAFAssetPreviewFactorySubsystem* Subsystem = GEditor->GetEditorSubsystem<UUAFAssetPreviewFactorySubsystem>();
        Subsystem->AddAssetPreviewFactory(MakeShared<UE::UAF::Editor::FUAFAssetPreviewFactory>(Factory));
    }
};
```

## Demo 示例
一个最小化的C++示例，展示如何响应UAF编辑器的事件。
*(注意：此示例仅为演示流程，实际使用需确保模块正确依赖和初始化)*

### MyUAFListener.h
```cpp
#pragma once
#include "CoreMinimal.h"
#include "IAnimNextEditorModule.h"

class FMyUAFListener
{
public:
    void Initialize();
    void Shutdown();

private:
    // 处理图表中双击节点的事件
    void OnNodeDoubleClicked(
        const UE::Workspace::FWorkspaceEditorContext& Context,
        const UEdGraphNode* Node);

    FDelegateHandle DoubleClickDelegateHandle;
};
```

### MyUAFListener.cpp
```cpp
#include "MyUAFListener.h"
#include "Modules/ModuleManager.h"

void FMyUAFListener::Initialize()
{
    // 获取UAF编辑器模块
    IAnimNextEditorModule& UAFEditorModule = FModuleManager::GetModuleChecked<IAnimNextEditorModule>("UAFEditor");

    // 注册节点双击处理函数
    DoubleClickDelegateHandle = UAFEditorModule.RegisterNodeDblClickHandler(
        IAnimNextEditorModule::FNodeDblClickNotificationDelegate::CreateRaw(
            this, &FMyUAFListener::OnNodeDoubleClicked));

    UE_LOG(LogTemp, Log, TEXT("MyUAFListener: Registered for node double-click events."));
}

void FMyUAFListener::Shutdown()
{
    if (IAnimNextEditorModule* UAFEditorModule = FModuleManager::GetModulePtr<IAnimNextEditorModule>("UAFEditor"))
    {
        // 注销处理函数
        UAFEditorModule->UnregisterNodeDblClickHandler(DoubleClickDelegateHandle);
    }
}

void FMyUAFListener::OnNodeDoubleClicked(
    const UE::Workspace::FWorkspaceEditorContext& Context,
    const UEdGraphNode* Node)
{
    if (Node)
    {
        UE_LOG(LogTemp, Log, TEXT("MyUAFListener: User double-clicked on node '%s' in asset '%s'."),
            *Node->GetName(),
            *Context.GetAssetName().ToString());
        // 在此处添加自定义逻辑，例如打开特定的资产或窗口
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LiveCoding` | 支持编辑器中的热重载功能，便于快速迭代 |
| `PropertyViewer` | 为变量选择器 (`SVariablePicker`) 提供核心的属性浏览和树状视图控件 |
| `RigVM` | 核心的虚拟机和图表编辑器基础，UAF 图表底层基于 RigVM |
| `AnimationCore`, `AnimationBlueprintLibrary` | 提供动画核心数据结构和蓝图动画库，与UAF动画逻辑层交互 |
| `GraphEditor` | 提供图表编辑器的基础框架，UAF 图表编辑器基于此扩展 |
| `Workspace` | 提供通用的资产编辑器“工作区”框架，UAF 编辑器是其上的一个定制化模式 |
| `RewindDebugger` | 集成动画回溯调试器，用于可视化调试UAF动画状态和变量 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `eeaff753` | UAF: Introduce optional tick dependency between the UAF Component targeting a ACharacters mesh compo | 为UAF组件引入可选的Tick依赖关系，针对ACharacter的网格体组件。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在MSVC和Clang编译器之间具有可移植性。 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了在格式化函数中使用的作用域枚举可能导致输出乱码的问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了格式化说明符位宽与参数位宽不匹配的问题（32位与64位）。 |
| 2026-04-24 | `523ac953` | Fix incorrect quaternion attribute type usage | 修复了四元数属性类型的错误使用。 |

### 维护评价
UAF 是一个**非常新的、处于活跃实验阶段**的插件。

*   **年龄与阶段**：创建于 2025 年中，版本号仅为 0.1，且明确标记为 `IsExperimentalVersion=true`，表明它仍在快速迭代和演变中，API 和架构可能会发生较大变化。
*   **活跃度**：从提交历史看，**维护非常活跃**。最近几个月持续有功能改进（如组件依赖）、编译器兼容性修复、以及关键的底层数据正确性修复（枚举、四元数类型）。这表明 Epic 正在积极开发和完善它。
*   **推荐使用**：
    *   **不推荐用于正式生产环境项目**：鉴于其实验状态、0.1的版本号以及未来可能发生破坏性更改的风险，目前不适合作为稳定依赖。
    *   **强烈推荐用于技术预研和原型开发**：如果你对下一代动画框架的架构感兴趣，或者正在为一个大型、复杂的动画系统做技术预研，UAF 提供了一个极其强大和前瞻性的参考。它是学习数据驱动动画系统和工作流设计的绝佳案例。
*   **已知限制**：作为实验性插件，文档和支持资源有限，主要依赖于源码阅读和社区探索。部分功能（如资产预览系统）被注释为“待替换”。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAF)