# MassGameplay

> Implementation of large-scale agent simulation based on MassEntity

| 属性 | 值 |
|---|---|
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、配置资产） |
| 模块 | `MassActors` (Runtime), `MassCommon` (Runtime), `MassEQS` (Runtime), `MassGameplayDebug` (Runtime), `MassGameplayEditor` (Runtime), `MassGameplayExternalTraits` (Runtime), `MassGameplayTestSuite` (Runtime), `MassLOD` (Runtime), `MassMovement` (Runtime), `MassMovementEditor` (Runtime), `MassReplication` (Runtime), `MassRepresentation` (Runtime), `MassSignals` (Runtime), `MassSimulation` (Runtime), `MassSmartObjects` (Runtime), `MassSpawner` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 👴 老古董（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MassGameplay) | |

## 用途

MassGameplay 是 Unreal Engine MassEntity (ECS) 框架在游戏玩法层面的具体应用和扩展。它解决的核心问题是：**如何将基于 MassEntity 的大规模、高性能实体模拟与传统的 Actor 游戏对象系统无缝集成**。

MassEntity 本身是一个底层的、面向数据的实体组件系统（ECS），专注于数据布局和批量处理。MassGameplay 在此之上构建了一套完整的游戏玩法层，提供了以下关键能力：

1.  **Actor 与 Mass 实体的桥梁**：通过 `UMassAgentComponent` 和 `UMassAgentSubsystem`，允许将一个 Actor（如 NPC、载具）与一个 Mass 实体关联。Actor 可以作为实体的“前端”表现，而 Mass 实体则承载其核心数据和逻辑。
2.  **数据同步**：提供了一系列 `Translator`（翻译器），用于在 Actor 的组件（如 `USceneComponent`, `UCharacterMovementComponent`）和 Mass 实体的 Fragment（数据片段）之间同步变换、速度、朝向等数据。
3.  **大规模实体管理**：通过 `UMassSpawnerSubsystem` 和 `UMassActorSpawnerSubsystem`，支持基于模板的、高性能的实体批量生成、销毁和池化管理。
4.  **游戏玩法集成**：将 Mass 实体与 UE 的其他游戏系统（如 EQS 环境查询、SmartObjects、行为树、LOD 管理、网络复制）连接起来，使 ECS 实体能够参与复杂的游戏逻辑。
5.  **可视化与调试**：提供了 `MassRepresentation` 模块，用于根据实体的 LOD 等级动态切换其表现形式（如从完整 Actor 切换到静态网格体或完全隐藏），并包含调试工具。

简而言之，MassGameplay 让开发者能够利用 ECS 的性能优势来处理成千上万的游戏对象（如人群、子弹、粒子），同时保留与现有 Actor 蓝图工作流和游戏系统的兼容性。

## 使用场景

-   **大规模 NPC 模拟**：你需要在一个开放世界中模拟成千上万的市民、士兵或生物，它们有简单的 AI 行为（巡逻、聚集、逃跑）。使用 MassGameplay 可以高效管理它们的移动、状态和表现。
-   **RTS 或塔防游戏**：游戏中存在大量可控制的单位（士兵、坦克、防御塔）。MassGameplay 可以处理单位的批量移动、攻击指令和状态同步，性能远优于为每个单位创建独立 Actor。
-   **弹幕或投射物系统**：需要同时处理成百上千颗子弹或魔法飞弹的碰撞、移动和生命周期。MassEntity 的批量处理非常适合此类场景。
-   **动态环境物体**：如森林中的树木、草地、可破坏的物体，它们需要根据玩家距离动态加载、卸载或切换表现形式（LOD）。
-   **需要网络同步的大规模实体**：`MassReplication` 模块为 Mass 实体提供了网络复制支持，适用于多人游戏中的大规模单位同步。

## 蓝图用法

