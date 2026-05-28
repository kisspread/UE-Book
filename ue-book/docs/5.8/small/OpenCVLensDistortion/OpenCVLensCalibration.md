# OpenCV Lens Distortion

> Plugin to handle camera calibration and lens distortion/undistortion displacement map generation using OpenCV.

| 属性 | 值 |
|---|---|
| 中文名 | OpenCV 镜头畸变 |
| 分类 | Compositing |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质模板） |
| 模块 | `OpenCVLensCalibration` (Runtime), `OpenCVLensDistortion` (Runtime) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Compositing/OpenCVLensDistortion) | |

## 用途

本插件的核心功能是利用 OpenCV 库实现**高精度的相机镜头畸变校准与校正**。它解决的是虚拟制片和影视合成中一个关键问题：如何精确模拟并消除真实物理相机镜头带来的畸变（如桶形畸变、枕形畸变），从而使 CG 元素能与实拍素材完美匹配。

插件提供了两个核心能力：
1.  **镜头校准**：通过拍摄已知图案（如棋盘格），计算出特定镜头的畸变参数。
2.  **畸变/反畸变贴图生成**：根据校准参数，生成可用于材质后期处理的**位移贴图**，实现镜头畸变的实时校正或反向应用。

这与 UE 内置的、较为基础的镜头畸变方案不同，它利用 OpenCV 的精确算法，为专业影视制作提供了工业级的镜头校准工作流。

## 使用场景

-   **虚拟制片 (Virtual Production)**：在 LED 幕墙前拍摄时，需要精确校正用于拍摄前景演员和背景板的物理相机镜头，确保 CG 虚拟场景与实拍画面在几何上无缝衔接。
-   **影视合成 (Film Compositing)**：将 CG 角色或物体合成到实拍镜头中时，必须对 CG 渲染结果应用与实拍镜头完全相同的畸变，否则画面会出现“对不齐”的穿帮感。
-   **增强现实 (AR)**：开发需要精确理解摄像头畸变的 AR 应用，以实现稳定的虚实融合。

## 蓝图用法

插件主要通过 `UOpenCVLensCalibrator` 类和 `UOpenCVLensUndistortionRendererInterface` 接口提供蓝图功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Calibrator` | 创建一个镜头校准器对象，用于收集棋盘格图像数据。 | `UOpenCVLensCalibrator` |
| `Feed Render Target` | 将一张包含棋盘格的渲染目标图像喂给校准器。 | `UOpenCVLensCalibrator` |
| `Feed Image` | 将一张包含棋盘格的图像文件路径喂给校准器。 | `UOpenCVLensCalibrator` |
| `Calculate Lens Parameters` | 根据喂入的图像数据，计算镜头的畸变参数、误差和相机视图信息。 | `UOpenCVLensCalibrator` |

### 使用示例（蓝图描述）

一个典型的镜头校准蓝图流程如下：

1.  **创建校准器**：调用 `Create Calibrator` 节点，设置棋盘格的宽度（内角点数）、高度（内角点数）和方格大小。返回一个 `UOpenCVLensCalibrator` 对象。
2.  **喂入数据**：在循环中，多次调用 `Feed Render Target` 或 `Feed Image`，将从同一物理相机在不同角度拍摄的棋盘格图像传给校准器。每次调用会返回一个布尔值，表示是否成功检测到棋盘格。
3.  **计算参数**：当收集了足够多（通常10-30张）不同角度的棋盘格图像后，调用 `Calculate Lens Parameters`。如果成功，将输出 `LensDistortionParameters`（畸变参数结构体）、`MarginOfError`（重投影误差，越小越好）和 `CameraViewInfo`（相机FOV等信息）。
4.  **应用校正**：将计算出的 `LensDistortionParameters` 传给实现了 `UOpenCVLensUndistortionRendererInterface` 的对象或材质，用于渲染畸变/反畸变位移贴图，最终通过后处理材质应用。

## C++ 用法

### 头文件引入

```cpp
#include "OpenCVLensCalibrator.h"
// 如果使用畸变/反畸变功能
#include "IOpenCVLensDistortionModule.h"
```

### 基本用法（镜头校准）

以下代码展示了如何使用 C++ 进行镜头校准。

**注意**：需要链接 `OpenCVLensCalibration` 模块。

```cpp
// 包含头文件
#include "OpenCVLensCalibrator.h"

