# Motion Design Scene State Event

> “”（原文无描述，根据源码分析，这是一个用于处理场景状态事件的运行时模块）

| 属性 | 值 |
|---|---|
| 中文名 | 场景状态事件 |
| 分类 | Experimental |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `SceneStateEvent` (Runtime) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2025-08-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/SceneState/Source/SceneStateEvent) | |

## 用途

`SceneStateEvent` 模块是 Motion Design 场景状态插件的核心事件系统。它提供了一个轻量级、可序列化的事件总线架构，允许场景中的不同组件和系统之间松耦合地进行通信。

该模块解决的核心问题是：在复杂的虚拟制片（Virtual Production）场景中，如何标准化、可靠地传递事件和状态变更通知。通过定义统一的“事件模式（Event Schema）”并使用“事件流（Event Stream）”作为中转，它可以确保事件数据的类型安全和一致性，避免了直接调用或接口绑定带来的紧耦合问题。这对于管理大型、动态的 Motion Design 场景至关重要。

## 使用场景

-   你在构建一个交互式的虚拟制片场景，需要根据用户输入、时间轴事件或物理触发器来同步控制多个灯光、粒子和动画 Actor。
-   你需要在不同的蓝图脚本或 C++ 系统之间传递带参数的自定义事件，而不希望它们直接相互引用。
-   你希望实现一个事件“回放”或“捕获”机制，用于调试或创建复杂的交互序列。

## 蓝图用法

核心蓝图节点主要通过 `USceneStateEventLibrary` 提供，所有节点均在 `Scene State | Event` 分类下。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Push Event` | 向指定的事件流中推送一个事件 | `USceneStateEventLibrary` |
| `Broadcast Event` | 向整个世界中的所有已注册事件流广播一个事件 | `USceneStateEventLibrary` |
| `Find Event` | 在事件流中查找特定模式的事件 | `USceneStateEventLibrary` |
| `Has Event` | 检查事件流中是否存在特定模式的事件 | `USceneStateEventLibrary` |
| `Event Data To Struct` | 将事件数据（`FInstancedStruct`）转换为具体的结构体类型 | `USceneStateEventLibrary` |

### 使用示例（蓝图描述）

1.  **初始化事件流**：在你的 Actor 或组件的“BeginPlay”事件中，创建一个 `USceneStateEventStream` 对象，并调用其 `Register` 函数将其注册到全局事件子系统。
2.  **定义与触发事件**：
    *   在编辑器中创建 `USceneStateEventSchemaObject` 资产来定义事件的模式（例如，一个名为 `LightToggleEvent` 的事件，其结构体包含一个布尔型 `bIsOn` 字段）。
    *   在蓝图中，使用“Create Event Template”节点（或直接构建 `FInstancedStruct`）准备事件数据。
    *   调用 `Push Event` 节点，将事件数据推送到你希望的事件流中；或者使用 `Broadcast Event` 节点向世界广播。
3.  **响应事件**：
    *   在需要响应事件的 Actor 或组件中，持有对同一个 `USceneStateEventStream` 对象的引用。
    *   使用 `Find Event` 或 `Has Event` 节点（配合 `FSceneStateEventHandler`）来检查是否有匹配的事件到达。
    *   如果找到事件，可以使用 `Event Data To Struct` 节点将事件数据转换回 `LightToggleEvent` 结构体，并读取其中的值来执行相应逻辑。

## C++ 用法

### 头文件引入

```cpp
#include "SceneStateEventUtils.h" // 核心工具函数
#include "SceneStateEventStream.h" // 事件流
#include "SceneStateEventSchemaHandle.h" // 事件模式句柄
```

### 基本用法：创建事件流并处理单个事件

以下示例展示了如何创建事件流、推送一个事件并消费它。

```cpp
// 某个 Actor 或组件的头文件中
UPROPERTY()
TObjectPtr<USceneStateEventStream> MyEventStream;

// BeginPlay 中初始化
void AMyActor::BeginPlay()
{
    Super::BeginPlay();
    MyEventStream = NewObject<USceneStateEventStream>(this);
    MyEventStream->Register(); // 注册到全局子系统以接收广播事件
}

// 推送一个自定义事件（假设已有一个 FMyCustomEvent 结构体和对应的事件模式句柄 SchemaHandle）
void AMyActor::TriggerCustomEvent(const FSceneStateEventSchemaHandle& InSchemaHandle, const FMyCustomEvent& InPayload)
{
    FInstancedStruct EventData;
    EventData.InitializeAs<FMyCustomEvent>(InPayload);
    
    // 使用工具函数推送事件
    UE::SceneState::PushEvent(MyEventStream, InSchemaHandle, MoveTemp(EventData));
}

// Tick 或其他合适的地方检查并消费事件
void AMyActor::CheckForEvents()
{
    // SchemaHandle 是对特定事件模式的引用
    if (MyEventStream && MyEventStream->ConsumeEventBySchema(MySchemaHandle))
    {
        // 事件已消费，执行相应逻辑
        UE_LOG(LogTemp, Log, TEXT("Custom event consumed!"));
    }
}
```

**来源**：`Public/SceneStateEventUtils.h`, `Public/SceneStateEventStream.h`

### 进阶用法：使用事件处理器捕获特定事件

事件处理器 (`FSceneStateEventHandler`) 允许你绑定到特定的事件实例，用于更精确的事件捕获和查询。

```cpp
// 头文件中
FSceneStateEventHandler MyEventHandler;
FSceneStateEventSchemaHandle TargetEventSchema;

