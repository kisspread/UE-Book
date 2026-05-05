# Motion Design Scene State

> 

| 属性 | 值 |
|---|---|
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、事件模式） |
| 模块 | `SceneState` (Runtime), `SceneStateBinding` (Runtime), `SceneStateBlueprint` (Runtime), `SceneStateBlueprintEditor` (Runtime), `SceneStateEditor` (Runtime), `SceneStateEvent` (Runtime), `SceneStateEventEditor` (Runtime), `SceneStateEventGraph` (Runtime), `SceneStateGameplay` (Runtime), `SceneStateGameplayEditor` (Runtime), `SceneStateMachineEditor` (Runtime), `SceneStateMachineGraph` (Runtime), `SceneStateTasks` (Runtime), `SceneStateTransitionGraph` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/SceneState) | |

## 用途

SceneState 是一个用于虚拟制作（Virtual Production）和 Motion Design 的场景状态管理与事件驱动系统。它旨在解决复杂场景中，不同元素（如灯光、动画、材质、几何体等）需要根据时间线、用户交互或逻辑条件进行状态切换和同步的问题。该插件提供了一套框架，允许用户定义场景状态、状态之间的转换，以及在这些状态变化时触发的事件，从而实现对场景元素的精确、可编程控制。

## 使用场景

-   **虚拟制作**：在电影或电视制作的虚拟场景中，需要根据拍摄脚本或导演指令，实时切换场景的灯光氛围、背景元素、角色动画状态等。
-   **Motion Design**：在动态图形设计中，需要创建复杂的、基于时间线的动画序列，其中多个视觉元素需要同步变化。
-   **交互式体验**：在展览、主题公园或游戏内场景中，需要根据用户的输入或游戏逻辑，动态改变场景的视觉表现。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Push Event` | 向指定的事件流（Event Stream）推送一个事件。 | `USceneStateEventLibrary` |
| `Broadcast Event` | 向一个世界（World）范围内所有已注册的事件流广播一个事件。 | `USceneStateEventLibrary` |
| `Find Event` | 在事件流中查找一个匹配指定模式的事件（可以是已捕获的或仅推送的）。 | `USceneStateEventLibrary` |
| `Has Event` | 检查事件流中是否存在一个匹配指定模式的事件。 | `USceneStateEventLibrary` |
| `Event Data To Struct` | 将事件数据（InstancedStruct）转换为通配符结构体类型。 | `USceneStateEventLibrary` |

### 使用示例（蓝图描述）

1.  **定义事件模式**：首先，需要在内容浏览器中创建 `SceneStateEventSchemaCollection` 资产，并在其中添加 `SceneStateEventSchemaObject` 来定义事件的名称和可选的数据结构。
2.  **创建事件流**：在场景中的某个Actor（例如一个管理器Actor）上，添加一个 `SceneStateEventStream` 组件。
3.  **推送事件**：在蓝图中，使用 `Push Event` 节点，将事件流组件作为输入，并指定之前定义的事件模式句柄（`FSceneStateEventSchemaHandle`）和可选的事件数据。
4.  **监听与处理事件**：在其他需要响应事件的Actor或蓝图中，同样使用事件流组件，并通过 `Find Event` 或 `Has Event` 节点来检查特定事件是否发生，然后执行相应的逻辑（如改变材质、播放动画等）。

## C++ 用法

### 头文件引入

```cpp
#include "SceneStateEvent.h"
#include "SceneStateEventSchema.h"
#include "SceneStateEventStream.h"
#include "SceneStateEventUtils.h"
```

### 基本用法

以下示例展示了如何在 C++ 中创建事件模式并推送事件。

```cpp
// 假设你已经有一个 USceneStateEventStream* EventStream 指针
// 以及一个指向 USceneStateEventSchemaObject 的指针 EventSchema

// 1. 创建事件数据（如果事件模式定义了结构体）
FInstancedStruct EventData;
// EventData.InitializeAs<FMyEventPayload>(...); // 填充数据

