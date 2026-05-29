# MassGameplay

> Implementation of large-scale agent simulation based on MassEntity

| 属性 | 值 |
|---|---|
| 中文名 | 大规模游戏模拟 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、实体配置） |
| 模块 | `MassActors` (Runtime), `MassCharacterTrajectory` (Runtime), `MassCommon` (Runtime), `MassEQS` (Runtime), `MassGameplayDebug` (Runtime), `MassGameplayEditor` (Runtime), `MassGameplayExternalTraits` (Runtime), `MassGameplayTestSuite` (Runtime), `MassLOD` (Runtime), `MassMovement` (Runtime), `MassMovementEditor` (Runtime), `MassReplication` (Runtime), `MassRepresentation` (Runtime), `MassSimulation` (Runtime), `MassSmartObjects` (Runtime), `MassSpawner` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay) | |

## 用途

MassGameplay 是基于 MassEntity ECS 框架的**大规模实体游戏逻辑实现层**。它解决的核心问题是：**如何让成千上万的 Actor（如 NPC、人群、敌人）高效运行并参与游戏逻辑**。

具体来说，MassGameplay 提供了以下能力：
1. **Actor-Entity 双向桥接**：通过 `UMassAgentComponent` 让传统 Actor 与 Mass ECS 实体互通
2. **大规模 Actor 生成管理**：`UMassActorSpawnerSubsystem` 提供优先级队列、预算控制、Actor 池化
3. **Agent 生命周期管理**：`UMassAgentSubsystem` 处理 Agent 注册、更新、取消注册和木偶（Puppet）模式
4. **LOD 分层处理**：根据距离切换实体/Actor 的详细程度
5. **网络复制**：大规模实体的客户端同步
6. **智能对象交互**：Mass 实体与 SmartObject 系统集成

这个插件是 MassEntity 的"游戏化"封装，将 ECS 框架与传统 Actor 架构无缝连接。

## 使用场景

- 你在做一个开放世界游戏，需要数千个 NPC 在城市中行走 → 使用 MassGameplay
- 你需要大规模敌人 AI（如僵尸群、军队）同时运行 → 使用 MassGameplay
- 你想要用 Mass ECS 高性能处理实体，但仍需要传统的 Actor 功能（动画、碰撞、渲染）→ 使用 MassGameplay 的 Agent 桥接
- 你需要控制大量 Actor 的生成顺序和预算（避免卡顿）→ 使用 MassActorSpawnerSubsystem
- 你在做一个需要网络同步的大规模多人游戏 → 使用 MassReplication 模块

## 蓝图用法

### Agent 组件（UMassAgentComponent）

`UMassAgentComponent` 是 Actor 连接 Mass 系统的核心组件，提供以下蓝图节点：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Enable` | 启用组件，注册到 Mass 系统 | `UMassAgentComponent` |
| `Disable` | 禁用组件，从 Mass 系统取消注册 | `UMassAgentComponent` |
| `KillEntity` | 销毁关联的 Mass 实体 | `UMassAgentComponent` |

### Actor 池化接口（IMassActorPoolableInterface）

实现此接口可让 Actor 参与 Mass 系统的对象池复用：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CanBePooled` | 返回该 Actor 是否可以被池化 | `IMassActorPoolableInterface` |
| `PrepareForPooling` | Actor 回收前的准备工作（关闭碰撞、停止动画等） | `IMassActorPoolableInterface` |
| `PrepareForGame` | Actor 从池中取出后的恢复工作 | `IMassActorPoolableInterface` |

### 使用示例

**启用 Agent 连接**：
1. 在 Actor 蓝图中添加 `UMassAgentComponent`
2. 设置 `EntityConfig` 选择实体配置资产
3. 在 `BeginPlay` 时调用 `Enable()` 节点
4. 实体会自动创建并与 Actor 同步

**实现可池化 Actor**：
1. 创建 Actor 蓝图并实现 `IMassActorPoolableInterface` 接口
2. 在 `CanBePooled` 中返回 true
3. 在 `PrepareForPooling` 中禁用碰撞、停止移动等
4. 在 `PrepareForGame` 中恢复所有状态

## C++ 用法

### 头文件引入

```cpp
#include "MassAgentComponent.h"
#include "MassActorSubsystem.h"
#include "MassAgentSubsystem.h"
#include "MassActorSpawnerSubsystem.h"
```

### 基本用法 - Actor-Entity 桥接

```cpp
// 来源：MassActors 模块示例用法

// 获取 Mass Actor 子系统
UMassActorSubsystem* ActorSubsystem = GetWorld()->GetSubsystem<UMassActorSubsystem>();

// 从 Actor 获取关联的 Mass Entity Handle
FMassEntityHandle EntityHandle = ActorSubsystem->GetEntityHandleFromActor(MyActor);

// 从 Entity Handle 获取关联的 Actor
AActor* AssociatedActor = ActorSubsystem->GetActorFromHandle(EntityHandle);

// 手动设置 Actor 与 Entity 的关联
ActorSubsystem->SetHandleForActor(MyActor, EntityHandle);
```

### 进阶用法 - Actor 生成请求

