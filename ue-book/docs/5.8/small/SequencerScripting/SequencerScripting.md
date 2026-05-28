# Sequencer Scripting

> Python and editor utility scripting extensions for sequencer and movie scenes

| 属性 | 值 |
|---|---|
| 中文名 | 序列器脚本 |
| 分类 | Scripting |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `SequencerScripting` (Runtime), `SequencerScriptingEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-05-09 |
| 年龄标签 | 🏛️ 文物（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/SequencerScripting) | |

## 用途

SequencerScripting 将 UE 的 Sequencer（序列器/过场动画编辑器）核心数据结构暴露为脚本友好的 API，支持蓝图和 Python 两种脚本环境。它解决的核心问题是：**通过代码批量创建、修改、查询 Sequencer 序列及其轨道/通道/关键帧数据**。

该插件在 Sequencer 的底层 C++ 数据模型之上，构建了一套面向脚本的包装层（Scripting Layer），将 `FMovieSceneFloatChannel`、`FMovieSceneDoubleChannel` 等内部通道类型包装为蓝图可用的 `UMovieSceneScriptingFloatChannel`、`UMovieSceneScriptingDoubleChannel` 等对象。所有对脚本对象的修改会直接同步到底层数据结构，实现双向绑定。

主要能力包括：
- 创建和管理 Level Sequence、Master Track、Object Binding（Possessable/Spawnable）
- 操作各种类型的动画通道（Float、Double、Bool、Integer、String、Text、Event、ActorReference、ObjectPath、Particle、Byte/Enum）
- 对关键帧进行增删改查、设置切线/插值模式
- 管理序列的播放范围、显示率、Tick 分辨率
- 管理文件夹、标记帧、条件求值等辅助功能
- 通过扩展库（Extension Libraries）将方法"提升"到原生类型上，使蓝图和 Python 调用体验更自然

## 使用场景

- 你需要通过 Python 脚本批量生成大量过场动画序列 → 用 SequencerScripting
- 你需要在编辑器工具中程序化地创建关键帧动画 → 用 SequencerScripting
- 你需要通过蓝图在运行时动态修改 Sequencer 轨道数据 → 用 SequencerScripting
- 你需要实现自动化的镜头/动画批处理流水线 → 用 SequencerScripting
- 你需要通过代码查询和遍历序列中的所有绑定、轨道、通道 → 用 SequencerScripting
- 你需要在无人值守环境（Commandlet）中处理 Level Sequence 资产 → 用 SequencerScripting

## 蓝图用法

本插件大量使用 `ScriptMethod` 元数据将静态函数库的方法"提升"到目标类型上，因此在蓝图中你会看到这些函数直接出现在 Sequencer 相关对象的右键菜单中。

### 核心节点

#### 序列操作（UMovieSceneSequenceExtensions）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetMovieScene` | 获取序列的 MovieScene 数据对象 | `UMovieSceneSequenceExtensions` |
| `GetTracks` | 获取序列中的所有轨道 | `UMovieSceneSequenceExtensions` |
| `FindTracksByType` | 按类型查找轨道 | `UMovieSceneSequenceExtensions` |
| `AddTrack` | 向序列添加新轨道 | `UMovieSceneSequenceExtensions` |
| `RemoveTrack` | 从序列移除轨道 | `UMovieSceneSequenceExtensions` |
| `GetDisplayRate` / `SetDisplayRate` | 获取/设置显示帧率 | `UMovieSceneSequenceExtensions` |
| `GetTickResolution` / `SetTickResolution` | 获取/设置 Tick 分辨率 | `UMovieSceneSequenceExtensions` |
| `MakeRange` / `MakeRangeSeconds` | 创建时间范围 | `UMovieSceneSequenceExtensions` |
| `GetPlaybackStart` / `SetPlaybackEnd` | 获取/设置播放范围 | `UMovieSceneSequenceExtensions` |
| `FindOrAddMasterTrack` | 查找或添加主轨道 | `UMovieSceneSequenceExtensions` |
| `AddMarkedFrame` / `GetMarkedFrames` | 管理标记帧 | `UMovieSceneSequenceExtensions` |

