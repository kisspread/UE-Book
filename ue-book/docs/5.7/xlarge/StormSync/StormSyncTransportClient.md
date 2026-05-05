# Storm Sync

> Sync, Pull, Push, asset dependencies.
>
> This plugin is a recommended part of the Motion Design work flow.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资产） |
| 模块 | `StormSyncCore` (Runtime), `StormSyncDrives` (Runtime), `StormSyncEditor` (Runtime), `StormSyncImport` (Runtime), `StormSyncTests` (Runtime), `StormSyncTransportClient` (Runtime), `StormSyncTransportCore` (Runtime), `StormSyncTransportServer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-01-28 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/StormSync) | |

## 用途

StormSync 是一个面向虚拟制片（Virtual Production）和 Motion Design 工作流的**资产依赖同步系统**。它解决的核心问题是：在多台设备/编辑器实例之间，如何高效地同步资产（Package）及其依赖关系。

与简单的文件复制不同，StormSync 提供了完整的资产同步协议：

1. **状态查询（Status）**：查询远程设备上指定资产的状态，判断哪些需要更新
2. **推送（Push）**：将本地资产及其依赖推送到远程设备
3. **拉取（Pull）**：从远程设备拉取资产到本地
4. **广播同步（Synchronize）**：向所有已连接设备广播同步请求

该插件采用 UE 的 MessageBus（消息总线）架构进行设备间通信，支持局域网内的自动发现和点对点传输。它被设计为 Motion Design 工作流的推荐组件，适用于需要在多台工作站之间保持资产一致性的虚拟制片场景。

## 模块架构

```
StormSync/
├── StormSyncCore              ← 核心数据结构与同步逻辑
├── StormSyncDrives            ← 驱动器/存储抽象层
├── StormSyncImport            ← 资产导入处理
├── StormSyncTransportCore     ← 传输层核心（消息定义、本地端点接口）
├── StormSyncTransportClient   ← 传输客户端（发起同步请求）
├── StormSyncTransportServer   ← 传输服务端（响应同步请求）
├── StormSyncEditor            ← 编辑器集成
└── StormSyncTests             ← 自动化测试
```

## 使用场景

- 你在多台工作站上协作进行 Motion Design 制作 → 用 StormSync 保持资产同步
- 你需要将虚拟制片场景推送到渲染农场的编辑器实例 → 用 Push 功能
- 你想检查远程设备上的资产是否与本地一致 → 用 Status 查询
- 你需要在所有连接设备上同步更新材质或蓝图资产 → 用 Synchronize 广播

---

# StormSyncTransportClient 模块

> 传输客户端模块，负责向远程 StormSync 设备发起同步请求。

## 模块概述

`StormSyncTransportClient` 是 StormSync 插件的**客户端传输模块**，提供向远程设备发起状态查询、推送和拉取请求的能力。它是用户与 StormSync 传输层交互的主要入口点。

该模块通过 UE 的 MessageBus 系统与远程 StormSyncTransportServer 通信，支持异步请求和回调。

## C++ 用法

### 头文件引入

```cpp
#include "IStormSyncTransportClientModule.h"
#include "IStormSyncTransportClientLocalEndpoint.h"
```

### 基本用法 — 获取模块实例

通过单例模式获取客户端模块，这是所有操作的起点。

```cpp
// 检查模块是否可用
if (IStormSyncTransportClientModule::IsAvailable())
{
    // 获取模块实例
    IStormSyncTransportClientModule& ClientModule = IStormSyncTransportClientModule::Get();
    
    // 启动客户端端点
    ClientModule.StartClientEndpoint(TEXT("MyClientEndpoint"));
}
```

### 查询远程设备资产状态

向指定远程地址发送状态查询请求，异步获取回调结果。

```cpp
// 来源: IStormSyncTransportClientLocalEndpoint.h
IStormSyncTransportClientModule& ClientModule = IStormSyncTransportClientModule::Get();

