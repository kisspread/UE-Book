# Async Message System Tests

> Async Message System Tests

| 属性 | 值 |
|---|---|
| 中文名 | 异步消息系统测试 |
| 分类 | Framework |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资产） |
| 模块 | `AsyncMessageSystemTests` (Runtime) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2024-12-11 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AsyncMessageSystemTests) | |

## 用途

该插件并非一个独立的功能插件，而是**针对 `AsyncMessageSystem` 插件的性能与功能验证测试套件**。它存在的目的是将 `AsyncMessageSystem` 的自动化测试（尤其是性能测试）独立出来，从而避免使 `AsyncMessageSystem` 主插件依赖于 `RuntimeTests` 框架。这使得 `AsyncMessageSystem` 更加轻量，同时又能保证其测试可以在打包的客户端中运行。

通过此插件，开发者可以验证异步消息系统的核心功能，如消息绑定、发送、处理、引用计数以及在不同 Tick 阶段的性能表现。

## 使用场景

- 你是 `AsyncMessageSystem` 插件的**开发者或维护者**，需要运行其性能基准测试和回归测试。
- 你正在修改 `AsyncMessageSystem` 的核心逻辑，希望确保改动不会引入性能退化或功能异常。
- 你想了解如何对 Unreal Engine 的异步消息系统进行压力测试和自动化测试。

## 蓝图用法

该插件中的核心测试类（如 `AASyncMessagePerfTest`）均为隐藏的、不可蓝图化的类，因此不提供蓝图节点。其主要测试逻辑在 C++ 层面通过自动化测试框架驱动。

可供蓝图使用的主要是一些测试数据结构体，用于构造测试负载：

### 核心结构体

| 结构体 | 说明 | 所在模块 |
|---|---|---|
| `FAsyncMessagePerfTestPayload` | 简单的性能测试负载，包含一个指向 `AEngineTestTickActor` 的弱指针。 | `AsyncMessageSystemTests` |
| `FTest_RefCollection_Payload` | 用于测试载荷数据引用计数的负载，包含强引用和弱引用。 | `AsyncMessageSystemTests` |

## C++ 用法

该插件的 C++ 用法主要围绕其自动化测试用例展开。以下代码展示了如何设置一个基于异步消息的性能测试 Actor。

### 头文件引入

```cpp
// 需要同时包含异步消息系统头文件和此插件的测试头文件
#include "AsyncMessageSystem/AsyncMessageSubsystem.h"
#include "AsyncMessageSystemTestsModule.h"
#include "AsyncMessageSystemPerformanceTests.h"
```

### 基本用法（设置性能测试 Actor）

以下代码改编自 `AsyncMessageSystemPerformanceTests.h` 中的类定义，展示如何创建一个监听特定异步消息的测试 Actor。

```cpp
// 来自 Source/AsyncMessageSystemTests/Private/AsyncMessageSystemPerformanceTests.h
// 一个简单的性能测试 Actor
class AASyncMessagePerfTest : public AEngineTestTickActor
{
    GENERATED_BODY()
public:
    // 绑定到特定的消息
    void SetupBindingToMessage(const FAsyncMessageId& MessageToBindTo, const FAsyncMessageBindingOptions& BindingOpts);
    // 消息回调处理函数
    void HandleTestCallback(const FAsyncMessage& Message);

    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    TArray<FAsyncMessageHandle> BoundHandles;
    // ... 其他模拟工作的函数和属性
};
```

### 进阶用法（测试载荷引用计数）

此插件还包含用于测试消息载荷（Payload）生命周期和引用计数的 UObject 子类。

```cpp
// 来自 Source/AsyncMessageSystemTests/Private/AsyncMessageSystemPerformanceTests.h
// 一个用于测试引用计数的 UObject
class UTestRefCollectionObject : public UObject
{
    GENERATED_BODY()
public:
    UPROPERTY()
    int32 TestValue = 5;
};
```

在实际测试中，这些对象会与 `FTest_RefCollection_Payload` 一起使用，通过 `AsyncMessageSubsystem` 发送，并验证在消息处理完成后，载荷中的对象引用是否被正确清理。

## Demo 示例

