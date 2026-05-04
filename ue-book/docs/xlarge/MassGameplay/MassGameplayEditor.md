# MassGameplay

> Implementation of large-scale agent simulation based on MassEntity（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、测试资源） |
| 模块 | `MassActors` (Runtime), `MassCommon` (Runtime), `MassEQS` (Runtime), `MassGameplayDebug` (Runtime), `MassGameplayEditor` (Runtime), `MassGameplayExternalTraits` (Runtime), `MassGameplayTestSuite` (Runtime), `MassLOD` (Runtime), `MassMovement` (Runtime), `MassMovementEditor` (Runtime), `MassReplication` (Runtime), `MassRepresentation` (Runtime), `MassSignals` (Runtime), `MassSimulation` (Runtime), `MassSmartObjects` (Runtime), `MassSpawner` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MassGameplay) | |

## 用途

MassGameplay 是基于 MassEntity 框架构建的大规模智能体（Agent）模拟系统。它解决的核心问题是：**当游戏中需要同时模拟成千上万个实体（如 NPC、载具、子弹、环境物体）时，传统的 Actor 模型因内存开销大、Tick 函数调用频繁而无法满足性能需求。**

该插件提供了一套完整的、面向数据的解决方案，用于：
1.  **高效生成与管理**：通过 `MassSpawner` 模块，可以基于模板（Entity Template）批量生成和销毁大量实体。
2.  **行为与逻辑**：通过 `MassMovement`、`MassSignals`、`MassSmartObjects` 等模块，为实体提供移动、信号响应、与游戏世界交互（如使用 SmartObject）的能力。
3.  **视觉与网络**：通过 `MassRepresentation` 和 `MassReplication` 模块，处理实体的视觉表现（如 Actor 代理、ISM 渲染）和网络同步。
4.  **性能优化**：通过 `MassLOD` 模块，根据距离和重要性动态调整实体的更新频率和细节层次，确保大规模模拟的流畅性。

它本质上是一个**游戏玩法层**，将 MassEntity 的底层 ECS（实体组件系统）能力，封装成更易于游戏设计师和程序员使用的、面向游戏逻辑的模块。

## 使用场景

- **大规模 RTS 游戏**：你需要模拟数百甚至数千个士兵、载具单位，它们需要寻路、攻击、响应命令。
- **开放世界游戏**：你需要填充大量背景 NPC，它们有简单的巡逻、交互行为，但不需要复杂的 AI。
- **弹幕射击游戏**：你需要同时管理成千上万颗子弹或投射物，每颗都有独立的轨迹和碰撞检测。
- **模拟经营游戏**：你需要模拟大量顾客、员工等实体，他们有各自的状态和简单行为。
- **任何需要“数量级”提升实体模拟性能的场景**：当你发现传统 Actor 的数量成为性能瓶颈时，MassGameplay 是 Epic 官方提供的首选解决方案。

## 蓝图用法

MassGameplay 的蓝图 API 主要分布在 `MassSpawner`、`MassMovement`、`MassRepresentation` 等运行时模块中。`MassGameplayEditor` 模块主要提供编辑器工具，不直接暴露运行时蓝图节点。

### 核心节点（来自其他运行时模块）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SpawnEntities` | 根据实体模板和生成数据，在指定位置批量生成实体。 | `AMassSpawner` |
| `SetMovementParameters` | 设置实体的移动参数，如最大速度、转向力。 | `UMassMovementFunctionLibrary` |
| `AddFragment` | 向实体动态添加一个数据片段（Fragment）。 | `UMassEntityFunctionLibrary` |
| `GetEntityHandle` | 通过 Actor 或其他标识获取对应的实体句柄。 | `UMassEntityFunctionLibrary` |

### 使用示例（蓝图描述）

1.  **生成一群 NPC**：
    *   在场景中放置一个 `MassSpawner` Actor。
    *   在其细节面板中，指定一个 `MassEntityConfig`（实体配置资产），该资产定义了要生成的实体由哪些 Trait（特征，如移动、视觉、AI）组成。
    *   设置生成数量、生成区域形状（如盒体、球体）。
    *   调用 `SpawnEntities` 节点，即可在区域内批量生成实体。

2.  **让实体移动到目标点**：
    *   获取目标实体的句柄（Entity Handle）。
    *   调用 `SetMovementParameters` 节点，为该实体设置移动目标位置（`TargetLocation`）。
    *   `MassMovement` 处理器会自动驱动实体向目标移动。

## C++ 用法

MassGameplay 的 C++ 用法核心在于理解其基于 Trait 和 Fragment 的组合模式。以下示例展示了如何创建一个自定义的“可受伤”Trait。

### 头文件引入

