# MassGameplay

> Implementation of large-scale agent simulation based on MassEntity（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 大规模游戏玩法 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、测试资源） |
| 模块 | `MassActors` (Runtime), `MassCharacterTrajectory` (Runtime), `MassCommon` (Runtime), `MassEQS` (Runtime), `MassGameplayDebug` (Runtime), `MassGameplayEditor` (Runtime), `MassGameplayExternalTraits` (Runtime), `MassGameplayTestSuite` (Runtime), `MassLOD` (Runtime), `MassMovement` (Runtime), `MassMovementEditor` (Runtime), `MassReplication` (Runtime), `MassRepresentation` (Runtime), `MassSimulation` (Runtime), `MassSmartObjects` (Runtime), `MassSpawner` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay) | |

## 用途

MassGameplay 是 UE5 大规模实体模拟框架的核心游戏玩法实现层。它建立在底层 ECS 框架 MassEntity 之上，旨在解决如何将成千上万甚至更多的实体（如 NPC、生物、物体）高效地表示、模拟、渲染和同步到游戏世界中的问题。

它不仅仅是“让很多东西动起来”，而是提供了一整套解决方案来处理大规模实体带来的性能挑战，包括：
- **实体-Actor 映射**：智能地管理实体与其在游戏中 Actor 表示（或视觉表示，如 ISM/HISM）之间的切换。
- **性能自适应（LOD）**：根据距离和重要性动态调整实体的更新频率、移动计算和视觉表现。
- **高效移动**：为海量实体提供优化的移动和轨迹计算。
- **网络同步**：专门为大规模实体设计的、带宽高效的复制策略。
- **游戏玩法集成**：提供与 Smart Objects、EQS 等系统的集成，让大规模实体能参与更复杂的游戏逻辑。

简而言之，如果你想在游戏中模拟大规模群体（人群、军队、生态系统），而不是处理少量高精度的独立对象，那么 MassGameplay 就是 Epic 提供的官方解决方案。

## 使用场景

- **RTS/模拟经营游戏**：你需要控制数百甚至上千个单位、工人或车辆。
- **开放世界中的动态群体**：城市中的市民、野外的动物群落、战场上的士兵。
- **生存游戏**：需要模拟大量低智能生物（如僵尸、昆虫）的生态系统。
- **演出/过场动画**：需要渲染庞大的背景人群或军队方阵。
- **任何需要“数量即质量”游戏体验的场景**，重点是整体模拟的规模和行为规律，而非单个实体的精细控制。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Mass Simulation Subsystem` | 获取当前世界的 Mass 模拟子系统实例，是访问大部分 Mass 功能的入口 | `UBlueprintLibrary` |
| `Register Dynamic Processor` | 运行时动态注册一个自定义处理器（Processor）到模拟管线中 | `UMassSimulationSubsystem` |
| `Unregister Dynamic Processor` | 移除一个动态注册的处理器 | `UMassSimulationSubsystem` |
| `Pause Simulation` | 暂停所有实体的处理器执行，但相位（Phase）转换仍继续 | `UMassSimulationSubsystem` |
| `Resume Simulation` | 恢复模拟执行 | `UMassSimulationSubsystem` |
| `Is Simulation Started` | 检查 Mass 模拟是否已经启动 | `UMassSimulationSubsystem` |
| `Is Simulation Paused` | 检查模拟当前是否处于暂停状态 | `UMassSimulationSubsystem` |
| `Get On Simulation Paused` | 获取模拟暂停时的委托，用于事件驱动逻辑 | `UMassSimulationSubsystem` |
| `Get On Simulation Resumed` | 获取模拟恢复时的委托 | `UMassSimulationSubsystem` |

### 使用示例（蓝图描述）

1.  **启动与监控模拟**：
    *   在某个游戏模式或管理器 Actor 的 `BeginPlay` 事件中，使用 `Get Mass Simulation Subsystem` 节点获取子系统。
    *   可以绑定 `Get On Simulation Started` 委托来监听模拟何时开始。

2.  **运行时调整行为**：
    *   创建一个继承自 `UMassProcessor` 的蓝图类（或 C++ 类），在其中编写自定义的实体逻辑（例如，特殊的群体聚集行为）。
    *   在游戏中，当玩家触发某个事件（如技能、区域进入），通过子系统节点 `Register Dynamic Processor` 将这个自定义处理器临时加入模拟管线。
    *   当事件结束或需要移除时，调用 `Unregister Dynamic Processor`。

3.  **调试与优化**：
    *   使用 `Is Simulation Started` 和 `Is During Mass Processing`（C++ 节点）检查模拟状态，用于在 HUD 上显示调试信息。
    *   通过配置 `UMassSimulationSettings`（在项目设置中）来调整 Actor 生成/销毁的时间切片预算，以平衡性能和流畅度。

## C++ 用法

### 头文件引入

```cpp
#include "MassSimulationSubsystem.h"
#include "MassProcessor.h"
// 其他根据需要引入的 Mass 模块头文件，如 MassRepresentationTypes.h
```

### 基本用法

```cpp
// 在某个 UGameInstanceSubsystem 或 Actor 中
void AMyManager::BeginPlay()
{
    Super::BeginPlay();
    if (UWorld* World = GetWorld())
    {
        // 获取 Mass 模拟子系统
        UMassSimulationSubsystem* MassSimulation = World->GetSubsystem<UMassSimulationSubsystem>();
        if (MassSimulation)
        {
            // 监听模拟开始事件
            MassSimulation->GetOnSimulationStarted().AddUObject(this, &AMyManager::OnMassSimulationStarted);

            // 绑定处理器执行阶段事件
            MassSimulation->GetOnProcessingPhaseStarted(EMassProcessingPhase::PostPhysics).AddUObject(
                this, &AMyManager::OnPostPhysicsPhaseStarted);
        }
    }
}

