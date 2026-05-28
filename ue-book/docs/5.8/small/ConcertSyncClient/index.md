# Concert Sync - Client

> Client plugin to enables multi-users editor sessions when connecting to a Concert Server

| 属性 | 值 |
|---|---|
| 中文名 | 多用户编辑客户端 |
| 分类 | Networking |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ConcertSyncClient` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-01-11 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertSync/ConcertSyncClient) | |

## 用途

ConcertSyncClient 插件是 Unreal Engine 多用户编辑（Multi-User Editing）系统的核心客户端组件。它实现了连接到 Concert 服务器后，多个编辑器实例之间进行实时协作所需的所有客户端逻辑。其主要解决的问题包括：

1.  **实时状态同步**：在多个编辑器实例之间同步场景资产的修改（如 Actor 的移动、旋转、属性变化），确保所有参与者看到一致的世界状态。
2.  **存在感知与导航**：让每个用户能在编辑器中看到其他用户的虚拟化身（Avatar），并支持快速传送到其他用户位置。
3.  **协作冲突管理**：处理并解决多个用户同时编辑同一资产时产生的冲突，通过事务（Transaction）系统确保操作的序列化。
4.  **数据与资源共享**：提供共享数据存储、资源锁定机制以及 Sequencer（序列器）同步，以支持复杂的协同工作流程。
5.  **灾难恢复支持**：记录会话活动（Activity）和事务历史，为崩溃恢复提供可能。

简而言之，此插件使多个开发者能够同时在同一个 Unreal Engine 项目上工作，实时看到彼此的更改，从而极大地提升了协作效率，尤其适用于大型项目开发、虚拟制片（Virtual Production）和实时场景搭建等场景。

## 使用场景

- **游戏关卡协同设计**：关卡设计师、灯光师、美术师同时在一个场景中工作。一人在搭建地形，一人在放置灯光，一人在调整材质，所有人的改动实时同步到其他人的视图中。
- **虚拟制片（VP）现场**：虚拟制片现场需要快速迭代。美术修改了虚拟场景中的一个道具，远处的灯光师和摄影师能立即在他们的视口中看到变化。
- **复杂资产的远程审查**：项目负责人可以加入一个协作会话，观察其他成员对某个角色或载具进行的编辑和动画调整，无需对方进行屏幕共享。
- **分布式团队开发**：团队成员位于不同地点，通过 Concert 服务器连接，共同编辑和调试一个复杂的游戏场景或过场动画序列。
- **现场活动与演示**：在直播或现场演示中，多个操作员控制同一个场景的不同部分（如摄像头、灯光、特效），实现复杂的实时视觉效果。

## 蓝图用法

此插件本身主要是一个 C++ 框架，为编辑器内部的多用户功能提供基础。其核心功能（如加入会话、同步修改）通常由编辑器 UI 或其他高级模块（如 `ConcertMain`）调用。直接通过蓝图暴露的节点有限。

### 核心节点

该插件主要通过 C++ 接口提供服务，无直接对应的蓝图可调用节点。其功能集成在编辑器的 “Multi-User Editing” 面板和操作流程中。

### 使用示例（蓝图描述）

蓝图中无法直接使用此插件的底层节点。通常的使用流程是通过编辑器菜单或专用的多用户编辑控制面板启动或加入一个 Concert 会话。会话建立后，所有基于编辑器资产（如 Actor、Material、Sequence）的更改都会自动通过此插件同步。

## C++ 用法

以下代码展示了如何使用 `ConcertSyncClient` 模块提供的关键接口。

### 头文件引入

```cpp
#include "IConcertSyncClientModule.h"
#include "IConcertSyncClient.h"
#include "IConcertClientPresenceManager.h"
#include "IConcertClientReplicationManager.h"
```

### 基本用法：初始化并连接客户端

从 `IConcertSyncClientModule` 创建客户端实例，并设置其运行角色（例如，用于多用户编辑或灾难恢复）。

```cpp
// 获取Concert同步客户端模块
IConcertSyncClientModule& ConcertSyncClientModule = IConcertSyncClientModule::Get();

