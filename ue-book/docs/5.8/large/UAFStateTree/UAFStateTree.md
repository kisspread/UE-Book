# UAF State Tree

> StateTree integration for UAF.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | UAF状态树集成 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（状态树资产、蓝图资产） |
| 模块 | `UAFStateTree` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFStateTree) | |

## 用途

这个插件的核心作用是架起 Unreal Animation Framework (UAF) 与 StateTree 状态机系统之间的桥梁。它解决了在复杂的动画逻辑中，如何利用 StateTree 强大的状态管理能力来驱动 UAF 动画图（Animation Graph）的问题。通过提供一组基类、任务（Tasks）和条件（Conditions），它让开发者能够在 StateTree 中直接创建、播放和控制基于 UAF 的动画资产，并管理其共享变量，从而实现更结构化、更易维护的动画状态逻辑。

## 使用场景

- 你正在使用 UAF 构建角色动画系统，并且需要一个强大的状态机来管理不同动画状态（如 Idle、Run、Attack）之间的转换和逻辑。
- 你需要在动画状态转换时，通过 StateTree 的任务和条件来触发 UAF 动画图的播放、混合或参数变更。
- 你希望将复杂的动画控制逻辑从蓝图或 C++ 代码中剥离出来，转移到更直观、更专业的 StateTree 编辑器中进行设计和调试。

## 蓝图用法

本插件主要提供 StateTree 编辑器中可用的节点（任务和条件）。这些节点以结构体形式存在，可在 StateTree Asset 编辑器中直接使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UAF Graph` | 核心任务节点。当状态激活时，将指定的 UAF 动画图资产推入混合栈，并管理其播放时间、混合和循环。 | `FAnimNextStateTreeGraphInstanceTask` |
| `UAF Set Variable` | 任务节点。在进入状态时，将指定的值写入一个 UAF 共享变量。 | `FUAFStateTreeSetVariableTask` |
| `(PROTOTYPE) UAF Float Variable Compare` | 条件节点。比较一个 UAF 浮点变量与指定值。 | `FUAFFloatCompareCondition` |
| `(PROTOTYPE) UAF Enum Variable Compare` | 条件节点。比较一个 UAF 枚举变量与指定值。 | `FUAFEnumCompareCondition` |

### 使用示例（蓝图描述）

在 StateTree Asset 编辑器中：
1.  添加一个新状态，例如 “AttackState”。
2.  在该状态的 **Tasks** 列表中，添加 “UAF Graph” 任务。
3.  在该任务的 **Details** 面板中，通过 “Asset Data” 属性选择或创建要播放的 `UAnimNextStateTree` 资产。
4.  可配置 **Blend Options**（混合选项）、**Blend Profile**（混合配置文件）以及 **Complete Blend Out Time**（提前触发淡出时间）等参数。
5.  在状态的 **Conditions** 或转换规则中，可以使用 “(PROTOTYPE) UAF Float Variable Compare” 等节点来检查变量，决定状态是否进入或退出。

## C++ 用法

### 头文件引入

```cpp
#include "UAFStateTree/Internal/AnimNextStateTree.h"
#include "UAFStateTree/Internal/Tasks/AnimNextStateTreeGraphInstanceTask.h"
#include "UAFStateTree/Internal/Tasks/UAFStateTreeSetVariableTask.h"
```

### 基本用法

从资产中获取 StateTree 实例并设置。
（来源：`Internal/AnimNextStateTree.h`）

```cpp
// 获取一个 UAnimNextStateTree 资产
UAnimNextStateTree* MyAnimationGraph = LoadObject<UAnimNextStateTree>(nullptr, TEXT("/Game/Animation/MyAnimNextStateTree"));

// 检查其内部包含的 StateTree 资产
if (MyAnimationGraph && MyAnimationGraph->StateTree)
{
    UStateTree* StateTreeAsset = MyAnimationGraph->StateTree;
    // StateTreeAsset 现在可以在 StateTree 组件中使用
}
```

### 进阶用法

理解插件为 StateTree 任务提供的上下文（Context）和结构，便于进行自定义扩展。
（来源：`Private/UAFStateTreeContext.h`, `Internal/Tasks/AnimNextStateTreeGraphInstanceTask.h`）

```cpp
// 理解 StateTree 任务执行时，通过 FUAFStateTreeContext 获取 UAF 上下文
struct FUAFStateTreeContext
{
    // 虚函数，用于将动画资产推入 UAF 的混合栈
    virtual bool PushAssetOntoBlendStack(UE::UAF::FGraphAssetHandleConstView InAsset, const FAlphaBlendArgs& InBlendArguments, const UUAFBlendProfile* InBlendProfile) const;