void AMyManager::OnMassSimulationStarted(UWorld* World)
{
    UE_LOG(LogTemp, Log, TEXT("Mass Simulation has started in world: %s"), *World->GetName());
}

void AMyManager::OnPostPhysicsPhaseStarted(const float DeltaSeconds, const EMassProcessingPhase Phase)
{
    // 在物理后处理阶段每帧做一些自定义逻辑，例如更新某个外部 UI
}
```

### 进阶用法

```cpp
// 动态注册自定义处理器
void AMyManager::EnableCustomFlockingBehavior(bool bEnable)
{
    UMassSimulationSubsystem* MassSimulation = GetWorld()->GetSubsystem<UMassSimulationSubsystem>();
    if (!MassSimulation) return;

    static UMassProcessor* FlockingProcessor = nullptr;
    if (bEnable)
    {
        if (!FlockingProcessor)
        {
            // 创建处理器实例（通常作为单例或从对象池获取）
            FlockingProcessor = NewObject<UMyCustomFlockingProcessor>(GetTransientPackage());
            FlockingProcessor->Initialize(/* ... */);
        }
        MassSimulation->RegisterDynamicProcessor(*FlockingProcessor);
    }
    else
    {
        if (FlockingProcessor)
        {
            MassSimulation->UnregisterDynamicProcessor(*FlockingProcessor);
        }
    }
}
```

## Demo 示例

以下是一个最小化示例，展示如何创建一个自定义 Mass 处理器并将其注册到模拟中。该处理器会将所有带有特定标签的实体速度降低一半。

**自定义处理器头文件 (MySlowDownProcessor.h)**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "MassProcessor.h"
#include "MySlowDownProcessor.generated.h"

UCLASS()
class UMySlowDownProcessor : public UMassProcessor
{
    GENERATED_BODY()

public:
    UMySlowDownProcessor();

protected:
    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

private:
    FMassEntityQuery EntityQuery;
};
```

