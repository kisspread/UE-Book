# Concert Sync - Client

> Client plugin to enables multi-users editor sessions when connecting to a Concert Server

| 属性 | 值 |
|---|---|
| 中文名 | 多用户编辑客户端 |
| 分类 | Networking |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `ConcertSyncClient` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-01-11 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertSync/ConcertSyncClient) | |

## 用途

ConcertSyncClient 是 Unreal Engine 多用户协作编辑系统（Multi-User Editing）的**客户端核心组件**。它负责在本地编辑器实例与 Concert Server 之间建立同步连接，使多个开发者能够同时编辑同一个关卡和资产。

该插件解决的核心问题包括：
- **事务同步**：将编辑器的 Undo/Redo 事务系统与网络同步桥接，使多个用户的编辑操作实时传播
- **资产管理**：管理本地沙盒中的包文件同步、锁定、持久化，避免多人同时修改同一资产导致冲突
- **对象复制**：提供基于属性级别的复制系统，允许客户端声明要发送/接收的对象属性和流
- **用户存在**：在编辑器视口中显示其他用户的光标、镜头位置和 VR 控制器，直观呈现协作者的操作
- **Sequencer 同步**：在多个用户之间同步 Sequencer 的播放状态、时间轴和远程打开/关闭
- **键值数据存储**：提供客户端间的共享键值存储，用于协调分布式计数器等跨客户端状态

本质上，这个插件是 UE5 Multi-User Editing 功能的客户端引擎，使多个美术、设计师和程序员能够在不互相干扰的前提下协同编辑同一项目。

## 使用场景

- 你正在做一个需要多人同时编辑关卡的大型项目 → 用 Concert 连接到服务器，所有人的编辑操作会实时同步
- 你需要在编辑器中看到其他协作者正在编辑的位置 → Presence Manager 会在视口中显示用户头像
- 你想要多人同时在 Sequencer 中工作并同步播放 → Sequencer Manager 提供播放同步
- 你需要在多人会话中锁定某个资产防止他人修改 → Workspace 提供资源锁定 API
- 你需要在多个客户端间共享计数器或状态变量（如相机 ID）→ 使用 DataStore 的 CompareExchange 实现无冲突并发写入
- 你需要自定义哪些对象参与网络复制 → 使用 ReplicationManager 声明复制流和权限
- 你在使用 LiveLinkHub 进行实时协作 → 该插件作为 LiveLinkHub 的支持组件被引用

## 蓝图用法

该插件主要面向 C++ 开发者，公开的蓝图 API 有限。以下是可在蓝图中使用的关键类和属性。

### 核心 Actor

| Actor 类 | 说明 |
|---|---|
| `AConcertClientPresenceActor` | 其他用户的基础存在表示，包含网格体和文本组件 |
| `AConcertClientVRPresenceActor` | VR 用户的头像，显示左右手控制器和激光指针 |
| `AConcertClientDesktopPresenceActor` | 桌面用户的头像，显示摄像头位置和激光指针 |

### Presence Actor 蓝图属性

| 属性 | 说明 | 所在类 |
|---|---|---|
| `PresenceDeviceType` | 设备类型标识（Oculus/Vive/Desktop） | `AConcertClientPresenceActor` |
| `PresenceMeshComponent` | 显示摄像头位置的网格体组件 | `AConcertClientPresenceActor` |
| `PresenceTextComponent` | 显示用户名称的文本组件 | `AConcertClientPresenceActor` |
| `LeftControllerMeshComponent` | VR 左手控制器网格体 | `AConcertClientVRPresenceActor` |
| `RightControllerMeshComponent` | VR 右手控制器网格体 | `AConcertClientVRPresenceActor` |
| `LaserThickness` | 激光指针粗细 | `AConcertClientVRPresenceActor` |

### 使用示例（蓝图描述）

Presence Actor 是 `Blueprintable` 的，你可以创建子类自定义头像外观：

