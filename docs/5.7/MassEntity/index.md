# MassEntity

> Gameplay-focused framework supporting data-oriented processing. This plugin is now DEPRECATED. All of MassEntity code has been moved to the engine and there's no need to enable this plugin anymore.

| 属性 | 值 |
|---|---|
| 分类 | Runtime |
| 默认启用 | false (已废弃) |
| 包含内容 | true (仅测试资源) |
| 模块 | 无 (已移至引擎源码) |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕 (≤5年，≈4年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/Runtime/MassEntity) | |

> **⚠️ 重要提示**: MassEntity plugin 本身已从 UE 5.5 起被标记为废弃。所有源码已迁移至引擎核心 `Engine/Source/Runtime/MassEntity/`。无需再单独启用此 plugin，引擎已自动包含 MassEntity 模块。

## 用途

MassEntity 是 UE5 的 **ECS (Entity Component System)** 框架实现，提供面向数据（Data-Oriented）的大规模实体处理能力。它解决了传统 UObject 模式在处理**数万甚至数十万**同类型对象时的性能瓶颈：

- **传统 UObject 模式**: 每个实体都是独立的 UObject，有独立的 GC 追踪、虚表、反射开销
- **Mass ECS 模式**: 实体被压缩存储在内存连续的 Archetype/Chunk 中，处理器按数据布局批量遍历

核心设计理念：
1. **Entity** 只是一个轻量句柄 `FMassEntityHandle`（8 字节，Index + SerialNumber）
2. **Fragment** 是附着在 Entity 上的数据块（类似 ECS 中的 Component），继承自 `FMassFragment`
3. **Tag** 是零数据的标记类型，仅用于过滤，继承自 `FMassTag`
4. **Archetype** 描述一组 Entity 的 Fragment/Tag 组合，相同组合的实体存储在同一 Archetype 的 Chunk 中
5. **Processor** 是对满足特定条件的 Entity 集合执行操作的逻辑单元

这套架构被 Lyra、CitySample 等 Epic 官方项目广泛使用，是 UE5 大规模模拟的基础。

## 使用场景

- 你需要在场景中同时管理 **数万个 NPC/Agent** → 用 MassEntity 的 Archetype 存储和 Query 批量遍历
- 你需要实现一个 **RTS 游戏** 中的大量单位 AI → 用 MassEntity + MassAI plugin
- 你需要高效的 **寻路决策树 (State Tree)** 集成 → 用 MassEntity + StateTree
- 你需要 **ISM (Instanced Static Mesh)** 的批量渲染 → MassEntity 的 Chunk 内存布局天然适配
- 你需要 Entity 之间的 **关系（父子、拥有等）** → 用 MassEntity 的 Relation 系统

## 蓝图用法

MassEntity 模块没有暴露任何 `BlueprintCallable` 函数。它是一个纯 C++ 运行时框架。

如果你需要在蓝图中使用 Mass，应使用上层的 **MassGameplay** 插件（如 `UMassSpawnerSubsystem`），它通过 Subsystem 暴露了部分蓝图接口。

## C++ 用法

### 模块依赖

在你的 `Build.cs` 中添加：

```cpp
PublicDependencyModuleNames.AddRange(new string[] {
    "MassEntity"
});
```

如需 Mass AI 相关功能，额外依赖 `MassAIBehavior`、`MassNavigation` 等模块。

### 头文件引入

```cpp
#include "MassEntityManager.h"
#include "MassEntitySubsystem.h"
#include "MassEntityTypes.h"
#include "MassEntityQuery.h"
#include "MassEntityBuilder.h"
#include "MassEntityView.h"
```

### 核心概念：数据类型体系

MassEntity 定义了 5 种实体数据基类，均在 `MassEntityElementTypes.h` 中声明：

| 基类 | 用途 | 是否存储数据 | 内存位置 |
|---|---|---|---|
| `FMassFragment` | 实体的普通数据组件 | ✅ 每个实体独立 | Chunk 内 |
| `FMassTag` | 零数据标记，仅用于过滤 | ❌ | Bitset 追踪 |
| `FMassChunkFragment` | Chunk 级别共享数据 | ✅ 每 Chunk 一份 | Chunk 头部 |
| `FMassSharedFragment` | 跨 Chunk 共享的可变数据 | ✅ 引用计数管理 | 外部存储 |
| `FMassConstSharedFragment` | 跨 Chunk 共享的不可变数据 | ✅ 仅读 | 外部存储 |