```cpp
// 来源：MassActorSpawnerSubsystem.h

// 准备生成请求
FMassActorSpawnRequest SpawnRequest;
SpawnRequest.Template = AMyNPC::StaticClass();
SpawnRequest.Transform = FTransform(FRotator::ZeroRotator, SpawnLocation);
SpawnRequest.Priority = 1.0f; // 优先级（值越小优先级越高）

// 设置生成后的回调
SpawnRequest.ActorPostSpawnDelegate.BindLambda(
    [](const FMassActorSpawnRequestHandle& Handle, FConstStructView Request) -> EMassActorSpawnRequestAction
    {
        // 处理生成后的 Actor
        return EMassActorSpawnRequestAction::Remove; // 自动移除请求
    });

// 提交生成请求
UMassActorSpawnerSubsystem* SpawnerSubsystem = GetWorld()->GetSubsystem<UMassActorSpawnerSubsystem>();
FMassActorSpawnRequestHandle Handle = SpawnerSubsystem->RequestActorSpawn(SpawnRequest);

// 查询请求状态
const FMassActorSpawnRequest& StoredRequest = SpawnerSubsystem->GetSpawnRequest<FMassActorSpawnRequest>(Handle);
if (StoredRequest.SpawnStatus == ESpawnRequestStatus::Succeeded)
{
    AActor* SpawnedActor = StoredRequest.SpawnedActor;
}
```

### 辅助函数 - 从 Actor 操作 Entity

```cpp
// 来源：MassActorHelper.h

#include "MassActorHelper.h"

// 给 Actor 关联的 Entity 添加 Tag
UE::MassActor::AddEntityTagToActor<FMyCustomTag>(*MyActor);

// 从 Actor 关联的 Entity 移除 Tag
UE::MassActor::RemoveEntityTagFromActor<FMyCustomTag>(*MyActor);
```

## Demo 示例

### 可池化的 NPC Actor

```cpp
// MassPoolableNPC.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "MassActorPoolableInterface.h"
#include "MassAgentComponent.h"
#include "MassPoolableNPC.generated.h"

UCLASS()
class AMassPoolableNPC : public ACharacter, public IMassActorPoolableInterface
{
    GENERATED_BODY()

public:
    AMassPoolableNPC();

    // IMassActorPoolableInterface
    virtual bool CanBePooled_Implementation() override;
    virtual void PrepareForPooling_Implementation() override;
    virtual void PrepareForGame_Implementation() override;

    UPROPERTY(VisibleAnywhere)
    UMassAgentComponent* MassAgentComponent;
};
```

```cpp
// MassPoolableNPC.cpp
#include "MassPoolableNPC.h"

AMassPoolableNPC::AMassPoolableNPC()
{
    MassAgentComponent = CreateDefaultSubobject<UMassAgentComponent>(TEXT("MassAgent"));
}

bool AMassPoolableNPC::CanBePooled_Implementation()
{
    // 检查是否可以被池化
    return MassAgentComponent && MassAgentComponent->IsReadyForPooling();
}

void AMassPoolableNPC::PrepareForPooling_Implementation()
{
    // 回收前准备
    SetActorHiddenInGame(true);
    SetActorEnableCollision(false);
    SetActorTickEnabled(false);
    GetCharacterMovement()->StopMovementImmediately();
    GetCharacterMovement()->DisableMovement();
}

void AMassPoolableNPC::PrepareForGame_Implementation()
{
    // 从池中取出后恢复
    SetActorHiddenInGame(false);
    SetActorEnableCollision(true);
    SetActorTickEnabled(true);
    GetCharacterMovement()->SetMovementMode(MOVE_Walking);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MassEntity` | MassEntity 核心 ECS 框架 |
| `MassEntityEditor` | Mass 实体编辑器支持（调试、编辑器集成） |
| `SmartObjectsModule` | 智能对象系统集成 |
| `MassSpawner` | Mass 实体生成器 |
| `MassEQS` | Mass 实体环境查询系统 |
| `AIModule` | AI 系统（行为树、EQS 等） |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `07ab5d30` | Revert earlier change to MassAgentComponent. | 回滚 MassAgentComponent 的早期修改 |
| 2026-05-13 | `751e48da` | [MassRepresentation] Wait for actor readiness before switching off ISM | Actor 就绪前不关闭 ISM，修复表示层问题 |
| 2026-05-13 | `022b39e0` | Fix handling of non-puppet actors in Mass crowds | 修复 Mass 人群中非木偶 Actor 的处理 |
| 2026-05-12 | `7c7f835b` | [MassRepresentation] Cluster of pre-existing bugs in `TMassLODCalculator`'s per-viewer LOD path | 修复 LOD 计算器的多个已知 Bug |
| 2026-05-12 | `f59bc340` | [Mass representation] Switched two manually calculated `bDoKeepActorExtraFrame` to use the new UE::M | 重构 Actor 额外帧保留逻辑 |

### 维护评价

**维护状态：活跃维护中** ✅

- **创建时间**：2021 年 9 月，约 5 年历史
- **最近更新**：2026 年 5 月仍有密集更新，修复 Bug 和重构
- **活跃度**：近期内有多次功能性更新和 Bug 修复
- **实验性**：插件标记为 `IsExperimentalVersion=true`，且 `EnabledByDefault=false`
- **推荐使用**：⚠️ **谨慎使用** - 虽然活跃维护，但仍是实验性功能，API 可能变动。适合新项目和愿意跟踪 API 变化的团队。不建议在生产环境中依赖稳定的 API。

**注意事项**：
1. 这是一个实验性插件，需要手动启用
2. API 变化频繁（如近期的 ActorSpawnerSubsystem 回调签名变更）
3. 需要理解 MassEntity ECS 框架的概念
4. 与传统 Actor 系统有桥接开销，不适合所有场景

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay)
- [官方文档]()（无）
- [MassEntity 插件文档](../MassEntity/index.md)