#### 绑定操作（UMovieSceneBindingExtensions）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetId` | 获取绑定的 GUID | `UMovieSceneBindingExtensions` |
| `GetDisplayName` / `SetDisplayName` | 获取/设置显示名称 | `UMovieSceneBindingExtensions` |
| `GetTracks` | 获取绑定下的所有轨道 | `UMovieSceneBindingExtensions` |
| `AddTrack` | 向绑定添加轨道 | `UMovieSceneBindingExtensions` |
| `RemoveTrack` | 从绑定移除轨道 | `UMovieSceneBindingExtensions` |
| `GetChildPossessables` | 获取子 Possessable | `UMovieSceneBindingExtensions` |
| `GetParent` / `SetParent` | 获取/设置父绑定 | `UMovieSceneBindingExtensions` |
| `MoveBindingContents` | 迁移绑定内容 | `UMovieSceneBindingExtensions` |

#### 轨道操作（UMovieSceneTrackExtensions）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddSection` | 向轨道添加 Section | `UMovieSceneTrackExtensions` |
| `GetSections` | 获取轨道的所有 Section | `UMovieSceneTrackExtensions` |
| `RemoveSection` | 从轨道移除 Section | `UMovieSceneTrackExtensions` |
| `SetDisplayName` / `GetDisplayName` | 设置/获取轨道显示名 | `UMovieSceneTrackExtensions` |
| `SetColorTint` / `GetColorTint` | 设置/获取轨道颜色 | `UMovieSceneTrackExtensions` |

#### Section 操作（UMovieSceneSectionExtensions）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `HasStartFrame` / `HasEndFrame` | 查询是否有起止帧 | `UMovieSceneSectionExtensions` |
| `GetStartFrame` / `GetEndFrame` | 获取起止帧号 | `UMovieSceneSectionExtensions` |
| `SetRange` / `SetRangeSeconds` | 设置时间范围 | `UMovieSceneSectionExtensions` |
| `GetAllChannels` | 获取 Section 的所有通道 | `UMovieSceneSectionExtensions` |
| `GetChannelsByType` | 按类型获取通道 | `UMovieSceneSectionExtensions` |
| `GetChannel` | 按名称获取通道 | `UMovieSceneSectionExtensions` |

#### 通道与关键帧操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddKey` | 向通道添加关键帧 | 各 `UMovieSceneScripting*Channel` |
| `RemoveKey` | 从通道移除关键帧 | 各 `UMovieSceneScripting*Channel` |
| `GetKeys` / `GetKeysByIndex` | 获取通道的关键帧 | 各 `UMovieSceneScripting*Channel` |
| `GetNumKeys` | 获取关键帧数量 | 各 `UMovieSceneScripting*Channel` |
| `EvaluateKeys` | 按范围求值关键帧 | 各 `UMovieSceneScripting*Channel` |
| `SetDefault` / `GetDefault` | 设置/获取通道默认值 | 各 `UMovieSceneScripting*Channel` |
| `HasDefault` | 查询是否有默认值 | 各 `UMovieSceneScripting*Channel` |
| `RemoveDefault` | 移除默认值 | 各 `UMovieSceneScripting*Channel` |
| `Transform` | 对关键帧进行偏移/缩放变换 | 各 `UMovieSceneScripting*Channel` |
| `GetTime` / `SetTime` | 获取/设置关键帧时间 | 各 `UMovieSceneScripting*Key` |
| `GetValue` / `SetValue` | 获取/设置关键帧值 | 各 `UMovieSceneScripting*Key` |

