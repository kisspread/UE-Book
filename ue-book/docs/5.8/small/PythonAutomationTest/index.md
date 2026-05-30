# Python Automation Test

> 

| 属性 | 值 |
|---|---|
| 中文名 | Python 自动化测试 |
| 分类 | Testing |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源、示例脚本） |
| 模块 | `PythonAutomationTest` (Editor) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2019-09-17 |
| 年龄标签 | 🏛️ 文物（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/PythonAutomationTest) | |

## 用途

这个插件为 Unreal Engine 的自动化测试框架（Gauntlet 或其他）提供了一个与 **Python** 脚本进行集成的桥梁。它本身不包含测试用例，而是提供了一套蓝图和 C++ 接口，用于在自动化测试流程中**启动、监控和管理 Python 潜命令（Latent Command）的执行状态**。它解决的核心问题是：如何将 Python 脚本作为自动化测试的一个步骤，并将其执行状态与 UE 的测试框架同步。

## 使用场景

- 你在编写复杂的自动化测试，其中某些步骤（如生成特定资产、验证文件结构）用 Python 脚本实现更方便。→ 使用此插件来包装你的 Python 脚本，使其能作为测试命令被 UE 测试框架识别和管理。
- 你需要一个 Python 脚本在测试过程中异步运行，测试框架需要等待其完成或超时。→ 使用此插件提供的 `SetIsRunningPyLatentCommand` 和 `GetIsRunningPyLatentCommand` 来管理异步状态。
- 你在使用 Unreal 的 Python 自动化测试框架，并需要自定义潜命令的超时时间。→ 使用 `SetPyLatentCommandTimeout`。

## 蓝图用法

### 核心节点

该插件主要提供了一个蓝图函数库 `UPyAutomationTestLibrary`，包含以下核心节点：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Is Running Py Latent Command` | 设置 Python 潜命令是否正在运行的状态标记。 | `UPyAutomationTestLibrary` |
| `Get Is Running Py Latent Command` | 获取当前 Python 潜命令是否正在运行的状态标记。 | `UPyAutomationTestLibrary` |
| `Set Py Latent Command Timeout` | 设置 Python 潜命令的超时时间（秒）。 | `UPyAutomationTestLibrary` |
| `Get Py Latent Command Timeout` | 获取当前设置的 Python 潜命令超时时间（秒）。 | `UPyAutomationTestLibrary` |
| `Reset Py Latent Command` | 重置潜命令状态，通常将“正在运行”标记为 false。 | `UPyAutomationTestLibrary` |

### 使用示例（蓝图描述）

在蓝图测试逻辑中，你可以这样组织：
1.  在启动一个 Python 潜命令（例如通过 `Python Editor Script Plugin` 执行一个脚本）之前，调用 `Set Is Running Py Latent Command` 并传入 `True`。
2.  （可选）根据需要调用 `Set Py Latent Command Timeout` 来设置一个合理的等待时间。
3.  潜命令（Python 脚本）在后台执行。
4.  在一个循环或潜命令节点中，持续调用 `Get Is Running Py Latent Command` 来检查 Python 脚本是否已完成（返回 `False`）。结合 `Get Py Latent Command Timeout` 来判断是否超时。
5.  当 Python 脚本完成（其内部逻辑应调用 `Set Is Running Py Latent Command (False)` 或外部脚本管理器调用它），测试框架即可得知该步骤结束，继续后续测试逻辑。

## C++ 用法

### 头文件引入

```cpp
#include "PythonAutomationTest.h"
```

### 基本用法

此插件主要提供全局静态函数来管理测试状态。以下是一个简化的 C++ 测试用例逻辑示例。

```cpp
// 假设在一个自动化测试类中
#include "PythonAutomationTest.h"
#include "Misc/AutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FPythonLatentCommandTest,
    "Project.Python.Integration.LatentCommand",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FPythonLatentCommandTest::RunTest(const FString& Parameters)
{
    // 1. 重置状态
    UPyAutomationTestLibrary::ResetPyLatentCommand();

    // 2. 设置一个超时，例如 10 秒
    UPyAutomationTestLibrary::SetPyLatentCommandTimeout(10.0f);

    // 3. 假设这里启动了一个 Python 脚本作为潜命令...
    // ... (启动脚本的代码)
    UPyAutomationTestLibrary::SetIsRunningPyLatentCommand(true);

    // 4. 模拟等待潜命令完成（实际使用可能需要在 Tick 中检查）
    const float StartTime = FPlatformTime::Seconds();
    while (UPyAutomationTestLibrary::GetIsRunningPyLatentCommand())
    {
        // 检查超时
        if (FPlatformTime::Seconds() - StartTime > UPyAutomationTestLibrary::GetPyLatentCommandTimeout())
        {
            AddError(TEXT("Python latent command timed out!"));
            return false; // 测试失败
        }
        // 等待一小段时间，避免忙等待
        FPlatformProcess::Sleep(0.1f);
    }

    // 5. 潜命令完成，测试继续
    AddInfo(TEXT("Python latent command completed successfully."));
    return true; // 测试通过
}
```

**来源**: 基于 `Public/PythonAutomationTest.h` 中的 API 推断的标准测试用法。

### 进阶用法

更复杂的场景可能涉及自定义的 Python 潜命令节点，该节点内部会利用这些库函数来正确报告其状态给 UE 测试框架，确保测试的阻塞、超时和错误处理机制能正常工作。

## Demo 示例

一个使用此插件库的最小 C++ 类示例头文件（`.cpp` 实现类似上面的 `RunTest`）：

```cpp
// PythonLatentCommandDemo.h
#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "PythonLatentCommandDemo.generated.h"

