# Multi-User Editing

> Allow collaborative multi-users sessions in the Editor

| 属性 | 值 |
|---|---|
| 中文名 | 多人协作编辑 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MultiUserClient` (Runtime), `MultiUserClientLibrary` (Runtime), `MultiUserReplicationEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-03-28 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertApp/MultiUserClient) | |

## 用途

MultiUserClient 是 Unreal Engine 多人协作编辑系统（Multi-User Editing）的客户端实现插件。它允许**多个编辑器实例连接到同一个 Concert 会话**，实现资产的实时协作编辑和属性级（Property-level）网络复制。

该插件解决的核心问题：
- **多人同时编辑同一项目**：多个开发者可以通过网络连接到同一个会话，协同编辑资产和关卡
- **资产复制（Replication）管理**：允许客户端声明哪些对象和属性由自己负责复制，避免多人同时修改同一属性的冲突
- **远程编辑控制**：支持客户端间的 P2P 复制请求、权限管理（Authority）、静音（Mute）和属性所有权转移
- **会话管理**：创建、归档、恢复、加入和浏览 Concert 会话
- **沙箱持久化**：将会话中修改的文件持久化到磁盘，并集成源代码控制提交流程

该插件是 Epic 内部 Concert 协作架构在编辑器端的完整客户端实现，依赖于 `ConcertSyncClient`、`ConcertSyncCore` 等底层模块。

**注意**：该插件默认未启用（`EnabledByDefault=false`），且标记为 Beta 版本。需要在项目设置中手动启用。

## 使用场景

- 你的团队需要多人同时编辑同一个 UE 项目和关卡 → 启用 MultiUserClient，配合 Concert 服务器使用
- 你需要在网络上实时复制 Actor 的属性变化（如 Transform）给其他编辑器 → 使用复制（Replication）系统
- 你需要管理多个客户端对同一对象属性的复制权限 → 使用 Authority 管理和所有权转移功能
- 你需要将协作编辑的修改持久化到磁盘并通过源代码控制提交 → 使用 Sandbox 持久化功能
- 你想让客户端 A 通过网络请求客户端 B 修改其注册的复制流 → 使用远程提交（Remote Submission）机制
- 你需要为多人复制设置对象的复制频率（如每秒 30 次） → 使用频率设置和预设管理

## 蓝图用法

该插件的核心逻辑主要在 C++ 层运行，没有大量暴露 `BlueprintCallable` 函数。UI 交互通过 Slate 控件实现。但模块接口 `IMultiUserClientModule` 提供了通过 C++ 访问协作系统的入口。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get()` | 获取 MultiUserClient 模块单例 | `IMultiUserClientModule` |
| `IsAvailable()` | 检查模块是否已加载 | `IMultiUserClientModule` |
| `GetClient()` | 获取执行 Multi-User 角色的 Concert 同步客户端 | `IMultiUserClientModule` |
| `GetReplication()` | 获取复制系统接口，用于与复制 API 交互 | `IMultiUserClientModule` |
| `OpenBrowser()` | 打开 Multi-User 浏览器选项卡 | `IMultiUserClientModule` |
| `DefaultConnect()` | 连接到默认 Concert 连接设置 | `IMultiUserClientModule` |
| `DisconnectSession()` | 断开当前会话连接（可选提示用户确认） | `IMultiUserClientModule` |
| `LaunchConcertServer()` | 在本地机器上启动 Concert 服务器 | `IMultiUserClientModule` |
| `ShutdownConcertServer()` | 关闭所有本地运行的 Concert 服务器 | `IMultiUserClientModule` |
| `IsConcertServerRunning()` | 检查 Concert 服务器是否正在运行 | `IMultiUserClientModule` |

### 复制系统核心接口

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FindReplicationMapForClient()` | 获取客户端的服务器端注册对象映射 | `IMultiUserReplication` |
| `IsReplicatingObject()` | 检查客户端是否正在复制指定对象 | `IMultiUserReplication` |
| `EnqueueChanges()` | 排队请求更改客户端的复制流和权限 | `IMultiUserReplication` |
| `ForEachOfflineClient()` | 遍历所有离线客户端 | `IMultiUserReplication` |
| `FindOfflineClient()` | 通过 EndpointId 查找离线客户端 | `IMultiUserReplication` |

