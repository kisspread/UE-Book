# Concert - Main

> Allow collaborative multi-users sessions in the Editor

| 属性 | 值 |
|---|---|
| 分类 | Networking |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Concert` (UncookedOnly), `ConcertClient` (UncookedOnly), `ConcertServer` (UncookedOnly), `ConcertTransport` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-01-10 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertMain) | |

## 用途

ConcertMain 是 Unreal Engine **Multi-User Editing（多人协作编辑）** 系统的核心基础插件。它实现了一个客户端-服务器架构，允许多个编辑器实例连接到同一个 Concert 服务器，通过**会话（Session）**进行实时协作。

这个插件本身是一个**基础通信框架**，定义了：
- 客户端/服务器的抽象接口
- 会话的创建、加入、归档、恢复、复制等生命周期管理
- 可靠的消息传输协议
- 自定义事件/请求的扩展机制

**实际的 Multi-User 同步逻辑**（如 Actor 同步、事务同步、包同步）由上层插件 `ConcertSyncCore` / `ConcertSyncClient` / `ConcertSyncServer` 实现，ConcertMain 只提供通信基础设施。

### 支持的角色

ConcertMain 的模块通过**角色（Role）**区分用途，支持多种程序类型：

| 程序 | 说明 |
|---|---|
| `UnrealMultiUserServer` | 独立 Multi-User 服务器（命令行） |
| `CoopMultiUserServer` | 协作 Multi-User 服务器 |
| `UnrealMultiUserSlateServer` | 带 UI 的 Multi-User 服务器 |
| `UnrealRecoverySvc` | 灾难恢复服务 |
| `CrashReportClientEditor` | 崩溃报告客户端 |
| `LiveLinkHub` | Live Link Hub |

## 使用场景

- **多人协作编辑** — 多个美术/设计同时编辑同一个关卡，通过 Concert 服务器同步变更
- **灾难恢复** — 服务器自动记录所有编辑操作，可在崩溃后恢复
- **会话归档/恢复** — 保存编辑会话快照，后续可恢复到任意历史状态
- **跨设备协作** — 不同机器上的编辑器实例连接同一服务器协作

## 模块架构

```
┌──────────────────────────────────────────────────────┐
│                    ConcertMain                        │
│                                                      │
│  ┌──────────────────┐  ┌───────────────────────────┐ │
│  │  ConcertTransport│  │  Concert                  │ │
│  │  (传输层)         │  │  (会话抽象层)              │ │
│  │                  │  │                           │ │
│  │  • 端点通信       │  │  • IConcertSession        │ │
│  │  • 消息协议       │  │  • 管理消息               │ │
│  │  • 可靠传输       │  │  • 数据结构               │ │
│  │  • 标识符表       │  │  • 自定义消息框架          │ │
│  │  • 协议追踪       │  │  • 服务器事件             │ │
│  └────────┬─────────┘  └─────────┬─────────────────┘ │
│           │                      │                   │
│  ┌────────┴──────────────────────┴─────────────────┐ │
│  │                                                  │ │
│  │  ┌──────────────────┐  ┌─────────────────────┐  │ │
│  │  │  ConcertClient   │  │  ConcertServer      │  │ │
│  │  │  (客户端)         │  │  (服务端)            │  │ │
│  │  │                  │  │                     │  │ │
│  │  │  • 服务器发现     │  │  • 会话生命周期      │  │ │
│  │  │  • 会话 CRUD     │  │  • 归档/恢复         │  │ │
│  │  │  • 自动连接       │  │  • 客户端审批        │  │ │
│  │  │  • 连接任务管线   │  │  • 会话仓库          │  │ │
│  │  └──────────────────┘  └─────────────────────┘  │ │
│  └──────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
```

## 模块文档

| 模块 | 说明 | 文档 |
|---|---|---|
| ConcertTransport | 底层消息传输层 | [ConcertTransport.md](ConcertTransport.md) |
| Concert | 核心会话抽象层 | [Concert.md](Concert.md) |
| ConcertClient | 客户端模块 | [ConcertClient.md](ConcertClient.md) |
| ConcertServer | 服务端模块 | [ConcertServer.md](ConcertServer.md) |

## 蓝图用法

ConcertMain 是一个纯 C++ 框架插件，**不暴露蓝图节点**。它的所有接口都是 C++ 抽象类（`IConcertClient`, `IConcertServer`, `IConcertSession` 等），供上层插件（如 ConcertSyncClient/ConcertSyncServer）使用。

如果需要在蓝图中使用 Multi-User 功能，应使用上层的 Multi-User Editing UI，而不是直接调用 ConcertMain API。

## C++ 用法

### 头文件引入

```cpp
#include "IConcertClientModule.h"   // 客户端模块
#include "IConcertServerModule.h"   // 服务器模块
#include "IConcertClient.h"         // 客户端接口
#include "IConcertServer.h"         // 服务器接口
#include "IConcertSession.h"        // 会话接口
#include "ConcertMessages.h"        // 管理消息
```

### 基本用法：创建客户端

```cpp
// 来源：IConcertClientModule.h / IConcertClient.h
IConcertClientModule& ClientModule = IConcertClientModule::Get();
IConcertClientPtr Client = ClientModule.CreateClient(TEXT("MultiUser"));

