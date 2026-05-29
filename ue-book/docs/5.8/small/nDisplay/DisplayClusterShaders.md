# DisplayClusterShaders

> 支持多 PC 同步集群渲染的着色器模块，用于 nDisplay 的单目/立体渲染管线。

| 属性 | 值 |
|---|---|
| 中文名 | 显示集群着色器 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DisplayClusterShaders` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 🏛️ 文物（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterShaders) | |

## 用途

DisplayClusterShaders 是 nDisplay 插件的核心渲染着色器模块，提供**纹理操作工具链**和**渲染管线着色器**。它解决了以下问题：

1. **Warp & Blend 渲染**：将渲染画面通过网格变形（warp）和混合（blend）投射到各种物理屏幕配置上，支持 MPCDI 标准格式和 ICVFX（虚拟制片内部摄影机）两种模式
2. **ICVFX 合成**：在虚拟制片场景中，将多个内部摄影机画面、色度键（chromakey）、LightCard（光卡）层合成为最终外视口画面
3. **纹理工具链**：提供跨 RHI/RDG 的统一纹理拷贝、重采样、颜色编码转换等工具
4. **后处理着色器**：包括模糊（高斯/膨胀）、输出重映射、Mip 生成、PQ HDR 编解码、叠加层混合、纹理旋转/翻转等

**为什么需要单独的着色器模块**：nDisplay 需要在渲染线程执行大量自定义 GPU 操作（warp、blend、ICVFX 合成），这些操作不适合放在标准渲染管线中，因此抽离为独立模块，便于维护和跨平台适配。

## 使用场景

- 你在搭建 LED 虚拟制片摄影棚（如 The Volume） → 使用 ICVFX 模式进行多摄像机画面合成
- 你需要将 UE 画面投射到曲面屏幕或多屏拼接墙 → 使用 MPCDI Warp & Blend
- 你正在构建多 PC 集群渲染系统，需要在输出端应用畸变校正 → 使用 Output Remap
- 你需要在 nDisplay 视口间传递纹理并进行颜色空间转换 → 使用 TextureUtils
- 你在做 HDR 工作流，需要 PQ/Linear 之间的编码转换 → 使用 Media PQ 着色器

## 蓝图用法

DisplayClusterShaders 主要是 C++ 渲染管线模块，直接暴露的蓝图节点有限。但通过 `FMPCDIGeometryImportData` 和 `FMPCDIGeometryExportData` 结构体可与蓝图交互。

### 核心结构体

| 结构体 | 说明 | 所在类 |
|---|---|---|
| `FMPCDIGeometryImportData` | MPCDI 几何体导入数据（顶点+网格尺寸） | `MPCDIGeometryData.h` |
| `FMPCDIGeometryExportData` | MPCDI 几何体导出数据（顶点+法线+UV+三角形） | `MPCDIGeometryData.h` |

### 使用示例（蓝图描述）

1. **导入 MPCDI 几何体**：创建 `FMPCDIGeometryImportData` 结构体，设置 `Width`/`Height` 网格尺寸和 `Vertices` 顶点数组，传入 nDisplay 配置系统
2. **导出 MPCDI 几何体**：从 `FMPCDIGeometryExportData` 获取 `Vertices`/`Normal`/`UV`/`Triangles` 数据，可用于自定义几何体渲染

## C++ 用法

### 头文件引入

```cpp
// 核心接口
#include "IDisplayClusterShaders.h"

// 纹理工具
#include "IDisplayClusterShadersTextureUtils.h"
#include "Containers/DisplayClusterShaderContainers_TextureUtils.h"

// ICVFX 参数
#include "ShaderParameters/DisplayClusterShaderParameters_ICVFX.h"

// WarpBlend 参数
#include "ShaderParameters/DisplayClusterShaderParameters_WarpBlend.h"
```

### 基本用法 — 获取着色器模块接口

```cpp
// 来源: Public/IDisplayClusterShaders.h
// 获取 IDisplayClusterShaders 单例
IDisplayClusterShaders& ShadersModule = IDisplayClusterShaders::Get();

