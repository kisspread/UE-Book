# Movie Render Queue

> Advanced movie rendering pipeline for use in creating rendered cinematics or other multi-media creation.

| 属性 | 值 |
|---|---|
| 中文名 | 影片渲染队列 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `MovieRenderPipelineCore` (Runtime), `MovieRenderPipelineEditor` (Runtime), `MovieRenderPipelineMP4Encoder` (Runtime), `MovieRenderPipelineRenderPasses` (Runtime), `MovieRenderPipelineSettings` (Runtime), `UEOpenExrRTTI` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-30 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/MovieRenderPipeline) | |

## 用途

Movie Render Queue（MRQ）是 UE5 中用于**离线渲染高质量影片序列**的核心系统。它解决的核心问题是：在编辑器中预览的实时渲染效果无法满足电影级输出要求——分辨率受限于 GPU 显存、抗锯齿质量不够、缺少运动模糊等高级效果的精确控制。

MRQ 提供了一套完整的渲染管线，支持：

- **多通道图像渲染**：延迟渲染（Deferred）、路径追踪器（Path Tracer）、全景渲染（Panoramic）
- **高分辨率分块渲染（Tiling）**：突破 GPU 显存限制，将画面分块逐片渲染后拼合
- **多采样抗锯齿**：空间采样 + 时间采样，实现超高质量抗锯齿
- **降噪器集成**：空间/时空降噪器插件支持
- **多格式输出**：EXR（单层/多层/多部件）、PNG、JPG、BMP、WAV 音频
- **OCIO 色彩管理**：支持 OpenColorIO 变换，满足影视色彩流程需求
- **后处理材质通道**：可自定义后处理材质输出（如深度、法线、ID 等）
- **模板裁剪层（Stencil Layers）**：基于 Actor Layer 或 Data Layer 分层渲染

该插件需要手动启用（`EnabledByDefault: false`），因为它是专业影视/虚拟制作工具，面向需要离线渲染输出的用户。

## 使用场景

- 你需要将 Sequencer 中的过场动画渲染为 4K+ 高质量影片序列 → 使用 MRQ 的 Deferred 或 Path Tracer 渲染通道
- 你需要输出带多通道（Beauty、Depth、Object ID、Motion Vector）的 EXR 文件给后期合成软件 → 使用多层 EXR 输出节点
- 你需要渲染超大分辨率（8K+）的画面但 GPU 显存不够 → 启用高分辨率分块渲染
- 你需要路径追踪器渲染物理精确的光照并降噪 → 使用 Path Tracer 节点并启用降噪器
- 你需要输出符合影视色彩流程的线性 EXR → 禁用 Tone Curve + 配置 OCIO 变换
- 你需要按 Actor Layer 分层渲染用于合成 → 使用模板裁剪层功能
- 你需要渲染全景图像用于 VR/环境贴图 → 使用 Deferred Panoramic 节点

## 蓝图用法

MRQ 的蓝图接口主要通过 Movie Render Graph（新系统）的节点和设置进行配置，核心功能通过渲染通道节点和输出节点暴露。

### 核心渲染通道节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| 延迟渲染通道 | 标准延迟渲染，支持 TAA/TSR/MSAA | `UMovieGraphDeferredRenderPassNode` |
| 路径追踪器通道 | 物理精确的路径追踪渲染，支持降噪 | `UMovieGraphPathTracerRenderPassNode` |
| 全景渲染通道 | 多视角全景渲染（用于 VR/环境贴图） | `UMovieGraphDeferredPanoramicNode` |

### 核心输出节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| EXR 单层输出 | 输出单层 EXR 文件 | `UMovieGraphImageSequenceOutputNode_EXR` |
| EXR 多层输出 | 输出多层 EXR 文件（所有通道合一） | `UMovieGraphImageSequenceOutputNode_MultiLayerEXR` |
| PNG 序列输出 | 输出 8-bit PNG 图片序列 | `UMovieGraphImageSequenceOutputNode_PNG` |
| BMP/JPG 序列输出 | 输出 BMP/JPG 格式 | `UMoviePipelineImageSequenceOutput_BMP` / `_JPG` |
| WAV 音频输出 | 输出 WAV 音频文件 | `UMoviePipelineWaveOutput` |

