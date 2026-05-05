# Code Quality Tests Unreal Test Plugin (CQTest)

> Tests for the CQTest Unreal Engine module

| 属性 | 值 |
|---|---|
| 分类 | Testing |
| 默认启用 | ✅ EnabledByDefault (未设置，默认 false) |
| 包含内容 | false |
| 模块 | CQTestTests (DeveloperTool) |
| 创建时间 | 2023-03-29 |
| 年龄标签 | 🆕 (约 3 年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Tests/CQTest) | |

> **注意**: 本 plugin 是 CQTest 框架的**测试套件**。CQTest 框架本体位于 `Engine/Source/Developer/CQTest/`，是一个内置模块（无需额外 plugin）。本文档同时覆盖框架本身和测试 plugin 的用法。

## 用途

CQTest（Code Quality Test）是 Epic 为 Unreal Engine 开发的 **C++ 自动化测试框架**，在 UE 原生 `IMPLEMENT_SIMPLE_AUTOMATION_TEST` 基础上提供了一套更高层的 DSL（领域特定语言），包括：

- **BDD 风格的测试组织**：`TEST_CLASS` / `TEST_METHOD` 替代冗长的 `IMPLEMENT_SIMPLE_AUTOMATION_TEST` 宏
- **Fixture 生命周期管理**：`BEFORE_EACH` / `AFTER_EACH` / `BEFORE_ALL` / `AFTER_ALL`
- **断言系统**：`ASSERT_THAT` 宏 + `FNoDiscardAsserter` 链式断言，支持 `[[nodiscard]]` 检查
- **Latent 命令构建器**：`FTestCommandBuilder` 提供链式 API 构建异步测试序列
- **Actor/Object 生成辅助**：`FActorTestSpawner` / `FMapTestSpawner` / `TObjectBuilder`
- **网络测试组件**：`FPIENetworkComponent` 支持 PIE 下的 Server/Client 联网测试
- **资产查询辅助**：`CQTestAssetHelper` 在测试中查找 Blueprint 和资产

该框架解决了 UE 原生测试宏代码冗余、缺乏 fixture 管理、异步测试写法繁琐等问题。

## 使用场景

- 你需要编写 C++ 自动化测试，但不想每次手写 `IMPLEMENT_SIMPLE_AUTOMATION_TEST` + 完整的 class 定义 → 用 `TEST_CLASS` + `TEST_METHOD`
- 你需要在测试间共享 setup/teardown 逻辑 → 用 `BEFORE_EACH` / `AFTER_EACH`
- 你需要测试涉及多帧的异步逻辑（等待 Actor tick、等待条件满足）→ 用 `FTestCommandBuilder` 的 `Do` / `Until` / `StartWhen`
- 你需要在测试中生成 Actor 并设置属性 → 用 `FActorTestSpawner` + `TObjectBuilder`
- 你需要测试网络复制功能 → 用 `FPIENetworkComponent` + `NETWORK_TEST_CLASS`
- 你需要在测试中加载地图并验证 → 用 `FMapTestSpawner`

## 蓝图用法

CQTest 是纯 C++ 测试框架，不提供蓝图节点。所有 API 均在 C++ 层面使用。

## C++ 用法

### 头文件引入

```cpp
// 核心框架 — 所有测试都需要
#include "CQTest.h"

// Actor 生成
#include "Components/ActorTestSpawner.h"

// 地图加载测试
#include "Components/MapTestSpawner.h"

// 网络测试
#include "Components/PIENetworkComponent.h"

// Object 构建器
#include "ObjectBuilder.h"

// 资产辅助
#include "Helpers/CQTestAssetHelper.h"
```

### 基本用法 — 最简测试

> 来源: `Engine/Plugins/Tests/CQTest/Source/CQTestTests/Private/CQTestTests.cpp`

```cpp
#include "CQTest.h"

// 最简单的测试：单个 TEST 宏
TEST(MyFirstTest, "Game.Example")
{
    ASSERT_THAT(IsTrue(1 + 1 == 2));
};
```

### 测试类 + 测试方法

