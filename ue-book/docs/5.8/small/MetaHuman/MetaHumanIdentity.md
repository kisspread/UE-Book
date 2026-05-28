# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画师 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（网格体、DNA 资产、配置文件、蓝图资产） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-04-01 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

> **注意**：本文档聚焦于 `MetaHumanIdentity` 模块，该插件包含 28 个模块、544 个源文件，属于超大型插件（xlarge）。

## 用途

MetaHuman Animator 是 Epic Games 提供的完整 MetaHuman 工具链，用于从真实人物的**面部捕获数据**（网格扫描或视频素材）生成带有完整绑定（Rig）的数字人面部骨骼网格体。

核心解决的问题：
- **从真实人脸数据生成可动画的数字人**：通过面部特征追踪 → 模板网格拟合 → 自动绑定服务的流水线，将捕获数据转化为可驱动的 SkeletalMesh
- **面部动画驱动**：生成的 Identity 资产可配合 MetaHuman Performance 资产，从视频素材生成面部动画序列
- **与 MetaHuman Creator 集成**：可创建完整的 MetaHuman 角色并通过 Quixel Bridge 下载

`MetaHumanIdentity` 模块是整个工具链的核心资产系统，定义了 Identity 资产的数据结构、面部拟合（Conforming）、自动绑定（Auto-Rigging）和预测求解器（Predictive Solver）训练等关键流程。

## 使用场景

- 你有一段人物面部视频素材（RGB + 深度）→ 使用 MetaHuman Identity 从素材创建数字人面部
- 你有一个 3D 面部扫描网格 → 使用 Identity 的 Face Fitting 功能将模板网格拟合到扫描数据
- 你需要为一个已有的面部网格生成 MetaHuman 兼容的绑定 → 使用 Auto-Rigging 服务
- 你需要为面部动画生成预测求解器 → 使用 Predictive Solver Training 流程
- 你需要批量处理多个 MetaHuman → 使用 MetaHumanBatchProcessor 模块

## 蓝图用法

### 核心节点

#### Identity 资产管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FindPartOfClass` | 按类查找 Identity 中的某个 Part（如 Face、Body） | `UMetaHumanIdentity` |
| `GetOrCreatePartOfClass` | 获取或创建指定类型的 Part | `UMetaHumanIdentity` |
| `CanAddPartOfClass` | 判断是否可以添加指定类型的 Part | `UMetaHumanIdentity` |
| `CanAddPoseOfClass` | 判断是否可以添加指定类型的 Pose | `UMetaHumanIdentity` |
| `HandleError` | 处理 Identity 流程中的错误（静态函数） | `UMetaHumanIdentity` |

#### 自动绑定（Auto-Rigging）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `LogInToAutoRigService` | 登录 MetaHuman 自动绑定服务 | `UMetaHumanIdentity` |
| `IsLoggedInToService` | 检查是否已登录（仅检查本地 session） | `UMetaHumanIdentity` |
| `IsAutoRiggingInProgress` | 是否正在执行自动绑定 | `UMetaHumanIdentity` |
| `CreateDNAForIdentity` | 为 Identity 创建 DNA（调用远程服务） | `UMetaHumanIdentity` |
| `DiagnosticsIndicatesProcessingIssue` | 诊断是否存在处理问题 | `UMetaHumanIdentity` |

#### 面部追踪流水线

| 节点 | 说明 | 所在类 |
|---|---|---|
| `StartFrameTrackingPipeline` | 启动帧追踪流水线（处理图像+深度数据） | `UMetaHumanIdentity` |
| `SetBlockingProcessing` | 设置是否阻塞式处理 | `UMetaHumanIdentity` |
| `IsFrameTrackingPipelineProcessing` | 是否正在处理帧追踪 | `UMetaHumanIdentity` |

#### DNA 导入导出

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ImportDNAFile` | 从 DNA 文件初始化 Identity（编辑器专用） | `UMetaHumanIdentity` |
| `ExportDNADataToFiles` | 导出 DNA 和眉毛数据到文件 | `UMetaHumanIdentity` |

#### 面部 Part 操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Conform` | 执行面部拟合（Solve 或 Copy 模式） | `UMetaHumanIdentityFace` |
| `IsConformalRigValid` | 检查拟合后的 Rig 是否有效 | `UMetaHumanIdentityFace` |
| `ExportTemplateMesh` | 导出模板网格体 | `UMetaHumanIdentityFace` |
| `FindPoseByType` | 按类型查找 Pose（Neutral/Teeth/Custom） | `UMetaHumanIdentityFace` |
| `AddPoseOfType` | 添加指定类型的 Pose | `UMetaHumanIdentityFace` |
| `RemovePose` | 移除 Pose | `UMetaHumanIdentityFace` |
| `GetPoses` | 获取所有 Pose 列表 | `UMetaHumanIdentityFace` |
| `HasDNABuffer` | 是否已有 DNA 数据 | `UMetaHumanIdentityFace` |
| `HasPredictiveSolvers` | 是否已有预测求解器 | `UMetaHumanIdentityFace` |
| `RunPredictiveSolverTraining` | 运行预测求解器训练 | `UMetaHumanIdentityFace` |