#### 文件夹操作（UMovieSceneFolderExtensions）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetFolderName` / `SetFolderName` | 获取/设置文件夹名 | `UMovieSceneFolderExtensions` |
| `GetChildFolders` / `AddChildFolder` | 管理子文件夹 | `UMovieSceneFolderExtensions` |
| `GetChildTracks` / `AddChildTrack` | 管理文件夹内轨道 | `UMovieSceneFolderExtensions` |
| `GetChildObjectBindings` / `AddChildObjectBinding` | 管理文件夹内绑定 | `UMovieSceneFolderExtensions` |

#### 条件操作（UMovieSceneConditionExtensions）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetSectionCondition` / `SetSectionCondition` | 获取/设置 Section 条件 | `UMovieSceneConditionExtensions` |
| `GetTrackCondition` / `SetTrackCondition` | 获取/设置轨道条件 | `UMovieSceneConditionExtensions` |
| `GetTrackRowCondition` / `SetTrackRowCondition` | 获取/设置轨道行条件 | `UMovieSceneConditionExtensions` |

### 支持的通道类型

| 通道类型 | Key 类型 | 值类型 |
|---|---|---|
| `UMovieSceneScriptingFloatChannel` | `UMovieSceneScriptingFloatKey` | `float` |
| `UMovieSceneScriptingDoubleChannel` | `UMovieSceneScriptingDoubleKey` | `double` |
| `UMovieSceneScriptingBoolChannel` | `UMovieSceneScriptingBoolKey` | `bool` |
| `UMovieSceneScriptingIntegerChannel` | `UMovieSceneScriptingIntegerKey` | `int32` |
| `UMovieSceneScriptingStringChannel` | `UMovieSceneScriptingStringKey` | `FString` |
| `UMovieSceneScriptingTextChannel` | `UMovieSceneScriptingTextKey` | `FText` |
| `UMovieSceneScriptingByteChannel` | `UMovieSceneScriptingByteKey` | `uint8` (枚举) |
| `UMovieSceneScriptingEventChannel` | `UMovieSceneScriptingEventKey` | `FMovieSceneEvent` |
| `UMovieSceneScriptingActorReferenceChannel` | `UMovieSceneScriptingActorReferenceKey` | `FMovieSceneObjectBindingID` |
| `UMovieSceneScriptingObjectPathChannel` | `UMovieSceneScriptingObjectPathKey` | `UObject*` |
| `UMovieSceneScriptingParticleChannel` | `UMovieSceneScriptingParticleKey` | `EParticleKey` |

### 使用示例（蓝图描述）

**示例 1：创建序列并添加 Float 关键帧**

1. 调用 `Asset > Create Asset` 创建一个 `LevelSequence` 资产
2. 从序列返回值拉线，调用 `SequenceExtensions > SetPlaybackStart` 和 `SetPlaybackEnd` 设置播放范围（如 0-150 帧）
3. 调用 `SequenceExtensions > AddMasterTrack`（传入 `UMovieSceneFloatTrack` 类型）添加主轨道
4. 从返回的 Track 拉线，调用 `TrackExtensions > AddSection` 添加 Section
5. 从 Section 拉线，调用 `SectionExtensions > GetAllChannels` 获取通道列表
6. 从通道数组取第一个元素，转换为 `UMovieSceneScriptingFloatChannel` 类型
7. 调用通道的 `AddKey (Float)` 节点，传入帧号 0 和值 0.0
8. 再次调用 `AddKey (Float)`，传入帧号 150 和值 1.0

**示例 2：遍历序列中的所有绑定并重命名**

1. 获取 Level Sequence 引用
2. 调用 `SequenceExtensions > GetBindings` 获取所有绑定（返回 `FMovieSceneBindingProxy` 数组）
3. 用 ForEach 循环遍历每个绑定
4. 对每个绑定调用 `BindingExtensions > GetDisplayName` 获取当前名称
5. 用 String 操作拼接新名称后，调用 `BindingExtensions > SetDisplayName` 设置新名称

**示例 3：批量修改关键帧插值模式**

