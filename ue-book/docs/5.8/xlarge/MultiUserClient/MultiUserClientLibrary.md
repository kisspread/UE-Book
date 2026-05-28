# Multi-User Editing

> Allow collaborative multi-users sessions in the Editor

| 属性 | 值 |
|---|---|
| 中文名 | 多人协同编辑 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MultiUserClient` (UncookedOnly), `MultiUserClientLibrary` (Runtime), `MultiUserReplicationEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-03-28 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertApp/MultiUserClient) | |

## 用途

Multi-User Editing 插件的核心功能是让多个 Unreal Editor 实例能够加入同一个网络会话，实现实时资产同步。其根本目的是解决团队协作中的冲突和效率问题，通过基于属性（Property）的细粒度复制控制，允许多个用户同时编辑不同的资产，或者精确控制同一资产的不同部分，从而避免传统“文件锁”模式的阻塞，实现真正的实时协同编辑。

## 使用场景

*   **团队协作开发**：多名设计师、关卡设计师和程序员可以同时在同一项目中工作，实时看到彼此的更改（例如物体移动、材质调整），极大提升协作效率。
*   **代码审查与测试**：一名程序员可以在一个编辑器中修改代码或蓝图，另一名测试人员可以在另一个连接的编辑器中实时触发和测试这些改动，无需等待完整构建。
*   **实时技术演示与指导**：资深成员可以将自己的编辑器视图同步给团队成员，进行实时操作演示和教学。
*   **大型开放世界构建**：多个关卡设计师可以同时负责相邻的区域，一人创建地形，另一人放置植被和建筑，所有更改在中央服务器合并后同步给所有人。

## 蓝图用法

### 核心节点

**会话与客户端管理 (`UMultiUserSubsystem`)**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsConnectedToSession` | 检查是否已连接到一个多用户会话。 | `UMultiUserSubsystem` |
| `GetLocalClientId` | 获取本地编辑器实例在会话中的客户端ID (FGuid)。 | `UMultiUserSubsystem` |
| `GetRemoteClientIds` | 获取所有远程客户端（其他用户）的ID列表。 | `UMultiUserSubsystem` |
| `Send Custom Event` | 向会话中其他客户端发送自定义结构体事件。 | `UMultiUserSubsystem` |
| `RegisterCustomEventHandler` | 为指定的结构体类型注册自定义事件处理委托。 | `UMultiUserSubsystem` |

**资产复制控制 (`UMultiUserReplicationSubsystem`)**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsReplicatingObject` | 检查指定客户端是否正在复制（同步）某个对象。 | `UMultiUserReplicationSubsystem` |
| `GetReplicatedObjects` | 获取某个客户端当前正在复制的对象列表。 | `UMultiUserReplicationSubsystem` |
| `GetRegisteredObjects` | 获取某个客户端已注册到服务器的对象列表（注册是复制的前置步骤）。 | `UMultiUserReplicationSubsystem` |
| `ChangeClient` (异步) | 异步修改指定客户端的复制流（注册对象及属性）和权限（实际控制哪些对象的复制）。 | `UChangeClientAsyncAction` |

