# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman动画师 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的一套完整的 MetaHuman 数字人制作工具链。它并非一个单一功能的插件，而是整合了从面部捕捉、动画制作到角色配置的一整套工作流。其核心目的是在 Unreal Engine 内，将来自 iPhone、视频或第三方软件捕捉的真实人脸表演，高效、准确地应用到 MetaHuman 数字角色模型上，生成高质量的面部动画。它解决了将现实世界的表演转化为虚拟角色动画的关键技术问题。

## 使用场景

-   **从 iPhone 捕捉创建数字人**：使用配备原深感摄像头的 iPhone 捕捉面部数据，并在 UE 中通过此插件将其应用到 MetaHuman 角色，生成动画。
-   **从视频或音频生成动画**：利用 `MetaHumanSpeech2Face` 等模块，从一段普通的视频或音频文件中提取或推测出面部动画。
-   **自定义角色动画与适配**：使用 `MetaHumanFaceFittingSolver` 和 `MetaHumanIdentity` 模块，对 MetaHuman 模型进行面部拓扑匹配、表情绑定和动画重定向，使其适配自定义的角色。
-   **动画批量处理与导出**：使用 `MetaHumanBatchProcessor` 对大量捕捉数据或动画进行批量处理，并通过 `MetaHumanSequencer` 集成将动画序列导出或用于影片渲染。
-   **高级面部动画制作**：结合 `MetaHumanFaceAnimationSolver` 和 `ControlRig`，对角色的面部表情、眼睛视线、口型同步进行精细的后期调整和优化。

## 蓝图用法

该插件主要提供编辑器内工具、资产和数据结构，其大量核心功能通过编辑器自定义资产（如 `UFaceTrackerCaptureData`, `UCaptureData`）和 Slate UI 面板实现，而非典型的运行时蓝图节点。以下是从当前提供的头文件中可提取的蓝图相关接口：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreatePreviewComponent` | 根据 `UCaptureData` 创建一个用于在场景中预览捕获数据的 `USceneComponent`。 | `MetaHumanCaptureDataUtils` (命名空间) |

### 使用示例（蓝图描述）

由于提供的模块主要是编辑器工具，其使用主要在编辑器操作中。例如，`SMetaHumanCameraCombo` 是一个 Slate 组合框控件，它在 `MetaHumanCaptureDataEditor` 模块的细节面板中，用于让用户从捕获的素材（如 `UFootageCaptureData`）中选择一个特定的摄像机视角。你不需要在蓝图图表中直接连接这个节点，它会在你编辑与捕获数据相关的资产时自动出现在属性面板中。

## C++ 用法

该插件的许多核心功能（如求解器、追踪器）都有对应的 C++ API，但需要结合其内部定义的特定数据类型（如 `UCaptureData`, `FControlRigMapping`）使用。以下基于提供的有限代码和通用模式进行说明。

### 头文件引入

由于模块众多，引入头文件取决于你要使用的具体功能。例如：
```cpp
// 使用预览工具
#include "CaptureDataUtils.h"

// 处理 MetaHuman 配置（假设存在）
#include "MetaHumanConfig.h"
```

### 基本用法

从提供的 `CaptureDataUtils.h` 可以看到，该插件提供了实用工具函数来创建预览组件。

```cpp
// 文件：Source/MetaHumanCaptureDataEditor/Private/SomeAssetEditor.cpp（概念示例）
#include "CaptureDataUtils.h"
#include "CaptureData.h" // UCaptureData

