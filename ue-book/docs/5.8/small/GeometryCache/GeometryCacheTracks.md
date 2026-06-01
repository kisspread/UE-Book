# Geometry Cache

> Support for distilled Geometry animations

| 属性 | 值 |
|---|---|
| 中文名 | 几何缓存 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `GeometryCache` (Runtime), `GeometryCacheEd` (Runtime), `GeometryCacheSequencer` (Runtime), `GeometryCacheStreamer` (Runtime), `GeometryCacheTracks` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-01-26 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeometryCache) | |

## 用途

该插件用于支持**几何缓存动画**的导入、播放和序列化。它本质上是一个**顶点动画**的容器和播放器，用于播放预先烘焙好的（Distilled）顶点位置数据序列，通常从其他DCC软件（如Maya、Blender）或物理模拟中导出为Alembic（.abc）格式。与传统骨骼动画不同，几何缓存记录的是每一帧网格的精确顶点位置，因此非常适合表现布料、流体、面部捕捉等复杂的、非拓扑结构变化的动画。

## 使用场景

-   你从Maya或Blender中导出了一段使用布料模拟或流体模拟生成的动画，并希望将其导入UE中作为完整的网格序列播放。
-   你有一个复杂的面部捕捉表演数据，需要以每帧独立网格的形式在UE中重现。
-   你需要将一段预先计算好的刚体破碎动画以网格序列的方式集成到项目中，而不是实时物理模拟。
-   你需要在Sequencer（定序器）中精确控制一段几何缓存动画的播放时间、速度和混合。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Geometry Cache Asset` (属性) | 指定要播放的几何缓存资产（`UGeometryCache`） | `FMovieSceneGeometryCacheParams` |
| `Play Rate` (属性) | 设置几何缓存动画的播放速率 | `FMovieSceneGeometryCacheParams` |
| `Reverse` (属性) | 是否反向播放动画 | `FMovieSceneGeometryCacheParams` |
| `Add New Animation` | 向几何缓存轨道添加一个新的动画片段 | `UMovieSceneGeometryCacheTrack` |

### 使用示例（蓝图描述）

1.  **在Sequencer中使用**:
    *   在你的Level Sequence中，为拥有`GeometryCacheComponent`的Actor添加一个**Geometry Cache Track**。
    *   右键单击该轨道，选择“Add New Animation”，这会创建一个新的`MovieSceneGeometryCacheSection`（片段）。
    *   在片段的属性面板中，通过 **Geometry Cache Asset** 属性指定你导入的`UGeometryCache`资产。
    *   通过 **Play Rate** 和 **Reverse** 属性调整播放效果。
    *   通过移动和缩放该片段（Section）来控制其在时间轴上的起始、结束和持续时间。

2.  **通过蓝图操作组件**:
    *   对于直接的组件控制，通常使用`GeometryCacheComponent`的蓝图函数（如`Play`、`SetPlaybackSpeed`）更为直接。此插件的核心蓝图接口主要面向**Sequencer集成**。

## C++ 用法

### 头文件引入

```cpp
#include "GeometryCacheTracks/GeometryCacheTracksModule.h"
#include "Sections/MovieSceneGeometryCacheSection.h"
#include "Tracks/MovieSceneGeometryCacheTrack.h"
```

### 基本用法

从代码中提取的创建和配置几何缓存动画片段的基本流程。

```cpp
// 假设你已经有一个 UMovieSceneGeometryCacheTrack* Track
// (来源：MovieSceneGeometryCacheTrack.h)

// 1. 创建一个新的动画片段
UMovieSceneGeometryCacheSection* NewSection = Cast<UMovieSceneGeometryCacheSection>(Track->CreateNewSection());

// 2. 配置片段参数
NewSection->Params.GeometryCacheAsset = YourGeometryCacheAsset; // 指定几何缓存资产
NewSection->Params.PlayRate = 1.0f; // 设置播放速率
NewSection->Params.bReverse = false; // 不反向播放

// 3. 设置片段的时间范围 (FFrameNumber 以 Tick Resolution 为单位)
NewSection->SetRange(TRange<FFrameNumber>(StartFrame, EndFrame));

// 4. 将片段添加到轨道
Track->AddSection(*NewSection);
```

### 进阶用法

使用 `FMovieSceneGeometryCacheParams` 结构体来管理一组动画参数，并应用于片段。

```cpp
// 来源：MovieSceneGeometryCacheSection.h 中的 FMovieSceneGeometryCacheParams
FMovieSceneGeometryCacheParams Params;
Params.GeometryCacheAsset = LoadObject<UGeometryCache>(nullptr, TEXT("/Game/PathToYourAsset.YourAsset"));
Params.PlayRate = 0.5f;
Params.bReverse = false;
Params.FirstLoopStartFrameOffset = 0;
Params.StartFrameOffset = 10; // 从动画的第10帧开始播放
Params.EndFrameOffset = -5;   // 提前5帧结束播放
Params.GetSequenceLength();   // 获取动画序列的原始长度

