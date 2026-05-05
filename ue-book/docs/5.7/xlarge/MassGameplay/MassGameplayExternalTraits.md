# MassGameplay

> Implementation of large-scale agent simulation based on MassEntity

| 属性 | 值 |
|---|---|
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `MassActors` (Runtime), `MassCommon` (Runtime), `MassEQS` (Runtime), `MassGameplayDebug` (Runtime), `MassGameplayEditor` (Runtime), `MassGameplayExternalTraits` (Runtime), `MassGameplayTestSuite` (Runtime), `MassLOD` (Runtime), `MassMovement` (Runtime), `MassMovementEditor` (Runtime), `MassReplication` (Runtime), `MassRepresentation` (Runtime), `MassSignals` (Runtime), `MassSimulation` (Runtime), `MassSmartObjects` (Runtime), `MassSpawner` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MassGameplay) | |

## 用途

MassGameplay 是 Unreal Engine 5 中基于 MassEntity（ECS 框架）构建的大规模智能体（Agent）模拟系统。它并非一个独立的 AI 系统，而是为在 MassEntity 框架下运行的游戏逻辑提供了一套完整的、高性能的实现方案。

该插件的核心价值在于解决了在 ECS 架构下实现复杂游戏逻辑的挑战。它将传统面向对象的游戏功能（如移动、表示、LOD、网络复制、智能对象交互）解构为可组合的“片段”（Fragment）和“处理器”（Processor），从而能够高效地驱动成千上万个实体。它主要服务于需要处理海量单位（如 RTS 游戏中的士兵、开放世界中的 NPC 群体）的场景，通过数据导向的设计来最大化 CPU 缓存利用率和并行处理能力。

## 使用场景

- **大规模即时战略（RTS）游戏**：你需要同时控制和模拟成百上千个单位（士兵、车辆）的移动、战斗和寻路。
- **开放世界游戏中的 NPC 群体模拟**：你需要一个城市或区域中大量 NPC 具有基础的 AI 行为（巡逻、聚集、避障），但又不想为每个 NPC 都运行完整的行为树。
- **需要高性能 AI 的场景**：你的游戏逻辑涉及大量实体的简单决策（例如，根据距离和威胁值选择目标），传统的 Actor 模型性能开销过大。
- **原型开发与压力测试**：你需要快速搭建一个能模拟大量实体交互的场景，用于测试游戏设计或引擎性能。

## 蓝图用法

MassGameplay 的蓝图 API 主要集中在实体的生成、配置和调试上。由于其 ECS 本质，大部分核心逻辑在 C++ 的 Processor 中实现，蓝图更多用于触发和配置。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Spawn Entities` | 根据指定的实体类型（EntityTypes）和数量，在指定位置生成 Mass Entity。 | `AMassSpawner` |
| `Get Mass Entity Manager` | 获取当前世界的 Mass Entity Manager 单例，用于查询和操作实体。 | `UMassEntitySubsystem` (World Subsystem) |
| `Debug Draw Entities` | 在视口中可视化所有 Mass Entity 的位置和状态，用于调试。 | `UMassGameplayDebug` |

### 使用示例（蓝图描述）

1.  **生成实体**：在关卡中放置一个 `MassSpawner` Actor。在它的细节面板中，配置 `EntityTypes` 数组，每个元素定义了一种要生成的实体类型及其数量、生成范围等。运行游戏后，`MassSpawner` 会根据配置批量生成实体。
2.  **查询实体**：通过 `Get Mass Entity Manager` 节点获取管理器，然后可以调用如 `Get Entities With Fragment` 等函数来查询具有特定数据片段（Fragment）的实体集合。
3.  **调试**：在游戏运行时，通过控制台命令或蓝图调用 `Debug Draw Entities`，可以在视口中看到所有实体的点阵分布，帮助确认生成和移动是否符合预期。

## C++ 用法

MassGameplay 的 C++ 用法遵循 MassEntity 的 ECS 模式。开发者主要工作是定义自定义的 Fragment（数据）和 Processor（逻辑）。

### 头文件引入

```cpp
// 核心框架
#include "MassEntityTypes.h"
#include "MassProcessor.h"
#include "MassEntitySubsystem.h"

// 具体功能模块
#include "MassRepresentationTypes.h" // 来自 MassRepresentation
#include "MassMovementTypes.h"      // 来自 MassMovement
```

### 基本用法

**定义自定义 Fragment（数据）**：
```cpp
// MyGameTypes.h
#pragma once
#include "MassEntityTypes.h"

