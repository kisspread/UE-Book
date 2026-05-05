# Concert Sync Core

> Shared plugin for Concert Sync client and server plugins

| 属性 | 值 |
|---|---|
| 分类 | Networking |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ConcertSyncCore` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-01-10 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertSync/ConcertSyncCore) | |

## 用途

ConcertSyncCore 是 Unreal Engine 多用户协作编辑系统（Concert / Multi-User Editing）的**核心共享库**。它不直接面向终端用户，而是为 ConcertSync 的客户端插件和服务器插件提供底层基础设施。

该插件解决的核心问题包括：

- **对象复制（Object Replication）**：定义了如何将 UObject 的属性变更序列化、传输、反序列化的完整管线。支持多种复制格式（如 `FFullObjectFormat` 整体序列化），并提供可扩展的 `IObjectReplicationFormat` 接口。
- **复制处理管线（Replication Processing）**：提供 `FObjectReplicationProcessor`、`FObjectReplicationSender`、`FObjectReplicationReceiver` 等处理器，负责对象数据的优先级排序、发送和接收。
- **复制后动作（Replication Actions）**：当属性被复制后，可自动触发 `PostEditChange`、`MarkRenderStateDirty`、`UpdateComponentToWorld` 等操作，确保编辑器状态正确刷新。
- **权限与同步控制（Authority & Sync Control）**：管理哪个客户端对哪些对象拥有编辑权限，处理权限冲突，以及同步控制状态的变更通知。
- **历史编辑（History Edition）**：提供活动依赖图（Activity Dependency Graph）构建能力，支持对协作会话历史进行分析和编辑操作。
- **对象路径工具**：提供 `FSoftObjectPath` 的外层遍历、Actor 路径提取、路径替换等实用工具。

简而言之，这是 Concert 多用户系统的"引擎"——所有数据同步、冲突解决、历史管理的逻辑都在这里。

## 使用场景

- **多用户协作编辑**：多个设计师同时编辑同一个关卡，ConcertSyncCore 负责将每个人的修改实时同步给其他人。
- **Multi-User Server**：`UnrealMultiUserServer` 等独立程序使用此插件作为服务端核心，接收客户端的对象复制数据并转发。
- **Take Recorder 多用户录制**：在多用户会话中录制 Take 时，此插件处理录制过程中的数据同步和冲突。
- **Live Link Hub**：Live Link Hub 程序也依赖此插件进行数据同步。
- **自定义复制格式开发**：如果你需要实现自定义的对象复制策略（而非默认的整体序列化），需要基于 `IObjectReplicationFormat` 接口开发。

> **注意**：此插件默认禁用（`EnabledByDefault: false`），且标记为 Hidden 和 Beta。它仅在特定程序（`UnrealMultiUserServer`、`LiveLinkHub` 等）中加载，普通游戏项目不需要也不应直接依赖此插件。

## 蓝图用法

此插件主要面向 C++ 层，提供的蓝图 API 非常有限。大部分核心类（如 `FObjectReplicationProcessor`、`FObjectReplicationSender`）是纯 C++ 类，不暴露给蓝图。

可蓝图使用的主要是**数据结构**（USTRUCT），用于消息传递和配置：

### 核心数据结构

| 结构体 | 说明 | 用途 |
|---|---|---|
| `FConcertReplication_BatchReplicationEvent` | 批量复制事件，包含多个流的复制数据 | 客户端↔服务器传输 |
| `FConcertReplication_StreamReplicationEvent` | 单个流的复制事件 | 包含流 ID 和对象列表 |
| `FConcertReplication_ObjectReplicationEvent` | 单个对象的复制事件 | 包含对象路径和序列化载荷 |
| `FConcertReplicationActionEntry` | 复制动作条目 | 配置属性复制后触发的动作 |
| `FConcertAuthorityConflict` | 权限冲突描述 | 记录两个对象间的权限冲突 |
| `FConcertQueriedClientInfo` | 客户端查询信息 | 包含流信息和权限信息 |
| `FConcertReplication_ChangeClientEvent` | 客户端变更事件 | 服务器通知客户端其流/权限被外部修改 |

### 复制动作（可配置）

| 动作 | 说明 | 所在类 |
|---|---|---|
| `Post Edit Change` | 调用 `PostEditChange()` 刷新编辑器状态 | `FConcertReplicationAction_PostEditChange` |
| `Mark Render State Dirty` | 对 `USceneComponent` 调用 `MarkRenderStateDirty()` | `FConcertReplicationAction_MarkRenderStateDirty` |
| `Update Component To World` | 对 `USceneComponent` 调用 `UpdateComponentToWorld()` | `FConcertReplicationAction_UpdateComponentToWorld` |

这些动作通过 `TInstancedStruct<FConcertReplicationAction>` 实现多态，可在 `.ini` 配置文件中设置。

## C++ 用法

### 头文件引入

```cpp
#include "Replication/Processing/ObjectReplicationProcessor.h"
#include "Replication/Processing/ObjectReplicationSender.h"
#include "Replication/Processing/ObjectReplicationReceiver.h"
#include "Replication/Formats/FullObjectFormat.h"
#include "Replication/Processing/Actions/ReplicationActionDispatcher.h"
#include "HistoryEdition/DependencyGraphBuilder.h"
#include "Misc/ObjectUtils.h"
#include "Misc/ObjectPathUtils.h"
```

### 基本用法：对象复制发送

创建一个发送器，将本地对象的属性变更发送到指定端点：

```cpp
// 来源: ObjectReplicationSender.h
#include "Replication/Processing/ObjectReplicationSender.h"

