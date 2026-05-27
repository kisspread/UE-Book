# Sequencer Scripting

> Python and editor utility scripting extensions for sequencer and movie scenes（Beta 版本，提供 Sequencer 关键帧/轨道/绑定等数据的蓝图与 Python 脚本化访问）

| 属性 | 值 |
|---|---|
| 中文名 | 序列器脚本 |
| 分类 | Scripting |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产/脚本支持） |
| 模块 | `SequencerScripting` (Runtime), `SequencerScriptingEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-05-09 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/SequencerScripting) | |

## 用途

Sequencer Scripting 插件将 Unreal Engine 的 Sequencer（时间轴编辑器）内部数据结构暴露给蓝图和 Python 脚本，使开发者能够在编辑器外通过代码自动创建、修改、分析动画序列。

核心功能包括：
- **关键帧（Key）的编程化创建、读取、修改与删除**：覆盖 Float、Double、Bool、Integer、String、Text、Event、Particle、ObjectPath、ActorReference 等全部主流通道类型。
- **通道（Channel）的批量操控**：设置/获取默认值、批量变换关键帧时间、烘焙评估通道值、计算有效时间范围。
- **绑定（Binding）的查询与管理**：创建 Possessable/Spawnable 绑定、查找/添加/移除轨道、管理父子层级、设置绑定标签。
- **序列（Sequence）的全局属性**：修改播放范围、显示帧率、Tick 分辨率、评估类型、标记帧（Marked Frames）、工作区/视区范围。
- **轨道（Track）与 Section 的精细控制**：添加/移除 Section、设置时间范围（帧/秒）、访问通道数据、配置缓入/缓出。

此插件解决的核心问题是：**没有它，Sequencer 只能通过编辑器 UI 手工操作；有了它，整个 Sequencer 数据都可以通过 Python 脚本自动化**，实现批量动画编辑、CI 流水线中的序列验证、程序化动画生成等场景。

## 使用场景

- 你需要用 Python 脚本批量为多个角色创建 Level Sequence → 用此插件创建序列并添加 Transform 轨道
- 你需要自动化地为大量资产生成预览动画 → 用 Python 遍历资产列表，为每个创建关键帧动画
- 你需要在 CI 流水线中验证动画序列的时间范围/关键帧数量是否正确 → 用此插件的查询 API 进行断言
- 你需要在蓝图中动态读取/修改 Sequencer 轨道的关键帧数据 → 使用暴露的 BlueprintCallable 节点
- 你需要自定义 Sequencer 编辑器工具 → 结合此插件与 Editor Utility Widget 实现自动化工具

## 蓝图用法

所有 API 通过 `meta=(ScriptMethod)` 标记，以扩展方法（Extension Method）的形式挂载到 `UMovieSceneSequence`、`UMovieSceneSection`、`UMovieSceneTrack`、`FMovieSceneBindingProxy` 等核心类型上。

### 核心节点 — 序列操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Movie Scene` | 获取序列的 MovieScene 数据对象 | `UMovieSceneSequenceExtensions` |
| `Find Tracks By Type` | 按类型查找序列中的所有轨道 | `UMovieSceneSequenceExtensions` |
| `Add Track` | 在序列中添加指定类型的新轨道 | `UMovieSceneSequenceExtensions` |
| `Get Display Rate` | 获取序列的显示帧率 | `UMovieSceneSequenceExtensions` |
| `Set Display Rate` | 设置序列的显示帧率 | `UMovieSceneSequenceExtensions` |
| `Make Range` | 创建一个帧格式的时间范围 | `UMovieSceneSequenceExtensions` |
| `Get Playback Range` | 获取序列播放范围 | `UMovieSceneSequenceExtensions` |
| `Set Playback Start` | 设置序列播放起始帧 | `UMovieSceneSequenceExtensions` |
| `Get Master Tracks` | 获取序列主轨道列表 | `UMovieSceneSequenceExtensions` |
| `Add Marked Frame` | 添加标记帧 | `UMovieSceneSequenceExtensions` |
| `Find Bindings` | 按标签查找绑定 | `UMovieSceneSequenceExtensions` |

