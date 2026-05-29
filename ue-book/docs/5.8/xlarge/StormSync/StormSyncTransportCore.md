# Storm Sync

> Sync, Pull, Push, asset dependencies.
> This plugin is a recommended part of the Motion Design work flow.

| 属性 | 值 |
|---|---|
| 中文名 | 资产同步 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `StormSyncCore` (Runtime), `StormSyncDrives` (Runtime), `StormSyncEditor` (Runtime), `StormSyncImport` (Runtime), `StormSyncTests` (Runtime), `StormSyncTransportClient` (Runtime), `StormSyncTransportCore` (Runtime), `StormSyncTransportServer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync) | |

## 用途

StormSync 是一个**多机器资产依赖同步工具**，专为 Motion Design（运动设计）工作流中的虚拟制片团队设计。

它解决的核心问题是：当多个 Unreal Engine 实例在同一个局域网上协作时，如何高效地同步项目资产及其依赖关系（如材质、纹理、蓝图等）。与简单的文件复制不同，StormSync 会：

1. **解析资产依赖树**——不只是复制指定的 uasset 文件，而是自动追踪其引用的所有依赖资源
2. **计算差异（diff）**——对比本地和远程的文件哈希、大小、时间戳，生成 Addition/Missing/Overwrite 三种修饰符
3. **通过 TCP 传输数据包**——使用自定义协议将打包好的资产缓冲区从一台机器发送到另一台
4. **基于 Message Bus 的服务发现**——自动发现局域网上的其他 UE 实例，无需手动输入 IP

整体架构采用**客户端-服务器模式**：`StormSyncTransportServer` 负责监听和接收，`StormSyncTransportClient` 负责发起同步请求，`StormSyncTransportCore` 提供底层消息协议和传输核心。

## 使用场景

- 你在团队中使用 Motion Design 进行虚拟制片，多台工作站需要共享同一个 UE 项目资产 → 使用 StormSync 自动同步
- 你需要将资产推送到远程机器（Push）或从远程拉取（Pull）→ 使用 Push/Pull 请求
- 你需要先检查远程机器上哪些文件需要同步，再决定是否执行 → 使用 Status 请求进行差异预览
- 你需要自动发现局域网上的其他 UE 实例 → 使用基于 Message Bus 的发现机制

## 蓝图用法

由于 StormSyncTransportCore 主要提供的是传输协议层（USTRUCT 消息定义和配置），直接暴露给蓝图的节点较少。蓝图可交互的接口集中在 `StormSyncCore` 和 `StormSyncEditor` 模块中。

### 核心配置类

| 类 | 说明 | 所在模块 |
|---|---|---|
| `UStormSyncTransportSettings` | 传输/网络相关配置（服务器地址、端口、超时等） | `StormSyncTransportCore` |

在编辑器中可通过 **Edit → Project Settings → Plugins → Transport & Network** 面板进行配置。

### 关键消息结构（用于理解同步流程）

| 消息结构 | 说明 |
|---|---|
| `FStormSyncTransportSyncRequest` | 同步请求，包含目标包名列表和包描述符（文件哈希、大小等） |
| `FStormSyncTransportPushRequest` | 推送请求，用于向指定远程实例发送同步 |
| `FStormSyncTransportPullRequest` | 拉取请求，包含本地服务器地址信息以便远程回连 |
| `FStormSyncTransportSyncResponse` | 同步响应，包含差异列表（Modifiers）和状态 |
| `FStormSyncTransportStatusRequest` | 状态查询请求，仅检查差异而不执行同步 |
| `FStormSyncTransportStatusResponse` | 状态查询响应，`bNeedsSynchronization` 标示是否需要同步 |
| `FStormSyncTransportConnectMessage` | 连接消息，携带本地项目/主机信息 |
| `FStormSyncTransportPingMessage` | Ping 消息，携带主机名、用户名、项目名 |

## C++ 用法

### 头文件引入

```cpp
#include "StormSyncTransportMessages.h"
#include "StormSyncTransportSettings.h"
#include "StormSyncTransportNetworkUtils.h"
#include "IStormSyncTransportCoreModule.h"
```

### 基本用法：读取传输配置

```cpp
// 获取传输配置单例
const UStormSyncTransportSettings& Settings = UStormSyncTransportSettings::Get();

