# UAF Anim Graph

> Framework for defining animation graphs.

| 属性 | 值 |
|---|---|
| 中文名 | 动画图框架 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器资产、调试跟踪） |
| 模块 | `UAFAnimGraph` (Runtime), `UAFAnimGraphEditor` (Editor), `UAFAnimGraphUncookedOnly` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-26 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFAnimGraph) | |

## 用途

UAFAnimGraph 是 Unreal Animation Framework (UAF) 的动画图组件。它提供了一个基于 Trait（特性）的框架，用于在编辑器中以可视化节点图的形式定义和组合动画逻辑。这个插件解决了以下问题：

1.  **模块化动画逻辑**：通过 Trait 系统，允许将动画行为（如混合、IK、物理等）封装成可复用的模块，并在图中进行堆栈组合，以构建复杂的动画状态机。
2.  **可视化编辑**：提供集成在工作区（Workspace）编辑器中的图编辑器、Trait 列表和 Trait 堆栈视图，方便美术和动画师直观地编辑动画逻辑。
3.  **运行时驱动**：基于 RigVM 虚拟机驱动动画图的执行，将编辑时定义的图转换为高效的运行时评估程序。
4.  **调试与分析**：集成重绕调试器（Rewind Debugger），提供动画图评估程序和序列信息的跟踪与可视化回放，便于分析动画执行过程。
5.  **资产预览**：在编辑器中为动画图资产提供可交互的 3D 视口预览。

## 使用场景

- 你需要一个比传统动画蓝图更灵活、更模块化的系统来定义复杂的动画状态和过渡逻辑。
- 你的项目使用了 UAF（Unreal Animation Framework），并希望利用其 Trait 系统来构建动画。
- 你希望在编辑器中通过拖放 Trait 节点来构建动画逻辑图，并实时预览结果。
- 你需要一个强大的动画调试工具，能够回溯并可视化动画图的执行过程和内部状态。

## 蓝图用法

此插件的运行时核心 (`UAFAnimGraph` 模块) 主要面向 C++，其蓝图接口由 UAF 核心插件提供。编辑器模块 (`UAFAnimGraphEditor`) 主要提供编辑器功能，没有公开的蓝图节点。因此，该插件的使用主要通过 C++ 或编辑器操作进行。

## C++ 用法

### 头文件引入

由于这是实验性插件，公共头文件可能较少。使用时主要需要依赖 `UAF` 和 `RigVM` 插件的核心头文件。

### 基本用法

创建和使用一个动画图资产的基本流程如下（需要结合 UAF 插件的其他部分）：

```cpp
// 1. 创建动画图资产 (通常通过编辑器或工厂)
// 具体创建流程由 UFactory (UUAFAnimGraphFactory) 处理。
UObject* NewAnimGraph = UUAFAnimGraphFactory::CreateNewAnimationGraph(/* ... */);

// 2. 获取或创建 Trait 堆栈 (Trait Stack)
// Trait 是构建动画逻辑的单元。在编辑器中通过 STraitEditorView 和 STraitStackView 进行管理。
// 在 C++ 中，操作需要通过 URigVMController 等 RigVM 接口进行。
// 示例概念：向堆栈中添加一个 Trait
// RigVMController->AddTraitToStack(/* ... */);

// 3. 将动画图资产连接到运行时组件 (UUAFComponent) 并驱动
// UAFComponent 负责在运行时评估动画图。
UUAFComponent* UAFComponent = /* 获取或创建组件 */;
UAFComponent->SetAnimationGraph(Cast<UUAFAnimGraph>(NewAnimGraph));
```

### 进阶用法

结合编辑器工具自定义行为：

```cpp
// 注册自定义的 Trait 编辑器扩展或资产预览工厂。
// 通过注册 FUAFGraphAssetPreviewFactory 为动画图资产提供自定义预览。
// 通过继承并注册 ITraitStackEditor (FTraitStackEditor) 来扩展 Trait 堆栈的编辑界面。

// 使用 FAnimNextAnimGraphProvider 和 FAnimNextAnimGraphAnalyzer 进行动画图运行时数据的跟踪分析。
// 通常用于集成到重绕调试器或自定义分析工具中。
```

## Demo 示例

