# QUIC Messaging

> Adds a QUIC based transport layer to the messaging sub-system for sending and receiving messages between networked computers and devices.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | QUIC 消息传输 |
| 分类 | Messaging |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `QuicMessaging` (Runtime), `QuicMessagingTransport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023-06-16 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/QuicMessaging) | |

## 用途

为 UE5 的消息总线 (Message Bus) 系统提供一个基于现代 QUIC 协议的高性能、安全网络传输层。该插件解决了传统 TCP 传输在高延迟或不可靠网络环境下性能不佳的问题，利用 QUIC 协议的多路复用、低延迟连接建立和内置 TLS 1.3 加密特性，为网络设备间的 IPC（进程间通信）和远程过程调用（RPC）提供了更强大、更安全的替代方案。

## 使用场景

-   你需要在多台计算机或设备之间建立低延迟、高可靠性的通信通道，例如用于多人游戏服务器、分布式计算或云端游戏串流。
-   你的应用场景对安全性有较高要求，希望通信内容默认加密，无需额外配置 TLS。
-   你需要一个比 UE5 默认的 TCP 消息传输层更现代化、性能更优的底层网络栈。

## 模块概述

该插件包含两个运行时模块，协同工作：

-   **[`QuicMessaging`](QuicMessaging.md)**：提供与 UE5 消息总线 (UMessageEndpoint) 集成的高级接口。负责消息的序列化、路由以及管理传输层的生命周期。
-   **[`QuicMessagingTransport`](QuicMessagingTransport.md)**：底层的网络传输引擎。封装了基于 QUIC 协议的网络连接、流管理、数据包收发和安全握手。

## 核心蓝图节点

该插件提供的蓝图 API 主要集中在对底层传输服务的控制。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start Transport` | 启动 QUIC 传输服务，开始监听连接。 | `UQuicMessagingTransport` |
| `Stop Transport` | 停止 QUIC 传输服务，断开所有连接。 | `UQuicMessagingTransport` |
| `Is Transport Running` | 查询传输服务是否正在运行。 | `UQuicMessagingTransport` |
| `Get Connection State` | 获取与特定远程地址的连接状态。 | `UQuicMessagingTransport` |

## C++ 用法

### 头文件引入

```cpp
#include "IMessagingModule.h"
#include "QuicMessagingTransport.h"
```

### 基本用法

通过消息总线系统使用 QUIC 传输，通常无需直接与底层传输模块交互。
（基于 `QuicMessaging` 模块的接口抽象）

```cpp
// 创建消息端点，系统会根据配置选择传输层（包括 QUIC）
TSharedRef<FMessageEndpoint, ESPMode::ThreadSafe> MyEndpoint = FMessageEndpoint::Builder("MyEndpointName")
    .Handling<FMyMessageType>(this, &FMyClass::HandleMessage);

// 发送消息到网络上的其他端点
MyEndpoint->Send<FMyMessageType>(Payload, FMyRecipientEndpoint);
```

### 进阶用法

直接管理和监控底层 QUIC 传输服务。
（源自 `QuicMessagingTransport` 模块的测试与用例）

```cpp
// 获取单例传输实例
UQuicMessagingTransport* Transport = UQuicMessagingTransport::Get();

// 启动传输，并指定监听端口
Transport->StartTransport(12345);

// 检查是否正在运行
if (Transport->IsRunning())
{
    // 获取连接状态
    EQuicConnectionState State = Transport->GetConnectionState(RemoteAddress);
}

// 在不需要时停止
Transport->StopTransport();
```

## Demo 示例

一个最小化的 C++ 示例，展示如何创建使用 QUIC 传输的消息端点并发送一条消息。
**依赖**：确保 `QuicMessaging` 和 `QuicMessagingTransport` 模块已在你的 `.Build.cs` 文件中被引用。

```cpp
// MyQuicDemoActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "IMessagingModule.h"
#include "MyQuicDemoActor.generated.h"

USTRUCT(BlueprintType)
struct FTestMessage
{
    GENERATED_BODY()

    UPROPERTY()
    FString Content;
};

UCLASS()
class AMyQuicDemoActor : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    TSharedPtr<FMessageEndpoint, ESPMode::ThreadSafe> MessageEndpoint;

    void HandleTestMessage(const FTestMessage& Message, const TSharedRef<IMessageContext, ESPMode::ThreadSafe>& Context);
};
```

```cpp
// MyQuicDemoActor.cpp
#include "MyQuicDemoActor.h"
#include "MessageEndpointBuilder.h"

void AMyQuicDemoActor::BeginPlay()
{
    Super::BeginPlay();

    // 创建一个使用 QUIC 传输的消息端点
    MessageEndpoint = FMessageEndpoint::Builder("MyQuicDemoEndpoint")
        .Handling<FTestMessage>(this, &AMyQuicDemoActor::HandleTestMessage)
        .ReceivingOnThread(ENamedThreads::GameThread); // 在游戏线程处理消息

    if (MessageEndpoint.IsValid())
    {
        // 向所有订阅了 FTestMessage 的端点广播消息
        FTestMessage TestMsg;
        TestMsg.Content = TEXT("Hello via QUIC!");
        MessageEndpoint->Publish(TestMsg);
        UE_LOG(LogTemp, Log, TEXT("Sent test message via QUIC transport."));
    }
}

void AMyQuicDemoActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (MessageEndpoint.IsValid())
    {
        MessageEndpoint.Reset();
    }
    Super::EndPlay(EndPlayReason);
}

void AMyQuicDemoActor::HandleTestMessage(const FTestMessage& Message, const TSharedRef<IMessageContext, ESPMode::ThreadSafe>& Context)
{
    UE_LOG(LogTemp, Log, TEXT("Received: %s"), *Message.Content);
}
```

## 模块依赖

从模块的 `Build.cs` 文件分析，该插件无特殊外部模块依赖。它的核心依赖是 UE5 的标准 `Messaging` 模块以及底层网络模块（如 `Networking`、`Sockets`）。使用者在自己的模块中添加对 `QuicMessaging` 模块的引用即可。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了用于格式化函数的枚举可能导致输出乱码的问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正了 32 位与 64 位格式说明符与参数不匹配的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏 `UE_LOG` 迁移为 `UE_LOGF`。 |
| 2026-02-03 | `20825e79` | Fix duplicate symbol linker errors | 修复了链接时符号重复的错误。 |
| 2025-09-12 | `fd5c41be` | Addressing instances “ignoring return value of function declared with 'nodiscard' attribute” issue f | 处理了忽略 `[[nodiscard]]` 函数返回值的编译器警告问题。 |

### 维护评价

-   **创建时间**：插件于 2023 年 6 月创建，相对较新（约 3 年历史）。
-   **维护活跃度**：近期（2025-2026年）有多次提交，但主要集中在修复编译器警告、代码格式和链接错误，没有重大功能更新或架构变更。这表明插件处于**稳定但维护不活跃**的状态。
-   **状态**：该插件仍位于 `Experimental` 目录下且默认未启用，表明 Epic 官方可能仍在评估其稳定性和适用性，未达到正式发布的标准。
-   **推荐使用**：如果你需要一个基于 QUIC 的高性能消息传输层，并且能够接受实验性插件的潜在风险和未来可能的变化，可以尝试使用。对于生产环境项目，建议进行充分测试并关注官方对该插件状态的更新。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/QuicMessaging)
-   官方文档 URL 未提供。
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/QuicMessaging/Tests)