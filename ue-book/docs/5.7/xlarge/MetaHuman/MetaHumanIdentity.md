# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（MetaHuman 资产、配置、模板） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-02-02 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的 MetaHuman 角色动画制作工具链。它解决的核心问题是：**如何从真实人脸的视频或扫描数据，自动生成带有完整骨骼绑定的 MetaHuman 面部网格，并驱动面部动画**。

整个工作流程分为三个主要阶段：

1. **Identity 创建**（MetaHumanIdentity 模块）：从面部视频或 3D 扫描数据中提取面部特征，通过轮廓追踪、模板网格拟合，生成一个代表特定人脸的 Identity 资产。该资产可以发送到 MetaHuman Service 进行自动绑定，生成带有 MetaHuman 拓扑的骨骼网格体。

2. **Performance 捕获**（MetaHumanPerformance 模块）：使用已创建的 Identity，从新的视频素材中提取面部动画数据，生成动画序列。

3. **管线处理**（MetaHumanPipeline 模块）：提供可扩展的处理管线架构，将各个处理步骤（追踪、拟合、求解等）串联起来。

该插件包含 28 个模块，覆盖了从数据采集、面部追踪、网格拟合、预测求解器训练到 Sequencer 集成的完整流程。

## 使用场景

- 你有一段演员面部的视频素材，需要生成一个逼真的 MetaHuman 角色 → 使用 MetaHuman Identity 工作流
- 你已经有了 MetaHuman Identity，需要从新的视频中提取面部动画 → 使用 MetaHuman Performance 工作流
- 你需要批量处理多个 MetaHuman 角色的动画数据 → 使用 MetaHumanBatchProcessor
- 你需要通过 Live Link 实时捕捉面部数据 → 使用 MetaHumanCaptureProtocolStack
- 你需要从音频生成面部动画 → 使用 MetaHumanSpeech2Face

## 模块架构

```
MetaHumanAnimator/
├── MetaHumanIdentity          ← 核心：Identity 资产定义与管理
├── MetaHumanIdentityEditor    ← Identity 编辑器 UI
├── MetaHumanPerformance       ← Performance 动画提取
├── MetaHumanPipeline          ← 处理管线框架
├── MetaHumanFaceContourTracker ← 面部轮廓追踪
├── MetaHumanFaceFittingSolver  ← 面部网格拟合求解
├── MetaHumanFaceAnimationSolver ← 面部动画求解
├── MetaHumanDepthGenerator    ← 深度图生成
├── MetaHumanCaptureSource     ← 捕获数据源
├── MetaHumanCaptureProtocolStack ← 捕获协议栈
├── MetaHumanCaptureUtils      ← 捕获工具函数
├── MetaHumanSpeech2Face       ← 语音驱动面部
├── MetaHumanBatchProcessor    ← 批量处理
├── MetaHumanSequencer         ← Sequencer 集成
├── MetaHumanToolkit           ← 工具箱 UI
├── MetaHumanConfig            ← 配置管理
├── MetaHumanCore              ← 核心工具库
├── MetaHumanPlatform          ← 平台抽象层
├── MeshTrackerInterface       ← 网格追踪器接口
└── ...Editor 模块             ← 各模块的编辑器扩展
```

## 子模块文档

| 模块 | 说明 | 文档 |
|---|---|---|
| MetaHumanIdentity | Identity 资产核心，管理面部/身体部位、姿态、提升帧 | [详细文档](./MetaHumanIdentity.md) |
| MetaHumanPerformance | 从视频提取面部动画 | - |
| MetaHumanPipeline | 处理管线框架 | - |
| MetaHumanFaceContourTracker | 面部轮廓追踪算法 | - |
| MetaHumanFaceFittingSolver | 面部网格拟合求解 | - |
| MetaHumanSpeech2Face | 语音驱动面部动画 | - |
| MetaHumanBatchProcessor | 批量处理工具 | - |

## 模块依赖