一个最小化的、用于说明核心概念的 C++ 示例。请注意，完整的工作流程需要 UAF 和 RigVM 插件的配合。

**MyAnimGraphExample.h**
```cpp
#pragma once
#include "CoreMinimal.h"
// 包含 UAF 和 RigVM 的核心头文件
// #include "UAFAnimGraph.h" // 如果有公共API
// #include "RigVMBlueprint.h"

class UMyAnimGraphExample
{
public:
    // 概念性演示：描述如何与动画图资产交互
    static void DemonstrateAnimGraphUsage();
};
```

**MyAnimGraphExample.cpp**
```cpp
#include "MyAnimGraphExample.h"
#include "Engine/World.h"
#include "Components/SkeletalMeshComponent.h"
#include "UAFComponent.h" // 假设的UAF运行时组件
#include "UAFAnimGraph.h" // 假设的动画图资产类

void UMyAnimGraphExample::DemonstrateAnimGraphUsage()
{
    // 在此示例中，我们假设已经通过编辑器创建并保存了一个 UAFAnimGraph 资产。
    // 在实际运行时，你通常会从加载的资产开始。

    // 1. 加载动画图资产
    // UObject* LoadedAnimGraph = LoadObject<UUAFAnimGraph>(nullptr, TEXT("/Game/AnimGraphs/MyGraph.MyGraph"));

    // 2. 在角色或Actor上设置UAF组件，并关联动画图
    // 假设我们在一个已有骨骼网格体组件（SkeletalMeshComp）的Actor上操作
    // AActor* MyActor = GetWorld()->SpawnActor<AActor>();
    // USkeletalMeshComponent* SkelComp = MyActor->CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("Skel"));
    // UUAFComponent* UAFComp = MyActor->CreateDefaultSubobject<UUAFComponent>(TEXT("UAF"));

    // 3. 绑定动画图（概念）
    // if (UUAFAnimGraph* AnimGraph = Cast<UUAFAnimGraph>(LoadedAnimGraph))
    // {
    //     UAFComp->SetAnimGraph(AnimGraph);
    //     // UAFComp 现在将驱动 AnimGraph 的执行，并通过 SkelComp 输出动画
    // }

    // 4. 运行时逻辑通常由UAFComponent内部处理，通过RigVM评估Trait堆栈。
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `UAF` | 核心动画框架，提供 Trait、组件和运行时基础 |
| `RigVM` | RigVM 虚拟机，用于执行动画图逻辑 |
| `Workspace` | 工作区编辑器框架，提供图编辑器的宿主环境 |
| `ToolMenus` | 工具菜单扩展，用于注册编辑器菜单项 |
| `RewindDebugger` | 重绕调试器集成，用于动画图执行跟踪 |
| `PropertyEditor` | 属性自定义，用于 Trait 数据的细节面板展示 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `43658976` | Sequencer: Anim Mixer: Fix crash when scrubbing a level sequence after changing a Mix Layer transiti | 修复动画混合器在更换混合层过渡后拖动时间轴导致的崩溃 |
| 2026-05-12 | `14c22336` | UAF: Add tick order dependecy between the UAF Montage Tick and CMC Tick to ensure the movement compo | 添加UAF蒙太奇Tick与移动组件Tick之间的顺序依赖，确保移动组件更新正确 |
| 2026-04-22 | `287203b9` | UE 5.8 Animation deprecation clean up (CL 9/10): UAF | UE 5.8动画功能弃用清理（系列9/10）：针对UAF模块 |

### 维护评价

- **活跃维护**：最近一次更新发生在2026年5月，包含功能性修复（崩溃修复）和引擎兼容性更新（UE 5.8弃用清理）。这表明插件仍处于**活跃维护**状态。
- **实验性状态**：插件明确标记为 `IsExperimentalVersion: true`，且 `EnabledByDefault: false`，表明它是一个实验性功能，API和功能在未来版本中可能发生重大变化。
- **推荐使用**：对于希望在项目中**前瞻性地探索 UAF 框架**或需要**高度模块化动画图编辑**的开发者，可以尝试使用。但鉴于其**实验性**本质，不建议用于追求长期稳定的生产项目，除非你愿意承担未来重构的风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFAnimGraph)
- [官方文档]() (暂无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFAnimGraph/Tests)