// 可以将配置好的 Params 应用于一个已有的 Section
// MovieSceneSection->Params = Params;
```

## Demo 示例

以下是一个最小化的示例，展示如何在 C++ 中创建一个配置好的几何缓存轨道和片段。

**MyGeometryCacheDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "MovieSceneSequence.h"
#include "GeometryCache.h"

class UMovieSceneGeometryCacheTrack;
class UMovieSceneGeometryCacheSection;

class FGeometryCacheDemo
{
public:
    void CreateDemoSequence();

private:
    void AddGeometryCacheTrack(UMovieSceneSequence* Sequence, UGeometryCache* GeometryCacheAsset);
};
```

**MyGeometryCacheDemo.cpp**
```cpp
#include "MyGeometryCacheDemo.h"
#include "MovieScene.h"
#include "Tracks/MovieSceneGeometryCacheTrack.h"
#include "Sections/MovieSceneGeometryCacheSection.h"
#include "Evaluation/MovieSceneEvaluationTemplateInstance.h"

void FGeometryCacheDemo::CreateDemoSequence()
{
    // 创建一个临时的序列对象（实际项目中会从资产加载或创建）
    UMovieSceneSequence* DemoSequence = NewObject<UMovieSceneSequence>();

    // 假设你已经加载了一个几何缓存资产
    UGeometryCache* MyAnimAsset = LoadObject<UGeometryCache>(nullptr, TEXT("/Game/MyMeshAnim.MyMeshAnim"));
    if (MyAnimAsset)
    {
        AddGeometryCacheTrack(DemoSequence, MyAnimAsset);
    }
}

void FGeometryCacheDemo::AddGeometryCacheTrack(UMovieSceneSequence* Sequence, UGeometryCache* GeometryCacheAsset)
{
    UMovieScene* MovieScene = Sequence->GetMovieScene();
    if (!MovieScene) return;

    // 1. 创建几何缓存轨道
    UMovieSceneGeometryCacheTrack* GeomCacheTrack = MovieScene->AddTrack<UMovieSceneGeometryCacheTrack>();
    if (!GeomCacheTrack) return;

    // 2. 创建一个动画片段
    UMovieSceneGeometryCacheSection* Section = Cast<UMovieSceneGeometryCacheSection>(GeomCacheTrack->CreateNewSection());
    if (!Section) return;

    // 3. 配置片段参数
    Section->Params.GeometryCacheAsset = GeometryCacheAsset;
    Section->Params.PlayRate = 1.0f;
    Section->Params.bReverse = false;

    // 4. 设置片段在序列中的时间范围（例如从帧0到帧120）
    const FFrameRate DisplayRate = MovieScene->GetDisplayRate();
    const FFrameRate TickResolution = MovieScene->GetTickResolution();
    const FFrameNumber StartFrame = 0;
    const FFrameNumber DurationFrames = FFrameNumber(120) * TickResolution / DisplayRate; // 将显示帧数转换为 Tick Resolution

    Section->SetRange(TRange<FFrameNumber>(StartFrame, StartFrame + DurationFrames));

    // 5. 将配置好的片段添加到轨道
    GeomCacheTrack->AddSection(*Section);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MeshUtilitiesCommon` | 提供网格相关的通用工具和数据结构，用于处理导入的网格数据。 |
| `UnrealEd` | 编辑器功能依赖，用于资产导入、编辑器集成和属性自定义等。 |

**注意**：该插件的其他子模块（如`GeometryCacheSequencer`, `GeometryCacheTracks`）很可能依赖于 `SequencerCore`, `MovieScene`, `MovieSceneTracks` 等 Sequencer 核心模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口相关重构，优化了客户端关联/解离时的通知逻辑。 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回退了某个提交（CL53913857）。 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 同 `cfb610df`，对视口关联逻辑的另一次相关提交。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的 `UE_LOG` 日志调用迁移到新的 `UE_LOGF` 宏。 |
| 2026-04-08 | `f5e682af` | [Sequencer] Simple View with toolable timeline initial release | Sequencer 功能更新：初始版本的简易视图与可工具化时间轴。 |

### 维护评价

**活跃维护**。GeometryCache 插件于 2022 年从实验性模块正式迁移，是一个相对成熟的功能。从近期提交记录看（截至 2026 年 5 月），其所属的 `Engine/Plugins/Runtime/GeometryCache/` 目录仍有活动，更新内容包括日志规范更新和底层视口/Sequencer 集成优化。这表明 Epic 仍在对其进行维护和底层架构的改进。该插件是处理特定类型动画（顶点缓存）的标准方案，推荐在需要此类功能的项目中使用。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeometryCache)
-   [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/AlembicImporter/#importasgeometrycache)
-   测试用例：位于 `Engine/Tests/` 目录下（未在本次分析的插件目录内）。