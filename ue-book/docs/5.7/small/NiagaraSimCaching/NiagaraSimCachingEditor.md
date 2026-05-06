# NiagaraSimCaching

> Adds support for recording and playing back Niagara simulations in sequencer via take recorder

| 属性 | 值 |
|---|---|
| 中文名 | Niagara 模拟缓存录制 |
| 分类 | FX |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `NiagaraSimCaching` (Runtime), `NiagaraSimCachingEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-03-18 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/NiagaraSimCaching) | |

## 用途

NiagaraSimCaching 插件扩展了 Take Recorder 系统，使得在 Sequencer 中录制和回放 Niagara 粒子系统模拟成为可能。传统的 Sequencer 录制只能记录 actor 属性或关键帧，而 Niagara 模拟是 CPU/GPU 实时计算的，无法简单回放。该插件通过缓存每帧的模拟状态（例如粒子位置、速度）到 Sequencer 轨道的缓存片段中，从而允许在回放时直接读取缓存数据，无需重新模拟。这解决了以下问题：

- 需要精确回放复杂的粒子效果，避免因性能波动导致效果不一致。
- 在过场动画或录制过程中，希望将 Niagara 模拟作为场景的一部分进行录制，并在后续编辑中任意时间点预览。
- 提高编辑器性能，特别是在预览复杂粒子系统时可通过缓存替代实时模拟。

## 使用场景

- 你正在使用 Take Recorder 录制一个包含 Niagara 粒子效果的过场动画 → 此插件允许你将 Niagara 组件作为可录制对象，自动在 Sequencer 上创建 Niagara Cache Track。
- 你需要播放预先录制的粒子模拟，以获得确定性的回放效果 → 使用编辑器内缓存捕获功能，将模拟结果保存到缓存资产中。
- 作为 Niagara 开发者，希望测试不同时间点的模拟快照 → 利用 Cache Track Editor 提供的录制功能手动记录关键帧。

## 蓝图用法

该模块以 C++ 实现为主，仅在 Sequencer 编辑环境中提供功能，未暴露 `BlueprintCallable` 或 `BlueprintReadWrite` 属性到蓝图中。Niagara Cache Track 的录制与播放完全在 Sequencer UI 和 C++ 级别处理。

> **注意**：`UMovieSceneNiagaraTrackRecorder` 继承自 `UMovieSceneTrackRecorder`，其核心函数（如 `RecordSampleImpl`, `CreateTrackImpl`）均为 `UE_API` 而非 `UFUNCTION`，因此无法从蓝图直接调用。同样，`FNiagaraCacheTrackEditor` 是纯 C++ 类，不可在蓝图中使用。

### 编辑器中操作（蓝图不可用）

录制操作通过 Sequencer 的轨道菜单或 Take Recorder 自动创建。用户需：
1. 在 Sequencer 中为 Niagara Component 添加 Niagara Cache Track。
2. 使用 Take Recorder 录制 Niagara 的模拟缓存。
3. 回放时自动使用缓存数据。

> 具体操作步骤请参阅官方教程：https://dev.epicgames.com/community/learning/tutorials/Rk9v/unreal-engine-niagara-simulation-caching-in-sequencer

## C++ 用法

### 头文件引入

```cpp
#include "NiagaraSimCachingEditor/Public/Sequencer/MovieSceneNiagaraTrackRecorder.h"
#include "NiagaraSimCachingEditor/Public/Sequencer/NiagaraCacheTrackEditor.h"
```

### 基本用法

#### 1. 创建 Niagara Cache 轨道

当在 Sequencer 中绑定一个 Niagara 组件并为其添加 Niagara Cache Track 时，`FMovieSceneNiagaraTrackRecorderFactory` 会自动处理。工厂类的 `CanRecordObject` 和 `CreateTrackRecorderForObject` 用于判断对象是否可录制并创建对应的 Recorder。

```cpp
// 检查给定对象是否可以录制为 Niagara Cache Track
bool FMovieSceneNiagaraTrackRecorderFactory::CanRecordObject(UObject* InObjectToRecord) const
{
    // 内部判断逻辑：是否为 UNiagaraComponent
    // 源码路径：Source/NiagaraSimCachingEditor/Private/MovieSceneNiagaraTrackRecorder.cpp
}
```

#### 2. 手动创建 Track Recorder

如果需要通过代码触发录制，可以创建 `FMovieSceneNiagaraTrackRecorderFactory` 并调用 `CreateTrackRecorderForObject` 获得 `UMovieSceneNiagaraTrackRecorder` 实例，然后手动驱动录制流程。

```cpp
// 创建录制器工厂
FMovieSceneNiagaraTrackRecorderFactory Factory;

