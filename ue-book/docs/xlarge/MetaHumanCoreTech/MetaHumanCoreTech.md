# MetaHuman Core Tech

> The core technology behind the MetaHuman Creator and MetaHuman Animator plugins.

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、数据资产） |
| 模块 | `MetaHumanCaptureData` (Runtime), `MetaHumanCoreTech` (Runtime), `MetaHumanCoreTechLib` (Runtime), `MetaHumanImageViewer` (Runtime), `MetaHumanPipelineCore` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-01-20 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanCoreTechLib) | |

## 用途

MetaHumanCoreTech 是 MetaHuman 生态系统的底层技术库，为 MetaHuman Creator 和 MetaHuman Animator 插件提供核心算法和数据结构支持。它并非一个面向最终用户的独立工具，而是作为其他 MetaHuman 插件的基础组件。

该插件主要解决以下问题：
1.  **面部动画数据处理**：定义了用于存储面部、牙齿、眼睛网格顶点数据的结构体 (`FMetaHumanMeshData`)，以及包含动画数据、质量等级和音频处理模式的帧动画数据 (`FFrameAnimationData`)。
2.  **实时动画平滑与校准**：提供了实时动画平滑算法 (`FMetaHumanRealtimeSmoothing`)，支持滚动平均和 1€ 滤波器两种方法，用于减少实时面部捕捉数据的抖动。同时包含实时校准功能 (`FMetaHumanRealtimeCalibration`)。
3.  **追踪与置信度管理**：定义了用于存储面部追踪轮廓数据 (`FFrameTrackingContourData`) 和追踪置信度 (`FFrameTrackingConfidenceData`) 的结构体，以及光流追踪配置 (`FTrackerOpticalFlowConfiguration`)。
4.  **GUI 控制转换**：提供了将 GUI 控制参数转换为原始控制参数的工具函数 (`GuiToRawControlsUtils`)。
5.  **头部变换转换**：提供了在独立头部骨骼网格和完整 MetaHuman 角色头部骨骼之间转换变换的工具类 (`FMetaHumanHeadTransform`)。
6.  **音频驱动动画情绪**：定义了音频驱动动画的情绪枚举 (`EAudioDrivenAnimationMood`)，并提供了编辑器内的选择控件。
7.  **通用数据工具**：提供了获取 DNA 文件路径、设置后处理动画蓝图、获取默认控制绑定等通用工具函数 (`FMetaHumanCommonDataUtils`)。
8.  **图像处理工具**：提供了将点或线绘制到图像缓冲区的工具函数 (`epic::core::BurnPointsIntoImage`, `BurnLineIntoImage`)。

## 使用场景

-   你正在开发或扩展 **MetaHuman Creator** 或 **MetaHuman Animator** 插件，需要调用底层的面部动画处理、平滑和校准算法。
-   你需要处理来自面部捕捉设备的实时数据流，并希望应用平滑滤波以获得更稳定的动画输出。
-   你需要管理面部追踪轮廓的置信度数据，用于后续的动画质量评估或修复。
-   你需要将用户界面（GUI）上的控制滑块值映射到驱动 MetaHuman 面部的原始控制参数。
-   你需要在独立的头部模型和完整的 MetaHuman 角色之间正确地转换头部变换，以保持姿势一致。
-   你正在实现音频驱动的面部动画，并需要选择或处理不同的情绪状态。

## 蓝图用法

该插件主要提供底层 C++ 类和结构体，直接暴露给蓝图的节点相对有限，主要集中在数据定义和配置上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `EAudioDrivenAnimationMood` (枚举) | 定义了音频驱动动画的情绪类型，如中性、快乐、悲伤等，可在蓝图中用于选择或设置情绪。 | `EAudioDrivenAnimationMood` |
| `UMetaHumanRealtimeSmoothingParams` (数据资产) | 一个数据资产类，用于配置实时平滑的参数（如平滑方法、滚动平均帧数、1€滤波器参数）。可在蓝图中创建和编辑实例。 | `UMetaHumanRealtimeSmoothingParams` |
| `FFrameAnimationData` (结构体) | 包含单帧动画数据的结构体，包含姿态、动画数据映射、网格数据等。可在蓝图中读取或传递。 | `FFrameAnimationData` |

### 使用示例（蓝图描述）

