# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、配置资产、编辑器工具） |
| 模块 | `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanToolkit` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MeshTrackerInterface` (Runtime), `MetaHumanControlsConversionTest` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-02-02 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的 MetaHuman 面部动画制作工具集。它解决的核心问题是：**如何将真实世界的面部表演数据（视频、深度信息、iPhone 捕获等）高效地转换为 MetaHuman 角色的面部动画**。

该插件提供了一套完整的面部动画制作流水线（Pipeline），涵盖以下关键能力：

1. **面部捕获数据导入**（MetaHumanCaptureSource / MetaHumanFootageIngest）：支持从多种来源导入面部表演素材，包括 iPhone TrueDepth 摄像头录制、专业面部捕捉设备、普通视频素材等。
2. **面部轮廓追踪**（MetaHumanFaceContourTracker）：对导入的视频帧进行面部关键点和轮廓的自动检测与追踪。
3. **深度图生成**（MetaHumanDepthGenerator）：从单目或多目视频生成面部深度信息，辅助后续的 3D 面部重建。
4. **面部拟合求解**（MetaHumanFaceFittingSolver）：将追踪到的 2D 面部数据拟合到 MetaHuman 的面部骨骼和控制绑定（Control Rig）上。
5. **面部动画求解**（MetaHumanFaceAnimationSolver）：基于拟合结果生成最终的面部动画曲线，驱动 MetaHuman 角色的面部表情。
6. **语音驱动面部动画**（MetaHumanSpeech2Face）：仅通过音频输入即可生成对应的面部口型动画（Lip Sync）。
7. **身份管理**（MetaHumanIdentity）：管理 MetaHuman 角色的面部身份数据，包括面部拓扑、骨骼映射等。
8. **Sequencer 集成**（MetaHumanSequencer）：将生成的面部动画无缝集成到 UE5 的 Sequencer 时间线中进行编辑和混合。
9. **批量处理**（MetaHumanBatchProcessor）：支持对大量捕获素材进行批量自动化处理。
10. **控制转换**（MetaHumanControlsConversionTest）：处理 GUI 控制参数与原始（Raw）控制参数之间的映射和转换。

简而言之，这个插件是 MetaHuman 角色从"静态模型"变为"活生生的表演"的核心桥梁。

## 使用场景

- 你有一个 MetaHuman 角色，需要基于 iPhone 录制的面部表演视频生成动画 → 使用 MetaHuman Animator 的捕获导入 + 追踪 + 拟合 + 求解流水线
- 你有一段对话音频，需要为 MetaHuman 角色生成口型同步动画 → 使用 Speech2Face 模块
- 你有一个影视级项目，需要批量处理数十个演员的面部表演数据 → 使用 MetaHumanBatchProcessor
- 你需要在 Sequencer 中对 MetaHuman 面部动画进行精细的时间线编辑和混合 → 使用 MetaHumanSequencer 集成
- 你使用专业的面部捕捉设备（如 HMC），需要将数据导入到 UE5 中驱动 MetaHuman → 使用 MetaHumanCaptureProtocolStack 和 MetaHumanCaptureSource
- 你需要管理多个 MetaHuman 角色的面部身份和控制绑定配置 → 使用 MetaHumanIdentity 和 MetaHumanConfig

## 蓝图用法

> **注意**：由于该插件规模极大（830+ 源文件），以下仅列出核心模块的关键蓝图接口。完整 API 请参考源码。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create MetaHuman Identity` | 创建新的 MetaHuman 面部身份资产 | `UMetaHumanIdentity` |
| `Import Capture Data` | 从文件路径导入面部捕获数据 | `UMetaHumanCaptureSource` |
| `Run Face Tracking` | 对捕获数据执行面部轮廓追踪 | `UMetaHumanFaceContourTracker` |
| `Generate Depth Map` | 从视频帧生成深度图 | `UMetaHumanDepthGenerator` |
| `Solve Face Fitting` | 将追踪数据拟合到 MetaHuman 面部网格 | `UMetaHumanFaceFittingSolver` |
| `Solve Face Animation` | 从拟合结果生成面部动画 | `UMetaHumanFaceAnimationSolver` |
| `Generate Speech Animation` | 从音频生成口型动画 | `UMetaHumanSpeech2Face` |
| `Batch Process` | 批量处理多个捕获数据资产 | `UMetaHumanBatchProcessor` |
| `Convert GUI to Raw Controls` | 将 GUI 控制参数转换为原始控制参数 | `UMetaHumanControlsConversion` |

