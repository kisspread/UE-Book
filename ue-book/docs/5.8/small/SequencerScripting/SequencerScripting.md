# Sequencer Scripting

> Python and editor utility scripting extensions for sequencer and movie scenes

| 属性 | 值 |
|---|---|
| 中文名 | Sequencer 脚本扩展 |
| 分类 | Scripting |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（示例资产、测试蓝图） |
| 模块 | `SequencerScripting` (Runtime), `SequencerScriptingEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-05-09 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/SequencerScripting) | |

## 用途

SequencerScripting 将 Sequencer（Sequencer 编辑器中的 Movie Scene 序列系统）的内部数据结构通过一套面向脚本的代理类暴露给蓝图和 Python。它解决的核心问题是：原生 Sequencer API 面向 C++ 游戏线程和编辑器插桩设计，层级深、指针多、不直观，无法直接在蓝图/Python 中高效操作。

该插件提供了以下关键能力：

- **键（Key）级别的完整 CRUD**：对所有 Sequencer 支持的数据通道类型（Float、Double、Bool、Byte/Enum、Integer、String、Text、Event、Particle、ActorReference、ObjectPath、Color 等）进行添加、删除、修改和查询操作
- **通道（Channel）管理**：批量烘焙求值、有效范围计算、默认值管理、时间变换
- **绑定（Binding）扩展**：获取/设置 Possessable 和 Spawnable 绑定、管理轨道层级
- **序列（Sequence）控制**：播放范围、显示率/滴答分辨率、标记帧、求值类型等全局设置
- **文件夹（Folder）管理**：Sequencer 大纲中的组织结构操作
- **轨道（Track）/切片（Section）操作**：添加、删除、范围设置、缓入缓出、条件系统
- **标签系统**：基于名称的绑定标签，用于运行时查询（`FindBindingByTag`）

简而言之，这是一个让开发者通过 Python 脚本或蓝图程序化地创建、编辑和操控 Sequencer 序列的桥梁层。

## 使用场景

- 你需要批量生成数百个动画序列中的关键帧 → 用 Python 脚本遍历并操作 `UMovieSceneScriptingFloatChannel`
- 你在做程序化过场动画，需要根据配置表动态生成 Sequencer 绑定和轨道 → 用 `MovieSceneSequenceExtensions` 和 `MovieSceneBindingExtensions`
- 你想要在关卡蓝图中程序化地设置 Sequencer Section 的时间范围 → 用 `MovieSceneSectionExtensions`
- 你需要在运行时通过标签查找 Sequencer 中的绑定对象 → 用 `MovieSceneBindingTagExtensions`
- 你需要批量处理 Sequencer 的标记帧（Marked Frames）用于镜头管理 → 用 `MovieSceneSequenceExtensions` 的标记帧 API

## 蓝图用法

### 核心节点

#### 序列操作（MovieSceneSequenceExtensions）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetMovieScene` | 获取序列的底层 MovieScene 数据 | `UMovieSceneSequenceExtensions` |
| `GetTracks` / `FindTracksByType` / `FindTracksByExactType` | 查询序列中的轨道 | `UMovieSceneSequenceExtensions` |
| `AddTrack` / `RemoveTrack` | 添加或删除轨道 | `UMovieSceneSequenceExtensions` |
| `GetDisplayRate` / `SetDisplayRate` | 获取/设置序列的显示帧率 | `UMovieSceneSequenceExtensions` |
| `GetTickResolution` / `SetTickResolution` | 获取/设置序列的时间分辨率 | `UMovieSceneSequenceExtensions` |
| `GetPlaybackStart` / `SetPlaybackStart` / `GetPlaybackEnd` / `SetPlaybackEnd` | 控制播放范围 | `UMovieSceneSequenceExtensions` |
| `MakeRange` / `MakeRangeSeconds` | 创建时间范围对象 | `UMovieSceneSequenceExtensions` |
| `SetEvaluationType` / `SetClockSource` | 设置求值模式和时钟源 | `UMovieSceneSequenceExtensions` |
| `AddMarkedFrame` / `FindMarkedFrameByLabel` | 管理标记帧 | `UMovieSceneSequenceExtensions` |
| `FindMarkedFrameByFrameNumberInSequence` | 按帧号查找标记帧 | `UMovieSceneSequenceExtensions` |