// 假设已有 Session 和 DataSource
IConcertSession& Session = ...;
IReplicationDataSource& DataSource = ...;
FGuid TargetEndpointId = ...;

// 创建发送器
FObjectReplicationSender Sender(TargetEndpointId, Session, DataSource);

// 每帧处理待复制的对象
FProcessObjectsParams Params;
Params.DeltaTime = GetWorld()->GetDeltaSeconds();
Sender.ProcessObjects(Params);
```

### 基本用法：对象复制接收

```cpp
// 来源: ObjectReplicationReceiver.h
#include "Replication/Processing/ObjectReplicationReceiver.h"

IConcertSession& Session = ...;
FObjectReplicationCache& Cache = ...;

// 创建接收器 - 自动注册消息处理
FObjectReplicationReceiver Receiver(Session, Cache);

// 可重写 ShouldAcceptObject 过滤不需要的对象
class FMyReceiver : public FObjectReplicationReceiver
{
protected:
    virtual bool ShouldAcceptObject(
        const FConcertSessionContext& SessionContext,
        const FConcertReplication_StreamReplicationEvent& StreamEvent,
        const FConcertReplication_ObjectReplicationEvent& ObjectEvent) const override
    {
        // 只接受特定类型的对象
        return ObjectEvent.ReplicatedObject.ToString().Contains(TEXT("MyActor"));
    }
};
```

### 基本用法：复制动作分发

```cpp
// 来源: ReplicationActionDispatcher.h
#include "Replication/Processing/Actions/ReplicationActionDispatcher.h"
#include "Replication/Data/ReplicationActionEntry.h"

// 配置动作列表
TArray<FConcertReplicationActionEntry> Actions;
// ... 添加动作条目

// 创建分发器
FReplicationActionDispatcher Dispatcher(Actions);

// 在复制过程中，对每个属性调用
// （通常在 IObjectReplicationFormat::ApplyReplicationEvent 内部使用）
Dispatcher.OnReplicateProperty(SomeProperty);

// 所有属性处理完后，执行触发的动作
FReplicationActionArgs Args(ObjectId, ReplicatedObject);
Dispatcher.ExecuteActions(Args);
```

### 进阶用法：历史依赖图构建

```cpp
// 来源: DependencyGraphBuilder.h, HistoryEdition.h
#include "HistoryEdition/DependencyGraphBuilder.h"
#include "HistoryEdition/HistoryEdition.h"

// 从会话数据库构建依赖图
FConcertSyncSessionDatabase& SessionDatabase = ...;
FActivityDependencyGraph DependencyGraph = 
    UE::ConcertSyncCore::BuildDependencyGraphFrom(SessionDatabase);

// 合并删除需求
FHistoryAnalysisResult AnalysisResult = ...;
TSet<FActivityID> Requirements = 
    UE::ConcertSyncCore::CombineRequirements(AnalysisResult);