| 模块 | 用途 |
|---|---|
| `SkeletalMeshUtilitiesCommon` | 骨骼网格体工具函数 |
| `ControlRigDeveloper` | Control Rig 开发者工具，用于面部绑定 |
| `MetaHumanCaptureDataEditor` | 捕获数据编辑器 |
| `MetaHumanSDKEditor` | MetaHuman SDK 编辑器集成 |

## 维护状态

### 近期更新

```
- 9c62fae4c655 [MHA] Removing whitespace from the loctext #rb skip
- c202ed7d4678 [Backout] - CL46258616 [FYI] richard.graham - Backing out as does not work as required for BP scripting users. #rnx
- 5eabb033c502 [Metahuman BP API] - Allow BP scripting access to the MH Identity validation state so users can create batch scripts that can check for a valid (prepared for performance) identity.
```

### 维护评价

MetaHuman Animator 是 Epic Games 的旗舰产品之一，创建于 2024 年 2 月，属于较新的插件。从近期 commit 可以看到：

- **活跃开发中**：仍在持续添加新功能（如蓝图 API 扩展）
- **代码质量高**：有完善的日志系统、状态验证、错误处理
- **架构成熟**：28 个模块的清晰分层，Runtime/Editor 分离
- **已知限制**：最近一次 commit 回退了蓝图验证状态 API，说明部分功能仍在迭代中

**推荐使用**：这是 MetaHuman 工作流的核心组件，如果你在使用 MetaHuman 角色，这个插件是必需的。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/metahuman-animator-in-unreal-engine/)（MetaHuman Animator 文档）

---

# MetaHumanIdentity 模块

> MetaHuman Identity 资产核心模块，管理面部/身体部位、姿态、提升帧和模板网格

## 模块概述

MetaHumanIdentity 是 MetaHuman Animator 的核心模块，定义了 `UMetaHumanIdentity` 资产及其相关组件。该模块负责：

1. **Identity 资产管理**：定义和管理 MetaHuman Identity 资产，包含面部和身体部位
2. **姿态系统**：管理 Neutral（中性表情）和 Teeth（牙齿）等姿态的捕获数据
3. **提升帧（Promoted Frames）**：从视频中选取关键帧进行面部特征追踪
4. **模板网格管理**：管理用于拟合的 MetaHuman 拓扑模板网格
5. **预测求解器**：异步训练预测求解器，用于面部动画
6. **状态验证**：追踪 Identity 的处理进度和有效性

## 核心类

### UMetaHumanIdentity

Identity 资产的主类，代表一个完整的 MetaHuman 身份。

```cpp
// 获取或创建 Identity 资产
UMetaHumanIdentity* Identity = NewObject<UMetaHumanIdentity>();

// 查找面部部位
UMetaHumanIdentityPart* FacePart = Identity->FindPartOfClass(UMetaHumanIdentityFace::StaticClass());

// 获取或创建部位（不存在则创建）
UMetaHumanIdentityPart* Part = Identity->GetOrCreatePartOfClass(UMetaHumanIdentityFace::StaticClass());
```

### UMetaHumanIdentityPose

表示 Identity 的一个姿态（如中性表情、牙齿姿态）。

```cpp
// 创建姿态并设置捕获数据
UMetaHumanIdentityPose* Pose = NewObject<UMetaHumanIdentityPose>();
Pose->SetCaptureData(MyCaptureData);

// 添加提升帧
int32 FrameIndex;
UMetaHumanIdentityPromotedFrame* Frame = Pose->AddNewPromotedFrame(FrameIndex);

// 获取所有有效轮廓数据的帧
TArray<UMetaHumanIdentityPromotedFrame*> ValidFrames = Pose->GetAllPromotedFramesWithValidContourData();
```

### UMetaHumanIdentityPromotedFrame

表示从视频中选取的关键帧，用于面部特征追踪。

