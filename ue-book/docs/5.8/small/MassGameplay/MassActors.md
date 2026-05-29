# MassActors

> Implementation of large-scale agent simulation based on MassEntity

| 属性 | 值 |
|---|---|
| 中文名 | 大规模代理Actor |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源） |
| 模块 | `MassActors` (Runtime), `MassCharacterTrajectory` (Runtime), `MassCommon` (Runtime), `MassEQS` (Runtime), `MassGameplayDebug` (Runtime), `MassGameplayEditor` (Runtime), `MassGameplayExternalTraits` (Runtime), `MassGameplayTestSuite` (Runtime), `MassLOD` (Runtime), `MassMovement` (Runtime), `MassMovementEditor` (Runtime), `MassReplication` (Runtime), `MassRepresentation` (Runtime), `MassSimulation` (Runtime), `MassSmartObjects` (Runtime), `MassSpawner` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay) | |

## 用途

`MassGameplay` 插件的核心目的是在 Unreal Engine 的 `MassEntity` ECS 框架之上，构建一套完整的游戏玩法系统。它解决了在开发包含大量实体（如成千上万的 NPC、可交互对象或弹道）的游戏时，如何将 `MassEntity` 的高性能数据处理能力与 Unreal Engine 传统的 Actor 模型进行桥接和结合的问题。

**为什么存在？**
`MassEntity` 提供了一种面向数据、可扩展的 ECS 架构，适合处理大规模同质实体的逻辑。然而，游戏的渲染、物理、动画、网络复制等功能依然深度依赖于 Actor 和 ActorComponent 体系。`MassGameplay` 提供了必要的基础设施（如 `UMassAgentComponent`、`UMassActorSpawnerSubsystem`），使得：
1.  **双向转换**：可以在 Actor 和 Mass Entity 之间安全地创建、关联和转换，实现逻辑与表现的分离。
2.  **性能扩展**：将游戏玩法逻辑（如移动、感知、决策）部署到 Mass 系统中处理，而仅在需要表现（如渲染、物理交互）时生成或激活对应的 Actor。
3.  **无缝集成**：提供了与 Unreal 标准系统（如行为树、角色移动组件、EQS）的集成点（通过 Translator），让开发者可以逐步采用 Mass 框架。

简单来说，`MassGameplay` 是让你在享受 `MassEntity` 带来的海量实体性能优势的同时，还能使用 Unreal Actor 生态系统所有功能的“粘合剂”和“扩展包”。

## 使用场景

