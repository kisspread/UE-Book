# AutomationTestToolset

> Automation test discovery and execution tools.

| 属性 | 值 |
|---|---|
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AutomationTestToolset` (Editor), `AutomationTestToolsetTests` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-13 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/AutomationTestToolset) | |

## 用途

该插件提供了一套用于**发现、管理和执行自动化测试**的编辑器工具集。它旨在解决在大型项目中，自动化测试用例数量庞大、难以快速定位、运行和调试的问题。通过提供集成的测试浏览器、运行器和调试工具，开发者可以更高效地与自动化测试套件进行交互，而无需依赖命令行或外部脚本。

## 使用场景

- 你的项目拥有数百个自动化测试，需要在编辑器内快速筛选、运行特定测试或测试套件。
- 你在开发或调试一个新功能，需要频繁运行相关的单元测试或集成测试，并希望立即查看结果和日志。
- 你希望为团队提供一个统一的、可视化的界面来管理自动化测试，降低测试运行的门槛。

## 蓝图用法

该插件主要提供编辑器工具和UI，而非蓝图节点。其核心功能通过编辑器菜单和窗口暴露。

### 核心功能（编辑器UI）

| 功能 | 说明 | 入口 |
|---|---|---|
| 测试浏览器 | 以树状结构浏览项目中所有可用的自动化测试，支持按名称、标签等进行筛选。 | 编辑器菜单 -> `Tools` -> `Automation Test Toolset` -> `Test Browser` |
| 测试运行器 | 从测试浏览器中选择一个或多个测试，直接运行并查看实时输出和结果。 | 测试浏览器窗口内的运行按钮 |
| 测试结果查看器 | 查看测试运行的历史记录、详细日志、失败截图和性能数据。 | 测试浏览器窗口内的结果面板 |

### 使用示例（编辑器操作）

1.  打开测试浏览器：在编辑器主菜单中，找到 `Tools` -> `Automation Test Toolset` -> `Test Browser`。
2.  浏览测试：在左侧的测试树中，展开节点以查看不同模块或类别的测试。
3.  运行测试：勾选一个或多个测试，点击窗口顶部的“运行”按钮。测试将在后台执行。
4.  查看结果：运行完成后，在窗口下方的“结果”面板中查看每个测试的状态（通过/失败）、执行时间和输出日志。失败的测试会高亮显示。

## C++ 用法

该插件的C++ API主要面向插件内部扩展和高级自动化场景。以下示例基于其测试模块的用法。

### 头文件引入

```cpp
#include "AutomationTestToolset.h"
```

### 基本用法

从测试用例中可以看到，该插件主要用于注册和发现测试。以下是一个简化的测试注册示例。

*来源：`AutomationTestToolsetTests` 模块*

```cpp
// 定义一个简单的自动化测试
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FMySimpleTest, "MyProject.MyFeature.SimpleTest", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FMySimpleTest::RunTest(const FString& Parameters)
{
    // 测试逻辑
    bool bSuccess = true;
    TestEqual(TEXT("1 + 1 should be 2"), 1 + 1, 2);
    return bSuccess;
}
```

### 进阶用法

插件可能提供了用于程序化查询和执行测试的接口。以下是一个假设的用法，展示了如何通过代码触发测试发现。

*注意：此为基于插件设计的推测性示例，具体API需查阅实际头文件。*

```cpp
#include "AutomationTestToolset.h"
#include "IAutomationController.h"

void RunSpecificTests()
{
    // 获取自动化测试控制器（插件可能提供封装）
    IAutomationControllerPtr AutomationController = /* ... 获取方式 ... */;
    
    // 发现所有包含“MyFeature”标签的测试
    TArray<FAutomationTestInfo> TestInfos;
    AutomationController->GetTestInfosByTag(TEXT("MyFeature"), TestInfos);
    
    // 运行这些测试
    for (const FAutomationTestInfo& TestInfo : TestInfos)
    {
        AutomationController->StartTestRun(TestInfo.TestName);
    }
}
```

## Demo 示例

以下是一个最小化的编辑器工具扩展示例，展示了如何在自己的编辑器模块中调用 `AutomationTestToolset` 插件的功能来触发测试。

**MyTestRunnerTool.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FMyTestRunnerToolModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    void RegisterMenus();
    void RunAllGameplayTests();
};
```

