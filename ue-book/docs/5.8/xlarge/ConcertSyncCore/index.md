# Concert Sync Core

> Shared plugin for Concert Sync client and server plugins

| 属性 | 值 |
|---|---|
| 中文名 | 多人同步核心 |
| 分类 | Networking |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ConcertSyncCore` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-01-10 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertSync/ConcertSyncCore) | |

## 用途

ConcertSyncCore 是 Unreal Engine **Multi-User Editing（多人协作编辑）** 系统的核心基础设施层。它不直接提供用户界面或完整的客户端/服务器功能，而是为 ConcertSyncClient 和 ConcertSyncServer 插件提供共享的底层机制。

该插件解决的核心问题包括：

- **会话活动历史管理**：通过 SQLite 持久化所有多人会话中的活动（连接、锁定、事务、资产包、复制），支持会话重放和灾难恢复
- **类型安全的键值数据存储**：为多个协作客户端提供共享状态同步机制（ConcertDataStore）
- **对象属性级复制系统**：支持对 Actor/Component 的特定属性进行网络复制，包含频率控制、同步控制（Sync Control）、静音（Muting）和权限（Authority）管理
- **序列化归档系统**：处理跨编辑器实例的对象序列化，支持对象路径重映射和版本兼容
- **资产包同步**：管理大文件（可达数GB）在协作客户端间的传输

该插件仅在特定程序中启用：UnrealMultiUserServer、LiveLinkHub、CrashReportClientEditor 等，普通游戏客户端和服务器不会加载。

## 使用场景

- 你需要构建多人协作编辑系统 → ConcertSyncClient/Server 依赖本插件的核心活动数据库和同步协议
- 你需要在多个编辑器实例间实时同步 Actor 属性 → 使用 Replication 子系统（FConcertPropertyChain、FObjectReplicationProcessor）
- 你需要实现会话历史记录和回放 → 使用 FConcertSyncSessionDatabase
- 你需要在多个客户端间共享运行时状态 → 使用 FConcertDataStore
- 你需要构建自定义的 Live Link 或灾难恢复系统 → 本插件提供底层基础设施

## 蓝图用法

本插件是纯 C++ 基础设施插件，**没有暴露任何蓝图节点**。所有类均不包含 `UFUNCTION(BlueprintCallable)` 标记。使用者需要通过 C++ API 调用。

## C++ 用法

### 头文件引入

```cpp
#include "ConcertSyncSessionDatabase.h"
#include "ConcertDataStore.h"
#include "ConcertSyncArchives.h"
#include "Replication/Data/ConcertPropertySelection.h"
#include "Replication/Data/ReplicationStream.h"
#include "Replication/Processing/ObjectReplicationCache.h"
```

### 基本用法 — 会话活动数据库

数据库用于持久化多人会话中的所有活动记录，支持创建、查询和枚举。

```cpp
// 引擎参考: Source/ConcertSyncCore/Public/ConcertSyncSessionDatabase.h

// 创建并打开数据库
FConcertSyncSessionDatabase Database;
bool bSuccess = Database.Open(TEXT("/path/to/session/data"));
check(bSuccess);

// 设置端点信息（客户端连接时调用）
FGuid EndpointId = FGuid::NewGuid();
FConcertSyncEndpointData EndpointData;
EndpointData.ClientInfo.ClientName = TEXT("Designer_01");
Database.SetEndpoint(EndpointId, EndpointData);

// 添加连接活动（服务器端使用）
FConcertSyncConnectionActivity ConnectionActivity;
ConnectionActivity.EndpointId = EndpointId;
ConnectionActivity.EventTime = FDateTime::UtcNow();
ConnectionActivity.EventData.ConnectionEventType = EConcertSyncConnectionEventType::Connected;

int64 ActivityId, ConnectionEventId;
Database.AddConnectionActivity(ConnectionActivity, ActivityId, ConnectionEventId);

// 枚举所有活动
Database.EnumerateActivities([](FConcertSyncActivity&& Activity) -> EBreakBehavior
{
    UE_LOG(LogTemp, Log, TEXT("Activity %lld: Type=%d"), Activity.ActivityId, (int32)Activity.EventType);
    return EBreakBehavior::Continue;
});

// 关闭数据库（可选删除数据文件）
Database.Close(false);
```

### 基本用法 — ConcertDataStore（类型安全键值存储）

```cpp
// 引擎参考: Source/ConcertSyncCore/Public/ConcertDataStore.h 和 ConcertDataStoreMessages.h

FConcertDataStore Store;

// 存储一个整数值
FName Key = TEXT("MaxPlayers");
const uint32 DesiredValue = 8;