### 使用示例（蓝图描述）

**基本面部动画制作流程**：

1. 在 Content Browser 中右键 → MetaHuman → 创建 MetaHuman Identity 资产
2. 在 Identity 编辑器中导入面部参考照片或视频
3. 配置面部标记点（Landmark），运行自动拟合
4. 导入表演捕获数据（iPhone 录制的 .mov 文件或专业设备数据）
5. 在 Pipeline 面板中依次执行：追踪 → 深度生成 → 拟合求解 → 动画求解
6. 生成的动画数据自动关联到 MetaHuman 的 Control Rig
7. 在 Sequencer 中播放和编辑生成的面部动画

**语音驱动动画**：

1. 准备一段对话音频文件
2. 使用 Speech2Face 模块，指定目标 MetaHuman Identity
3. 自动生成口型同步动画，可在 Sequencer 中进一步调整

## C++ 用法

### 头文件引入

```cpp
// 核心模块
#include "MetaHumanCoreModule.h"

// 面部身份
#include "MetaHumanIdentity.h"

// 捕获数据
#include "MetaHumanCaptureSource.h"

// 面部追踪
#include "MetaHumanFaceContourTracker.h"

// 面部拟合
#include "MetaHumanFaceFittingSolver.h"

// 面部动画求解
#include "MetaHumanFaceAnimationSolver.h"

// 流水线
#include "MetaHumanPipeline.h"

// 控制转换
#include "MetaHumanControlsConversion.h"
```

### 基本用法

以下示例展示了如何通过 C++ 代码驱动面部动画求解流程：

```cpp
// MetaHumanAnimator 基本面部动画求解流程
// 来源: MetaHumanFaceAnimationSolver 模块

#include "MetaHumanIdentity.h"
#include "MetaHumanFaceAnimationSolver.h"
#include "MetaHumanCaptureSource.h"

// 获取 MetaHuman Identity 资产
UMetaHumanIdentity* Identity = LoadObject<UMetaHumanIdentity>(
    nullptr, TEXT("/Game/MetaHumans/MyCharacter/MI_MyCharacter")
);

if (Identity)
{
    // 配置求解器参数
    FMetaHumanFaceAnimationSolverParams SolverParams;
    SolverParams.bUseGPU = true;
    SolverParams.QualityLevel = EMetaHumanQualityLevel::High;

    // 执行面部动画求解
    UMetaHumanFaceAnimationSolver* Solver = NewObject<UMetaHumanFaceAnimationSolver>();
    USkeletalMesh* TargetMesh = Identity->GetSkeletalMesh();

    FMetaHumanAnimationResult Result;
    bool bSuccess = Solver->SolveAnimation(
        CaptureData,      // 输入的捕获数据
        TargetMesh,       // 目标 MetaHuman 骨骼网格
        SolverParams,     // 求解参数
        Result            // 输出结果
    );

    if (bSuccess)
    {
        // 将结果应用到 Sequencer 或直接驱动 Control Rig
        UE_LOG(LogMetaHuman, Log, TEXT("Animation solved: %d frames"), Result.FrameCount);
    }
}
```

### 进阶用法

以下示例展示了批量处理和自定义流水线的用法：

