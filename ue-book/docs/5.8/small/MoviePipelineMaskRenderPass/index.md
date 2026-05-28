# Movie Render Queue Additional Render Passes

> Additional render passes for the Movie Render Queue. This currently includes the ObjectId pass (Editor Only) which generates object mattes with some limitations (using the Cryptomatte specification), and a Panoramic pass with better Sequencer integration than the Panoramic Capture plugin.

| 属性 | 值 |
|---|---|
| 中文名 | 额外渲染通道 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `MoviePipelineMaskRenderPass` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/MoviePipelineMaskRenderPass) | |

## 用途

本插件为 Movie Render Queue（MRQ）提供两种额外的渲染通道：

1. **Object ID Pass（对象 ID 通道）**：基于 HitProxy 生成符合 Cryptomatte 规范的对象遮罩（matte），用于后期合成时精确抠取特定对象、材质、Actor 或文件夹。支持多种分组方式（按材质、Actor、文件夹层级、Actor 层等）。该功能仅在编辑器中可用。
2. **Panoramic Pass（全景通道）**：生成等距矩形投影（equirectangular projection）的全景图像，支持立体声（top/bottom）。相比独立的 Panoramic Capture 插件，它与 Sequencer 的集成更紧密，支持 TAA、Lumen 等时序效果。

**为什么存在**：MRQ 的核心只提供标准的延迟渲染通道。当你需要从电影管线输出 Cryptomatte 遮罩用于合成（如 Nuke、DaVinci Resolve），或需要渲染 360° 全景视频用于 VR 回放时，就需要这个插件。

## 使用场景

- 你用 MRQ 渲染过场动画，后期需要在 Nuke/After Effects 中逐对象抠图 → 添加 ObjectId 通道
- 你需要为不同材质、Actor 或文件夹分别生成遮罩层 → 配置 `IdType` 选择分组方式
- 你要渲染 VR 全景视频或 360° 漫游预览 → 添加 Panoramic 通道
- 你需要立体全景渲染用于 VR 头显播放 → Panoramic 通道支持 stereo 模式
- 你想用 Cryptomatte 标准确保与主流合成软件的兼容性 → ObjectId 通道原生支持 Cryptomatte 元数据

**前置条件**：必须先启用 `MovieRenderPipeline` 和 `ActorLayerUtilities` 插件。

## 蓝图用法

### 核心节点 — Object ID 通道

| 属性/函数 | 说明 | 所在类 |
|---|---|---|
| `IdType` | 对象分组方式：Full / Material / Actor / ActorWithHierarchy / Folder / Layer | `UMoviePipelineObjectIdRenderPass` |
| `bIncludeTranslucentObjects` | 是否在遮罩中包含半透明对象（作为不透明层渲染） | `UMoviePipelineObjectIdRenderPass` |

### 核心节点 — 全景通道

| 属性/函数 | 说明 | 所在类 |
|---|---|---|
| `NumHorizontalSteps` | 水平方向拆分的渲染步数（越高畸变越小，渲染越慢） | `UMoviePipelinePanoramicPass` |
| `NumVerticalSteps` | 垂直方向拆分的渲染步数 | `UMoviePipelinePanoramicPass` |
| `bFollowCameraOrientation` | 是否跟随相机的俯仰/偏航/滚转，否则只使用位置 | `UMoviePipelinePanoramicPass` |
| `Filter` | 混合滤波类型（Bilinear 最快，采样 2×2 像素） | `UMoviePipelinePanoramicPass` |
| `HorzFieldOfView` | 覆盖水平视场角（高级，0 为自动） | `UMoviePipelinePanoramicPass` |
| `VertFieldOfView` | 覆盖垂直视场角（高级，0 为自动） | `UMoviePipelinePanoramicPass` |
| `bAllocateHistoryPerPane` | 是否为每个 Pane 分配独立的渲染历史（启用 TAA/Lumen 等时序效果，但消耗大量内存） | `UMoviePipelinePanoramicPass` |
| `bPageToSystemMemory` | 是否将持久化 GPU 数据镜像到系统内存（支持更高分辨率，但增加渲染时间） | `UMoviePipelinePanoramicPass` |

### 核心节点 — Graph ObjectId 节点（新版渲染图）

| 属性/函数 | 说明 | 所在类 |
|---|---|---|
| `SpatialSampleCount` | 空间采样数（不使用时间亚采样的多重采样） | `UMovieGraphObjectIdNode` |
| `IdType` | 对象分组方式 | `UMovieGraphObjectIdNode` |
| `bIncludeTranslucentObjects` | 是否包含半透明对象 | `UMovieGraphObjectIdNode` |

