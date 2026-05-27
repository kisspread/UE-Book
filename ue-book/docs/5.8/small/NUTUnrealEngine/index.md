# Netcode Unit Test - Unreal Engine

> Exploit unit tests for Unreal Engine and some base Unreal Engine games, based on the Netcode Unit Test framework

| 属性 | 值 |
|---|---|
| 中文名 | 网络代码单元测试引擎模块 |
| 分类 | Networking |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NUTUnrealEngine` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2021-03-23 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NetcodeUnitTest/NUTUnrealEngine) | |

## 用途

此插件是 **Netcode Unit Test** 框架的引擎层实现。它不是一个通用的网络功能插件，而是一个**开发和测试工具**。其核心用途是提供一组预定义的、针对 Unreal Engine 引擎本身及一些基础游戏（如 ShooterGame、QAGame）的**漏洞利用与边界条件单元测试**。

这些测试旨在：
1.  **复现历史漏洞**：如 `FTextCrash`（空 FText RPC 崩溃）和 `UTT61_DebugReplicateData`（数组溢出崩溃）。
2.  **验证网络边界**：如 `PacketLimitTest`，用于测试网络数据包大小限制、发送失败及边缘情况。
3.  **提供测试环境**：为 `ShooterGame`、`QAGame` 等特定项目配置默认测试地图和连接 URL。

**它解决的问题**：为引擎网络代码提供一个标准化的、可自动化的测试套件，用于在开发阶段早期发现网络相关的崩溃、漏洞和边界问题。

## 使用场景

- 你是 **Epic 内部或参与引擎开发的开发者**，需要运行和验证 Unreal Engine 的网络代码健壮性。
- 你在开发或测试一个**基于 Unreal 网络架构的游戏**，需要针对已知的引擎网络漏洞（如特定 RPC 崩溃、数据包处理问题）编写或运行防护性测试。
- 你需要为你的项目配置一个**标准化的网络测试环境**，需要参考 `ShooterGameEnvironment` 这样的模式来定义默认地图和连接参数。

**重要提示**：此插件 `EnabledByDefault` 为 `false`，且模块类型为 `UncookedOnly`，表明它**不包含在发布版本中**，是纯粹的开发/测试工具。

## 蓝图用法

此插件主要面向 C++ 开发者，**几乎没有公开的蓝图 API**。源码中未发现 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)`。其功能通过编写 C++ 测试用例来使用。

## C++ 用法

### 头文件引入

```cpp
#include "NUTUnrealEngine.h"
```

### 基本用法：编写一个网络单元测试

该插件的核心是提供了一系列继承自 `UClientUnitTest` 或 `UUnitTest` 的测试类。要使用，你需要基于这些基类创建自己的测试。

**示例：一个简单的测试类 (来自 `FTextCrash.h` 的简化模式)**
```cpp
// MyNetworkTest.h
#pragma once
#include "UnitTests/ClientUnitTest.h" // 或 UnitTests/UnitTest.h
#include "MyNetworkTest.generated.h"

UCLASS()
class UMyNetworkTest : public UClientUnitTest
{
    GENERATED_UCLASS_BODY()

public:
    virtual void InitializeEnvironmentSettings() override;
    virtual void ExecuteClientUnitTest() override;
    virtual void NotifyProcessLog(TWeakPtr<FUnitTestProcess> InProcess, const TArray<FString>& InLogLines) override;
};
```

```cpp
// MyNetworkTest.cpp
#include "MyNetworkTest.h"

UMyNetworkTest::UMyNetworkTest(const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer)
{
}

void UMyNetworkTest::InitializeEnvironmentSettings()
{
    // 在此配置测试环境，例如设置测试标志
    Super::InitializeEnvironmentSettings();
}

void UMyNetworkTest::ExecuteClientUnitTest()
{
    // 在此实现测试的核心逻辑
    // 例如：发送一个特殊的 RPC，触发特定的网络行为
}

void UMyNetworkTest::NotifyProcessLog(TWeakPtr<FUnitTestProcess> InProcess, const TArray<FString>& InLogLines)
{
    // 在此处理测试过程中服务器或客户端的日志输出，用于验证预期行为
}
```

