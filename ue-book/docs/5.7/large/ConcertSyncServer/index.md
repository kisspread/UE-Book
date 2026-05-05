# Concert Sync - Server

> Server plugin to enables multi-users editor sessions

| 属性 | 值 |
|---|---|
| 分类 | Networking |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ConcertSyncServer` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-01-10 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertSync/ConcertSyncServer) | |

## 用途

ConcertSyncServer 是 Unreal Engine 多用户编辑 (Multi-User Editing, MUE) 功能的服务端核心。它以独立的服务器进程（`UnrealMultiUserServer`、`CoopMultiUserServer`、`UnrealMultiUserSlateServer`、`UnrealRecoverySvc`、`CrashReportClientEditor`）形式运行，接收多个编辑器客户端的连接，管理实时协作会话（Session）。

该插件的核心职责包括：

1. **会话生命周期管理**：创建、销毁、归档（Archive）、恢复（Restore）、导出（Export）协作会话
2. **事务同步**：将一个客户端的 Actor/资产修改（Transaction、Package Change）同步到其他客户端
3. **资源锁管理**：实现资产级别的排他锁，防止多人同时修改同一资产
4. **属性复制 (Replication)**：基于 `EConcertSyncSessionFlags` 可选启用的服务端属性复制系统，包括 Authority 管理、Sync Control、Mute 管理等
5. **Sequencer 同步**：同步多客户端的 Sequencer 打开/关闭/播放状态
6. **数据存储 (Data Store)**：为连接的客户端提供共享的键值存储，支持原子的 FetchOrAdd 和 CompareExchange 操作
7. **会话数据库**：将所有活动（Activity）持久化到 SQLite 数据库，支持后续归档和回放

该插件默认禁用，且隐藏（`Hidden: true`），因为它只在特定的服务器程序中使用，不会在普通编辑器中加载。

## 使用场景

- **多人实时协作编辑**：多个设计师/开发者同时在同一关卡中工作，各自的修改实时同步给其他人 → 启动 `UnrealMultiUserServer`，所有编辑器客户端连接到该服务器
- **灾难恢复 / Undo 历史保存**：服务器记录所有活动到数据库，可归档会话用于事后回溯 → 使用 `UnrealRecoverySvc` 角色
- **PIE/SIE 多人测试**：服务端同步各客户端的 Play In Editor 状态，支持多人联机调试
- **跨团队资产锁定**：通过资源锁机制确保关键资产不被多人同时修改

## 蓝图用法

此插件 **没有暴露任何蓝图节点**。它是一个纯 C++ 服务端模块，不提供 BlueprintCallable 接口。配置通过命令行参数和配置文件完成。

## C++ 用法

### 头文件引入

```cpp
#include "IConcertSyncServerModule.h"
#include "IConcertSyncServer.h"
#include "ConcertSyncServerLoop.h"
#include "ConcertSyncServerLoopInitArgs.h"
```

### 基本用法 — 启动服务器主循环

`ConcertSyncServerLoop` 是一个阻塞式的主循环函数，用于在独立进程中运行 Concert 服务器。

```cpp
// 来源: ConcertSyncServerLoop.inl

// 配置服务器初始化参数
FConcertSyncServerLoopInitArgs InitArgs;
InitArgs.IdealFramerate = 60;
InitArgs.SessionFlags = EConcertSyncSessionFlags::ShouldReplicateProperties; // 启用属性复制
InitArgs.ServiceRole = TEXT("MultiUser");
InitArgs.ServiceFriendlyName = TEXT("Multi-User Server");

// 启动服务器主循环（阻塞调用）
int32 Result = ConcertSyncServerLoop(FCommandLine::Get(), InitArgs);
```

### 进阶用法 — 自定义服务器配置

```cpp
// 来源: ConcertSyncServerModule.cpp