**会话与客户端信息 (`UMultiUserClientStatics`)**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Multi-User Session Info` | 获取当前会话的信息（名称、服务器等）。 | `UMultiUserClientStatics` |
| `Get Multi-User Client Info by Name` | 通过显示名查找客户端信息。 | `UMultiUserClientStatics` |
| `Get Remote Multi-User Client Infos` | 获取所有远程客户端的详细信息列表。 | `UMultiUserClientStatics` |
| `Configure Multi-User Client` | 配置默认服务器URL、会话名称等参数。 | `UMultiUserClientStatics` |
| `Start Multi-User Default Connection` | 使用默认配置发起连接。 | `UMultiUserClientStatics` |

### 使用示例（蓝图描述）

**基本会话连接流程：**
1.  使用 `Configure Multi-User Client` 节点设置 `DefaultServerURL`（例如 “127.0.0.1”）和 `DefaultSessionName`。
2.  调用 `Start Multi-User Default Connection`。
3.  绑定 `OnSessionConnected` 事件，在连接成功后执行后续逻辑（如查询客户端信息）。

**查看并控制另一个用户的复制：**
1.  在连接成功的事件中，调用 `Get Remote Multi-User Client Infos` 获取所有远程客户端。
2.  遍历客户端列表，通过 `Get Replicated Objects` 查看某个远程用户（ID为 `RemoteId`）正在复制哪些对象。
3.  使用 `ChangeClient` 节点，将一个本地创建的 `NewActor` 添加到该远程用户的复制流中。设置 `ClientId` 为 `RemoteId`，`Request.StreamChangeRequest.PropertyChanges` 中填入 `NewActor` 及其要同步的属性。

## C++ 用法

### 头文件引入

```cpp
// 核心子系统
#include "MultiUserSubsystem.h"
#include "Replication/MultiUserReplicationSubsystem.h"

// 用于发起异步复制更改
#include "Replication/Async/ChangeClientAsyncAction.h"
```

### 基本用法

以下示例展示了如何连接到会话并监听客户端变化：

```cpp
// 在某个 UObject (例如 GameInstance) 中
#include "MultiUserSubsystem.h"

void UMyGameInstance::InitMultiUser()
{
    if (UMultiUserSubsystem* MuSubsystem = GEngine->GetEngineSubsystem<UMultiUserSubsystem>())
    {
        // 绑定会话连接事件
        MuSubsystem->OnSessionConnected.AddDynamic(this, &UMyGameInstance::HandleSessionConnected);
        // 配置并连接
        MuSubsystem->ConfigureMultiUserClient(/* config params */);
        MuSubsystem->StartMultiUserDefaultConnection();
    }
}

void UMyGameInstance::HandleSessionConnected()
{
    UMultiUserSubsystem* MuSubsystem = GEngine->GetEngineSubsystem<UMultiUserSubsystem>();
    FGuid LocalId;
    if (MuSubsystem && MuSubsystem->GetLocalClientId(LocalId))
    {
        UE_LOG(LogTemp, Log, TEXT("Multi-User Connected. Local Client ID: %s"), *LocalId.ToString());
    }
}
```

### 进阶用法

以下示例展示了如何通过代码修改远程客户端的复制流：

```cpp
#include "Replication/Async/ChangeClientAsyncAction.h"
#include "Replication/Async/ChangeClientBlueprintParams.h"

void UMyEditorTool::AddObjectToRemoteClient(const FGuid& RemoteClientId, UObject* ObjectToReplicate)
{
    // 构建请求
    FMultiUserChangeClientReplicationRequest Request;
    FMultiUserPropertyChange& PropertyChange = Request.StreamChangeRequest.PropertyChanges.Add(ObjectToReplicate);
    PropertyChange.Properties.Add(/* ... 添加要同步的属性链 ... */);
    PropertyChange.ChangeType = EMultiUserPropertyChangeType::Add;

    // 发起异步操作
    UChangeClientAsyncAction* Action = UChangeClientAsyncAction::ChangeClient(RemoteClientId, Request);
    Action->OnCompleted.AddDynamic(this, &UMyEditorTool::HandleReplicationChangeResult);
    Action->Activate();
}

void UMyEditorTool::HandleReplicationChangeResult(const FMultiUserChangeClientReplicationResult& Result)
{
    if (Result.StreamResponse.ErrorCode == EMultiUserChangeStreamOperationResult::Success)
    {
        UE_LOG(LogTemp, Log, TEXT("Successfully changed remote client's replication stream."));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Failed to change stream. Error: %d"), (int32)Result.StreamResponse.ErrorCode);
    }
}
```

## Demo 示例

```cpp
// MyMultiUserManager.h
#pragma once
#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "MyMultiUserManager.generated.h"

UCLASS()
class UMyMultiUserManager : public UGameInstanceSubsystem
{
    GENERATED_BODY()
public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

private:
    UFUNCTION()
    void OnSessionConnected();

    UFUNCTION()
    void OnSessionClientChanged(const FGuid& EndpointId);

    TWeakObjectPtr<class UMultiUserSubsystem> CachedMuSubsystem;
};

// MyMultiUserManager.cpp
#include "MyMultiUserManager.h"
#include "MultiUserSubsystem.h"
#include "MultiUserClientStatics.h"

void UMyMultiUserManager::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    if (GEngine)
    {
        CachedMuSubsystem = GEngine->GetEngineSubsystem<UMultiUserSubsystem>();
        if (CachedMuSubsystem.IsValid())
        {
            CachedMuSubsystem->OnSessionConnected.AddDynamic(this, &UMyMultiUserManager::OnSessionConnected);
            CachedMuSubsystem->OnSessionClientChanged.AddDynamic(this, &UMyMultiUserManager::OnSessionClientChanged);
        }
    }
}

void UMyMultiUserManager::Deinitialize()
{
    if (CachedMuSubsystem.IsValid())
    {
        CachedMuSubsystem->OnSessionConnected.RemoveDynamic(this, &UMyMultiUserManager::OnSessionConnected);
        CachedMuSubsystem->OnSessionClientChanged.RemoveDynamic(this, &UMyMultiUserManager::OnSessionClientChanged);
    }
    Super::Deinitialize();
}

void UMyMultiUserManager::OnSessionConnected()
{
    FMultiUserSessionInfo SessionInfo = UMultiUserClientStatics::GetMultiUserSessionInfo();
    if (SessionInfo.bValid)
    {
        UE_LOG(LogTemp, Log, TEXT("Connected to Multi-User session: %s on server: %s"), *SessionInfo.SessionName, *SessionInfo.ServerName);
    }
}

void UMyMultiUserManager::OnSessionClientChanged(const FGuid& EndpointId)
{
    FMultiUserClientInfo ClientInfo;
    // 假设 EndpointId 是新加入的客户端
    if (UMultiUserClientStatics::GetMultiUserClientInfoByName(/* 名字 */, ClientInfo))
    {
        UE_LOG(LogTemp, Log, TEXT("Client '%s' joined or left the session."), *ClientInfo.DisplayName);
    }
}
```

## 模块依赖

要使用 MultiUserClientLibrary 模块提供的蓝图和 C++ API，你的模块需要在 `Build.cs` 中添加以下依赖：

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "MultiUserClientLibrary"
});

// 如果你需要直接使用底层 Concert 协议或内部功能，可能还需要：
// "Concert"
// "ConcertClient"
// "ConcertTransport"
```

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `39d8e540` | IsObjectHierarchyReplicated lambda dereferences Object->IsA<AActor>() without a null check. IPropert | 修复对象层级复制检查中的空指针崩溃。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志系统迁移，使用新的日志宏格式。 |
| 2025-12-10 | `c4420deb` | Multi User: Fix crash in -game | 修复以游戏模式(-game)运行时的崩溃问题。 |
| 2025-12-10 | `fec01c4e` | Multi User: Register Multi User with the sandbox system. | 将插件集成到沙盒系统，改善打包和运行时行为。 |
| 2025-11-26 | `025cea32` | Concert: Convert ConcertClient to use new FileSandbox API for package sandbox. | 底层Concert客户端改用新的文件沙盒API。 |

### 维护评价

**活跃维护中**。该插件创建于2022年，属于较新的工具。从Git历史看，近一年内有多次功能性更新和Bug修复（如2025年底的崩溃修复和系统集成），表明它仍被积极维护。插件本身标记为 `IsBetaVersion: true` 且 `EnabledByDefault: false`，说明其功能可能还未完全稳定，或需要用户显式启用。这是一个有特定专业需求（多人协同）但维护良好的高级工具插件，适合有明确协作需求的团队使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertApp/MultiUserClient)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertApp/MultiUserClient/Tests) (位于插件内的Tests目录)