// 检查模块是否可用
if (IDisplayClusterShaders::IsAvailable())
{
    IDisplayClusterShaders& Shaders = IDisplayClusterShaders::Get();
    // 使用着色器功能...
}
```

### 基本用法 — 执行 Warp & Blend 渲染

```cpp
// 来源: Public/IDisplayClusterShaders.h, Public/ShaderParameters/DisplayClusterShaderParameters_WarpBlend.h
FRHICommandListImmediate& RHICmdList = /* ... */;

// 构造 WarpBlend 参数
FDisplayClusterShaderParameters_WarpBlend WarpBlendParams;
WarpBlendParams.Src.Set(SourceTexture, SourceRect);
WarpBlendParams.Dest.Set(DestTexture, DestRect);
WarpBlendParams.WarpInterface = MyWarpBlendInterface;
WarpBlendParams.bRenderAlphaChannel = true;

// 执行 MPCDI warp blend
bool bSuccess = IDisplayClusterShaders::Get().RenderWarpBlend_MPCDI(RHICmdList, WarpBlendParams);
```

### 基本用法 — 纹理拷贝工具链

```cpp
// 来源: Public/IDisplayClusterShadersTextureUtils.h, Private/DisplayClusterShadersTextureUtils.h
// 创建 RHI 模式的纹理工具
TSharedRef<IDisplayClusterShadersTextureUtils> TextureUtils =
    IDisplayClusterShaders::Get().CreateTextureUtils_RenderThread(RHICmdList);

// 设置输入输出纹理
FDisplayClusterShadersTextureViewport InputViewport(SourceTexture, SourceRect);
FDisplayClusterShadersTextureViewport OutputViewport(DestTexture, DestRect);

TextureUtils->SetInput(InputViewport)
             ->SetOutput(OutputViewport)
             ->Resolve();

// 使用 RDG 模式
TSharedRef<IDisplayClusterShadersTextureUtils> RDGTextureUtils =
    IDisplayClusterShaders::Get().CreateTextureUtils_RenderThread(GraphBuilder);

FDisplayClusterShadersTextureViewport RDGInput(RDGInputTexture, InputRect);
FDisplayClusterShadersTextureViewport RDGOutput(RDGOutputTexture, OutputRect);

RDGTextureUtils->SetInput(RDGInput)
                ->SetOutput(RDGOutput)
                ->Resolve();
```

### 进阶用法 — ICVFX 多摄像机合成

```cpp
// 来源: Public/ShaderParameters/DisplayClusterShaderParameters_ICVFX.h
FRHICommandListImmediate& RHICmdList = /* ... */;

// 构造 WarpBlend 参数（外视口）
FDisplayClusterShaderParameters_WarpBlend WarpBlendParams;
WarpBlendParams.Src.Set(OuterViewportTexture, OuterViewportRect);
WarpBlendParams.Dest.Set(OutputTexture, OutputRect);

// 构造 ICVFX 参数
FDisplayClusterShaderParameters_ICVFX ICVFXParams;

// 添加内部摄像机
FDisplayClusterShaderParameters_ICVFX::FCameraSettings Camera;
Camera.Resource.ViewportId = TEXT("camera_inner_1");
Camera.ChromakeySource = EDisplayClusterShaderParametersICVFX_ChromakeySource::FrameColor;
Camera.ChromakeyColor = FLinearColor::Green;
Camera.RenderOrder = 0;
ICVFXParams.Cameras.Add(Camera);

// 设置 LightCard
ICVFXParams.LightCardOver.ViewportId = TEXT("lightcard_over");
ICVFXParams.LightCardGamma = 2.2f;

// 设置摄像机投影数据
FDisplayClusterShaderParametersICVFX_CameraViewProjection ViewProj;
ViewProj.ViewRotation = FRotator(0, 90, 0);
ViewProj.ViewLocation = FVector(0, 0, 100);
ViewProj.PrjMatrix = FTranslationMatrix(FVector::ZeroVector) * ProjectionMatrix;
ICVFXParams.Cameras[0].SetViewProjection(ViewProj, Origin2WorldTransform);

