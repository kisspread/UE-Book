# AutomatedPerfTesting

> This plugin provides Gauntlet Test Controllers to facilitate automatic performance testing.

| 属性 | 值 |
|---|---|
| 中文名 | 自动性能测试 |
| 分类 | Testing |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AutomatedPerfTesting` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-05-23 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Performance/AutomatedPerfTesting) | |

## 用途

`AutomatedPerfTesting` 插件是一个用于自动化执行游戏性能基准测试的框架。它基于 UE5 的 Gauntlet 测试系统构建，提供了一套标准化的 `UGauntletTestController` 子类，用于管理性能测试的完整生命周期（初始化、预热、数据采集、冷却、清理）。其核心目的是将手动或脚本驱动的性能测试流程自动化、标准化，并统一收集性能数据（如帧率、CSV分析、Insights追踪、视频录制），以便在 CI/CD 流程或开发迭代中持续监控项目性能。

插件内置了多种常见测试场景的控制器，如静态相机测试、材质性能测试、关卡序列测试、回放测试以及一个可高度自定义的 ProfileGo 测试系统。开发者可以继承这些控制器来快速实现符合项目需求的自动化测试。

## 使用场景

- **项目性能回归测试**：在每日构建后，自动运行一组预定义的性能测试关卡或场景，监控性能指标是否达标或出现退化。
- **自动化数据采集**：需要定期（例如每次美术资源提交后）自动采集特定场景或材质的帧率、绘制调用、内存占用等数据。
- **材质性能评估**：有一批需要测试性能的材质，需要在一个标准化的场景中自动加载、渲染并收集数据。
- **固定视角关卡性能测试**：在关卡中放置多个固定摄像机，自动循环切换并采集每个视角的性能数据。
- **过场动画序列性能分析**：需要分析游戏内过场动画或 Cinematic Sequence 的渲染性能。
- **回放性能分析**：需要分析游戏回放文件（`.replay`）的回放性能。
- **复杂的自定义测试流程**：使用 `ProfileGo` 系统定义一套包含位置传送、控制台命令执行、数据采集的复杂测试流程。

## 蓝图用法

该插件主要面向 C++ 开发者，但也提供了一些蓝图可用的接口、设置和事件。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetTestID` | 获取当前测试的唯一标识符 | `UAutomatedPerfTestSubsystem` |
| `GetMapFromAssetName` | 从资源名获取关卡软引用 | `UAutomatedStaticCameraPerfTestProjectSettings` |
| `GetComboFromTestName` | 根据测试名获取关卡/序列组合 | `UAutomatedSequencePerfTestProjectSettings` |
| `GetReplayPathFromName` | 根据测试名获取回放文件路径 | `UAutomatedReplayPerfTestProjectSettings` |
| `SetupTest` | [蓝图可实现事件] 测试初始化阶段 | `IAutomatedPerfTestInterface` |
| `RunTest` | [蓝图可实现事件] 测试执行阶段 | `IAutomatedPerfTestInterface` |
| `TeardownTest` | [蓝图可实现事件] 测试清理阶段 | `IAutomatedPerfTestInterface` |
| `Exit` | [蓝图可实现事件] 测试退出 | `IAutomatedPerfTestInterface` |

### 使用示例（蓝图描述）

1.  **在 GameMode 中实现测试接口**：
    - 创建一个继承自 `AAutomatedPerfTestGameModeBase` 的蓝图。
    - 在该蓝图的事件图表中，覆盖 `SetupTest`、`RunTest` 和 `TeardownTest` 事件，编写测试逻辑（例如生成Actor、触发特定游戏状态）。
    - 在项目设置中，将此 GameMode 设置为特定性能测试关卡使用的 GameMode。

2.  **配置静态相机测试**：
    - 打开“项目设置” -> “插件” -> “自动性能测试 | 静态相机”。
    - 在 `MapsToTest` 列表中添加需要测试的关卡资产路径。
    - 设置 `WarmUpTime`（预热时间）、`SoakTime`（数据采集时间）和 `CooldownTime`（冷却时间）。
    - 根据需要勾选 `bCaptureScreenshots`。

## C++ 用法

### 头文件引入

