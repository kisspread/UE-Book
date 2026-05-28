# AutomatedPerfTesting

> This plugin provides Gauntlet Test Controllers to facilitate automatic performance testing.

| 属性 | 值 |
|---|---|
| 中文名 | 自动化性能测试 |
| 分类 | Testing |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AutomatedPerfTesting` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-05-23 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Performance/AutomatedPerfTesting) | |

## 用途

这个插件解决的是**自动化性能回归测试**的问题。

在游戏开发中，团队需要持续监控帧率、内存、材质渲染开销等性能指标是否出现退化。手动测试效率低且难以重复。此插件基于 UE 的 Gauntlet 测试框架，提供了一系列可配置的测试控制器（Test Controller），支持以下自动化场景：

- **静态相机测试**：自动加载关卡，遍历预设相机位置，逐个采集性能数据（FPS Chart、Insights Trace、CSV Profiler）
- **材质性能测试**：自动加载材质列表，在固定场景中逐个渲染并采集 GPU 开销
- **关卡序列测试**：自动播放 Sequencer 序列，按镜头切换采集性能数据
- **回放测试**：自动播放录制的回放文件，在回放过程中采集性能数据
- **ProfileGo 测试**：集成 ProfileGo 系统，支持基于场景（Scenario）的灵活脚本化测试

所有测试支持自动截图、Insights Trace、CSV 导出、FPS Chart、视频录制等采集手段，并通过 Gauntlet 框架与 CI/CD 管线集成。

## 使用场景

- 你在 CI/CD 管线中需要自动化验证每个构建版本的帧率表现 → 使用 Gauntlet + 此插件的静态相机测试
- 你需要批量测试项目中数十种材质的渲染性能 → 使用材质性能测试控制器
- 你需要验证 Sequencer 过场动画播放时的性能 → 使用序列性能测试控制器
- 你需要在固定脚本路径上反复采集性能数据用于回归对比 → 使用 ProfileGo 测试
- 你需要通过回放文件重现真实游戏场景并采集性能 → 使用回放性能测试控制器

## 蓝图用法

### 核心节点

#### 测试生命周期接口（IAutomatedPerfTestInterface）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetupTest` | 测试初始化阶段，可蓝图实现 | `IAutomatedPerfTestInterface` |
| `RunTest` | 执行测试逻辑 | `IAutomatedPerfTestInterface` |
| `TeardownTest` | 测试清理阶段 | `IAutomatedPerfTestInterface` |
| `Exit` | 退出测试 | `IAutomatedPerfTestInterface` |

#### 游戏模式基类（蓝图可继承）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetupTest` | 蓝图可实现的测试设置 | `AAutomatedPerfTestGameModeBase` |
| `RunTest` | 蓝图可实现的测试运行 | `AAutomatedPerfTestGameModeBase` |
| `TeardownTest` | 蓝图可实现的测试清理 | `AAutomatedPerfTestGameModeBase` |
| `Exit` | 蓝图可实现的退出逻辑 | `AAutomatedPerfTestGameModeBase` |

#### 基础控制器

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetTestName` | 获取当前测试名称 | `UAutomatedPerfTestControllerBase` |
| `GetTestID` | 获取当前测试唯一 ID | `UAutomatedPerfTestControllerBase` |
| `GetPerfTestTypeID` | 获取性能测试类型标识（虚函数，子类重写） | `UAutomatedPerfTestControllerBase` |
| `RequestsInsightsTrace` | 查询是否请求了 Insights Trace | `UAutomatedPerfTestControllerBase` |
| `RequestsCSVProfiler` | 查询是否请求了 CSV Profiler | `UAutomatedPerfTestControllerBase` |
| `RequestsFPSChart` | 查询是否请求了 FPS Chart | `UAutomatedPerfTestControllerBase` |
| `RequestsVideoCapture` | 查询是否请求了视频录制 | `UAutomatedPerfTestControllerBase` |
| `TakeScreenshot` | 拍摄截图并保存 | `UAutomatedPerfTestControllerBase` |
| `ConsoleCommand` | 执行控制台命令 | `UAutomatedPerfTestControllerBase` |

#### 配置查询节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetMapFromAssetName` | 根据资产名获取关卡 SoftObjectPath | `UAutomatedStaticCameraPerfTestProjectSettings` |
| `GetComboFromTestName` | 根据测试名获取关卡/序列组合 | `UAutomatedSequencePerfTestProjectSettings` |
| `GetReplayPathFromName` | 根据回放名获取回放文件路径 | `UAutomatedReplayPerfTestProjectSettings` |

#### ProfileGo 子系统

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetStatusMessage` | 获取当前 ProfileGo 状态消息 | `UProfileGoSubsystem` |
| `IsRunning` | 查询 ProfileGo 是否正在运行 | `UProfileGoSubsystem` |
| `HasEncounteredError` | 查询是否遇到错误 | `UProfileGoSubsystem` |

### 使用示例（蓝图描述）

**自定义静态相机性能测试：**

1. 创建一个蓝图类，父类选择 `UAutomatedStaticCameraPerfTestBase`
2. 在项目设置 `Plugins > Static Cameras` 中配置 `MapsToTest`（要测试的关卡列表）、`WarmUpTime`、`SoakTime`、`CooldownTime`
3. 在关卡中放置 `AAutomatedPerfTestStaticCamera` 类型的相机演员，插件会自动收集这些相机位置
4. 通过 Gauntlet 框架启动测试，控制器会自动遍历每个相机位置，执行暖机→采集→冷却流程

**自定义材质性能测试：**

1. 在项目设置 `Plugins > Materials` 中配置 `MaterialsToTest`（要测试的材质列表）
2. 设置 `MaterialPerformanceTestMap`（测试用关卡）和 `MaterialPlate`（材质展示网格体）
3. 插件自动打开测试关卡，逐个加载材质并采集 GPU 性能数据

**通过 GameMode 实现蓝图测试逻辑：**

1. 创建蓝图游戏模式，父类选择 `AAutomatedPerfTestGameModeBase`
2. 重写 `SetupTest`：放置测试用的 Actor、加载关卡内容
3. 重写 `RunTest`：执行实际测试逻辑
4. 重写 `TeardownTest`：清理资源
5. 重写 `Exit`：退出游戏

## C++ 用法

### 头文件引入

```cpp
#include "AutomatedPerfTestControllerBase.h"
#include "AutomatedStaticCameraPerfTestBase.h"
#include "AutomatedMaterialPerfTest.h"
#include "AutomatedSequencePerfTest.h"
#include "AutomatedProfileGoTest.h"
#include "AutomatedReplayPerfTest.h"
#include "ProfileGo.h"
#include "ProfileGoSubsystem.h"
```

### 基本用法

**创建自定义性能测试控制器**（基于源码结构推断的标准模式）：

```cpp
// MyPerfTestController.h
#pragma once

#include "AutomatedPerfTestControllerBase.h"
#include "MyPerfTestController.generated.h"

UCLASS()
class UMyPerfTestController : public UAutomatedPerfTestControllerBase
{
    GENERATED_BODY()

public:
    virtual FString GetPerfTestTypeID() const override
    {
        return TEXT("MyCustomPerfTest");
    }

    virtual void GatherTestMetadata(TArray<TPair<FString, FString>>& OutMetadata) const override
    {
        Super::GatherTestMetadata(OutMetadata);
        // 添加自定义元数据
        OutMetadata.Add({TEXT("TestMap"), TEXT("MyTestMap")});
    }

    virtual void SetupTest() override
    {
        Super::SetupTest();
        // 自定义初始化逻辑
    }

    virtual void RunTest() override
    {
        Super::RunTest();
        // 执行测试
        // ...
        // 完成后调用 EndTestSuccess() 或 EndTestFailure()
        EndTestSuccess();
    }
};
```

### 进阶用法

**集成 ProfileGo 场景化测试**（参考 `UAutomatedProfileGoTest` 和 `UProfileGoSubsystem` 的使用模式）：

```cpp
// 在自定义 GameMode 或测试控制器中启动 ProfileGo
void AMyTestGameMode::RunTest()
{
    UWorld* World = GetWorld();
    UProfileGoSubsystem* ProfileGoSubsystem = World->GetSubsystem<UProfileGoSubsystem>();
    
    if (ProfileGoSubsystem)
    {
        // 设置测试控制器引用
        ProfileGoSubsystem->SetTestController(this);
        
        // 注册回调
        ProfileGoSubsystem->OnPassEnded().AddUObject(this, &AMyTestGameMode::OnProfileGoPassEnded);
        ProfileGoSubsystem->OnScenarioStarted().AddUObject(this, &AMyTestGameMode::OnScenarioStarted);
        
        // 启动 ProfileGo 测试（使用默认 UProfileGo 类，指定场景名）
        ProfileGoSubsystem->Run<UProfileGo>(TEXT("MyScenario"), TEXT(""));
    }
}

void AMyTestGameMode::OnScenarioStarted(const FString& ScenarioName)
{
    UE_LOG(LogAutomatedPerfTest, Log, TEXT("Scenario started: %s"), *ScenarioName);
}