// 执行 ICVFX warp blend
bool bSuccess = IDisplayClusterShaders::Get().RenderWarpBlend_ICVFX(
    RHICmdList, WarpBlendParams, ICVFXParams);
```

### 进阶用法 — 纹理变换与 HDR 编码

```cpp
// 来源: Public/ShaderParameters/DisplayClusterShaderParameters_TransformTexture.h
// 纹理旋转/翻转
FDisplayClusterShaderParameters_TransformTexture TransformParams;
TransformParams.InputTexture = InputRDGTexture;
TransformParams.TranformationType =
    FDisplayClusterShaderParameters_TransformTexture::ETranformation::Rotation_90;

IDisplayClusterShaders::Get().AddTransformTexturePass(GraphBuilder, TransformParams);
// 结果在 TransformParams.OutputTexture 中

// 来源: Public/ShaderParameters/DisplayClusterShaderParameters_Media.h
// PQ HDR 编码（Linear → PQ）
FDisplayClusterShaderParameters_MediaPQ PQParams;
PQParams.InputTexture = LinearTexture;
PQParams.InputRect = InputRect;
PQParams.OutputTexture = PQTexture;
PQParams.OutputRect = OutputRect;

IDisplayClusterShaders::Get().AddLinearToPQPass(GraphBuilder, PQParams);

// PQ HDR 解码（PQ → Linear）
IDisplayClusterShaders::Get().AddPQToLinearPass(GraphBuilder, PQParams);
```

### 进阶用法 — 自定义纹理上下文迭代

```cpp
// 来源: Public/IDisplayClusterShadersTextureUtils.h
// 使用 ForEachContextByPredicate 进行自定义上下文处理
TSharedRef<IDisplayClusterShadersTextureUtils> Utils =
    IDisplayClusterShaders::Get().CreateTextureUtils_RenderThread(RHICmdList);

Utils->SetInput(InputViewport)
      ->SetOutput(OutputViewport)
      ->ForEachContextByPredicate(
          [](const FDisplayClusterShadersTextureViewportContext& Input,
             const FDisplayClusterShadersTextureViewportContext& Output)
          {
              // 对每一对输入/输出上下文执行自定义操作
              // 例如：立体渲染中对左右眼分别处理
          });
```

### 进阶用法 — 纹理工具设置选项

```cpp
// 来源: Public/Containers/DisplayClusterShaderContainers_TextureUtils.h
FDisplayClusterShadersTextureUtilsSettings Settings;

// 仅写入特定颜色通道
Settings.ColorMask = EColorWriteMask::CW_RED | EColorWriteMask::CW_GREEN;

// 使用输出纹理作为输入（原地操作）
Settings.Flags = EDisplayClusterShaderTextureUtilsFlags::UseOutputTextureAsInput;

// 禁用重采样着色器，仅执行简单拷贝
Settings.Flags = EDisplayClusterShaderTextureUtilsFlags::DisableResampleShader;

// 线性 alpha 羽化（边缘淡出）
Settings.Flags = EDisplayClusterShaderTextureUtilsFlags::EnableLinearAlphaFeather;

// 覆盖 alpha 通道
Settings.OverrideAlpha = EDisplayClusterShaderTextureUtilsOverrideAlpha::Set_Alpha_One;

Utils->SetInput(InputViewport)
      ->SetOutput(OutputViewport)
      ->Resolve(Settings);
```

## Demo 示例

### ICVFX 外视口合成的最小示例

```cpp
// NDShadersDemo.h
#pragma once

#include "CoreMinimal.h"

class FNDShadersDemo
{
public:
    static bool RenderICVFXDemo(FRHICommandListImmediate& RHICmdList,
        FRHITexture* OuterViewportTexture, const FIntRect& OuterViewportRect,
        FRHITexture* OutputTexture, const FIntRect& OutputRect,
        FRHITexture* InnerCameraTexture, const FIntRect& InnerCameraRect,
        FRHITexture* LightCardTexture);
};
```

```cpp
// NDShadersDemo.cpp
#include "NDShadersDemo.h"

#include "IDisplayClusterShaders.h"
#include "ShaderParameters/DisplayClusterShaderParameters_WarpBlend.h"
#include "ShaderParameters/DisplayClusterShaderParameters_ICVFX.h"

bool FNDShadersDemo::RenderICVFXDemo(
    FRHICommandListImmediate& RHICmdList,
    FRHITexture* OuterViewportTexture, const FIntRect& OuterViewportRect,
    FRHITexture* OutputTexture, const FIntRect& OutputRect,
    FRHITexture* InnerCameraTexture, const FIntRect& InnerCameraRect,
    FRHITexture* LightCardTexture)
{
    if (!IDisplayClusterShaders::IsAvailable())
    {
        return false;
    }

    // 1. 设置 WarpBlend 参数
    FDisplayClusterShaderParameters_WarpBlend WarpBlendParams;
    WarpBlendParams.Src.Set(OuterViewportTexture, OuterViewportRect);
    WarpBlendParams.Dest.Set(OutputTexture, OutputRect);

    // 2. 设置 ICVFX 参数
    FDisplayClusterShaderParameters_ICVFX ICVFXParams;

    // 内部摄像机设置
    FDisplayClusterShaderParameters_ICVFX::FCameraSettings Camera;
    Camera.Resource.ViewportId = TEXT("inner_camera");
    Camera.Resource.Texture = InnerCameraTexture;
    Camera.ChromakeySource = EDisplayClusterShaderParametersICVFX_ChromakeySource::FrameColor;
    Camera.ChromakeyColor = FLinearColor::Green;
    Camera.RenderOrder = 0;
    ICVFXParams.Cameras.Add(Camera);

    // LightCard 设置
    ICVFXParams.LightCardOver.ViewportId = TEXT("lightcard");
    ICVFXParams.LightCardOver.Texture = LightCardTexture;
    ICVFXParams.LightCardGamma = 2.2f;

    // 3. 执行渲染
    return IDisplayClusterShaders::Get().RenderWarpBlend_ICVFX(
        RHICmdList, WarpBlendParams, ICVFXParams);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DisplayClusterConfiguration` | nDisplay 配置数据访问 |
| `DisplayClusterWarp` | Warp & Blend 网格变形接口（`IDisplayClusterWarpBlend`） |
| `MPCDI` | MPCDI 标准格式支持 |
| `RHI` / `RenderCore` | 底层 GPU 命令和 RDG 构建 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 支持 MoviePipeline EXR 多图层导出 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 合并 WarpBlendAlpha 模式到 WarpBlend 主流程 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复 MRG 中拓扑感知摄影机命名和 MPCDI/ICVFX 不透明 alpha 问题 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 输出帧编码回退时支持非默认 DisplayGamma |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复 GUI 纹理尺寸小于视口尺寸时的闪烁问题 |

### 维护评价

- **创建时间**：2018-06-07，随 UE 4.20 企业版功能分支引入，已有约 8 年历史
- **更新频率**：**非常活跃**。近期更新密集（2026 年 5 月多周内有多次功能性更新），持续在修复 bug 和增加新功能（EXR 多图层、HDR gamma 支持等）
- **维护状态**：**活跃维护中**。Epic Games 持续投入资源，这是虚拟制片（Virtual Production）和 LED 墙渲染的核心模块
- **已知限制**：
  - 依赖 UnrealEd（即使标记为 Runtime 模块，Build.cs 中包含 UnrealEd 依赖）
  - 需要特定硬件配置（多 GPU、Sync 卡等）才能发挥全部功能
  - 文档和学习曲线较陡峭
- **推荐程度**：⭐⭐⭐⭐⭐ — 如果你在做虚拟制片、LED 墙或大规模集群渲染，这是必用模块

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterShaders)
- [官方文档](https://docs.unrealengine.com/en-US/ProductionPipelines/VirtualProduction/nDisplay/)
- [nDisplay 插件根目录](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)