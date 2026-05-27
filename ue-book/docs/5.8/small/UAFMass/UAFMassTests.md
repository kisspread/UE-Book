# UAF Mass

> Mass integration for UAF.

| 属性 | 值 |
|---|---|
| 中文名 | UAF动画框架Mass集成 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UAFMass` (Runtime) |
| 实验性 | ⚚ 是 |
| 创建时间 | 2025-11-10 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFMass) | |

## 用途
此插件旨在将 Unreal Animation Framework (UAF) 的能力与 Mass Entity 处理系统集成。其核心作用是解决在使用 MassEntity 系统处理海量实体（如大量 NPC、生物群或动态物体）时，动画播放的性能与同步问题。它为 Mass 实体提供了一种高效的、与 Mass 处理流程紧密集成的动画驱动方案，取代了传统的单个 Actor 上动画组件的模式，适用于需要高性能动画的场景。

## 使用场景
- 你在使用 MassEntity 系统创建成千上万的动态实体（如人群、植被、群聚生物），并且需要为它们统一、高效地播放或驱动动画。
- 你需要让动画事件（如脚步声、攻击判定）能够精确地与 Mass 处理框架（如移动、伤害计算）协同工作。
- 你希望自定义动画在 Mass 处理流水线中的具体执行阶段，以实现更优的性能调度。

## 蓝图用法
由于该插件处于早期实验阶段，且主要面向底层系统集成，其公开的蓝图接口可能有限。建议通过查阅最新源码（`UAFMass` 模块下的 `Public` 头文件）来获取可用的 `UFUNCTION(BlueprintCallable)` 和 `UPROPERTY(BlueprintReadWrite)`。

### 核心节点
（基于插件功能推断的可能接口）

| 节点 | 说明 | 所在类 |
|---|---|---|
| （待源码确认） | （待源码确认） | （待源码确认） |

### 使用示例（蓝图描述）
（由于是底层集成，主要使用场景可能在 C++ 代码或通过配置 Mass 处理器的子类实现。蓝图使用示例待官方文档或更稳定的 API 发布后补充。）

## C++ 用法

### 头文件引入
```cpp
#include "UAFMass.h"
```

### 基本用法
该插件的核心是提供 UAF 动画与 Mass 实体之间的桥接。一个基本用法可能涉及创建一个自定义的 `UMassProcessor` 来驱动实体上的动画片段。
（具体代码示例需参考插件的测试用例或引擎内其他集成代码，此处基于功能描述进行示意）

```cpp
// 假设存在一个 UAFMass 相关的 Mass Fragment 或 Processor
// 这段代码仅为示意架构，非实际可编译代码
#include "MassProcessor.h"
#include "MassEntityTypes.h"
// ... 可能需要的 UAF 头文件

class UMyAnimDrivenProcessor : public UMassProcessor
{
public:
    UMyAnimDrivenProcessor();

protected:
    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

private:
    // 定义查询，例如查找拥有动画状态片段和移动目标片段的实体
    FMassEntityQuery EntityQuery;
};

// 在处理器的 Execute 函数中，可能会调用 UAFMass 提供的工具函数来更新或驱动动画。
```

### 进阶用法
插件很可能提供了将 UAF 的动画更新循环与 Mass 的处理阶段（Phase）进行事件依赖绑定的功能。从首次提交信息 “Add Mass Processing Phase event dependency option in UAF” 可以推断。
进阶用法可能包括：
1.  注册自定义的 Mass 处理阶段。
2.  将动画系统的更新（如骨骼更新、动画蓝图计算）设置为依赖某个特定的 Mass 阶段（如 `PrePhysics` 或 `PostPhysics`），以确保正确的执行顺序。

```cpp
// 伪代码示例：注册一个自定义阶段并建立依赖
// FMassProcessingPhase MyAnimationPhase = ...;
// FProcessingPhaseDependency AnimationDependency;
// AnimationDependency.Phase = MyAnimationPhase;
// // 假设 UAFMass 提供了 API 来设置此依赖
// UUAFMassSubsystem::Get()->SetAnimationUpdateDependency(AnimationDependency);
```

## Demo 示例
一个典型的最小用法可能涉及在你的项目中启用该插件，并创建一个继承自 `UMassProcessor` 的类，在其中配置实体查询和执行逻辑。

**MyAnimProcessor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "MassProcessor.h"
#include "MyAnimProcessor.generated.h"

// 假设需要查询的片段
struct FAnimStateFragment;
struct FTransformFragment;

UCLASS()
class MYPROJECT_API UMyAnimProcessor : public UMassProcessor
{
    GENERATED_BODY()

public:
    UMyAnimProcessor();

protected:
    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

private:
    FMassEntityQuery EntityQuery;
};
```