定义自定义 Fragment/Tag：

```cpp
// Fragment：存储数据
USTRUCT()
struct FHealthFragment : public FMassFragment
{
    GENERATED_BODY()
    float CurrentHealth = 100.f;
    float MaxHealth = 100.f;
};

// Tag：纯标记
USTRUCT()
struct FEnemyTag : public FMassTag
{
    GENERATED_BODY()
};

// Shared Fragment：多个实体共享同一份数据
USTRUCT()
struct FTeamSharedFragment : public FMassSharedFragment
{
    GENERATED_BODY()
    int32 TeamID = 0;
    FLinearColor TeamColor = FLinearColor::White;
};

// Const Shared Fragment：不可变的共享数据
USTRUCT()
struct FUnitConfigConstSharedFragment : public FMassConstSharedFragment
{
    GENERATED_BODY()
    float MoveSpeed = 600.f;
    float AttackRange = 500.f;
};
```

### 获取 EntityManager

```cpp
// 方式 1：通过 World Subsystem 获取（推荐）
UMassEntitySubsystem* MassSubsystem = GetWorld()->GetSubsystem<UMassEntitySubsystem>();
FMassEntityManager& EntityManager = MassSubsystem->GetMutableEntityManager();

// 方式 2：通过工具函数
FMassEntityManager* Manager = UE::Mass::Utils::GetEntityManager(GetWorld());
```

### 基本用法：创建和销毁实体

```cpp
// 方式 1：使用 FEntityBuilder（推荐，链式 API）
FMassEntityHandle Entity = EntityManager.MakeEntityBuilder()
    .Add<FTransformFragment>(FTransform(FVector(100, 200, 0)))
    .Add<FHealthFragment>(FHealthFragment{ .CurrentHealth = 50.f, .MaxHealth = 100.f })
    .Add<FEnemyTag>()
    .Commit();

// 方式 2：直接创建
FMassArchetypeHandle Archetype = EntityManager.CreateArchetype({
    FTransformFragment::StaticStruct(),
    FHealthFragment::StaticStruct(),
    FEnemyTag::StaticStruct()
});
FMassEntityHandle Entity2 = EntityManager.CreateEntity(Archetype);

// 销毁实体
EntityManager.DestroyEntity(Entity);

// 批量销毁
TArray<FMassEntityHandle> EntitiesToDestroy = { Entity, Entity2 };
EntityManager.BatchDestroyEntities(EntitiesToDestroy);
```

### 基本用法：Query 遍历实体

`FMassEntityQuery` 是 MassEntity 的核心查询工具，用于声明式地匹配 Archetype 并批量遍历实体：

```cpp
// 在 Processor 中定义 Query（通常作为成员变量）
FMassEntityQuery Query;

// 在 ConfigureQueries 中设置需求
void ConfigureQueries()
{
    Query.AddRequirement<FTransformFragment>(EMassFragmentAccess::ReadWrite);
    Query.AddRequirement<FHealthFragment>(EMassFragmentAccess::ReadWrite);
    Query.AddRequirement<FEnemyTag>(EMassFragmentPresence::All);
}

// 在 Execute 中遍历
void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    Query.ForEachEntityChunk(EntityManager, Context,
        [&](FMassExecutionContext& ExecutionContext)
        {
            const int32 NumEntities = ExecutionContext.GetNumEntities();
            TMutableArrayView<FTransformFragment> Transforms =
                ExecutionContext.GetMutableFragmentView<FTransformFragment>();
            TMutableArrayView<FHealthFragment> Healths =
                ExecutionContext.GetMutableFragmentView<FHealthFragment>();

            for (int32 i = 0; i < NumEntities; ++i)
            {
                Transforms[i].GetMutableTransform().AddToTranslation(FVector(0, 0, 1));
                Healths[i].CurrentHealth -= 1.f;
            }
        });
}
```

### 进阶用法：FEntityBuilder

`FEntityBuilder`（`UE::Mass::FEntityBuilder`）是 5.5+ 新增的实体构建工具，提供流畅的链式 API：