```cpp
// 检查帧是否可以追踪
if (Frame->CanTrack())
{
    // 检查是否有活跃的轮廓数据
    if (Frame->FrameContoursContainActiveData())
    {
        // 执行追踪...
    }
}

// 检查诊断信息
FText WarningMessage;
float MinCoverage = 0.8f;
float MinWidth = 0.5f;
if (Frame->DiagnosticsIndicatesProcessingIssue(MinCoverage, MinWidth, WarningMessage))
{
    UE_LOG(LogMetaHumanIdentity, Warning, TEXT("Diagnostic issue: %s"), *WarningMessage.ToString());
}
```

### UMetaHumanTemplateMeshComponent

管理 MetaHuman 模板网格的组件，支持头部、眼睛和牙齿网格。

```cpp
// 加载网格资产
TemplateMeshComponent->LoadMeshAssets();
TemplateMeshComponent->LoadMaterialsForMeshes();

// 显示特定姿态的头部网格
TemplateMeshComponent->ShowHeadMeshForPose(EIdentityPoseType::Neutral);

// 获取和设置顶点
TArray<FVector> HeadVertices;
TemplateMeshComponent->GetPoseHeadMeshVertices(
    EIdentityPoseType::Neutral,
    FTransform::Identity,
    ETemplateVertexConversion::ConformerToUE,
    HeadVertices
);

// 管理眼睛和牙齿网格
TemplateMeshComponent->SetEyeMeshesVisibility(true);
TemplateMeshComponent->SetTeethMeshVisibility(true);
```

### FPredictiveSolversTask

异步训练预测求解器的任务类。

```cpp
// 配置求解器任务
FPredictiveSolversTaskConfig Config;
Config.TemplateDescriptionJson = TEXT("...");
Config.ConfigurationJson = TEXT("...");
Config.DNAAsset = MyDNAAsset;
Config.bTrainPreviewSolvers = true;

// 同步执行
FPredictiveSolversTask Task(Config);
FPredictiveSolversResult Result = Task.StartSync();

if (Result.bSuccess)
{
    // 使用训练结果
    TArray<uint8> SolverData = Result.PredictiveSolvers;
}

// 或异步执行
FPredictiveSolversTask AsyncTask(Config);
AsyncTask.OnCompletedCallback().BindLambda([](const FPredictiveSolversResult& Result)
{
    if (Result.bSuccess)
    {
        // 处理完成
    }
});
AsyncTask.OnProgressCallback().BindLambda([](float Progress)
{
    UE_LOG(LogMetaHumanIdentity, Log, TEXT("Training progress: %.1f%%"), Progress * 100.0f);
});
AsyncTask.StartAsync();

// 轮询进度
float CurrentProgress;
if (AsyncTask.PollProgress(CurrentProgress))
{
    // 任务仍在进行
}

// 取消任务
AsyncTask.Cancel();
```

### FMetaHumanIdentityStateValidator

验证 Identity 处理状态的工具类。

