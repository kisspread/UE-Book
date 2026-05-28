# Async Message System

> Async Message System

| 属性 | 值 |
|---|---|
| 中文名 | 异步消息系统 |
| 分类 | Framework |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AsyncMessageSystem` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-10-31 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AsyncMessageSystem) | |

## 用途

AsyncMessageSystem 插件提供了一个用于在 Unreal Engine 中不同线程和 Tick Group 之间安全、高效地传递消息和数据的框架。它旨在简化异步工作的协调和同步问题。

**核心解决的问题**：
1.  **跨线程通信**：允许在一个线程上生成数据（例如在工作线程中），并安全地在另一个线程（例如游戏线程）上接收和处理这些数据。
2.  **Tick Group 同步**：允许监听器指定在哪个 Tick Group（如 `TG_PrePhysics`, `TG_PostUpdateWork`）接收消息，确保游戏逻辑的确定性顺序执行。
3.  **消息层次结构**：消息 ID 基于 `FGameplayTag`，支持父-子层次结构。监听父消息可以接收到所有子消息，便于处理大量相关事件。
4.  **生命周期管理**：通过弱引用绑定监听器，当监听对象被销毁时自动解绑，避免野指针和内存泄漏。

## 使用场景

-   你正在编写一个在工作线程上进行复杂物理模拟或 AI 计算的系统，并且需要在主线程的特定 Tick Group 中应用计算结果。
-   你需要构建一个高度模块化的事件系统，其中不同模块（可能运行在不同线程）需要以解耦的方式通信。
-   你的游戏需要处理大量的游戏内事件（如伤害、拾取、技能触发），并且需要一个高性能、可扩展的消息广播和监听机制。
-   你需要一个消息系统，其监听器可以精确控制接收消息的时间点（基于 Tick Group 或任务优先级）。

## 蓝图用法

虽然插件当前主要面向 C++，但已提供了基础的蓝图功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start Listening for Async Message` | 创建一个异步任务来监听指定的消息。返回 `UAsyncAction_ListenForAsyncMessage` 对象，可通过 `StopListeningForAsyncMessage` 停止监听。 | `UAsyncAction_ListenForAsyncMessage` |
| `Queue Async Message for Broadcast` | 将一条消息及其载荷数据排入队列，等待在绑定选项指定的时机进行广播。 | `UAsyncMessageSystemBlueprintLibrary` |
| `To String (Async Message Id)` | 将 `FAsyncMessageId` 转换为字符串表示形式。 | `UAsyncMessageSystemBlueprintLibrary` |
| `Get Message Native/Blueprint Callstack` | （调试用）获取消息被排队时的原生 C++ 或蓝图脚本调用栈。 | `UAsyncMessageSystemBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  **监听消息**：
    *   创建一个 `AsyncAction_ListenForAsyncMessage` 对象。
    *   将其 `On Message Received` 委托连接到你需要处理消息的自定义事件。
    *   调用 `Start Listening for Async Message` 节点，传入要监听的 `FAsyncMessageId` 和期望的 Tick Group。
    *   在不需要监听时，调用 `Stop Listening for Async Message`。

2.  **发送消息**：
    *   使用 `Queue Async Message for Broadcast` 节点。
    *   输入 `MessageId` 和 `Payload`（一个 `FInstancedStruct`，包含你想要传递的数据）。
    *   可以指定一个 `DesiredEndpoint`（通常来自 `UAsyncMessageBindingComponent`），如果留空，则使用默认的世界消息端点。

3.  **组件化端点**：
    *   将 `UAsyncMessageBindingComponent` 添加到你的 Actor。
    *   该组件会自动创建并管理一个专用的 `FAsyncMessageBindingEndpoint`。
    *   在上述蓝图节点中，可以通过 `IAsyncMessageBindingEndpointInterface` 接口将此组件作为端点传入，实现消息路由的隔离。

## C++ 用法

### 头文件引入

```cpp
#include "AsyncMessageSystemBase.h"
#include "AsyncGameplayMessageSystem.h"
#include "AsyncMessageWorldSubsystem.h"
#include "AsyncMessageId.h"
#include "AsyncMessage.h"
#include "AsyncMessageBindingOptions.h"
```

### 基本用法

从测试用例和头文件中提取的基本流程：创建消息系统、绑定监听器、发送消息。
（来源：`AsyncMessageSystemTests.cpp`, `AsyncMessageSystemBase.h`）

```cpp
// 1. 定义你的消息ID和载荷结构
const FAsyncMessageId MyMessageId = FAsyncMessageId(FName("Game.Combat.DamageDealt"));