### 进阶用法：注册自定义测试环境

参考 `FShooterGameEnvironment`，你可以为自己的项目注册特定的测试环境设置。

```cpp
#include "UnrealEngineEnvironment.h" // 包含基类 FUnitTestEnvironment

class FMyProjectEnvironment : public FUnitTestEnvironment
{
public:
    static void Register()
    {
        AddUnitTestEnvironment(TEXT("MyProjectName"), new FMyProjectEnvironment());
    }

    virtual FString GetDefaultMap(EUnitTestFlags UnitTestFlags) override
    {
        FString CurrentGame = FApp::GetProjectName();
        if (CurrentGame == TEXT("MyProjectName"))
        {
            return TEXT("MyTestMap");
        }
        return FUnitTestEnvironment::GetDefaultMap(UnitTestFlags);
    }
};
```

通常在模块启动时调用 `FMyProjectEnvironment::Register()`。

## Demo 示例

一个完整的、最小化的自定义网络单元测试示例。

**MySimpleTest.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "UnitTests/UnitTest.h"
#include "MySimpleTest.generated.h"

/**
 * 一个简单的自定义网络单元测试示例
 */
UCLASS()
class UMySimpleTest : public UUnitTest
{
    GENERATED_UCLASS_BODY()

public:
    /** 执行测试 */
    virtual bool ExecuteUnitTest() override;
};
```

**MySimpleTest.cpp**
```cpp
#include "MySimpleTest.h"

UMySimpleTest::UMySimpleTest(const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer)
{
}

bool UMySimpleTest::ExecuteUnitTest()
{
    // 这里是测试的核心逻辑
    // 例如，验证某个网络相关的条件或函数
    UE_LOG(LogTemp, Log, TEXT("MySimpleTest executed successfully!"));

    // 返回 true 表示测试通过，false 表示失败
    return true;
}
```

## 模块依赖

从 Build.cs 分析，此插件除了常见的引擎模块外，**唯一独特且必须的依赖**是：

| 模块 | 用途 |
|---|---|
| `NetcodeUnitTest` | 提供网络单元测试框架的基类、测试执行器和工具（如 `UUnitTest`, `UClientUnitTest`, `FUnitTestEnvironment` 等）。这是此插件存在的核心前提。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了 64 位整数在日志格式化字符串中的警告问题。 |
| 2024-11-06 | `bc63a88d` | Redirect old cppcompilewarning properties to new *.CppCompileWarningSettings | 将旧的编译器警告属性重定向到新的设置类，属于编译系统适配。 |
| 2023-11-01 | `e4faf8ba` | Enable truncation warnings in NetcodeUnitTest. | 在 NetcodeUnitTest 框架中启用了类型转换截断警告，提升代码严谨性。 |
| 2023-02-18 | `e599d19e` | Removing redundant Private includes. | 清理代码，移除冗余的 `#include` 语句。 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 一次针对引擎插件的通用性修改。 |

### 维护评价

- **状态**：**维护不活跃**。最近一次功能性更新在2026年4月，但内容是编译器警告修复，并非新测试用例或功能。实质性更新停留在2021-2023年。
- **频率**：更新非常稀疏，每年仅1-2次，且多为编译兼容性或代码清理。
- **推荐度**：**不推荐普通开发者主动使用**。此插件属于 Epic 内部的**测试基础设施**，用于保障引擎网络代码的质量。它依赖的 `NetcodeUnitTest` 框架本身也具有很高的专业性。除非你明确需要运行或扩展这套特定的引擎网络漏洞测试套件，否则无需关注。

## 相关链接

- [源码 (NUTUnrealEngine)](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NetcodeUnitTest/NUTUnrealEngine)
- [依赖框架 (NetcodeUnitTest)](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NetcodeUnitTest)