```cpp
// 初始化验证器
FMetaHumanIdentityStateValidator Validator;
Validator.PostAssetLoadHashInitialization(Identity);

// 更新处理进度
Validator.UpdateIdentityProgress();

// 更新各个阶段的状态
Validator.MeshConformedStateUpdate();
Validator.MeshAutoriggedUpdate();
Validator.MeshPreparedForPerformanceUpdate();
Validator.TeethFittedUpdate();

// 获取无效状态提示
FText Tooltip = Validator.GetInvalidationStateToolTip();
```

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Find Part Of Class` | 查找指定类型的部位 | `UMetaHumanIdentity` |
| `Get Or Create Part Of Class` | 获取或创建指定类型的部位 | `UMetaHumanIdentity` |
| `Set Capture Data` | 设置姿态的捕获数据 | `UMetaHumanIdentityPose` |
| `Get Capture Data` | 获取姿态的捕获数据 | `UMetaHumanIdentityPose` |
| `Is Capture Data Valid` | 检查捕获数据是否有效 | `UMetaHumanIdentityPose` |
| `Add New Promoted Frame` | 添加新的提升帧 | `UMetaHumanIdentityPose` |
| `Remove Promoted Frame` | 移除提升帧 | `UMetaHumanIdentityPose` |
| `Frame Contours Contain Active Data` | 检查帧是否有活跃轮廓数据 | `UMetaHumanIdentityPromotedFrame` |
| `Can Track` | 检查帧是否可以追踪 | `UMetaHumanIdentityPromotedFrame` |
| `Is Navigation Locked` | 检查导航是否锁定 | `UMetaHumanIdentityPromotedFrame` |
| `Set Navigation Locked` | 设置导航锁定状态 | `UMetaHumanIdentityPromotedFrame` |
| `Toggle Navigation Locked` | 切换导航锁定状态 | `UMetaHumanIdentityPromotedFrame` |
| `Diagnostics Indicates Processing Issue` | 检查诊断是否指示处理问题 | `UMetaHumanIdentityPromotedFrame` |
| `Initialize Contour Data For Footage Frame` | 为素材帧初始化轮廓数据 | `UPromotedFrameUtils` |
| `Get Promoted Frame As Pixel Array From Disk` | 从磁盘获取提升帧的像素数组 | `UPromotedFrameUtils` |
| `Get Image Path For Frame` | 获取帧的图像路径 | `UPromotedFrameUtils` |
| `Toggle Current Pose Visibility` | 切换当前姿态可见性 | `UMetaHumanIdentityViewportSettings` |
| `Is Current Pose Visible` | 检查当前姿态是否可见 | `UMetaHumanIdentityViewportSettings` |
| `Toggle Template Mesh Visibility` | 切换模板网格可见性 | `UMetaHumanIdentityViewportSettings` |
| `Is Template Mesh Visible` | 检查模板网格是否可见 | `UMetaHumanIdentityViewportSettings` |
| `Set Selected Promoted Frame` | 设置选中的提升帧 | `UMetaHumanIdentityViewportSettings` |
| `Get Selected Promoted Frame` | 获取选中的提升帧 | `UMetaHumanIdentityViewportSettings` |
| `Set Frame Time For Pose` | 设置姿态的帧时间 | `UMetaHumanIdentityViewportSettings` |
| `Get Frame Time For Pose` | 获取姿态的帧时间 | `UMetaHumanIdentityViewportSettings` |

### 使用示例（蓝图描述）

**创建 Identity 并设置捕获数据：**

1. 使用 `Create Object` 节点创建 `UMetaHumanIdentity` 实例
2. 使用 `Get Or Create Part Of Class` 节点获取 `UMetaHumanIdentityFace` 部位
3. 从面部部位获取 Neutral 姿态
4. 使用 `Set Capture Data` 节点设置视频捕获数据
5. 使用 `Add New Promoted Frame` 添加关键帧
6. 使用 `Initialize Contour Data For Footage Frame` 初始化轮廓数据

**检查 Identity 处理状态：**

1. 获取 `UMetaHumanIdentityPromotedFrame` 引用
2. 使用 `Can Track` 检查是否可以追踪
3. 使用 `Frame Contours Contain Active Data` 检查轮廓数据
4. 使用 `Diagnostics Indicators Processing Issue` 检查诊断问题

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanIdentity.h"
#include "MetaHumanIdentityParts.h"
#include "MetaHumanIdentityPose.h"
#include "MetaHumanIdentityPromotedFrames.h"
#include "MetaHumanTemplateMeshComponent.h"
#include "MetaHumanPredictiveSolversTask.h"
#include "MetaHumanIdentityStateValidator.h"
#include "PromotedFrameUtils.h"
```

### 基本用法

**创建和管理 Identity 资产：**