## C++ 用法

### 头文件引入

```cpp
// 模块接口
#include "IMultiUserClientModule.h"

// 复制系统公共接口
#include "Replication/IMultiUserReplication.h"
#include "Replication/ChangeOperationTypes.h"
```

### 基本用法 — 连接到 Concert 会话

```cpp
// 来源: Public/IMultiUserClientModule.h
// 获取模块并连接到默认 Concert 会话

#include "IMultiUserClientModule.h"

// 检查模块是否可用
if (IMultiUserClientModule::IsAvailable())
{
    IMultiUserClientModule& MultiUserModule = IMultiUserClientModule::Get();
    
    // 连接到默认连接设置
    bool bConnected = MultiUserModule.DefaultConnect();
    
    // 或手动打开浏览器选择会话
    MultiUserModule.OpenBrowser();
}
```

### 基本用法 — 使用复制 API 查询客户端状态

```cpp
// 来源: Public/Replication/IMultiUserReplication.h
// 查询客户端的复制映射和权限状态

#include "IMultiUserClientModule.h"
#include "Replication/IMultiUserReplication.h"

void QueryClientReplicationState(const FGuid& ClientEndpointId)
{
    if (!IMultiUserClientModule::IsAvailable()) return;
    
    IMultiUserClientModule& Module = IMultiUserClientModule::Get();
    UE::MultiUserClient::IMultiUserReplication* Replication = Module.GetReplication();
    if (!Replication) return;
    
    // 获取客户端的注册对象映射（服务器端状态）
    const FConcertObjectReplicationMap* ReplicationMap = 
        Replication->FindReplicationMapForClient(ClientEndpointId);
    
    // 检查客户端是否正在复制某个对象
    FSoftObjectPath ObjectPath(TEXT("/Game/Maps/MyLevel.MyLevel:PersistentLevel.MyActor"));
    bool bIsReplicating = Replication->IsReplicatingObject(ClientEndpointId, ObjectPath);
    
    // 获取复制频率设置
    const FConcertStreamFrequencySettings* FrequencySettings = 
        Replication->FindReplicationFrequenciesForClient(ClientEndpointId);
}
```

### 基本用法 — 发起复制变更请求

```cpp
// 来源: Public/Replication/IMultiUserReplication.h + Public/Replication/ChangeOperationTypes.h
// 通过 EnqueueChanges 排队请求修改客户端的复制流

#include "IMultiUserClientModule.h"
#include "Replication/IMultiUserReplication.h"
#include "Replication/ChangeOperationTypes.h"

void EnqueueReplicationChange(const FGuid& ClientEndpointId, UObject* TargetObject)
{
    IMultiUserClientModule& Module = IMultiUserClientModule::Get();
    UE::MultiUserClient::IMultiUserReplication* Replication = Module.GetReplication();
    if (!Replication) return;
    
    // 构建变更请求
    UE::MultiUserClient::FChangeClientReplicationRequest Request;
    
    // 流变更：注册对象和属性
    UE::MultiUserClient::FChangeStreamRequest StreamRequest;
    UE::MultiUserClient::FPropertyChange PropChange;
    PropChange.ChangeType = UE::MultiUserClient::EPropertyChangeType::Add;
    PropChange.Properties.Add(FConcertPropertyChain{TEXT("Location")});
    StreamRequest.PropertyChanges.Add(TargetObject, MoveTemp(PropChange));
    
    Request.StreamChangeRequest = MoveTemp(StreamRequest);
    
    // 权限变更：开始复制该对象
    UE::MultiUserClient::FChangeAuthorityRequest AuthRequest;
    AuthRequest.ObjectsToStartReplicating.Add(FSoftObjectPath(TargetObject));
    Request.AuthorityChangeRequest = MoveTemp(AuthRequest);
    
    // 排队执行变更
    TSharedRef<UE::MultiUserClient::IClientChangeOperation> Operation = 
        Replication->EnqueueChanges(ClientEndpointId, 
            TAttribute<UE::MultiUserClient::FChangeClientReplicationRequest>(Request));
    
    // 监听操作结果
    Operation->OnOperationCompleted().Then([](TFuture<UE::MultiUserClient::FChangeClientReplicationResult> Future)
    {
        auto Result = Future.Get();
        if (Result.StreamChangeResult.ErrorCode == UE::MultiUserClient::EChangeStreamOperationResult::Success)
        {
            UE_LOG(LogTemp, Log, TEXT("Stream change succeeded!"));
        }
    });
}
```