#### 绑定操作（MovieSceneBindingExtensions）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsValid` | 检查绑定是否有效 | `UMovieSceneBindingExtensions` |
| `GetId` / `GetDisplayName` / `SetName` | 获取/设置绑定标识信息 | `UMovieSceneBindingExtensions` |
| `GetTracks` / `AddTrack` / `RemoveTrack` | 操作绑定上的轨道 | `UMovieSceneBindingExtensions` |
| `GetChildPossessables` / `GetParent` / `SetParent` | 管理绑定层级关系 | `UMovieSceneBindingExtensions` |
| `GetObjectTemplate` / `GetPossessedObjectClass` | 获取绑定关联的对象信息 | `UMovieSceneBindingExtensions` |
| `MoveBindingContents` | 将一个绑定的内容转移到另一个 | `UMovieSceneBindingExtensions` |
| `SetSpawnableBindingID` | 设置 Possessable 对 Spawnable 的引用 | `UMovieSceneBindingExtensions` |

#### 轨道操作（MovieSceneTrackExtensions）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddSection` / `GetSections` / `RemoveSection` | 管理轨道上的切片 | `UMovieSceneTrackExtensions` |
| `SetDisplayName` / `GetDisplayName` | 设置轨道显示名称 | `UMovieSceneTrackExtensions` |
| `SetSortingOrder` / `GetSortingOrder` | 控制轨道排序 | `UMovieSceneTrackExtensions` |
| `SetColorTint` / `GetColorTint` | 设置轨道颜色 | `UMovieSceneTrackExtensions` |
| `SetSectionToKey` / `GetSectionToKey` | 指定接收外部修改的关键切片 | `UMovieSceneTrackExtensions` |

#### 切片操作（MovieSceneSectionExtensions）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `HasStartFrame` / `HasEndFrame` | 检查切片是否有起止帧（非无限） | `UMovieSceneSectionExtensions` |
| `GetStartFrame` / `SetStartFrame` / `GetEndFrame` / `SetEndFrame` | 以帧号操作切片范围 | `UMovieSceneSectionExtensions` |
| `GetStartFrameSeconds` / `SetStartFrameSeconds` | 以秒操作切片范围 | `UMovieSceneSectionExtensions` |
| `SetRange` / `SetRangeSeconds` | 一次性设置切片范围 | `UMovieSceneSectionExtensions` |
| `GetAllChannels` / `GetChannelsByType` / `GetChannel` | 获取切片中的数据通道 | `UMovieSceneSectionExtensions` |
| `GetParentSequenceFrame` | 子序列切片的帧映射 | `UMovieSceneSectionExtensions` |

#### 键和通道操作（以 Float 为例）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddKey (Float)` | 在指定时间添加浮点关键帧 | `UMovieSceneScriptingFloatChannel` |
| `Remove Key (Float)` | 删除关键帧 | `UMovieSceneScriptingFloatChannel` |
| `Get Keys (Float)` | 获取所有关键帧 | `UMovieSceneScriptingFloatChannel` |
| `Get Num Keys (Float)` | 获取关键帧数量 | `UMovieSceneScriptingFloatChannel` |
| `Evaluate Keys (Float)` | 按指定帧率烘焙求值 | `UMovieSceneScriptingFloatChannel` |
| `Set Default (Float)` / `Get Default (Float)` | 管理无关键帧时的默认值 | `UMovieSceneScriptingFloatChannel` |
| `Transform (Float)` | 对通道内的关键帧进行时间偏移/缩放 | `UMovieSceneScriptingFloatChannel` |
| `Get Value (Float)` / `Set Value (Float)` | 操作单个关键帧的值 | `UMovieSceneScriptingFloatKey` |
| `Get Time (Float)` / `Set Time (Float)` | 操作单个关键帧的时间 | `UMovieSceneScriptingFloatKey` |
| `GetInterpolationMode` / `SetInterpolationMode` | 设置关键帧插值模式 | `UMovieSceneScriptingFloatKey` |
| `GetArriveTangent` / `SetLeaveTangent` | 操作贝塞尔切线 | `UMovieSceneScriptingFloatKey` |

> 所有通道类型（Double、Bool、Byte/Enum、Integer、String、Text、Event、Particle、ActorReference、ObjectPath）都有一组功能等价的节点，后缀分别为 `(Double)`、`(Bool)`、`(Enum)` 等。