1. 获取目标 Section 的 Float 通道
2. 调用 `GetKeys` 获取所有关键帧
3. 遍历每个关键帧，Cast 为 `UMovieSceneScriptingActualFloatKey`
4. 对每个关键帧调用 `SetInterpolationMode` 设为 `RCIM_Cubic`
5. 调用 `SetArriveTangent` 和 `SetLeaveTangent` 设置切线值

## C++ 用法

### 头文件引入

```cpp
#include "MovieSceneScriptingChannel.h"
#include "MovieSceneSequenceExtensions.h"
#include "MovieSceneBindingExtensions.h"
#include "MovieSceneSectionExtensions.h"
#include "MovieSceneTrackExtensions.h"
```

### 基本用法：创建序列并添加关键帧

```cpp
#include "MovieSceneSequenceExtensions.h"
#include "MovieSceneScriptingChannel.h"
#include "MovieSceneSectionExtensions.h"
#include "MovieSceneTrackExtensions.h"
#include "LevelSequence.h"

// 创建或加载一个 Level Sequence
ULevelSequence* Sequence = NewObject<ULevelSequence>();

// 设置播放范围
UMovieSceneSequenceExtensions::SetPlaybackStart(Sequence, 0);
UMovieSceneSequenceExtensions::SetPlaybackEnd(Sequence, 150);

// 添加主轨道
UMovieSceneFloatTrack* FloatTrack = Cast<UMovieSceneFloatTrack>(
    UMovieSceneSequenceExtensions::AddMasterTrack(Sequence, UMovieSceneFloatTrack::StaticClass())
);

// 添加 Section
UMovieSceneSection* Section = UMovieSceneTrackExtensions::AddSection(FloatTrack);

// 获取 Float 通道
TArray<UMovieSceneScriptingChannel*> Channels = UMovieSceneSectionExtensions::GetAllChannels(Section);
if (Channels.Num() > 0)
{
    UMovieSceneScriptingFloatChannel* FloatChannel = Cast<UMovieSceneScriptingFloatChannel>(Channels[0]);
    if (FloatChannel)
    {
        // 在第 0 帧添加值为 0.0 的关键帧
        FloatChannel->AddKey(FFrameNumber(0), 0.0f);
        // 在第 150 帧添加值为 1.0 的关键帧
        FloatChannel->AddKey(FFrameNumber(150), 1.0f);
    }
}
```

### 进阶用法：遍历绑定并操作多类型通道

```cpp
#include "MovieSceneSequenceExtensions.h"
#include "MovieSceneBindingExtensions.h"
#include "MovieSceneScriptingChannel.h"
#include "MovieSceneSectionExtensions.h"
#include "MovieSceneTrackExtensions.h"

void ManipulateSequence(ULevelSequence* Sequence)
{
    // 获取所有绑定
    TArray<FMovieSceneBindingProxy> Bindings = UMovieSceneSequenceExtensions::GetBindings(Sequence);
    
    for (const FMovieSceneBindingProxy& Binding : Bindings)
    {
        // 获取显示名
        FText Name = UMovieSceneBindingExtensions::GetDisplayName(Binding);
        
        // 获取该绑定下的所有轨道
        TArray<UMovieSceneTrack*> Tracks = UMovieSceneBindingExtensions::GetTracks(Binding);
        
        for (UMovieSceneTrack* Track : Tracks)
        {
            // 获取所有 Section
            TArray<UMovieSceneSection*> Sections = UMovieSceneTrackExtensions::GetSections(Track);
            
            for (UMovieSceneSection* Section : Sections)
            {
                // 获取 Float 通道
                TArray<UMovieSceneScriptingChannel*> Channels = 
                    UMovieSceneSectionExtensions::GetChannelsByType(Section, UMovieSceneScriptingFloatChannel::StaticClass());
                
                for (UMovieSceneScriptingChannel* Channel : Channels)
                {
                    UMovieSceneScriptingFloatChannel* FloatChannel = 
                        Cast<UMovieSceneScriptingFloatChannel>(Channel);
                    
                    if (FloatChannel)
                    {
                        // 遍历所有关键帧并修改切线
                        TArray<UMovieSceneScriptingKey*> Keys = FloatChannel->GetKeys();
                        for (UMovieSceneScriptingKey* Key : Keys)
                        {
                            UMovieSceneScriptingFloatKey* FloatKey = Cast<UMovieSceneScriptingFloatKey>(Key);
                            if (FloatKey)
                            {
                                FloatKey->SetInterpolationMode(ERichCurveInterpMode::RCIM_Cubic);
                                FloatKey->SetArriveTangent(0.0f);
                                FloatKey->SetLeaveTangent(0.0f);
                            }
                        }
                    }
                }
            }
        }
    }
}
```

