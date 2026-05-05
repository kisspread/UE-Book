# Multi-User Editing

> Allow collaborative multi-users sessions in the Editor

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MultiUserClient` (Runtime), `MultiUserClientLibrary` (Runtime), `MultiUserReplicationEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-06-10 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertApp/MultiUserClient) | |

## 用途

Multi-User Editing 插件基于 Epic 的 Concert 框架，为 Unreal Editor 提供多人协作编辑能力。多个开发者可以同时连接到同一个编辑会话，在各自的编辑器实例中对同一项目进行修改，所有变更通过服务器实时同步。

该插件解决的核心问题是：**多人同时编辑同一个 UE 项目时的冲突协调与资产同步**。它包含三个子模块：

- **MultiUserClient**：核心客户端逻辑，处理与 Concert 服务器的连接、会话管理、资产同步（事务传输、包同步等）
- **MultiUserClientLibrary**：暴露给蓝图的 API 层，提供会话管理子系统、复制（Replication）子系统、自定义事件系统等蓝图友好的接口
- **MultiUserReplicationEditor**：编辑器中用于管理对象属性复制的 UI 和逻辑，处理客户端之间的属性所有权（Authority）分配

该插件默认未启用（`EnabledByDefault=false`），且标记为 Beta 版本，需要在项目设置中手动开启。

## 使用场景

- 你的团队有多名开发者同时在一个 UE 项目上工作 → 用 Multi-User Editing 让所有人实时看到彼此的修改
- 你需要在蓝图中检测多人会话状态、发送自定义事件给其他客户端 → 用 `MultiUserClientLibrary` 模块的蓝图 API
- 你需要精细控制哪些对象的哪些属性由哪个客户端负责复制 → 用 Replication 子系统注册对象和属性的所有权
- 你需要在运行时（PIE）中让多个客户端实例同步游戏状态 → 用 Replication 系统的 Authority 机制

## 蓝图用法

`MultiUserClientLibrary` 模块提供了两个引擎子系统和一组蓝图函数库，是蓝图层面与 Multi-User 系统交互的主要入口。

### 核心子系统

#### UMultiUserSubsystem — 会话管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsConnectedToSession` | 返回当前是否已连接到多人会话 | `UMultiUserSubsystem` |
| `GetLocalClientId` | 获取本地客户端的 Endpoint ID | `UMultiUserSubsystem` |
| `GetRemoteClientIds` | 获取所有远程客户端的 Endpoint ID 列表 | `UMultiUserSubsystem` |
| `K2_SendCustomEvent` | 向会话中发送自定义结构体事件 | `UMultiUserSubsystem` |
| `K2_ExtractEventData` | 从接收到的事件数据中提取结构体 | `UMultiUserSubsystem` |
| `RegisterCustomEventHandler` | 注册指定结构体类型的自定义事件处理器 | `UMultiUserSubsystem` |
| `UnregisterCustomEventHandler` | 注销指定类型的事件处理器 | `UMultiUserSubsystem` |

**委托（Delegate）**：

| 委托 | 触发时机 |
|---|---|
| `OnSessionConnected` | 本地编辑器加入会话时 |
| `OnSessionDisconnected` | 本地编辑器离开会话时 |
| `OnSessionClientChanged` | 会话中客户端信息变化时（如其他客户端加入/离开） |

#### UMultiUserReplicationSubsystem — 复制管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsReplicatingObject` | 查询指定客户端是否正在复制某个对象 | `UMultiUserReplicationSubsystem` |
| `GetRegisteredObjects` | 获取客户端已注册的对象列表（已注册 ≠ 正在复制） | `UMultiUserReplicationSubsystem` |
| `GetReplicatedObjects` | 获取客户端正在复制的对象列表 | `UMultiUserReplicationSubsystem` |
| `GetPropertiesRegisteredToObject` | 获取客户端为某对象注册的属性列表 | `UMultiUserReplicationSubsystem` |
| `GetObjectReplicationFrequency` | 获取对象的复制频率设置 | `UMultiUserReplicationSubsystem` |
| `GetOwningOfflineClients` | 获取某对象的离线拥有者列表（断线后重连时会尝试恢复所有权） | `UMultiUserReplicationSubsystem` |
| `IsOwnedByOfflineClient` | 查询某对象是否被离线客户端拥有 | `UMultiUserReplicationSubsystem` |
| `GetOfflineClients` | 获取所有离线客户端的 Endpoint ID 列表 | `UMultiUserReplicationSubsystem` |