// 创建校准器
// 棋盘格 9x6 个内角点，每个方格实际尺寸为 3.0 单位
UOpenCVLensCalibrator* Calibrator = UOpenCVLensCalibrator::CreateCalibrator(9, 6, 3.0f);

// 喂入数据（示例：从文件加载）
bool bFound = Calibrator->FeedImage(TEXT("/Game/CheckerboardImages/shot_001.jpg"));
if (bFound)
{
    UE_LOG(LogTemp, Log, TEXT("在 shot_001.jpg 中成功找到棋盘格。"));
}

// ... 喂入更多图片 ...

// 计算参数
FOpenCVLensDistortionParameters DistortionParams;
float ReprojectionError;
FOpenCVCameraViewInfo CameraInfo;

bool bSuccess = Calibrator->CalculateLensParameters(DistortionParams, ReprojectionError, CameraInfo);

if (bSuccess)
{
    UE_LOG(LogTemp, Log, TEXT("校准成功！重投影误差: %f"), ReprojectionError);
    // 此时可以使用 DistortionParams 和 CameraInfo
}
```

### 进阶用法（获取与应用畸变参数）

计算出的 `FOpenCVLensDistortionParameters` 可以用于生成位移贴图。

```cpp
#include "IOpenCVLensDistortionModule.h"

// 获取 OpenCV 镜头畸变模块
if (IOpenCVLensDistortionModule::IsAvailable())
{
    IOpenCVLensDistortionModule& LensDistortionModule = IOpenCVLensDistortionModule::Get();
    
    // 使用之前校准得到的参数
    FOpenCVLensUndistortionParameters UndistortionParams;
    // 将 FOpenCVLensDistortionParameters 转换为 FOpenCVLensUndistortionParameters
    UndistortionParams.DistortionParameters = DistortionParams;
    UndistortionParams.CameraViewInfo = CameraInfo;

    // 生成反畸变位移贴图（用于校正畸变）
    // 需要提供一个尺寸匹配的渲染目标
    UTextureRenderTarget2D* UndistortionMap = ...; 
    bool bRendered = LensDistortionModule.RenderLensUndistortion(
        UndistortionParams,
        1.0f, // 裁切缩放因子
        UndistortionMap,
        FOpenCVLensDistortionDelegates() // 回调
    );
}
```

## Demo 示例

一个完整的、可编译的最小示例，演示如何创建校准器并计算参数。

**MyLensCalibrationActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyLensCalibrationActor.generated.h"

class UOpenCVLensCalibrator;
class UTextureRenderTarget2D;

UCLASS()
class AMyLensCalibrationActor : public AActor
{
    GENERATED_BODY()

public:
    AMyLensCalibrationActor();

protected:
    virtual void BeginPlay() override;

public:
    // 校准器对象指针
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Calibration")
    UOpenCVLensCalibrator* LensCalibrator;

    // 存储校准结果
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Calibration")
    FOpenCVLensDistortionParameters LastDistortionParameters;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Calibration")
    float LastReprojectionError = 0.0f;

    // 执行一次校准流程（可在蓝图或按键触发）
    UFUNCTION(BlueprintCallable, Category = "Calibration")
    void PerformCalibration();
};
```