// 使用 TConcertDataStoreType 自动包装基础类型为 USTRUCT
using WrappedType = TConcertDataStoreType<uint32>::StructType; // FConcertDataStore_Integer
WrappedType WrappedValue = TConcertDataStoreType<uint32>::AsStructType(DesiredValue);

FConcertSessionSerializedPayload SerializedValue;
SerializedValue.SetPayload(WrappedType::StaticStruct(), &WrappedValue);

FConcertDataStoreResult Result = Store.Store(Key, TConcertDataStoreType<uint32>::GetFName(), SerializedValue);
check(Result.Code == EConcertDataStoreResultCode::Added);

// 读取值
FConcertDataStoreResult FetchResult = Store.Fetch(Key, TConcertDataStoreType<uint32>::GetFName());
if (FetchResult.Code == EConcertDataStoreResultCode::Fetched)
{
    uint32 FetchedValue = FetchResult.Value->DeserializeUnchecked<uint32>();
    // FetchedValue == 8
}

// FetchOrAdd：如果不存在则添加，存在则获取
FConcertDataStoreResult FetchOrAddResult = Store.FetchOrAdd(Key, TConcertDataStoreType<uint32>::GetFName(), SerializedValue);
// 返回 Added 或 Fetched，取决于 Key 是否已存在
```

### 基本用法 — 对象属性链（Property Chain）

```cpp
// 引擎参考: Source/ConcertSyncCore/Public/Replication/Data/ConcertPropertySelection.h

// 从路径创建属性链
TArray<FName> PropertyPath = { TEXT("RelativeLocation"), TEXT("X") };
TOptional<FConcertPropertyChain> Chain = FConcertPropertyChain::CreateFromPath(
    ASceneComponent::StaticClass(), PropertyPath);

if (Chain.IsSet())
{
    // 检查是否为根属性
    bool bIsRoot = Chain->IsRootProperty();  // false, 有2个元素
    
    // 解析属性
    FProperty* Prop = Chain->ResolveProperty(ASceneComponent::StaticClass());
    
    // 构建属性选择
    FConcertPropertySelection Selection;
    Selection.ReplicatedProperties.Add(*Chain);
    
    // 添加另一个属性
    TArray<FName> LocationYPath = { TEXT("RelativeLocation"), TEXT("Y") };
    TOptional<FConcertPropertyChain> YChain = FConcertPropertyChain::CreateFromPath(
        ASceneComponent::StaticClass(), LocationYPath);
    if (YChain.IsSet())
    {
        Selection.ReplicatedProperties.Add(*YChain);
    }
    
    // 自动发现并添加隐式父属性
    // 执行后 Selection 包含: ["RelativeLocation", "X"], ["RelativeLocation", "Y"], ["RelativeLocation"]
    Selection.DiscoverAndAddImplicitParentProperties();
}
```

### 进阶用法 — 复制流管理

```cpp
// 引擎参考: Source/ConcertSyncCore/Public/Replication/Data/ReplicationStream.h
//           Source/ConcertSyncCore/Public/Replication/Misc/ReplicationStreamUtils.h

// 创建复制流
FConcertReplicationStream Stream;
Stream.BaseDescription.Identifier = FGuid::NewGuid();

// 注册对象到流中
FSoftObjectPath ActorPath = TEXT("/Game/Maps/MyMap.MyMap:PersistentLevel.MyActor");
FConcertReplicatedObjectInfo ObjectInfo;
ObjectInfo.ClassPath = AMyActor::StaticClass();

// 添加属性选择
TArray<FName> TransformPath = { TEXT("RootComponent"), TEXT("RelativeLocation") };
TOptional<FConcertPropertyChain> TransformChain = FConcertPropertyChain::CreateFromPath(
    AMyActor::StaticClass(), TransformPath);
if (TransformChain.IsSet())
{
    ObjectInfo.ReplicatedProperties.ReplicatedProperties.Add(*TransformChain);
}

Stream.BaseDescription.ReplicationMap.ReplicatedObjects.Add(ActorPath, ObjectInfo);

// 设置频率
Stream.BaseDescription.FrequencySettings.Defaults.ReplicationRate = 30; // 每秒30次

// 查找流中的对象
const FConcertReplicatedObjectInfo* Found = UE::ConcertSyncCore::FindObjectInfo(Stream, ActorPath);
if (Found)
{
    // Found->ClassPath 存储了类路径
}

// 检查对象或子对象是否被引用
bool bReferenced = UE::ConcertSyncCore::IsObjectOrChildReferenced(
    MakeArrayView(&Stream, 1), ActorPath);
```

### 进阶用法 — 同步控制状态管理

```cpp
// 引擎参考: Source/ConcertSyncCore/Public/Replication/SyncControlState.h

