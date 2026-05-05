# MessageBus Tester

> Plugin to test and monitor message bus reliability（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Messaging |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MessageBusTester` (Runtime), `MessageBusTesterEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-11-10 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MessageBusTester) | |

## 用途

该插件是一个用于测试和监控 Unreal Engine 消息总线（Message Bus）系统可靠性的专用工具。它并非面向最终用户的功能插件，而是一个开发者工具，旨在帮助引擎开发者或高级用户验证消息总线在不同网络条件下的性能、稳定性和消息传递的可靠性。

它通过创建一个测试环境，允许用户定义测试计划（如发送特定负载的消息），并监控多个测试实例之间的消息交换情况，从而量化消息传递的延迟、丢包率和吞吐量等关键指标。

## 使用场景

- **引擎开发与测试**：当 Epic 或引擎开发者对消息总线系统（如 `UdpMessaging`）进行修改或优化后，使用此插件进行回归测试，确保改动没有引入性能下降或可靠性问题。
- **网络环境压力测试**：在模拟高延迟、高丢包率的网络环境下，测试消息总线的健壮性。
- **自定义消息通道验证**：在开发依赖消息总线的自定义系统（如自定义 RPC、状态同步）前，先用此工具验证底层通信是否符合预期。

## 蓝图用法

该插件主要面向 C++ 开发，其核心接口 `IMessageBusTester` 和 `IMessageBusTesterLogger` 均为纯虚类，未暴露 `BlueprintCallable` 函数。因此，**无法直接在蓝图中使用**。其功能通过 C++ 模块接口访问。

## C++ 用法

### 头文件引入

```cpp
#include "IMessageBusTesterModule.h"
#include "IMessageBusTester.h"
#include "IMessageBusTesterLogger.h"
```

### 基本用法

通过模块接口获取测试器和日志器实例，并启动测试系统。

```cpp
// 获取 MessageBusTester 模块
IMessageBusTesterModule& TesterModule = FModuleManager::Get().LoadModuleChecked<IMessageBusTesterModule>(TEXT("MessageBusTester"));

// 获取核心测试器和日志器接口
IMessageBusTester& Tester = TesterModule.GetMessageBusTester();
IMessageBusTesterLogger& Logger = TesterModule.GetLogger();

// 启动测试系统（开始发现其他测试实例）
if (Tester.StartSystem())
{
    UE_LOG(LogTemp, Log, TEXT("MessageBus Tester system started."));
}

// 定义一个简单的测试计划项
FTestPlanItem TestItem;
TestItem.PayloadSize = 1024; // 发送 1KB 的负载
TestItem.bIsReliable = true; // 使用可靠传输
TestItem.IterationCount = 10; // 发送 10 次

// 添加测试计划
Tester.AddTestPlanItem(TestItem);

// 开始执行测试
if (Tester.StartTest())
{
    UE_LOG(LogTemp, Log, TEXT("Test started."));
}

// ... 在测试过程中，可以通过 Logger 记录日志
Logger.Log(FName(TEXT("MyTest")), TEXT("Test is running..."), EMessageSeverity::Info);

// 停止测试
Tester.StopTest();
// 停止系统
Tester.StopSystem();
```

### 进阶用法

监听测试器状态变化和日志事件。

```cpp
// 绑定发现测试器列表变化的委托
Tester.OnDiscoveredTesterListChanged().AddLambda([]()
{
    UE_LOG(LogTemp, Log, TEXT("Discovered tester list changed!"));
    // 可以在这里获取最新的测试器列表
    // Tester.GetDiscoveredTesters();
});

// 绑定新日志接收的委托
Logger.OnMessageBusTesterNewLogReceived().AddLambda([](TSharedRef<FMessageBusTesterLogEntry> LogEntry)
{
    UE_LOG(LogTemp, Log, TEXT("[%s] %s"), *LogEntry->Source.ToString(), *LogEntry->LogMessage);
});

// 获取当前测试状态
EMessageBusTesterState CurrentState = Tester.GetState();
if (CurrentState == EMessageBusTesterState::Active)
{
    // 测试正在进行中
}

// 清理已丢失的测试器
Tester.ClearLostTesters();
```

## Demo 示例

一个最小化的控制台应用程序或游戏模块中集成测试的示例。

**MyTestActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "IMessageBusTester.h"
#include "MyTestActor.generated.h"

class IMessageBusTesterLogger;

UCLASS()
class AMyTestActor : public AActor
{
    GENERATED_BODY()

public:
    AMyTestActor();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    void StartMessageBusTest();

    TScriptInterface<IMessageBusTester> MessageBusTester;
    TScriptInterface<IMessageBusTesterLogger> MessageBusLogger;
};
```

**MyTestActor.cpp**
```cpp
#include "MyTestActor.h"
#include "IMessageBusTesterModule.h"

AMyTestActor::AMyTestActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyTestActor::BeginPlay()
{
    Super::BeginPlay();
    StartMessageBusTest();
}

void AMyTestActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (MessageBusTester)
    {
        MessageBusTester->StopTest();
        MessageBusTester->StopSystem();
    }
    Super::EndPlay(EndPlayReason);
}

void AMyTestActor::StartMessageBusTest()
{
    // 加载模块并获取接口
    if (FModuleManager::Get().IsModuleLoaded(TEXT("MessageBusTester")))
    {
        IMessageBusTesterModule& Module = FModuleManager::Get().LoadModuleChecked<IMessageBusTesterModule>(TEXT("MessageBusTester"));
        MessageBusTester = &Module.GetMessageBusTester();
        MessageBusLogger = &Module.GetLogger();

        if (MessageBusTester)
        {
            // 启动系统以发现其他测试实例
            MessageBusTester->StartSystem();

            // 添加一个测试项：发送 512 字节的可靠消息，重复 5 次
            FTestPlanItem Item;
            Item.PayloadSize = 512;
            Item.bIsReliable = true;
            Item.IterationCount = 5;
            MessageBusTester->AddTestPlanItem(Item);

            // 开始测试
            MessageBusTester->StartTest();
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `UdpMessaging` | 提供底层的 UDP 消息传输实现，是本插件进行网络通信的基础。 |
| `Messaging` | Unreal Engine 的核心消息总线框架，本插件在此基础上构建测试功能。 |

## 维护状态

### 近期更新

*（注意：以下为基于插件创建日期的模拟示例，实际 commit 信息需从 git log 获取）*
- 2025-11-10 `a1b2c3d` Initial commit of MessageBusTester plugin for UE 5.8
- 2025-11-10 `e4f5g6h` Add core tester and logger interfaces
- 2025-11-10 `i7j8k9l` Implement discovery and basic test plan logic

### 维护评价

- **创建时间**：2025年11月10日，是一个非常新的插件。
- **实验性状态**：插件明确标记为 `IsBetaVersion=true`，且 `Installed=false`，表明它仍处于实验和开发阶段，API 和功能可能不稳定。
- **维护活跃度**：由于创建时间极短，目前无法判断长期维护趋势。作为 Epic 官方实验性插件，其更新通常与引擎版本发布周期同步。
- **已知限制**：
    1.  仅支持 `MessageBusTesterApp` 程序，通用性有限。
    2.  主要面向 C++，无蓝图支持。
    3.  依赖特定的网络消息插件 (`UdpMessaging`)。
- **推荐使用**：**仅推荐给需要深度测试或调试 Unreal 消息总线系统的引擎开发者或高级用户**。对于普通项目开发，此插件并非必需，且其不稳定性可能带来问题。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MessageBusTester)
- [官方文档]()（暂无）
- [测试用例]()（暂未发现独立的测试文件目录）