### 核心节点 — 绑定操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Is Valid` | 检查绑定是否有效 | `UMovieSceneBindingExtensions` |
| `Get Id` | 获取绑定的 GUID | `UMovieSceneBindingExtensions` |
| `Get Display Name` | 获取绑定的显示名称 | `UMovieSceneBindingExtensions` |
| `Get Tracks` | 获取绑定下的所有轨道 | `UMovieSceneBindingExtensions` |
| `Add Track` | 在绑定下添加新轨道 | `UMovieSceneBindingExtensions` |
| `Find Tracks By Type` | 按类型查找绑定下的轨道 | `UMovieSceneBindingExtensions` |
| `Remove Track` | 从绑定移除指定轨道 | `UMovieSceneBindingExtensions` |
| `Tag Binding` | 为绑定附加标签 | `UMovieSceneBindingTagExtensions` |
| `Get Binding Tags` | 获取绑定上的所有标签 | `UMovieSceneBindingTagExtensions` |

### 核心节点 — Section 操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Has Start Frame` / `Has End Frame` | 检查 Section 是否有起始/结束帧 | `UMovieSceneSectionExtensions` |
| `Set Range` | 设置 Section 的帧范围 | `UMovieSceneSectionExtensions` |
| `Get All Channels` | 获取 Section 下所有通道 | `UMovieSceneSectionExtensions` |
| `Get Section Condition` | 获取 Section 上的条件 | `UMovieSceneConditionExtensions` |
| `Get Ease In Duration` | 获取缓入持续帧数 | `UMovieSceneSectionEasingExtensions` |

### 核心节点 — 关键帧操作（以 Float 通道为例）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Add Key (Float)` | 向 Float 通道添加关键帧 | `UMovieSceneScriptingFloatChannel` |
| `Remove Key (Float)` | 移除指定关键帧 | `UMovieSceneScriptingFloatChannel` |
| `Get Keys (Float)` | 获取通道所有关键帧 | `UMovieSceneScriptingFloatChannel` |
| `Evaluate Keys (Float)` | 在指定范围烘焙评估通道值 | `UMovieSceneScriptingFloatChannel` |
| `Set Default (Float)` | 设置通道默认值 | `UMovieSceneScriptingFloatChannel` |
| `Transform (Float)` | 批量偏移/缩放关键帧时间 | `UMovieSceneScriptingFloatChannel` |
| `Get Value (Float)` | 获取关键帧的浮点值 | `UMovieSceneScriptingActualFloatKey` |
| `Set Value (Float)` | 设置关键帧的浮点值 | `UMovieSceneScriptingActualFloatKey` |
| `Get Time (Float)` | 获取关键帧时间 | `UMovieSceneScriptingActualFloatKey` |
| `Set Interpolation Mode` | 设置关键帧插值模式 | `UMovieSceneScriptingActualFloatKey` |
| `Set Arrive Tangent` | 设置到达切线值 | `UMovieSceneScriptingActualFloatKey` |

### 使用示例（蓝图描述）

**示例 1：创建序列并添加动画关键帧**

1. 使用 `Create Level Sequence` 节点创建新序列（需 Sequencer Editor 模块）
2. 拖拽序列资产到蓝图，使用 `Get Movie Scene` 获取 MovieScene
3. 使用 `Add Track` 并指定 `UMovieSceneFloatTrack` 轨道类型
4. 对轨道调用 `Add Section`，对 Section 调用 `Set Range` 设置时间范围
5. 对 Section 调用 `Get All Channels` 获取 Float 通道
6. 对通道循环调用 `Add Key (Float)` 添加关键帧，传入帧号和值

**示例 2：查询并修改已有序列的关键帧**