```cpp
// 创建 Identity 资产
UMetaHumanIdentity* Identity = NewObject<UMetaHumanIdentity>();

// 获取或创建面部部位
UMetaHumanIdentityFace* Face = Cast<UMetaHumanIdentityFace>(
    Identity->GetOrCreatePartOfClass(UMetaHumanIdentityFace::StaticClass())
);

// 获取 Neutral 姿态
UMetaHumanIdentityPose* NeutralPose = Face->GetPose(EIdentityPoseType::Neutral);

// 设置捕获数据
NeutralPose->SetCaptureData(MyCaptureData);

// 添加提升帧
int32 FrameIndex;
UMetaHumanIdentityPromotedFrame* Frame = NeutralPose->AddNewPromotedFrame(FrameIndex);

// 初始化轮廓数据
UPromotedFrameUtils::InitializeContourDataForFootageFrame(NeutralPose, Cast<UMetaHumanIdentityFootageFrame>(Frame));
```

**检查帧状态：**

```cpp
// 检查帧是否可以追踪
if (Frame->CanTrack())
{
    // 检查是否有活跃的轮廓数据
    if (Frame->FrameContoursContainActiveData())
    {
        // 执行追踪操作
    }
}

// 检查诊断信息
FText WarningMessage;
float MinCoverage = 0.8f;
float MinWidth = 0.5f;
if (Frame->DiagnosticsIndicatesProcessingIssue(MinCoverage, MinWidth, WarningMessage))
{
    UE_LOG(LogMetaHumanIdentity, Warning, TEXT("Diagnostic issue: %s"), *WarningMessage.ToString());
}
```

### 进阶用法

**异步训练预测求解器：**

```cpp
// 配置求解器任务
FPredictiveSolversTaskConfig Config;
Config.TemplateDescriptionJson = LoadTemplateJson();
Config.ConfigurationJson = LoadConfigJson();
Config.DNAAsset = LoadDNAAsset();
Config.bTrainPreviewSolvers = true;

// 创建异步任务
FPredictiveSolversTask Task(Config);

// 绑定完成回调
Task.OnCompletedCallback().BindLambda([this](const FPredictiveSolversResult& Result)
{
    if (Result.bSuccess)
    {
        // 保存训练结果
        SaveSolverData(Result.PredictiveSolvers);
        SaveSolverData(Result.PredictiveWithoutTeethSolver);
    }
});

// 绑定进度回调
Task.OnProgressCallback().BindLambda([](float Progress)
{
    UE_LOG(LogMetaHumanIdentity, Log, TEXT("Training progress: %.1f%%"), Progress * 100.0f);
});

// 启动异步任务
Task.StartAsync();

// 在 Tick 中轮询进度
void Tick(float DeltaTime)
{
    float Progress;
    if (Task.PollProgress(Progress))
    {
        // 更新进度条
        UpdateProgressBar(Progress);
    }
    
    if (Task.IsDone())
    {
        // 任务完成
    }
}

// 可以随时取消
Task.Cancel();
```

**管理模板网格：**

```cpp
// 获取模板网格组件
UMetaHumanTemplateMeshComponent* TemplateMesh = GetTemplateMeshComponent();

// 加载网格资产
TemplateMesh->LoadMeshAssets();
TemplateMesh->LoadMaterialsForMeshes();

// 显示 Neutral 姿态的头部网格
TemplateMesh->ShowHeadMeshForPose(EIdentityPoseType::Neutral);

// 获取顶点数据（从 Conformer 空间转换到 UE 空间）
TArray<FVector> HeadVertices;
TemplateMesh->GetPoseHeadMeshVertices(
    EIdentityPoseType::Neutral,
    FTransform::Identity,
    ETemplateVertexConversion::ConformerToUE,
    HeadVertices
);

// 获取眼睛和牙齿顶点
TArray<FVector> LeftEyeVertices, RightEyeVertices;
TemplateMesh->GetEyeMeshesVertices(
    FTransform::Identity,
    ETemplateVertexConversion::ConformerToUE,
    LeftEyeVertices,
    RightEyeVertices
);

TArray<FVector> TeethVertices;
TemplateMesh->GetTeethMeshVertices(
    FTransform::Identity,
    ETemplateVertexConversion::ConformerToUE,
    TeethVertices
);

// 设置眼睛和牙齿可见性
TemplateMesh->SetEyeMeshesVisibility(true);
TemplateMesh->SetTeethMeshVisibility(true);
```

