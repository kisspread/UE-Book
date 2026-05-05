# Async Message System

> Async Message System

| 属性 | 值 |
|---|---|
| 分类 | Framework |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AsyncMessageSystem` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-10-31 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/AsyncMessageSystem) | |

## 用途

Async Message System 是一个**线程安全的异步消息/事件广播系统**，允许在不同线程之间安全地传递消息和数据。它解决的核心问题是：在 UE5 的多线程环境下，游戏逻辑需要一种可靠的方式来跨线程发送和接收信号，而传统的 delegate/事件系统在这方面存在局限。

该系统的设计特点：
- **线程安全**：消息队列使用 `TMpscQueue`（多生产者单消费者队列）和原子操作，支持从任意线程安全地入队消息
- **Payload 复制**：消息数据在入队时会被复制（通过 `FInstancedStruct`），确保监听者在其他线程访问时数据安全
- **层级消息 ID**：基于 `FGameplayTag` 的消息 ID 支持父子层级关系，监听父消息会自动接收子消息
- **绑定端点（Endpoint）**：支持将消息路由到特定端点，实现消息的定向投递
- **灵活的调度选项**：监听者可以选择在特定 Tick Group、命名线程或 Task 优先级线程池中接收消息

## 使用场景

- 你需要在游戏线程和 Worker 线程之间安全地传递事件 → 用 Async Message System
- 你需要一个支持层级关系的消息系统（如监听 `message.colors` 自动接收 `message.colors.red`） → 用 Async Message System
- 你需要将消息定向投递给特定 Actor 或组件（通过 Endpoint） → 用 Async Message System
- 你需要在蓝图中使用异步消息监听（通过 Async Action） → 用 Async Message System

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Queue Async Message for Broadcast` | 入队一条异步消息等待广播 | `UAsyncMessageSystemBlueprintLibrary` |
| `Start Listening for Async Message` | 开始监听指定的异步消息（Async Action） | `UAsyncAction_ListenForAsyncMessage` |
| `Stop Listening for Async Message` | 停止当前 Async Action 的消息监听 | `UAsyncAction_ListenForAsyncMessage` |
| `To String (Async Message Id)` | 将 Message Id 转为字符串 | `UAsyncMessageSystemBlueprintLibrary` |
| `Get Message Native Queue Callstack` | 获取消息入队时的 C++ 调用栈（调试用） | `UAsyncMessageSystemBlueprintLibrary` |
| `Get Message Blueprint Script Callstack` | 获取消息入队时的蓝图脚本调用栈（调试用） | `UAsyncMessageSystemBlueprintLibrary` |

### 使用示例（蓝图描述）

**发送消息**：
1. 创建一个 `FAsyncMessageId`（通过 Gameplay Tag 变量）
2. 创建一个 `FInstancedStruct` 作为 Payload 数据
3. 调用 `Queue Async Message for Broadcast` 节点，传入 World Context、Message Id、Payload 和可选的 Endpoint

**接收消息**：
1. 调用 `Start Listening for Async Message` 节点，传入要监听的 Message Id
2. 在 `On Message Received` 委托引脚上连接后续逻辑
3. 从返回的 `FAsyncMessage` 中提取 Payload 数据
4. 不再需要时调用 `Stop Listening for Async Message` 解除绑定

**组件用法**：
- 添加 `UAsyncMessageBindingComponent` 到 Actor 上，该组件会在 `BeginPlay` 时创建一个专属 Endpoint
- 通过 `IAsyncMessageBindingEndpointInterface` 接口获取 Endpoint，实现消息定向投递给特定 Actor

## C++ 用法

### 头文件引入

```cpp
#include "AsyncMessageSystemBase.h"
#include "AsyncMessage.h"
#include "AsyncMessageId.h"
#include "AsyncMessageWorldSubsystem.h"
```

### 基本用法

**获取消息系统并发送消息**（来源：`AsyncMessageWorldSubsystem.h`）：

```cpp
// 通过 World Subsystem 获取消息系统
TSharedPtr<FAsyncMessageSystemBase> Sys = UAsyncMessageWorldSubsystem::GetSharedMessageSystem(GetWorld());

// 创建消息 ID（基于 Gameplay Tag）
FAsyncMessageId MessageId{FGameplayTag::RequestGameplayTag(TEXT("MyGame.Events.Damage"))};

// 创建 Payload 数据
struct FDamagePayload : public FAsyncMessagePayloadBase
{
    float DamageAmount = 0.f;
    AActor* Instigator = nullptr;
};

FDamagePayload Payload;
Payload.DamageAmount = 50.f;
FInstancedStruct PayloadData = FInstancedStruct::Make<FDamagePayload>(Payload);

// 入队消息
Sys->QueueMessageForBroadcast(MessageId, PayloadData);
```

