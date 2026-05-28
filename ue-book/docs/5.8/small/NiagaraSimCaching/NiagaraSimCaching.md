# NiagaraSimCaching

> Adds support for recording and playing back Niagara simulations in sequencer via take recorder

| 属性 | 值 |
|---|---|
| 中文名 | 尼亚加拉模拟缓存 |
| 分类 | FX |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、配置数据） |
| 模块 | `NiagaraSimCaching` (Runtime), `NiagaraSimCachingEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2022-09-12 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/NiagaraSimCaching) | |

## 用途

这个插件解决了在电影级镜头（Cinematics）制作中，精确控制复杂 Niagara 粒子效果的核心问题。它的核心功能是将 Niagara 系统的模拟结果（如粒子位置、速度、颜色等）**录制**到名为 `UNiagaraSimCache` 的资产中，然后在 Sequencer 的时间轴上对这个缓存资产进行**播放**。

它存在的主要价值在于：
1.  **确定性回放**：避免了实时模拟可能因帧率波动或并行处理导致的细微不一致，确保每次播放镜头时粒子效果完全一致，这对于最终渲染至关重要。
2.  **性能优化**：在复杂场景中，缓存播放比实时运行粒子模拟消耗更少的运行时性能。
3.  **离线控制**：动画师可以在 Sequencer 中像控制骨骼动画一样，精确地调整粒子效果的入出点、播放速度（拉伸模式），甚至锁定录制结果以防止误操作。

## 使用场景

-   你正在为一个预渲染的过场动画或游戏内电影级镜头制作特效 → 使用此插件在 Sequencer 中录制关键镜头的 Niagara 模拟，然后进行精确的编排和剪辑。
-   你需要一个复杂粒子效果在多个镜头中表现完全一致 → 使用此插件录制一次，然后在不同的 Sequencer 序列中重复播放缓存。
-   你希望优化包含大量粒子效果的场景的运行时性能 → 对于不参与实时交互、主要起装饰作用的复杂粒子系统，可以预录制并在游戏中播放缓存。

## 蓝图用法

此插件主要面向 Sequencer 和编辑器操作，直接暴露给蓝图的运行时函数较少。其功能主要通过 Sequencer 的 Cache Track 和属性面板进行配置。

### 核心类型与枚举

| 节点/类型 | 说明 | 所在类/文件 |
|---|---|---|
| `ENiagaraSimCacheSectionPlayMode` | 当序列中没有缓存数据时的行为模式：`SimWithoutCache`（运行实时模拟）或 `DisplayCacheOnly`（禁用组件）。 | `MovieSceneNiagaraCacheSection.h` |
| `ENiagaraSimCacheSectionStretchMode` | 缓存片段在时间轴上被拉伸时的行为：`Repeat`（重复播放）或 `TimeDilate`（拉伸时间）。 | `MovieSceneNiagaraCacheSection.h` |

### 参数配置 (`FMovieSceneNiagaraCacheParams`)

此结构体用于在 Sequencer 的 Cache Section 属性面板中配置录制和播放参数，通常通过编辑器 UI 操作，而非直接在蓝图节点中创建。

-   `SimCache`: 指向要录制/播放的 `UNiagaraSimCache` 资产。
-   `bLockCacheToReadOnly`: 锁定缓存，防止被意外覆盖。
-   `bOverrideQualityLevel` & `RecordQualityLevel`: 录制时可指定引擎质量等级，用于模拟不同画质下的效果。
-   `CacheReplayPlayMode`: 无数据时的播放模式（见上述枚举）。
-   `SectionStretchMode`: 片段拉伸模式（见上述枚举）。

### 使用示例（蓝图描述）

在 Sequencer 中操作：
1.  添加一个 Niagara Component 轨道。
2.  右键点击轨道，选择“Add New Cache Section”。
3.  在右侧细节面板中，设置 `SimCache` 资产（可新建或选择现有资产）。
4.  根据需要设置 `CacheReplayPlayMode` 和 `SectionStretchMode`。
5.  使用 Take Recorder 或 Sequencer 的录制功能来录制模拟。

## C++ 用法

### 头文件引入

```cpp
// 核心类型
#include "Niagara/Sequencer/MovieSceneNiagaraCacheSection.h"
#include "Niagara/Sequencer/MovieSceneNiagaraCacheTrack.h"

// 如果需要与缓存资产交互，需要引用 Niagara 模块
#include "NiagaraSimCache.h"
```

### 基本用法：与缓存系统交互

虽然主要通过编辑器 UI 操作，但理解底层类型有助于调试和扩展。
*来源: `Public/Niagara/Sequencer/MovieSceneNiagaraCacheSection.h`*

```cpp
// 获取一个缓存片段（Section）的参数
UMovieSceneNiagaraCacheSection* CacheSection = ...; // 通常从 Sequencer 轨道获取
FMovieSceneNiagaraCacheParams& Params = CacheSection->Params;

// 检查并应用播放模式
if (Params.CacheReplayPlayMode == ENiagaraSimCacheSectionPlayMode::DisplayCacheOnly)
{
    // 在没有缓存数据时，对应的 NiagaraComponent 应该被禁用
}

