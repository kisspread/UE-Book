# AutomatedPerfTesting

> This plugin provides Gauntlet Test Controllers to facilitate automatic performance testing.

| 属性 | 值 |
|---|---|
| 中文名 | 自动化性能测试 |
| 分类 | Testing |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（项目设置、蓝图接口、测试场景资产） |
| 模块 | `AutomatedPerfTesting` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-05-23 |
| 年龄标签 | 👴 老古董（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Performance/AutomatedPerfTesting) | |

## 用途

此插件为 Unreal Engine 的 **Gauntlet 测试框架** 提供了一系列即开即用的“测试控制器”（Test Controllers），用于自动化执行各种性能基准测试。它解决的核心问题是：**将手动的、重复性的性能测试流程（如定点截图、材质评估、序列回放）自动化，从而能够轻松地集成到持续集成/持续交付 (CI/CD) 流水线中，进行定期的性能回归测试。** 它不仅仅是一个测试工具，更是一套可扩展的框架，允许开发者基于它快速构建和定制针对项目特定需求的性能测试场景。

## 使用场景

- **持续集成性能门禁**：你的团队希望在代码提交或构建后自动运行一套性能基准测试，确保关键场景的帧率、加载时间等指标不出现回退。使用此插件可以配置一个 Gauntlet 测试，在 CI 服务器上自动启动游戏，运行预设的静态相机测试或 ProfileGo 场景，并收集 CSV、Insights 数据或 FPS 图表。
- **材质与着色器性能评估**：美术团队需要评估一系列新材质在特定硬件下的性能表现。可以使用 `AutomatedMaterialPerfTest` 控制器，批量加载预设的材质列表，在固定场景下对每个材质进行计时性能数据采集，并可选地截屏用于视觉比对。
- **过场动画性能验证**：使用 `AutomatedSequencePerfTest` 控制器，可以自动加载关卡并播放预设的过场动画序列，精确测量序列播放期间的性能开销，特别是针对相机切换等关键点。
- **自定义复杂性能场景**：使用 `AutomatedProfileGoTest` 控制器，可以利用 ProfileGo 框架编排复杂的测试剧本，例如将角色传送到多个指定位置、执行一系列控制台命令（如切换光照模式、生成特定物体）、等待资源流送完成等，实现高度可定制的长周期性能测试。

## 蓝图用法

插件主要通过 C++ 提供测试控制器，但部分项目设置和接口可在蓝图中使用。

### 核心节点与配置

| 节点/配置 | 说明 | 所在类/设置 |
|---|---|---|
| `SetupTest` | 初始化测试环境，蓝图可实现事件 | `IAutomatedPerfTestInterface` |
| `RunTest` | 执行主要测试逻辑，蓝图可实现事件 | `IAutomatedPerfTestInterface` |
| `TeardownTest` | 清理测试环境，蓝图可实现事件 | `IAutomatedPerfTestInterface` |
| `Exit` | 请求退出测试，蓝图可实现事件 | `IAutomatedPerfTestInterface` |
| `GetTestID` | 获取当前测试的唯一标识符 | `UAutomatedPerfTestSubsystem` |
| `GetReplayPathFromName` | 根据回放名称查找回放文件路径 | `UAutomatedReplayPerfTestProjectSettings` |
| `GetComboFromTestName` | 根据组合名称查找地图/序列组合 | `UAutomatedSequencePerfTestProjectSettings` |
| `GetMapFromAssetName` | 根据资产名称查找地图软引用 | `UAutomatedStaticCameraPerfTestProjectSettings` |

### 使用示例（蓝图描述）

**场景1：使用自定义 GameMode 实现接口**
1. 创建一个继承自 `AAutomatedPerfTestGameModeBase` 的蓝图 GameMode。
2. 在该蓝图 GameMode 中，重写 `Setup Test`、`Run Test` 等事件。在 `Run Test` 中，你可以放置自己的性能测试逻辑，例如生成物体、播放动画等。
3. 将此 GameMode 设置为项目在运行自动化性能测试时使用的模式（通过命令行参数或项目设置）。
4. 当通过 Gauntlet 框架启动测试时，你的蓝图逻辑将被自动调用。

**场景2：配置静态相机测试**
1. 打开“项目设置” > “Plugins” > “Automated Performance Testing | Static Camera”。
2. 在 `Maps To Test` 数组中，添加你想要测试的地图资产。
3. 配置 `Warm Up Time`（预热时间）、`Soak Time`（测试时长）、`Cooldown Time`（冷却时间）等参数。
4. 启用 `Capture Screenshots` 可以在每个相机测试点后截取屏幕快照。
5. 在需要测试的地图中放置 `AAutomatedPerfTestStaticCamera` 或普通 `ACameraActor`。对于前者，你可以设置其 `Collection Name` 以进行分组。
6. 当通过 `AutomatedStaticCameraPerfTest` 控制器运行测试时，它会自动遍历所有配置的地图和相机位置。

## C++ 用法

### 头文件引入

```cpp
#include "AutomatedPerfTestControllerBase.h"
// 选择需要的特定测试控制器头文件
#include "StaticCameraTests/AutomatedStaticCameraPerfTestBase.h"
#include "AutomatedMaterialPerfTest.h"
#include "ProfileGo/ProfileGoSubsystem.h"
```

### 基本用法：继承基类创建自定义测试控制器

以下是一个简单的自定义静态相机测试控制器示例，它继承自 `UAutomatedStaticCameraPerfTestBase` 并重写了获取相机列表的方法。
（来源：基于 `UAutomatedPlacedStaticCameraPerfTest` 和 `UAutomatedStaticCameraPerfTestBase` 的设计模式）

