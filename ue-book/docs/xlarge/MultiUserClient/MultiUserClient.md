# Multi-User Editing

> Allow collaborative multi-users sessions in the Editor（照抄，不翻译）

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

MultiUserClient 是 Unreal Engine 多用户协作编辑系统（Concert）的客户端实现。它解决的核心问题是：**让多个开发者能够同时连接到同一个编辑器会话，实时协作编辑同一个项目**。

该插件基于 Concert 框架构建，提供了以下核心能力：

1. **会话管理**：连接、断开、启动本地服务器，管理多用户编辑会话的生命周期
2. **对象复制系统**：基于 Concert 复制协议，允许客户端注册对象和属性进行跨客户端同步
3. **权限管理**：通过 Authority 机制控制哪个客户端对哪些对象属性拥有编辑权限
4. **离线客户端支持**：当用户断开连接后，保留其复制配置，以便重新加入时恢复
5. **自动发现机制**：通过 `IReplicationDiscoverer` 接口，自动为新添加的对象配置默认复制设置

该插件默认禁用（`EnabledByDefault: false`），且标记为实验性（`IsBetaVersion: true`），需要手动在插件管理器中启用。

## 使用场景

- **多人关卡设计**：多个关卡设计师同时编辑同一个关卡，各自负责不同区域，实时看到彼此的修改
- **美术与设计协作**：美术师调整材质/光照的同时，设计师在调整游戏逻辑，避免文件冲突
- **大型项目团队协作**：团队成员分布在不同机器上，通过 Concert 服务器进行实时协作
- **远程协作**：团队成员不在同一物理位置，通过网络连接到同一 Concert 服务器进行协作编辑
- **自定义复制工作流**：通过 `IReplicationDiscoverer` 为特定 Actor 类型自动配置复制属性（如自动同步位置和旋转）

## 蓝图用法

> 注意：MultiUserClient 模块本身是 Runtime 类型但主要在编辑器中使用。蓝图友好的 API 封装在 `MultiUserClientLibrary` 模块中。以下基于 MultiUserClient 模块的公共 API 分析。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetClient` | 获取 Concert 同步客户端实例 | `IMultiUserClientModule` |
| `GetReplication` | 获取多用户复制系统接口 | `IMultiUserClientModule` |
| `OpenBrowser` | 打开多用户浏览器标签页 | `IMultiUserClientModule` |
| `OpenSettings` | 打开 Concert 设置页面 | `IMultiUserClientModule` |
| `DefaultConnect` | 连接到默认连接配置 | `IMultiUserClientModule` |
| `DisconnectSession` | 断开当前会话（可选确认提示） | `IMultiUserClientModule` |
| `LaunchConcertServer` | 在本地启动 Concert 服务器 | `IMultiUserClientModule` |
| `FindReplicationMapForClient` | 获取指定客户端的对象复制映射 | `IMultiUserReplication` |
| `FindReplicationFrequenciesForClient` | 获取指定客户端的复制频率设置 | `IMultiUserReplication` |
| `IsReplicatingObject` | 检查客户端是否对指定对象拥有复制权限 | `IMultiUserReplication` |
| `EnqueueChanges` | 入队请求更改客户端的复制流和权限 | `IMultiUserReplication` |
| `RegisterReplicationDiscoverer` | 注册复制发现器（自动配置新对象） | `IMultiUserReplication` |
| `ForEachOfflineClient` | 遍历所有离线客户端 | `IMultiUserReplication` |

### 使用示例（蓝图描述）

**连接到多用户会话：**
1. 获取 `IMultiUserClientModule` 单例 → 调用 `DefaultConnect()` 启动连接
2. 或调用 `OpenBrowser()` 打开多用户浏览器 UI 手动选择会话

**查询对象复制状态：**
1. 获取 `IMultiUserReplication` 接口（通过 `GetReplication()`）
2. 调用 `FindReplicationMapForClient(ClientId)` 获取某客户端的复制映射
3. 调用 `IsReplicatingObject(ClientId, ObjectPath)` 检查特定对象

## C++ 用法

### 头文件引入

```cpp
#include "IMultiUserClientModule.h"
#include "Replication/IMultiUserReplication.h"
#include "Replication/IClientChangeOperation.h"
#include "Replication/IReplicationDiscoverer.h"
#include "Replication/IReplicationDiscoveryContext.h"
#include "Replication/ChangeOperationTypes.h"
```

### 基本用法

**获取模块接口并连接会话：**

```cpp
// 来源: IMultiUserClientModule.h
if (IMultiUserClientModule::IsAvailable())
{
    IMultiUserClientModule& MultiUserModule = IMultiUserClientModule::Get();
    
    // 连接到默认会话
    bool bConnected = MultiUserModule.DefaultConnect();
    
    // 或打开浏览器 UI
    MultiUserModule.OpenBrowser();
    
    // 启动本地服务器
    TOptional<FProcHandle> ServerHandle = MultiUserModule.LaunchConcertServer();
}
```

**查询复制状态：**

```cpp
// 来源: IMultiUserReplication.h
IMultiUserClientModule& MultiUserModule = IMultiUserClientModule::Get();
UE::MultiUserClient::IMultiUserReplication* Replication = MultiUserModule.GetReplication();