```cpp
// MetaHumanAnimator 批量处理示例
// 来源: MetaHumanBatchProcessor + MetaHumanPipeline 模块

#include "MetaHumanBatchProcessor.h"
#include "MetaHumanPipeline.h"
#include "MetaHumanIdentity.h"

// 自定义处理流水线
class FMyCustomPipeline : public FMetaHumanPipeline
{
public:
    virtual void Configure() override
    {
        // 添加处理步骤
        AddStep<FMetaHumanFaceTrackingStep>();
        AddStep<FMetaHumanDepthGenerationStep>();
        AddStep<FMetaHumanFaceFittingStep>();
        AddStep<FMetaHumanFaceAnimationStep>();

        // 配置各步骤参数
        SetStepParam<FMetaHumanFaceTrackingStep>(
            "bInterpolateGaps", true
        );
        SetStepParam<FMetaHumanDepthGenerationStep>(
            "Resolution", EMetaHumanDepthResolution::High
        );
    }
};

// 批量处理多个捕获数据
void BatchProcessCaptures(const TArray<FAssetData>& CaptureAssets)
{
    UMetaHumanBatchProcessor* BatchProcessor = NewObject<UMetaHumanBatchProcessor>();

    FMetaHumanBatchProcessSettings Settings;
    Settings.PipelineClass = FMyCustomPipeline::StaticClass();
    Settings.MaxConcurrentTasks = 4;
    Settings.bAutoSaveResults = true;

    // 绑定进度回调
    BatchProcessor->OnProgress.AddLambda(
        [](int32 Current, int32 Total, const FString& AssetName)
        {
            UE_LOG(LogMetaHuman, Log,
                TEXT("Processing %d/%d: %s"), Current, Total, *AssetName
            );
        }
    );

    // 绑定完成回调
    BatchProcessor->OnComplete.AddLambda(
        [](const FMetaHumanBatchResult& Result)
        {
            UE_LOG(LogMetaHuman, Log,
                TEXT("Batch complete: %d succeeded, %d failed"),
                Result.SucceededCount, Result.FailedCount
            );
        }
    );

    // 启动批量处理
    BatchProcessor->StartBatchProcess(CaptureAssets, Settings);
}
```

### 控制转换用法

```cpp
// GUI 控制参数与原始控制参数之间的转换
// 来源: MetaHumanControlsConversionTest 模块

#include "MetaHumanControlsConversion.h"

// GUI 控制参数 → 原始（Raw）控制参数
void ConvertControlsExample()
{
    // GUI 控制参数是面向用户的、经过美化的参数名称
    // Raw 控制参数是底层 Control Rig 实际使用的参数
    TMap<FName, float> GUIControls;
    GUIControls.Add(FName("CTRL_L_brow_up"), 0.75f);
    GUIControls.Add(FName("CTRL_R_brow_up"), 0.60f);
    GUIControls.Add(FName("CTRL_mouth_smile"), 0.90f);

    TMap<FName, float> RawControls;
    FMetaHumanControlsConversion::ConvertGUIToRaw(GUIControls, RawControls);

    // RawControls 现在包含底层 Control Rig 可直接使用的参数值
    // 注意：RBF 控制已从 GUI→Raw 转换中移除（参见 git commit 3293be28）
}
```

## Demo 示例

以下是一个最小的 MetaHuman 面部动画求解示例：

### MetaHumanAnimatorDemo.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MetaHumanAnimatorDemo.generated.h"

class UMetaHumanIdentity;
class UMetaHumanFaceAnimationSolver;
class UMetaHumanCaptureSource;

UCLASS(BlueprintType)
class MYPROJECT_API AMetaHumanAnimatorDemo : public AActor
{
    GENERATED_BODY()

public:
    AMetaHumanAnimatorDemo();

    /** 要处理的 MetaHuman Identity 资产 */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MetaHuman")
    TSoftObjectPtr<UMetaHumanIdentity> IdentityAsset;

    /** 捕获数据源路径 */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MetaHuman")
    FDirectoryPath CaptureDataPath;

    /** 是否使用 GPU 加速 */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MetaHuman")
    bool bUseGPU = true;

    /** 开始处理 */
    UFUNCTION(BlueprintCallable, Category = "MetaHuman")
    void StartProcessing();

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY()
    UMetaHumanFaceAnimationSolver* Solver;

    UPROPERTY()
    UMetaHumanCaptureSource* CaptureSource;

    void OnProcessingComplete(bool bSuccess);
};
```

### MetaHumanAnimatorDemo.cpp

```cpp
#include "MetaHumanAnimatorDemo.h"
#include "MetaHumanIdentity.h"
#include "MetaHumanFaceAnimationSolver.h"
#include "MetaHumanCaptureSource.h"

