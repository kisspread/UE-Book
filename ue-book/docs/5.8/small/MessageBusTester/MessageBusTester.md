# Message Bus Tester

> Plugin to test and monitor message bus reliability（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 消息总线测试器 |
| 分类 | Messaging |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MessageBusTester` (Runtime), `MessageBusTesterEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-10-24 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MessageBusTester) | |

## 用途

本插件提供了一个**自动化测试框架**，用于对 UE5 的 UDP 消息总线 (UDP Message Bus) 的传输层进行压力测试和可靠性验证。它并非一个面向最终用户的运行时功能，而是一个**开发者工具**。其核心目的是通过模拟多个测试实例之间的消息交换（包括发现、心跳、自定义测试负载等），来分析消息总线的性能边界、检测潜在的数据丢失问题，并确保底层网络传输代码按预期工作。

## 使用场景

-   你需要验证你的自定义消息类型通过 `UdpMessaging` 插件进行网络传输时的可靠性和性能。
-   你在开发对网络消息延迟和丢包敏感的分布式系统或网络密集型应用，需要系统化地进行测试。
-   你需要在 CI/CD 流水线中集成消息总线的自动化集成测试。
-   你需要一个可控制的环境来模拟多客户端消息交互，以调试复杂的网络问题。

## 蓝图用法

本插件主要面向 C++ 开发者和自动化测试环境。其核心接口 (`IMessageBusTester`, `IMessageBusTesterModule`) 均为纯 C++ 接口，未暴露 `BlueprintCallable` 函数。所有测试的配置、启动、监控和停止均通过 C++ 代码完成。

## C++ 用法

### 头文件引入

```cpp
#include "MessageBusTesterModule.h"
```

### 基本用法

通过模块接口获取测试器实例，配置并启动一个简单的测试。
（来源：基于 `Public/IMessageBusTester.h` 和 `Public/MessageBusTesterCommon.h` 推断的典型用法）

```cpp
// 1. 获取测试器模块和测试器实例
IMessageBusTesterModule& Module = FModuleManager::LoadModuleChecked<IMessageBusTesterModule>(TEXT("MessageBusTester"));
IMessageBusTester& Tester = Module.GetMessageBusTester();

// 2. 确保测试系统已启动（用于发现其他测试实例）
if (!Tester.IsRunning())
{
    Tester.StartSystem();
}

// 3. 配置测试计划（向所有已连接的测试实例发送 1KB 负载）
FTestPlanItem TestItem;
TestItem.NumBytes = 1024; // 负载大小（字节）
TestItem.IntervalSeconds = 0.5f; // 发送间隔（秒）
Tester.AddTestPlanItem(TestItem);

// 4. 启动测试
if (Tester.StartTest())
{
    UE_LOG(LogTemp, Log, TEXT("Test started successfully."));
}

// ... 等待一段时间或根据条件 ...

// 5. 停止测试（不触发应用退出）
Tester.StopTest(false);
```

### 进阶用法

监听测试状态变化和获取详细的统计信息。
（来源：基于 `Public/IMessageBusTester.h` 和 `Public/DiscoveredTester.h` 推断）

```cpp
// 1. 监听已发现的测试实例列表变化
FDelegateHandle DiscoveryDelegate = Tester.OnDiscoveredTesterListChanged().AddLambda([]()
{
    TConstArrayView<TSharedPtr<FDiscoveredTester, ESPMode::ThreadSafe>> Testers = Tester.GetDiscoveredTesters();
    UE_LOG(LogTemp, Log, TEXT("Discovered %d testers."), Testers.Num());

    for (const TSharedPtr<FDiscoveredTester, ESPMode::ThreadSafe>& DiscoveredTester : Testers)
    {
        if (DiscoveredTester.IsValid())
        {
            UE_LOG(LogTemp, Log, TEXT("Tester %s (ID: %s), State: %d, Connection: %d"),
                *DiscoveredTester->Descriptor.FriendlyName.ToString(),
                *DiscoveredTester->Identifier.ToString(),
                (int32)DiscoveredTester->State,
                (int32)DiscoveredTester->ConnectionState);
        }
    }
});

// 2. 获取特定测试实例的统计信息
// 在某个时刻，例如测试运行一段时间后
TConstArrayView<TSharedPtr<FDiscoveredTester, ESPMode::ThreadSafe>> Testers = Tester.GetDiscoveredTesters();
if (Testers.Num() > 0)
{
    const FDiscoveredTester& FirstTester = *Testers[0];
    UE_LOG(LogTemp, Log, TEXT("Average KeepAlive Interval (Reliable): %.4f s"),
        FirstTester.KeepAliveStatistics.AverageReliableKeepAliveInterval);
    UE_LOG(LogTemp, Log, TEXT("Average Transfer Speed: %.2f MB/s"),
        FirstTester.AverageMbPerSecond.GetAverage());
}

// 3. 清理委托
Tester.OnDiscoveredTesterListChanged().Remove(DiscoveryDelegate);
```

