# Storm Sync

> Sync, Pull, Push, asset dependencies.
>
> This plugin is a recommended part of the Motion Design work flow.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（资产内容） |
| 模块 | `StormSyncCore` (Runtime), `StormSyncDrives` (Runtime), `StormSyncEditor` (Runtime), `StormSyncImport` (Runtime), `StormSyncTests` (Runtime), `StormSyncTransportClient` (Runtime), `StormSyncTransportCore` (Runtime), `StormSyncTransportServer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-01-28 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/StormSync) | |

---

## 用途

StormSync 是一个**资产依赖同步系统**，专为虚拟制片（Virtual Production）和 Motion Design 工作流设计。它解决的核心问题是：**在多个 Unreal Engine 实例之间高效地同步资产及其依赖关系**。

具体来说，StormSync 提供：

1. **资产依赖分析**：自动追踪和解析资产的完整依赖树（包括材质、纹理、蓝图等）
2. **增量同步**：通过比较文件哈希、时间戳和大小，只传输有变化的文件
3. **Push / Pull 操作**：支持将本地资产推送到远程实例，或从远程拉取资产
4. **TCP 传输层**：基于 TCP Socket 的可靠文件传输，支持进度追踪和断点续传
5. **消息总线发现**：通过 Unreal 的 Message Bus 自动发现网络中的其他 StormSync 实例
6. **心跳与连接管理**：维护实例间的连接状态，自动检测离线设备

该插件从 `/Plugins/Experimental` 迁移到 `/Plugins/VirtualProduction`，表明它已成为 Motion Design 工作流的正式推荐组件。

## 模块架构

```
StormSync/
├── StormSyncCore              ← 核心类型定义、包描述、依赖解析
├── StormSyncDrives            ← 驱动器/存储相关功能
├── StormSyncEditor            ← 编辑器 UI、向导、面板
├── StormSyncImport            ← 资产导入逻辑
├── StormSyncTests             ← 自动化测试
├── StormSyncTransportCore     ← 传输层核心：网络工具、TCP 包、设置、消息定义
├── StormSyncTransportClient   ← 客户端：连接服务器、发送同步请求
└── StormSyncTransportServer   ← 服务端：监听连接、处理同步请求
```

## 使用场景

- **多机协作**：你在多台工作站上运行 Unreal Engine 进行虚拟制片，需要保持资产同步 → 用 StormSync Push/Pull
- **Motion Design 工作流**：你在做 Motion Design 项目，需要在编辑器实例间快速同步场景资产 → 用 StormSync
- **资产依赖管理**：你需要了解某个资产的完整依赖树，并确保所有依赖都同步到目标机器 → 用 StormSync 依赖分析
- **远程渲染同步**：你有一个渲染农场需要获取最新的资产版本 → 用 StormSync Server/Client 架构

---

## 子模块文档

| 模块 | 说明 | 文档 |
|---|---|---|
| StormSyncCore | 核心类型、包描述、依赖解析 | [StormSyncCore.md](StormSyncCore.md) |
| StormSyncTransportCore | 传输层核心：网络、TCP、设置、消息 | [StormSyncTransportCore.md](StormSyncTransportCore.md) |
| StormSyncTransportClient | 客户端连接与同步请求 | [StormSyncTransportClient.md](StormSyncTransportClient.md) |
| StormSyncTransportServer | 服务端监听与请求处理 | [StormSyncTransportServer.md](StormSyncTransportServer.md) |
| StormSyncEditor | 编辑器 UI 与向导 | [StormSyncEditor.md](StormSyncEditor.md) |
| StormSyncImport | 资产导入逻辑 | [StormSyncImport.md](StormSyncImport.md) |
| StormSyncDrives | 驱动器/存储功能 | [StormSyncDrives.md](StormSyncDrives.md) |
| StormSyncTests | 自动化测试 | [StormSyncTests.md](StormSyncTests.md) |

---

## 维护状态

### 近期更新

```
- 5e98ccb853ee Motion Design: moved the following plugins from /Plugins/Experimental to /Plugins/VirtualProduction: ActorModifier, ActorModifierCore, Motion Design, ClonerEffector, CustomDetailsView, Material Designer, GeometryMask, OperatorStack, PropertyAnimator, PropertyAnimatorCore, StormSync, StormSync Motion Design Bridge
```

此次提交将 StormSync 从实验性目录正式迁移到 VirtualProduction 目录，表明插件已通过实验阶段，成为 Motion Design 工作流的正式推荐组件。

### 维护评价

- **状态**：🆕 新插件，约 1 年历史
- **迁移记录**：从 Experimental 迁移到 VirtualProduction，说明 Epic 认为其已达到生产可用状态
- **架构成熟度**：8 个模块的分层架构（Core / Transport / Client / Server / Editor / Import / Drives / Tests）表明设计较为成熟
- **推荐**：✅ 推荐用于 Virtual Production 和 Motion Design 工作流中的资产同步需求

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/StormSync)

---

# StormSyncTransportCore

> 传输层核心模块：网络工具、TCP 数据包定义、传输设置、消息总线消息定义。

| 属性 | 值 |
|---|---|
| 类型 | Runtime |
| 所属插件 | StormSync |

## 模块职责

StormSyncTransportCore 是 StormSync 传输层的**基础设施模块**，为 Client 和 Server 模块提供共享的类型定义和工具函数。它不直接处理同步逻辑，而是定义了：

1. **网络工具**：获取服务器地址、本地网卡地址、TCP 端点信息
2. **TCP 数据包协议**：定义传输过程中使用的 JSON 数据包结构
3. **传输设置**：通过 `UDeveloperSettings` 暴露所有网络/传输相关配置
4. **消息总线消息**：定义心跳、连接、同步请求等消息结构
5. **本地端点接口**：抽象消息端点的创建和管理
6. **命令行工具**：解析 `-StormSyncServerEndpoint=` 等启动参数

## 蓝图用法

### 核心节点

StormSyncTransportCore 主要提供 C++ 接口和设置类，蓝图可访问的内容有限：

| 节点 | 说明 | 所在类 |
|---|---|---|
| 项目设置面板 | 配置 TCP 服务器地址、端口、超时等参数 | `UStormSyncTransportSettings` |

### 设置面板

在 **Edit → Project Settings → Plugins → Transport & Network** 中可配置：

- **Server Address**：TCP 服务器监听地址（默认 `0.0.0.0`）
- **Server Port**：TCP 服务器端口（默认端口）
- **Port Max Offset**：端口冲突时的偏移范围
- **Server Name**：服务器显示名称（默认为主机名）
- **Auto Start Server**：是否在启动时自动启动服务器
- **Inactive Timeout**：客户端不活跃超时时间（秒）
- **Connection Retry Delay**：连接重试延迟
- **Dry Run**：调试模式，不实际提取文件
- **Message Bus Heartbeat Period**：心跳频率（秒）
- **Heartbeat Timeout**：心跳超时时间（秒）
- **Discovery Periodic Publish**：是否定期广播发现消息

## C++ 用法

### 头文件引入

```cpp
// 网络工具
#include "StormSyncTransportNetworkUtils.h"