### 旧版渲染通道（MRQ 传统系统）

| 节点 | 说明 | 所在类 |
|---|---|---|
| 延迟渲染（Lit） | 标准延迟渲染 | `UMoviePipelineDeferredPassBase` |
| 无光照（Unlit） | 无光照模式 | `UMoviePipelineDeferredPass_Unlit` |
| 仅细节光照 | 细节光照模式 | `UMoviePipelineDeferredPass_DetailLighting` |
| 仅光照 | 光照通道 | `UMoviePipelineDeferredPass_LightingOnly` |
| 仅反射 | 反射通道 | `UMoviePipelineDeferredPass_ReflectionsOnly` |
| 路径追踪器 | 旧版路径追踪器 | `UMoviePipelineDeferredPass_PathTracer` |

### 关键属性（Deferred Render Pass）

**采样设置**：
- `SpatialSampleCount`：每个时间采样的空间子像素抖动次数（建议配合时间采样使用）
- `AntiAliasingMethod`：抗锯齿方法（None 时 MRQ 自行处理子像素抖动）
- `bWriteAllSamples`：调试用，写出每个独立采样

**后处理设置**：
- `bDisableToneCurve`：禁用色调曲线，输出线性值（配合 OCIO 使用）
- `bAllowOCIO`：允许 OCIO 色彩变换
- `AdditionalPostProcessMaterials`：额外后处理材质通道数组

**高分辨率分块**：
- `bEnableHighResolutionTiling`：启用分块渲染
- `TileCount`：每边分块数（如 2 表示 2×2=4 块）
- `OverlapPercentage`：块间重叠百分比（0-50）
- `bAllocateHistoryPerTile`：每块分配独立历史缓存（Lumen/TAA 需要）
- `bPageToSystemMemory`：实验性功能，将历史数据暂存到系统内存

## C++ 用法

### 头文件引入

```cpp
// 延迟渲染通道
#include "MoviePipelineDeferredPasses.h"

// 路径追踪器通道
#include "MoviePipelineDeferredPasses.h"  // UMoviePipelineDeferredPass_PathTracer

// 图像序列输出
#include "MoviePipelineImageSequenceOutput.h"
#include "MoviePipelineEXROutput.h"

// Movie Graph 新系统
#include "Graph/Nodes/MovieGraphDeferredPassNode.h"
#include "Graph/Nodes/MovieGraphPathTracerPassNode.h"
#include "Graph/Nodes/MovieGraphImagePassBaseNode.h"
#include "MovieGraphImageSequenceOutputNode.h"

// 渲染器基类
#include "Graph/Renderers/MovieGraphImagePassBase.h"
#include "Graph/Renderers/MovieGraphDeferredPass.h"
```

### 基本用法：注册自定义延迟渲染通道工厂

`UMovieGraphDeferredRenderPassNode` 提供了工厂注册机制，允许插件在不创建新节点类型的情况下自定义延迟渲染行为。

```cpp
// 来源: Public/Graph/Nodes/MovieGraphDeferredPassNode.h
#include "Graph/Nodes/MovieGraphDeferredPassNode.h"

// 注册自定义通道实例工厂
void RegisterCustomDeferredPass()
{
    UMovieGraphDeferredRenderPassNode::RegisterPassInstanceFactory(
        FName("MyCustomPass"),
        [](const UMovieGraphDeferredRenderPassNode::FPassInstanceFactoryContext& InContext)
            -> TUniquePtr<UE::MovieGraph::Rendering::FMovieGraphImagePassBase>
        {
            // 在此自定义通道行为，返回 nullptr 则回退到默认
            // 可以根据 InContext.LayerData / InContext.EvaluatedConfig 决定行为
            return nullptr;
        }
    );
}

// 注销
void UnregisterCustomDeferredPass()
{
    UMovieGraphDeferredRenderPassNode::UnregisterPassInstanceFactory(FName("MyCustomPass"));
}
```

