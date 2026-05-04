# Async Message System Tests

> Async Message System Tests

| 属性 | 值 |
|---|---|
| 分类 | Framework |
| 默认启用 | false |
| 包含内容 | true |
| 模块 | AsyncMessageSystemTests (Runtime) |
| 创建时间 | 2024-12-11 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/AsyncMessageSystemTests) | |

## 用途

这是 [AsyncMessageSystem](../AsyncMessageSystem/index.md) 的**性能与功能测试插件**。它不是一个提供运行时 API 的工具型插件，而是一个纯粹的测试插件，用于验证异步消息系统的性能表现和正确性。

插件包含以下测试用例：

1. **单消息广播性能测试** — 在游戏线程上创建大量 Actor，绑定单个消息并逐帧广播，测量消息系统调度开销
2. **多消息广播性能测试** — 同时绑定并广播多个不同消息，测试消息系统在多消息并发时的性能
3. **多线程消息广播性能测试** — 从多个后台线程同时排队消息，测试消息系统的线程安全性和并发性能
4. **Payload 引用追踪测试** — 验证消息队列中的 `UPROPERTY` 引用不会被垃圾回收器提前回收

这些测试属于 Unreal 自动化测试框架（Automation Test），可以通过编辑器中的 Session Frontend 或命令行运行。

## 使用场景

- 你是 AsyncMessageSystem 的开发者或贡献者，需要验证消息系统的正确性和性能
- 你在项目中大量使用 AsyncMessageSystem，需要基准测试来评估不同场景下的消息系统开销
- 你在学习 AsyncMessageSystem 的使用方式，想通过测试代码了解 API 的实际调用模式

## 蓝图用法

此插件不提供任何蓝图可调用接口。它完全由 C++ 自动化测试组成。

## C++ 用法

此插件的源码本身就是学习 AsyncMessageSystem API 的最佳示例。以下是从测试代码中提取的关键用法。

### 头文件引入

```cpp
#include "AsyncMessageSystemBase.h"
#include "AsyncMessageHandle.h"
#include "AsyncGameplayMessageSystem.h"
#include "AsyncMessageWorldSubsystem.h"
#include "NativeGameplayTags.h"
```

### 基本用法 — 获取消息系统实例

通过 `UAsyncMessageWorldSubsystem` 获取绑定到当前 World 的共享消息系统：

```cpp
// 获取共享消息系统（TSharedPtr）
TSharedPtr<FAsyncGameplayMessageSystem> MessageSys =
    UAsyncMessageWorldSubsystem::GetSharedMessageSystem<FAsyncGameplayMessageSystem>(GetWorld());
check(MessageSys.IsValid());
```

> 来源: `AsyncMessageSystemPerformanceTests.cpp` — `AASyncMessagePerfTest::SetupBindingToMessage()`

### 基本用法 — 绑定消息监听器

使用 Gameplay Tag 定义消息 ID，然后绑定监听器：

```cpp
// 定义消息 ID（使用 Gameplay Tag）
UE_DEFINE_GAMEPLAY_TAG_COMMENT(TestMessage_RunVirtualTick,
    "AsyncMessages.Internal.test.RunVirtualTick",
    "A test gameplay tag for the async message system");
const FAsyncMessageId RunVirtualTickMessageId = { TestMessage_RunVirtualTick };

// 绑定监听器 — 使用成员函数回调
FAsyncMessageBindingOptions BindingOptions;
BindingOptions.SetTickGroup(TG_PrePhysics);

const FAsyncMessageHandle Handle = MessageSys->BindListener(
    RunVirtualTickMessageId,
    TWeakObjectPtr<AASyncMessagePerfTest>(this),
    &AASyncMessagePerfTest::HandleTestCallback,
    BindingOptions
);
ensure(Handle.IsValid());
BoundHandles.Emplace(Handle);
```

> 来源: `AsyncMessageSystemPerformanceTests.cpp` — `AASyncMessagePerfTest::SetupBindingToMessage()`

### 基本用法 — Lambda 回调绑定

也可以使用 Lambda 绑定监听器，通过后台线程执行回调：

```cpp
FAsyncMessageBindingOptions BindOptions;
BindOptions.SetNamedThread(ENamedThreads::HighTaskPriority);

const FAsyncMessageHandle Handle = MessageSys->BindListener(
    SomeMessageId,
    [WeakActor = TWeakObjectPtr<AMyActor>(this)](const FAsyncMessage& Message)
    {
        if (WeakActor.IsValid())
        {
            WeakActor->DoSomeWork();
        }
    },
    BindOptions
);
```

> 来源: `AsyncMessageSystemPerformanceTests.cpp` — 多线程性能测试