#### 条件系统（MovieSceneConditionExtensions）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetSectionCondition` / `SetSectionCondition` / `ClearSectionCondition` | 管理切片级条件 | `UMovieSceneConditionExtensions` |
| `GetTrackCondition` / `SetTrackCondition` / `ClearTrackCondition` | 管理轨道级条件 | `UMovieSceneConditionExtensions` |
| `GetTrackRowCondition` / `SetTrackRowCondition` / `ClearTrackRowCondition` | 管理轨道行级条件 | `UMovieSceneConditionExtensions` |

#### 标签系统（MovieSceneBindingTagExtensions）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetAllBindingTags` | 获取序列中所有已注册的标签名 | `UMovieSceneBindingTagExtensions` |
| `GetBindingTags` | 获取特定绑定上的所有标签 | `UMovieSceneBindingTagExtensions` |
| `TagBinding` / `UntagBinding` | 为绑定添加/移除标签 | `UMovieSceneBindingTagExtensions` |
| `RemoveBindingTag` | 从序列中完全删除标签 | `UMovieSceneBindingTagExtensions` |

### 使用示例（蓝图描述）

**示例 1：程序化创建序列并添加关键帧**

1. 通过 `Asset > Create` 或 Python 创建一个 `ULevelSequence` 资产
2. 调用 `MovieSceneSequenceExtensions::GetPlaybackStart` 和 `SetPlaybackEnd` 设置播放范围（如 0 到 150 帧）
3. 调用 `MovieSceneSequenceExtensions::AddTrack` 为序列添加一个 `UMovieSceneFloatTrack`（目标属性的浮点轨道）
4. 通过 `MovieSceneTrackExtensions::GetSections` 获取新轨道的切片
5. 在切片上调用 `MovieSceneSectionExtensions::GetChannel` 获取浮点通道
6. 在通道上连续调用 `AddKey (Float)` 创建关键帧，传入帧号和值

**示例 2：批量变换关键帧时间**

1. 从 `MovieSceneSectionExtensions::GetAllChannels` 获取目标切片的所有通道
2. 对每个通道调用 `Get Keys` 获取所有关键帧
3. 调用 `Transform (Float)` 节点，传入偏移帧数、缩放比例和枢轴帧，一次性批量移动关键帧

**示例 3：通过标签在运行时查找绑定**

1. 在 Sequencer 编辑器中通过 RMB → Expose 为绑定添加标签（如 "MainCamera"）
2. 在运行时，调用 `MovieSceneSequenceExtensions::GetMovieScene` 获取 MovieScene
3. 使用 `UMovieSceneSequence::FindBindingByTag`（引擎原生 API）按标签名查找绑定

## C++ 用法

### 头文件引入

```cpp
#include "ExtensionLibraries/MovieSceneSequenceExtensions.h"
#include "ExtensionLibraries/MovieSceneBindingExtensions.h"
#include "ExtensionLibraries/MovieSceneSectionExtensions.h"
#include "ExtensionLibraries/MovieSceneTrackExtensions.h"
#include "MovieSceneScriptingChannel.h"
```

### 基本用法

操作序列和关键帧的完整流程（来源：基于源码中 `UMovieSceneSequenceExtensions` 和 `TMovieSceneScriptingChannel` 的实现）：

```cpp
// 1. 加载或创建一个 Level Sequence
ULevelSequence* LevelSequence = LoadObject<ULevelSequence>(nullptr, TEXT("/Game/MySequence"));

// 2. 获取底层 MovieScene
UMovieScene* MovieScene = UMovieSceneSequenceExtensions::GetMovieScene(LevelSequence);

// 3. 设置播放范围（帧号方式）
UMovieSceneSequenceExtensions::SetPlaybackStart(LevelSequence, 0);
UMovieSceneSequenceExtensions::SetPlaybackEnd(LevelSequence, 150);

// 4. 设置显示帧率
UMovieSceneSequenceExtensions::SetDisplayRate(LevelSequence, FFrameRate(24, 1));

// 5. 添加轨道
UMovieSceneFloatTrack* FloatTrack = Cast<UMovieSceneFloatTrack>(
    UMovieSceneSequenceExtensions::AddTrack(LevelSequence, UMovieSceneFloatTrack::StaticClass())
);

// 6. 获取轨道的切片
TArray<UMovieSceneSection*> Sections = UMovieSceneTrackExtensions::GetSections(FloatTrack);
UMovieSceneSection* Section = Sections[0];

// 7. 设置切片范围
UMovieSceneSectionExtensions::SetRange(Section, 0, 150);

// 8. 获取浮点通道并添加关键帧
TArray<UMovieSceneScriptingChannel*> Channels = 
    UMovieSceneSectionExtensions::GetAllChannels(Section);
UMovieSceneScriptingFloatChannel* FloatChannel = Cast<UMovieSceneScriptingFloatChannel>(Channels[0]);

if (FloatChannel)
{
    FloatChannel->AddKey(FFrameNumber(0), 0.0f);     // 第 0 帧，值 0
    FloatChannel->AddKey(FFrameNumber(50), 1.0f);    // 第 50 帧，值 1
    FloatChannel->AddKey(FFrameNumber(100), 0.0f);   // 第 100 帧，值 0
    
    // 设置默认值（无关键帧时使用）
    FloatChannel->SetDefault(0.5f);
}
```

