# Concert Sync - Test

> Plugin to enables multi-users tests

| 属性 | 值 |
|---|---|
| 分类 | Networking |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ConcertSyncTest` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-01-10 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertSync/ConcertSyncTest) | |

## 用途

ConcertSyncTest 是 UE5 Multi-User Editing (Concert/Multi-User Editing) 系统的自动化测试插件。它不包含任何运行时功能或蓝图节点——纯粹由自动化测试组成，用于验证 Concert 同步系统的核心功能：

- **会话数据库**：活动（Activity）的记录、查询、序列化
- **数据存储**（DataStore）：客户端/服务端键值存储的读写、缓存、Compare-Exchange 语义
- **Replication**：对象属性复制的握手、发送/接收、权限控制、频率限制
- **History Edition**：活动依赖图构建、自上而下/自下而上分析、撤销/重做链
- **Misc**：对象路径层次结构（ObjectPathHierarchy）等工具类

该插件默认禁用且标记为 Hidden，仅在引擎开发/CI 环境中通过 `Automation` 窗口或命令行 `-ExecCmds="Automation RunTests VirtualProduction.Concert"` 运行。

## 使用场景

- 你是引擎开发者，修改了 ConcertSyncCore / ConcertSyncClient / ConcertSyncServer 的代码 → 运行此插件的测试验证无回归
- 你在做 Multi-User Editing 相关的 Bug 修复 → 参考测试用例了解预期行为
- 你在构建自定义同步协议 → 参考测试中的 Mock 和 Base 类了解如何模拟客户端/服务端通信

## 蓝图用法

无。本插件不包含任何 BlueprintCallable 函数或 UPROPERTY。它是纯 C++ 测试模块。

## C++ 用法

### 头文件引入

```cpp
#include "Misc/AutomationTest.h"
#include "Util/ClientServerCommunicationTest.h"
#include "Replication/Util/SendReceiveObjectTestBase.h"
#include "Replication/Util/Spec/ReplicationServer.h"
#include "Replication/Util/Spec/ReplicationClient.h"
```

### 基本用法 — 经典 Automation Test 风格

测试使用 `IMPLEMENT_SIMPLE_AUTOMATION_TEST` 或 `IMPLEMENT_CUSTOM_SIMPLE_AUTOMATION_TEST` 宏注册，测试名以 `VirtualProduction.Concert.` 为前缀。

```cpp
// 来源: Replication/ReplicationHandshakeTests.cpp
namespace UE::ConcertSyncTests::Replication::Handshake
{
    // 使用 FConcertClientServerCommunicationTest 作为基类（提供客户端/服务端通信基础设施）
    IMPLEMENT_CUSTOM_SIMPLE_AUTOMATION_TEST(
        FJoinHandshakeTest,
        FConcertClientServerCommunicationTest,
        "VirtualProduction.Concert.Replication.Handshake",
        EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter
    );