```cpp
#include "CQTest.h"

TEST_CLASS(MyFixture, "Game.Example")
{
    // 成员变量在每个测试方法间独立重置
    int32 Counter = 0;

    BEFORE_EACH()
    {
        Counter = 10;
    }

    AFTER_EACH()
    {
        // 清理逻辑
    }

    TEST_METHOD(Counter_StartsAt10)
    {
        ASSERT_THAT(AreEqual(10, Counter));
    }

    TEST_METHOD(CanIncrementCounter)
    {
        Counter++;
        ASSERT_THAT(AreEqual(11, Counter));
    }
};
```

### 断言 API

> 来源: `Engine/Plugins/Tests/CQTest/Source/CQTestTests/Private/Assert/AssertionTests.cpp`

`FNoDiscardAsserter` 提供以下断言（均标记为 `[[nodiscard]]`，必须配合 `ASSERT_THAT` 使用）：

```cpp
// 布尔断言
ASSERT_THAT(IsTrue(Condition));
ASSERT_THAT(IsTrue(Condition, "自定义错误消息"));
ASSERT_THAT(IsFalse(Condition));

// 相等断言（整数/字符串，不支持直接比较浮点数）
ASSERT_THAT(AreEqual(Expected, Actual));
ASSERT_THAT(AreNotEqual(Expected, Actual));

// 忽略大小写字符串比较
ASSERT_THAT(AreEqualIgnoreCase("Hello", "hello"));
ASSERT_THAT(AreNotEqualIgnoreCase("Hello", "world"));

// 浮点近似比较
ASSERT_THAT(IsNear(3.14, 3.141, 0.01));

// 指针断言
ASSERT_THAT(IsNull(Ptr));
ASSERT_THAT(IsNotNull(Ptr));

// 立即失败并返回
ASSERT_FAIL("测试失败消息");

// 预期错误（测试中故意触发的错误）
Assert.ExpectError("预期的错误消息");
Assert.ExpectErrorRegex("\\d+ milliseconds");

// 手动失败
Assert.Fail("手动失败");
```

### Fixture 生命周期

```cpp
TEST_CLASS(LifecycleExample, "Game.Example")
{
    // 静态初始化 — 整个测试类只执行一次
    BEFORE_ALL()
    {
        // 适合做昂贵的一次性初始化
    }

    // 每个测试方法前执行
    BEFORE_EACH()
    {
        // 每个测试的 setup
    }

    // 每个测试方法后执行
    AFTER_EACH()
    {
        // 每个测试的 teardown
    }

    // 静态清理 — 整个测试类只执行一次
    AFTER_ALL()
    {
        // 适合做昂贵的一次性清理
    }

    TEST_METHOD(SomeTest)
    {
        // 测试逻辑
    }
};
```

### Latent 命令（异步测试）

> 来源: `Engine/Plugins/Tests/CQTest/Source/CQTestTests/Private/CQTestTests.cpp`

`FTestCommandBuilder` 支持链式构建异步测试序列：

```cpp
TEST_CLASS(AsyncExample, "Game.Example")
{
    TEST_METHOD(WaitForCondition)
    {
        // Do: 在下一帧执行
        TestCommandBuilder.Do([&]() {
            // 某些异步逻辑
        });

        // Until: 每帧检查条件，直到为 true
        TestCommandBuilder.Until([&]() {
            return SomeCondition();
        });

        // Then: 条件满足后执行
        TestCommandBuilder.Then([&]() {
            ASSERT_THAT(IsTrue(SomeCondition()));
        });
    }

    TEST_METHOD(StartWhenExample)
    {
        // StartWhen: 等待条件成立后才开始执行后续命令
        TestCommandBuilder
            .StartWhen([&]() { return bReady; })
            .Then([&]() { ASSERT_THAT(IsTrue(bReady)); });
    }
};
```

也可以直接使用底层 latent command：

```cpp
TEST_METHOD(UsingAddCommand)
{
    // 直接添加 latent command
    AddCommand(new FWaitUntil(*TestRunner, [&]() {
        return Tickable.TickCount > 2;
    }));
}
```