### 进阶用法 — 监听复制事件并管理离线客户端

```cpp
// 来源: Public/Replication/IMultiUserReplication.h + Private/Replication/Client/Offline/OfflineClientManager.h
// 监听复制状态变化并查询离线客户端

#include "IMultiUserClientModule.h"
#include "Replication/IMultiUserReplication.h"

class FMyReplicationObserver
{
    FDelegateHandle StreamChangedHandle;
    FDelegateHandle OfflineChangedHandle;
    
    void StartObserving()
    {
        IMultiUserClientModule& Module = IMultiUserClientModule::Get();
        UE::MultiUserClient::IMultiUserReplication* Replication = Module.GetReplication();
        if (!Replication) return;
        
        // 监听流状态变化
        StreamChangedHandle = Replication->OnStreamServerStateChanged()
            .AddLambda([this](const FGuid& EndpointId)
            {
                UE_LOG(LogTemp, Log, TEXT("Client %s stream state changed"), *EndpointId.ToString());
            });
        
        // 监听离线客户端变化
        OfflineChangedHandle = Replication->OnOfflineClientsChanged()
            .AddLambda([Replication]()
            {
                // 遍历所有离线客户端
                Replication->ForEachOfflineClient([](const UE::MultiUserClient::IOfflineReplicationClient& OfflineClient)
                {
                    UE_LOG(LogTemp, Log, TEXT("Offline client found"));
                    return EBreakBehavior::Continue;
                });
            });
    }
    
    void StopObserving()
    {
        IMultiUserClientModule& Module = IMultiUserClientModule::Get();
        if (UE::MultiUserClient::IMultiUserReplication* Replication = Module.GetReplication())
        {
            Replication->OnStreamServerStateChanged().Remove(StreamChangedHandle);
            Replication->OnOfflineClientsChanged().Remove(OfflineChangedHandle);
        }
    }
};
```

### 进阶用法 — 注册复制发现器（Replication Discoverer）

```cpp
// 来源: Public/Replication/IMultiUserReplication.h
// 注册自定义发现器，自动为对象配置复制属性

#include "IMultiUserClientModule.h"
#include "Replication/IMultiUserReplication.h"

// 自定义复制发现器接口实现
class FMyReplicationDiscoverer : public UE::MultiUserClient::IReplicationDiscoverer
{
    // 当用户添加对象时，自动发现相关属性和子对象
    // 具体接口方法取决于 IReplicationDiscoverer 的定义
};

void RegisterDiscoverer()
{
    IMultiUserClientModule& Module = IMultiUserClientModule::Get();
    UE::MultiUserClient::IMultiUserReplication* Replication = Module.GetReplication();
    if (!Replication) return;
    
    TSharedRef<FMyReplicationDiscoverer> Discoverer = MakeShared<FMyReplicationDiscoverer>();
    Replication->RegisterReplicationDiscoverer(Discoverer);
    
    // 之后可以移除
    // Replication->RemoveReplicationDiscoverer(Discoverer);
}
```

## Demo 示例

以下示例展示如何在编辑器工具中使用 MultiUserClient 的公共 API 连接到会话并查询复制状态：

**MyMultiUserTool.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "IMultiUserClientModule.h"
#include "Replication/IMultiUserReplication.h"

