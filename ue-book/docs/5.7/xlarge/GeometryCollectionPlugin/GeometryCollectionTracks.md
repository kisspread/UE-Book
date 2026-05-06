# Geometry

> Adds Geometry Collection Container.

| 属性 | 值 |
|---|---|
| 中文名 | 几何集合 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资源） |
| 模块 | `GeometryCollectionDepNodes` (Runtime), `GeometryCollectionEditor` (Runtime), `GeometryCollectionNodes` (Runtime), `GeometryCollectionSequencer` (Runtime), `GeometryCollectionTracks` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-06 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GeometryCollectionPlugin) | |

## 用途

该插件基于 **Geometry Collection**（几何集合）系统，提供了在关卡序列（Sequencer）中播放几何体缓存动画的能力，以及通过 Dataflow 图表进行程序化生成和编辑的功能。它还包含依赖节点和编辑器扩展，使得艺术家和设计师可以直接在时间线上操控破碎几何体的回放，无需编写代码。本质上，它是将物理模拟或预录制的几何体变形数据（缓存在 `UGeometryCollectionCache` 中）转化为可被序列器驱动的时间线轨道。

## 使用场景

- 你需要预录一个破碎物体的物理模拟效果，然后在游戏/电影序列中精确控制它的播放速度、起止偏移。
- 你希望将多个几何集合缓存动画叠加、混合，或与其他动画轨道（如 Transform、Visibility）同步。
- 你正在使用 Dataflow 编辑器程序化生成复杂的几何集合，并希望将其结果直接用于序列器轨道。
- 你需要在编辑器中预览并调整几何体缓存的播放范围，而无需重新模拟。

## 蓝图用法

> **注意**：`GeometryCollectionTracks` 模块主要提供 C++ 级别的轨道和模板，蓝图可直接调用 `Get` 和 `Set` 节点操作 `UMovieSceneGeometryCollectionTrack`，通常由序列器自动管理。以下列出与本节相关的函数，其余模块（如 `GeometryCollectionNodes`）可能提供更多蓝图节点，但不在本节覆盖范围。

### 序列器轨道控制节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Add New Animation` | 在轨道上为指定几何集合组件添加新的动画段 | `UMovieSceneGeometryCollectionTrack` |
| `Map Time To Animation` | 将序列时间（帧）映射到动画内部时间（秒） | `UMovieSceneGeometryCollectionSection` |
| `Get Anim Sections At Time` | 获取某一时间点上的所有动画段 | `UMovieSceneGeometryCollectionTrack` |

这些节点通常在 C++ 中用于自定义轨道行为，但暴露为 `BlueprintCallable` / `BlueprintPure` 的版本需要确认（本模块头文件中未标记 `BlueprintCallable`，需在完整代码中确认）。

## C++ 用法

### 头文件引入

```cpp
#include "GeometryCollectionTracksModule.h"
#include "MovieSceneGeometryCollectionTrack.h"
#include "MovieSceneGeometryCollectionSection.h"
#include "MovieSceneGeometryCollectionTemplate.h"
```

### 基本用法：创建轨道和添加动画

以下示例演示在关卡序列中创建一个几何集合轨道，并添加一条动画段。

```cpp
// 假设已有一个 UMovieSceneSequence* Sequence 和一个 UGeometryCollectionComponent* GeomCacheComp
UMovieSceneSequence* Sequence = /* 从某个源获取 */;
UGeometryCollectionComponent* GeomCacheComp = /* 目标几何集合组件 */;

// 获取主序列的 MovieScene
UMovieScene* MovieScene = Sequence->GetMovieScene();

// 添加轨道
UMovieSceneGeometryCollectionTrack* NewTrack = MovieScene->AddTrack<UMovieSceneGeometryCollectionTrack>(GeomCacheComp->GetOwner());
if (NewTrack)
{
    // 在当前时间位置添加动画段
    FFrameNumber KeyTime = MovieScene->GetPlaybackRange().GetLowerBoundValue();
    UMovieSceneSection* NewSection = NewTrack->AddNewAnimation(KeyTime, GeomCacheComp);

    // 设置参数
    UMovieSceneGeometryCollectionSection* Section = Cast<UMovieSceneGeometryCollectionSection>(NewSection);
    if (Section)
    {
        Section->Params.PlayRate = 1.0f;
        Section->Params.EndFrameOffset = 0;
        // 设置缓存的软引用
        Section->Params.GeometryCollectionCache = FSoftObjectPath(TEXT("/Game/MyCache.MyCache"));
    }
}
```

> 来源文件：`MovieSceneGeometryCollectionTrack.h`, `MovieSceneGeometryCollectionSection.h`

### 进阶用法：自定义评价模板

如果需要实现更复杂的求值逻辑，可以继承 `FMovieSceneGeometryCollectionSectionTemplate` 并重写 `Evaluate` 方法。默认的 `Evaluate` 会委托给 `FMovieSceneGeometryCollectionSectionTemplateParameters::MapTimeToAnimation` 并最终调用 `IMovieScenePlayer` 设置几何集合组件的缓存播放状态。