1. 创建 `AConcertClientPresenceActor` 的蓝图子类
2. 在事件图表中重写 `InitPresence` 事件，使用 `InAssetContainer` 加载自定义网格体和材质
3. 重写 `HandleEvent` 事件来响应特定的用户存在事件
4. 通过 `SetPresenceName` 和 `SetPresenceColor` 接收用户名称和颜色信息
5. 重写 `Tick` 事件实现自定义的移动平滑逻辑

> **注意**：Presence Actor 是 `Transient`、`NotPlaceable`、`IsEditorOnly()` 且不可在场景大纲中列出。它们由 PresenceManager 在运行时自动创建和管理。

## C++ 用法

### 头文件引入

```cpp
// 模块入口
#include "IConcertSyncClientModule.h"

// 核心接口
#include "IConcertSyncClient.h"
#include "IConcertClientWorkspace.h"

// 事务桥接
#include "IConcertClientTransactionBridge.h"

// 包管理桥接
#include "IConcertClientPackageBridge.h"

// 对象复制
#include "Replication/IConcertClientReplicationManager.h"
#include "Replication/IConcertClientReplicationBridge.h"

// 数据存储
#include "IConcertClientDataStore.h"
#include "ConcertClientLocalDataStore.h"

// 用户存在
#include "IConcertClientPresenceManager.h"
#include "IConcertClientPresenceMode.h"

// Sequencer 同步
#include "IConcertClientSequencerManager.h"
```

### 基本用法：获取模块和创建客户端

```cpp
// 来源: IConcertSyncClientModule.h
// 获取 ConcertSyncClient 模块
IConcertSyncClientModule& ConcertModule = IConcertSyncClientModule::Get();

// 解析命令行客户端设置
UConcertClientConfig* ClientSettings = ConcertModule.ParseClientSettings(FCommandLine::Get());

// 创建一个同步客户端（指定角色，如 "MultiUser"）
TSharedRef<IConcertSyncClient> SyncClient = ConcertModule.CreateClient(TEXT("MultiUser"));

// 启动客户端并连接到会话
SyncClient->Startup(ClientSettings, EConcertSyncSessionFlags::None);
```

### 基本用法：获取各管理器

```cpp
// 来源: IConcertSyncClient.h
// 获取工作区（会话同步后可用）
TSharedPtr<IConcertClientWorkspace> Workspace = SyncClient->GetWorkspace();

// 获取用户存在管理器
IConcertClientPresenceManager* PresenceMgr = SyncClient->GetPresenceManager();

// 获取 Sequencer 管理器
IConcertClientSequencerManager* SequencerMgr = SyncClient->GetSequencerManager();

// 获取复制管理器
IConcertClientReplicationManager* ReplicationMgr = SyncClient->GetReplicationManager();

// 获取各桥接器
IConcertClientTransactionBridge* TxnBridge = SyncClient->GetTransactionBridge();
IConcertClientPackageBridge* PkgBridge = SyncClient->GetPackageBridge();
IConcertClientReplicationBridge* RepBridge = SyncClient->GetReplicationBridge();
```

### 基本用法：工作区操作

```cpp
// 来源: IConcertClientWorkspace.h
IConcertClientWorkspace& Workspace = *SyncClient->GetWorkspace();

// 检查是否有会话变更
bool bHasChanges = Workspace.HasSessionChanges();

// 收集会话中修改的资产列表
TArray<FName> ChangedPackages = Workspace.GatherSessionChanges(/*IgnorePersisted=*/true);

// 锁定资源以防止其他用户修改
TArray<FName> ResourcesToLock = { TEXT("/Game/MyLevel") };
Workspace.LockResources(ResourcesToLock);

// 解锁资源
Workspace.UnlockResources(ResourcesToLock);

// 持久化会话变更并准备源代码控制提交
FPersistParameters Params;
Params.PackagesToPersist = ChangedPackages;
Params.bShouldMakeWritableIfNoSourceControl = true;
FPersistResult Result = Workspace.PersistSessionChanges(Params);
```

### 进阶用法：数据存储（键值共享）

