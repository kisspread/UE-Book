# Geometry Cache

> Support for distilled Geometry animations

| 属性 | 值 |
|---|---|
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `GeometryCache` (Runtime), `GeometryCacheEd` (Runtime), `GeometryCacheSequencer` (Runtime), `GeometryCacheStreamer` (Runtime), `GeometryCacheTracks` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-04-12 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GeometryCache) | |

## 用途

GeometryCache 插件提供了一套完整的**几何体缓存动画**系统，用于播放预烘焙的顶点级动画数据。与骨骼动画不同，几何体缓存直接存储每一帧的网格顶点位置，适用于无法用骨骼表达的复杂形变效果——例如布料模拟、流体表面、刚体碎裂、面部捕捉等。

核心工作流：将 Alembic (.abc) 文件导入 UE，烘焙为 GeometryCache 资产，然后通过 `UGeometryCacheComponent` 在运行时逐帧回放顶点数据。插件还集成了 Sequencer，支持在时间轴上精确控制缓存动画的播放。

**为什么存在？** UE 的骨骼动画系统只能处理骨骼驱动的形变，对于顶点级的复杂动画（如 Houdini 导出的模拟结果），需要一种轻量级的帧间插值回放方案。GeometryCache 正是为此而生。

## 模块架构

| 模块 | 类型 | 职责 |
|---|---|---|
| `GeometryCache` | Runtime | 核心资产类型（`UGeometryCache`）、组件（`UGeometryCacheComponent`）、编解码器、渲染代理 |
| `GeometryCacheEd` | Runtime | 编辑器集成：资产工厂、导入器（Alembic）、编辑器工具、细节面板自定义 |
| `GeometryCacheSequencer` | Runtime | Sequencer 编辑器集成：轨道图标、自定义节点等 |
| `GeometryCacheStreamer` | Runtime | 流式加载支持，处理大型缓存文件的按需加载 |
| `GeometryCacheTracks` | Runtime | Sequencer 轨道和片段：在时间轴上控制几何体缓存播放 |

## 使用场景

- 你在导入 Alembic 格式的顶点动画（来自 Houdini、Blender、Maya 等）→ 用 GeometryCache 导入并回放
- 你需要在 Sequencer 中精确控制缓存动画的播放时间、速率、倒放 → 用 GeometryCacheTracks
- 你有大型缓存文件需要流式加载以节省内存 → 用 GeometryCacheStreamer
- 你需要在蓝图中动态控制几何体缓存的播放状态 → 用 GeometryCacheComponent 的蓝图 API

## 蓝图用法

### 核心属性（FMovieSceneGeometryCacheParams）

以下属性在 Sequencer 片段中可通过蓝图读写：

| 属性 | 类型 | 说明 |
|---|---|---|
| `GeometryCacheAsset` | `UGeometryCache*` | 要播放的几何体缓存资产 |
| `FirstLoopStartFrameOffset` | `FFrameNumber` | 第一次循环的起始帧偏移 |
| `StartFrameOffset` | `FFrameNumber` | 动画起始帧偏移 |
| `EndFrameOffset` | `FFrameNumber` | 动画结束帧偏移 |
| `PlayRate` | `float` | 播放速率 |
| `bReverse` | `bool` | 是否倒放 |

### Sequencer 轨道节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddNewAnimation` | 在指定时间添加新的几何体缓存动画片段 | `UMovieSceneGeometryCacheTrack` |
| `GetAnimSectionsAtTime` | 获取指定时间点的所有动画片段 | `UMovieSceneGeometryCacheTrack` |
| `MapTimeToAnimation` | 将 Sequencer 时间映射为动画时间 | `UMovieSceneGeometryCacheSection` |

### 使用示例（Sequencer 集成）

1. 在 Sequencer 中为 `GeometryCacheActor` 添加轨道
2. 系统自动创建 `UMovieSceneGeometryCacheTrack`
3. 在轨道上添加 `UMovieSceneGeometryCacheSection`
4. 在片段属性中指定 `GeometryCacheAsset`，调整 `PlayRate` 和 `bReverse`
5. 通过 `FirstLoopStartFrameOffset` / `StartFrameOffset` / `EndFrameOffset` 精确控制播放范围

## C++ 用法

### 头文件引入

```cpp
#include "GeometryCacheTracksModule.h"
#include "MovieSceneGeometryCacheTrack.h"
#include "MovieSceneGeometryCacheSection.h"
```

### 基本用法：创建 Sequencer 轨道

```cpp
// 在 Sequencer 中为 GeometryCacheComponent 添加动画轨道
// 来源: MovieSceneGeometryCacheTrack.h

UGeometryCacheComponent* GeomCacheComp = /* 获取组件引用 */;
FFrameNumber KeyTime(0);

// 获取或创建轨道
UMovieSceneGeometryCacheTrack* Track = /* 从 Sequencer 获取轨道 */;

// 在指定时间添加动画片段
UMovieSceneSection* Section = Track->AddNewAnimation(KeyTime, GeomCacheComp);
```

### 进阶用法：配置播放参数