    bool FJoinHandshakeTest::RunTest(const FString& Parameters)
    {
        // 1. 初始化服务端
        InitServer();
        const TSharedPtr<IConcertServerSession>& ServerSession = GetServerSessionMock();
        FReplicationWorkspaceEmptyMock WorkspaceEmptyMock;
        const TSharedRef<IConcertServerReplicationManager> ServerReplicationManager =
            CreateServerReplicationManager(ServerSession.ToSharedRef(), WorkspaceEmptyMock);

        // 2. 连接客户端并创建 Replication Manager
        FClientInfo& Client = ConnectClient();
        const TSharedRef<IConcertClientReplicationBridge> BridgeMock =
            MakeShared<FConcertClientReplicationBridgeMock>();
        const TSharedRef<IConcertClientReplicationManager> ClientReplicationManager =
            CreateClientReplicationManager(Client.ClientSessionMock.ToSharedRef(), BridgeMock.Get());

        // 3. 定义复制流和属性
        const FSoftObjectPath Path(TEXT("/Game/Map.Map:PersistentLevel.StaticMeshActor0.StaticMeshComponent0"));
        const FConcertPropertyChain ForcedLodModel =
            *FConcertPropertyChain::CreateFromPath(*UStaticMeshComponent::StaticClass(), { TEXT("ForcedLodModel") });

        // 4. 执行握手并验证结果
        // ...
    }
}
```

### 基本用法 — Spec (BDD) 风格

较新的测试使用 `BEGIN_DEFINE_SPEC` + `Describe/It/BeforeEach` 的 BDD 风格：

```cpp
// 来源: Misc/ObjectPathHierarchy.spec.cpp
namespace UE::ConcertSyncTests
{
    BEGIN_DEFINE_SPEC(FObjectPathHierarchySpec,
        "VirtualProduction.Concert.Components.ObjectPathHierarchy",
        EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
        ConcertSyncCore::FObjectPathHierarchy Hierarchy;
    END_DEFINE_SPEC(FObjectPathHierarchySpec);

    void FObjectPathHierarchySpec::Define()
    {
        AfterEach([this]() { Hierarchy.Clear(); });

        Describe("Explicit hierarchy", [this]()
        {
            BeforeEach([this]()
            {
                Hierarchy.AddObject(FSoftObjectPath{ TEXT("/Game/Maps.Map") });
                Hierarchy.AddObject(FSoftObjectPath{ TEXT("/Game/Maps.Map:PersistentLevel") });
                Hierarchy.AddObject(FSoftObjectPath{ TEXT("/Game/Maps.Map:PersistentLevel.Cube") });
            });

            It("IsInHierarchy", [this]()
            {
                TestTrue("Is in hierarchy",
                    Hierarchy.IsInHierarchy(FSoftObjectPath{ TEXT("/Game/Maps.Map") }).IsSet());
            });
        });
    }
}
```

### 进阶用法 — Spec 风格 Server/Client 复制测试

使用 `FReplicationServer` 和 `FReplicationClient` 工具类模拟完整的多用户复制场景：

```cpp
// 来源: Replication/PutState/PutStateAndReplicate.spec.cpp（模式参考）
// 使用 FReplicationServer 创建服务器，连接多个客户端

// 1. 创建测试服务器
FReplicationServer Server(TestContext, EConcertSyncSessionFlags::Default_MultiUserSession);

// 2. 连接发送者和接收者客户端
FReplicationClient& Sender = Server.ConnectClient();
FReplicationClient& Receiver = Server.ConnectClient();

// 3. 发送者加入复制会话（注册流和对象）
Sender.JoinReplication(/* FJoinReplicatedSessionArgs */);

// 4. 接收者加入并监听
Receiver.JoinReplicationAsListener({ ObjectsToReceive });

// 5. Tick 模拟消息传递
Server.TickServer();
Sender.TickClient();
Receiver.TickClient();
```

### 进阶用法 — 权限测试

```cpp
// 来源: Replication/ReplicationAuthorityTests.cpp
// 测试: 没有权限的客户端发送的数据会被服务端拒绝

// 1. 初始化客户端/服务端
SetUpClientAndServer();

// 2. 生成复制数据
ConcertSyncCore::FFullObjectFormat SerializeObject;
const TOptional<FConcertSessionSerializedPayload> Payload =
    SerializeObject.CreateReplicationEvent(*TestObject, [](auto* Chain, const FProperty& Prop) { return true; });

// 3. 构造 BatchReplicationEvent
FConcertReplication_BatchReplicationEvent ReplicationBatchEvent;
// ... fill streams and objects

// 4. 发送数据（无权限）→ 预期被拒绝
AddExpectedError(TEXT("Rejected 1 object change"));
Client_Sender->ClientSessionMock->SendCustomEvent(ReplicationBatchEvent, { ServerSessionId },
    EConcertMessageFlags::ReliableOrdered);
TickServer();
```

### 进阶用法 — 会话数据库测试

```cpp
// 来源: Database/ConcertDatabaseTests.cpp
// 测试: 会话数据库的活动记录和查询

FConcertSyncSessionDatabase SessionDatabase;
SessionDatabase.Open(TestSessionPath);

// 设置 Endpoint
FConcertSyncEndpointData EndpointData;
EndpointData.ClientInfo.Initialize();
SessionDatabase.SetEndpoint(EndpointId, EndpointData);

// 添加各种活动
FConcertSyncConnectionActivity ConnectionActivity;
ConnectionActivity.EndpointId = EndpointId;
ConnectionActivity.EventData.ConnectionEventType = EConcertSyncConnectionEventType::Connected;
int64 ActivityId = 0, EventId = 0;
SessionDatabase.AddConnectionActivity(ConnectionActivity, ActivityId, EventId);

FConcertSyncTransactionActivity TransactionActivity;
TransactionActivity.EndpointId = EndpointId;
TransactionActivity.EventData.Transaction.ModifiedPackages.Add(TEXT("/Game/TestAsset"));
SessionDatabase.AddTransactionActivity(TransactionActivity, ActivityId, EventId);
```

### 进阶用法 — 依赖图构建

```cpp
// 来源: HistoryEdition/DependencyGraphBuilderTests.cpp
// 测试: 从活动历史构建依赖图，验证依赖关系正确

FScopedSessionDatabaseWithEndpoint SessionDatabase(*this);
// 模拟一系列用户操作: 创建地图 → 添加 Actor → 重命名 → 编辑 → 删除
const TTestActivityArray<int64> Activities = CreateActivityHistory(SessionDatabase, SessionDatabase.GetEndpoint());

// 构建依赖图
const ConcertSyncCore::FActivityDependencyGraph DependencyGraph =
    ConcertSyncCore::BuildDependencyGraphFrom(SessionDatabase);

// 验证依赖关系
// 2 -> 1 (PackageCreation)
// 3 -> 2 (EditPossiblyDependsOnPackage)
// 5 -> 1 (PackageCreation)
// 7 -> 5 (PackageRename)
ValidateExpectedDependencies(*this, Activities, DependencyGraph);
```

## Demo 示例

本插件不提供可独立使用的运行时功能。以下是最小测试示例，展示如何编写一个 Concert 复制测试：

```cpp
// MyConcertTest.h — 无，纯 cpp 文件即可

// MyConcertTest.cpp
#include "Util/ClientServerCommunicationTest.h"
#include "Replication/IConcertClientReplicationManager.h"
#include "Replication/IConcertServerReplicationManager.h"
#include "Replication/Util/Mocks/ReplicationWorkspaceEmptyMock.h"
#include "Misc/AutomationTest.h"

IMPLEMENT_CUSTOM_SIMPLE_AUTOMATION_TEST(
    FMyConcertTest,
    UE::ConcertSyncTests::Replication::FConcertClientServerCommunicationTest,
    "MyProject.Concert.MyTest",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter
);

bool FMyConcertTest::RunTest(const FString& Parameters)
{
    using namespace UE::ConcertSyncTests::Replication;

    // 初始化服务端
    InitServer();
    FReplicationWorkspaceEmptyMock WorkspaceMock;
    auto ServerReplicationManager = CreateServerReplicationManager(
        GetServerSessionMock().ToSharedRef(), WorkspaceMock);

    // 连接客户端
    auto& Client = ConnectClient();
    auto BridgeMock = MakeShared<FConcertClientReplicationBridgeMock>();
    auto ClientReplicationManager = CreateClientReplicationManager(
        Client.ClientSessionMock.ToSharedRef(), BridgeMock.Get());

    // 你的测试逻辑...
    return true;
}
```

**Build.cs 依赖**（在你的测试模块中）：

```csharp
PrivateDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Concert",
    "ConcertTransport",
    "ConcertSyncCore",
    "ConcertSyncClient",
    "ConcertSyncServer",
    "ConcertSyncTest", // 引用测试基础设施
    "Engine"
});
```

## 模块依赖

从 Build.cs 的 `PublicDependencyModuleNames` 和 `PrivateDependencyModuleNames` 提取：

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心库 |
| `CoreUObject` | UObject 系统 |
| `Concert` | Concert 协议定义、消息类型 |
| `ConcertTransport` | Concert 传输层 |
| `ConcertSyncCore` | 同步核心逻辑（数据库、活动历史、依赖图） |
| `ConcertSyncClient` | 客户端同步逻辑（Replication Manager、DataStore） |
| `ConcertSyncServer` | 服务端同步逻辑（Server Replication Manager、Workspace） |
| `ConcertClientSharedSlate` | 客户端 UI 组件（插件级依赖） |
| `ConcertSharedSlate` | 共享 UI 组件（插件级依赖） |
| `Engine` | 引擎核心（World、Actor 等） |

## 测试分类总览

本插件包含约 93 个源文件（67 个 .cpp + 26 个 .h），测试覆盖以下领域：

### Replication（复制系统）— 主要测试群

| 子目录 | 测试内容 | 文件数 |
|---|---|---|
| `Stream/` | 流注册/查询/变更、频率控制、流权限交互 | 5 |
| `PutState/` | PutState 操作：复制、静音、同步控制、拒绝、活动记录 | 8 |
| `Muting/` | 对象静音：静音复制、静音拒绝、静音+查询、重置静音 | 5 |
| `Restore/` | 内容恢复：有/无/禁用预存内容、静音恢复、活动生产 | 6 |
| `Components/` | 组件级：缓存、频率、同步控制、标签重映射、组合请求 | 9 |
| `ClientManager/` | 客户端管理器事件：PutClientState、RestoreContent、ChangeStream | 3 |
| `Bugs/` | Bug 回归测试：RevertChange、复制中改名 | 2 |
| `UI/` | GenericReplicationStreamModel UI 测试 | 1 |
| 根目录 | Handshake、SendReceive、Authority、Frequency、Property 测试 | 6 |

### Database（数据库）

| 文件 | 测试内容 |
|---|---|
| `ConcertDatabaseTests.cpp` | 会话数据库的 CRUD 操作（连接、锁定、事务活动） |
| `ReplicationActivity.spec.cpp` | 复制活动的记录和查询 |

### HistoryEdition（历史编辑）

| 文件 | 测试内容 |
|---|---|
| `DependencyGraphBuilderTests.cpp` | 从活动序列构建依赖图 |
| `DependencyGraphTests.cpp` | 依赖图数据结构操作 |
| `HistoryTopDownAnalysisTests.cpp` | 自上而下分析 |
| `HistoryBottomUpAnalysisTests.cpp` | 自下而上分析 |
| `RenameEditAndDeleteMapsFlow.cpp` | 地图重命名/编辑/删除的完整流程 |

### DataStore（数据存储）

| 文件 | 测试内容 |
|---|---|
| `ConcertDataStoreTests.cpp` | 客户端/服务端 DataStore 的键值读写、缓存、Compare-Exchange |

### Misc（工具类）

| 文件 | 测试内容 |
|---|---|
| `ObjectPathHierarchy.spec.cpp` | 对象路径层次结构的构建、查询、遍历 |
| `ObjectPathUtils.spec.cpp` | 对象路径工具函数 |

## 测试基础设施

本插件提供了丰富的 Mock 和基类，可复用于其他 Concert 相关测试：

### Mock 对象

| 类 | 用途 |
|---|---|
| `FConcertClientReplicationBridgeMock` | 模拟客户端复制桥 |
| `FReplicationWorkspaceEmptyMock` | 空的复制工作空间 Mock |
| `FReplicationWorkspaceCallInterceptorMock` | 拦截并记录工作空间调用 |
| `ConcertClientWorkspaceBaseMock` | 客户端工作空间 Mock |
| `ConcertClientDataStoreBaseMock` | 客户端 DataStore Mock |

### 测试基类

| 类 | 用途 |
|---|---|
| `FConcertClientServerCommunicationTest` | 客户端/服务端通信基础测试 |
| `FSendReceiveTestBase` | 发送/接收测试基类 |
| `FSendReceiveObjectTestBase` | 对象级发送/接收测试（含 `UTestReflectionObject`） |
| `FSendReceiveWorldTestBase` | World 级发送/接收测试 |
| `FSendReceiveGenericStreamTestBase` | 通用流发送/接收测试 |
| `FChangeStreamsTestBase` | 流变更测试 |
| `FReplicationServer` | Spec 风格的服务器模拟器 |
| `FReplicationClient` | Spec 风格的客户端模拟器 |
| `FObjectTestReplicator` | 对象复制器辅助类 |

### 辅助工具

| 类/文件 | 用途 |
|---|---|
| `ScopedSessionDatabase.h` | 作用域内自动管理会话数据库生命周期 |
| `ScopedSessionDatabaseWithEndpoint.h` | 带 Endpoint 的作用域数据库 |
| `ActivityBuilder.h` | 流式构建测试活动 |
| `ClientEventRecorder.h` | 记录客户端事件用于断言 |
| `UTestReflectionObject` | 带反射属性的测试对象（Float、Vector 等） |

## 维护状态

### 近期更新

1. **2025-06-02** `e320100f` — Moving Concert unit tests from Editor to VirtualProduction test suite
   - 将测试从 `Editor` 分类迁移到 `VirtualProduction` 分类，统一测试组织结构

2. **2025-03-19** `b183b487` — MU Replication: Added UConcertSyncReplicationConfig
   - 新增可配置的复制后动作（如 Transform 属性复制后调用 `UpdateComponentTransform`）

3. **2024-10-31** `c544f3ff` — Attempt to fix failing unit test on Mac
   - 修复 Mac 平台测试失败问题

### 维护评价

- **创建时间**：2019-01-10，约 7 年历史
- **最近更新**：2025-06-02，约 11 个月前有实质性更新（测试迁移）
- **维护状态**：**活跃维护** — 作为 Concert 系统的核心测试套件，随 ConcertSyncClient/Server 同步更新
- **实验性标记**：`IsBetaVersion=true`，`EnabledByDefault=false`，`Hidden=true`
- **推荐使用**：✅ 推荐作为参考和 CI 回归测试使用。不建议直接依赖此插件的内部 API，因为它们是 Epic 内部测试基础设施，可能随版本变化

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertSync/ConcertSyncTest)
- [ConcertSyncClient 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertSync/ConcertSyncClient)
- [ConcertSyncServer 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertSync/ConcertSyncServer)
- [ConcertSyncCore 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertSync/ConcertSyncCore)
