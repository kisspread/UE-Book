# Take Recorder

> A suite of tools and interfaces designed for recording, reviewing and playing back takes in a virtual production environment.

| 属性 | 值 |
|---|---|
| 中文名 | 过场录制器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `CacheTrackRecorder` (Runtime), `TakeMovieScene` (Runtime), `TakeRecorder` (Runtime), `TakeRecorderEditor` (Runtime), `TakeRecorderNamingTokens` (Runtime), `TakeRecorderSources` (Runtime), `TakeSequencer` (Runtime), `TakeTrackRecorders` (Runtime), `TakesCore` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-01-11 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Takes) | |

## 用途

**Take Recorder** 是一个面向虚拟制片（Virtual Production）的综合工具集。它解决了在虚拟制片流程中，需要对演员表演、摄像机运动、动画数据等进行一次性或多次录制，并能够方便地回放、对比和选择最佳“Take”（镜头）的核心工作流问题。它将录制的数据转化为可编辑的 Sequencer 轨道和关键帧，使得录制的表演数据能够直接在引擎内进行后期调整和合成。

## 使用场景

-   你在进行虚拟制片，使用 LED 墙或绿幕配合实时渲染进行拍摄 → 使用 Take Recorder 录制演员的动作捕捉数据、面部表情以及摄像机的运动轨迹。
-   你需要为同一个镜头录制多次表演，并从中挑选最佳的一次 → 使用 Take Recorder 管理和对比不同的“Take”。
-   你需要将外部的动作捕捉设备（如 VR 头盔、控制器）的实时数据录制到 Sequencer 中 → 使用 Take Recorder 配合相应的“源”（Source）进行录制。
-   你希望录制的动画数据能够在 Sequencer 中以关键帧曲线的形式进行后期编辑和微调。

## 蓝图用法

Take Recorder 的主要功能通过编辑器界面（一个独立的面板）和 Sequencer 集成来暴露。虽然其核心逻辑在 C++ 层面，但通过 `UTakeRecorderSubsystem` 等类提供了一些蓝图可调用的接口。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start Recording` | 开始一次新的录制会话。 | `UTakeRecorderSubsystem` |
| `Stop Recording` | 停止当前的录制会话。 | `UTakeRecorderSubsystem` |
| `Get Active Recorder` | 获取当前活跃的录制器实例。 | `UTakeRecorderSubsystem` |

### 使用示例（蓝图描述）

在蓝图中，你可以通过获取 `Game Instance` 子系统 `Take Recorder Subsystem` 来控制录制流程。典型连接如下：
1.  获取 `Take Recorder Subsystem`。
2.  调用 `Start Recording` 节点，可传入一个 `UTakePreset` 资产来预设录制参数（如要录制的源、输出设置等）。
3.  在适当的时机（如用户按下按钮），调用 `Stop Recording` 节点。
4.  录制完成后，录制的数据会自动添加到 Sequencer 的当前关卡序列中，你可以像编辑普通动画一样编辑它们。

## C++ 用法

### 头文件引入

```cpp
#include "TakeRecorderSubsystem.h"
#include "TakePreset.h"
```

### 基本用法

通过子系统启动录制，需要指定一个预设（`UTakePreset`）。

```cpp
// 来源：可参考引擎内类似功能的测试或示例代码
#include "TakeRecorderSubsystem.h"

void AMyActor::StartTakeRecording()
{
    // 获取Take Recorder子系统
    UTakeRecorderSubsystem* TakeSubsystem = GEditor->GetEditorSubsystem<UTakeRecorderSubsystem>();
    if (TakeSubsystem)
    {
        // 加载或创建一个录制预设资产
        UTakePreset* Preset = LoadObject<UTakePreset>(nullptr, TEXT("/Game/MyPresets/MyTakePreset"));
        if (Preset)
        {
            // 开始录制
            UTakeRecorder* Recorder = TakeSubsystem->StartRecording(Preset);
            // 录制器可用于监控状态或提前停止
        }
    }
}
```

### 进阶用法

录制器（`UTakeRecorder`）本身提供了丰富的接口来监控录制状态和配置。更高级的用法涉及自定义录制“源”（`UTakeRecorderSource`）和“接收器”（`UTakeRecorderReceiver`），以支持新的设备或数据格式。

## Demo 示例

一个最小的 C++ 示例，展示如何通过代码启动一次使用默认设置的录制。

```cpp
// MyTakeRecorderActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyTakeRecorderActor.generated.h"