1. 通过资产引用获取 `ULevelSequence`
2. 调用 `Find Tracks By Type` 查找所有 Float 轨道
3. 对每个轨道调用 `Get Sections` 获取所有 Section
4. 对 Section 调用 `Get All Channels` 或 `Get Channels By Type`
5. 对每个通道调用 `Get Keys` 获取关键帧列表
6. 对每个关键帧调用 `Get Value`/`Set Value` 和 `Get Time`/`Set Time` 进行修改

## C++ 用法

### 头文件引入

```cpp
#include "MovieSceneSequenceExtensions.h"
#include "MovieSceneBindingExtensions.h"
#include "MovieSceneSectionExtensions.h"
#include "MovieSceneTrackExtensions.h"
#include "MovieSceneScriptingChannel.h"
```

### 基本用法 — 创建序列并添加关键帧

```cpp
// 创建新的 Level Sequence 资产
ULevelSequence* NewSequence = NewObject<ULevelSequence>(GetTransientPackage(), "TestSequence");

// 获取 MovieScene
UMovieScene* MovieScene = UMovieSceneSequenceExtensions::GetMovieScene(NewSequence);

// 添加一个 Float 轨道到 Master Tracks
UMovieSceneFloatTrack* FloatTrack = Cast<UMovieSceneFloatTrack>(
    UMovieSceneSequenceExtensions::AddTrack(NewSequence, UMovieSceneFloatTrack::StaticClass())
);

// 添加 Section 并设置时间范围
UMovieSceneSection* Section = UMovieSceneTrackExtensions::AddSection(FloatTrack);
UMovieSceneSectionExtensions::SetRange(Section, 0, 120);  // 0 到 120 帧

// 获取通道并添加关键帧
TArray<UMovieSceneScriptingChannel*> Channels = UMovieSceneSectionExtensions::GetAllChannels(Section);
for (UMovieSceneScriptingChannel* Channel : Channels)
{
    if (UMovieSceneScriptingFloatChannel* FloatChannel = Cast<UMovieSceneScriptingFloatChannel>(Channel))
    {
        FloatChannel->AddKey(FFrameNumber(0), 1.0f);
        FloatChannel->AddKey(FFrameNumber(60), 0.5f);
        FloatChannel->AddKey(FFrameNumber(120), 0.0f);
    }
}
```

### 基本用法 — 查询绑定与轨道

```cpp
// 获取序列中所有 Possessable 绑定
TArray<FMovieSceneBindingProxy> Bindings = UMovieSceneSequenceExtensions::GetPossessables(NewSequence);

for (const FMovieSceneBindingProxy& Binding : Bindings)
{
    // 获取绑定下的所有轨道
    TArray<UMovieSceneTrack*> Tracks = UMovieSceneBindingExtensions::GetTracks(Binding);
    
    for (UMovieSceneTrack* Track : Tracks)
    {
        TArray<UMovieSceneSection*> Sections = UMovieSceneTrackExtensions::GetSections(Track);
        
        for (UMovieSceneSection* Section : Sections)
        {
            // 访问 Section 的起止时间
            if (UMovieSceneSectionExtensions::HasStartFrame(Section))
            {
                int32 StartFrame = UMovieSceneSectionExtensions::GetStartFrame(Section);
                int32 EndFrame = UMovieSceneSectionExtensions::GetEndFrame(Section);
                UE_LOG(LogTemp, Log, TEXT("Section range: %d - %d"), StartFrame, EndFrame);
            }
        }
    }
}
```

### 进阶用法 — 批量烘焙通道评估值

```cpp
// 评估 Float 通道在指定范围内的所有值
UMovieSceneScriptingFloatChannel* FloatChannel = /* ...获取通道... */;

// 创建评估范围：0 到 120 帧
FSequencerScriptingRange EvalRange;
EvalRange.bHasStart = true;
EvalRange.bHasEnd = true;
EvalRange.InclusiveStart = 0;
EvalRange.ExclusiveEnd = 120;

// 以每帧 1 次的频率评估
TArray<float> BakedValues = FloatChannel->EvaluateKeys(EvalRange, FFrameRate(30, 1));

for (int32 i = 0; i < BakedValues.Num(); ++i)
{
    UE_LOG(LogTemp, Log, TEXT("Frame %d: Value = %f"), i, BakedValues[i]);
}
```