### 进阶用法：自定义图像渲染通道

继承 `UMovieGraphImagePassBaseNode` 创建自定义渲染通道：

```cpp
// 来源: Public/Graph/Nodes/MovieGraphImagePassBaseNode.h
#include "Graph/Nodes/MovieGraphImagePassBaseNode.h"

UCLASS(MinimalAPI)
class UMyCustomRenderPassNode : public UMovieGraphImagePassBaseNode
{
    GENERATED_BODY()

public:
    // 配置 Show Flags
    virtual FEngineShowFlags GetShowFlags() const override
    {
        FEngineShowFlags Flags(ESFIM_Game);
        // 自定义显示标志
        return Flags;
    }

    // 配置视图模式
    virtual EViewModeIndex GetViewModeIndex() const override
    {
        return VMI_Lit;
    }

    // 空间采样数
    virtual int32 GetNumSpatialSamples() const override { return 1; }

    // 禁用色调曲线（输出线性值）
    virtual bool GetDisableToneCurve() const override { return false; }

    // 允许 OCIO 变换
    virtual bool GetAllowOCIO() const override { return true; }

    // 允许降噪器
    virtual bool GetAllowDenoiser() const override { return true; }

    // 允许合成其他通道
    virtual bool GetAllowsCompositing() const override { return true; }

    // 创建通道实例
    virtual TUniquePtr<UE::MovieGraph::Rendering::FMovieGraphImagePassBase>
        CreateInstance() const override;

protected:
    // 每层渲染前的设置
    virtual void PreLayerRender(
        const TUniquePtr<UE::MovieGraph::Rendering::FMovieGraphImagePassBase>& InInstance,
        const FMovieGraphTraversalContext& InFrameTraversalContext,
        const FMovieGraphTimeStepData& InTimeData) override;

    // 每层渲染后的清理
    virtual void PostLayerRender(
        const TUniquePtr<UE::MovieGraph::Rendering::FMovieGraphImagePassBase>& InInstance,
        const FMovieGraphTraversalContext& InFrameTraversalContext,
        const FMovieGraphTimeStepData& InTimeData) override;
};
```

## Demo 示例

以下示例展示如何创建一个自定义的 Movie Graph 渲染通道节点：

```cpp
// MyCustomRenderPassNode.h
#pragma once

#include "Graph/Nodes/MovieGraphImagePassBaseNode.h"
#include "Graph/Renderers/MovieGraphImagePassBase.h"
#include "MyCustomRenderPassNode.generated.h"

UCLASS(MinimalAPI, BlueprintType)
class UMyCustomRenderPassNode : public UMovieGraphImagePassBaseNode
{
    GENERATED_BODY()

public:
    UMyCustomRenderPassNode();

    // --- UMovieGraphImagePassBaseNode 接口 ---

    virtual FEngineShowFlags GetShowFlags() const override;
    virtual EViewModeIndex GetViewModeIndex() const override;
    virtual TUniquePtr<UE::MovieGraph::Rendering::FMovieGraphImagePassBase>
        CreateInstance() const override;
    virtual int32 GetNumSpatialSamples() const override { return SpatialSampleCount; }
    virtual bool GetDisableToneCurve() const override { return bDisableToneCurve; }

#if WITH_EDITOR
    virtual FText GetNodeTitle(bool bGetDescriptive = false) const override;
    virtual FSlateIcon GetIconAndTint(FLinearColor& OutColor) const override;
#endif

    // --- 可配置属性 ---

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Sampling")
    int32 SpatialSampleCount = 1;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Post Processing")
    bool bDisableToneCurve = false;
};
```

