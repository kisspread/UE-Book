# Lens Distortion (Deprecated)

> This plugin has been deprecated and will be removed in a future engine version. Please update your project to use the features of the CameraCalibration plugin instead.
Plugin to generate UV displacement for lens distortion/undistortion on the GPU from standard camera model.

| 属性 | 值 |
|---|---|
| 中文名 | 镜头畸变 |
| 分类 | Compositing |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `LensDistortion` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-06-27 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Compositing/LensDistortion) | |

## 用途

此插件的核心功能是解决**视频合成中真实摄像机镜头畸变的模拟与矫正问题**。它提供了一个标准的相机模型 (`FLensDistortionCameraModel`)，该模型基于OpenCV的畸变参数（径向畸变 K1-K3， 切向畸变 P1-P2， 焦距 F 和光心 C）。通过此模型，插件能够在GPU上生成一张UV位移图，该图的红绿通道存储了畸变位移，蓝Alpha通道存储了矫正位移。然后，可以将此UV位移图应用于后处理材质或渲染目标，从而在虚拟摄像机画面上实现逼真的镜头畸变效果，或对已有画面进行畸变矫正。

**简而言之，它的存在是为了让UE4/UE5能够方便地与真实摄像机拍摄的视频进行合成，或者创建具有真实感镜头缺陷的虚拟摄像机画面。**

## 使用场景

-   你正在使用UE进行视觉特效（VFX）或虚拟制片（Virtual Production），需要将CG内容与实拍镜头进行匹配，而实拍镜头存在明显的桶形或枕形畸变。
-   你需要在UE中模拟一个特定品牌和型号的真实摄像机镜头的光学特性。
-   你在构建增强现实（AR）或混合现实（MR）应用，需要对摄像机输入流进行实时的畸变矫正。

## 蓝图用法

所有核心功能已通过蓝图函数库 (`ULensDistortionBlueprintLibrary`) 暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Draw UV Displacement to Render Target` | 核心功能。根据输入的相机模型参数，在指定的渲染目标上绘制UV位移图。 | `ULensDistortionBlueprintLibrary` |
| `Get Undistort Overscan Factor` | 计算在进行畸变矫正渲染时，为了避免边缘出现未渲染像素所需的过扫描比例。 | `ULensDistortionBlueprintLibrary` |
| `Equal (LensDistortionCameraModel)` | 比较两个相机模型是否相等。可用于判断模型参数是否发生变化，以决定是否需要重新生成UV位移图。 | `ULensDistortionBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  **创建或获取 `FLensDistortionCameraModel` 数据**：你可以通过创建结构体变量、从数据表读取或通过蓝图函数计算来获得一组镜头畸变参数。
2.  **获取过扫描因子**：调用 `Get Undistort Ovscan Factor` 节点，输入相机模型、畸变后的水平视野（FOV）和宽高比，输出 `UndistortOverscanFactor`。
3.  **绘制UV位移图**：调用 `Draw UV Displacement to Render Target` 节点。将 `WorldContext` 对象（如当前玩家控制器）、相机模型、步骤2中得到的 `UndistortOverscanFactor` 以及一个作为输出目标的 `Texture Render Target 2D` 连接起来。可以调整 `Output Multiply` 和 `Output Add` 来对输出值进行缩放和偏移，使其适配后续材质的输入范围。
4.  **应用位移图**：将上一步生成的渲染目标作为纹理参数，传入一个后处理材质。在该材质中，采样该纹理的RG通道作为Distortion UV，采样BA通道作为Undistortion UV，使用这些UV对场景颜色或世界位置进行偏移采样，即可实现最终的畸变/矫正效果。

## C++ 用法

### 头文件引入

```cpp
#include "LensDistortionAPI.h"
#include "LensDistortionBlueprintLibrary.h" // 如果需要使用蓝图库的静态函数
```

### 基本用法

以下代码演示了如何创建一个相机模型并计算其畸变矫正系数。
*来源：`Source/LensDistortion/Classes/LensDistortionAPI.h`*

```cpp
// 1. 创建一个镜头畸变相机模型实例
FLensDistortionCameraModel MyCameraModel;

// 2. 设置参数（通常从文件、数据资产或序列化数据中读取）
MyCameraModel.K1 = -0.28f;  // 径向畸变参数1
MyCameraModel.K2 = 0.08f;   // 径向畸变参数2
MyCameraModel.K3 = 0.0f;    // 径向畸变参数3
MyCameraModel.P1 = 0.001f;  // 切向畸变参数1
MyCameraModel.P2 = 0.0005f; // 切向畸变参数2
MyCameraModel.F = FVector2D(1000.f, 1000.f); // 焦距 (Fx, Fy)
MyCameraModel.C = FVector2D(960.f, 540.f);  // 光心 (Cx, Cy)

// 3. 计算矫正过扫描因子
float DesiredHFOV = 90.f; // 期望的畸变后画面水平视野（度）
float DesiredAspectRatio = 16.f/9.f; // 期望的畸变后画面宽高比
float OverscanFactor = MyCameraModel.GetUndistortOverscanFactor(DesiredHFOV, DesiredAspectRatio);

// 此时，OverscanFactor 包含了将视野扩大多少倍才能在矫正后填满原始画面的信息。
```

