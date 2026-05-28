# Concert Sync - Server

> Server plugin to enables multi-users editor sessions

| 属性 | 值 |
|---|---|
| 中文名 | 多用户同步服务器 |
| 分类 | Networking |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ConcertSyncServer` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-01-10 |
| 年龄标签 | 🏛️ 文物（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertSync/ConcertSyncServer) | |

## 用途

ConcertSyncServer 是 UE5 **多用户编辑（Multi-User Editing / Concert）** 系统的**服务器端核心**。它不是普通的编辑器插件，而是专为独立服务器程序（如 `UnrealMultiUserServer`）设计的后端服务。

该插件解决的核心问题是：**在多人协同编辑同一个 UE 项目时，如何管理会话状态、同步事务、分配复制权限、处理资源锁定，以及将所有活动持久化到数据库中以便回放和恢复。**

具体职责包括：

- **会话管理**：创建、存档、恢复、复制、导出多用户编辑会话
- **工作区同步**：接收客户端的包更新（Package Update）、事务（Transaction），并向其他客户端广播
- **资源锁定**：防止多人同时编辑同一个资产导致冲突
- **属性复制（Replication）**：管理对象级复制的权限分配（Authority）、静音状态（Mute）、同步控制（Sync Control）
- **序列器协同**：同步多客户端的 Sequencer 打开/关闭/预加载状态
- **活动记录**：将所有操作记录为 Activity，支持回放、恢复和灾难恢复
- **文件共享**：支持大文件的高效交换

**为什么存在**：多用户编辑需要一个中央服务器来充当"真相来源（Ground Truth）"，协调多个 UE 编辑器实例之间的状态。此插件就是该服务器的实现。

## 使用场景

- 你的团队需要多个编辑器实例**同时编辑同一个关卡**，且实时看到彼此的修改 → 启动一个 UnrealMultiUserServer 并运行此插件
- 你需要**灾难恢复**功能：服务器记录所有活动，编辑器崩溃后可以从服务器恢复状态 → 使用此插件的活动归档和恢复机制
- 你在做 **Pixel Streaming 协作**或 **Remote Control** 场景 → 底层依赖此服务器
- 你需要自定义服务器行为（如自定义文件共享服务、自定义初始化流程）→ 使用 `ConcertSyncServerLoop` API

**注意**：此插件仅对特定程序可用（`UnrealMultiUserServer`、`CoopMultiUserServer` 等），不适用于普通游戏运行时或编辑器模块。

## 蓝图用法

此插件为纯 C++ 服务器模块，**不包含蓝图可调用的接口**。所有 API 均为 C++ 接口，供服务器程序使用。

## C++ 用法

### 头文件引入

```cpp
// 模块接口
#include "IConcertSyncServerModule.h"

// 服务器实例接口
#include "IConcertSyncServer.h"

// 服务器主循环（独立程序入口）
#include "ConcertSyncServerLoop.h"

// 服务器循环初始化参数
#include "ConcertSyncServerLoopInitArgs.h"
```

### 基本用法 — 创建和启动服务器

通过模块接口创建服务器实例并启动：

```cpp
#include "IConcertSyncServerModule.h"
#include "IConcertSyncServer.h"

// 获取模块
IConcertSyncServerModule& ServerModule = IConcertSyncServerModule::Get();

// 创建服务器，指定角色（如 "MultiUser"）和自动归档过滤器
FConcertSessionFilter AutoArchiveFilter;
TSharedRef<IConcertSyncServer> Server = ServerModule.CreateServer(TEXT("MultiUser"), AutoArchiveFilter);

// 启动服务器（传入配置和会话标志）
Server->Startup(ServerConfig, EConcertSyncSessionFlags::None);
```

### 基本用法 — 独立服务器主循环

对于独立服务器程序，使用阻塞式主循环：

```cpp
#include "ConcertSyncServerLoop.h"
#include "ConcertSyncServerLoopInitArgs.h"

