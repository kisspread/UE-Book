# Netcode Unit Test - Unreal Engine

> Exploit unit tests for Unreal Engine and some base Unreal Engine games, based on the Netcode Unit Test framework

| 属性 | 值 |
|---|---|
| 中文名 | 网络漏洞测试 |
| 分类 | Networking |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NUTUnrealEngine` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2021-03-23 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NetcodeUnitTest/NUTUnrealEngine) | |

## 用途

本插件并非通用功能插件，而是 **Epic Games 内部用于网络协议安全测试的专用工具库**。它基于 `NetcodeUnitTest` 框架，提供了针对 Unreal Engine 本身（如网络序列化、RPC 机制）以及一些内部示例游戏项目（如 `ShooterGame`、`QAGame`）的**已知网络漏洞或边界条件的单元测试用例**。

其核心目的是：
1.  **漏洞复现与验证**：为历史上发现的网络协议相关崩溃或安全问题（如 FText RPC 崩溃、Packet 大小边界、数组溢出）提供精确的自动化复现步骤。
2.  **回归测试**：确保引擎网络栈的改动不会引入已知问题的回归。
3.  **内部游戏集成**：为特定内部游戏项目提供预配置的测试环境和默认地图。

## 使用场景

- 你是 **Epic 内部的安全或网络引擎工程师**，需要验证针对 Unreal 网络协议的攻击或边界情况的修复是否有效。
- 你在进行 **网络协议栈的深度开发或重构**，需要一套现成的、针对历史问题的测试用例来进行回归测试。
- 你在研究 **Unreal 网络安全性**，希望了解已知的漏洞模式及其复现方法。

## 蓝图用法

本插件不包含面向游戏逻辑的公开蓝图接口。其所有功能均为 C++ 测试类和底层环境设置。

## C++ 用法

### 头文件引入

```cpp
#include "NUTUnrealEngine.h"
```

### 基本用法：注册自定义测试环境

本插件允许为特定的项目或游戏配置默认的测试地图。你可以通过继承 `FUnitTestEnvironment` 来实现。

**来源文件**: `Source/NUTUnrealEngine/Public/UnrealEngineEnvironment.h`

```cpp
#include "UnitTestEnvironment.h"

// 为你的项目“MyGame”创建一个测试环境
class FMyGameEnvironment : public FUnitTestEnvironment
{
public:
    static void Register()
    {
        AddUnitTestEnvironment(TEXT("MyGame"), new FMyGameEnvironment());
    }

    // 为你的项目指定一个专门用于网络测试的默认地图
    virtual FString GetDefaultMap(EUnitTestFlags UnitTestFlags) override
    {
        FString ReturnVal = FUnitTestEnvironment::GetDefaultMap(UnitTestFlags);
        if (FApp::GetProjectName() == TEXT("MyGame"))
        {
            ReturnVal = TEXT("NetTestMap");
        }
        return ReturnVal;
    }
};
```

### 进阶用法：复现网络漏洞

插件中的单元测试类（如 `UPacketLimitTest`）展示了如何使用 `NetcodeUnitTest` 框架来精确控制网络交互并验证边界条件。

**来源文件**: `Source/NUTUnrealEngine/Classes/UnitTests/PacketLimitTest.h`

```cpp
#include "ClientUnitTest.h"

// 示例：一个测试网络数据包大小限制的单元测试
// 它会拦截发送到 Socket 的原始数据包，并阻止不符合预期大小的包发送
class UPacketLimitTest : public UClientUnitTest
{
protected:
    // 重写此函数以实现对原始网络包发送的拦截和逻辑判断
    virtual void NotifySocketSendRawPacket(void* Data, int32 Count, bool& bBlockSend) override
    {
        // 计算当前数据包大小
        int32 CurrentPacketSize = CalculatePacketSize(Data, Count);

        // 如果当前大小不等于目标测试大小，则阻止发送
        if (CurrentPacketSize != TargetSocketSendSize)
        {
            bBlockSend = true; // 阻止这个包发送
            UE_LOG(LogNet, Warning, TEXT("Blocked packet with size %d, target is %d"), CurrentPacketSize, TargetSocketSendSize);
        }
        // 否则，允许发送（bBlockSend 保持默认的 false）
    }

public:
    // 执行测试逻辑，按阶段推进测试
    virtual void ExecuteClientUnitTest() override
    {
        // 初始化测试阶段...
        NextTestStage();
    }
};
```

## Demo 示例

以下示例演示了如何为一个自定义项目 `“MyGame”` 创建并注册一个简单的测试环境。

**MyGameTestEnvironment.h**
```cpp
#pragma once
#include "UnitTestEnvironment.h"