// 创建一个用于多用户编辑的客户端实例
TSharedRef<IConcertSyncClient> MultiUserClient = ConcertSyncClientModule.CreateClient(TEXT("MultiUser"));

// 准备客户端配置（服务器地址、端口等）
UConcertClientConfig* ClientConfig = ConcertSyncClientModule.ParseClientSettings(FCommandLine::Get());

// 启动客户端，会话标志控制同步行为（如同步编辑器播放模式等）
EConcertSyncSessionFlags SessionFlags = EConcertSyncSessionFlags::ShouldIncludeEditorOnlyData;
MultiUserClient->Startup(ClientConfig, SessionFlags);

// 获取会话工作区，用于管理资产锁和持久化
TSharedPtr<IConcertClientWorkspace> Workspace = MultiUserClient->GetWorkspace();
if (Workspace.IsValid())
{
    // 尝试锁定一个资源包，防止其他用户同时编辑
    TArray<FName> PackagesToLock = { TEXT("/Game/Maps/MyLevel") };
    Workspace->LockResources(PackagesToLock).Next([](FConcertResourceLockResponse Response)
    {
        if (Response.bSuccess)
        {
            UE_LOG(LogConcert, Log, TEXT("Successfully locked level"));
        }
    });
}
```

### 进阶用法：管理存在（Presence）和复制（Replication）

会话启动后，可以获取存在管理器来查看其他用户，并使用复制管理器来控制对象属性的网络复制。

```cpp
// 假设 MultiUserClient 已启动并加入会话
IConcertClientPresenceManager* PresenceMgr = MultiUserClient->GetPresenceManager();
if (PresenceMgr)
{
    // 启用存在显示
    PresenceMgr->SetPresenceEnabled(true);

    // 设置一个特定用户的化身可见性
    FGuid SomeEndpointId = /* 从会话客户端列表获取的ID */;
    PresenceMgr->SetPresenceVisibility(SomeEndpointId, true);

    // 传送到某个用户的位置
    PresenceMgr->InitiateJumpToPresence(SomeEndpointId);
}

// 获取复制管理器，用于同步对象的属性（如Transform, Visibility等）
IConcertClientReplicationManager* ReplicationMgr = MultiUserClient->GetReplicationManager();
if (ReplicationMgr && ReplicationMgr->IsConnectedToReplicationSession())
{
    // 注册一组我们想要复制到服务器的对象
    TArray<FConcertReplicationStream> StreamsToRegister;
    // ... 填充要复制的对象和属性列表 ...

    // 加入复制会话
    UE::ConcertSyncClient::Replication::FJoinReplicatedSessionArgs JoinArgs;
    JoinArgs.Streams = StreamsToRegister;

    ReplicationMgr->JoinReplicationSession(JoinArgs).Next([](
        const UE::ConcertSyncClient::Replication::FJoinReplicatedSessionResult& Result)
    {
        if (Result.ErrorCode == EJoinReplicationErrorCode::Success)
        {
            UE_LOG(LogConcert, Log, TEXT("Successfully joined replication session"));
        }
    });

    // 请求对某个对象的控制权
    FSoftObjectPath ObjectPath(TEXT("/Game/Props/Chair.Chair"));
    ReplicationMgr->TakeAuthorityOver({ObjectPath});
}
```

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何获取 `ConcertSyncClient` 模块并创建一个客户端。请注意，这仅为模块初始化示例，完整的连接和同步需要更多的配置和事件处理。

**MyMultiUserClass.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "IConcertSyncClient.h"

class FMyMultiUserClass
{
public:
    FMyMultiUserClass();
    ~FMyMultiUserClass();

    void StartMultiUserSession();
    void Shutdown();

private:
    TSharedPtr<IConcertSyncClient> SyncClient;
};
```

