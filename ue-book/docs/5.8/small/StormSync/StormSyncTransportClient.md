# Storm Sync Transport Client

> Sync, Pull, Push, asset dependencies.
>
> This plugin is a recommended part of the Motion Design work flow.

| 属性 | 值 |
|---|---|
| 中文名 | 风暴同步传输客户端 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `StormSyncCore` (Runtime), `StormSyncDrives` (Runtime), `StormSyncEditor` (Runtime), `StormSyncImport` (Runtime), `StormSyncTests` (Runtime), `StormSyncTransportClient` (Runtime), `StormSyncTransportCore` (Runtime), `StormSyncTransportServer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync) | |

## 用途

StormSync 是虚幻引擎虚拟制作 / Motion Design 工作流中的资产同步工具。它解决的核心问题是：**在多个 Unreal Editor 实例之间，高效地同步资产包（Package）的依赖关系**。

该插件提供了三种核心同步操作：
- **Push**：将本地资产推送到远程实例
- **Pull**：从远程实例拉取资产到本地
- **Synchronize**：广播同步请求，让所有连接的设备保持一致

**StormSyncTransportClient** 模块是客户端侧的传输层实现，负责：
1. 通过 **消息总线（Message Bus）** 发送同步请求/响应消息（Push、Pull、Status）
2. 通过 **TCP Socket** 传输实际的资产二进制数据（Pak Buffer）
3. 管理 TCP 连接的生命周期（连接、重连、断开）

架构上采用消息总线 + TCP 混合模式：消息总线用于轻量级的控制消息（请求、响应、状态查询），TCP 用于大体积的资产数据传输。

## 使用场景

- 你在虚拟制作环境中使用 Motion Design 工具，需要在多台机器间同步资产 → 用 StormSync
- 你需要将本地修改的资产包推送到远程工作站（Push） → 用 StormSyncTransportClient
- 你需要从远程工作站拉取最新版本的资产包（Pull） → 用 StormSyncTransportClient
- 你需要查询远程机器上指定资产的状态（是否需要更新） → 用 Status Request

## 蓝图用法

本模块的核心 API 主要通过 `IStormSyncTransportClientModule` 模块接口暴露，底层为 C++ 消息总线通信，蓝图可用节点有限。推荐通过 C++ 方式使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SynchronizePackages` | 广播同步请求到所有已连接设备 | `IStormSyncTransportClientModule` |
| `PushPackages` | 向指定远程地址发送 Push 同步请求 | `IStormSyncTransportClientModule` |
| `PullPackages` | 向指定远程地址发送 Pull 同步请求 | `IStormSyncTransportClientModule` |
| `RequestPackagesStatus` | 查询远程指定资产的状态 | `IStormSyncTransportClientModule` |
| `StartClientEndpoint` | 启动客户端消息端点 | `IStormSyncTransportClientModule` |
| `GetClientEndpointMessageAddressId` | 获取当前客户端端点的消息地址 ID | `IStormSyncTransportClientModule` |

## C++ 用法

### 头文件引入

```cpp
#include "IStormSyncTransportClientModule.h"
```

### 基本用法

```cpp
// 来源: Source/StormSyncTransportClient/Public/IStormSyncTransportClientModule.h

// 检查模块是否可用
if (IStormSyncTransportClientModule::IsAvailable())
{
    // 获取模块实例
    IStormSyncTransportClientModule& ClientModule = IStormSyncTransportClientModule::Get();

    // 启动客户端端点（引擎初始化后调用）
    ClientModule.StartClientEndpoint(TEXT("MyClient"));

    // 获取客户端消息地址
    FString AddressId = ClientModule.GetClientEndpointMessageAddressId();
}
```

### 发起 Pull 请求

```cpp
// 来源: Source/StormSyncTransportClient/Private/Services/StormSyncPullMessageService.h

IStormSyncTransportClientModule& ClientModule = IStormSyncTransportClientModule::Get();

// 准备包描述符和包名列表
FStormSyncPackageDescriptor PackageDescriptor;
TArray<FName> PackageNames;
PackageNames.Add(TEXT("/Game/MyAsset"));

// 指定远程目标地址（通过消息总线发现）
FMessageAddress RemoteAddress;

// 完成回调
FOnStormSyncPullComplete OnPullComplete;
OnPullComplete.BindLambda([](const TSharedPtr<FStormSyncTransportPullResponse>& Response)
{
    if (Response.IsValid())
    {
        UE_LOG(LogTemp, Log, TEXT("Pull completed: %s"), *Response->Status.ToString());
    }
});

// 发起 Pull 请求
ClientModule.PullPackages(PackageDescriptor, PackageNames, RemoteAddress, OnPullComplete);
```

