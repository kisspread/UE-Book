# Motion Design Scene State

> 

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计场景状态 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `SceneState` (Runtime), `SceneStateBinding` (Runtime), `SceneStateBlueprint` (Runtime), `SceneStateBlueprintEditor` (Runtime), `SceneStateEditor` (Runtime), `SceneStateEvent` (Runtime), `SceneStateEventEditor` (Runtime), `SceneStateEventGraph` (Runtime), `SceneStateGameplay` (Runtime), `SceneStateGameplayEditor` (Runtime), `SceneStateMachineEditor` (Runtime), `SceneStateMachineGraph` (Runtime), `SceneStateTasks` (Runtime), `SceneStateTransitionGraph` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/SceneState) | |

## 用途

Scene State 是一套用于虚拟制片和动态设计的场景状态管理与驱动系统。其核心是**基于状态机（State Machine）的场景逻辑蓝图**，允许美术和技术人员在不编写传统 C++ 代码的情况下，通过可视化的图表（Graph）来定义复杂的场景状态切换、事件响应和数据绑定逻辑。它类似于行为树（Behavior Tree）或蓝图，但专注于**场景物体的宏观状态管理**，解决的是在虚拟拍摄、交互式装置或数据驱动演示中，如何组织和触发一系列复杂的场景状态变化（如灯光、动画、特效、物体变换）的问题。它提供了数据绑定（Binding）框架，使得场景状态可以与蓝图变量、事件和函数紧密关联，实现动态驱动。

## 使用场景

-   你正在为虚拟制片（Virtual Production）项目构建一个可交互的场景，需要根据拍摄指令（如导演喊“Action”）或外部输入（如传感器数据）来驱动整个场景的灯光、机位、特效和动画序列。
-   你在制作一个交互式艺术装置或数据可视化大屏，希望场景能根据用户的实时输入或后台数据流的变化，自动在不同展示模式（状态）间平滑切换。
-   你需要一个高度模块化的场景逻辑组织工具，将复杂的场景行为分解为清晰、可复用的状态和任务，并希望以蓝图方式快速原型和迭代。

## 蓝图用法

该插件的核心是创建和编辑 `USceneStateBlueprint`（场景状态蓝图）。主要通过蓝图编辑器和状态机图表（Graph）进行操作。

### 核心节点

由于插件高度依赖图形化编辑，其可直接调用的核心蓝图节点较少，主要集中在创建和查询上。更复杂的逻辑通过状态机图表中的节点（如状态、任务、转换）来配置。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateRootBinding` | 创建该蓝图的根绑定描述，用于将蓝图变量暴露为可绑定的数据源。 | `USceneStateBlueprint` |
| `GetBindingStructs` | 根据参数（目标结构体ID、是否包含全局/函数绑定）获取所有可绑定的描述信息数组。 | `USceneStateBlueprint` |
| `SetSceneStateSchema` | 设置此蓝图使用的场景状态模式（Schema），用于定义蓝图支持的状态机类型。 | `USceneStateBlueprint` |
| `FindStateMachineMatchingId` | 根据ID查找蓝图中匹配的状态机图表。 | `UE::SceneState::Graph` (工具函数) |
| `FindStateMatchingId` | 根据ID查找蓝图中匹配的状态节点。 | `UE::SceneState::Graph` (工具函数) |

### 使用示例（蓝图描述）

1.  **创建状态蓝图**: 在内容浏览器右键，选择 `Blueprint Class`，在父类选择中搜索并选择 `Motion Design Scene State Blueprint`。
2.  **编辑状态机**: 双击打开蓝图资产。在“我的蓝图”面板中，你会看到一个或多个“状态机图表”（State Machine Graphs）。双击图表进入状态机编辑器。
3.  **构建逻辑**: 在状态机图表中，右键可以创建：
    *   **状态（State）**: 代表场景的一个特定配置。在状态节点内部，可以添加“任务（Task）”来执行具体操作（如播放动画、设置材质）。
    *   **转换（Transition）**: 连接两个状态，定义转换条件（如基于时间、事件或蓝图变量）。
    *   **数据绑定**: 在状态、任务或转换的细节面板中，可以将它们的属性（参数）与蓝图的变量、函数或其他状态的数据通过“绑定（Binding）”进行关联，实现数据流驱动。
4.  **调试**: 在蓝图编辑器工具栏选择要调试的游戏实例或Actor，即可在运行时观察状态机的执行流程和数据变化。

## C++ 用法

### 头文件引入

```cpp
#include "SceneStateBlueprint.h"
#include "SceneStateBindingUtils.h"
#include "SceneStateBlueprintUtils.h"
```

### 基本用法

创建和查询一个场景状态蓝图资产（通常在编辑器工具中）。

```cpp
// 创建一个新的USceneStateBlueprint资产 (来源: UnrealEd/AssetTools模块常用模式)
UPackage* Package = CreatePackage(nullptr, TEXT("/Game/MySceneState"));
USceneStateBlueprint* Blueprint = NewObject<USceneStateBlueprint>(Package, TEXT("BP_MyScene"), RF_Public | RF_Standalone);
Blueprint->SetSceneStateSchema(UMyCustomSchema::StaticClass()); // 设置自定义模式
FAssetRegistryModule::AssetCreated(Blueprint);

