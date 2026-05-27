# Sequencer Scripting

> Python and editor utility scripting extensions for sequencer and movie scenes

| 属性 | 值 |
|---|---|
| 中文名 | 序列脚本 |
| 分类 | Scripting |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `SequencerScripting` (Runtime), `SequencerScriptingEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-05-09 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/SequencerScripting) | |

## 用途

SequencerScripting 插件将 UE Sequencer（过场动画/动画序列编辑器）的内部数据结构——包括序列、轨道、片段、通道、关键帧和绑定——通过蓝图和 Python 脚本完整暴露出来。

**解决的核心问题**：原生 Sequencer API（`MovieScene*` 系列类）是面向引擎内部的 C++ 接口，不具备蓝图/Python 可调用性。此插件在底层 `MovieSceneChannel` 模板体系之上，构建了一套 `UMovieSceneScriptingChannel` / `UMovieSceneScriptingKey` 的包装层，使非 C++ 工作者（技术美术、管线工程师）能够用脚本批量创建、编辑、读取序列数据。

**为什么存在**：影视/虚拟制片管线中，大量序列资产需要程序化生成或批量修改（如镜头批量偏移、关键帧批量重定时、通道默认值批量设置），手动操作不可行。此插件是 UE Sequencer 自动化的官方基石。

## 使用场景

- 你需要用 Python 脚本批量创建 Level Sequence 并填充动画关键帧 → 使用 `MovieSceneSequenceExtensions` + 各种 Channel 的 `AddKey`
- 你需要在蓝图中读取/修改已有序列的关键帧时间或插值模式 → 使用 `UMovieSceneScriptingFloatKey` / `UMovieSceneScriptingDoubleKey`
- 你需要程序化地管理序列中的对象绑定（Possessable/Spawnable）→ 使用 `MovieSceneBindingExtensions`
- 你需要在管线中批量调整序列的播放范围、帧率、Marked Frames → 使用 `MovieSceneSequenceExtensions`
- 你需要为虚拟制片管线自动创建 Event Track 并绑定蓝图事件 → 使用 `MovieSceneEventTrackExtensions`
- 你需要管理序列中轨道的条件（Condition）系统 → 使用 `MovieSceneConditionExtensions`
- 你需要在 Python 中操作序列文件夹结构（Folder 组织）→ 使用 `MovieSceneFolderExtensions`

## 蓝图用法

本插件大量使用 `BlueprintFunctionLibrary` + `meta=(ScriptMethod)` 模式，即函数定义在独立的 FunctionLibrary 类中，但通过 ScriptMethod 元数据"提升"（hoist）到目标类上，使得蓝图中看起来像是 Sequence/Track/Section/Channel 的原生方法。

### 核心节点

#### 序列管理（Sequence Extensions）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Movie Scene` | 获取序列的 MovieScene 数据对象 | `UMovieSceneSequenceExtensions` |
| `Get Tracks` / `Find Tracks By Type` | 获取/按类型查找序列中的所有轨道 | `UMovieSceneSequenceExtensions` |
| `Add Track` / `Remove Track` | 添加/移除轨道 | `UMovieSceneSequenceExtensions` |
| `Get Display Rate` / `Set Display Rate` | 获取/设置序列显示帧率 | `UMovieSceneSequenceExtensions` |
| `Get Tick Resolution` / `Set Tick Resolution` | 获取/设置序列时钟分辨率 | `UMovieSceneSequenceExtensions` |
| `Get Playback Start` / `Get Playback End` | 获取播放范围起止帧 | `UMovieSceneSequenceExtensions` |
| `Set Playback Start` / `Set Playback End` | 设置播放范围起止帧 | `UMovieSceneSequenceExtensions` |
| `Make Range` / `Make Range Seconds` | 创建脚本范围对象 | `UMovieSceneSequenceExtensions` |
| `Get Bindings` / `Add Possessable` / `Add Spawnable` | 管理对象绑定 | `UMovieSceneSequenceExtensions` |
| `Find Marked Frame By Label` | 按标签查找标记帧 | `UMovieSceneSequenceExtensions` |
| `Add Marked Frame` / `Delete Marked Frame` | 管理标记帧 | `UMovieSceneSequenceExtensions` |
| `Set Evaluation Type` | 设置评估类型 | `UMovieSceneSequenceExtensions` |
| `Set Clock Source` | 设置时钟源 | `UMovieSceneSequenceExtensions` |
| `Set ReadOnly` / `Is ReadOnly` | 设置/查询只读状态 | `UMovieSceneSequenceExtensions` |
| `Set Playback Range Locked` | 锁定播放范围 | `UMovieSceneSequenceExtensions` |