// 准备要查询的包名列表
TArray<FName> PackageNames;
PackageNames.Add(TEXT("/Game/MyAsset"));
PackageNames.Add(TEXT("/Game/MyMaterial"));

// 定义状态查询完成回调
FOnStormSyncRequestStatusComplete StatusDelegate;
StatusDelegate.BindLambda([](const TSharedPtr<FStormSyncTransportStatusResponse>& Response)
{
    if (Response.IsValid())
    {
        UE_LOG(LogTemp, Log, TEXT("Status response received"));
        // 处理状态响应...
    }
});

// 发送状态查询请求
ClientModule.RequestPackagesStatus(RemoteAddress, PackageNames, StatusDelegate);
```

### 推送资产到远程设备

将本地资产推送到指定的远程设备。

```cpp
// 来源: IStormSyncTransportClientModule.h
IStormSyncTransportClientModule& ClientModule = IStormSyncTransportClientModule::Get();

// 准备包描述符和包名列表
FStormSyncPackageDescriptor PackageDescriptor;
TArray<FName> PackageNames;
PackageNames.Add(TEXT("/Game/Shared/Blueprint"));

// 定义推送完成回调
FOnStormSyncPushComplete PushDelegate;
PushDelegate.BindLambda([](const TSharedPtr<FStormSyncTransportPushResponse>& Response)
{
    if (Response.IsValid())
    {
        UE_LOG(LogTemp, Log, TEXT("Push completed successfully"));
    }
});

// 推送到指定远程设备
ClientModule.PushPackages(PackageDescriptor, PackageNames, RemoteAddress, PushDelegate);
```

### 从远程设备拉取资产

从指定远程设备拉取资产到本地。

```cpp
// 来源: IStormSyncTransportClientModule.h
IStormSyncTransportClientModule& ClientModule = IStormSyncTransportClientModule::Get();

FStormSyncPackageDescriptor PackageDescriptor;
TArray<FName> PackageNames;
PackageNames.Add(TEXT("/Game/Shared/Texture"));

// 定义拉取完成回调
FOnStormSyncPullComplete PullDelegate;
PullDelegate.BindLambda([](const TSharedPtr<FStormSyncTransportPullResponse>& Response)
{
    if (Response.IsValid())
    {
        UE_LOG(LogTemp, Log, TEXT("Pull completed successfully"));
    }
});

// 从指定远程设备拉取
ClientModule.PullPackages(PackageDescriptor, PackageNames, RemoteAddress, PullDelegate);
```

### 广播同步到所有设备

向所有已连接的 StormSync 设备广播同步请求。

```cpp
// 来源: IStormSyncTransportClientModule.h
IStormSyncTransportClientModule& ClientModule = IStormSyncTransportClientModule::Get();

FStormSyncPackageDescriptor PackageDescriptor;
TArray<FName> PackageNames;
PackageNames.Add(TEXT("/Game/MotionDesign/Template"));

// 广播同步（无回调，发送到所有设备）
ClientModule.SynchronizePackages(PackageDescriptor, PackageNames);
```

### 中止进行中的请求

通过请求 ID 中止已发出的异步请求。

```cpp
// 来源: IStormSyncTransportClientLocalEndpoint.h
// 假设已通过 RequestStatus/RequestPushPackages/RequestPullPackages 获取了 RequestId

// 中止状态查询
ClientEndpoint->AbortStatusRequest(StatusRequestId);

// 中止推送请求
ClientEndpoint->AbortPushRequest(PushRequestId);

// 中止拉取请求
ClientEndpoint->AbortPullRequest(PullRequestId);
```

### 进阶用法 — 使用底层端点接口

如果需要更细粒度的控制，可以直接使用 `IStormSyncTransportClientLocalEndpoint` 接口。

```cpp
// 来源: IStormSyncTransportClientLocalEndpoint.h
// 通过模块获取底层消息端点
IStormSyncTransportClientModule& ClientModule = IStormSyncTransportClientModule::Get();
FMessageEndpointSharedPtr MessageEndpoint = ClientModule.GetClientMessageEndpoint();