### 进阶用法：使用标记帧和范围操作

```cpp
#include "MovieSceneSequenceExtensions.h"
#include "SequencerScriptingRange.h"

void WorkWithRangesAndMarks(ULevelSequence* Sequence)
{
    // 添加标记帧
    int32 MarkIndex = UMovieSceneSequenceExtensions::AddMarkedFrame(Sequence, TEXT("Important Shot"));
    UMovieSceneSequenceExtensions::SetMarkedFrame(Sequence, MarkIndex, FFrameNumber(72));
    
    // 创建时间范围
    FSequencerScriptingRange PlaybackRange = UMovieSceneSequenceExtensions::GetPlaybackRange(Sequence);
    
    // 检查范围属性
    if (USequencerScriptingRangeExtensions::HasStart(PlaybackRange))
    {
        int32 StartFrame = USequencerScriptingRangeExtensions::GetStartFrame(PlaybackRange);
        float StartSeconds = USequencerScriptingRangeExtensions::GetStartSeconds(PlaybackRange);
    }
    
    // 设置显示率和 Tick 分辨率
    UMovieSceneSequenceExtensions::SetDisplayRate(Sequence, FFrameRate(24, 1));
    UMovieSceneSequenceExtensions::SetTickResolution(Sequence, FFrameRate(24000, 1));
}
```

## Demo 示例