#### Pose 操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetCaptureData` | 设置 Pose 的捕获数据 | `UMetaHumanIdentityPose` |
| `GetCaptureData` | 获取 Pose 的捕获数据 | `UMetaHumanIdentityPose` |
| `IsCaptureDataValid` | 捕获数据是否有效 | `UMetaHumanIdentityPose` |
| `AddNewPromotedFrame` | 创建新的提升帧（Promoted Frame） | `UMetaHumanIdentityPose` |
| `RemovePromotedFrame` | 移除提升帧 | `UMetaHumanIdentityPose` |
| `LoadDefaultTracker` | 加载默认追踪器 | `UMetaHumanIdentityPose` |

#### Promoted Frame 操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FrameContoursContainActiveData` | 帧轮廓数据中是否有活跃曲线 | `UMetaHumanIdentityPromotedFrame` |
| `CanTrack` | 该帧是否满足追踪条件 | `UMetaHumanIdentityPromotedFrame` |
| `IsNavigationLocked` | 视口导航是否锁定 | `UMetaHumanIdentityPromotedFrame` |
| `SetNavigationLocked` | 设置视口导航锁定状态 | `UMetaHumanIdentityPromotedFrame` |
| `ToggleNavigationLocked` | 切换视口导航锁定 | `UMetaHumanIdentityPromotedFrame` |

#### 工具函数

| 节点 | 说明 | 所在类 |
|---|---|---|
| `InitializeContourDataForFootageFrame` | 为素材帧初始化轮廓数据 | `UPromotedFrameUtils` |
| `GetPromotedFrameAsPixelArrayFromDisk` | 从磁盘读取帧图像为像素数组 | `UPromotedFrameUtils` |
| `GetImagePathForFrame` | 获取指定帧的图像路径 | `UPromotedFrameUtils` |

#### 视口设置

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ToggleCurrentPoseVisibility` | 切换当前 Pose 在视口中的可见性 | `UMetaHumanIdentityViewportSettings` |
| `ToggleTemplateMeshVisibility` | 切换模板网格可见性 | `UMetaHumanIdentityViewportSettings` |
| `SetSelectedPromotedFrame` | 设置选中的提升帧 | `UMetaHumanIdentityViewportSettings` |
| `SetFrameTimeForPose` | 设置 Pose 的帧时间 | `UMetaHumanIdentityViewportSettings` |

### 使用示例（蓝图描述）

**创建并拟合一个 MetaHuman Identity：**

1. 创建 `UMetaHumanIdentity` 资产
2. 调用 `GetOrCreatePartOfClass(UMetaHumanIdentityFace::StaticClass())` 获取面部 Part
3. 获取 Neutral Pose：调用 `FindPoseByType(EIdentityPoseType::Neutral)`
4. 为 Neutral Pose 设置捕获数据：调用 `SetCaptureData(YourCaptureData)`
5. 添加提升帧：调用 `AddNewPromotedFrame(OutIndex)` 并配置追踪数据
6. 执行面部拟合：调用 `Conform(EConformType::Solve)`
7. 登录并提交自动绑定：`LogInToAutoRigService()` → `CreateDNAForIdentity(false)`
8. 监听完成委托：绑定 `OnAutoRigServiceFinishedDynamicDelegate`

**监听自动绑定完成事件：**

绑定 `UMetaHumanIdentity` 的 `OnAutoRigServiceFinishedDynamicDelegate`，参数 `bInSuccess` 为 `true` 表示成功。完成后可通过 `FindPartOfClass<UMetaHumanIdentityFace>()` 获取面部 Part 并访问 `RigComponent` 获取生成的骨骼网格体。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanIdentity.h"
#include "MetaHumanIdentityParts.h"
#include "MetaHumanIdentityPose.h"
#include "MetaHumanIdentityPromotedFrames.h"
#include "MetaHumanTemplateMeshComponent.h"
#include "MetaHumanPredictiveSolversTask.h"
```