#### 片段管理（Section Extensions）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Has Start Frame` / `Has End Frame` | 查询片段是否有有限的起止帧 | `UMovieSceneSectionExtensions` |
| `Get Start Frame` / `Get End Frame` | 获取片段起止帧号 | `UMovieSceneSectionExtensions` |
| `Set Range` / `Set Range Seconds` | 设置片段时间范围 | `UMovieSceneSectionExtensions` |
| `Get All Channels` | 获取片段中的所有通道 | `UMovieSceneSectionExtensions` |
| `Get Channels By Type` | 按类型筛选通道 | `UMovieSceneSectionExtensions` |
| `Get Ease In Duration` / `Get Ease Out Duration` | 获取缓入缓出时长 | `UMovieSceneSectionEasingExtensions` |
| `Set Ease In Duration` / `Set Ease Out Duration` | 设置缓入缓出时长 | `UMovieSceneSectionEasingExtensions` |
| `Set Section Condition` / `Clear Section Condition` | 管理片段条件 | `UMovieSceneConditionExtensions` |

#### 轨道管理（Track Extensions）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Add Section` / `Remove Section` | 添加/移除轨道中的片段 | `UMovieSceneTrackExtensions` |
| `Get Sections` | 获取轨道的所有片段 | `UMovieSceneTrackExtensions` |
| `Set Display Name` / `Get Display Name` | 设置/获取轨道显示名称 | `UMovieSceneTrackExtensions` |
| `Set Sorting Order` / `Get Sorting Order` | 设置/获取轨道排序 | `UMovieSceneTrackExtensions` |
| `Set Property Name And Path` | 设置属性轨道的目标属性 | `UMovieScenePropertyTrackExtensions` |
| `Set Byte Track Enum` | 设置字节轨道的枚举类型 | `UMovieScenePropertyTrackExtensions` |
| `Set Num Channels Used` | 设置向量轨道使用的通道数 | `UMovieSceneFloatVectorTrackExtensions` |
| `Add Event Repeater Section` / `Add Event Trigger Section` | 创建事件片段 | `UMovieSceneEventTrackExtensions` |
| `Set Material Info` | 设置材质轨道信息 | `UMovieSceneMaterialTrackExtensions` |
| `Set Track Condition` / `Set Track Row Condition` | 管理轨道条件 | `UMovieSceneConditionExtensions` |

#### 绑定管理（Binding Extensions）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Is Valid` | 检查绑定是否有效 | `UMovieSceneBindingExtensions` |
| `Get Id` / `Get Name` / `Get Display Name` | 获取绑定信息 | `UMovieSceneBindingExtensions` |
| `Get Tracks` / `Find Tracks By Type` | 获取绑定上的轨道 | `UMovieSceneBindingExtensions` |
| `Add Track` / `Remove Track` | 管理绑定上的轨道 | `UMovieSceneBindingExtensions` |
| `Get Child Possessables` | 获取子 Possessable 绑定 | `UMovieSceneBindingExtensions` |
| `Set Parent` / `Get Parent` | 设置/获取父绑定 | `UMovieSceneBindingExtensions` |
| `Move Binding Contents` | 将一个绑定的所有内容移动到另一个绑定 | `UMovieSceneBindingExtensions` |
| `Tag Binding` / `Untag Binding` | 管理绑定标签 | `UMovieSceneBindingTagExtensions` |
| `Get All Binding Tags` | 获取所有绑定标签名 | `UMovieSceneBindingTagExtensions` |

