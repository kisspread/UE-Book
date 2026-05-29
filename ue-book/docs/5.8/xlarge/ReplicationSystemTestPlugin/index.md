# Replication System Test Plugin

> Unit and functional tests for the network replication system.

| 属性 | 值 |
|---|---|
| 中文名 | 复制系统测试插件 |
| 分类 | Networking |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ReplicationSystemTestPlugin` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2022-07-13 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ReplicationSystemTestPlugin) | |

## 用途

这是 UE5 新一代网络复制系统（内部代号 **Iris**）的官方单元测试和功能测试插件。它**不是**一个面向终端用户的功能插件，而是 Epic Games 内部用于验证 `ReplicationSystem`（Iris）正确性的测试基础设施。

该插件解决的核心问题：
- 为 Iris 复制系统提供**完整的端到端测试框架**，模拟服务器-客户端（Server-Client）架构
- 提供网络序列化器（NetSerializer）的标准化测试工具，验证量化、序列化、反序列化、Delta 压缩等流程
- 测试复制状态（ReplicationState）描述符构建、属性复制、FastArray 复制、对象引用、RPC 等各种场景
- 提供 Mock 组件（过滤器、NetBlob 处理器、对象工厂、对象优先级器）用于隔离测试

该插件默认禁用（`EnabledByDefault: false`），仅在需要运行 Iris 相关自动化测试时启用。

**注意**：此插件依赖外部测试框架 **Catch2**。

## 使用场景

- 你是 Epic 网络团队的开发者，正在开发或修改 Iris 复制系统 → 启用此插件运行自动化测试
- 你正在为自定义 NetSerializer 编写测试 → 参考 `FTestNetSerializerFixture` 的测试模式
- 你需要模拟 Server-Client 复制流程进行单元测试 → 使用 `FReplicationSystemServerClientTestFixture`
- 你在研究 Iris 复制系统的内部工作原理 → 阅读此插件的测试代码是最好的学习材料

## 蓝图用法

此插件**不包含任何蓝图可用的功能**。它是一个纯 C++ 测试插件，仅在未打包（UncookedOnly）的编辑器环境中运行自动化测试。所有类均为测试专用的 `UCLASS` / `USTRUCT`，不对外暴露 `BlueprintCallable` 接口。

## C++ 用法

此插件的核心价值在于提供**测试框架和测试辅助类**。以下是其主要组成部分的用法说明。

### 头文件引入

```cpp
#include "ReplicationSystemTestPlugin/NetworkAutomationTest.h"
#include "ReplicationSystemTestPlugin/HAL/UserSuppliedArchivePlatformFile.h"
```

### 网络自动化测试宏

插件提供了自定义的断言宏，兼容 Catch2 和 UE 自动化测试框架两种模式：

```cpp
// 来源: Source/Private/NetworkAutomationTestMacros.h

// 断言宏（失败时终止测试）
UE_NET_ASSERT_EQ(V1, V2)      // 等于
UE_NET_ASSERT_NE(V1, V2)      // 不等于
UE_NET_ASSERT_LT(V1, V2)      // 小于
UE_NET_ASSERT_LE(V1, V2)      // 小于等于
UE_NET_ASSERT_GT(V1, V2)      // 大于
UE_NET_ASSERT_GE(V1, V2)      // 大于等于
UE_NET_ASSERT_TRUE(V)          // 为真
UE_NET_ASSERT_FALSE(V)         // 为假

// 期望宏（失败时记录警告但继续执行）
UE_NET_EXPECT_EQ(V1, V2)
UE_NET_EXPECT_NE(V1, V2)
UE_NET_EXPECT_TRUE(V)
UE_NET_EXPECT_FALSE(V)

// 带消息的版本
UE_NET_ASSERT_EQ_MSG(V1, V2, Message)
UE_NET_EXPECT_EQ_MSG(V1, V2, Message)

// 手动失败/警告
UE_NET_FAIL(Message)
UE_NET_WARN(Message)
UE_NET_LOG(Message)
```

### 测试用例定义宏

```cpp
// 来源: Source/Private/NetworkAutomationTest.h

