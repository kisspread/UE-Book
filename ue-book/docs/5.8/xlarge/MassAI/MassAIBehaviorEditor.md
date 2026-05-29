# MassAI

> AI-specific functionality extending MassGameplay（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 大规模AI |
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源） |
| 模块 | `MassAIBehavior` (Runtime), `MassAIBehaviorEditor` (Runtime), `MassAIDebug` (Runtime), `MassAIReplication` (Runtime), `MassAITestSuite` (Runtime), `MassNavMeshNavigation` (Runtime), `MassNavigation` (Runtime), `MassNavigationEditor` (Runtime), `MassZoneGraphNavigation` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/MassAI) | |

## 用途

MassAI 是 MassGameplay 框架在人工智能领域的专用扩展。它并非一个通用的行为树或状态机插件，而是旨在解决**大规模实体**（如人群、军队、生态系统）的 AI 问题。核心目标是让数千甚至数万个 AI 代理能够高效、协调地共享行为逻辑、导航和感知数据。

这个插件存在是因为传统的单个 `ACharacter` + `UBehaviorTree` 的模式在面对海量 AI 时性能开销巨大。MassAI 通过 ECS (实体组件系统) 架构，将 AI 的行为（行为树）、导航（寻路）、感知（视线、声音）等作为“处理器”附加到实体数据片段上，由 Mass 系统统一、批量地调度执行，从而实现性能的指数级提升。

## 使用场景

- 你在开发一个开放世界游戏，需要成千上万的平民 NPC 自然地在城市中生活、行走、互动。
- 你正在制作一个大规模即时战略（RTS）游戏，需要海量的单位智能地寻路、攻击、执行战术命令。
- 你的游戏包含庞大的生态系统，需要大量生物基于简单的规则（如觅食、躲避捕食者）自主行动。
- 你需要复用和组合海量实体的 AI 逻辑，例如所有“平民”共享一个行为树模板，但每个实体的具体决策根据其“职业”、“心情”等数据片段动态变化。

## 蓝图用法

MassAI 作为底层框架，其核心逻辑在 C++ 中实现，蓝图暴露的接口主要用于配置和调试。大部分 AI 行为逻辑（如行为树）仍需在 C++ 中定义处理器。

### 核心节点

| 肹点 | 说明 | 所在类 |
|---|---|---|
| `UMassAISubsystem` | 用于查询和管理 Mass AI 实例的子系统 | `UMassAISubsystem` |
| `UMassLookAtSetting` | 用于配置实体视线（Look At）行为的全局设置数据资产 | `UMassLookAtSetting` |
| `UMassZoneGraphAnnotationSubsystem` | 用于查询 Zone Graph 导航标注信息的子系统 | `UMassZoneGraphAnnotationSubsystem` |

### 使用示例（蓝图描述）

1.  **配置视线行为**：创建一个 `UMassLookAtSetting` 数据资产（Data Asset），在其中定义不同优先级的“兴趣点”（如对话、枪声）及其对应的视线行为参数。然后，在游戏模式的 `BeginPlay` 中，获取 `MassAISubsystem`，并调用类似 `SetLookAtDefaultSetting` 的函数将此配置应用为全局默认。
2.  **查询导航信息**：在蓝图中，可以通过 `MassZoneGraphAnnotationSubsystem` 查询某个位置所属的 Zone Graph 区块（如“人行道”、“车行道”）或获取到附近特定类型区域的路径，这些信息可以用来辅助调试或实现基于区域的游戏逻辑。

## C++ 用法

### 头文件引入

```cpp
#include "MassAIBehavior.h"
#include "MassNavigation.h"
```

### 基本用法：创建 AI 实体与添加处理器

从测试套件中可以看到，首先需要创建包含必要数据片段的实体，然后通过“处理器”（Processor）来驱动其行为。
*（来源：Source/MassAITestSuite/Tests/MassAIProcessorTest.cpp）*