**自定义处理器源文件 (MySlowDownProcessor.cpp)**
```cpp
#include "MySlowDownProcessor.h"
#include "MassMovementFragments.h"
#include "MassEntityTypes.h"
#include "MassCommonFragments.h"

UMySlowDownProcessor::UMySlowDownProcessor()
{
    // 设置执行阶段，例如在 PrePhysics（移动计算前）
    ExecutionFlags = static_cast<int32>(EProcessorExecutionFlags::AllNetModes);
    // 将此处理器放入预定义的处理阶段组
    ProcessingPhase = EMassProcessingPhase::PrePhysics;
}

void UMySlowDownProcessor::ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager)
{
    // 配置查询：寻找拥有“Slow”标签片段和速度片段的实体
    EntityQuery.AddRequirement<FMassVelocityFragment>(EMassFragmentAccess::ReadWrite);
    EntityQuery.AddTagRequirement<FMassSlowTag>(EMassFragmentPresence::All);
}

void UMySlowDownProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    // 遍历所有匹配的实体，并执行逻辑
    EntityQuery.ForEachEntityChunk(EntityManager, Context, [&](FMassExecutionContext& MyContext)
    {
        // 获取该区块（chunk）内所有实体的速度片段数组
        TConstArrayView<FMassVelocityFragment> Velocities = MyContext.GetFragmentView<FMassVelocityFragment>();
        // 遍历并修改速度
        for (FMassVelocityFragment& Velocity : Velocities)
        {
            Velocity.Value *= 0.5f; // 速度减半
        }
    });
}
```

**使用该处理器的 Actor 头文件 (MySlowField.h)**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MySlowField.generated.h"

class UMassSimulationSubsystem;
class UMySlowDownProcessor;

UCLASS()
class AMySlowField : public AActor
{
    GENERATED_BODY()

public:
    AMySlowField();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    UPROPERTY()
    UMySlowDownProcessor* SlowProcessor;

    FDelegateHandle SimulationStartedHandle;

    void OnSimulationStarted(UWorld* World);
    void RegisterProcessor();
};
```

**使用该处理器的 Actor 源文件 (MySlowField.cpp)**
```cpp
#include "MySlowField.h"
#include "MassSimulationSubsystem.h"
#include "MySlowDownProcessor.h"
#include "Engine/World.h"

AMySlowField::AMySlowField()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMySlowField::BeginPlay()
{
    Super::BeginPlay();

    if (UWorld* World = GetWorld())
    {
        if (UMassSimulationSubsystem* MassSub = World->GetSubsystem<UMassSimulationSubsystem>())
        {
            // 如果模拟已启动，立即注册处理器
            if (MassSub->IsSimulationStarted())
            {
                RegisterProcessor();
            }
            else
            {
                // 否则，等待模拟启动
                SimulationStartedHandle = MassSub->GetOnSimulationStarted().AddUObject(this, &AMySlowField::OnSimulationStarted);
            }
        }
    }
}

void AMySlowField::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (UMassSimulationSubsystem* MassSub = GetWorld()->GetSubsystem<UMassSimulationSubsystem>())
    {
        if (SlowProcessor)
        {
            MassSub->UnregisterDynamicProcessor(*SlowProcessor);
        }
        MassSub->GetOnSimulationStarted().Remove(SimulationStartedHandle);
    }

    Super::EndPlay(EndPlayReason);
}

void AMySlowField::OnSimulationStarted(UWorld* World)
{
    // 模拟开始后，注册我们的处理器
    RegisterProcessor();
    // 清理委托
    if (UWorld* MyWorld = GetWorld())
    {
        if (UMassSimulationSubsystem* MassSub = MyWorld->GetSubsystem<UMassSimulationSubsystem>())
        {
            MassSub->GetOnSimulationStarted().Remove(SimulationStartedHandle);
        }
    }
}