```cpp
// SequencerDemo.h
#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "MovieSceneSequenceExtensions.h"
#include "MovieSceneScriptingChannel.h"
#include "MovieSceneSectionExtensions.h"
#include "MovieSceneTrackExtensions.h"
#include "MovieSceneBindingExtensions.h"
#include "LevelSequence.h"
#include "SequencerDemo.generated.h"

UCLASS()
class USequencerDemoLibrary : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    /**
     * 演示：创建一个简单的动画序列
     * 在指定绑定上创建一个 Float 动画通道，并设置两个关键帧
     */
    UFUNCTION(BlueprintCallable, Category = "SequencerDemo")
    static UMovieSceneScriptingFloatChannel* CreateSimpleAnimation(
        ULevelSequence* Sequence,
        const FMovieSceneBindingProxy& Binding,
        int32 StartFrame,
        int32 EndFrame,
        float StartValue,
        float EndValue)
    {
        if (!Sequence || !Binding.Sequence)
        {
            return nullptr;
        }

        // 向绑定添加 Float 轨道
        UMovieSceneTrack* Track = UMovieSceneBindingExtensions::AddTrack(
            Binding, UMovieSceneFloatTrack::StaticClass());
        if (!Track)
        {
            return nullptr;
        }

        // 添加 Section
        UMovieSceneSection* Section = UMovieSceneTrackExtensions::AddSection(Track);
        if (!Section)
        {
            return nullptr;
        }

        // 设置 Section 范围
        UMovieSceneSectionExtensions::SetRange(Section, StartFrame, EndFrame);

        // 获取 Float 通道
        TArray<UMovieSceneScriptingChannel*> Channels = 
            UMovieSceneSectionExtensions::GetAllChannels(Section);
        
        UMovieSceneScriptingFloatChannel* FloatChannel = nullptr;
        for (UMovieSceneScriptingChannel* Channel : Channels)
        {
            FloatChannel = Cast<UMovieSceneScriptingFloatChannel>(Channel);
            if (FloatChannel)
            {
                break;
            }
        }

        if (!FloatChannel)
        {
            return nullptr;
        }

        // 添加起始关键帧
        UMovieSceneScriptingFloatKey* StartKey = FloatChannel->AddKey(
            FFrameNumber(StartFrame), StartValue);
        if (StartKey)
        {
            StartKey->SetInterpolationMode(ERichCurveInterpMode::RCIM_Cubic);
            StartKey->SetArriveTangent(0.0f);
            StartKey->SetLeaveTangent(0.0f);
        }

        // 添加结束关键帧
        UMovieSceneScriptingFloatKey* EndKey = FloatChannel->AddKey(
            FFrameNumber(EndFrame), EndValue);
        if (EndKey)
        {
            EndKey->SetInterpolationMode(ERichCurveInterpMode::RCIM_Cubic);
            EndKey->SetArriveTangent(0.0f);
            EndKey->SetLeaveTangent(0.0f);
        }

        return FloatChannel;
    }

    /**
     * 演示：查询序列中所有绑定的名称
     */
    UFUNCTION(BlueprintCallable, Category = "SequencerDemo")
    static TArray<FString> GetAllBindingNames(ULevelSequence* Sequence)
    {
        TArray<FString> Names;
        if (!Sequence)
        {
            return Names;
        }

        TArray<FMovieSceneBindingProxy> Bindings = 
            UMovieSceneSequenceExtensions::GetBindings(Sequence);
        
        for (const FMovieSceneBindingProxy& Binding : Bindings)
        {
            Names.Add(Binding.DisplayName.ToString());
        }

        return Names;
    }
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LevelSequence` | Level Sequence 核心资产类型 |
| `MovieScene` | MovieScene 核心框架，包含序列、轨道、通道等基础类型 |
| `MovieSceneTracks` | 内置的 MovieScene 轨道实现（Float、Transform、Event 等） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `b209798d` | Anim In Engine: Add bRemoveExcludedCurves option to animation recording so we can remove curves alre | 动画录制新增移除排除曲线选项 |
| 2026-04-24 | `8b8110b4` | [EDA] Add Sequencer tool wrappers + fix sequencer toolset tests | 添加序列器工具包装器并修复工具集测试 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 新日志宏 |
| 2026-04-10 | `77af3950` | [EDA] Add SequencerTools toolset with Anim Mixer split into separate plugin | 添加 SequencerTools 工具集，动画混合器拆分为独立插件 |
| 2026-04-10 | `8bd8f719` | [Backout] - CL52569948 | 回退变更 CL52569948 |

### 维护评价

- **年龄**：创建于 2018 年 5 月，至今约 8 年
- **活跃度**：非常活跃。2026 年 4-5 月仍有密集更新，持续接收新功能（EDA 序列器工具集成、动画录制改进）和维护性改动（日志宏迁移）
- **实验性状态**：`IsBetaVersion = true`，但已有 8 年历史且被大量使用，属于成熟度较高但官方尚未正式摘除 Beta 标签的插件
- **依赖关系**：依赖 Python 插件（在 .uplugin 的 Plugins 字段中声明），是 UE5 Sequencer 脚本化的核心基础设施
- **推荐程度**：**强烈推荐**。这是 UE5 中通过脚本（蓝图/Python）操作 Sequencer 的唯一官方方式，功能全面且持续维护。尽管标记为 Beta，但已成为 Sequencer 生态中不可或缺的组件

⚠️ **注意**：虽然插件标记为 `IsBetaVersion = true`，但其 API 已相当稳定，且在 UE5 各版本中持续迭代维护，实际使用风险较低。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/SequencerScripting)
- 官方文档：无（.uplugin 中 DocsURL 为空）