// 获取 TCP 服务器端点地址（格式: "IP:Port"）
FString Endpoint = Settings.GetServerEndpoint();

// 获取服务器名称（用户自定义或回退到主机名）
FString ServerName = Settings.GetServerName();

// 获取 TCP 服务器地址和端口
FString Address = Settings.GetTcpServerAddress();
uint16 Port = Settings.GetTcpServerPort();

// 检查是否为 Dry Run 模式（仅显示不提取）
bool bDryRun = Settings.IsTcpDryRun();

// 检查是否自动启动服务器
bool bAutoStart = Settings.IsAutoStartServer();
```

### 基本用法：网络工具类

```cpp
#include "StormSyncTransportNetworkUtils.h"

// 获取当前 TCP 服务器端点地址（实际运行中的地址，可能因端口冲突与配置不同）
FString CurrentEndpoint = FStormSyncTransportNetworkUtils::GetCurrentTcpServerEndpointAddress();

// 获取本地所有网卡适配器地址
TArray<FString> AdapterAddresses = FStormSyncTransportNetworkUtils::GetLocalAdapterAddresses();

// 获取 Message Bus 的服务器/客户端端点地址
FString ServerMsgAddr = FStormSyncTransportNetworkUtils::GetServerEndpointMessageAddress();
FString ClientMsgAddr = FStormSyncTransportNetworkUtils::GetClientEndpointMessageAddress();
```

### 进阶用法：构建和解析同步请求/响应

```cpp
#include "StormSyncTransportMessages.h"

// 构建一个同步请求
TArray<FName> PackageNames;
PackageNames.Add(FName("/Game/MotionDesign/MyAsset"));

FStormSyncPackageDescriptor PackageDescriptor; // 来自 StormSyncCore
// ... 填充 PackageDescriptor 的依赖信息 ...

FStormSyncTransportSyncRequest SyncRequest(PackageNames, PackageDescriptor);
UE_LOG(LogTemp, Log, TEXT("Sync Request: %s"), *SyncRequest.ToString());

// 构建推送请求（发送到特定远程实例）
FStormSyncTransportPushRequest PushRequest(PackageNames, PackageDescriptor);

// 构建拉取请求（包含本地网络信息以便远程回连）
FStormSyncTransportPullRequest PullRequest(PackageNames, PackageDescriptor);

// 处理同步响应
FStormSyncTransportSyncResponse SyncResponse;
// 从网络层接收后...
if (SyncResponse.Status == EStormSyncResponseResult::Success)
{
    for (const FStormSyncFileModifierInfo& Modifier : SyncResponse.Modifiers)
    {
        // 每个 Modifier 代表一个需要同步的文件操作
        // 类型: Addition（新增）、Missing（缺失）、Overwrite（覆盖）
    }
}
else if (SyncResponse.Status == EStormSyncResponseResult::Error)
{
    UE_LOG(LogTemp, Error, TEXT("Sync failed: %s"), *SyncResponse.StatusText.ToString());
}
```

### 进阶用法：命令行参数解析

```cpp
#include "Utils/StormSyncTransportCommandUtils.h"

using namespace UE::StormSync::Transport::Private;

// 解析命令行中的服务器端点参数: -StormSyncServerEndpoint=192.168.1.100:40990
FString EndpointValue;
if (GetServerEndpointParam(EndpointValue))
{
    UE_LOG(LogTemp, Log, TEXT("Command line endpoint: %s"), *EndpointValue);
}

// 检查是否通过命令行禁用了自动启动
if (IsServerAutoStartDisabled())
{
    // 不会自动启动 Storm Sync 服务器
}
```

### 进阶用法：通过模块接口获取端点信息

```cpp
#include "IStormSyncTransportCoreModule.h"