### 发起 Push 请求

```cpp
// 来源: Source/StormSyncTransportClient/Private/Services/StormSyncPushMessageService.h

IStormSyncTransportClientModule& ClientModule = IStormSyncTransportClientModule::Get();

FStormSyncPackageDescriptor PackageDescriptor;
TArray<FName> PackageNames;
PackageNames.Add(TEXT("/Game/MyAsset"));
FMessageAddress RemoteAddress;

FOnStormSyncPushComplete OnPushComplete;
OnPushComplete.BindLambda([](const TSharedPtr<FStormSyncTransportPushResponse>& Response)
{
    if (Response.IsValid())
    {
        UE_LOG(LogTemp, Log, TEXT("Push completed"));
    }
});

ClientModule.PushPackages(PackageDescriptor, PackageNames, RemoteAddress, OnPushComplete);
```

### 查询远程状态

```cpp
// 来源: Source/StormSyncTransportClient/Private/Services/StormSyncStatusMessageService.h

IStormSyncTransportClientModule& ClientModule = IStormSyncTransportClientModule::Get();

TArray<FName> PackageNames;
PackageNames.Add(TEXT("/Game/MyAsset"));

FMessageAddress RemoteAddress;

FOnStormSyncRequestStatusComplete OnStatusComplete;
OnStatusComplete.BindLambda([](const TSharedPtr<FStormSyncTransportStatusResponse>& Response)
{
    if (Response.IsValid())
    {
        UE_LOG(LogTemp, Log, TEXT("Status response received"));
    }
});

ClientModule.RequestPackagesStatus(RemoteAddress, PackageNames, OnStatusComplete);
```

### 进阶用法

通过 TCP Socket 直接建立连接并发送缓冲区数据：

```cpp
// 来源: Source/StormSyncTransportClient/Private/Socket/StormSyncTransportClientSocket.h

// 创建到远程 TCP 服务器的客户端 Socket
FIPv4Endpoint RemoteEndpoint(FIPv4Address(192, 168, 1, 100), 7777);
auto ClientSocket = MakeShared<FStormSyncTransportClientSocket>(RemoteEndpoint);

// 监听连接状态变化
ClientSocket->OnConnectionStateChanged().BindLambda([ClientSocket]()
{
    UE_LOG(LogTemp, Log, TEXT("Connection state: %s"),
        *FStormSyncTransportClientSocket::GetReadableConnectionState(ClientSocket->GetConnectionState()));
});

// 监听接收进度
ClientSocket->OnReceivedSizeDelegate().BindLambda([](int32 ReceivedSize)
{
    UE_LOG(LogTemp, Log, TEXT("Received %d bytes"), ReceivedSize);
});

// 监听传输完成
ClientSocket->OnTransferComplete().BindLambda([]()
{
    UE_LOG(LogTemp, Log, TEXT("Transfer complete!"));
});

// 启动传输（内部创建线程）
ClientSocket->StartTransport();

// 发送数据缓冲区
FStormSyncBuffer Buffer;
// ... 填充 Buffer 数据
ClientSocket->SendBuffer(Buffer);
```

通过客户端端点进行异步发送：

```cpp
// 来源: Source/StormSyncTransportClient/Private/StormSyncTransportClientEndpoint.h

auto ClientEndpoint = MakeShared<FStormSyncTransportClientEndpoint>();
ClientEndpoint->InitializeMessaging(TEXT("MyEndpoint"));

// 使用 StartSendingBuffer 异步发送
FStormSyncTransportSyncResponse SyncResponseMessage;
// ... 填充 SyncResponseMessage
TSharedPtr<FStormSyncTransportClientSocket> ActiveConnection;

FOnStormSyncSendBufferCallback SendCallback;
SendCallback.BindLambda([](const TSharedPtr<FStormSyncSendingBufferPayload>& Payload)
{
    if (Payload.IsValid() && Payload->bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("Buffer sent successfully"));
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to send buffer: %s"),
            Payload.IsValid() ? *Payload->ErrorText.ToString() : TEXT("Unknown error"));
    }
});

ClientEndpoint->StartSendingBuffer(SyncResponseMessage, ActiveConnection, SendCallback);
```