void AMyActor::ShowCaptureDataPreview()
{
    UCaptureData* MyCaptureData = /* ... 获取或创建一个捕获数据资产 ... */;
    if (MyCaptureData)
    {
        // 在此对象（InObject，例如编辑器Actor）上创建一个预览组件
        USceneComponent* PreviewComp = MetaHumanCaptureDataUtils::CreatePreviewComponent(MyCaptureData, this);
        // PreviewComp 现已附加到此 Actor，可以在场景中显示捕获的点云、网格等。
    }
}
```

### 进阶用法

更高级的用法涉及使用其完整的管线（Pipeline）和求解器（Solver）。例如，你可以编写 C++ 代码来驱动 `MetaHumanFaceFittingSolver`，将一个自定义的控制点动画映射到 MetaHuman 面部网格上，这需要实例化求解器类、配置其输入数据（如拓扑、目标姿态），并调用其求解函数。这些 API 通常封装在 `MetaHumanFaceFittingSolver`、`MetaHumanFaceAnimationSolver` 等模块的公共头文件中。

## Demo 示例

由于 MetaHuman Animator 是一个庞大的套件，通常没有单一的“最小示例”。一个典型的可编译工作流始于设置项目依赖并创建一个简单的处理任务。以下是一个概念性的 C++ 框架，展示如何开始使用其核心模块之一。

```cpp
// MyMetaHumanProcessor.h
#pragma once
#include "CoreMinimal.h"

class UMetaHumanFaceFittingSolver;

class FMyMetaHumanProcessor
{
public:
    void ProcessFaceAnimation(UCaptureData* InSourceData, USkeletalMesh* InTargetMesh);
private:
    // 持有对内部求解器实例的引用
    TWeakObjectPtr<UMetaHumanFaceFittingSolver> FaceSolver;
};

// MyMetaHumanProcessor.cpp
#include "MyMetaHumanProcessor.h"
#include "MetaHumanFaceFittingSolver.h" // 假设的头文件

void FMyMetaHumanProcessor::ProcessFaceAnimation(UCaptureData* InSourceData, USkeletalMesh* InTargetMesh)
{
    if (!InSourceData || !InTargetMesh) return;

    // 获取或初始化求解器（具体初始化方式需查阅API）
    if (!FaceSolver.IsValid())
    {
        // FaceSolver = NewObject<UMetaHumanFaceFittingSolver>();
        // 或者从某个全局管理器获取
    }

    // if (FaceSolver.IsValid())
    // {
    //     // 配置求解器参数
    //     FaceSolver->SetSourceCaptureData(InSourceData);
    //     FaceSolver->SetTargetSkeletalMesh(InTargetMesh);
    //     // 执行求解，生成动画数据
    //     FaceSolver->Solve(/* 输出参数 */);
    // }
}
```
**注意**：以上代码为示意，`UMetaHumanFaceFittingSolver` 等类的实际名称、头文件路径和 API 需查阅插件源码确认。

## 模块依赖

该插件内部模块间有复杂的依赖关系。对你的项目模块而言，若要使用其特定功能，通常需要依赖对应的 **Runtime** 模块。

| 模块 | 用途 |
|---|---|
| `MetaHumanCore` | 提供 MetaHuman 系统的核心数据结构和功能 |
| `MetaHumanFaceFittingSolver` | 面部网格拟合与重定向求解器 |
| `MetaHumanFaceAnimationSolver` | 面部动画求解器（口型、表情） |
| `MetaHumanPipeline` | 数据处理管线框架 |
| `MetaHumanCaptureUtils` | 捕获数据的通用工具函数 |
| `MetaHumanSpeech2Face` | 从语音生成面部动画 |
| `ControlRig` | 用于驱动最终面部动画的 Control Rig 系统（UE引擎模块） |
| `SkeletalMeshUtilitiesCommon` | 骨骼网格体工具，用于网格体操作 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体追踪时，禁用关卡序列导出功能。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复了 MetaHuman 上的渲染瑕疵。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 为已存在的网格体导出动画序列。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复序列器缓存问题。 |

### 维护评价

MetaHuman Animator 是一个处于**活跃维护**状态的核心官方插件。
- **创建时间**：虽然精确时间未知，但 MetaHuman 技术栈在近年持续发展。
- **更新频率**：从近期提交看，更新非常频繁（每天都有提交），且内容集中在**功能优化（如序列缓存）、Bug修复（渲染瑕疵）和新功能集成（身体追踪相关）**。
- **状态**：作为 Epic 官方维护的关键人物创建技术的一部分，其开发持续进行。
- **推荐**：**强烈推荐使用**。它是创建和驱动 MetaHuman 角色动画的官方且功能完备的解决方案，生态系统成熟，文档和社区支持正在不断完善中。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/Character/MetaHuman/) （UE文档中的MetaHuman章节）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Tests) （插件目录下可能存在测试）