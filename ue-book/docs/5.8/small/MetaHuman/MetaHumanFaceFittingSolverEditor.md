# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman动画师工具 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（MetaHuman资产） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-04-11 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

`MetaHuman Animator` 插件是一个完整的工作流程工具集，其核心目的是将真实人物的面部表演（Performance Capture）数据高效、精确地应用到 UE5 中的 MetaHuman 数字人角色上。它解决了从原始视频或深度数据中提取面部运动信息，并驱动高保真 MetaHuman 角色进行动画创作的完整流程问题。该插件并非单一功能模块，而是一个包含捕捉、追踪、求解、编辑和播放等子系统的庞大框架。

## 使用场景

-   **面部动画驱动**：你拥有一段使用 iPhone 或专业摄像设备拍摄的演员面部表演视频，希望将其转化为驱动 MetaHuman 角色面部的动画序列。
-   **深度数据应用**：你使用了如 LiDAR 等设备采集了面部深度信息，希望利用这些数据来增强动画的精度。
-   **批量处理动画**：你有大量的面部表演素材需要转换为 MetaHuman 动画，需要一个自动化的批量处理流程。
-   **从语音生成动画**：你希望仅通过一段语音音频，就能为 MetaHuman 角色生成对应的口型及基础面部动画。
-   **自定义面部求解器**：你需要调整或定制面部动画求解算法，以匹配特定的表演风格或解决特定的变形问题。

## 蓝图用法

由于插件规模巨大且包含大量模块，以下列出基于源码分析推断的、可能被暴露到蓝图的核心功能节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ImportFootage` / `ProcessFootage` | 从文件路径导入并处理视频/深度数据 | `UMetaHumanFootageIngest` |
| `StartFaceTracking` / `StopFaceTracking` | 启动或停止对源视频的面部特征点追踪 | `UMetaHumanFaceContourTracker` |
| `RunFaceFittingSolver` | 使用拟合求解器将追踪数据转换为控制绑定参数 | `UMetaHumanFaceFittingSolver` |
| `RunFaceAnimationSolver` | 使用动画求解器从控制参数生成最终的面部动画曲线 | `UMetaHumanFaceAnimationSolver` |
| `CreatePerformance` / `ExportPerformance` | 创建、导出或应用动画性能资产 (`UMetaHumanPerformance`) | `UMetaHumanPerformance` |
| `StartSpeech2Face` | 从音频输入开始生成面部动画 | `UMetaHumanSpeech2Face` |
| `TrackMesh` | 使用网格追踪器辅助进行面部配准 | `UMeshTrackerInterface` |

*注意：具体函数签名需查阅各模块头文件，以上为功能分组描述。*

### 使用示例（蓝图描述）

假设要从一个 MP4 文件生成动画并应用到 MetaHuman：
1.  使用 `MetaHumanFootageIngest` 模块的函数，传入文件路径，获取处理后的帧数据。
2.  将数据传递给 `MetaHumanFaceContourTracker` 的追踪函数，获取每帧的 2D 面部特征点。
3.  将特征点序列输入到 `MetaHumanFaceFittingSolver`，运行求解，得到 MetaHuman 控制绑定 (Control Rig) 的参数流。
4.  将这些参数通过 `MetaHumanFaceAnimationSolver` 或 `MetaHumanPerformance` 系统，应用到场景中的 MetaHuman 骨架网格体组件上。
5.  最后，可将整个流程的输出保存为 `UMetaHumanPerformance` 资产，用于 Sequencer 回放或导出。

## C++ 用法

### 头文件引入

```cpp
// 根据你需要使用的子模块引入相应头文件
#include "MetaHumanFaceFittingSolver.h"
#include "MetaHumanFaceFittingSolverEditor.h" // 如果涉及编辑器特定功能
#include "MetaHumanPerformance.h"
#include "MetaHumanFaceContourTracker.h"
```

### 基本用法

由于测试用例未直接提供，以下是基于模块接口推断的典型用法模式：

```cpp
// 1. 初始化和运行面部追踪器（示意）
UMetaHumanFaceContourTracker* Tracker = NewObject<UMetaHumanFaceContourTracker>();
Tracker->Initialize(TrackerConfig); // 加载追踪器配置
TArray<FTrackedFrame> TrackedData = Tracker->TrackSequence(VideoFrames);

// 2. 运行面部拟合求解器
UMetaHumanFaceFittingSolver* FittingSolver = NewObject<UMetaHumanFaceFittingSolver>();
FittingSolver->Initialize(FittingConfig); // 加载求解器配置
FFittingResult FittingResult = FittingSolver->Solve(TrackedData);

