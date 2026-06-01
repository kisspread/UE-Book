```markdown
# Avalanche Transition Editor

> Compositing, designer and broadcasting tool.

| 属性 | 值 |
|---|---|
| 中文名 | 动态过渡编辑器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Avalanche` (Runtime), `AvalancheAttribute` (Runtime), `AvalancheAttributeEditor` (Runtime), `AvalancheCamera` (Runtime), `AvalancheComponentVisualizers` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheEditorCore` (Runtime), `AvalancheEffectors` (Runtime), `AvalancheEffectorsEditor` (Runtime), `AvalancheFunctionalTest` (Runtime), `AvalancheInteractiveTools` (Runtime), `AvalancheInteractiveToolsRuntime` (Runtime), `AvalancheLevelViewport` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheMRQEditor` (Runtime), `AvalancheMask` (Runtime), `AvalancheMaskEditor` (Runtime), `AvalancheMaterial` (Runtime), `AvalancheMedia` (Runtime), `AvalancheMediaEditor` (Runtime), `AvalancheModifiers` (Runtime), `AvalancheModifiersEditor` (Runtime), `AvalancheOutliner` (Runtime), `AvalanchePropertyAnimator` (Runtime), `AvalanchePropertyAnimatorEditor` (Runtime), `AvalancheRemoteControl` (Runtime), `AvalancheRemoteControlEditor` (Runtime), `AvalancheSVGEditor` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheSceneRigEditor` (Runtime), `AvalancheSceneTree` (Runtime), `AvalancheSequence` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheShapes` (Runtime), `AvalancheShapesEditor` (Runtime), `AvalancheTag` (Runtime), `AvalancheTagEditor` (Runtime), `AvalancheText` (Runtime), `AvalancheTextEditor` (Runtime), `AvalancheTransition` (Runtime), `AvalancheTransitionEditor` (Runtime), `AvalancheViewport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

AvalancheTransitionEditor 是 Motion Design（Avalanche）插件中负责**过渡逻辑编辑**的模块。该模块基于 Unreal Engine 的 StateTree 系统，为 Motion Design 场景提供可视化的状态过渡编辑器。

核心功能包括：
- **过渡树编辑器**：提供图形化界面编辑状态之间的过渡逻辑，包含条件（Conditions）、任务（Tasks）和过渡（Transitions）三个容器
- **MVVM 架构**：采用严格的 ViewModel 模式，将编辑器 UI 与底层 StateTree 数据分离，支持注册表（Registry）系统按 Key 查找 ViewModel
- **调试支持**：内建调试器，可在编辑器中实时查看 StateTree 实例的执行状态、节点进入/退出事件
- **编译系统**：集成 StateTree 编译器，支持编译状态管理、错误日志、保存策略配置
- **拖拽操作**：支持状态节点的拖放重排、复制移动等操作
- **场景桥接**：通过 `IAvaTransitionBehavior` 接口与 Motion Design 场景系统集成，控制过渡图层（Transition Layer）、实例化模式等

该模块从实验性插件目录迁移到 VirtualProduction 目录，标志着其已成为 Motion Design 正式功能的一部分。

## 使用场景

- 你在制作虚拟制片直播画面，需要控制不同场景状态之间的自动切换逻辑 → 用 AvalancheTransitionEditor
- 你需要定义"当满足某个条件时，从场景 A 过渡到场景 B，并在过渡期间执行特定任务" → 用过渡树编辑器
- 你需要实时调试 Motion Design 场景中状态机的执行流程 → 使用内建调试器
- 你需要通过远程控制接口触发场景过渡 → 结合 AvalancheRemoteControl 模块

## 蓝图用法

该模块主要为编辑器模块，大部分功能通过 C++ API 暴露。以下是可蓝图访问的关键接口：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetTransitionLayer` | 获取过渡图层句柄（已废弃） | `UAvaTransitionTreeEditorData` |
| `SetTransitionLayer` | 设置过渡图层句柄（已废弃） | `UAvaTransitionTreeEditorData` |
| `ShouldCreateTransitionLogicDefaultScene` | 查询是否创建默认过渡场景 | `UAvaTransitionEditorSettings` |
| `ToggleCreateTransitionLogicDefaultScene` | 切换是否创建默认过渡场景 | `UAvaTransitionEditorSettings` |

