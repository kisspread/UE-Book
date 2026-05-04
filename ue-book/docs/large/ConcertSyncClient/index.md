# Concert Sync - Client

> Client plugin to enables multi-users editor sessions when connecting to a Concert Server

| 属性 | 值 |
|---|---|
| 分类 | Networking |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质、网格体、桌面/VR 表现资产） |
| 模块 | `ConcertSyncClient` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-01-10 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertSync/ConcertSyncClient) | |

## 用途

ConcertSyncClient 是 UE5 Multi-User Editing（多人协作编辑）系统的**客户端实现**。它为编辑器提供连接到 Concert Server 后的完整同步能力，包括：

- **资产同步**（Package Bridge）：将本地编辑器的资产保存/丢弃事件转化为 Concert 网络消息，并将远端资产变更应用到本地沙盒
- **事务同步**（Transaction Bridge）：拦截编辑器的 Undo/Redo 事务系统，将本地事务序列化后发送给其他客户端，同时将远端事务反序列化后应用到本地对象
- **对象复制**（Replication）：实时同步 UObject 属性变化，支持权限管理（Authority）、静音（Muting）、流注册（Stream Registration）
- **用户存在感**（Presence）：在编辑器视口中显示其他用户的 3D 头像、VR 控制器和桌面显示器，支持桌面和 VR 两种表现模式
- **Sequencer 同步**：同步 Sequencer 的播放状态、时间轴位置，支持远程打开/关闭 Sequencer UI
- **数据存储**（Data Store）：提供一个跨客户端共享的键值存储，支持原子比较交换操作
- **资源锁定**：防止多个用户同时编辑同一资产
- **变更持久化**：将会话中的修改保存到本地磁盘并准备源码控制提交

这个 plugin **不会**独立工作——它依赖 `ConcertSyncCore` 提供的核心同步逻辑和 `ConcertMain` 提供的连接管理 UI。ConcertSyncClient 专注于**客户端侧**的编辑器集成：监听编辑器事件、管理沙盒文件系统、在视口中渲染其他用户的存在感等。

## 使用场景

- 你的团队需要在同一关卡中同时编辑不同的 Actor → 使用 Multi-User Editing 连接到 Concert Server
- 你需要在 VR 中预览场景，同时看到同事在桌面端的视角 → Presence 系统会在视口中显示桌面用户的位置
- 你需要分布式地分配编辑权限，避免两人同时修改同一个 Blueprint → 资源锁定系统会阻止冲突
- 你使用 Live Link Hub 进行虚拟制片，需要多机协同 → 本插件通过 `SupportedPrograms` 限制仅在 `LiveLinkHub` 中可用

> **注意**：本插件默认禁用（`EnabledByDefault: false`），需要手动在插件管理器中启用。它也是实验性功能（`IsBetaVersion: true`）。

## C++ 用法

### 模块入口

```cpp
#include "IConcertSyncClientModule.h"
```

通过 `IConcertSyncClientModule::Get()` 获取模块单例，然后通过 `CreateClient()` 创建同步客户端实例。

### 创建和启动客户端

```cpp
// 获取模块
IConcertSyncClientModule& SyncClientModule = IConcertSyncClientModule::Get();

// 解析命令行参数并创建客户端配置
UConcertClientConfig* ClientSettings = SyncClientModule.ParseClientSettings(FCommandLine::Get());

// 创建同步客户端（角色名用于区分不同用途的客户端，如 "MultiUser"、"DisasterRecovery"）
TSharedRef<IConcertSyncClient> SyncClient = SyncClientModule.CreateClient(TEXT("MultiUser"));

// 启动客户端，传入配置和会话标志
SyncClient->Startup(ClientSettings, EConcertSyncSessionFlags::EnablePackages | EConcertSyncSessionFlags::EnablePresence);
```

### 获取各子系统

