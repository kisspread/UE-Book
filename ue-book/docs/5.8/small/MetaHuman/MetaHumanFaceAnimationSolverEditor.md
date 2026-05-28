# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器工具、动画求解器、配置资产） |
| 模块 | `MetaHumanCore` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanSequencer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | unknown |
| 年龄标签 | 🆕（约 N 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是一个完整的数字人面部动画制作工具链，旨在将真实世界中的面部表演数据（视频、音频）转换为可在 Unreal Engine 中驱动 MetaHuman 角色的高质量动画资产。它不仅仅是一个简单的动画重定向工具，而是涵盖了从数据捕获、面部追踪、动画求解到最终导出的全流程管线，解决了从现实到数字世界（Reality-to-Digital）的面部动画自动化生成问题。

其核心价值在于：
1.  **高保真面部追踪**：通过 `MetaHumanFaceContourTracker` 等模块，从输入视频中精确捕捉面部关键点。
2.  **自动化动画求解**：利用 `MetaHumanFaceAnimationSolver` 和 `MetaHumanSpeech2Face` 等模块，将追踪数据或音频信号驱动 MetaHuman 的面部骨骼和形态目标（Morph Target），生成流畅的动画。
3.  **批处理能力**：`MetaHumanBatchProcessor` 支持自动化处理大量素材，提升工作流效率。
4.  **一体化编辑器体验**：通过 `MetaHumanCoreEditor`、`MetaHumanFaceAnimationSolverEditor` 等众多编辑器模块，提供资产创建、自定义调整和序列导出的完整集成环境。

## 使用场景

-   **影视与过场动画制作**：将演员的面部表演视频快速转换为数字角色的动画，用于电影、游戏过场。
-   **虚拟主播与直播**：从摄像头实时或离线生成面部动画，驱动虚拟形象进行直播或内容创作。
-   **游戏内容开发**：批量生成 NPC 的口型动画（Lip Sync），或为主角制作从真人表演捕捉来的复杂情感动画。
-   **语音驱动动画**：仅通过音频文件生成口型和面部表情动画，用于本地化配音或快速原型制作。
-   **研究与实验**：利用其模块化的管线（Pipeline），探索和自定义面部动画处理的不同阶段。

## 蓝图用法

> **注意**：提供的当前模块 `MetaHumanFaceAnimationSolverEditor` 主要为编辑器扩展功能。完整的运行时蓝图 API 分布在诸如 `MetaHumanPerformance`、`MetaHumanSpeech2Face` 等模块中。以下为基于插件整体推断的核心蓝图交互点。

### 核心节点

| 节点 | 说明 | 所在类（推断） |
|---|---|---|
| `Create MetaHuman Performance` | 从捕获数据资产创建一个新的 MetaHuman Performance 资产，用于存储和驱动动画数据。 | `UMetaHumanPerformance` (MetaHumanPerformance) |
| `Bake to Level Sequence` | 将计算出的面部动画烘焙到 Unreal 的 `ULevelSequence` 中，以便于在 Sequencer 中编辑和混合。 | `UMetaHumanPerformance` 或相关工具类 |
| `Apply Face Animation` | 将性能数据应用到目标 MetaHuman 骨骼网格体组件上，实时预览动画。 | `UMetaHumanPerformance` (推断) |
| `Process Batch` | 触发批处理作业，对指定的一组输入数据（如一组视频）进行统一处理。 | `UMetaHumanBatchProcessor` |
| `Start Speech to Face` | 启动从音频文件生成面部动画的任务。 | `UMetaHumanSpeech2Face` (推断) |

### 使用示例（蓝图描述）

1.  **从视频创建动画**:
    *   在内容浏览器中右键，选择 “Animation” -> “MetaHuman Performance” 来创建一个新的性能资产。
    *   在该资产的细节面板中，设置输入源为一个包含人物面部表演的视频文件。
    *   通过蓝图或编辑器UI触发求解过程，资产将自动分析视频并生成驱动数据。
    *   最后，将此资产拖拽到场景中的 MetaHuman 角色上，或使用“Bake to Level Sequence”节点将动画导出。