void AMySlowField::RegisterProcessor()
{
    if (!SlowProcessor)
    {
        SlowProcessor = NewObject<UMySlowDownProcessor>(this);
    }
    if (UMassSimulationSubsystem* MassSub = GetWorld()->GetSubsystem<UMassSimulationSubsystem>())
    {
        MassSub->RegisterDynamicProcessor(*SlowProcessor);
        UE_LOG(LogTemp, Log, TEXT("Custom SlowDown Processor registered with Mass Simulation."));
    }
}
```

## 模块依赖

要使用 MassGameplay 插件的功能，你的项目模块通常需要依赖以下一个或多个模块，具体取决于你使用的子功能。

| 模块 | 用途 |
|---|---|
| `MassEntity` | 底层 ECS 框架，提供实体、片段（Fragments）、处理器等核心概念 |
| `MassCommon` | 通用片段和类型定义，如位置、速度、标签等 |
| `MassSpawner` | 实体生成和管理，包括 `UMassSpawner` 和生成器（Spawner）相关类 |
| `MassRepresentation` | 管理实体在游戏世界中的视觉表示（Actor、ISM、HISM 等） |
| `MassMovement` | 提供移动、跟随、转向等移动相关处理器和片段 |
| `MassLOD` | 实体的细节层次（LOD）管理和距离计算 |
| `MassReplication` | 为大规模实体提供网络复制支持 |
| `MassSmartObjects` | 将 Smart Objects 系统与 Mass 实体连接起来 |
| `MassSimulation` | 模拟子系统、相位管理和配置设置（本汇总页核心模块） |

*注：未列出常见的 `Core`, `CoreUObject`, `Engine` 等基础模块。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `07ab5d30` | Revert earlier change to MassAgentComponent. | 回滚了之前对 MassAgentComponent 的修改 |
| 2026-05-13 | `751e48da` | [MassRepresentation] Wait for actor readiness before switching off ISM | 修复了 Representation 模块，在关闭 ISM 表示前等待 Actor 准备就绪 |
| 2026-05-13 | `022b39e0` | Fix handling of non-puppet actors in Mass crowds | 修复了处理 Mass 群组中非傀儡 Actor 的问题 |
| 2026-05-12 | `7c7f835b` | [MassRepresentation] Cluster of pre-existing bugs in `TMassLODCalculator`'s per-viewer LOD path. | 修复了 LOD 计算器在按查看者计算 LOD 路径中存在的多个遗留 Bug |
| 2026-05-12 | `f59bc340` | [Mass representation] Switched two manually calculated `bDoKeepActorExtraFrame` to use the new UE::M | 将两处手动计算 `bDoKeepActorExtraFrame` 的逻辑改为使用新的 UE::Mass 命名空间下的工具函数 |

### 维护评价

MassGameplay 插件**处于活跃维护状态**。

- **创建时间**：2021 年 9 月，至今约 5 年，属于框架级核心插件。
- **近期更新**：最近一周内有多次实质性更新（截至 2026 年 5 月 14 日），主要集中在 `MassRepresentation` 和 `MassLOD` 模块，修复 Bug 和优化 Actor 表示切换的可靠性。这表明 Epic 仍在持续投入和改进此框架。
- **状态**：`.uplugin` 中标记为 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`，这明确表示它仍是一个**实验性**功能。开发者在使用时应意识到其 API 和功能在未来版本中可能会有变动。
- **已知限制**：作为实验性功能，文档相对较少，且部分功能（如网络复制）的成熟度和用法可能需要在实际项目中进一步验证。
- **推荐**：**推荐用于对大规模实体模拟有明确需求的项目**。尽管是实验性状态，但它是 UE5 官方支持的唯一的大规模实体模拟解决方案，社区和 Epic 自身的使用案例（如 CitySample）已经证明了其可行性和性能。建议在项目早期进行技术验证，并密切关注版本更新日志。

**警告**：此插件标记为实验性 (`IsExperimentalVersion: true`)，请在生产环境中谨慎使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay)
- 官方文档：暂无 (DocsURL 为空)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay/Source/MassGameplayTestSuite) （位于 `MassGameplayTestSuite` 模块）