**MyAnimProcessor.cpp**
```cpp
#include "MyAnimProcessor.h"
// 引入所需的 UAFMass 和 Mass 头文件
// #include "MassCommonFragments.h"
// #include "UAFMassContexts.h"

UMyAnimProcessor::UMyAnimProcessor()
{
    ExecutionFlags = (int32)EProcessorExecutionFlags::All;
    // 根据 UAFMass 文档或示例设置处理阶段
    // ProcessingPhase = ...; 
    bRequiresGameThreadExecution = false;
}

void UMyAnimProcessor::ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager)
{
    EntityQuery.AddRequirement<FTransformFragment>(EMassFragmentAccess::ReadWrite);
    EntityQuery.AddRequirement<FAnimStateFragment>(EMassFragmentAccess::ReadWrite);
    // 根据 UAFMass 的集成方式，可能需要添加其他特定查询
    // EntityQuery.AddSharedRequirement<...>(...);
}

void UMyAnimProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    // 遍历所有符合查询的实体
    EntityQuery.ForEachEntityChunk(EntityManager, Context, [this](FMassExecutionContext& Context)
    {
        const TArrayView<FTransformFragment> TransformList = Context.GetMutableFragmentView<FTransformFragment>();
        const TArrayView<FAnimStateFragment> AnimStateList = Context.GetMutableFragmentView<FAnimStateFragment>();

        for (int32 i = 0; i < Context.GetNumEntities(); ++i)
        {
            FTransformFragment& Transform = TransformList[i];
            FAnimStateFragment& AnimState = AnimStateList[i];

            // 这里是核心逻辑，使用 UAFMass 提供的 API 或工具来根据游戏逻辑更新 AnimState，
            // 然后驱动 Transform 或动画播放。
            // 例如：更新动画状态，计算根运动等。
            // UAFMassUtils::UpdateAnimationState(AnimState, ...);
            // AnimState.RootMotionDelta = ...;
            // Transform.GetMutableTransform().AppendTranslation(AnimState.RootMotionDelta);
        }
    });
}
```

## 模块依赖
从插件的功能描述和首次提交信息推断，其 `Build.cs` 文件很可能包含以下依赖：
| 模块 | 用途 |
|---|---|
| `MassEntity` | Mass 实体管理的核心模块，用于创建和查询实体。 |
| `MassGameplay` | Mass 游戏玩法框架，提供处理器、片段等基础设施。 |
| `UAF` (或其他相关UAF模块) | 提供底层的动画框架功能。 |
*（以上为根据插件功能推断的依赖，实际依赖请查阅 `UAFMass.Build.cs` 文件）*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-23 | `746b6abb` | Move UAF-Mass trajectory bridge into engine UAFMass plugin | 将UAF与Mass的轨迹桥接功能移入此插件 |
| 2026-04-01 | `58888966` | [MassCore] Move headers to Public/Mass/ subdirectory, strip Mass prefix from filenames | 重构MassCore头文件目录结构，移除文件名前缀 |
| 2026-03-30 | `161605b0` | [Mass] Extract MassCore module from MassEntity | 从MassEntity中提取出MassCore模块 |
| 2026-03-11 | `1d291fa1` | [Mass] Multi-fragment observer support in UMassObserverProcessor | 为Mass观察者处理器增加多片段支持 |
| 2026-02-17 | `baf983b4` | [SubmitTool - UAF] Add validators to build and run LowLevelTests for UAF plugins | 为UAF插件添加低层级测试的构建和运行验证器 |

### 维护评价
- **创建时间**: 2025年11月，是一个非常年轻的插件。
- **近期活动**: 在2026年2月至4月期间有连续的提交，内容涉及核心功能开发（轨迹桥接）和底层架构重构（Mass模块拆分、目录调整）。这表明插件正在**积极开发**中。
- **活跃维护**: 是。近期提交均为功能性和结构性更新，而非简单的编译修复。
- **已知限制**: 作为 `Experimental` 且 `IsExperimentalVersion: true` 的插件，API 不稳定，随时可能发生破坏性更改。默认未启用 (`EnabledByDefault: false`)，需要用户手动在项目中启用。
- **推荐使用**: **不推荐用于生产环境**。适合对 MassEntity 系统和 UAF 有深入研究、且愿意跟进最新实验性功能的开发者进行学习和原型开发。等待其移出 `Experimental` 分类并稳定 API 后再考虑用于正式项目。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFMass)
- [官方文档]（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFMass/Tests) （UAFMassTests 模块所在路径）