using namespace UE::ConcertSyncCore::Replication;

// 初始化同步控制状态
FSyncControlState SyncState;

// 模拟接收同步控制变更事件
FConcertReplication_ChangeSyncControl SyncControlEvent;
SyncControlEvent.NewControlStates.Add(
    FConcertObjectInStreamID{ StreamId, ObjectPath },
    true // 获得控制权
);

// 应用变更，带回调
SyncState.AppendChanges(SyncControlEvent,
    [](const FConcertObjectInStreamID& Object)
    {
        UE_LOG(LogTemp, Log, TEXT("获得同步控制: %s"), *Object.ToString());
    },
    [](const FConcertObjectInStreamID& Object)
    {
        UE_LOG(LogTemp, Log, TEXT("失去同步控制: %s"), *Object.ToString());
    }
);

// 检查对象是否允许复制
bool bAllowed = SyncState.IsObjectAllowed(FConcertObjectInStreamID{ StreamId, ObjectPath });

// 处理流变更（隐式影响同步控制）
FConcertReplication_ChangeStream_Request StreamChange;
StreamChange.StreamsToRemove.Add(StreamId);
SyncState.AppendStreamChange(StreamChange, [](const FConcertObjectInStreamID& Removed)
{
    UE_LOG(LogTemp, Log, TEXT("流移除导致失去控制: %s"), *Removed.ToString());
});
```

### 进阶用法 — 对象路径层级遍历

```cpp
// 引擎参考: Source/ConcertSyncCore/Public/Misc/ObjectPathHierarchy.h

using namespace UE::ConcertSyncCore;

FObjectPathHierarchy Hierarchy;

// 添加对象（自动构建隐式父级）
Hierarchy.AddObject(TEXT("/Game/Maps/MyMap.MyMap:PersistentLevel.MyActor.StaticMeshComponent0"));
// 隐式添加: MyActor, PersistentLevel, MyMap

// 从顶向下遍历
Hierarchy.TraverseTopToBottom([](const FChildRelation& Relation) -> ETreeTraversalBehavior
{
    UE_LOG(LogTemp, Log, TEXT("%s -> %s [%s]"),
        *Relation.Parent.Object.ToString(),
        *Relation.Child.Object.ToString(),
        Relation.Child.Type == EHierarchyObjectType::Explicit ? TEXT("显式") : TEXT("隐式"));
    return ETreeTraversalBehavior::Continue;
});

// 检查对象是否在层级中
TOptional<EHierarchyObjectType> Type = Hierarchy.IsInHierarchy(
    TEXT("/Game/Maps/MyMap.MyMap:PersistentLevel.MyActor"));
// Type == EHierarchyObjectType::Implicit (因为没有直接 AddObject)

// 移除对象
Hierarchy.RemoveObject(TEXT("/Game/Maps/MyMap.MyMap:PersistentLevel.MyActor.StaticMeshComponent0"));
// MyActor 变为 Implicit（如果它没有其他显式子对象则完全移除）
```

## Demo 示例

一个使用 FConcertDataStore 进行类型安全键值存储的最小示例：

```cpp
// ConcertDataStoreDemo.h
#pragma once

#include "CoreMinimal.h"
#include "ConcertDataStore.h"
#include "ConcertDataStoreMessages.h"

class FConcertDataStoreDemo
{
public:
    /** 存储一个字符串值到数据存储 */
    bool StoreStringValue(const FName& Key, const FString& Value);
    
    /** 从数据存储读取一个字符串值 */
    TOptional<FString> FetchStringValue(const FName& Key);
    
    /** 存储一个整数值到数据存储 */
    bool StoreIntValue(const FName& Key, int32 Value);
    
    /** 从数据存储读取一个整数值 */
    TOptional<int32> FetchIntValue(const FName& Key);
    
    /** 枚举所有存储的键值对 */
    void DumpAllEntries() const;

private:
    FConcertDataStore DataStore;
};
```

```cpp
// ConcertDataStoreDemo.cpp
#include "ConcertDataStoreDemo.h"

bool FConcertDataStoreDemo::StoreStringValue(const FName& Key, const FString& Value)
{
    // TConcertDataStoreType<FString> 自动映射到 FConcertDataStore_String USTRUCT
    using WrappedType = TConcertDataStoreType<FString>::StructType;
    WrappedType WrappedValue = TConcertDataStoreType<FString>::AsStructType(Value);

    FConcertSessionSerializedPayload Serialized;
    Serialized.SetPayload(WrappedType::StaticStruct(), &WrappedValue);

    FConcertDataStoreResult Result = DataStore.Store(
        Key, TConcertDataStoreType<FString>::GetFName(), Serialized);

    return Result.Code == EConcertDataStoreResultCode::Added
        || Result.Code == EConcertDataStoreResultCode::Exchanged;
}