// 配置初始化参数
FConcertSyncServerLoopInitArgs InitArgs;
InitArgs.IdealFramerate = 60;
InitArgs.ServiceRole = TEXT("MultiUser");
InitArgs.ServiceFriendlyName = TEXT("Multi-User Server");
InitArgs.SessionFlags = EConcertSyncSessionFlags::None;
InitArgs.bShowConsole = true;

// 可选：配置服务器设置（从命令行解析）
InitArgs.GetServerConfigFunc = [&ServerModule, CommandLine]() -> const UConcertServerConfig*
{
    return ServerModule.ParseServerSettings(CommandLine);
};

// 可选：初始化前回调
InitArgs.PreInitServerLoop.AddLambda([]()
{
    // 在服务器循环初始化前执行自定义逻辑
});

// 可选：初始化后回调
InitArgs.PostInitServerLoop.AddLambda([](TSharedRef<IConcertSyncServer> InServer)
{
    // 在服务器循环开始前执行自定义初始化
});

// 可选：每帧回调
InitArgs.TickPostGameThread.AddLambda([](double DeltaTime)
{
    // 在游戏线程 Tick 之后执行自定义逻辑
});

// 运行阻塞式服务器主循环
int32 ExitCode = ConcertSyncServerLoop(FCommandLine::Get(), InitArgs);

// 关闭服务器
ShutdownConcertSyncServer(InitArgs.ServiceFriendlyName);
```

### 基本用法 — 设置文件共享服务

大文件传输需要配置文件共享服务：

```cpp
// 方式一：通过 InitArgs 静态设置
TSharedRef<IConcertFileSharingService> FileService = ServerModule.CreateFileSharingService(TEXT("MultiUser"));
InitArgs.FileSharingService = FileService;

// 方式二：通过 InitArgs 延迟获取（推荐）
InitArgs.GetFileSharingServiceFunc = [&ServerModule]() -> TSharedPtr<IConcertFileSharingService>
{
    return ServerModule.CreateFileSharingService(TEXT("MultiUser"));
};

// 方式三：通过 Server 接口设置
Server->SetFileSharingService(FileService);
```

### 进阶用法 — 获取会话数据库

服务器运行后，可访问实时会话和归档会话的数据库：

```cpp
// 获取实时会话数据库
FGuid SessionId = /* 会话 ID */;
TOptional<FConcertSyncSessionDatabaseNonNullPtr> LiveDb = Server->GetLiveSessionDatabase(SessionId);
if (LiveDb.IsSet())
{
    FConcertSyncSessionDatabase* Database = LiveDb.GetValue();
    // 使用数据库查询活动历史...
}

// 获取归档会话数据库
TOptional<FConcertSyncSessionDatabaseNonNullPtr> ArchivedDb = Server->GetArchivedSessionDatabase(SessionId);
if (ArchivedDb.IsSet())
{
    FConcertSyncSessionDatabase* Database = ArchivedDb.GetValue();
    // 使用数据库查询归档数据...
}
```

### 进阶用法 — 监听服务器创建事件

```cpp
#include "IConcertSyncServerModule.h"

IConcertSyncServerModule& ServerModule = IConcertSyncServerModule::Get();

// 注册服务器创建回调
ServerModule.OnServerCreated().AddLambda([](TWeakPtr<IConcertSyncServer> WeakServer)
{
    if (TSharedPtr<IConcertSyncServer> Server = WeakServer.Pin())
    {
        // 服务器已创建，可执行自定义逻辑
    }
});
```

## Demo 示例

一个最小的独立多用户服务器程序：

```cpp
// MyMultiUserServer.h
#pragma once

#include "CoreMinimal.h"

class FMyMultiUserServerApp
{
public:
    static int32 Main(const TCHAR* CommandLine);
};
```

```cpp
// MyMultiUserServer.cpp
#include "MyMultiUserServer.h"
#include "IConcertSyncServerModule.h"
#include "IConcertSyncServer.h"
#include "ConcertSyncServerLoop.h"
#include "ConcertSyncServerLoopInitArgs.h"