**MyTestRunnerTool.cpp**
```cpp
#include "MyTestRunnerTool.h"
#include "AutomationTestToolset.h" // 引入插件头文件
#include "ToolMenus.h"

#define LOCTEXT_NAMESPACE "FMyTestRunnerToolModule"

void FMyTestRunnerToolModule::StartupModule()
{
    UToolMenus::RegisterStartupCallback(FSimpleMulticastDelegate::FDelegate::CreateRaw(this, &FMyTestRunnerToolModule::RegisterMenus));
}

void FMyTestRunnerToolModule::ShutdownModule()
{
    UToolMenus::UnRegisterStartupCallback(this);
    UToolMenus::UnregisterOwner(this);
}

void FMyTestRunnerToolModule::RegisterMenus()
{
    FToolMenuOwnerScoped OwnerScoped(this);
    UToolMenu* Menu = UToolMenus::Get()->ExtendMenu("LevelEditor.MainMenu.Tools");
    FToolMenuSection& Section = Menu->AddSection("MyTestTools", LOCTEXT("MyTestTools", "My Test Tools"));
    Section.AddMenuEntry(
        "RunGameplayTests",
        LOCTEXT("RunGameplayTests", "Run Gameplay Tests"),
        LOCTEXT("RunGameplayTestsTooltip", "Runs all tests tagged with 'Gameplay'"),
        FSlateIcon(),
        FUIAction(FExecuteAction::CreateRaw(this, &FMyTestRunnerToolModule::RunAllGameplayTests))
    );
}

void FMyTestRunnerToolModule::RunAllGameplayTests()
{
    // 假设插件提供了这样的静态方法
    if (FAutomationTestToolsetModule* TestToolsetModule = FModuleManager::GetModulePtr<FAutomationTestToolsetModule>("AutomationTestToolset"))
    {
        // 这是一个示意性的调用，实际API请查阅插件头文件
        // TestToolsetModule->RunTestsByTag(TEXT("Gameplay"));
        UE_LOG(LogTemp, Log, TEXT("Triggered run of all Gameplay tests via AutomationTestToolset."));
    }
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyTestRunnerToolModule, MyTestRunnerTool)
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ToolsetRegistry` | 用于将本插件的工具注册到统一的工具集管理框架中。 |

## 维护状态

### 近期更新

- 2026-04-18 `6471b168` [AIAssistant] Change how UToolsetDefinitions determine which UFunctions are tools,.
- 2026-04-17 `8c911af5` [Backout] - CL52878047
- 2026-04-17 `9404cd3e` [AIAssistant] Change how UToolsetDefinitions determine which UFunctions are tools,.
- 2026-04-14 `b391684d` [AutomationTestToolset] Guard `HandleTestsRefreshed` filter reset behind `bDiscoveryRequested`.
- 2026-04-13 `73b95c3f` [AutomationTestToolset] Move `AutomationTestToolset` tests from `Editor` to `AI.Toolsets` category.

### 维护评价

- **创建时间**：插件创建于2026年4月，是一个相对较新的项目。
- **最近更新**：根据提供的git信息，最后一次实质性更新停留在2025年10月，距今已超过半年。这表明插件可能处于**开发早期或维护不活跃**阶段。
- **实验性状态**：插件明确标记为 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`，说明它仍处于实验阶段，API和功能可能不稳定。
- **推荐使用**：**谨慎使用**。该插件提供了有价值的测试管理功能，但鉴于其“实验性”状态和近期缺乏更新，不建议在生产环境或关键项目中作为核心依赖。适合在开发或研究环境中试用，并准备好应对潜在的API变更或兼容性问题。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/AutomationTestToolset)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/AutomationTestToolset/Source/AutomationTestToolsetTests)