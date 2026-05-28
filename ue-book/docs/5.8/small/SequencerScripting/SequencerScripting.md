# Sequencer Scripting

> Python and editor utility scripting extensions for sequencer and movie scenes

| 属性 | 值 |
|---|---|
| 中文名 | Sequencer 脚本 |
| 分类 | Scripting |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `SequencerScripting` (Runtime), `SequencerScriptingEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-05-09 |
| 年龄标签 | 🏛️ 文物（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/SequencerScripting) | |

## 用途

这个插件为 UE5 的 Sequencer（序列器）系统提供完整的蓝图和 Python 脚本 API。Sequencer 本身是一个底层 C++ 框架，没有对蓝图/Python 开放操作接口；本插件通过大量的 `UFUNCTION(BlueprintCallable)` 扩展库和脚本包装类，将 Sequencer 的核心对象（序列、绑定、轨道、区段、通道、关键帧等）全部暴露给脚本层。

**解决的问题**：没有这个插件，你无法通过蓝图或 Python 程序化地创建/编辑过场动画序列——只能手动在 Sequencer 编辑器中操作。有了它，你可以：
- 批量生成过场动画序列
- 自动化关键帧编辑和曲线调整
- 通过 Python 脚本实现序列的导入导出、批处理
- 在编辑器工具中程序化操作 Sequencer 数据

## 使用场景

- 你正在做电影级过场，需要批量处理上百个序列文件 → 用 Python 脚本遍历和修改
- 你需要自动生成带动画关键帧的 Level Sequence → 用蓝图/Python 调用 `AddKey` 系列节点
- 你正在开发编辑器工具来自动化 Sequencer 工作流 → 使用扩展库的 `ScriptMethod` 节点
- 你需要程序化地设置序列的播放范围、时间分辨率 → 用 `SetPlaybackStart`、`SetDisplayRate` 等
- 你需要管理 Sequencer 中的对象绑定、轨道和文件夹 → 用 Binding/Track/Folder 扩展

## 蓝图用法

本插件的 API 主要通过 **扩展函数库**（Extension Libraries）暴露，使用 `meta=(ScriptMethod)` 将静态函数"提升"到目标类上。这意味着在蓝图中，这些函数会作为目标对象的方法出现。

### 序列操作（核心节点）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetMovieScene` | 获取序列的 MovieScene 数据对象 | `UMovieSceneSequenceExtensions` |
| `GetTracks` / `FindTracksByType` | 获取/查找序列中的轨道 | `UMovieSceneSequenceExtensions` |
| `AddTrack` | 向序列添加新轨道 | `UMovieSceneSequenceExtensions` |
| `GetDisplayRate` / `SetDisplayRate` | 获取/设置序列显示帧率 | `UMovieSceneSequenceExtensions` |
| `GetPlaybackStart` / `SetPlaybackStart` | 获取/设置播放起始帧 | `UMovieSceneSequenceExtensions` |
| `GetPlaybackEnd` / `SetPlaybackEnd` | 获取/设置播放结束帧 | `UMovieSceneSequenceExtensions` |
| `MakeRange` / `MakeRangeSeconds` | 创建时间范围 | `UMovieSceneSequenceExtensions` |
| `GetPlaybackRange` | 获取播放范围 | `UMovieSceneSequenceExtensions` |
| `FindMarkedFrameByLabel` | 按标签查找标记帧 | `UMovieSceneSequenceExtensions` |
| `SetReadOnly` | 设置序列为只读 | `UMovieSceneSequenceExtensions` |
| `AddMasterTrack` | 添加主轨道 | `UMovieSceneSequenceExtensions` |
| `GetBindings` | 获取所有对象绑定 | `UMovieSceneSequenceExtensions` |
| `MakeBindingID` / `LocateBoundObjects` | 创建绑定ID / 定位绑定对象 | `UMovieSceneSequenceExtensions` |