#### 关键帧通道操作（Key/Channel Operations）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Add Key (Float)` / `Add Key (Double)` / `Add Key (Integer)` / `Add Key (Bool)` 等 | 为不同类型通道添加关键帧 | `UMovieSceneScripting*Channel` |
| `Remove Key` | 移除关键帧 | `UMovieSceneScripting*Channel` |
| `Get Keys` / `Get Keys By Index` | 获取所有/按索引获取关键帧 | `UMovieSceneScripting*Channel` |
| `Get Num Keys` | 获取关键帧数量 | `UMovieSceneScripting*Channel` |
| `Evaluate Keys` | 在指定范围内烘焙求值关键帧 | `UMovieSceneScripting*Channel` |
| `Compute Effective Range` | 计算通道的有效时间范围 | `UMovieSceneScripting*Channel` |
| `Set Default` / `Get Default` / `Remove Default` / `Has Default` | 管理通道默认值 | `UMovieSceneScripting*Channel` |
| `Transform` | 对通道中的关键帧进行偏移/缩放/枢轴变换 | `UMovieSceneScripting*Channel` |
| `Get Time` / `Set Time` | 获取/设置关键帧时间 | `UMovieSceneScripting*Key` |
| `Get Value` / `Set Value` | 获取/设置关键帧值 | `UMovieSceneScripting*Key` |
| `Get Interpolation Mode` / `Set Interpolation Mode` | 获取/设置插值模式（浮点通道） | `UMovieSceneScriptingFloatKey` |
| `Get Arrive Tangent` / `Set Arrive Tangent` | 获取/设置到达切线（浮点通道） | `UMovieSceneScriptingFloatKey` |
| `Get Leave Tangent` / `Set Leave Tangent` | 获取/设置离开切线（浮点通道） | `UMovieSceneScriptingFloatKey` |

#### 范围操作（Range Extensions）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Has Start` / `Has End` | 检查范围是否有起止边界 | `USequencerScriptingRangeExtensions` |
| `Get Start Frame` / `Get End Frame` | 获取范围起止帧 | `USequencerScriptingRangeExtensions` |
| `Set Start Frame` / `Set End Frame` | 设置范围起止帧 | `USequencerScriptingRangeExtensions` |
| `Get Start Seconds` / `Get End Seconds` | 获取范围起止秒数 | `USequencerScriptingRangeExtensions` |
| `Remove Start` / `Remove End` | 移除范围边界使其无限 | `USequencerScriptingRangeExtensions` |

#### 文件夹管理（Folder Extensions）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Folder Name` / `Set Folder Name` | 获取/设置文件夹名称 | `UMovieSceneFolderExtensions` |
| `Get Child Folders` / `Add Child Folder` | 管理子文件夹 | `UMovieSceneFolderExtensions` |
| `Get Child Tracks` / `Add Child Track` | 管理文件夹中的轨道 | `UMovieSceneFolderExtensions` |
| `Get Child Object Bindings` / `Add Child Object Binding` | 管理文件夹中的绑定 | `UMovieSceneFolderExtensions` |

#### 时间扭曲（TimeWarp Extensions）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `To PlayRate` | 将 TimeWarp 变体转换为播放速率 | `UMovieSceneTimeWarpExtensions` |
| `To Fixed PlayRate` / `Set Fixed PlayRate` | 获取/设置固定播放速率 | `UMovieSceneTimeWarpExtensions` |

### 使用示例（蓝图描述）

