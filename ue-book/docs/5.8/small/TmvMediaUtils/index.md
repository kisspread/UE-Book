# Tiled Mipmap Video Utilities

> Additional tools for the tiled-mipmap video (TMV) framework.
Implements Movie Render Graph (MRG) integration.

| 属性 | 值 |
|---|---|
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MovieRenderPipelineTmvEncoder` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-18 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/TmvMediaUtils) | |

## 用途

TmvMediaUtils 插件是 Tiled Mipmap Video (TMV) 框架的扩展工具集。其核心功能是将 TMV 编码能力集成到 Unreal Engine 的 **Movie Render Graph (MRG)** 系统中。它解决的问题是：如何在使用 MRG 进行高质量离线渲染时，将渲染结果直接输出为 TMV 格式（包括 APV1 图像序列或 TMV 容器文件），从而利用 TMV 的分块和多级渐进纹理特性，为后续的流媒体传输或高效加载做准备。

## 使用场景

- 你正在使用 **Movie Render Graph** 进行电影级质量的视频渲染，并希望输出为 **TMV 格式** 以便于后续的流媒体处理或高效加载。
- 你需要将渲染帧输出为 **APV1 图像序列**，用于逐帧分析或作为其他处理流程的输入。
- 你的渲染管线需要集成 **OCIO 颜色管理**，并希望在 TMV 编码节点中正确处理颜色空间转换。

## 蓝图用法

该插件的核心是一个 Movie Render Graph 节点，可在蓝图中配置和使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Tmv Encoder` | Movie Render Graph 的输出节点，用于将渲染帧编码为 TMV 或 APV1 格式。 | `UMovieGraphTmvEncoderNode` |

### 使用示例（蓝图描述）

1.  在你的 Movie Render Graph 资产中，右键点击并搜索 “Tmv Encoder” 节点，将其添加到图中。
2.  将该节点连接到渲染管线的输出端。
3.  在节点的细节面板中，配置 `Output Type` 属性：
    -   选择 `APV1 Image Sequence` 将输出一系列单独的 `.apv1` 文件。
    -   选择 `TMV Video File` 将输出一个单一的 `.tmv` 容器文件。
4.  根据需要配置其他编码选项（如 OCIO 配置）。

## C++ 用法

### 头文件引入

```cpp
#include "Graph/MovieGraphTmvEncoderNode.h"
```

### 基本用法

在 C++ 中，你可以通过 Movie Render Graph 的 API 来创建和配置 TMV 编码器节点。

```cpp
// 假设你已经有一个 UMovieGraphPipeline 实例 (Pipeline)
// 以及一个 UMovieGraphEvaluatedConfig 实例 (EvaluatedConfig)

// 创建 TMV 编码器节点实例
UMovieGraphTmvEncoderNode* TmvEncoderNode = NewObject<UMovieGraphTmvEncoderNode>();

// 设置输出类型为 TMV 视频文件
TmvEncoderNode->OutputType = ETmvEncoderNodeOutputType::TmvVideoFile;

// 将节点添加到评估配置的某个分支中（例如 “Final” 分支）
FName BranchName = TEXT(“Final”);
TArray<UMovieGraphSettingNode*>& BranchNodes = EvaluatedConfig->GetBranchSettings(BranchName);
BranchNodes.Add(TmvEncoderNode);
```

### 进阶用法

节点实现了 `IMovieGraphEvaluationNodeInjector` 接口，允许在评估过程中动态注入其他设置节点（例如 OCIO 节点）。通常，你不需要直接调用此接口，MRG 系统会自动处理。但了解其存在有助于理解节点如何与颜色管理管线集成。

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何在自定义的 Movie Render Graph 设置中添加并配置 TMV 编码器节点。

**MyTmvRenderSettings.h**
```cpp
// MyTmvRenderSettings.h
#pragma once

#include “MoviePipelineSetting.h”
#include “MyTmvRenderSettings.generated.h”

class UMovieGraphTmvEncoderNode;

UCLASS(BlueprintType)
class UMyTmvRenderSettings : public UMoviePipelineSetting
{
    GENERATED_BODY()

public:
    UMyTmvRenderSettings();

    // 当此设置被添加到管线时调用
    virtual void SetupForPipelineImpl(UMoviePipeline* InPipeline) override;

private:
    UPROPERTY()
    TObjectPtr<UMovieGraphTmvEncoderNode> TmvEncoderNode;
};
```

**MyTmvRenderSettings.cpp**
```cpp
// MyTmvRenderSettings.cpp
#include “MyTmvRenderSettings.h”
#include “Graph/MovieGraphTmvEncoderNode.h”
#include “MoviePipeline.h”
#include “MovieGraphPipeline.h”

UMyTmvRenderSettings::UMyTmvRenderSettings()
{
    // 设置此设置的显示名称
    DisplayName = FText::FromString(“Custom TMV Output”);
}

void UMyTmvRenderSettings::SetupForPipelineImpl(UMoviePipeline* InPipeline)
{
    Super::SetupForPipelineImpl(InPipeline);

    // 检查是否是 Movie Graph Pipeline
    UMovieGraphPipeline* GraphPipeline = Cast<UMovieGraphPipeline>(InPipeline);
    if (!GraphPipeline)
    {
        return;
    }

    // 获取或创建 TMV 编码器节点
    if (!TmvEncoderNode)
    {
        TmvEncoderNode = NewObject<UMovieGraphTmvEncoderNode>(this);
    }

    // 配置节点：输出为 APV1 图像序列
    TmvEncoderNode->OutputType = ETmvEncoderNodeOutputType::Apv1ImageSequence;

    // 将节点注入到管线的评估配置中
    // 注意：实际注入逻辑可能更复杂，这里仅为演示
    UMovieGraphEvaluatedConfig* EvaluatedConfig = GraphPipeline->GetEvaluationConfig();
    if (EvaluatedConfig)
    {
        // 假设我们注入到默认分支
        const FName DefaultBranch = NAME_None;
        TArray<UMovieGraphSettingNode*>& Nodes = EvaluatedConfig->GetBranchSettings(DefaultBranch);
        Nodes.Add(TmvEncoderNode);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ApvMedia` | TMV 框架的核心模块，提供 APV 编解码器和 TMV 容器格式的基础支持。 |

## 维护状态

### 近期更新

- 2026-04-24 c7065a2f [Tmv Media] Transcoding Commandlet
- 2026-04-23 efcad028 HDR: Fix HDR normalization factor across media causing incorrect brightness levels going from/to the
- 2026-04-22 323ab3ea [TmvMediaUtils] Addressing Ux feedback for the MRG node

### 维护评价

该插件创建于 **2026年4月18日**，是一个非常新的插件。从最近的提交记录看，它正处于**活跃开发**阶段，最近一周内有多次提交，内容包括功能添加（转码命令行工具）、关键问题修复（HDR 亮度）以及用户体验优化。由于标记为 `IsBetaVersion=true` 且 `EnabledByDefault=false`，表明它仍处于实验性阶段，API 和功能可能会发生变化。**推荐在实验性项目或需要前沿 TMV/MRG 集成的场景中试用**，但不建议用于追求稳定性的生产环境。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/TmvMediaUtils)
- [官方文档]() (无)
- [测试用例]() (未在提供的信息中明确，可能位于 `Engine/Tests/` 目录下)