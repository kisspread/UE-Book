# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（MetaHuman 面部动画资产、配置数据、求解器模板） |
| 模块 | `MetaHumanFaceAnimationSolver` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕（约 N 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 为 MetaHuman（数字人）技术提供的官方工具包。该插件的核心目的是**将真实的人类面部表演（如演员的表演捕捉数据）转换为可驱动 MetaHuman 数字角色的高质量动画**。它不仅仅是一个简单的映射工具，而是一个包含数据捕获、处理、求解、转换和编辑的完整管线（Pipeline）。

`MetaHumanFaceAnimationSolver` 模块是此管线中的关键组件，它是一个**面部动画求解器**。其作用是将追踪到的面部特征点或深度数据（来自捕获源）转换为 MetaHuman 骨骼网格体的变形目标（Blend Shapes）或控制参数，从而驱动数字人的面部表情。它负责配置和管理求解过程，例如是否使用深度图、牙齿模式、平滑度等参数，以确保最终动画的质量和准确性。

## 使用场景

-   **虚拟制片/电影制作**：需要将演员的实时或录制的面部表演，高保真地应用于虚拟 MetaHuman 角色，用于实时虚拟制作或后期动画生成。
-   **游戏开发**：为游戏内的 MetaHuman NPC 或玩家角色制作丰富的面部表情动画。
-   **数字内容创作**：创建用于社交媒体、营销或虚拟偶像的数字人内容，其中面部动画是核心。
-   **批量处理**：使用 `MetaHumanBatchProcessor` 模块对大量预先录制的捕获数据进行自动化动画求解。
-   **面部动画定制**：当默认的求解结果不满足特定艺术要求时，通过覆盖求解器的配置（如深度图影响、眼睛平滑度）来精细调整动画输出。

## 蓝图用法

`MetaHumanFaceAnimationSolver` 主要作为配置资产在编辑器中使用。它的属性主要通过细节面板进行编辑，而非通过蓝图节点调用。

### 核心属性

| 属性 | 说明 | 类型 |
|---|---|---|
| `bOverrideDeviceConfig` | 是否覆盖全局设备配置。 | `bool` |
| `DeviceConfig` | 指定用于此求解器的 `MetaHumanConfig` 资产。 | `UMetaHumanConfig*` |
| `bOverrideDepthMapInfluence` | 是否覆盖深度图影响设置。 | `bool` |
| `DepthMapInfluence` | 深度图对最终求解结果的影响程度（`None`, `Low`, `High`）。 | `EDepthMapInfluenceValue` |
| `bOverrideEyeSolveSmoothness` | 是否覆盖眼睛求解平滑度。 | `bool` |
| `EyeSolveSmoothness` | 应用于眼睛视线控制的平滑程度（0.0 - 1.0）。 | `float` |
| `bOverrideTeethMode` | 是否覆盖牙齿模式。 | `bool` |
| `TeethMode` | 牙齿动画的生成方式（使用追踪点 `TrackingPoints` 或由程序估算 `Estimated`）。 | `ETeethMode` |

### 使用示例（蓝图/编辑器描述）

1.  **创建求解器资产**：在内容浏览器中右键 -> `Animation` -> `MetaHuman Face Animation Solver` 创建一个新的求解器资产。
2.  **配置求解器**：在资产的细节面板中，勾选 `bOverrideDeviceConfig` 并指定一个 `MetaHumanConfig` 资产，该资产定义了捕获设备（如 iPhone 的摄像头参数）。
3.  **调整参数**：根据需要覆盖其他参数，如将 `DepthMapInfluence` 设置为 `High` 以增加深度信息对结果的影响，或者调整 `EyeSolveSmoothness` 让眼神动作更平滑。
4.  **在管线中使用**：在 MetaHuman Animator 的处理管线（如 `MetaHumanPipeline`）中，将此配置好的求解器资产指定给相应的求解步骤。当处理捕获数据时，求解器将使用这些配置来生成动画。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanFaceAnimationSolver.h"
```

### 基本用法

创建和配置一个面部动画求解器实例。
```cpp
// 创建求解器对象
UMetaHumanFaceAnimationSolver* Solver = NewObject<UMetaHumanFaceAnimationSolver>();

// 配置求解器参数
Solver->bOverrideDepthMapInfluence = true;
Solver->DepthMapInfluence = EDepthMapInfluenceValue::High;

Solver->bOverrideEyeSolveSmoothness = true;
Solver->EyeSolveSmoothness = 0.3f;

Solver->bOverrideTeethMode = true;
Solver->TeethMode = ETeethMode::Estimated;

