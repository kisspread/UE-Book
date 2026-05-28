# Niagara Sim Caching

> Adds support for recording and playing back Niagara simulations in sequencer via take recorder

| 属性 | 值 |
|---|---|
| 中文名 | Niagara 模拟缓存 |
| 分类 | FX |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `NiagaraSimCaching` (Runtime), `NiagaraSimCachingEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2022-09-12 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/NiagaraSimCaching) | |

## 用途

该插件为 Niagara 粒子系统提供模拟缓存功能，核心解决**复杂 Niagara 特效与 Sequencer 时间线精确同步**的问题。它允许通过 Take Recorder 将实时运行的 Niagara 模拟结果录制并缓存下来，随后在 Sequencer 中作为预录制数据进行回放。这使得艺术家可以在 Sequencer 中精确控制复杂、耗时的粒子动画的时机、剪辑和合成，无需每次都实时计算，显著提升了 Sequencer 中处理 Niagara 特效的工作流稳定性和效率。

## 使用场景

-   你在 Sequencer 中编排过场动画，其中包含复杂的、带有碰撞和流体行为的 Niagara 烟雾/火焰特效，并需要确保每帧结果绝对一致，不随性能波动。
-   你正在使用 Take Recorder 录制一段包含角色技能特效（如魔法释放）的实机动画，并希望将粒子特效的完整表现一并录制下来。
-   你需要对一段已录制的 Niagara 特效进行后期调整，例如在 Sequencer 中缩放、滑动或修剪其持续时间。

## 蓝图用法

主要功能通过 Sequencer 编辑器界面和 Take Recorder 集成实现，直接的蓝图节点较少，核心操作围绕录制器和轨道展开。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RecordSampleImpl` | 记录当前帧的 Niagara 模拟数据（由 Take Recorder 调用） | `UMovieSceneNiagaraTrackRecorder` |
| `FinalizeTrackImpl` | 完成录制并最终确定轨道数据 | `UMovieSceneNiagaraTrackRecorder` |
| `CreateTrackImpl` | 创建用于存储缓存数据的 Sequencer 轨道 | `UMovieSceneNiagaraTrackRecorder` |
| `SetRecordingEnabled` | 启用或禁用录制过程 | `UMovieSceneNiagaraTrackRecorder` |

### 使用示例（蓝图描述）

该插件通常不通过蓝图节点直接驱动，而是作为 Sequencer 和 Take Recorder 的扩展组件使用。标准工作流程如下：
1.  在 Sequencer 中，为目标 Actor 或 NiagaraComponent 添加一个 “Niagara Cache Track”。
2.  启用 Take Recorder，选择要录制的 Niagara 组件。
3.  执行录制操作。插件会创建一个 `UMovieSceneNiagaraTrackRecorder` 实例，它会在每一帧调用 `RecordSampleImpl` 来采集数据，并在录制结束时调用 `FinalizeTrackImpl` 生成缓存。
4.  录制完成后，缓存的动画数据以 Section 的形式存在于 Niagara Cache Track 上，可在 Sequencer 中像处理普通动画轨道一样进行编辑。

## C++ 用法

该插件的 API 主要用于引擎和编辑器内部集成。开发者通常通过 Sequencer 的扩展接口进行交互。

### 头文件引入

```cpp
#include "Sequencer/NiagaraCacheTrackEditor.h"
#include "Sequencer/MovieSceneNiagaraTrackRecorder.h"
```

### 基本用法

展示如何在 C++ 中创建一个 Niagara 缓存轨道录制器（通常由引擎内部框架调用）。
*参考自 `Public/Sequencer/MovieSceneNiagaraTrackRecorder.h`*

```cpp
// 假设你已经拥有一个有效的 UNiagaraComponent* MyNiagaraComp
// 和一个用于存储的 UMovieSceneNiagaraCacheTrack* TargetTrack

// 创建录制器实例
UMovieSceneNiagaraTrackRecorder* Recorder = NewObject<UMovieSceneNiagaraTrackRecorder>();

// 配置录制器（通常由 FMovieSceneNiagaraTrackRecorderFactory 完成）
// Recorder->NiagaraCacheTrack = TargetTrack;
// Recorder->SystemToRecord = MyNiagaraComp;

// 启动录制
Recorder->SetRecordingEnabled(true);

// 在后续的 Tick 中，调用 RecordSampleImpl 来记录当前帧
FQualifiedFrameTime CurrentTime = /* ... 从 Sequencer 获取当前时间 ... */;
Recorder->RecordSampleImpl(CurrentTime);

// 录制结束后
Recorder->FinalizeTrackImpl();
```

### 进阶用法

插件通过注册 Sequencer Track Editor 来集成 UI。核心类 `FNiagaraCacheTrackEditor` 负责在 Sequencer 大纲中构建菜单、创建 Section 界面和处理编辑操作。
*参考自 `Public/Sequencer/NiagaraCacheTrackEditor.h`*