```cpp
// 工作区 —— 管理资产变更、资源锁定、活动历史
TSharedPtr<IConcertClientWorkspace> Workspace = SyncClient->GetWorkspace();

// 存在感管理器 —— 管理其他用户的 3D 头像显示
IConcertClientPresenceManager* PresenceMgr = SyncClient->GetPresenceManager();

// Sequencer 管理器 —— 管理 Sequencer 播放同步
IConcertClientSequencerManager* SequencerMgr = SyncClient->GetSequencerManager();

// 复制管理器 —— 管理 UObject 实时属性同步
IConcertClientReplicationManager* ReplicationMgr = SyncClient->GetReplicationManager();

// 桥接器 —— 编辑器子系统与 Concert 之间的适配层
IConcertClientTransactionBridge* TxnBridge = SyncClient->GetTransactionBridge();
IConcertClientPackageBridge* PkgBridge = SyncClient->GetPackageBridge();
IConcertClientReplicationBridge* ReplBridge = SyncClient->GetReplicationBridge();
```

### 资源锁定与解锁

```cpp
// 锁定一个资源（其他用户将无法编辑它）
TArray<FName> Resources = { FName(TEXT("/Game/Maps/MyLevel")) };
Workspace->LockResources(Resources).Next([](FConcertResourceLockResponse Response)
{
    if (Response.LockStatus == EConcertResourceLockType::Locked)
    {
        UE_LOG(LogTemp, Log, TEXT("Resource locked successfully"));
    }
});

// 解锁资源
Workspace->UnlockResources(Resources);
```

### 使用共享数据存储

```cpp
// 初始化一个共享计数器
FName Key(TEXT("CameraId"));
int64 InitialValue = 0;

Workspace->GetDataStore().FetchOrAdd(Key, InitialValue).Next([](const TConcertDataStoreResult<int64>& Result)
{
    if (Result)
    {
        int64 CameraId = Result.GetValue();
        UE_LOG(LogTemp, Log, TEXT("Camera ID: %lld"), CameraId);
    }
});

// 原子比较交换 —— 生成唯一 ID
int64 Expected = 0;
int64 Desired = 1;
Workspace->GetDataStore().CompareExchange(Key, Expected, Desired).Next([](const TConcertDataStoreResult<int64>& Result)
{
    if (Result.GetCode() == EConcertDataStoreResultCode::Exchanged)
    {
        UE_LOG(LogTemp, Log, TEXT("Acquired unique camera ID"));
    }
});
```

### 持久化会话变更

```cpp
// 持久化特定包
TArray<FName> Packages = { FName(TEXT("/Game/Maps/MyLevel")) };
SyncClient->PersistSpecificChanges(Packages);

// 持久化所有变更
SyncClient->PersistAllSessionChanges();
```

### 复制系统（Replication）

```cpp
// 加入复制会话
using namespace UE::ConcertSyncClient::Replication;
FJoinReplicatedSessionArgs Args;
Args.Streams.Add(MyReplicationStream); // FConcertReplicationStream

SyncClient->GetReplicationManager()->JoinReplicationSession(Args).Next(
    [](FJoinReplicatedSessionResult Result)
    {
        if (Result.ErrorCode == EJoinReplicationErrorCode::Success)
        {
            UE_LOG(LogTemp, Log, TEXT("Joined replication session"));
        }
    });

// 获取权限
TArray<FSoftObjectPath> Objects = { FSoftObjectPath(TEXT("/Game/Maps/MyLevel.MyLevel:PersistentLevel.MyActor")) };
SyncClient->GetReplicationManager()->TakeAuthorityOver(Objects);

// 离开复制会话
SyncClient->GetReplicationManager()->LeaveReplicationSession();
```

### 监听工作区生命周期

```cpp
// 工作区启动时
SyncClient->OnWorkspaceStartup().AddLambda([](const TSharedPtr<IConcertClientWorkspace>& InWorkspace)
{
    UE_LOG(LogTemp, Log, TEXT("Workspace created, session is active"));
});

// 工作区关闭时
SyncClient->OnWorkspaceShutdown().AddLambda([](const TSharedPtr<IConcertClientWorkspace>& InWorkspace)
{
    UE_LOG(LogTemp, Log, TEXT("Workspace destroyed"));
});

// 同步会话启动前
SyncClient->OnSyncSessionStartup().AddLambda([](const IConcertSyncClient* InClient)
{
    UE_LOG(LogTemp, Log, TEXT("Sync session starting"));
});
```

### 检查资产是否被其他用户修改

