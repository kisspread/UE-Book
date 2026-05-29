# Camera Calibration

> Framework to support lens distortion and camera calibration in engine.

| 属性 | 值 |
|---|---|
| 中文名 | 摄像机校准 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质资产、蓝图资产） |
| 模块 | `CameraCalibrationEditor` (Runtime), `TrackingAlignment` (Runtime), `TrackingAlignmentEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-04-29 |
| 年龄标签 | 👴 老古董（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CameraCalibration) | |

## 用途

Camera Calibration 是虚幻引擎为**虚拟制片 (Virtual Production)** 领域提供的一套核心框架，旨在解决**真实摄像机与虚拟摄像机参数匹配**的问题。其主要功能是支持**镜头畸变 (Lens Distortion)** 的模拟与消除，以及**摄像机内参（如焦距、像主点）和外参（位置、旋转）** 的精确校准。在 LED 虚拟制片（如 nDisplay）或绿幕合成流程中，精确的镜头校准是实现虚实画面无缝融合、避免画面边缘失真和运动视差错误的关键。

## 使用场景

- **LED 虚拟制片**：在 LED 墙前拍摄时，需要将真实摄像机的镜头参数（如畸变）与虚拟场景中的摄像机同步，确保演员移动时，背景的透视和畸变与真实镜头完全一致。
- **后期视觉特效合成**：在绿幕拍摄中，通过校准获取真实摄像机的精确镜头数据，以便在后期将 CG 元素完美地合成到实拍素材中，避免边缘失真或透视错误。
- **虚拟摄像机预演**：在前期预演阶段，使用校准过的镜头数据来驱动虚拟摄像机，获得更真实的镜头感。

## 蓝图用法

此插件提供了校准工作流所需的核心对象和函数，蓝图主要用作工作流编排和数据配置。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Lens File` | 创建一个新的镜头文件（Lens File）资产，用于存储特定镜头的校准数据。 | `ULensCalibrationSubsystem` |
| `Add Distortion Model` | 向镜头文件中添加一个畸变模型（如 Brown-Conrady）。 | `ULensFile` |
| `Set Distortion State` | 根据当前焦距等参数，在运行时从镜头文件中查询并应用正确的畸变状态到摄像机上。 | `ULensComponent` |

### 使用示例（蓝图描述）

1.  **数据准备**：通过编辑器工具或蓝图，创建一个 `Lens File` 资产，并为其添加一个畸变模型（例如 `ULensDistortionModelHandlerBase` 的子类）。
2.  **组件附加**：在你的虚拟摄像机 Actor 上添加 `ULensComponent` 组件。
3.  **数据绑定**：将 `ULensComponent` 的 `Lens File` 属性指向你创建的镜头文件资产。
4.  **运行时应用**：在游戏开始或需要时，调用 `Lens Component` 的 `Evaluate Distortion` 函数，它将根据当前摄像机的参数自动计算并应用镜头畸变后处理效果。

## C++ 用法

该插件的核心是数据管理与查询，C++ 用法主要围绕操作 `ULensFile` 对象和使用 `ULensComponent`。

### 头文件引入

```cpp
#include "LensFile.h"
#include "LensComponent.h"
#include "LensDistortionModelHandlerBase.h"
```

### 基本用法

通过 `ULensCalibrationSubsystem` 创建和管理镜头文件数据。
（来源：`LensFile.h`, `LensComponent.h`）

```cpp
// 获取校准子系统
ULensCalibrationSubsystem* CalibSubsystem = GEngine->GetEngineSubsystem<ULensCalibrationSubsystem>();

// 创建一个新的镜头文件资产
ULensFile* NewLensFile = CalibSubsystem->CreateLensFile(TEXT("MyCineLens"));

// 在镜头文件中添加一个畸变点（简化示例，实际需填充具体参数）
NewLensFile->AddDistortionPoint(FocalLength, ...);

// 在 Actor 上，获取或创建 LensComponent 并应用数据
if (ULensComponent* LensComp = MyCameraActor->FindComponentByClass<ULensComponent>())
{
    LensComp->SetLensFile(NewLensFile);
}
```