class FMyGameTestEnvironment : public FUnitTestEnvironment
{
public:
    static void Register();

    virtual FString GetDefaultMap(EUnitTestFlags UnitTestFlags) override;
    virtual FString GetDefaultClientConnectURL() override;
};
```

**MyGameTestEnvironment.cpp**
```cpp
#include "MyGameTestEnvironment.h"

void FMyGameTestEnvironment::Register()
{
    AddUnitTestEnvironment(TEXT("MyGame"), new FMyGameTestEnvironment());
}

FString FMyGameTestEnvironment::GetDefaultMap(EUnitTestFlags UnitTestFlags)
{
    // 获取基础默认地图
    FString BaseMap = FUnitTestEnvironment::GetDefaultMap(UnitTestFlags);
    // 仅在当前项目为 MyGame 时覆盖
    if (FApp::GetProjectName() == TEXT("MyGame"))
    {
        // 返回你专门为网络测试准备的地图名称
        return TEXT("/Game/Maps/NetworkTestLevel");
    }
    return BaseMap;
}

FString FMyGameTestEnvironment::GetDefaultClientConnectURL()
{
    FString BaseURL = FUnitTestEnvironment::GetDefaultClientConnectURL();
    // 可以为特定项目追加连接参数，例如版本检查
    if (FApp::GetProjectName() == TEXT("MyGame"))
    {
        BaseURL += TEXT("?MyGameParam=1");
    }
    return BaseURL;
}
```

**使用（在模块启动时注册）**:
```cpp
#include "MyGameTestEnvironment.h"

void FMyGameModule::StartupModule()
{
    FMyGameTestEnvironment::Register();
}
```

## 模块依赖

本插件自身依赖于 `NetcodeUnitTest` 框架。如果你想在自己的模块中使用或扩展本插件的测试环境或测试用例，你需要：

| 模块 | 用途 |
|---|---|
| `NetcodeUnitTest` | 核心的网络单元测试框架，提供 `UUnitTest`、`FUnitTestEnvironment` 等基类和工具。 |
| `NUTUnrealEngine` | 本插件模块，包含针对 UE 及特定游戏的测试实现和环境设置。 |

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了日志输出中 32/64 位格式说明符不匹配的问题。 |
| 2024-11-06 | `bc63a88d` | Redirect old cppcompilewarning properties to new *.CppCompileWarningSettings | 更新了编译器警告设置的属性，以适配新的项目设置结构。 |
| 2023-11-01 | `e4faf8ba` | Enable truncation warnings in NetcodeUnitTest. | 启用了 NetcodeUnitTest 中的截断警告，提升代码健壮性。 |
| 2023-02-18 | `e599d19e` | Removing redundant Private includes. | 清理了冗余的私有头文件包含，简化依赖。 |

### 维护评价

- **创建时间**：2021年3月，作为从 UE4 迁移到 UE5 的一部分（基于首次 commit 信息）。
- **更新频率**：最近一次实质性（非编译修复）更新在 **2023年11月**。之后的更新主要是编译器兼容性和代码清理，没有新的测试用例或功能添加。
- **活跃度**：**维护不活跃**。该插件更像一个历史测试用例的存档库，而非活跃开发的功能模块。
- **已知问题/限制**：
    1.  `EnabledByDefault: false`，且 `Installed: false`，表明这是一个需要手动启用的、非常特殊的插件。
    2.  `UncookedOnly` 类型，意味着它**仅在编辑器和未打包的开发版本中可用**，不会包含在最终发布的游戏中。
    3.  包含一些标记为 `Obsolete` 的测试类（如 `UUTT61_DebugReplicateData`）。
- **推荐使用**：**不推荐**普通开发者用于生产项目。它是 Epic 内部网络协议安全测试和引擎验证流程的一部分。对于大多数开发者，其价值在于**参考和学习**如何为 Unreal 网络协议编写深度的、可复现漏洞的单元测试。如果你需要测试自己的网络游戏，应使用 `NetcodeUnitTest` 框架编写自己的测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NetcodeUnitTest/NUTUnrealEngine)