**示例 1：用脚本创建一个 Level Sequence 并添加 Float 关键帧**

1. 使用 `Create Level Sequence`（或其他资产创建方式）获得一个 `ULevelSequence` 引用
2. 在该 Sequence 上调用 `Get Movie Scene` → `Add Track`（传入 `UMovieSceneFloatTrack` 类型）
3. 在返回的 Track 上调用 `Add Section` → 获得 `UMovieSceneSection`
4. 在 Section 上调用 `Get Channels By Type`（传入 `UMovieSceneScriptingFloatChannel` 类型）→ 获得 Channel
5. 在 Channel 上调用 `Add Key (Float)`，传入时间（FrameNumber）和值
6. 重复步骤 5 添加更多关键帧

**示例 2：批量偏移序列中的所有关键帧**

1. 获取 Sequence → `Get Tracks` → 遍历所有 Track
2. 对每个 Track 调用 `Get Sections` → 遍历所有 Section
3. 对每个 Section 调用 `Get All Channels` → 遍历所有 Channel
4. 对每个 Channel 调用 `Transform`，传入偏移量（OffsetFrame）和范围（ScriptingRange）

**示例 3：给绑定添加标签**

1. 获取 Sequence → `Get Bindings` → 选择目标 Binding
2. 在 Binding 上调用 `Tag Binding`，传入标签名 `"MyTag"`
3. 在运行时通过 `Find Binding By Tag` 查找该绑定

## C++ 用法

### 头文件引入

```cpp
#include "MovieSceneSequenceExtensions.h"
#include "MovieSceneSectionExtensions.h"
#include "MovieSceneTrackExtensions.h"
#include "MovieSceneBindingExtensions.h"
#include "MovieSceneScriptingChannel.h"
#include "MovieSceneScriptingFloat.h"       // Float/Double 通道
#include "MovieSceneScriptingDouble.h"      // Double 通道
#include "MovieSceneScriptingInteger.h"     // Integer 通道
#include "MovieSceneScriptingBool.h"        // Bool 通道
#include "MovieSceneScriptingString.h"      // String 通道
#include "MovieSceneScriptingEvent.h"       // Event 通道
#include "MovieSceneScriptingActorReference.h" // Actor Reference 通道
#include "SequencerScriptingRange.h"
```

### 基本用法

**在 C++ 中通过 Sequence Extensions 管理序列**（来源：`MovieSceneSequenceExtensions.h`）

```cpp
// 获取序列的 MovieScene 对象
UMovieScene* MovieScene = UMovieSceneSequenceExtensions::GetMovieScene(MySequence);

// 获取序列中的所有轨道
TArray<UMovieSceneTrack*> Tracks = UMovieSceneSequenceExtensions::GetTracks(MySequence);

// 按类型查找轨道
TArray<UMovieSceneTrack*> FloatTracks = UMovieSceneSequenceExtensions::FindTracksByType(
    MySequence, UMovieSceneFloatTrack::StaticClass());

// 添加新轨道
UMovieSceneTrack* NewTrack = UMovieSceneSequenceExtensions::AddTrack(
    MySequence, UMovieSceneFloatTrack::StaticClass());

// 设置显示帧率和时钟分辨率
UMovieSceneSequenceExtensions::SetDisplayRate(MySequence, FFrameRate(30, 1));
UMovieSceneSequenceExtensions::SetTickResolution(MySequence, FFrameRate(24000, 1));

// 设置播放范围
UMovieSceneSequenceExtensions::SetPlaybackStart(MySequence, 0);
UMovieSceneSequenceExtensions::SetPlaybackEnd(MySequence, 300); // 10 秒 @ 30fps
```

**管理片段时间范围**（来源：`MovieSceneSectionExtensions.h`）