// 定义一个网络自动化测试用例
UE_NET_TEST(TestSuiteName, TestCaseName)
{
    // 测试体
}

// 使用自定义 Fixture 的测试用例
UE_NET_TEST_FIXTURE(FMyTestFixture, TestCaseName)
{
    // 测试体，自动执行 SetUp/TearDown
}
```

### 基本用法：编写网络自动化测试

```cpp
// 来源: Source/Private/Tests/Serialization/TestNetSerializerFixture.h

#include "NetworkAutomationTest.h"
#include "NetworkAutomationTestMacros.h"

// 使用 FTestNetSerializerFixture 测试自定义 NetSerializer
UE_NET_TEST(FMyNetSerializerTest, QuantizeAndSerialize)
{
    // TTestNetSerializerFixture 模板化测试工具
    // ConfigPrinter: 配置打印函数指针
    // SourceType: 源数据类型
    TTestNetSerializerFixture<PrintMyConfig, FMyValueType> Fixture(FMyNetSerializerSerializer);
    
    FMyNetSerializerConfig Config;
    FMyValueType TestValues[] = { 0, 42, 100 };
    
    // 测试量化
    Fixture.TestQuantize(TestValues, 3, Config);
    
    // 测试序列化（源值与期望值比较）
    FMyValueType ExpectedValues[] = { 0, 42, 100 };
    Fixture.TestSerialize(TestValues, ExpectedValues, 3, Config, /*bQuantizedCompare=*/true);
    
    // 测试 Delta 序列化
    Fixture.TestSerializeDelta(TestValues, 3, Config);
    
    // 测试相等性判断
    bool ExpectedResults[] = { true, false, true };
    Fixture.TestIsEqual(TestValues, TestValues, ExpectedResults, 3, Config, /*bQuantizedCompare=*/false);
}
```

### 进阶用法：Server-Client 端到端测试

```cpp
// 来源: Source/Private/Tests/ReplicationSystem/ReplicationSystemServerClientTestFixture.h

#include "ReplicationSystemServerClientTestFixture.h"

// 继承 FReplicationSystemServerClientTestFixture 获得完整的 Server-Client 测试环境
class FMyReplicationTest : public UE::Net::FReplicationSystemServerClientTestFixture
{
    // 自动创建 Server 和 Client 节点
    // SetUp 中初始化 ReplicationSystem、NetTokenStore、DataStream 等
};

UE_NET_TEST_FIXTURE(FMyReplicationTest, BasicReplication)
{
    // 在 Server 上创建复制对象
    UTestReplicatedIrisObject* ServerObject = Server->CreateObject();
    ServerObject->SetIntA(123);
    
    // Server 发送更新到 Client
    Server->SendAndDeliverTo(Client);
    
    // 在 Client 上获取复制后的对象
    UTestReplicatedIrisObject* ClientObject = Client->GetObjectAs<UTestReplicatedIrisObject>(...);
    
    // 验证复制结果
    UE_NET_ASSERT_EQ(ClientObject->GetIntA(), 123);
}
```

### 测试 Fixture 继承层次

```cpp
// 核心继承关系（来源: 多个 TestFixture 头文件）

// 最基础的测试 Fixture
FNetworkAutomationTestSuiteFixture
├── FReplicationSystemTestFixture          // 单节点复制系统测试
├── FReplicationSystemServerClientTestFixture  // Server-Client 配对测试
│   ├── FNetBlobTestFixture               // NetBlob 传输测试
│   └── FTestNetObjectPrioritizerFixture  // 对象优先级测试
├── FMultiReplicationSystemsTestFixture   // 多 Server 场景测试
├── FReplicationSystemProxyTestFixture    // 代理服务器（Proxy）测试
└── FTestNetSerializerFixture             // NetSerializer 序列化测试
    └── TTestNetSerializerFixture<>       // 类型安全的模板化版本
```

## Demo 示例

由于此插件是测试基础设施而非功能插件，以下示例展示如何使用其测试框架编写自定义网络测试：

```cpp
// MyReplicationTest.h
#pragma once
#include "NetworkAutomationTest.h"
#include "ReplicationSystemServerClientTestFixture.h"