```cpp
#include "AutomatedPerfTestControllerBase.h"
// 包含特定测试类型的头文件，例如：
#include "StaticCameraTests/AutomatedStaticCameraPerfTestBase.h"
#include "AutomatedMaterialPerfTest.h"
#include "AutomatedSequencePerfTest.h"
#include "AutomatedReplayPerfTest.h"
#include "AutomatedProfileGoTest.h"
#include "ProfileGo/ProfileGoSubsystem.h"
```

### 基本用法

创建一个自定义的性能测试控制器。 (来源: `AutomatedPerfTestControllerBase.h`)

```cpp
// MyCustomPerfTestController.h
#pragma once

#include "AutomatedPerfTestControllerBase.h"
#include "MyCustomPerfTestController.generated.h"

UCLASS()
class UMyCustomPerfTestController : public UAutomatedPerfTestControllerBase
{
    GENERATED_BODY()

public:
    // 重写测试ID，用于结果标识
    virtual FString GetPerfTestTypeID() const override { return TEXT("MyCustomTest"); }

    // 测试初始化
    virtual void SetupTest() override
    {
        Super::SetupTest();
        // 在这里执行测试前的准备工作，例如生成特定的测试对象
    }

    // 开始执行测试逻辑
    virtual void RunTest() override
    {
        Super::RunTest();
        // 在这里执行测试的核心逻辑
        // 可以通过 TakeScreenshot() 截图
        // 通过 ConsoleCommand() 执行控制台命令
    }

    // 测试清理
    virtual void TeardownTest(bool bExitAfterTeardown = true) override
    {
        // 在这里清理测试中生成的对象
        Super::TeardownTest(bExitAfterTeardown);
    }

    // 收集测试元数据（如关卡名、配置信息）
    virtual void GatherTestMetadata(TArray<TPair<FString, FString>>& OutMetadata) const override
    {
        Super::GatherTestMetadata(OutMetadata);
        OutMetadata.Add(TPair<FString, FString>(TEXT("CustomProperty"), TEXT("Value")));
    }
};
```

### 进阶用法

**1. 扩展 ProfileGo 系统 (来源: `ProfileGo.h`, `ProfileGoSubsystem.h`)**

`ProfileGo` 是一个强大的测试场景定义和执行引擎。你可以注册自定义命令和场景生成器。

```cpp
// 在某个模块（如GameMode）的 BeginPlay 或 Initialize 中注册
UProfileGoSubsystem* ProfileGoSubsystem = GetWorld()->GetSubsystem<UProfileGoSubsystem>();
if (ProfileGoSubsystem && ProfileGoSubsystem->ProfileGo)
{
    // 注册一个自定义的命令处理函数
    ProfileGoSubsystem->ProfileGo->RegisterCommandDelegate(
        TEXT("MyCustomCommand"),
        UProfileGo::CommandHandlerDelegate::CreateLambda([](FString& Log, const FProfileGoCommandAPT& Command) -> bool
        {
            // 在这里处理命令
            UE_LOG(LogAutomatedPerfTest, Log, TEXT("Executing custom command: %s"), *Command.Command);
            return true; // 返回 true 表示命令执行成功
        })
    );

    // 注册一个自定义的场景生成器
    ProfileGoSubsystem->ProfileGo->RegisterGeneratedScenarioDelegate(
        TEXT("MyGeneratedScenario"),
        UProfileGo::GeneratedScenarioHandlerDelegate::CreateLambda([](FString& OutLog, FString& InArgs) -> bool
        {
            // 根据参数 InArgs 生成测试场景
            return true;
        })
    );
}
```

**2. 在游戏模式中启动自动化测试**

```cpp
// MyTestGameMode.cpp
#include "AutomatedPerfTestGameModeBase.h"
#include "MyTestGameMode.generated.h"

UCLASS()
class AMyTestGameMode : public AAutomatedPerfTestGameModeBase
{
    GENERATED_BODY()

    virtual void SetupTest_Implementation() override
    {
        Super::SetupTest_Implementation();
        // 初始化测试环境，例如生成敌人、设置天气等
        GetWorld()->SpawnActor<...>(...);
    }

    virtual void RunTest_Implementation() override
    {
        Super::RunTest_Implementation();
        // 开始执行测试逻辑，例如模拟玩家移动
        // 可以使用定时器或等待特定事件来触发 TeardownTest
        FTimerHandle TimerHandle;
        GetWorldTimerManager().SetTimer(TimerHandle, this, &AMyTestGameMode::OnTestLogicComplete, 10.0f, false);
    }

    void OnTestLogicComplete()
    {
        // 测试逻辑完成，请求退出
        Exit();
    }
};
```