MassGameplay 的蓝图接口主要集中在实体配置、组件管理和子系统交互上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RegisterAgentComponent` | 将一个 `UMassAgentComponent` 注册到 Mass 模拟系统，为其创建对应的 Mass 实体。 | `UMassAgentSubsystem` |
| `UnregisterAgentComponent` | 从 Mass 系统中注销一个 Agent 组件，并销毁其关联的实体。 | `UMassAgentSubsystem` |
| `UpdateAgentComponent` | 当 Agent 组件的属性（如 Fragment 组成）发生变化时，通知系统更新实体。 | `UMassAgentSubsystem` |
| `AddEntityTagToActor` | 查找与给定 Actor 关联的 Mass 实体，并为其添加一个 Tag。 | `UE::MassActor` (蓝图函数库) |
| `RemoveEntityTagFromActor` | 查找与给定 Actor 关联的 Mass 实体，并移除其一个 Tag。 | `UE::MassActor` (蓝图函数库) |
| `GetEntityHandle` | 获取 `UMassAgentComponent` 当前关联的 Mass 实体句柄。 | `UMassAgentComponent` |
| `SetEntityHandle` | 手动设置 `UMassAgentComponent` 关联的实体句柄（高级用法）。 | `UMassAgentComponent` |
| `PausePuppet` | 暂停或恢复一个“傀儡”（Puppet）Actor 的 Mass 数据同步。 | `UMassAgentComponent` |

### 使用示例（蓝图描述）

1.  **创建一个可被 Mass 管理的 Actor**：
    *   创建一个 Actor 蓝图。
    *   添加一个 `UMassAgentComponent`。
    *   在 `UMassAgentComponent` 的详情面板中，通过 `EntityConfig` 属性指定一个 `UMassEntityConfigAsset`，该资产定义了实体的初始 Fragment 和 Trait 组成。
    *   当这个 Actor 被生成时，`UMassAgentComponent` 会自动尝试向 `UMassAgentSubsystem` 注册，从而创建一个 Mass 实体。

2.  **在运行时动态修改实体**：
    *   获取目标 Actor 的 `UMassAgentComponent` 引用。
    *   调用 `AddEntityTagToActor` 节点，传入 Actor 引用和一个自定义的 `FMassTag` 结构体类型（例如 `FMyCustomTag`）。这会为该 Actor 对应的 Mass 实体添加一个标签，可能触发相关的处理器逻辑。
    *   调用 `RemoveEntityTagFromActor` 可以移除标签。

3.  **使用 Trait 配置同步行为**：
    *   在 `UMassEntityConfigAsset` 中，可以添加各种 Trait（如 `UMassAgentCapsuleCollisionSyncTrait`, `UMassAgentMovementSyncTrait`）。
    *   这些 Trait 会自动配置相应的 `Translator`，实现 Actor 组件与 Mass Fragment 之间的数据双向同步。例如，`UMassAgentMovementSyncTrait` 会确保 Actor 的移动组件速度与 Mass 实体的 `FMassVelocityFragment` 保持同步。

## C++ 用法

### 头文件引入

```cpp
#include "MassAgentComponent.h"
#include "MassAgentSubsystem.h"
#include "MassActorSubsystem.h"
#include "MassActorHelper.h"
```

### 基本用法

以下示例展示了如何在 C++ 中与 MassGameplay 交互。

```cpp
// 假设我们有一个 AMyCharacter 类，它包含一个 UMassAgentComponent。
// 在某个游戏逻辑中，我们想给这个角色对应的 Mass 实体添加一个“受伤”标签。

#include "MassAgentComponent.h"
#include "MassActorHelper.h"
#include "MyCustomTags.h" // 包含自定义的 FMassTag 定义

void AMyCharacter::ApplyDamageEffect()
{
    // 方法1：通过 Actor 辅助函数（推荐）
    // 这会自动查找关联的实体并添加标签。
    UE::MassActor::AddEntityTagToActor<FInjuredTag>(*this);

    // 方法2：直接通过组件操作（更底层）
    if (UMassAgentComponent* AgentComp = FindComponentByClass<UMassAgentComponent>())
    {
        if (FMassEntityHandle EntityHandle = AgentComp->GetEntityHandle())
        {
            // 需要获取 EntityManager 来操作实体
            UWorld* World = GetWorld();
            if (UMassAgentSubsystem* AgentSubsystem = World->GetSubsystem<UMassAgentSubsystem>())
            {
                // AgentSubsystem 内部持有 EntityManager 的引用
                // 但通常推荐使用更高层的API，如上面的 AddEntityTagToActor
            }
        }
    }
}
```

### 进阶用法：自定义 Trait 和 Processor

MassGameplay 的强大之处在于其可扩展性。你可以创建自定义的 Trait 来定义实体的行为，并创建 Processor 来处理这些行为。

```cpp
// 1. 定义一个自定义 Fragment（数据）
USTRUCT()
struct FHealthFragment : public FMassFragment
{
    GENERATED_BODY()
    float CurrentHealth = 100.f;
    float MaxHealth = 100.f;
};