**绑定监听器 — Lambda**（来源：`AsyncMessageSystemTests.cpp`）：

```cpp
FAsyncMessageHandle Handle = Sys->BindListener(MessageId, [](const FAsyncMessage& Message)
{
    if (const FDamagePayload* Data = Message.GetPayloadData<const FDamagePayload>())
    {
        UE_LOG(LogTemp, Log, TEXT("Damage: %f"), Data->DamageAmount);
    }
});
```

**绑定监听器 — UObject 成员函数**（来源：`AsyncMessageSystemTests.cpp`）：

```cpp
// 自动管理生命周期：当 UObject 被 GC 回收后，监听器自动解除绑定
FAsyncMessageHandle Handle = Sys->BindListener(
    MessageId,
    TWeakObjectPtr<UMyObject>(MyObject),
    &UMyObject::OnDamageReceived
);
```

**绑定监听器 — TSharedPtr 对象**（来源：`AsyncMessageSystemTests.cpp`）：

```cpp
TSharedPtr<FMyListener> Listener = MakeShared<FMyListener>();
FAsyncMessageHandle Handle = Sys->BindListener(
    MessageId,
    Listener.ToWeakPtr(),
    &FMyListener::OnMessageCallback
);
```

**解除绑定**：

```cpp
Sys->UnbindListener(Handle);
```

### 进阶用法

**自定义绑定选项 — 指定 Tick Group**（来源：`AsyncMessageSystemTests.cpp`）：

```cpp
// 在物理模拟前的游戏线程上接收消息
Sys->BindListener(MessageId, MyCallback, FAsyncMessageBindingOptions(ETickingGroup::TG_PrePhysics));

// 在后处理工作完成后接收
Sys->BindListener(MessageId, MyCallback, FAsyncMessageBindingOptions(ETickingGroup::TG_PostUpdateWork));
```

**自定义绑定选项 — 指定命名线程**：

```cpp
// 在高优先级任务线程上接收
Sys->BindListener(MessageId, MyCallback, FAsyncMessageBindingOptions(ENamedThreads::HighTaskPriority));
```

**自定义绑定选项 — 指定 Task 优先级**：

```cpp
// 在后台普通优先级线程池中接收
Sys->BindListener(MessageId, MyCallback,
    FAsyncMessageBindingOptions(UE::Tasks::ETaskPriority::BackgroundNormal, UE::Tasks::EExtendedTaskPriority::None));
```

**自定义 Endpoint — 定向投递**（来源：`AsyncMessageSystemTests.cpp`）：

```cpp
// 创建自定义端点
TSharedPtr<FAsyncMessageBindingEndpoint> CustomEndpoint = MakeShared<FAsyncMessageBindingEndpoint>();

// 绑定到自定义端点
Sys->BindListener(MessageId, MyCallback, {}, CustomEndpoint);

// 发送到自定义端点（只有绑定到该端点的监听者会收到）
Sys->QueueMessageForBroadcast(MessageId, PayloadData, CustomEndpoint);
```

**消息层级关系**（来源：`AsyncMessageSystemTests.cpp`）：

```cpp
// 监听 "AsyncMessages.Internal.test" 会同时收到：
//   - "AsyncMessages.Internal.test" 自身的消息
//   - "AsyncMessages.Internal.test.child" 等子消息
FAsyncMessageId ParentMessage{FGameplayTag::RequestGameplayTag("AsyncMessages.Internal.test")};
Sys->BindListener(ParentMessage, [](const FAsyncMessage& Message)
{
    // Message.GetMessageId() 返回被监听的父消息 ID
    // Message.GetMessageSourceId() 返回实际触发的子消息 ID
    // 如果两者相同，说明就是该消息本身触发的
});
```

**从消息中获取元数据**：

```cpp
Message.GetMessageId();           // 消息 ID
Message.GetMessageSourceId();     // 触发源消息 ID（子消息场景）
Message.GetQueueTimestamp();      // 入队时间戳
Message.GetQueueFrame();          // 入队时的帧号
Message.GetThreadQueuedFromThreadId(); // 入队时的线程 ID
Message.GetSequenceId();          // 同帧内同类型消息的序列号
```

