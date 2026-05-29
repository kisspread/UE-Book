# UAF Anim Graph

> Framework for defining animation graphs.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | UAF 动画图 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `UAFAnimGraph` (Runtime), `UAFAnimGraphEditor` (Editor), `UAFAnimGraphUncookedOnly` (UncookedOnly), `UAFAnimGraphTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-26 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFAnimGraph) | |

## 用途

UAFAnimGraph 是 Unreal Animation Framework (UAF) 的核心模块，旨在提供一个高度模块化、数据驱动的动画图定义和执行框架。它取代了传统的、相对固化的动画蓝图状态机（Animation Blueprint State Machine）和AnimGraph，允许开发者通过图形化方式或纯C++代码来构建、组合和执行复杂的动画逻辑、状态转换和混合树。其主要解决的问题是：为大型、复杂的动画系统提供更灵活、可扩展、可重用且性能更优的底层架构，特别适用于需要程序化动画、动态动画融合或复杂动画逻辑的游戏项目。

## 使用场景

- 你正在开发一款开放世界RPG，需要高度动态和复杂的角色动画系统，包括程序化的运动混合和反应式动画。
- 你需要创建一个可复用的动画逻辑“库”，供不同角色类型（如人类、怪物）共享和组合，而不是为每个角色创建庞大的单一AnimGraph。
- 你的动画系统需要与物理系统（如Ragdoll）、IK 或游戏逻辑进行深度且灵活的交互。
- 你希望将动画逻辑的构建从单一的可视化编辑器，部分转移到更易于版本控制和测试的C++代码或数据资产中。

## 蓝图用法

由于此插件为实验性的基础框架，且 `CanContainContent` 为 true，其蓝图用法主要体现在资产创建和通过框架提供的接口进行高级配置，而非直接提供大量用户友好的 `BlueprintCallable` 函数节点。核心的“蓝图”使用可能在于创建 **UAFAnimGraph** 资产（一种数据资产），并在其中配置状态、混合节点等。

### 核心资产与节点

| 资产/节点 | 说明 | 所在类 |
|---|---|---|
| `UAFAnimGraph` 资产 | 定义动画图逻辑的主要数据容器 | `UUAFAnimGraph` |
| 状态 (State) | 动画图中的一个逻辑状态或行为节点 | `UUAFAnimGraphNode_State` |
| 转换 (Transition) | 定义状态之间的转换规则和条件 | `UUAFAnimGraphNode_Transition` |
| 混合节点 (Blend Node) | 负责混合不同动画源（如AnimSequence、其他Graph输出） | `UUAFAnimGraphNode_Blend` |

### 使用示例（蓝图资产编辑）

1.  在内容浏览器右键，选择 **Animation > UAF Anim Graph** 创建一个新资产。
2.  双击打开资产编辑器（类似于旧版的动画蓝图编辑器，但基于UAF框架）。
3.  在图表中，右键添加 **State** 节点来表示角色的不同动画行为（如Idle, Walk, Run）。
4.  使用 **Transition** 节点连接状态，并在细节面板中设置转换条件（例如，角色速度大于某个阈值）。
5.  在状态节点内部，添加 **Blend** 节点来混合具体的动画序列（Animation Sequence）。
6.  将此 `UAFAnimGraph` 资产关联到角色的 `UAFAnimInstance` 组件上，使其在运行时被执行。

## C++ 用法

UAFAnimGraph 的C++接口主要用于高级扩展、程序化创建图表或深度集成。测试用例（位于 `Tests/` 目录）是理解其API的最佳参考。

### 头文件引入

```cpp
#include "UAFAnimGraph.h"
```

### 基本用法

以下示例展示了如何通过代码查询一个UAFAnimGraph资产中的状态信息。此模式常见于游戏逻辑需要动画系统状态的场景。

```cpp
// 假设你已经有了一个指向 UAFAnimGraph 资产的指针：UUAFAnimGraph* MyAnimGraph;
// 来源参考：测试用例中对图表资产的序列化与反序列化检查

if (MyAnimGraph)
{
    // 获取图中所有定义的状态节点
    const TArray<UUAFAnimGraphNode_State*>& States = MyAnimGraph->GetStateNodes();

    // 遍历状态，进行逻辑检查或修改
    for (UUAFAnimGraphNode_State* StateNode : States)
    {
        UE_LOG(LogTemp, Log, TEXT("Found Animation State: %s"), *StateNode->GetName());

        // 检查状态是否具有特定的元数据标签（示例）
        if (StateNode->HasTag(FName("CriticalState")))
        {
            // 对特殊状态进行处理
        }
    }
}
```

### 进阶用法

更复杂的用法涉及继承UAF框架的核心类来实现自定义节点或扩展图表求值器。这通常需要对RigVM有深入了解，因为UAFAnimGraph底层使用RigVM来驱动图表执行。

```cpp
// 1. 创建一个自定义的动画图节点（例如，一个特殊的混合节点）
// 来源参考：UAFAnimGraphNode_Blend 和相关测试用例