// 检查求解器是否可以处理数据
if (Solver->CanProcess())
{
    // 求解器配置有效，可以用于处理管线
}
```

### 进阶用法

获取求解器生成的配置数据，用于传递给底层的本地求解器库。
```cpp
UMetaHumanFaceAnimationSolver* Solver = /* 已配置的求解器 */;
UCaptureData* CaptureData = /* 某份捕获数据 */;

// 获取用于配置底层求解器的模板数据（JSON字符串）
FString SolverTemplateData = Solver->GetSolverTemplateData(CaptureData);
// 获取求解器配置数据
FString SolverConfigData = Solver->GetSolverConfigData(CaptureData);
// ... 获取其他类型的数据

// 使用获取到的数据（例如，传递给本地计算库）
bool bSuccess = SomeLocalSolvingFunction(SolverConfigData, SolverTemplateData);
```

## Demo 示例

一个最小化的 C++ 示例，展示如何创建和配置一个 `UMetaHumanFaceAnimationSolver` 对象。

```cpp
// MetaHumanFaceAnimationSolverDemo.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "MetaHumanFaceAnimationSolverDemo.generated.h"

UCLASS()
class UMetaHumanFaceAnimationSolverDemoSubsystem : public UGameInstanceSubsystem
{
	GENERATED_BODY()

public:
	virtual void Initialize(FSubsystemCollectionBase& Collection) override;
	virtual void Deinitialize() override;

private:
	UPROPERTY()
	TObjectPtr<class UMetaHumanFaceAnimationSolver> Solver;
};
```

```cpp
// MetaHumanFaceAnimationSolverDemo.cpp
#include "MetaHumanFaceAnimationSolverDemo.h"
#include "MetaHumanFaceAnimationSolver.h" // 包含求解器头文件

void UMetaHumanFaceAnimationSolverDemoSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
	Super::Initialize(Collection);

	// 创建求解器实例
	Solver = NewObject<UMetaHumanFaceAnimationSolver>(this);

	// 配置一个自定义的求解器设置
	Solver->bOverrideEyeSolveSmoothness = true;
	Solver->EyeSolveSmoothness = 0.5f; // 设置一个中等程度的眼睛平滑
	Solver->bOverrideTeethMode = true;
	Solver->TeethMode = ETeethMode::Estimated; // 使用估算模式处理牙齿

	// 验证配置
	if (Solver->CanProcess())
	{
		UE_LOG(LogTemp, Log, TEXT("MetaHuman Face Animation Solver is configured and ready."));
		// 在实际应用中，可以将 `Solver` 对象设置到某个处理组件或缓存起来
	}
	else
	{
		UE_LOG(LogTemp, Warning, TEXT("MetaHuman Face Animation Solver configuration is incomplete."));
	}
}

void UMetaHumanFaceAnimationSolverDemoSubsystem::Deinitialize()
{
	Solver = nullptr;
	Super::Deinitialize();
}
```

## 模块依赖

`MetaHumanFaceAnimationSolver` 模块自身没有列出独特的公共依赖。根据其所在插件 `MetaHumanAnimator` 的整体结构，它很可能依赖 `MetaHumanCore` 等基础模块，但这些属于插件内部依赖。对于插件使用者而言，**无特殊依赖（仅标准 Core/Engine/Slate 等）**。如果要使用 `MetaHumanConfig` 资产，你的模块需要依赖 `MetaHumanConfig`。

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | 提供核心的面部求解和处理算法（可能为二进制库）。 |
| `MetaHumanCaptureData` | 处理捕获的音频、视频、深度图数据。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时，禁用关卡序列导出，避免功能冲突。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 上的渲染伪影问题。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 在身体追踪模式下过滤可视化对象，优化显示。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 新增功能：支持为已有的网格体导出动画序列。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 的缓存问题，提升稳定性。 |

### 维护评价

MetaHuman Animator 是 Epic Games **官方维护**的旗舰级 MetaHuman 工具集，属于**活跃维护**状态。从最近的提交记录看，更新非常频繁（每日甚至每日多次），内容涵盖功能增强、Bug 修复和渲染优化，表明其开发处于高度活跃期。

`MetaHumanFaceAnimationSolver` 作为其核心模块，随着主插件一起获得持续更新。该插件是 MetaHuman 工作流的核心部分，对于任何需要制作高质量数字人动画的项目都至关重要，**强烈推荐使用**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanFaceAnimationSolver)
- [官方文档]() （当前 .uplugin 未提供 DocsURL，建议查阅 Epic 官方 MetaHuman 文档中心）
- [测试用例]() （当前分析未提供测试文件路径）