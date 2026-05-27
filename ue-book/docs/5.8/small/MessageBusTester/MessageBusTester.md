# MessageBus Tester

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

该插件是一个专门用于**测试和监控 UE MessageBus 底层 UDP 消息传输可靠性**的调试工具。它并非面向最终用户的功能插件，而是 Epic 内部用来验证 `UdpMessaging` 插件和 MessageBus 基础设施是否正常工作的测试框架。

核心能力包括：
- **发现机制**：自动发现同一网络上的其他 MessageBusTester 实例（通过周期性广播发现消息）
- **测试计划**：定义负载大小、发送间隔等测试参数，支持多条测试项组合
- **负载收发**：在发现的 Tester 之间发送带 payload 的测试消息，跟踪确认（ACK）状态
- **性能统计**：收集 KeepAlive 间隔、丢包率、传输带宽（MB/s）等关键指标
- **结果导出**：测试结束后可将结果导出为 CSV 文件

> **注意**：该插件通过 `AllowlistPrograms` 限制仅在 `MessageBusTesterApp` 专用测试程序中加载，普通编辑器或游戏项目中不会激活。

## 使用场景

- 你在开发跨进程/跨机器的实时通信功能，需要验证 UDP 消息传输的丢包率和延迟
- 你需要对 `UdpMessaging` 插件的底层传输层进行压力测试或回归测试
- 你需要在多个 Unreal 实例之间进行消息总线可靠性的端到端测试
- 你在排查 MessageBus 在高负载或网络抖动场景下的表现

## 蓝图用法

该插件主要通过 C++ 接口驱动，**没有暴露 BlueprintCallable 函数**。所有操作均通过 `IMessageBusTester` 接口在 C++ 层完成。

## C++ 用法

### 头文件引入

```cpp
#include "IMessageBusTesterModule.h"
#include "IMessageBusTester.h"
#include "MessageBusTesterCommon.h"
#include "DiscoveredTester.h"
#include "MessageBusTesterSettings.h"
```

### 基本用法

从模块获取 Tester 接口并启动系统：

```cpp
// 获取模块实例
IMessageBusTesterModule& Module = FModuleManager::Get().LoadModuleChecked<IMessageBusTesterModule>("MessageBusTester");
IMessageBusTester& Tester = Module.GetMessageBusTester();

// 启动消息总线测试系统
Tester.StartSystem();

// 配置测试计划
FTestPlanItem Item;
Item.NumBytes = 2048;            // 每个 payload 的字节数
Item.IntervalSeconds = 0.1f;     // 发送间隔（秒）
Tester.AddTestPlanItem(Item);

// 启动测试
Tester.StartTest();

// 监听发现的测试者列表变化
Tester.OnDiscoveredTesterListChanged().AddLambda([]()
{
    // 处理新发现或丢失的 Tester
});
```

### 进阶用法

监控发现的 Tester 列表及其性能统计：

```cpp
// 获取所有已发现的 Tester
TConstArrayView<TSharedPtr<FDiscoveredTester, ESPMode::ThreadSafe>> Testers = Tester.GetDiscoveredTesters();

for (const TSharedPtr<FDiscoveredTester>& DiscoveredTester : Testers)
{
    if (DiscoveredTester.IsValid())
    {
        // 打印 Tester 信息
        UE_LOG(LogTemp, Log, TEXT("Tester: %s, State: %s, Connection: %s"),
            *DiscoveredTester->Identifier.ToString(),
            DiscoveredTester->State == EMessageBusTesterState::Active ? TEXT("Active") : TEXT("Idle"),
            DiscoveredTester->ConnectionState == EDiscoveredTesterConnectionState::Connected ? TEXT("Connected") : TEXT("Lost"));

        // 检查 KeepAlive 统计
        const FKeepAliveStatistics& KeepAliveStats = DiscoveredTester->KeepAliveStatistics;
        UE_LOG(LogTemp, Log, TEXT("  Unreliable KeepAlive Avg: %.4f ms, Reliable KeepAlive Avg: %.4f ms"),
            KeepAliveStats.AverageUnreliableKeepAliveInterval * 1000.0,
            KeepAliveStats.AverageReliableKeepAliveInterval * 1000.0);

        // 检查传输带宽
        UE_LOG(LogTemp, Log, TEXT("  Avg Transfer: %.2f MB/s"), DiscoveredTester->AverageMbPerSecond.Get());
    }
}

// 清除已丢失的 Tester
Tester.ClearLostTesters();

// 停止测试（可选参数控制是否退出应用）
Tester.StopTest(/*bShouldExitOnStop=*/false);
```

