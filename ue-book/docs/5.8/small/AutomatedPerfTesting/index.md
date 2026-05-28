# AutomatedPerfTesting

> This plugin provides Gauntlet Test Controllers to facilitate automatic performance testing.

| 属性 | 值 |
|---|---|
| 中文名 | 自动性能测试 |
| 分类 | Testing |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资产） |
| 模块 | `AutomatedPerfTesting` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-05-24 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Performance/AutomatedPerfTesting) | |

## 用途

AutomatedPerfTesting 基于 UE5 的 Gauntlet 自动化测试框架，提供了一套**可配置的性能测试控制器**，用于在 CI/CD 流水线中自动运行性能基准测试并收集 profiling 数据。

这个插件解决的核心问题是：**在无人值守的自动化流程中，标准化地运行性能测试并生成可比较的结果**。它将 Insight Trace、CSV Profiler、FPS Chart、视频录制等性能分析工具统一编排，按"预热→采集→冷却"的固定模式执行测试，确保每次测试的条件一致。

插件内置了多种预设的测试类型：
- **静态相机测试**：在关卡中放置的固定相机位置逐个测试，评估关卡各区域的渲染性能
- **材质测试**：对材质列表逐一加载到测试板上，隔离评估单个材质的渲染开销
- **序列测试**：播放 Level Sequence 并采集性能数据，适合过场动画或预录制流程的性能评估
- **回放测试**：回放录制的游戏过程，采集回放时的性能数据
- **ProfileGo 测试**：支持将玩家传送到指定坐标，运行自定义控制台命令序列，是最灵活的测试模式

所有测试类型最终都继承自 `UAutomatedPerfTestControllerBase`，该基类管理 profiling 工具的生命周期、测试元数据收集、以及退出码的正确返回。

## 使用场景

- 你的项目需要在 CI 中**自动验证关卡渲染性能**是否达标 → 使用静态相机测试
- 你需要**对比不同材质的 GPU 开销** → 使用材质测试
- 你需要**评估过场动画或 Cinematic 的性能表现** → 使用序列测试
- 你需要**回放历史游戏过程并测量性能** → 使用回放测试
- 你需要**最灵活的自动化性能测试**（自定义坐标、命令序列、动态场景生成）→ 使用 ProfileGo 测试
- 你希望通过 Gauntlet 框架在远程设备上运行性能测试 → 本插件正是为此设计

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetTestID` | 获取当前测试的唯一标识符 | `UAutomatedPerfTestSubsystem` |
| `GetMapFromAssetName` | 根据资产名称获取关卡软引用路径 | `UAutomatedStaticCameraPerfTestProjectSettings` |
| `GetReplayPathFromName` | 根据回放名称获取回放文件路径 | `UAutomatedReplayPerfTestProjectSettings` |
| `GetComboFromTestName` | 根据测试名称获取关卡/序列组合 | `UAutomatedSequencePerfTestProjectSettings` |

### 测试生命周期接口（IAutomatedPerfTestInterface）

该接口定义了四个蓝图可实现事件，如果你使用 `AAutomatedPerfTestGameModeBase` 作为游戏模式，可以在蓝图中覆盖这些事件：

| 事件 | 说明 |
|---|---|
| `SetupTest` | 测试开始前的初始化（加载资源、配置场景） |
| `RunTest` | 执行测试主体逻辑 |
| `TeardownTest` | 测试结束后的清理工作 |
| `Exit` | 退出测试 |

### 项目设置配置

插件在 **项目设置 → Plugins** 下注册了多个设置面板：

1. **Automated Performance Testing** — 全局设置（Teardown 到退出的延迟时间）
2. **Automated Performance Testing | Static Camera** — 配置要测试的关卡列表、预热/采集/冷却时间、是否截图
3. **Automated Performance Testing | Materials** — 配置材质列表、测试关卡、相机/板材参数
4. **Automated Performance Testing | Sequence** — 配置关卡/序列组合列表
5. **Automated Performance Testing | Replay** — 配置回放文件路径
6. **Automated Performance Testing | ProfileGo** — 配置 ProfileGo 场景、集合、命令

所有设置类都暴露了 `BlueprintReadWrite` 属性，可在蓝图中动态修改。

## C++ 用法

### 头文件引入

```cpp
#include "AutomatedPerfTestControllerBase.h"
#include "AutomatedStaticCameraPerfTestBase.h"
#include "AutomatedMaterialPerfTest.h"
#include "AutomatedSequencePerfTest.h"
#include "AutomatedReplayPerfTest.h"
#include "AutomatedProfileGoTest.h"
#include "ProfileGo.h"
```

### 基本用法：自定义测试控制器

从 `UAutomatedPerfTestControllerBase` 继承来创建自定义测试控制器。

**来源**：`Source/AutomatedPerfTesting/Public/AutomatedPerfTestControllerBase.h`

```cpp
UCLASS(MinimalAPI)
class UMyCustomPerfTest : public UAutomatedPerfTestControllerBase
{
    GENERATED_BODY()

public:
    // 返回唯一标识符，用于输出制品文件命名
    virtual FString GetPerfTestTypeID() const override { return TEXT("MyCustomTest"); }

