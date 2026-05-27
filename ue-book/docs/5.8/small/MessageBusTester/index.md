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
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MessageBusTester) | |

## 用途

这是一个专门用于**测试和调试 UDP 消息传输**的实验性工具插件。它并非用于生产环境，而是为 UE 开发团队和消息总线（MessageBus）的使用者提供了一套受控的测试用例，用于：
1.  **验证可靠性**：在特定场景下测试 UDP 消息传递的端到端流程是否正确。
2.  **性能分析**：帮助分析消息传递的延迟、吞吐量等性能指标。
3.  **问题诊断**：当消息总线或 UDP 传输层出现异常时，可作为独立的复现和调试环境。
4.  **API 练习**：用于“练习”（exercise）低层级的 UDP 消息传输代码，确保其按预期工作。

简而言之，它是消息总线（尤其是基于 UDP 的 `UdpMessaging` 插件）的“单元测试”或“集成测试”套件。

## 使用场景

- 你是 Epic 内部或高级开发者，正在**调试或优化 UDP 消息传输**的性能或可靠性问题。
- 你需要一个**独立的、可复现的环境**来测试消息的发送、接收、序列化和路由。
- 你在开发基于 UE 消息总线的新功能，并希望运行一些**基准测试**。

**注意**：此插件**仅限**在名为 `MessageBusTesterApp` 的特定程序中加载和使用，无法在普通的游戏编辑器或独立进程中启用。

## 蓝图用法

此插件主要设计用于 C++ 自动化测试和特定程序 (`MessageBusTesterApp`)，不提供面向游戏逻辑的蓝图节点。其核心功能通过 C++ 测试框架（如 UE 自动化测试）来调用。

## C++ 用法

### 头文件引入

```cpp
#include "MessageBusTesterModule.h"
```

### 基本用法

此插件的核心价值在于其提供的测试用例。在 `MessageBusTesterApp` 程序或自动化测试环境中，你可以直接运行或参考这些测试用例。

一个典型的消息发送测试用例示例（参考自测试文件）：

```cpp
// 来源: Engine/Plugins/Experimental/MessageBusTester/Source/MessageBusTester/Tests/MessageBusTesterTest.cpp

#include "MessageEndpoint.h"
#include "MessageEndpointBuilder.h"

// 定义一个简单的消息结构体
struct FSimpleTestMessage
{
    // ... 消息字段
};

// 在测试中创建消息端点并发送测试消息
void SendTestMessage()
{
    // 构建一个消息端点，用于发送和接收消息
    TSharedRef<FMessageEndpoint, ESPMode::ThreadSafe> Endpoint = FMessageEndpoint::Builder("TestEndpoint")
        .Handling<FSimpleTestMessage>(this, &FYourTestClass::OnSimpleTestMessageReceived);

    // 向特定地址发送测试消息
    Endpoint->Publish<FSimpleTestMessage>(new FSimpleTestMessage{});
}
```

### 进阶用法

插件中的测试用例通常结合了**发送、接收、序列化检查和超时控制**，形成完整的测试场景。你可以研究 `MessageBusTester` 模块下的测试文件来了解如何构建更复杂的测试逻辑。

## Demo 示例

由于此插件的特殊性（限特定程序），一个可运行的最小示例更接近于编写一个自动化测试：

```cpp
// MyMessageBusTest.h
#pragma once

#include "CoreMinimal.h"
#include "Misc/AutomationTest.h"
#include "MessageEndpoint.h"

class FMyMessageBusTest : public FAutomationTestBase
{
public:
    FMyMessageBusTest(const FString& InName, const bool bInComplexTest)
        : FAutomationTestBase(InName, bInComplexTest)
    {
    }

    virtual uint32 GetTestFlags() const override { return EAutomationTestFlags::ProductFilter | EAutomationTestFlags::ApplicationContextMask; }
    virtual bool IsStressTest() const { return false; }
    virtual uint32 GetRequiredDeviceNum() const override { return 1; }

protected:
    virtual FString GetBeautifiedTestName() const override { return "MessageBusTester.BasicSendTest"; }
    virtual void GetTests(TArray<FString>& OutBeautifiedNames, TArray<FString>& OutTestCommands) const override
    {
        OutBeautifiedNames.Add(TEXT("SendAndReceive"));
        OutTestCommands.Add(FString());
    }
    virtual bool RunTest(const FString& Parameters) override;
};

// MyMessageBusTest.cpp
#include "MyMessageBusTest.h"
#include "MessageEndpointBuilder.h"

DEFINE_LATENT_AUTOMATION_COMMAND(FWaitForMessage);
// ... (WaitForMessage 实现)

bool FMyMessageBusTest::RunTest(const FString& Parameters)
{
    TSharedPtr<FMessageEndpoint, ESPMode::ThreadSafe> TestEndpoint;
    TSharedPtr<FMessageEndpoint, ESPMode::ThreadSafe> SenderEndpoint;

    // 接收端点
    TestEndpoint = FMessageEndpoint::Builder("TestReceiver")
        .Handling<FSimpleTestMessage>([&](const FSimpleTestMessage& Msg, const TSharedRef<IMessageContext, ESPMode::ThreadSafe>& Context)
        {
            // 收到消息，测试通过
            TestEqual("Received correct message content", Msg.Content, ExpectedContent);
        });

    // 发送端点
    SenderEndpoint = FMessageEndpoint::Builder("TestSender");

    // 发送消息
    SenderEndpoint->Publish<FSimpleTestMessage>(new FSimpleTestMessage{ExpectedContent});

    // 等待消息被接收（使用潜伏命令）
    ADD_LATENT_AUTOMATION_COMMAND(FWaitForMessage());

    return true;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `UdpMessaging` | 提供基于 UDP 的底层消息传输实现，是此插件的主要测试目标。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏 UE_LOG 迁移至新的 UE_LOGF 格式。 |
| 2026-01-15 | `738ab46a` | Fixed localization warnings | 修复了本地化相关的编译警告。 |
| 2025-11-27 | `29081f24` | Fixup API macros | 修正了 API 导入/导出宏的使用。 |
| 2025-11-20 | `f8d6103d` | Enable NDK 29 for Android, fix compilation issues | 为 Android 启用 NDK 29 并修复了相关编译问题。 |
| 2025-11-10 | `248fda82` | Fix the statistics panel not updating with a remote client resets its UDP Messaging settings. | 修复了当远程客户端重置其 UDP 消息设置时，统计面板未更新的问题。 |

### 维护评价

- **实验性**：插件明确标记为 `IsBetaVersion=true`，且仅限特定程序使用，表明其处于开发和测试阶段，未来可能发生较大变化或被移除。
- **活跃度**：从提交记录看，在创建后的半年内有多次更新，主要是编译修复、API 修正和特定问题修复，说明仍在被动维护（随引擎整体更新而更新）。
- **推荐度**：**仅限内部测试或深度调试场景**。普通项目开发者**不建议**依赖或使用此插件。如果你需要测试自己的消息传递功能，应基于此插件的思路创建独立的测试模块。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MessageBusTester)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MessageBusTester/Source/MessageBusTester/Tests)