```cpp
// 获取片段的起止帧
bool bHasStart = UMovieSceneSectionExtensions::HasStartFrame(MySection);
if (bHasStart)
{
    int32 StartFrame = UMovieSceneSectionExtensions::GetStartFrame(MySection);
}

// 设置片段范围
UMovieSceneSectionExtensions::SetRange(MySection, 0, 150);

// 以秒为单位设置
UMovieSceneSectionExtensions::SetRangeSeconds(MySection, 0.0f, 5.0f);

// 获取片段中的所有通道
TArray<UMovieSceneScriptingChannel*> AllChannels = 
    UMovieSceneSectionExtensions::GetAllChannels(MySection);
```

### 进阶用法

**创建序列、添加绑定和关键帧的完整流程**（来源：`MovieSceneSequenceExtensions.h` + `MovieSceneBindingExtensions.h` + `MovieSceneScriptingFloat.h`）

```cpp
// 1. 创建一个 Possessable 绑定
FGuid BindingId = MySequence->GetMovieScene()->AddPossessable(
    TEXT("MyActor"), AActor::StaticClass());
FMovieSceneBindingProxy BindingProxy(BindingId, MySequence);

// 2. 为该绑定添加 Transform 轨道
UMovieSceneTrack* Track = UMovieSceneBindingExtensions::AddTrack(
    BindingProxy, UMovieScene3DTransformTrack::StaticClass());

// 3. 获取 Track 的 Section
UMovieSceneSection* Section = UMovieSceneTrackExtensions::AddSection(Track);

// 4. 设置片段范围
UMovieSceneSectionExtensions::SetRange(Section, 0, 300);

// 5. 获取 Float Channel 并添加关键帧
TArray<UMovieSceneScriptingChannel*> Channels = 
    UMovieSceneSectionExtensions::GetAllChannels(Section);

for (UMovieSceneScriptingChannel* Channel : Channels)
{
    if (UMovieSceneScriptingFloatChannel* FloatChannel = 
            Cast<UMovieSceneScriptingFloatChannel>(Channel))
    {
        // 在帧 0 添加值为 0.0 的关键帧
        UMovieSceneScriptingFloatKey* Key0 = FloatChannel->AddKey(
            FFrameNumber(0), 0.0f, 0.f, EMovieSceneTimeUnit::DisplayRate);
        
        // 在帧 300 添加值为 100.0 的关键帧
        UMovieSceneScriptingFloatKey* Key1 = FloatChannel->AddKey(
            FFrameNumber(300), 100.0f, 0.f, EMovieSceneTimeUnit::DisplayRate);
        
        // 设置插值模式为立方插值
        Key0->SetInterpolationMode(ERichCurveInterpMode::RCIM_Cubic);
        Key1->SetInterpolationMode(ERichCurveInterpMode::RCIM_Cubic);
        
        // 设置切线
        Key0->SetLeaveTangent(0.5f);
        Key1->SetArriveTangent(0.5f);
    }
}
```

**批量修改关键帧（Transform 操作）**（来源：`MovieSceneScriptingChannel.h`）

```cpp
// 对某个通道中的所有关键帧进行批量偏移
for (UMovieSceneScriptingChannel* Channel : AllChannels)
{
    if (UMovieSceneScriptingFloatChannel* FloatChannel = 
            Cast<UMovieSceneScriptingFloatChannel>(Channel))
    {
        // 创建一个范围覆盖整个序列
        FSequencerScriptingRange ScriptingRange = 
            UMovieSceneSequenceExtensions::MakeRange(MySequence, 0, 300);
        
        // 偏移 100 帧，不缩放，以帧 0 为枢轴
        FloatChannel->Transform(
            FFrameNumber(100),     // 偏移量
            1.0,                   // 缩放因子（1.0 = 不缩放）
            FFrameNumber(0),       // 枢轴帧
            ScriptingRange,        // 范围
            EMovieSceneTimeUnit::DisplayRate
        );
    }
}
```

**操作 Event Track**（来源：`MovieSceneEventTrackExtensions.h`）