### 基本用法 — 广播消息

构造 payload 数据并排队广播：

```cpp
// 构造 payload
FAsyncMessagePerfTestPayload PayloadData;
PayloadData.bDoLessWork = true;
FConstStructView PayloadView = FConstStructView::Make<FAsyncMessagePerfTestPayload>(PayloadData);

// 排队广播（消息会在同一帧内分发给所有监听器）
MessageSys->QueueMessageForBroadcast(RunVirtualTickMessageId, PayloadView);
```

> 来源: `AsyncMessageSystemPerformanceTests.cpp` — `TMessageSystemPerformance_BroadcastingMessages::RunTest()`

### 基本用法 — 接收消息与提取 Payload

在回调中提取 payload 数据：

```cpp
void HandleTestCallback(const FAsyncMessage& Message)
{
    if (const FAsyncMessagePerfTestPayload* Data =
        Message.GetPayloadData<const FAsyncMessagePerfTestPayload>())
    {
        // 使用 payload 数据
        if (Data->bDoLessWork)
        {
            DoSimpleWork();
        }
        else
        {
            DoHeavyWork();
        }
    }
}
```

> 来源: `AsyncMessageSystemPerformanceTests.cpp` — `AASyncMessagePerfTest::HandleTestCallback()`

### 基本用法 — 取消绑定

在 `EndPlay` 时取消所有绑定：

```cpp
void AASyncMessagePerfTest::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    Super::EndPlay(EndPlayReason);

    auto Sys = UAsyncMessageWorldSubsystem::GetSharedMessageSystem(GetWorld());
    if (Sys.IsValid())
    {
        for (const FAsyncMessageHandle& BoundHandle : BoundHandles)
        {
            Sys->UnbindListener(BoundHandle);
        }
    }
}
```

> 来源: `AsyncMessageSystemPerformanceTests.cpp` — `AASyncMessagePerfTest::EndPlay()`

### 进阶用法 — 多线程消息广播

从后台线程排队消息，利用 UE::Tasks 系统：

```cpp
// 从后台线程排队消息
struct FQueueMessageFromBackgroundThread
{
    TSharedPtr<FAsyncGameplayMessageSystem> MessageSystem;
    FAsyncMessageId MessageToQueue;
    FConstStructView PayloadDataView;

    void operator()()
    {
        if (MessageSystem.IsValid() && MessageToQueue.IsValid())
        {
            MessageSystem->QueueMessageForBroadcast(MessageToQueue, PayloadDataView);
        }
    }
};

// 启动后台任务
UE::Tasks::FTask T = UE::Tasks::Launch(
    UE_SOURCE_LOCATION,
    FQueueMessageFromBackgroundThread {
        .MessageSystem = MessageSys,
        .MessageToQueue = SomeMessageId,
        .PayloadDataView = PayloadView
    },
    UE::Tasks::ETaskPriority::Normal,
    UE::Tasks::EExtendedTaskPriority::None);

PendingTasks.Push(T);

// 等待所有任务完成
UE::Tasks::Wait(PendingTasks);
```

> 来源: `AsyncMessageSystemPerformanceTests.cpp` — `TMessageSystemPerformance_BroadcastSeveralMessagesMultithread::RunTest()`

### 进阶用法 — 不同 Tick Group 分配

将监听器均匀分配到 6 个 Tick Group，模拟真实游戏场景：

```cpp
FAsyncMessageBindingOptions BindingOptions;
BindingOptions.SetTickGroup(TG_PrePhysics);      // 或 TG_StartPhysics, TG_DuringPhysics,
                                                  //    TG_EndPhysics, TG_PostPhysics,
                                                  //    TG_PostUpdateWork
```

> 来源: `AsyncMessageSystemPerformanceTests.cpp` — `AddBindingsToAllTestActors()`

### 进阶用法 — 消息层级（Parent Tag）

消息系统支持 Tag 层级。绑定父 Tag 可以接收到子 Tag 广播的消息：

```cpp
// 绑定消息 ID 及其父 Tag
AddBindingsToAllTestActors({
    RunVirtualTickMessageId,
    RunVirtualTickMessageId.GetParentMessageId()   // 父 Tag 也会被触发
});
```

> 来源: `AsyncMessageSystemPerformanceTests.cpp` — `TMessageSystemPerformance_BroadcastingMessages::RunTest()`

## 测试运行说明

### 通过编辑器运行

1. 启用插件: **Edit → Plugins → 搜索 "AsyncMessageSystemTests" → 启用 → 重启编辑器**
2. 打开 Session Frontend: **Window → Developer Tools → Session Frontend**
3. 切换到 **Automation** 标签页
4. 搜索 `AsyncMessagePassing` 相关测试
5. 选择测试并点击 **Start**

