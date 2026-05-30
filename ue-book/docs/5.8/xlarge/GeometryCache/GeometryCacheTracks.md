# Geometry Cache Tracks

> Support for distilled Geometry animations（支持烘焙几何体动画，即顶点动画缓存的 Sequencer 时间轴集成）

| 属性 | 值 |
|---|---|
| 中文名 | 几何缓存轨迹 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `GeometryCache` (Runtime), `GeometryCacheEd` (Runtime), `GeometryCacheSequencer` (Runtime), `GeometryCacheStreamer` (Runtime), `GeometryCacheTracks` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-01-26 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeometryCache) | |

## 用途

GeometryCache 插件用于导入和播放**预烘焙的几何体动画**（顶点级动画），典型来源是 Alembic (.abc) 文件。与骨骼动画不同，几何缓存直接存储每一帧的顶点位置，适用于布料模拟、流体模拟、破碎效果等无法用骨骼驱动的变形动画。

**GeometryCacheTracks** 是该插件的 Sequencer 集成模块，它将几何缓存资产作为**Sequencer 轨道**暴露出来，让用户能够在时间轴上精确控制几何缓存的播放时机、速率、循环偏移和倒放。核心解决的问题是：如何在 Sequencer 影片编辑器中像控制骨骼动画一样控制几何缓存动画。

## 使用场景

- 你在 Sequencer 中编排一段过场动画，其中包含 Alembic 导入的破碎模拟 → 用 GeometryCacheTracks 将缓存动画放到时间轴上
- 你需要在影片中精确同步几何缓存动画与其他事件（如音效、粒子）→ 用 Sequencer 轨道对齐
- 你需要控制几何缓存的播放速率、倒放或循环起点 → 通过轨道参数面板调整
- 你正在做实时渲染预览（如建筑可视化中的窗帘飘动动画）→ 将几何缓存放入 Sequencer 统一管理

## 蓝图用法

GeometryCacheTracks 模块主要服务于 Sequencer 编辑器内部，大多数参数通过 Sequencer 面板暴露，但部分结构体和属性支持蓝图读写。

### 核心参数（FMovieSceneGeometryCacheParams）

| 属性 | 类型 | 说明 |
|---|---|---|
| `GeometryCacheAsset` | `UGeometryCache*` | 要播放的几何缓存资产 |
| `FirstLoopStartFrameOffset` | `FFrameNumber` | 第一次循环的起始帧偏移 |
| `StartFrameOffset` | `FFrameNumber` | 动画起始帧偏移 |
| `EndFrameOffset` | `FFrameNumber` | 动画结束帧偏移 |
| `PlayRate` | `float` | 播放速率（1.0 = 正常速度） |
| `bReverse` | `bool` | 是否倒放 |

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetSequenceLength` | 获取动画序列原始长度（不受 PlayRate 影响） | `FMovieSceneGeometryCacheParams` |
| `AddNewAnimation` | 在指定时间向轨道添加新的几何缓存动画段 | `UMovieSceneGeometryCacheTrack` |
| `GetAnimSectionsAtTime` | 获取指定时间处的所有动画段 | `UMovieSceneGeometryCacheTrack` |
| `MapTimeToAnimation` | 将 Sequencer 帧时间映射为实际动画时间 | `UMovieSceneGeometryCacheSection` |

### 使用示例（蓝图描述）

1. **在 Sequencer 中手动使用**：创建一个 Sequencer → 右键添加轨道 → 选择 "Geometry Cache Track" → 在轨道上右键创建 Section → 在 Details 面板中指定 `GeometryCacheAsset`，调整 `PlayRate`、`bReverse` 等参数。

2. **通过蓝图动态创建**：获取 Sequencer 的 `UMovieSceneSequence` → 找到或创建 `UMovieSceneGeometryCacheTrack` → 调用 `AddNewAnimation(KeyTime, GeomCacheComp)` 添加动画段 → 通过返回的 Section 的 `Params` 属性设置播放参数。

## C++ 用法

### 头文件引入

```cpp
#include "GeometryCacheTracks/Public/GeometryCacheTracksModule.h"
#include "GeometryCache/Classes/MovieSceneGeometryCacheSection.h"
#include "GeometryCache/Classes/MovieSceneGeometryCacheTrack.h"
```

### 基本用法

创建一个 Sequencer 几何缓存轨道并配置参数：

```cpp
// 来源: Classes/MovieSceneGeometryCacheSection.h, Classes/MovieSceneGeometryCacheTrack.h

#include "MovieSceneGeometryCacheSection.h"
#include "MovieSceneGeometryCacheTrack.h"
#include "GeometryCache.h"

// 获取或创建 GeometryCacheTrack
UMovieSceneGeometryCacheTrack* GeomCacheTrack = Sequence->FindFirstTrack<UMovieSceneGeometryCacheTrack>();
if (!GeomCacheTrack)
{
    GeomCacheTrack = Sequence->AddTrack<UMovieSceneGeometryCacheTrack>();
}

// 创建新的动画段并设置参数
UMovieSceneSection* NewSection = GeomCacheTrack->CreateNewSection();
UMovieSceneGeometryCacheSection* GeomCacheSection = Cast<UMovieSceneGeometryCacheSection>(NewSection);

// 配置播放参数
GeomCacheSection->Params.GeometryCacheAsset = MyGeometryCache;
GeomCacheSection->Params.PlayRate = 1.0f;
GeomCacheSection->Params.bReverse = false;
GeomCacheSection->Params.StartFrameOffset = FFrameNumber(0);
GeomCacheSection->Params.EndFrameOffset = FFrameNumber(0);