```cpp
// 来源: IConcertClientDataStore.h, ConcertClientLocalDataStore.h
// 跨客户端共享的分布式计数器示例
IConcertClientDataStore& DataStore = Workspace.GetDataStore();

// 初始化一个共享的相机 ID 计数器
FName Key(TEXT("CameraId"));
int64 InitialValue = 0;

DataStore.FetchOrAdd(Key, InitialValue).Next(
    [&Key, &DataStore](const TConcertDataStoreResult<int64>& Result)
    {
        if (Result) // Added 或 Fetched
        {
            int64 CurrentId = Result.GetValue();
            // 使用 CompareExchange 无冲突地递增计数器
            int64 NewId = CurrentId + 1;
            DataStore.CompareExchange(Key, CurrentId, NewId).Next(
                [](const TConcertDataStoreResult<int64>& ExchangeResult)
                {
                    if (ExchangeResult.Code == EConcertDataStoreResultCode::Exchanged)
                    {
                        // 成功获取新 ID
                        int64 AllocatedId = ExchangeResult.GetValue();
                    }
                }
            );
        }
    }
);

// 监听其他客户端对该键的修改
DataStore.RegisterChangeNotificationHandler<int64>(Key,
    [](const FName& InKey, TOptional<int64> Value)
    {
        if (Value.IsSet())
        {
            // 其他客户端更新了 CameraId
        }
    },
    EConcertDataStoreChangeNotificationOptions::NotifyOnInitialValue
);
```

### 进阶用法：自定义对象工厂

```cpp
// 来源: ConcertClientObjectFactory.h
// 扩展 Concert 能够创建/销毁的对象类型
UCLASS()
class UMyCustomObjectFactory : public UConcertClientObjectFactory
{
    GENERATED_BODY()

public:
    virtual bool SupportsClass(const UClass* Class) const override
    {
        return Class == UMySpecialObject::StaticClass();
    }

    virtual bool CreateObject(UObject*& OutObject, UObject* Outer,
        const UClass* Class, const FName Name, const EObjectFlags Flags) const override
    {
        // 自定义对象创建逻辑
        OutObject = NewObject<UMySpecialObject>(Outer, Class, Name, Flags);
        return true;
    }

    virtual bool DestroyObject(UObject* Object) const override
    {
        // 自定义对象销毁逻辑
        return true;
    }

    virtual void InitializeObjects(TArrayView<UObject* const> Objects) const override
    {
        // 对同一事务中的所有对象进行延迟初始化
        // 适用于相互依赖的对象
    }
};
```

### 进阶用法：用户存在管理

```cpp
// 来源: IConcertClientPresenceManager.h
IConcertClientPresenceManager* PresenceMgr = SyncClient->GetPresenceManager();

// 启用/禁用存在显示
PresenceMgr->SetPresenceEnabled(true);

// 按名称设置可见性（持久化到下次连接）
PresenceMgr->SetPresenceVisibility(TEXT("OtherArtist"), true, /*bPropagateToAll=*/true);

// 获取其他用户的变换
FTransform OtherUserTransform = PresenceMgr->GetPresenceTransform(OtherEndpointId);

// 传送到其他用户位置
PresenceMgr->InitiateJumpToPresence(OtherEndpointId);

// 获取其他用户当前打开的世界路径
EEditorPlayMode PlayMode;
FString WorldPath = PresenceMgr->GetPresenceWorldPath(OtherEndpointId, PlayMode);
```

### 进阶用法：事务桥接过滤

```cpp
// 来源: IConcertClientTransactionBridge.h
IConcertClientTransactionBridge* TxnBridge = SyncClient->GetTransactionBridge();

// 启动事务桥接
TxnBridge->StartBridge();

// 注册事务过滤器，排除特定对象的事务同步
TxnBridge->RegisterTransactionFilter(TEXT("MyFilter"),
    FOnFilterTransactionDelegate::CreateLambda(
        [](const FConcertTransactionFilterArgs& Args) -> ETransactionFilterResult
        {
            // 排除临时编辑器对象
            if (Args.ObjectToFilter->IsA<AEditorActor>())
            {
                return ETransactionFilterResult::Exclude;
            }
            return ETransactionFilterResult::UseDefault;
        }
    )
);

// 监听事务快照事件（用于自定义冲突处理）
TxnBridge->OnLocalTransactionSnapshot().AddLambda(
    [](const FConcertClientLocalTransactionCommonData& CommonData,
       const FConcertClientLocalTransactionSnapshotData& SnapshotData)
    {
        // 事务快照已生成
    }
);
```