2.  **音频驱动口型动画**:
    *   使用 `Start Speech to Face` 蓝图节点（或对应编辑器功能），输入一段对话音频文件。
    *   指定目标 MetaHuman 角色。
    *   工具将分析音频并生成匹配的口型和基本面部表情动画，可以直接预览或导出为序列。

## C++ 用法

### 头文件引入

由于该插件模块众多，根据你所需功能引入相应模块的头文件。例如，操作动画求解器资产时：
```cpp
#include "MetaHumanFaceAnimationSolver.h"
```
操作性能资产时：
```cpp
#include "MetaHumanPerformance.h"
```

### 基本用法

以下示例演示如何在代码中创建一个 `UMetaHumanFaceAnimationSolver` 资产（基于 `MetaHumanFaceAnimationSolverEditor` 模块中的 Factory）。

```cpp
// 假设在编辑器工具代码中
#include "MetaHumanFaceAnimationSolverFactoryNew.h" // 来自当前模块 Private 文件
#include "AssetToolsModule.h"
#include "IAssetTools.h"

void CreateNewFaceAnimationSolverAsset()
{
    UMetaHumanFaceAnimationSolverFactoryNew* Factory = NewObject<UMetaHumanFaceAnimationSolverFactoryNew>();
    if (Factory)
    {
        UObject* NewAsset = FAssetToolsModule::GetModule().Get().CreateAsset(
            TEXT("NewFaceAnimSolver"),          // 资产名称
            TEXT("/Game/MetaHuman/Animations"), // 路径
            UMetaHumanFaceAnimationSolver::StaticClass(), // 资产类，需引入对应头文件
            Factory
        );
        // NewAsset 现在是一个新创建的 UMetaHumanFaceAnimationSolver 实例
    }
}
```
*(注：此代码示例基于 `UMetaHumanFaceAnimationSolverFactoryNew` 类推断，实际创建流程可能更复杂，通常通过编辑器的“资产创建”菜单完成。)*

### 进阶用法

利用 `MetaHumanPipeline` 模块构建自定义处理流程，将面部追踪与动画求解串联：
```cpp
// 此为概念性代码，展示模块间交互
#include "MetaHumanPipeline.h"
#include "MetaHumanFaceContourTracker.h"
#include "MetaHumanFaceAnimationSolver.h"

void ProcessFootageWithCustomPipeline()
{
    // 1. 创建并配置面部追踪节点
    UMetaHumanFaceContourTrackerNode* TrackerNode = NewObject<UMetaHumanFaceContourTrackerNode>();
    TrackerNode->SetInputVideo(/* ... */);

    // 2. 创建并配置动画求解节点
    UMetaHumanFaceAnimationSolverNode* SolverNode = NewObject<UMetaHumanFaceAnimationSolverNode>();
    SolverNode->SetSolverAsset(/* 一个已配置的求解器资产 */);

    // 3. 构建管线，将两个节点连接
    UMetaHumanPipeline* Pipeline = NewObject<UMetaHumanPipeline>();
    Pipeline->AddNode(TrackerNode);
    Pipeline->AddNode(SolverNode);
    Pipeline->ConnectNodes(TrackerNode, SolverNode);

    // 4. 执行管线
    Pipeline->Execute();
    // 执行后，SolverNode 的输出可能包含生成的动画数据
}
```
*(注：`MetaHumanPipeline` 模块的确切 API 和节点类型需查阅源码，此处仅为逻辑示意。)*

## Demo 示例

一个最小的、读取已有 MetaHuman Performance 资产并打印其信息的示例。

**MyMetaHumanAnimHelper.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MyMetaHumanAnimHelper.generated.h"

class UMetaHumanPerformance;