## Demo 示例

一个自定义静态相机测试控制器和其对应的测试 GameMode 的最小实现。

**头文件 (MyStaticCameraTestController.h)**:
```cpp
#pragma once
#include "StaticCameraTests/AutomatedStaticCameraPerfTestBase.h"
#include "MyStaticCameraTestController.generated.h"

UCLASS()
class UMyStaticCameraTestController : public UAutomatedStaticCameraPerfTestBase
{
    GENERATED_BODY()
public:
    virtual FString GetPerfTestTypeID() const override { return TEXT("MyStaticCameraTest"); }
    virtual void GatherTestMetadata(TArray<TPair<FString, FString>>& OutMetadata) const override
    {
        Super::GatherTestMetadata(OutMetadata);
        OutMetadata.Add(TPair<FString, FString>(TEXT("TestVersion"), TEXT("1.0")));
    }
};
```

**头文件 (MyPerfTestGameMode.h)**:
```cpp
#pragma once
#include "AutomatedPerfTestGameModeBase.h"
#include "MyPerfTestGameMode.generated.h"

UCLASS()
class AMyPerfTestGameMode : public AAutomatedPerfTestGameModeBase
{
    GENERATED_BODY()
public:
    virtual void SetupTest_Implementation() override;
    virtual void RunTest_Implementation() override;
    virtual void TeardownTest_Implementation() override;
};
```

**源文件 (MyPerfTestGameMode.cpp)**:
```cpp
#include "MyPerfTestGameMode.h"

void AMyPerfTestGameMode::SetupTest_Implementation()
{
    // 在这里执行测试初始化，例如加载特定资源、生成测试 Actor
    Super::SetupTest_Implementation();
}

void AMyPerfTestGameMode::RunTest_Implementation()
{
    // 通知基类开始运行测试（将启动相机循环等流程）
    Super::RunTest_Implementation();
    // 自定义运行逻辑（如果需要）
}

void AMyPerfTestGameMode::TeardownTest_Implementation()
{
    // 清理测试中生成的对象
    Super::TeardownTest_Implementation();
}
```

## 模块依赖

插件本身依赖 `Gauntlet` 和 `ProjectLauncher` 插件。对于使用该插件的用户模块，在 `Build.cs` 中需要添加以下依赖（除了常见的 `Core`, `Engine` 等）：

| 模块 | 用途 |
|---|---|
| `Gauntlet` | 核心测试框架，所有测试控制器的基类 |
| `ProjectLauncher` | 用于通过 UAT 启动打包项目和测试 |
| `AutomationController` | 自动化测试控制器（Gauntlet 内部使用） |
| `ProfilerService` | 性能分析服务（用于 Insights 集成） |
| `LevelSequence` | 关卡序列播放器（用于序列性能测试） |
| `MediaUtils` | 媒体工具（可能用于视频捕获相关） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点数导致的编译警告 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了作用域枚举在格式化函数中可能导致乱码输出的问题 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了32位和64位格式说明符与参数位宽不匹配的问题 |
| 2026-04-15 | `e1420e00` | Automation: Only set OutputPath if we're not setting an ArtifactsPath. This means that we can easily | 自动化：仅当未设置 ArtifactsPath 时才设置 OutputPath，以便更灵活地管理输出路径 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF |

### 维护评价

- **创建时间**：2024年5月创建，是一个相对年轻的插件。
- **近期更新频率**：最近几个月有持续的提交，主要集中在**编译警告修复**、**代码质量改进**和**日志系统迁移**上，表明该插件处于**积极维护**状态。
- **活跃度**：插件仍在更新，以适应新的引擎版本和编译器要求。
- **已知问题与限制**：该插件在 `.uplugin` 中被标记为 `IsExperimentalVersion: true`，且默认未启用 (`Installed: false`)，表明其 API 和功能可能尚未完全稳定，不建议直接用于正式生产环境的 CI/CD 关键路径。
- **推荐度**：对于游戏项目的内部自动化性能测试、CI/CD 集成或性能分析团队，该插件提供了强大的基础框架。鉴于其**实验性**状态，建议在测试环境中充分评估后使用，并关注后续版本的更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Performance/AutomatedPerfTesting)
- 官方文档（无）