USTRUCT(BlueprintType)
struct FDamagePayload
{
    GENERATED_BODY()
    UPROPERTY()
    float DamageAmount = 0.0f;
    UPROPERTY()
    AActor* DamageInstigator = nullptr;
};

// 2. 获取或创建消息系统
// 方式A: 使用提供的世界子系统 (推荐用于游戏逻辑)
TSharedPtr<FAsyncGameplayMessageSystem> MsgSystem = UAsyncMessageWorldSubsystem::GetSharedMessageSystem<FAsyncGameplayMessageSystem>(GetWorld());
// 方式B: 自定义创建 (用于测试或特殊需求)
// TSharedPtr<FAsyncMessageSystemBase> MsgSystem = FAsyncMessageSystemBase::CreateMessageSystem<FAsyncMessageSystemBase>();

// 3. 绑定一个监听器 (使用Lambda)
FAsyncMessageHandle Handle = MsgSystem->BindListener(
    MyMessageId,
    [this](const FAsyncMessage& Message)
    {
        // 安全地从载荷中获取数据
        if (const FDamagePayload* Payload = Message.GetPayloadData<FDamagePayload>())
        {
            ApplyDamage(Payload->DamageAmount, Payload->DamageInstigator);
        }
    },
    FAsyncMessageBindingOptions(ETickingGroup::TG_PostPhysics) // 在PostPhysics Tick Group接收
);

// 4. 发送一条消息
FDamagePayload Payload;
Payload.DamageAmount = 15.0f;
Payload.DamageInstigator = SomeActor;
MsgSystem->QueueMessageForBroadcast(MyMessageId, FConstStructView::Make(Payload));

// 5. 解绑监听器 (通常在对象销毁时或不需要时)
MsgSystem->UnbindListener(Handle);
```

### 进阶用法

绑定一个成员函数，当消息触发时，如果持有对象的弱指针有效，则调用该成员函数；如果对象已销毁，则自动解绑。
（来源：`AsyncMessageSystemBase.h` 模板函数）

```cpp
// 绑定到一个UObject的成员函数
FAsyncMessageHandle WeakObjHandle = MsgSystem->BindListener(
    MyDamageMessageId,
    TWeakObjectPtr<AMyActor>(this), // 使用弱对象指针
    &AMyActor::OnDamageReceived, // 成员函数指针
    FAsyncMessageBindingOptions(ETickingGroup::TG_Default) // 使用默认Tick组
);

// 当`this`指向的AMyActor被销毁后，系统会自动解绑`WeakObjHandle`。
```

## Demo 示例

一个完整的、可编译的最小示例，演示如何使用 `UAsyncMessageWorldSubsystem` 发送和接收消息。

```cpp
// MyActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "AsyncMessageId.h"
#include "AsyncMessageHandle.h"
#include "MyActor.generated.h"

UCLASS()
class AMyActor : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    UFUNCTION()
    void OnAsyncEventReceived(const FAsyncMessage& Message);

    FAsyncMessageHandle ListenerHandle;
    FAsyncMessageId EventMessageId;
};
```

```cpp
// MyActor.cpp
#include "MyActor.h"
#include "AsyncMessageWorldSubsystem.h"
#include "AsyncGameplayMessageSystem.h"
#include "AsyncMessage.h"

// 定义载荷结构
USTRUCT()
struct FSimplePayload
{
    GENERATED_BODY()
    UPROPERTY()
    int32 Value = 0;
};