1.  **配置实时平滑参数**：
    *   在内容浏览器中右键，选择 `Miscellaneous` -> `Data Asset`。
    *   在类选择器中搜索并选择 `MetaHuman Realtime Smoothing`。
    *   为创建的数据资产命名（例如 `DA_MySmoothingParams`）。
    *   打开该资产，在 `Smoothing` 分类下，可以添加或修改各个面部属性（如 `EyeBlinkLeft`）的平滑参数，选择 `RollingAverage` 或 `OneEuro` 方法并调整相应数值。
    *   在动画蓝图或处理逻辑中，获取该数据资产的引用，并将其传递给 `FMetaHumanRealtimeSmoothing` 的构造函数或相关处理函数。

2.  **使用情绪枚举**：
    *   在蓝图中，可以创建一个 `EAudioDrivenAnimationMood` 类型的变量。
    *   通过枚举选择节点（如 `Switch on EAudioDrivenAnimationMood`）或直接设置变量值（如 `EAudioDrivenAnimationMood::Happiness`）来控制音频驱动动画的情绪状态。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanCoreTech.h" // 主模块头文件
// 或根据需要引入具体头文件
#include "MetaHumanRealtimeSmoothing.h"
#include "MetaHumanHeadTransform.h"
#include "FrameAnimationData.h"
```

### 基本用法

**1. 使用实时平滑器处理动画帧数据**
```cpp
// 来源: MetaHumanRealtimeSmoothing.h
#include "MetaHumanRealtimeSmoothing.h"

// 假设已有平滑参数
TMap<FName, FMetaHumanRealtimeSmoothingParam> SmoothingParams = FMetaHumanRealtimeSmoothing::GetDefaultSmoothingParams();

// 创建平滑器实例
FMetaHumanRealtimeSmoothing Smoother(SmoothingParams);

// 在动画更新循环中处理每一帧
TArray<FName> PropertyNames = { TEXT("EyeBlinkLeft"), TEXT("JawOpen") };
TArray<float> CurrentFrameData = { 0.0f, 0.5f }; // 当前帧的原始数据
double DeltaTime = 0.016f; // 帧间隔时间

// ProcessFrame 会就地修改 CurrentFrameData
bool bSuccess = Smoother.ProcessFrame(PropertyNames, CurrentFrameData, DeltaTime);
// CurrentFrameData 现在包含平滑后的值
```

**2. 转换头部变换**
```cpp
// 来源: MetaHumanHeadTransform.h
#include "MetaHumanHeadTransform.h"

// 假设有一个应用到独立头部网格的变换
FTransform MeshTransform(FRotator(0, 45, 0), FVector(10, 0, 0), FVector::OneVector);

// 将其转换为适用于完整 MetaHuman 角色头部骨骼的变换
FTransform BoneTransform = FMetaHumanHeadTransform::MeshToBone(MeshTransform);

// 反向转换
FTransform BackToMesh = FMetaHumanHeadTransform::BoneToMesh(BoneTransform);
```

### 进阶用法

**结合平滑与头部变换处理实时捕捉数据**
```cpp
#include "MetaHumanRealtimeSmoothing.h"
#include "MetaHumanHeadTransform.h"
#include "FrameAnimationData.h"

class FMyMetaHumanProcessor
{
public:
    FMyMetaHumanProcessor()
        : Smoother(FMetaHumanRealtimeSmoothing::GetDefaultSmoothingParams())
    {
    }

    void ProcessCaptureData(const FFrameAnimationData& InRawData, float InDeltaTime)
    {
        // 1. 提取需要平滑的属性名和值
        TArray<FName> PropertyNames;
        TArray<float> PropertyValues;
        for (const auto& Pair : InRawData.AnimationData)
        {
            PropertyNames.Add(FName(*Pair.Key));
            PropertyValues.Add(Pair.Value);
        }

        // 2. 应用实时平滑
        Smoother.ProcessFrame(PropertyNames, PropertyValues, InDeltaTime);

        // 3. 将平滑后的数据写回（示例）
        FFrameAnimationData SmoothedData = InRawData;
        for (int32 i = 0; i < PropertyNames.Num(); ++i)
        {
            SmoothedData.AnimationData[PropertyNames[i].ToString()] = PropertyValues[i];
        }

        // 4. 处理头部姿态（假设 Pose 是头部变换）
        FTransform SmoothedHeadPose = SmoothedData.Pose;
        // 如果需要将此变换应用到完整角色的头部骨骼，可能需要转换
        // FTransform FinalBonePose = FMetaHumanHeadTransform::MeshToBone(SmoothedHeadPose);
        // ... 将 FinalBonePose 应用到角色
    }

private:
    FMetaHumanRealtimeSmoothing Smoother;
};
```

## Demo 示例

一个最小化的示例，展示如何初始化并使用实时平滑器。

**MyMetaHumanProcessor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "MetaHumanRealtimeSmoothing.h"

class FMyMetaHumanProcessor
{
public:
    FMyMetaHumanProcessor();
    void UpdateAnimation(float DeltaTime);

private:
    FMetaHumanRealtimeSmoothing Smoother;
    TArray<FName> TrackedProperties;
    TArray<float> CurrentValues;
};
```