// 通过命令行参数覆盖默认设置
// 支持的命令行参数:
//   -CONCERTSERVER=<name>           服务器名称
//   -CONCERTSESSION=<name>          默认会话名称
//   -CONCERTSESSIONTORESTORE=<name> 从归档恢复的会话名
//   -CONCERTPROJECT=<name>          项目名称
//   -CONCERTREVISION=<revision>     基础版本号
//   -CONCERTWORKINGDIR=<path>       工作目录
//   -CONCERTSAVEDDIR=<path>         归档目录
//   -CONCERTENDPOINTTIMEOUT=<sec>   远端超时秒数
//   -CONCERTCLEAN                   启动时清理工作目录
//   -CONCERTLOGGING                 启用传输层日志
//   -CONCERTIGNORE                  忽略会话设置限制

UConcertServerConfig* ServerConfig = IConcertSyncServerModule::Get().ParseServerSettings(FCommandLine::Get());
```

### 进阶用法 — 自定义初始化钩子

```cpp
// 来源: ConcertSyncServerLoopInitArgs.h

FConcertSyncServerLoopInitArgs InitArgs;

// 在服务器初始化前执行（模块加载前）
InitArgs.PreInitServerLoop.AddLambda([]()
{
    // 自定义预初始化逻辑
});

// 在服务器初始化完成后执行
InitArgs.PostInitServerLoop.AddLambda([](TSharedRef<IConcertSyncServer> Server)
{
    // 自定义后初始化逻辑，例如设置文件共享服务
    Server->SetFileSharingService(MyFileSharingService);
});

// 每帧 Tick 回调
InitArgs.TickPostGameThread.AddLambda([](double DeltaTime)
{
    // 自定义每帧逻辑
});

// 自定义服务器配置获取函数
InitArgs.GetServerConfigFunc = []() -> const UConcertServerConfig*
{
    return GetMyCustomConfig();
};
```

### 进阶用法 — 访问会话数据库

```cpp
// 来源: IConcertSyncServer.h

TSharedPtr<IConcertSyncServer> Server = ...;

// 获取活跃会话的数据库
TOptional<FConcertSyncSessionDatabaseNonNullPtr> LiveDb = Server->GetLiveSessionDatabase(SessionId);
if (LiveDb)
{
    FConcertSyncSessionDatabase& Database = *LiveDb.GetValue();
    // 使用数据库进行查询...
}

// 获取归档会话的数据库
TOptional<FConcertSyncSessionDatabaseNonNullPtr> ArchivedDb = Server->GetArchivedSessionDatabase(ArchivedSessionId);
```

## Demo 示例

由于此插件仅在专用服务器进程中运行，典型用法是创建一个自定义的服务器 Target：

**MyMultiUserServer.Target.cs**

```csharp
using UnrealBuildTool;

public class MyMultiUserServerTarget : TargetRules
{
    public MyMultiUserServerTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Program;
        DefaultBuildSettings = BuildSettingsVersion.V4;
        IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_3;

        ExtraModuleNames.Add("Launch");

        // 启用 UDP 或 QUIC 传输插件（二选一）
        bWithQuic = true;
    }
}
```

**服务器入口代码**

```cpp
#include "ConcertSyncServerLoop.h"