UCLASS()
class AMyTakeRecorderActor : public AActor
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "Take Recorder")
    void StartSimpleRecording();
};
```

```cpp
// MyTakeRecorderActor.cpp
#include "MyTakeRecorderActor.h"
#include "TakeRecorderSubsystem.h"
#include "TakePreset.h"

void AMyTakeRecorderActor::StartSimpleRecording()
{
    UTakeRecorderSubsystem* Subsystem = GEditor->GetEditorSubsystem<UTakeRecorderSubsystem>();
    if (!Subsystem) return;

    // 尝试使用一个在编辑器中已存在的预设
    TArray<UTakePreset*> Presets = Subsystem->GetAllPresets();
    if (Presets.Num() > 0)
    {
        UTakeRecorder* Recorder = Subsystem->StartRecording(Presets[0]);
        if (Recorder)
        {
            UE_LOG(LogTemp, Log, TEXT("Take recording started."));
            // 你可以保存 Recorder 指针以便稍后停止: Subsystem->StopRecording(Recorder);
        }
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("No Take Presets found. Please create one in the editor first."));
    }
}
```

## 模块依赖

`TakeRecorder` 及相关模块依赖众多 UE 子系统，对于使用者而言，最常见的依赖是 Sequencer 相关模块。

| 模块 | 用途 |
|---|---|
| `MovieScene` | Sequencer 的核心场景定义模块。 |
| `Sequencer` | Sequencer 编辑器框架。 |
| `LevelSequence` | 关卡序列资产，录制结果存储于此。 |
| `MovieSceneTools` | Sequencer 工具和辅助功能，Take Track Editor 需要注册到此模块。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `ee6722f8` | Take Recorder: Correcting regression where the Attach Track Recorder does not correctly record attac | 修复了附加轨道录制器无法正确记录附加关系的回归问题。 |
| 2026-05-14 | `d17111f0` | Take Recorder: Protecting against crashing on a null sub section sequence. | 增加空值检查，防止因子序列为空导致崩溃。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量截断到浮点数产生的警告。 |
| 2026-05-13 | `0c5ab24a` | Take Recorder: Adding missing WITH_EDITOR guard on log. | 在日志输出前添加缺失的编辑器宏保护。 |
| 2026-05-13 | `6aee158b` | Take Recorder: Fixing possible crash where a weak pointer could trigger an assertion due to a CastCh | 修复因弱指针转换可能触发断言导致的潜在崩溃。 |

### 维护评价

**Take Recorder** 是一个**成熟但仍在积极维护**的核心虚拟制片功能。它创建于2019年，已有约7年历史，属于引擎中的“老古董”级功能。然而，从Git日志可以看出，直到2026年5月仍有频繁的bug修复和稳定性改进（尤其是`TakeRecorder`模块），这表明它依然是Epic Games支持的关键工作流。虽然不属于实验性功能（`Installed: false` 表示默认不自动启用，但功能本身稳定），但由于其复杂性和对硬件的依赖，可能存在一些特定场景下的限制。

**推荐使用**：对于任何涉及虚拟制片和实时录制表演的项目，Take Recorder 都是官方推荐且必须使用的标准工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Takes)

---

# TakeSequencer 模块

> 该模块负责将 Take 数据集成到 Unreal 的 Sequencer 中，使其能够以轨道和关键帧的形式被查看和编辑。它注册了用于编辑 Take 数据的轨道编辑器。

| 属性 | 值 |
|---|---|
| 中文名 | 过场序列器模块 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `TakeSequencer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-01-11 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Takes/Source/TakeSequencer) | |

## 用途

**TakeSequencer** 模块是 Take Recorder 系统与 Sequencer 编辑器之间的桥梁。它的主要作用是扩展 Sequencer 的功能，使其能够识别、显示和编辑由 Take Recorder 录制生成的“Take”数据。它通过实现 `FTakeTrackEditor` 类，将 Take 数据映射为 Sequencer 中的一条自定义轨道，并支持从外部导入动画曲线和字符串属性到 Sequencer 中。

## 使用场景

-   你在 Sequencer 中打开了一个包含录制 Take 的关卡序列，希望像编辑普通动画一样编辑其中的摄像机或角色动画数据 → `TakeSequencer` 模块使得这些数据以可编辑的关键帧曲线形式呈现。
-   你开发了一个自定义的数据导入管道，需要将外部动画数据（如 FBX 中的曲线）导入到 Sequencer 的 Take 轨道中 → 可以使用 `FTakeTrackEditor` 实现的 `IMovieSceneToolsTrackImporter` 接口。

