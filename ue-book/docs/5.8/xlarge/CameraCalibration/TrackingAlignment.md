# Camera Calibration

> Framework to support lens distortion and camera calibration in engine.

| 属性 | 值 |
|---|---|
| 中文名 | 摄像头标定框架 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（可能包含材质、资产等） |
| 模块 | `CameraCalibrationEditor` (Runtime), `TrackingAlignment` (Runtime), `TrackingAlignmentEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-04-29 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CameraCalibration) | |

## 用途
此插件是用于虚拟制片流程中摄像头标定和空间对齐的框架。其核心功能之一（`TrackingAlignment` 模块）是解决两套独立追踪系统（例如，动作捕捉系统与头戴显示器的 Inside-Out 追踪）之间的坐标系对齐问题。它通过采集两个空间中同一对象的变换样本，利用 OpenCV 的 “手眼标定”（Eye-To-Hand）算法，计算出一个变换关系，从而将追踪空间 B 的坐标系与追踪空间 A 对齐。这对于确保虚拟摄像机、跟踪物体在混合追踪环境下的空间一致性至关重要。

## 使用场景
- **虚拟制片**：当您的片场同时使用了光学动捕系统（追踪空间 A）和头戴式 VR 显示器（追踪空间 B）时，需要将两者追踪到的世界坐标系对齐，以便虚拟摄像机能够正确匹配演员的物理位置和方向。
- **混合现实**：将传统的光学追踪设备（如 OptiTrack）与新兴的 AR/MR 设备（如 HoloLens）结合使用，需要建立两者之间的空间映射关系。
- **自定义追踪解决方案**：任何需要整合两套独立追踪系统数据，并要求它们在同一坐标系下工作的场景。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetMinimumRequiredTrackerAligmentSampleCount` | 获取计算追踪空间对齐所需的最小样本数量。 | `UTrackingAlignmentFunctionLibrary` |
| `GetAlignedTrackerBOrigin` | 根据给定的校准配置文件，使用 OpenCV 计算并返回追踪空间 B 相对于追踪空间 A 的对齐后原点变换。 | `UTrackingAlignmentFunctionLibrary` |
| `FindAndUpdateOriginActor` | 根据追踪的 `SourceActor`，查找并更新其 `OriginActor` 为直接的父 Actor。 | `UTrackingAlignmentFunctionLibrary` |
| `CaptureSample` | 为配置的 `TrackerAActors` 和 `TrackerBActors` 捕获一个新样本。 | `UTrackingAlignmentCalibrationProfile` |
| `RemoveSample` | 移除指定索引处的样本。 | `UTrackingAlignmentCalibrationProfile` |
| `ClearSamples` | 清除所有已采集的样本。 | `UTrackingAlignmentCalibrationProfile` |

### 使用示例（蓝图描述）
1.  **创建校准配置文件**：在内容浏览器中创建一个 `UTrackingAlignmentCalibrationProfile` 资产。
2.  **配置追踪 Actor**：在配置文件的细节面板中，为 `TrackerAActors` 和 `TrackerBActors` 分别指定 `SourceActor`（被追踪的物体，如一个标记点）和 `OriginActor`（代表该追踪空间原点的物体）。
3.  **采集样本**：在游戏视图或编辑器中，通过蓝图调用配置文件的 `CaptureSample` 节点。在不同的位置和方向重复此操作多次（至少达到 `GetMinimumRequiredTrackerAligmentSampleCount` 返回的最小值）。
4.  **计算对齐变换**：调用 `GetAlignedTrackerBOrigin` 节点，传入步骤 1 创建的校准配置文件。该节点会返回一个 `FTransform`，代表追踪空间 B 的原点在追踪空间 A 中的位置和旋转。
5.  **应用对齐**：将返回的 `FTransform` 应用到需要将追踪空间 B 对象转换到追踪空间 A 的逻辑中，例如，将其作为虚拟摄像机或跟踪物体的根变换的一部分。

## C++ 用法

### 头文件引入
```cpp
#include "TrackingAlignmentBPLibrary.h"
#include "TrackingAlignmentCalibrationProfile.h"
```

### 基本用法
以下代码片段展示了在 C++ 中执行一次追踪对齐的基本流程（基于头文件推断的逻辑）：

```cpp
// 假设我们已经获得了一个指向校准配置文件的指针
UTrackingAlignmentCalibrationProfile* CalibrationProfile = ...;

// 1. 检查当前样本数是否足够
int32 MinSamples = UTrackingAlignmentFunctionLibrary::GetMinimumRequiredTrackerAligmentSampleCount();
if (CalibrationProfile->Samples.Num() >= MinSamples)
{
    // 2. 计算对齐变换
    FTransform AlignedTransform = UTrackingAlignmentFunctionLibrary::GetAlignedTrackerBOrigin(CalibrationProfile);
    
    // 3. 使用对齐后的变换
    // 例如，设置某个 Actor 的世界变换
    SomeTrackedActor->SetActorWorldTransform(AlignedTransform);
}
else
{
    UE_LOG(LogTemp, Warning, TEXT("需要更多样本以完成对齐，当前：%d，最少需要：%d"), 
           CalibrationProfile->Samples.Num(), MinSamples);
}
```