```cpp
#include "MassEntityTraitBase.h"
#include "MassEntityTypes.h"
#include "MassMovementFragments.h" // 示例：使用移动相关的Fragment
```

### 基本用法：定义一个自定义 Fragment 和 Trait

**1. 定义数据片段 (Fragment)**
```cpp
// MyHealthFragment.h
#pragma once
#include "MassEntityTypes.h"
#include "MyHealthFragment.generated.h"

USTRUCT()
struct FMyHealthFragment : public FMassFragment
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, Category = "Health")
    float CurrentHealth = 100.0f;

    UPROPERTY(EditAnywhere, Category = "Health")
    float MaxHealth = 100.0f;
};
```

**2. 定义特征 (Trait)**
```cpp
// MyHealthTrait.h
#pragma once
#include "MassEntityTraitBase.h"
#include "MyHealthTrait.generated.h"

UCLASS(meta=(DisplayName="Health"))
class MYPROJECT_API UMyHealthTrait : public UMassEntityTraitBase
{
    GENERATED_BODY()

protected:
    virtual void BuildTemplate(FMassEntityTemplateBuildContext& BuildContext, const UWorld& World) const override
    {
        // 向实体模板中添加我们定义的 HealthFragment
        BuildContext.AddFragment<FMyHealthFragment>();

        // 可以在这里设置 Fragment 的初始值
        FMyHealthFragment& HealthFragment = BuildContext.GetFragment<FMyHealthFragment>();
        HealthFragment.MaxHealth = 100.0f;
        HealthFragment.CurrentHealth = 100.0f;
    }
};
```

**3. 创建一个处理逻辑的处理器 (Processor)**
```cpp
// MyHealthProcessor.h
#pragma once
#include "MassProcessor.h"
#include "MyHealthProcessor.generated.h"

UCLASS()
class MYPROJECT_API UMyHealthProcessor : public UMassProcessor
{
    GENERATED_BODY()

public:
    UMyHealthProcessor();

protected:
    virtual void ConfigureQueries() override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

private:
    FMassEntityQuery EntityQuery;
};
```

```cpp
// MyHealthProcessor.cpp
#include "MyHealthProcessor.h"
#include "MyHealthFragment.h"

UMyHealthProcessor::UMyHealthProcessor()
{
    // 设置处理器执行阶段，例如在模拟阶段
    ExecutionOrder.ExecuteInGroup = UE::Mass::ProcessorGroupNames::Behavior;
}

void UMyHealthProcessor::ConfigureQueries()
{
    // 配置查询：寻找同时拥有 HealthFragment 和 MovementTag 的实体
    EntityQuery.AddRequirement<FMyHealthFragment>(EMassFragmentAccess::ReadWrite);
    EntityQuery.AddTagRequirement<FMassMovementTag>(EMassFragmentPresence::All);
}

void UMyHealthProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    // 遍历所有匹配查询的实体
    EntityQuery.ForEachEntityChunk(EntityManager, Context, [this](FMassExecutionContext& Context)
    {
        // 获取当前 Chunk 中所有实体的 HealthFragment 数组
        TConstArrayView<FMyHealthFragment> HealthList = Context.GetFragmentView<FMyHealthFragment>();

        for (int32 i = 0; i < Context.GetNumEntities(); ++i)
        {
            FMyHealthFragment& Health = HealthList[i];
            // 示例逻辑：每帧缓慢恢复生命值
            Health.CurrentHealth = FMath::Min(Health.CurrentHealth + 0.1f, Health.MaxHealth);
        }
    });
}
```

### 进阶用法：在 Trait 中组合多个 Fragment 和配置

一个 Trait 通常会组合多个基础 Fragment 来定义一个完整的行为单元。
```cpp
// 在 BuildTemplate 中组合
void UMyAdvancedTrait::BuildTemplate(FMassEntityTemplateBuildContext& BuildContext, const UWorld& World) const
{
    // 添加基础移动能力
    BuildContext.AddFragment<FMassVelocityFragment>();
    BuildContext.AddFragment<FMassForceFragment>();
    BuildContext.AddTag<FMassMovementTag>();

    // 添加我们自定义的健康数据
    BuildContext.AddFragment<FMyHealthFragment>();

    // 添加一个表示需求，告诉系统这个实体需要视觉代理
    BuildContext.AddFragment<FMassRepresentationFragment>();

    // 可以从 Trait 的 UPROPERTY 读取配置
    FMyHealthFragment& Health = BuildContext.GetFragment<FMyHealthFragment>();
    Health.MaxHealth = InitialMaxHealth; // InitialMaxHealth 是 Trait 的 UPROPERTY
}
```

## Demo 示例

