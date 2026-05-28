# Concert Sync - Test

> Plugin to enables multi-users tests（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 多用户测试框架 |
| 分类 | Networking |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ConcertSyncTest` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-01-11 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertSync/ConcertSyncTest) | |

## 用途

这个插件是 UE5 **Concert 多用户编辑系统**的**自动化测试基础设施**，不提供任何面向最终用户的功能。它包含：

- **Mock 对象**：完整模拟了 Concert 的服务器会话、客户端会话、数据存储、工作区、复制桥接器等核心接口，使测试无需启动真实的网络环境
- **测试基类**：提供可复用的测试基类（如 `FConcertClientServerCommunicationTest`、`FSendReceiveTestBase`），封装了"创建服务器 → 连接客户端 → 执行握手"的通用流程
- **复制（Replication）测试工具**：用于验证对象属性从发送端到接收端的同步正确性
- **历史编辑（History Edition）测试工具**：用于验证会话历史中包的创建、保存、重命名、删除等操作的依赖图正确性

插件本身 **默认禁用、隐藏、标记为 Beta**，仅供引擎开发者在 CI 或本地运行 Concert 子系统的单元测试。

## 使用场景

- 你是引擎开发者，需要为 Concert 多用户系统的某个模块编写或运行单元测试 → 依赖此插件的测试基础设施
- 你在开发 Concert 插件的新功能（如复制子系统），需要验证客户端/服务器交互逻辑 → 继承 `FSendReceiveTestBase` 或使用 `FReplicationClient` / `FReplicationServer`
- 你在修改会话历史功能，需要验证活动依赖图 → 使用 `FActivityBuilder` 构造测试场景

## 蓝图用法

此插件**不包含任何蓝图可用的 API**。所有代码均为 C++ 测试基础设施，没有 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性。

## C++ 用法

### 核心测试架构

测试框架分为两层：

1. **通信层**（`ClientServerCommunicationTest`）：模拟 Concert 的客户端-服务器通信
2. **业务层**（`SendReceiveTestBase` 等）：在通信层之上模拟具体的复制、数据存储等业务场景

### 头文件引入

```cpp
#include "Util/ClientServerCommunicationTest.h"           // 基础通信测试
#include "Replication/Util/SendReceiveTestBase.h"          // 复制发送/接收测试
#include "Replication/Util/SendReceiveObjectTestBase.h"    // 对象属性复制测试
#include "Replication/Util/Spec/ReplicationClient.h"       // Spec 风格客户端
#include "Replication/Util/Spec/ReplicationServer.h"       // Spec 风格服务器
```

### 基本用法：客户端-服务器通信测试

`FConcertClientServerCommunicationTest` 是所有 Concert 测试的根基类，提供无网络的客户端-服务器交互模拟。

```cpp
// 来源: Source/ConcertSyncTest/Private/Util/ClientServerCommunicationTest.h

// 定义测试（使用 IMPLEMENT_SIMPLE_AUTOMATION_TEST 或类似宏）
class FMyConcertTest : public UE::ConcertSyncTests::FConcertClientServerCommunicationTest
{
public:
    FMyConcertTest(const FString& InName, const bool bInComplexTask)
        : FConcertClientServerCommunicationTest(InName, bInComplexTask) {}

    virtual bool RunTest(const FString& Parameters) override
    {
        // 1. 初始化服务器
        InitServer();

        // 2. 连接客户端
        FClientInfo& ClientA = ConnectClient(FConcertClientInfo{});
        FClientInfo& ClientB = ConnectClient(FConcertClientInfo{});

        // 3. 通过 ClientSessionMock 进行测试逻辑
        // ClientA.ClientSessionMock 是 IConcertClientSession 的模拟实现

        return true;
    }
};
```

### 进阶用法：对象复制发送/接收测试

`FSendReceiveObjectTestBase` 封装了"创建服务器 → 连接发送端和接收端 → 模拟对象属性同步"的完整流程。

```cpp
// 来源: Source/ConcertSyncTest/Private/Replication/Util/SendReceiveObjectTestBase.h

class FMyReplicationTest : public UE::ConcertSyncTests::Replication::FSendReceiveObjectTestBase
{
public:
    FMyReplicationTest(const FString& InName, const bool bInComplexTask)
        : FSendReceiveObjectTestBase(InName, bInComplexTask) {}

    virtual bool RunTest(const FString& Parameters) override
    {
        // 1. 建立服务器、连接发送端和接收端客户端
        SetUpClientAndServer();

        // 2. 模拟从发送端到接收端的属性同步
        SimulateSendObjectToReceiver();

        // 3. 验证接收端收到了正确的值
        TestEqualTestValues(*TestObject, EPropertyTestFlags::All);

        return true;
    }
};
```

### Spec 风格用法：ReplicationClient / ReplicationServer

对于更精细的控制，可使用 `FReplicationServer` 和 `FReplicationClient` 直接管理服务器和客户端。

```cpp
// 来源: Source/ConcertSyncTest/Private/Replication/Util/Spec/ReplicationServer.h
//        Source/ConcertSyncTest/Private/Replication/Util/Spec/ReplicationClient.h

