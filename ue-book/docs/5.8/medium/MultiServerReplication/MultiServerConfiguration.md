# Multi-server Replication

> Code to help facilitate connecting multiple UE server processes to each other.

| 属性 | 值 |
|---|---|
| 中文名 | 多服务器复制 |
| 分类 | Networking |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MultiServerReplication` (Runtime), `MultiServerConfiguration` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-08-15 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MultiServerReplication) | |

## 用途

MultiServerReplication 旨在为连接多个独立的 Unreal Engine 服务器进程提供基础架构。它提供了一种类似点对点的通信接口，其底层基于在线信标 (Online Beacons) 来实现服务器之间的消息传递。该插件解决的核心问题是：在超大规模多人游戏或分布式服务器架构中，如何让多个 UE 服务器进程能够相互发现、连接并高效地交换游戏状态与控制信息。

## 使用场景

- **超大规模开放世界游戏**：游戏世界被划分为多个由不同服务器进程管理的区域（Zone），当玩家在这些区域之间移动或交互时，需要服务器间实时同步数据。
- **无缝大地图分区**：将一个连续的庞大地图拆分到多个服务器上进行逻辑处理，对玩家表现为无缝大世界。
- **玩家跨服务器边界交互**：玩家位于不同服务器管理的区域时，其行为（如射击、技能）需要能被另一个服务器正确处理和响应。

## 蓝图用法

**基于当前提供的源码分析**，该插件的核心功能（如信标管理、传输层）主要通过 C++ 接口暴露，未发现直接的 `BlueprintCallable` 节点。其配置和使用高度依赖于 C++ 编码。

## C++ 用法

### 头文件引入

```cpp
#include "MultiServerReplication/Transport/MultiServerTransport.h"
#include "MultiServerReplication/Beacons/MultiServerBeaconClient.h"
```

### 基本用法

插件定义了核心的传输接口，并通过信标客户端实现。基本用法是实现 `IMultiServerTransport` 接口并使用信标进行通信。

```cpp
// 来源：Engine/Plugins/Runtime/MultiServerReplication/Tests/MultiServerReplicationTest.cpp
// 参考其测试用例结构

// 1. 获取或创建一个传输实例
TSharedPtr<IMultiServerTransport> Transport = ...; // 通常通过工厂方法或模块获取

// 2. 目标服务器地址
FMultiServerAddress DestinationAddress;
DestinationAddress.Address = TEXT(“192.168.1.100”);
DestinationAddress.Port = 7778;

// 3. 发送消息
FMultiServerMessageHeader Header;
Header.MessageId = /* 某个消息ID */;
Header.PayloadSize = /* 负载大小 */;

TArray<uint8> Payload = /* 要发送的数据 */;

Transport->SendMessage(DestinationAddress, Header, Payload);
```

### 进阶用法

实现自定义的传输层。插件提供了接口，允许开发者基于不同的网络技术（如 UDP、信标、或自定义协议）来满足特定的服务器间通信需求。

```cpp
// 来源：Engine/Plugins/Runtime/MultiServerReplication/Source/MultiServerReplication/Public/Transport/MultiServerTransport.h
// 1. 继承 IMultiServerTransport 接口
class FMyCustomTransport : public IMultiServerTransport
{
public:
    virtual bool SendMessage(const FMultiServerAddress& Address, const FMultiServerMessageHeader& Header, const TArray<uint8>& Payload) override
    {
        // 实现自定义发送逻辑，例如直接使用 UDP Socket 或其他中间件
        // ...
        return bSuccess;
    }

    virtual void Tick(float DeltaTime) override
    {
        // 处理接收和连接状态维护
    }
    // ... 实现其他必要的接口方法
};

// 2. 在初始化时注册或使用你的自定义传输实例
```

## Demo 示例

一个简单的服务器间消息发送示例，展示了接口的基本使用流程。

**MyMultiServerSender.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Transport/MultiServerTransport.h"

class FMyMultiServerSender
{
public:
    FMyMultiServerSender();
    ~FMyMultiServerSender();

    void SendTestMessageToServer(const FString& ServerIP, int32 ServerPort);

private:
    TSharedPtr<IMultiServerTransport> ServerTransport;
};
```

**MyMultiServerSender.cpp**
```cpp
#include "MyMultiServerSender.h"
#include "MultiServerReplicationModule.h"

FMyMultiServerSender::FMyMultiServerSender()
{
    // 通常通过 MultiServerReplication 模块获取全局或创建的传输实例
    ServerTransport = IMultiServerReplicationModule::Get().CreateTransport();
}

FMyMultiServerSender::~FMyMultiServerSender()
{
}

void FMyMultiServerSender::SendTestMessageToServer(const FString& ServerIP, int32 ServerPort)
{
    if (!ServerTransport.IsValid())
    {
        UE_LOG(LogMultiServerReplication, Error, TEXT(“Transport is not valid.”));
        return;
    }

    // 构造目标地址
    FMultiServerAddress TargetAddress;
    TargetAddress.Address = ServerIP;
    TargetAddress.Port = ServerPort;

    // 构造消息头
    FMultiServerMessageHeader MessageHeader;
    MessageHeader.MessageId = 1001; // 自定义消息ID
    MessageHeader.PayloadSize = 0;  // 此示例无实际负载

    // 发送消息（无负载）
    TArray<uint8> EmptyPayload;
    if (ServerTransport->SendMessage(TargetAddress, MessageHeader, EmptyPayload))
    {
        UE_LOG(LogMultiServerReplication, Log, TEXT(“Test message sent to %s:%d”), *ServerIP, ServerPort);
    }
    else
    {
        UE_LOG(LogMultiServerReplication, Warning, TEXT(“Failed to send test message to %s:%d”), *ServerIP, ServerPort);
    }
}
```

## 模块依赖

从 Build.cs 分析，使用者需依赖以下模块：

| 模块 | 用途 |
|---|---|
| `OnlineSubsystemUtils` | 插件的依赖项，用于提供在线子系统的工具类和接口，是信标功能的基石。 |
| `Networking` | UE 的核心网络模块，提供 Socket、网络连接等基础功能，被自定义传输层使用。 |
| `Sockets` | 提供底层 Socket API。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了格式化函数中作用域枚举可能导致乱码输出的问题 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正了32位与64位格式化说明符不匹配的问题，防止数据截断或错误 |
| 2026-04-15 | `025454a5` | static analysis fix: using alloca in a loop | 修复了静态分析发现的循环内使用 alloca 的潜在风险 |
| 2026-04-15 | `f0b565cd` | FMultiServerTransport | 对核心传输接口 `FMultiServerTransport` 进行了改动（具体未说明，可能是重构或扩展） |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF |

### 维护评价

- **年龄**：创建于 2024 年 8 月，插件非常新。
- **更新频率**：最近一次更新在 2026 年 4 月，但近期提交主要是**编译修复、静态分析修复和代码质量改进**，而非功能性更新。
- **状态**：插件标记为 **实验性 (IsExperimentalVersion=true)** 且默认不启用 (EnabledByDefault=false)，表明 Epic 将其视为前瞻性和探索性的功能，接口和实现可能在未来发生重大变化。
- **推荐度**：不建议在需要稳定性的生产项目中直接依赖此插件。它适用于技术预研、学习分布式服务器架构原理，或作为未来大规模多人游戏服务器框架的起点。由于其实验性质，使用时需要做好适配未来版本变化的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MultiServerReplication)
- [官方文档]（暂无公开官方文档链接）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MultiServerReplication/Tests)