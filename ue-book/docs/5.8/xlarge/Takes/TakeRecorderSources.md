# Take Recorder Sources

> 一套专为在虚拟制作环境中录制、审阅和回放 Take 而设计的工具和接口套件。

| 属性 | 值 |
|---|---|
| 中文名 | Take录制源管理器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CacheTrackRecorder` (Runtime), `TakeMovieScene` (Runtime), `TakeRecorder` (Runtime), `TakeRecorderEditor` (Runtime), `TakeRecorderNamingTokens` (Runtime), `TakeRecorderSources` (Runtime), `TakeSequencer` (Runtime), `TakeTrackRecorders` (Runtime), `TakesCore` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-01-11 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Takes) | |

## 用途

`TakeRecorderSources` 模块是 **Take Recorder** 插件的核心组成部分，负责管理和抽象不同的录制数据来源（“录制源”）。它解决的问题是：在虚拟制作（如影视拍摄）中，艺术家需要精确控制录制哪些内容（例如特定的 Actor、麦克风音频、世界状态或玩家输入），并将这些来源以统一、可配置的方式集成到 Sequencer 的 Take 录制流程中。

该模块通过定义 `UTakeRecorderSource` 的子类（如 `UTakeRecorderActorSource`、`UTakeRecorderMicrophoneAudioSource` 等），为不同的录制数据（Actor属性、音频、级别可见性等）提供了标准化的接口。它管理这些源的生命周期，处理录制前后的初始化与清理，并将录制的数据最终写入到 Level Sequence 中。它使得用户可以通过 UI 或脚本灵活地添加、移除和配置录制源，而无需关心底层 Sequencer 轨道创建的复杂细节。

## 使用场景

-   **录制演员表演**：在电影或动画制作中，你需要录制一个角色（Actor）的动画、变换和组件属性。→ 使用 `UTakeRecorderActorSource`。
-   **录制环境音效**：在拍摄现场，你需要同步录制麦克风输入的现场音效。→ 使用 `UTakeRecorderMicrophoneAudioSource`。
-   **记录动态场景状态**：你需要一个录制“快照”，自动记录场景中所有物体的状态（包括非玩家控制的物体）。→ 使用 `UTakeRecorderWorldSource` 并启用 `bAutotrackActors`。
-   **录制玩家操作**：在游戏测试中，你需要录制玩家控制器的操作输入和相机视角。→ 使用 `UTakeRecorderPlayerSource`。
-   **触发并录制其他序列**：你需要在录制主 Take 的同时，同步播放并录制另一个 Level Sequence Actor 的动画。→ 使用 `UTakeRecorderLevelSequenceSource`。
-   **记录摄像机切换**：在多摄像机拍摄场景中，你需要自动记录导演在哪个时间点切换到了哪个摄像机视角。→ 使用 `UTakeRecorderCameraCutSource`。

## 蓝图用法

`TakeRecorderSources` 模块通过 `TakeRecorderSourceHelpers` 和各个录制源类暴露了蓝图节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddActorSources` | 向指定的 Take 录制源列表添加一个或多个 Actor 作为录制源。 | `TakeRecorderSourceHelpers` |
| `RemoveActorSources` | 从录制源列表中移除一个或多个 Actor 源。 | `TakeRecorderSourceHelpers` |
| `RemoveAllActorSources` | 移除指定录制源列表中的所有 Actor 源。 | `TakeRecorderSourceHelpers` |
| `GetSourceActor` | 从通用的 `UTakeRecorderSource` 对象获取其对应的源 Actor（如果适用）。 | `TakeRecorderSourceHelpers` |
| `AddSourceForActor` | 为指定的 Actor 添加一个录制源到目标 Sources 列表。返回已添加或已存在的源。 | `UTakeRecorderActorSource` |
| `RemoveActorFromSources` | 从指定的 Sources 列表中移除与给定 Actor 关联的录制源。 | `UTakeRecorderActorSource` |
| `SetSourceActor` | 设置要录制的目标 Actor，并重置其属性录制映射。 | `UTakeRecorderActorSource` |
| `EnumerateAudioDevices` | 枚举当前系统上可用的音频输入设备。 | `UTakeRecorderMicrophoneAudioManager` |
| `GetDeviceChannelCount` | 获取当前选定音频设备的输入通道数。 | `UTakeRecorderMicrophoneAudioManager` |
| `SetAudioInputDevice` | 设置用于麦克风录制的音频输入设备及其参数。 | `UTakeRecorderMicrophoneAudioManager` |

### 使用示例（蓝图描述）

1.  **动态添加 Actor 源**：
    *   拖拽一个 `AActor` 变量到事件图表。
    *   从该变量拉出引线，连接到 `AddSourceForActor` 节点的 `InActor` 引脚。
    *   你需要一个 `UTakeRecorderSources` 对象作为 `InSources` 输入。通常可以通过 `ITakeRecorderSourcesManager` 的 `FindOrAddSources` 蓝图节点（如果存在）获取，或在自定义逻辑中创建。
    *   执行该节点后，该 Actor 将被添加到录制列表中。

2.  **配置麦克风音频源**：
    *   获取 `UTakeRecorderMicrophoneAudioManager` 的单例（通常通过 `GetMutableDefault`）。
    *   调用 `EnumerateAudioDevices` 刷新设备列表。
    *   调用 `SetAudioInputDevice` 节点，传入一个配置好的 `FAudioInputDeviceProperty` 结构体来设置目标设备。
    *   在你的录制源设置中，创建 `UTakeRecorderMicrophoneAudioSource`，其 `AudioChannel` 属性可以引用管理器中的设备信息。

## C++ 用法

`TakeRecorderSources` 主要通过其模块接口和辅助函数与外部代码交互。

### 头文件引入

```cpp
// 用于访问模块接口和注册能力
#include "ITakeRecorderSourcesModule.h"
// 用于便捷地操作录制源的辅助函数
#include "TakeRecorderSourceHelpers.h"
// 如果需要操作特定的录制源类型
#include "TakeRecorderActorSource.h"
```

### 基本用法

以下示例展示如何通过编程方式向一个 Level Sequence 添加 Actor 录制源。

```cpp
// 假设你已经有了一个 Level Sequence 和想要录制的 Actor
// 来源推断：Public/TakeRecorderSourceHelpers.h
#include "TakeRecorderSourceHelpers.h"

void AddActorToTakeRecording(ULevelSequence* InLevelSequence, AActor* InActorToRecord)
{
    // 通过 Sources Manager 为这个 Level Sequence 获取或创建 Take Recorder Sources 对象
    UTakeRecorderSources* Sources = ITakeRecorderSourcesManager::GetChecked().FindOrAddSources(InLevelSequence);
    if (Sources && InActorToRecord)
    {
        // 使用辅助函数添加 Actor 源，允许关键帧缩减并显示进度对话框
        TakeRecorderSourceHelpers::AddActorSources(Sources, {InActorToRecord}, /*bReduceKeys*/true, /*bShowProgress*/true);
    }
}
```

### 进阶用法

以下示例展示了如何注册一个自定义的“是否可录制”判断逻辑，用于在构建属性列表时过滤特定对象。

```cpp
// 来源：Public/ITakeRecorderSourcesModule.h
#include "ITakeRecorderSourcesModule.h"

// 定义一个判断函数，决定某个对象是否应该被录制到属性列表中
bool ShouldRecordObjectForMyGame(const UE::TakeRecorderSources::FCanRecordArgs& Args)
{
    // 例如：只允许记录来自特定模块或实现了特定接口的对象
    IMyRecordingInterface* MyInterface = Cast<IMyRecordingInterface>(Args.ObjectToRecord);
    return MyInterface != nullptr;
}

void RegisterMyRecordingRule()
{
    // 检查模块是否可用
    if (UE::TakeRecorderSources::ITakeRecorderSourcesModule::IsAvailable())
    {
        UE::TakeRecorderSources::ITakeRecorderSourcesModule& Module = UE::TakeRecorderSources::ITakeRecorderSourcesModule::Get();
        // 注册我们的自定义规则。HandleId 用于唯一标识此注册，以便后续取消注册。
        FName Handle = TEXT("MyGameRecordingRule");
        Module.RegisterCanRecordDelegate(Handle, UE::TakeRecorderSources::FCanRecordDelegate::CreateStatic(&ShouldRecordObjectForMyGame));
    }
}

void UnregisterMyRecordingRule()
{
    if (UE::TakeRecorderSources::ITakeRecorderSourcesModule::IsAvailable())
    {
        UE::TakeRecorderSources::ITakeRecorderSourcesModule::Get().UnregisterCanRecordDelegate(TEXT("MyGameRecordingRule"));
    }
}
```

## Demo 示例

以下是一个最小化的 C++ 示例，演示如何创建一个自定义的录制源（继承自 `UTakeRecorderSource`），并在录制开始时向 Sequencer 添加一个自定义注释轨道。

**MyCustomTakeRecorderSource.h**
```cpp
// Copyright My Game, Inc. All Rights Reserved.

#pragma once

#include "TakeRecorderSource.h"
#include "MyCustomTakeRecorderSource.generated.h"

UCLASS(MinimalAPI, Category = "MyGame")
class UMyCustomTakeRecorderSource : public UTakeRecorderSource
{
    GENERATED_BODY()

public:
    UMyCustomTakeRecorderSource(const FObjectInitializer& ObjInit);

    // 一个自定义的属性，在编辑器中可配置
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Source")
    FString CustomNote;

    // UTakeRecorderSource 接口
    virtual TArray<UTakeRecorderSource*> PreRecording(ULevelSequence* InSequence, FMovieSceneSequenceID InSequenceID, ULevelSequence* InRootSequence, FManifestSerializer* InManifestSerializer) override;
    virtual FText GetDisplayTextImpl() const override;
    virtual FText GetAddSourceDisplayTextImpl() const override;
    // ~UTakeRecorderSource 接口
};
```

