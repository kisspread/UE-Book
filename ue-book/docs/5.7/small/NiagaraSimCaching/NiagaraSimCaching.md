# NiagaraSimCaching

> Adds support for recording and playing back Niagara simulations in sequencer via take recorder

| 属性 | 值 |
|---|---|
| 中文名 | Niagara缓存录制 |
| 分类 | FX |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（录制缓存资产、蓝图资源） |
| 模块 | `NiagaraSimCaching` (Runtime), `NiagaraSimCachingEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-03-18 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/NiagaraSimCaching) | |

## 用途

NiagaraSimCaching 插件在 Sequencer 中为 Niagara 粒子系统增加了**模拟状态录制与回放**功能。它允许用户在录制过场动画（Take Recorder）或手动录制时，将 Niagara 组件的每一帧模拟结果（粒子位置、速度、属性等）保存为缓存资源（`UNiagaraSimCache`），并在后续播放时直接读取缓存数据而非重新运行模拟。

这一机制解决了以下问题：

- **确定性回放**：粒子模拟可能因帧率波动、随机种子变化等产生不一致结果，缓存回放保证每次播放完全相同。
- **性能优化**：复杂粒子系统模拟开销大，缓存回放免除每帧计算，适合电影级画面。
- **编辑器 VFX 预览**：在 Sequencer 中精确预览粒子效果，便于镜头调整与合成。

## 使用场景

- **电影级过场动画**：需要精确控制粒子爆发、飘雪、火焰等效果，与镜头及音效完美对齐。
- **游戏内预渲染序列**：如剧情动画、开场动画，要求视觉一致且高性能。
- **VFX 迭代**：在编辑器中快速回放录制好的粒子缓存，避免反复重新模拟调试。
- **多镜头重拍**：使用 Take Recorder 多次录制，保留最佳镜头版本。

## 蓝图用法

本插件主要通过 **编辑器界面**（Sequencer 轨道、细节面板）操作，未暴露直接的 BlueprintCallable 函数。以下枚举类型可在蓝图中作为属性参数使用：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ENiagaraSimCacheSectionPlayMode` | 缓存回放模式：无缓存时运行模拟 / 仅显示缓存 | 全局枚举 |
| `ENiagaraSimCacheSectionStretchMode` | 缓存拉伸模式：重复数据 / 时间拉伸 | 全局枚举 |
| `SimCache` | 引用的 `UNiagaraSimCache` 资源 | `FMovieSceneNiagaraCacheParams` |
| `CacheReplayPlayMode` | 设置当前 Section 的缓存回放模式 | `FMovieSceneNiagaraCacheParams` |
| `SectionStretchMode` | 设置当前 Section 的缓存拉伸模式 | `FMovieSceneNiagaraCacheParams` |

**使用示例（蓝图编辑器描述）**  
1. 在 Sequencer 中为 Niagara 组件添加 **Niagara 缓存轨道**。  
2. 选中该轨道上的 Section，细节面板中可设置：  
   - `Sim Cache`：指向已录制好的 `UNiagaraSimCache` 资源。  
   - `Cache Replay Play Mode`：选择“仅显示缓存”（`DisplayCacheOnly`）或“无缓存时模拟”（`SimWithoutCache`）。  
   - `Section Stretch Mode`：选择缓存时长不足时的行为。  
   - `Lock Cache to Read Only`：防止意外重新录制覆盖数据。  
   - `Override Quality Level`：录制时强制使用指定画质等级。

## C++ 用法

### 头文件引入

```cpp
#include "Niagara/Sequencer/MovieSceneNiagaraCacheTrack.h"
#include "Niagara/Sequencer/MovieSceneNiagaraCacheSection.h"
```

### 基本用法

以下示例演示如何通过 C++ 在 Sequencer 中手动创建缓存轨道并添加 Section（通常用于自动化工具或高级扩展）。

```cpp
// 假设已有 UMovieScene* MovieScene 和 UWorld* World
UMovieScene* MovieScene = ...;

// 创建 Niagara 缓存轨道
UMovieSceneNiagaraCacheTrack* CacheTrack = MovieScene->AddTrack<UMovieSceneNiagaraCacheTrack>();
if (CacheTrack)
{
    // 添加 Section，指定起始帧
    FFrameNumber StartTime = ...;
    UMovieSceneNiagaraCacheSection* NewSection = Cast<UMovieSceneNiagaraCacheSection>(
        CacheTrack->AddNewAnimation(StartTime, NiagaraComponent));
    if (NewSection)
    {
        // 配置 Section 参数
        FMovieSceneNiagaraCacheParams& Params = NewSection->Params;
        Params.SimCache = LoadObject<UNiagaraSimCache>(nullptr, TEXT("/Game/caches/MySimCache.MySimCache"));
        Params.CacheReplayPlayMode = ENiagaraSimCacheSectionPlayMode::DisplayCacheOnly;
        Params.SectionStretchMode = ENiagaraSimCacheSectionStretchMode::TimeDilate;
        NewSection->SetRange(TRange<FFrameNumber>(StartTime, StartTime + 100));
    }
}
```

> 来源：参考 `UMovieSceneNiagaraCacheTrack::AddNewAnimation` 和 `FMovieSceneNiagaraCacheParams` 定义。

### 进阶用法

利用 `FMovieSceneNiagaraSectionTemplateParameter` 和 `FMovieSceneNiagaraCacheSectionTemplate` 实现自定义求值逻辑（通常配合 Sequencer 编译扩展使用）。

```cpp
// 构建 Section 模板参数
TArray<FMovieSceneNiagaraSectionTemplateParameter> TemplateParams;
FMovieSceneNiagaraSectionTemplateParameter Param;
Param.SectionRange = Section->GetRange();
Param.Params = Section->Params;
TemplateParams.Add(Param);

// 创建求值模板
FMovieSceneNiagaraCacheSectionTemplate Template(TemplateParams);
```