### 进阶用法 — 配置通道默认值与插值

```cpp
UMovieSceneScriptingFloatChannel* FloatChannel = /* ... */;

// 设置通道默认值（无关键帧时使用的值）
FloatChannel->SetDefault(0.5f);
bool bHasDefault = FloatChannel->HasDefault();
float DefaultVal = FloatChannel->GetDefault();

// 添加带自定义插值的关键帧
UMovieSceneScriptingFloatKey* Key = FloatChannel->AddKey(
    FFrameNumber(30), 1.0f, 0.0f,
    EMovieSceneTimeUnit::DisplayRate,
    EMovieSceneKeyInterpolation::Cubic
);

// 设置切线
Key->SetArriveTangent(0.5f);
Key->SetLeaveTangent(-0.5f);
Key->SetInterpolationMode(ERichCurveInterpMode::RCIM_Cubic);
Key->SetTangentMode(ERichCurveTangentMode::RCTM_User);

// 批量变换关键帧时间（偏移 +10 帧，缩放 2x）
FSequencerScriptingRange TransformRange;
TransformRange.bHasStart = true;
TransformRange.bHasEnd = true;
TransformRange.InclusiveStart = 0;
TransformRange.ExclusiveEnd = 120;
FloatChannel->Transform(FFrameNumber(10), 2.0, FFrameNumber(0), TransformRange);
```

## Demo 示例

```cpp
// SequencerScriptingDemo.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/EditorSubsystem.h"
#include "SequencerScriptingDemo.generated.h"

UCLASS()
class USequencerScriptingDemo : public UEditorSubsystem
{
    GENERATED_BODY()

public:
    /** 创建一个简单的渐变动画序列 */
    UFUNCTION(BlueprintCallable, Category = "Demo")
    void CreateGradientAnimationSequence();
};
```

```cpp
// SequencerScriptingDemo.cpp
#include "SequencerScriptingDemo.h"

#include "LevelSequence.h"
#include "MovieScene.h"
#include "MovieSceneSequenceExtensions.h"
#include "MovieSceneSectionExtensions.h"
#include "MovieSceneTrackExtensions.h"
#include "MovieSceneBindingExtensions.h"
#include "MovieSceneScriptingChannel.h"

#include "Tracks/MovieSceneFloatTrack.h"
#include "Sections/MovieSceneFloatSection.h"

void USequencerScriptingDemo::CreateGradientAnimationSequence()
{
    // 1. 创建 Level Sequence
    ULevelSequence* Sequence = NewObject<ULevelSequence>(
        GetTransientPackage(), "DemoSequence", RF_Transient
    );

    // 2. 设置播放范围（0 ~ 150 帧 @ 30fps = 5 秒）
    UMovieSceneSequenceExtensions::SetPlaybackStart(Sequence, 0);
    UMovieSceneSequenceExtensions::SetPlaybackEnd(Sequence, 150);
    UMovieSceneSequenceExtensions::SetDisplayRate(Sequence, FFrameRate(30, 1));

    // 3. 添加一个 Float 轨道（用于控制某个浮点属性）
    UMovieSceneTrack* Track = UMovieSceneSequenceExtensions::AddTrack(
        Sequence, UMovieSceneFloatTrack::StaticClass()
    );

    // 4. 添加 Section 并配置时间范围
    UMovieSceneSection* Section = UMovieSceneTrackExtensions::AddSection(Track);
    UMovieSceneSectionExtensions::SetRange(Section, 0, 150);

    // 5. 获取 Float 通道并创建关键帧
    TArray<UMovieSceneScriptingChannel*> Channels =
        UMovieSceneSectionExtensions::GetAllChannels(Section);

    for (UMovieSceneScriptingChannel* Channel : Channels)
    {
        if (UMovieSceneScriptingFloatChannel* FloatChannel =
                Cast<UMovieSceneScriptingFloatChannel>(Channel))
        {
            // 设置默认值
            FloatChannel->SetDefault(0.0f);

            // 创建渐变关键帧：0.0 -> 1.0 -> 0.0
            FloatChannel->AddKey(FFrameNumber(0), 0.0f);
            FloatChannel->AddKey(FFrameNumber(75), 1.0f);
            FloatChannel->AddKey(FFrameNumber(150), 0.0f);

            // 设置三次插值
            TArray<UMovieSceneScriptingKey*> Keys = FloatChannel->GetKeys();
            for (UMovieSceneScriptingKey* K : Keys)
            {
                if (UMovieSceneScriptingFloatKey* FKey =
                        Cast<UMovieSceneScriptingFloatKey>(K))
                {
                    FKey->SetInterpolationMode(ERichCurveInterpMode::RCIM_Cubic);
                }
            }

            // 6. 烘焙评估验证
            FSequencerScriptingRange Range;
            Range.bHasStart = true;
            Range.bHasEnd = true;
            Range.InclusiveStart = 0;
            Range.ExclusiveEnd = 150;

            TArray<float> Values = FloatChannel->EvaluateKeys(Range, FFrameRate(30, 1));
            UE_LOG(LogTemp, Log,
                TEXT("Gradient animation: %d frames evaluated, first=%f, mid=%f, last=%f"),
                Values.Num(),
                Values.IsValidIndex(0) ? Values[0] : -1.0f,
                Values.IsValidIndex(75) ? Values[75] : -1.0f,
                Values.IsValidIndex(149) ? Values[149] : -1.0f
            );
        }
    }

    UE_LOG(LogTemp, Log, TEXT("Demo sequence created successfully with %d tracks"),
        UMovieSceneSequenceExtensions::GetTracks(Sequence).Num());
}
```