// 初始化处理器（通常在构造函数或Initialize中）
AMyActor::AMyActor()
{
    // 初始化处理器会生成唯一ID
    MyEventHandler = FSceneStateEventHandler(EForceInit);
    TargetEventSchema = /* 从数据资产或其他地方加载 */;
}

// 将处理器与事件流关联，尝试捕获匹配事件
void AMyActor::AttemptCaptureEvent()
{
    // 假设 MyEventStream 已存在并注册
    MyEventStream->CaptureEvents({MyEventHandler});
    
    // 查询是否有事件被此处理器捕获
    FSceneStateEvent* CapturedEvent = MyEventStream->FindCapturedEvent(MyEventHandler.GetHandlerId());
    if (CapturedEvent)
    {
        FConstStructView EventData = CapturedEvent->GetDataView();
        // 处理事件数据...
    }
}
```

**来源**：`Public/SceneStateEventHandler.h`, `Public/SceneStateEventStream.h`

## Demo 示例

一个最小化的 C++ 示例，演示如何定义事件模式、创建事件流、推送并消费一个简单事件。

```cpp
// MySceneStateDemo.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SceneStateEventStream.h"
#include "SceneStateEventSchemaHandle.h"
#include "MySceneStateDemo.generated.h"

UCLASS()
class AMySceneStateDemo : public AActor
{
    GENERATED_BODY()

public:
    AMySceneStateDemo();

protected:
    virtual void BeginPlay() override;

public:
    virtual void Tick(float DeltaTime) override;

private:
    UPROPERTY()
    TObjectPtr<USceneStateEventStream> EventStream;

    // 事件模式句柄，指向一个预先创建的、名为“PingEvent”的USceneStateEventSchemaObject资产
    UPROPERTY(EditAnywhere, Category="Event")
    FSceneStateEventSchemaHandle PingEventSchemaHandle;

    void GeneratePingEvent();
    void ConsumePingEvent();
};
```

```cpp
// MySceneStateDemo.cpp
#include "MySceneStateDemo.h"
#include "SceneStateEventUtils.h"

AMySceneStateDemo::AMySceneStateDemo()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AMySceneStateDemo::BeginPlay()
{
    Super::BeginPlay();

    // 创建并注册事件流
    EventStream = NewObject<USceneStateEventStream>(this);
    EventStream->Register();
}

void AMySceneStateDemo::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    // 每隔一段时间生成一个Ping事件
    static float TimeAccumulator = 0.0f;
    TimeAccumulator += DeltaTime;
    if (TimeAccumulator > 2.0f)
    {
        GeneratePingEvent();
        TimeAccumulator = 0.0f;
    }

    // 持续检查并消费事件
    ConsumePingEvent();
}

void AMySceneStateDemo::GeneratePingEvent()
{
    if (!PingEventSchemaHandle.GetEventSchema() || !EventStream)
    {
        return;
    }

    // 推送一个无参数的Ping事件
    FInstancedStruct EmptyData;
    UE::SceneState::PushEvent(EventStream, PingEventSchemaHandle, MoveTemp(EmptyData));
    UE_LOG(LogTemp, Log, TEXT("Ping event pushed."));
}

void AMySceneStateDemo::ConsumePingEvent()
{
    if (!PingEventSchemaHandle.GetEventSchema() || !EventStream)
    {
        return;
    }

    // 尝试消费事件
    if (EventStream->ConsumeEventBySchema(PingEventSchemaHandle))
    {
        UE_LOG(LogTemp, Log, TEXT("Ping event consumed!"));
        // 在这里执行响应Ping的逻辑
    }
}
```

## 模块依赖

该模块 (`SceneStateEvent`) 的 `Build.cs` 未在信息中提供，但根据其公开的头文件和功能，可以推断其核心依赖。无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口相关改动，间接影响事件系统通知机制。 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回滚了一个提交，可能是与事件系统相关的变更。 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 同`cfb610df`，视口逻辑重构。 |
| 2026-04-17 | `6e111b5d` | Motion Design Scene State: fixed issues with bindings not checking for null event payload struct (op | **关键修复**：修复了数据绑定未检查事件负载结构体是否为空的问题，增强了稳定性。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的日志宏迁移到新的`UE_LOGF`，是维护性改动。 |

### 维护评价

`SceneStateEvent` 模块是活跃维护中的较新模块。

-   **创建时间**：创建于 2025 年 8 月，非常年轻。
-   **更新频率**：在最近的 1 个月内有多次提交，包括功能修复和日志系统更新。
-   **活跃度**：**活跃维护**。最新的提交修复了一个重要的空指针检查缺陷，表明开发团队正在积极打磨此模块。
-   **已知问题/限制**：作为实验性（Beta）插件的一部分，其 API 未来可能存在变动。事件模式的管理（创建、查找）依赖于编辑器资产，在纯运行时蓝图中可能存在不便。
-   **推荐度**：**推荐在虚拟制片和Motion Design项目中探索使用**。它为解决复杂场景中的事件通信提供了标准化的框架，且维护状态良好。但鉴于其Beta状态，不建议用于对稳定性要求极高的生产环境。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/SceneState/Source/SceneStateEvent)