```cpp
// MyCustomStaticCameraTest.h
#pragma once
#include "StaticCameraTests/AutomatedStaticCameraPerfTestBase.h"
#include "MyCustomStaticCameraTest.generated.h"

UCLASS()
class MYPROJECT_API UMyCustomStaticCameraTest : public UAutomatedStaticCameraPerfTestBase
{
	GENERATED_BODY()

public:
	virtual TArray<ACameraActor*> GetMapCameraActors() override;
};
```

```cpp
// MyCustomStaticCameraTest.cpp
#include "MyCustomStaticCameraTest.h"

TArray<ACameraActor*> UMyCustomStaticCameraTest::GetMapCameraActors()
{
	// 默认实现在基类中，这里可以覆盖为自定义逻辑
	// 例如：只获取属于特定 Actor 标签的相机
	TArray<ACameraActor*> AllCameras = Super::GetMapCameraActors();
	
	AllCameras.RemoveAll([](ACameraActor* Cam)
	{
		// 过滤逻辑
		return !Cam->ActorHasTag(FName("PerfTestCam"));
	});
	
	return AllCameras;
}
```

### 进阶用法：使用 ProfileGo 子系统编排复杂场景

ProfileGo 提供了一种高度可配置的方式来编排测试步骤。

```cpp
// 在某个测试控制器或游戏模式中
#include "ProfileGo/ProfileGoSubsystem.h"

void UMyTestController::RunProfileGoScenario()
{
	// 获取世界的 ProfileGo 子系统
	if (UProfileGoSubsystem* ProfileGoSubsystem = GetWorld()->GetSubsystem<UProfileGoSubsystem>())
	{
		// 监听状态事件
		ProfileGoSubsystem->OnPassEnded().AddUObject(this, &UMyTestController::OnProfileGoPassEnded);
		
		// 运行一个名为 “MyHeavyScenario” 的预定义场景
		// 可以在项目设置 (UProfileGo) 或 JSON 文件中定义此场景
		ProfileGoSubsystem->Run(TEXT("MyHeavyScenario"), TEXT("-arg1 value1"));
	}
}

void UMyTestController::OnProfileGoPassEnded()
{
	// ProfileGo 测试通过结束
	EndTestSuccess();
}
```

## Demo 示例

一个最小的、可编译的自定义性能测试控制器，它在测试开始时打印一条消息。

```cpp
// SimplePerfTestController.h
#pragma once
#include "AutomatedPerfTestControllerBase.h"
#include "SimplePerfTestController.generated.h"

UCLASS()
class USimplePerfTestController : public UAutomatedPerfTestControllerBase
{
	GENERATED_BODY()

public:
	virtual void SetupTest() override
	{
		Super::SetupTest();
		UE_LOG(LogAutomatedPerfTest, Log, TEXT("SimplePerfTest: Setup complete. Starting test."));
	}

	virtual void RunTest() override
	{
		// 这里是执行性能测试的主要逻辑。
		// 例如：生成一些物体，等待一段时间测量性能。
		UE_LOG(LogAutomatedPerfTest, Log, TEXT("SimplePerfTest: Running performance workload..."));

		// 模拟工作负载
		FPlatformProcess::Sleep(5.0f);

		UE_LOG(LogAutomatedPerfTest, Log, TEXT("SimplePerfTest: Workload finished. Tearing down."));
		// 工作完成后，调用基类的结束测试方法
		EndTestSuccess();
	}
};
```

## 模块依赖

从 `.uplugin` 文件的 `Plugins` 节和插件功能推断，使用此插件时，你的项目或模块需要依赖以下插件/模块：

| 模块/插件 | 用途 |
|---|---|
| `Gauntlet` | 核心依赖，提供 `UGauntletTestController` 基类和测试运行框架 |
| `ProjectLauncher` | 用于支持在特定平台启动和运行测试 |
| `Automation` | UE 自动化测试框架，用于报告和收集测试结果 |
| `Insights` (Trace) | 用于控制 Unreal Insights 跟踪数据的采集 |
| `CSVProfiler` | 用于控制 CSV 性能分析器的启动和停止 |
| `MovieScene`, `LevelSequence` | 仅 `AutomatedSequencePerfTest` 需要，用于播放过场动画序列 |
| `Replay` | 仅 `AutomatedReplayPerfTest` 需要，用于播放和分析游戏回放 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点数时产生的编译器警告。 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了在格式化函数中使用作用域枚举可能导致垃圾输出的问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正了当参数为64位时，32位格式说明符应为64位，反之亦然的问题。 |
| 2026-04-15 | `e1420e00` | Automation: Only set OutputPath if we're not setting an ArtifactsPath. This means that we can easily | 优化自动化流程：仅当未设置 ArtifactsPath 时才设置 OutputPath，便于管理输出路径。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志输出从 UE_LOG 迁移至 UE_LOGF 宏。 |

### 维护评价

该插件创建于 2024 年 5 月，从 2026 年 4 月到 5 月有多次更新，但主要集中在 **代码规范修复和编译器警告处理**（如格式说明符、枚举输出、浮点模式），而非新功能的添加或性能特性的增强。

- **维护状态**：处于**维护性更新**阶段，修复已知代码问题，但没有活跃的功能开发迹象。
- **实验性**：`.uplugin` 中 `IsExperimentalVersion=true`，表明 Epic 官方将其视为实验性功能，API 和行为在后续版本中可能发生变化。
- **建议**：对于追求稳定性的生产项目，使用此插件需谨慎，并准备好在引擎版本升级时处理潜在的兼容性问题。对于内部测试、技术预研或工具链开发，它提供了一个非常强大且可扩展的自动化性能测试基础。**推荐在了解其实验性质的前提下使用。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Performance/AutomatedPerfTesting)
- [官方文档]() （.uplugin 中 DocsURL 为空，暂无官方文档链接）