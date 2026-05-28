# Geometry Collection Plugin

> Adds Geometry Collection Container.

| 属性 | 值 |
|---|---|
| 中文名 | 几何体集合 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `GeometryCollectionDepNodes` (Runtime), `GeometryCollectionEditor` (Runtime), `GeometryCollectionNodes` (Runtime), `GeometryCollectionSequencer` (Runtime), `GeometryCollectionTracks` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-07-31 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GeometryCollectionPlugin) | |

## 用途

GeometryCollectionPlugin 提供了一套完整的几何体集合管理系统，主要用于：

1. **几何体集合容器**：将多个几何体组合成一个可管理的集合，支持父子层级关系（BoneHierarchy）
2. **物理模拟集成**：支持基于层级的碰撞检测、破碎聚类（Clustering）和约束管理
3. **Sequencer 动画集成**：提供 MovieScene 轨道和模板，用于在 Sequencer 中播放几何体集合的缓存动画
4. **Dataflow 数据流支持**：提供节点图接口，用于程序化处理几何体集合数据

该插件是 Chaos 物理引擎破坏系统（Destruction System）的核心数据结构基础，为大型复杂几何体的拆分、破碎和物理模拟提供了底层支撑。

## 使用场景

- 你需要制作可破坏的建筑或环境 → 使用 GeometryCollection 管理碎片层级
- 你需要在 Sequencer 中精确控制破坏动画回放 → 使用 GeometryCollectionTracks
- 你需要程序化生成或处理几何体集合 → 使用 Dataflow 节点
- 你需要基于物理的破坏聚类效果 → 使用 Clustering 功能

## 蓝图用法

### 核心节点

GeometryCollectionTracks 模块主要提供 Sequencer 集成，蓝图直接暴露的 API 较少。主要类通过 MovieScene 系统使用：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddNewAnimation` | 向轨迹添加新的动画段 | `UMovieSceneGeometryCollectionTrack` |
| `GetAnimSectionsAtTime` | 获取指定时间的动画段 | `UMovieSceneGeometryCollectionTrack` |
| `MapTimeToAnimation` | 将帧时间映射到动画时间 | `UMovieSceneGeometryCollectionSection` |

### 使用示例（蓝图描述）

在 Sequencer 中使用 GeometryCollection 动画：

1. 创建一个 Sequencer
2. 添加 `UMovieSceneGeometryCollectionTrack` 轨道
3. 在轨道上创建 `UMovieSceneGeometryCollectionSection`
4. 在 Section 的 Params 中设置 `GeometryCollectionCache`（指定缓存资产）
5. 配置 `PlayRate`、`StartFrameOffset`、`EndFrameOffset` 控制播放行为

## C++ 用法

### 头文件引入

```cpp
#include "MovieSceneGeometryCollectionSection.h"
#include "MovieSceneGeometryCollectionTrack.h"
#include "MovieSceneGeometryCollectionTemplate.h"
```

### 基本用法

创建和配置几何体集合的 Sequencer 参数：

```cpp
// 来源: Public/MovieSceneGeometryCollectionSection.h

// 配置几何体集合播放参数
FMovieSceneGeometryCollectionParams Params;
Params.GeometryCollectionCache = FSoftObjectPath("/Game/Caches/MyDestructibleCache");
Params.StartFrameOffset = FFrameNumber(0);
Params.EndFrameOffset = FFrameNumber(0);
Params.PlayRate = 1.0f;

// 获取动画时长
float Duration = Params.GetDuration();
float SequenceLength = Params.GetSequenceLength();
```

### 进阶用法

自定义 MovieScene 模板实现评估逻辑：

```cpp
// 来源: Public/MovieSceneGeometryCollectionTemplate.h

// 创建模板参数，包含时间范围信息
FMovieSceneGeometryCollectionSectionTemplateParameters TemplateParams(
    Params,                                    // 基础参数
    FFrameNumber(0),                           // Section 起始帧
    FFrameNumber(100)                          // Section 结束帧
);

// 将帧时间映射到动画时间
FFrameTime CurrentTime(50);
FFrameRate TickResolution(24000, 1);
float AnimationTime = TemplateParams.MapTimeToAnimation(CurrentTime, TickResolution);
```

## Demo 示例

```cpp
// MyGeometryCollectionPlayer.h
#pragma once

#include "CoreMinimal.h"
#include "MovieSceneGeometryCollectionSection.h"
#include "MovieSceneGeometryCollectionTrack.h"

class FMyGeometryCollectionPlayer
{
public:
    void SetupTrack(UMovieSceneGeometryCollectionTrack* Track, 
                    UGeometryCollectionCache* Cache, 
                    FFrameNumber StartTime)
    {
        if (!Track || !Cache)
            return;

        // 添加新的动画段
        UMovieSceneSection* Section = Track->AddNewAnimation(StartTime, nullptr);
        
        // 获取几何体集合参数并配置
        UMovieSceneGeometryCollectionSection* GCSection = 
            Cast<UMovieSceneGeometryCollectionSection>(Section);
        if (GCSection)
        {
            GCSection->Params.GeometryCollectionCache = 
                FSoftObjectPath(Cache->GetPathName());
            GCSection->Params.PlayRate = 1.0f;
            GCSection->Params.StartFrameOffset = FFrameNumber(0);
            GCSection->Params.EndFrameOffset = FFrameNumber(0);
        }
    }

    void PrintAnimationInfo(const UMovieSceneGeometryCollectionSection* Section)
    {
        if (!Section)
            return;

        float Duration = Section->Params.GetDuration();
        float Length = Section->Params.GetSequenceLength();
        UE_LOG(LogTemp, Log, TEXT("Animation Duration: %f, Length: %f, PlayRate: %f"),
               Duration, Length, Section->Params.PlayRate);
    }
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Sequencer` | Sequencer 框架核心 |
| `MovieScene` | MovieScene 评估系统 |
| `GeometryCollectionEngine` | 几何体集合引擎运行时 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-23 | `176334d2` | Fix localization warnings for UE 5.8 | 修复 UE 5.8 本地化警告 |
| 2026-05-14 | `ae91b9c4` | Dataflow: | Dataflow 功能更新 |
| 2026-05-14 | `28e138a1` | [Backout] - CL53945814 | 回退之前的提交 |
| 2026-05-14 | `88fb5004` | Dataflow: | Dataflow 功能更新 |
| 2026-05-14 | `d2897727` | Dataflow : add a node to create external collision on a geometry collection | 新增 Dataflow 节点：创建几何体集合的外部碰撞 |

### 维护评价

**状态：活跃维护中**

- ✅ 最近 1 年内有功能性更新（Dataflow 集成）
- ✅ 作为 Chaos 物理引擎破坏系统的核心组件，持续受到关注
- ⚠️ 仍标记为实验性（IsBetaVersion=true）且默认未启用
- ⚠️ 插件版本号为 0.1，API 可能发生破坏性变更
- ✅ 推荐在需要物理破碎效果的项目中使用，但需注意 API 稳定性

该插件自 2018 年创建以来持续迭代，已从早期的物理实验功能演进为成熟的几何体集合系统。近期开发重心转向 Dataflow 数据流集成，表明 Epic 正在将其与程序化工作流深度整合。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GeometryCollectionPlugin)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GeometryCollectionPlugin/Tests)（如存在）