**状态验证：**

```cpp
// 创建状态验证器
FMetaHumanIdentityStateValidator Validator;

// 在资产加载后初始化
Validator.PostAssetLoadHashInitialization(Identity);

// 在各个处理阶段更新状态
Validator.MeshConformedStateUpdate();  // 网格拟合完成
Validator.MeshAutoriggedUpdate();      // 自动绑定完成
Validator.TeethFittedUpdate();         // 牙齿拟合完成
Validator.MeshPreparedForPerformanceUpdate();  // 准备用于 Performance

// 更新整体进度
Validator.UpdateIdentityProgress();

// 获取无效状态提示
FText Tooltip = Validator.GetInvalidationStateToolTip();
if (!Tooltip.IsEmpty())
{
    UE_LOG(LogMetaHumanIdentity, Warning, TEXT("Identity state issue: %s"), *Tooltip.ToString());
}
```

## Demo 示例

### 完整的 Identity 创建和验证流程

```cpp
// MetaHumanIdentityManager.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MetaHumanIdentityManager.generated.h"

class UMetaHumanIdentity;
class UMetaHumanIdentityFace;
class UMetaHumanIdentityPose;
class UMetaHumanIdentityPromotedFrame;
class UMetaHumanTemplateMeshComponent;
class FPredictiveSolversTask;
class FMetaHumanIdentityStateValidator;

UCLASS()
class AMetaHumanIdentityManager : public AActor
{
    GENERATED_BODY()

public:
    AMetaHumanIdentityManager();

    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    // 创建新的 Identity
    UFUNCTION(BlueprintCallable, Category = "MetaHuman")
    void CreateNewIdentity();

    // 设置捕获数据
    UFUNCTION(BlueprintCallable, Category = "MetaHuman")
    void SetCaptureData(UCaptureData* CaptureData);

    // 添加提升帧
    UFUNCTION(BlueprintCallable, Category = "MetaHuman")
    UMetaHumanIdentityPromotedFrame* AddPromotedFrame(int32& OutFrameIndex);

    // 开始异步训练求解器
    UFUNCTION(BlueprintCallable, Category = "MetaHuman")
    void StartSolverTraining();

    // 取消训练
    UFUNCTION(BlueprintCallable, Category = "MetaHuman")
    void CancelSolverTraining();

    // 检查 Identity 状态
    UFUNCTION(BlueprintCallable, Category = "MetaHuman")
    bool IsIdentityValid() const;

    // 获取训练进度
    UFUNCTION(BlueprintPure, Category = "MetaHuman")
    float GetTrainingProgress() const;

    // 获取状态提示
    UFUNCTION(BlueprintPure, Category = "MetaHuman")
    FText GetStateTooltip() const;

protected:
    // Identity 资产
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MetaHuman")
    UMetaHumanIdentity* Identity;

    // 面部部位
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MetaHuman")
    UMetaHumanIdentityFace* FacePart;

    // Neutral 姿态
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MetaHuman")
    UMetaHumanIdentityPose* NeutralPose;

    // 模板网格组件
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MetaHuman")
    UMetaHumanTemplateMeshComponent* TemplateMeshComponent;

private:
    // 预测求解器任务
    TUniquePtr<FPredictiveSolversTask> SolverTask;

    // 状态验证器
    TSharedPtr<FMetaHumanIdentityStateValidator> StateValidator;

    // 训练进度
    float CurrentTrainingProgress;

    // 是否正在训练
    bool bIsTraining;
};
```

