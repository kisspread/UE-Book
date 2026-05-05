# Experimental Code Quality Unreal Test Plugin

> Simplified testing of experimental features for Unreal Engine

| 属性 | 值 |
|---|---|
| 分类 | Testing |
| 默认启用 | ❌ No（Installed: false, IsExperimentalVersion: true） |
| 包含内容 | false |
| 模块 | CQTestExperimentalTests (Runtime) |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕 (≤5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Tests/CQTestExperimental) | |

## 用途

CQTestExperimental 是 CQTest 框架的扩展插件，专门用于测试 UE5 的**实验性 Iris 网络复制系统**。

在 UE5 的网络架构演进中，Epic 引入了 Iris Replication System 作为下一代网络复制方案，取代传统的 `DOREPLIFETIME` 宏驱动的复制机制。CQTestExperimental 提供了使用 CQTest 框架测试 Iris 复制系统的样板代码和测试用例，帮助开发者验证自己的网络功能在 Iris 系统下的行为是否正确。

**为什么存在：** CQTest 核心插件提供了 `FPIENetworkComponent` 来测试传统的 PIE 网络复制场景，但 Iris 是一个全新的复制系统，需要通过设置 `net.Iris.UseIrisReplication=1` 控制台变量来启用。CQTestExperimental 展示了如何在 CQTest 框架内正确配置和测试 Iris 复制。

## 使用场景

- 你正在使用 Iris 复制系统开发多人游戏功能，需要自动化测试网络同步行为
- 你需要验证 Actor 属性在 Iris 复制系统下是否能正确同步到客户端
- 你需要测试"迟到加入"（Late Join）场景下 Iris 复制系统的状态同步
- 你需要验证自定义 GameInstance / GameMode 在 Iris 网络会话中的行为

## 蓝图用法

本插件是纯测试框架插件，不包含任何 BlueprintCallable 节点或蓝图可用资产。

## C++ 用法

本插件的源码本身是测试用例，展示了如何使用 CQTest 的 `FPIENetworkComponent` 配合 Iris 复制系统编写测试。以下是基于源码的用法指南。

### 前置条件

1. 启用 `CQTest` 插件（核心测试框架）
2. 启用 `CQTestExperimental` 插件
3. 项目模块需要依赖 `CQTest` 模块

### 头文件引入

```cpp
#include "CQTest.h"
#include "Components/PIENetworkComponent.h"

// 启用条件编译守卫
#if ENABLE_PIE_NETWORK_TEST && UE_WITH_IRIS
// ... 测试代码
#endif
```

### 基本用法：设置 Iris 网络测试环境

Iris 测试的关键区别在于需要在 `BEFORE_ALL` 中通过 `FScopedTestEnvironment` 启用 Iris 复制：

```cpp
// 来源: PIENetworkComponentTests.cpp (IrisStateTest)
NETWORK_TEST_CLASS(MyIrisTest, "TestFramework.CQTest.Experimental.Network")
{
    FPIENetworkComponent<FBasePIENetworkComponentState> Network{
        TestRunner, TestCommandBuilder, bInitializing
    };

    // 必须在 BEFORE_ALL 中启用 Iris
    inline static TSharedPtr<FScopedTestEnvironment> TestEnvironment{ nullptr };
    BEFORE_ALL()
    {
        TestEnvironment = FScopedTestEnvironment::Get();
        TestEnvironment->SetConsoleVariableValue(
            TEXT("net.Iris.UseIrisReplication"), TEXT("1"));
    }

    BEFORE_EACH()
    {
        FNetworkComponentBuilder()
            .WithClients(2)
            .WithGameInstanceClass(UGameInstance::StaticClass())
            .WithGameMode(AGameModeBase::StaticClass())
            .Build(Network);
    }

    AFTER_ALL()
    {
        TestEnvironment = nullptr;
    }
};
```

### 进阶用法：自定义 State 与 Actor 复制测试

通过派生 `FBasePIENetworkComponentState` 来存储测试中需要的 Actor 指针：