```cpp
// 在插件的 StartupModule 中（通常由 INiagaraSimCachingEditorPlugin 处理）
// 绑定创建 Track Editor 的回调到 Sequencer
ISequencer& Sequencer = /* ... */;
TSharedRef<FNiagaraCacheTrackEditor> TrackEditor = MakeShared<FNiagaraCacheTrackEditor>(Sequencer.ToSharedRef());
```

## Demo 示例

以下是一个演示如何创建和配置 Niagara 轨道录制器的最小化示例框架。实际使用时，录制器通常由 Take Recorder 管理。

```cpp
// MyRecordingHelper.h
#pragma once

#include "CoreMinimal.h"
#include "Sequencer/MovieSceneNiagaraTrackRecorder.h"
#include "NiagaraComponent.h"

class FMyNiagaraCacheDemo
{
public:
    static void StartRecordingDemo(UNiagaraComponent* ComponentToRecord);
    static void StopRecordingDemo(UMovieSceneNiagaraTrackRecorder* Recorder);
};
```

```cpp
// MyRecordingHelper.cpp
#include "MyRecordingHelper.h"
#include "MovieScene.h"
#include "Tracks/MovieSceneNiagaraCacheTrack.h"

void FMyNiagaraCacheDemo::StartRecordingDemo(UNiagaraComponent* ComponentToRecord)
{
    if (!ComponentToRecord) return;

    // 1. 创建一个临时的缓存轨道（在实际流程中，这个轨道会创建在 Sequencer 的 MovieScene 上）
    UMovieSceneNiagaraCacheTrack* CacheTrack = NewObject<UMovieSceneNiagaraCacheTrack>();

    // 2. 创建并配置录制器
    UMovieSceneNiagaraTrackRecorder* Recorder = NewObject<UMovieSceneNiagaraTrackRecorder>();
    Recorder->SystemToRecord = ComponentToRecord;
    Recorder->NiagaraCacheTrack = CacheTrack;

    // 3. 启用并开始录制（这里模拟一个简单的录制循环）
    Recorder->SetRecordingEnabled(true);
    
    // 在真实应用中，OnRecordFrame 应该由 Tick 或定时器调用
    // 这里为了示例，我们假设它在下个 Tick 被调用
    // GetWorld()->GetTimerManager().SetTimerForNextTick([Recorder]() {
    //     FQualifiedFrameTime CurrentTime = /* ... */;
    //     Recorder->OnRecordFrame(CurrentTime);
    // });
    
    UE_LOG(LogTemp, Log, TEXT("Niagara Sim Caching Demo: Recording started for %s"), *ComponentToRecord->GetName());
}

void FMyNiagaraCacheDemo::StopRecordingDemo(UMovieSceneNiagaraTrackRecorder* Recorder)
{
    if (Recorder)
    {
        Recorder->SetRecordingEnabled(false);
        Recorder->FinalizeTrackImpl();
        UE_LOG(LogTemp, Log, TEXT("Niagara Sim Caching Demo: Recording finished. Track populated."));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Niagara` | 核心的 Niagara 粒子系统引擎模块 |
| `Takes` | Take Recorder 系统框架，用于录制功能集成 |
| `SequencerCore` | Sequencer 的核心数据结构和接口 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `057dbc69` | Fix crashes in PostEditChangeProperty overrides when MemberProperty is null, which occurs when Python... | 修复了当属性成员为空时（例如通过 Python 脚本访问）`PostEditChangeProperty` 覆写中的崩溃问题。 |
| 2026-04-14 | `79d7a59b` | TLazyObjectPtr Deprecation: | 处理 `TLazyObjectPtr` 的废弃警告，更新为现代 API。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 `UE_LOG` 迁移至 `UE_LOGF`，进行日志系统的现代化。 |
| 2026-01-16 | `f9a5ba2b` | Sequencer: Rename parameter from InFrameRate to InTickResolution since it’s really expecting a Tick... | Sequencer 参数重命名，将 `InFrameRate` 改为更准确的 `InTickResolution`。 |
| 2025-12-08 | `8bfcdab5` | Sequencer: Large anim mixer update and Sequencer MVVM refactor. | Sequencer 动画混合器的大型更新和 MVVM 架构重构。 |

### 维护评价

该插件处于 **活跃维护** 状态。
- **年龄**：创建于 2022 年，是一个相对较新的插件（约 3 年）。
- **更新频率**：最近一年内有连续的提交记录，更新内容以**兼容性修复、API 现代化和引擎子系统重构适配**为主，表明它紧跟引擎核心的发展步伐。
- **功能状态**：作为 Niagara 与 Sequencer 集成的官方解决方案，其核心功能稳定。更新主要是为了保持与底层引擎（Sequencer, Logging, Object System）的兼容性，而非添加新功能。
- **推荐使用**：**强烈推荐**。这是在 Sequencer 时间线中处理复杂 Niagara 特效的官方标准工作流，功能完整且持续维护，能有效提升动画和过场制作的可靠性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/NiagaraSimCaching)
- [官方文档](https://dev.epicgames.com/community/learning/tutorials/Rk9v/unreal-engine-niagara-simulation-caching-in-sequencer)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/NiagaraSimCaching/Tests) (如果存在)