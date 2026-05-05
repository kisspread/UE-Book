# Netcode Unit Test

> A unit testing framework for testing the Unreal Engine netcode, primarily for bugs and exploits

| 属性 | 值 |
|---|---|
| 分类 | Networking |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NetcodeUnitTest` (UncookedOnly), `NUTUnrealEngine` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2015-05-05 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/NetcodeUnitTest) | |

## 用途

NetcodeUnitTest 是 Epic Games 内部开发的网络代码单元测试框架，专门用于测试 Unreal Engine 网络层的 bug 和安全漏洞。与 UE 内置的自动化测试框架不同，这个插件提供了一套完整的网络测试基础设施，包括：

- **MinimalClient**：轻量级的网络客户端实现，可以独立创建 UWorld/UNetDriver/UNetConnection，无需启动完整游戏客户端即可进行网络测试
- **NUTActor**：服务器端 Actor，通过自定义控制通道消息与测试客户端通信，支持在服务器上执行测试逻辑
- **UnitTestManager**：集中管理测试的排队、执行、资源限制和日志记录
- **VM Reflection Helper**：完全通过反射访问 UScript/Blueprint 虚拟机，无需静态引用任何类，保持跨版本兼容性

该插件的设计目标是：能够在不依赖特定游戏代码的情况下，系统性地测试网络代码的各种边界情况和潜在漏洞。

## 使用场景

- 你需要测试 UE 网络复制代码是否存在溢出/截断问题 → 用 PacketLimitTest
- 你需要验证 WebSocket 客户端连接是否正常 → 用 WebSocketClient 测试
- 你需要测试 Steam 网络后端的连接流程 → 用 SteamClient 测试
- 你需要编写自定义的网络漏洞/bug 测试，复现并验证修复 → 继承 UClientUnitTest
- 你需要在 CI/CD 中批量运行网络相关测试 → 用 UnitTestCommandlet
- 你需要测试 IP 网络驱动的基本连接功能 → 用 IPClient 测试

## 蓝图用法

此插件不提供蓝图接口。所有功能均通过 C++ 实现。

## C++ 用法

### 核心概念

#### 类继承体系

```
UUnitTestBase              ← 基础 tick 框架
  └─ UUnitTest             ← 单元测试基类（名称、类型、超时、验证状态）
      └─ UProcessUnitTest  ← 管理子进程（启动服务器/客户端进程、日志收集、崩溃检测）
          └─ UClientUnitTest ← 网络客户端测试（MinimalClient 集成、RPC 控制、Actor 管理）
```

#### 关键组件

| 组件 | 说明 |
|---|---|
| `UUnitTestManager` | 全局单例，管理测试排队、执行、资源限制、日志窗口 |
| `UMinimalClient` | 轻量级网络客户端，创建独立的 UWorld/UNetDriver/UNetConnection |
| `ANUTActor` | 服务器端 Actor，通过自定义 NMT_NUTControl 消息与客户端通信 |
| `UUnitTask` | 用于在测试执行前完成复杂设置（如游戏认证流程） |
| `FUnitTestEnvironment` | 每个游戏的环境配置（默认地图、服务器参数、进度日志等） |
| `FVMReflection` | UScript/Blueprint VM 反射助手，通过名称访问任何属性/函数 |

### 头文件引入

```cpp
#include "NetcodeUnitTest.h"
#include "UnitTest.h"
#include "ClientUnitTest.h"
#include "MinimalClient.h"
#include "NUTActor.h"
#include "NUTEnum.h"
#include "UnitTask.h"
```

### 编写一个基本的网络单元测试

所有网络单元测试继承自 `UClientUnitTest`，并在构造函数中配置测试元数据和标志：

```cpp
// MyExploitTest.h
#pragma once

#include "CoreMinimal.h"
#include "ClientUnitTest.h"
#include "MyExploitTest.generated.h"

UCLASS()
class UMyExploitTest : public UClientUnitTest
{
    GENERATED_UCLASS_BODY()

protected:
    virtual void InitializeEnvironmentSettings() override;
    virtual void ExecuteClientUnitTest() override;
    virtual void NotifyProcessLog(TWeakPtr<FUnitTestProcess> InProcess,
                                  const TArray<FString>& InLogLines) override;
};
```

```cpp
// MyExploitTest.cpp
#include "MyExploitTest.h"

UMyExploitTest::UMyExploitTest(const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer)
{
    // 测试元数据
    UnitTestName = TEXT("MyExploitTest");
    UnitTestType = TEXT("Exploit");
    UnitTestDate = FDateTime(2024, 1, 15);

    // 配置测试标志：启动服务器、接受 PlayerController、等待 Pawn 就绪
    UnitTestFlags = EUnitTestFlags::LaunchServer
                  | EUnitTestFlags::AcceptPlayerController
                  | EUnitTestFlags::RequirePawn;

    // 配置 MinimalClient 标志：接受 Actor、接受 RPC、通知网络事件
    MinClientFlags = EMinClientFlags::AcceptActors
                   | EMinClientFlags::AcceptRPCs
                   | EMinClientFlags::NotifyProcessNetEvent;

    // 超时时间（秒）
    UnitTestTimeout = 60;

    // 预期结果：指定每个游戏的预期验证状态
    ExpectedResult.Add(TEXT("NullUnitEnv"), EUnitTestVerification::VerifiedNotFixed);
}