### 绑定操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetId` | 获取绑定的 GUID | `UMovieSceneBindingExtensions` |
| `GetDisplayName` / `SetDisplayName` | 获取/设置绑定显示名称 | `UMovieSceneBindingExtensions` |
| `GetTracks` / `AddTrack` | 获取/添加绑定内的轨道 | `UMovieSceneBindingExtensions` |
| `Remove` | 删除整个绑定 | `UMovieSceneBindingExtensions` |
| `GetParent` / `SetParent` | 获取/设置父绑定 | `UMovieSceneBindingExtensions` |
| `GetChildPossessables` | 获取子 Possessable 绑定 | `UMovieSceneBindingExtensions` |
| `TagBinding` / `UntagBinding` | 给绑定打标签/移除标签 | `UMovieSceneBindingTagExtensions` |
| `MoveBindingContents` | 移动绑定内容到另一个绑定 | `UMovieSceneBindingExtensions` |

### 轨道操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetSections` / `AddSection` / `RemoveSection` | 获取/添加/删除区段 | `UMovieSceneTrackExtensions` |
| `SetDisplayName` / `GetDisplayName` | 获取/设置轨道显示名 | `UMovieSceneTrackExtensions` |
| `GetPropertyName` / `SetPropertyNameAndPath` | 获取/设置属性轨道的属性名 | `UMovieScenePropertyTrackExtensions` |
| `SetObjectPropertyClass` | 设置对象属性轨道的目标类 | `UMovieScenePropertyTrackExtensions` |
| `SetByteTrackEnum` | 设置字节轨道的枚举 | `UMovieScenePropertyTrackExtensions` |
| `SetNumChannelsUsed` | 设置向量轨道使用的通道数 | `UMovieSceneFloatVectorTrackExtensions` |

### 区段操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `HasStartFrame` / `HasEndFrame` | 检查区段是否有起止帧 | `UMovieSceneSectionExtensions` |
| `GetStartFrame` / `GetEndFrame` | 获取区段起止帧 | `UMovieSceneSectionExtensions` |
| `SetRange` / `SetRangeSeconds` | 设置区段范围 | `UMovieSceneSectionExtensions` |
| `SetStartFrameBounded` / `SetEndFrameBounded` | 设置区段是否为有限范围 | `UMovieSceneSectionExtensions` |
| `GetAllChannels` / `GetChannelsByType` | 获取区段内的通道 | `UMovieSceneSectionExtensions` |
| `GetSectionCondition` / `SetSectionCondition` | 获取/设置区段条件 | `UMovieSceneConditionExtensions` |
| `GetEaseInDuration` / `SetEaseInDuration` | 获取/设置缓入时长 | `UMovieSceneSectionEasingExtensions` |

### 关键帧与通道操作

每种数据类型都有对应的 Key 和 Channel 类，API 模式一致：

| 数据类型 | Key 类 | Channel 类 |
|---|---|---|
| 浮点数 | `UMovieSceneScriptingFloatKey` | `UMovieSceneScriptingFloatChannel` |
| 双精度浮点 | `UMovieSceneScriptingDoubleKey` | `UMovieSceneScriptingDoubleChannel` |
| 整数 | `UMovieSceneScriptingIntegerKey` | `UMovieSceneScriptingIntegerChannel` |
| 布尔值 | `UMovieSceneScriptingBoolKey` | `UMovieSceneScriptingBoolChannel` |
| 字符串 | `UMovieSceneScriptingStringKey` | `UMovieSceneScriptingStringChannel` |
| 文本 | `UMovieSceneScriptingTextKey` | `UMovieSceneScriptingTextChannel` |
| 字节/枚举 | `UMovieSceneScriptingByteKey` | `UMovieSceneScriptingByteChannel` |
| 事件 | `UMovieSceneScriptingEventKey` | `UMovieSceneScriptingEventChannel` |
| 粒子 | `UMovieSceneScriptingParticleKey` | `UMovieSceneScriptingParticleChannel` |
| 对象引用 | `UMovieSceneScriptingActorReferenceKey` | `UMovieSceneScriptingActorReferenceChannel` |
| 对象路径 | `UMovieSceneScriptingObjectPathKey` | `UMovieSceneScriptingObjectPathChannel` |