```cpp
// 链式构建
FMassEntityHandle Entity = EntityManager.MakeEntityBuilder()
    .Add<FMassStaticRepresentationTag>()
    .Add<FTransformFragment>()
    .Add<FAgentRadiusFragment>(FAgentRadiusFragment{ .Radius = 35.f })
    .Add<FMassVelocityFragment>()
    .Commit();

// 先获取句柄，后续配置
UE::Mass::FEntityBuilder Builder(EntityManager);
FMassEntityHandle ReservedEntity = Builder;  // 自动预留句柄
Builder.Add_GetRef<FTransformFragment>().GetMutableTransform().SetTranslation(FVector(100, 200, 0));
Builder.Commit();  // 正式创建

// 从已有实体复制数据
UE::Mass::FEntityBuilder CloneBuilder(EntityManager);
CloneBuilder.CopyDataFromEntity(ExistingEntity);
CloneBuilder.Commit();

// 带 Relation 的构建
Builder.Add<FChildOfTag>()
    .AddRelation<FChildOfRelation>(ParentEntity, Relations::ERelationRole::Subject)
    .Commit();
```

### 进阶用法：FMassEntityView

`FMassEntityView` 提供对单个实体数据的直接访问（适用于低频操作，非批量遍历场景）：

```cpp
// 通过 EntityManager 获取 View
FMassEntityView View(EntityManager, EntityHandle);

// 读取 Fragment
FHealthFragment* HealthPtr = View.GetFragmentDataPtr<FHealthFragment>();
if (HealthPtr)
{
    UE_LOG(LogTemp, Log, TEXT("Health: %f"), HealthPtr->CurrentHealth);
}

// 检查 Tag
if (View.HasTag<FEnemyTag>())
{
    UE_LOG(LogTemp, Log, TEXT("This is an enemy"));
}

// 读取 Shared Fragment
const FTeamSharedFragment* TeamPtr = View.GetConstSharedFragmentDataPtr<FTeamSharedFragment>();
```

### 进阶用法：Command Buffer（延迟操作）

在 Processor 执行期间，实体布局不能改变。所有变更操作需要通过 Command Buffer 延迟执行：

```cpp
// 获取默认 Command Buffer
FMassCommandBuffer& Commands = EntityManager.Defer();

// 入队操作
Commands.PushCommand<FMassCommandAddFragmentTypes>(EntityHandle, FHealthFragment::StaticStruct());
Commands.PushCommand<FMassCommandRemoveFragmentTypes>(EntityHandle, FHealthFragment::StaticStruct());
Commands.PushCommand<FMassDeferredSetCommand<FTransformFragment>>(EntityHandle,
    [](FTransformFragment& Fragment) { Fragment.GetMutableTransform().SetScale3D(FVector(2.f)); });

// 在帧末尾统一执行
EntityManager.FlushCommands();
```

### 进阶用法：Relation 系统

MassEntity 5.5+ 内建了实体关系系统，用于表达实体之间的关联（如父子、拥有等）：

```cpp
// 定义关系类型
USTRUCT()
struct FChildOfRelation : public FMassRelation
{
    GENERATED_BODY()
};

// 批量创建关系
TArray<FMassEntityHandle> Children = { Child1, Child2 };
TArray<FMassEntityHandle> Parents = { Parent1, Parent1 };
EntityManager.BatchCreateRelations<FChildOfRelation>(Children, Parents);
```

### 进阶用法：Entity Collection

`FEntityCollection` 用于管理一组实体引用，自动处理 Archetype 变更导致的索引失效：

```cpp
UE::Mass::FEntityCollection Collection;
Collection.AddHandle(Entity1);
Collection.AppendHandles({ Entity2, Entity3 });

// 自动获取最新的 Per-Archetype 分组
TConstArrayView<FMassArchetypeEntityCollection> PerArchetype =
    Collection.GetUpToDatePerArchetypeCollections(EntityManager);

// 用于批量操作
EntityManager.BatchDestroyEntityChunks(PerArchetype);
```

## Demo 示例

### 完整的自定义 Processor 示例

**FMyModule.Build.cs**:
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "MassEntity",
    "MassGameplay"  // 如果需要 MassSpawner 等功能
});
```

**FHealthDecayProcessor.h**:
```cpp
#pragma once