AMetaHumanAnimatorDemo::AMetaHumanAnimatorDemo()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMetaHumanAnimatorDemo::BeginPlay()
{
    Super::BeginPlay();

    // 创建求解器实例
    Solver = NewObject<UMetaHumanFaceAnimationSolver>(this);
    CaptureSource = NewObject<UMetaHumanCaptureSource>(this);
}

void AMetaHumanAnimatorDemo::StartProcessing()
{
    if (!Solver || !CaptureSource)
    {
        UE_LOG(LogTemp, Error, TEXT("Solver or CaptureSource not initialized"));
        return;
    }

    // 加载 Identity 资产
    UMetaHumanIdentity* Identity = IdentityAsset.LoadSynchronous();
    if (!Identity)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load Identity asset"));
        return;
    }

    // 导入捕获数据
    bool bImported = CaptureSource->ImportFromDirectory(CaptureDataPath.Path);
    if (!bImported)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to import capture data from: %s"),
            *CaptureDataPath.Path);
        return;
    }

    // 配置求解参数
    FMetaHumanFaceAnimationSolverParams Params;
    Params.bUseGPU = bUseGPU;

    UE_LOG(LogTemp, Log, TEXT("Starting MetaHuman animation processing..."));

    // 异步执行求解（实际使用中应绑定回调）
    // Solver->SolveAnimationAsync(CaptureSource, Identity, Params,
    //     FOnAnimationSolveComplete::CreateUObject(
    //         this, &AMetaHumanAnimatorDemo::OnProcessingComplete
    //     )
    // );
}

void AMetaHumanAnimatorDemo::OnProcessingComplete(bool bSuccess)
{
    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("MetaHuman animation processing completed successfully"));
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("MetaHuman animation processing failed"));
    }
}
```

## 模块依赖

该插件包含 28 个模块，以下列出各模块之间的关键依赖关系和使用者需要关注的外部依赖：

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | MetaHuman 核心技术库（底层算法，面部拟合/求解的数学基础） |
| `SkeletalMeshUtilitiesCommon` | 骨骼网格工具（面部网格处理和变形） |
| `ControlRigDeveloper` | Control Rig 开发者工具（面部控制绑定的创建和编辑） |
| `MetaHumanSDKEditor` | MetaHuman SDK 编辑器集成（与 MetaHuman Creator 的接口） |
| `MetaHumanImageViewerEditor` | 图像查看器编辑器（捕获数据的预览和检查） |

> **注意**：该插件的模块之间存在大量内部依赖。如果你只需要使用部分功能（如仅使用面部追踪），可以仅依赖对应的子模块。但完整的面部动画制作流程需要依赖 MetaHumanCore 及其下游模块。

## 维护状态

### 近期更新

```
- 0f2260027766 [MH-Plugin] Unify the interchange usage between plugins #rb Thales.Sabino #virtualized
- 3293be285c68 Removing RBF controls from Gui to Raw control conversion
- 3f5e7c60251f Updated GUI to raw control name mappings
```

### 维护评价

- **创建时间**：2024 年 2 月，属于较新的插件
- **更新频率**：从近期 commit 来看，仍在积极维护中，有功能更新和重构
- **活跃程度**：活跃维护中。MetaHuman 是 Epic Games 的战略级产品线，Animator 作为核心工具链的一部分，预计会持续获得更新
- **已知限制**：
  - 仅支持 Win64 和 Linux 平台（不支持 macOS/移动端）
  - 默认未启用（`Installed: false`），需要在插件管理器中手动启用
  - 部分高级功能（如 HMC 捕获设备支持）可能需要额外的第三方库
  - 控制转换模块中已移除 RBF 控制的 GUI→Raw 转换（commit 3293be28）
- **推荐程度**：⭐⭐⭐⭐⭐ 强烈推荐。这是 Epic Games 官方维护的 MetaHuman 动画制作工具，是使用 MetaHuman 角色进行面部动画制作的首选方案。对于需要高质量面部动画的项目，这是不可或缺的插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/en-US/metahuman-animator/)（MetaHuman Animator 官方文档）
- [MetaHuman Creator](https://metahuman.unrealengine.com/)（在线 MetaHuman 创建工具）