## Demo 示例

### Build.cs 依赖

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "AsyncMessageSystem",
    "GameplayTags",
    "StructUtils",
});
```

### 完整示例

**MyDamageSystem.h**：
```cpp
#pragma once

#include "AsyncMessageSystemBase.h"
#include "AsyncMessageHandle.h"
#include "AsyncMessageId.h"

class FMyDamageSystem
{
public:
    void Init(TSharedPtr<FAsyncMessageSystemBase> InMessageSystem);
    void Shutdown();

    void SendDamageEvent(float DamageAmount);

private:
    void OnDamageReceived(const FAsyncMessage& Message);

    TSharedPtr<FAsyncMessageSystemBase> MessageSystem;
    FAsyncMessageHandle ListenerHandle;
};
```

**MyDamageSystem.cpp**：
```cpp
#include "MyDamageSystem.h"
#include "AsyncMessage.h"
#include "InstancedStruct.h"
#include "NativeGameplayTags.h"

UE_DEFINE_GAMEPLAY_TAG(TAG_MyGame_Damage, "MyGame.Events.Damage");

struct FDamagePayload
{
    GENERATED_BODY()

    UPROPERTY()
    float DamageAmount = 0.f;
};

void FMyDamageSystem::Init(TSharedPtr<FAsyncMessageSystemBase> InMessageSystem)
{
    MessageSystem = InMessageSystem;

    // 绑定监听器
    FAsyncMessageId DamageMessageId{TAG_MyGame_Damage};
    ListenerHandle = MessageSystem->BindListener(
        DamageMessageId,
        [this](const FAsyncMessage& Msg) { OnDamageReceived(Msg); }
    );
}

void FMyDamageSystem::Shutdown()
{
    if (ListenerHandle.IsValid())
    {
        MessageSystem->UnbindListener(ListenerHandle);
    }
}

void FMyDamageSystem::SendDamageEvent(float DamageAmount)
{
    FDamagePayload Payload;
    Payload.DamageAmount = DamageAmount;
    FInstancedStruct PayloadData = FInstancedStruct::Make<FDamagePayload>(Payload);

    FAsyncMessageId DamageMessageId{TAG_MyGame_Damage};
    MessageSystem->QueueMessageForBroadcast(DamageMessageId, PayloadData);
}

void FMyDamageSystem::OnDamageReceived(const FAsyncMessage& Message)
{
    if (const FDamagePayload* Data = Message.GetPayloadData<const FDamagePayload>())
    {
        UE_LOG(LogTemp, Log, TEXT("Received damage: %f"), Data->DamageAmount);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、容器、线程原语 |
| `CoreUObject` | UObject 系统、反射、GC |
| `DeveloperSettings` | 项目设置（`UAsyncMessageDeveloperSettings`） |
| `Engine` | World Subsystem、Tick Function、Gameplay 基础设施 |
| `GameplayTags` | 消息 ID 底层使用 `FGameplayTag` 实现层级关系 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-07-10 | `abb369e` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files | Epic 批量代码修复工具自动应用，无实质功能变化 |
| 2025-06-13 | `185bf17` | Replace some usages of FORCEINLINE with inline in Engine modules | 引擎级别重构，非插件专属改动 |
| 2025-03-03 | `130b2b2` | Fix a crash if an endpoint has gone out of scope | **Bug 修复**：修复了 Endpoint 失效时的崩溃问题 |

### 维护评价

- **创建时间**：2024-10-31，是一个较新的插件（约 1.5 年）
- **实验性标记**：`IsExperimentalVersion=true`，`EnabledByDefault=false`，需要手动在项目设置中启用
- **更新频率**：近半年有实质性 Bug 修复（2025-03-03 修复 Endpoint 崩溃），说明 Epic 内部仍在使用和维护
- **代码质量**：有完善的单元测试和性能测试（独立测试插件），多线程压力测试覆盖充分
- **推荐程度**：适合在需要跨线程消息传递的项目中使用，但需注意其**实验性**状态，API 可能在未来版本中变化

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/AsyncMessageSystem)
- [测试插件源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/AsyncMessageSystemTests)
- [单元测试](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/AsyncMessageSystem/Source/AsyncMessageSystem/Private/Tests/AsyncMessageSystemTests.cpp)
- [性能测试](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/AsyncMessageSystemTests/Source/AsyncMessageSystemTests/Private/AsyncMessageSystemPerformanceTests.cpp)