```cpp
FName AssetName(TEXT("/Game/Blueprints/MyBlueprint"));
int32 OtherClientCount = 0;
TArray<FConcertClientInfo> OtherClients;

if (Workspace->IsAssetModifiedByOtherClients(AssetName, &OtherClientCount, &OtherClients, 5))
{
    for (const FConcertClientInfo& Client : OtherClients)
    {
        UE_LOG(LogTemp, Warning, TEXT("Asset modified by: %s"), *Client.DisplayName);
    }
}
```

### 获取会话活动历史

```cpp
int64 LastActivityId = Workspace->GetLastActivityId();
TMap<FGuid, FConcertClientInfo> ClientInfoMap;
TArray<FConcertSessionActivity> Activities;

// 获取最近 50 个活动
Workspace->GetActivities(FMath::Max<int64>(1, LastActivityId - 49), 50, ClientInfoMap, Activities);

for (const FConcertSessionActivity& Activity : Activities)
{
    // 处理每个活动（事务、包保存、连接事件等）
}
```

### 事务桥接过滤

```cpp
// 注册事务过滤器，排除某些对象的同步
SyncClient->GetTransactionBridge()->RegisterTransactionFilter(
    FName(TEXT("MyFilter")),
    FOnFilterTransactionDelegate::CreateLambda([](const FConcertTransactionFilterArgs& Args) -> ETransactionFilterResult
    {
        // 排除特定对象
        if (Args.ObjectToFilter && Args.ObjectToFilter->GetName() == TEXT("LocalOnlyActor"))
        {
            return ETransactionFilterResult::ExcludeObject;
        }
        return ETransactionFilterResult::UseDefault;
    })
);
```

## 子模块概览

本插件是一个大型模块（约 95 个源文件），按功能划分为以下子系统：

### 核心架构

| 组件 | 文件 | 说明 |
|---|---|---|
| 模块入口 | `ConcertSyncClientModule` | 模块加载、客户端工厂、桥接器管理 |
| 同步客户端 | `ConcertSyncClient` | 顶层客户端实现，管理所有子系统生命周期 |
| 活动会话 | `ConcertSyncClientLiveSession` | 连接后的活跃会话封装 |

### 工作区与资产

| 组件 | 文件 | 说明 |
|---|---|---|
| 工作区 | `ConcertClientWorkspace` | 沙盒文件系统、资源锁定、活动查询、持久化 |
| 包桥接 | `ConcertClientPackageBridge` | 监听编辑器资产事件，过滤/转换为 Concert 消息 |
| 包管理器 | `ConcertClientPackageManager` | 管理沙盒中的包加载、重载、保存 |
| 沙盒平台文件 | `ConcertSandboxPlatformFile` | 虚拟文件系统层，将文件操作重定向到沙盒 |
| 源码控制代理 | `ConcertSourceControlProxy` | 在会话期间代理源码控制操作 |

### 事务系统

| 组件 | 文件 | 说明 |
|---|---|---|
| 事务桥接 | `ConcertClientTransactionBridge` | 拦截编辑器 Undo 事务，序列化/反序列化为 Concert 格式 |
| 事务管理器 | `ConcertClientTransactionManager` | 管理事务的发送队列和接收应用 |
| 实时事务作者追踪 | `ConcertClientLiveTransactionAuthors` | 追踪哪个客户端正在编辑哪个包 |

### 复制系统

| 组件 | 文件 | 说明 |
|---|---|---|
| 复制管理器 | `Replication/Manager/ReplicationManager` | 状态机驱动的复制会话管理 |
| 复制桥接 | `ConcertClientReplicationBridge` | 追踪 UObject 可用性（关卡加载/卸载） |
| 复制数据收集器 | `ClientReplicationDataCollector` | 收集待发送的属性变化 |
| 复制数据队列器 | `ClientReplicationDataQueuer` | 排队和批处理复制数据 |
| 复制应用处理器 | `ObjectReplicationApplierProcessor` | 将接收到的复制数据应用到本地对象 |

### 存在感与 UI

| 组件 | 文件 | 说明 |
|---|---|---|
| 存在感管理器 | `ConcertClientPresenceManager` | 管理所有客户端的 3D 头像显示和可见性 |
| 存在感模式 | `ConcertClientPresenceMode` | 桌面/VR 表现模式实现 |
| 桌面存在感 Actor | `ConcertClientDesktopPresenceActor` | 桌面用户的 3D 显示（显示器+头像） |
| VR 存在感 Actor | `ConcertClientVRPresenceActor` | VR 用户的 3D 显示（HMD+手柄） |
| Sequencer 管理器 | `ConcertClientSequencerManager` | Sequencer 播放同步、远程打开/关闭 |

