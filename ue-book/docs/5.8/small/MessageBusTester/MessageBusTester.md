# MessageBus Tester

> Plugin to test and monitor message bus reliability

| 属性 | 值 |
|---|---|
| 中文名 | 消息总线测试器 |
| 分类 | Messaging |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MessageBusTester` (Runtime), `MessageBusTesterEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-10-24 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MessageBusTester) | |

## 用途

本插件是一个用于**测试和监控 Unreal Engine 消息总线（MessageBus）系统，特别是 UDP 消息传输可靠性**的开发工具。它并非生产环境功能，而是一个专为开发和调试设计的测试框架。

插件的核心功能是创建多个“测试者”（Tester）实例，这些实例可以在网络中相互发现，并按照预定义的“测试计划”（Test Plan）互相发送数据负载（Payload），然后统计和验证这些数据的接收情况。它可以帮助开发者：
-   **验证 UDP 消息的送达率**：通过对比发送和接收的负载数量，检查是否有消息丢失。
-   **测量网络性能**：计算消息的往返延迟、传输速度（MB/s）。
-   **模拟真实场景**：自定义不同大小、不同发送间隔的负载来测试网络极限。
-   **监控连接状态**：跟踪各个测试者实例的连接和心跳状态。

## 使用场景

-   你正在开发一个依赖于 UDP 网络通信的多人游戏或应用，需要验证消息能否在复杂的网络环境下可靠送达。
-   你对 Unreal Engine 底层消息总线的性能和行为感兴趣，希望对其进行压力测试或基准测试。
-   你遇到了网络消息丢失或延迟的问题，需要一个工具来量化问题并定位瓶颈。
-   **注意**：由于本插件标记为 Beta 实验性（`IsBetaVersion: true`）且仅限特定程序（`MessageBusTesterApp`）使用，它主要用于 Epic 内部的引擎开发测试，**不推荐直接在生产项目中依赖**。

## 蓝图用法

本插件主要面向 C++ 开发者，其核心逻辑和接口均通过 C++ 暴露。插件提供的公开接口 `IMessageBusTester` 和 `IMessageBusTesterModule` 没有对应的蓝图可调用函数（`UFUNCTION(BlueprintCallable)`）或蓝图属性（`UPROPERTY(BlueprintReadWrite)`）。其控制完全在 C++ 层面进行。

要访问测试器功能，需要在 C++ 中获取 `MessageBusTester` 模块的实例。

## C++ 用法

### 头文件引入

```cpp
#include "IMessageBusTesterModule.h"
#include "IMessageBusTester.h"
#include "MessageBusTesterCommon.h"
```

### 基本用法

以下代码演示了如何获取插件模块、配置测试并启动一次测试序列。

```cpp
// 1. 获取消息总线测试器模块
IMessageBusTesterModule& TesterModule = FModuleManager::LoadModuleChecked<IMessageBusTesterModule>("MessageBusTester");

// 2. 获取测试器实例的引用
IMessageBusTester& Tester = TesterModule.GetMessageBusTester();

// 3. 配置测试计划
FTestPlanItem SmallPayloadItem;
SmallPayloadItem.NumBytes = 1024; // 负载大小：1KB
SmallPayloadItem.IntervalSeconds = 1.0f; // 发送间隔：1秒

FTestPlanItem LargePayloadItem;
LargePayloadItem.NumBytes = 64 * 1024; // 负载大小：64KB
LargePayloadItem.IntervalSeconds = 0.5f; // 发送间隔：0.5秒

Tester.AddTestPlanItem(SmallPayloadItem);
Tester.AddTestPlanItem(LargePayloadItem);

// 4. 启动测试器系统（建立通信，开始发现其他测试者）
Tester.StartSystem();

// 5. 当发现其他测试者后，可以启动测试
// 通常在你的游戏逻辑或一个自定义的控制台命令中触发
if (Tester.IsRunning())
{
    Tester.StartTest();
}

// 6. 监听测试状态变化（可选）
Tester.OnTestPlanChanged().AddLambda([]() {
    UE_LOG(LogTemp, Log, TEXT("测试计划已更改！"));
});

// 7. 查询已发现的测试者
TConstArrayView<TSharedPtr<FDiscoveredTester, ESPMode::ThreadSafe>> Testers = Tester.GetDiscoveredTesters();
for (const auto& DiscoveredTester : Testers)
{
    UE_LOG(LogTemp, Log, TEXT("发现测试者: %s (机器: %s, PID: %u)"),
        *DiscoveredTester->Identifier.ToString(),
        *DiscoveredTester->Descriptor.MachineName,
        DiscoveredTester->Descriptor.ProcessId);
}

// 8. 停止测试（可选择是否退出应用）
Tester.StopTest(false); // false 表示停止测试但不退出应用
Tester.StopSystem();
```
**来源**: 基于 `IMessageBusTester.h`, `MessageBusTesterCommon.h` 及 `MessageBusTester.h` 中的接口和类结构推断。

### 进阶用法：自定义配置与日志

插件通过 `UMessageBusTesterSettings` 提供配置，并有一个专用的 Logger。