-   **你正在开发一款开放世界游戏**，需要同时渲染和模拟数千名市民、士兵或车辆。你可以使用 `MassGameplay` 让大部分实体仅在 Mass 系统中运行轻量级 AI 和移动逻辑，只有玩家附近的实体才会生成完整的 Actor 来获得动画、物理和高级 AI。
-   **你正在制作一款即时战略（RTS）游戏**，需要管理成千上万的战斗单位。`MassGameplay` 可以帮助你将单位的基础移动和状态更新放在高性能的 Mass 系统中执行，而将复杂的攻击动画、技能特效和寻路请求交给 Actor 系统处理。
-   **你的游戏有大量可投射物或交互式粒子效果**。可以使用 Mass 实体来管理它们的轨迹和生命周期计算，仅在碰撞或需要视觉表现时生成 Actor。
-   **你希望将一部分游戏逻辑（如群体行为、资源采集）从 Actor 的 Tick 中剥离出来，以优化性能**。`MassGameplay` 提供了将这部分逻辑迁移到 Mass 处理器（Processor/Translator）的路径。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Enable` | 启用 `UMassAgentComponent`，使其与 Mass 模拟系统通信，创建关联的实体。 | `UMassAgentComponent` |
| `Disable` | 禁用 `UMassAgentComponent`，切断与 Mass 模拟系统的连接。 | `UMassAgentComponent` |
| `KillEntity` | 关闭并销毁组件关联的 Mass 实体，可选是否同时销毁所属的 Actor。 | `UMassAgentComponent` |
| `CanBePooled` | （蓝图可实现事件）查询当前 Actor 是否准备好被回收到对象池。 | `IMassActorPoolableInterface` |
| `PrepareForPooling` | （蓝图可实现事件）在 Actor 被回收到对象池前进行清理或重置。 | `IMassActorPoolableInterface` |
| `PrepareForGame` | （蓝图可实现事件）在 Actor 从对象池中取出并重新激活前进行初始化。 | `IMassActorPoolableInterface` |

### 使用示例（蓝图描述）

1.  **创建可被 Mass 管理的 Actor**：
    -   在 Actor 蓝图中添加 `UMassAgentComponent`。
    -   在组件的细节面板中，配置 `EntityConfig` 资产，该资产定义了此 Actor 对应的 Mass 实体模板（包含哪些片段、标签等）。
    -   在 `BeginPlay` 或其他逻辑中，调用 `Enable` 节点来启动与 Mass 系统的同步。

2.  **实现可池化的 Actor**：
    -   让 Actor 蓝图实现 `IMassActorPoolableInterface` 接口。
    -   实现 `CanBePooled`（例如，检查 Actor 是否处于空闲状态）、`PrepareForPooling`（例如，隐藏网格、禁用碰撞）和 `PrepareForGame`（例如，显示网格、启用碰撞）事件。
    -   系统会自动在合适的时候调用这些事件。

3.  **从 Mass 端控制 Actor**：
    -   在 Mass 处理器或转换器（Translator）中，通过 `UMassActorSubsystem` 获取实体关联的 Actor，并操作它（如播放动画、施加力）。

## C++ 用法

### 头文件引入

```cpp
#include "MassActors/MassActorSubsystem.h"
#include "MassActors/MassActorSpawnerSubsystem.h"
#include "MassActors/MassAgentComponent.h"
```

### 基本用法

**1. 请求生成一个 Actor (来自 `UMassActorSpawnerSubsystem`)**
```cpp
// 引自: Engine/Plugins/Runtime/MassGameplay/Source/MassActors/Public/MassActorSpawnerSubsystem.h
// 获取子系统
UMassActorSpawnerSubsystem* ActorSpawnerSubsystem = GetWorld()->GetSubsystem<UMassActorSpawnerSubsystem>();

// 准备生成请求
FMassActorSpawnRequest SpawnRequest;
SpawnRequest.Template = MyActorClass; // TSubclassOf<AActor>
SpawnRequest.Transform = FTransform(FRotator::ZeroRotator, SpawnLocation, FVector::OneVector);
SpawnRequest.Priority = 10.0f; // 数值越小优先级越高

// 提交请求，获取句柄用于后续跟踪
FMassActorSpawnRequestHandle SpawnHandle = ActorSpawnerSubsystem->RequestActorSpawn(SpawnRequest);

// 可以稍后通过句柄查询状态或移除请求
// ESpawnRequestStatus Status = ActorSpawnerSubsystem->GetSpawnRequest<FMassActorSpawnRequest>(SpawnHandle).SpawnStatus;
```

**2. 查询实体与 Actor 的关联 (来自 `UMassActorSubsystem`)**
```cpp
// 引自: Engine/Plugins/Runtime/MassGameplay/Source/MassActors/Public/MassActorSubsystem.h
UMassActorSubsystem* ActorSubsystem = GetWorld()->GetSubsystem<UMassActorSubsystem>();

// 给定一个 Actor，查找其关联的 Mass 实体句柄
AActor* MyActor = /* ... */;
FMassEntityHandle EntityHandle = ActorSubsystem->GetEntityHandleFromActor(MyActor);
if (EntityHandle.IsValid())
{
    // 拥有了实体句柄，就可以在 Mass 框架下操作它
}