// 设置时间范围
FFrameNumber StartFrame(0);
FFrameNumber EndFrame(static_cast<int32>(MyGeometryCache->GetDuration() * Framerate));
NewSection->SetRange(TRange<FFrameNumber>(StartFrame, EndFrame));

// 添加到轨道
GeomCacheTrack->AddSection(*NewSection);
```

### 进阶用法

将帧时间映射到动画时间并控制播放方向：

```cpp
// 来源: Classes/MovieSceneGeometryCacheSection.h - MapTimeToAnimation

// 在自定义评估逻辑中，将 Sequencer 的当前时间映射为动画时间
float ComponentDuration = GeomCacheComponent->GetDuration();
FFrameTime CurrentPosition = Context.GetTime();
FFrameRate TickResolution = Context.GetFrameRate();

// MapTimeToAnimation 处理了循环、偏移和倒放的逻辑
float AnimTime = GeomCacheSection->MapTimeToAnimation(
    ComponentDuration,
    CurrentPosition,
    TickResolution
);

// AnimTime 已考虑 PlayRate、bReverse、StartFrameOffset、EndFrameOffset
// 可直接用于驱动 GeomCacheComponent
GeomCacheComponent->SetStartTimeOffset(AnimTime);
```

### 模块可用性检查

```cpp
// 来源: Public/GeometryCacheTracksModule.h

#include "GeometryCacheTracksModule.h"

// 安全检查模块是否已加载
if (FGeometryCacheTracksModule::IsAvailable())
{
    FGeometryCacheTracksModule& Module = FGeometryCacheTracksModule::Get();
    // 模块已就绪，可以安全使用
}
```

## Demo 示例

一个完整的最小示例，在 Sequencer 中通过 C++ 动态创建几何缓存轨道：

```cpp
// MySequenceHelper.h
#pragma once

#include "CoreMinimal.h"

class ULevelSequence;
class UGeometryCache;

class FMySequenceHelper
{
public:
    /** 在 Sequencer 中添加几何缓存轨道 */
    static void AddGeometryCacheToSequence(
        ULevelSequence* InSequence,
        UGeometryCache* InGeometryCache,
        float InStartTime,
        float InPlayRate = 1.0f,
        bool bInReverse = false
    );
};
```

```cpp
// MySequenceHelper.cpp
#include "MySequenceHelper.h"

#include "LevelSequence.h"
#include "MovieSceneGeometryCacheSection.h"
#include "MovieSceneGeometryCacheTrack.h"
#include "GeometryCache.h"
#include "MovieScene.h"

void FMySequenceHelper::AddGeometryCacheToSequence(
    ULevelSequence* InSequence,
    UGeometryCache* InGeometryCache,
    float InStartTime,
    float InPlayRate,
    bool bInReverse)
{
    if (!InSequence || !InGeometryCache)
    {
        return;
    }

    UMovieScene* MovieScene = InSequence->GetMovieScene();
    if (!MovieScene)
    {
        return;
    }

    // 创建几何缓存轨道
    UMovieSceneGeometryCacheTrack* Track = InSequence->AddTrack<UMovieSceneGeometryCacheTrack>(MovieScene->GetSelectionID());
    if (!Track)
    {
        return;
    }

    // 创建 Section
    UMovieSceneGeometryCacheSection* Section = Cast<UMovieSceneGeometryCacheSection>(Track->CreateNewSection());
    if (!Section)
    {
        return;
    }

    // 配置参数
    Section->Params.GeometryCacheAsset = InGeometryCache;
    Section->Params.PlayRate = InPlayRate;
    Section->Params.bReverse = bInReverse;
    Section->Params.FirstLoopStartFrameOffset = FFrameNumber(0);
    Section->Params.StartFrameOffset = FFrameNumber(0);
    Section->Params.EndFrameOffset = FFrameNumber(0);

    // 计算时间范围（基于帧率 24fps）
    const FFrameRate FrameRate(24, 1);
    const FFrameNumber StartFrame = FrameRate.AsFrameNumber(InStartTime);
    const FFrameNumber EndFrame = StartFrame + FrameRate.AsFrameNumber(InGeometryCache->GetDuration() / FMath::Max(InPlayRate, SMALL_NUMBER));

    Section->SetRange(TRange<FFrameNumber>(StartFrame, EndFrame));

    // 添加到轨道
    Track->AddSection(*Section);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GeometryCache` | 几何缓存核心运行时（资产类型、组件、流式加载） |
| `MovieScene` | Sequencer 影片场景核心（Section、Track、EvalTemplate 基类） |
| `MeshUtilitiesCommon` | 网格体工具公共类型 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated with a viewport | 视口关联/解除关联时通知客户端的重构 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回退之前的变更 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated with a viewport | 视口关联通知机制重构 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移：UE_LOG 改为 UE_LOGF |
| 2026-04-08 | `f5e682af` | [Sequencer] Simple View with toolable timeline initial release | Sequencer 简易视图与可工具化时间轴初始发布 |

### 维护评价

**状态：活跃维护**

- 创建于 2022 年 1 月（从 Experimental 迁移到正式版），约 4 年历史
- 近期有持续更新，2026 年 4-5 月仍有活动
- 最近的改动集中在引擎全局重构（日志宏迁移、视口通知机制）和 Sequencer 新功能（Simple View），说明该模块随引擎版本持续维护
- 作为 Sequencer 核心轨道之一（与 SkeletalMesh Track 平级），属于基础功能，不会被轻易废弃
- **推荐使用**：这是在 Sequencer 中使用几何缓存动画的标准方式，API 稳定，文档完善

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GeometryCache)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/AlembicImporter/#importasgeometrycache)