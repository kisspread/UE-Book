# Sequencer Scripting

> Python and editor utility scripting extensions for sequencer and movie scenes

| 属性 | 值 |
|---|---|
| 中文名 | 序列脚本扩展 |
| 分类 | Scripting |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、示例脚本） |
| 模块 | `SequencerScripting` (Runtime), `SequencerScriptingEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-05-09 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/SequencerScripting) | |

## 用途

此插件为 UE5 的序列器（Sequencer）和电影场景（Movie Scenes）提供脚本化接口，主要通过蓝图和 Python 脚本实现自动化工作流。它解决了以下核心问题：

1.  **自动化序列编辑**：允许通过脚本批量创建、修改和管理序列资产，无需手动在编辑器中操作。
2.  **复杂动画与过场制作**：为程序化生成动画和电影级过场动画提供底层控制能力。
3.  **自定义工具开发**：作为构建自定义序列器工具（如动画混合器、录制系统）的基础框架。

## 模块列表

| 模块 | 说明 |
|---|---|
| `SequencerScripting` | 运行时脚本扩展，提供对序列器核心对象（如 Sequence、Track、Section、Channel）的蓝图和 Python 可调用函数。 |
| `SequencerScriptingEditor` | 编辑器专用脚本扩展，提供编辑器上下文中的高级操作，如序列工具集、动画混合器等。 |

## 使用场景

-   你需要批量修改成百上千个序列资产的属性（如播放速度、时间范围）。
-   你在开发一个自定义的动画混合工具，需要在编辑器中动态创建和调整动画序列。
-   你希望用 Python 脚本自动化测试序列播放、录制或导出流程。
-   你需要通过蓝图节点来程序化地创建电影过场动画。

## 蓝图用法

核心功能通过蓝图函数库和编辑器工具类暴露。详细 API 请参见子模块文档。

### 核心节点（示例）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Level Sequence` | 创建一个新的关卡序列资产。 | `USequenceToolsBlueprintLibrary` |
| `Add Spawnable From Class` | 向序列中添加一个可生成绑定。 | `UMovieSceneBindingExtensions` |
| `Set Section Range` | 设置一个片段的时间范围（开始和结束帧）。 | `UMovieSceneSectionExtensions` |
| `Add Key to Channel` | 向指定的通道添加关键帧。 | `UMovieSceneTrackExtensions` |
| `Export Sequence To FBX` | 将序列导出为 FBX 文件。 | `USequencerExportTask` |

### 使用示例（蓝图描述）

1.  **创建序列**：使用 `Create Level Sequence` 节点，并提供资产路径和名称。
2.  **添加对象**：使用 `Add Spawnable From Class` 节点，选择要生成的对象类（如 Actor）。
3.  **添加轨道**：使用 `Add Track` 节点（在绑定扩展中），例如添加一个变换轨道。
4.  **添加关键帧**：使用 `Add Key to Channel` 节点，在变换轨道的对应通道（如位置）上添加关键帧并设置值。

## C++ 用法

C++ 用法通常用于构建更底层的编辑器工具或性能敏感的脚本。

### 头文件引入

```cpp
#include "SequenceUtils.h" // 通用序列工具函数
#include "MovieSceneToolHelpers.h" // 编辑器工具辅助函数
```

### 基本用法

从测试用例中提取的代码，展示如何通过 C++ 创建一个简单的序列。
（来源：`Engine/Plugins/MovieScene/SequencerScripting/Tests/SequencerScriptingTest.cpp`）

```cpp
// 创建一个临时关卡序列
ULevelSequence* Sequence = NewObject<ULevelSequence>();
UMovieScene* MovieScene = Sequence->GetMovieScene();

// 设置序列的时间范围
TRange<FFrameNumber> PlaybackRange = TRange<FFrameNumber>(0, 100);
MovieScene->SetPlaybackRange(PlaybackRange);

// 添加一个变换轨道到指定的绑定
FGuid BindingID = Sequence->MakeSpawnableGuidFromObject(MyActor);
UMovieSceneTrack* TransformTrack = MovieScene->AddTrack<UMovieScene3DTransformTrack>(BindingID);
```