// 2. 推送事件到流
bool bSuccess = UE::SceneState::PushEvent(EventStream, EventSchema->Id, MoveTemp(EventData));
```

### 进阶用法

以下示例展示了如何广播事件，使其被世界中所有相关的事件流接收。

```cpp
// 在某个 UObject（如 Actor）的上下文中广播事件
UObject* ContextObject = this; // 当前对象
FSceneStateEventSchemaHandle EventSchemaHandle;
EventSchemaHandle.EventSchema = EventSchemaSoftRef; // 设置软引用

FInstancedStruct EventData;
// ... 初始化 EventData ...

// 广播事件
bool bBroadcasted = UE::SceneState::BroadcastEvent(ContextObject, EventSchemaHandle, MoveTemp(EventData));
```

## Demo 示例

以下是一个最小化的 C++ 示例，演示如何定义一个事件模式类并使用事件流。

**MySceneStateEventDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SceneStateEventSchemaHandle.h"
#include "MySceneStateEventDemo.generated.h"

class USceneStateEventStream;
class USceneStateEventSchemaObject;

UCLASS()
class MYPROJECT_API AMySceneStateEventDemo : public AActor
{
	GENERATED_BODY()
	
public:	
	AMySceneStateEventDemo();

protected:
	virtual void BeginPlay() override;

public:	
	virtual void Tick(float DeltaTime) override;

private:
	UPROPERTY(VisibleAnywhere)
	TObjectPtr<USceneStateEventStream> EventStream;

	// 事件模式句柄，用于引用在编辑器中创建的事件模式资产
	UPROPERTY(EditAnywhere, Category = "Events")
	FSceneStateEventSchemaHandle TestEventHandle;

	// 一个简单的计时器，用于定期推送测试事件
	float EventTimer = 0.0f;
};
```

**MySceneStateEventDemo.cpp**
```cpp
#include "MySceneStateEventDemo.h"
#include "SceneStateEventStream.h"
#include "SceneStateEventUtils.h"

AMySceneStateEventDemo::AMySceneStateEventDemo()
{
	PrimaryActorTick.bCanEverTick = true;
	EventStream = CreateDefaultSubobject<USceneStateEventStream>(TEXT("EventStream"));
}

void AMySceneStateEventDemo::BeginPlay()
{
	Super::BeginPlay();
	// 注册事件流以接收广播事件
	EventStream->Register();
}

void AMySceneStateEventDemo::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	EventTimer += DeltaTime;
	if (EventTimer >= 2.0f) // 每2秒推送一次事件
	{
		EventTimer = 0.0f;

		// 推送一个事件到自己的事件流
		// 注意：这里假设 TestEventHandle 已经在编辑器中正确设置
		UE::SceneState::PushEvent(EventStream, TestEventHandle, FInstancedStruct());
	}
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `StructUtils` | 提供 `FInstancedStruct` 和 `FSharedStruct` 等高级结构体工具，用于事件数据的动态类型存储。 |

## 维护状态

### 近期更新

-   2025-04-22 94f961385e8e Motion Design: Moved scene state and data link plugins out of experimental into virtualproduction

### 维护评价

该插件创建于 2025 年 4 月，非常新。从唯一的 git 提交记录来看，它刚刚从 `Experimental` 目录移动到 `VirtualProduction` 目录，这表明它可能正处于从实验性功能向正式虚拟制作工具过渡的阶段。目前没有更多的更新历史，无法判断其长期维护频率。

**综合评价**：
-   **状态**：实验性（Beta），且刚完成一次重要的目录迁移。
-   **活跃度**：由于历史记录极少，无法判断是否活跃维护。
-   **推荐度**：**谨慎使用**。该插件功能明确，架构清晰，适用于虚拟制作和 Motion Design 的特定需求。但由于其“实验性”标签和极短的公开历史，它可能尚未稳定，API 和功能在未来版本中可能发生重大变化。建议仅在可以接受这些风险的项目或原型开发中使用，并密切关注后续版本更新。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/SceneState)
-   [官方文档]() （暂无）
-   [测试用例]() （暂未在提供的路径中发现明确的测试文件）