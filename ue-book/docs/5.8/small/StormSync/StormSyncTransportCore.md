# Storm Sync

> Sync, Pull, Push, asset dependencies.
>
> This plugin is a recommended part of the Motion Design work flow.

| 属性 | 值 |
|---|---|
| 中文名 | 风暴同步 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（配置资产） |
| 模块 | `StormSyncCore` (Runtime), `StormSyncDrives` (Runtime), `StormSyncEditor` (Runtime), `StormSyncImport` (Runtime), `StormSyncTests` (Runtime), `StormSyncTransportClient` (Runtime), `StormSyncTransportCore` (Runtime), `StormSyncTransportServer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync) | |

## 用途

StormSync 是一个**网络资产依赖同步系统**，用于在多个 Unreal Engine 实例之间同步、推送和拉取资产包及其依赖项。

它解决的核心问题是：在 Motion Design / Virtual Production 工作流中，多个艺术家或工作站需要保持相同的资产状态。传统方式依赖手动复制或版本控制，而 StormSync 提供了**实时的网络同步能力**：

- **Push**：将本地资产包及其依赖推送到指定远程实例
- **Pull**：从远程实例拉取资产包到本地
- **Sync**：广播同步请求，让所有在线实例检查并应用差异
- **Status**：查询远程实例的资产状态，比较差异但不执行同步

底层架构使用 **Message Bus**（基于 UDP 的消息总线）进行服务发现和协调，使用 **TCP Socket** 进行实际的二进制数据传输。通过心跳机制管理连接状态，支持自动重连。

> **注意**：此插件原位于 `/Plugins/Experimental`，于 2025-05 迁移至 `/Plugins/VirtualProduction`，说明已从实验阶段毕业。

## 使用场景

- 你在做 Motion Design 项目，多个 UE 实例需要实时同步资产 → 用 StormSync Push/Pull
- 你需要检查两个工作站的资产包是否一致，但不立即同步 → 用 Status 请求
- 你需要在 Virtual Production 环境中管理多台渲染机器的资产一致性 → 用 StormSync 全套同步流程
- 你需要自定义 TCP 传输层配置（端口、地址、超时等） → 配置 `UStormSyncTransportSettings`

## 蓝图用法

本模块（StormSyncTransportCore）主要是底层传输基础设施，定义了消息结构和网络工具类。核心结构体均为 `USTRUCT`，可被蓝图引用，但**无直接 BlueprintCallable 函数暴露**。

### 核心消息结构

| 结构体 | 说明 |
|---|---|
| `FStormSyncTransportPingMessage` | Ping 消息，包含主机名、用户名、项目名 |
| `FStormSyncTransportPongMessage` | Pong 响应，继承自 PingMessage |
| `FStormSyncTransportSyncRequest` | 同步请求，包含包名列表和包描述符 |
| `FStormSyncTransportPushRequest` | Push 请求，用于向指定远程推送 |
| `FStormSyncTransportPullRequest` | Pull 请求，附带本地服务器地址信息 |
| `FStormSyncTransportSyncResponse` | 同步响应，包含差异列表（Modifiers） |
| `FStormSyncTransportStatusRequest` | 状态查询请求 |
| `FStormSyncTransportStatusResponse` | 状态查询响应，标识是否需要同步 |

### 设置项

在编辑器 **Project Settings → Transport & Network** 中可配置：

- **TcpServerAddress / TcpServerPort**：TCP 服务器监听地址和端口（默认 40990）
- **bAutoStartServer**：是否在编辑器启动时自动启动服务器
- **InactiveTimeoutSeconds**：客户端不活跃超时时间（默认 5 秒）
- **bTcpDryRun**：调试模式，仅显示收到的 buffer 而不解压到本地
- **ConnectionRetryDelay**：断线重连延迟（0 = 禁用重连）
- **MessageBusHeartbeatPeriod**：心跳发送频率（默认 1 秒）
- **MessageBusHeartbeatTimeout**：心跳超时判定（默认 2 秒）
- **bShowImportWizard**：收到同步 buffer 时是否显示导入向导

## C++ 用法

### 头文件引入

```cpp
#include "StormSyncTransportMessages.h"
#include "StormSyncTransportSettings.h"
#include "StormSyncTransportNetworkUtils.h"
#include "IStormSyncTransportCoreModule.h"
```

### 基本用法 - 获取传输设置

```cpp
// 获取传输设置单例
const UStormSyncTransportSettings& Settings = UStormSyncTransportSettings::Get();