#### UChangeClientAsyncAction — 异步复制变更

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ChangeClient` | 异步修改指定客户端的 Stream（注册的对象/属性）和/或 Authority（所有权） | `UChangeClientAsyncAction` |

### 使用示例（蓝图描述）

**场景 1：检测会话状态并获取客户端信息**

1. 获取 `MultiUserSubsystem` 子系统对象
2. 调用 `IsConnectedToSession` 判断是否在会话中
3. 若已连接，调用 `GetLocalClientId` 获取本地 ID，调用 `GetRemoteClientIds` 获取远程客户端列表
4. 绑定 `OnSessionConnected` / `OnSessionDisconnected` 委托以响应会话状态变化

**场景 2：发送自定义事件**

1. 创建一个自定义 UStruct（如 `FMyCustomEventData`）
2. 获取 `MultiUserSubsystem`，调用 `Send Custom Event` 节点，传入结构体实例
3. 在接收端，先调用 `Register Custom Event Handler` 注册 `FMyCustomEventData` 类型的处理器
4. 在处理器回调中调用 `Extract Event Data` 提取接收到的数据

**场景 3：注册对象复制并请求所有权**

1. 实现 `IMultiUserReplicationRegistration` 接口的蓝图类，在 `DiscoverReplicationSettings` 中调用 `Context.AddPropertiesToObject` 注册对象和属性
2. 使用 `ChangeClient` 异步节点，构造 `FMultiUserChangeClientReplicationRequest`，指定要添加的对象和属性
3. 监听 `OnCompleted` 回调，检查 `FMultiUserChangeClientReplicationResult` 中的 `StreamResult` 和 `AuthorityResult` 枚举值

## C++ 用法

### 头文件引入

```cpp
#include "MultiUserSubsystem.h"
#include "MultiUserReplicationSubsystem.h"
#include "MultiUserClientStatics.h"
#include "Replication/IMultiUserReplicationRegistration.h"
#include "Replication/Async/ChangeClientAsyncAction.h"
```

### 基本用法 — 会话状态查询

```cpp
// 获取 MultiUser 子系统
UMultiUserSubsystem* MultiUserSubsystem = GEngine->GetEngineSubsystem<UMultiUserSubsystem>();
if (!MultiUserSubsystem || !MultiUserSubsystem->IsConnectedToSession())
{
    UE_LOG(LogTemp, Warning, TEXT("未连接到多人会话"));
    return;
}

// 获取本地和远程客户端 ID
FGuid LocalClientId;
MultiUserSubsystem->GetLocalClientId(LocalClientId);

TArray<FGuid> RemoteClientIds;
MultiUserSubsystem->GetRemoteClientIds(RemoteClientIds);

UE_LOG(LogTemp, Log, TEXT("本地客户端: %s, 远程客户端数量: %d"),
    *LocalClientId.ToString(), RemoteClientIds.Num());
```

### 基本用法 — 复制状态查询

```cpp
// 获取复制子系统
UMultiUserReplicationSubsystem* ReplSubsystem = GEngine->GetEngineSubsystem<UMultiUserReplicationSubsystem>();

FGuid ClientId;
GEngine->GetEngineSubsystem<UMultiUserSubsystem>()->GetLocalClientId(ClientId);

FSoftObjectPath ObjectPath(TEXT("/Game/MyAsset.MyAsset"));

// 查询对象是否正在被复制
bool bIsReplicating = ReplSubsystem->IsReplicatingObject(ClientId, ObjectPath);