// 一个简单的生命值片段
USTRUCT()
struct FHealthFragment : public FMassFragment
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, Category = "Health")
    float CurrentHealth = 100.0f;

    UPROPERTY(EditAnywhere, Category = "Health")
    float MaxHealth = 100.0f;
};
```

**定义简单的 Processor（逻辑）**：
```cpp
// HealthRegenerationProcessor.h
#pragma once
#include "MassProcessor.h"
#include "MyGameTypes.h"

UCLASS()
class UHealthRegenerationProcessor : public UMassProcessor
{
    GENERATED_BODY()

public:
    UHealthRegenerationProcessor();

protected:
    virtual void ConfigureQueries() override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

private:
    // 查询所有拥有 FHealthFragment 的实体
    FMassEntityQuery EntityQuery;
};

// HealthRegenerationProcessor.cpp
#include "HealthRegenerationProcessor.h"

UHealthRegenerationProcessor::UHealthRegenerationProcessor()
{
    // 设置处理器在模拟阶段执行
    ExecutionFlags = (int32)EProcessorExecutionFlags::All;
    ProcessingPhase = EMassProcessingPhase::PrePhysics; // 在物理模拟前执行
}

void UHealthRegenerationProcessor::ConfigureQueries()
{
    EntityQuery.AddRequirement<FHealthFragment>(EMassFragmentAccess::ReadWrite);
}

void UHealthRegenerationProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    // 遍历所有匹配查询的实体
    EntityQuery.ForEachEntityChunk(EntityManager, Context, [this](FMassExecutionContext& Context)
    {
        // 获取当前 Chunk 中所有实体的 FHealthFragment 数组
        TConstArrayView<FHealthFragment> HealthFragments = Context.GetFragmentView<FHealthFragment>();

        for (int32 i = 0; i < Context.GetNumEntities(); ++i)
        {
            FHealthFragment& Health = const_cast<FHealthFragment&>(HealthFragments[i]); // 需要写权限，所以 const_cast
            // 简单的每秒恢复 1 点生命值（假设处理器每秒执行一次）
            Health.CurrentHealth = FMath::Min(Health.CurrentHealth + 1.0f, Health.MaxHealth);
        }
    });
}
```

### 进阶用法

**组合多个 Fragment 和使用标签（Tag）**：
```cpp
// 定义一个标签，用于标记需要治疗的实体
USTRUCT()
struct FNeedsHealingTag : public FMassTag
{
    GENERATED_BODY()
};

// 在 Processor 中查询同时拥有 FHealthFragment 和 FNeedsHealingTag 的实体
void UHealingProcessor::ConfigureQueries()
{
    EntityQuery.AddRequirement<FHealthFragment>(EMassFragmentAccess::ReadWrite);
    EntityQuery.AddTagRequirement<FNeedsHealingTag>(EMassFragmentPresence::All);
}
```

**使用共享片段（Shared Fragment）存储配置数据**：
```cpp
// 一组实体共享的配置数据
USTRUCT()
struct FUnitConfigSharedFragment : public FMassSharedFragment
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere)
    float HealingRate = 5.0f;
};

// 在 Processor 中访问共享片段
void UHealingProcessor::Execute(...)
{
    EntityQuery.ForEachEntityChunk(EntityManager, Context, [this](FMassExecutionContext& Context)
    {
        // 获取当前 Chunk 关联的共享片段
        const FUnitConfigSharedFragment& Config = Context.GetSharedFragment<FUnitConfigSharedFragment>();
        TConstArrayView<FHealthFragment> HealthFragments = Context.GetFragmentView<FHealthFragment>();

        for (int32 i = 0; i < Context.GetNumEntities(); ++i)
        {
            FHealthFragment& Health = const_cast<FHealthFragment&>(HealthFragments[i]);
            Health.CurrentHealth += Config.HealingRate * Context.GetDeltaTimeSeconds();
        }
    });
}
```

## Demo 示例

以下是一个最小化的自定义“伤害处理器”示例，当实体与特定 Actor 重叠时减少其生命值。

**DamageOnOverlapProcessor.h**
```cpp
#pragma once
#include "MassProcessor.h"
#include "MyGameTypes.h" // 包含 FHealthFragment

UCLASS()
class UDamageOnOverlapProcessor : public UMassProcessor
{
    GENERATED_BODY()

public:
    UDamageOnOverlapProcessor();

protected:
    virtual void ConfigureQueries() override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

private:
    FMassEntityQuery EntityQuery;
    // 存储造成伤害的 Actor 位置（简化示例）
    FVector DamageOrigin;
    float DamageRadius;
    float DamageAmount;
};
```

**DamageOnOverlapProcessor.cpp**
```cpp
#include "DamageOnOverlapProcessor.h"
#include "MassRepresentationTypes.h" // 用于获取实体位置