## Demo 示例

一个最小的控制台应用程序或模块，用于运行消息总线测试。
**注意**：此插件被配置为仅在 `MessageBusTesterApp` 程序中加载。以下示例展示了如何在其设计的上下文中使用。

**MessageBusTesterDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"

class FMessageBusTesterDemo
{
public:
    void RunDemo();

private:
    FDelegateHandle TestPlanDelegate;
    FDelegateHandle DiscoveryDelegate;
};
```

**MessageBusTesterDemo.cpp**
```cpp
#include "MessageBusTesterDemo.h"
#include "MessageBusTesterModule.h"
#include "IMessageBusTester.h"
#include "DiscoveredTester.h"

void FMessageBusTesterDemo::RunDemo()
{
    // 确保模块已加载
    IMessageBusTesterModule* Module = FModuleManager::GetModulePtr<IMessageBusTesterModule>(TEXT("MessageBusTester"));
    if (!Module)
    {
        UE_LOG(LogTemp, Error, TEXT("MessageBusTester module is not loaded!"));
        return;
    }

    IMessageBusTester& Tester = Module->GetMessageBusTester();

    // 监听发现事件
    DiscoveryDelegate = Tester.OnDiscoveredTesterListChanged().AddRaw(this, &FMessageBusTesterDemo::HandleTestersDiscovered);
    UE_LOG(LogTemp, Log, TEXT("Listening for other testers..."));

    // 配置一个简单的测试计划
    Tester.ClearLostTesters(); // 清除之前可能存在的失败连接
    FTestPlanItem Item;
    Item.NumBytes = 512;
    Item.IntervalSeconds = 1.0f;
    Tester.AddTestPlanItem(Item);

    // 设置测试计划变更回调
    TestPlanDelegate = Tester.OnTestPlanChanged().AddLambda([]()
    {
        UE_LOG(LogTemp, Log, TEXT("Test plan has been updated."));
    });

    // 启动测试系统（如果未运行）
    if (!Tester.IsRunning())
    {
        Tester.StartSystem();
        UE_LOG(LogTemp, Log, TEXT("Tester system started. Waiting for peers..."));
    }

    // 在实际应用中，测试的启动可能需要等待满足一定条件（例如检测到其他实例）
    // 这里为演示，我们假设稍后某个时刻会调用 Tester.StartTest()
}

void FMessageBusTesterDemo::HandleTestersDiscovered()
{
    IMessageBusTesterModule* Module = FModuleManager::GetModulePtr<IMessageBusTesterModule>(TEXT("MessageBusTester"));
    if (Module)
    {
        const auto Testers = Module->GetMessageBusTester().GetDiscoveredTesters();
        if (Testers.Num() >= 2) // 示例：检测到至少2个实例后启动测试
        {
            UE_LOG(LogTemp, Log, TEXT("Enough peers detected. Starting test..."));
            Module->GetMessageBusTester().StartTest();
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `UdpMessaging` | 核心依赖，提供 UDP 消息传输实现。 |
| `Json` | 用于将测试结果导出为 CSV 文件时的序列化支持。 |
| `MessageBus` | 底层消息总线框架。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新版本。 |
| 2026-01-15 | `738ab46a` | Fixed localization warnings | 修复了本地化警告。 |
| 2025-11-27 | `29081f24` | Fixup API macros | 修复了 API 导出宏。 |
| 2025-11-20 | `f8d6103d` | Enable NDK 29 for Android, fix compilation issues | 启用 Android NDK 29 并修复编译问题。 |
| 2025-11-10 | `248fda82` | Fix the statistics panel not updating with a remote client resets its UDP Messaging settings. | 修复当远程客户端重置其 UDP 消息设置时，统计面板未更新的问题。 |

### 维护评价

**实验性工具，维护活跃但功能可能变动。**
该插件创建于 2025 年底，至今约 1 年，最近一次更新在 2026 年 4 月，表明仍在维护中。然而，其 `.uplugin` 中明确标注 `IsBetaVersion=true`，且首次提交信息中声明“*This is only designed for testing and debugging at the moment and may be changed or removed in the future*”。近期的提交主要是编译兼容性和小问题修复，没有重大的功能迭代。

**结论**：这是一个用于内部开发和测试的实验性工具，**不建议**用于生产环境或作为正式项目的核心依赖。它适合在需要深度调试 UDP 消息总线时临时启用。由于其生命周期不确定，使用时应做好未来被移除或大幅改动的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MessageBusTester)
- [官方文档]() (无)
- [测试用例]() (可能集成在应用程序或单独的自动化测试中，路径未在分析中明确)