int32 FMyMultiUserServerApp::Main(const TCHAR* CommandLine)
{
    // 解析服务器配置
    IConcertSyncServerModule& ServerModule = IConcertSyncServerModule::Get();
    UConcertServerConfig* ServerConfig = ServerModule.ParseServerSettings(CommandLine);

    // 配置初始化参数
    FConcertSyncServerLoopInitArgs InitArgs;
    InitArgs.IdealFramerate = 30;
    InitArgs.ServiceRole = TEXT("MultiUser");
    InitArgs.ServiceFriendlyName = TEXT("My Multi-User Server");
    InitArgs.SessionFlags = EConcertSyncSessionFlags::AllowRestoreActivities;
    InitArgs.bShowConsole = true;

    // 绑定服务器配置获取函数
    InitArgs.GetServerConfigFunc = [ServerConfig]() -> const UConcertServerConfig*
    {
        return ServerConfig;
    };

    // 创建文件共享服务（用于大文件传输）
    InitArgs.GetFileSharingServiceFunc = [&ServerModule]() -> TSharedPtr<IConcertFileSharingService>
    {
        return ServerModule.CreateFileSharingService(TEXT("MultiUser"));
    };

    // 在服务器初始化后记录日志
    InitArgs.PostInitServerLoop.AddLambda([](TSharedRef<IConcertSyncServer> InServer)
    {
        UE_LOG(LogTemp, Log, TEXT("Multi-User Server started successfully"));
    });

    // 运行阻塞式主循环
    int32 ExitCode = ConcertSyncServerLoop(CommandLine, InitArgs);

    // 关闭
    ShutdownConcertSyncServer(InitArgs.ServiceFriendlyName);

    return ExitCode;
}
```

## 模块依赖

从 Build.cs 和 .uplugin 的 Plugins 字段提取：

| 模块/插件 | 用途 |
|---|---|
| `ConcertMain` | Concert 系统核心，提供基础会话和消息框架 |
| `ConcertSyncCore` | Concert 同步核心，提供数据库、活动记录、复制缓存等共享逻辑 |

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `43543b9f` | Fix missing #include. | 修复缺失的头文件引用 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF |
| 2025-12-08 | `ce8c0205` | Implements a file sharing system that can be used with Multi-user. FConcertCloudSharingService will | 实现多用户文件共享系统，支持云文件共享服务 |
| 2025-11-05 | `84b1f524` | Fix Multi-user data store to allow for oodle compression type by splitting the compression details s | 修复数据存储以支持 Oodle 压缩类型 |
| 2025-08-25 | `baa46427` | Multi User Server: Fix Concert.Replication.LogAuthorityRequestsAndResponsesOnServer not logging auth | 修复服务器端复制权限日志记录不生效的问题 |

### 维护评价

- **创建时间**：2019 年 1 月，约 7 年历史
- **最近更新**：2026 年 4 月仍有活跃更新（日志迁移、缺失引用修复）
- **功能更新频率**：2025 年有多次实质性功能更新（文件共享、压缩支持、日志修复），维护活跃
- **实验性状态**：`IsBetaVersion=true`，`EnabledByDefault=false`，`Hidden=true` — 该插件仍处于 Beta 阶段
- **限制**：
  - 仅限特定程序（UnrealMultiUserServer 等）使用，不适用于普通编辑器或游戏运行时
  - Beta 状态意味着 API 可能在未来版本中发生变化
  - 需要配合 `ConcertMain` 和 `ConcertSyncCore` 插件使用
- **推荐**：✅ 如果你在开发多用户编辑服务器或需要灾难恢复功能，此插件是必经之路。虽然标记为 Beta，但它是 UE 官方 Multi-User Editing 功能的核心服务器实现，Epic 持续维护中。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertSync/ConcertSyncServer)
- [官方文档](https://docs.unrealengine.com/en-US/ProductionPipelines/LevelDesign/MultiUserEditing/)（Multi-User Editing）