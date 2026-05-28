# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（模型、动画资产、配置文件、工具） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-06-10 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 推出的官方 MetaHuman 工具套件，旨在将真实的表演数据（如 iPhone 的深度摄像头数据、手机视频或音频）转换为高质量的 MetaHuman 角色动画。它解决了将现实世界中的面部表演和身体动作“移植”到虚拟角色身上的问题，是创建逼真数字人动画的核心工作流程工具。

## 使用场景

- **电影/电视制作**：将演员的表演通过 iPhone 深度摄像头捕获，并将其应用到 MetaHuman 角色上，用于后期制作。
- **游戏开发**：快速为游戏中的 NPC 或主角创建逼真的面部动画和口型同步。
- **虚拟主播/数字人**：利用手机视频或音频流实时驱动虚拟形象，用于直播或虚拟客服。
- **动画预览**：在 Unreal Engine 中快速预览表演动画效果，用于创意迭代。

## 蓝图用法

由于 MetaHuman Animator 主要作为离线处理工具（Editor 工具），其核心功能通过编辑器 UI 暴露，而非蓝图节点。大部分操作在“MetaHuman Animator”编辑器窗口中完成。不过，插件提供了一些资产类型和配置项，可以在蓝图中引用和控制。

### 核心资产

| 资产类型 | 说明 |
|---|---|
| `UMetaHumanFaceFittingSolver` | 面部拟合求解器资产，定义如何将捕获的面部数据拟合到 MetaHuman 模型上。 |
| `UMetaHumanIdentity` | MetaHuman 身份资产，存储一个特定 MetaHuman 角色的所有绑定和配置。 |
| `UMetaHumanPerformance` | MetaHuman 表演资产，包含从捕获数据中提取的动画数据。 |

### 使用示例（蓝图描述）

1.  **加载表演**：在蓝图中，你可以使用 `LoadAsset` 节点加载一个 `UMetaHumanPerformance` 资产，并将其引用存储在一个变量中，以便后续控制动画播放。
2.  **应用到骨骼网格体**：通过获取 `UMetaHumanIdentity` 资产中绑定的骨骼网格体组件，你可以将表演资产中的动画数据应用到场景中的角色上。通常，这涉及到将表演资产设置为动画组件的动画源。

## C++ 用法

在 C++ 层面，插件提供了底层的数据处理和算法接口，主要用于实现自定义工具或深度集成。

### 头文件引入

```cpp
#include "MetaHumanFaceFittingSolver.h" // 面部拟合求解器
#include "MetaHumanIdentity.h"          // MetaHuman 身份资产
#include "MetaHumanPerformance.h"       // 表演数据资产
```

### 基本用法

以下示例展示如何以编程方式创建并配置一个面部拟合求解器资产（来源：`MetaHumanFaceFittingSolverEditor` 模块的工厂类）。

```cpp
// 创建一个新的 MetaHuman 面部拟合求解器资产
// 参考: MetaHumanFaceFittingSolverFactoryNew.h
UFactory* SolverFactory = NewObject<UMetaHumanFaceFittingSolverFactoryNew>();
UObject* NewAsset = SolverFactory->FactoryCreateNew(
    UMetaHumanFaceFittingSolver::StaticClass(),
    InParent,
    TEXT("MyFaceSolver"),
    RF_Public | RF_Standalone,
    nullptr,
    GWarn
);

// 将新资产保存到磁盘
FAssetEditorManager::Get().OpenEditorForAsset(NewAsset); // 可选：在编辑器中打开
FAssetRegistryModule::AssetCreated(NewAsset);
```

### 进阶用法

结合 `MetaHumanIdentity` 和 `MetaHumanFaceFittingSolver`，可以实现一个完整的从身份创建到表演应用的自定义流程。这通常需要访问多个模块的 API，例如使用 `MetaHumanFaceFittingSolver` 模块中的求解器对捕获的面部网格数据进行拟合，然后将结果应用到 `MetaHumanIdentity` 资产中定义的角色上。

## Demo 示例

由于 MetaHuman Animator 是一个工作流驱动的复杂插件，完整的 C++ 示例涉及多个模块和资产系统的交互，通常通过编辑器工具链完成。一个最小化的概念性示例是操作其资产类型：