### 进阶用法
结合样本管理进行更精细的控制：

```cpp
// 动态管理校准配置文件
UTrackingAlignmentCalibrationProfile* Profile = NewObject<UTrackingAlignmentCalibrationProfile>();

// 配置追踪 Actor
FTrackingAlignmentActors& TrackerA = Profile->TrackerAActors;
TrackerA.SourceActor = OpticalMocapMarkerActor;
TrackerA.OriginActor = MocapOriginActor;

FTrackingAlignmentActors& TrackerB = Profile->TrackerBActors;
TrackerB.SourceActor = VRHeadsetTrackedActor;
TrackerB.OriginActor = VRTrackingOriginActor;

// 捕获样本
FTrackingAlignmentSample NewSample;
if (Profile->CaptureSample(NewSample))
{
    UE_LOG(LogTemp, Log, TEXT("成功捕获样本。"));
}

// 移除可能的异常样本（例如索引 2 的样本）
Profile->RemoveSample(2);

// 清除所有样本以重新开始
Profile->ClearSamples();
```

## Demo 示例
一个最小可编译的示例，演示如何创建并使用 `TrackingAlignmentCalibrationProfile`。

**MyAlignmentActor.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyAlignmentActor.generated.h"

class UTrackingAlignmentCalibrationProfile;
struct FTrackingAlignmentSample;

UCLASS()
class MYPROJECT_API AMyAlignmentActor : public AActor
{
    GENERATED_BODY()

public:
    AMyAlignmentActor();

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Alignment")
    UTrackingAlignmentCalibrationProfile* CalibrationProfile;

    UFUNCTION(BlueprintCallable, Category = "Alignment")
    void PerformCalibration();
};
```

**MyAlignmentActor.cpp**
```cpp
#include "MyAlignmentActor.h"
#include "TrackingAlignmentCalibrationProfile.h"
#include "TrackingAlignmentBPLibrary.h"

AMyAlignmentActor::AMyAlignmentActor()
{
    PrimaryActorTick.bCanEverTick = false;
    CalibrationProfile = CreateDefaultSubobject<UTrackingAlignmentCalibrationProfile>(TEXT("DefaultCalibrationProfile"));
}

void AMyAlignmentActor::PerformCalibration()
{
    if (!CalibrationProfile)
    {
        UE_LOG(LogTemp, Error, TEXT("校准配置文件为空！"));
        return;
    }

    // 确保 Actor 引用有效（此处需要在编辑器或蓝图中预先设置好 TrackerAActors 和 TrackerBActors）
    // 这里假设它们已经被设置

    // 模拟捕获几个样本
    for (int32 i = 0; i < 5; ++i)
    {
        FTrackingAlignmentSample Sample;
        if (CalibrationProfile->CaptureSample(Sample))
        {
            UE_LOG(LogTemp, Log, TEXT("捕获样本 %d: TransformA: %s, TransformB: %s"), 
                i, *Sample.TransformA.ToString(), *Sample.TransformB.ToString());
        }
    }

    // 计算对齐
    FTransform AlignedOrigin = UTrackingAlignmentFunctionLibrary::GetAlignedTrackerBOrigin(CalibrationProfile);
    UE_LOG(LogTemp, Log, TEXT("计算出的对齐变换 (TrackerB in TrackerA space): %s"), *AlignedOrigin.ToString());
}
```

## 模块依赖
| 模块 | 用途 |
|---|---|
| `OpenCV` | 用于执行核心的手眼标定（Eye-To-Hand）数学计算。 |

## 维护状态

### 近期更新
| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口相关代码重构，不影响核心标定逻辑。 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回退了一个变更。 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 与 `cfb610df` 相同的视口代码重构提交。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了严格浮点模式下双精度常量截断为浮点数的编译警告。 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the new ones. | 虚拟制片资产目录结构整理，将资产迁移到新分类。 |

### 维护评价
该插件（具体到 `TrackingAlignment` 模块）处于**活跃维护**状态。最近几次提交（2026年5月）主要是通用性代码重构、编译警告修复和资产管理优化，并非针对此模块的功能性更新。由于插件本身标记为实验性（`IsBetaVersion`），且创建于约3年前，建议在生产环境中谨慎使用，注意其 API 和行为可能在未来版本中发生变化。总体来说，其核心功能稳定，适合作为虚拟制片空间对齐的解决方案。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CameraCalibration)
- [官方文档]()（暂无）
- [测试用例]()（暂未发现相关测试文件）