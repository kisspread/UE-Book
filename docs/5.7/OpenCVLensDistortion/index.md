# OpenCV Lens Distortion

> Plugin to handle camera calibration and lens distortion/undistortion displacement map generation using OpenCV.

| 属性 | 值 |
|---|---|
| 分类 | Compositing |
| 默认启用 | false |
| 包含内容 | true |
| 模块 | OpenCVLensCalibration (Runtime), OpenCVLensDistortion (Runtime) |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Compositing/OpenCVLensDistortion) | |

## 用途

这个 plugin 提供了两个核心能力：

1. **相机标定（Camera Calibration）**：通过输入棋盘格（checkerboard）图像，利用 OpenCV 的 `calibrateCamera` / `fisheye::calibrate` 算法，计算出相机的内参矩阵和镜头畸变系数（K1-K6, P1, P2）。支持标准针孔模型（pinhole）和鱼眼模型（fisheye）。

2. **畸变位移图生成（Displacement Map Generation）**：根据标定得到的畸变参数，生成 UV 位移纹理（Displacement Map），用于在渲染管线中对图像进行去畸变（undistort）或反向畸变（re-distort）。位移图的 R/G 通道存储 distort→undistort 的偏移，B/A 通道存储 undistort→distort 的偏移。底层通过自定义 Global Shader（`DisplacementMapGeneration.usf`）在 GPU 上执行。

简单来说：**它把 OpenCV 的镜头畸变校正能力桥接到了 UE5 的渲染管线中**，使得你可以用真实的相机参数来校正虚拟合成画面的畸变，或对真实相机画面进行去畸变处理。

## 使用场景

- **虚拟制片（Virtual Production）**：你用真实摄像机拍摄绿幕画面，需要对画面做去畸变后再与虚拟场景合成 → 先用棋盘格标定镜头参数，再生成位移图进行去畸变
- **AR 合成**：需要让虚拟物体的透视畸变与真实镜头一致 → 用标定参数对虚拟相机施加相同的畸变效果
- **相机标定工具**：需要在引擎内直接完成相机标定流程，而不必依赖外部工具

## 蓝图用法

### 核心节点

#### 标定相关（OpenCVLensCalibration 模块）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateCalibrator` | 创建标定器，指定棋盘格尺寸和方格大小 | `UOpenCVLensCalibrator` |
| `FeedRenderTarget` | 将包含棋盘格的 RenderTarget 喂入标定器，返回是否成功检测到棋盘格 | `UOpenCVLensCalibrator` |
| `FeedImage` | 将包含棋盘格的图片文件路径喂入标定器 | `UOpenCVLensCalibrator` |
| `CalculateLensParameters` | 根据已喂入的图像计算畸变参数，输出 `FOpenCVLensDistortionParameters` 和相机视角信息 | `UOpenCVLensCalibrator` |

#### 位移图相关（OpenCVLensDistortion 模块）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateUndistortUVDisplacementMap` | 根据畸变参数和目标图像尺寸，生成去畸变位移纹理 | `UOpenCVLensDistortionBlueprintLibrary` |
| `DrawDisplacementMapToRenderTarget` | 将预计算的位移图绘制到 RenderTarget（含双向位移） | `UOpenCVLensDistortionBlueprintLibrary` |

### 使用示例（蓝图描述）

**场景：标定相机并生成去畸变位移图**

1. 使用 `CreateCalibrator` 节点，设置 BoardWidth=7, BoardHeight=5, SquareSize=3.0
2. 循环调用 `FeedRenderTarget`，每次传入一张包含棋盘格的 RenderTarget（建议 10-25 张，覆盖画面不同区域）
3. 调用 `CalculateLensParameters` 获取 `FOpenCVLensDistortionParameters`、重投影误差（MarginOfError）和相机视角信息
4. 调用 `CreateUndistortUVDisplacementMap`，传入参数和目标图像尺寸，CroppingFactor 控制裁剪程度（0=保留全部像素，1=裁掉黑边）
5. 使用 `DrawDisplacementMapToRenderTarget` 将位移图渲染到 RenderTarget
6. 将生成的位移图用于后期材质，对画面进行去畸变

## C++ 用法

### 头文件引入

```cpp
#include "OpenCVLensDistortionParameters.h"
#include "OpenCVLensDistortionBlueprintLibrary.h"
```

### 基本用法

```cpp
// 1. 创建标定器（来源：OpenCVLensCalibrator.cpp）
UOpenCVLensCalibrator* Calibrator = UOpenCVLensCalibrator::CreateCalibrator(
    7,      // BoardWidth - 棋盘格内角点宽
    5,      // BoardHeight - 棋盘格内角点高
    3.0f,   // SquareSize - 方格大小（世界单位）
    false   // bUseFisheyeModel - 是否使用鱼眼模型
);

// 2. 喂入棋盘格图像
bool bFound = Calibrator->FeedRenderTarget(MyRenderTarget);
// bFound == true 表示成功检测到棋盘格角点

// 3. 计算畸变参数
FOpenCVLensDistortionParameters LensParams;
float MarginOfError;
FOpenCVCameraViewInfo CameraViewInfo;
bool bSuccess = Calibrator->CalculateLensParameters(LensParams, MarginOfError, CameraViewInfo);
```

### 进阶用法

```cpp
// 生成去畸变位移图
FOpenCVCameraViewInfo OutViewInfo;
UTexture2D* DisplacementMap = UOpenCVLensDistortionBlueprintLibrary::CreateUndistortUVDisplacementMap(
    LensParams,
    FIntPoint(1920, 1080),  // 相机图像分辨率
    1.0f,                    // CroppingFactor: 1=裁掉所有黑边
    OutViewInfo
);

// 将位移图绘制到 RenderTarget（包含双向位移信息）
UOpenCVLensDistortionBlueprintLibrary::DrawDisplacementMapToRenderTarget(
    WorldContextObject,
    OutputRenderTarget,
    DisplacementMap
);

// OutViewInfo 中的 FOV 可用于调整 SceneCapture 的视角
// OutViewInfo.HorizontalFOV / VerticalFOV / FocalLengthRatio
```

### FOpenCVLensDistortionParameters 结构体

这个结构体是整个 plugin 的数据核心，继承自 `FOpenCVLensDistortionParametersBase`（来自 OpenCVHelper 模块），包含：

| 字段 | 说明 |
|---|---|
| `F` (FVector2D) | 归一化焦距 (Fx, Fy) |
| `C` (FVector2D) | 归一化主点 (Cx, Cy) |
| `K1` - `K6` | 径向畸变系数 |
| `P1`, `P2` | 切向畸变系数 |
| `bUseFisheyeModel` | 是否使用鱼眼模型（鱼眼模型仅使用 K1-K4） |

### FOpenCVCameraViewInfo 结构体

| 字段 | 说明 |
|---|---|
| `HorizontalFOV` | 水平视场角（度） |
| `VerticalFOV` | 垂直视场角（度） |
| `FocalLengthRatio` | 焦距纵横比 Fy/Fx |

## Demo 示例

### 最小可编译示例

**Build.cs 依赖：**

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "OpenCVLensDistortion",
    "OpenCVLensCalibration"
});
```

**MyLensCalibrationActor.h：**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "OpenCVLensDistortionParameters.h"
#include "MyLensCalibrationActor.generated.h"

UCLASS()
class AMyLensCalibrationActor : public AActor
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    UTextureRenderTarget2D* CalibrationRenderTarget;

    UPROPERTY(BlueprintReadOnly)
    FOpenCVLensDistortionParameters LensParameters;

    UPROPERTY(BlueprintReadOnly)
    FOpenCVCameraViewInfo CameraViewInfo;

    UPROPERTY(BlueprintReadOnly)
    float ReprojectionError;

    UFUNCTION(BlueprintCallable)
    void RunCalibration();
};
```

**MyLensCalibrationActor.cpp：**

```cpp
#include "MyLensCalibrationActor.h"
#include "OpenCVLensCalibrator.h"
#include "OpenCVLensDistortionBlueprintLibrary.h"

void AMyLensCalibrationActor::RunCalibration()
{
    // 创建标定器
    UOpenCVLensCalibrator* Calibrator = UOpenCVLensCalibrator::CreateCalibrator(7, 5, 3.0f);

    // 喂入多张棋盘格图像（此处仅示意一张）
    if (Calibrator->FeedRenderTarget(CalibrationRenderTarget))
    {
        // 计算参数
        if (Calibrator->CalculateLensParameters(LensParameters, ReprojectionError, CameraViewInfo))
        {
            UE_LOG(LogTemp, Log, TEXT("标定成功！误差: %f, 水平FOV: %f"),
                ReprojectionError, CameraViewInfo.HorizontalFOV);
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `OpenCV` | OpenCV 第三方库本体（plugin 级依赖） |
| `OpenCVHelper` | UE 封装的 OpenCV 辅助模块，提供 `FOpenCVLensDistortionParametersBase` 基类 |
| `Core` | UE 核心模块 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心（Texture, World 等） |
| `RenderCore` | 渲染核心（GlobalShader 等） |
| `RHI` | 渲染硬件接口 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2024-01-29 | `10cdd4a` | Merging Dev-ParallelRendering to Main | 合并并行渲染分支，非针对性改动 |
| 2023-03-01 | `dd7c021` | Changing code to use batched shader parameters | Shader 参数批量化重构，属于底层渲染 API 适配 |
| 2023-01-17 | `44aeabe` | Fixed non unity/pch compile errors | 编译修复，非功能性改动 |

### 维护评价

- **年龄**：2018 年创建，已超过 7 年
- **最后实质性更新**：最近 3 次提交均为全引擎范围的编译/重构变更，非本 plugin 的功能更新
- **Beta 状态**：`.uplugin` 中 `IsBetaVersion=true`，自创建以来一直是 Beta
- **平台限制**：仅支持 Win64、Linux、Mac
- **默认未启用**：`EnabledByDefault=false`，需要手动在项目设置中启用
- **⚠️ 警告**：该 plugin 已超过 **6 年没有实质性功能更新**，且一直处于 Beta 状态。它功能完整但可能不会收到新特性。对于生产环境的虚拟制片项目仍可使用，但需自行验证与当前 UE 版本的兼容性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Compositing/OpenCVLensDistortion)
- 官方文档：无（DocsURL 为空）
- [Shader 源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Compositing/OpenCVLensDistortion/Shaders/Private/DisplacementMapGeneration.usf)