// 配置
UConcertClientConfig* Config = NewObject<UConcertClientConfig>();
Config->DefaultServerURL = TEXT("MyServer");
Config->DefaultSessionName = TEXT("MySession");
Config->ClientSettings.DisplayName = TEXT("Artist1");
Client->Configure(Config);

// 启动并发现服务器
Client->Startup();
Client->StartDiscovery();
```

### 基本用法：创建服务器

```cpp
// 来源：IConcertServerModule.h / IConcertServer.h
IConcertServerModule& ServerModule = IConcertServerModule::Get();

// 需要提供 IConcertServerEventSink 实现
IConcertServerPtr Server = ServerModule.CreateServer(
    TEXT("MultiUser"),
    FConcertSessionFilter(),  // 自动归档过滤器
    MyEventSink);             // 事件回调实现

// 配置
UConcertServerConfig* Config = NewObject<UConcertServerConfig>();
Config->ServerName = TEXT("MyServer");
Config->DefaultSessionName = TEXT("MySession");
Server->Configure(Config);

// 启动
Server->Startup();
```

### 进阶用法：自定义消息

```cpp
// 来源：IConcertSession.h
// 定义自定义事件
USTRUCT()
struct FMyEvent : public FConcertEventData
{
    GENERATED_BODY()
    FString Message;
};

// 注册处理器
Session->RegisterCustomEventHandler<FMyEvent>(
    [](const FConcertSessionContext& Ctx, const FMyEvent& Evt)
    {
        UE_LOG(LogTemp, Log, TEXT("Received: %s"), *Evt.Message);
    });

// 发送事件
FMyEvent Evt;
Evt.Message = TEXT("Hello!");
Session->SendCustomEvent(Evt, TargetEndpointId,
    EConcertMessageFlags::ReliableOrdered);
```

## Demo 示例

完整的最小客户端-服务器示例：

```cpp
// MyConcertExample.h
#pragma once
#include "IConcertClientModule.h"
#include "IConcertServerModule.h"
#include "IConcertServerEventSink.h"

class FMyConcertExample
{
public:
    void StartServer()
    {
        IConcertServerModule& Mod = IConcertServerModule::Get();
        Server = Mod.CreateServer(TEXT("Example"), FConcertSessionFilter(), &EventSink);

        UConcertServerConfig* Cfg = NewObject<UConcertServerConfig>();
        Cfg->ServerName = TEXT("ExampleServer");
        Server->Configure(Cfg);
        Server->Startup();
    }

    void ConnectClient(const FString& DisplayName)
    {
        IConcertClientModule& Mod = IConcertClientModule::Get();
        Client = Mod.CreateClient(TEXT("Example"));

        UConcertClientConfig* Cfg = NewObject<UConcertClientConfig>();
        Cfg->ClientSettings.DisplayName = DisplayName;
        Cfg->DefaultServerURL = TEXT("ExampleServer");
        Client->Configure(Cfg);
        Client->Startup();
        Client->StartDiscovery();
    }

private:
    IConcertServerPtr Server;
    IConcertClientPtr Client;
    // IConcertServerEventSink 的具体实现（需自行提供）
    FMyEventSink EventSink;
};
```

**Build.cs 依赖：**

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Concert",
    "ConcertClient",  // 或 "ConcertServer"
    "ConcertTransport",
});
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础引擎功能 |
| `CoreUObject` | UObject 反射系统 |
| `ConcertTransport` | 底层消息传输 |
| `Concert` | 会话接口和管理消息 |
| `Serialization` | 数据序列化 |
| `GameplayTags` | 角色标签（仅 Client） |
| `Engine` | 引擎核心（仅 Client） |
| `MessagingCommon` | 消息系统基础（仅 Transport） |
| `TraceLog` | Insights 追踪（仅 Transport） |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-09-23 | `dad0163` | 修复 Multi-User 服务器中用户不被允许加入时的崩溃 |
| 2025-09-12 | `ce6ff39` | 修复 `FTSTicker::RemoveTicker` 的 nodiscard 警告 |
| 2025-08-29 | `1d7d2cd` | 修复 no-PCH 配置下的缺失 include |

### 维护评价

- **活跃维护** — 最近 6 个月内持续有更新
- 创建于 2019 年（约 7 年前），属于老古董级别
- 仍在**活跃维护中**，最近的更新包括 bug 修复、性能改进（发现线程移出游戏线程）和编译修复
- 标记为 `IsBetaVersion: true`，`EnabledByDefault: false`，属于实验性功能
- **推荐使用** — 作为 UE5 Multi-User Editing 的基础设施，它是唯一的选择。虽然标记为 Beta，但已在 Epic 内部广泛使用
- 注意：该插件**仅在编辑器环境**（UncookedOnly）中加载，不参与游戏打包

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertMain)
- 官方文档（无，.uplugin 中 DocsURL 为空）
- 上层插件：ConcertSyncCore, ConcertSyncClient, ConcertSyncServer（实现实际的 Actor/事务同步）