```

### 进阶用法：对象路径工具

```cpp
// 来源: ObjectUtils.h, ObjectPathUtils.h, ObjectPathOuterIterator.h
#include "Misc/ObjectUtils.h"
#include "Misc/ObjectPathUtils.h"
#include "Misc/ObjectPathOuterIterator.h"

FSoftObjectPath ComponentPath(TEXT("/Game/Maps.Map:PersistentLevel.Cube.StaticMeshComponent0"));

// 获取 Actor 路径
TOptional<FSoftObjectPath> ActorPath = 
    UE::ConcertSyncCore::GetActorOf(ComponentPath);
// 结果: /Game/Maps.Map:PersistentLevel.Cube

// 遍历所有外层对象
for (UE::ConcertSyncCore::FObjectPathOuterIterator It(ComponentPath); It; ++It)
{
    const FSoftObjectPath& OuterPath = *It;
    // 1st: /Game/Maps.Map:PersistentLevel.Cube.StaticMeshComponent0
    // 2nd: /Game/Maps.Map:PersistentLevel.Cube
    // 3rd: /Game/Maps.Map:PersistentLevel
    // 4th: /Game/Maps.Map
}

// 替换路径中的 Actor
FSoftObjectPath OldPath(TEXT("/Game/OldMap.OldMap:PersistentLevel.OldActor.Subobject"));
FSoftObjectPath NewActor(TEXT("/Game/NewMap.NewMap:PersistentLevel.NewActor"));
TOptional<FSoftObjectPath> Result = 
    UE::ConcertSyncCore::ReplaceActorInPath(OldPath, NewActor);
// 结果: /Game/NewMap.NewMap:PersistentLevel.NewActor.Subobject
```

### 进阶用法：属性解析缓存

```cpp
// 来源: PropertyResolutionCache.h
#include "Replication/PropertyResolutionCache.h"

using namespace UE::ConcertSyncCore::PropertyChain;

FPropertyResolutionCache Cache;

// 解析属性链并缓存结果（避免重复遍历属性层级）
FProperty* ResolvedProperty = Cache.ResolveAndCache(Struct, PropertyChain);

// 类结构变更时清除缓存
Cache.Invalidate(Struct);

// 全部清除
Cache.Clear();
```

### 进阶用法：自定义复制格式

```cpp
// 来源: FullObjectFormat.h, IObjectReplicationFormat.h
#include "Replication/Formats/FullObjectFormat.h"

// FFullObjectFormat 是默认的整体序列化格式
// 你可以实现 IObjectReplicationFormat 来创建自定义格式
UE::ConcertSyncCore::FFullObjectFormat Format;

// 创建复制事件（序列化对象）
auto IsPropertyAllowed = [](const FArchiveSerializedPropertyChain* Chain, const FProperty& Property) 
{
    return true; // 允许所有属性
};
TOptional<FConcertSessionSerializedPayload> Payload = 
    Format.CreateReplicationEvent(MyObject, IsPropertyAllowed);

// 应用复制事件（反序列化到对象）
Format.ApplyReplicationEvent(MyObject, *Payload, 
    [](const FProperty& Property) { /* 属性访问回调 */ });

// 合并两个复制事件（较新的覆盖较旧的）
Format.CombineReplicationEvents(OldPayload, NewerPayload);
```

## Demo 示例

以下示例展示如何创建一个自定义的复制动作，在对象属性被复制后自动标记组件为脏：

```cpp
// MyReplicationAction.h
#pragma once

#include "Replication/Processing/Actions/ConcertReplicationAction.h"
#include "MyReplicationAction.generated.h"

/** 自定义复制动作：在属性复制后打印日志并通知组件 */
USTRUCT(DisplayName = "Log And Notify")
struct FMyReplicationAction : public FConcertReplicationAction
{
    GENERATED_BODY()

    virtual void Apply(const UE::ConcertSyncCore::FReplicationActionArgs& InArgs) const override
    {
        UE_LOG(LogTemp, Log, TEXT("Object %s was replicated"), *InArgs.ObjectId.Object.ToString());
        
        // 可以在这里执行任何自定义逻辑
        // 例如：通知其他系统、更新缓存、触发事件等
    }
};
```

```cpp
// MyReplicationManager.h
#pragma once