UCLASS()
class UMyCustomBlendNode : public UUAFAnimGraphNode_Blend
{
    GENERATED_BODY()

public:
    // 覆盖此方法来实现自定义的混合逻辑
    virtual void Evaluate_AnyThread(FUAFAnimGraphEvaluationContext& Context) const override
    {
        // 获取输入动画数据
        const FAnimationPoseData& PoseA = Context.GetInputPose(0);
        const FAnimationPoseData& PoseB = Context.GetInputPose(1);

        // 执行自定义混合（这里只是简单示例）
        FAnimationPoseData BlendedPose = Context.GetOutputPose();
        // ... 混合逻辑 ...
        Context.SetOutputPose(BlendedPose);
    }
};

// 2. 在运行时动态操作UAFAnimGraph资产（如通过游戏逻辑添加状态）
// 注意：动态修改资产通常仅限于编辑器或工具代码，运行时修改是高级且不常见的操作。
// 来源参考：图表构建器和工厂类的测试

UUAFAnimGraph* DynamicGraph = NewObject<UUAFAnimGraph>();
UUAFAnimGraphNode_State* NewState = DynamicGraph->AddNewState(FName("Dodging"));
// ... 配置新状态 ...
```

## Demo 示例

一个最小的、可编译的C++示例，演示如何创建一个继承自UAFAnimInstance的自定义动画实例类，用于管理一个UAFAnimGraph资产。

```cpp
// MyAnimInstance.h
#pragma once

#include "CoreMinimal.h"
#include "UAFAnimInstance.h" // 包含UAF动画实例基类
#include "MyAnimInstance.generated.h"

UCLASS()
class UMyAnimInstance : public UUAFAnimInstance
{
    GENERATED_BODY()

public:
    // 可选：覆盖初始化函数，设置默认的UAFAnimGraph资产
    virtual void InitializeWithAnimationGraph(UUAFAnimGraph* InAnimGraph) override
    {
        Super::InitializeWithAnimationGraph(InAnimGraph);
        // 可以在这里进行一些初始化设置
    }

    // 可选：覆盖每帧的图表评估函数，注入额外逻辑
    virtual void NativeUpdateAnimation(float DeltaSeconds) override
    {
        Super::NativeUpdateAnimation(DeltaSeconds);
        // 在此处更新UAFAnimGraph评估上下文所需的变量
        // 例如：SetUAFGraphVariable(FName("bIsInAir"), bCharacterIsInAir);
    }
};
```

```cpp
// MyAnimInstance.cpp
#include "MyAnimInstance.h"
// 可能需要其他头文件，具体取决于您在NativeUpdateAnimation中调用的函数
```

## 模块依赖

您的模块需要依赖以下模块才能使用UAFAnimGraph：

| 模块 | 用途 |
|---|---|
| `UAF` | UAFAnimation核心框架，UAFAnimGraph的父插件 |
| `RigVM` | Rig Virtual Machine，UAFAnimGraph图表的底层执行引擎 |
| `AnimGraphRuntime` | 传统的动画图运行时组件，UAF可能需要与其交互或桥接 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `43658976` | Sequencer: Anim Mixer: Fix crash when scrubbing a level sequence after changing a Mix Layer transiti | 修复了在Sequencer动画混合器中切换混合层后拖动时间轴导致的崩溃。 |
| 2026-05-12 | `61c7c092` | [UEMHC] - Fix Geometry Export crash and material issues on re-export | 修复了重新导出几何体时的崩溃和材质问题。 |
| 2026-05-12 | `14c22336` | UAF: Add tick order dependecy between the UAF Montage Tick and CMC Tick to ensure the movement compo | 为UAF蒙太奇Tick和角色移动组件(CMC)Tick添加了执行顺序依赖，确保移动计算正确。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了格式化字符串说明符与参数位宽不匹配的问题。 |
| 2026-04-22 | `287203b9` | UE 5.8 Animation deprecation clean up (CL 9/10): UAF | 进行了UE 5.8动画系统废弃接口清理。 |

### 维护评价

UAFAnimGraph 是一个于2025年6月创建的较新插件，目前处于**实验性**阶段（`IsExperimentalVersion=true`）。从其近期（2026年5月）的Git提交记录看，开发仍然非常**活跃**，提交内容涵盖了功能完善（如Tick依赖）、关键Bug修复（崩溃问题）以及与引擎主线的兼容性更新（废弃清理）。这表明该插件是Epic未来动画系统（UAF）的核心实验田，虽然API和功能可能不稳定，但正在被积极塑造和维护。**作为实验性功能，不推荐在需要长期稳定性的生产项目中直接使用，但非常适合用于研究学习、原型开发或对动画框架有极高定制需求的前沿项目。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFAnimGraph)
- [官方文档]()（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFAnimGraph/Tests)