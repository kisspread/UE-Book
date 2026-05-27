# UAF Mass

> Mass integration for UAF.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | Mass动画集成 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UAFMass` (Runtime), `UAFMassTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-11-10 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFMass) | |

## 用途

这个插件是 **Mass 动画框架 (UAF)** 与 **Mass 实体系统** 之间的集成桥梁。它解决了在 Unreal Engine 的大规模实体系统 (Mass) 中，如何驱动实体执行 UAF 动画逻辑的问题。

简单来说，它让成千上万的 Mass 实体（例如成群的 NPC、敌人）能够共享并运行 UAF 动画系统（如动画蓝图、状态机），从而在实现大规模角色动画的同时保持高性能。它负责管理 UAF 系统在 Mass 实体上的创建、更新和销毁生命周期。

## 使用场景

- **大规模 NPC 群体**：开放世界游戏中，需要数百甚至数千个 NPC 同时拥有动画和行为逻辑（如巡逻、战斗）。
- **战场模拟**：RTS 或策略游戏中大量士兵单位的移动、攻击动画。
- **性能敏感场景**：当使用传统蓝图动画无法满足海量实体的性能要求时，转向基于 Mass 和 UAF 的解决方案。

## 蓝图用法

该插件主要提供在 **Mass 实体模板** 中使用的 Trait 和配置，而不是直接的蓝图节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Mass UAF Trait` | 为 Mass 实体添加 UAF 动画系统支持的 Trait。 | `UMassUAFTrait` |
| `Character Trajectory UAF Setup` | 配置角色轨迹与 UAF 动画变量的映射关系。 | `UCharacterTrajectoryUAFTrait` |
| `Mass Phase Processor` | 一个模块事件依赖性 Trait，使 UAF 模块的事件与指定的 Mass 处理阶段同步。 | `FRigVMTrait_ModuleEventDependency_MassPhaseProcessor` |

### 使用示例（蓝图描述）

1.  **配置实体模板**：在 Mass Entity Data Asset 或 Spawner 中，为你的实体添加 `Mass UAF Trait`。在 Trait 的详情面板中，设置 `Asset` 属性为你想要实体运行的 UAF 系统资产（例如一个动画蓝图）。
2.  **设置轨迹驱动**（可选）：如果实体需要运动轨迹来驱动动画，再添加 `Character Trajectory UAF Setup` Trait，并配置 `PoseVariableName`（如 “Trajectory”）、`SteeringVariableName`（如 “TargetOrientation”）等参数，将 Mass 系统中的轨迹数据映射到 UAF 动画变量上。
3.  **同步事件**（进阶）：在 UAF 模块的依赖性设置中，可以使用 `Mass Phase Processor` 来精确控制 UAF 动画事件在哪个 Mass 处理阶段（如 `PrePhysics`）执行，确保逻辑顺序正确。

## C++ 用法

该插件的核心用法体现在自定义 Mass 处理器（Processor）中，以便与 UAF 系统交互。

### 头文件引入

```cpp
#include "MassEntityTypes.h"
#include "MassUAFComponentFragment.h"
#include "MassUAFFragment.h"
#include "CharacterTrajectoryUAFFragments.h"
```

### 基本用法

在自定义的 Mass 处理器中，通过查询 `FMassUAFFragment` 和 `FCharacterTrajectoryUAFData` 来驱动 UAF 系统。
（来源：`CharacterTrajectoryToUAFProcessor.cpp` 推断）

```cpp
// 在处理器的 ConfigureQueries 中设置查询
void UMyCustomProcessor::ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager)
{
    // 查询拥有 UAF 片段和轨迹数据的实体
    EntityQuery.AddRequirement<FMassUAFFragment>(EMassFragmentAccess::ReadWrite);
    EntityQuery.AddConstSharedRequirement<FCharacterTrajectoryUAFData>();
    // 可能还需要添加位置、速度等片段
    EntityQuery.AddRequirement<FMassMovementFragment>(EMassFragmentAccess::ReadOnly);
    EntityQuery.RegisterWithProcessor(*this);
}

// 在处理器的 Execute 中执行逻辑
void UMyCustomProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    EntityQuery.ForEachEntityChunk(Context, [this](FMassExecutionContext& Context)
    {
        // 获取每个 Chunk 的 UAF 数据
        const FCharacterTrajectoryUAFData& TrajectoryData = Context.GetConstSharedFragment<FCharacterTrajectoryUAFData>();
        
        // 遍历 Chunk 中的每个实体
        const TArrayView<FMassUAFFragment> UAFFragments = Context.GetMutableFragmentView<FMassUAFFragment>();
        const TArrayView<FMassMovementFragment> MovementFragments = Context.GetMutableFragmentView<FMassMovementFragment>();

        for (int32 i = 0; i < Context.GetNumEntities(); ++i)
        {
            FMassUAFFragment& UAFFragment = UAFFragments[i];
            // 检查 UAF 系统是否有效
            if (UAFFragment.SystemReference.IsValid())
            {
                // 使用 MovementFragments[i] 计算轨迹数据
                FVector Trajectory = /* ... */;
                // 将轨迹数据设置到 UAF 系统的变量中
                UAFFragment.SystemReference->SetVariableByName(TrajectoryData.PoseVariableName, FAnimNextDataValueType(Trajectory));
            }
        }
    });
}
```

### 进阶用法

该插件本身提供了完整的处理器实现，展示了如何初始化、更新和销毁 UAF 系统。
（来源：`MassUAFProcessor.h`）

- **`UMassUAFInitializer`**：一个观察者处理器（Observer Processor），在实体首次获得 `FMassUAFFragment` 时触发，负责根据 `Asset` 创建和初始化 UAF 系统实例。
- **`UMassUAFProcessor`**：主处理器，每帧更新所有拥有 `FMassUAFFragment` 的实体的 UAF 系统状态。
- **`UMassUAFDestructor`**：另一个观察者处理器，在实体的 `FMassUAFFragment` 被移除时触发，负责清理和销毁 UAF 系统实例。
- **`UCharacterTrajectoryToUAFProcessor`**：一个具体的处理器示例，将 Mass 实体的轨迹数据转化为 UAF 动画系统变量。

## Demo 示例

一个最小的自定义 Mass 处理器，用于根据实体速度更新 UAF 系统的 “Speed” 变量。

**MySpeedToUAFProcessor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "MassProcessor.h"
#include "MySpeedToUAFProcessor.generated.h"

class UMySpeedToUAFProcessor : public UMassProcessor
{
    GENERATED_BODY()

public:
    UMySpeedToUAFProcessor();

protected:
    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

private:
    FMassEntityQuery EntityQuery;
};
```