class FMyMultiUserTool
{
public:
    /** 初始化并连接到默认 Concert 会话 */
    bool Initialize();
    
    /** 查询指定客户端的复制对象数量 */
    int32 GetReplicatedObjectCount(const FGuid& ClientEndpointId) const;
    
    /** 关闭工具并断开会话 */
    void Shutdown();
    
private:
    /** 获取复制接口的便捷方法 */
    UE::MultiUserClient::IMultiUserReplication* GetReplication() const
    {
        if (!IMultiUserClientModule::IsAvailable()) return nullptr;
        return IMultiUserClientModule::Get().GetReplication();
    }
};
```

**MyMultiUserTool.cpp**
```cpp
#include "MyMultiUserTool.h"

bool FMyMultiUserTool::Initialize()
{
    if (!IMultiUserClientModule::IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("MultiUserClient module is not loaded"));
        return false;
    }
    
    IMultiUserClientModule& Module = IMultiUserClientModule::Get();
    
    // 打开会话浏览器让用户选择会话
    Module.OpenBrowser();
    
    return true;
}

int32 FMyMultiUserTool::GetReplicatedObjectCount(const FGuid& ClientEndpointId) const
{
    UE::MultiUserClient::IMultiUserReplication* Replication = GetReplication();
    if (!Replication) return 0;
    
    const FConcertObjectReplicationMap* Map = 
        Replication->FindReplicationMapForClient(ClientEndpointId);
    
    return Map ? Map->ReplicatedObjects.Num() : 0;
}

void FMyMultiUserTool::Shutdown()
{
    if (IMultiUserClientModule::IsAvailable())
    {
        IMultiUserClientModule::Get().DisconnectSession();
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ConcertSyncClient` | Concert 同步客户端核心，提供会话和工作区管理 |
| `ConcertSyncCore` | Concert 同步核心，提供复制协议和对象层次结构 |
| `ConcertSharedSlate` | 共享 Slate 控件库，用于复制流编辑器 UI |
| `ConcertClientSharedSlate` | 客户端特定的 Slate 控件 |
| `ConcertClientWidgets` | Concert 客户端 UI 控件 |
| `FileSandboxUI` | 文件沙箱 UI，用于资产持久化界面 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `39d8e540` | IsObjectHierarchyReplicated lambda dereferences Object->IsA<AActor>() without a null check. IPropert | 修复对象层次结构复制中的空指针解引用崩溃 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移到新的 UE_LOGF 格式 |
| 2025-12-10 | `c4420deb` | Multi User: Fix crash in -game | 修复在 -game 模式下运行时的崩溃问题 |
| 2025-12-10 | `fec01c4e` | Multi User: Register Multi User with the sandbox system. | 将多人编辑注册到新的沙箱系统中 |
| 2025-11-26 | `025cea32` | Concert: Convert ConcertClient to use new FileSandbox API for package sandbox. | 迁移到新的 FileSandbox API |

### 维护评价

**活跃维护** ✅

- **创建时间**：2022 年 3 月，约 4 年历史，属于较新的 UE5 时代插件
- **最近更新**：最近一次实质性更新在 2026 年 5 月，修复了空指针崩溃问题，说明仍在积极维护
- **更新频率**：过去半年内有多次提交，包括 bug 修复、API 迁移和新功能集成
- **Beta 状态**：标记为 `IsBetaVersion=true`，说明 API 可能仍在演进中
- **代码规模**：282 个源文件，架构设计成熟（使用了 Adapter、Fence、Observer 等设计模式）
- **推荐使用**：适合需要多人协作编辑的团队，但需注意 Beta 状态意味着 API 可能在后续版本中变化。建议通过公共接口（`IMultiUserClientModule` 和 `IMultiUserReplication`）访问功能，避免依赖私有内部类

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertApp/MultiUserClient)
- [官方文档](https://docs.unrealengine.com/en-US/working-with-collaboration-in-unreal-editor/)（Multi-User Editing 总览）