## 蓝图用法

本模块主要为 Sequencer 编辑器提供后台支持，不直接向蓝图暴露特殊节点。其效果体现在 Sequencer 编辑器界面中：当序列包含 Take 数据时，会自动出现对应的“Take”轨道，允许用户查看和编辑关键帧。

## C++ 用法

### 头文件引入

```cpp
#include "TakeSequencerModule.h"
#include "TakeTrackEditor.h" // 如果是扩展或引用
```

### 基本用法

此模块通常不需要用户直接调用。它的核心功能是通过 `IModuleInterface` 在引擎启动时自动注册到 Sequencer 的工具模块中。作为开发者，你可能关心的是如何确保该模块被正确加载。

```cpp
// 检查TakeSequencer模块是否已加载
if (FTakeSequencerModule::IsAvailable())
{
    // 模块可用，Sequencer应该已经能够显示Take轨道了
    FTakeSequencerModule& TakeSequencerModule = FTakeSequencerModule::Get();
    // ... 进行模块相关的操作（如果需要）
}
```

### 进阶用法

更深入的使用场景是扩展或模拟 `FTakeTrackEditor` 的功能，例如创建一个能够导入自定义动画格式到 Sequencer 的编辑器工具。这需要实现 `IMovieSceneToolsTrackImporter` 接口并注册。

```cpp
// 创建一个自定义的轨道导入器
class FMyCustomTrackImporter : public IMovieSceneToolsTrackImporter
{
public:
    // 实现接口方法，将导入的动画数据写入到指定的MovieScene中
    virtual bool ImportAnimatedProperty(const FString& InPropertyName, const FRichCurve& InCurve, FGuid InBinding, UMovieScene* InMovieScene) override
    {
        // 自定义导入逻辑
        // ... 创建或找到对应的UMovieSceneTakeSection，将InCurve数据添加进去
        return true;
    }
};

// 注册导入器（通常在模块启动时）
FMovieSceneToolsModule::Get().RegisterTrackImporter(MyImporterInstance);
```

## Demo 示例

展示如何创建一个简化的 Take 轨道编辑器，仅用于演示其结构。实际使用中，`TakeRecorder` 插件的 `TakeSequencer` 模块已经提供了完整的实现。

```cpp
// MySimpleTakeTrackEditor.h
#pragma once
#include "CoreMinimal.h"
#include "MovieSceneTrackEditor.h"
#include "ISequencerSection.h"

class UMySimpleTakeSection;
class UMovieSceneTakeSection;

class FMySimpleTakeTrackEditor : public FMovieSceneTrackEditor
{
public:
    FMySimpleTakeTrackEditor(TSharedRef<ISequencer> InSequencer)
        : FMovieSceneTrackEditor(InSequencer)
    {}

    static TSharedRef<ISequencerTrackEditor> CreateTrackEditor(TSharedRef<ISequencer> OwningSequencer);

    // ISequencerTrackEditor interface
    virtual FText GetDisplayName() const override;
    virtual TSharedRef<ISequencerSection> MakeSectionInterface(UMovieSceneSection& SectionObject, UMovieSceneTrack& Track, FGuid ObjectBinding) override;
    virtual bool SupportsType(TSubclassOf<UMovieSceneTrack> Type) const override;
    // ... 其他接口实现
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MovieScene` | Sequencer 核心场景定义，用于操作 Section、Track 等。 |
| `MovieSceneTools` | 提供 `IMovieSceneToolsTrackImporter` 接口，并管理轨道编辑器的注册。 |
| `TakeCore` | 提供 `UMovieSceneTakeSection` 等核心数据类型。 |

## 维护状态

### 近期更新

从提供的 Git 历史看，对 `Takes` 插件整体的更新频繁，但未单独列出 `TakeSequencer` 模块的提交。考虑到该模块是插件的核心组件，上述针对 Take Recorder 的稳定性修复很可能间接影响或包含了此模块。模块自创建以来结构稳定，主要进行维护性更新。

### 维护评价

**TakeSequencer** 模块是 **稳定且维护中的** 基础设施代码。它自插件创建之初就存在，代码结构相对固定，主要服务于将 Take 数据可视化到 Sequencer 这一特定功能。近期更新主要集中在与 Take Recorder 相关的稳定性修复上，表明它作为依赖组件得到了同步维护。对于开发者而言，它是一个可靠但无需过多关注的底层模块。