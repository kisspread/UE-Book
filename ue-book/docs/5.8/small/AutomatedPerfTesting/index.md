# AutomatedPerfTesting

> This plugin provides Gauntlet Test Controllers to facilitate automatic performance testing.

| 属性 | 值 |
|---|---|
| 中文名 | 自动化性能测试 |
| 分类 | Testing |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、项目设置资产） |
| 模块 | `AutomatedPerfTesting` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-05-23 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Performance/AutomatedPerfTesting) | |

## 用途

AutomatedPerfTesting 是一个基于 **Gauntlet 自动化测试框架**的性能测试插件，提供了多种预构建的测试控制器（Test Controller），用于在无人值守的情况下自动收集游戏运行时的性能数据。

该插件解决的核心问题是：**如何标准化、自动化地衡量项目在不同场景下的性能表现**。它封装了 Unreal Insights 追踪、CSV 性能分析器、FPS 图表、视频录制等性能收集工具的启动/停止逻辑，并提供了多种测试模式（静态相机、材质、序列、回放、ProfileGo），让开发者无需手动编写采集脚本即可执行可重复的性能基准测试。

插件设计为通过 Gauntlet 框架在 CI/CD 流水线中运行，也可以在编辑器中用于日常性能回归测试。

## 使用场景

- 你在项目中需要**定期检测帧率回归**，想在 CI 中自动跑基准测试 → 使用 Static Camera 测试模式
- 你需要**对比不同材质的渲染开销**，逐个在固定场景中评估材质性能 → 使用 Material 测试模式
- 你需要**对 Sequencer 过场动画进行性能采集**，按镜头切割分段记录数据 → 使用 Sequence 测试模式
- 你有一套 **ProfileGo 场景配置**（JSON），需要在多个位置自动传送、执行控制台命令并采集数据 → 使用 ProfileGo 测试模式
- 你需要**回放录制的会话并采集回放过程中的性能数据** → 使用 Replay 测试模式
- 你正在搭建 **CI/CD 性能回归测试流水线**，需要所有测试统一输出格式 → 使用本插件提供的 Gauntlet 控制器基类

## 蓝图用法

### 核心接口

插件定义了 `IAutomatedPerfTestInterface` 接口，所有测试生命周期通过蓝图实现：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetupTest` | 测试前的准备工作（蓝图可重写） | `IAutomatedPerfTestInterface` |
| `RunTest` | 执行测试逻辑（蓝图可重写） | `IAutomatedPerfTestInterface` |
| `TeardownTest` | 测试结束后的清理工作（蓝图可重写） | `IAutomatedPerfTestInterface` |
| `Exit` | 退出测试（蓝图可重写） | `IAutomatedPerfTestInterface` |

### 项目设置访问

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetMapFromAssetName` | 根据资产名称获取关卡软引用路径 | `UAutomatedStaticCameraPerfTestProjectSettings` |
| `GetComboFromTestName` | 根据测试名称查找关卡/序列组合 | `UAutomatedSequencePerfTestProjectSettings` |
| `GetReplayPathFromName` | 根据名称获取回放文件路径 | `UAutomatedReplayPerfTestProjectSettings` |
| `GetTestID` | 获取当前测试的唯一标识符 | `UAutomatedPerfTestSubsystem` |

### 游戏模式蓝图实现

`AAutomatedPerfTestGameModeBase` 提供了完整的蓝图可实现事件：

1. 在蓝图中创建继承自 `AutomatedPerfTestGameModeBase` 的游戏模式
2. 在项目设置中配置 "Maps and Modes" 使用该模式别名
3. 在各测试配置中通过 `GameModeOverride` 字段指定别名
4. 重写 `SetupTest` / `RunTest` / `TeardownTest` 来定义自定义测试逻辑

### 静态相机测试配置（蓝图描述）

在 **项目设置 → Plugins → Static Cameras** 中：
1. 将需要测试的关卡添加到 `MapsToTest` 数组
2. 设置 `WarmUpTime`（预热时间，秒）
3. 设置 `SoakTime`（数据采集时间，秒）
4. 设置 `CooldownTime`（冷却时间，秒）
5. 可选启用 `bCaptureScreenshots` 截取每个相机的截图

在关卡中放置 `AAutomatedPerfTestStaticCamera` 相机演员标记测试位置，可设置 `CollectionName` 分组。

### 材质测试配置（蓝图描述）

在 **项目设置 → Plugins → Materials** 中：
1. 将需要测试的材质添加到 `MaterialsToTest` 数组
2. 指定 `MaterialPerformanceTestMap` 测试关卡
3. 指定 `MaterialPlate` 静态网格体作为材质载体
4. 设置 `CameraProjectionMode`（透视/正交）
5. 设置 `PlateDistanceFromCamera` 板面距离
6. 配置 `WarmUpTime` / `SoakTime` / `CooldownTime`