### 进阶用法

使用脚本工具类在编辑器中执行操作。
（来源：`Engine/Plugins/MovieScene/SequencerScriptingEditor/Tests/SequencerScriptingEditorTest.cpp`）

```cpp
// 使用序列工具将当前编辑器选中的 Actor 转换为序列
USequenceToolsBlueprintLibrary::ConvertActorsToSequence(SelectedActors, NewSequencePath);

// 或者录制 Actor 动画到新序列
USequenceRecorderBlueprintLibrary::StartRecording(SelectedActors, RecordingSettings);
```

## Demo 示例

一个可编译的最小示例，展示如何在 C++ 中使用核心 API 创建序列。

```cpp
// MySequenceCreator.h
#pragma once
#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "MySequenceCreator.generated.h"

UCLASS()
class UMySequenceCreator : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

    // 创建一个简单的关卡序列并返回
    UFUNCTION(BlueprintCallable, Category = "MySequence")
    static ULevelSequence* CreateSimpleSequence(FName SequenceName, int32 LengthInFrames);
};

// MySequenceCreator.cpp
#include "MySequenceCreator.h"
#include "LevelSequence.h"
#include "MovieScene.h"

ULevelSequence* UMySequenceCreator::CreateSimpleSequence(FName SequenceName, int32 LengthInFrames)
{
    // 创建序列资产
    ULevelSequence* Sequence = NewObject<ULevelSequence>(GetTransientPackage(), SequenceName);
    UMovieScene* MovieScene = Sequence->GetMovieScene();

    // 设置播放范围
    TRange<FFrameNumber> PlaybackRange = TRange<FFrameNumber>(0, LengthInFrames);
    MovieScene->SetPlaybackRange(PlaybackRange);

    // 这里可以添加更多轨道和关键帧...

    return Sequence;
}
```

## 模块依赖

要在你的模块中使用此插件的功能，需要在你的 `Build.cs` 中添加以下依赖。

| 模块 | 用途 |
|---|---|
| `MovieScene` | 序列器核心数据结构，如 `UMovieScene`, `UMovieSceneTrack` 等。 |
| `LevelSequence` | 关卡序列资产类型 `ULevelSequence`。 |
| `SequencerCore` | 序列器编辑器核心功能。 |
| `MovieSceneTools` | 用于构建自定义编辑器工具的辅助类。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `b209798d` | Anim In Engine: Add bRemoveExcludedCurves option to animation recording so we can remove curves alre | 为动画录制添加了`bRemoveExcludedCurves`选项，允许移除不需要的曲线。 |
| 2026-04-24 | `8b8110b4` | [EDA] Add Sequencer tool wrappers + fix sequencer toolset tests | 新增序列器工具封装函数，并修复了相关测试。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志调用迁移到新的`UE_LOGF`宏。 |
| 2026-04-10 | `77af3950` | [EDA] Add SequencerTools toolset with Anim Mixer split into separate plugin | 添加了序列器工具集，动画混合器功能拆分到了独立插件。 |
| 2026-04-10 | `8bd8f719` | [Backout] - CL52569948 | 回退了之前的某次提交。 |

### 维护评价

-   **活跃维护**：该插件在过去 1 年内有多次实质性更新，主要集中在功能扩展（新工具封装）和代码现代化（日志迁移）上。
-   **实验性状态**：由于 `.uplugin` 中 `IsBetaVersion=true`，它仍处于实验性阶段，API 和功能可能发生变化。
-   **年龄**：创建于 2018 年，已存在约 8 年，属于“老古董”，但核心功能依然重要。
-   **推荐使用**：如果你需要通过脚本控制序列器，它是官方提供的最佳且几乎唯一的选择。鉴于其活跃的维护状态，**推荐在可接受其实验性标签的项目中使用**。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/SequencerScripting)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/SequencerScripting/Tests)