void AMyActor::BeginPlay()
{
    Super::BeginPlay();
    
    // 1. 定义要监听的消息
    EventMessageId = FAsyncMessageId(FName("MySystem.SomeEvent"));
    
    // 2. 获取当前世界的消息系统
    TSharedPtr<FAsyncGameplayMessageSystem> MsgSys = UAsyncMessageWorldSubsystem::GetSharedMessageSystem<FAsyncGameplayMessageSystem>(GetWorld());
    if (MsgSys.IsValid())
    {
        // 3. 绑定监听器
        ListenerHandle = MsgSys->BindListener(
            EventMessageId,
            TWeakObjectPtr<AMyActor>(this),
            &AMyActor::OnAsyncEventReceived,
            FAsyncMessageBindingOptions(ETickingGroup::TG_PostUpdateWork)
        );

        // 4. 模拟：稍后发送一条消息
        FTimerHandle TimerHandle;
        GetWorldTimerManager().SetTimer(TimerHandle, [this, MsgSys]()
        {
            FSimplePayload Payload;
            Payload.Value = 42;
            MsgSys->QueueMessageForBroadcast(EventMessageId, FConstStructView::Make(Payload));
        }, 3.0f, false);
    }
}

void AMyActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    // 5. 清理：解绑监听器
    TSharedPtr<FAsyncGameplayMessageSystem> MsgSys = UAsyncMessageWorldSubsystem::GetSharedMessageSystem<FAsyncGameplayMessageSystem>(GetWorld());
    if (MsgSys.IsValid() && ListenerHandle.IsValid())
    {
        MsgSys->UnbindListener(ListenerHandle);
        ListenerHandle = FAsyncMessageHandle::Invalid;
    }
    Super::EndPlay(EndPlayReason);
}

void AMyActor::OnAsyncEventReceived(const FAsyncMessage& Message)
{
    if (const FSimplePayload* Payload = Message.GetPayloadData<FSimplePayload>())
    {
        UE_LOG(LogTemp, Log, TEXT("Received async message on frame %llu. Value: %d"), Message.GetQueueFrame(), Payload->Value);
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式UE_LOG迁移到新的UE_LOGF宏。 |
| 2026-03-05 | `a3b601d8` | Remove includes guarded by `UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_5`. Delete header files that now | 清理5.5版本中已弃用的头文件包含顺序守卫。 |
| 2025-12-09 | `3702bde1` | [Async Message System] In UAsyncMessageBindingComponent, create the endpoint on Initialize component | 修复了绑定组件在初始化时创建端点，避免在 `BeginPlay` 前使用的问题。 |
| 2025-12-09 | `31afcbe1` | [Async Message System] Remove overzealous ensures about the task sync manager. | 移除了关于任务同步管理器的过于严格的断言检查。 |
| 2025-11-25 | `bf725086` | [Async Message System] Use the new TickTaskManager to process events bound in TickGroups. | 使用新的 TickTaskManager 处理绑定在 TickGroup 上的事件，属于架构性更新。 |

### 维护评价

*   **状态**：**活跃维护中**。插件创建于 2024 年底，至今（2026年4月）仍有持续的功能性更新和优化（如迁移到新日志系统、使用新 TickTaskManager），表明它处于积极开发阶段。
*   **实验性**：插件在 `.uplugin` 中明确标记为 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`，表明其 API 可能尚未完全稳定，未来版本可能会有变动。
*   **功能**：插件提供了从底层 C++ 系统到蓝图异步任务的完整功能链，架构清晰，支持调试选项，具备生产环境使用潜力。
*   **推荐**：如果你的项目确实需要跨线程、跨 Tick Group 的消息通信，并且可以接受其实验性状态，这是一个**值得尝试和跟进**的高质量插件。建议密切跟踪其版本更新日志。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AsyncMessageSystem)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Experimental/AsyncMessageSystem/Source/AsyncMessageSystem/Private/Tests/AsyncMessageSystemTests.cpp)