### 基本用法

**创建并配置 MetaHuman Identity 资产**

```cpp
// 来源: Public/MetaHumanIdentity.h - UMetaHumanIdentity 类

// 创建 Identity 资产
UMetaHumanIdentity* Identity = NewObject<UMetaHumanIdentity>();

// 获取或创建面部 Part
UMetaHumanIdentityFace* Face = Identity->GetOrCreatePartOfClass(UMetaHumanIdentityFace::StaticClass());

// 查找 Neutral Pose
UMetaHumanIdentityPose* NeutralPose = Face->FindPoseByType(EIdentityPoseType::Neutral);

// 设置捕获数据
NeutralPose->SetCaptureData(MyCaptureData);

// 检查是否可以执行拟合
if (Face->CanConform())
{
    // 执行面部拟合（Solve 模式会运行完整的拟合算法）
    EIdentityErrorCode ErrorCode = Face->Conform(EConformType::Solve);
    
    // 处理错误
    UMetaHumanIdentity::HandleError(ErrorCode);
}
```

**面部拟合与自动绑定流程**

```cpp
// 来源: Public/MetaHumanIdentityParts.h - UMetaHumanIdentityFace 类

// 检查是否已登录自动绑定服务
if (!Identity->IsLoggedInToService())
{
    Identity->LogInToAutoRigService();
}

// 检查是否可以提交到自动绑定
if (Face->CanSubmitToAutorigging())
{
    // 创建 DNA（false = 显示 UI 提示，true = 仅日志）
    Identity->CreateDNAForIdentity(false);
}

// 监听完成
Identity->OnAutoRigServiceFinishedDelegate.AddLambda([](bool bSuccess)
{
    if (bSuccess)
    {
        UE_LOG(LogMetaHumanIdentity, Log, TEXT("Auto-rigging completed successfully"));
    }
});
```

**管理 DNA 数据**

```cpp
// 来源: Public/MetaHumanIdentityParts.h - UMetaHumanIdentityFace 的 DNA 管理接口

// 检查 DNA 数据
if (Face->HasDNABuffer())
{
    // 获取 DNA 缓冲区
    TArray<uint8> DNABuffer = Face->GetDNABuffer();
    
    // 获取 PCA Rig
    TArray<uint8> PCARig = Face->GetPCARig();
    
    // 获取眉毛数据
    TArray<uint8> BrowsBuffer = Face->GetBrowsBuffer();
}

// 导出 DNA 和眉毛数据到文件
FString DnaPath = TEXT("/Game/DNA/face.dna");
FString BrowsPath = TEXT("/Game/DNA/brows.json");
Face->ExportDNADataToFiles(DnaPath, BrowsPath);
```

### 进阶用法

**异步预测求解器训练**

```cpp
// 来源: Public/MetaHumanPredictiveSolversTask.h - FPredictiveSolversTask 类

// 配置训练参数
FPredictiveSolversTaskConfig Config;
Config.DNAReader = MyDNAReader;
Config.TemplateDescriptionJson = TemplateDescJson;
Config.ConfigurationJson = ConfigJson;
Config.bTrainPreviewSolvers = true;

// 运行异步训练
bool bScheduled = Face->RunAsyncPredictiveSolverTraining(
    // 进度回调
    FOnPredictiveSolversProgress::CreateLambda([](float Progress)
    {
        UE_LOG(LogMetaHumanIdentity, Log, TEXT("Training progress: %.1f%%"), Progress * 100.0f);
    }),
    // 完成回调
    FOnPredictiveSolversCompleted::CreateLambda([](const FPredictiveSolversResult& Result)
    {
        if (Result.bSuccess)
        {
            UE_LOG(LogMetaHumanIdentity, Log, TEXT("Predictive solver training completed"));
        }
    })
);

// 轮询进度
if (bScheduled)
{
    float CurrentProgress = 0.0f;
    if (Face->PollAsyncPredictiveSolverTrainingProgress(CurrentProgress))
    {
        // 训练仍在进行中
    }
}

// 取消训练
Face->CancelAsyncPredictiveSolverTraining();
```

**手动管理预测求解器任务**

```cpp
// 来源: Public/MetaHumanPredictiveSolversTask.h - FPredictiveSolversTaskManager

// 获取任务管理器单例
FPredictiveSolversTaskManager& TaskManager = FPredictiveSolversTaskManager::Get();

// 创建新任务
FPredictiveSolversTask* Task = TaskManager.New(Config);

// 同步执行
FPredictiveSolversResult SyncResult = Task->StartSync();

// 或异步执行
Task->StartAsync();
Task->OnCompletedCallback().BindLambda([](const FPredictiveSolversResult& Result)
{
    // 处理结果
});
Task->OnProgressCallback().BindLambda([](float Progress)
{
    // 报告进度
});

// 停止所有任务
TaskManager.StopAll();
```

