# Lens Distortion (Deprecated)

> ⚠️ **此插件已废弃（Deprecated since UE 5.0）**，将在未来引擎版本中移除。请迁移到 [CameraCalibration](../CameraCalibration/index.md) 插件。
>
> 原始描述：Plugin to generate UV displacement for lens distortion/undistortion on the GPU from standard camera model.

| 属性 | 值 |
|---|---|
| 分类 | Compositing |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 是 |
| 模块 | LensDistortion (Runtime) |
| 创建时间 | 2017-06-27 |
| 年龄标签 | 👴 老古董（~9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Compositing/LensDistortion) | |

## 用途

LensDistortion 插件提供基于标准相机模型（径向畸变 K1/K2/K3 + 切向畸变 P1/P2）的 GPU 端镜头畸变/反畸变 UV 置换图生成能力。

它的核心功能是：根据相机内参（焦距 F、主点 C）和畸变系数，将 OpenCV 标准相机标定模型应用到 UE 的渲染管线中，生成一张 UV displacement map（位移贴图），然后可以用这张贴图对渲染结果进行畸变或反畸变处理。

**为什么存在：** 在影视虚拟制作（Virtual Production）场景中，需要将虚拟摄像机的画面与真实摄像机的画面进行合成。真实镜头存在光学畸变，如果虚拟摄像机不应用相同的畸变，合成结果会出现画面边缘对不上的问题。这个插件就是用来解决这个问题的。

**已被取代：** UE 5.0 引入了功能更完善的 CameraCalibration 插件，提供了相机标定、镜头畸变、nodal offset 等完整工作流。本插件的所有功能已被 CameraCalibration 覆盖。

## 使用场景

- 你在做虚拟制作（Virtual Production），需要将 CG 渲染与实拍镜头合成 → 请用 CameraCalibration
- 你有 OpenCV 标定得到的相机参数（K1-K3, P1-P2, F, C），需要在 UE 中应用镜头畸变 → 请用 CameraCalibration
- 你维护的是 UE 4.x 时代的遗留项目，还没迁移到 CameraCalibration → 仍可使用本插件，但建议尽快迁移

## 蓝图用法

> ⚠️ 所有蓝图节点均标记为 `DeprecatedFunction`，使用时会显示废弃警告。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetUndistortOverscanFactor` | 计算反畸变所需的 overscan 缩放因子，避免渲染时出现黑边 | `ULensDistortionBlueprintLibrary` |
| `DrawUVDisplacementToRenderTarget` | 将 UV 位移图渲染到 RenderTarget 中（RG 通道=畸变位移，BA 通道=反畸变位移） | `ULensDistortionBlueprintLibrary` |
| `Equal (LensDistortionCameraModel)` | 比较两个相机模型是否相等 | `ULensDistortionBlueprintLibrary` |
| `NotEqual (LensDistortionCameraModel)` | 比较两个相机模型是否不等 | `ULensDistortionBlueprintLibrary` |

### 使用示例（蓝图描述）

**生成 UV 位移贴图：**

1. 创建一个 `FLensDistortionCameraModel` 结构体变量
2. 填入你的相机标定参数：K1、K2、K3（径向畸变）、P1、P2（切向畸变）、F（焦距 Fx/Fy）、C（主点 Cx/Cy）
3. 调用 `GetUndistortOverscanFactor` 节点，输入 CameraModel + 水平 FOV + 宽高比，得到 OverscanFactor
4. 创建一个 `TextureRenderTarget2D`（大小可与渲染分辨率不同）
5. 调用 `DrawUVDisplacementToRenderTarget` 节点，将位移图渲染到 RenderTarget 中
6. 在后处理材质中采样该 RenderTarget，应用 UV 偏移实现畸变/反畸变效果

## C++ 用法

### 头文件引入

```cpp
#include "LensDistortionAPI.h"
#include "LensDistortionBlueprintLibrary.h"  // 如需蓝图函数库
```

### 基本用法

```cpp
// 来源: Source/LensDistortion/Classes/LensDistortionAPI.h + LensDistortionRendering.cpp

// 1. 创建并配置相机模型
FLensDistortionCameraModel CameraModel;
CameraModel.K1 = -0.2f;   // 径向畸变系数 1
CameraModel.K2 = 0.03f;   // 径向畸变系数 2
CameraModel.K3 = 0.0f;    // 径向畸变系数 3
CameraModel.P1 = 0.0f;    // 切向畸变系数 1
CameraModel.P2 = 0.0f;    // 切向畸变系数 2
CameraModel.F  = FVector2D(1.0f, 1.0f);    // 归一化焦距 Fx, Fy
CameraModel.C  = FVector2D(0.5f, 0.5f);    // 归一化主点 Cx, Cy

// 2. 计算 overscan 因子
float HorizontalFOV = FMath::DegreesToRadians(90.0f);
float AspectRatio = 16.0f / 9.0f;
float OverscanFactor = CameraModel.GetUndistortOverscanFactor(HorizontalFOV, AspectRatio);

// 3. 绘制 UV 位移图到 RenderTarget
UTextureRenderTarget2D* RT = /* 你的 RenderTarget */;
CameraModel.DrawUVDisplacementToRenderTarget(
    GetWorld(),
    HorizontalFOV,
    AspectRatio,
    OverscanFactor,
    RT,
    0.5f,  // OutputMultiply：位移缩放因子（默认 0.5 将 [-1,1] 映射到 [0,1]）
    0.5f   // OutputAdd：位移偏移值（默认 0.5）
);
```

### 进阶用法：手动反畸变单个点

```cpp
// 来源: Source/LensDistortion/Private/LensDistortionRendering.cpp
// UndistortNormalizedViewPosition 是核心数学函数，可用于手动反畸变

FVector2D DistortedViewPos(0.1f, 0.05f);  // 归一化视空间坐标 (x, y, z=1)
FVector2D UndistortedViewPos = CameraModel.UndistortNormalizedViewPosition(DistortedViewPos);
```

UV 位移图的通道含义：
- **R, G 通道**：畸变→反畸变的 UV 偏移（DistortUV to UndistortUV）
- **B, A 通道**：反畸变→畸变的 UV 偏移（UndistortUV to DistortUV）

内部实现使用 32×16 网格细分，在 GPU 上通过 vertex shader 做反畸变，pixel shader 计算双向位移，避免在 GPU 上运行牛顿迭代法。

## 模块依赖

从 `LensDistortion.Build.cs` 提取。你的模块需要依赖：

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、数学库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | World、RenderTarget、Texture 等 |
| `RenderCore` | 渲染核心、Shader 编译 |
| `RHI` | RHI 层硬件抽象 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2024-02-22 | `01203093` | Deprecate FRHITexture2D 等类型 | RHI 层 API 清理，非功能性变更 |
| 2024-01-29 | `10cdd4a1` | Merging Dev-ParallelRendering | 分支合并，无实质性改动 |
| 2023-03-01 | `dd7c0212` | Changing code to use batched shader parameters | Shader 参数传递方式重构，适配 RHI API 变化 |

### 维护评价

- **状态：已废弃（Deprecated）** — 自 UE 5.0 起标记为废弃，建议使用 CameraCalibration 替代
- 最后一次功能性更新在 2023 年之前，近年的 commit 都是跟随 RHI 层 API 变化的被动维护
- `.uplugin` 中 `EnabledByDefault: false`，默认不启用
- 所有公开 API 均标注了 `UE_DEPRECATED(5.0, ...)` 宏
- **建议：不要在新项目中使用此插件。** 如果你在维护旧项目且已启用此插件，应规划迁移到 CameraCalibration。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Compositing/LensDistortion)
- CameraCalibration 插件（本插件的替代品，位于 `Engine/Plugins/CameraCalibration/`）