```cpp
// 来源: PIENetworkComponentTests.cpp (IrisReplicationTest)
NETWORK_TEST_CLASS(IrisReplicationTest, "TestFramework.CQTest.Experimental.Network")
{
    // 1. 定义派生 State，添加需要测试的 Actor 指针
    struct DerivedState : public FBasePIENetworkComponentState
    {
        AIrisTestReplicatedActor* ReplicatedActor = nullptr;
    };

    FPIENetworkComponent<DerivedState> Network{
        TestRunner, TestCommandBuilder, bInitializing
    };

    // 2. 启用 Iris（同上）
    inline static TSharedPtr<FScopedTestEnvironment> TestEnvironment{ nullptr };
    BEFORE_ALL()
    {
        TestEnvironment = FScopedTestEnvironment::Get();
        TestEnvironment->SetConsoleVariableValue(
            TEXT("net.Iris.UseIrisReplication"), TEXT("1"));
    }

    BEFORE_EACH()
    {
        FNetworkComponentBuilder<DerivedState>()
            .WithGameInstanceClass(UGameInstance::StaticClass())
            .WithGameMode(AGameModeBase::StaticClass())
            .Build(Network);
    }

    AFTER_ALL()
    {
        TestEnvironment = nullptr;
    }

    // 3. 测试：Spawn Actor 并验证复制到客户端
    TEST_METHOD(SpawnAndReplicateActor_ProvidesActorToClients)
    {
        Network.SpawnAndReplicate<AIrisTestReplicatedActor, &DerivedState::ReplicatedActor>()
            .ThenServer([this](DerivedState& ServerState) {
                ASSERT_THAT(IsNotNull(ServerState.ReplicatedActor));
            })
            .ThenClients([this](DerivedState& ClientState) {
                ASSERT_THAT(IsNotNull(ClientState.ReplicatedActor));
            });
    }

    // 4. 测试：属性修改后同步到客户端
    TEST_METHOD(UpdateProperty_SyncsToClients)
    {
        const int32 ExpectedValue = 42;

        Network.SpawnAndReplicate<AIrisTestReplicatedActor, &DerivedState::ReplicatedActor>()
            .ThenServer([this](DerivedState& ServerState) {
                ServerState.ReplicatedActor->ReplicatedInt = ExpectedValue;
            })
            .UntilClients([this](DerivedState& ClientState) {
                return ClientState.ReplicatedActor->ReplicatedInt == ExpectedValue;
            });
    }
};
```

### 进阶用法：Late Join（迟到加入）测试

```cpp
// 来源: PIENetworkComponentTests.cpp (IrisLateJoinTest)
TEST_METHOD(ThenClientJoins_AfterStart_AddsClient)
{
    Network.ThenServer([this](DerivedState& ServerState) {
        ASSERT_THAT(AreEqual(ServerState.ClientCount, 1));
    })
    .ThenClientJoins()  // 在测试中途加入新客户端
    .ThenServer([this](DerivedState& ServerState) {
        ASSERT_THAT(AreEqual(ServerState.ClientCount, 2));
    });
}

TEST_METHOD(ThenClientJoins_ReplicatesState)
{
    Network.SpawnAndReplicate<AIrisTestReplicatedActor, &DerivedState::ReplicatedActor>()
        .ThenClient(0, [this](DerivedState& ClientState) {
            ASSERT_THAT(IsNotNull(ClientState.ReplicatedActor));
        })
        .ThenClientJoins()  // 新客户端加入
        .ThenClient(1, [this](DerivedState& ClientState) {
            ASSERT_THAT(IsNotNull(ClientState.ReplicatedActor)); // 新客户端也能收到
        });
}
```

### 进阶用法：多 Actor 复制

```cpp
// 来源: PIENetworkComponentTests.cpp (IrisMultipleActorStateReplication)
struct DerivedState : public FBasePIENetworkComponentState
{
    AIrisTestReplicatedActor* ReplicatedActor1 = nullptr;
    AIrisTestReplicatedActor* ReplicatedActor2 = nullptr;
};

// 链式 SpawnAndReplicate 多个 Actor
Network.SpawnAndReplicate<AIrisTestReplicatedActor, &DerivedState::ReplicatedActor1>(MakeSetInt(42))
    .SpawnAndReplicate<AIrisTestReplicatedActor, &DerivedState::ReplicatedActor2>(MakeSetInt(24))
    .ThenClients([this](DerivedState& ClientState) {
        ASSERT_THAT(AreEqual(42, ClientState.ReplicatedActor1->ReplicatedInt));
        ASSERT_THAT(AreEqual(24, ClientState.ReplicatedActor2->ReplicatedInt));
    });
```

## Demo 示例

### 最小 Iris 网络测试示例

**头文件：MyReplicatedActor.h**

```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "MyReplicatedActor.generated.h"

UCLASS(NotBlueprintable)
class AMyReplicatedActor : public AActor
{
    GENERATED_BODY()
public:
    AMyReplicatedActor();

    void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;

    UPROPERTY(Replicated)
    int32 ReplicatedInt = 0;
};
```

**实现文件：MyReplicatedActor.cpp**

```cpp
#include "MyReplicatedActor.h"
#include "Net/UnrealNetwork.h"

AMyReplicatedActor::AMyReplicatedActor()
{
    bReplicates = true;
    bAlwaysRelevant = true;
}

void AMyReplicatedActor::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);
    DOREPLIFETIME(AMyReplicatedActor, ReplicatedInt);
}
```

**测试文件：MyIrisTest.cpp**