    virtual void SetupTest() override
    {
        // 调用基类初始化 profiling 工具
        Super::SetupTest();
        // 自定义测试准备逻辑
    }

    UFUNCTION()
    virtual void RunTest() override
    {
        Super::RunTest();
        // 标记 profiling 区域开始
        MarkProfilingStart();
        // ... 执行测试逻辑
    }

    virtual void TeardownTest(bool bExitAfterTeardown = true) override
    {
        // 标记 profiling 区域结束
        MarkProfilingEnd();
        Super::TeardownTest(bExitAfterTeardown);
    }

    // 添加自定义元数据到 profiling 输出
    virtual void GatherTestMetadata(TArray<TPair<FString, FString>>& OutMetadata) const override
    {
        Super::GatherTestMetadata(OutMetadata);
        OutMetadata.Add({TEXT("CustomKey"), TEXT("CustomValue")});
    }
};
```

### 基本用法：配置 Profiling 工具

基类提供了一组方法用于控制各种 profiling 工具的开关：

```cpp
// 检查是否请求了特定 profiling 工具（在子类中通过配置控制）
if (RequestsInsightsTrace())
{
    TryStartInsightsTrace();
}

if (RequestsCSVProfiler())
{
    TryStartCSVProfiler(TEXT("MyTest.csv"), TEXT("/Path/To/Output"));
}

if (RequestsFPSChart())
{
    TryStartFPSChart();
}

if (RequestsVideoCapture())
{
    TryStartVideoCapture();
}
```

### 进阶用法：ProfileGo 子系统

ProfileGo 是最灵活的测试模式，支持自定义坐标传送和命令序列执行。

**来源**：`Source/AutomatedPerfTesting/Public/ProfileGo/ProfileGoSubsystem.h`、`Source/AutomatedPerfTesting/Public/ProfileGo/ProfileGo.h`

```cpp
// 获取 ProfileGo 子系统
UProfileGoSubsystem* ProfileGoSubsystem = GetWorld()->GetSubsystem<UProfileGoSubsystem>();

// 注册自定义命令处理器
UProfileGo& ProfileGo = UProfileGo::GetCDO();
ProfileGo.RegisterCommandDelegate(TEXT("MyCommand"), 
    UProfileGo::CommandHandlerDelegate::CreateLambda(
        [](FString& Output, const FProfileGoCommandAPT& Command) -> bool
        {
            // 执行自定义命令逻辑
            Output = TEXT("Command executed successfully");
            return true;
        })
    );

// 注册自定义场景生成器
ProfileGo.RegisterGeneratedScenarioDelegate(TEXT("MyScenario"),
    UProfileGo::GeneratedScenarioHandlerDelegate::CreateLambda(
        [](FString& Output, FString& Args) -> bool
        {
            // 动态生成场景
            return true;
        })
    );

// 监听 ProfileGo 事件
ProfileGoSubsystem->OnRequestFailed().AddLambda([]()
{
    UE_LOG(LogAutomatedPerfTest, Error, TEXT("ProfileGo request failed!"));
});

ProfileGoSubsystem->OnScenarioStarted().AddLambda([](const FString& ScenarioName)
{
    UE_LOG(LogAutomatedPerfTest, Log, TEXT("Scenario started: %s"), *ScenarioName);
});

ProfileGoSubsystem->OnScenarioEnded().AddLambda([](const FString& ScenarioName)
{
    UE_LOG(LogAutomatedPerfTest, Log, TEXT("Scenario ended: %s"), *ScenarioName);
});
```

### 进阶用法：从 JSON 加载 ProfileGo 配置

```cpp
// 从 JSON 文件加载场景和命令配置
ProfileGoSubsystem->LoadFromJSON(TEXT("ProfileGoConfig.json"));