### 编辑器设置

过渡逻辑编辑器设置位于 **Project Settings → Motion Design → Transition Logic** 中：
- **Default Template**：配置新建过渡树时使用的模板资产
- **Create Transition Logic Default Scene**：控制首次创建 Motion Design 场景时是否自动生成默认过渡逻辑

## C++ 用法

### 头文件引入

```cpp
// 编辑器模块接口
#include "IAvaTransitionEditorModule.h"

// 过渡树编辑器数据
#include "AvaTransitionTreeEditorData.h"

// 编辑器设置
#include "Settings/AvaTransitionEditorSettings.h"
```

### 基本用法 — 检查模块并注册回调

```cpp
// 来源: Public/IAvaTransitionEditorModule.h
#include "IAvaTransitionEditorModule.h"

if (IAvaTransitionEditorModule::IsLoaded())
{
    IAvaTransitionEditorModule& TransitionModule = IAvaTransitionEditorModule::Get();
    
    // 注册回调：当创建默认过渡树时执行自定义逻辑
    TransitionModule.GetOnBuildDefaultTransitionTree().BindLambda(
        [](UAvaTransitionTreeEditorData& InEditorData)
        {
            // 在这里自定义默认过渡树的构建逻辑
        });
}
```

### 基本用法 — 编辑过渡树编辑器数据

```cpp
// 来源: Public/AvaTransitionTreeEditorData.h
#include "AvaTransitionTreeEditorData.h"

// 创建新状态（在指定状态之前或之后）
UStateTreeState& NewState = EditorData->CreateState(SiblingState, /*bInAfter=*/true);

// 查找状态元数据（颜色、描述等）
const FAvaTransitionStateMetadata* Metadata = EditorData->FindStateMetadata(StateId);
if (Metadata)
{
    // 使用元数据
}

// 获取或创建状态元数据
FAvaTransitionStateMetadata& MetadataRef = EditorData->FindOrAddStateMetadata(StateId);

// 监听树刷新请求
EditorData->GetOnTreeRequestRefresh().AddLambda([]()
{
    // 树数据已变更，需要刷新编辑器
});

// 比较两份编辑器数据是否相同
bool bSame = EditorData->Compare(OtherEditorData);
```

### 进阶用法 — ViewModel 注册表系统

```cpp
// 来源: Private/ViewModels/Registry/AvaTransitionViewModelRegistryCollection.h
#include "AvaTransitionViewModelRegistryCollection.h"

// 通过 UObject 查找对应的 ViewModel
TSharedPtr<FAvaTransitionViewModel> ViewModel = RegistryCollection->FindViewModel(SomeUObject);

// 通过 GUID 查找 ViewModel
FGuid StateId = /* ... */;
TSharedPtr<FAvaTransitionViewModel> FoundVM = RegistryCollection->FindViewModel(StateId);
```

### 进阶用法 — ViewModel 遍历工具

```cpp
// 来源: Private/ViewModels/AvaTransitionViewModelUtils.h
using namespace UE::AvaTransitionEditor;

// 遍历所有状态 ViewModel
TArray<TSharedRef<FAvaTransitionStateViewModel>> StateVMs = 
    GetViewModelsOfType<FAvaTransitionStateViewModel>(ViewModels, /*bInRecursive=*/true);

// 递归遍历并支持中断
ForEachViewModelOfType<FAvaTransitionStateViewModel>(ViewModels,
    [](const TAvaTransitionCastedViewModel<FAvaTransitionStateViewModel>& InVM, EAvaTransitionIterationResult& OutResult)
    {
        // 处理每个状态
        if (ShouldStop)
        {
            OutResult = EAvaTransitionIterationResult::Break;
        }
    }, /*bInRecursive=*/true);

// 查找某个 ViewModel 的特定类型祖先
TSharedPtr<FAvaTransitionStateViewModel> Ancestor = 
    FindAncestorOfType<FAvaTransitionStateViewModel>(CurrentViewModel, /*bIncludeSelf=*/false);
```