```cpp
#include "CQTest.h"
#include "Components/PIENetworkComponent.h"
#include "MyReplicatedActor.h"

#if ENABLE_PIE_NETWORK_TEST && UE_WITH_IRIS

NETWORK_TEST_CLASS(MyIrisTest, "MyProject.Iris")
{
    struct TestState : public FBasePIENetworkComponentState
    {
        AMyReplicatedActor* Actor = nullptr;
    };

    FPIENetworkComponent<TestState> Network{ TestRunner, TestCommandBuilder, bInitializing };

    inline static TSharedPtr<FScopedTestEnvironment> TestEnv{ nullptr };
    BEFORE_ALL()
    {
        TestEnv = FScopedTestEnvironment::Get();
        TestEnv->SetConsoleVariableValue(TEXT("net.Iris.UseIrisReplication"), TEXT("1"));
    }

    BEFORE_EACH()
    {
        FNetworkComponentBuilder<TestState>()
            .WithClients(1)
            .WithGameInstanceClass(UGameInstance::StaticClass())
            .WithGameMode(AGameModeBase::StaticClass())
            .Build(Network);
    }

    AFTER_ALL() { TestEnv = nullptr; }

    TEST_METHOD(ReplicatedInt_SyncsToClient)
    {
        Network.SpawnAndReplicate<AMyReplicatedActor, &TestState::Actor>()
            .ThenServer([](TestState& S) {
                S.Actor->ReplicatedInt = 99;
            })
            .UntilClients([](TestState& C) {
                return C.Actor->ReplicatedInt == 99;
            });
    }
};

#endif
```

**Build.cs 依赖**

```csharp
PrivateDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "NetCore",
    "CQTest"       // 必须
});
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心（World, Actor, GameMode 等） |
| `NetCore` | 网络核心模块 |
| `CQTest` | CQTest 测试框架（提供 PIENetworkComponent, TestRunner 等） |
| `EngineSettings` | 编辑器专用，引擎设置 |
| `LevelEditor` | 编辑器专用，关卡编辑器 |
| `UnrealEd` | 编辑器专用，编辑器框架 |

## 关键 API 速查

### FNetworkComponentBuilder

| 方法 | 说明 |
|---|---|
| `WithClients(int32)` | 设置客户端数量 |
| `AsDedicatedServer()` | 使用专用服务器 |
| `AsListenServer()` | 使用监听服务器 |
| `WithGameMode(TSubclassOf<AGameModeBase>)` | 设置 GameMode |
| `WithGameInstanceClass(FSoftClassPath)` | 设置 GameInstance 类 |
| `WithPacketSimulationSettings(FPacketSimulationSettings*)` | 设置丢包模拟 |
| `Build(FPIENetworkComponent&)` | 构建网络组件 |

### FPIENetworkComponent\<T\>

| 方法 | 说明 |
|---|---|
| `ThenServer(TFunction<void(T&)>)` | 在服务器执行（下一帧） |
| `ThenClient(int32, TFunction<void(T&)>)` | 在指定客户端执行 |
| `ThenClients(TFunction<void(T&)>)` | 在所有客户端执行 |
| `UntilServer(TFunction<bool(T&)>)` | 在服务器轮询直到返回 true |
| `UntilClients(TFunction<bool(T&)>)` | 在所有客户端轮询直到返回 true |
| `ThenClientJoins()` | 中途加入新客户端 |
| `SpawnAndReplicate<Actor, &State::Ptr>()` | Spawn Actor 并复制到所有客户端 |
| `Then(TFunction<void()>)` | 通用延迟命令 |
| `Until(TFunction<bool()>)` | 通用轮询命令 |
| `StartWhen(TFunction<bool()>)` | 等待条件满足后开始 |

### FBasePIENetworkComponentState

| 字段 | 类型 | 说明 |
|---|---|---|
| `World` | `UWorld*` | PIE 会话的世界引用 |
| `ClientConnections` | `TArray<UNetConnection*>` | 服务器端的客户端连接列表 |
| `ClientIndex` | `int32` | 当前客户端在连接列表中的索引 |
| `ClientCount` | `int32` | 客户端数量 |
| `bIsDedicatedServer` | `bool` | 是否为专用服务器 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-07-30 | `758607848502` | Fix for null entries in ClientConnections array | 修复了 ClientConnections 数组中可能出现 null 条目的 bug，属于稳定性修复 |
| 2025-05-09 | `b9141519ee99` | Added support for the upcoming Iris replication system as part of the new CQTestExperimental plugin | 插件首次提交，引入 Iris 复制系统的测试支持 |

### 维护评价

- **状态**: 🆕 新建插件（2025-05-09 创建，约 3 个月历史）
- **更新频率**: 2 次提交，均为实质性更新
- **活跃度**: 活跃维护中，有持续的 bug 修复
- **稳定性**: IsExperimentalVersion = true，表明 API 可能随 Iris 系统的演进而变化
- **建议**: 如果你在使用 Iris 复制系统，这个插件是编写网络测试的必备参考。即使不直接使用插件本身，其中的测试用例也是学习 FPIENetworkComponent + Iris 的最佳资料。注意该插件标记为 Experimental，API 可能随 Iris 系统演进而变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Tests/CQTestExperimental)
- [CQTest 核心插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Tests/CQTest)
- [Iris 复制系统文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/iris-replication-system-in-unreal-engine)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Tests/CQTestExperimental/Source/CQTestExperimentalTests/Private/Iris/PIENetworkComponentTests.cpp)