void UMyExploitTest::InitializeEnvironmentSettings()
{
    Super::InitializeEnvironmentSettings();
    // 可选：覆盖默认服务器/客户端 URL 和参数
}

void UMyExploitTest::ExecuteClientUnitTest()
{
    Super::ExecuteClientUnitTest();

    // 在此处编写测试逻辑
    // 此时 MinimalClient 已连接，PlayerController 和 Pawn 已就绪

    // 例如：发送自定义 RPC 到服务器
    SendUnitRPCChecked(TEXT("MyServerFunction"));
}

void UMyExploitTest::NotifyProcessLog(TWeakPtr<FUnitTestProcess> InProcess,
                                       const TArray<FString>& InLogLines)
{
    Super::NotifyProcessLog(InProcess, InLogLines);

    // 根据服务器日志判断测试结果
    for (const FString& LogLine : InLogLines)
    {
        if (LogLine.Contains(TEXT("Exploit succeeded")))
        {
            // 标记为已验证（问题未修复）
            VerificationState = EUnitTestVerification::VerifiedNotFixed;
            EndUnitTest();
        }
    }
}
```

### EUnitTestFlags 配置指南

| 标志 | 说明 |
|---|---|
| `LaunchServer` | 自动启动一个游戏服务器进程（当前必须设置） |
| `LaunchClient` | 自动启动一个完整游戏客户端 |
| `AcceptPlayerController` | 接受 PlayerController 的创建 |
| `RequirePlayerController` | 等待 PlayerController 就绪后再执行 |
| `RequirePawn` | 等待 PlayerController 的 Pawn 就绪 |
| `RequirePlayerState` | 等待 PlayerState 就绪 |
| `RequireNUTActor` | 等待 NUTActor 复制完成 |
| `RequireBeacon` | 等待 Beacon 复制完成 |
| `ExpectServerCrash` | 预期服务器会崩溃（不影响测试结果） |
| `ExpectDisconnect` | 预期会断开连接 |
| `CaptureReceivedRaw` | 捕获原始接收数据包 |
| `NotifyProcessEvent` | 启用 NotifyProcessEvent 回调 |

### EMinClientFlags 配置指南

| 标志 | 说明 |
|---|---|
| `AcceptActors` | 接受 Actor 通道（配合 `NotifyAllowNetActor` 白名单使用） |
| `AcceptRPCs` | 接受执行 Actor RPC（默认全部阻止） |
| `SendRPCs` | 允许发送 RPC |
| `AcceptRepNotifies` | 接受执行 RepNotify |
| `SkipControlJoin` | 跳过发送 NMT_Join |
| `BeaconConnect` | 连接到服务器的 Beacon（限制连接） |
| `NotifyNetActors` | Actor 创建后触发通知 |
| `NotifyProcessNetEvent` | 每个客户端 RPC 函数触发通知 |
| `DumpReceivedRaw` | 十六进制转储接收到的原始数据包 |
| `DumpSendRaw` | 十六进制转储发送的原始数据包 |

### UnitTask 系统

UnitTask 用于在测试执行前完成复杂的共享设置逻辑（如游戏认证）：

```cpp
UCLASS()
class UMyAuthTask : public UUnitTask
{
    GENERATED_UCLASS_BODY()

public:
    virtual void Attach(UUnitTest* InOwner) override;
    virtual void StartTask() override;
    virtual bool IsTaskComplete() override;
    virtual void Cleanup() override;
};

// 构造函数中设置标志
UMyAuthTask::UMyAuthTask(const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer)
{
    UnitTaskFlags = EUnitTaskFlags::RequireServer
                  | EUnitTaskFlags::BlockMinClient;
}
```

### VM Reflection Helper

`FVMReflection` 通过名称字符串访问任何 UE 属性，无需静态依赖：

```cpp
#include "NUTUtilReflection.h"

// 访问对象属性
bool bError = false;
FString Result = (FString)(FVMReflection(MyObject)->*"MyStringProperty", &bError);

// 访问数组元素
int32 Value = (int32)(FVMReflection(MyObject)->*"IntArrayProp", &bError)[0];

// 访问结构体
FVector Location = *(FVector*)(void*)(FVMReflection(MyObject)->*"LocationProp",
                                      &bError)[FVector::StaticStruct()];