// 反向查找：给定一个实体句柄，获取关联的 Actor
FMassEntityHandle SomeEntity = /* ... */;
AActor* AssociatedActor = ActorSubsystem->GetActorFromHandle(SomeEntity);
if (AssociatedActor)
{
    // 找到了关联的 Actor
}
```

### 进阶用法

**1. 使用 Agent 组件同步属性**
通过在实体模板中添加特定的 `Trait` (如 `UMassAgentCapsuleCollisionSyncTrait`)，可以自动将 Actor 的胶囊体尺寸、位置等属性同步到 Mass 实体上，反之亦然。
```cpp
// 在你的实体配置资产或自定义 Trait 中，添加同步特性
// 引自: Engine/Plugins/Runtime/MassGameplay/Source/MassActors/Public/MassAgentTraits.h
// 当添加了 UMassAgentCapsuleCollisionSyncTrait 后，系统会自动处理 Actor 的 UCapsuleComponent 和实体的 FTransformFragment 之间的同步。
```

**2. 手动断开 Actor 与实体的关联**
```cpp
// 引自: Engine/Plugins/Runtime/MassGameplay/Source/MassActors/Public/MassActorSubsystem.h
UMassActorSubsystem* ActorSubsystem = GetWorld()->GetSubsystem<UMassActorSubsystem>();
AActor* ActorToDisconnect = /* ... */;
FMassEntityHandle EntityHandleToDisconnect = /* ... */;

// 安全地断开连接，系统会自动清理内部映射
ActorSubsystem->DisconnectActor(ActorToDisconnect, EntityHandleToDisconnect);
```

## Demo 示例

一个最小化的示例，演示如何从一个 Actor 请求生成另一个 Actor 并跟踪其状态。

**MySpawnerActor.h**
```cpp
// Fill out your copyright notice in the Description page of Project Settings.
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MassActors/MassActorSpawnerSubsystem.h"
#include "MySpawnerActor.generated.h"

UCLASS()
class MASSGAMEPLAY_API AMySpawnerActor : public AActor
{
	GENERATED_BODY()
	
public:	
	AMySpawnerActor();

protected:
	virtual void BeginPlay() override;

public:	
	virtual void Tick(float DeltaTime) override;

	/** 要生成的 Actor 类 */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Mass Spawning")
	TSubclassOf<AActor> ActorToSpawn;

	/** 用于跟踪生成请求的句柄 */
	FMassActorSpawnRequestHandle SpawnRequestHandle;
	
	/** 是否已经发起过生成请求 */
	bool bSpawnRequested = false;
};
```

**MySpawnerActor.cpp**
```cpp
// Fill out your copyright notice in the Description page of Project Settings.
#include "MySpawnerActor.h"
#include "MassActors/MassActorSpawnerSubsystem.h"

AMySpawnerActor::AMySpawnerActor()
{
	PrimaryActorTick.bCanEverTick = true;
}

void AMySpawnerActor::BeginPlay()
{
	Super::BeginPlay();
}