**MyMetaHumanProcessor.cpp**
```cpp
#include "MyMetaHumanProcessor.h"

FMyMetaHumanProcessor::FMyMetaHumanProcessor()
    : Smoother(FMetaHumanRealtimeSmoothing::GetDefaultSmoothingParams())
{
    // 初始化要追踪的属性
    TrackedProperties = { TEXT("EyeBlinkLeft"), TEXT("EyeBlinkRight"), TEXT("JawOpen") };
    CurrentValues.SetNumZeroed(TrackedProperties.Num());
}

void FMyMetaHumanProcessor::UpdateAnimation(float DeltaTime)
{
    // 模拟从捕捉设备获取新的原始数据
    // 在实际应用中，这些值来自面部捕捉系统
    CurrentValues[0] = FMath::RandRange(0.0f, 1.0f); // EyeBlinkLeft
    CurrentValues[1] = FMath::RandRange(0.0f, 1.0f); // EyeBlinkRight
    CurrentValues[2] = FMath::RandRange(0.0f, 0.8f); // JawOpen

    // 应用平滑
    Smoother.ProcessFrame(TrackedProperties, CurrentValues, DeltaTime);

    // 平滑后的值存储在 CurrentValues 中，可用于驱动动画
    // UE_LOG(LogTemp, Log, TEXT("Smoothed EyeBlinkLeft: %f"), CurrentValues[0]);
}
```

## 模块依赖

该插件的模块依赖如下（已省略 Core, CoreUObject, Engine 等常见依赖）：

| 模块 | 用途 |
|---|---|
| `MetaHumanImageViewer` | 提供图像查看功能，被 `MetaHumanCaptureData` 模块依赖。 |
| `DirectoryWatcher` | 监视文件系统目录变化，被 `MetaHumanCaptureData` 模块依赖。 |
| `UnrealEd` | 编辑器功能，被 `MetaHumanCoreTechLib` 和 `MetaHumanPipelineCore` 模块依赖。 |
| `OnlineSubsystem` | 在线子系统功能，被 `MetaHumanCoreTechLib` 模块依赖。 |
| `OpenCVHelper` | OpenCV 辅助功能，被 `MetaHumanPipelineCore` 模块依赖。 |
| `OpenCV` | 计算机视觉库，被 `MetaHumanPipelineCore` 模块依赖。 |

## 维护状态

### 近期更新

```
- fb15849136ed 2025-01-20 Audio solver mood refactoring
- 71c0fdfd700c 2025-01-20 [Backout] - CL46056783 [FYI] jon.cook #rnx Original CL Desc ----------------------------------------------------------------- Audio solver mood refactoring #rb jack.taylor
- 5d5578dda2a9 2025-01-20 Audio solver mood refactoring #rb jack.taylor
```

### 维护评价

-   **创建时间**：2025年1月20日，非常新的插件。
-   **最近更新**：最近的提交（2025-01-20）集中在“音频求解器情绪重构”上，表明插件正在积极开发和完善其核心功能（音频驱动动画）。
-   **活跃状态**：**活跃维护中**。作为 MetaHuman 技术栈的核心组件，预计会随着 MetaHuman Creator 和 Animator 的更新而持续维护。
-   **已知限制**：该插件默认未启用 (`EnabledByDefault: false`)，表明它主要作为其他 MetaHuman 插件的内部依赖，不建议直接在最终用户项目中单独启用。
-   **推荐使用**：**仅推荐给 MetaHuman 插件开发者**。如果你正在开发依赖 MetaHuman 核心技术的自定义工具或插件，可以依赖此库。对于普通用户，应通过 MetaHuman Creator 或 Animator 插件间接使用其功能。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanCoreTechLib)
-   [官方文档]() (暂无)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanCoreTechLib/Tests) (如果存在)