```

### 运行测试

#### 通过控制台命令

```
UnitTest MyExploitTest
```

#### 通过 Commandlet（CI/CD 推荐）

```bash
UnrealEditor.exe MyGame -run=NetcodeUnitTest.UnitTestCommandlet -UnitTest=MyExploitTest
```

Commandlet 参数：
- `-UnitTest=Name` — 只运行指定测试
- `-UnitTestNoAutoClose` — 禁用自动关闭
- `-UnitTestServerParms="..."` — 附加服务器参数
- `-UnitTestClientParms="..."` — 附加客户端参数
- `-UnitTestClientDebug` — 启用客户端调试窗口
- `-UnitTestCap=x` — 最大并发测试数

#### 通过自动化测试

框架自动注册为 `System.Netcode Unit Test` 下的自动化测试，可在编辑器自动化测试面板中运行。

## Demo 示例

### 最小的网络单元测试

**头文件** — `Classes/MyNetworkTest.h`：

```cpp
#pragma once
#include "ClientUnitTest.h"
#include "MyNetworkTest.generated.h"

UCLASS()
class UMyNetworkTest : public UClientUnitTest
{
    GENERATED_UCLASS_BODY()
public:
    virtual void ExecuteClientUnitTest() override;
    virtual void NotifyProcessLog(TWeakPtr<FUnitTestProcess> InProcess,
                                  const TArray<FString>& InLogLines) override;
};
```

**实现文件** — `Private/MyNetworkTest.cpp`：

```cpp
#include "MyNetworkTest.h"

UMyNetworkTest::UMyNetworkTest(const FObjectInitializer& OI) : Super(OI)
{
    UnitTestName = TEXT("MyNetworkTest");
    UnitTestType = TEXT("Bug");
    UnitTestDate = FDateTime::Now();
    UnitTestTimeout = 30;

    UnitTestFlags = EUnitTestFlags::LaunchServer
                  | EUnitTestFlags::AcceptPlayerController
                  | EUnitTestFlags::RequirePawn;

    MinClientFlags = EMinClientFlags::AcceptActors
                   | EMinClientFlags::AcceptRPCs
                   | EMinClientFlags::NotifyProcessNetEvent;

    ExpectedResult.Add(TEXT("NullUnitEnv"), EUnitTestVerification::VerifiedFixed);
}

void UMyNetworkTest::ExecuteClientUnitTest()
{
    Super::ExecuteClientUnitTest();
    // 测试逻辑写在这里
    ResetTimeout(TEXT("Test started"));
}

void UMyNetworkTest::NotifyProcessLog(TWeakPtr<FUnitTestProcess> InProcess,
                                       const TArray<FString>& InLogLines)
{
    Super::NotifyProcessLog(InProcess, InLogLines);
    for (const FString& Line : InLogLines)
    {
        if (Line.Contains(TEXT("Expected result")))
        {
            VerificationState = EUnitTestVerification::VerifiedFixed;
            EndUnitTest();
        }
    }
}
```

**Build.cs 依赖**：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core", "CoreUObject", "Engine", "NetcodeUnitTest"
});
```

## 模块依赖

### NetcodeUnitTest 模块

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、容器、日志 |
| `CoreUObject` | UObject 系统、反射 |
| `Engine` | 引擎核心（NetDriver、NetConnection、Actor） |
| `Sockets` | 网络 Socket 操作 |
| `ApplicationCore` | 平台应用核心（私有） |
| `EngineSettings` | 引擎配置（私有） |
| `InputCore` | 输入系统（私有） |
| `PacketHandler` | 数据包处理器（私有） |
| `RenderCore` | 渲染核心（私有） |
| `Slate` / `SlateCore` | UI 框架（私有，用于日志窗口） |
| `NetCore` | 网络核心（私有） |
| `StandaloneRenderer` | 独立渲染器（仅非单体构建） |

### NUTUnrealEngine 模块

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `NetcodeUnitTest` | 本插件核心框架 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-07-18 | `462ec4ed` | 修复 V623 静态分析警告：三元运算符临时对象问题 |
| 2025-07-15 | `35e62d59` | 修复/静默 V530 未处理返回值警告 |
| 2025-06-16 | `e29a7072` | 修复非 Unity 构建编译错误（缺少 StrProperty.h 头文件） |

### 维护评价

⚠️ **维护不活跃** — 此插件的近期更新仅涉及编译警告修复和构建兼容性调整，没有功能性更新。从 commit 历史来看，这是一个长期存在的内部工具，由 Epic Games 在需要时维护。

**综合评价**：

- 创建于 2015 年，已有 11 年历史
- 仅支持 Win64 和 Linux 平台
- `EnabledByDefault = false`，需要手动启用
- 代码中存在大量 `@todo` 注释，表明仍有计划中的重构（特别是 MinimalClient 的重构）
- 框架本身设计完善，适合编写网络漏洞/bug 测试
- 不推荐作为通用单元测试框架使用，仅适用于网络代码测试场景

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/NetcodeUnitTest)
- 官方文档：无
