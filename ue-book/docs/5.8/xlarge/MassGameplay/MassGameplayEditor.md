# MassGameplay

> Implementation of large-scale agent simulation based on MassEntity（基于 MassEntity 的大规模智能体模拟实现）

| 属性 | 值 |
|---|---|
| 中文名 | 大规模玩法 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `MassActors` (Runtime), `MassCharacterTrajectory` (Runtime), `MassCommon` (Runtime), `MassEQS` (Runtime), `MassGameplayDebug` (Runtime), `MassGameplayEditor` (Runtime), `MassGameplayExternalTraits` (Runtime), `MassGameplayTestSuite` (Runtime), `MassLOD` (Runtime), `MassMovement` (Runtime), `MassMovementEditor` (Runtime), `MassReplication` (Runtime), `MassRepresentation` (Runtime), `MassSimulation` (Runtime), `MassSmartObjects` (Runtime), `MassSpawner` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay) | |

## 用途

MassGameplay 是虚幻引擎 5 中构建大规模实体（智能体）模拟的核心插件。它基于 MassEntity 框架，旨在解决当场景中存在成千上万个 AI 代理（如 NPC、人群、生物）时，传统基于 Actor 的 Actor 系统所带来的性能瓶颈。

该插件提供了一整套模块化系统，用于高效地生成、移动、表示（视觉表现）、LOD（细节层次）管理、复制以及调试这些大规模实体。它的核心目标是将游戏逻辑（Gameplay）与底层的实体数据高效结合，使得开发者可以构建支持海量单位的 RTS 游戏、城市模拟、开放世界 AI 等复杂项目。

## 使用场景

-   **大规模 RTS/MOBA 游戏**：需要管理数百甚至数千个单位，要求极致的寻路、战斗和状态更新性能。
-   **城市模拟与人群系统**：模拟城市中大量市民、车辆的日常行为和移动。
-   **开放世界游戏中的分布式 AI**：在玩家视线外远处，需要大量 AI 维持低开销的“模拟”。
-   **任何需要批量处理逻辑相似的大量实体的游戏场景**。

## 蓝图用法

MassGameplay 的大部分高级功能需要通过 C++ 与 MassEntity 框架交互。但在 Editor 工具和一些 Spawner 类中暴露了关键的蓝图接口。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SpawnEntities` | 从配置的模板批量生成 Mass 实体 | `UMassEntitySpawnerSubsystem` |
| `SetMovementStyle` | 为实体设置移动模式（如漫步、奔跑） | `UMassMovementFunctionLibrary` |

### 使用示例（蓝图描述）

1.  **批量生成实体**：
    在关卡中放置一个 `AMassSpawner` Actor。在其 Details 面板中，配置 “Entity Config” 资产（定义实体应包含哪些 Fragment 和 Trait）。在游戏蓝图中，获取 `MassEntitySpawnerSubsystem`，调用 `SpawnEntities` 节点，传入 Spawner Actor 和要生成的数量，即可在 Spawner 的位置批量生成实体。

2.  **控制移动**：
    获取需要控制移动的实体的 Entity Handle，然后调用 `SetMovementStyle` 蓝图函数库节点，传入 Handle 和想要的移动风格枚举值（如 `Walk`, `Run`），即可改变其移动行为。

## C++ 用法

### 头文件引入

```cpp
// 包含核心的 MassEntity 框架
#include "MassEntitySubsystem.h"
#include "MassEntityView.h"

// 包含 MassGameplay 的通用定义
#include "MassCommonTypes.h"
#include "MassEntityTemplate.h"

// 包含特定功能的头文件，例如移动
#include "MassMovementTypes.h"
```

### 基本用法

以下是创建一个简单 Mass 实体并修改其数据的基本流程（概念性示例，具体实现取决于项目架构）：

```cpp
// 假设已在你的 GameMode 或某个 Manager 类中持有 World 和 MassSubsystem 指针
// UWorld* World;
// UMassEntitySubsystem* MassSubsystem;

// 1. 获取一个有效的实体模板 (UMassEntityTemplate)。这通常从蓝图资产加载或通过代码构建。
UMassEntityTemplate* EntityTemplate = ...; // 获取或创建模板

// 2. 生成实体
FMassEntityHandle NewEntity = MassSubsystem->CreateEntity(*EntityTemplate);

// 3. 通过 EntityView 安全地访问和修改实体数据（Fragment）
FMassEntityView EntityView(MassSubsystem->GetEntityManager(), NewEntity);

// 4. 获取或添加一个 Fragment，例如一个自定义的 `FMyHealthFragment`
if (EntityView.HasFragment<FMyHealthFragment>())
{
    FMyHealthFragment& HealthFragment = EntityView.GetFragment<FMyHealthFragment>();
    HealthFragment.Health = 100.0f;
}
```

*（基本用法概念基于 MassEntity 标准模式）*

### 进阶用法

结合 `MassMovement` 和 `MassRepresentation` 模块，实现一个可移动且可见的实体：

```cpp
// ...接续上面的代码

