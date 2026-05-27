```markdown
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

这是一个专用于 UE 网络代码（Netcode）的单元测试框架，核心目标是**验证和复现网络代码中的 bug 与安全漏洞（exploit）**。

该插件提供了一套完整的最小化客户端（MinimalClient）实现，能够以极低开销连接到游戏服务器，同时屏蔽掉绝大部分常规客户端逻辑，仅保留最精简的网络通信链路。这使得开发者可以精确地发送和拦截特定网络数据包、RPC 调用、属性复制等行为，从而：

- **复现网络 bug**：通过最小化客户端精确控制网络交互，定位并重现难以复现的网络问题
- **验证安全漏洞**：测试恶意构造的网络数据是否能触发服务端崩溃或异常行为
- **回归测试**：通过 Commandlet 自动化运行，在 CI/CD 中持续验证网络代码的正确性
- **验证修复**：标记测试用例为"已修复"或"未修复"，跟踪修复进度

与 UE 内置的 Automation Test 框架不同，该框架专注于**跨进程的端到端网络测试**——会实际启动独立的服务器和客户端进程，模拟真实的游戏网络环境。

## 使用场景

- 你需要测试某个 RPC 是否能被恶意构造的参数导致服务端崩溃 → 用 MinimalClient + FVMReflection 构造畸形参数发送
- 你需要验证某个属性复制漏洞是否已修复 → 创建 UClientUnitTest 子类，配置 EMinClientFlags 控制接受行为
- 你需要在 CI 中批量运行所有网络相关的单元测试 → 使用 `UnitTestCommandlet` 无头运行
- 你需要调试某个特定的网络数据包序列 → 使用 FScopedLog / FScopedLogNet 开启详细日志
- 你需要访问 UE UScript 虚拟机中的任意属性（无需静态依赖） → 使用 FVMReflection 反射辅助类

## 蓝图用法

该插件主要面向 C++ 开发者，蓝图支持非常有限。核心测试逻辑通过 C++ 继承实现。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Admin` | 在服务器上执行控制台命令 | `ANUTActor` |
| `UnitSeamlessTravel` | 触发无缝迁移 | `ANUTActor` |
| `UnitTravel` | 触发普通迁移 | `ANUTActor` |
| `NetFlush` | 刷新所有待发送的网络包 | `ANUTActor` |
| `Wait` | 使游戏线程等待指定秒数 | `ANUTActor` |
| `ServerReceiveText` | 向服务器发送测试文本 | `ANUTActor` |

> 注意：这些节点主要用于 NUTActor 的服务端通信，实际单元测试的编写和执行需要在 C++ 中完成。

## C++ 用法

### 头文件引入

```cpp
#include "NetcodeUnitTest.h"
#include "NUTUtil.h"
#include "NUTEnum.h"
#include "ClientUnitTest.h"
#include "MinimalClient.h"
#include "UnitTestEnvironment.h"
#include "NUTUtilReflection.h"
```

### 基本用法：创建一个单元测试

创建一个继承自 `UClientUnitTest` 的测试类，配置标志位并实现测试逻辑。

```cpp
// Source/NetcodeUnitTest/Classes/ClientUnitTest.h
// 最小化的 ClientUnitTest 子类骨架

UCLASS()
class UMyNetTest : public UClientUnitTest
{
    GENERATED_UCLASS_BODY()

    UMyNetTest()
    {
        // 测试名称和类型
        UnitTestName = TEXT("MyNetTest");
        UnitTestType = TEXT("Exploit");

        // 配置测试标志：自动启动服务器，等待 PlayerController 后执行
        UnitTestFlags = EUnitTestFlags::LaunchServer
                      | EUnitTestFlags::RequirePlayerController;

        // 最小客户端标志：接受 Actor 创建
        MinClientFlags = EMinClientFlags::AcceptActors;

        // 超时时间（秒）
        UnitTestTimeout = 60;
    }

    // 核心测试逻辑实现
    virtual void ExecuteClientUnitTest() override
    {
        Super::ExecuteClientUnitTest();

        // UNIT_LOG 宏记录单元测试状态日志
        UNIT_LOG(ELogType::StatusImportant, TEXT("开始执行网络单元测试"));

        // 在此处编写测试逻辑：构造数据包、发送 RPC、验证结果等
        // 测试完成后调用 EndUnitTest
        EndUnitTest();
    }
};
```

### 进阶用法：使用 FVMReflection 进行反射式属性访问

无需静态引用目标类，通过字符串名称访问任意 UObject 属性：

```cpp
// Source/NetcodeUnitTest/Public/NUTUtilReflection.h
// 通过反射访问 PlayerController 的嵌套属性

// 获取 PC 的 QuickBars 属性
AActor* QuickBars = (AActor*)(UObject*)(FVMReflection(UnitPC.Get())->*"QuickBars");

// 访问深层嵌套属性：WorldInventory->Inventory->Items[0]->ItemGuid
FGuid* EntryItemGuidRef = (FGuid*)(void*)(
    (((FVMReflection(UnitPC.Get())
        ->*"WorldInventory"->*"Inventory"->*"Items")
            ["FFortItemEntry"][0]->*"ItemGuid")
                ["FGuid"])
);

// 对比传统手动反射代码，FVMReflection 将十几行代码缩减为一两行
```

### 进阶用法：使用 MinimalClient 发送自定义 RPC

```cpp
// Source/NetcodeUnitTest/Classes/MinimalClient.h
// 通过反射准备 RPC 参数并发送

FFuncReflection FuncRefl(PlayerStateObj, TEXT("UndoRemoveCardFromHandAtIndex"));
FVMReflection(FuncRefl.ParmsRefl)->*"CardData"->*"CardGuid"->*"A" = 1;

MinClient->SendRPCChecked(PlayerStateObj, FuncRefl);
```

### 进阶用法：作用域日志控制

```cpp
// Source/NetcodeUnitTest/Public/NUTUtilDebug.h
// 开启特定网络类别的详细日志
{
    FScopedLogNet LogScope(UnitTest, /*bRemoteLogging=*/false);
    // 此作用域内 LogNet、LogRep、LogNetTraffic 等类别全部开启
    DoSomeNetOperation();
}

// 自定义日志类别
{
    FScopedLog LogScope(TEXT("LogNetTraffic"), UnitTest);
    // 仅开启 LogNetTraffic
}

// 抑制特定日志
{
    FScopedLogSuppress SuppressScope(TEXT("LogNet"));
    // 此作用域内 LogNet 日志被抑制
}
```

### 进阶用法：Commandlet 自动化运行

```bash
# 源码参考: Source/NetcodeUnitTest/Classes/UnitTestCommandlet.h

# 运行所有网络单元测试
UnrealEditor.exe YourGame -run=NetcodeUnitTest.UnitTestCommandlet

# 只运行指定测试
UnrealEditor.exe YourGame -run=NetcodeUnitTest.UnitTestCommandlet -UnitTest=MyNetTest

# 带自定义服务器参数
UnrealEditor.exe YourGame -run=NetcodeUnitTest.UnitTestCommandlet -UnitTestServerParms="-LogCmds=\"LogNet all\""

# 限制并发测试数量
UnrealEditor.exe YourGame -run=NetcodeUnitTest.UnitTestCommandlet -UnitTestCap=4
```

## Demo 示例

一个完整的最小网络单元测试示例，测试服务端 RPC 的基本连通性：

```cpp
// MyPingTest.h
#pragma once

#include "CoreMinimal.h"
#include "ClientUnitTest.h"
#include "MyPingTest.generated.h"

UCLASS()
class UMyPingTest : public UClientUnitTest
{
    GENERATED_UCLASS_BODY()

    virtual void ExecuteClientUnitTest() override;

protected:
    virtual void NotifyProcessLog(TWeakPtr<FUnitTestProcess> InProcess,
                                   const TArray<FString>& InLogLines) override;
};
```

```cpp
// MyPingTest.cpp
#include "MyPingTest.h"
#include "MinimalClient.h"
#include "NUTActor.h"
#include "UnitLogging.h"

UMyPingTest::UMyPingTest()
{
    UnitTestName = TEXT("MyPingTest");
    UnitTestType = TEXT("Bug");
    UnitTestTimeout = 30;

    UnitTestFlags = EUnitTestFlags::LaunchServer
                  | EUnitTestFlags::RequirePlayerController
                  | EUnitTestFlags::RequireNUTActor;

    MinClientFlags = EMinClientFlags::AcceptActors;
}

void UMyPingTest::ExecuteClientUnitTest()
{
    Super::ExecuteClientUnitTest();

    UNIT_LOG(ELogType::StatusImportant, TEXT("发送 ping RPC 到服务端"));

    // 获取已复制的 NUTActor 并调用 ServerClientPing RPC
    if (UnitNUTActor.IsValid())
    {
        ANUTActor* NUTActor = UnitNUTActor.Get();
        NUTActor->ServerClientPing();
    }
    else
    {
        UNIT_LOG(ELogType::StatusFailure, TEXT("NUTActor 未就绪"));
        EndUnitTest();
    }
}

void UMyPingTest::NotifyProcessLog(TWeakPtr<FUnitTestProcess> InProcess,
                                     const TArray<FString>& InLogLines)
{
    Super::NotifyProcessLog(InProcess, InLogLines);

    for (const FString& Line : InLogLines)
    {
        if (Line.Contains(TEXT("NetMulticastPing")))
        {
            UNIT_LOG(ELogType::StatusSuccess, TEXT("成功收到 ping 响应"));
            EndUnitTest();
            return;
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit... | 视口相关重构，通知客户端关联/解除关联事件 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回退了 CL53913857 的改动 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit... | 视口相关重构（重复提交） |
| 2026-04-29 | `bef86caa` | Whitespace: followup to migrate UE_LOG to UE_LOGF: Restore newlines in multi-line format strings tha... | 将 UE_LOG 迁移到 UE_LOGF 后的格式修复 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符不匹配问题 |

### 维护评价

该插件创建于 2015 年，已有约 11 年历史，属于 Epic Games 内部网络代码测试基础设施的一部分。

**活跃度**：近期（2026年）仍有更新，但多为编译修复、格式迁移和全局重构，并非功能性的网络测试改进。这表明该插件处于**低频维护状态**——能持续编译通过，但已无新功能开发。

**使用限制**：
- 默认未启用（`EnabledByDefault: false`），需手动在项目中启用
- 仅支持 Win64 和 Linux 平台
- 模块类型为 `UncookedOnly`，仅在编辑器/开发构建中可用，打包版本不包含
- 代码中存在大量 `@todo` 注释，表明有许多未完成的计划功能
- 代码风格较老，包含较多 hack 和 workaround

**推荐**：适用于需要自动化回归测试 UE 网络代码的团队（特别是 Epic 内部）。对于一般项目，建议优先使用 UE 内置的 Automation Test 框架；仅当需要跨进程端到端网络测试时才考虑使用此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NetcodeUnitTest/NetcodeUnitTest)
```