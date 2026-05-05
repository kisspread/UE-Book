# MetaHuman Animator Calibration Processing

> The official MetaHuman Calibration Processing Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（内容资产） |
| 模块 | `MetaHumanCalibrationCore` (Runtime), `MetaHumanCalibrationGenerator` (Runtime), `MetaHumanCalibrationLib` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-04-01 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanCalibrationProcessing) | |

## 用途

本插件是 MetaHuman Animator 工作流的核心组成部分，专门用于处理从多相机视频中提取高质量标定数据。它解决的核心问题是：如何从多个不同视角的相机拍摄的棋盘格图案或特征点中，精确计算出每个相机的内参（焦距、畸变等）和外参（位置、旋转），并实现稳健的跨相机特征匹配。这些精确的标定数据是后续进行高质量面部动作捕捉和动画重建的基础，确保不同视角的视频能够准确对齐和融合。

## 使用场景

- 你正在使用 MetaHuman Animator 从多相机（如立体相机对或相机阵列）拍摄的视频创建面部动画 → 需要此插件来处理相机标定和特征匹配。
- 你需要为自定义的多相机面部捕捉系统生成精确的相机参数，以便在 Unreal Engine 中进行准确的 3D 重建。
- 你在开发涉及计算机视觉和相机标定的工具链，需要集成到 Unreal Engine 中。

## 蓝图用法

本插件主要提供 C++ 库和底层算法接口，其核心类（如 `FMetaHumanStereoCalibrator` 和 `FMetaHumanRobustFeatureMatcher`）未暴露 `BlueprintCallable` 函数。因此，**不支持直接在蓝图中使用**。其功能通常通过 C++ 代码或由其他上层插件（如 MetaHuman Animator 主插件）调用。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanStereoCalibrator.h"
#include "MetaHumanRobustFeatureMatcher.h"
```

### 基本用法 - 相机标定 (`FMetaHumanStereoCalibrator`)

以下代码展示了使用 `FMetaHumanStereoCalibrator` 进行多相机标定的基本流程。

```cpp
// 来源：基于 MetaHumanStereoCalibrator.h 头文件推断的典型用法
#include "MetaHumanStereoCalibrator.h"

void PerformStereoCalibration()
{
    using namespace UE::Wrappers;

    // 1. 创建标定器实例
    FMetaHumanStereoCalibrator Calibrator;

    // 2. 初始化，指定棋盘格参数（内角点数，方格尺寸厘米）
    const uint32 PatternWidth = 9;
    const uint32 PatternHeight = 6;
    const float SquareSize = 2.5f; // 2.5cm
    if (!Calibrator.Init(PatternWidth, PatternHeight, SquareSize))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to initialize stereo calibrator."));
        return;
    }

    // 3. 添加相机视图
    const FString CameraNameLeft = TEXT("LeftCamera");
    const FString CameraNameRight = TEXT("RightCamera");
    const uint32 ImageWidth = 1920;
    const uint32 ImageHeight = 1080;
    Calibrator.AddCamera(CameraNameLeft, ImageWidth, ImageHeight);
    Calibrator.AddCamera(CameraNameRight, ImageWidth, ImageHeight);

    // 4. 检测棋盘格角点（假设已加载图像数据到 InImageLeft 和 InImageRight）
    TArray<FVector2D> CornerPointsLeft, CornerPointsRight;
    double SharpnessLeft, SharpnessRight;
    const unsigned char* InImageLeft = /* ... */;
    const unsigned char* InImageRight = /* ... */;
    bool bDetectedLeft = Calibrator.DetectPattern(CameraNameLeft, InImageLeft, CornerPointsLeft, SharpnessLeft);
    bool bDetectedRight = Calibrator.DetectPattern(CameraNameRight, InImageRight, CornerPointsRight, SharpnessRight);

    if (bDetectedLeft && bDetectedRight)
    {
        // 5. 收集多帧数据（此处仅示意一帧）
        TArray<TMap<FString, TArray<FVector2D>>> PointsPerCameraPerFrame;
        TMap<FString, TArray<FVector2D>> FrameData;
        FrameData.Add(CameraNameLeft, CornerPointsLeft);
        FrameData.Add(CameraNameRight, CornerPointsRight);
        PointsPerCameraPerFrame.Add(FrameData);

        // 6. 执行标定
        TArray<FCameraCalibration> OutCalibrations;
        double OutMSE;
        if (Calibrator.Calibrate(PointsPerCameraPerFrame, OutCalibrations, OutMSE))
        {
            UE_LOG(LogTemp, Log, TEXT("Calibration successful. MSE: %f"), OutMSE);

            // 7. 导出结果到 JSON 文件
            FString ExportPath = FPaths::ProjectSavedDir() / TEXT("Calibration.json");
            Calibrator.ExportCalibrations(OutCalibrations, ExportPath);
        }
    }
}
```

### 进阶用法 - 稳健特征匹配 (`FMetaHumanRobustFeatureMatcher`)

以下代码展示了如何使用 `FMetaHumanRobustFeatureMatcher` 在已标定的相机之间进行特征匹配和三角测量。

```cpp
// 来源：基于 MetaHumanRobustFeatureMatcher.h 头文件推断的典型用法
#include "MetaHumanRobustFeatureMatcher.h"
#include "CameraCalibration.h" // 假设 FCameraCalibration 定义在此