// 获取 TCP 服务器端点地址
FString Endpoint = Settings.GetServerEndpoint();
// 返回格式: "0.0.0.0:40990"

// 获取服务器名称
FString ServerName = Settings.GetServerName();

// 获取端口范围
uint16 Port = Settings.GetTcpServerPort();          // 默认 40990
uint16 MaxOffset = Settings.GetTcpServerPortMaxOffset(); // 默认 10
// 实际端口范围: [40990, 40999]
```

### 基本用法 - 网络工具类

```cpp
// 获取本地网络适配器地址列表
TArray<FString> Adapters = FStormSyncTransportNetworkUtils::GetLocalAdapterAddresses();

// 获取当前 TCP 服务器端点（可能与配置不同，因为端口冲突时会自动偏移）
FString CurrentEndpoint = FStormSyncTransportNetworkUtils::GetCurrentTcpServerEndpointAddress();

// 获取 Message Bus 端点地址
FString ServerMsgAddr = FStormSyncTransportNetworkUtils::GetServerEndpointMessageAddress();
FString ClientMsgAddr = FStormSyncTransportNetworkUtils::GetClientEndpointMessageAddress();
```

### 基本用法 - 构造同步消息

```cpp
// 构造 Ping 消息（自动填充当前主机名和用户名）
FStormSyncTransportPingMessage PingMsg;

// 构造自定义 Ping
FStormSyncTransportPingMessage CustomPing(TEXT("MyHost"), TEXT("MyUser"));

// 构造连接信息
FStormSyncConnectionInfo ConnInfo;
ConnInfo.HostName = FPlatformProcess::ComputerName();
ConnInfo.ProjectName = FApp::GetProjectName();
ConnInfo.ProjectDir = FPaths::ProjectDir();

// 调试输出连接信息
FString DebugStr = ConnInfo.ToString();
UE_LOG(LogStormSyncTransportCore, Log, TEXT("Connection Info: %s"), *DebugStr);
```

### 进阶用法 - 构造 Push/Pull 请求

```cpp
// 构造包名列表
TArray<FName> PackageNames;
PackageNames.Add(FName("/Game/MyAsset"));
PackageNames.Add(FName("/Game/MyMaterial"));

// 构造包描述符（包含依赖信息）
FStormSyncPackageDescriptor PackageDesc;
// ... 填充描述符元数据 ...

// 构造 Push 请求（发送到指定远程）
FStormSyncTransportPushRequest PushRequest(PackageNames, PackageDesc);

// 构造 Pull 请求（包含本地服务器信息以便远程回传）
FStormSyncTransportPullRequest PullRequest(PackageNames, PackageDesc);
PullRequest.HostName = FPlatformProcess::ComputerName();
PullRequest.HostAddress = FStormSyncTransportNetworkUtils::GetCurrentTcpServerEndpointAddress();
PullRequest.HostAdapterAddresses = FStormSyncTransportNetworkUtils::GetLocalAdapterAddresses();
```

### 进阶用法 - 处理同步响应

```cpp
// 处理同步响应
void HandleSyncResponse(const FStormSyncTransportSyncResponse& Response)
{
    if (Response.Status == EStormSyncResponseResult::Error)
    {
        UE_LOG(LogStormSyncTransportCore, Error, TEXT("Sync failed: %s"), *Response.StatusText.ToString());
        return;
    }

    // 检查差异列表
    for (const FStormSyncFileModifierInfo& Modifier : Response.Modifiers)
    {
        // 每个 Modifier 代表一个文件的变更操作：
        // Addition（新增）、Missing（缺失）、Overwrite（覆盖）
        UE_LOG(LogStormSyncTransportCore, Log, TEXT("Modifier: %s"), *Modifier.ToString());
    }
}
```

### 进阶用法 - 命令行参数解析

```cpp
#include "Utils/StormSyncTransportCommandUtils.h"

// 从命令行解析自定义服务器端点
FString EndpointValue;
if (UE::StormSync::Transport::Private::GetServerEndpointParam(EndpointValue))
{
    UE_LOG(LogStormSyncTransportCore, Log, TEXT("Custom server endpoint: %s"), *EndpointValue);
}