TOptional<FString> FConcertDataStoreDemo::FetchStringValue(const FName& Key)
{
    FConcertDataStoreResult Result = DataStore.Fetch(
        Key, TConcertDataStoreType<FString>::GetFName());

    if (Result.Code == EConcertDataStoreResultCode::Fetched)
    {
        return Result.Value->DeserializeUnchecked<FString>();
    }
    return {};
}

bool FConcertDataStoreDemo::StoreIntValue(const FName& Key, int32 Value)
{
    using WrappedType = TConcertDataStoreType<int32>::StructType;
    WrappedType WrappedValue = TConcertDataStoreType<int32>::AsStructType(Value);

    FConcertSessionSerializedPayload Serialized;
    Serialized.SetPayload(WrappedType::StaticStruct(), &WrappedValue);

    FConcertDataStoreResult Result = DataStore.Store(
        Key, TConcertDataStoreType<int32>::GetFName(), Serialized);

    return Result.Code == EConcertDataStoreResultCode::Added
        || Result.Code == EConcertDataStoreResultCode::Exchanged;
}

TOptional<int32> FConcertDataStoreDemo::FetchIntValue(const FName& Key)
{
    FConcertDataStoreResult Result = DataStore.Fetch(
        Key, TConcertDataStoreType<int32>::GetFName());

    if (Result.Code == EConcertDataStoreResultCode::Fetched)
    {
        return Result.Value->DeserializeUnchecked<int32>();
    }
    return {};
}

void FConcertDataStoreDemo::DumpAllEntries() const
{
    DataStore.Visit([](const FName& Key, const FConcertDataStore_StoreValue& Value)
    {
        UE_LOG(LogTemp, Log, TEXT("Key: %s, Type: %s, Version: %u"),
            *Key.ToString(), *Value.TypeName.ToString(), Value.Version);
    });
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/SQLiteCore 等基础设施）。

本插件的 `.uplugin` 声明了以下插件依赖（非模块依赖）：

| 插件 | 用途 |
|---|---|
| `ConcertMain` | Concert 框架基础，提供会话管理、消息路由等核心抽象 |
| `SQLiteCore` | SQLite 数据库引擎封装，用于 FConcertSyncSessionDatabase 的活动持久化 |

使用者的 Build.cs 通常需要依赖：

| 模块 | 用途 |
|---|---|
| `ConcertSyncCore` | 本插件的核心模块，包含所有 API |
| `ConcertMain` | Concert 会话框架接口 |
| `SQLiteCore` | 如果需要直接操作数据库 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移到新的 UE_LOGF 宏 |
| 2026-04-02 | `50a24ff6` | Deprecated GetObjects*/ForEachObjectWithOuter functions that take bool bIncludeNestedObjects. Introd | 废弃旧的带 bIncludeNestedObjects 参数的遍历函数，引入新 API |
| 2026-02-27 | `b70addf2` | [Backout] - CL51269965 | 回退了一次提交 |
| 2026-02-26 | `32a49f74` | Update live edit systems to use `UE::CoreUObject::SerializeItemWithConversion` instead of `FProperty | 更新序列化系统使用新 API 替代旧的 FProperty 序列化 |
| 2025-12-15 | `129825d3` | Concert Replication: Fix removing items from TMap while iterating through it. This fixes several uni | 修复复制系统中迭代 TMap 时删除元素导致的崩溃，修复了多个单元测试 |

### 维护评价

- **活跃维护**：最近 6 个月内有多次实质性更新，包括 API 迁移、bug 修复和新功能引入
- **核心基础设施**：作为 Multi-User Editing 和 Live Link Hub 的底层依赖，Epic Games 持续维护
- **标记为实验性/Beta**：`.uplugin` 中 `IsBetaVersion=true` 且 `EnabledByDefault=false`，说明 API 可能发生变化
- **代码规模大**：127 个源文件，包含复杂的复制、同步控制和活动历史系统
- **依赖特定程序**：仅在 MultiUserServer、LiveLinkHub 等特定编辑器程序中可用
- **推荐使用**：如果你在构建 Multi-User Editing 相关功能或自定义协作工具，这是不可或缺的基础插件。但作为实验性 API，需做好应对 breaking changes 的准备

⚠️ **注意**：该插件标记为实验性（Beta），API 不稳定，可能随引擎版本更新发生 breaking changes。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertSync/ConcertSyncCore)
- 测试用例: 源码目录内未发现独立测试文件，测试可能位于 `Engine/Tests/` 或 `ConcertSyncTest` 模块中