```cpp
// MetaHumanIdentityManager.cpp
#include "MetaHumanIdentityManager.h"
#include "MetaHumanIdentity.h"
#include "MetaHumanIdentityParts.h"
#include "MetaHumanIdentityPose.h"
#include "MetaHumanIdentityPromotedFrames.h"
#include "MetaHumanTemplateMeshComponent.h"
#include "MetaHumanPredictiveSolversTask.h"
#include "MetaHumanIdentityStateValidator.h"
#include "PromotedFrameUtils.h"
#include "MetaHumanIdentityLog.h"

AMetaHumanIdentityManager::AMetaHumanIdentityManager()
{
    PrimaryActorTick.bCanEverTick = true;

    // 创建模板网格组件
    TemplateMeshComponent = CreateDefaultSubobject<UMetaHumanTemplateMeshComponent>(TEXT("TemplateMesh"));
    RootComponent = TemplateMeshComponent;

    CurrentTrainingProgress = 0.0f;
    bIsTraining = false;
}

void AMetaHumanIdentityManager::BeginPlay()
{
    Super::BeginPlay();

    // 自动创建 Identity
    CreateNewIdentity();
}

void AMetaHumanIdentityManager::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    // 轮询求解器训练进度
    if (bIsTraining && SolverTask.IsValid())
    {
        float Progress;
        if (SolverTask->PollProgress(Progress))
        {
            CurrentTrainingProgress = Progress;
        }

        if (SolverTask->IsDone())
        {
            bIsTraining = false;
            UE_LOG(LogMetaHumanIdentity, Log, TEXT("Solver training completed"));
        }
    }
}

void AMetaHumanIdentityManager::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    // 取消正在进行的训练
    if (SolverTask.IsValid() && bIsTraining)
    {
        SolverTask->Cancel();
    }

    Super::EndPlay(EndPlayReason);
}

void AMetaHumanIdentityManager::CreateNewIdentity()
{
    // 创建 Identity 资产
    Identity = NewObject<UMetaHumanIdentity>();

    // 获取或创建面部部位
    FacePart = Cast<UMetaHumanIdentityFace>(
        Identity->GetOrCreatePartOfClass(UMetaHumanIdentityFace::StaticClass())
    );

    if (FacePart)
    {
        // 获取 Neutral 姿态
        NeutralPose = FacePart->GetPose(EIdentityPoseType::Neutral);

        if (NeutralPose)
        {
            UE_LOG(LogMetaHumanIdentity, Log, TEXT("Identity created with Neutral pose"));
        }
    }

    // 初始化状态验证器
    StateValidator = MakeShared<FMetaHumanIdentityStateValidator>();
    StateValidator->PostAssetLoadHashInitialization(Identity);

    // 加载模板网格
    TemplateMeshComponent->LoadMeshAssets();
    TemplateMeshComponent->LoadMaterialsForMeshes();
    TemplateMeshComponent->ShowHeadMeshForPose(EIdentityPoseType::Neutral);
}

void AMetaHumanIdentityManager::SetCaptureData(UCaptureData* CaptureData)
{
    if (NeutralPose && CaptureData)
    {
        NeutralPose->SetCaptureData(CaptureData);
        UE_LOG(LogMetaHumanIdentity, Log, TEXT("Capture data set for Neutral pose"));
    }
}

UMetaHumanIdentityPromotedFrame* AMetaHumanIdentityManager::AddPromotedFrame(int32& OutFrameIndex)
{
    if (!NeutralPose)
    {
        return nullptr;
    }

    UMetaHumanIdentityPromotedFrame* Frame = NeutralPose->AddNewPromotedFrame(OutFrameIndex);

    if (Frame)
    {
        UE_LOG(LogMetaHumanIdentity, Log, TEXT("Promoted frame added at index %d"), OutFrameIndex);

        // 初始化轮廓数据
        UPromotedFrameUtils::InitializeContourDataForFootageFrame(
            NeutralPose,
            Cast<UMetaHumanIdentityFootageFrame>(Frame)
        );
    }

    return Frame;
}

void AMetaHumanIdentityManager::StartSolverTraining()
{
    if (bIsTraining)
    {
        UE_LOG(LogMetaHumanIdentity, Warning, TEXT("Training already in progress"));
        return;
    }

    // 配置求解器任务
    FPredictiveSolversTaskConfig Config;
    Config.TemplateDescriptionJson = TEXT("{}");  // 实际使用时加载真实配置
    Config.ConfigurationJson = TEXT("{}");
    Config.DNAAsset = nullptr;  // 实际使用时加载 DNA 资产
    Config.bTrainPreviewSolvers = true;

    // 创建并启动异步任务
    SolverTask = MakeUnique<FPredictiveSolversTask>(Config);

    // 绑定完成回调
    SolverTask->OnCompletedCallback().BindLambda([this](const FPredictiveSolversResult& Result)
    {
        if (Result.bSuccess)
        {
            UE_LOG(LogMetaHumanIdentity, Log, TEXT("Solver training succeeded"));
            
            // 更新状态验证器
            if (StateValidator.IsValid())
            {
                StateValidator->MeshConformedStateUpdate();
                StateValidator->UpdateIdentityProgress();
            }
        }
        else
        {
            UE_LOG(LogMetaHumanIdentity, Error, TEXT("Solver training failed"));
        }
    });

    // 绑定进度回调
    SolverTask->OnProgressCallback().BindLambda([this](float Progress)
    {
        CurrentTrainingProgress = Progress;
    });

    SolverTask->StartAsync();
    bIsTraining = true;

    UE_LOG(LogMetaHumanIdentity, Log, TEXT("Solver training started"));
}

void AMetaHumanIdentityManager::CancelSolverTraining()
{
    if (SolverTask.IsValid() && bIsTraining)
    {
        SolverTask->Cancel();
        bIsTraining = false;
        CurrentTrainingProgress = 0.0f;

        UE_LOG(LogMetaHumanIdentity, Log, TEXT("Solver training cancelled"));
    }
}

bool AMetaHumanIdentityManager::IsIdentityValid() const
{
    if (!StateValidator.IsValid())
    {
        return false;
    }

    FText Tooltip = StateValidator->GetInvalidationStateToolTip();
    return Tooltip.IsEmpty();
}

float AMetaHumanIdentityManager::GetTrainingProgress() const
{
    return CurrentTrainingProgress;
}

FText AMetaHumanIdentityManager::GetStateTooltip() const
{
    if (StateValidator.IsValid())
    {
        return StateValidator->GetInvalidationStateToolTip();
    }

    return FText::GetEmpty();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `SkeletalMeshUtilitiesCommon` | 骨骼网格体工具函数 |
| `ControlRigDeveloper` | Control Rig 开发者工具，用于面部绑定 |
| `MetaHumanCaptureDataEditor` | 捕获数据编辑器 |
| `MetaHumanSDKEditor` | MetaHuman SDK 编辑器集成 |

## 维护状态

### 近期更新

```
- 9c62fae4c655 [MHA] Removing whitespace from the loctext #rb skip
- c202ed7d4678 [Backout] - CL46258616 [FYI] richard.graham - Backing out as does not work as required for BP scripting users. #rnx
- 5eabb033c502 [Metahuman BP API] - Allow BP scripting access to the MH Identity validation state so users can create batch scripts that can check for a valid (prepared for performance) identity.
```

### 维护评价

MetaHumanIdentity 模块是 MetaHuman Animator 的核心组件，创建于 2024 年 2 月，属于较新的模块。

**优点：**
- **架构清晰**：Identity → Part → Pose → PromotedFrame 的层次结构设计合理
- **功能完整**：覆盖了从数据输入到求解器训练的完整流程
- **异步支持**：预测求解器训练支持异步执行和取消
- **状态管理完善**：有专门的状态验证器追踪处理进度
- **蓝图友好**：大量 BlueprintCallable 函数，便于可视化脚本使用

**已知限制：**
- 最近一次 commit 回退了蓝图验证状态 API，说明部分功能仍在迭代中
- 依赖 MetaHuman Service 进行自动绑定，需要网络连接

**推荐使用**：这是 MetaHuman 工作流的核心模块，如果你在使用 MetaHuman 角色，这个模块是必需的。建议关注 Epic 的更新，因为该模块仍在活跃开发中。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanIdentity)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/metahuman-animator-in-unreal-engine/)（MetaHuman Animator 文档）