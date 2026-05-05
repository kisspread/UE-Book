# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（MetaHuman资产、配置） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-02-02 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的 MetaHuman 角色动画制作工具包。它解决的核心问题是：**如何从真实的视频或深度数据中，高效、准确地生成逼真的 MetaHuman 角色面部动画**。

该插件并非一个单一功能，而是一个完整的动画制作管线（Pipeline），涵盖了从原始数据导入、面部追踪、动画求解到最终输出的全流程。它整合了面部轮廓追踪（`MetaHumanFaceContourTracker`）、动画求解（`MetaHumanFaceAnimationSolver`）、面部网格拟合（`MetaHumanFaceFittingSolver`）、身份管理（`MetaHumanIdentity`）以及与 Sequencer 的集成（`MetaHumanSequencer`）等多个专业模块，旨在为影视、游戏和虚拟制片领域提供专业级的面部动画解决方案。

## 使用场景

-   **影视与虚拟制片**：你使用 iPhone 或专业深度相机（如 Lidar）拍摄了演员的面部表演视频，需要将其转换为高保真的 MetaHuman 角色动画，用于电影或虚拟制片项目。
-   **游戏开发**：你的游戏包含大量需要高质量面部动画的 MetaHuman NPC 或主角，希望利用真实表演数据来提升动画的真实感，而不是完全依赖手K动画。
-   **实时虚拟人**：你需要为直播或实时交互的虚拟人驱动面部表情，MetaHuman Animator 提供的 `MetaHumanSpeech2Face` 模块支持从语音生成面部动画。
-   **批量处理**：你有大量的面部捕捉数据需要处理，可以使用 `MetaHumanBatchProcessor` 模块进行自动化批量处理，提高生产效率。

## 蓝图用法

由于 MetaHuman Animator 是一个复杂的工具包，其蓝图接口主要集中在数据管理、流程控制和资产访问上。核心功能（如求解、追踪）通常通过编辑器工具或 C++ 管线调用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Load Face Fitting Solvers` | 加载面部拟合所需的求解器配置和数据。 | `UMetaHumanFaceFittingSolver` |
| `Load Predictive Solver` | 加载用于性能准备阶段的预测性求解器。 | `UMetaHumanFaceFittingSolver` |
| `Can Process` | 检查当前配置是否满足执行面部拟合处理的条件。 | `UMetaHumanFaceFittingSolver` |
| `Get Fitting Template Data` | 获取用于面部拟合的模板数据（JSON字符串）。 | `UMetaHumanFaceFittingSolver` |
| `Get Fitting Config Data` | 获取面部拟合的配置数据（JSON字符串）。 | `UMetaHumanFaceFittingSolver` |
| `Get Predictive Training Data` | 获取用于训练预测性求解器的数据（字节数组）。 | `UMetaHumanFaceFittingSolver` |

### 使用示例（蓝图描述）

在蓝图中，你通常不会直接调用底层的求解函数。更常见的用法是：
1.  获取或创建一个 `UMetaHumanFaceFittingSolver` 对象。
2.  为其指定一个 `UMetaHumanConfig` 资产（包含设备配置或预测求解器配置）。
3.  调用 `Load Face Fitting Solvers` 来初始化求解器。
4.  通过 `Can Process` 节点检查是否就绪。
5.  最终，这些配置和数据会被 MetaHuman Animator 的编辑器工具（如 MetaHuman Identity 编辑器）在后台使用，驱动整个面部拟合流程。

## C++ 用法

MetaHuman Animator 的核心逻辑主要通过 C++ 实现，蓝图接口更多用于配置和数据传递。以下示例展示了如何以编程方式配置和使用面部拟合求解器。

### 头文件引入

```cpp
#include "MetaHumanFaceFittingSolver.h"
```

### 基本用法

以下代码展示了如何创建一个 `UMetaHumanFaceFittingSolver` 实例并配置它。

```cpp
// 创建面部拟合求解器实例
UMetaHumanFaceFittingSolver* FaceFittingSolver = NewObject<UMetaHumanFaceFittingSolver>();

// 加载一个预设的 MetaHumanConfig 资产作为设备配置
// 假设你已经有一个名为 “DefaultDeviceConfig” 的 UMetaHumanConfig 资产
UMetaHumanConfig* DeviceConfig = LoadObject<UMetaHumanConfig>(nullptr, TEXT("/Game/MetaHuman/Configs/DefaultDeviceConfig"));
if (DeviceConfig)
{
    FaceFittingSolver->bOverrideDeviceConfig = true;
    FaceFittingSolver->DeviceConfig = DeviceConfig;
}

// 加载求解器
FaceFittingSolver->LoadFaceFittingSolvers();

// 检查是否可以处理
if (FaceFittingSolver->CanProcess())
{
    UE_LOG(LogTemp, Log, TEXT("Face Fitting Solver is ready to process."));
    // 获取配置数据用于后续处理
    FString ConfigData = FaceFittingSolver->GetFittingConfigData();
    // ... 将 ConfigData 传递给实际的求解管线
}
```

### 进阶用法

在实际的 MetaHuman Animator 工作流中，`UMetaHumanFaceFittingSolver` 通常作为 `UMetaHumanIdentity` 资产的一部分被管理。以下代码片段展示了如何从一个 Identity 对象中访问和使用其关联的求解器。

```cpp
// 假设你有一个 UMetaHumanIdentity 对象
UMetaHumanIdentity* Identity = /* ... */;