### 进阶用法 — 编译过渡树

```cpp
// 来源: Private/Compiler/AvaTransitionCompiler.h
#include "AvaTransitionCompiler.h"

FAvaTransitionCompiler Compiler;
Compiler.SetTransitionTree(TransitionTree);

// 编译（支持不同编辑模式）
bool bSuccess = Compiler.Compile(EAvaTransitionEditorMode::Default);

// 获取编译状态图标
FSlateIcon StatusIcon = Compiler.GetCompileStatusIcon();

// 获取编译结果日志
IMessageLogListing& Results = Compiler.GetCompilerResultsListing();
```

## Demo 示例

以下是一个最小的自定义过渡行为（Transition Behavior）示例，展示如何与过渡树系统集成：

```cpp
// MyTransitionBehavior.h
#pragma once

#include "CoreMinimal.h"
#include "AvaTransitionBehavior.h"  // 来自 AvalancheTransition 模块

class UMyTransitionBehavior : public UObject, public IAvaTransitionBehavior
{
    GENERATED_BODY()

public:
    //~ Begin IAvaTransitionBehavior
    virtual FAvaTagHandle GetTransitionLayer() const override;
    virtual void SetTransitionLayer(const FAvaTagHandle& InTransitionLayer) override;
    virtual UWorld* GetWorld() const override;
    //~ End IAvaTransitionBehavior
};
```

```cpp
// MyTransitionBehavior.cpp
#include "MyTransitionBehavior.h"
#include "IAvaTransitionEditorModule.h"

FAvaTagHandle UMyTransitionBehavior::GetTransitionLayer() const
{
    return TransitionLayer;
}

void UMyTransitionBehavior::SetTransitionLayer(const FAvaTagHandle& InTransitionLayer)
{
    TransitionLayer = InTransitionLayer;
}

UWorld* UMyTransitionBehavior::GetWorld() const
{
    return GetOuter()->GetWorld();
}
```

## 模块依赖

从源码分析，Avalanche 插件包含以下依赖（见 .uplugin Description）：

| 模块 | 用途 |
|---|---|
| `AdvancedRenamer` | 高级重命名工具 |
| `CustomDetailsView` | 自定义细节面板视图 |
| `DynamicMaterial` | 动态材质系统 |
| `GeometryCache` | 几何体缓存 |
| `GeometryScripting` | 几何体脚本 |
| `MediaCompositing` | 媒体合成 |
| `MediaIOFramework` | 媒体 IO 框架 |
| `MeshModelingToolsetExp` | 网格建模工具集 |
| `RemoteControl` | 远程控制 |
| `SVGImporter` | SVG 导入器 |
| `Text3D` | 3D 文本 |
| `ActorModifierCore` | Actor 修改器核心 |
| `StateTree` | 状态树系统（过渡逻辑核心依赖） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将 Motion Design 的场景设置和大纲视图面板移至独立分组 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 使用 Rundown 页面设置时添加 MRQ 分析数据 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 为节目控制工具栏添加页面加载选项 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 添加项目设置以强制禁用 Text3D 和形状的碰撞 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口客户端关联/断开通知机制 |

### 维护评价

**活跃维护**。Avalanche（Motion Design）是 Epic Games 虚拟制片管线的核心组件之一：

- **创建时间**：2025 年 5 月，从实验性目录正式迁移至 VirtualProduction
- **更新频率**：非常活跃，近一周内有 5 次提交，涵盖功能添加、UI 改进和性能优化
- **项目规模**：2060 个源文件，43 个模块，是一个大型企业级插件
- **活跃度**：持续有新功能和改进提交，是 UE5 虚拟制片工具链的活跃组成部分
- **推荐使用**：如果你的项目涉及虚拟制片（Virtual Production）场景管理、直播画面切换或广播级内容制作，强烈推荐使用

⚠️ 注意：该插件默认未启用（`EnabledByDefault=false`），需要在 Plugins 面板中手动启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [官方文档](https://docs.unrealengine.com/en-US/RenderingAndGraphics/VirtualProduction/)
```