if (Replication)
{
    FGuid ClientId = /* 某个客户端 ID */;
    
    // 获取客户端的复制映射
    const FConcertObjectReplicationMap* ReplicationMap = Replication->FindReplicationMapForClient(ClientId);
    
    // 检查客户端是否正在复制某个对象
    FSoftObjectPath ObjectPath(TEXT("/Game/Maps/MyLevel.MyLevel:PersistentLevel.MyActor_0"));
    bool bIsReplicating = Replication->IsReplicatingObject(ClientId, ObjectPath);
    
    // 获取复制频率设置
    const FConcertStreamFrequencySettings* FreqSettings = Replication->FindReplicationFrequenciesForClient(ClientId);
}
```

### 进阶用法

**注册自定义复制发现器：**

```cpp
// 来源: IReplicationDiscoverer.h, IReplicationDiscoveryContext.h
// 自定义发现器：为特定 Actor 类型自动配置复制属性
class FMyReplicationDiscoverer : public UE::MultiUserClient::IReplicationDiscoverer
{
public:
    virtual void DiscoverReplicationSettings(
        const UE::MultiUserClient::FReplicationDiscoveryParams& Params) override
    {
        // 检查对象类型
        if (AActor* Actor = Cast<AActor>(&Params.ExtendedObject))
        {
            // 自动添加位置和旋转属性
            FConcertPropertyChain LocationChain;
            LocationChain.AddProperty(GET_MEMBER_NAME_CHECKED(AActor, RootComponent));
            // ... 构建属性链
            
            Params.Context.AddPropertyTo(Params.ExtendedObject, LocationChain);
            
            // 添加额外对象（如子组件）
            if (USceneComponent* RootComp = Actor->GetRootComponent())
            {
                Params.Context.AddAdditionalObject(*RootComp);
            }
        }
    }
};

// 注册发现器
TSharedRef<FMyReplicationDiscoverer> Discoverer = MakeShared<FMyReplicationDiscoverer>();
Replication->RegisterReplicationDiscoverer(Discoverer);

// 使用完毕后移除
Replication->RemoveReplicationDiscoverer(Discoverer);
```

**异步更改客户端复制配置：**

```cpp
// 来源: IClientChangeOperation.h, ChangeOperationTypes.h
FGuid ClientId = /* 目标客户端 ID */;

// 创建更改请求
TAttribute<UE::MultiUserClient::FChangeClientReplicationRequest> RequestAttr;
// ... 配置请求参数

// 入队更改操作
TSharedRef<UE::MultiUserClient::IClientChangeOperation> Operation = 
    Replication->EnqueueChanges(ClientId, RequestAttr);

// 监听流更改完成
Operation->OnChangeStream().Then([](TFuture<UE::MultiUserClient::FChangeClientStreamResponse> Future)
{
    UE::MultiUserClient::FChangeClientStreamResponse Response = Future.Get();
    // 处理结果
});

// 监听权限更改完成
Operation->OnChangeAuthority().Then([](TFuture<UE::MultiUserClient::FChangeClientAuthorityResponse> Future)
{
    UE::MultiUserClient::FChangeClientAuthorityResponse Response = Future.Get();
    // 处理结果
});

// 或等待整个操作完成
Operation->OnOperationCompleted().Then([](TFuture<UE::MultiUserClient::FChangeClientReplicationResult> Future)
{
    UE::MultiUserClient::FChangeClientReplicationResult Result = Future.Get();
    // 所有子操作已完成
});
```

**遍历离线客户端：**

```cpp
// 来源: IMultiUserReplication.h, IOfflineReplicationClient.h
Replication->ForEachOfflineClient([](const UE::MultiUserClient::IOfflineReplicationClient& OfflineClient)
{
    const FConcertClientInfo& ClientInfo = OfflineClient.GetClientInfo();
    const FGuid& LastEndpoint = OfflineClient.GetLastAssociatedEndpoint();
    const FConcertBaseStreamInfo& PredictedStream = OfflineClient.GetPredictedStream();
    
    UE_LOG(LogTemp, Log, TEXT("Offline client: %s, last endpoint: %s"),
        *ClientInfo.DisplayName, *LastEndpoint.ToString());
    
    return EBreakBehavior::Continue; // 继续遍历
});
```

## Demo 示例

```cpp
// MyMultiUserManager.h
#pragma once

#include "CoreMinimal.h"
#include "Replication/IReplicationDiscoverer.h"

class FMyMultiUserManager
{
public:
    void Initialize();
    void Shutdown();
    
    void ConnectToSession();
    void DisconnectFromSession();
    
    void CheckReplicationStatus(const FGuid& ClientId, const FSoftObjectPath& ObjectPath);

private:
    TSharedPtr<UE::MultiUserClient::IReplicationDiscoverer> Discoverer;
};
```

```cpp
// MyMultiUserManager.cpp
#include "MyMultiUserManager.h"
#include "IMultiUserClientModule.h"
#include "Replication/IMultiUserReplication.h"
#include "Replication/IReplicationDiscoveryContext.h"