**MyLensCalibrationActor.cpp**
```cpp
#include "MyLensCalibrationActor.h"
#include "OpenCVLensCalibrator.h"

AMyLensCalibrationActor::AMyLensCalibrationActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyLensCalibrationActor::BeginPlay()
{
    Super::BeginPlay();

    // 1. 创建校准器
    // 假设使用 9x6 棋盘格，方格大小为 2.5 厘米
    LensCalibrator = UOpenCVLensCalibrator::CreateCalibrator(9, 6, 2.5f);
}

void AMyLensCalibrationActor::PerformCalibration()
{
    if (!LensCalibrator)
    {
        UE_LOG(LogTemp, Error, TEXT("校准器未初始化！"));
        return;
    }

    // 2. 喂入示例图片（实际项目中应从渲染目标或摄像头获取）
    // 这里仅为演示，使用假路径
    TArray<FString> ImagePaths = {
        TEXT("/Game/CalibrationImages/checkerboard_01.jpg"),
        TEXT("/Game/CalibrationImages/checkerboard_02.jpg"),
        TEXT("/Game/CalibrationImages/checkerboard_03.jpg"),
        TEXT("/Game/CalibrationImages/checkerboard_04.jpg"),
        TEXT("/Game/CalibrationImages/checkerboard_05.jpg")
    };

    int32 SuccessfulFeeds = 0;
    for (const FString& Path : ImagePaths)
    {
        if (LensCalibrator->FeedImage(Path))
        {
            SuccessfulFeeds++;
            UE_LOG(LogTemp, Log, TEXT("成功喂入图片: %s"), *Path);
        }
    }

    if (SuccessfulFeeds < 3)
    {
        UE_LOG(LogTemp, Warning, TEXT("成功喂入的图片不足（%d 张），无法进行可靠校准。"), SuccessfulFeeds);
        return;
    }

    // 3. 计算参数
    FOpenCVCameraViewInfo CameraViewInfo;
    bool bSuccess = LensCalibrator->CalculateLensParameters(
        LastDistortionParameters,
        LastReprojectionError,
        CameraViewInfo
    );

    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("镜头校准成功！重投影误差: %f"), LastReprojectionError);
        // 现在可以使用 LastDistortionParameters 来生成畸变贴图了
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("镜头校准失败。"));
    }
}
```

## 模块依赖

使用此插件，你的项目需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `OpenCV` | 核心计算机视觉库，提供相机标定和图像处理算法。 |
| `OpenCVLensCalibration` | 插件提供的校准器实现模块。 |
| `OpenCVLensDistortion` | 插件提供的畸变/反畸变渲染与参数模块。 |
| `OpenCVHelper` | 引擎提供的 OpenCV 与 UE 类型转换辅助模块。 |
| `RenderCore` | 用于渲染目标操作和 GPU 资源管理。 |
| `Renderer` | 用于访问渲染管线，生成位移贴图。 |
| `RHI` | 渲染硬件接口，底层图形 API 抽象。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式UE_LOG宏迁移到新的UE_LOGF宏，属代码现代化更新。 |
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 将插件配置文件从`Base*.ini`重命名为`Default*.ini`，遵循引擎新约定。 |
| 2024-01-29 | `10cdd4a1` | Merging //UE5/Dev-ParallelRendering/... | 合并并行渲染分支，可能包含渲染相关重构，非插件功能更新。 |
| 2023-03-01 | `dd7c0212` | Changing a lot more code to use batched shader parameters. | 大规模将代码改为使用批处理着色器参数，属渲染后端优化。 |
| 2023-01-17 | `44aeabe4` | [Engine/Plugins] | 引擎插件级别的通用提交，无具体信息。 |

### 维护评价

-   **创建时间**：2018年，是一个有一定历史的插件。
-   **最近更新频率和内容**：最近两年的更新主要是引擎底层的通用维护（配置文件重命名、宏迁移、渲染后端优化），**没有实质性的功能增强或 bug 修复**。最后的实质性功能更新可能追溯到2020-2021年左右。
-   **活跃维护状态**：**维护不活跃**。插件处于“仅维持编译通过”的状态，核心功能长期未更新。
-   **已知问题或限制**：
    1.  标记为 `IsBetaVersion: true`，意味着API可能不稳定。
    2.  `EnabledByDefault: false`，需要手动在项目设置中启用。
    3.  受限于OpenCV版本，可能无法利用最新的镜头模型算法。
    4.  仅支持Win64、Linux、Mac平台。
-   **是否推荐使用**：**谨慎推荐**。如果你正在维护一个使用此插件的旧项目，它仍能工作。对于新项目，除非你有强烈的精确OpenCV校准需求且愿意处理潜在的兼容性问题，否则建议评估UE内置方案或其他更现代、活跃的第三方插件。由于长期未更新，集成到新版本引擎或遇到问题时，获得支持的难度较大。

## 相关链接

-   [源码目录](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Compositing/OpenCVLensDistortion)
-   [官方文档] 无
-   [测试用例] 插件目录内未发现专用测试文件。核心功能测试可能位于引擎测试套件中，路径如 `Engine/Tests/Compositing/`。