void AMyTestGameMode::OnProfileGoPassEnded()
{
    EndTestSuccess();
}
```

**配置自定义 ProfileGo 场景和命令**（参考 `UProfileGo` 的 JSON 加载能力）：

```cpp
// 在项目设置或 JSON 文件中定义场景
// 也可通过代码动态添加
void AMyTestGameMode::ConfigureProfileGoScenarios()
{
    UProfileGoSubsystem* Sub = GetWorld()->GetSubsystem<UProfileGoSubsystem>();
    
    // 加载预定义的场景配置
    Sub->LoadFromJSON(TEXT("Config/ProfileGo/MyScenarios.json"));
    
    // 或通过 CDO 直接操作
    UProfileGo& ProfileGo = UProfileGo::GetCDO();
    
    FProfileGoScenarioAPT Scenario;
    Scenario.Name = TEXT("MyScenario");
    Scenario.Position = FVector(1000, 2000, 300);
    Scenario.Orientation = FRotator(0, 90, 0);
    Scenario.OnBegin = TEXT("stat fps; stat unit");
    Scenario.OverrideCommands = TEXT("");
    Scenario.OnEnd = TEXT("stat none");
    
    // 可以动态注册自定义命令处理器
    // RegisterCommandDelegate / RegisterGeneratedScenarioDelegate
}
```

**使用 Insights Trace 和 CSV Profiler 采集数据**（参考 `UAutomatedPerfTestControllerBase` 的采集 API）：

```cpp
void UMyPerfTestController::RunTest()
{
    // 手动控制采集流程
    if (RequestsInsightsTrace())
    {
        TryStartInsightsTrace();
    }
    
    if (RequestsCSVProfiler())
    {
        // 自定义文件名和目标目录
        TryStartCSVProfiler(TEXT("MyPerfTest"), TEXT(""), 300); // 采集300帧
    }
    
    if (RequestsFPSChart())
    {
        TryStartFPSChart();
    }
    
    if (RequestsVideoCapture())
    {
        TryStartVideoCapture();
    }
    
    // ... 执行测试 ...
    
    // 停止采集
    TryStopInsightsTrace();
    TryStopCSVProfiler();
    TryStopFPSChart();
    TryFinalizingVideoCapture();
}
```

## Demo 示例

以下是一个完整的自定义静态相机性能测试控制器实现：

```cpp
// CustomStaticCameraPerfTest.h
#pragma once

#include "StaticCameraTests/AutomatedStaticCameraPerfTestBase.h"
#include "CustomStaticCameraPerfTest.generated.h"

UCLASS()
class UCustomStaticCameraPerfTest : public UAutomatedStaticCameraPerfTestBase
{
    GENERATED_BODY()

public:
    virtual FString GetPerfTestTypeID() const override
    {
        return TEXT("CustomStaticCameraTest");
    }

    virtual void GatherTestMetadata(TArray<TPair<FString, FString>>& OutMetadata) const override
    {
        Super::GatherTestMetadata(OutMetadata);
        // 添加关卡相关元数据
        OutMetadata.Add({TEXT("TestType"), TEXT("StaticCamera")});
    }

    // 可选：覆盖相机收集逻辑
    virtual TArray<ACameraActor*> GetMapCameraActors() override
    {
        // 使用基类逻辑收集 AAutomatedPerfTestStaticCamera 和关卡中放置的相机
        return Super::GetMapCameraActors();
    }
};
```

```cpp
// CustomStaticCameraPerfTest.cpp
#include "CustomStaticCameraPerfTest.h"

// 基类已实现了完整的测试流程：
// SetupTest() → 遍历地图列表
// RunTest() → SetUpNextCamera() → [WarmUp] → MarkCameraStart() → [Soak] → 
//              MarkCameraEnd() → EvaluateCamera() → [Cooldown] → ScreenshotCamera() → FinishCamera() → 下一个相机
// 每个阶段的时间由项目设置中的 WarmUpTime/SoakTime/CooldownTime 控制
```

## 模块依赖

该插件依赖以下插件（在 `.uplugin` 中声明）：

| 插件 | 用途 |
|---|---|
| `Gauntlet` | UE 自动化测试框架，提供 `UGauntletTestController` 基类和测试生命周期管理 |
| `ProjectLauncher` | 项目启动器，用于通过命令行启动测试目标平台 |

无特殊模块依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 到 float 截断的编译警告 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复格式化函数中作用域枚举导致的乱码输出 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符与参数不匹配的问题 |
| 2026-04-15 | `e1420e00` | Automation: Only set OutputPath if we're not setting an ArtifactsPath. This means that we can easily | 修复输出路径和 ArtifactsPath 的冲突逻辑 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 日志宏 |

### 维护评价

- **创建时间**：2024 年 5 月，是一个相对较新的插件
- **实验性标记**：`.uplugin` 中 `IsExperimentalVersion=true`，仍处于实验阶段
- **近期更新**：2026 年 4-5 月有密集的代码质量修复（编译警告、格式化问题、日志迁移），表明仍在活跃维护
- **功能状态**：核心功能完整（静态相机、材质、序列、回放、ProfileGo 五种测试类型），但作为实验性功能可能仍有 API 变动
- **CI/CD 集成**：通过 Gauntlet 框架天然支持 CI/CD 管线集成

**推荐使用**：适合需要自动化性能回归测试的团队，尤其是在 CI/CD 管线中集成性能验证的场景。由于是实验性插件，建议在正式生产环境中使用前充分测试，并关注 API 可能的变动。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Performance/AutomatedPerfTesting)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Performance/AutomatedPerfTesting/Tests)（如果有）