# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画师 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（内容资产、蓝图工具） |
| 模块 | `MetaHumanCore` (Runtime), `MetaHumanAnimator` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-04-23 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 为 Unreal Engine 打造的官方 MetaHuman 生产工具包。它并非仅是一个“工具包”，而是一个完整的**数字人创建与动画管线**。该插件集成了从原始表演数据（视频、深度序列）生成、驱动和编辑 MetaHuman 角色的全部关键功能，旨在大幅简化数字人内容的生产流程。

**核心解决的问题**：
1.  **自动化面部动画**：从 iPhone/深度摄像头等设备的表演数据中，自动追踪面部轮廓、求解动画控制器，并生成可驱动 MetaHuman 模型的动画序列。
2.  **高保真面部拟合**：将扫描或拍摄的面部几何体，精确地拟合（Fitting）到 MetaHuman 的标准骨骼和控制器体系中，创建具有演员特定身份（Identity）的角色。
3.  **一体化工作流**：将数据捕获、处理（Pipeline）、预览、编辑和最终导出整合在一个统一的编辑器环境内。

## 使用场景

-   **影视与游戏过场动画**：你拥有一段演员的高清面部表演视频，希望快速为其对应的 MetaHuman 角色生成高质量的口型与表情动画序列。
-   **数字人资产创建**：你通过 3D 扫描获得了一个面部模型（OBJ/点云），需要将其转化为一个可以在 UE 中被标准 MetaHuman 动画控制器驱动的、具有特定身份（Identity）的 MetaHuman 角色。
-   **动画数据修正**：你已通过管线自动生成了 MetaHuman 的动画，但需要在编辑器中直观地检查和手动微调动画曲线（例如嘴角、眉毛的细微动作）。
-   **批量化处理**：你需要对一批表演数据应用相同的处理流程，以提高生产效率。

## 蓝图用法

主要的蓝图可调用功能集中在 `UMetaHumanPerformance` 和 `UMetaHumanPipeline` 类中，用于驱动处理流程和管理资产。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create` | 创建一个空的 MetaHuman 性能资产（`.performance`） | `UMetaHumanPerformance` |
| `Set` | 设置性能资产的关键属性，如源数据、关联的 MetaHuman 标识体 | `UMetaHumanPerformance` |
| `SetAnimation` | 为性能资产设置已求解好的动画序列数据 | `UMetaHumanPerformance` |
| `AddPipelineNode` | 向处理管线中添加一个数据处理节点 | `UMetaHumanPipeline` |
| `SetPipelineNodeProperties` | 配置管线中某个节点的详细参数 | `UMetaHumanPipeline` |
| `Run` | 执行整个管线，处理输入数据并生成输出 | `UMetaHumanPipeline` |

### 使用示例（蓝图描述）

1.  **创建并配置一个性能资产**：
    *   使用 `MetaHumanPerformance::Create` 节点创建新资产。
    *   调用 `Set` 节点，将其 `Source` 引用到导入的视频/深度媒体资产，将 `Identity` 引用到对应的 MetaHuman 标识体资产。
2.  **构建并执行一个简单处理管线**：
    *   使用 `MetaHumanPipeline::Create` 创建管线对象。
    *   连续调用 `AddPipelineNode` 节点添加 `Capture Source`、`Face Contour Tracker`、`Face Animation Solver` 等节点。
    *   对每个节点，调用 `SetPipelineNodeProperties` 进行配置（例如指定输入输出）。
    *   最后调用 `Run` 节点，管线将按顺序执行所有处理步骤。
    *   从管线输出中获取生成的动画数据，并通过 `MetaHumanPerformance::SetAnimation` 应用到性能资产上。

## C++ 用法

核心 C++ API 用于在编辑器工具或自动化脚本中控制 MetaHuman 处理管线。以下示例基于测试用例提炼。

### 头文件引入

```cpp
// 核心性能资产管理
#include "MetaHumanPerformance.h"
// 管线构建与执行
#include "MetaHumanPipeline.h"
```

### 基本用法

创建并配置一个 MetaHuman 性能资产。
*（来源：`Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanPerformance/Tests/MetaHumanPerformanceTest.cpp`）*

```cpp
// 1. 创建一个新的 MetaHuman Performance 资产
UMetaHumanPerformance* NewPerformance = NewObject<UMetaHumanPerformance>();
NewPerformance->SetFlags(RF_Transactional);

// 2. 设置关键属性（示例，实际属性名需根据版本调整）
//    NewPerformance->SetSource(MyMediaSourceAsset);
//    NewPerformance->SetIdentity(MyMetaHumanIdentityAsset);

// 3. (可选) 设置已求解的动画序列
//    UAnimSequence* MyAnimSequence = ...;
//    NewPerformance->SetAnimation(MyAnimSequence);
```

### 进阶用法

构建并运行一个完整的数据处理管线。这是插件的核心工作模式。
*（来源：`Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanPipeline/Tests/MetaHumanPipelineTest.cpp`）*

```cpp
// 1. 创建管线
UMetaHumanPipeline* Pipeline = NewObject<UMetaHumanPipeline>();