```cpp
// 为序列添加事件轨道
UMovieSceneEventTrack* EventTrack = UMovieSceneSequenceExtensions::AddTrack(
    MySequence, UMovieSceneEventTrack::StaticClass())->Cast<UMovieSceneEventTrack>();

// 添加事件触发片段
UMovieSceneEventTriggerSection* TriggerSection = 
    UMovieSceneEventTrackExtensions::AddEventTriggerSection(EventTrack);

// 获取事件通道并添加事件关键帧
TArray<UMovieSceneScriptingChannel*> EventChannels = 
    UMovieSceneSectionExtensions::GetAllChannels(TriggerSection);

for (UMovieSceneScriptingChannel* Ch : EventChannels)
{
    if (UMovieSceneScriptingEventChannel* EventChannel = 
            Cast<UMovieSceneScriptingEventChannel>(Ch))
    {
        FMovieSceneEvent EventPayload;
        EventPayload.CallInEditor = true;
        // ... 配置事件有效载荷 ...
        
        EventChannel->AddKey(FFrameNumber(60), EventPayload);
    }
}
```

## Demo 示例

一个完整的、可编译的最小示例：通过 C++ 创建一个 Level Sequence，添加 Float 轨道并设置关键帧。

### MySequenceBuilder.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "MovieSceneSequenceExtensions.h"
#include "MovieSceneSectionExtensions.h"
#include "MovieSceneTrackExtensions.h"
#include "MovieSceneScriptingFloat.h"
#include "SequencerScriptingRange.h"
#include "MySequenceBuilder.generated.h"

class ULevelSequence;

UCLASS()
class UMySequenceBuilder : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    /**
     * 创建一个简单的动画序列：包含 2 个 Float 关键帧
     * @param InLevelSequence 目标 Level Sequence
     */
    UFUNCTION(BlueprintCallable, Category = "Demo")
    static void BuildSimpleFloatAnimation(ULevelSequence* InLevelSequence);
};
```

### MySequenceBuilder.cpp

```cpp
#include "MySequenceBuilder.h"
#include "LevelSequence.h"
#include "MovieScene.h"
#include "Tracks/MovieSceneFloatTrack.h"
#include "Sections/MovieSceneFloatSection.h"