#include "Replication/Processing/ObjectReplicationProcessor.h"
#include "Replication/Processing/Actions/ReplicationActionDispatcher.h"
#include "Replication/Data/ReplicationActionEntry.h"

class FMyReplicationManager
{
public:
    void Initialize(IConcertSession& Session, IReplicationDataSource& DataSource);
    void Tick(float DeltaTime);

private:
    TUniquePtr<UE::ConcertSyncCore::FObjectReplicationProcessor> Processor;
    TArray<FConcertReplicationActionEntry> ActionEntries;
    TUniquePtr<UE::ConcertSyncCore::FReplicationActionDispatcher> ActionDispatcher;
};
```

```cpp
// MyReplicationManager.cpp
#include "MyReplicationManager.h"
#include "Replication/Processing/ObjectReplicationSender.h"
#include "Replication/Processing/Actions/ConcertReplicationAction_PostEditChange.h"

void FMyReplicationManager::Initialize(IConcertSession& Session, IReplicationDataSource& DataSource)
{
    // 创建发送处理器
    FGuid TargetEndpoint = FGuid::NewGuid();
    Processor = MakeUnique<UE::ConcertSyncCore::FObjectReplicationSender>(
        TargetEndpoint, Session, DataSource);

    // 配置复制动作
    {
        FConcertReplicationActionEntry Entry;
        Entry.Action = TInstancedStruct<FConcertReplicationAction>::Make<FConcertReplicationAction_PostEditChange>();
        ActionEntries.Add(MoveTemp(Entry));
    }

    ActionDispatcher = MakeUnique<UE::ConcertSyncCore::FReplicationActionDispatcher>(ActionEntries);
}

void FMyReplicationManager::Tick(float DeltaTime)
{
    UE::ConcertSyncCore::FProcessObjectsParams Params;
    Params.DeltaTime = DeltaTime;
    Processor->ProcessObjects(Params);
}
```

## 模块依赖

从 `.uplugin` 的 Plugins 依赖和源码 include 分析：

| 模块 | 用途 |
|---|---|
| `ConcertMain` | Concert 框架核心，提供 `IConcertSession`、消息数据结构等 |
| `SQLiteCore` | 会话数据库存储（`FConcertSyncSessionDatabase`） |
| `StructUtils` | `TInstancedStruct` 支持，用于复制动作的多态配置 |

> 依赖 `ConcertMain` 和 `SQLiteCore` 在 Client/Server target 中被排除（`TargetDenyList`），仅在独立程序中可用。

## 维护状态

### 近期更新

```
- 3f2fbbd3cd31 Multiuser: Fix possible crash when stopping a take record or reverting take changes.
- 3686a9b4efbf Composite: Prevent new types from being filtered out in multi-user.
- 5946fd16ec18 Change default value for bIncludeAnnotationObjectChanges to use the updated code path for transaction diffing in Multi-user. This will allow us to deprecate the old path in the future.
- 9803c443cfab Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied using UnrealCodeFixup)
- 638cb70d3801 Restrict plugin dependencies from ConcertSyncCore and an internal plugin to not pull in the SQLiteCore plugin and module on console platforms.
```

近期更新涵盖了崩溃修复（Take Recorder 相关）、类型过滤修复、事务差异代码路径更新、代码质量改进（内联生成宏）以及平台兼容性优化（控制台平台限制 SQLite 依赖）。更新内容表明该插件仍在**积极维护**中。

### 维护评价

- **活跃维护**：作为 Epic Games 多用户协作编辑系统的核心组件，持续有功能性更新和 bug 修复。
- **Beta 状态**：标记为 `IsBetaVersion: true`，API 可能在未来版本中发生变化。
- **程序专用**：仅在特定独立程序中加载（`UnrealMultiUserServer`、`LiveLinkHub` 等），普通游戏项目无需关注。
- **代码规模大**：206 个源文件，涵盖复制、历史编辑、权限管理等多个子系统，是 Concert 生态中最复杂的插件之一。
- **推荐使用**：如果你在开发多用户协作工具或扩展 Concert 系统，这是必经之路。普通项目不需要直接使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertSync/ConcertSyncCore)
- [ConcertSync 客户端插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertSync/ConcertSyncClient)
- [ConcertSync 服务器插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertSync/ConcertSyncServer)
- [ConcertMain 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertMain)