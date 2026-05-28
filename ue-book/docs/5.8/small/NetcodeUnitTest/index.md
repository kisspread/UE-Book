# Netcode Unit Test

> A unit testing framework for testing the Unreal Engine netcode, primarily for bugs and exploits

| 属性 | 值 |
|---|---|
| 中文名 | 网络代码单元测试 |
| 分类 | Networking |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NetcodeUnitTest` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2015-05-05 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NetcodeUnitTest/NetcodeUnitTest) | |

## 用途

NetcodeUnitTest 插件提供了一个专门用于测试虚幻引擎网络代码（Netcode）的单元测试框架。它不仅仅是一个普通的单元测试运行器，更是一个集成了高度可控的“最小客户端”、强大的日志追踪、VM反射工具、进程管理和自定义UI调试窗口的综合工具链。其核心目标是为网络程序员和测试工程师提供一套可靠的自动化环境，用于**主动发现、复现和验证**网络相关的 Bug 和安全漏洞（Exploit），确保多人游戏中的网络逻辑健壮可靠。

## 使用场景

- **你是一名网络程序员，怀疑某段 RPC 或复制逻辑存在 Bug** → 使用此框架编写最小化的单元测试来复现问题，自动启动服务器和最小客户端进行测试。
- **你正在开发一个新的网络功能，想要验证其安全性（例如，某个客户端能否发送非法 RPC）** → 创建 ClientUnitTest 子类，配置最小客户端的 `MinClientFlags` 来精确控制允许/禁止的行为，然后编写测试用例。
- **你需要对网络代码进行批量、自动化的回归测试** → 使用 `UUnitTestCommandlet` 以无UI模式运行，集成到CI/CD流程中。
- **你在调试复杂的网络问题，需要查看详细的、分场景（本地/服务器/客户端）的日志和原始数据包** → 利用插件提供的 Slate 日志窗口、`FScopedLog` 工具以及 `ELogType` 过滤系统。
- **你需要访问游戏对象上未公开（Private/Protected）的属性或函数来进行测试** → 使用 `FVMReflection` 反射助手和 `GET_PRIVATE`/`CALL_PROTECTED` 宏。

## 蓝图用法

此插件主要面向 C++ 开发，但通过 `ANUTActor` 在蓝图中暴露了一些关键的 RPC 和调试函数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Admin` | 在服务器上执行一个控制台命令 | `ANUTActor` |
| `UnitTravel` | 触发普通场景旅行（Dest 为空则旅行到当前关卡） | `ANUTActor` |
| `UnitSeamlessTravel` | 触发无缝场景旅行 | `ANUTActor` |
| `NetFlush` | 刷新当前所有待发送的网络包 | `ANUTActor` |
| `Wait` | 使游戏线程等待指定的秒数（用于调试/同步） | `ANUTActor` |

### 使用示例（蓝图描述）

1.  在需要进行网络测试的关卡中，放置一个 `ANUTActor`（或在游戏开始时 Spawn 一个）。
2.  在蓝图图表中，通过 `Get Player Controller` 获取本地玩家控制器。
3.  从控制器拖出引线，使用 `Call Function` 节点调用 `Admin`，在 `Command` 参数中输入服务器控制台命令（如 `stat net`）。
4.  要进行场景旅行，同样调用 `UnitTravel` 或 `UnitSeamlessTravel`，`Dest` 参数可以留空（表示重载当前关卡）或指定新关卡路径。
5.  当需要测试网络包发送时序时，可以调用 `NetFlush` 强制立即发送所有排队的数据包。
6.  使用 `Wait` 节点可以在蓝图流程中插入延迟，以便观察网络状态变化，例如在发送RPC后等待1秒再执行后续操作。

## C++ 用法

### 头文件引入

```cpp
#include “NetcodeUnitTest.h”
#include “NUTUtil.h”
#include “NUTUtilDebug.h”
#include “NUTUtilReflection.h”
```

### 基本用法：编写一个简单的客户端单元测试

以下代码演示了如何创建一个测试客户端 RPC 的最小用例。

**MyUnitTest.h**
```cpp
#pragma once
#include “ClientUnitTest.h”

UCLASS()
class UMyNetcodeTest : public UClientUnitTest
{
    GENERATED_BODY()

public:
    UMyNetcodeTest()
    {
        UnitTestName = TEXT(“TestSimpleRPC”);
        UnitTestType = TEXT(“Bug”);
        UnitTestFlags = EUnitTestFlags::LaunchServer | EUnitTestFlags::RequirePawn;
        MinClientFlags = EMinClientFlags::AcceptActors | EMinClientFlags::AcceptRPCs;
    }

    virtual void ExecuteClientUnitTest() override;
};
```

**MyUnitTest.cpp**
```cpp
#include “MyUnitTest.h”

void UMyNetcodeTest::ExecuteClientUnitTest()
{
    Super::ExecuteClientUnitTest();

    // 使用 FScopedLog 开启 Net 和 Rep 的日志记录
    FScopedLogNet ScopedLog(this);

    // 获取本地控制的 Pawn
    APawn* TestPawn = UnitPC->GetPawn();
    if (TestPawn)
    {
        // 使用反射助手设置一个属性，用于触发某个逻辑
        FVMReflection Refl(TestPawn);
        Refl->*”bSomeTestFlag” = true;

        // 发送一个 RPC 到服务器，并等待确认
        MinClient->SendRPCChecked(TestPawn, TEXT(“ServerDoSomething”), &SomeParams, sizeof(SomeParams));

        // 标记测试执行部分已完成，后续验证逻辑可在此添加
        FinishUnitTest(EUnitTestVerification::VerifiedFixed);
    }
    else
    {
        UNIT_LOG(ELogType::StatusError, TEXT(“获取 Pawn 失败，测试中止。”));
        AbortUnitTest();
    }
}
```

### 进阶用法：利用 FScopedLog 和反射进行深度调试

```cpp
#include “NUTUtilDebug.h”
#include “NUTUtilReflection.h”

void DebugNetcodeFunction(UMinimalClient* MinClient)
{
    // 1. 作用域日志：启用特定的日志类别，并在退出作用域时自动禁用
    {
        FScopedLog ScopedLog({TEXT(“LogNetTraffic”), TEXT(“LogNetSerialization”)}, /* bRemoteLogging */ true);
        // 在此作用域内的网络操作，其详细流量日志都会被捕获
        MinClient->SendRPCChecked(…);
    } // 离开作用域，日志恢复原状

    // 2. 反射访问：安全地读取一个私有成员
    IMPLEMENT_GET_PRIVATE_VAR(FStackTracker, bIsEnabled, bool);
    FStackTracker* Tracker = /* 获取某个Tracker实例 */;
    bool bEnabled = GET_PRIVATE(FStackTracker, Tracker, bIsEnabled);
    UE_LOG(LogTemp, Log, TEXT(“StackTracker Enabled: %s”), bEnabled ? TEXT(“True”) : TEXT(“False”));

    // 3. 链式反射：深度访问对象图
    UObject* TargetObj = /* 某个UObject*/;
    FVMReflection Refl(TargetObj);
    // 访问 TargetObj->WorldInventory->Inventory->Items[0]->ItemGuid->A
    int32* Value = (int32*)(((Refl->*”WorldInventory”->*”Inventory”->*”Items”)[“FFortItemEntry”][0]->*”ItemGuid”)[“FGuid”]->*”A”);
    if (Value)
    {
        UE_LOG(LogTemp, Log, TEXT(“Guid.A = %d”), *Value);
    }
}
```

## Demo 示例

一个完整的最小示例，展示如何在自定义单元测试中使用核心工具。

**DemoUnitTest.h**
```cpp
#pragma once
#include “UnitTest.h”
#include “NUTUtilDebug.h” // for FScopedLog
#include “NUTUtilReflection.h” // for FVMReflection

UCLASS()
class UDemoUnitTest : public UUnitTest
{
    GENERATED_BODY()

public:
    UDemoUnitTest();
    virtual bool ExecuteUnitTest() override;
};
```

**DemoUnitTest.cpp**
```cpp
#include “DemoUnitTest.h”

UDemoUnitTest::UDemoUnitTest()
{
    UnitTestName = TEXT(“DemoReflectionLog”);
    UnitTestType = TEXT(“Example”);
    bWorkInProgress = true;
}

bool UDemoUnitTest::ExecuteUnitTest()
{
    // 启用作用域日志
    FScopedLog LogScope({TEXT(“LogTemp”)});

    // 创建一个测试对象
    UObject* TestObject = NewObject<UObject>();

    // 使用反射设置一个属性（假设 UObject 有此属性）
    FVMReflection Refl(TestObject);
    Refl->*”SomeProperty” = 42;

    // 读取它
    int32* Value = (int32*)(Refl->*”SomeProperty”);
    if (Value && *Value == 42)
    {
        UNIT_LOG(ELogType::StatusSuccess, TEXT(“反射测试通过！”));
        return true; // 测试成功
    }
    else
    {
        UNIT_LOG(ELogType::StatusFailure, TEXT(“反射测试失败。”));
        return false; // 测试失败
    }
}
```

## 模块依赖

该插件依赖以下非标准模块，你的项目模块需要在 `.Build.cs` 中引用它们以使用此插件的高级功能。

| 模块 | 用途 |
|---|---|
| `UnitTestCore` | 提供单元测试基础框架和核心类型 |
| `Sockets` | 用于底层的网络套接字操作 |
| `Networking` | UE的核心网络模块 |
| `PacketHandler` | 用于拦截和处理底层网络数据包 |
| `OnlineSubsystem` | 涉及在线子系统相关测试 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 涉及视口代码重构，与网络代码单元测试无直接功能关联。 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回退了一个之前的更改。 |
| 2026-04-29 | `bef86caa` | Whitespace: followup to migrate UE_LOG to UE_LOGF: Restore newlines in multi-line format strings tha | 日志宏迁移的后续格式化修复，属于代码维护。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了跨平台（32/64位）的日志格式化说明符问题。 |

### 维护评价

- **年龄**：插件创建于2015年，属于“文物”级别，有超过11年的历史。
- **更新频率**：最近一次功能性更新远早于最近的提交（2026年的提交都是编译修复、代码重构或与插件核心功能无关的改动）。
- **维护状态**：**维护不活跃**。虽然近期仍有提交以保证其能在新版引擎中编译，但核心功能已长期没有更新或增强。插件本身已处于成熟但“冻结”的状态。
- **已知限制**：插件默认禁用 (`EnabledByDefault: false`)，表明它是一个专业工具而非通用功能。它依赖特定的平台（Win64, Linux）和特定的构建类型（UncookedOnly）。
- **推荐使用**：**仅推荐给有明确网络测试需求的高级开发者或测试团队**。它是一个功能强大的专业工具，但对于一般的游戏开发流程来说过于复杂。在使用前，需要充分理解其架构（尤其是最小客户端和单元测试标志）。对于新的项目，应评估是否有更现代的替代方案或自研更轻量的测试框架。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NetcodeUnitTest/NetcodeUnitTest)
- [官方文档](https://docs.unrealengine.com)（插件本身无独立文档，可在引擎文档中搜索相关概念）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NetcodeUnitTest/NetcodeUnitTest/Source/NetcodeUnitTest/Classes/UnitTests)