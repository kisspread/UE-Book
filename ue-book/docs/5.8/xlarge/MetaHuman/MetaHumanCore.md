# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画师 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（MetaHuman角色资产、动画数据、配置资源） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2026（根据近期提交推断） |
| 年龄标签 | 🆕（约 N 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是一套完整的 MetaHuman 角色面部动画处理工具集。它**不是**一个简单的资产包，而是一个覆盖了从原始面部捕捉数据（如来自 Live Link Face 的序列）到最终可驱动 MetaHuman 角色面部动画的完整工作流程的专业管线。核心解决的问题是如何将捕捉到的面部运动数据，高效、精准地转换为符合 MetaHuman 骨骼和肌肉系统要求的动画数据，并支持在编辑器内进行可视化、编辑和批量处理。

## 使用场景

- **数字人动画制作**：你使用 iPhone 的 Live Link Face 应用录制了演员的面部表演，需要将这些数据应用到一个 MetaHuman 角色上并进行细节调整。
- **批量处理动画数据**：你有一个项目包含数十个 MetaHuman 角色的面部动画序列，需要统一调整或重新应用动画数据。
- **自定义面部动画工作流**：你需要在 UE 内部自定义面部动画的融合、求解或修复流程，而不是仅仅依赖最终动画序列。
- **面部捕捉与性能优化**：你需要从视频素材中自动提取面部关键点（轮廓线），并将其用于驱动动画，或优化动画数据的存储和传输。

## 蓝图用法

该插件主要通过编辑器工具和资产操作来使用，其公共 API 主要集中在 `MetaHumanCore` 模块中，提供了视口设置、轮廓数据控制和配置版本管理等功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetViewModeIndex` | 获取指定视图模式（A/B视图）下的视口显示模式 | `UMetaHumanViewportSettings` |
| `SetViewModeIndex` | 设置指定视图模式下的视口显示模式（如光照、线框等） | `UMetaHumanViewportSettings` |
| `ToggleShowCurves` | 切换指定视图模式下控制曲线的可见性 | `UMetaHumanViewportSettings` |
| `IsShowingCurves` | 查询指定视图模式下控制曲线是否可见 | `UMetaHumanViewportSettings` |
| `ToggleSkeletalMeshVisibility` | 切换指定视图模式下骨骼网格体的可见性 | `UMetaHumanViewportSettings` |
| `ToggleFootageVisibility` | 切换指定视图模式下原始捕捉画面的可见性 | `UMetaHumanViewportSettings` |
| `IsFootageVisible` | 查询指定视图模式下原始捕捉画面是否可见 | `UMetaHumanViewportSettings` |

### 使用示例（蓝图描述）

在蓝图中，你通常不会直接创建 `UMetaHumanViewportSettings`，而是通过 MetaHuman 编辑器工具栏的按钮或菜单来操作。例如，在“MetaHuman Animator”编辑器窗口中：
1.  **显示模式切换**：通过 `SetViewModeIndex` 节点，将视图A设置为 `VMI_Lit`（光照模式），视图B设置为 `VMI_Wireframe`（线框模式），以便同时观察光照效果和网格拓扑。
2.  **查看捕捉画面**：调用 `ToggleFootageVisibility` 并传入 `EABImageViewMode::A`，可以快速在视图A中显示或隐藏原始捕捉视频，用于比对动画驱动的准确性。
3.  **显示控制点**：调用 `ToggleShowControlVertices` 来显示或隐藏用于手动调整动画曲线的控制点。

## C++ 用法

核心功能围绕面部捕捉数据的处理和控制展开。

### 头文件引入

```cpp
#include "MetaHumanCore.h"
#include "MetaHumanViewportSettings.h"
#include "MetaHumanContourData.h"
#include "MetaHumanCurveDataController.h"
```

### 基本用法

以下代码演示了如何获取和设置视口状态，这在开发自定义 MetaHuman 动画工具时非常有用。

```cpp
// 来源: 基于 Public/MetaHumanViewportSettings.h 分析
// 获取当前的视口设置对象（通常由编辑器模块持有）
UMetaHumanViewportSettings* ViewportSettings = GetYourViewportSettingsInstance();

// 检查视图A是否正在显示骨骼网格体
bool bIsSkeletalVisible = ViewportSettings->IsSkeletalMeshVisible(EABImageViewMode::A);

// 在视图A中切换显示控制顶点
ViewportSettings->ToggleShowControlVertices(EABImageViewMode::A);

// 设置视图A的曝光值为 1.5
ViewportSettings->SetEV100(EABImageViewMode::A, 1.5f, true);
```

### 进阶用法

以下代码展示了如何操作面部轮廓数据（Contour Data），这是驱动 MetaHuman 面部动画的基础数据。

```cpp
// 来源: 基于 Public/MetaHumanContourData.h 和 Public/MetaHumanCurveDataController.h 分析
// 假设你已经有一个 UMetaHumanContourData 对象
TObjectPtr<UMetaHumanContourData> ContourData = ...; // 从资产或处理流程中获取