void FMyMultiUserManager::Initialize()
{
    if (!IMultiUserClientModule::IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("MultiUserClient module not available"));
        return;
    }
    
    // 注册自定义复制发现器
    Discoverer = MakeShared<UE::MultiUserClient::IReplicationDiscoverer>();
    // ... 配置发现器逻辑
    
    IMultiUserClientModule& Module = IMultiUserClientModule::Get();
    if (UE::MultiUserClient::IMultiUserReplication* Replication = Module.GetReplication())
    {
        Replication->RegisterReplicationDiscoverer(Discoverer.ToSharedRef());
    }
}

void FMyMultiUserManager::Shutdown()
{
    if (Discoverer.IsValid() && IMultiUserClientModule::IsAvailable())
    {
        IMultiUserClientModule& Module = IMultiUserClientModule::Get();
        if (UE::MultiUserClient::IMultiUserReplication* Replication = Module.GetReplication())
        {
            Replication->RemoveReplicationDiscoverer(Discoverer.ToSharedRef());
        }
    }
    Discoverer.Reset();
}

void FMyMultiUserManager::ConnectToSession()
{
    IMultiUserClientModule& Module = IMultiUserClientModule::Get();
    
    // 启动本地服务器（如果需要）
    Module.LaunchConcertServer();
    
    // 连接到默认会话
    if (Module.DefaultConnect())
    {
        UE_LOG(LogTemp, Log, TEXT("Connected to multi-user session"));
    }
}

void FMyMultiUserManager::DisconnectFromSession()
{
    IMultiUserClientModule& Module = IMultiUserClientModule::Get();
    Module.DisconnectSession(true); // 始终提示确认
}

void FMyMultiUserManager::CheckReplicationStatus(
    const FGuid& ClientId, const FSoftObjectPath& ObjectPath)
{
    IMultiUserClientModule& Module = IMultiUserClientModule::Get();
    UE::MultiUserClient::IMultiUserReplication* Replication = Module.GetReplication();
    
    if (!Replication)
    {
        return;
    }
    
    // 检查对象是否正在被复制
    bool bReplicating = Replication->IsReplicatingObject(ClientId, ObjectPath);
    UE_LOG(LogTemp, Log, TEXT("Object %s replication status: %s"),
        *ObjectPath.ToString(), bReplicating ? TEXT("Active") : TEXT("Inactive"));
    
    // 获取完整的复制映射
    if (const FConcertObjectReplicationMap* Map = Replication->FindReplicationMapForClient(ClientId))
    {
        UE_LOG(LogTemp, Log, TEXT("Client has %d objects registered for replication"),
            Map->ReplicationMap.Num());
    }
}
```

## 模块依赖

从 Build.cs 分析，该插件依赖 Concert 生态系统的多个模块：

| 模块 | 用途 |
|---|---|
| `ConcertSyncClient` | Concert 同步客户端核心，提供会话连接和数据同步 |
| `ConcertSyncCore` | Concert 同步核心协议和消息定义 |
| `ConcertClient` | Concert 客户端实现 |
| `ConcertTransport` | Concert 传输层 |
| `ConcertShared` | Concert 共享类型和工具 |
| `ConcertMessages` | Concert 消息定义（复制请求/响应等） |
| `MultiUserClientLibrary` | 蓝图友好的 API 封装层 |

## 维护状态

### 近期更新

```
- 42ee03c1add9 Multi User: Fix missing icons in persist menu.
- 726f5b59dc16 If we are auto connecting and the user asked to disconnect allow the disconnect to happen by stopping the auto connect task.
- ce6ff392ddca Addressing instances "ignoring return value of function declared with 'nodiscard' attribute" issue for FTSTicker::RemoveTicker usage.
```

### 维护评价

**综合评价：活跃维护中**

- **创建时间**：2019 年 6 月，已有约 6 年历史
- **实验性状态**：标记为 `IsBetaVersion: true`，仍处于 Beta 阶段
- **默认禁用**：`EnabledByDefault: false`，需要手动启用
- **近期更新**：最近的提交包含 UI 修复、连接逻辑改进和代码质量改进，表明仍在积极维护
- **代码规模**：334 个源文件，属于大型插件，架构复杂
- **Epic 官方维护**：由 Epic Games 开发和维护，作为 UE5 多用户协作的核心功能

**注意事项**：
- 该插件仍标记为 Beta，API 可能在未来版本中发生变化
- 需要 Concert 服务器基础设施支持
- 复制系统依赖于 Concert 协议，与 UE5 的通用复制系统不同

**推荐使用**：✅ 推荐。这是 UE5 官方的多用户协作解决方案，虽然仍在 Beta 阶段，但已经是生产可用的功能，Epic 持续维护和改进。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertApp/MultiUserClient)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/multi-user-editing-in-unreal-engine/)（Concert 多用户编辑文档）