void UMySequenceBuilder::BuildSimpleFloatAnimation(ULevelSequence* InLevelSequence)
{
    if (!InLevelSequence)
    {
        UE_LOG(LogTemp, Error, TEXT("BuildSimpleFloatAnimation: InLevelSequence is null"));
        return;
    }

    // 1. 设置序列参数
    UMovieSceneSequenceExtensions::SetDisplayRate(InLevelSequence, FFrameRate(30, 1));
    UMovieSceneSequenceExtensions::SetPlaybackStart(InLevelSequence, 0);
    UMovieSceneSequenceExtensions::SetPlaybackEnd(InLevelSequence, 150); // 5 秒 @ 30fps

    // 2. 添加 Float 轨道（Master 轨道级别）
    UMovieSceneTrack* Track = UMovieSceneSequenceExtensions::AddTrack(
        InLevelSequence, UMovieSceneFloatTrack::StaticClass());

    if (!Track)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to add float track"));
        return;
    }

    // 3. 添加片段
    UMovieSceneSection* Section = UMovieSceneTrackExtensions::AddSection(Track);
    if (!Section)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to add section"));
        return;
    }

    // 4. 设置片段范围
    UMovieSceneSectionExtensions::SetRange(Section, 0, 150);

    // 5. 获取 Float Channel
    TArray<UMovieSceneScriptingChannel*> Channels = 
        UMovieSceneSectionExtensions::GetAllChannels(Section);

    for (UMovieSceneScriptingChannel* Channel : Channels)
    {
        UMovieSceneScriptingFloatChannel* FloatChannel = 
            Cast<UMovieSceneScriptingFloatChannel>(Channel);
        if (!FloatChannel) continue;

        // 6. 添加关键帧：帧 0 值为 0.0
        UMovieSceneScriptingFloatKey* Key0 = FloatChannel->AddKey(
            FFrameNumber(0), 0.0f, 0.f, EMovieSceneTimeUnit::DisplayRate);

        // 7. 添加关键帧：帧 150 值为 1.0
        UMovieSceneScriptingFloatKey* Key1 = FloatChannel->AddKey(
            FFrameNumber(150), 1.0f, 0.f, EMovieSceneTimeUnit::DisplayRate);

        // 8. 设置立方插值
        if (Key0) Key0->SetInterpolationMode(ERichCurveInterpMode::RCIM_Cubic);
        if (Key1) Key1->SetInterpolationMode(ERichCurveInterpMode::RCIM_Cubic);

        // 9. 设置默认值
        FloatChannel->SetDefault(0.0f);

        // 10. 验证：烘焙求值
        FSequencerScriptingRange Range = 
            UMovieSceneSequenceExtensions::MakeRange(InLevelSequence, 0, 150);
        TArray<float> EvaluatedValues = FloatChannel->EvaluateKeys(
            Range, FFrameRate(30, 1));

        UE_LOG(LogTemp, Log, TEXT("Evaluated %d key values across the range"), 
            EvaluatedValues.Num());

        // 只处理第一个通道
        break;
    }

    UE_LOG(LogTemp, Log, TEXT("Simple float animation built successfully"));
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MovieScene` | Sequencer 核心数据结构（MovieScene、Track、Section、Channel 等） |
| `MovieSceneTracks` | 内置轨道类型（Float、Transform、Event 等） |
| `LevelSequence` | LevelSequence 资产类型 |
| `TimeManagement` | 时间码和时钟源相关 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `b209798d` | Anim In Engine: Add bRemoveExcludedCurves option to animation recording so we can remove curves alre | 动画录制添加排除曲线移除选项 |
| 2026-04-24 | `8b8110b4` | [EDA] Add Sequencer tool wrappers + fix sequencer toolset tests | 添加 Sequencer 工具封装并修复工具集测试 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移至 UE_LOGF |
| 2026-04-10 | `77af3950` | [EDA] Add SequencerTools toolset with Anim Mixer split into separate plugin | 将 Anim Mixer 拆分为独立插件并添加 SequencerTools |
| 2026-04-10 | `8bd8f719` | [Backout] - CL52569948 | 回退提交 CL52569948 |

### 维护评价

**活跃维护中**。

该插件创建于 2018 年，已超过 7 年历史，但持续有实质性更新。从近期提交记录看，2026 年 4-5 月仍有功能添加（Sequencer 工具封装、日志系统迁移等），表明 Epic 仍在积极维护。

**注意事项**：
- `.uplugin` 中 `IsBetaVersion = true`，意味着该 API 可能在未来版本中发生变化
- `SupportedPrograms` 包含 `LiveLinkHub`，表明此插件对虚拟制片管线有特别关注
- `EnabledByDefault = false`，需要在项目设置中手动启用插件
- 该插件大量使用 `ScriptMethod` 元数据提升函数到目标类上，这是一种 UE5 特有的蓝图暴露模式，与传统直接在类上定义函数不同
- 部分标记为 `DevelopmentOnly` 的函数（如 `Set DisplayName`、Folder 颜色等）在打包版本中不可用
- 通道系统的 `Float` 通道同时支持 `FMovieSceneFloatChannel` 和 `FMovieSceneDoubleChannel`，通过内部适配统一为 Float API

**推荐使用**：如果你需要通过 Python 或蓝图程序化操作 Sequencer 数据，这是官方推荐的方式。尽管标记为 Beta，但实际上已经成为许多影视管线的核心依赖。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/SequencerScripting)
- 官方文档：无（.uplugin 中 DocsURL 为空）