### OnTearDown（清理命令）

```cpp
TEST_METHOD(WithCleanup)
{
    TestCommandBuilder
        .Do([&]() { /* 做一些需要清理的事 */ })
        .OnTearDown([&]() {
            // 即使测试失败也会执行（逆序执行）
        });
}
```

### Actor 生成

> 来源: `Engine/Plugins/Tests/CQTest/Source/CQTestTests/Private/Components/SpawnHelperTests.cpp`

```cpp
#include "CQTest.h"
#include "Components/ActorTestSpawner.h"

TEST_CLASS(ActorSpawnExample, "Game.Actor")
{
    FActorTestSpawner Spawner;

    TEST_METHOD(SpawnBasicActor)
    {
        // 生成默认 Actor
        AActor& Actor = Spawner.SpawnActor<AActor>();
        ASSERT_THAT(IsNotNull(&Actor));
    }

    TEST_METHOD(SpawnWithParameters)
    {
        FActorSpawnParameters Params;
        Params.Name = TEXT("MyActor");
        AActor& Actor = Spawner.SpawnActor<AActor>(Params);
        ASSERT_THAT(AreEqual(Actor.GetFName(), FName(TEXT("MyActor"))));
    }

    TEST_METHOD(SpawnAndAddComponent)
    {
        AActor& Owner = Spawner.SpawnActor<AActor>();
        auto* Component = NewObject<USceneComponent>(&Owner);
        Component->RegisterComponent();
        ASSERT_THAT(AreEqual(Component->GetOwner(), &Owner));
    }

    TEST_METHOD(SpawnNonActorObject)
    {
        // SpawnObject 用于非 Actor 的 UObject
        auto& Component = Spawner.SpawnObject<USceneComponent>();
    }
};
```

### TObjectBuilder（属性构建器）

> 来源: `Engine/Plugins/Tests/CQTest/Source/CQTestTests/Private/ObjectBuilderTests.cpp`

`TObjectBuilder` 提供 builder 模式，在 Spawn 前设置属性：

```cpp
TEST_CLASS(ObjectBuilderExample, "Game.Actor")
{
    FActorTestSpawner Spawner;

    TEST_METHOD(BuildActorWithProperties)
    {
        auto& Actor = TObjectBuilder<AMyActor>(Spawner)
            .SetParam("Health", 100)
            .SetParam("Name", FName("Hero"))
            .SetParam("Location", FVector::UpVector)
            .Spawn();

        ASSERT_THAT(AreEqual(Actor.Health, 100));
    }

    TEST_METHOD(BuildActorWithComponent)
    {
        auto& Actor = TObjectBuilder<AMyActor>(Spawner)
            .AddComponentTo<USceneComponent>()
            .Spawn();

        ASSERT_THAT(AreEqual(Actor.GetComponents().Num(), 1));
    }

    TEST_METHOD(BuildActorWithChildActor)
    {
        auto& Actor = TObjectBuilder<AMyActor>(Spawner)
            .AddChildActorComponentTo<AChildActor>()
            .Spawn();
    }

    TEST_METHOD(BuildNonActorObject)
    {
        auto& Anim = TObjectBuilder<UAnimSequence>()
            .SetParam<bool>("bEnableRootMotion", true)
            .SetParam("RefFrameIndex", 321)
            .Spawn();

        ASSERT_THAT(IsTrue(Anim.bEnableRootMotion));
    }
};
```

支持的属性类型：`bool`, `int8/16/32/64`, `uint8/16/32/64`, `float`, `double`, `FName`, `FVector`, 枚举，UStruct，`TArray`, `TSet`, `TMap`, `TObjectPtr`，以及任意 `UObject*` 派生类型。

### 地图加载测试

```cpp
#include "CQTest.h"
#include "Components/MapTestSpawner.h"

TEST_CLASS(MapExample, "Game.Map")
{
    TUniquePtr<FMapTestSpawner> Spawner;

    BEFORE_EACH()
    {
        Spawner = MakeUnique<FMapTestSpawner>(
            TEXT("/Game/Maps"), TEXT("TestMap"));
        Spawner->AddWaitUntilLoadedCommand(TestRunner);
    }

    TEST_METHOD(PlayerPawnExists)
    {
        APawn* Pawn = nullptr;
        TestCommandBuilder
            .StartWhen([this, &Pawn]() {
                Pawn = Spawner->FindFirstPlayerPawn();
                return nullptr != Pawn;
            })
            .Then([&]() { ASSERT_THAT(IsNotNull(Pawn)); });
    }
};
```

### 网络测试（PIE Network）

```cpp
#include "CQTest.h"
#include "Components/PIENetworkComponent.h"

#if ENABLE_PIE_NETWORK_TEST

NETWORK_TEST_CLASS(NetworkExample, "Game.Network")
{
    struct NetState : public FBasePIENetworkComponentState
    {
        APawn* ReplicatedPawn;
    };

    FPIENetworkComponent<NetState> Network{
        TestRunner, TestCommandBuilder, bInitializing
    };

    BEFORE_EACH()
    {
        FNetworkComponentBuilder<NetState>()
            .WithClients(2)
            .WithGameMode(AGameModeBase::StaticClass())
            .Build(Network);
    }

    TEST_METHOD(SpawnAndReplicate)
    {
        Network.SpawnAndReplicate<APawn, &NetState::ReplicatedPawn>()
            .ThenServer([](NetState& Server) {
                ASSERT_THAT(IsNotNull(Server.ReplicatedPawn));
            })
            .ThenClients([](NetState& Client) {
                ASSERT_THAT(IsNotNull(Client.ReplicatedPawn));
            });
    }
};

#endif
```

### 自定义 Assert 和基类

> 来源: `Engine/Plugins/Tests/CQTest/Source/CQTestTests/Private/ExtensionTests.cpp`

```cpp
// 自定义断言器
struct FMyAsserter : public FNoDiscardAsserter
{
    using FNoDiscardAsserter::FNoDiscardAsserter;

    bool IsValidHealth(int32 Health)
    {
        return Health > 0 && Health <= 100;
    }
};

// 使用自定义断言
TEST_CLASS_WITH_ASSERTS(MyTest, "Game.Example", FMyAsserter)
{
    TEST_METHOD(HealthIsValid)
    {
        ASSERT_THAT(IsValidHealth(50));
    }
};

// 自定义基类
template <typename Derived, typename AsserterType>
struct TMyTestBase : public TTest<Derived, AsserterType>
{
    int32 SharedValue = 42;
};

TEST_CLASS_WITH_BASE(DerivedTest, "Game.Example", TMyTestBase)
{
    TEST_METHOD(InheritsBaseValue)
    {
        ASSERT_THAT(AreEqual(42, SharedValue));
    }
};
```

### 测试标签和标志

```cpp
// 带标签的测试类
TEST_CLASS_WITH_TAGS(TaggedTest, "Game.Example", "[Smoke][Gameplay]")
{
    // 类级别的标签会传播到所有方法
    TEST_METHOD(SomeTest) { }

    // 方法级别额外标签
    TEST_METHOD_WITH_TAGS(TaggedMethod, "[Slow]")
    {
        // 该方法的标签: [Smoke][Gameplay][Slow]
    }
};

// 带自定义标志的测试类
TEST_CLASS_WITH_FLAGS(EngineTest, "Engine.Example",
    EAutomationTestFlags_ApplicationContextMask | EAutomationTestFlags::EngineFilter)
{
    TEST_METHOD(SomeEngineTest) { }
};
```

### 日志抑制

```cpp
TEST_METHOD(SuppressLogErrors)
{
    // 抑制 Error 级别日志（避免测试因已知错误日志失败）
    TestRunner->SetSuppressLogErrors();
    UE_LOG(LogTemp, Error, TEXT("This will be suppressed"));

    // 恢复
    TestRunner->SetSuppressLogErrors(ECQTestSuppressLogBehavior::False);
}

TEST_METHOD(SuppressLogWarnings)
{
    TestRunner->SetSuppressLogWarnings();
    UE_LOG(LogTemp, Warning, TEXT("This will be suppressed"));
}
```

### 超时配置

CQTest 通过 CVar 控制 latent 命令的超时时间：

| CVar | 默认值 | 用途 |
|---|---|---|
| `TestFramework.CQTest.CommandTimeout` | 10s | 通用 latent 命令超时 |
| `TestFramework.CQTest.CommandTimeout.Network` | 30s | 网络测试超时 |
| `TestFramework.CQTest.CommandTimeout.MapTest` | 30s | 地图加载超时 |

可在 `DefaultEngine.ini` 中配置：

```ini
[/Script/CQTest.CQTestSettings]
CommandTimeout=15.0
NetworkTimeout=60.0
```

## Demo 示例

### 最小可编译测试示例

**Build.cs 依赖**（你的测试模块需要依赖 CQTest）：

```csharp
// YourTestModule.Build.cs
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "CQTest"  // 关键依赖
});
```

**完整测试文件**：

```cpp
// MyGameTests.cpp
#include "CQTest.h"
#include "Components/ActorTestSpawner.h"

namespace MyGameTests
{

// 最简单的测试
TEST(SimpleMath, "MyGame.Math")
{
    ASSERT_THAT(AreEqual(4, 2 + 2));
};

// 带 Fixture 的测试类
TEST_CLASS(ActorTests, "MyGame.Actor")
{
    FActorTestSpawner Spawner;
    int32 SpawnCount = 0;

    BEFORE_EACH()
    {
        SpawnCount = 0;
    }

    TEST_METHOD(CanSpawnActor)
    {
        AActor& Actor = Spawner.SpawnActor<AActor>();
        ASSERT_THAT(IsNotNull(&Actor));
        SpawnCount++;
        ASSERT_THAT(AreEqual(1, SpawnCount));
    }

    TEST_METHOD(ActorHasDefaultLocation)
    {
        AActor& Actor = Spawner.SpawnActor<AActor>();
        ASSERT_THAT(IsTrue(
            Actor.GetActorLocation().IsZero()));
    }
};

} // namespace MyGameTests
```

## 模块依赖

CQTest 框架模块 (`Engine/Source/Developer/CQTest/`) 的依赖：

| 模块 | 用途 |
|---|---|
| `DeveloperSettings` | 通过 `UCQTestSettings` 支持 CVar 配置（公共依赖） |
| `Core` | UE 核心模块 |
| `CoreUObject` | UObject 系统（反射、属性访问） |
| `Engine` | 引擎核心（World、Actor） |
| `NetCore` | 网络核心（`TAsyncResult`） |
| `Slate` | UI 框架（Slate 测试组件） |
| `EngineSettings` | 引擎设置（仅编辑器） |
| `LevelEditor` | 关卡编辑器（仅编辑器） |
| `UnrealEd` | 编辑器功能（仅编辑器） |

使用 CQTest 的模块只需依赖 `CQTest`：

```csharp
PrivateDependencyModuleNames.Add("CQTest");
```

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-07-30 | `758607848502` | Fix for null entries in ClientConnections array | 网络组件 bug 修复，修复了 ClientConnections 中存在 null 条目的问题 |
| 2025-07-10 | `abb369e2fd63` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files | 代码质量改进，使用新宏优化编译 |
| 2025-05-29 | `26a10c8fad93` | CQTest - Support assert macros in base test classes | 功能更新，支持在基类测试中使用 ASSERT_THAT 宏 |

### 维护评价

- **创建时间**: 2023-03-29，约 3 年历史
- **最近更新**: 2025-07-30，约 1 个月前
- **更新频率**: 持续活跃，最近 3 个月内有多次实质性更新
- **更新内容**: 包含 bug 修复、编译优化和功能增强
- **维护状态**: ✅ **活跃维护**
- **推荐使用**: ✅ 推荐。作为 Epic 官方的测试框架，在引擎源码中被广泛使用，API 稳定且持续改进

## 相关链接

- [CQTest Plugin 源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Tests/CQTest)
- [CQTest 框架模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/Developer/CQTest)
- [CQTest 测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Tests/CQTest/Source/CQTestTests/Private)
