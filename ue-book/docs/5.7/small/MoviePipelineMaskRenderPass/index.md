# Movie Render Queue Additional Render Passes

> Additional render passes for the Movie Render Queue. This currently includes the ObjectId pass (Editor Only) which generates object mattes with some limitations (using the Cryptomatte specification), and a Panoramic pass with better Sequencer integration than the Panoramic Capture plugin.

| 属性 | 值 |
|---|---|
| 分类 | Rendering |
| 默认启用 | false |
| 包含内容 | true |
| 模块 | MoviePipelineMaskRenderPass (UncookedOnly) |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/MovieScene/MoviePipelineMaskRenderPass) | |

## 用途

这个 plugin 为 Movie Render Queue (MRQ) 提供两种额外的渲染 Pass：

1. **Object ID Pass（Cryptomatte）**：为每个 Actor/材质/文件夹生成唯一颜色编码的遮罩（matte），输出为 [Cryptomatte](https://www.cryptomatte.com/) 格式的 EXR 文件。后期合成时可以精确选中任意物体进行调色、替换或遮罩操作。这是行业标准的物体遮罩方案，被 Nuke、After Effects 等合成软件广泛支持。

2. **Panoramic Pass（全景渲染）**：将场景渲染为等距矩形投影（equirectangular projection）的 360° 全景图。与旧的 Panoramic Capture 插件不同，它深度集成 Sequencer，支持时间轴动画、多通道输出、高分辨率分块渲染等 MRQ 特性。

## 使用场景

- **影视后期合成**：你需要为每个角色/物体生成精确的遮罩，在 Nuke 中做单独调色或合成 → 使用 Object ID Pass
- **VR 全景内容**：你要为 VR 头显或 YouTube 360° 视频生成全景画面 → 使用 Panoramic Pass
- **游戏场景展示**：你需要 360° 环绕展示关卡设计 → 使用 Panoramic Pass
- **批量遮罩输出**：你需要按 Actor 名称、材质或文件夹分组生成遮罩 → 使用 Object ID Pass 的不同 ID Type

## 蓝图用法

本 plugin 的渲染 Pass 通过 Movie Render Queue 设置面板添加，不需要直接操作蓝图节点。以下是相关可配置属性：

### Object ID Pass 属性

| 属性 | 类型 | 说明 | 所在类 |
|---|---|---|---|
| `IdType` | `EMoviePipelineObjectIdPassIdType` | 分组方式（Full/Material/Actor/ActorWithHierarchy/Folder/Layer） | `UMoviePipelineObjectIdRenderPass` |
| `bIncludeTranslucentObjects` | `bool` | 是否包含半透明物体（会以不透明层形式输出） | `UMoviePipelineObjectIdRenderPass` |

### Panoramic Pass 属性

| 属性 | 类型 | 说明 | 所在类 |
|---|---|---|---|
| `NumHorizontalSteps` | `int32` | 水平方向渲染步数（越高越少畸变，渲染越慢） | `UMoviePipelinePanoramicPass` |
| `NumVerticalSteps` | `int32` | 垂直方向渲染步数 | `UMoviePipelinePanoramicPass` |
| `bFollowCameraOrientation` | `bool` | 是否跟随相机朝向（否则仅使用位置） | `UMoviePipelinePanoramicPass` |
| `Filter` | `EMoviePipelinePanoramicFilterType` | 混合滤波器（Bilinear 最快） | `UMoviePipelinePanoramicPass` |
| `HorzFieldOfView` | `float` | 水平 FOV 覆盖（高级，0=自动） | `UMoviePipelinePanoramicPass` |
| `VertFieldOfView` | `float` | 垂直 FOV 覆盖（高级，0=自动） | `UMoviePipelinePanoramicPass` |
| `bAllocateHistoryPerPane` | `bool` | 每个 Pane 独立分配场景历史（启用 TAA/Lumen 等，内存开销大） | `UMoviePipelinePanoramicPass` |
| `bPageToSystemMemory` | `bool` | 将 GPU 数据镜像到系统内存（支持更高分辨率） | `UMoviePipelinePanoramicPass` |

### ID Type 详细说明

| 值 | 分组逻辑 |
|---|---|
| `Full` | 最精细：每个 Folder/Actor/Component/Material/Section 组合独立 |
| `Material` | 按材质名分组，使用相同材质的不同物体会合并 |
| `Actor` | 按 Actor 名称分组，同名 Actor 合并 |
| `ActorWithHierarchy` | 按 Actor 名称 + 文件夹层级分组，不同文件夹中的同名 Actor 不合并 |
| `Folder` | 按 World Outliner 文件夹层级分组 |
| `Layer` | 按 Actor Layer 分组（取 `AActor::Layers` 的第一个） |

### 使用示例（蓝图描述）

**添加 Object ID Pass：**
1. 打开 Movie Render Queue 设置（`CineCameraActor` → Sequencer → Movie Render Queue）
2. 在设置中点击 `+` → `Render Pass` → 选择 `Object Ids (Limited)`
3. 展开 Pass 设置，选择 `Id Type`（如 `Full`）
4. 勾选 `Include Translucent Objects`（如果需要半透明物体遮罩）
5. 输出格式建议选择 EXR（自动包含 Cryptomatte 元数据）

**添加 Panoramic Pass：**
1. 在 Movie Render Queue 设置中点击 `+` → `Render Pass` → 选择 `Panoramic Rendering`
2. 设置 `Num Horizontal Steps`（推荐 6-12，360° 分成多少步）
3. 设置 `Num Vertical Steps`（推荐 3-6）
4. 勾选 `Follow Camera Orientation`（如果需要相机朝向影响全景方向）
5. 输出分辨率会自动根据 Pane 数量计算

## C++ 用法

### 头文件引入

```cpp
#include "MoviePipelineObjectIdPass.h"
#include "MoviePipelinePanoramicPass.h"
```

### 基本用法

Object ID Pass 和 Panoramic Pass 都是 `UMoviePipelineImagePassBase` 的子类，通过 Movie Render Queue 的设置系统注册使用。在 C++ 中通常不需要直接实例化它们，而是通过配置系统添加：

```cpp
// 获取或创建 Movie Pipeline 设置
UMoviePipelinePrimaryConfig* Config = ...;

// 添加 Object ID Pass 作为渲染 Pass
UMoviePipelineObjectIdRenderPass* ObjectIdPass = NewObject<UMoviePipelineObjectIdRenderPass>(Config);
ObjectIdPass->IdType = EMoviePipelineObjectIdPassIdType::Full;
ObjectIdPass->bIncludeTranslucentObjects = false;
Config->FindOrAddSettingByClass(UMoviePipelineObjectIdRenderPass::StaticClass());
```

### ID Type 配置示例

```cpp
// 按材质分组 — 适合材质级调色
ObjectIdPass->IdType = EMoviePipelineObjectIdPassIdType::Material;

// 按 Actor + 文件夹层级分组 — 适合结构化场景
ObjectIdPass->IdType = EMoviePipelineObjectIdPassIdType::ActorWithHierarchy;

// 按文件夹分组 — 适合大型场景批量遮罩
ObjectIdPass->IdType = EMoviePipelineObjectIdPassIdType::Folder;
```

### Movie Graph 用法

UE5 的 Movie Render Graph (MRG) 系统提供了节点化的渲染配置方式。Object ID Pass 对应的节点是 `UMovieGraphObjectIdNode`：

```cpp
// 创建 Object ID 节点
UMovieGraphObjectIdNode* ObjectIdNode = NewObject<UMovieGraphObjectIdNode>(Graph);
ObjectIdNode->IdType = EMoviePipelineObjectIdPassIdType::Full;
ObjectIdNode->bIncludeTranslucentObjects = true;
ObjectIdNode->SpatialSampleCount = 4; // 空间采样数（抗锯齿）

// 覆盖属性需要先启用 Override toggle
ObjectIdNode->bOverride_IdType = true;
ObjectIdNode->bOverride_bIncludeTranslucentObjects = true;
ObjectIdNode->bOverride_SpatialSampleCount = true;
```

## Demo 示例

### 最小 Movie Render Graph 配置

以下展示如何通过 C++ 配置一个包含 Object ID Pass 的 Movie Render Graph：

```cpp
// MyRenderGraphSetup.h
#pragma once
#include "CoreMinimal.h"

// MyRenderGraphSetup.cpp
#include "MoviePipelineQueue.h"
#include "MoviePipelinePrimaryConfig.h"
#include "MoviePipelineObjectIdPass.h"
#include "Graph/MovieGraphObjectIdNode.h"

void SetupRenderWithObjectIdPass()
{
    // 1. 创建渲染队列和 Job
    UMoviePipelineQueue* Queue = NewObject<UMoviePipelineQueue>();
    UMoviePipelineExecutorJob* Job = Queue->AllocateNewJob(UMoviePipelineExecutorJob::StaticClass());
    
    // 2. 配置输出格式为 EXR（Cryptomatte 需要）
    UMoviePipelinePrimaryConfig* Config = Job->GetConfiguration();
    UMoviePipelineOutputSetting* OutputSetting = Config->FindOrAddSettingByClass<UMoviePipelineOutputSetting>();
    OutputSetting->OutputFormat = TEXT("exr");
    
    // 3. 添加 Object ID Pass
    UMoviePipelineObjectIdRenderPass* ObjectIdPass = Config->FindOrAddSettingByClass<UMoviePipelineObjectIdRenderPass>();
    ObjectIdPass->IdType = EMoviePipelineObjectIdPassIdType::Full;
    ObjectIdPass->bIncludeTranslucentObjects = false;
    
    // 4. 添加延迟渲染器（Object ID 需要 HitProxy）
    Config->FindOrAddSettingByClass(UMoviePipelineDeferredPass_Base::StaticClass());
}
```

### Build.cs 依赖

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "MoviePipelineMaskRenderPass",
    "MovieRenderPipelineCore"
});
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MovieRenderPipelineCore` | MRQ 核心框架（管线管理、输出合并） |
| `MovieRenderPipelineRenderPasses` | 基础渲染 Pass（延迟渲染、路径追踪） |
| `RenderCore` | 渲染核心（RHI 命令、着色器） |
| `RHI` | 渲染硬件接口 |
| `ActorLayerUtilities` | Actor Layer 查询（Layer ID Type 使用） |
| `OpenColorIO` | OCIO 色彩管理 |
| `SlateCore` | UI 框架（编辑器设置面板） |

插件依赖（.uplugin 中声明）：
- `MovieRenderPipeline` — MRQ 主插件
- `ActorLayerUtilities` — Actor Layer 功能

## 维护状态

### 近期更新

| 日期 | Hash | 说明 |
|---|---|---|
| 2025-10-10 | `5f7ae42` | **修复 Object ID "Include Translucent Objects" 属性不生效的 bug**，并支持该属性在不同层之间独立设置。 |
| 2025-09-03 | `ae546c5` | MRG 文件名消歧义改进：新增 `PPM File Name Format` 属性到 Deferred 和 Path Traced 渲染器节点。 |
| 2025-09-03 | `6352cab` | **修复 MRG Metadata 问题**：多层 EXR 文件的 per-camera metadata 缺失和 key 冲突。重命名元数据格式为 `unreal/layerData/<layerName>/<key>`。 |

### 维护评价

- **创建时间**：2020 年 9 月，已超过 5 年
- **Beta 状态**：`.uplugin` 中 `IsBetaVersion: true`、`EnabledByDefault: false`，需要手动启用
- **活跃度**：2025 年 10 月仍有实质性 bug 修复和功能改进，属于活跃维护
- **模块类型**：`UncookedOnly` — 仅在编辑器/开发环境加载，不会被打包到发布版本中
- **推荐**：✅ 推荐使用。Object ID Pass 是 UE5 中生成 Cryptomatte 遮罩的唯一官方方案；Panoramic Pass 是最完善的全景渲染方案。虽然是 Beta 状态，但已经相当成熟。
- **注意事项**：
  - Object ID Pass 仅在编辑器中可用（依赖 HitProxy 系统）
  - 不支持 Screen Percentage 缩放（会混合不同物体的 ID）
  - 半透明物体以不透明形式输出（技术限制）
  - Panoramic Pass 的立体渲染（`bStereo`）功能当前被注释掉，未暴露为 UPROPERTY

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/MovieScene/MoviePipelineMaskRenderPass)
- [官方文档]()（无）
- 测试用例：本 plugin 无独立测试文件