// 2. 定义一个自定义 Tag（标签，用于标识实体）
USTRUCT()
struct FCanTakeDamageTag : public FMassTag
{
    GENERATED_BODY()
};

// 3. 创建一个 Trait，用于将 Fragment 和 Tag 添加到实体模板
UCLASS()
class UHealthTrait : public UMassEntityTraitBase
{
    GENERATED_BODY()
protected:
    virtual void BuildTemplate(FMassEntityTemplateBuildContext& BuildContext, const UWorld& World) const override
    {
        // 添加数据片段
        BuildContext.AddFragment<FHealthFragment>();
        // 添加标签
        BuildContext.AddTag<FCanTakeDamageTag>();
    }
};

// 4. 创建一个 Processor，用于处理带有特定标签的实体
UCLASS()
class UDamageProcessor : public UMassProcessor
{
    GENERATED_BODY()
public:
    UDamageProcessor();
protected:
    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

    FMassEntityQuery EntityQuery;
};

// .cpp 实现
UDamageProcessor::UDamageProcessor()
{
    // 设置处理器在模拟的哪个阶段执行
    ExecutionOrder.ExecuteInGroup = UE::Mass::ProcessorGroupNames::Behavior;
    ProcessingPhase = EMassProcessingPhase::PrePhysics;
}

void UDamageProcessor::ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager)
{
    // 配置查询：查找同时拥有 FHealthFragment 和 FCanTakeDamageTag 的实体
    EntityQuery.AddRequirement<FHealthFragment>(EMassFragmentAccess::ReadWrite);
    EntityQuery.AddTagRequirement<FCanTakeDamageTag>(EMassFragmentPresence::All);
    EntityQuery.RegisterWithProcessor(*this);
}

void UDamageProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    // 批量处理所有匹配的实体
    EntityQuery.ForEachEntityChunk(Context, [this](FMassExecutionContext& Context)
    {
        // 获取当前 Chunk 中所有实体的 FHealthFragment 数据视图
        TConstArrayView<FHealthFragment> HealthList = Context.GetFragmentView<FHealthFragment>();

        for (int32 i = 0; i < Context.GetNumEntities(); ++i)
        {
            FHealthFragment& Health = Context.GetMutableFragmentView<FHealthFragment>()[i];
            // 执行伤害逻辑...
            Health.CurrentHealth -= 10.f;
            if (Health.CurrentHealth <= 0.f)
            {
                // 可以在这里添加死亡逻辑，例如销毁实体或添加死亡标签
            }
        }
    });
}
```

## Demo 示例

一个完整的、可编译的最小示例，展示如何创建一个自定义的“可受伤”实体 Trait 和对应的伤害处理器。

**MyDamageSystem.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "MassEntityTraitBase.h"
#include "MassProcessor.h"
#include "MyDamageSystem.generated.h"

// 自定义数据片段
USTRUCT()
struct FHealthFragment : public FMassFragment
{
    GENERATED_BODY()
    float CurrentHealth = 100.f;
};

// 自定义标签
USTRUCT()
struct FVulnerableTag : public FMassTag
{
    GENERATED_BODY()
};

// 自定义 Trait，用于将上述 Fragment 和 Tag 添加到实体
UCLASS()
class UMyVulnerableTrait : public UMassEntityTraitBase
{
    GENERATED_BODY()
protected:
    virtual void BuildTemplate(FMassEntityTemplateBuildContext& BuildContext, const UWorld& World) const override;
};

// 自定义处理器，用于每帧减少生命值
UCLASS()
class UDecayHealthProcessor : public UMassProcessor
{
    GENERATED_BODY()
public:
    UDecayHealthProcessor();
protected:
    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

    FMassEntityQuery EntityQuery;
};
```