#include "MassProcessor.h"
#include "FHealthDecayProcessor.generated.h"

USTRUCT()
struct FHealthFragment : public FMassFragment
{
    GENERATED_BODY()
    float CurrentHealth = 100.f;
};

USTRUCT()
struct FDecayTag : public FMassTag
{
    GENERATED_BODY()
};

UCLASS()
class UHealthDecayProcessor : public UMassProcessor
{
    GENERATED_BODY()

public:
    UHealthDecayProcessor();

    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

private:
    FMassEntityQuery EntityQuery;
};
```

**FHealthDecayProcessor.cpp**:
```cpp
#include "FHealthDecayProcessor.h"
#include "MassExecutionContext.h"

UHealthDecayProcessor::UHealthDecayProcessor()
{
    bAutoRegisterWithProcessingPhases = true;
    ExecutionFlags = static_cast<int32>(EProcessorExecutionFlags::All);
}

void UHealthDecayProcessor::ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager)
{
    EntityQuery.AddRequirement<FHealthFragment>(EMassFragmentAccess::ReadWrite);
    EntityQuery.AddRequirement<FDecayTag>(EMassFragmentPresence::All);
    EntityQuery.RegisterWithProcessor(*this);
}

void UHealthDecayProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    EntityQuery.ForEachEntityChunk(EntityManager, Context,
        [&Context](FMassExecutionContext& ExecutionContext)
        {
            const float DeltaTime = ExecutionContext.GetDeltaTimeSeconds();
            const int32 NumEntities = ExecutionContext.GetNumEntities();
            TMutableArrayView<FHealthFragment> Healths =
                ExecutionContext.GetMutableFragmentView<FHealthFragment>();

            for (int32 i = 0; i < NumEntities; ++i)
            {
                Healths[i].CurrentHealth -= 10.f * DeltaTime;
                if (Healths[i].CurrentHealth <= 0.f)
                {
                    // 标记为待销毁（通过 Command Buffer）
                    ExecutionContext.Defer().DestroyEntity(ExecutionContext.GetEntity(i));
                }
            }
        });
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 基础库 |
| `CoreUObject` | UObject 系统、反射 |
| `Engine` | 引擎核心（UWorld、Subsystem 等） |
| `DeveloperSettings` | 配置设置基类（UMassEntitySettings） |
| `TraceLog` | 追踪和性能分析 |
| `StructUtils` | 位集合（StructTypeBitSet）、InstancedStruct 等工具 |

## 维护状态

### 近期更新

```
188070d|2024-07-29|[Mass] Marked the MassEntity plugin as deprecated in 5.5, following the move of all of its code over to the engine.
e7bdda6|2024-07-25|[Backout] - Moved the rest of MassEntity modules over to the Engine's Source/ code.
8571531|2024-07-25|[Backout] - Moved the rest of MassEntity modules over to the Engine's Source/ code.
```

### 维护评价

- **创建时间**: 2021-09-29，约 4 年历史
- **Plugin 状态**: ⚠️ **已废弃** — UE 5.5 起 plugin 本身仅作为遗留占位符存在
- **引擎源码**: MassEntity 模块已迁移至 `Engine/Source/Runtime/MassEntity/`，**仍在积极维护和扩展**
- **活跃程度**: 非常活跃。Epic 在 5.5/5.6/5.7 中持续增强 Mass 框架（新增 Relation 系统、FEntityBuilder、Entity Collection、TypeManager 等）
- **推荐使用**: ✅ 推荐使用引擎内建的 MassEntity 模块。**不要**再启用旧的 MassEntity plugin
- **注意事项**:
  - `MassEntity.uplugin` 的 `DeprecatedEngineVersion` 设置为 `5.5`，意味着未来版本可能移除此 plugin 占位符
  - `IsBetaVersion = true` — Mass 框架仍在演进中，API 可能在大版本间发生变化
  - 大量 5.5/5.6 标记了 `UE_DEPRECATED` 的 API，升级时需关注迁移指南

## 相关链接

- [源码 (Plugin 占位)](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MassEntity)
- [源码 (引擎内建)](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/Runtime/MassEntity)
- 官方文档: 暂无公开文档链接