// TCP 数据包
#include "StormSyncTransportTcpPackets.h"

// 传输设置
#include "StormSyncTransportSettings.h"

// 消息定义
#include "StormSyncTransportMessages.h"

// 本地端点接口
#include "IStormSyncTransportLocalEndpoint.h"

// 消息服务接口
#include "IStormSyncTransportMessageService.h"

// 命令行工具
#include "Utils/StormSyncTransportCommandUtils.h"

// 模块接口
#include "IStormSyncTransportCoreModule.h"
```

### 基本用法：获取网络信息

```cpp
#include "StormSyncTransportNetworkUtils.h"

// 获取服务器名称（配置值或回退到主机名）
FString ServerName = FStormSyncTransportNetworkUtils::GetServerName();

// 获取 TCP 端点地址（ip:port 格式）
FString TcpEndpoint = FStormSyncTransportNetworkUtils::GetTcpEndpointAddress();

// 获取所有本地网卡地址（带端口）
TArray<FString> AdapterAddresses = FStormSyncTransportNetworkUtils::GetLocalAdapterAddresses();

// 获取当前实际运行的 TCP 服务器地址（可能因端口冲突与配置不同）
FString CurrentEndpoint = FStormSyncTransportNetworkUtils::GetCurrentTcpServerEndpointAddress();

// 获取消息总线端点地址
FString ServerMsgAddr = FStormSyncTransportNetworkUtils::GetServerEndpointMessageAddress();
FString ClientMsgAddr = FStormSyncTransportNetworkUtils::GetClientEndpointMessageAddress();
```

### 基本用法：读取传输设置

```cpp
#include "StormSyncTransportSettings.h"