**录制缓存时自定义参数**：设置 `bOverrideQualityLevel` 和 `CacheRecordRateFPS` 以控制录制质量与帧率。

```cpp
#if WITH_EDITORONLY_DATA
Params.bOverrideRecordRate = true;
Params.CacheRecordRateFPS = 60.0f;
#endif
```

## Demo 示例

以下演示一个简单的 Actor 组件，在游戏运行时动态创建缓存轨道并播放录制好的缓存。

### NiagaraCachePlayer.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MovieSceneSequencePlayer.h"
#include "Niagara/Sequencer/MovieSceneNiagaraCacheTrack.h"
#include "NiagaraCachePlayer.generated.h"

UCLASS(ClassGroup = (Custom), meta = (BlueprintSpawnableComponent))
class UNiagaraCachePlayer : public UActorComponent
{
    GENERATED_BODY()

public:
    UNiagaraCachePlayer();

    // 播放指定缓存资源
    UFUNCTION(BlueprintCallable, Category = "NiagaraCache")
    void PlayCache(UNiagaraSimCache* SimCache, UMovieSceneSequence* Sequence);

protected:
    virtual void BeginPlay() override;
    virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
    TObjectPtr<UMovieSceneNiagaraCacheTrack> CachedTrack;
    TObjectPtr<UMovieSceneSequencePlayer> SequencePlayer;
};
```

### NiagaraCachePlayer.cpp

```cpp
#include "NiagaraCachePlayer.h"
#include "MovieScene.h"
#include "MovieSceneSection.h"
#include "LevelSequence.h"

UNiagaraCachePlayer::UNiagaraCachePlayer()
{
    PrimaryComponentTick.bCanEverTick = true;
}

void UNiagaraCachePlayer::PlayCache(UNiagaraSimCache* SimCache, UMovieSceneSequence* Sequence)
{
    if (!Sequence || !SimCache) return;

    // 获取或创建缓存轨道
    UMovieScene* MovieScene = Sequence->GetMovieScene();
    if (!MovieScene) return;

    // 清理旧轨道
    if (CachedTrack)
    {
        MovieScene->RemoveTrack(*CachedTrack);
        CachedTrack = nullptr;
    }

    // 创建新轨道
    CachedTrack = MovieScene->AddTrack<UMovieSceneNiagaraCacheTrack>();
    if (!CachedTrack) return;

    // 添加 Section 并设置缓存
    FFrameNumber StartTime = 0;
    UMovieSceneNiagaraCacheSection* Section = Cast<UMovieSceneNiagaraCacheSection>(
        CachedTrack->AddNewAnimation(StartTime, GetOwner()->FindComponentByClass<UNiagaraComponent>()));
    if (Section)
    {
        Section->Params.SimCache = SimCache;
        Section->Params.CacheReplayPlayMode = ENiagaraSimCacheSectionPlayMode::DisplayCacheOnly;
        Section->SetRange(TRange<FFrameNumber>(StartTime, StartTime + SimCache->GetNumFrames()));

        // 播放序列
        if (!SequencePlayer)
        {
            SequencePlayer = NewObject<UMovieSceneSequencePlayer>(this);
        }
        FMovieSceneSequencePlaybackSettings Settings;
        Settings.bPlayReverse = false;
        SequencePlayer->Initialize(Sequence, Settings);
        SequencePlayer->Play();
    }
}

void UNiagaraCachePlayer::BeginPlay()
{
    Super::BeginPlay();
}

void UNiagaraCachePlayer::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
    // 可在此处实现自定义播放控制逻辑
}
```

## 模块依赖

由于本插件主要依赖 Niagara 和 Takes，以下为其编辑器及运行时模块的特殊依赖（已省略 Core 等通用模块）：

| 模块 | 用途 |
|---|---|
| `Niagara` | 提供 Niagara 粒子系统核心功能及 `UNiagaraSimCache` 类型 |
| `Takes` | 提供 Take Recorder 录制框架，与 Sequencer 集成 |

**额外说明**：若在 C++ 中使用本插件，需在 `Build.cs` 中添加：

```cpp
PublicDependencyModuleNames.AddRange(new string[] { "Niagara", "Takes", "MovieScene", "MovieSceneTracks" });
```

## 维护状态

### 近期更新

- 2025-08-05 `ae82625a` — Sequencer: Deprecate SetObjectGuid and GetBindings and FMovieSceneBinding constructors. （涉及插件适配）
- 2025-06-26 `a2e75189` — Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. （编译系统优化）
- 2025-05-31 `52e3dac1` — Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars. (API 规范修正)
- 2025-04-23 `6ae57335` — Used UnrealGame build target to find and convert all files to have dllstorage on methods. (API 导出规范)
- 2025-03-18 `f1935581` — Sequencer: Use static_cast<int32> instead of int. (代码风格修正)

### 维护评价

- **创建时间**：2025-03-18，至今约 1 年。
- **近期活动**：最近一次实质性更新在 2025-08-05（Sequencer API 废弃适配），其他多为编译规范调整。
- **状态评估**：插件仍处于活跃维护期，Epic 定期适配最新引擎 API。目前没有已知重大 Bug 或废弃标记。
- **推荐度**：✅ 推荐使用，尤其是需要精确控制 Niagara 粒子回放的电影级或预渲染项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/NiagaraSimCaching)
- [官方文档](https://dev.epicgames.com/community/learning/tutorials/Rk9v/unreal-engine-niagara-simulation-caching-in-sequencer)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/NiagaraSimCaching/Tests)（如有）