void PerformRobustFeatureMatching(const TArray<FCameraCalibration>& InCalibrations)
{
    using namespace UE::Wrappers;

    // 1. 创建特征匹配器实例
    FMetaHumanRobustFeatureMatcher Matcher;

    // 2. 初始化，传入相机标定数据
    const double ReprojectionThreshold = 5.0; // 像素
    const double RatioThreshold = 0.75;
    if (!Matcher.Init(InCalibrations, ReprojectionThreshold, RatioThreshold))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to initialize robust feature matcher."));
        return;
    }

    // 3. 添加相机信息（与标定时一致）
    Matcher.AddCamera(TEXT("LeftCamera"), 1920, 1080);
    Matcher.AddCamera(TEXT("RightCamera"), 1920, 1080);

    // 4. 检测特征（假设已加载一帧的图像数据）
    const int64 FrameIndex = 0;
    const unsigned char* ImageLeft = /* ... */;
    const unsigned char* ImageRight = /* ... */;
    TArray<const unsigned char*> Images = {ImageLeft, ImageRight};
    if (Matcher.DetectFeatures(FrameIndex, Images))
    {
        // 5. 获取匹配结果
        TArray<FVector2D> Points3D;
        TArray<TArray<FVector2D>> CameraPoints; // 每个相机的2D点
        TArray<TArray<FVector2D>> ReprojectedPoints;
        if (Matcher.GetFeatures(FrameIndex, Points3D, CameraPoints, ReprojectedPoints))
        {
            UE_LOG(LogTemp, Log, TEXT("Found %d 3D points from stereo matching."), Points3D.Num());
            // 此处可以使用 Points3D 进行后续的3D重建或动画驱动
        }
    }
}
```

## Demo 示例

一个完整的、可编译的最小示例，展示如何组合使用两个核心类。

```cpp
// MetaHumanCalibrationDemo.h
#pragma once

#include "CoreMinimal.h"

class FMetaHumanCalibrationDemo
{
public:
    static void RunDemo();
};
```

```cpp
// MetaHumanCalibrationDemo.cpp
#include "MetaHumanCalibrationDemo.h"
#include "MetaHumanStereoCalibrator.h"
#include "MetaHumanRobustFeatureMatcher.h"
#include "CameraCalibration.h"

void FMetaHumanCalibrationDemo::RunDemo()
{
    using namespace UE::Wrappers;

    // --- 第一阶段：相机标定 ---
    FMetaHumanStereoCalibrator Calibrator;
    if (!Calibrator.Init(9, 6, 2.5f))
    {
        return;
    }

    const FString Cam1 = TEXT("Cam1");
    const FString Cam2 = TEXT("Cam2");
    Calibrator.AddCamera(Cam1, 1920, 1080);
    Calibrator.AddCamera(Cam2, 1920, 1080);

    // 模拟检测到角点（实际应从图像处理获得）
    TArray<FVector2D> Points1, Points2;
    double Sharpness1, Sharpness2;
    // ... 填充 Points1, Points2 ...

    TArray<TMap<FString, TArray<FVector2D>>> AllFrameData;
    TMap<FString, TArray<FVector2D>> Frame1;
    Frame1.Add(Cam1, Points1);
    Frame1.Add(Cam2, Points2);
    AllFrameData.Add(Frame1);

    TArray<FCameraCalibration> Calibrations;
    double MSE;
    if (Calibrator.Calibrate(AllFrameData, Calibrations, MSE))
    {
        // 标定成功，导出结果
        Calibrator.ExportCalibrations(Calibrations, TEXT("D:/Calib.json"));

        // --- 第二阶段：特征匹配 ---
        FMetaHumanRobustFeatureMatcher Matcher;
        if (Matcher.Init(Calibrations))
        {
            Matcher.AddCamera(Cam1, 1920, 1080);
            Matcher.AddCamera(Cam2, 1920, 1080);

            // 模拟图像数据
            const unsigned char* Img1 = /* ... */;
            const unsigned char* Img2 = /* ... */;
            TArray<const unsigned char*> Images = {Img1, Img2};

            if (Matcher.DetectFeatures(0, Images))
            {
                TArray<FVector2D> Points3D;
                TArray<TArray<FVector2D>> CamPoints, Reprojected;
                if (Matcher.GetFeatures(0, Points3D, CamPoints, Reprojected))
                {
                    // 成功获得3D点，可用于动画驱动
                }
            }
        }
    }
}
```

## 模块依赖

本插件（MetaHumanCalibrationLib 模块）的依赖关系如下：

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 提供编辑器功能支持（尽管是 Runtime 模块，可能用于编辑器内工具或资产处理） |

**注意**：其他两个模块（`MetaHumanCalibrationCore` 和 `MetaHumanCalibrationGenerator`）的依赖未在提供信息中列出。通常，此类底层视觉处理库可能依赖 OpenCV 或其他计算机视觉库，但具体需查看其 Build.cs 文件。

## 维护状态

### 近期更新

```
- 2025-04-15 123a52cc7ddd [UEMHC] fix build health issue #1044612 #rb trivial
- 2025-04-10 f0b69dbb0bff [UEMHC] update titan and TS models to v7.20.1 #rb jarl.ostensen, jovan.mijatov
- 2025-04-08 9952a3061a13 Added missing files from last cl.
```

### 维护评价

- **创建时间**：2025年4月，非常新的插件。
- **最近更新**：最近一次更新在2025年4月15日，主要是构建健康修复和模型更新，表明处于**活跃维护**状态。
- **维护状态**：**活跃维护**。作为 MetaHuman 工具链的核心新组件，预计会持续更新以支持新功能和修复问题。
- **已知问题/限制**：作为新插件，可能存在与特定硬件配置或边缘情况相关的未发现问题。其功能高度依赖于输入图像的质量和棋盘格图案的清晰度。
- **推荐使用**：**强烈推荐**。如果你正在使用或计划使用 MetaHuman Animator 进行多相机面部捕捉，此插件是必需的基础设施。它提供了经过验证的、集成的标定和特征匹配算法。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanCalibrationProcessing)
- [官方文档]() (暂无)
- [测试用例]() (暂未发现)