### 进阶用法

**操作绑定并添加多个轨道：**

```cpp
// 获取序列中的所有绑定
TArray<FMovieSceneBindingProxy> Bindings; // 通常通过 GetSpawnables/GetPossessables 获得

for (const FMovieSceneBindingProxy& Binding : Bindings)
{
    // 检查绑定有效性
    if (!UMovieSceneBindingExtensions::IsValid(Binding))
        continue;
    
    // 获取绑定名称
    FText DisplayName = UMovieSceneBindingExtensions::GetDisplayName(Binding);
    
    // 获取绑定下的所有轨道
    TArray<UMovieSceneTrack*> Tracks = UMovieSceneBindingExtensions::GetTracks(Binding);
    
    // 查找特定类型的轨道
    TArray<UMovieSceneTrack*> FloatTracks = 
        UMovieSceneBindingExtensions::FindTracksByType(Binding, UMovieSceneFloatTrack::StaticClass());
    
    // 管理层级关系
    TArray<FMovieSceneBindingProxy> Children = 
        UMovieSceneBindingExtensions::GetChildPossessables(Binding);
    FMovieSceneBindingProxy Parent = 
        UMovieSceneBindingExtensions::GetParent(Binding);
}
```

**批量烘焙求值通道数据：**

```cpp
// 在指定范围内按特定帧率烘焙关键帧值
if (FloatChannel)
{
    FSequencerScriptingRange Range;
    Range.bHasStart = true;
    Range.bHasEnd = true;
    Range.InclusiveStart = 0;
    Range.ExclusiveEnd = 150;
    
    // 按 24fps 采样
    TArray<float> BakedValues = FloatChannel->EvaluateKeys(Range, FFrameRate(24, 1));
    
    // 获取通道有效范围
    FSequencerScriptingRange EffectiveRange = FloatChannel->ComputeEffectiveRange();
    int32 NumKeys = FloatChannel->GetNumKeys();
}
```

**使用标签系统：**

```cpp
#include "ExtensionLibraries/MovieSceneBindingTagExtensions.h"

// 为绑定添加标签
UMovieSceneBindingTagExtensions::TagBinding(BindingProxy, FName("CameraRig"));

// 获取绑定上的所有标签
TArray<FName> Tags = UMovieSceneBindingTagExtensions::GetBindingTags(BindingProxy);

// 获取序列中所有已注册的标签
TArray<FName> AllTags = UMovieSceneBindingTagExtensions::GetAllBindingTags(MySequence);

// 在运行时按标签查找绑定（使用引擎原生 API）
FMovieSceneBindingID FoundBinding = MySequence->FindBindingByTag(FName("CameraRig"));
```

## Demo 示例