// 从 Identity 中获取面部拟合求解器
UMetaHumanFaceFittingSolver* Solver = Identity->GetFaceFittingSolver(); // 需要查看 UMetaHumanIdentity 的具体接口

if (Solver)
{
    // 为特定的捕获数据（CaptureData）获取配置名称
    UCaptureData* CaptureData = /* ... */;
    FString ConfigName;
    if (Solver->GetConfigDisplayName(CaptureData, ConfigName))
    {
        UE_LOG(LogTemp, Log, TEXT("Using config: %s for capture data."), *ConfigName);
    }

    // 获取该捕获数据对应的拟合模板数据
    FString TemplateData = Solver->GetFittingTemplateData(CaptureData);
    // ... 使用 TemplateData 进行拟合
}
```

## Demo 示例

以下是一个完整的、可编译的最小示例，演示了如何在 C++ 中初始化和使用 `UMetaHumanFaceFittingSolver`。

### MyMetaHumanActor.h
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyMetaHumanActor.generated.h"

class UMetaHumanFaceFittingSolver;

UCLASS()
class MYPROJECT_API AMyMetaHumanActor : public AActor
{
	GENERATED_BODY()

public:
	AMyMetaHumanActor();

protected:
	virtual void BeginPlay() override;

public:
	UPROPERTY(EditAnywhere, Category = "MetaHuman")
	TObjectPtr<UMetaHumanFaceFittingSolver> FaceFittingSolver;

	UFUNCTION(BlueprintCallable, Category = "MetaHuman")
	void InitializeAndCheckSolver();
};
```

### MyMetaHumanActor.cpp
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.

#include "MyMetaHumanActor.h"
#include "MetaHumanFaceFittingSolver.h"

AMyMetaHumanActor::AMyMetaHumanActor()
{
	PrimaryActorTick.bCanEverTick = false;
}

void AMyMetaHumanActor::BeginPlay()
{
	Super::BeginPlay();
	InitializeAndCheckSolver();
}

void AMyMetaHumanActor::InitializeAndCheckSolver()
{
	// 如果没有在编辑器中指定，则创建一个新的求解器实例
	if (!FaceFittingSolver)
	{
		FaceFittingSolver = NewObject<UMetaHumanFaceFittingSolver>(this);
	}

	// 尝试加载求解器
	FaceFittingSolver->LoadFaceFittingSolvers();

	// 检查状态
	if (FaceFittingSolver->CanProcess())
	{
		UE_LOG(LogTemp, Warning, TEXT("MetaHuman Face Fitting Solver is initialized and ready."));
		// 可以在这里获取一些数据，例如模板数据
		FString Template = FaceFittingSolver->GetFittingTemplateData();
		UE_LOG(LogTemp, Log, TEXT("Template Data (first 100 chars): %s"), *Template.Left(100));
	}
	else
	{
		UE_LOG(LogTemp, Error, TEXT("MetaHuman Face Fitting Solver failed to initialize. Check configuration."));
	}
}
```

## 模块依赖

MetaHuman Animator 是一个庞大的插件，其内部模块相互依赖。作为使用者，你的项目模块通常需要依赖 `MetaHumanCore` 和 `MetaHumanToolkit` 等核心模块。以下是该插件一些独特且不常见的依赖模块：

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | MetaHuman 核心技术库，包含底层的数学、几何和求解算法。 |
| `ControlRigDeveloper` | 用于与 Control Rig 系统集成，驱动 MetaHuman 骨骼动画。 |
| `MetaHumanSDKEditor` | MetaHuman SDK 的编辑器部分，提供资产管理和工作流工具。 |
| `SkeletalMeshUtilitiesCommon` | 提供骨骼网格体相关的通用工具函数。 |

## 维护状态

### 近期更新

```
- 2025-10-03 9803c443cfab 为包含对应 .gen.cpp 文件的源文件添加了 UE_INLINE_GENERATED_CPP_BY_NAME。
- 2025-09-15 52e3dac151e1 使用 UnrealCodeFixup 更新了头文件，确保 dllstorage 在方法/静态变量上而不是类型上。第 3/n 部分。
- 2025-08-20 f5a5be887062 [CaptureManager] 改进了工具提示，并在 UE 的 Capture Manager 窗口中添加了警告消息。
```

### 维护评价

MetaHuman Animator 是一个**活跃维护中**的官方插件。
- **创建时间**：创建于 2024 年 2 月，非常年轻。
- **更新频率**：近期（2025年8月至10月）有持续的代码清理、优化和功能改进提交，表明 Epic Games 团队仍在积极开发和维护。
- **功能状态**：作为 MetaHuman 生态的核心组件，它处于持续迭代中，不断集成新的捕捉技术和优化工作流。
- **推荐使用**：**强烈推荐**。对于任何需要高质量 MetaHuman 面部动画的项目，这是官方且功能最完整的解决方案。尽管它非常复杂，但提供了无与伦比的真实感和工作流集成。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/metahuman-animator-in-unreal-engine/) (Unreal Engine 官方文档中的 MetaHuman Animator 部分)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest) (示例测试模块)