**MyMultiUserClass.cpp**
```cpp
#include "MyMultiUserClass.h"
#include "IConcertSyncClientModule.h"
#include "ConcertClientConfig.h"

FMyMultiUserClass::FMyMultiUserClass()
{
}

FMyMultiUserClass::~FMyMultiUserClass()
{
    Shutdown();
}

void FMyMultiUserClass::StartMultiUserSession()
{
    if (IConcertSyncClientModule::IsAvailable())
    {
        IConcertSyncClientModule& Module = IConcertSyncClientModule::Get();

        // 创建一个客户端实例，角色可以是任何字符串，用于区分不同用途的客户端
        SyncClient = Module.CreateClient(TEXT("MyCustomClient"));

        // 获取默认或自定义的客户端配置
        UConcertClientConfig* DefaultConfig = NewObject<UConcertClientConfig>();
        DefaultConfig->ClientSettings.ServerURL = TEXT("127.0.0.1");
        DefaultConfig->ClientSettings.ServerPort = 9999;

        // 启动客户端，连接到指定的Concert服务器
        // 启用包含编辑器数据和灾难恢复活动的同步
        EConcertSyncSessionFlags Flags = EConcertSyncSessionFlags::ShouldIncludeEditorOnlyData |
                                         EConcertSyncSessionFlags::ShouldEnableDisasterRecoveryActivities;
        SyncClient->Startup(DefaultConfig, Flags);
    }
}

void FMyMultiUserClass::Shutdown()
{
    if (SyncClient.IsValid())
    {
        SyncClient->Shutdown();
        SyncClient.Reset();
    }
}
```

## 模块依赖

要使用 `ConcertSyncClient` 插件，你的模块需要在 `.Build.cs` 文件中添加以下依赖。它依赖于 Concert 系统的核心模块。

| 模块 | 用途 |
|---|---|
| `ConcertSyncCore` | 提供 Concert 同步的核心数据结构、消息协议和基类。 |
| `ConcertMain` | 提供主 Concert 客户端和服务器连接管理。 |
| `FileSandbox` | 为多用户会话提供沙盒文件系统，隔离各客户端的临时文件修改。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `2e6f87f2` | Concert: Fix manifest file getting overriden on shutdown. | 修复客户端关闭时清单文件被覆盖的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF。 |
| 2026-04-02 | `50a24ff6` | Deprecated GetObjects*/ForEachObjectWithOuter functions that take bool bIncludeNestedObjects. Introduced new functions that take a flags enum. | 废弃了使用布尔参数的旧版对象查询函数，引入了使用枚举标志的新版本。 |
| 2026-03-23 | `eab5e4c7` | Moving TransactionCommon from Engine to CoreUObject. | 将事务通用代码从 Engine 模块迁移到 CoreUObject 模块。 |
| 2026-03-10 | `a69ab07d` | [IsSavingPackage] | (推测) 可能与包保存状态检查相关的更新。 |

### 维护评价

- **创建时间**：该插件创建于 2019 年 1 月，已有约 7 年历史，属于 Unreal Engine 的成熟基础组件。
- **近期活动**：从 2026 年 3 月至 5 月，该插件有持续的更新记录，包括功能修复、API 迁移和重构。这表明它仍在**活跃维护**中。
- **状态**：插件 `.uplugin` 中标记为 `IsBetaVersion: true` 且 `EnabledByDefault: false`，说明它目前处于实验性阶段，并非默认启用，需要用户手动开启。
- **推荐**：对于需要进行多人协作编辑的项目，此插件是官方提供的核心解决方案。尽管处于测试阶段，但由 Epic 官方维护，稳定性有保障。推荐在受控环境（如内部团队或虚拟制片现场）中试用，以提升协作效率。使用前应了解其限制（如实验性状态），并确保团队网络环境稳定。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertSync/ConcertSyncClient)
- [官方文档]() （.uplugin 中未提供 DocsURL）
- [测试用例]() （此插件的测试用例可能位于 `Engine/Tests/` 目录或作为其他集成测试的一部分，未在提供的文件列表中明确列出）