```cpp
#include "MessageBusTesterSettings.h"
#include "IMessageBusTesterLogger.h"

// 修改测试设置（这些是全局设置，影响所有实例）
UMessageBusTesterSettings* Settings = GetMutableDefault<UMessageBusTesterSettings>();
if (Settings)
{
    Settings->TimeoutInterval = 15.0f; // 将超时时间从10秒改为15秒
    Settings->bUseSessionId = true;
    Settings->SessionId = 123; // 设置一个自定义会话ID
}

// 获取并使用 Logger 来记录自定义事件
IMessageBusTesterLogger& Logger = TesterModule.GetLogger();
Logger.Log(FName(TEXT("MyTestComponent")), TEXT("测试组件已初始化。"), EMessageSeverity::Info);

// 监听新的日志条目
Logger.OnMessageBusTesterNewLogReceived().AddLambda([](TSharedRef<FMessageBusTesterLogEntry> LogEntry) {
    UE_LOG(LogTemp, Warning, TEXT("[%s] %s"), *LogEntry->Source.ToString(), *LogEntry->LogMessage);
});
```
**来源**: 基于 `MessageBusTesterSettings.h` 和 `IMessageBusTesterLogger.h` 中的类定义。

## Demo 示例

一个最小的、可编译的控制台应用程序（或游戏模式）示例，用于启动并观察消息总线测试。

**MessageBusTesterDemo.h**
```cpp
// MyGame.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "IMessageBusTester.h" // 包含消息总线测试器接口
#include "MyGame.generated.h"

UCLASS()
class AMyGameMode : public AGameModeBase
{
    GENERATED_BODY()
    
public:
    virtual void InitGame(const FString& MapName, const FString& Options, FString& ErrorMessage) override;

private:
    /** 消息总线测试器实例的引用（通过模块获取） */
    TScriptInterface<IMessageBusTester> BusTester;
    
    /** 当测试器发现新测试者时的回调 */
    UFUNCTION()
    void OnNewTesterDiscovered();
};
```

**MessageBusTesterDemo.cpp**
```cpp
// MyGame.cpp
#include "MyGame.h"
#include "IMessageBusTesterModule.h"

void AMyGameMode::InitGame(const FString& MapName, const FString& Options, FString& ErrorMessage)
{
    Super::InitGame(MapName, Options, ErrorMessage);
    
    // 加载并获取 MessageBusTester 模块
    if (FModuleManager::Get().IsModuleLoaded("MessageBusTester"))
    {
        IMessageBusTesterModule& TesterModule = FModuleManager::GetModuleChecked<IMessageBusTesterModule>("MessageBusTester");
        BusTester = TesterModule.GetMessageBusTester();
        
        if (BusTester)
        {
            // 注册发现新测试者的回调
            BusTester->OnDiscoveredTesterListChanged().AddUObject(this, &AMyGameMode::OnNewTesterDiscovered);
            
            // 配置一个简单的测试计划
            FTestPlanItem PlanItem;
            PlanItem.NumBytes = 512;
            PlanItem.IntervalSeconds = 2.0f;
            BusTester->AddTestPlanItem(PlanItem);
            
            // 启动测试系统
            BusTester->StartSystem();
            UE_LOG(LogTemp, Log, TEXT("消息总线测试器系统已启动。"));
        }
    }
}

void AMyGameMode::OnNewTesterDiscovered()
{
    UE_LOG(LogTemp, Log, TEXT("发现了新的测试者！当前已发现 %d 个测试者。"), 
        BusTester ? BusTester->GetDiscoveredTesters().Num() : 0);
    
    // 如果发现了至少两个测试者（包括自己），且当前没有在运行测试，则启动测试
    if (BusTester && BusTester->GetDiscoveredTesters().Num() >= 2 && !BusTester->IsRunning())
    {
        BusTester->StartTest();
        UE_LOG(LogTemp, Log, TEXT("开始执行消息总线测试。"));
    }
}
```
**说明**: 此示例展示了在 `GameMode` 中集成消息总线测试器的基本流程。实际应用中，你可能需要通过控制台命令或 UI 按钮来更灵活地控制测试的启停和配置。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `UdpMessaging` | 提供底层的 UDP 消息传输实现，是本插件进行网络测试的基础。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧版日志宏 UE_LOG 迁移为新版 UE_LOGF，属于引擎日志系统更新适配。 |
| 2026-01-15 | `738ab46a` | Fixed localization warnings | 修复了本地化相关警告，提升代码整洁度。 |
| 2025-11-27 | `29081f24` | Fixup API macros | 修正了 API 导出宏的定义或使用。 |
| 2025-11-20 | `f8d6103d` | Enable NDK 29 for Android, fix compilation issues | 启用 Android NDK 29 并修复了由此引发的编译问题，扩展了平台支持。 |
| 2025-11-10 | `248fda82` | Fix the statistics panel not updating with a remote client resets its UDP Messaging settings. | 修复了当远程客户端重置其 UDP 消息设置时，统计面板不更新的问题。 |

### 维护评价

-   **状态**：**实验性/Beta**。插件明确标记为 `IsBetaVersion: true`，且仅限于特定程序 `MessageBusTesterApp` 使用。其接口和功能未来可能发生变化或被移除。
-   **活跃度**：**活跃维护中**。最近一次更新在 2026 年 4 月，主要进行代码现代化（日志宏迁移）和问题修复，表明 Epic 仍在对其维护。
-   **推荐度**：**仅用于特定目的**。如果你正在参与 Unreal Engine 底层网络或消息系统的开发与调试，这个插件是宝贵的工具。对于常规的游戏或应用开发项目，**不推荐直接集成或依赖此插件**。应将其视为一个内部测试和验证工具。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MessageBusTester)
-   [官方文档] (无)