// 创建一个曲线数据控制器，用于管理轮廓线的交互和编辑
FMetaHumanCurveDataController CurveController(ContourData, ECurveDisplayMode::Editing);

// 从配置初始化轮廓线数据（例如从追踪结果加载）
FFrameTrackingContourData DefaultData = ...;
CurveController.InitializeContoursFromConfig(DefaultData, TEXT("5.0"));

// 模拟用户在视口中选择了一条名为 “LipUpperOuter” 的曲线
TSet<FString> SelectedCurves;
SelectedCurves.Add(TEXT(“LipUpperOuter”));
CurveController.SetCurveSelection(SelectedCurves, true);

// 获取选中曲线的控制点位置，用于绘制或进一步处理
TArray<FVector2D> ControlPoints = ContourData->GetControlVertexPositions(TEXT(“LipUpperOuter”));
```

## Demo 示例

一个可编译的最小示例，演示如何监听视口设置变更并做出响应。

```cpp
// MetaHumanViewportDemo.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "MetaHumanViewportSettings.h"
#include "MetaHumanViewportDemo.generated.h"

UCLASS()
class UMetaHumanViewportDemoSubsystem : public UGameInstanceSubsystem
{
	GENERATED_BODY()

public:
	virtual void Initialize(FSubsystemCollectionBase& Collection) override;
	virtual void Deinitialize() override;

private:
	UFUNCTION()
	void OnViewportSettingsChanged();

	UPROPERTY()
	TObjectPtr<UMetaHumanViewportSettings> CachedSettings;
};
```

```cpp
// MetaHumanViewportDemo.cpp
#include "MetaHumanViewportDemo.h"

void UMetaHumanViewportDemoSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
	Super::Initialize(Collection);

	// 假设通过某种方式获取到编辑器模块中的视口设置实例
	// 在实际插件开发中，可能需要通过模块间引用或自定义接口获取
	// 这里仅为示例逻辑。
	// CachedSettings = GEditor->GetEditorSubsystem<UMyMetaHumanEditorSubsystem>()->GetViewportSettings();
	if (CachedSettings)
	{
		CachedSettings->OnSettingsChangedDelegate.AddUObject(this, &UMetaHumanViewportDemoSubsystem::OnViewportSettingsChanged);
	}
}

void UMetaHumanViewportDemoSubsystem::Deinitialize()
{
	if (CachedSettings)
	{
		CachedSettings->OnSettingsChangedDelegate.RemoveAll(this);
	}
	Super::Deinitialize();
}

void UMetaHumanViewportDemoSubsystem::OnViewportSettingsChanged()
{
	if (CachedSettings)
	{
		// 当设置改变时，例如视口模式改变，这里可以执行响应逻辑
		bool bIsSingle = CachedSettings->IsShowingSingleView();
		UE_LOG(LogTemp, Log, TEXT(“Viewport changed. Single view mode: %s”), bIsSingle ? TEXT(“true”) : TEXT(“false”));
	}
}
```

## 模块依赖

要使用 `MetaHumanAnimator` 插件的核心功能，你的项目或插件模块需要根据具体依赖的功能进行配置。

| 模块 | 用途 |
|---|---|
| `MetaHumanCore` | 提供视口设置、轮廓数据管理和基础工具类 |
| `MetaHumanPipeline` | 处理数据管线，如捕获数据的引入和转换 |
| `MetaHumanConfig` | 管理 MetaHuman 特定的配置数据（依赖于 MetaHumanCoreTechLib） |
| `MetaHumanFaceContourTracker` | 从图像/视频中提取面部轮廓关键点 |
| `MetaHumanFaceAnimationSolver` | 使用轮廓数据驱动面部动画 |
| `MetaHumanCaptureUtils` | 面部捕获相关的工具函数 |
| `MetaHumanIdentity` | 管理和编辑 MetaHuman 角色身份资产 |
| `MetaHumanSequencer` | 与 UE 的 Sequencer 集成，处理动画序列 |
| `MetaHumanBatchProcessor` | 批量处理多个 MetaHuman 相关资产 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时，禁用关卡序列导出功能。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 角色上的渲染瑕疵。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 在身体追踪时过滤可视化对象。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 为现有网格体导出动画序列。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题。 |

### 维护评价

该插件**处于活跃维护状态**。根据提交记录，最近一周内（截至2026年5月22日）有持续的更新，包括功能改进（动画导出）、渲染问题修复和缓存优化。作为 Epic 官方维护的 MetaHuman 工具集，它与 UE 版本发布和 MetaHuman 技术栈的发展紧密同步。虽然无法从给定信息推断其确切创建时间，但从版本号（5.0.0）和密集的近期提交来看，这是一个较新且仍在积极开发的插件。**推荐使用**，尤其是对于需要完整 MetaHuman 面部动画工作流的项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- 官方文档（.uplugin 中未提供链接）