```cpp
// MyCustomRenderPassNode.cpp
#include "MyCustomRenderPassNode.h"
#include "Graph/Renderers/MovieGraphImagePassBase.h"

UMyCustomRenderPassNode::UMyCustomRenderPassNode()
{
}

FEngineShowFlags UMyCustomRenderPassNode::GetShowFlags() const
{
    FEngineShowFlags Flags(ESFIM_Game);
    return Flags;
}

EViewModeIndex UMyCustomRenderPassNode::GetViewModeIndex() const
{
    return EViewModeIndex::VMI_Lit;
}

TUniquePtr<UE::MovieGraph::Rendering::FMovieGraphImagePassBase>
UMyCustomRenderPassNode::CreateInstance() const
{
    // 返回自定义的 FMovieGraphImagePassBase 子类实例
    // 或使用默认基类进行标准渲染
    return MakeUnique<UE::MovieGraph::Rendering::FMovieGraphImagePassBase>();
}

#if WITH_EDITOR
FText UMyCustomRenderPassNode::GetNodeTitle(bool bGetDescriptive) const
{
    return NSLOCTEXT("MyPlugin", "CustomPassTitle", "My Custom Render Pass");
}

FSlateIcon UMyCustomRenderPassNode::GetIconAndTint(FLinearColor& OutColor) const
{
    OutColor = FLinearColor::White;
    return FSlateIcon(FName("MovieRenderPipelineStyle"),
        "MovieRenderPipeline.Graph.Icon.RenderSequenceOutput");
}
#endif
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MovieRenderPipelineCore` | MRQ 核心框架，渲染管线、任务管理、输出合并器 |
| `ConsoleVariablesEditor` | 控制台变量编辑器集成（Settings 模块依赖） |
| `OpenExrRTTI` | OpenEXR 文件格式 RTTI 支持，用于 EXR 多层/多部件输出 |
| `OpenColorIODisplay` | OCIO 色彩管理显示扩展（延迟通道中使用） |

> 注：该插件还依赖标准模块如 `RenderCore`、`RHI`、`Renderer`、`ImageWriteQueue` 等渲染相关模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | nDisplay 场景支持 EXR 多层输出 |
| 2026-05-26 | `353f4079` | MoviePipeline: Fixed an issue with layer warm-ups in the graph that could cause some skeletal meshes | 修复 Graph 中层预热导致骨骼网格体异常的问题 |
| 2026-05-26 | `5b4aedd1` | MoviePipeline: Reverting a change made to letterboxing, which was meant to correct it when it's comb | 回退了一项关于黑边（letterboxing）的修改 |
| 2026-05-21 | `a1446fbd` | MoviePipeline: Added an "Anti Aliasing Method" property to the Basic configuration type for the Defe | 为 Deferred 通道的基础配置新增抗锯齿方法属性 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 使用 Rundown Page 设置时添加 MRQ 分析数据 |

### 维护评价

**积极维护中**。MRQ 是 Epic Games 重点维护的影视渲染基础设施，持续获得功能更新和 bug 修复。从近期提交记录看：

- ✅ **活跃度高**：最近一周内有多次功能性更新和修复
- ✅ **持续演进**：正在从传统 MRQ 系统向 Movie Render Graph（基于节点图的新系统）迁移，新旧系统并存
- ✅ **功能扩展**：持续增加新特性（nDisplay 多层 EXR、抗锯齿配置改进等）
- ⚠️ **架构复杂**：新旧系统并存增加了学习成本，建议新项目优先使用 Movie Graph 系统
- ⚠️ **实验性功能**：部分功能（如 `bPageToSystemMemory`）仍标记为实验性

**推荐使用**。对于需要高质量离线渲染输出的影视、虚拟制作、建筑可视化等项目，MRQ 是 UE5 的标准解决方案。建议从 Movie Render Graph（节点图系统）开始学习，它提供了更灵活的配置能力。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/MovieRenderPipeline)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/MovieRenderPipeline)（测试文件通常位于插件目录或 Engine/Tests/ 下）