void AMySpawnerActor::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	// 在 Tick 中尝试请求生成
	if (!bSpawnRequested && ActorToSpawn)
	{
		if (UMassActorSpawnerSubsystem* SpawnerSys = GetWorld()->GetSubsystem<UMassActorSpawnerSubsystem>())
		{
			FMassActorSpawnRequest Request;
			Request.Template = ActorToSpawn;
			Request.Transform = GetActorTransform();
			Request.Priority = 5.0f;

			SpawnRequestHandle = SpawnerSys->RequestActorSpawn(Request);
			bSpawnRequested = true;
			UE_LOG(LogTemp, Log, TEXT("Spawn request submitted. Handle: %s"), *SpawnRequestHandle.ToString());
		}
	}

	// 检查生成状态
	if (bSpawnRequested && SpawnRequestHandle.IsValid())
	{
		if (UMassActorSpawnerSubsystem* SpawnerSys = GetWorld()->GetSubsystem<UMassActorSpawnerSubsystem>())
		{
			const FMassActorSpawnRequest& Request = SpawnerSys->GetSpawnRequest<FMassActorSpawnRequest>(SpawnRequestHandle);
			switch (Request.SpawnStatus)
			{
			case ESpawnRequestStatus::Succeeded:
				UE_LOG(LogTemp, Log, TEXT("Actor spawned successfully!"));
				// 可以在这里对生成的 Actor 进行操作，例如: Request.SpawnedActor->SetActorHiddenInGame(false);
				break;
			case ESpawnRequestStatus::Failed:
				UE_LOG(LogTemp, Warning, TEXT("Actor spawn failed!"));
				// 可以考虑重试: SpawnerSys->RetryActorSpawnRequest(SpawnRequestHandle);
				break;
			case ESpawnRequestStatus::Pending:
			case ESpawnRequestStatus::Processing:
				// 等待中
				break;
			default:
				break;
			}
		}
	}
}
```

## 模块依赖

本插件（MassActors模块）主要依赖于以下特定模块，这些依赖关系在 `MassActors.Build.cs` 中定义：

| 模块 | 用途 |
|---|---|
| `EditorFramework` | 提供编辑器框架支持，用于编辑器内的可视化和调试功能。 |
| `UnrealEd` | 提供 Unreal 编辑器核心功能，用于实现自定义资产编辑器、细节面板扩展等。 |

**说明**：除了上述模块，MassGameplay 插件的其他子模块（如 `MassSimulation`, `MassCommon`）会依赖更多的核心和 Mass 系统模块。对于最终使用者而言，通常只需要在项目的 `.Build.cs` 文件中添加对 `MassGameplay` 插件模块的依赖（如 `MassActors`, `MassCommon`, `MassSimulation`），无需手动添加上述编辑器依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `07ab5d30` | Revert earlier change to MassAgentComponent. | 撤销了对 MassAgentComponent 的早期修改，可能是为了解决回归问题。 |
| 2026-05-13 | `751e48da` | [MassRepresentation] Wait for actor readiness before switching off ISM | [MassRepresentation] 在关闭实例化静态网格体(ISM)前等待 Actor 就绪，提升了切换过程的稳定性。 |
| 2026-05-13 | `022b39e0` | Fix handling of non-puppet actors in Mass crowds | 修复了在 Mass 人群系统中处理非傀儡(puppet) Actor 时的逻辑错误。 |
| 2026-05-12 | `7c7f835b` | [MassRepresentation] Cluster of pre-existing bugs in `TMassLODCalculator`'s per-viewer LOD path. | [MassRepresentation] 修复了 `TMassLODCalculator` 在 per-viewer LOD 路径上存在的一簇历史遗留 Bug。 |
| 2026-05-12 | `f59bc340` | [Mass representation] Switched two manually calculated `bDoKeepActorExtraFrame` to use the new UE::M | [Mass representation] 将两处手动计算 `bDoKeepActorExtraFrame` 的代码切换为使用新的 `UE::Mass` 公共工具函数。 |

### 维护评价

`MassGameplay` 是一个相对年轻的插件（创建于 2021 年），并且被明确标记为 **实验性**。从最近的 Git 历史来看，它在 **2026 年 5 月仍有密集的更新**，主要集中在修复 Bug（如 Actor 与实体状态同步、LOD 切换）和改进系统稳定性（如表示层、复制系统）。

**评价**：
- **活跃维护**：尽管是实验性功能，但 Epic Games 团队仍在积极开发和修复问题。
- **推荐使用**：该插件是 Epic 官方推出的大规模实体游戏玩法解决方案，技术方向明确且投入持续。对于有大规模实体需求的项目，**强烈建议关注和尝试**，但需做好应对 API 变化（当前版本 0.4）和潜在不稳定性的准备。
- **风险提示**：由于其“实验性”标签，不建议直接用于要求极致稳定性的商业发布版本。建议在开发前期进行原型验证，并密切关注版本更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay/Source/MassGameplayTestSuite)