UDamageOnOverlapProcessor::UDamageOnOverlapProcessor()
{
    ExecutionFlags = (int32)EProcessorExecutionFlags::All;
    ProcessingPhase = EMassProcessingPhase::PrePhysics;
    // 初始化伤害参数（实际项目中应从配置读取）
    DamageOrigin = FVector::ZeroVector;
    DamageRadius = 500.0f;
    DamageAmount = 10.0f;
}

void UDamageOnOverlapProcessor::ConfigureQueries()
{
    // 需要生命值和位置信息
    EntityQuery.AddRequirement<FHealthFragment>(EMassFragmentAccess::ReadWrite);
    EntityQuery.AddRequirement<FMassRepresentationFragment>(EMassFragmentAccess::ReadOnly); // 用于获取位置
}

void UDamageOnOverlapProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    EntityQuery.ForEachEntityChunk(EntityManager, Context, [this](FMassExecutionContext& Context)
    {
        TConstArrayView<FHealthFragment> HealthFragments = Context.GetFragmentView<FHealthFragment>();
        TConstArrayView<FMassRepresentationFragment> RepresentationFragments = Context.GetFragmentView<FMassRepresentationFragment>();

        for (int32 i = 0; i < Context.GetNumEntities(); ++i)
        {
            const FVector& EntityLocation = RepresentationFragments[i].GetTransform().GetLocation();
            float DistanceSq = FVector::DistSquared(EntityLocation, DamageOrigin);

            if (DistanceSq <= FMath::Square(DamageRadius))
            {
                FHealthFragment& Health = const_cast<FHealthFragment&>(HealthFragments[i]);
                Health.CurrentHealth -= DamageAmount;
                // 可以在此处添加死亡逻辑或发送信号
            }
        }
    });
}
```

## 模块依赖

MassGameplay 插件由多个模块组成，每个模块负责特定功能。使用时，你的项目模块需要根据所需功能依赖对应的 MassGameplay 子模块。

| 模块 | 用途 |
|---|---|
| `MassEntity` | 核心 ECS 框架，提供实体、片段、处理器等基础架构。**必须依赖**。 |
| `MassRepresentation` | 处理实体的视觉表示（静态网格、Actor 等）。 |
| `MassMovement` | 处理实体的移动和导航。 |
| `MassSpawner` | 提供实体生成功能。 |
| `MassLOD` | 处理实体的细节层次（LOD）管理。 |
| `MassReplication` | 处理实体的网络复制。 |
| `MassSmartObjects` | 集成智能对象系统，允许实体与场景中的智能对象交互。 |
| `MassSignals` | 提供实体间的信号通信机制。 |

## 维护状态

### 近期更新

- 2025-10-03 99d775716420 [Mass] TypeInfoManager - where we store type traits so that Mass can deduce things about accessing data at runtime. Additionally: * Mass type information used to properly set “is game thread” property of FMassSubsystemRequirements and FMassFragmentRequirements when the subsystem or shared fragment type is used by UStruct pointer. * Removed MassGameplayExternalTraits.h header inclusion (no longer necessary) * Mass subsystems markup changes and type info registration * Added helper functions to Mass subsystem base classes to simplify subsystem type registration * Fixed processor dependency solving not handling subsystem requirements information into consideration. The change is now possible due to MassTypeManager making relevant information available at runtime.
- 2025-09-15 73c74eaf426f Removing redundant include paths: - PublicIncludePaths.Add(ModuleDirectory + "/Public"); - PrivateIncludePaths.Add("<module name>/Private");
- 2025-08-20 94e059bb705e Fixed MassZoneGraphAnnotationProcessor's access to UZoneGraphAnnotationSubsystem

### 维护评价

MassGameplay 是一个**活跃维护**中的实验性插件。

- **创建时间**：约 4 年前（2021年），相对较新。
- **更新频率**：近期（2025年）有持续的实质性更新，主要集中在框架底层优化（如类型信息管理、处理器依赖解析）和代码清理。
- **维护状态**：由 Epic Games 官方维护，是 UE5 MassEntity 框架的核心游戏逻辑层，与引擎版本同步更新。
- **已知限制**：作为实验性功能（`IsExperimentalVersion: true`），其 API 可能在未来版本中发生变化。默认未启用（`EnabledByDefault: false`），需要手动在插件设置中开启。
- **推荐使用**：**推荐**用于需要处理海量实体的新项目。它代表了 UE5 在高性能游戏逻辑方面的未来方向。但由于其实验性，不建议在追求绝对稳定性的已发布项目中作为核心依赖。建议在原型阶段或新项目中积极采用，并关注版本更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MassGameplay)