    // 虚函数，用于查询当前动画图的播放信息
    virtual void QueryPlaybackInfo(FPlaybackInfo& OutPlaybackInfo) const;

    // 虚函数，用于获取持有共享变量的资产实例
    virtual FUAFAssetInstance* GetVariablesOwner() const;
};

// 任务实例数据包含动画图播放所需的核心参数
struct FAnimNextGraphInstanceTaskInstanceData
{
    TInstancedStruct<FUAFGraphFactoryAsset> AssetData; // 要实例化的动画图资产
    FAlphaBlendArgs BlendOptions; // 混合选项
    float PlaybackRatio = 1.0f;   // 当前播放比例
    float TimeLeft = std::numeric_limits<float>::infinity(); // 剩余时间
    // ... 其他播放状态
};
```

## Demo 示例

这是一个最小示例，展示如何定义一个简单的自定义 StateTree 任务基类，该基类能访问 UAF 上下文。

**MyStateTreeTaskBase.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "UAFStateTree/Internal/AnimNextStateTreeTypes.h"
#include "UAFStateTree/Private/UAFStateTreeContext.h"
#include "StateTreeTaskBase.h"
#include "MyStateTreeTaskBase.generated.h"

USTRUCT()
struct FMyTaskInstanceData
{
    GENERATED_BODY()
};

USTRUCT()
struct FMyStateTreeTaskBase : public FStateTreeTaskBase
{
    GENERATED_BODY()

    using FInstanceDataType = FMyTaskInstanceData;

    virtual bool Link(FStateTreeLinker& Linker) override
    {
        Linker.LinkExternalData(ContextHandle);
        return true;
    }

    // 基础任务接口（示例，实际任务需要实现 EnterState/Tick/ExitState 等）
    virtual const UStruct* GetInstanceDataType() const override { return FInstanceDataType::StaticStruct(); }

    // 持有到 UAF 上下文的句柄，用于在任务函数中访问动画混合栈和变量
    TStateTreeExternalDataHandle<FUAFStateTreeContext> ContextHandle;
};
```

## 模块依赖

从源码头文件中对其他模块的引用推断，主要依赖 UAF 核心模块和 StateTree 模块。

| 模块 | 用途 |
|---|---|
| `UAF` | 核心动画框架，提供动画图、变量、混合栈等基础能力。 |
| `StateTree` | 状态树运行时和编辑器框架，提供状态机核心逻辑和节点类型定义。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式日志宏更新为新的宏，属于代码维护。 |
| 2026-04-13 | `6f1ea925` | State Tree: Updated state tree reference struct details to show the display name of the struct rathe | 优化了编辑器 UI，使状态树引用结构的显示更友好。 |
| 2026-04-13 | `5078d880` | Add UAFSharedAssets plugin for content we want to provide that references UAF assets defined in sepa | 添加了配套的共享资产插件，组织项目依赖。 |
| 2026-04-10 | `797a6da6` | Rename GetComponent to GetOrAddComponent to match functionality | 重命名函数以更准确地反映其功能。 |
| 2026-03-31 | `4e41a45f` | Fix crash attempting to manually create UAF ST by hiding UAF ST Schema | 修复了一个崩溃问题，通过隐藏一个内部 Schema 类实现。 |

### 维护评价

该插件仍处于 **实验性阶段**（`IsExperimentalVersion=true`，`EnabledByDefault=false`），表明它尚未稳定，API 可能发生破坏性变更。从提交记录看，近期的更新（截至2026年4月）以小规模的功能改进、UI 优化和 Bug 修复为主，没有重大的新功能提交，表明它处于 **维护中但开发节奏放缓** 的状态。考虑到其创建时间（2025年6月）距今不足两年，且核心功能已基本成型，它主要面向愿意尝试前沿功能的高级用户和内部开发。对于生产项目，建议谨慎评估，或作为学习 UAF 与 StateTree 集成原理的参考。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFStateTree)
- [官方文档]()（暂无）
- [测试用例]()（未在提供的源码路径中发现独立测试文件，可能集成在 UAF 主插件测试中）