// 自定义测试 Fixture，可添加额外的 SetUp/TearDown 逻辑
class FMyCustomNetworkTest : public UE::Net::FReplicationSystemServerClientTestFixture
{
    typedef UE::Net::FReplicationSystemServerClientTestFixture Super;

protected:
    virtual void SetUp() override
    {
        Super::SetUp();  // 自动初始化 Server + Client
        // 你的额外初始化逻辑
    }
    
    virtual void TearDown() override
    {
        // 你的额外清理逻辑
        Super::TearDown();
    }
};
```

```cpp
// MyReplicationTest.cpp
#include "MyReplicationTest.h"
#include "Tests/ReplicationSystem/ReplicatedTestObject.h"

// 测试 1: 基本属性复制
UE_NET_TEST_FIXTURE(FMyCustomNetworkTest, PropertyReplication)
{
    // 在 Server 创建对象并设置属性
    UTestReplicatedIrisObject* ServerObj = Server->CreateObject();
    ServerObj->SetIntA(42);
    ServerObj->SetIntB(99);
    
    // 发送并投递给 Client
    Server->SendAndDeliverTo(Client, /*bDeliver=*/true, TEXT("InitialSync"));
    
    // Client 接收更新
    // 通过 NetRefHandle 获取 Client 侧的对应对象
    // 验证属性值已正确复制
}

// 测试 2: RPC 测试
UE_NET_TEST_FIXTURE(FMyCustomNetworkTest, ClientRPC)
{
    UTestReplicatedObjectWithRPC* ServerObj = Server->CreateObject<UTestReplicatedObjectWithRPC>();
    ServerObj->Init(Server->GetReplicationSystem());
    ServerObj->bIsServerObject = true;
    
    // Server 发起 Client RPC
    ServerObj->ClientRPC();
    
    // 发送数据到 Client
    Server->SendAndDeliverTo(Client);
    
    // 验证 Client 侧 RPC 被调用
}

// 测试 3: 多 Server 场景
class FMultiServerTest : public UE::Net::FMultiReplicationSystemsTestFixture
{
};

UE_NET_TEST_FIXTURE(FMultiServerTest, MultiServerReplication)
{
    CreateSomeServers();  // 创建默认数量的 Server（3 个）
    
    auto AllServers = GetAllServers();
    for (auto* Srv : AllServers)
    {
        CreateClientForServer(Srv);
    }
    
    auto* Obj = CreateObject({});
    BeginReplication(Obj);
    FullSendAndDeliverUpdate();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Catch2` | C++ 测试框架，用于低级别单元测试 |
| `IrisCore` | Iris 复制系统核心（隐式依赖，测试对象使用 Iris API） |
| `NetCore` | 网络核心模块（FNetRefHandle、FNetToken 等） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `94eef76b` | Iris | Iris 复制系统相关更新 |
| 2026-05-13 | `5d469e0b` | Iris | Iris 复制系统相关更新 |
| 2026-05-12 | `07f19496` | Iris | Iris 复制系统相关更新 |
| 2026-05-12 | `8073c4ae` | Iris | Iris 复制系统相关更新 |
| 2026-05-12 | `dfd3b48c` | Iris | Iris 复制系统相关更新 |

### 维护评价

- **创建时间**：2022 年 7 月，随 Iris 复制系统一起提交
- **活跃度**：**高度活跃** — 最近的提交集中在 2026 年 5 月，且持续有更新
- **维护模式**：commit message 均为简短的 "Iris"，表明这是 Iris 系统持续开发的一部分。每次 Iris 核心功能变更都会同步更新此测试插件
- **功能覆盖**：测试覆盖范围非常全面，包括序列化器、复制状态描述符、Server-Client 端到端、FastArray、对象引用、RPC、过滤器、优先级、NetBlob、代理服务器等
- **推荐**：**仅推荐给 Iris/ReplicationSystem 开发者**。普通游戏开发者不需要也不应该启用此插件。如果你在研究 Iris 系统的工作原理，此插件的测试代码是极佳的学习资料

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ReplicationSystemTestPlugin)
- 官方文档：无（内部测试插件，无公开文档）