// 检查是否通过命令行禁用了自动启动
if (UE::StormSync::Transport::Private::IsServerAutoStartDisabled())
{
    // 服务器不会自动启动，需要手动启动
}
// 命令行标志: -NoStormSyncServerAutoStart
// 端点标志:   -StormSyncServerEndpoint=hostname:1234
```

## Demo 示例

```cpp
// StormSyncDemo.h
#pragma once

#include "CoreMinimal.h"
#include "StormSyncTransportMessages.h"
#include "StormSyncTransportNetworkUtils.h"

class FStormSyncDemo
{
public:
    /** 打印当前网络环境信息 */
    static void PrintNetworkInfo();
    
    /** 检查两个实例的资产差异 */
    static FStormSyncTransportStatusRequest BuildStatusCheck(const TArray<FName>& InPackageNames);
};

// StormSyncDemo.cpp
#include "StormSyncDemo.h"
#include "StormSyncTransportSettings.h"
#include "StormSyncTransportCoreLog.h"

void FStormSyncDemo::PrintNetworkInfo()
{
    const UStormSyncTransportSettings& Settings = UStormSyncTransportSettings::Get();
    
    UE_LOG(LogStormSyncTransportCore, Log, TEXT("=== Storm Sync Network Info ==="));
    UE_LOG(LogStormSyncTransportCore, Log, TEXT("Server Name: %s"), *FStormSyncTransportNetworkUtils::GetServerName());
    UE_LOG(LogStormSyncTransportCore, Log, TEXT("TCP Endpoint: %s"), *Settings.GetServerEndpoint());
    UE_LOG(LogStormSyncTransportCore, Log, TEXT("Auto Start: %s"), Settings.IsAutoStartServer() ? TEXT("Yes") : TEXT("No"));
    
    TArray<FString> Adapters = FStormSyncTransportNetworkUtils::GetLocalAdapterAddresses();
    for (const FString& Addr : Adapters)
    {
        UE_LOG(LogStormSyncTransportCore, Log, TEXT("  Adapter: %s"), *Addr);
    }
}

FStormSyncTransportStatusRequest FStormSyncDemo::BuildStatusCheck(const TArray<FName>& InPackageNames)
{
    // 收集文件依赖（实际使用中由 StormSyncCore 模块提供）
    TArray<FStormSyncFileDependency> Dependencies;
    // ... 从资产注册表收集依赖 ...
    
    return FStormSyncTransportStatusRequest(InPackageNames, Dependencies);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `StormSyncCore` | 核心资产同步逻辑、包描述符、文件依赖管理 |
| `Networking` | TCP/UDP 网络通信基础设施 |
| `Serialization` | 序列化支持（JSON 包解析） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `c830b630` | Storm Sync: fixed vulnerability where a malicious actor can make an spak containing package names/pa | 修复安全漏洞：恶意构造的 spak 文件可包含非法包名 |
| 2026-05-12 | `3e9d09b7` | Motion Design: fixed storm sync export wizard UI creating a large number of nested folders when chan | 修复导出向导在变更路径时创建过多嵌套文件夹的 UI 问题 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复日志中 32/64 位格式说明符不匹配的问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移到新的 UE_LOGF 宏 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复上一次错误的查找替换操作 |

### 维护评价

- **活跃维护**：最近 3 个月内有持续更新，包括安全修复和 UI 改进
- **安全性**：2026-05 修复了安全漏洞，表明 Epic 正在积极审查此插件的安全性
- **成熟度**：已从 Experimental 迁移到 VirtualProduction，说明经过评估认为稳定可用
- **代码质量**：近期 commit 包含格式说明符修复和 UE_LOG 迁移，说明正在做代码规范化
- **推荐使用**：✅ 推荐。作为 Motion Design 工作流的推荐组件，处于活跃维护状态，且已修复安全问题

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync)
- 官方文档（暂无）
- [StormSyncCore 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync/Source/StormSyncCore)
- [StormSyncTransportClient 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync/Source/StormSyncTransportClient)
- [StormSyncTransportServer 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync/Source/StormSyncTransportServer)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync/Source/StormSyncTests)