## Demo 示例

### 完整的多用户客户端管理器

```cpp
// MyMultiUserManager.h
#pragma once

#include "CoreMinimal.h"
#include "IConcertSyncClient.h"

class FMyMultiUserManager
{
public:
    void Initialize();
    void Shutdown();

    /** 尝试连接到 Concert 服务器 */
    bool ConnectToServer(const FString& ServerAddress);

    /** 断开连接 */
    void Disconnect();

    /** 获取当前工作区 */
    TSharedPtr<IConcertClientWorkspace> GetWorkspace() const;

    /** 持久化当前所有会话变更 */
    FPersistResult PersistAllChanges();

    /** 自定义锁策略：锁定正在编辑的资产 */
    void LockEditingAsset(FName PackageName);

    /** 解锁资产 */
    void UnlockAsset(FName PackageName);

private:
    TSharedPtr<IConcertSyncClient> SyncClient;

    void OnWorkspaceStartup(const TSharedPtr<IConcertClientWorkspace>& Workspace);
    void OnWorkspaceShutdown(const TSharedPtr<IConcertClientWorkspace>& Workspace);
};
```

```cpp
// MyMultiUserManager.cpp
#include "MyMultiUserManager.h"
#include "IConcertSyncClientModule.h"
#include "IConcertClientWorkspace.h"
#include "IConcertClientPresenceManager.h"

void FMyMultiUserManager::Initialize()
{
    IConcertSyncClientModule& Module = IConcertSyncClientModule::Get();

    // 创建多用户编辑客户端
    SyncClient = Module.CreateClient(TEXT("MultiUser"));

    // 注册工作区回调
    SyncClient->OnWorkspaceStartup().AddRaw(this, &FMyMultiUserManager::OnWorkspaceStartup);
    SyncClient->OnWorkspaceShutdown().AddRaw(this, &FMyMultiUserManager::OnWorkspaceShutdown);
}

void FMyMultiUserManager::Shutdown()
{
    if (SyncClient.IsValid())
    {
        SyncClient->Shutdown();
        SyncClient.Reset();
    }
}

bool FMyMultiUserManager::ConnectToServer(const FString& ServerAddress)
{
    if (!SyncClient.IsValid())
    {
        return false;
    }

    IConcertSyncClientModule& Module = IConcertSyncClientModule::Get();
    UConcertClientConfig* Settings = Module.ParseClientSettings(FCommandLine::Get());
    // 可根据 ServerAddress 自定义设置
    SyncClient->Startup(Settings, EConcertSyncSessionFlags::None);
    return true;
}

void FMyMultiUserManager::Disconnect()
{
    if (SyncClient.IsValid())
    {
        SyncClient->Shutdown();
    }
}

TSharedPtr<IConcertClientWorkspace> FMyMultiUserManager::GetWorkspace() const
{
    return SyncClient.IsValid() ? SyncClient->GetWorkspace() : nullptr;
}

FPersistResult FMyMultiUserManager::PersistAllChanges()
{
    TSharedPtr<IConcertClientWorkspace> Workspace = GetWorkspace();
    if (!Workspace.IsValid())
    {
        FPersistResult Result;
        Result.PersistStatus = EPersistStatus::NotAllowed;
        Result.FailureReasons.Add(NSLOCTEXT("MyMU", "NoWorkspace", "No active workspace"));
        return Result;
    }

    TArray<FName> Changes = Workspace->GatherSessionChanges(true);
    if (Changes.Num() == 0)
    {
        FPersistResult Result;
        Result.PersistStatus = EPersistStatus::Success;
        return Result;
    }

    FPersistParameters Params;
    Params.PackagesToPersist = Changes;
    Params.bShouldMakeWritableIfNoSourceControl = true;
    return Workspace->PersistSessionChanges(Params);
}

void FMyMultiUserManager::LockEditingAsset(FName PackageName)
{
    TSharedPtr<IConcertClientWorkspace> Workspace = GetWorkspace();
    if (Workspace.IsValid())
    {
        TArray<FName> Packages = { PackageName };
        Workspace->LockResources(Packages);
    }
}

void FMyMultiUserManager::UnlockAsset(FName PackageName)
{
    TSharedPtr<IConcertClientWorkspace> Workspace = GetWorkspace();
    if (Workspace.IsValid())
    {
        TArray<FName> Packages = { PackageName };
        Workspace->UnlockResources(Packages);
    }
}

void FMyMultiUserManager::OnWorkspaceStartup(const TSharedPtr<IConcertClientWorkspace>& Workspace)
{
    UE_LOG(LogTemp, Display, TEXT("Multi-User workspace started"));

    // 启用用户存在显示
    if (IConcertClientPresenceManager* Presence = SyncClient->GetPresenceManager())
    {
        Presence->SetPresenceEnabled(true);
    }
}

void FMyMultiUserManager::OnWorkspaceShutdown(const TSharedPtr<IConcertClientWorkspace>& Workspace)
{
    UE_LOG(LogTemp, Display, TEXT("Multi-User workspace shut down"));
}
```