if (IStormSyncTransportCoreModule::IsAvailable())
{
    IStormSyncTransportCoreModule& Module = IStormSyncTransportCoreModule::Get();
    
    // 通过委托查询当前绑定的 TCP 服务器地址
    FString TcpAddress = Module.OnGetCurrentTcpServerEndpointAddress().Execute();
    
    // 查询 Message Bus 服务器端点
    FString ServerAddress = Module.OnGetServerEndpointMessageAddress().Execute();
    
    // 查询 Message Bus 客户端端点
    FString ClientAddress = Module.OnGetClientEndpointMessageAddress().Execute();
}
```

## Demo 示例

以下示例展示如何在自定义模块中使用 StormSyncTransportCore 的消息结构和配置。

**MySyncHelper.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "StormSyncTransportMessages.h"

class FMySyncHelper
{
public:
    /** 构造一个状态查询请求并打印信息 */
    static void QuerySyncStatus(const TArray<FName>& InPackageNames, const TArray<FStormSyncFileDependency>& InDependencies);
    
    /** 打印当前传输配置摘要 */
    static void PrintTransportConfig();
    
    /** 打印网络适配器信息 */
    static void PrintNetworkInfo();
};
```

**MySyncHelper.cpp**
```cpp
#include "MySyncHelper.h"
#include "StormSyncTransportSettings.h"
#include "StormSyncTransportNetworkUtils.h"
#include "IStormSyncTransportCoreModule.h"

void FMySyncHelper::QuerySyncStatus(const TArray<FName>& InPackageNames, const TArray<FStormSyncFileDependency>& InDependencies)
{
    FStormSyncTransportStatusRequest StatusRequest(InPackageNames, InDependencies);
    UE_LOG(LogTemp, Log, TEXT("Status Request: %s"), *StatusRequest.ToString());
    
    // 实际使用中，这里会通过 Message Bus 发送请求
    // StatusResponse 包含 bNeedsSynchronization 标志和 Modifiers 差异列表
}

void FMySyncHelper::PrintTransportConfig()
{
    const UStormSyncTransportSettings& Settings = UStormSyncTransportSettings::Get();
    
    UE_LOG(LogTemp, Log, TEXT("=== Storm Sync Transport Config ==="));
    UE_LOG(LogTemp, Log, TEXT("Server Name: %s"), *Settings.GetServerName());
    UE_LOG(LogTemp, Log, TEXT("Server Endpoint: %s"), *Settings.GetServerEndpoint());
    UE_LOG(LogTemp, Log, TEXT("TCP Address: %s"), *Settings.GetTcpServerAddress());
    UE_LOG(LogTemp, Log, TEXT("TCP Port: %u"), Settings.GetTcpServerPort());
    UE_LOG(LogTemp, Log, TEXT("Port Max Offset: %u"), Settings.GetTcpServerPortMaxOffset());
    UE_LOG(LogTemp, Log, TEXT("Auto Start Server: %s"), Settings.IsAutoStartServer() ? TEXT("Yes") : TEXT("No"));
    UE_LOG(LogTemp, Log, TEXT("Inactive Timeout: %u s"), Settings.GetInactiveTimeoutSeconds());
    UE_LOG(LogTemp, Log, TEXT("Dry Run: %s"), Settings.IsTcpDryRun() ? TEXT("Yes") : TEXT("No"));
    UE_LOG(LogTemp, Log, TEXT("Heartbeat Period: %.1f s"), Settings.GetMessageBusHeartbeatPeriod());
    UE_LOG(LogTemp, Log, TEXT("Heartbeat Timeout: %.1f s"), Settings.GetMessageBusHeartbeatTimeout());
    UE_LOG(LogTemp, Log, TEXT("Discovery Tick Interval: %.1f s"), Settings.GetDiscoveryManagerTickInterval());
    UE_LOG(LogTemp, Log, TEXT("Show Import Wizard: %s"), Settings.ShouldShowImportWizard() ? TEXT("Yes") : TEXT("No"));
}

void FMySyncHelper::PrintNetworkInfo()
{
    UE_LOG(LogTemp, Log, TEXT("=== Network Info ==="));
    UE_LOG(LogTemp, Log, TEXT("Current TCP Endpoint: %s"), *FStormSyncTransportNetworkUtils::GetCurrentTcpServerEndpointAddress());
    UE_LOG(LogTemp, Log, TEXT("Server Msg Address: %s"), *FStormSyncTransportNetworkUtils::GetServerEndpointMessageAddress());
    UE_LOG(LogTemp, Log, TEXT("Client Msg Address: %s"), *FStormSyncTransportNetworkUtils::GetClientEndpointMessageAddress());
    
    TArray<FString> Adapters = FStormSyncTransportNetworkUtils::GetLocalAdapterAddresses();
    for (const FString& Addr : Adapters)
    {
        UE_LOG(LogTemp, Log, TEXT("  Adapter: %s"), *Addr);
    }
}
```

