# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | 元人类动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器工具） |
| 模块 | `MetaHumanAnimatorCore` (Runtime), `MetaHumanAnimatorEditor` (Runtime), `MetaHumanAnimatorBridge` (Runtime), `MetaHumanAnimatorMetadata` (Runtime), `MetaHumanAssetValidator` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanBlueprint` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime), `MeshTrackerInterface` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 无法计算 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途
MetaHuman Animator 是 Epic Games 为 MetaHuman 角色提供的一整套动画制作工具包。它不仅仅是一个插件，而是一个完整的生态系统，旨在将视频捕捉数据（包括来自 iPhone 的深度数据）转化为可用于 MetaHuman 角色的高质量、带有驱动骨骼的面部动画。其核心流程包括：面部追踪、轮廓追踪、深度估计、动画求解、面部拟合以及最终的动画应用。它解决了从原始视频素材到可驱动的数字角色动画之间复杂的转换和自动化处理问题。

## 使用场景
- 你使用 iPhone 的 LiDAR 传感器或专业摄像机拍摄了演员的面部表演视频 → 使用 MetaHuman Animator 将其转化为 MetaHuman 角色的动画序列。
- 你需要为游戏或虚拟制作项目批量生成大量对话动画 → 利用其批处理模块 (`MetaHumanBatchProcessor`) 自动化处理流程。
- 你希望基于语音音频生成面部动画草稿 → 使用其内置的 Speech2Face (`MetaHumanSpeech2Face`) 功能进行快速预览。
- 你需要对生成的动画数据进行精细的编辑和调整 → 通过其 Sequencer 集成 (`MetaHumanSequencer`) 在 UE 内完成。

## 蓝图用法
MetaHuman Animator 的功能主要通过编辑器工具和资产系统暴露，而非直接的蓝图节点。核心操作通常在 MetaHuman Animator 编辑器面板中完成。

### 核心节点
由于该插件的主要交互发生在编辑器UI和资产处理管线中，直接的 `BlueprintCallable` 节点较少。功能主要通过以下方式访问：
- **资产工厂**：创建 `UMetaHumanFaceContourTrackerAsset` 等核心资产。
- **编辑器工具**：通过工具栏按钮或面板启动动画捕捉和处理流程。
- **命令行/批处理**：使用 `MetaHumanBatchProcessor` 模块进行脚本化处理。

### 使用示例（蓝图描述）
虽然无法直接在蓝图中串联节点，但一个典型的 `MetaHumanPerformance`（性能资产）处理流程如下：
1. 在内容浏览器中右键，选择 “MetaHuman” -> “Performance” 创建一个新的 `UMetaHumanPerformance` 资产。
2. 在该资产的编辑器中，导入或引用视频素材。
3. 调整追踪和求解参数。
4. 点击“处理”按钮，插件会内部调用 `MetaHumanFaceContourTracker`、`MetaHumanFaceAnimationSolver` 等模块进行计算。
5. 处理完成后，将生成的动画序列应用到 MetaHuman 角色的骨骼网格体上。

## C++ 用法
此插件的 C++ 用法主要用于其内部模块的扩展、自定义处理管线或深度集成。对于终端开发者，主要是使用其提供的资产类和管理器。

### 头文件引入
```cpp
#include "MetaHumanFaceContourTrackerAsset.h" // 使用轮廓追踪资产
#include "MetaHumanPerformance.h"            // 使用性能（动画）资产
```

### 基本用法
（基于模块命名和常见UE资产模式推断）
```cpp
// 加载一个已创建的 MetaHumanPerformance 资产
UMetaHumanPerformance* PerformanceAsset = LoadObject<UMetaHumanPerformance>(nullptr, TEXT("/Game/Path/To/Your/PerformanceAsset.PerformanceAsset"));