每个 Channel 的通用操作：

| 节点 | 说明 |
|---|---|
| `AddKey` | 在指定时间添加关键帧 |
| `RemoveKey` | 删除指定关键帧 |
| `GetKeys` | 获取所有关键帧 |
| `GetKeysByIndex` | 按索引获取关键帧 |
| `SetDefault` / `GetDefault` / `RemoveDefault` | 设置/获取/移除默认值 |
| `HasDefault` | 检查是否有默认值 |
| `Transform` | 对关键帧进行时间变换（偏移、缩放） |

每个 Key 的通用操作：

| 节点 | 说明 |
|---|---|
| `GetTime` / `SetTime` | 获取/设置关键帧时间 |
| `GetValue` / `SetValue` | 获取/设置关键帧值 |

### 使用示例（蓝图描述）

**示例 1：程序化创建序列并添加关键帧**

1. 使用 `LevelSequenceActor` 节点获取现有的 Level Sequence（或用 `CreateLevelSequence` 新建）
2. 调用 `GetMovieScene` 获取内部 MovieScene
3. 调用 `AddTrack` (传入 `UMovieSceneFloatTrack` 类型) 添加浮点轨道
4. 从返回的 Track 调用 `AddSection` 创建区段
5. 调用 `SetRange` 设置区段时间范围
6. 调用 `GetAllChannels` 或 `GetChannelsByType` 获取浮点通道
7. 在通道上调用 `AddKey` 添加关键帧

**示例 2：遍历并修改所有绑定**

1. 对目标序列调用 `GetBindings` 获取所有绑定数组
2. 遍历数组，对每个 `FMovieSceneBindingProxy` 调用 `GetDisplayName` 获取名称
3. 用 `GetTracks` 获取该绑定的轨道
4. 对每个轨道调用 `GetSections` 获取区段并修改

## C++ 用法

### 头文件引入

```cpp
#include "MovieSceneSequenceExtensions.h"
#include "MovieSceneBindingExtensions.h"
#include "MovieSceneSectionExtensions.h"
#include "MovieSceneTrackExtensions.h"
#include "MovieScenePropertyTrackExtensions.h"
#include "MovieSceneScriptingChannel.h"
```

### 基本用法：操作序列和轨道

```cpp
// 来源: Public/ExtensionLibraries/MovieSceneSequenceExtensions.h

// 获取序列的 MovieScene 数据
UMovieScene* MovieScene = UMovieSceneSequenceExtensions::GetMovieScene(MyLevelSequence);

// 获取所有轨道
TArray<UMovieSceneTrack*> AllTracks = UMovieSceneSequenceExtensions::GetTracks(MyLevelSequence);

// 按类型查找轨道
TArray<UMovieSceneTrack*> FloatTracks = UMovieSceneSequenceExtensions::FindTracksByType(
    MyLevelSequence, UMovieSceneFloatTrack::StaticClass());

// 添加新轨道
UMovieSceneTrack* NewTrack = UMovieSceneSequenceExtensions::AddTrack(
    MyLevelSequence, UMovieSceneFloatTrack::StaticClass());

// 设置显示帧率为 30fps
UMovieSceneSequenceExtensions::SetDisplayRate(MyLevelSequence, FFrameRate(30, 1));

// 设置播放范围
UMovieSceneSequenceExtensions::SetPlaybackStart(MyLevelSequence, 0);
UMovieSceneSequenceExtensions::SetPlaybackEnd(MyLevelSequence, 300);

// 创建时间范围
FSequencerScriptingRange Range = UMovieSceneSequenceExtensions::MakeRange(MyLevelSequence, 0, 300);

// 获取所有绑定
TArray<FMovieSceneBindingProxy> Bindings = UMovieSceneSequenceExtensions::GetBindings(MyLevelSequence);
```

### 进阶用法：操作区段和通道