// 5. 为实体添加移动能力（如果模板未包含）
if (!EntityView.HasFragment<FMassVelocityFragment>())
{
    MassSubsystem->AddFragmentToEntity<FMassVelocityFragment>(NewEntity);
}

// 6. 设置初始速度
FMassVelocityFragment& VelocityFragment = EntityView.GetFragment<FMassVelocityFragment>();
VelocityFragment.Value = FVector(100.0f, 0.0f, 0.0f); // 设置一个初始X方向速度

// 7. 确保实体有表示（例如，一个静态网格体实例或一个 Actor）
// 这通常通过模板中的 Trait 或 Fragment（如 FMassRepresentationFragment）来管理。
// 框架会根据其 FMassRepresentationFragment 中的设置，自动选择使用 ISM (Instanced Static Mesh) 或 Actor 作为视觉表现。
```

## Demo 示例

一个定义实体模板并生成实体的最小示例片段：

```cpp
// MyMassAgentManager.h
#pragma once
#include "GameFramework/Actor.h"
#include "MassEntityTypes.h"
#include "MyMassAgentManager.generated.h"

class UMassEntitySubsystem;
class UMassEntityTemplate;

UCLASS()
class AMyMassAgentManager : public AActor
{
    GENERATED_BODY()
public:
    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere)
    TObjectPtr<UMassEntityTemplate> AgentTemplate;

    UPROPERTY(EditAnywhere)
    int32 SpawnCount = 1000;

private:
    UPROPERTY()
    TObjectPtr<UMassEntitySubsystem> MassSubsystem;
};
```

```cpp
// MyMassAgentManager.cpp
#include "MyMassAgentManager.h"
#include "MassEntitySubsystem.h"
#include "Engine/World.h"

void AMyMassAgentManager::BeginPlay()
{
    Super::BeginPlay();

    MassSubsystem = UWorld::GetSubsystem<UMassEntitySubsystem>(GetWorld());
    if (!MassSubsystem || !AgentTemplate)
    {
        return;
    }

    // 批量生成实体
    FMassSpawnData SpawnData;
    SpawnData.Template = AgentTemplate;
    SpawnData.Count = SpawnCount;
    SpawnData.SpawnLocation = GetActorLocation();

    MassSubsystem->SpawnEntities(SpawnData);
}
```

## 模块依赖

MassGameplay 是一个**内容插件**，其核心运行时逻辑依赖于 `MassEntity` 插件。在你的项目中使用它，需要在 `Build.cs` 中添加依赖：

```csharp
// 你的模块的 Build.cs
PublicDependencyModuleNames.AddRange(new string[]
{
    "MassEntity",      // 核心的 ECS 框架
    "MassGameplay",    // 本次插件的通用逻辑
    // 根据你使用的具体功能，可能还需要其他模块，例如：
    // "MassSpawner", "MassMovement", "MassRepresentation" 等
});
```

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `07ab5d30` | Revert earlier change to MassAgentComponent. | 回滚了对 MassAgentComponent 组件的先前改动。 |
| 2026-05-13 | `751e48da` | [MassRepresentation] Wait for actor readiness before switching off ISM | 在关闭实例化静态网格体（ISM）前，现在会等待相关 Actor 就绪。 |
| 2026-05-13 | `022b39e0` | Fix handling of non-puppet actors in Mass crowds | 修复了在人群模拟中对非傀儡 Actor 的处理问题。 |
| 2026-05-12 | `7c7f835b` | [MassRepresentation] Cluster of pre-existing bugs in `TMassLODCalculator`'s per-viewer LOD path. | 修复了 LOD 计算器中针对每个观察者计算 LOD 路径上的一系列既有 Bug。 |
| 2026-05-12 | `f59bc340` | [Mass representation] Switched two manually calculated `bDoKeepActorExtraFrame` to use the new UE::M | 将两个手动计算的 `bDoKeepActorExtraFrame` 标志替换为使用新的引擎接口。 |

### 维护评价

MassGameplay 是虚幻引擎 5 实现大规模 AI 的**核心框架之一**，处于**活跃维护**状态。

- **优势**：Epic Games 官方持续投入开发，近期更新频繁（最近一次更新距今仅数天），且修复内容涉及核心的表示、LOD 和移动系统，说明其仍在不断优化和完善。
- **注意**：`.uplugin` 中 `IsExperimentalVersion` 为 `true`，且 `EnabledByDefault` 为 `false`。这意味着该插件被官方标记为实验性功能，**API 可能发生破坏性更改**，不建议在追求长期稳定性的商业项目核心部分直接深度依赖，但在开发原型、内部项目或技术研究中可以放心使用。
- **推荐**：对于任何希望实现大规模实体模拟的项目，MassGameplay 都是必须研究和使用的核心技术栈。虽然处于实验阶段，但其成熟度和官方支持度很高，是同类问题的官方解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay/Source/MassGameplayTestSuite) (MassGameplayTestSuite 模块)