// 假设已有一个 NiagaraComponent
UNiagaraComponent* NiagaraComp = ...;

// 创建录制器
UMovieSceneTrackRecorder* Recorder = Factory.CreateTrackRecorderForObject();
if (UMovieSceneNiagaraTrackRecorder* NiagaraRecorder = Cast<UMovieSceneNiagaraTrackRecorder>(Recorder))
{
    // 开始录制（设置开始时间等）
    NiagaraRecorder->SetSectionStartTimecodeImpl(...);
    NiagaraRecorder->CreateTrackImpl();
    // 每帧调用 RecordSampleImpl
    NiagaraRecorder->RecordSampleImpl(CurrentFrameTime);
    // 最后 Finalize
    NiagaraRecorder->FinalizeTrackImpl();
}
```

#### 3. 自定义缓存轨道编辑器

`FNiagaraCacheTrackEditor` 提供了 Sequencer 中 Niagra Cache Track 的 UI 和交互逻辑。可通过 `CreateTrackEditor` 静态方法注册到 Sequencer。

```cpp
// 在模块加载时注册自定义轨道编辑器
void MyModule::StartupModule()
{
    ISequencerTrackEditor::RegisterTrackEditor(FOnCreateTrackEditor::CreateStatic(&FNiagaraCacheTrackEditor::CreateTrackEditor));
}
```

### 进阶用法

#### 结合 Take Recorder 进行录制

该插件设计为与 Take Recorder 深度集成。`FMovieSceneNiagaraTrackRecorderFactory` 同时实现了 `CreateTrackRecorderForCacheTrack` 用于从已有的缓存轨道回放。在 Take Recorder 录制过程中，会自动检测场景中的 Niagara 组件并为其创建缓存轨道。

```cpp
// 工厂类的 CreateTrackRecorderForCacheTrack 用于处理缓存轨道（回放时）
UMovieSceneTrackRecorder* FMovieSceneNiagaraTrackRecorderFactory::CreateTrackRecorderForCacheTrack(
    IMovieSceneCachedTrack* CachedTrack,
    const TObjectPtr<ULevelSequence>& Sequence,
    const TSharedPtr<ISequencer>& Sequencer) const
{
    // 实现细节：创建 UMovieSceneNiagaraTrackRecorder 并关联到 CachedTrack
    // 源码路径：Source/NiagaraSimCachingEditor/Private/MovieSceneNiagaraTrackRecorder.cpp
}
```

#### 轨道编辑器中的录制按钮

`FNiagaraCacheTrackEditor` 的 `BuildTrackContextMenu` 和 `RecordCacheTrack` 允许用户在轨道上下文菜单中手动触发录制，最终调用 `AddKeyInternal` 将当前帧缓存写入。

```cpp
// 处理录制按钮点击
FReply FNiagaraCacheTrackEditor::RecordCacheTrack(IMovieSceneCachedTrack* CachedTrack)
{
    // 内部调用 Sequencer 的录制机制
    // 源码路径：Source/NiagaraSimCachingEditor/Private/NiagaraCacheTrackEditor.cpp
}
```

## Demo 示例

以下是一个完整的 C++ 模块示例，演示如何通过代码创建 Niagara Cache Track 并录制单帧缓存。假设已有 Sequencer 实例和 NiagaraComponent。

### MyModule.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleInterface.h"

class UMovieSceneNiagaraTrackRecorder;
class UNiagaraComponent;

class FMyCacheDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

    void RecordNiagaraCache(UNiagaraComponent* NiagaraComp, UMovieSceneSequence* Sequence, FFrameNumber StartFrame);
};
```

### MyModule.cpp