// 获取已注册的对象列表
TArray<FSoftObjectPath> RegisteredObjects = ReplSubsystem->GetRegisteredObjects(ClientId);

// 获取正在复制的对象列表（已注册但可能尚未开始复制）
TArray<FSoftObjectPath> ReplicatedObjects = ReplSubsystem->GetReplicatedObjects(ClientId);

// 获取为某对象注册的属性
TArray<FConcertPropertyChainWrapper> Properties = ReplSubsystem->GetPropertiesRegisteredToObject(ClientId, ObjectPath);
```

### 进阶用法 — 实现复制注册接口

```cpp
// MyReplicationRegistrar.h
#pragma once

#include "Replication/IMultiUserReplicationRegistration.h"
#include "MyReplicationRegistrar.generated.h"

UCLASS(BlueprintType, Blueprintable)
class UMyReplicationRegistrar : public UObject, public IMultiUserReplicationRegistration
{
    GENERATED_BODY()

public:
    // IMultiUserReplicationRegistration 接口实现
    virtual void DiscoverReplicationSettings_Implementation(
        const FMultiUserReplicationRegistrationParams& Params) override
    {
        IMultiUserReplicationRegistrationContext* Context = 
            Cast<IMultiUserReplicationRegistrationContext>(Params.Context.GetObject());
        if (!Context)
        {
            return;
        }

        // 注册一个额外的对象及其属性
        UObject* MyObject = /* 获取要复制的对象 */;
        if (MyObject)
        {
            TArray<FConcertPropertyChainWrapper> Properties;
            // 构造属性链...
            Context->AddPropertiesToObject(MyObject, Properties);
        }
    }
};
```

### 进阶用法 — 异步修改客户端复制设置

```cpp
// 通过蓝图异步 Action 修改客户端的 Stream 和 Authority
FGuid TargetClientId = /* 目标客户端 ID */;

FMultiUserChangeClientReplicationRequest Request;
// 构造请求：添加对象到 Stream
// Request.StreamChanges.Add(...);
// 构造请求：请求对象的 Authority
// Request.AuthorityChanges.Add(...);

UChangeClientAsyncAction* Action = UChangeClientAsyncAction::ChangeClient(TargetClientId, Request);
Action->OnCompleted.AddDynamic(this, &UMyClass::OnReplicationChangeCompleted);
Action->Activate();
```

## Demo 示例

以下示例展示如何创建一个自定义的复制注册器，注册对象属性并在蓝图中查询复制状态。

```cpp
// MyMultiUserReplicationComponent.h
#pragma once

#include "Components/ActorComponent.h"
#include "Replication/IMultiUserReplicationRegistration.h"
#include "MyMultiUserReplicationComponent.generated.h"

UCLASS(ClassGroup=(MultiUser), meta=(BlueprintSpawnableComponent))
class UMyMultiUserReplicationComponent : public UActorComponent, public IMultiUserReplicationRegistration
{
    GENERATED_BODY()

public:
    UMyMultiUserReplicationComponent();

    //~ IMultiUserReplicationRegistration Interface
    virtual void DiscoverReplicationSettings_Implementation(
        const FMultiUserReplicationRegistrationParams& Params) override;

    /** 查询当前组件所属 Actor 的复制状态 */
    UFUNCTION(BlueprintPure, Category = "Multi-user")
    bool IsOwnerActorReplicating() const;

    /** 获取当前组件所属 Actor 已注册的属性列表 */
    UFUNCTION(BlueprintPure, Category = "Multi-user")
    TArray<FConcertPropertyChainWrapper> GetOwnerActorRegisteredProperties() const;
};
```

```cpp
// MyMultiUserReplicationComponent.cpp
#include "MyMultiUserReplicationComponent.h"
#include "MultiUserSubsystem.h"
#include "MultiUserReplicationSubsystem.h"