以下是一个最小化的性能测试 Actor 示例，它会在 `BeginPlay` 时绑定消息，并在 `Tick` 时触发消息发送。

```cpp
// MyAsyncPerfTestActor.h
#pragma once

#include "CoreMinimal.h"
#include "Engine/EngineTestTickActor.h"
#include "AsyncMessageSystem/AsyncMessageTypes.h"
#include "MyAsyncPerfTestActor.generated.h"

UCLASS(NotBlueprintable)
class AMyAsyncPerfTestActor : public AEngineTestTickActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    UPROPERTY()
    FAsyncMessageId TestMessageId;

    FAsyncMessageHandle MessageHandle;

    int32 TickCounter = 0;
};
```

```cpp
// MyAsyncPerfTestActor.cpp
#include "MyAsyncPerfTestActor.h"
#include "AsyncMessageSystem/AsyncMessageSubsystem.h"

void AMyAsyncPerfTestActor::BeginPlay()
{
    Super::BeginPlay();

    // 定义要监听的消息 ID
    TestMessageId = FAsyncMessageId(FName("Demo.PerfTest.Message"));

    // 获取异步消息子系统
    if (UAsyncMessageSubsystem* AMS = UAsyncMessageSubsystem::Get(GetWorld()))
    {
        // 绑定消息，并指定在游戏线程回调
        MessageHandle = AMS->BindMessage(TestMessageId, FAsyncMessageBindingOptions(),
            [this](const FAsyncMessage& Message) {
                UE_LOG(LogTemp, Log, TEXT("Received test message on tick: %d"), TickCounter);
                // 在这里处理消息...
            });
    }
}

void AMyAsyncPerfTestActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    TickCounter++;

    // 每 100 帧发送一条测试消息
    if (TickCounter % 100 == 0)
    {
        if (UAsyncMessageSubsystem* AMS = UAsyncMessageSubsystem::Get(GetWorld()))
        {
            FAsyncMessage Message;
            Message.Id = TestMessageId;
            // 可以在这里填充 Message.Payload
            AMS->SendMessage(Message);
        }
    }
}

void AMyAsyncPerfTestActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    // 解绑消息句柄，避免悬挂引用
    if (UAsyncMessageSubsystem* AMS = UAsyncMessageSubsystem::Get(GetWorld()))
    {
        AMS->UnbindMessage(MessageHandle);
    }

    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

该插件自身的模块 `AsyncMessageSystemTests` 依赖较少，但运行测试需要依赖其他插件。

| 模块 | 用途 |
|---|---|
| `AsyncMessageSystem` | 提供被测的异步消息系统核心功能。 |
| `RuntimeTests` | 提供编写和运行自动化测试用例的框架（如 `IMPLEMENT_SIMPLE_AUTOMATION_TEST`）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 更新日志宏至新版本。 |
| 2025-11-25 | `bf725086` | [Async Message System] Use the new TickTaskManager to process events bound in TickGroups. | 适配主消息系统更新，使用新任务管理器处理 TickGroup 事件。 |
| 2025-07-10 | `abb369e2` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applie… | 为源文件添加内联生成宏，优化编译。 |
| 2025-01-28 | `a5b12c89` | [Async Message System] | 异步消息系统相关的更新。 |
| 2024-12-13 | `2178ce9b` | Add GC reference tracking for Async Message Payload data. | 为异步消息载荷数据添加垃圾回收引用跟踪。 |

### 维护评价

该插件是一个相对较新的测试套件（约2年）。从 Git 记录看，它随着 `AsyncMessageSystem` 主插件的更新而被动维护，例如适配新的日志宏、任务管理器等。最近一次更新（2026年4月）表明它仍被维护以保持与引擎版本的兼容性。

**评价**: 作为 `AsyncMessageSystem` 的官方配套测试，它确保了主插件的质量。虽然功能单一，但维护状态良好。**仅建议引擎开发者或研究该系统的开发者使用**。对于普通内容创作者，此插件无需关注，也无需启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AsyncMessageSystemTests)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AsyncMessageSystemTests/Source/AsyncMessageSystemTests/Private)
- [被测插件：AsyncMessageSystem](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AsyncMessageSystem)