### 进阶用法

在渲染循环中生成并使用UV位移图。
*来源：`Source/LensDistortion/Classes/LensDistortionAPI.h` 和 `Source/LensDistortion/Classes/LensDistortionBlueprintLibrary.h`*

```cpp
// 假设在某个渲染或 Tick 函数中
// ... MyCameraModel 已经设置好 ... 
// ... OverscanFactor 已经计算好 ...
// ... MyRenderTarget 是一个 UTextureRenderTarget2D* ...

// 方式一：通过模型成员函数直接绘制（需要UWorld*）
if (UWorld* World = GetWorld())
{
    MyCameraModel.DrawUVDisplacementToRenderTarget(
        World,
        DesiredHFOV,
        DesiredAspectRatio,
        OverscanFactor,
        MyRenderTarget,
        0.5f, // OutputMultiply
        0.5f  // OutputAdd
    );
}

// 方式二：通过蓝图库的静态函数绘制（更常见于蓝图或通用代码）
ULensDistortionBlueprintLibrary::DrawUVDisplacementToRenderTarget(
    this, // WorldContextObject
    MyCameraModel,
    DesiredHFOV,
    DesiredAspectRatio,
    OverscanFactor,
    MyRenderTarget,
    0.5f,
    0.5f
);
```

## Demo 示例

一个完整的最小C++示例，用于生成并保存一张UV位移图。

**LensDistortionDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "LensDistortionAPI.h"

class FLensDistortionDemo
{
public:
    static void GenerateAndSaveUVDisplacementMap();
};
```

**LensDistortionDemo.cpp**
```cpp
#include "LensDistortionDemo.h"
#include "LensDistortionBlueprintLibrary.h"
#include "Engine/TextureRenderTarget2D.h"
#include "Kismet/KismetRenderingLibrary.h"

void FLensDistortionDemo::GenerateAndSaveUVDisplacementMap()
{
    // 创建并配置相机模型
    FLensDistortionCameraModel Model;
    Model.K1 = -0.28f;
    Model.K2 = 0.08f;
    Model.F = FVector2D(1000.f, 1000.f);
    Model.C = FVector2D(960.f, 540.f);

    // 创建输出渲染目标
    UTextureRenderTarget2D* RenderTarget = NewObject<UTextureRenderTarget2D>();
    RenderTarget->InitAutoFormat(1920, 1080);

    // 计算过扫描因子并绘制
    float Overscan = Model.GetUndistortOverscanFactor(90.f, 16.f/9.f);
    ULensDistortionBlueprintLibrary::DrawUVDisplacementToRenderTarget(
        GEngine->GetWorldContexts()[0].World(),
        Model,
        90.f,
        16.f/9.f,
        Overscan,
        RenderTarget,
        0.5f,
        0.5f
    );

    // 可选：将渲染目标保存为文件以便查看
    FString SavePath = FPaths::ProjectSavedDir() / TEXT("UVDisplacement.png");
    UKismetRenderingLibrary::ExportRenderTarget(nullptr, RenderTarget, FPaths::GetPath(SavePath), FPaths::GetCleanFilename(SavePath));
}
```

## 模块依赖

要使用此插件，你的模块需要依赖以下核心模块（假设在 `Build.cs` 中已定义）：

| 模块 | 用途 |
|---|---|
| `LensDistortion` | 插件本身的核心模块 |
| `RenderCore` | 用于访问渲染线程命令和 GPU 资源 |
| `RHI` | 渲染硬件接口 |

## 维护状态

**已废弃 (Deprecated)**。此插件已被官方标记为废弃，并将在未来的引擎版本中移除。Epic Games 明确建议使用 `CameraCalibration` 插件作为替代。

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-02-22 | `01203093` | Deprecate: | 正式将插件标记为废弃。 |
| 2024-01-29 | `10cdd4a1` | Merging //UE5/Dev-ParallelRendering/... | 合并并行渲染分支代码，可能是通用的渲染线程重构。 |
| 2023-03-01 | `dd7c0212` | Changing a lot more code to use batched shader parameters. | 大规模更新代码以使用批处理着色器参数。 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 通用的插件目录代码更新或维护。 |
| 2022-12-08 | `6e30ddb0` | Dependency cleanup around DataDrivenShaderPlatformInfo and a few other headers. | 清理与数据驱动着色器平台信息相关的依赖。 |

### 维护评价

-   **状态**: **已废弃**。最后实质性更新（标记废弃）在 2024 年初，但在此之前其核心功能已基本稳定，多年未有重大功能更新。
-   **推荐度**: **不推荐用于新项目**。官方已明确弃用。所有新开发都应使用功能更强大、受支持的 `CameraCalibration` 插件。仅当维护一个需要此特定旧功能的遗留项目时，才可能仍需了解此插件。
-   **已知限制**: 功能相对单一，仅支持基于 OpenCV 参数的畸变模型。已被更全面的相机校准系统取代。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Compositing/LensDistortion)
-   [官方文档](https://docs.unrealengine.com/) (无直接链接，相关内容已整合至相机校准文档)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Compositing/LensDistortion/Tests)