### 使用示例（蓝图描述）

**添加 ObjectId 通道到 MRQ 队列**：
1. 在 Movie Pipeline 配置资产中，点击 "Add Render Pass" → 选择 "Object Ids (Limited)"
2. 设置 `IdType` 为所需分组方式（如 `Material` 将按材质名合并遮罩）
3. 设置 `bIncludeTranslucentObjects` 是否包含半透明对象
4. 渲染后输出包含 Cryptomatte 元数据的 EXR 文件，可在 Nuke 中通过 Cryptomatte 节点读取

**添加全景通道到 MRQ 队列**：
1. 在 Movie Pipeline 配置资产中，点击 "Add Render Pass" → 选择 "Panoramic Rendering"
2. 设置 `NumHorizontalSteps`（推荐 8-16）和 `NumVerticalSteps`（推荐 4-8）
3. 勾选 `bFollowCameraOrientation` 以使用 Sequencer 中相机的朝向
4. 渲染输出为等距矩形投影的全景图像

## C++ 用法

### 头文件引入

```cpp
#include "MoviePipelinePanoramicPass.h"
#include "MoviePipelineObjectIdPass.h"
#include "MoviePipelineObjectIdUtils.h"
#include "Graph/MovieGraphObjectIdNode.h"
```

### 基本用法 — 配置 Object ID 通道

在 C++ 中以编程方式创建和配置 Object ID 通道：

```cpp
// 创建 Object ID 通道实例
UMoviePipelineObjectIdRenderPass* ObjectIdPass = NewObject<UMoviePipelineObjectIdRenderPass>();

// 设置分组类型为按材质分组
ObjectIdPass->IdType = EMoviePipelineObjectIdPassIdType::Material;

// 包含半透明对象（作为不透明层渲染）
ObjectIdPass->bIncludeTranslucentObjects = true;
```

### 基本用法 — 配置全景通道

```cpp
// 创建全景通道实例
UMoviePipelinePanoramicPass* PanoramicPass = NewObject<UMoviePipelinePanoramicPass>();

// 水平 12 步，垂直 6 步
PanoramicPass->NumHorizontalSteps = 12;
PanoramicPass->NumVerticalSteps = 6;

// 跟随相机朝向
PanoramicPass->bFollowCameraOrientation = true;

// 使用双线性滤波混合（最快）
PanoramicPass->Filter = EMoviePipelinePanoramicFilterType::Bilinear;

// 启用每个 Pane 独立历史（支持 TAA/Lumen）
PanoramicPass->bAllocateHistoryPerPane = true;
```

### 进阶用法 — 自定义 ObjectId 分组逻辑

`EMoviePipelineObjectIdPassIdType` 枚举提供了六种分组模式，适用于不同后期合成需求：

```cpp
// Full: 最高精度 — 每个 Folder/Actor/Component/Material/Section 唯一标识
EMoviePipelineObjectIdPassIdType::Full;

// Material: 按材质名称合并（不同对象共享相同材质则合并为同一遮罩）
EMoviePipelineObjectIdPassIdType::Material;

// Actor: 按 Actor 名称合并（忽略文件夹层级）
EMoviePipelineObjectIdPassIdType::Actor;

// ActorWithHierarchy: 按 Actor 名称 + 文件夹路径合并（同名 Actor 在不同文件夹中不会合并）
EMoviePipelineObjectIdPassIdType::ActorWithHierarchy;

// Folder: 按文件夹路径合并（World Outliner 中同一文件夹下所有 Actor 合并）
EMoviePipelineObjectIdPassIdType::Folder;

// Layer: 按 Actor 所在的第一个 Layer 合并
EMoviePipelineObjectIdPassIdType::Layer;
```

### 进阶用法 — Graph 节点中的 Object ID

在新的 Movie Graph 渲染图系统中，使用 `UMovieGraphObjectIdNode`：

```cpp
// 在渲染图中创建 ObjectId 节点
UMovieGraphObjectIdNode* ObjectIdNode = NewObject<UMovieGraphObjectIdNode>();

// 启用属性覆盖
ObjectIdNode->bOverride_SpatialSampleCount = 1;
ObjectIdNode->bOverride_IdType = 1;
ObjectIdNode->bOverride_bIncludeTranslucentObjects = 1;

// 配置参数
ObjectIdNode->SpatialSampleCount = 4;  // 4 次空间采样
ObjectIdNode->IdType = EMoviePipelineObjectIdPassIdType::ActorWithHierarchy;
ObjectIdNode->bIncludeTranslucentObjects = false;
```

## Demo 示例

以下示例展示如何在 C++ 中以编程方式向 MRQ 管线添加 Object ID 和全景通道：

```cpp
// MyMoviePipelineExtensions.h
#pragma once

#include "CoreMinimal.h"

class FMyMoviePipelineExtensions
{
public:
    /** 向给定管线配置添加 Object ID 通道 */
    static void AddObjectIdPass(class UMoviePipelinePrimaryConfig* InConfig);

    /** 向给定管线配置添加全景通道 */
    static void AddPanoramicPass(class UMoviePipelinePrimaryConfig* InConfig);
};
```

```cpp
// MyMoviePipelineExtensions.cpp
#include "MyMoviePipelineExtensions.h"

#include "MoviePipelinePrimaryConfig.h"
#include "MoviePipelineObjectIdPass.h"
#include "MoviePipelinePanoramicPass.h"
#include "MoviePipelineObjectIdUtils.h"

void FMyMoviePipelineExtensions::AddObjectIdPass(UMoviePipelinePrimaryConfig* InConfig)
{
    if (!InConfig)
    {
        return;
    }

    // 创建 Object ID 通道
    UMoviePipelineObjectIdRenderPass* ObjectIdPass = InConfig->FindOrAddSettingByClass<UMoviePipelineObjectIdRenderPass>();

    // 按 Actor 层级 + 文件夹路径分组
    ObjectIdPass->IdType = EMoviePipelineObjectIdPassIdType::ActorWithHierarchy;
    ObjectIdPass->bIncludeTranslucentObjects = false;
}

void FMyMoviePipelineExtensions::AddPanoramicPass(UMoviePipelinePrimaryConfig* InConfig)
{
    if (!InConfig)
    {
        return;
    }

    // 创建全景通道
    UMoviePipelinePanoramicPass* PanoramicPass = InConfig->FindOrAddSettingByClass<UMoviePipelinePanoramicPass>();

    // 配置全景参数
    PanoramicPass->NumHorizontalSteps = 12;
    PanoramicPass->NumVerticalSteps = 6;
    PanoramicPass->bFollowCameraOrientation = true;
    PanoramicPass->Filter = EMoviePipelinePanoramicFilterType::Bilinear;
    PanoramicPass->bAllocateHistoryPerPane = true;
    PanoramicPass->bPageToSystemMemory = false;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MovieRenderPipeline` | MRQ 核心管线，提供基础渲染通道和累积器框架 |
| `ActorLayerUtilities` | Actor 层工具，用于 ObjectId 的 Layer 分组模式 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `66bd9c1e` | MoviePipeline: Speculative fix for a rare crash (likely due to a data race) with Object IDs in MRG. | 修复 Object ID 在渲染图中罕见的数据竞争崩溃 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到 UE_LOGF 格式 |
| 2026-01-29 | `fb527471` | Eliminate IsInverted and associated defines given that the assumption is so ingrained in the engine | 移除 IsInverted 及相关宏定义 |
| 2025-10-29 | `cb2d83fb` | MoviePipeline: Updated spatial sampling in the graph so it only affects the last 5 warm-up frames. | 优化图中空间采样仅影响最后 5 帧预热 |
| 2025-10-10 | `e3bbc8de` | MoviePipeline: Fixed a bug in the Object ID implementation that caused the "Include Translucent Objects" | 修复 Object ID 中包含半透明对象的 bug |

### 维护评价

- **创建时间**：2020 年 9 月，已约 6 年历史
- **仍在活跃维护**：最近一次更新（2026-04-30）距今仅数月，持续有功能修复和优化
- **Beta 状态**：`IsBetaVersion=true`，说明 Epic 仍认为该功能未完全稳定，API 可能在后续版本中变动
- **未默认启用**：`EnabledByDefault=false`，需要手动在插件设置中启用
- **注意事项**：Object ID 通道依赖编辑器的 HitProxy 系统，仅在编辑器中可用（UncookedOnly 模块类型）；全景通道的立体模式（bStereo）相关属性目前被注释掉，属于未完成功能
- **推荐使用**：**推荐**。对于需要 Cryptomatte 遮罩或全景渲染的 MRQ 用户，这是唯一的官方解决方案。虽然是 Beta，但已经过多年实际使用验证。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/MoviePipelineMaskRenderPass)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/MoviePipelineMaskRenderPass/Tests)（如果存在）