// 2. 添加处理节点（模拟从源数据到最终动画的步骤）
UMetaHumanPipelineNode* SourceNode = Pipeline->AddPipelineNode(/* NodeClass 或 FName */);
UMetaHumanPipelineNode* TrackerNode = Pipeline->AddPipelineNode(/* NodeClass 或 FName */);
UMetaHumanPipelineNode* SolverNode = Pipeline->AddPipelineNode(/* NodeClass 或 FName */);

// 3. 配置节点属性（将节点的输入输出连接起来，设置具体参数）
// 这是一个概念示例，具体属性名和连接方式需查阅节点类定义。
// Pipeline->SetPipelineNodeProperty(SourceNode, “OutputData”, /* ... */);
// Pipeline->SetPipelineNodeProperty(TrackerNode, “InputData”, /* 从SourceNode的输出引用 */);
// Pipeline->SetPipelineNodeProperty(SolverNode, “InputContours”, /* 从TrackerNode的输出引用 */);

// 4. 执行管线
FMetaHumanPipelineState State;
bool bSuccess = Pipeline->Run(State);
if (bSuccess)
{
    // 从 State 中提取结果，例如生成的动画曲线或性能资产
    UAnimSequence* GeneratedAnim = State.GetAnimationSequence();
    // ... 对动画数据进行后续处理
}
```

## Demo 示例

一个最小化的 C++ 示例，展示如何启动并监听一个 MetaHuman 处理任务。

```cpp
// MyMetaHumanDemo.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "MyMetaHumanDemo.generated.h"

UCLASS()
class UMyMetaHumanDemoSubsystem : public UGameInstanceSubsystem
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, Category = "MetaHumanDemo")
	void StartDemoProcessing();
};
```

```cpp
// MyMetaHumanDemo.cpp
#include "MyMetaHumanDemo.h"
#include "MetaHumanPerformance.h"

void UMyMetaHumanDemoSubsystem::StartDemoProcessing()
{
	// 假设我们已经有了引用到的源数据和标识体资产
	// UMediaSource* MyMediaSource = ...;
	// UMetaHumanIdentity* MyIdentity = ...;

	// 创建一个新的性能资产
	UMetaHumanPerformance* PerfAsset = NewObject<UMetaHumanPerformance>();

	// 通常，你会将这个资产保存到项目内容浏览器中
	// PerfAsset->CreateMyAssetPackage();

	// 设置数据。实际的属性名需要根据当前插件版本和头文件确定。
	// PerfAsset->SetSource(MyMediaSource);
	// PerfAsset->SetIdentity(MyIdentity);

	// 保存资产包
	// PerfAsset->SavePackage();

	UE_LOG(LogTemp, Log, TEXT("Created MetaHuman Performance Asset. You can now process it in the editor."));
}
```

## 模块依赖

此插件包含大量相互依赖的模块。要使用其核心功能，你的项目模块通常需要依赖以下非通用模块：

| 模块 | 用途 |
|---|---|
| `MetaHumanCore` | MetaHuman 核心类型和基础功能 |
| `MetaHumanAnimator` | 动画求解和编辑器集成的核心 |
| `MetaHumanIdentity` | 面部标识体（Identity）创建与管理 |
| `MetaHumanPerformance` | 性能（Performance）资产，承载表演数据与动画 |
| `MetaHumanPipeline` | 可配置的数据处理管线框架 |
| `MetaHumanCaptureProtocolStack` | 捕获协议栈，处理设备通信 |
| `ControlRigDeveloper` | 与 ControlRig 深度集成，用于动画控制 |

**注意**：此插件模块众多（如 `MetaHumanFaceFittingSolver`, `MetaHumanSpeech2Face` 等），上表仅列出最核心和通用的依赖。根据你使用的具体功能（如深度生成、语音驱动），可能需要引入更多相关模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体追踪时禁用关卡序列导出功能 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 渲染伪影问题 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 进行身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持为现有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存相关问题 |

### 维护评价

-   **活跃维护**：从近期的 Git 提交记录看，该插件在 **2026 年 5 月仍在进行频繁的功能性更新和 Bug 修复**（如身体追踪、渲染修复、导出功能），维护状态非常活跃。
-   **官方核心产品**：作为 Epic Games 的官方 MetaHuman 工具，其开发得到了公司层面的支持，预计会随着 UE 版本和 MetaHuman 技术栈的演进持续更新。
-   **推荐使用**：对于任何涉及 MetaHuman 数字人创建和动画制作的项目，此插件是**官方推荐且必须使用**的核心工具。虽然功能强大、模块复杂，但其提供了最完整、最标准的工作流。建议直接使用最新可用版本。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/using-meta-humans-in-unreal-engine/) (MetaHuman 整体文档)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source) (各模块 `Tests` 目录下)