// 3. 生成或应用动画性能数据
UMetaHumanPerformance* Performance = NewObject<UMetaHumanPerformance>();
Performance->InitializeFromFittingResult(FittingResult);
Performance->ApplyToSkeletalMeshComponent(MyMetaHumanSkeletalMeshComponent);
```

*注：此为示意代码，实际 API 需查阅 `MetaHumanFaceContourTracker.h`、`MetaHumanFaceFittingSolver.h` 等头文件。*

### 进阶用法

结合多个模块构建自定义处理管线 (Pipeline)：
```cpp
// 使用 MetaHumanPipeline 模块来编排整个处理流程
TSharedRef<FPipelineNode> FootageNode = MakeShareable(new FFootageIngestNode());
TSharedRef<FPipelineNode> TrackingNode = MakeShareable(new FFaceTrackingNode());
TSharedRef<FPipelineNode> FittingNode = MakeShareable(new FFaceFittingNode());
TSharedRef<FPipelineNode> ExportNode = MakeShareable(new FPerformanceExportNode());

// 连接节点
FootageNode->ConnectTo(TrackingNode);
TrackingNode->ConnectTo(FittingNode);
FittingNode->ConnectTo(ExportNode);

// 执行管线
FPipeline Pipeline;
Pipeline.Execute(FootageNode, InputData);
```

## Demo 示例

一个最小化的、从追踪数据拟合到 MetaHuman 控制参数的示例：

**MetaHumanDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MetaHumanFaceFittingSolver.h"
#include "MetaHumanDemo.generated.h"

class UMetaHumanFaceFittingSolver;

UCLASS(BlueprintType)
class MYPROJECT_API UMetaHumanDemo : public UObject
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, Category = "MetaHuman")
	void RunFaceFittingDemo();

private:
	UPROPERTY()
	TObjectPtr<UMetaHumanFaceFittingSolver> FittingSolver;
};
```

**MetaHumanDemo.cpp**
```cpp
#include "MetaHumanDemo.h"
#include "MetaHumanFaceFittingSolver.h"

void UMetaHumanDemo::RunFaceFittingDemo()
{
	// 创建求解器实例
	FittingSolver = NewObject<UMetaHumanFaceFittingSolver>(this);
	
	// 加载默认或指定的配置资产
	// FittingSolver->LoadConfig(ConfigAsset);
	
	// 假设已有从追踪阶段获得的 TrackedData (FTrackedFrame 数组)
	// 这里为了演示，创建一个空数据
	TArray<FTrackedFrame> DummyTrackedData;
	
	// 执行求解
	FFittingResult Result = FittingSolver->Solve(DummyTrackedData);
	
	// Result 包含了驱动 MetaHuman 控制绑定所需的数据
	// 你可以将 Result 传递给下游的动画系统或保存为资产
	if (Result.bSuccess)
	{
		UE_LOG(LogTemp, Log, TEXT("Face fitting solved successfully."));
	}
}
```

## 模块依赖

由于插件包含大量相互依赖的模块，以下是使用者在构建依赖此插件中特定功能的模块时，可能需要添加的独特依赖。请注意，很多依赖是内部的。

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | 核心的 MetaHuman 数学和算法库 |
| `MetaHumanSDKEditor` | 提供编辑器侧的 SDK 功能，供 Identity 等模块依赖 |
| `ControlRigDeveloper` | 用于开发和操作控制绑定 (Control Rig)，驱动 MetaHuman 骨骼 |
| `SkeletalMeshUtilitiesCommon` | 骨骼网格体通用工具，用于处理 MetaHuman 网格 |
| `MeshTrackerInterface` | 网格追踪接口，用于面部网格配准 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时，禁用关卡序列导出功能 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 身体的渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持为已有的网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题 |

### 维护评价

-   **创建时间**：约 3 年前 (2022-04-11)，是较新的插件。
-   **更新频率**：**极其活跃**。仅在最近一周内就有 5 次提交，且集中在功能修复和增强上（如修复渲染瑕疵、增加身体追踪兼容性、扩展导出功能）。
-   **维护状态**：**活跃维护中**。由 Epic Games 官方团队持续开发和维护，是 MetaHuman 生态系统的核心组件。
-   **已知问题/限制**：从提交历史看，团队正在积极修复各类渲染和缓存问题。作为大型复杂系统，可能存在对特定硬件或数据格式的兼容性问题，但会持续得到更新。
-   **推荐使用**：**强烈推荐**。这是将真实人物表演赋予 MetaHuman 角色的官方且功能最完整的解决方案。尽管功能复杂、学习曲线较陡，但其维护力度和效果表明它是一个可靠且不断进化的工具。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
-   [官方文档]() (`.uplugin` 中未提供 DocsURL)
-   [测试用例]() (大型插件，测试用例分散在各子模块的 `Private/Tests` 目录中)