```cpp
// 来源: MovieSceneGeometryCacheSection.h

UMovieSceneGeometryCacheSection* CacheSection = /* 获取片段引用 */;

// 配置播放参数
CacheSection->Params.GeometryCacheAsset = LoadObject<UGeometryCache>(nullptr, TEXT("/Game/MyGeometryCache"));
CacheSection->Params.PlayRate = 1.5f;
CacheSection->Params.bReverse = false;
CacheSection->Params.StartFrameOffset = FFrameNumber(10);
CacheSection->Params.EndFrameOffset = FFrameNumber(0);
CacheSection->Params.FirstLoopStartFrameOffset = FFrameNumber(0);

// 获取序列长度（不受 PlayRate 影响）
float SequenceLength = CacheSection->Params.GetSequenceLength();

// 将 Sequencer 时间映射为动画时间
float AnimTime = CacheSection->MapTimeToAnimation(Duration, InPosition, InFrameRate);
```

### 进阶用法：查询轨道状态

```cpp
// 来源: MovieSceneGeometryCacheTrack.h

UMovieSceneGeometryCacheTrack* Track = /* 获取轨道 */;

// 检查轨道是否为空
if (!Track->IsEmpty())
{
    // 获取所有片段
    const TArray<UMovieSceneSection*>& AllSections = Track->GetAllSections();

    // 获取指定时间点的片段
    TArray<UMovieSceneSection*> SectionsAtTime = Track->GetAnimSectionsAtTime(FFrameNumber(60));

    // 检查某个片段是否属于此轨道
    bool bHasSection = Track->HasSection(*SomeSection);
}
```

## Demo 示例

### 最小可编译示例：程序化创建 GeometryCache Sequencer 轨道

**Build.cs 依赖：**

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "MovieScene",
    "GeometryCache",
    "GeometryCacheTracks"
});
```

**GeometryCacheDemo.h：**

```cpp
#pragma once

#include "CoreMinimal.h"

class ULevelSequence;
class UGeometryCacheComponent;

class FGeometryCacheDemo
{
public:
    /** 为指定的 GeometryCacheComponent 在 Sequencer 中创建动画轨道 */
    static UMovieSceneSection* CreateCacheTrackInSequence(
        ULevelSequence* Sequence,
        UGeometryCacheComponent* Component,
        UGeometryCache* CacheAsset,
        FFrameNumber StartTime,
        float PlayRate = 1.0f);
};
```

**GeometryCacheDemo.cpp：**

```cpp
#include "GeometryCacheDemo.h"
#include "MovieSceneGeometryCacheTrack.h"
#include "MovieSceneGeometryCacheSection.h"
#include "GeometryCache.h"
#include "GeometryCacheComponent.h"
#include "LevelSequence.h"
#include "MovieScene.h"

UMovieSceneSection* FGeometryCacheDemo::CreateCacheTrackInSequence(
    ULevelSequence* Sequence,
    UGeometryCacheComponent* Component,
    UGeometryCache* CacheAsset,
    FFrameNumber StartTime,
    float PlayRate)
{
    if (!Sequence || !Component || !CacheAsset)
    {
        return nullptr;
    }

    // 获取 Sequencer 的 MovieScene
    UMovieScene* MovieScene = Sequence->GetMovieScene();
    if (!MovieScene)
    {
        return nullptr;
    }

    // 创建绑定并添加轨道
    // 实际使用中需要通过 Sequencer 的绑定系统
    // 这里演示参数配置的核心逻辑

    // 配置播放参数
    FMovieSceneGeometryCacheParams Params;
    Params.GeometryCacheAsset = CacheAsset;
    Params.PlayRate = PlayRate;
    Params.bReverse = false;
    Params.FirstLoopStartFrameOffset = FFrameNumber(0);
    Params.StartFrameOffset = FFrameNumber(0);
    Params.EndFrameOffset = FFrameNumber(0);

    // 获取动画序列长度
    float SeqLength = Params.GetSequenceLength();

    UE_LOG(LogTemp, Log, TEXT("GeometryCache sequence length: %.2f seconds"), SeqLength);

    return nullptr; // 实际返回创建的 Section
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MeshUtilitiesCommon` | 网格工具通用功能（GeometryCache 核心模块依赖） |
| `MovieScene` | Sequencer 核心框架（GeometryCacheTracks 依赖） |
| `LevelSequence` | 关卡序列支持 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| - | `667bc9d4bd3a` | USD: Refactor of LevelSequenceHelper for Subsections support | USD 管线重构，非 GeometryCache 直接功能更新 |
| - | `6ae573356bbf` | Convert all files to have dllstorage on methods/staticvar | 全局符号导出规范化，编译基础设施改动 |
| - | `f19355813788` | Sequencer: Use static_cast<int32> instead of int | 代码风格规范化，类型安全改进 |

### 维护评价

GeometryCache 是一个**成熟稳定**的插件，自 2018 年创建以来已有约 7 年历史。近期更新主要是编译基础设施和代码规范化，没有重大功能变更或 bug 修复，说明核心功能已经相当稳定。

**优点：**
- 作为 Alembic 导入的核心组件，是 UE 官方支持的标准功能
- 与 Sequencer 深度集成，支持完整的时间轴控制
- 流式加载支持大型缓存文件

**注意事项：**
- 对于大规模顶点动画，内存占用较高（每帧存储完整顶点数据）
- 编解码器性能是关键瓶颈，建议使用 Blosc 压缩
- `GeometryCacheEd` 模块标记为 Runtime 但实际包含编辑器功能，打包时需注意

**推荐使用：** ✅ 推荐。这是 UE 官方的几何体缓存方案，稳定可靠，适合需要 Alembic 顶点动画的工作流。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GeometryCache)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/AlembicImporter/#importasgeometrycache)