using namespace UE::ConcertSyncTests::Replication;

// 创建服务器
FReplicationServer Server(*this);

// 连接两个客户端
FReplicationClient& Sender = Server.ConnectClient(FConcertClientInfo{});
FReplicationClient& Receiver = Server.ConnectClient(FConcertClientInfo{});

// 创建对象复制器
FObjectTestReplicator Replicator;
auto SenderArgs = Replicator.CreateSenderArgs();

// 发送端加入复制会话（带 Mock 桥接器）
Sender.JoinReplication(SenderArgs).Get();

// 接收端加入复制会话（作为监听者）
Receiver.JoinReplicationAsListener({ Replicator.TestObject }).Get();

// 设置测试值并模拟传输
Replicator.SetTestValues();
Replicator.SimulateSendObjectToReceiver(*this, 
    { Sender, Server, Receiver, TEXT("MyTest") },
    { Replicator.TestObject->GetStreamId() });

// 验证接收端收到的值
Replicator.TestValuesWereReplicated(*this, EPropertyReplicationFlags::All);
```

## Demo 示例

以下展示如何使用测试基础设施编写一个最小的客户端-服务器通信测试：

```cpp
// MyConcertTest.h
#pragma once

#include "Util/ClientServerCommunicationTest.h"

namespace UE::ConcertSyncTests
{
    /** 验证两个客户端可以通过模拟的服务器会话交换事件 */
    class FClientConnectionTest : public FConcertClientServerCommunicationTest
    {
    public:
        FClientConnectionTest(const FString& InName, const bool bInComplexTask)
            : FConcertClientServerCommunicationTest(InName, bInComplexTask) {}

        virtual FString GetTestSourceFileName() const override { return __FILE__; }
        virtual int32 GetTestSourceFileLine() const override { return __LINE__; }
    };
}
```

```cpp
// MyConcertTest.cpp
#include "MyConcertTest.h"

namespace UE::ConcertSyncTests
{
    // 注册自动化测试
    IMPLEMENT_SIMPLE_AUTOMATION_TEST(
        FClientConnectionTestImpl,
        "Concert.MyTests.ClientConnection",
        EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter
    )

    bool FClientConnectionTestImpl::RunTest(const FString& Parameters)
    {
        // 初始化模拟服务器
        FConcertClientServerCommunicationTest* TestData = new FClientConnectionTest(GetTestName(), true);
        TestData->InitServer();

        // 连接两个客户端
        FClientInfo& ClientA = TestData->ConnectClient(FConcertClientInfo{});
        FClientInfo& ClientB = TestData->ConnectClient(FConcertClientInfo{});

        // 验证客户端会话 mock 已创建
        TestNotNull(TEXT("Client A session"), ClientA.ClientSessionMock.Get());
        TestNotNull(TEXT("Client B session"), ClientB.ClientSessionMock.Get());

        return true;
    }
}
```

## 模块依赖

从 `.uplugin` 的 Plugins 列表及源码推断的依赖：

| 模块 | 用途 |
|---|---|
| `ConcertSyncClient` | 客户端复制管理器、工作区接口、会话接口 |
| `ConcertSyncServer` | 服务器复制管理器、工作区接口 |
| `ConcertSharedSlate` | 共享 Slate UI 组件（通过 .uplugin 声明依赖） |
| `ConcertClientSharedSlate` | 客户端 Slate UI 组件（通过 .uplugin 声明依赖） |

> 无特殊依赖（仅标准 Core/Engine/CoreUObject/Slate 等）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF |
| 2026-02-03 | `20825e79` | Fix duplicate symbol linker errors | 修复重复符号链接错误 |
| 2025-06-02 | `e320100f` | Automation - Moving Concert unit tests from Editor to VirtualProduction test suite | 将 Concert 单元测试从 Editor 测试套件迁移到 VirtualProduction 测试套件 |
| 2025-03-19 | `b183b487` | MU Replication: Added UConcertSyncReplicationConfig which contains configurable actions to execute | 多用户复制：新增可配置的复制动作执行选项 |
| 2024-10-31 | `c544f3ff` | Attempt to fix failing unit test on Mac. | 尝试修复 Mac 平台上失败的单元测试 |

### 维护评价

- **活跃维护**：最近 3 个月内有更新（2026-04、2026-02），均为基础设施维护（日志迁移、编译修复）
- **功能性更新**：2025 年有两次功能性更新（测试套件迁移、复制配置新增），表明 Concert 复制子系统仍在演进
- **Beta 状态**：插件标记为 `IsBetaVersion=true`、`Hidden=true`，说明 API 不稳定
- **测试用途**：作为纯测试插件，不存在面向最终用户的稳定性承诺；其存在依赖于 Concert 主插件的持续开发
- **推荐程度**：仅推荐引擎开发者或深度定制 Concert 的团队使用，普通项目无需关注

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertSync/ConcertSyncTest)
- 官方文档：无
- 测试用例：本插件自身即为测试，测试代码位于 `Source/ConcertSyncTest/Private/` 目录下