UCLASS()
class UPythonLatentCommandDemo : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    /** 演示如何使用 PythonAutomationTest 库来管理一个模拟的 Python 潜命令。 */
    UFUNCTION(BlueprintCallable, Category = "Demo")
    static void RunDemoPythonLatentCommand();
};
```

```cpp
// PythonLatentCommandDemo.cpp
#include "PythonLatentCommandDemo.h"
#include "PythonAutomationTest.h"
#include "Misc/AutomationTest.h"

void UPythonLatentCommandDemo::RunDemoPythonLatentCommand()
{
    // 这是一个蓝图可调用的演示函数
    UE_LOG(LogTemp, Warning, TEXT("Resetting and starting a demo Python latent command..."));
    UPyAutomationTestLibrary::ResetPyLatentCommand();
    UPyAutomationTestLibrary::SetPyLatentCommandTimeout(5.0f);
    UPyAutomationTestLibrary::SetIsRunningPyLatentCommand(true);

    // 在实际应用中，这里会启动一个真正的 Python 脚本。
    // 为了演示，我们创建一个定时器在 3 秒后模拟命令完成。
    FTimerHandle TimerHandle;
    GWorld->GetTimerManager().SetTimer(TimerHandle, [TimerHandle]()
    {
        UPyAutomationTestLibrary::SetIsRunningPyLatentCommand(false);
        UE_LOG(LogTemp, Warning, TEXT("Demo Python latent command finished."));
    }, 3.0f, false);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AutomationTest` | UE 自动化测试框架的核心模块，提供测试基类和宏。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-05-31 | `2739c3d3` | Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of ty | 代码格式化，统一 DLL 导出声明风格。 |
| 2024-11-10 | `66e9bb39` | Removed all #if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes from the code base | 清理旧版本兼容性代码，简化头文件。 |
| 2023-06-13 | `06817dd8` | Avoid looking for tests in pluting content python site-packages folder | 修复了在插件内容目录的 Python site-packages 文件夹中错误查找测试的 bug。 |
| 2023-05-11 | `91c57d39` | Removed redundant module includes. | 移除多余的模块包含，清理代码。 |
| 2023-01-13 | `3c9aacb1` | [Engine/Plugins] | 批量插件目录重构。 |

### 维护评价

该插件创建于 2019 年，**最近一次实质性功能/修复更新停留在 2023 年中（避免错误查找测试）**。2024 和 2025 年的更新均属于底层代码维护和兼容性修复，未增加新功能。作为 Epic 官方内部测试工具，它可能仅在需要时被动维护，**活跃度较低**。由于其标记为 `IsBetaVersion` 且 `EnabledByDefault=false`，**不建议在正式项目生产环境中依赖它**，更适合作为理解或扩展 UE 自动化测试 Python 集成方式的参考。如果您的项目需要稳定的 Python 自动化测试集成，应考虑使用更成熟、社区活跃的方案（如 `UnrealEnginePython` 插件或官方 `Python Editor Script Plugin` 本身提供的自动化能力）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/PythonAutomationTest)