// 获取设置单例
const UStormSyncTransportSettings& Settings = UStormSyncTransportSettings::Get();

// 获取服务器端点（ip:port 格式）
FString Endpoint = Settings.GetServerEndpoint();

// 获取 TCP 服务器地址和端口
FString Address = Settings.GetTcpServerAddress();
uint16 Port = Settings.GetTcpServerPort();

// 获取超时配置
uint32 InactiveTimeout = Settings.GetInactiveTimeoutSeconds();
uint32 RetryDelay = Settings.GetConnectionRetryDelay();

// 获取心跳配置
float HeartbeatPeriod = Settings.GetMessageBusHeartbeatPeriod();
double HeartbeatTimeout = Settings.GetMessageBusHeartbeatTimeout();

// 检查是否自动启动服务器
bool bAutoStart = Settings.IsAutoStartServer();

// 检查是否为干运行模式（不实际提取文件）
bool bDryRun = Settings.IsTcpDryRun();
```

### 基本用法：命令行参数解析

```cpp
#include "Utils/StormSyncTransportCommandUtils.h"

using namespace UE::StormSync::Transport::Private;

// 解析 -StormSyncServerEndpoint=hostname:port 命令行参数
FString EndpointValue;
if (GetServerEndpointParam(EndpointValue))
{
    // 使用自定义端点
    UE_LOG(LogTemp, Log, TEXT("Custom server endpoint: %s"), *EndpointValue);
}

// 检查是否禁用了服务器自动启动（-NoStormSyncServerAutoStart）
bool bDisabled = IsServerAutoStartDisabled();
```

### 进阶用法：实现本地端点

```cpp
#include "IStormSyncTransportLocalEndpoint.h"
#include "IStormSyncTransportMessageService.h"
#include "StormSyncTransportMessages.h"

// 实现自定义本地端点
class FMyTransportEndpoint : public IStormSyncTransportLocalEndpoint
{
public:
    virtual bool IsRunning() const override
    {
        return MessageEndpoint.IsValid();
    }

    virtual TSharedPtr<FMessageEndpoint, ESPMode::ThreadSafe> GetMessageEndpoint() const override
    {
        return MessageEndpoint;
    }

    void Initialize()
    {
        // 创建消息端点
        MessageEndpoint = FMessageEndpoint::Builder("MyStormSyncEndpoint")
            .Handling<FStormSyncTransportHeartbeatMessage>(this, &FMyTransportEndpoint::HandleHeartbeat)
            .Handling<FStormSyncTransportConnectMessage>(this, &FMyTransportEndpoint::HandleConnect);

        // 注册消息服务
        for (auto& Service : MessageServices)
        {
            FMessageEndpointBuilder Builder = MessageEndpoint->ToBuilder();
            Service->InitializeMessageEndpoint(Builder);
        }
    }

private:
    TSharedPtr<FMessageEndpoint, ESPMode::ThreadSafe> MessageEndpoint;
    TArray<TSharedPtr<IStormSyncTransportMessageService>> MessageServices;

    void HandleHeartbeat(const FStormSyncTransportHeartbeatMessage& Message, const TSharedRef<IMessageContext, ESPMode::ThreadSafe>& Context)
    {
        // 处理心跳消息
        UE_LOG(LogTemp, Log, TEXT("Heartbeat from %s, server running: %d"),
            *Context->GetSender().ToString(), Message.bIsServerRunning);
    }

    void HandleConnect(const FStormSyncTransportConnectMessage& Message, const TSharedRef<IMessageContext, ESPMode::ThreadSafe>& Context)
    {
        // 处理连接消息
        UE_LOG(LogTemp, Log, TEXT("Connect from %s (%s)"),
            *Message.HostName, *Message.ProjectName);
    }
};
```

### 进阶用法：构造 TCP 数据包

```cpp
#include "StormSyncTransportTcpPackets.h"

// 状态包 - 连接时发送
FStormSyncTransportTcpStatePacket StatePacket;
// StatePacket.Command 自动设为 "state"
// StatePacket.HostName 自动设为当前主机名

// 大小包 - 接收方通知发送方已接收的字节数
FStormSyncTransportTcpSizePacket SizePacket(1024 * 512); // 已接收 512KB
// SizePacket.Command 自动设为 "size"

