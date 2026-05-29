# Camera Calibration

> Framework to support lens distortion and camera calibration in engine.

| 属性 | 值 |
|---|---|
| 中文名 | 相机校准工具箱 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `CameraCalibrationEditor` (Runtime), `TrackingAlignment` (Runtime), `TrackingAlignmentEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-04-29 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CameraCalibration) | |

## 用途

这个插件不仅仅是一个简单的畸变校准工具。它为 Unreal Engine 的虚拟制作管线提供了一套完整的**镜头数据采集、编辑、求解、验证和导出的系统**。

其核心是围绕 `ULensFile` 资产构建的。`ULensFile` 是一个数据容器，用于存储随镜头焦距 (Focus)、变焦 (Zoom) 和光圈 (Iris) 参数变化的镜头内参（焦距、图像中心）、畸变参数和节点偏移 (Nodal Offset)。

该插件旨在解决以下问题：
1.  **精确的实景合成 (Compositing)**：确保 CG 摄像机渲染的画面与实拍媒体素材在畸变、焦距和光学中心上完全对齐。
2.  **跟踪摄像机校准**：计算并补偿虚拟摄像机和物理摄像机之间的节点偏移，使得跟踪数据能够准确对应到 CG 世界的正确透视点。
3.  **数据驱动管线**：将校准得到的镜头数据从 `ULensFile` 资产中提取，并应用到 `CineCamera` 和 `LensComponent`，实现实时的镜头模拟。

## 使用场景

-   **虚拟制片**：在现场合成中，使用 `LensFile` 资产精确地扭曲 CG 渲染的视频流，使其与现场 LED 屏幕上播放的实拍素材完美匹配，消除“CG感”。
-   **跟踪镜头校准**：当使用 OptiTrack、Vicon 等光学跟踪系统驱动虚拟摄像机时，使用“节点偏移”(Nodal Offset)工具来精确计算并补偿摄像机旋转中心与物理摄像机旋转中心的偏差。
-   **构建镜头库**：为不同型号的电影镜头（如 Cooke、Panavision）创建 `LensFile` 资产库，存储其精确的畸变和呼吸效应数据，供后续项目直接使用。
-   **向其他软件导出数据**：将引擎内采集或编辑的镜头数据（焦距、畸变、节点偏移）导出为 JSON 文件，以便在 Nuke、Houdini 等后期软件中使用。

## 蓝图用法

本插件主要通过 `ULensFile` 资产及其数据评估接口暴露蓝图功能。以下是核心的蓝图可用函数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Calibrate` | 根据输入的 3D/2D 点对应关系，运行镜头畸变求解算法。 | `ULensDistortionSolverOpenCV` |
| `Evaluate` | 根据输入的 Focus 和 Zoom 值，评估 `LensFile` 中存储的焦距、图像中心、畸变和节点偏移数据。 | `ULensFile` |
| `SetLensInfo` | 设置 `LensFile` 的基本信息，如序列号、型号、畸变模型。 | `ULensFile` |
| `AddDistortionPoint` | 向 `LensFile` 添加一个新的畸变数据点（需要 Focus, Zoom, 畸变参数等）。 | `ULensFile` |
| `AddNodalOffsetPoint` | 向 `LensFile` 添加一个新的节点偏移数据点。 | `ULensFile` |

### 使用示例（蓝图描述）

1.  **评估镜头数据**：
    *   创建或获取一个 `ULensFile` 资产的引用。
    *   在蓝图图表中，从 `LensFile` 引用拖出，搜索并添加 `Evaluate` 节点。
    *   将当前镜头的 `Focus` 和 `Zoom` 值连接到 `Evaluate` 节点的对应输入引脚。
    *   执行后，节点的输出引脚将提供评估后的 `DistortionInfo`, `FocalLengthInfo`, `ImageCenterInfo` 和 `NodalOffset` 结构体。
    *   可以将这些数据直接输入到 `CineCamera` 或通过 `LensComponent` 应用到任何摄像机。