### 进阶用法

在运行时，根据摄像机状态动态设置畸变参数。通常需要结合 `UCameraComponent` 的更新循环。
（来源：`LensComponent.h`）

```cpp
// 在每帧或摄像机参数变化时调用
void AMyVirtualCamera::UpdateLensDistortion()
{
    if (ULensComponent* LensComp = FindComponentByClass<ULensComponent>())
    {
        FCameraLensDistortionState DistortionState;
        // 从当前摄像机的焦距、对焦距离等参数计算当前的畸变状态
        LensComp->EvaluateDistortion(CurrentFocalLength, CurrentFocusDistance, DistortionState);
        // 将计算出的畸变状态应用到后期处理
        LensComp->ApplyDistortion(DistortionState);
    }
}
```

## Demo 示例

一个最小化的 C++ 示例，展示如何在 Actor 初始化时设置一个基本的镜头校准组件。

```cpp
// MyCalibratedCamera.h
#pragma once
#include "GameFramework/Actor.h"
#include "MyCalibratedCamera.generated.h"

class ULensComponent;
class ULensFile;

UCLASS()
class AMyCalibratedCamera : public AActor
{
    GENERATED_BODY()
public:
    AMyCalibratedCamera();
    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere)
    ULensComponent* LensComponent;

    UPROPERTY(EditAnywhere, Category="Calibration")
    ULensFile* MyLensFile;
};

// MyCalibratedCamera.cpp
#include "MyCalibratedCamera.h"
#include "LensComponent.h"
#include "LensFile.h"

AMyCalibratedCamera::AMyCalibratedCamera()
{
    PrimaryActorTick.bCanEverTick = false;
    LensComponent = CreateDefaultSubobject<ULensComponent>(TEXT("LensComponent"));
}

void AMyCalibratedCamera::BeginPlay()
{
    Super::BeginPlay();
    if (LensComponent && MyLensFile)
    {
        LensComponent->SetLensFile(MyLensFile);
        // 触发一次初始的畸变评估
        LensComponent->EvaluateDistortion(FVector::ZeroVector, FVector::ZeroVector);
    }
}
```

## 模块依赖

该插件的模块依赖主要围绕虚拟制片生态系统，使用者通常需要依赖以下非通用模块：

| 模块 | 用途 |
|---|---|
| `Media` | 处理媒体输入，可能用于分析校准图案 |
| `MediaUtils` | 媒体工具函数 |
| `MediaAssets` | 媒体资产类型 |
| `LensComponent` | 核心的镜头组件，提供畸变应用逻辑 |
| `CineCamera` | 专业电影摄像机功能 |
| `MeshDescription` | 可能用于生成畸变网格 |
| `LevelSequence` | 与序列器集成，支持动画校准参数 |
| `RenderCore` | 底层渲染支持 |
| `RHI` | 渲染硬件接口 |
| `Renderer` | 渲染器核心 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated with a viewport. | 重构视口客户端关联逻辑，改善代码结构。 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回退了提交 CL53913857 的改动。 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated with a viewport. | 同 `cfb610df`，是同一功能的另一次提交。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量截断为浮点数导致的编译警告。 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the ... | 调整了多个虚拟制片资产的分类和归属。 |

### 维护评价

**维护中且活跃**。该插件创建于2021年，虽标记为实验性（`IsBetaVersion=true`），但作为虚拟制片的核心组件，一直有持续更新。从2026年5月的密集提交可以看出，其代码仍在积极重构和优化中（如视口逻辑重写），并伴随着常规的编译问题修复。这表明插件功能在不断完善，是虚拟制片流程中推荐使用的关键基础设施。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CameraCalibration)
- [官方文档] 无
- [测试用例] 无