// 获取端点消息地址 ID（用于调试或日志）
FString AddressId = ClientModule.GetClientEndpointMessageAddressId();
UE_LOG(LogTemp, Log, TEXT("Client endpoint address: %s"), *AddressId);
```

## 核心接口参考

### IStormSyncTransportClientModule

模块级接口，提供单例访问和高层同步操作。

| 方法 | 说明 |
|---|---|
| `Get()` | 获取模块单例实例 |
| `IsAvailable()` | 检查模块是否已加载 |
| `StartClientEndpoint(FriendlyName)` | 启动客户端传输端点 |
| `GetClientEndpointMessageAddressId()` | 获取客户端端点的消息地址 ID |
| `GetClientMessageEndpoint()` | 获取底层消息端点共享指针 |
| `SynchronizePackages(Descriptor, Names)` | 广播同步到所有已连接设备 |
| `PushPackages(Descriptor, Names, Address, Delegate)` | 推送资产到指定远程设备 |
| `PullPackages(Descriptor, Names, Address, Delegate)` | 从指定远程设备拉取资产 |
| `RequestPackagesStatus(Address, Names, Delegate)` | 查询远程设备资产状态 |

### IStormSyncTransportClientLocalEndpoint

底层端点接口，提供请求级别的精细控制。

| 方法 | 说明 |
|---|---|
| `RequestStatus(Address, Names, Delegate)` | 发送状态查询请求 |
| `RequestPushPackages(Address, Descriptor, Names, Delegate)` | 发送推送请求 |
| `RequestPullPackages(Address, Descriptor, Names, Delegate)` | 发送拉取请求 |
| `AbortStatusRequest(RequestId)` | 中止状态查询请求 |
| `AbortPushRequest(RequestId)` | 中止推送请求 |
| `AbortPullRequest(RequestId)` | 中止拉取请求 |

### 回调委托类型

| 委托 | 参数 | 用途 |
|---|---|---|
| `FOnStormSyncRequestStatusComplete` | `TSharedPtr<FStormSyncTransportStatusResponse>` | 状态查询完成回调 |
| `FOnStormSyncPushComplete` | `TSharedPtr<FStormSyncTransportPushResponse>` | 推送完成回调 |
| `FOnStormSyncPullComplete` | `TSharedPtr<FStormSyncTransportPullResponse>` | 拉取完成回调 |

## 模块依赖

| 模块 | 用途 |
|---|---|
| `StormSyncTransportCore` | 传输层核心接口（`IStormSyncTransportLocalEndpoint`、`StormSyncTransportMessages`） |
| `Messaging` | UE MessageBus 消息端点（`FMessageEndpoint`） |

## 维护状态

### 近期更新

```
- 5e98ccb853ee Motion Design: moved the following plugins from /Plugins/Experimental to /Plugins/VirtualProduction: ActorModifier, ActorModifierCore, Motion Design, ClonerEffector, CustomDetailsView, Material Designer, GeometryMask, OperatorStack, PropertyAnimator, PropertyAnimatorCore, StormSync, StormSync Motion Design Bridge
```

此次提交将 StormSync 从 Experimental 目录正式迁移到 VirtualProduction 目录，表明该插件已通过实验阶段，成为 Motion Design 工作流的正式推荐组件。

### 维护评价

- **状态**：活跃维护中
- **创建时间**：2024 年 1 月，约 1 年历史
- **最近活动**：从 Experimental 正式迁移到 VirtualProduction，说明 Epic 认为其已达到生产可用状态
- **推荐程度**：✅ 推荐使用 — 作为 Motion Design 工作流的官方推荐组件，有 Epic 持续维护
- **注意事项**：该插件依赖 UE MessageBus 进行设备间通信，仅适用于局域网环境；需要配合 StormSyncTransportServer 模块使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/StormSync)
- [StormSyncTransportCore 模块](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/StormSync/Source/StormSyncTransportCore)
- [StormSyncTransportServer 模块](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/StormSync/Source/StormSyncTransportServer)