以下是一个最小的、可编译的自定义 Trait 和 Processor 示例，用于演示如何扩展 MassGameplay。

**MyDamageableTrait.h**
```cpp
#pragma once
#include "MassEntityTraitBase.h"
#include "MyDamageableTrait.generated.h"

USTRUCT(BlueprintType)
struct FDamageableFragment : public FMassFragment
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    float Health = 100.0f;
};

UCLASS(meta=(DisplayName="Damageable"))
class MYPROJECT_API UMyDamageableTrait : public UMassEntityTraitBase
{
    GENERATED_BODY()

protected:
    virtual void BuildTemplate(FMassEntityTemplateBuildContext& BuildContext, const UWorld& World) const override
    {
        BuildContext.AddFragment<FDamageableFragment>();
    }
};
```

**MyDamageProcessor.h**
```cpp
#pragma once
#include "MassProcessor.h"
#include "MyDamageProcessor.generated.h"

UCLASS()
class MYPROJECT_API UMyDamageProcessor : public UMassProcessor
{
    GENERATED_BODY()

public:
    UMyDamageProcessor();

protected:
    virtual void ConfigureQueries() override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

private:
    FMassEntityQuery EntityQuery;
};
```

**MyDamageProcessor.cpp**
```cpp
#include "MyDamageProcessor.h"
#include "MyDamageableTrait.h" // 包含 FDamageableFragment 的定义

UMyDamageProcessor::UMyDamageProcessor()
{
    ExecutionOrder.ExecuteInGroup = UE::Mass::ProcessorGroupNames::Behavior;
}

void UMyDamageProcessor::ConfigureQueries()
{
    EntityQuery.AddRequirement<FDamageableFragment>(EMassFragmentAccess::ReadWrite);
}

void UMyDamageProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    EntityQuery.ForEachEntityChunk(EntityManager, Context, [](FMassExecutionContext& Context)
    {
        TConstArrayView<FDamageableFragment> DamageableList = Context.GetFragmentView<FDamageableFragment>();

        for (int32 i = 0; i < Context.GetNumEntities(); ++i)
        {
            FDamageableFragment& Damageable = DamageableList[i];
            // 示例：每帧受到 1 点固定伤害
            Damageable.Health -= 1.0f;
            if (Damageable.Health <= 0.0f)
            {
                // 标记实体待销毁（实际销毁逻辑通常由其他系统处理）
                Context.Defer().DestroyEntity(Context.GetEntity(i));
            }
        }
    });
}
```

## 模块依赖

MassGameplay 作为一个大型插件，其内部模块相互依赖。对于**使用者**（在你的项目中使用 MassGameplay）而言，你需要依赖以下关键模块：

| 模块 | 用途 |
|---|---|
| `MassEntity` | MassGameplay 的底层 ECS 框架，提供实体、片段、处理器等核心概念。 |
| `MassEntityEditor` | 提供编辑器支持，如实体模板编辑器、调试工具。 |
| `NavigationSystem` | `MassMovement` 模块依赖此模块实现寻路功能。 |
| `SmartObjectsModule` | `MassSmartObjects` 模块依赖此模块实现与游戏世界交互点的集成。 |

*注意：`Core`, `CoreUObject`, `Engine`, `Slate`, `UMG` 等是 UE 基础模块，此处省略。*

## 维护状态

### 近期更新

```
- 2025-10-03 a01ceff5fb6d [Mass] Limited access to FMassArchetypeComposition's bitsets in preparation for near-future changes
- 2025-09-15 9803c443cfab Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied using UnrealCodeFixup)
- 2025-08-20 2739c3d30ebc Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 4/n
```

### 维护评价

MassGameplay 是一个**仍在积极维护中**的实验性插件。
- **创建时间**：约 4 年前（2021年），相对较新。
- **更新频率**：近期更新主要是代码现代化和底层重构（如访问控制、代码生成宏），表明 Epic 正在为其未来的大版本更新做准备，而非简单修复。
- **活跃度**：作为 MassEntity 框架的官方游戏玩法实现，它是 UE5 大规模模拟的核心组件，预计会长期维护。
- **已知限制**：标记为 `IsExperimentalVersion=true` 和 `EnabledByDefault=false`，意味着 API 可能发生变化，且需要手动启用。在生产环境中使用需谨慎，并做好应对 API 变更的准备。
- **推荐使用**：如果你的项目确实需要处理海量实体，并且愿意接受实验性 API 的潜在变动，MassGameplay 是官方推荐且功能强大的解决方案。建议从其提供的示例项目（如 `CitySample`）开始学习。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MassGameplay)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/mass-entity-in-unreal-engine/) (MassEntity 框架文档，MassGameplay 基于此)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MassGameplay/Source/MassGameplayTestSuite)