### 序列测试配置（蓝图描述）

在 **项目设置 → Plugins → Sequence** 中：
1. 添加 `MapsAndSequencesToTest` 条目，每个条目关联一个关卡和一个 LevelSequence
2. 设置 `ComboName` 用于命令行直接引用
3. 设置 `SequenceStartDelay`（序列启动延迟，秒）

## C++ 用法

### 头文件引入

```cpp
#include "AutomatedPerfTestControllerBase.h"
#include "ProfileGo/ProfileGoSubsystem.h"
#include "AutomatedPerfTestGameModeBase.h"
```

### 基本用法：创建自定义测试控制器

继承 `UAutomatedPerfTestControllerBase` 创建自定义 Gauntlet 测试控制器：

```cpp
// MyCustomPerfTest.h
#pragma once

#include "AutomatedPerfTestControllerBase.h"
#include "MyCustomPerfTest.generated.h"

UCLASS()
class UMyCustomPerfTest : public UAutomatedPerfTestControllerBase
{
    GENERATED_BODY()

public:
    virtual FString GetPerfTestTypeID() const override
    {
        return TEXT("MyCustom");
    }

    virtual void SetupTest() override
    {
        Super::SetupTest();
        // 设置测试环境
    }

    UFUNCTION()
    virtual void RunTest() override
    {
        Super::RunTest();
        // 执行测试逻辑，完成后调用 EndTestSuccess() 或 EndTestFailure()
    }

    virtual void GatherTestMetadata(TArray<TPair<FString, FString>>& OutMetadata) const override
    {
        Super::GatherTestMetadata(OutMetadata);
        // 添加自定义元数据
        OutMetadata.Add(TPair<FString, FString>(TEXT("TestType"), TEXT("Custom")));
    }
};
```

> 来源：`Source/AutomatedPerfTesting/Public/AutomatedPerfTestControllerBase.h`

### 基本用法：在 GameMode 中实现测试接口

```cpp
// MyPerfTestGameMode.h
#pragma once

#include "AutomatedPerfTestGameModeBase.h"
#include "MyPerfTestGameMode.generated.h"

UCLASS()
class AMyPerfTestGameMode : public AAutomatedPerfTestGameModeBase
{
    GENERATED_BODY()

public:
    void SetupTest_Implementation() override
    {
        // 蓝图级 SetupTest 实现
    }

    void RunTest_Implementation() override
    {
        // 蓝图级 RunTest 实现
    }

    void TeardownTest_Implementation() override
    {
        // 蓝图级 TeardownTest 实现
    }
};
```

> 来源：`Source/AutomatedPerfTesting/Public/AutomatedPerfTestGameModeBase.h`

### 进阶用法：使用 ProfileGo 子系统执行场景化测试

```cpp
// 在 GameMode 或其他 Actor 中
#include "ProfileGo/ProfileGoSubsystem.h"

void AMyGameMode::BeginPlay()
{
    Super::BeginPlay();

    // 获取 ProfileGo 子系统
    UProfileGoSubsystem* ProfileGoSubsystem = GetWorld()->GetSubsystem<UProfileGoSubsystem>();
    if (ProfileGoSubsystem)
    {
        // 绑定事件
        ProfileGoSubsystem->OnPassEnded().AddUObject(this, &AMyGameMode::OnProfileGoPassEnded);
        ProfileGoSubsystem->OnScenarioStarted().AddUObject(this, &AMyGameMode::OnScenarioStarted);

        // 运行 ProfileGo 配置
        ProfileGoSubsystem->Run(TEXT("MyProfileName"), TEXT("-args=value"));
    }
}

void AMyGameMode::OnProfileGoPassEnded()
{
    // ProfileGo 一轮测试完成
    UE_LOG(LogTemp, Log, TEXT("ProfileGo pass completed. Error: %d"),
        GetWorld()->GetSubsystem<UProfileGoSubsystem>()->HasEncounteredError());
}

void AMyGameMode::OnScenarioStarted(const FString& ScenarioName)
{
    UE_LOG(LogTemp, Log, TEXT("Scenario started: %s"), *ScenarioName);
}
```

> 来源：`Source/AutomatedPerfTesting/Public/ProfileGo/ProfileGoSubsystem.h`

### 进阶用法：控制性能采集工具

在自定义控制器中直接使用基类提供的采集控制方法：