## 模块依赖

从源码分析推断，本插件依赖以下模块（仅列出不常见的）：

| 模块 | 用途 |
|---|---|
| `MovieScene` | Sequencer 核心数据结构（MovieScene、Section、Channel 等） |
| `SequencerCore` | Sequencer 核心功能模块 |
| `LevelSequence` | Level Sequence 资产类型 |
| `MovieSceneTools` | Sequencer 编辑器工具 |
| `PythonScriptPlugin` | Python 脚本支持（.uplugin 声明的依赖） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `b209798d` | Anim In Engine: Add bRemoveExcludedCurves option to animation recording so we can remove curves alre | 动画录制新增排除曲线选项 |
| 2026-04-24 | `8b8110b4` | [EDA] Add Sequencer tool wrappers + fix sequencer toolset tests | 新增 Sequencer 工具包装器并修复测试 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移更新 |
| 2026-04-10 | `77af3950` | [EDA] Add SequencerTools toolset with Anim Mixer split into separate plugin | SequencerTools 工具集重构 |
| 2026-04-10 | `8bd8f719` | [Backout] - CL52569948 | 回退某次提交 |

### 维护评价

- **创建时间**：2018 年 5 月，已有约 8 年历史。
- **最近更新**：2026 年 4-5 月仍有活跃提交，主要集中在工具集重构、动画录制功能增强等方面。
- **维护状态**：活跃维护中。尽管标记为 `IsBetaVersion=true` 且 `Installed=false`（需手动启用），但 Epic 持续进行功能性更新。
- **已知限制**：
  - Beta 状态意味着 API 可能在未来版本中发生变化
  - 仅官方支持 `LiveLinkHub` 程序（从 `SupportedPrograms` 字段可知）
  - 某些标记为 `DevelopmentOnly` 的函数（如文件夹颜色设置、轨道显示名修改等）仅在开发构建中可用
- **推荐程度**：对于需要通过 Python/蓝图自动化 Sequencer 操作的项目，此插件是**必须**的。尽管标记为 Beta，其 API 稳定性和覆盖范围已相当成熟，实际生产中广泛使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/SequencerScripting)
- 官方文档（.uplugin 未提供 DocsURL）