配置测试会话（通过设置类）：

```cpp
UMessageBusTesterSettings* Settings = GetMutableDefault<UMessageBusTesterSettings>();
// 通过命令行 -MessageBusTesterSessionId=1 设置会话 ID
// 通过命令行 -MessageBusTesterFriendlyName=MyTester 设置友好名称
int32 SessionId = Settings->GetSessionId();
```

## Demo 示例

一个完整的最小可编译示例，展示如何初始化 MessageBusTester 并运行基础测试：

```cpp
// MyBusTest.h
#pragma once

#include "IMessageBusTesterModule.h"
#include "IMessageBusTester.h"
#include "DiscoveredTester.h"

class FMyBusTest
{
public:
    void Initialize();
    void Shutdown();

private:
    void OnTestersChanged();
    IMessageBusTester* BusTester = nullptr;
};
```

```cpp
// MyBusTest.cpp
#include "MyBusTest.h"
#include "MessageBusTesterCommon.h"
#include "Modules/ModuleManager.h"

void FMyBusTest::Initialize()
{
    // 加载模块
    IMessageBusTesterModule& Module = FModuleManager::Get().LoadModuleChecked<IMessageBusTesterModule>("MessageBusTester");
    BusTester = &Module.GetMessageBusTester();

    // 订阅 Tester 列表变化
    BusTester->OnDiscoveredTesterListChanged().AddRaw(this, &FMyBusTest::OnTestersChanged);

    // 启动系统
    BusTester->StartSystem();

    // 添加一个测试项：1KB 负载，每 0.5 秒发送一次
    FTestPlanItem Item;
    Item.NumBytes = 1024;
    Item.IntervalSeconds = 0.5f;
    BusTester->AddTestPlanItem(Item);

    UE_LOG(LogTemp, Log, TEXT("MessageBusTester initialized, waiting for remote testers..."));
}

void FMyBusTest::Shutdown()
{
    if (BusTester)
    {
        BusTester->StopTest(false);
        BusTester->StopSystem();
        BusTester = nullptr;
    }
}

void FMyBusTest::OnTestersChanged()
{
    if (!BusTester) return;

    TConstArrayView<TSharedPtr<FDiscoveredTester, ESPMode::ThreadSafe>> Testers = BusTester->GetDiscoveredTesters();
    UE_LOG(LogTemp, Log, TEXT("Discovered %d tester(s)"), Testers.Num());

    // 当至少发现一个远端 Tester 时，自动启动测试
    if (Testers.Num() > 0 && BusTester->GetState() == EMessageBusTesterState::Idle)
    {
        BusTester->StartTest();
    }
}
```

## 模块依赖

该插件依赖 `UdpMessaging` 插件（在 `.uplugin` 中声明）。以下为 C++ 模块层面的依赖：

| 模块 | 用途 |
|---|---|
| `Messaging` | `FMessageEndpoint`、`FMessageAddress`、`IMessageContext` 等消息总线核心 API |
| `UdpMessaging`（插件级依赖） | UDP 消息传输层，作为测试目标 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到 UE_LOGF 格式 |
| 2026-01-15 | `738ab46a` | Fixed localization warnings | 修复本地化警告 |
| 2025-11-27 | `29081f24` | Fixup API macros | 修复 API 导出宏定义 |
| 2025-11-20 | `f8d6103d` | Enable NDK 29 for Android, fix compilation issues | 修复 Android 编译问题 |
| 2025-11-10 | `248fda82` | Fix the statistics panel not updating with a remote client resets its UDP Messaging settings. | 修复远端客户端重置 UDP 设置后统计面板不更新的问题 |

### 维护评价

- **创建时间**：2025-10-24，插件历史不到 1 年
- **更新频率**：创建后 2 个月内密集修复（4 次提交），之后间隔约 3 个月
- **维护性质**：所有更新均为编译修复、API 规范化和平台兼容性调整，**无功能性新增**
- **实验性声明**：`.uplugin` 中 `IsBetaVersion=true`，且首条 commit 明确注明"may be changed or removed in the future"
- **使用限制**：通过 `AllowlistPrograms` 限定仅在 `MessageBusTesterApp` 专用测试程序中加载

**综合评价**：这是一个内部测试工具，处于实验阶段，功能完整但不面向外部使用者。仅推荐在调试 MessageBus/UDP 传输层时使用，**不建议用于生产项目**。由于最近一次更新（2026-04）仍属于维护性更新，插件仍在被维护中，但 Epic 可能在未来任意时间移除它。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MessageBusTester)