UMyMultiUserReplicationComponent::UMyMultiUserReplicationComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UMyMultiUserReplicationComponent::DiscoverReplicationSettings_Implementation(
    const FMultiUserReplicationRegistrationParams& Params)
{
    IMultiUserReplicationRegistrationContext* Context =
        Cast<IMultiUserReplicationRegistrationContext>(Params.Context.GetObject());
    if (!Context || !GetOwner())
    {
        return;
    }

    // 将 Owner Actor 注册为需要复制的对象
    Context->AddAdditionalObject(GetOwner());
}

bool UMyMultiUserReplicationComponent::IsOwnerActorReplicating() const
{
    UMultiUserSubsystem* MuSubsystem = GEngine ? GEngine->GetEngineSubsystem<UMultiUserSubsystem>() : nullptr;
    UMultiUserReplicationSubsystem* ReplSubsystem = GEngine ? GEngine->GetEngineSubsystem<UMultiUserReplicationSubsystem>() : nullptr;
    if (!MuSubsystem || !ReplSubsystem || !GetOwner())
    {
        return false;
    }

    FGuid LocalClientId;
    if (!MuSubsystem->GetLocalClientId(LocalClientId))
    {
        return false;
    }

    FSoftObjectPath ObjectPath(GetOwner());
    return ReplSubsystem->IsReplicatingObject(LocalClientId, ObjectPath);
}

TArray<FConcertPropertyChainWrapper> UMyMultiUserReplicationComponent::GetOwnerActorRegisteredProperties() const
{
    UMultiUserSubsystem* MuSubsystem = GEngine ? GEngine->GetEngineSubsystem<UMultiUserSubsystem>() : nullptr;
    UMultiUserReplicationSubsystem* ReplSubsystem = GEngine ? GEngine->GetEngineSubsystem<UMultiUserReplicationSubsystem>() : nullptr;
    if (!MuSubsystem || !ReplSubsystem || !GetOwner())
    {
        return {};
    }

    FGuid LocalClientId;
    if (!MuSubsystem->GetLocalClientId(LocalClientId))
    {
        return {};
    }

    FSoftObjectPath ObjectPath(GetOwner());
    return ReplSubsystem->GetPropertiesRegisteredToObject(LocalClientId, ObjectPath);
}
```

## 模块依赖

从头文件 include 分析，`MultiUserClientLibrary` 模块依赖以下 Concert 框架模块：

| 模块 | 用途 |
|---|---|
| `ConcertShared` | Concert 基础数据类型（`FConcertClientInfo`、`FConcertSessionClientInfo` 等） |
| `ConcertSyncCore` | Concert 同步核心（复制操作类型、属性链包装等） |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

```
- 4af2fd066dd0 Updating Dev-Release-5.5 from Main at CL #36144969（从 Main 分支同步到 5.5 开发分支）
- c9d4c23f5db0 Expose Blueprint API for querying offline MU replication client info（新增蓝图 API 查询离线客户端复制信息）
- dffd381e7d40 TObjectPtr upgrades for engine plugins.（引擎插件 TObjectPtr 升级重构）
```

### 维护评价

- **创建时间**：2019 年，已有约 6 年历史
- **维护状态**：**活跃维护中**。最近的 commit 包含新功能开发（暴露离线客户端查询的蓝图 API）和代码质量改进（TObjectPtr 升级），表明 Epic 持续投入维护
- **Beta 状态**：插件标记为 `IsBetaVersion=true`，API 可能在未来版本中发生变化
- **默认未启用**：`EnabledByDefault=false`，需要在项目设置中手动启用
- **已知限制**：
  - 仅在编辑器环境下可用（多人编辑是编辑器功能）
  - 复制系统依赖 Concert 服务器，需要先启动 Concert Server
  - Beta 版本，部分 API（如自定义事件的 `CustomThunk` 实现）可能在后续版本中调整
- **推荐程度**：✅ 推荐用于需要多人协作编辑的团队项目。虽然是 Beta，但作为 Epic 官方维护的核心协作工具，稳定性有保障。蓝图 API 覆盖面广，适合在编辑器工具脚本中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertApp/MultiUserClient)
- [MultiUserClientLibrary 源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertApp/MultiUserClient/Source/MultiUserClientLibrary)