```cpp
#include "MyModule.h"
#include "NiagaraSimCachingEditor/Public/Sequencer/MovieSceneNiagaraTrackRecorder.h"
#include "MovieScene.h"
#include "LevelSequence.h"
#include "ISequencer.h"
#include "ISequencerModule.h"

IMPLEMENT_MODULE(FMyCacheDemoModule, MyCacheDemoModule);

void FMyCacheDemoModule::StartupModule()
{
}

void FMyCacheDemoModule::ShutdownModule()
{
}

void FMyCacheDemoModule::RecordNiagaraCache(UNiagaraComponent* NiagaraComp, UMovieSceneSequence* Sequence, FFrameNumber StartFrame)
{
    // 创建 Track Recorder
    FMovieSceneNiagaraTrackRecorderFactory Factory;
    if (!Factory.CanRecordObject(NiagaraComp))
    {
        UE_LOG(LogTemp, Error, TEXT("Cannot record this Niagara component"));
        return;
    }

    UMovieSceneTrackRecorder* RecorderObj = Factory.CreateTrackRecorderForObject();
    if (!RecorderObj)
    {
        return;
    }

    UMovieSceneNiagaraTrackRecorder* NiagaraRecorder = Cast<UMovieSceneNiagaraTrackRecorder>(RecorderObj);
    if (!NiagaraRecorder)
    {
        return;
    }

    // 手动模拟录制流程（实际使用中应通过 Take Recorder 驱动）
    // 设置开始时间（这里仅示例）
    NiagaraRecorder->SetSectionStartTimecodeImpl(FTimecode(0, 0, 0, 0, false), StartFrame);

    // 创建 Track 和 Section（内部会调用 CreateTrackImpl）
    NiagaraRecorder->CreateTrackImpl();

    // 假设当前时间为 StartFrame，记录一帧模拟
    FQualifiedFrameTime FrameTime(StartFrame, FFrameRate(30, 1));
    NiagaraRecorder->RecordSampleImpl(FrameTime);

    // 结束录制
    NiagaraRecorder->FinalizeTrackImpl();

    // 此时 Sequence 中将包含一个 Niagara Cache 轨道及一帧缓存
}
```

> **注意**：上述示例仅为演示 API 调用方式，实际应用中应使用 Take Recorder 的 `UTakeRecorder` 或 Sequencer 录制功能，而非直接手动调用。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Takes` | 提供 Take Recorder 框架，实现录制流程 |
| `Niagara` | Niagara 粒子系统核心模块，提供 `UNiagaraComponent` 等 |
| `MovieSceneTracks`（隐式依赖） | Sequencer 轨道类型，包含 `UMovieSceneNiagaraCacheTrack` |
| `MovieSceneTools`（隐式依赖） | Sequencer 编辑器工具，实现 `FNiagaraCacheTrackEditor` |

> **常见依赖省略**：Core, CoreUObject, Engine, Slate, SlateCore, UMG, InputCore, UnrealEd, EditorSubsystem, DeveloperSettings 等标准模块未列出。

## 维护状态

### 近期更新

| 日期 | 提交 Hash | 说明 |
|---|---|---|
| 2025-08-05 | `ae82625a` | Sequencer: 弃用 `SetObjectGuid` 和 `GetBindings` 以及部分构造器；适配新 API |
| 2025-06-26 | `a2e75189` | 添加 `UE_INLINE_GENERATED_CPP_BY_NAME` 宏到对应 `.gen.cpp` 文件的源文件 |
| 2025-05-31 | `52e3acd1` | 使用 UnrealCodeFixup 更新头文件，将 dllstorage 从类型移到方法/静态变量 |
| 2025-04-23 | `6ae57335` | 使用 UnrealGame 构建目标查找并转换所有文件，将 dllstorage 从类型移到方法/静态变量 |
| 2025-03-18 | `f1935581` | Sequencer: 使用 `static_cast<int32>` 替代 `int` |

### 维护评价

- **创建时间**：2025年3月，距今不到1年，属于新插件。
- **近期更新**：2025年8月仍有活跃提交，内容涉及 Sequencer API 适配和代码规范调整，说明插件正随着引擎更新进行维护。
- **功能稳定性**：由于是相对较新的功能，可能存在未发现的边缘情况，但官方已在引擎中默认启用，推荐用于需要录制 Niagara 模拟的场景。
- **已知限制**：目前仅支持通过 Take Recorder 录制，不支持直接通过蓝图调用；部分高级编辑功能（如缓存预览）仍依赖 Sequencer UI。
- **推荐使用**：是 ✅。对于需要回放确定性 Niagara 效果的过场动画或录制场景，NiagaraSimCaching 是标准解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/NiagaraSimCaching)
- [官方教程](https://dev.epicgames.com/community/learning/tutorials/Rk9v/unreal-engine-niagara-simulation-caching-in-sequencer)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/NiagaraSimCaching/Tests)（可能为空，实际测试位于引擎测试目录）