```cpp
void UMyCustomPerfTest::RunTest()
{
    Super::RunTest();

    // 启动 CSV 性能分析器
    TryStartCSVProfiler(TEXT("MyTestData"), TEXT("/Path/To/Output"), 300);

    // 启动 Unreal Insights 追踪
    TryStartInsightsTrace();

    // 启动 FPS 图表
    TryStartFPSChart();

    // 启动视频录制
    TryStartVideoCapture();
}

void UMyCustomPerfTest::FinishTest()
{
    // 停止所有采集工具
    TryStopCSVProfiler();
    TryStopInsightsTrace();
    TryStopFPSChart();
    TryFinalizingVideoCapture();

    EndTestSuccess();
}
```

> 来源：`Source/AutomatedPerfTesting/Public/AutomatedPerfTestControllerBase.h`

## Demo 示例

### 自定义性能测试控制器（.h + .cpp）

```cpp
// SimpleBenchmarkController.h
#pragma once

#include "AutomatedPerfTestControllerBase.h"
#include "SimpleBenchmarkController.generated.h"

UCLASS()
class USimpleBenchmarkController : public UAutomatedPerfTestControllerBase
{
    GENERATED_BODY()

public:
    virtual FString GetPerfTestTypeID() const override { return TEXT("SimpleBenchmark"); }
    virtual void SetupTest() override;
    
    UFUNCTION()
    virtual void RunTest() override;

    virtual void GatherTestMetadata(TArray<TPair<FString, FString>>& OutMetadata) const override;

    UFUNCTION()
    void OnBenchmarkComplete();

private:
    float BenchmarkDuration = 30.0f;
    float ElapsedTime = 0.0f;
};
```

```cpp
// SimpleBenchmarkController.cpp
#include "SimpleBenchmarkController.h"

void USimpleBenchmarkController::SetupTest()
{
    Super::SetupTest();
    // 注册自定义元数据
    UE_LOG(LogAutomatedPerfTest, Log, TEXT("Simple Benchmark: Setting up test"));
}

void USimpleBenchmarkController::RunTest()
{
    Super::RunTest();
    // 启动 CSV 采集
    TryStartCSVProfiler(TEXT("SimpleBenchmark"));
    TryStartFPSChart();

    ElapsedTime = 0.0f;

    UE_LOG(LogAutomatedPerfTest, Log, TEXT("Simple Benchmark: Running for %.1f seconds"), BenchmarkDuration);
}

void USimpleBenchmarkController::GatherTestMetadata(
    TArray<TPair<FString, FString>>& OutMetadata) const
{
    Super::GatherTestMetadata(OutMetadata);
    OutMetadata.Add(TPair<FString, FString>(
        TEXT("BenchmarkType"), TEXT("Simple")));
    OutMetadata.Add(TPair<FString, FString>(
        TEXT("Duration"), FString::SanitizeFloat(BenchmarkDuration)));
}

void USimpleBenchmarkController::OnBenchmarkComplete()
{
    TryStopCSVProfiler();
    TryStopFPSChart();
    EndTestSuccess();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Gauntlet` | Gauntlet 自动化测试框架，提供 `UGauntletTestController` 基类 |
| `ProjectLauncher` | 项目启动器，用于在 CI 环境中启动和管理测试目标进程 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点数的警告 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复格式化函数中作用域枚举导致的乱码输出 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符与参数位宽不匹配的问题 |
| 2026-04-15 | `e1420e00` | Automation: Only set OutputPath if we're not setting an ArtifactsPath. This means that we can easily | 优化输出路径逻辑：仅在未设置 ArtifactsPath 时才设置 OutputPath |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 宏 |

### 维护评价

- **活跃维护**：该插件在 2026 年 4-5 月期间有密集的代码质量改进和平台兼容性修复，维护非常活跃
- **创建时间**：2024 年 5 月，至今约 2 年，处于早期成熟阶段
- **实验性标记**：`.uplugin` 中 `IsExperimentalVersion=true`，表明 Epic 将其视为实验性功能，API 可能发生变化
- **默认未启用**：`Installed=false` 且 `EnabledByDefault` 未设置（默认 false），需要手动在插件设置中启用
- **功能完整度**：已提供 5 种测试模式（静态相机、材质、序列、ProfileGo、回放），覆盖了常见的性能测试需求
- **CI 集成**：与 Gauntlet 和 ProjectLauncher 深度集成，天然支持 CI/CD 流水线
- **推荐使用**：✅ 推荐用于 CI 性能回归测试和自动化基准测试，但需注意其**实验性状态**，未来版本可能有 API 变更

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Performance/AutomatedPerfTesting)
- [Gauntlet 源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Testing/Gauntlet)（前置依赖）