// 传输完成包
FStormSyncTransportTcpTransferCompletePacket CompletePacket;
// CompletePacket.Command 自动设为 "transfer_complete"
```

### 进阶用法：使用连接信息消息

```cpp
#include "StormSyncTransportMessages.h"

// 构造连接信息
FStormSyncConnectionInfo ConnectionInfo;
ConnectionInfo.HostName = FPlatformProcess::ComputerName();
ConnectionInfo.ProjectName = FApp::GetProjectName();
ConnectionInfo.ProjectDir = FPaths::ProjectDir();

// 获取可读的调试字符串
FString DebugStr = ConnectionInfo.ToString();

// 通过消息总点发送连接消息
FStormSyncTransportConnectMessage ConnectMsg;
// ConnectMsg 继承自 FStormSyncConnectionInfo，自动填充所有字段

// 构造同步请求
FStormSyncTransportSyncRequest SyncRequest;
// 包含要同步的包名列表、包描述符元数据、依赖列表及其状态
```

### 进阶用法：模块接口委托

```cpp
#include "IStormSyncTransportCoreModule.h"

// 获取模块接口
IStormSyncTransportCoreModule& TransportModule = IStormSyncTransportCoreModule::Get();

// 绑定 TCP 服务器端点查询委托
TransportModule.OnGetCurrentTcpServerEndpointAddress().BindLambda([]() -> FString
{
    return FStormSyncTransportNetworkUtils::GetCurrentTcpServerEndpointAddress();
});

// 绑定消息总线端点查询委托
TransportModule.OnGetServerEndpointMessageAddress().BindLambda([]() -> FString
{
    return FStormSyncTransportNetworkUtils::GetServerEndpointMessageAddress();
});

TransportModule.OnGetClientEndpointMessageAddress().BindLambda([]() -> FString
{
    return FStormSyncTransportNetworkUtils::GetClientEndpointMessageAddress();
});
```

## Demo 示例

### 自定义传输端点实现

```cpp
// MyTransportEndpoint.h
#pragma once

#include "IStormSyncTransportLocalEndpoint.h"
#include "IStormSyncTransportMessageService.h"
#include "StormSyncTransportMessages.h"

class FMessageEndpoint;

class FMyTransportEndpoint : public IStormSyncTransportLocalEndpoint
{
public:
    FMyTransportEndpoint();
    virtual ~FMyTransportEndpoint();

    // IStormSyncTransportLocalEndpoint interface
    virtual bool IsRunning() const override;
    virtual TSharedPtr<FMessageEndpoint, ESPMode::ThreadSafe> GetMessageEndpoint() const override;

    /** 发送心跳到消息总线 */
    void SendHeartbeat();

    /** 发送连接信息到消息总线 */
    void SendConnectInfo();

private:
    TSharedPtr<FMessageEndpoint, ESPMode::ThreadSafe> MessageEndpoint;

    void HandleHeartbeat(const FStormSyncTransportHeartbeatMessage& Message, const TSharedRef<IMessageContext, ESPMode::ThreadSafe>& Context);
    void HandleConnect(const FStormSyncTransportConnectMessage& Message, const TSharedRef<IMessageContext, ESPMode::ThreadSafe>& Context);
    void HandleSyncRequest(const FStormSyncTransportSyncRequest& Message, const TSharedRef<IMessageContext, ESPMode::ThreadSafe>& Context);
};
```

```cpp
// MyTransportEndpoint.cpp
#include "MyTransportEndpoint.h"
#include "StormSyncTransportNetworkUtils.h"
#include "StormSyncTransportSettings.h"
#include "MessageEndpoint.h"
#include "MessageEndpointBuilder.h"