### 通过控制台命令运行

```
Automation RunTests AsyncMessagePassing
```

或单独运行性能测试：

```
Automation RunTests AsyncMessagePassing.Performance
```

### 可调参数（CVar）

| CVar | 默认值 | 说明 |
|---|---|---|
| `AsyncMessageSystem.Tests.Performance.ActorCount` | 4000 | 性能测试中生成的 Actor 数量 |
| `AsyncMessageSystem.Tests.Performance.TickCount` | 2000 | 性能测试中模拟的帧数 |

> 通过控制台命令修改：`AsyncMessageSystem.Tests.Performance.ActorCount 1000`

## Demo 示例

此插件本身没有可独立运行的 Demo。它是一个纯测试插件，需要通过自动化测试框架运行。

如果你想在自己的项目中编写类似的 AsyncMessageSystem 测试，可以参考以下最小示例：

### Build.cs 依赖

```csharp
PublicDependencyModuleNames.AddRange(
    new string[] {
        "AsyncMessageSystem",
        "Core",
        "CoreUObject",
        "Engine",
        "GameplayTags",
    }
);
```

### 测试代码示例

```cpp
#include "AsyncMessageWorldSubsystem.h"
#include "AsyncGameplayMessageSystem.h"
#include "NativeGameplayTags.h"

UE_DEFINE_GAMEPLAY_TAG(MyTestMessage, "MyGame.Test.Message");
static const FAsyncMessageId TestMessageId = { MyTestMessage };

// 定义 payload
struct FMyTestPayload
{
    int32 Value = 0;
};

// 在测试中使用
void FMyTest::RunTest()
{
    auto World = /* 获取测试 World */;
    auto MsgSys = UAsyncMessageWorldSubsystem::GetSharedMessageSystem<FAsyncGameplayMessageSystem>(World);

    // 绑定
    FAsyncMessageBindingOptions Opts;
    FAsyncMessageHandle Handle = MsgSys->BindListener(TestMessageId,
        [](const FAsyncMessage& Msg)
        {
            if (auto* Data = Msg.GetPayloadData<FMyTestPayload>())
            {
                // 处理消息
            }
        }, Opts);

    // 广播
    FMyTestPayload Payload{ .Value = 42 };
    FConstStructView View = FConstStructView::Make<FMyTestPayload>(Payload);
    MsgSys->QueueMessageForBroadcast(TestMessageId, View);

    // 取消绑定
    MsgSys->UnbindListener(Handle);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AsyncMessageSystem` | 被测目标：异步消息系统核心模块 |
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 系统（GC、反射等） |
| `Engine` | 引擎运行时（World、Actor 等） |
| `GameplayTags` | Gameplay Tag 系统（消息 ID 基于 Tag） |
| `RuntimeTests` | UE 运行时测试基础设施（FEngineTestTickBase 等） |

### 插件依赖

| 插件 | 用途 |
|---|---|
| `AsyncMessageSystem` | 被测目标插件 |
| `RuntimeTests` | 提供运行时自动化测试基类 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-07-10 | `abb369e2fd63` | 添加 `UE_INLINE_GENERATED_CPP_BY_NAME` 宏（自动化工具批量应用，非实质性改动） |
| 2025-01-28 | `a5b12c89e44e` | Async Message System 相关更新（具体 message 改动） |
| 2024-12-13 | `2178ce9b1a3b` | 新增 GC 引用追踪测试 — 验证消息队列中的 UPROPERTY 引用不会被垃圾回收 |

### 维护评价

- **创建时间**: 2024-12-11，约 1.4 年历史
- **最近更新**: 2025-07-10（约 10 个月前），但最后一次实质性更新在 2025-01-28
- **状态**: 实验性插件 (`IsExperimentalVersion: true`)，默认禁用
- **评估**: 维护不活跃。作为 AsyncMessageSystem 的测试配套插件，它的更新频率取决于主插件的变化。代码中设置了 `Experimental` 标记，尚处于试验阶段。3 次 commit 中只有 2 次是实质性改动（GC 引用追踪、系统更新），说明功能相对稳定，但开发团队不频繁维护测试代码。
- **是否推荐**: 如果你使用 AsyncMessageSystem，可以参考其测试代码来学习 API 用法；不建议在生产环境中依赖此插件。

## 相关链接

- [AsyncMessageSystemTests 源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/AsyncMessageSystemTests)
- [AsyncMessageSystem 主插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/AsyncMessageSystem)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/AsyncMessageSystemTests/Source/AsyncMessageSystemTests/Private/AsyncMessageSystemPerformanceTests.cpp)