UCLASS(BlueprintType)
class MYMODULE_API UMyMetaHumanAnimHelper : public UObject
{
    GENERATED_BODY()

public:
    /** 读取并打印一个 MetaHuman Performance 资产的基本信息。 */
    UFUNCTION(BlueprintCallable, Category = "MetaHuman Helper")
    static void LogPerformanceAssetInfo(UPARAM(ref) UMetaHumanPerformance* InPerformanceAsset);
};
```

**MyMetaHumanAnimHelper.cpp**
```cpp
#include "MyMetaHumanAnimHelper.h"
#include "MetaHumanPerformance.h" // 依赖 MetaHumanPerformance 模块

void UMyMetaHumanAnimHelper::LogPerformanceAssetInfo(UMetaHumanPerformance* InPerformanceAsset)
{
    if (!InPerformanceAsset)
    {
        UE_LOG(LogTemp, Warning, TEXT("Invalid Performance Asset provided."));
        return;
    }

    // 从资产获取一些基本信息
    const FString AssetName = InPerformanceAsset->GetName();
    const float Duration = InPerformanceAsset->GetDuration(); // 假设存在此方法

    UE_LOG(LogTemp, Log, TEXT("MetaHuman Performance Asset: %s"), *AssetName);
    UE_LOG(LogTemp, Log, TEXT("  Duration: %.2f seconds"), Duration);
    // 根据实际 API 可以打印更多信息，如追踪状态、求解配置等
}
```

## 模块依赖

以下为该插件自身独特的依赖模块（你的模块需要引用这些才能使用其特定功能）：

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | MetaHuman 核心技术库，包含底层的面部模型、变形和数学工具。 |
| `MetaHumanSDKEditor` | MetaHuman SDK 的编辑器功能，用于资产管理和工作流集成。 |
| `ControlRigDeveloper` | 用于开发、编辑和管理 Control Rig 资产，MetaHuman 动画驱动常基于 Control Rig。 |
| `SkeletalMeshUtilitiesCommon` | 提供骨骼网格体相关的通用编辑器工具和实用函数。 |

*(注：`MetaHumanFaceAnimationSolverEditor` 本身主要依赖 `MetaHumanCore`, `MetaHumanFaceAnimationSolver` 等内部模块，其 Build.cs 的公开依赖通常包含上述列表中的模块。你的项目模块若要与之交互，需在 .Build.cs 中添加相应依赖。)*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体追踪时，禁用关卡序列导出功能，以避免数据冲突或错误。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复了在 MetaHuman 角色上出现的渲染瑕疵或伪影问题。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 在进行身体追踪时，过滤掉不必要的可视化对象，提升编辑器视口清晰度。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MetaHuman Animator] 支持为已存在的网格体导出动画序列，增强了工作流灵活性。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复了 Sequencer 中的缓存问题，提升了动画预览和编辑的稳定性。 |

### 维护评价

-   **活跃维护**: 插件在近期（2026年5月）仍有频繁的功能性更新和Bug修复，表明其处于**活跃维护**状态。
-   **成熟度高**: 作为 Epic 官方用于驱动 MetaHuman 的核心工具链，其稳定性和可靠性要求极高，更新主要以修复和优化为主。
-   **实验性与限制**: 虽然插件本身标记为非实验性，但其部分功能（如身体追踪集成）可能仍处于开发或优化阶段（从提交记录中可见）。官方文档链接为空，建议参考 Epic 官方的 MetaHuman 技术文档和社区资源。
-   **推荐使用**: **强烈推荐**所有需要创建高质量、逼真面部动画的 MetaHuman 项目使用此插件。它是官方支持的唯一完整解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档]() （暂无，请查阅 Epic Games MetaHuman 官网及文档中心）
- [测试用例]() （路径未知，可能位于 `Engine/Plugins/MetaHuman/MetaHumanAnimator/Tests` 或 `Engine/Tests`）