```cpp
// 假设你已经有了 Mass 实体管理器和片段集合
UMassEntitySubsystem* EntitySubsystem = GetWorld()->GetSubsystem<UMassEntitySubsystem>();
check(EntitySubsystem);

// 1. 定义一个实体模板（Archetype），它包含了 AI 所需的核心数据片段
FMassArchetypeCompositionDescriptor Composition;
Composition.Add<FTransformFragment>(); // 位置、旋转、缩放
Composition.Add<FMassMoveTargetFragment>(); // 移动目标（导航所需）
Composition.Add<FMassLookAtFragment>(); // 视线状态（Look At 所需）

// 2. 基于模板创建一个实体
FMassEntityHandle EntityHandle = EntitySubsystem->CreateEntity(Composition);

// 3. 设置实体的初始位置
FTransformFragment* TransformFragment = EntitySubsystem->GetFragmentDataPtr<FTransformFragment>(EntityHandle);
if (TransformFragment)
{
    TransformFragment->GetMutableTransform().SetLocation(FVector(0.f, 0.f, 0.f));
}

// 4. 通过 Mass 世界订阅处理器。处理器会在每个 Tick 批量处理所有具有相关片段的实体。
// 例如，MassNavigation 模块提供的移动处理器会读取 FMassMoveTargetFragment 并更新 FTransformFragment。
// 你通常需要在游戏模块或子系统中“启用”或“构建”这些处理器。
```

### 进阶用法：集成行为树与自定义处理器

MassAI 的核心是其行为树处理器 (`UMassBehaviorTreeProcessor`)，它将传统的 Mass 数据片段与 UE 行为树连接起来。
*（综合自模块结构及公共头文件推断）*

```cpp
// 1. 创建自定义数据片段，用于在实体和行为树之间传递数据
USTRUCT()
struct FMyAITag : public FMassTag
{
    GENERATED_BODY()
};

USTRUCT()
struct FMyAIDesireFragment : public FMassFragment
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FName CurrentGoal; // 例如：”GatherResource”
};

// 2. 创建一个自定义处理器，用于在行为树外更新这些片段
UCLASS()
class UMyAIDesireProcessor : public UMassProcessor
{
    GENERATED_BODY()
public:
    UMyAIDesireProcessor();

    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override;
    virtual void Execute(UMassEntitySubsystem& EntitySubsystem, FMassExecutionContext& Context) override;

private:
    // 查询：寻找带有我的自定义Tag和片段的实体
    FMassEntityQuery EntityQuery;
};
```

```cpp
// .cpp 文件中
UMyAIDesireProcessor::UMyAIDesireProcessor()
{
    ExecutionOrder.ExecuteBefore.Add(UE::Mass::Processor::Name::BehaviorTree); // 在行为树处理器之前执行
    bAutoRegisterWithProcessorPhases = true;
}

void UMyAIDesireProcessor::ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager)
{
    EntityQuery.AddRequirement<FMyAIDesireFragment>(EMassFragmentAccess::ReadWrite);
    EntityQuery.AddRequirement<FMyAITag>(EMassFragmentPresence::All);
}

void UMyAIDesireProcessor::Execute(UMassEntitySubsystem& EntitySubsystem, FMassExecutionContext& Context)
{
    // 批量处理所有符合条件的实体
    EntityQuery.ForEachEntityChunk(EntitySubsystem, Context, [this](FMassExecutionContext& Context)
    {
        // 在这里，你可以根据游戏逻辑（如附近的资源点、威胁）批量更新 FMyAIDesireFragment 中的 CurrentGoal。
        // 之后，行为树处理器会读取这个片段，驱动相应的行为。
    });
}
```

## Demo 示例

一个最小的、配置了 MassAI 基础行为（移动和视线）的实体创建示例。

**MyMassAIEntity.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "MassEntityTypes.h"
#include "MyMassAIEntity.generated.h"

UCLASS()
class UMyMassAISubsystem : public UTickableWorldSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Tick(float DeltaTime) override;
    virtual TStatId GetStatId() const override;

private:
    // 用于存储我们创建的 AI 实体句柄
    TArray<FMassEntityHandle> SpawnedEntities;
};
```

**MyMassAIEntity.cpp**
```cpp
#include "MyMassAIEntity.h"
#include "MassEntitySubsystem.h"
#include "MassMovementFragments.h" // FMassMoveTargetFragment
#include "MassLookAtFragments.h"   // FMassLookAtFragment
#include "MassRepresentationFragments.h" // 用于可视化（可选）

void UMyMassAISubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);

    // 获取实体子系统
    UMassEntitySubsystem* EntitySubsystem = GetWorld()->GetSubsystem<UMassEntitySubsystem>();
    if (!EntitySubsystem) return;

    // 定义实体模板
    FMassArchetypeCompositionDescriptor Composition;
    Composition.Add<FTransformFragment>();
    Composition.Add<FMassMoveTargetFragment>();
    Composition.Add<FMassLookAtFragment>();
    // 如果需要可视化的代理表示（例如 Crowd），可以添加：
    // Composition.Add<FMassRepresentationFragment>();

    // 批量创建 10 个 AI 实体
    for (int32 i = 0; i < 10; ++i)
    {
        FMassEntityHandle EntityHandle = EntitySubsystem->CreateEntity(Composition);
        SpawnedEntities.Add(EntityHandle);

        // 设置初始位置，沿 X 轴分布
        FTransformFragment* TransformFragment = EntitySubsystem->GetFragmentDataPtr<FTransformFragment>(EntityHandle);
        if (TransformFragment)
        {
            TransformFragment->GetMutableTransform().SetLocation(FVector(i * 100.f, 0.f, 0.f));
        }
    }
}

void UMyMassAISubsystem::Tick(float DeltaTime)
{
    // 在这个简化的示例中，Tick 可以留空。
    // 真正的 AI 行为（移动、视线）由 MassNavigation 和 MassAIBehavior 模块中注册的处理器自动驱动。
    // 你可以在这里编写一些全局逻辑，例如随机给某个实体分配一个新的移动目标。
    UMassEntitySubsystem* EntitySubsystem = GetWorld()->GetSubsystem<UMassEntitySubsystem>();
    if (!EntitySubsystem || SpawnedEntities.Num() == 0) return;

    // 随机选择一个实体，给它一个新的移动目标
    int32 RandomIndex = FMath::RandRange(0, SpawnedEntities.Num() - 1);
    FMassEntityHandle& RandomEntity = SpawnedEntities[RandomIndex];

    FMassMoveTargetFragment* MoveTarget = EntitySubsystem->GetFragmentDataPtr<FMassMoveTargetFragment>(RandomEntity);
    if (MoveTarget)
    {
        // 设置一个世界范围内的随机目标点
        MoveTarget->Center = FMath::VRand() * FVector(1000.f, 1000.f, 0.f);
        MoveTarget->DesiredSpeed = 300.f;
    }
}

TStatId UMyMassAISubsystem::GetStatId() const
{
    RETURN_QUICK_DECLARE_CYCLE_STAT(UMyMassAISubsystem, STATGROUP_Tickables);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MassGameplay` | MassAI 的基础，提供核心实体框架和游戏玩法集成 |
| `MassEntity` | ECS 核心，提供实体、片段、处理器的基础定义 |
| `AIModule` | 传统 AI 系统，MassAI 的行为树处理器可能与之交互 |
| `NavigationSystem` | 寻路系统，MassAI 的导航处理器可能依赖其网格数据 |
| `GameplayTasks` | 用于集成 Gameplay 任务系统 |
| `ZoneGraph` | 为 MassZoneGraphNavigation 模块提供路径和区域数据 |

**注意**：上表只列出了相对独特的依赖。标准依赖如 Core, CoreUObject, Engine 等已省略。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `8e83e6bf` | Remove use of INFINITY to fix compile error on latest Windows SDK | 移除 `INFINITY` 宏以修复最新 Windows SDK 下的编译错误。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下，双精度常量截断为浮点数产生的警告。 |
| 2026-05-12 | `328c7999` | [Mass] PR #14001: Fix Mass debugger running with invalid entity | [Mass] 修复当实体无效时 Mass 调试器运行的问题。 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复格式化函数中使用的作用域枚举可能导致输出乱码的问题。 |
| 2026-04-15 | `4b250a9d` | [RewindDebugger] | [RewindDebugger] 相关改动（具体不明）。 |

### 维护评价

- **活跃状态**：**维护中**。最近一个月内有数次提交，但均属于编译兼容性修复（如修复特定 SDK、消除警告）和调试器 bug 修复，没有重大新功能引入。
- **年龄**：插件创建于 2021 年，历史约 5 年，作为 UE5 原生实验性功能，其迭代周期与引擎大版本发布同步。
- **评价**：作为 MassGameplay 框架的关键 AI 组件，其代码随着引擎主版本持续维护。`IsExperimentalVersion=true` 和 `EnabledByDefault=false` 标志表明它仍被视为实验性功能，API 和架构可能在后续版本中发生变化。**推荐用于学习和在允许实验性功能的项目中进行大规模 AI 的可行性验证。在正式商业项目中全面采用前，需谨慎评估其稳定性与长期支持承诺。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/MassAI)
- [官方文档]() （暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/MassAI/Source/MassAITestSuite)