**MyCustomTakeRecorderSource.cpp**
```cpp
// Copyright My Game, Inc. All Rights Reserved.

#include "MyCustomTakeRecorderSource.h"
#include "LevelSequence.h"
#include "MovieScene.h"
#include "Sections/MovieSceneCommentSection.h"
#include "Tracks/MovieSceneCommentTrack.h"

UMyCustomTakeRecorderSource::UMyCustomTakeRecorderSource(const FObjectInitializer& ObjInit)
    : Super(ObjInit)
{
    CustomNote = TEXT("Default Note");
}

TArray<UTakeRecorderSource*> UMyCustomTakeRecorderSource::PreRecording(ULevelSequence* InSequence, FMovieSceneSequenceID InSequenceID, ULevelSequence* InRootSequence, FManifestSerializer* InManifestSerializer)
{
    TArray<UTakeRecorderSource*> ExtraSources = Super::PreRecording(InSequence, InSequenceID, InRootSequence, InManifestSerializer);

    if (InSequence && !CustomNote.IsEmpty())
    {
        UMovieScene* MovieScene = InSequence->GetMovieScene();
        // 添加一个注释轨道
        UMovieSceneCommentTrack* CommentTrack = MovieScene->FindTrack<UMovieSceneCommentTrack>();
        if (!CommentTrack)
        {
            CommentTrack = MovieScene->AddTrack<UMovieSceneCommentTrack>();
        }

        if (CommentTrack)
        {
            // 添加一个注释 Section
            UMovieSceneCommentSection* CommentSection = Cast<UMovieSceneCommentSection>(CommentTrack->CreateNewSection());
            if (CommentSection)
            {
                // 设置注释文本和时间范围（这里简化为整个序列范围）
                CommentSection->SetCommentText(FText::FromString(CustomNote));
                CommentSection->SetRange(MovieScene->GetPlaybackRange());
                CommentTrack->AddSection(*CommentSection);
            }
        }
    }

    return ExtraSources;
}

FText UMyCustomTakeRecorderSource::GetDisplayTextImpl() const
{
    return NSLOCTEXT("MyTakeRecorder", "CustomSourceDisplay", "Custom Note Source");
}

FText UMyCustomTakeRecorderSource::GetAddSourceDisplayTextImpl() const
{
    return NSLOCTEXT("MyTakeRecorder", "AddCustomSource", "Add Custom Note Source");
}
```

## 模块依赖

根据模块名称和常见实践，`TakeRecorderSources` 模块依赖以下模块。由于其核心功能依赖于 `TakeRecorder` 基础库和 `TakesCore`，并最终写入 Sequencer，因此依赖如下：

| 模块 | 用途 |
|---|---|
| `TakesCore` | 提供 Take 录制系统的核心类型、接口和序列化逻辑。 |
| `TakeRecorder` | 提供 `UTakeRecorderSource` 等录制源的基类和核心录制管理逻辑。 |
| `TakeMovieScene` | 提供与 Take 相关的 MovieScene 轨道和 Section（如 `UMovieSceneTakeTrack`）。 |
| `LevelSequence` | 用于创建和操作 Level Sequence 资产。 |
| `MovieScene` | Sequencer 的核心，用于操作轨道、Section 和属性。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `ee6722f8` | Take Recorder: Correcting regression where the Attach Track Recorder does not correctly record attac | 修复了 Attach Track Recorder 无法正确录制附加关系的回归错误。 |
| 2026-05-14 | `d17111f0` | Take Recorder: Protecting against crashing on a null sub section sequence. | 防止因空的子 Section 序列导致崩溃。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量截断为浮点数的警告。 |
| 2026-05-13 | `0c5ab24a` | Take Recorder: Adding missing WITH_EDITOR guard on log. | 为日志添加了缺失的 WITH_EDITOR 宏保护。 |
| 2026-05-13 | `6aee158b` | Take Recorder: Fixing possible crash where a weak pointer could trigger an assertion due to a CastCh | 修复了一个可能因弱指针在 Cast 检查时触发断言而导致的崩溃。 |

### 维护评价

*   **活跃维护**：从近期的 git 历史来看，该模块在 **2026年5月** 仍有多次提交，内容主要是 bug 修复和回归修正，表明它仍在被积极使用和维护。
*   **稳定性**：最近的提交集中于解决崩溃、回归和警告，说明团队致力于保持模块的稳定性和可靠性。
*   **推荐使用**：作为 UE 虚拟制作（Virtual Production）工作流的核心组成部分，Take Recorder 及其 Sources 模块是进行影视级录制和动画数据捕捉的推荐方案。它功能成熟，与 Sequencer 深度集成，是相关项目的基础工具。
*   **注意事项**：虽然模块本身在维护，但使用时需要注意它与特定 UE 版本和虚拟制作管线（如 nDisplay， ICVFX）的兼容性。建议始终使用与项目引擎版本匹配的插件版本。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Takes)
- [官方文档](https://docs.unrealengine.com/en-US/working-with-media/virtual-production/record-and-playback/take-recorder/) （UE官方文档中关于Take Recorder的部分）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Takes/Source/TakeRecorderSources/Tests) （如果存在，路径可能在 `Tests` 子目录下）