// 根据ID查找状态机图表 (来源: SceneStateBlueprintBindingUtils.h)
FGuid TargetStateMachineId = /* ... */;
USceneStateMachineGraph* FoundGraph = UE::SceneState::Graph::FindStateMachineMatchingId(*Blueprint, TargetStateMachineId);
if (FoundGraph)
{
    // 处理找到的图表
}

// 获取可绑定的结构体信息 (来源: SceneStateBlueprint.h)
USceneStateBlueprint::FGetBindableStructsParams Params;
Params.TargetStructId = Blueprint->GetRootId();
Params.bIncludeGlobalDescs = true;
TArray<TInstancedStruct<FSceneStateBindingDesc>> BindingDescs;
Blueprint->GetBindingStructs(Params, BindingDescs);
```

### 进阶用法

遍历和操作状态机中的节点。这些工具函数在编辑器工具或自定义节点中非常有用。

```cpp
// 遍历蓝图中所有状态机图表的所有节点 (来源: SceneStateBlueprintUtils.h)
TArray<UEdGraph*> Graphs;
// ... 假设通过某种方式获取了蓝图中的图表列表 ...
UE::SceneState::Graph::VisitNodes(Graphs, [](USceneStateMachineNode* Node, UE::SceneState::Graph::EIterationResult& OutResult)
{
    if (USceneStateMachineStateNode* StateNode = Cast<USceneStateMachineStateNode>(Node))
    {
        // 处理状态节点
        UE_LOG(LogTemp, Log, TEXT("Found State: %s"), *StateNode->GetName());
    }
    else if (USceneStateMachineTaskNode* TaskNode = Cast<USceneStateMachineTaskNode>(Node))
    {
        // 处理任务节点
    }
    // 可以设置 OutResult = EIterationResult::Break 来提前中断遍历
    OutResult = UE::SceneState::Graph::EIterationResult::Continue;
});

// 为指定的状态节点创建蓝图变量 (来源: SceneStateBlueprintUtils.h， 结合 CreateParametersForStruct)
USceneStateMachineStateNode* TargetState = /* ... */;
if (TargetState)
{
    TArray<UE::PropertyBinding::FPropertyCreationDescriptor> CreationDescs;
    // ... 填充 CreationDescs，描述要创建的变量 ...
    UE::SceneState::Graph::CreateBlueprintVariables(Blueprint, CreationDescs);
}
```

## Demo 示例

一个最小的C++类，用于监听场景状态蓝图的调试对象变化。

**SceneStateDebugListener.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "SceneStateBlueprintDelegates.h"
#include "SceneStateDebugListener.generated.h"

UCLASS()
class USceneStateDebugListener : public UObject
{
    GENERATED_BODY()

public:
    void Initialize(USceneStateBlueprint* InBlueprint);
    void Deinitialize();

private:
    UFUNCTION()
    void OnDebugObjectChanged(const UE::SceneState::Graph::FBlueprintDebugObjectChange& Change);

    FDelegateHandle DelegateHandle;
};
```