2.  **运行自动标定**：
    *   收集一组标定板图像（如棋盘格）中检测到的角点 2D 像素坐标，以及对应的世界空间 3D 坐标。
    *   创建 `FObjectPoints` 和 `FImagePoints` 结构体数组。
    *   创建 `ULensDistortionSolverOpenCV` 对象。
    *   调用 `Solve` 函数，传入点数据、图像尺寸、初始焦距猜测值等参数。
    *   获取 `FDistortionCalibrationResult`，其中包含计算出的最优焦距、畸变系数、重投影误差等。

## C++ 用法

插件的核心逻辑主要面向 C++ 和蓝图扩展。以下示例展示了如何在 C++ 中评估镜头数据。

### 头文件引入

```cpp
#include "LensFile.h"
#include "LensDistortionModelHandlerBase.h"
```

### 基本用法

评估 `ULensFile` 中存储的镜头数据。
(来源: `Private/AssetEditor/SLensEvaluation.h` 和 `Private/AssetEditor/SLensEvaluation.cpp` 的逻辑简化)

```cpp
// 假设已经获取到一个有效的 ULensFile* LensFile 对象
ULensFile* MyLensFile = GetMyLensFile(); // 你的获取逻辑

if (MyLensFile)
{
    // 设置评估所需的输入参数
    FLensFileEvaluationInputs EvalInputs;
    EvalInputs.Focus = 2.5f;   // 当前对焦距离 (米)
    EvalInputs.Zoom = 1.0f;    // 当前变焦值

    // 执行评估
    FLensFileEvaluationResult EvalResult = MyLensFile->Evaluate(EvalInputs);

    if (EvalResult.bIsDistortionEvaluated)
    {
        FDistortionInfo DistInfo = EvalResult.DistortionInfo;
        // 使用畸变参数...例如，应用到自定义的后处理材质中
        // PostProcessMaterial->SetScalarParameterValue(TEXT("K1"), DistInfo.Parameters[0]);
    }

    if (EvalResult.bIsFocalLengthEvaluated)
    {
        FFocalLengthInfo FocalInfo = EvalResult.FocalLengthInfo;
        // FocalInfo.FocalLength 包含了评估后的焦距 (FxFy, 单位像素)
    }

    if (EvalResult.bIsNodalOffsetEvaluated)
    {
        FNodalPointOffset NodalOffset = EvalResult.NodalOffset;
        // NodalOffset 包含了位置和旋转偏移，可以应用到摄像机组件上
        // CameraComponent->SetRelativeLocation(NodalOffset.Location);
        // CameraComponent->SetRelativeRotation(NodalOffset.Rotation);
    }
}
```

### 进阶用法

创建一个自定义的镜头畸变求解器。
(来源: `Private/Calibrators/CameraCalibrationSolver.h`)

```cpp
#include "CameraCalibrationSolver.h" // 包含求解器基类定义

// 继承自基类
UCLASS(Blueprintable)
class UMyCustomLensSolver : public ULensDistortionSolver
{
    GENERATED_BODY()

public:
    // 必须重写此函数
    virtual FDistortionCalibrationResult Solve_Implementation(
        const TArray<FObjectPoints>& ObjectPointArray,
        const TArray<FImagePoints>& ImagePointArray,
        const FIntPoint ImageSize,
        const FVector2D& FocalLength,
        const FVector2D& ImageCenter,
        const TArray<float>& DistortionParameters,
        const TArray<FTransform>& CameraPoses,
        const TArray<FTransform>& TargetPoses,
        TSubclassOf<ULensModel> LensModel,
        double PixelAspect,
        ECalibrationFlags SolverFlags) override;

    virtual FText GetDisplayName_Implementation() const override
    {
        return FText::FromString(TEXT("My Custom Solver"));
    }

    // 在你的实现中，可以调用基类提供的状态报告函数
    void MySolveLogic(...)
    {
        // 长时间运行的操作中，检查是否被取消
        if (!IsRunning())
        {
            return;
        }
        // 更新进度状态
        SetStatusText(FText::FromString(TEXT("正在优化畸变参数...")));
        // ... 执行你的求解逻辑 ...
    }
};
```

## Demo 示例

一个完整的最小示例：在编辑器工具中评估镜头数据并输出到日志。

### MyLensCalibrationTool.h

