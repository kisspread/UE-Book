# OpenCV Lens Distortion

> Plugin to handle camera calibration and lens distortion/undistortion displacement map generation using OpenCV.

| 属性 | 值 |
|---|---|
| 中文名 | OpenCV镜头畸变 |
| 分类 | Compositing |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `OpenCVLensCalibration` (Runtime), `OpenCVLensDistortion` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Compositing/OpenCVLensDistortion) | |

## 用途

该插件解决的是在实时合成（Compositing）工作流中，将虚拟内容与真实摄像机画面无缝融合的关键问题：**镜头畸变校正**。它利用强大的开源计算机视觉库 OpenCV，为给定的摄像机镜头参数计算并生成精确的畸变/反畸变位移贴图（Displacement Map）。这些贴图可用于在后期合成或实时渲染管线中，对渲染的图像或摄像机画面进行反向扭曲，从而消除或匹配真实镜头的畸变效果，确保合成元素与真实世界视角的几何匹配。

简单来说，它提供了一套工具，让虚拟摄像机“理解”并模拟真实摄像机的镜头特性。

## 使用场景

- **虚拟制片 (Virtual Production)**：在 LED 墙幕前拍摄时，需要将虚拟场景与真实摄像机画面精准对齐。使用此插件校正虚拟摄像机的畸变，使其与现场使用的物理摄像机镜头畸变相匹配。
- **增强现实 (AR) / 混合现实 (MR) 开发**：将虚拟物体叠加到真实世界的摄像头流上时，需要对摄像头输入进行反畸变，以保证虚拟物体看起来稳定地“粘”在真实表面上，而不会随镜头畸变而扭曲。
- **游戏开发**：模拟特定真实摄像机镜头（如广角镜头、鱼眼镜头）的畸变效果，用于创造特殊的视觉风格或模拟监控摄像头、潜望镜等视角。
- **工业视觉与仿真**：在需要精确复现物理镜头光学特性的仿真或训练应用中使用。

## 蓝图用法

该插件主要提供两个模块的功能节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CalibrateCamera` | 使用一组标定图像和棋盘格参数，计算摄像机的内参矩阵和畸变系数。 | `UOpenCVLensCalibrationModule` |
| `CreateUndistortionUVDisplacementMap` | 根据给定的摄像机参数（内参、畸变系数、分辨率），生成用于反畸变的UV位移贴图。 | `UOpenCVLensDistortionBlueprintLibrary` |
| `CreateDistortionUVDisplacementMap` | 根据给定的摄像机参数，生成用于施加畸变效果的UV位移贴图。 | `UOpenCVLensDistortionBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  **相机标定**：首先，使用一组棋盘格图像调用 `CalibrateCamera` 节点，输出得到 `CameraIntrinsics`（包含焦距、主点）和 `DistortionCoefficients`（畸变系数）。
2.  **生成贴图**：将上一步得到的参数，连同目标图像分辨率，输入到 `CreateUndistortionUVDisplacementMap` 节点。该节点会输出一张 `UTexture2D` 格式的位移贴图。
3.  **应用贴图**：在后处理材质（Post Process Material）中，采样这张位移贴图，并将其 UV 坐标偏移应用到场景颜色或法线等通道上，从而实现对整个画面或特定通道的反畸变效果。

## C++ 用法

### 头文件引入

```cpp
#include "OpenCVLensCalibrationModule.h"
#include "OpenCVLensDistortionBlueprintLibrary.h"
```

### 基本用法

```cpp
// (1) 加载一组标定图像（假设已加载到 TArray<UTexture2D*> 中）
TArray<UTexture2D*> CalibrationImages;
// ... 加载图片逻辑 ...

// (2) 执行相机标定
FOpenCVCameraIntrinsics OutCameraIntrinsics;
FOpenCVCameraDistortionParameters OutDistortionParameters;
bool bSuccess = UOpenCVLensCalibrationModule::CalibrateCamera(
    CalibrationImages,
    FIntPoint(9, 6), // 棋盘格角点数
    2.5f,            // 方格尺寸（厘米）
    OutCameraIntrinsics,
    OutDistortionParameters
);

// (3) 生成反畸变贴图
FIntPoint OutputSize(1920, 1080);
UTexture2D* UndistortionMap = UOpenCVLensDistortionBlueprintLibrary::CreateUndistortionUVDisplacementMap(
    OutCameraIntrinsics,
    OutDistortionParameters,
    OutputSize,
    EOpenCVLensDistortionDisplacementMapType::Undistortion // 生成反畸变贴图
);
```
*代码逻辑基于模块文档描述的功能构建。*

### 进阶用法

可以进一步利用生成的位移贴图设置到材质参数集合中，或在后处理渲染管线中直接使用其生成的UV数据进行高级扭曲操作。

## 模块依赖

该插件依赖 OpenCV 核心库及图像封装库。

| 模块 | 用途 |
|---|---|
| `OpenCV` | 提供底层的计算机视觉算法，是镜头标定和畸变计算的核心。 |
| `ImageWrapper` | 用于处理图像文件的加载和格式转换（如加载标定用的棋盘格图片）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF，属于内部代码现代化。 |
| 2025-10-07 | `96352708` | Renaming Base<Plugin>.ini to Default<Plugin>.ini | 重命名插件配置文件，遵循新的UE命名规范。 |
| 2024-01-29 | `10cdd4a1` | Merging //UE5/Dev-ParallelRendering/... | 合并并行渲染开发分支的改动，可能涉及底层渲染或模块加载调整。 |
| 2023-03-01 | `dd7c0212` | Changing a lot more code to use batched shader parameters. | 大规模使用批处理着色器参数，性能优化改动。 |
| 2023-01-17 | `44aeabe4` | [Engine/Plugins] | 一次针对多个插件的常规性更新。 |

### 维护评价

该插件创建于2018年（约8年前），标记为**实验性**且**默认未启用**。从近期提交记录看，虽然最近一次功能提交停留在2023年初，但在2025和2026年仍有与引擎整体架构同步的维护性提交（如重命名配置文件、迁移日志宏）。这表明该插件处于**“维护中”** 状态，能够跟随引擎主版本进行必要的适配和编译修复，但近期没有新增功能。

**结论**：对于需要OpenCV镜头校正功能的项目，它是一个可用的、经过验证的工具。但由于其“实验性”状态，使用者应注意自行验证其稳定性和性能，并关注引擎更新可能带来的兼容性变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Compositing/OpenCVLensDistortion)
- [模块文档 - OpenCVLensCalibration](OpenCVLensCalibration.md)
- [模块文档 - OpenCVLensDistortion](OpenCVLensDistortion.md)