**MyDamageSystem.cpp**
```cpp
#include "MyDamageSystem.h"

void UMyVulnerableTrait::BuildTemplate(FMassEntityTemplateBuildContext& BuildContext, const UWorld& World) const
{
    BuildContext.AddFragment<FHealthFragment>();
    BuildContext.AddTag<FVulnerableTag>();
}

UDecayHealthProcessor::UDecayHealthProcessor()
{
    // 在行为阶段，物理模拟之前执行
    ExecutionOrder.ExecuteInGroup = UE::Mass::ProcessorGroupNames::Behavior;
    ProcessingPhase = EMassProcessingPhase::PrePhysics;
}

void UDecayHealthProcessor::ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager)
{
    EntityQuery.AddRequirement<FHealthFragment>(EMassFragmentAccess::ReadWrite);
    EntityQuery.AddTagRequirement<FVulnerableTag>(EMassFragmentPresence::All);
    EntityQuery.RegisterWithProcessor(*this);
}

void UDecayHealthProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    // 批量处理所有拥有 FHealthFragment 和 FVulnerableTag 的实体
    EntityQuery.ForEachEntityChunk(Context, [](FMassExecutionContext& Context)
    {
        // 获取可写的 Fragment 视图
        TArrayView<FHealthFragment> HealthFragments = Context.GetMutableFragmentView<FHealthFragment>();

        for (FHealthFragment& Health : HealthFragments)
        {
            // 每帧减少 1 点生命值
            Health.CurrentHealth -= 1.0f * Context.GetDeltaTimeSeconds();
            // 注意：实际项目中应添加死亡判断和清理逻辑
        }
    });
}
```

## 模块依赖

要使用 MassGameplay 插件，你的项目模块通常需要依赖以下核心模块：

| 模块 | 用途 |
|---|---|
| `MassEntity` | MassGameplay 的基石，提供 ECS 核心框架（EntityManager, Fragment, Archetype）。 |
| `MassEntityEditor` | 提供编辑器支持，用于配置实体模板、Trait 等。 |
| `MassSpawner` | 提供实体生成和池化管理的核心功能。 |
| `MassCommon` | 提供 Mass 系统通用的类型、Fragment 和工具。 |
| `MassSignals` | 提供实体间的信号通信机制。 |
| `SmartObjectsModule` | 用于将 Mass 实体与 SmartObject 系统集成。 |
| `GameplayBehaviorSmartObjectsModule` | 为 SmartObject 提供基于 GameplayBehavior 的交互逻辑。 |

**注意**：由于 MassGameplay 包含多个子模块，具体依赖取决于你使用的功能。例如，使用网络复制功能需要依赖 `MassReplication` 模块，使用 LOD 功能需要依赖 `MassLOD` 模块。

## 维护状态

### 近期更新

-   `457eba2e5782` (2025-10-03) PR #13332: Added std::is_trivially_copyable to the CFragment concept. (为 CFragment 概念添加了 std::is_trivially_copyable 检查)
-   `320972e0deb2` (2025-09-15) [MassGameplay] Fix crash when mass representation actor is destroyed while mass simulation is active. Remove checks in the representation API that can happen in this case and added reasonable default return values. Fixed teardown crash in MassAgentComponent. (修复了当 Mass 表现 Actor 在模拟活跃时被销毁导致的崩溃)
-   `8cded7886207` (2025-08-20) [Mass] removed code deprecated in 5.4 (移除了在 5.4 版本中已弃用的代码)

### 维护评价

MassGameplay 是 Unreal Engine MassEntity 框架的核心游戏玩法扩展，由 Epic Games 官方维护。

-   **创建时间**：2021年9月，已有约4年历史。
-   **维护状态**：**活跃维护中**。从近期提交记录看，团队仍在积极修复 Bug、优化性能并清理技术债务。最近的提交集中在概念完善、崩溃修复和代码清理上。
-   **实验性状态**：插件的 `.uplugin` 文件中 `IsExperimentalVersion` 标记为 `true`，且默认未启用 (`EnabledByDefault: false`)。这表明 Epic 仍将其视为实验性功能，API 和功能在未来版本中可能发生重大变更。
-   **推荐度**：**推荐用于新项目，但需谨慎**。如果你正在开发一个需要大规模实体模拟的新项目（如大型开放世界、RTS、MMO），MassGameplay 是官方提供的、与引擎深度集成的首选方案。然而，由于其“实验性”状态，你需要准备好应对 API 变动，并密切关注引擎更新日志。对于已上线的项目，引入此系统需要充分的测试和评估。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MassGameplay)