```cpp
// MyLensCalibrationTool.h
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "LensFile.h"
#include "MyLensCalibrationTool.generated.h"

UCLASS(Blueprintable)
class UMyLensCalibrationTool : public UObject
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Calibration")
    ULensFile* LensFileToEvaluate;

    UFUNCTION(BlueprintCallable, Category = "Calibration")
    void EvaluateAndLogLensData(float FocusDistance, float ZoomValue);
};
```

### MyLensCalibrationTool.cpp

```cpp
// MyLensCalibrationTool.cpp
#include "MyLensCalibrationTool.h"
#include "LensFile.h"

void UMyLensCalibrationTool::EvaluateAndLogLensData(float FocusDistance, float ZoomValue)
{
    if (!LensFileToEvaluate)
    {
        UE_LOG(LogTemp, Error, TEXT("No LensFile assigned!"));
        return;
    }

    FLensFileEvaluationInputs Inputs;
    Inputs.Focus = FocusDistance;
    Inputs.Zoom = ZoomValue;

    FLensFileEvaluationResult Result = LensFileToEvaluate->Evaluate(Inputs);

    UE_LOG(LogTemp, Log, TEXT("=== Lens File Evaluation (Focus: %.2f, Zoom: %.2f) ==="), FocusDistance, ZoomValue);

    if (Result.bIsDistortionEvaluated)
    {
        UE_LOG(LogTemp, Log, TEXT("Distortion Model: %s, Parameters: %s"),
            *Result.DistortionInfo.LensModel->GetName(),
            *Result.DistortionInfo.Parameters.ToString());
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Distortion data not evaluated for these inputs."));
    }

    if (Result.bIsFocalLengthEvaluated)
    {
        UE_LOG(LogTemp, Log, TEXT("Focal Length (FxFy in pixels): %s"),
            *Result.FocalLengthInfo.FocalLength.ToString());
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Focal length data not evaluated for these inputs."));
    }

    if (Result.bIsNodalOffsetEvaluated)
    {
        UE_LOG(LogTemp, Log, TEXT("Nodal Offset Location: %s, Rotation: %s"),
            *Result.NodalOffset.Location.ToString(),
            *Result.NodalOffset.Rotation.ToString());
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Nodal offset data not evaluated for these inputs."));
    }
}
```

## 模块依赖

本插件的模块依赖较多，主要集中在媒体播放和图像处理。如果你要开发基于此插件的扩展，需要注意以下关键依赖。

| 模块 | 用途 |
|---|---|
| `MediaUtils`, `MediaFrameworkUtilities` | 用于播放和处理来自媒体源（如Blackmagic DeckLink、AJA）的视频流。 |
| `OpenCV` | `CameraCalibrationEditor` 模块的核心依赖，用于棋盘格检测、Aruco标记检测和镜头畸变求解算法。 |
| `LensComponent` | 用于将评估后的镜头数据（畸变、焦距等）应用到摄像机组件上。 |
| `CalibrationPointComponent` | 提供用于标记3D校准点位置的组件，是进行手动或自动标定的基础。 |
| `CommonUI` | 编辑器工具界面（如Simulcam视口）的UI构建依赖。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口客户端，使其在关联/解除关联时收到通知，减少重复代码。 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回退了之前的一个改动。 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 与`cfb610df`相同的视口重构提交。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量截断为浮点数产生的警告。 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the new | 将多个虚拟制作资产移动到新的资产分类下。 |

### 维护评价

该插件处于**活跃维护但实验性**状态。
-   **创建时间**：创建于2021年，已有5年历史，属于虚拟制作功能集的成熟部分。
-   **更新频率**：近期（2026年5月）仍有针对视口、浮点精度和资产分类的更新，说明 Epic 仍在投入资源进行维护和优化。
-   **实验性标记**：`.uplugin` 文件中 `IsBetaVersion=true`，这意味着其 API 和功能在未来版本中可能发生变更，不推荐在最求稳定性的生产环境中无条件依赖其内部实现。
-   **推荐**：**推荐使用**。这是 Unreal Engine 官方提供的、功能完备的相机校准解决方案，尤其适合影视级虚拟制片项目。但请注意其“实验性”状态，关注版本更新日志。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CameraCalibration)
-   官方文档（.uplugin中未提供）
-   测试用例（位于引擎测试目录，非插件目录内）