FMyTransportEndpoint::FMyTransportEndpoint()
{
    const UStormSyncTransportSettings& Settings = UStormSyncTransportSettings::Get();

    MessageEndpoint = FMessageEndpoint::Builder("MyStormSyncTransport")
        .Handling<FStormSyncTransportHeartbeatMessage>(this, &FMyTransportEndpoint::HandleHeartbeat)
        .Handling<FStormSyncTransportConnectMessage>(this, &FMyTransportEndpoint::HandleConnect)
        .Handling<FStormSyncTransportSyncRequest>(this, &FMyTransportEndpoint::HandleSyncRequest);

    if (MessageEndpoint.IsValid())
    {
        // 订阅消息总线主题
        MessageEndpoint->Subscribe<FStormSyncTransportHeartbeatMessage>();
        MessageEndpoint->Subscribe<FStormSyncTransportConnectMessage>();

        UE_LOG(LogTemp, Log, TEXT("Transport endpoint initialized. Server: %s, Endpoint: %s"),
            *FStormSyncTransportNetworkUtils::GetServerName(),
            *FStormSyncTransportNetworkUtils::GetTcpEndpointAddress());
    }
}

FMyTransportEndpoint::~FMyTransportEndpoint()
{
    if (MessageEndpoint.IsValid())
    {
        MessageEndpoint.Reset();
    }
}

bool FMyTransportEndpoint::IsRunning() const
{
    return MessageEndpoint.IsValid();
}

TSharedPtr<FMessageEndpoint, ESPMode::ThreadSafe> FMyTransportEndpoint::GetMessageEndpoint() const
{
    return MessageEndpoint;
}

void FMyTransportEndpoint::SendHeartbeat()
{
    if (!MessageEndpoint.IsValid())
    {
        return;
    }

    FStormSyncTransportHeartbeatMessage Heartbeat;
    Heartbeat.bIsServerRunning = true;

    MessageEndpoint->Publish(Heartbeat);
}

void FMyTransportEndpoint::SendConnectInfo()
{
    if (!MessageEndpoint.IsValid())
    {
        return;
    }

    FStormSyncTransportConnectMessage ConnectMsg;
    // FStormSyncConnectionInfo 字段在构造时自动填充

    MessageEndpoint->Publish(ConnectMsg);
}

void FMyTransportEndpoint::HandleHeartbeat(const FStormSyncTransportHeartbeatMessage& Message, const TSharedRef<IMessageContext, ESPMode::ThreadSafe>& Context)
{
    UE_LOG(LogTemp, Log, TEXT("Received heartbeat from %s (server running: %s)"),
        *Context->GetSender().ToString(),
        Message.bIsServerRunning ? TEXT("true") : TEXT("false"));
}

void FMyTransportEndpoint::HandleConnect(const FStormSyncTransportConnectMessage& Message, const TSharedRef<IMessageContext, ESPMode::ThreadSafe>& Context)
{
    UE_LOG(LogTemp, Log, TEXT("Connection from %s | Project: %s | Host: %s"),
        *Message.ToString(),
        *Message.ProjectName,
        *Message.HostName);
}

void FMyTransportEndpoint::HandleSyncRequest(const FStormSyncTransportSyncRequest& Message, const TSharedRef<IMessageContext, ESPMode::ThreadSafe>& Context)
{
    UE_LOG(LogTemp, Log, TEXT("Received sync request from %s"), *Context->GetSender().ToString());
    // 处理同步请求...
}
```

## 模块依赖

从头文件分析，StormSyncTransportCore 依赖以下模块：

| 模块 | 用途 |
|---|---|
| `StormSyncCore` | 提供 `FStormSyncCommonTypes`、`FStormSyncPackageDescriptor` 等核心类型 |
| `Messaging` | 提供 `FMessageEndpoint`、`FMessageEndpointBuilder` 消息总线基础设施 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

```
- 5e98ccb853ee Motion Design: moved the following plugins from /Plugins/Experimental to /Plugins/VirtualProduction: ActorModifier, ActorModifierCore, Motion Design, ClonerEffector, CustomDetailsView, Material Designer, GeometryMask, OperatorStack, PropertyAnimator, PropertyAnimatorCore, StormSync, StormSync Motion Design Bridge
```

此次提交将 StormSync 整体从实验性目录迁移到 VirtualProduction 目录，标志着插件已通过实验阶段评估。

### 维护评价

- **状态**：🆕 新模块，约 1 年历史
- **架构质量**：接口驱动设计（`IStormSyncTransportLocalEndpoint`、`IStormSyncTransportMessageService`），解耦良好
- **成熟度**：从 Experimental 正式迁移到 VirtualProduction，Epic 认为已达到生产可用标准
- **推荐**：✅ 推荐用于需要在多个 UE 实例间同步资产的 Virtual Production 工作流

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/StormSync/Source/StormSyncTransportCore)
- [插件根目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/StormSync)