int main(int argc, char* argv[])
{
    FConcertSyncServerLoopInitArgs InitArgs;
    InitArgs.IdealFramerate = 60;
    InitArgs.SessionFlags = EConcertSyncSessionFlags::ShouldReplicateProperties;
    InitArgs.ServiceRole = TEXT("MultiUser");
    InitArgs.ServiceFriendlyName = TEXT("My Multi-User Server");

    return ConcertSyncServerLoop(FCommandLine::Get(), InitArgs);
}
```

## 架构概览

### 源码结构（58 个源文件）

```
Source/ConcertSyncServer/
├── Public/
│   ├── IConcertSyncServerModule.h          # 模块接口（入口）
│   ├── IConcertSyncServer.h                # 服务器接口
│   ├── ConcertSyncServerLoop.h             # 服务器主循环
│   ├── ConcertSyncServerLoop.inl           # 主循环实现（含 LaunchEngineLoop 依赖）
│   ├── ConcertSyncServerLoopInitArgs.h     # 初始化参数结构体
│   └── Replication/
│       ├── IConcertServerReplicationManager.h  # 复制管理器接口
│       └── IReplicationWorkspace.h             # 复制工作空间接口（支持单元测试 mock）
├── Private/
│   ├── ConcertSyncServerModule.cpp         # 模块实现
│   ├── ConcertSyncServer.h/.cpp           # 服务器核心实现
│   ├── ConcertSyncServerLiveSession.h/.cpp # 活跃会话封装
│   ├── ConcertSyncServerArchivedSession.h/.cpp  # 归档会话封装
│   ├── ConcertServerWorkspace.h/.cpp       # 工作空间（事务/锁/同步管理）
│   ├── ConcertServerSyncCommandQueue.h/.cpp  # 同步命令队列
│   ├── ConcertServerSequencerManager.h/.cpp  # Sequencer 状态同步
│   ├── ConcertServerDataStore.h/.cpp       # 共享键值存储
│   ├── ConcertServerEventForwardingSink.h  # CRTP 事件转发模板
│   └── Replication/
│       ├── ConcertServerReplicationManager.h/.cpp  # 复制管理器核心
│       ├── ConcertReplicationClient.h/.cpp  # 客户端复制状态
│       ├── AuthorityManager.h/.cpp          # Authority 管理
│       ├── SyncControlManager.h/.cpp        # Sync Control 管理
│       ├── ReplicationWorkspace.h/.cpp       # 复制工作空间实现
│       ├── Muting/
│       │   ├── MuteManager.h/.cpp           # 全局 Mute 管理
│       │   ├── ObjectHierarchyAdapter.h     # 对象层级适配
│       │   ├── PredictedStateObjectHierarchy.h/.cpp
│       │   └── IMuteValidationObjectHierarchy.h
│       ├── Processing/
│       │   ├── ServerObjectReplicationReceiver.h/.cpp  # 接收复制数据
│       │   └── ServerReplicationDataQueuer.h/.cpp      # 复制数据队列
│       ├── Enumeration/
│       │   ├── IStreamEnumerator.h          # Stream 枚举接口
│       │   ├── IClientEnumerator.h          # 客户端枚举接口
│       │   └── IRegistrationEnumerator.h    # 注册枚举接口
│       └── Util/
│           ├── StreamChangeValidation.h/.cpp
│           ├── JoinRequestValidation.h/.cpp
│           ├── GroundTruthOverride.h/.cpp
│           ├── ReplicationCVars.h/.cpp      # 控制台变量
│           └── LogUtils.h
```

### 核心类关系

```
IConcertSyncServerModule (模块接口)
  └── FConcertSyncServerModule (模块实现)
        └── CreateServer() → IConcertSyncServer
              └── FConcertSyncServer (服务器核心)
                    ├── IConcertServerRef ConcertServer (ConcertMain 提供的服务器)
                    ├── FConcertSyncServerLiveSession[]  (活跃会话)
                    ├── FConcertSyncServerArchivedSession[] (归档会话)
                    ├── FConcertServerWorkspace[]  (每个活跃会话一个)
                    │     ├── FConcertServerSyncCommandQueue (同步队列)
                    │     ├── FConcertServerDataStore (数据存储)
                    │     ├── FReplicationWorkspace (复制数据)
                    │     └── LockedResources (资源锁)
                    ├── FConcertServerSequencerManager[] (Sequencer 管理)
                    └── FConcertServerReplicationManager[] (复制管理)
                          ├── FAuthorityManager (Authority)
                          ├── FMuteManager (Mute)
                          ├── FSyncControlManager (Sync Control)
                          ├── FObjectReplicationCache (复制缓存)
                          └── FConcertReplicationClient[] (客户端状态)