**操作模板网格组件**

```cpp
// 来源: Public/MetaHumanTemplateMeshComponent.h - UMetaHumanTemplateMeshComponent

// 获取模板网格组件
UMetaHumanTemplateMeshComponent* TemplateMesh = Face->TemplateMeshComponent;

// 显示 Neutral Pose 的头部网格
TemplateMesh->ShowHeadMeshForPose(EIdentityPoseType::Neutral);

// 设置头部网格顶点（带坐标转换）
TArray<FVector3f> NewVertices;
TemplateMesh->SetPoseHeadMeshVertices(
    EIdentityPoseType::Neutral, 
    NewVertices, 
    ETemplateVertexConversion::RigToUE  // 从 Rig 空间转换到 UE 空间
);

// 获取眼睛网格顶点
TArray<FVector> LeftEyeVerts, RightEyeVerts;
FTransform MeshTransform = Face->TemplateMeshComponent->GetComponentTransform();
TemplateMesh->GetEyeMeshesVertices(
    MeshTransform, 
    ETemplateVertexConversion::RigToUE,
    LeftEyeVerts, 
    RightEyeVerts
);

// 切换眼睛和牙齿的可见性
TemplateMesh->SetEyeMeshesVisibility(true);
TemplateMesh->SetTeethMeshVisibility(true);
```

**Promoted Frame 与追踪数据管理**

```cpp
// 来源: Public/MetaHumanIdentityPromotedFrames.h / Public/MetaHumanIdentityPose.h

// 为 Neutral Pose 创建新的提升帧
int32 FrameIndex;
UMetaHumanIdentityPromotedFrame* Frame = NeutralPose->AddNewPromotedFrame(FrameIndex);

// 设置为正面视图
Frame->bIsFrontView = true;

// 设置帧名称
Frame->FrameName = FText::FromString(TEXT("Frontal"));

// 锁定视口导航
Frame->SetNavigationLocked(true);

// 检查是否可以追踪
if (Frame->CanTrack())
{
    // 检查是否有活跃的轮廓数据
    if (Frame->FrameContoursContainActiveData())
    {
        // 获取曲线数据控制器
        TSharedPtr<FMetaHumanCurveDataController> Controller = Frame->GetCurveDataController();
    }
}

// 对于素材帧（Footage Frame），设置帧号
UMetaHumanIdentityFootageFrame* FootageFrame = Cast<UMetaHumanIdentityFootageFrame>(Frame);
if (FootageFrame)
{
    FootageFrame->FrameNumber = 42;
}

// 对于相机帧（Camera Frame），获取相机信息
UMetaHumanIdentityCameraFrame* CameraFrame = Cast<UMetaHumanIdentityCameraFrame>(Frame);
if (CameraFrame)
{
    FMinimalViewInfo ViewInfo = CameraFrame->GetMinimalViewInfo();
    FTransform CameraTransform = CameraFrame->GetCameraTransform();
}
```

## Demo 示例

**完整的 MetaHuman Identity 创建与拟合流程**

```cpp
// MetaHumanIdentityExample.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MetaHumanIdentityExample.generated.h"

UCLASS()
class AMyMetaHumanExample : public AActor
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category = "MetaHuman")
    FString CaptureDataAssetPath;

    UPROPERTY(EditAnywhere, Category = "MetaHuman")
    FString OutputDNAPath;

    UFUNCTION(BlueprintCallable, CallInEditor, Category = "MetaHuman")
    void RunMetaHumanPipeline();

private:
    void OnAutoRigFinished(bool bSuccess);
};
```