// 检查片段是否被锁定
if (Params.bLockCacheToReadOnly)
{
    UE_LOG(LogNiagaraSimCaching, Warning, TEXT("This cache section is locked and cannot be rerecorded."));
}
```

### 进阶用法：程序化创建缓存轨道（概念性）

以下代码展示了如何通过 C++ 在 Sequencer 中创建和配置一个缓存轨道，这在编写自动化工具时可能有用。
*注意：实际 Sequencer 的程序化 API 较为复杂，此处为概念演示。*

```cpp
// 假设我们已经有了一个 UMovieScene 和 ULevelSequence 资产
UMovieScene* MovieScene = MyLevelSequence->GetMovieScene();

// 创建缓存轨道
UMovieSceneNiagaraCacheTrack* CacheTrack = Cast<UMovieSceneNiagaraCacheTrack>(
    MovieScene->AddTrack(UMovieSceneNiagaraCacheTrack::StaticClass(), MyNiagaraComponentBindingID)
);

if (CacheTrack)
{
    // 在某一帧添加一个缓存段
    FFrameNumber StartTime(0);
    UMovieSceneNiagaraCacheSection* NewSection = Cast<UMovieSceneNiagaraCacheSection>(
        CacheTrack->AddNewAnimation(StartTime, MyNiagaraComponent)
    );

    // 配置段参数
    if (NewSection)
    {
        FMovieSceneNiagaraCacheParams& Params = NewSection->Params;
        // 假设已经创建或加载了一个 SimCache 资产
        Params.SimCache = MyNiagaraSimCacheAsset;
        Params.CacheReplayPlayMode = ENiagaraSimCacheSectionPlayMode::DisplayCacheOnly;
        Params.bLockCacheToReadOnly = false; // 允许重新录制
    }
}
```

## Demo 示例

以下是一个最小的示例，演示了如何定义一个自定义类，该类可以持有 `FMovieSceneNiagaraCacheParams` 并初始化默认值。

**.h 文件**
```cpp
// MyCacheManager.h
#pragma once
#include "CoreMinimal.h"
#include "MovieSceneNiagaraCacheSection.h"
#include "MyCacheManager.generated.h"

UCLASS(BlueprintType)
class UMyCacheManager : public UObject
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "NiagaraCache")
    FMovieSceneNiagaraCacheParams CacheParams;

    UMyCacheManager();
};
```

**.cpp 文件**
```cpp
// MyCacheManager.cpp
#include "MyCacheManager.h"
#include "NiagaraSimCache.h" // 确保能访问 UNiagaraSimCache

UMyCacheManager::UMyCacheManager()
{
    // 设置一些合理的默认值
    CacheParams.bLockCacheToReadOnly = false;
    CacheParams.CacheReplayPlayMode = ENiagaraSimCacheSectionPlayMode::DisplayCacheOnly;
    CacheParams.SectionStretchMode = ENiagaraSimCacheSectionStretchMode::TimeDilate;
    CacheParams.bOverrideQualityLevel = true;
    CacheParams.RecordQualityLevel = EPerQualityLevels::Cinematic;

    // 在实际使用中，这里会创建或加载一个有效的 UNiagaraSimCache 资产
    // CacheParams.SimCache = LoadObject<UNiagaraSimCache>(nullptr, TEXT("/Game/Path/To/MyCache"));
}
```

## 模块依赖

从 `Build.cs` 文件推断，此插件依赖以下**独特**模块（省略了 Core, CoreUObject, Engine 等通用模块）：

| 模块 | 用途 |
|---|---|
| `Niagara` | 核心依赖，用于访问 Niagara 系统、组件和模拟缓存资产 (`UNiagaraSimCache`)。 |
| `Takes` | 用于与 Take Recorder 集成，实现通过录制流程创建缓存。 |
| `Sequencer` / `MovieScene` | 核心依赖，用于构建 Sequencer 轨道、片段和播放逻辑。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `057dbc69` | Fix crashes in PostEditChangeProperty overrides when MemberProperty is null, which occurs when Pytho | 修复了当属性为空时（例如在Python脚本操作中）`PostEditChangeProperty` 导致的崩溃。 |
| 2026-04-14 | `79d7a59b` | TLazyObjectPtr Deprecation: | 跟随引擎对 `TLazyObjectPtr` 的弃用，进行了代码迁移。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移为新的 `UE_LOGF` 格式。 |
| 2026-01-16 | `f9a5ba2b` | Sequencer: Rename parameter from InFrameRate to InTickReoslution since it's really expecting a Tick | 修正了 Sequencer 参数名，将 `InFrameRate` 重命名为更准确的 `InTickResolution`。 |
| 2025-12-08 | `8bfcdab5` | Sequencer: Large anim mixer update and Sequencer MVVM refactor. | 参与了 Sequencer 动画混合器的重大更新和 MVVM 架构重构。 |

### 维护评价

-   **活跃维护**：该插件仍在积极维护中。最近的提交（2026年5月）是实质性的问题修复，而非简单的编译适配。
-   **功能稳定**：创建于2022年，已有约3年历史，功能集相对成熟稳定。近期提交主要集中在引擎大版本适配（如弃用API迁移、架构重构）和编辑器健壮性改进（如修复崩溃）。
-   **推荐使用**：对于需要在 Sequencer 中精确控制 Niagara 粒子效果的电影或高质量过场动画制作，这是一个**推荐使用**的官方插件。它稳定、集成度高，并且持续跟随引擎核心模块（如 Sequencer）更新。
-   **注意事项**：该插件与 `Takes` 和 `Niagara` 插件强耦合，使用时需确保它们也被启用。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/NiagaraSimCaching)
-   [官方文档](https://dev.epicgames.com/community/learning/tutorials/Rk9v/unreal-engine-niagara-simulation-caching-in-sequencer)