```cpp
// SequencerScriptingDemo.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/EditorSubsystem.h"
#include "ExtensionLibraries/MovieSceneSequenceExtensions.h"
#include "ExtensionLibraries/MovieSceneTrackExtensions.h"
#include "ExtensionLibraries/MovieSceneSectionExtensions.h"
#include "SequencerScriptingDemo.generated.h"

UCLASS()
class USequencerScriptingDemoSubsystem : public UEditorSubsystem
{
    GENERATED_BODY()

public:
    /** 创建一个带有简单浮点动画的序列 */
    UFUNCTION(BlueprintCallable, Category = "Demo")
    ULevelSequence* CreateSimpleAnimationSequence();
};

// SequencerScriptingDemo.cpp
#include "SequencerScriptingDemo.h"
#include "LevelSequence.h"
#include "MovieScene.h"
#include "Tracks/MovieSceneFloatTrack.h"
#include "Sections/MovieSceneFloatSection.h"
#include "MovieSceneScriptingChannel.h"

ULevelSequence* USequencerScriptingDemoSubsystem::CreateSimpleAnimationSequence()
{
    // 创建新序列资产
    ULevelSequence* Sequence = NewObject<ULevelSequence>(GetTransientPackage(), NAME_None, RF_Transient);
    
    // 设置播放范围：0~120 帧
    UMovieSceneSequenceExtensions::SetPlaybackStart(Sequence, 0);
    UMovieSceneSequenceExtensions::SetPlaybackEnd(Sequence, 120);
    UMovieSceneSequenceExtensions::SetDisplayRate(Sequence, FFrameRate(24, 1));
    
    // 添加一个浮点轨道
    UMovieSceneFloatTrack* Track = Cast<UMovieSceneFloatTrack>(
        UMovieSceneSequenceExtensions::AddTrack(Sequence, UMovieSceneFloatTrack::StaticClass())
    );
    
    if (Track)
    {
        // 设置轨道属性名
        // UMovieScenePropertyTrackExtensions::SetPropertyNameAndPath(Track, "Opacity", "Opacity");
        
        // 获取自动创建的切片并设置范围
        TArray<UMovieSceneSection*> Sections = UMovieSceneTrackExtensions::GetSections(Track);
        if (Sections.Num() > 0)
        {
            UMovieSceneSectionExtensions::SetRange(Sections[0], 0, 120);
            
            // 获取浮点通道并添加关键帧
            TArray<UMovieSceneScriptingChannel*> Channels = 
                UMovieSceneSectionExtensions::GetAllChannels(Sections[0]);
            
            for (UMovieSceneScriptingChannel* Channel : Channels)
            {
                if (UMovieSceneScriptingFloatChannel* FloatChannel = 
                    Cast<UMovieSceneScriptingFloatChannel>(Channel))
                {
                    // 创建淡入淡出动画：0→1→0
                    FloatChannel->AddKey(FFrameNumber(0), 0.0f);
                    FloatChannel->AddKey(FFrameNumber(60), 1.0f);
                    FloatChannel->AddKey(FFrameNumber(120), 0.0f);
                    
                    // 设置无关键帧时的默认值
                    FloatChannel->SetDefault(0.0f);
                }
            }
        }
    }
    
    return Sequence;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LevelSequence` | Level Sequence 资产类型，序列编辑和播放 |
| `MovieScene` | Movie Scene 核心框架，通道、轨道、切片等基础设施 |
| `MovieSceneTracks` | 各种内置轨道类型（Float、Transform、Event 等） |
| `SequencerCore` | Sequencer 核心工具和绑定系统 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `b209798d` | Anim In Engine: Add bRemoveExcludedCurves option to animation recording so we can remove curves alre | 动画录制新增排除曲线选项 |
| 2026-04-24 | `8b8110b4` | [EDA] Add Sequencer tool wrappers + fix sequencer toolset tests | 添加 Sequencer 工具包装器并修复测试 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移至 UE_LOGF 格式 |
| 2026-04-10 | `77af3950` | [EDA] Add SequencerTools toolset with Anim Mixer split into separate plugin | 添加 SequencerTools 工具集，Anim Mixer 拆分为独立插件 |
| 2026-04-10 | `8bd8f719` | [Backout] - CL52569948 | 回退一次提交（CL52569948） |

### 维护评价

**活跃维护**。该插件自 2018 年创建以来一直持续更新，最近的提交集中在 2026 年 4-5 月，说明 Epic 仍在积极维护。近期改动包括：新增 Sequencer 工具封装、Anim Mixer 功能拆分、日志宏迁移等。尽管 `.uplugin` 中 `IsBetaVersion=true`，但实际上该插件已稳定使用多年，`Installed=false` 表示默认不启用（需手动启用）。`SupportedPrograms` 仅包含 `LiveLinkHub`，暗示主要用于专业影视管线而非游戏运行时。该插件属于 Sequencer 编辑器生态的核心扩展，长期推荐使用。

⚠️ 注意：`IsBetaVersion=true` 且 `Installed=false`，使用前需在插件管理器中手动启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/SequencerScripting)
- [官方文档]()（无官方文档链接）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/SequencerScripting/Tests)