**SceneStateDebugListener.cpp**
```cpp
#include "SceneStateDebugListener.h"
#include "SceneStateBlueprint.h"

void USceneStateDebugListener::Initialize(USceneStateBlueprint* InBlueprint)
{
    if (InBlueprint)
    {
        // 绑定到全局委托，监听任意场景状态蓝图的调试对象变化
        DelegateHandle = UE::SceneState::Graph::OnBlueprintDebugObjectChanged.AddUObject(this, &USceneStateDebugListener::OnDebugObjectChanged);
    }
}

void USceneStateDebugListener::Deinitialize()
{
    UE::SceneState::Graph::OnBlueprintDebugObjectChanged.Remove(DelegateHandle);
    DelegateHandle.Reset();
}

void USceneStateDebugListener::OnDebugObjectChanged(const UE::SceneState::Graph::FBlueprintDebugObjectChange& Change)
{
    // 当任何场景状态蓝图的调试对象改变时执行逻辑
    UE_LOG(LogTemp, Warning, TEXT("Blueprint '%s' debug object changed to '%s'"),
        *GetNameSafe(Change.Blueprint),
        *GetNameSafe(Change.DebugObject));
    // 在这里添加你的业务逻辑，例如更新UI或切换显示
}
```

## 模块依赖

该插件自包含，其公共模块依赖已在其内部处理。要在你自己的编辑器工具或运行时模块中使用 `SceneState` 的功能，你需要添加以下依赖：

| 模块 | 用途 |
|---|---|
| `SceneState` | 提供核心运行时数据结构（如 `FSceneStateBindingCollection`）。 |
| `SceneStateBinding` | 提供绑定框架的核心定义和工具（如 `FSceneStateBindingDesc`）。 |
| `SceneStateBlueprint` | 提供 `USceneStateBlueprint` 类，用于创建和管理场景状态蓝图资产。 |
| `SceneStateEvent` | 提供场景状态事件的核心定义。 |
| `PropertyBinding` | Epic 内部的属性绑定基础框架，SceneState 构建于此之上。 |
| `UnrealEd` (仅编辑器) | 如果你需要编写编辑器扩展来操作蓝图和图表。 |

**注意**: 大量模块（如 `*Editor`, `*Graph`, `*Tasks`）主要是为插件自身的蓝图编辑器提供支持，通常你不需要直接依赖它们。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口客户端关联/断开逻辑，减少冗余代码。 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回退了变更列表 53913857 的改动。 |
| 2026-04-17 | `6e111b5d` | Motion Design Scene State: fixed issues with bindings not checking for null event payload struct (op | 修复了绑定中未检查事件载荷结构体是否为空的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧版 UE_LOG 宏迁移到新版 UE_LOGF 宏。 |

### 维护评价

该插件创建于2025年8月，目前处于**活跃维护**状态。从git日志看，在最近几个月内仍有功能性更新（修复绑定空指针）和代码质量改进（宏迁移、重构）。尽管在 `.uplugin` 中被标记为 `IsBetaVersion: true` 和 `Category: Experimental`，表明其API和功能可能还不稳定，但持续的更新表明它正在被积极开发和用于虚拟制片管线中。对于虚拟制片或需要复杂场景状态管理的项目，这是一个值得尝试的**前沿工具**，但需注意其“实验性”标签，意味着未来版本可能发生重大变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/SceneState)
- [官方文档]() （暂无）
- [测试用例]() （插件目录内未发现明显测试文件）