```cpp
// 来源: Public/ExtensionLibraries/MovieSceneSectionExtensions.h
// 来源: Public/ExtensionLibraries/MovieSceneTrackExtensions.h

// 获取轨道的区段
TArray<UMovieSceneSection*> Sections = UMovieSceneTrackExtensions::GetSections(MyTrack);

if (Sections.Num() > 0)
{
    UMovieSceneSection* Section = Sections[0];
    
    // 检查并获取起止帧
    if (UMovieSceneSectionExtensions::HasStartFrame(Section))
    {
        int32 StartFrame = UMovieSceneSectionExtensions::GetStartFrame(Section);
    }
    
    // 设置区段范围（秒）
    UMovieSceneSectionExtensions::SetRangeSeconds(Section, 0.0f, 10.0f);
    
    // 获取区段内的通道
    TArray<UMovieSceneScriptingChannel*> Channels = 
        UMovieSceneSectionExtensions::GetAllChannels(Section);
    
    // 按类型过滤通道
    TArray<UMovieSceneScriptingChannel*> FloatChannels = 
        UMovieSceneSectionExtensions::GetChannelsByType(
            Section, UMovieSceneScriptingFloatChannel::StaticClass());
    
    if (FloatChannels.Num() > 0)
    {
        UMovieSceneScriptingFloatChannel* FloatChannel = 
            Cast<UMovieSceneScriptingFloatChannel>(FloatChannels[0]);
        
        // 在第 0 帧添加值为 1.0 的关键帧
        UMovieSceneScriptingFloatKey* Key = FloatChannel->AddKey(
            FFrameNumber(0), 1.0f, 0.f, EMovieSceneTimeUnit::DisplayRate);
        
        // 设置关键帧的插值模式
        Key->SetInterpolationMode(ERichCurveInterpMode::RCIM_Cubic);
        Key->SetArriveTangent(0.0f);
        Key->SetLeaveTangent(0.0f);
    }
}

// 来源: Public/ExtensionLibraries/MovieSceneBindingExtensions.h

// 操作绑定
FMovieSceneBindingProxy Binding = Bindings[0];

// 获取绑定信息
FGuid BindingId = UMovieSceneBindingExtensions::GetId(Binding);
FText DisplayName = UMovieSceneBindingExtensions::GetDisplayName(Binding);

// 获取子绑定
TArray<FMovieSceneBindingProxy> Children = 
    UMovieSceneBindingExtensions::GetChildPossessables(Binding);

// 给绑定添加标签（用于运行时查找）
UMovieSceneBindingTagExtensions::TagBinding(Binding, FName("MyTag"));
TArray<FName> Tags = UMovieSceneBindingTagExtensions::GetBindingTags(Binding);
```

### 高级用法：条件系统与缓动

```cpp
// 来源: Public/ExtensionLibraries/MovieSceneConditionExtensions.h
// 来源: Public/ExtensionLibraries/MovieSceneSectionEasingExtensions.h

// 为区段设置条件
UMovieSceneConditionExtensions::SetSectionCondition(
    MySection, UMyCustomCondition::StaticClass());

// 清除区段条件
UMovieSceneConditionExtensions::ClearSectionCondition(MySection);

// 设置缓入缓出
UMovieSceneSectionEasingExtensions::SetEaseInDuration(MySection, 5);
UMovieSceneSectionEasingExtensions::SetEaseOutDuration(MySection, 10);

int32 EaseIn = UMovieSceneSectionEasingExtensions::GetEaseInDuration(MySection);
```

## Demo 示例

```cpp
// MySequenceScriptTool.h
#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "MySequenceScriptTool.generated.h"

class ULevelSequence;

UCLASS()
class UMySequenceScriptTool : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    // 演示：程序化创建一个包含浮点动画的序列区段
    UFUNCTION(BlueprintCallable, Category = "Demo")
    static void Demo_AddFloatTrackWithKeys(ULevelSequence* Sequence, float StartValue, float EndValue);
};
```