## Demo 示例

### 完整的 Push 同步示例

```cpp
// StormSyncPushExample.h
#pragma once

#include "CoreMinimal.h"
#include "IStormSyncTransportClientModule.h"

class FStormSyncPushExample
{
public:
    void PushAssetsToRemote(const FMessageAddress& RemoteAddress);
};
```

```cpp
// StormSyncPushExample.cpp
#include "StormSyncPushExample.h"
#include "IStormSyncTransportClientModule.h"

void FStormSyncPushExample::PushAssetsToRemote(const FMessageAddress& RemoteAddress)
{
    if (!IStormSyncTransportClientModule::IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("StormSyncTransportClient module not available"));
        return;
    }

    IStormSyncTransportClientModule& ClientModule = IStormSyncTransportClientModule::Get();

    // 确保客户端端点已启动
    ClientModule.StartClientEndpoint(TEXT("PushExample"));

    // 准备要同步的资产列表
    TArray<FName> PackageNames;
    PackageNames.Add(TEXT("/Game/Characters/Hero"));
    PackageNames.Add(TEXT("/Game/Weapons/Sword"));

    // 构建包描述符（标识本次同步操作）
    FStormSyncPackageDescriptor PackageDescriptor;

    // 设置 Push 完成回调
    FOnStormSyncPushComplete OnComplete;
    OnComplete.BindLambda([](const TSharedPtr<FStormSyncTransportPushResponse>& Response)
    {
        if (Response.IsValid())
        {
            UE_LOG(LogTemp, Log, TEXT("Push operation completed successfully for %d packages"),
                Response->PackageNames.Num());
        }
        else
        {
            UE_LOG(LogTemp, Error, TEXT("Push operation failed - no response received"));
        }
    });

    // 发起 Push 请求
    // 流程: 消息总线发送 PushRequest → 远程端处理 → 远程端回复 PushResponse
    //       → 如果有差异，通过 TCP 传输实际数据
    ClientModule.PushPackages(PackageDescriptor, PackageNames, RemoteAddress, OnComplete);
}
```

## 模块依赖

从 `StormSyncTransportClient.Build.cs` 的依赖关系提取：

| 模块 | 用途 |
|---|---|
| `StormSyncCore` | 核心同步逻辑、包描述符、文件修改器等数据结构 |
| `StormSyncTransportCore` | 传输层核心：消息定义、本地端点接口、消息服务接口 |
| `MessageBus` | Unreal 消息总线，用于进程间轻量级消息通信 |
| `Networking` | TCP Socket 网络通信基础 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `c830b630` | Storm Sync: fixed vulnerability where a malicious actor can make an spak containing package names/pa | 修复安全漏洞：防止恶意 pak 文件包含非法包名路径 |
| 2026-05-12 | `3e9d09b7` | Motion Design: fixed storm sync export wizard UI creating a large number of nested folders when chan | 修复导出向导在切换路径时错误创建大量嵌套文件夹 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式化说明符不匹配的问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 新日志宏 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复之前查找替换操作导致的错误 |

### 维护评价

**积极维护中** ✅

- **创建时间**：2025-05-09，从 Experimental 目录迁移到 VirtualProduction，表明已通过内部审核
- **更新频率**：2026 年持续有功能性更新和安全修复，约每 1-2 个月有改动
- **安全性**：最近的 commit 修复了安全漏洞（恶意 pak 路径注入），说明 Epic 在积极关注其安全面
- **代码质量**：迁移到 UE_LOGF 新宏、修复格式化说明符，表明在持续进行代码质量改进
- **推荐使用**：作为 Motion Design 工作流的推荐组件，且仍在活跃维护，推荐在虚拟制作项目中使用
- **注意事项**：该插件默认未启用（`Installed: false`），需要在项目设置中手动启用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync/Source/StormSyncTests)