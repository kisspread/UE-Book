# Netcode Unit Test - Unreal Engine

> Exploit unit tests for Unreal Engine and some base Unreal Engine games, based on the Netcode Unit Test framework

| 属性 | 值 |
|---|---|
| 中文名 | UE网络漏洞测试 |
| 分类 | Networking |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NUTUnrealEngine` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2021-03-23 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NetcodeUnitTest/NUTUnrealEngine) | |

## 用途

这是一个基于 Netcode Unit Test 框架的网络漏洞测试插件，专门为 Unreal Engine 及一些基于 UE 的游戏（如 ShooterGame、QAGame、UnrealTournament）提供网络协议和包处理的漏洞单元测试。它的核心价值在于系统化地验证网络代码在极端情况下的健壮性，例如包大小边界、特定数据格式（如 FText）的序列化问题，以及特定游戏功能的调试数据同步问题。

## 使用场景

- **网络模块开发者**：当你在开发或修改 UE 的网络底层代码（如包处理、序列化、连接管理）时，用它来验证你的改动没有引入新的漏洞或回归问题。
- **游戏安全测试人员**：当你需要针对特定游戏（如 ShooterGame）的网络功能进行安全渗透测试时，可以利用此插件中预置的测试用例。
- **CI/CD 集成**：作为自动化测试流程的一部分，在提交网络相关代码前运行这些单元测试，确保网络栈的稳定性。

## 蓝图用法

此插件主要面向 C++ 测试，不直接提供蓝图节点。其测试用例通过 Unreal Automation 框架执行，通常以命令行或编辑器内自动化测试面板触发。

## C++ 用法

该插件提供了多个继承自 `UClientUnitTest` 或 `UUnitTest` 的测试类，每个类封装了一个具体的网络漏洞测试场景。

### 头文件引入

```cpp
#include "NUTUnrealEngine.h"
```

### 基本用法

该插件的主要用途是运行其内置的测试用例。你可以直接在编辑器中启用插件，然后通过 **Session Frontend → Automation** 面板运行包含 “NUT” 前缀的测试。

作为开发者，你更可能需要阅读和扩展这些测试。以下是一个测试类的基本结构（来自 `PacketLimitTest.h`）：

```cpp
// 文件: Engine/Plugins/NetcodeUnitTest/NUTUnrealEngine/Classes/UnitTests/PacketLimitTest.h
UCLASS()
class UPacketLimitTest : public UClientUnitTest
{
    GENERATED_UCLASS_BODY()

protected:
    bool bUseOodle;
    ELimitTestStage TestStage;
    int32 LastSocketSendSize;
    int32 TargetSocketSendSize;

public:
    // 初始化测试环境（如选择默认地图）
    virtual void InitializeEnvironmentSettings() override;
    
    // 验证测试设置
    virtual bool ValidateUnitTestSettings(bool bCDOCheck) override;
    
    // 执行客户端单元测试的核心逻辑
    virtual void ExecuteClientUnitTest() override;
    
    // 钩子：在发送原始数据包前被调用，可以阻止发送
    virtual void NotifySendRawPacket(void* Data, int32 Count, bool& bBlockSend) override;
    
    // 钩子：在Socket层发送原始数据包前被调用
    virtual void NotifySocketSendRawPacket(void* Data, int32 Count, bool& bBlockSend) override;
    
    // 处理测试进程的日志输出，用于判断测试状态
    virtual void NotifyProcessLog(TWeakPtr<FUnitTestProcess> InProcess, const TArray<FString>& InLogLines) override;

protected:
    // 前进到下一个测试阶段
    void NextTestStage();
};
```

### 进阶用法

要运行一个特定的漏洞测试（例如测试 FText 在 RPC 中为空时的崩溃），你需要找到对应的测试类（如 `UFTextCrash`）并了解其设置。通常，测试会自动完成初始化，但你可以通过继承和覆盖方法来自定义测试环境。

```cpp
// 模拟：运行一个自定义的网络漏洞测试
// 1. 确保 NetcodeUnitTest 和 NUTUnrealEngine 插件已启用。
// 2. 在自动化测试框架中注册你的测试（如果需要扩展）。
// 3. 通过控制台命令或自动化测试面板触发测试。

// 示例：查看内置测试的执行命令（通常在测试类的 .cpp 中有注释）
// 例如，UUTT61_DebugReplicateData 的注释中提到命令: UTT -b 61 127.0.0.1
```

## Demo 示例

此插件不提供常规的 Demo 项目，它的“示例”就是其内部包含的单元测试类本身。以下是一个理解测试类结构的最小示例头文件，展示了一个自定义测试的骨架：

```cpp
// MyCustomNetVulnerabilityTest.h
#pragma once

#include "CoreMinimal.h"
#include "UnitTests/ClientUnitTest.h"
#include "MyCustomNetVulnerabilityTest.generated.h"

UCLASS()
class UMyCustomNetVulnerabilityTest : public UClientUnitTest
{
    GENERATED_UCLASS_BODY()

public:
    /** 测试初始化：设置默认地图和客户端连接URL */
    virtual void InitializeEnvironmentSettings() override;

    /** 执行测试：触发漏洞场景 */
    virtual void ExecuteClientUnitTest() override;

    /** 处理日志：分析服务器或客户端的输出，判断测试是否通过/失败 */
    virtual void NotifyProcessLog(TWeakPtr<FUnitTestProcess> InProcess, const TArray<FString>& InLogLines) override;
};
```

对应的实现文件（.cpp）需要在构造函数中设置测试的唯一名称、描述和标志，并重写上述虚函数来实现具体的测试逻辑。

## 模块依赖

从插件的 .uplugin 和模块结构推断，它依赖于核心的测试框架。

| 模块 | 用途 |
|---|---|
| `NetcodeUnitTest` | 核心的网络单元测试框架，提供 `UClientUnitTest` 等基类 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了格式说明符与64位参数不匹配的编译警告或潜在错误。 |
| 2024-11-06 | `bc63a88d` | Redirect old cppcompilewarning properties to new *.CppCompileWarningSettings | 适应引擎新的编译警告配置系统。 |
| 2023-11-01 | `e4faf8ba` | Enable truncation warnings in NetcodeUnitTest. | 在关联的框架中启用了数据截断警告，提升代码严谨性。 |
| 2023-02-18 | `e599d19e` | Removing redundant Private includes. | 清理代码，移除多余的头文件包含。 |

### 维护评价

该插件是一个**专用的开发和测试工具**，而非面向最终用户的功能插件。其最近的更新主要是维护性工作（修复编译警告、适应新版本特性、代码清理），而非新功能开发。这符合其“测试工具”的定位——只要它依赖的框架和引擎底层没有破坏性变更，它就能持续工作。

- **年龄**：约 5 年，属于较新但稳定的工具。
- **活跃度**：维护不活跃，但偶尔有适配性更新。
- **推荐使用**：如果你在进行 UE 网络代码的安全性或健壮性测试，此插件及其依赖的框架是宝贵的资源库。对于普通的游戏开发项目，则无需启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NetcodeUnitTest/NUTUnrealEngine)
- [官方文档]() (无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NetcodeUnitTest/NUTUnrealEngine/Classes/UnitTests)