```cpp
// MySequenceScriptTool.cpp
#include "MySequenceScriptTool.h"
#include "LevelSequence.h"
#include "MovieSceneSequenceExtensions.h"
#include "MovieSceneTrackExtensions.h"
#include "MovieSceneSectionExtensions.h"
#include "MovieSceneScriptingChannel.h"
#include "Tracks/MovieSceneFloatTrack.h"

void UMySequenceScriptTool::Demo_AddFloatTrackWithKeys(
    ULevelSequence* Sequence, float StartValue, float EndValue)
{
    if (!Sequence)
    {
        return;
    }

    // 1. 添加浮点轨道
    UMovieSceneTrack* Track = UMovieSceneSequenceExtensions::AddTrack(
        Sequence, UMovieSceneFloatTrack::StaticClass());
    if (!Track) return;

    // 2. 创建区段并设置范围（0~60帧，约2秒@30fps）
    UMovieSceneSection* Section = UMovieSceneTrackExtensions::AddSection(Track);
    UMovieSceneSectionExtensions::SetRange(Section, 0, 60);

    // 3. 获取浮点通道并添加关键帧
    TArray<UMovieSceneScriptingChannel*> Channels = 
        UMovieSceneSectionExtensions::GetChannelsByType(
            Section, UMovieSceneScriptingFloatChannel::StaticClass());

    for (UMovieSceneScriptingChannel* Channel : Channels)
    {
        UMovieSceneScriptingFloatChannel* FloatChannel = 
            Cast<UMovieSceneScriptingFloatChannel>(Channel);
        if (!FloatChannel) continue;

        // 在第 0 帧添加起始值
        UMovieSceneScriptingFloatKey* StartKey = FloatChannel->AddKey(
            FFrameNumber(0), StartValue, 0.f, EMovieSceneTimeUnit::DisplayRate,
            EMovieSceneKeyInterpolation::Cubic);

        // 在第 60 帧添加结束值
        UMovieSceneScriptingFloatKey* EndKey = FloatChannel->AddKey(
            FFrameNumber(60), EndValue, 0.f, EMovieSceneTimeUnit::DisplayRate,
            EMovieSceneKeyInterpolation::Cubic);

        // 设置切线为自动
        if (StartKey)
        {
            StartKey->SetInterpolationMode(ERichCurveInterpMode::RCIM_Cubic);
            StartKey->SetArriveTangent(0.f);
            StartKey->SetLeaveTangent(0.f);
        }
        if (EndKey)
        {
            EndKey->SetInterpolationMode(ERichCurveInterpMode::RCIM_Cubic);
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LevelSequence` | 核心序列资产类型 |
| `MovieScene` | Sequencer 底层电影场景数据结构 |
| `MovieSceneTracks` | 内置轨道类型（Float、Transform 等） |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `b209798d` | Anim In Engine: Add bRemoveExcludedCurves option to animation recording so we can remove curves already on the existing sequence | 动画录制添加排除曲线选项 |
| 2026-04-24 | `8b8110b4` | [EDA] Add Sequencer tool wrappers + fix sequencer toolset tests | 添加 Sequencer 工具封装并修复测试 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移至 UE_LOGF |
| 2026-04-10 | `77af3950` | [EDA] Add SequencerTools toolset with Anim Mixer split into separate plugin | 添加 SequencerTools 工具集，Anim Mixer 拆分独立插件 |
| 2026-04-10 | `8bd8f719` | [Backout] - CL52569948 | 回退之前的提交 |

### 维护评价

- **活跃维护**：最近 6 个月内有持续的功能性更新（Sequencer 工具封装、日志迁移、动画录制改进）
- **持续演进**：插件从 2018 年创建至今 8 年，仍在持续添加新 API（如条件系统、绑定标签、时间扭曲扩展等 5.x 新增功能）
- **实验性标签**：`IsBetaVersion=true`，但实际已在生产环境广泛使用多年，此标签更多是 Epic 的惯性保留
- **推荐使用**：这是操作 Sequencer 的唯一官方脚本接口，没有替代方案。所有需要程序化操作序列的工作流都必须依赖此插件
- **注意事项**：部分 API 标记为 `DevelopmentOnly`（如视图范围设置、排序顺序等），这些功能仅在编辑器开发环境中可用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/SequencerScripting)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/sequencer-scripting-in-unreal-engine/)（Sequencer 脚本概述）