## 模块依赖

> 注意：以下信息基于对 `StormSyncTransportCore.Build.cs` 的分析。该模块的依赖关系需要结合其他模块文档。

| 模块 | 用途 |
|---|---|
| `MessageEndpoint` | Unreal Message Bus 端点，用于局域网服务发现和消息传递 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `c830b630` | Storm Sync: fixed vulnerability where a malicious actor can make an spak containing package names/pa | 修复恶意构造 spak 包名/路径的安全漏洞 |
| 2026-05-12 | `3e9d09b7` | Motion Design: fixed storm sync export wizard UI creating a large number of nested folders when chan | 修复导出向导在切换路径时创建大量嵌套文件夹的 UI 问题 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复格式化字符串中 32/64 位不匹配的编译警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏从 UE_LOG 到 UE_LOGF |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复错误的查找替换操作（第二次修正） |

### 维护评价

- **创建时间**：2025 年 5 月，约 1 年前从 Experimental 目录迁移到 VirtualProduction 目录
- **最近更新频率**：近期有活跃更新（最近一次 2026 年 5 月），包含安全漏洞修复
- **维护状态**：**活跃维护中**——Epic Games 持续投入，最近有安全性修复
- **模块数量**：8 个模块，架构较为成熟
- **推荐使用**：✅ 推荐。作为 Motion Design 工作流的官方推荐组件，有完整的客户端/服务器/传输/编辑器支持，且仍在积极维护和安全修复中
- **注意事项**：`Installed: false` 表示需要手动在插件设置中启用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync)
- [官方文档]()（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync/Source/StormSyncTests)

---

# StormSyncTransportCore

> 传输核心模块，提供 Storm Sync 的消息协议定义、网络配置和传输工具。

## 模块概述

`StormSyncTransportCore` 是 StormSync 插件的**传输层基础模块**，定义了所有跨机器通信使用的消息结构、网络配置和工具函数。它是 `StormSyncTransportClient` 和 `StormSyncTransportServer` 的公共依赖。

### 核心职责

1. **消息协议定义**——定义了完整的请求/响应消息结构（Sync、Push、Pull、Status、Ping/Pong、Heartbeat 等）
2. **网络配置管理**——通过 `UStormSyncTransportSettings` 管理 TCP 端口、地址、超时、心跳等配置
3. **TCP 数据包协议**——定义了 TCP 传输层的数据包结构（状态包、大小包、传输完成包）
4. **网络工具**——提供地址解析、适配器枚举等工具函数
5. **模块接口**——通过 `IStormSyncTransportCoreModule` 暴露端点配置查询委托

### 消息层次结构

```
FStormSyncConnectionInfo（连接信息：引擎版本、实例ID、主机名等）
├── FStormSyncTransportConnectMessage（连接事件）
└── FStormSyncTransportSyncRequest（同步请求：包名列表 + 包描述符）
    ├── FStormSyncTransportPushRequest（推送到特定远程）
    ├── FStormSyncTransportPullRequest（拉取请求，含本地网络信息）
    └── FStormSyncTransportSyncResponse（同步响应：差异列表 + 状态）
        ├── FStormSyncTransportPushResponse
        └── FStormSyncTransportPullResponse

FStormSyncTransportStatusRequest（状态查询请求）
FStormSyncTransportStatusResponse（状态查询响应：是否需要同步）

FStormSyncTransportPingMessage → FStormSyncTransportPongMessage
FStormSyncTransportHeartbeatMessage（心跳）
FStormSyncTransportWakeupRequest（唤醒）
```

### 传输流程

```
[Machine A: Client]                      [Machine B: Server]
     |                                        |
     |--- PingMessage (discovery) ----------->|
     |<-- PongMessage ------------------------|
     |                                        |
     |--- ConnectMessage (join) ------------->|
     |<-- ConnectMessage ---------------------|
     |                                        |
     |--- StatusRequest (check diff) -------->|
     |<-- StatusResponse (modifiers) ---------|
     |                                        |
     |--- PushRequest (sync data) ----------->|
     |<-- PushResponse (result) --------------|
     |                                        |
     | (TCP socket for actual file transfer)  |
     |<======================================>|
```