```cpp
// MetaHumanIdentityExample.cpp
#include "MetaHumanIdentityExample.h"
#include "MetaHumanIdentity.h"
#include "MetaHumanIdentityParts.h"
#include "MetaHumanIdentityPose.h"
#include "MetaHumanIdentityPromotedFrames.h"
#include "MetaHumanTemplateMeshComponent.h"
#include "MetaHumanIdentityLog.h"
#include "CaptureData.h"

void AMyMetaHumanExample::RunMetaHumanPipeline()
{
    // 1. 创建 Identity 资产
    UMetaHumanIdentity* Identity = NewObject<UMetaHumanIdentity>();
    if (!Identity)
    {
        UE_LOG(LogMetaHumanIdentity, Error, TEXT("Failed to create MetaHuman Identity"));
        return;
    }

    // 2. 获取面部 Part
    UMetaHumanIdentityFace* Face = Identity->GetOrCreatePartOfClass(
        UMetaHumanIdentityFace::StaticClass());
    if (!Face)
    {
        UMetaHumanIdentity::HandleError(EIdentityErrorCode::Failed);
        return;
    }

    // 3. 配置 Neutral Pose 的捕获数据
    UMetaHumanIdentityPose* NeutralPose = Face->FindPoseByType(EIdentityPoseType::Neutral);
    if (!NeutralPose)
    {
        UE_LOG(LogMetaHumanIdentity, Error, TEXT("Neutral Pose not found"));
        return;
    }

    // 加载捕获数据资产
    UCaptureData* CaptureData = LoadObject<UCaptureData>(nullptr, *CaptureDataAssetPath);
    if (CaptureData)
    {
        NeutralPose->SetCaptureData(CaptureData);
        NeutralPose->LoadDefaultTracker();
    }

    // 4. 执行面部拟合
    if (Face->CanConform())
    {
        EIdentityErrorCode ErrorCode = Face->Conform(EConformType::Solve);
        if (!UMetaHumanIdentity::HandleError(ErrorCode))
        {
            return;
        }

        UE_LOG(LogMetaHumanIdentity, Log, TEXT("Face conformed successfully"));
    }

    // 5. 绑定自动绑定完成回调
    Identity->OnAutoRigServiceFinishedDelegate.BindUObject(
        this, &AMyMetaHumanExample::OnAutoRigFinished);

    // 6. 检查登录状态并提交自动绑定
    if (!Identity->IsLoggedInToService())
    {
        Identity->LogInToAutoRigService();
    }

    if (Face->CanSubmitToAutorigging() && !Identity->IsAutoRiggingInProgress())
    {
        Identity->CreateDNAForIdentity(false);
    }

    // 7. 配置诊断参数
    Face->bSkipDiagnostics = false;
    Face->MaximumScaleDifferenceFromAverage = 25.0f;
    Face->MinimumDepthMapFaceCoverage = 80.0f;
    Face->MinimumDepthMapFaceWidth = 120.0f;
}

void AMyMetaHumanExample::OnAutoRigFinished(bool bSuccess)
{
    if (bSuccess)
    {
        UE_LOG(LogMetaHumanIdentity, Log, TEXT("Auto-rigging completed! Exporting DNA..."));
    }
    else
    {
        UE_LOG(LogMetaHumanIdentity, Error, TEXT("Auto-rigging failed"));
    }
}
```

## 模块依赖

以 `MetaHumanIdentity` 模块为例，以下是其独特依赖（已在 Build.cs 中声明）：

| 模块 | 用途 |
|---|---|
| `SkeletalMeshUtilitiesCommon` | 骨骼网格体工具函数，用于 DNA → 骨骼网格体转换 |
| `ControlRigDeveloper` | Control Rig 开发者 API，用于面部 Rig 的创建和管理 |
| `MetaHumanCaptureDataEditor` | 捕获数据编辑器支持 |
| `MetaHumanSDKEditor` | MetaHuman SDK 编辑器集成 |

其他模块的典型依赖模式：
- `MetaHumanConfig` 依赖 `MetaHumanCoreTechLib`（MetaHuman 核心技术库）
- `MetaHumanIdentity` 依赖 `UnrealEd`（编辑器功能，如 DNA 导入/资产操作）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 身体追踪启用时禁用关卡序列导出 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 上的渲染伪影 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持为已有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题 |

### 维护评价

**活跃维护** ⭐⭐⭐⭐⭐

- **更新频率**：最近更新集中在 2026 年 5 月，更新非常密集（多天连续提交），说明正在积极开发中
- **更新内容**：包含功能增强（身体追踪集成、动画序列导出）和 Bug 修复（渲染伪影、缓存问题），属于实质性更新
- **模块规模**：28 个模块、544 个源文件，是 UE5 中最大型的官方插件之一
- **实验性状态**：已脱离实验阶段（IsBetaVersion=false, IsExperimentalVersion=false），属于正式发布的稳定插件
- **平台支持**：支持 Win64、Linux、Mac

**推荐使用**：作为 Epic Games 官方的 MetaHuman 工具链核心组件，该插件维护状态极佳，适合所有需要创建数字人类的项目。需要注意的是，完整的 Auto-Rigging 流程需要连接 MetaHuman 云服务。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/en-US/metahuman-animator-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest)