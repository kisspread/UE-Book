# Concert Replication Scripting

> Exposes Concert Replication types for scripting, e.g. in Blueprints

| 属性 | 值 |
|---|---|
| 中文名 | 多端复制脚本化 |
| 分类 | Networking |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ConcertReplicationScripting` (Runtime), `ConcertReplicationScriptingEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023-12-08 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertScripting/ConcertReplicationScripting) | |

## 用途

本插件的核心目的是将 Unreal 的 `Concert Replication` 系统（用于在多人协作或多人在线编辑场景下同步对象状态）的内部 C++ 类型和函数暴露给蓝图系统。它使得开发者无需编写 C++ 代码，就能在蓝图中查询、配置和控制多端复制的复制流、客户端对象等，主要服务于多端编辑器和运行时复制的可视化调试与快速原型开发。

## 使用场景

- 你正在开发一个需要多人实时协作编辑关卡的工具 → 用本插件在蓝图中管理和调试复制流。
- 你需要快速为多端复制功能创建测试或演示蓝图，而不想编写 C++ 代码。
- 你希望在蓝图中动态地将游戏对象添加到多端复制系统，或查询当前复制状态。

## 蓝图用法

本插件将核心功能封装在两个子系统中，通过蓝图可调用的函数提供服务。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Concert Replication Client` | 根据客户端标识获取对应的多端复制客户端对象。 | `UConcertReplicationSubsystem` |
| `Add Objects to Replication` | 将一组对象添加到指定客户端的复制流中，使其状态能够被同步。 | `UConcertReplicationSubsystem` |
| `Remove Objects from Replication` | 将一组对象从指定客户端的复制流中移除。 | `UConcertReplicationSubsystem` |
| `Get Replicated Objects` | 获取指定客户端正在复制的所有对象列表。 | `UConcertReplicationSubsystem` |
| `Is Object Replicated` | 检查某个特定对象是否正在被某个客户端复制。 | `UConcertReplicationSubsystem` |

### 使用示例（蓝图描述）

1.  在任意蓝图（如 `GameMode` 或 `PlayerController`）的 `BeginPlay` 事件中，使用 `Get Concert Replication Subsystem` 节点获取子系统实例。
2.  通过 `Get Concert Replication Client` 节点，传入一个客户端 `FGuid` 标识，获取对应的客户端对象。
3.  使用 `Add Objects to Replication` 节点，将场景中需要同步的 `AActor` 或 `UActorComponent` 指针数组添加到该客户端的复制列表中。
4.  在后续逻辑中，可以使用 `Get Replicated Objects` 或 `Is Object Replicated` 来查询和调试复制状态。

## C++ 用法

### 头文件引入

```cpp
#include "ConcertReplicationSubsystem.h"
```

### 基本用法

以下代码展示了如何在 C++ 中初始化子系统并管理复制对象。

```cpp
// 假设在一个 GameInstance 或 PlayerController 的上下文中
void AMyGameMode::BeginPlay()
{
    Super::BeginPlay();

    // 1. 获取子系统实例
    UConcertReplicationSubsystem* ReplicationSubsystem = GetGameInstance()->GetSubsystem<UConcertReplicationSubsystem>();
    if (!ReplicationSubsystem) return;

    // 2. 定义一个客户端标识（通常来自 Concert 会话管理）
    FGuid MyClientGuid = FGuid::NewGuid();

    // 3. 获取或创建复制客户端
    UConcertReplicationClient* Client = ReplicationSubsystem->GetConcertReplicationClient(MyClientGuid);
    if (!Client) return;

    // 4. 创建一个要复制的对象数组
    TArray<UObject*> ObjectsToReplicate;
    // 假设我们想复制一个名为 ‘MyActor’ 的场景中的Actor
    AActor* MyActor = GetWorld()->SpawnActor<AActor>(AActor::StaticClass());
    if (MyActor)
    {
        ObjectsToReplicate.Add(MyActor);
    }

    // 5. 将对象添加到该客户端的复制流中
    Client->AddObjectsToReplication(ObjectsToReplicate);

    // 后续可以查询
    TArray<UObject*> ReplicatedObjects = Client->GetReplicatedObjects();
    // ...
}
```

### 进阶用法

结合事件和多个客户端，实现更复杂的复制管理逻辑。

```cpp
void AMyReplicationManager::SetupReplicationStreams()
{
    UConcertReplicationSubsystem* Subsystem = GetGameInstance()->GetSubsystem<UConcertReplicationSubsystem>();
    if (!Subsystem) return;

    // 为“场景物体”和“玩家物体”分别创建两个复制流/客户端
    FGuid SceneClientGuid = FGuid::NewGuid();
    FGuid PlayerClientGuid = FGuid::NewGuid();

    UConcertReplicationClient* SceneClient = Subsystem->GetConcertReplicationClient(SceneClientGuid);
    UConcertReplicationClient* PlayerClient = Subsystem->GetConcertReplicationClient(PlayerClientGuid);

    // ... 将不同的对象集合分配给不同的客户端/流
    SceneClient->AddObjectsToReplication(AllEnvironmentActors);
    PlayerClient->AddObjectsToReplication(PlayerOwnedActors);

    // 监听复制状态变化（需在蓝图或 C++ 中绑定相应的委托）
    // 例如：当对象被成功复制或复制失败时执行回调。
}
```

## Demo 示例

一个最小化的、展示基本复制对象管理的游戏模式示例。

**MyReplicationDemoGameMode.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "MyReplicationDemoGameMode.generated.h"

class UConcertReplicationSubsystem;

UCLASS()
class AMyReplicationDemoGameMode : public AGameModeBase
{
	GENERATED_BODY()

public:
	virtual void StartPlay() override;

private:
	UPROPERTY()
	TObjectPtr<AActor> ReplicatedTestActor;

	TObjectPtr<UConcertReplicationSubsystem> ReplicationSubsystem;
};
```

**MyReplicationDemoGameMode.cpp**
```cpp
#include "MyReplicationDemoGameMode.h"
#include "ConcertReplicationSubsystem.h"
#include "Engine/World.h"

void AMyReplicationDemoGameMode::StartPlay()
{
	Super::StartPlay();

	ReplicationSubsystem = GetGameInstance()->GetSubsystem<UConcertReplicationSubsystem>();
	if (!ReplicationSubsystem)
	{
		UE_LOG(LogTemp, Error, TEXT("ConcertReplicationSubsystem not found!"));
		return;
	}

	// 创建一个用于测试复制的 Actor
	ReplicatedTestActor = GetWorld()->SpawnActor<AActor>(AActor::StaticClass());
	if (ReplicatedTestActor)
	{
		ReplicatedTestActor->SetReplicates(true); // 确保 Actor 自身支持复制
		UE_LOG(LogTemp, Log, TEXT("Spawned test actor: %s"), *ReplicatedTestActor->GetName());

		// 模拟一个客户端 ID
		FGuid DemoClientGuid = FGuid::NewGuid();

		// 获取或创建对应的复制客户端，并将对象添加进去
		if (UConcertReplicationClient* Client = ReplicationSubsystem->GetConcertReplicationClient(DemoClientGuid))
		{
			Client->AddObjectsToReplication({ReplicatedTestActor});
			UE_LOG(LogTemp, Log, TEXT("Added actor to replication for client: %s"), *DemoClientGuid.ToString());

			// 立即验证
			bool bIsReplicated = Client->IsObjectReplicated(ReplicatedTestActor);
			UE_LOG(LogTemp, Log, TEXT("Actor replicated status: %s"), bIsReplicated ? TEXT("True") : TEXT("False"));
		}
	}
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Concert` | 核心的多端会话和同步框架。 |
| `ConcertSyncCore` | Concert 同步功能的核心逻辑实现。 |
| `ConcertTransport` | 与 Concert 后端通信的传输层。 |
| `Replication` | 基础的对象复制系统抽象。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了严格浮点模式下 double 常量截断为 float 导致的编译警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移至 `UE_LOGF`。 |
| 2024-06-03 | `c394e7b8` | Refactor FPropertyData to contain the objects for which the properties are being displayed. IPropert... | 重构了 `FPropertyData`，使其包含属性所关联的对象，优化了属性显示逻辑。 |
| 2024-05-01 | `a2b56134` | Slate: Deprecate SListView::ItemHeight and STreeViewItemHeight. ItemHeight and ItemWidth are only us... | Slate UI 更新：废弃了 `SListView::ItemHeight` 和 `STreeViewItemHeight`，统一使用 `ItemWidth`。 |
| 2024-04-11 | `33250188` | Refactor replication UI in preparation of matrix view: | 为矩阵视图重构了复制 UI 做准备。 |

### 维护评价

- **活跃维护**：插件创建于 2023 年底，至今仍有代码维护活动（最近一次为 2026 年 5 月，修复编译警告）。
- **功能稳定**：作为工具链插件，其核心 API（暴露 Concert Replication 功能）已基本稳定，近期的更新主要是代码质量改进、日志系统迁移和 Slate UI 的适配，而非大规模功能变更。
- **推荐使用**：如果你的项目需要在蓝图中与 Unreal 的多端复制系统进行交互，这是一个官方提供的、目的明确的工具插件。虽然近期没有新增重大功能，但持续的维护保证了其与引擎新版本的兼容性。对于需要可视化调试或快速原型开发多端复制逻辑的场景，推荐使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertScripting/ConcertReplicationScripting)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertScripting/ConcertReplicationScripting/Tests)