```

### 活动类型 (Activity Types)

服务器将所有会话活动记录到 SQLite 数据库，支持以下 6 种活动类型：

| 类型 | 说明 |
|---|---|
| `Connection` | 客户端连接/断开 |
| `Lock` | 资源锁变更 |
| `Transaction` | Actor 属性修改（事务） |
| `Package` | 资产包修改 |
| `Replication` | 复制状态变更（加入/离开/静音） |
| *(Count=6)* | 枚举计数守卫 |

### 复制系统子模块

属性复制系统是后期加入的重要功能，由以下子模块协作：

- **AuthorityManager**：跟踪每个客户端对哪些对象/属性拥有 Authority（即"谁有权发送数据"）。第一个注册属性的客户端获得 Authority，后续冲突可被检测和处理。
- **SyncControlManager**：决定客户端是否应该开始/停止复制。条件：客户端有 Authority 且有其他客户端在监听。
- **MuteManager**：管理全局 Mute 状态。支持显式 Mute/Unmute，以及基于对象层级的隐式 Mute 传播（`ObjectAndSubobjects` 标志）。
- **ConcertReplicationClient**：每个连接客户端的服务端复制代理，管理该客户端的 Stream 描述和数据发送频率。
- **ServerObjectReplicationReceiver**：接收来自所有端点的复制数据。
- **ServerReplicationDataQueuer**：将复制数据排队，带时间预算处理。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Concert` | Concert 基础框架（消息、数据类型、设置） |
| `ConcertSyncCore` | 同步核心逻辑（数据库、活动、复制格式） |
| `ConcertServer` | Concert 服务器框架（会话管理、传输） |
| `ConcertTransport` | 传输层（UDP/QUIC 消息传递） |
| `Serialization` | 序列化工具 |
| `JsonUtilities` | JSON 序列化/反序列化（SessionInfo.json） |

### 插件依赖

| 插件 | 用途 |
|---|---|
| `ConcertMain` | Concert 主框架（IConcertServer、IConcertSession） |
| `ConcertSyncCore` | 同步核心（数据库、活动类型、复制格式） |

### 运行时要求

服务器进程需要至少启用以下传输插件之一：

| 插件 | 说明 |
|---|---|
| `UdpMessaging` | UDP 消息传输（传统） |
| `QuicMessaging` | QUIC 消息传输（较新，更可靠） |

## 控制台命令

服务器运行时提供以下控制台命令：

| 命令 | 说明 |
|---|---|
| `Replication.LogStreams` | 打印所有客户端注册的复制 Stream |
| `Replication.LogAutority` | 打印所有客户端的 Authority 状态 |

## 控制台变量

| 变量 | 说明 |
|---|---|
| `Concert.Replication.LogStreamRequestsAndResponsesOnServer` | 在服务器上记录 Stream 请求/响应日志 |
| `Concert.Replication.LogAuthorityRequestsAndResponsesOnServer` | 在服务器上记录 Authority 请求/响应日志 |

## 维护状态

### 近期更新

- `baa46427a101` (2025-08-25): 修复 `Concert.Replication.LogAuthorityRequestsAndResponsesOnServer` 不记录日志的问题，将 Stream 和 Authority 的 CVar 日志移到新的 `ReplicationCVars.h`
- `b059f7b46335` (2025-03-13): 修复简单的不可达代码警告
- `742b5d3a99bb` (2025-03-06): 移除 `void` 返回函数上不恰当的 `UE_LIFETIMEBOUND` 使用

### 维护评价

- **创建时间**：2019-01-10，已有 7 年历史
- **维护状态**：**活跃维护** — 最近 6 个月内有实质性更新（2025-08），且修复涉及复制系统的核心日志功能
- **代码质量**：代码结构清晰，采用 CRTP 模式（`TConcertServerEventForwardingSink`）、接口抽象（`IReplicationWorkspace` 支持 mock 测试）、关注点分离（各 Manager 独立职责）
- **标记状态**：`IsBetaVersion: true`，表明 Epic 仍将其视为 Beta 功能
- **隐藏状态**：`Hidden: true`，不会出现在编辑器的插件列表中
- **限制**：
  - 仅在专用服务器进程中加载（`ProgramAllowList`）
  - `UncookedOnly` 模块类型，不包含在打包构建中
  - 复制系统仍在演进中（代码中有多处 TODO 注释）
- **推荐**：如果你正在构建多用户协作工具或自定义服务器程序，这是官方的核心基础设施，推荐基于它构建。对于普通编辑器使用，不需要直接接触此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertSync/ConcertSyncServer)
- 官方文档（无）
- [ConcertSyncCore](../ConcertSyncCore/) — 同步核心逻辑
- [ConcertMain](../../ConcertMain/) — Concert 主框架
- [ConcertServer](../../../Concert/) — 服务器框架