// 保存当前配置到 JSON
ProfileGoSubsystem->SaveToJSON(TEXT("ProfileGoConfig.json"));
```

## Demo 示例

### 自定义性能测试控制器

**MyPerfTestController.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "AutomatedPerfTestControllerBase.h"
#include "MyPerfTestController.generated.h"

UCLASS(MinimalAPI)
class UMyPerfTestController : public UAutomatedPerfTestControllerBase
{
    GENERATED_BODY()

public:
    virtual FString GetPerfTestTypeID() const override;
    virtual void SetupTest() override;
    virtual void GatherTestMetadata(TArray<TPair<FString, FString>>& OutMetadata) const override;

    UFUNCTION()
    virtual void RunTest() override;

protected:
    UFUNCTION()
    void OnEvaluationComplete();

    void OpenTestMap();

private:
    FSoftObjectPath TestMapPath;
    float EvaluationDuration = 10.0f;
};
```

**MyPerfTestController.cpp**
```cpp
#include "MyPerfTestController.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"

FString UMyPerfTestController::GetPerfTestTypeID() const
{
    return TEXT("MyPerfTest");
}

void UMyPerfTestController::SetupTest()
{
    Super::SetupTest();

    // 配置 CSV 输出文件名
    const FString CSVFileName = FString::Printf(TEXT("MyPerfTest_%s"), *GetTestID());

    // 启用所需 profiling 工具
    if (RequestsCSVProfiler())
    {
        TryStartCSVProfiler(CSVFileName);
    }
    if (RequestsInsightsTrace())
    {
        TryStartInsightsTrace();
    }
    if (RequestsFPSChart())
    {
        TryStartFPSChart();
    }
}

void UMyPerfTestController::GatherTestMetadata(
    TArray<TPair<FString, FString>>& OutMetadata) const
{
    Super::GatherTestMetadata(OutMetadata);
    OutMetadata.Add({TEXT("TestType"), TEXT("CustomPerformanceTest")});
    OutMetadata.Add({TEXT("MapPath"), TestMapPath.ToString()});
}

void UMyPerfTestController::RunTest()
{
    Super::RunTest();

    MarkProfilingStart();

    // 延迟后完成评估
    GetWorld()->GetTimerManager().SetTimerForNextTick([this]()
    {
        FTimerHandle Handle;
        GetWorld()->GetTimerManager().SetTimer(Handle, this,
            &UMyPerfTestController::OnEvaluationComplete,
            EvaluationDuration, false);
    });
}

void UMyPerfTestController::OnEvaluationComplete()
{
    MarkProfilingEnd();

    // 停止 profiling 工具
    if (RequestsCSVProfiler())
    {
        TryStopCSVProfiler();
    }
    if (RequestsInsightsTrace())
    {
        TryStopInsightsTrace();
    }
    if (RequestsFPSChart())
    {
        TryStopFPSChart();
    }

    // 截图记录
    TakeScreenshot(TEXT("FinalState"));

    // 结束测试（成功）
    TeardownTest(true);
}

void UMyPerfTestController::OpenTestMap()
{
    UGameplayStatics::OpenLevelBySoftObjectPtr(GetWorld(), TestMapPath);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Gauntlet` | 提供 Gauntlet 测试框架基础设施（测试控制器基类、生命周期管理） |
| `ProjectLauncher` | 用于通过命令行启动和管理项目实例（仅 Win64/Linux/Mac） |
| `LevelSequence` | 序列测试中播放 Level Sequence |
| `MediaUtils` | 视频录制功能支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复作用域枚举在格式化函数中导致乱码输出的问题 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符与参数不匹配的问题 |
| 2026-04-15 | `e1420e00` | Automation: Only set OutputPath if we're not setting an ArtifactsPath. | 优化输出路径逻辑，设置 ArtifactsPath 时不再重复设置 OutputPath |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移到 UE_LOGF 新宏格式 |

### 维护评价

- **创建时间**：2024 年 5 月，约 2 年历史
- **最近更新**：2026 年 5 月仍有活跃更新，最近的提交集中在编译警告修复和平台兼容性改进
- **维护状态**：**活跃维护中**，但近期更新均为底层修复（格式化、编译兼容性），非功能增强
- **实验性状态**：`IsExperimentalVersion=true` 且 `Installed=false`，API 可能发生变化
- **依赖风险**：依赖 Gauntlet 和 ProjectLauncher 两个插件，增加了集成复杂度
- **推荐程度**：适合有成熟 CI/CD 流水线的大型项目使用；如果你只需要简单的性能数据收集，内置的 Unreal Insights 可能更轻量。由于是实验性插件，建议做好版本升级时 API 变更的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Performance/AutomatedPerfTesting)
- [官方文档]()（暂无）
- [测试用例]()（暂未发现独立测试文件）