```cpp
struct FMyGeometrySectionTemplate : public FMovieSceneGeometryCollectionSectionTemplate
{
    FMyGeometrySectionTemplate(const UMovieSceneGeometryCollectionSection& Section)
        : FMovieSceneGeometryCollectionSectionTemplate(Section) { }

    virtual void Evaluate(const FMovieSceneEvaluationOperand& Operand, const FMovieSceneContext& Context,
        const FPersistentEvaluationData& PersistentData, FMovieSceneExecutionTokens& ExecutionTokens) const override
    {
        // 自定义评估逻辑
        // 获取几何集合组件，播放缓存
        // ...
    }
};
```

## Demo 示例

以下是一个完整的最小示例，演示如何在运行时创建序列、轨道并播放几何集合缓存。

**MyGeometryCollectionPlayer.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MovieSceneSequencePlayer.h"
#include "MyGeometryCollectionPlayer.generated.h"

UCLASS()
class AMyGeometryCollectionPlayer : public AActor
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "GeometryCache")
    class UGeometryCollectionComponent* GeometryCollectionComp;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Sequence")
    class ULevelSequence* Sequence;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Sequence")
    class UMovieSceneSequencePlayer* Player;

    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable, Category = "Playback")
    void Play();
};
```

**MyGeometryCollectionPlayer.cpp**
```cpp
#include "MyGeometryCollectionPlayer.h"
#include "LevelSequence.h"
#include "MovieScene.h"
#include "MovieSceneGeometryCollectionTrack.h"
#include "MovieSceneGeometryCollectionSection.h"
#include "GeometryCollection/GeometryCollectionComponent.h"
#include "MovieSceneGeometryCollectionCache.h" // 假设存在

void AMyGeometryCollectionPlayer::BeginPlay()
{
    Super::BeginPlay();

    if (!Sequence)
    {
        Sequence = NewObject<ULevelSequence>(this, "MyGeoSequence");
        Sequence->Initialize();
    }

    UMovieScene* MovieScene = Sequence->GetMovieScene();
    if (!MovieScene) return;

    // 设置播放范围（5秒）
    FFrameRate FrameRate(30, 1);
    MovieScene->SetDisplayRate(FrameRate);
    MovieScene->SetPlaybackRange(0, FrameRate.AsFrameNumber(5.0));

    // 添加轨道
    UMovieSceneGeometryCollectionTrack* Track = MovieScene->AddTrack<UMovieSceneGeometryCollectionTrack>(GeometryCollectionComp->GetOwner());
    if (!Track) return;

    // 添加段
    FFrameNumber StartTime(0);
    UMovieSceneSection* Section = Track->AddNewAnimation(StartTime, GeometryCollectionComp);
    UMovieSceneGeometryCollectionSection* GeoSect = Cast<UMovieSceneGeometryCollectionSection>(Section);
    if (GeoSect)
    {
        // 设置要播放的缓存（请替换为真实路径）
        GeoSect->Params.GeometryCollectionCache = FSoftObjectPath(TEXT("/Game/MyCaches/SimulationCache.SimulationCache"));
        GeoSect->Params.PlayRate = 1.0f;
    }

    // 创建播放器
    Player = NewObject<UMovieSceneSequencePlayer>(this, "SeqPlayer");
    Player->Initialize(Sequence, FrameRate);
}

void AMyGeometryCollectionPlayer::Play()
{
    if (Player && !Player->IsPlaying())
    {
        Player->Play();
    }
}
```

## 模块依赖

以下列出 `GeometryCollectionTracks` 模块的非标准依赖：

| 模块 | 用途 |
|---|---|
| `GeometryCollectionEngine` | 提供 `UGeometryCollectionCache` 和 `UGeometryCollectionComponent` 核心类 |
| `MovieScene` | 序列器框架基础 |
| `MovieSceneTracks` | 标准轨道类型，本模块扩展其中几何集合相关 |

其他常见模块（Core, Engine, CoreUObject）省略。

## 维护状态

### 近期更新

- 2025-09-25 `745ebb56` — Add support for override materials for geometry collection root proxies
- 2025-09-24 `787ab8b2` — Geometry collection : add cvar to disable the dialog that ask to create a Dataflow graph when opening
- 2025-09-23 `29aa54b8` — Dataflow : add settings for Dataflow editor
- 2025-09-16 `9a2a2477` — Dataflow : fix Tetrahedron rendering crashing when the source collection was split in multiple geometries
- 2025-09-06 `38d85df2` — dataflow : expose all properties of TransformCollection node as inputs

### 维护评价

插件创建于 2025-09-06，尚不足一个月，但已有 5 次实质性提交，涉及新功能（材质覆盖）、CVar、设置、Bug 修复。**处于非常活跃的初期开发阶段**。由于是实验性插件（`IsBetaVersion=true`），**API 可能还会发生较大变动**，但当前功能已经可用，推荐在原型项目中试用，并关注未来版本更新的破坏性变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GeometryCollectionPlugin)
- [官方文档](https://docs.unrealengine.com/5.3/en-US/geometry-collections-in-unreal-engine/)（通用几何集合文档，插件内序列器部分尚未单独文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GeometryCollectionPlugin/Tests)（如果存在）