**MySpeedToUAFProcessor.cpp**
```cpp
#include "MySpeedToUAFProcessor.h"
#include "MassEntityTypes.h"
#include "MassUAFFragment.h"
#include "MassMovementFragments.h"

UMySpeedToUAFProcessor::UMySpeedToUAFProcessor()
{
    // 设置处理器在 Movement 阶段之后执行
    ExecutionFlags = (int32)EProcessorExecutionFlags::All;
    ExecutionOrder.ExecuteAfter.Add(UE::Mass::ProcessorGroupNames::Movement);
}

void UMySpeedToUAFProcessor::ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager)
{
    // 需要 UAF 片段（可写）和移动片段（只读）
    EntityQuery.AddRequirement<FMassUAFFragment>(EMassFragmentAccess::ReadWrite);
    EntityQuery.AddRequirement<FMassMovementFragment>(EMassFragmentAccess::ReadOnly);
    EntityQuery.RegisterWithProcessor(*this);
}

void UMySpeedToUAFProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    EntityQuery.ForEachEntityChunk(Context, [this](FMassExecutionContext& Context)
    {
        const TArrayView<FMassUAFFragment> UAFFragments = Context.GetMutableFragmentView<FMassUAFFragment>();
        const TConstArrayView<FMassMovementFragment> MovementFragments = Context.GetFragmentView<FMassMovementFragment>();

        for (int32 i = 0; i < Context.GetNumEntities(); ++i)
        {
            const FMassMovementFragment& MoveData = MovementFragments[i];
            FMassUAFFragment& UAFFragment = UAFFragments[i];

            if (UAFFragment.SystemReference.IsValid())
            {
                // 获取速度大小
                const float Speed = MoveData.Velocity.Size();
                // 将速度值设置到 UAF 系统的 “Speed” 变量
                UAFFragment.SystemReference->SetVariableByName(TEXT("Speed"), FAnimNextDataValueType(Speed));
            }
        }
    });
}
```

## 模块依赖

你的项目模块需要依赖以下模块才能使用此插件的功能：

| 模块 | 用途 |
|---|---|
| `UAF` | 核心的 Unreal Animation Framework 模块。 |
| `MassEntity` | Mass 实体系统核心模块，提供实体、片段、处理器等基础设施。 |
| `MassSpawner` | （可选）用于生成 Mass 实体的模块。 |
| `MassCommon` | Mass 系统的通用类型和工具。 |
| `RigVM` | UAF 底层依赖的虚拟机模块，用于变量设置。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-23 | `746b6abb` | Move UAF-Mass trajectory bridge into engine UAFMass plugin | 将角色轨迹到UAF的桥接逻辑从外部代码移入官方插件，作为标准功能。 |
| 2026-04-01 | `58888966` | [MassCore] Move headers to Public/Mass/ subdirectory, strip Mass prefix from filenames | 对Mass核心头文件目录结构进行重构，使其更清晰。 |
| 2026-03-30 | `161605b0` | [Mass] Extract MassCore module from MassEntity | 从MassEntity中拆分出更底层的MassCore模块。 |
| 2026-03-11 | `1d291fa1` | [Mass] Multi-fragment observer support in UMassObserverProcessor | 为Mass观察者处理器增加了对多片段变化的监听支持。 |
| 2026-02-17 | `baf983b4` | [SubmitTool - UAF] Add validators to build and run LowLevelTests for UAF plugins | 增加了UAF相关插件的自动化构建和测试验证流程。 |

### 维护评价

UAFMass 是一个**非常新且处于实验性阶段**的插件。创建于 2025 年底，且最近在 2026 年 4 月仍有实质性更新（功能迁移和代码重构）。从 commit 信息看，它正处于**积极开发和集成**阶段，功能在不断稳定和优化中。

**主要特点与注意事项**：
1.  **实验性**：标记为 `IsExperimentalVersion = true`，且默认不启用 (`EnabledByDefault = false`)，意味着 API 可能发生不兼容的改动。
2.  **活跃维护**：作为 UAF 动画系统和 Mass 实体系统结合的关键部分，是 Epic 官方的重点关注领域，预计会持续更新。
3.  **使用建议**：适用于愿意跟踪引擎前沿功能、且有大规模动画需求的项目。在生产环境中使用需谨慎，并做好应对 API 变更的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFMass)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFMass/Tests)