## 模块依赖

从 .uplugin 的 Plugins 依赖和 Build.cs 分析，以下是该插件的独特依赖：

| 模块 | 用途 |
|---|---|
| `ConcertSyncCore` | Concert 同步核心，提供协议定义、数据序列化和同步基础设施 |
| `ConcertMain` | Concert 主模块，提供会话管理和客户端基础设施 |
| `FileSandbox` | 文件沙盒系统，为每个客户端提供隔离的文件编辑环境 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `2e6f87f2` | Concert: Fix manifest file getting overriden on shutdown. | 修复关闭时清单文件被覆盖的 bug |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移至 UE_LOGF 新格式 |
| 2026-04-02 | `50a24ff6` | Deprecated GetObjects*/ForEachObjectWithOuter functions that take bool bIncludeNestedObjects. Introduced new versions. | 废弃旧的对象遍历 API，引入新版本 |
| 2026-03-23 | `eab5e4c7` | Moving TransactionCommon from Engine to CoreUObject. | 将事务公共类型从 Engine 迁移到 CoreUObject |
| 2026-03-10 | `a69ab07d` | [IsSavingPackage] | 包保存状态相关的改动 |

### 维护评价

ConcertSyncClient 作为 Epic Games 官方维护的 Multi-User Editing 核心客户端组件，**处于活跃维护状态**：

- **创建时间**：2019 年 1 月，已有约 7 年历史
- **更新频率**：近期保持月度更新节奏，2026 年有多次功能性修复和 API 现代化
- **维护质量**：近期更新涵盖了 bug 修复（清单文件覆盖）、API 清理（废弃旧函数引入新版本）、模块重组（TransactionCommon 迁移）等实质性改动
- **实验性标记**：`.uplugin` 中 `IsBetaVersion=true`，且 `EnabledByDefault=false`，属于实验性功能，需要手动启用
- **代码规模**：98 个源文件，架构成熟，采用状态模式（State Pattern）管理复制状态机，设计精良

**推荐使用**：该插件是 UE5 Multi-User Editing 的核心实现，如果你的团队需要多人协作编辑功能，这是必经之路。由于标记为实验性，建议在生产环境使用前充分测试。注意该插件仅在 `UncookedOnly`（非打包）环境下可用，不支持在打包后的游戏中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertSync/ConcertSyncClient)
- [ConcertSyncCore 源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertSync/ConcertSyncCore)
- [ConcertMain 源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertMain)