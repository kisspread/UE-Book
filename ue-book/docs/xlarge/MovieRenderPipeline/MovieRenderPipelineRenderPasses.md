# Movie Render Pipeline - Render Passes

> Advanced movie rendering pipeline for use in creating rendered cinematics or other multi-media creation.

| 属性 | 值 |
|---|---|
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `MovieRenderPipelineCore` (Runtime), `MovieRenderPipelineEditor` (Runtime), `MovieRenderPipelineMP4Encoder` (Runtime), `MovieRenderPipelineRenderPasses` (Runtime), `MovieRenderPipelineSettings` (Runtime), `UEOpenExrRTTI` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-30 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MovieScene/MovieRenderPipeline) | |

---

## 用途

Movie Render Pipeline（MRP，又称 Movie Render Queue / MRQ）是 UE5 的专业级离线渲染管线，用于从 Sequencer 序列生成高质量的电影级渲染输出。它解决了实时引擎在影视制作中的核心矛盾：**实时渲染速度优先 vs 影视质量优先**。

MRP 通过以下机制实现影视级质量：

- **时间/空间超采样**：每帧渲染多个时间样本和空间子像素样本，消除锯齿和噪点
- **高分辨率分块渲染（Tiling）**：将超大分辨率画面拆分为多个 tile 分别渲染再拼合，突破 GPU 显存限制
- **路径追踪器集成**：支持 UE 内置 Path Tracer，可输出物理准确的全局光照结果
- **多通道输出**：单次渲染可同时输出 Beauty、Object ID、World Normal、Depth 等多个 AOV 通道
- **OCIO 色彩管理**：支持 OpenColorIO 变换，确保色彩在不同软件间的一致性
- **Movie Render Graph（MRG）**：新一代节点图系统，允许通过可视化节点组合自定义渲染管线

本模块（`MovieRenderPipelineRenderPasses`）是整个插件中**最核心的渲染逻辑层**，包含所有渲染 Pass 的实现（延迟渲染、路径追踪、全景渲染）以及所有输出格式的实现（EXR、PNG、BMP、JPG、WAV）。

## 使用场景

- 你在用 Sequencer 制作过场动画，需要渲染最终交付的 4K/8K 视频 → 用 MRQ 的 Deferred Pass + 高分辨率 Tiling
- 你需要物理准确的全局光照渲染（建筑可视化、产品展示）→ 用 Path Tracer Pass
- 你需要输出多通道 EXR 给后期合成软件（Nuke、DaVinci Resolve）→ 用 EXR Output Node，配置多层输出
- 你需要渲染 360° 全景视频（VR 内容）→ 用 Panoramic Pass Node
- 你需要自定义渲染管线（如同时渲染多个不同设置的 Pass）→ 用 Movie Render Graph 节点图系统
- 你需要在渲染时应用自定义后处理材质（如自定义 Outline、Toon Shading）→ 在 Deferred Pass Node 上配置 Additional Post Process Materials
- 你需要渲染带音频的视频 → 配合 Wave Output 节点输出 .wav 音频

## 蓝图用法

### 核心节点

#### 渲染 Pass 节点（Movie Render Graph）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetNumSpatialSamples` | 获取每帧空间采样数 | `UMovieGraphImagePassBaseNode` |
| `GetDisableToneCurve` | 是否禁用色调曲线（输出线性值） | `UMovieGraphImagePassBaseNode` |
| `GetAllowOCIO` | 是否允许 OCIO 色彩变换 | `UMovieGraphImagePassBaseNode` |
| `GetAllowDenoiser` | 是否启用降噪器（仅 Path Tracer） | `UMovieGraphImagePassBaseNode` |
| `GetAntiAliasingMethod` | 获取抗锯齿方法 | `UMovieGraphImagePassBaseNode` |
| `GetEnableHighResolutionTiling` | 是否启用高分辨率分块渲染 | `UMovieGraphImagePassBaseNode` |
| `GetTileCount` | 获取分块数量 | `UMovieGraphImagePassBaseNode` |
| `GetTileOverlapPercentage` | 获取分块重叠百分比 | `UMovieGraphImagePassBaseNode` |
| `GetWriteAllSamples` | 是否写出每个单独样本用于调试 | `UMovieGraphImagePassBaseNode` |
| `GetAdditionalPostProcessMaterials` | 获取附加后处理材质列表 | `UMovieGraphImagePassBaseNode` |

#### 输出节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FileNameFormatOverride` | WAV 文件名格式覆盖 | `UMoviePipelineWaveOutput` |

#### 延迟渲染 Pass 属性（蓝图可读写）

| 属性 | 说明 | 所在类 |
|---|---|---|
| `SpatialSampleCount` | 每帧空间采样数（1-64） | `UMovieGraphDeferredRenderPassNode` |
| `bDisableToneCurve` | 禁用色调曲线 | `UMovieGraphDeferredRenderPassNode` |
| `bAllowOCIO` | 允许 OCIO 变换 | `UMovieGraphDeferredRenderPassNode` |
| `bWriteAllSamples` | 写出所有样本 | `UMovieGraphDeferredRenderPassNode` |
| `bIncludeBeautyRenderInOutput` | 是否包含 Beauty Pass | `UMovieGraphDeferredRenderPassNode` |
| `bEnableHighResolutionTiling` | 启用高分辨率分块 | `UMovieGraphDeferredRenderPassNode` |
| `TileCount` | 分块数量 | `UMovieGraphDeferredRenderPassNode` |
| `OverlapPercentage` | 分块重叠百分比 | `UMovieGraphDeferredRenderPassNode` |
| `bAllocateHistoryPerTile` | 每个分块独立分配历史缓冲 | `UMovieGraphDeferredRenderPassNode` |
| `bPageToSystemMemory` | 分页到系统内存 | `UMovieGraphDeferredRenderPassNode` |

#### 路径追踪 Pass 属性

| 属性 | 说明 | 所在类 |
|---|---|---|
| `SpatialSampleCount` | 每帧空间采样数 | `UMovieGraphPathTracerRenderPassNode` |
| `SeedOffset` | 随机种子偏移 | `UMovieGraphPathTracerRenderPassNode` |
| `bEnableReferenceMotionBlur` | 启用参考级运动模糊 | `UMovieGraphPathTracerRenderPassNode` |
| `bEnableDenoiser` | 启用降噪器 | `UMovieGraphPathTracerRenderPassNode` |
| `DenoiserType` | 降噪器类型（Spatial/Temporal） | `UMovieGraphPathTracerRenderPassNode` |
| `MaxPathSamples` | 最大路径采样数 | `UMovieGraphPathTracerRenderPassNode` |
| `MaxBounces` | 最大光线反弹次数 | `UMovieGraphPathTracerRenderPassNode` |

#### 全景渲染 Pass 属性

| 属性 | 说明 | 所在类 |
|---|---|---|
| `NumHorizontalSteps` | 水平方向步数（最小 8） | `UMovieGraphDeferredPanoramicNode` |
| `NumVerticalSteps` | 垂直方向步数（最小 3） | `UMovieGraphDeferredPanoramicNode` |
| `bFollowCameraOrientation` | 是否跟随相机朝向 | `UMovieGraphDeferredPanoramicNode` |
| `bAllocateHistoryPerPane` | 每个面板独立分配历史缓冲 | `UMovieGraphDeferredPanoramicNode` |
| `bPageToSystemMemory` | 分页到系统内存 | `UMovieGraphDeferredPanoramicNode` |

### 使用示例（蓝图描述）

**配置 Movie Render Graph 延迟渲染 + EXR 输出：**

1. 在 Movie Render Graph 编辑器中，创建一个 `UMovieGraphDeferredRenderPassNode`
2. 设置 `SpatialSampleCount` 为 4（4x 超采样）
3. 启用 `bOverride_AntiAliasingMethod` 并设置为 `AAM_TemporalAA`
4. 创建一个 `UMovieGraphImageSequenceOutputNode_EXR` 输出节点
5. 在 EXR 节点中配置压缩格式（如 `DWAB`）和多层输出
6. 连接渲染 Pass 到输出节点
7. 通过 Movie Render Queue 面板提交渲染任务

**配置路径追踪渲染：**

1. 创建 `UMovieGraphPathTracerRenderPassNode`
2. 设置 `MaxPathSamples` 为 4096（高质量）
3. 设置 `MaxBounces` 为 12
4. 启用 `bEnableDenoiser` 并选择 `Temporal` 降噪器
5. 连接到 EXR 输出节点

## C++ 用法

### 头文件引入

```cpp
// 延迟渲染 Pass
#include "MoviePipelineDeferredPasses.h"

// 路径追踪 Pass
#include "Graph/Renderers/MovieGraphPathTracerPass.h"

// 全景渲染 Pass
#include "Graph/Renderers/MovieGraphDeferredPanoramicPass.h"

// 图像序列输出
#include "MoviePipelineImageSequenceOutput.h"

// EXR 输出
#include "MoviePipelineEXROutput.h"

// WAV 音频输出
#include "MoviePipelineWaveOutput.h"

// Movie Render Graph 节点
#include "Graph/Nodes/MovieGraphDeferredPassNode.h"
#include "Graph/Nodes/MovieGraphPathTracerPassNode.h"
#include "Graph/Nodes/MovieGraphDeferredPanoramicPassNode.h"
#include "MovieGraphImageSequenceOutputNode.h"
```

### 基本用法

**创建自定义渲染 Pass（继承 FMovieGraphDeferredPass）：**

```cpp
// 来源: Graph/Renderers/MovieGraphDeferredPass.h
namespace UE::MovieGraph::Rendering
{
    struct FMyCustomDeferredPass : public FMovieGraphDeferredPass
    {
        // 覆盖渲染前的场景视图设置
        virtual void PostRendererSubmission(
            const FMovieGraphSampleState& InSampleState,
            const FMovieGraphDefaultRenderer::FRenderTargetInitParams& InRenderTargetInitParams,
            FCanvas& InCanvas,
            const FMovieGraphDefaultRenderer::FCameraInfo& InCameraInfo) const override
        {
            // 自定义后处理逻辑
            FMovieGraphDeferredPass::PostRendererSubmission(
                InSampleState, InRenderTargetInitParams, InCanvas, InCameraInfo);
        }

        // 覆盖是否丢弃输出的判断
        virtual bool ShouldDiscardOutput(
            const TSharedRef<FSceneViewFamilyContext>& InFamily,
            const FMovieGraphDefaultRenderer::FCameraInfo& InCameraInfo) const override
        {
            return FMovieGraphDeferredPass::ShouldDiscardOutput(InFamily, InCameraInfo);
        }
    };
}
```

**创建自定义渲染节点（继承 UMovieGraphImagePassBaseNode）：**

```cpp
// 来源: Graph/Nodes/MovieGraphImagePassBaseNode.h
UCLASS(BlueprintType)
class UMyCustomRenderPassNode : public UMovieGraphImagePassBaseNode
{
    GENERATED_BODY()

public:
    // 创建对应的渲染 Pass 实例
    virtual TUniquePtr<UE::MovieGraph::Rendering::FMovieGraphImagePassBase> CreateInstance() const override
    {
        return MakeUnique<UE::MovieGraph::Rendering::FMyCustomDeferredPass>();
    }

    // 配置空间采样数
    virtual int32 GetNumSpatialSamples() const override { return 4; }

    // 禁用色调曲线以输出线性值
    virtual bool GetDisableToneCurve() const override { return true; }

    // 允许 OCIO 变换
    virtual bool GetAllowOCIO() const override { return true; }

    // 获取视图模式
    virtual EViewModeIndex GetViewModeIndex() const override { return VMI_Lit; }

    // 获取 Show Flags
    virtual FEngineShowFlags GetShowFlags() const override
    {
        FEngineShowFlags Flags = FEngineShowFlags(ESFIM_Game);
        // 自定义 show flags
        return Flags;
    }
};
```

### 进阶用法

**自定义 EXR 输出配置（多层 EXR）：**

```cpp
// 来源: MoviePipelineEXROutput.h
// 配置 EXR 写入任务
FEXRImageWriteTask ExrTask;
ExrTask.Filename = TEXT("/path/to/output.exr");
ExrTask.bOverwriteFile = true;
ExrTask.Compression = EEXRCompressionFormat::DWAB;  // 有损压缩，适合 RGB 通道
ExrTask.bMultiPart = true;  // 多层 EXR

// 为不同层设置不同压缩
ExrTask.CompressionByLayer.Add(EEXRCompressionFormat::ZIP);    // Beauty 层
ExrTask.CompressionByLayer.Add(EEXRCompressionFormat::PIZ);    // 数据层（无损）

// 添加颜色空间元数据
UE::MoviePipeline::FEXRColorSpaceMetadata ColorSpaceMetadata;
ColorSpaceMetadata.SourceName = TEXT("ACES - ACEScg");
ColorSpaceMetadata.DestinationName = TEXT("Output - sRGB");
```

**配置后处理材质 Pass：**

```cpp
// 来源: MoviePipelineDeferredPasses.h
FMoviePipelinePostProcessPass PPMConfig;
PPMConfig.bEnabled = true;
PPMConfig.Name = TEXT("CustomOutline");
PPMConfig.Material = TSoftObjectPtr<UMaterialInterface>(
    FSoftObjectPath("/Game/Materials/M_OutlinePostProcess"));
PPMConfig.bHighPrecisionOutput = true;   // 32 位输出
PPMConfig.bUseLosslessCompression = true; // 无损压缩
```

**使用图像累积系统：**

```cpp
// 来源: Graph/Renderers/MovieGraphImagePassBase.h
// 累积样本数据（在渲染线程调用）
UE::MovieGraph::Rendering::AccumulateSample_TaskThread(
    MoveTemp(PixelData),       // 像素数据
    SampleState,               // 样本状态（包含抖动偏移等）
    AccumulatorArgs            // 累积器参数
);
```

## Demo 示例

**自定义 Movie Render Graph 渲染节点：**

```cpp
// MyCustomRenderPassNode.h
#pragma once

#include "Graph/Nodes/MovieGraphImagePassBaseNode.h"
#include "MyCustomRenderPassNode.generated.h"

UCLASS(BlueprintType)
class UMyCustomRenderPassNode : public UMovieGraphImagePassBaseNode
{
    GENERATED_BODY()

public:
    UMyCustomRenderPassNode();

    // UMovieGraphImagePassBaseNode Interface
    virtual TUniquePtr<UE::MovieGraph::Rendering::FMovieGraphImagePassBase> CreateInstance() const override;
    virtual int32 GetNumSpatialSamples() const override;
    virtual bool GetDisableToneCurve() const override;
    virtual EViewModeIndex GetViewModeIndex() const override;
    virtual FEngineShowFlags GetShowFlags() const override;
    virtual void GetFormatResolveArgs(
        FMovieGraphResolveArgs& OutMergedFormatArgs,
        const FMovieGraphRenderDataIdentifier& InRenderDataIdentifier) const override;

#if WITH_EDITOR
    virtual FText GetNodeTitle(const bool bGetDescriptive = false) const override;
    virtual FSlateIcon GetIconAndTint(FLinearColor& OutColor) const override;
#endif

public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Custom Settings")
    int32 CustomSpatialSamples = 4;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Custom Settings")
    bool bCustomDisableToneCurve = true;
};
```

```cpp
// MyCustomRenderPassNode.cpp
#include "MyCustomRenderPassNode.h"
#include "Graph/Renderers/MovieGraphDeferredPass.h"

UMyCustomRenderPassNode::UMyCustomRenderPassNode()
{
}

TUniquePtr<UE::MovieGraph::Rendering::FMovieGraphImagePassBase> UMyCustomRenderPassNode::CreateInstance() const
{
    // 使用标准延迟渲染 Pass 作为基础
    return MakeUnique<UE::MovieGraph::Rendering::FMovieGraphDeferredPass>();
}

int32 UMyCustomRenderPassNode::GetNumSpatialSamples() const
{
    return CustomSpatialSamples;
}

bool UMyCustomRenderPassNode::GetDisableToneCurve() const
{
    return bCustomDisableToneCurve;
}

EViewModeIndex UMyCustomRenderPassNode::GetViewModeIndex() const
{
    return VMI_Lit;
}

FEngineShowFlags UMyCustomRenderPassNode::GetShowFlags() const
{
    FEngineShowFlags Flags = FEngineShowFlags(ESFIM_Game);
    return Flags;
}

void UMyCustomRenderPassNode::GetFormatResolveArgs(
    FMovieGraphResolveArgs& OutMergedFormatArgs,
    const FMovieGraphRenderDataIdentifier& InRenderDataIdentifier) const
{
    Super::GetFormatResolveArgs(OutMergedFormatArgs, InRenderDataIdentifier);
    OutMergedFormatArgs.FilenameArguments.Add(TEXT("custom_pass"), TEXT("MyCustomPass"));
}

#if WITH_EDITOR
FText UMyCustomRenderPassNode::GetNodeTitle(const bool bGetDescriptive) const
{
    return NSLOCTEXT("MyPlugin", "CustomPassNodeTitle", "Custom Render Pass");
}

FSlateIcon UMyCustomRenderPassNode::GetIconAndTint(FLinearColor& OutColor) const
{
    OutColor = FLinearColor::White;
    return FSlateIcon(FAppStyle::GetAppStyleSetName(), "LevelEditor.Tabs.Viewports");
}
#endif
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MovieRenderPipelineCore` | MRQ 核心框架（管线管理、任务调度、数据类型） |
| `OpenColorIO` | OCIO 色彩管理变换 |
| `ImageWriteQueue` | 异步图像写入队列 |
| `OpenExr` | EXR 文件格式读写 |
| `ConsoleVariablesEditor` | 控制台变量编辑器（MovieRenderPipelineSettings 依赖） |

无特殊依赖（仅标准 Core/Engine/Slate 等）

## 维护状态

### 近期更新

```
- ca49e32b07e3 MoviePipeline: Fixed cvars not being set correctly in some locations within MRG and MRQ after some recent changes to the engine were made. In some scenarios, cvars could be set with ECVF_SetByConstructor priority, which is no longer allowed.
- 9a264014555d MoviePipeline: Fixed a bug in the graph that would cause motion blur to break high-res tiling when Allocate History Per Tile is not enabled.
- c3860aecf660 MoviePipeline: Fixed an issue that could cause a crash in the graph when multiple output types are generated across multiple branches (regression from the recent filename disambiguation change).
```

### 维护评价

**活跃维护中** ✅

- **创建时间**：2019 年 10 月，已有约 6 年历史
- **最近更新**：近期有实质性 bug 修复，涉及 MRG（Movie Render Graph）和 MRQ 两个系统的兼容性修复、高分辨率分块渲染的运动模糊修复、多输出类型崩溃修复
- **活跃程度**：作为 UE5 影视制作管线的核心组件，由 Epic Games 持续维护，是 UE5 虚拟制片和影视渲染的关键基础设施
- **已知限制**：
  - `EnabledByDefault=false`，需要在项目设置中手动启用
  - 路径追踪器的降噪需要额外的降噪器插件
  - 全景渲染的 `bPageToSystemMemory` 会显著增加渲染时间
  - OCIO 功能仅在桌面平台可用
- **推荐使用**：强烈推荐。这是 UE5 中进行高质量离线渲染的官方标准方案，广泛应用于虚拟制片、建筑可视化、产品渲染等领域

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MovieScene/MovieRenderPipeline)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/rendering-high-quality-frames-with-movie-render-queue-in-unreal-engine/)