```cpp
// MyMetaHumanTool.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/EditorSubsystem.h"
#include "MyMetaHumanTool.generated.h"

class UMetaHumanFaceFittingSolver;
class UMetaHumanPerformance;

UCLASS()
class UMyMetaHumanTool : public UEditorSubsystem
{
	GENERATED_BODY()

public:
	virtual void Initialize(FSubsystemCollectionBase& Collection) override;
	virtual void Deinitialize() override;

	// 示例：加载一个求解器并打印其名称
	UFUNCTION(BlueprintCallable, Category = "MetaHuman|Demo")
	void PrintSolverInfo(const FString& SolverPath);

private:
	UPROPERTY()
	TObjectPtr<UMetaHumanFaceFittingSolver> LoadedSolver;
};

// MyMetaHumanTool.cpp
#include "MyMetaHumanTool.h"
#include "MetaHumanFaceFittingSolver.h"
#include "AssetRegistry/AssetRegistryModule.h"

void UMyMetaHumanTool::Initialize(FSubsystemCollectionBase& Collection)
{
	Super::Initialize(Collection);
}

void UMyMetaHumanTool::Deinitialize()
{
	LoadedSolver = nullptr;
	Super::Deinitialize();
}

void UMyMetaHumanTool::PrintSolverInfo(const FString& SolverPath)
{
	LoadedSolver = LoadObject<UMetaHumanFaceFittingSolver>(nullptr, *SolverPath);
	if (LoadedSolver)
	{
		UE_LOG(LogTemp, Log, TEXT("Loaded Solver: %s"), *LoadedSolver->GetName());
		// 在此处可以访问 LoadedSolver 的属性来配置求解过程
	}
	else
	{
		UE_LOG(LogTemp, Warning, TEXT("Failed to load solver from path: %s"), *SolverPath);
	}
}
```

## 模块依赖

MetaHuman Animator 插件包含大量模块，使用者通常只需依赖其中一部分。根据你的目标，可能需要依赖不同的模块组合。

| 模块 | 用途 |
|---|---|
| `MetaHumanCore` | 核心功能，提供基础类型和接口。 |
| `MetaHumanIdentity` | 处理 MetaHuman 身份资产的创建、编辑和管理。 |
| `MetaHumanFaceFittingSolver` | 面部拟合求解器的核心算法。 |
| `MetaHumanFaceFittingSolverEditor` | 面部拟合求解器的编辑器工具和资产定义。 |
| `MetaHumanPerformance` | 存储和管理从捕获数据中提取的动画表演。 |
| `MetaHumanPipeline` | 数据处理流水线，协调不同处理阶段。 |
| `MetaHumanCaptureProtocolStack` | 与外部捕获设备（如 iPhone）通信的协议栈。 |
| `MetaHumanConfig` | 处理插件的配置文件和设置。 |
| `MetaHumanSequencer` | 将 MetaHuman 动画集成到 Sequencer 中。 |
| `MetaHumanSDKEditor` | 与 MetaHuman SDK 编辑器部分的接口。 |

**注意**：如果你的目标是扩展编辑器工具（如 `MetaHumanFaceFittingSolverEditor`），则需要依赖编辑器模块（如 `UnrealEd`）。如果仅在运行时使用资产，则依赖对应的运行时模块即可。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 在启用身体追踪时禁用关卡序列导出。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 上的渲染伪影。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 在身体追踪时过滤可视化对象。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 为现有网格体导出动画序列。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题。 |

### 维护评价

MetaHuman Animator 是 Epic Games 官方维护的**核心工具链**，创建于约5年前。从近期提交历史来看（集中在2026年5月），插件仍在**非常活跃地维护**，更新频率高，内容涵盖功能增强（如新的导出功能）、Bug 修复（渲染、缓存问题）以及与新功能（身体追踪）的适配。

该插件是 MetaHuman 工作流的基石，预计将持续更新以支持最新的引擎版本和工作流程改进。**强烈推荐**用于任何涉及 MetaHuman 角色动画制作的项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/metahuman-animator-in-unreal-engine/)