### 其他

| 组件 | 文件 | 说明 |
|---|---|---|
| 数据存储 | `ConcertClientDataStore` | 跨客户端共享键值存储 |
| 活动流 | `ConcertActivityStream` | 异步流式获取服务器活动历史 |
| 对象工厂 | `ConcertClientObjectFactory` | 创建会话专用对象（如存在感 Actor） |
| 客户端移动 | `ConcertClientMovement` | 客户端视口/VR 位置插值和同步 |

## 模块依赖

从 `ConcertSyncClient.Build.cs` 提取：

### Public 依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心（Actor、World 等） |
| `Concert` | Concert 协议定义和共享类型 |
| `ConcertClient` | Concert 客户端连接管理 |
| `ConcertSyncCore` | 同步核心逻辑（会话数据库、事件类型） |

### Private 依赖

| 模块 | 用途 |
|---|---|
| `AssetRegistry` | 资产注册表查询 |
| `ConcertTransport` | Concert 网络传输层 |
| `HeadMountedDisplay` | VR HMD 支持 |
| `InputCore` | 输入系统（用于 VR 控制器） |
| `JsonUtilities` | JSON 序列化 |
| `LevelSequence` / `MovieScene` | Sequencer 集成 |
| `RenderCore` | 渲染支持 |
| `TimeManagement` | 时间同步 |
| `SlateCore` / `Slate` | UI 框架 |
| `SourceControl` | 源码控制集成 |
| `Serialization` | 序列化框架 |
| `TraceLog` | 跟踪日志 |

### 编辑器额外依赖（`bBuildEditor`）

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 编辑器框架 |
| `LevelEditor` | 关卡编辑器集成 |
| `Sequencer` | Sequencer 编辑器集成 |
| `EditorFramework` / `EditorStyle` | 编辑器 UI |
| `EngineSettings` | 引擎设置访问 |
| `ViewportInteraction` | 视口交互（VR 操作） |
| `VREditor` | VR 编辑器集成 |
| `TypedElementRuntime` / `TypedElementFramework` | 类型化元素系统 |
| `DirectoryWatcher` | 文件系统监控（动态加载） |

## 维护状态

### 近期更新

| 日期 | Hash | 提交信息 | 解读 |
|---|---|---|---|
| 2025-10-06 | `ea22e082` | Multi User: Fix crash when deleting Level Sequence in a MU session | 修复在多人会话中删除 Level Sequence 时的崩溃 |
| 2025-10-03 | `e82b0f82` | Address issue found on unregister and explicitly destroy any open players in -game instances | 修复反注册时的问题，显式销毁 `-game` 实例中的播放器 |
| 2025-10-03 | `c3b663dd` | Concert sequencer manager fix for garbage collection on exit | 修复 Sequencer 管理器在退出时的 GC 问题 |

### 维护评价

- **创建时间**：2019 年 1 月，已维护约 7 年
- **活跃程度**：活跃维护中。最近更新在 2025 年 10 月，均为 bug 修复
- **实验性状态**：标记为 `IsBetaVersion: true`，且 `EnabledByDefault: false`，`Hidden: true`
- **稳定性**：最近 3 次提交均为 crash/GC 修复，表明核心功能已成熟但边缘场景仍有问题
- **适用范围**：`SupportedPrograms` 限制为 `LiveLinkHub`，表明 Epic 主要将其定位为虚拟制片工具
- **推荐**：如果你需要 Multi-User Editing 或 Live Link Hub 协作功能，这是必选插件。注意它是实验性的，在生产环境中使用需充分测试

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertSync/ConcertSyncClient)
- [ConcertSyncCore 文档](../ConcertSyncCore/) — 同步核心逻辑
- [ConcertMain](../ConcertMain/) — Concert 连接管理 UI
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Developer/Concert/ConcertSync/ConcertSyncClient/Source/ConcertSyncClient/Test/ConcertClientLiveTransactionAuthorsTests.cpp) — 实时事务作者追踪测试