// 访问其内部处理状态或数据（假设接口）
if (PerformanceAsset && PerformanceAsset->GetProcessingState() == EMetaHumanPerformanceProcessingState::Processed)
{
    UAnimSequence* ResultAnimSequence = PerformanceAsset->GetResultAnimSequence();
    // ... 将 ResultAnimSequence 应用到角色
}
```

### 进阶用法
开发一个自定义的 MetaHuman 动画处理节点，可能需要组合多个底层模块：
1. 使用 `MetaHumanCaptureSource` 模块接入原始视频流。
2. 将数据传递给 `MetaHumanFaceContourTracker` 进行面部特征点追踪。
3. 将追踪结果送入 `MetaHumanFaceAnimationSolver` 生成骨骼动画曲线。
4. 最后由 `MetaHumanFaceFittingSolver` 进行网格体拟合和优化。

## Demo 示例
一个最小示例，展示如何在 C++ 中创建一个 `MetaHumanFaceContourTracker` 资产并设置其基本属性。

**MyFaceTrackerManager.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "MetaHumanFaceContourTrackerAsset.h"
#include "MyFaceTrackerManager.generated.h"

UCLASS()
class UMyFaceTrackerManager : public UObject
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category = "MetaHuman")
    UMetaHumanFaceContourTrackerAsset* FaceTrackerAsset;

    /** 创建一个临时的面部轮廓追踪器资产 */
    UFUNCTION(BlueprintCallable, Category = "MetaHuman")
    UMetaHumanFaceContourTrackerAsset* CreateTempFaceTrackerAsset();

    /** 初始化追踪器资产参数 */
    UFUNCTION(BlueprintCallable, Category = "MetaHuman")
    void InitializeTrackerSettings(UMetaHumanFaceContourTrackerAsset* InTrackerAsset);
};
```

**MyFaceTrackerManager.cpp**
```cpp
#include "MyFaceTrackerManager.h"
#include "MetaHumanFaceContourTrackerAsset.h"

UMetaHumanFaceContourTrackerAsset* UMyFaceTrackerManager::CreateTempFaceTrackerAsset()
{
    // 使用 NewObject 在内存中创建资产（不保存到磁盘）
    UMetaHumanFaceContourTrackerAsset* NewAsset = NewObject<UMetaHumanFaceContourTrackerAsset>(
        GetTransientPackage(),
        UMetaHumanFaceContourTrackerAsset::StaticClass(),
        FName("TempFaceTracker"),
        RF_Transient | RF_Public
    );

    return NewAsset;
}

void UMyFaceTrackerManager::InitializeTrackerSettings(UMetaHumanFaceContourTrackerAsset* InTrackerAsset)
{
    if (!InTrackerAsset)
    {
        return;
    }

    // 这里假设 UMetaHumanFaceContourTrackerAsset 有可配置的参数
    // 例如，设置使用的模型或检测置信度阈值
    // InTrackerAsset->SetDetectionModel(EDetectionModel::Lite);
    // InTrackerAsset->SetConfidenceThreshold(0.7f);

    UE_LOG(LogTemp, Log, TEXT("Initialized MetaHuman Face Contour Tracker Asset: %s"), *InTrackerAsset->GetName());
}
```

## 模块依赖
该插件由多个相互依赖的模块组成。使用者（若要扩展此插件）通常需要依赖其核心运行时模块。以下是一些关键的独特依赖：

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | MetaHuman 核心技术库，提供底层的面部追踪、求解等算法实现。 |
| `ControlRigDeveloper` | 用于创建和编辑 MetaHuman 角色使用的 Control Rig 资产。 |
| `MetaHumanSDKEditor` | MetaHuman SDK 的编辑器部分，提供与 MetaHuman 云端服务或其他集成工具的接口。 |
| `SkeletalMeshUtilitiesCommon` | 提供处理骨骼网格体的通用工具函数，用于动画应用和网格体操作。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 在启用身体追踪时，禁用关卡序列动画的导出功能。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 角色身上的渲染瑕疵（可能指穿模或闪烁）。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 在身体追踪模式下，过滤掉不需要的可视化对象以提升性能或清晰度。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 为已有的网格体添加导出动画序列的功能。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 中导致缓存问题的错误。 |

### 维护评价
- **维护状态**：**活跃维护**。从提交记录看，该插件在近期（2026年5月）有密集的功能更新和bug修复，表明 Epic Games 仍在积极开发和改进此插件。
- **稳定性**：频繁的修复提交（如“Fix rendering artefacts”, “Fix sequencer caching issues”）表明团队在关注并解决现有问题，有助于提升稳定性。
- **推荐度**：**强烈推荐**。作为 Epic Games 官方维护的 MetaHuman 工作流核心工具，它功能完整、与UE引擎深度集成，且正处于活跃的开发和优化阶段。对于任何涉及 MetaHuman 角色动画的项目，它都是必选的工具集。
- **注意事项**：由于插件庞大且功能复杂，新用户可能需要时间来熟悉其完整的工作流和众多模块。建议参考 Epic Games 官方发布的 MetaHuman 相关教程和文档进行学习。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest)