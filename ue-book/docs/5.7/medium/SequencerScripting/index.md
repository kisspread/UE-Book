# Sequencer Scripting

> Python and editor utility scripting extensions for sequencer and movie scenes

| 属性 | 值 |
|---|---|
| 分类 | Scripting |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图函数库、脚本化键/通道类型） |
| 模块 | `SequencerScripting` (Runtime), `SequencerScriptingEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-05-09 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MovieScene/SequencerScripting) | |

## 用途

Sequencer Scripting 插件将 UE5 Sequencer（电影/过场动画编辑器）的内部数据结构暴露给蓝图和 Python 脚本系统。Sequencer 本身的 C++ API 对蓝图不友好（大量模板、指针、内部类型），这个插件通过一系列 `UBlueprintFunctionLibrary` 扩展类，将 Sequence、Track、Section、Binding、Key/Channel 等核心概念包装成易于脚本调用的形式。

**核心设计模式**：所有函数都是静态函数库方法，使用 `meta=(ScriptMethod)` 标记，使得它们可以作为对象实例方法调用（例如在 Python 中 `sequence.GetTracks()` 而不是 `UMovieSceneSequenceExtensions.GetTracks(sequence)`）。

这个插件解决了什么问题：
- **批量自动化**：通过 Python/蓝图批量创建、修改、导出 Level Sequence
- **程序化动画**：在运行时或编辑器中通过代码创建关键帧、修改轨道
- **FBX 导入导出**：将 Sequencer 动画导出为 FBX 或从 FBX 导入
- **编辑器工具开发**：构建自定义的 Sequencer 编辑器工具和工作流

## 使用场景

- 你需要通过 Python 脚本批量处理数百个 Level Sequence（修改帧率、清理轨道等）
- 你要在编辑器工具中程序化创建过场动画关键帧
- 你需要将 Sequencer 中的骨骼动画导出为 AnimSequence
- 你需要从 FBX 文件导入动画数据到 Sequencer 绑定
- 你要通过蓝图在运行时动态创建和控制 Sequencer 动画
- 你需要操作 Sequencer 的曲线编辑器（选择关键帧、应用滤镜等）

## 蓝图用法

插件的核心 API 通过扩展函数库（Extension Libraries）暴露，所有函数都可以在蓝图中作为目标对象的方法调用。

### Sequence 扩展（UMovieSceneSequenceExtensions）

操作 Level Sequence 的顶层属性。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetMovieScene` | 获取序列的 MovieScene 数据对象 | `UMovieSceneSequenceExtensions` |
| `GetTracks` / `FindTracksByType` / `FindTracksByExactType` | 获取/查找轨道 | `UMovieSceneSequenceExtensions` |
| `AddTrack` / `RemoveTrack` | 添加/移除轨道 | `UMovieSceneSequenceExtensions` |
| `GetDisplayRate` / `SetDisplayRate` | 获取/设置显示帧率 | `UMovieSceneSequenceExtensions` |
| `GetTickResolution` / `SetTickResolution` | 获取/设置时钟分辨率 | `UMovieSceneSequenceExtensions` |
| `GetPlaybackStart` / `SetPlaybackStart` / `GetPlaybackEnd` / `SetPlaybackEnd` | 播放范围帧操作 | `UMovieSceneSequenceExtensions` |
| `GetPlaybackStartSeconds` / `SetPlaybackStartSeconds` 等 | 播放范围秒操作 | `UMovieSceneSequenceExtensions` |
| `GetPlaybackRange` | 获取播放范围（FSequencerScriptingRange） | `UMovieSceneSequenceExtensions` |
| `FindBindingByName` / `FindBindingById` | 按名称/ID 查找绑定 | `UMovieSceneSequenceExtensions` |
| `GetBindings` / `GetSpawnables` / `GetPossessables` | 获取所有绑定/可生成/可拥有对象 | `UMovieSceneSequenceExtensions` |
| `AddPossessable` | 添加可拥有对象绑定 | `UMovieSceneSequenceExtensions` |
| `LocateBoundObjects` | 查找绑定对象实例 | `UMovieSceneSequenceExtensions` |
| `GetBindingID` / `GetPortableBindingID` / `ResolveBindingID` | 绑定 ID 操作 | `UMovieSceneSequenceExtensions` |
| `GetRootFoldersInSequence` / `AddRootFolderToSequence` / `RemoveRootFolderFromSequence` | 文件夹管理 | `UMovieSceneSequenceExtensions` |
| `GetMarkedFrames` / `AddMarkedFrame` / `DeleteMarkedFrame` 等 | 标记帧操作 | `UMovieSceneSequenceExtensions` |
| `SetReadOnly` / `IsReadOnly` | 只读保护 | `UMovieSceneSequenceExtensions` |
| `SetEvaluationType` / `SetClockSource` | 评估类型和时钟源 | `UMovieSceneSequenceExtensions` |
| `SetViewRangeStart` / `SetWorkRangeStart` 等 | 视图/工作范围（仅编辑器） | `UMovieSceneSequenceExtensions` |

### Binding 扩展（UMovieSceneBindingExtensions）

操作 Sequencer 中的对象绑定。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsValid` | 检查绑定是否有效 | `UMovieSceneBindingExtensions` |
| `GetId` / `GetDisplayName` / `GetName` | 获取绑定标识 | `UMovieSceneBindingExtensions` |
| `SetDisplayName` / `SetName` | 设置绑定名称 | `UMovieSceneBindingExtensions` |
| `GetTracks` / `FindTracksByType` / `AddTrack` / `RemoveTrack` | 绑定内的轨道操作 | `UMovieSceneBindingExtensions` |
| `GetChildPossessables` / `GetParent` / `SetParent` | 父子绑定层级 | `UMovieSceneBindingExtensions` |
| `GetObjectTemplate` / `GetPossessedObjectClass` | 获取绑定对象信息 | `UMovieSceneBindingExtensions` |
| `MoveBindingContents` | 移动绑定内容到另一个绑定 | `UMovieSceneBindingExtensions` |
| `Remove` | 删除绑定 | `UMovieSceneBindingExtensions` |

### Track 扩展（UMovieSceneTrackExtensions）

操作 Sequencer 轨道。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetDisplayName` / `SetDisplayName` | 轨道显示名称 | `UMovieSceneTrackExtensions` |
| `GetSections` / `AddSection` / `RemoveSection` | Section 管理 | `UMovieSceneTrackExtensions` |
| `GetSortingOrder` / `SetSortingOrder` | 排序顺序 | `UMovieSceneTrackExtensions` |
| `GetColorTint` / `SetColorTint` | 颜色标记 | `UMovieSceneTrackExtensions` |
| `GetSectionToKey` / `SetSectionToKey` | 设置接收关键帧的 Section | `UMovieSceneTrackExtensions` |

### Section 扩展（UMovieSceneSectionExtensions）

操作 Sequencer Section（轨道中的时间片段）。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `HasStartFrame` / `HasEndFrame` | 检查是否有边界 | `UMovieSceneSectionExtensions` |
| `GetStartFrame` / `GetEndFrame` | 获取起止帧 | `UMovieSceneSectionExtensions` |
| `SetRange` / `SetRangeSeconds` | 设置时间范围 | `UMovieSceneSectionExtensions` |
| `SetStartFrame` / `SetEndFrame` / `SetStartFrameSeconds` / `SetEndFrameSeconds` | 设置起止帧 | `UMovieSceneSectionExtensions` |
| `SetStartFrameBounded` / `SetEndFrameBounded` | 设置是否有界 | `UMovieSceneSectionExtensions` |
| `GetAllChannels` / `GetChannelsByType` / `GetChannel` | 获取 Channel（键通道） | `UMovieSceneSectionExtensions` |
| `GetAutoSizeHasStartFrame` / `GetAutoSizeStartFrame` 等 | AutoSize 范围 | `UMovieSceneSectionExtensions` |
| `GetParentSequenceFrame` | 子序列帧转换 | `UMovieSceneSectionExtensions` |

### Property Track 扩展（UMovieScenePropertyTrackExtensions）

操作属性轨道（绑定了具体属性的轨道）。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetPropertyName` / `GetPropertyPath` | 获取属性名/路径 | `UMovieScenePropertyTrackExtensions` |
| `SetPropertyNameAndPath` | 设置属性名和路径 | `UMovieScenePropertyTrackExtensions` |
| `GetUniqueTrackName` | 获取唯一轨道名 | `UMovieScenePropertyTrackExtensions` |
| `SetObjectPropertyClass` / `GetObjectPropertyClass` | 对象属性类 | `UMovieScenePropertyTrackExtensions` |
| `SetByteTrackEnum` / `GetByteTrackEnum` | 字节轨道枚举 | `UMovieScenePropertyTrackExtensions` |

### 其他 Track 扩展

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetNumChannelsUsed` / `GetNumChannelsUsed` | 向量轨道通道数（Float/Double） | `UMovieSceneFloatVectorTrackExtensions` / `UMovieSceneDoubleVectorTrackExtensions` |
| `SetMaterialInfo` / `GetMaterialInfo` | 材质轨道材质信息 | `UMovieSceneMaterialTrackExtensions` / `UMovieScenePrimitiveMaterialTrackExtensions` |
| `AddEventRepeaterSection` / `AddEventTriggerSection` | 事件轨道 Section | `UMovieSceneEventTrackExtensions` |

### TimeWarp 扩展（UMovieSceneTimeWarpExtensions）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Conv_TimeWarpVariantToPlayRate` / `Conv_PlayRateToTimeWarpVariant` | TimeWarp 与播放速率互转 | `UMovieSceneTimeWarpExtensions` |
| `ToFixedPlayRate` / `SetFixedPlayRate` | 固定播放速率 | `UMovieSceneTimeWarpExtensions` |
| `MakeTimeWarp` / `BreakTimeWarp` | 创建/拆解 TimeWarp | `UMovieSceneTimeWarpExtensions` |

### Range 扩展（USequencerScriptingRangeExtensions）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `HasStart` / `HasEnd` | 检查范围边界 | `USequencerScriptingRangeExtensions` |
| `RemoveStart` / `RemoveEnd` | 移除边界（设为无限） | `USequencerScriptingRangeExtensions` |
| `GetStartFrame` / `GetEndFrame` / `GetStartSeconds` / `GetEndSeconds` | 获取范围值 | `USequencerScriptingRangeExtensions` |
| `SetStartFrame` / `SetEndFrame` / `SetStartSeconds` / `SetEndSeconds` | 设置范围值 | `USequencerScriptingRangeExtensions` |

### Folder 扩展（UMovieSceneFolderExtensions）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetFolderName` / `SetFolderName` | 文件夹名称 | `UMovieSceneFolderExtensions` |
| `GetFolderColor` / `SetFolderColor` | 文件夹颜色 | `UMovieSceneFolderExtensions` |
| `GetChildFolders` / `AddChildFolder` / `RemoveChildFolder` | 子文件夹管理 | `UMovieSceneFolderExtensions` |
| `GetChildTracks` / `AddChildTrack` / `RemoveChildTrack` | 文件夹内轨道 | `UMovieSceneFolderExtensions` |
| `GetChildObjectBindings` / `AddChildObjectBinding` / `RemoveChildObjectBinding` | 文件夹内绑定 | `UMovieSceneFolderExtensions` |

### 编辑器工具（USequencerToolsFunctionLibrary）

仅在编辑器可用，提供高级操作。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ExportLevelSequenceFBX` | 导出序列到 FBX | `USequencerToolsFunctionLibrary` |
| `ImportLevelSequenceFBX` | 从 FBX 导入到序列 | `USequencerToolsFunctionLibrary` |
| `ExportAnimSequence` | 导出为 AnimSequence | `USequencerToolsFunctionLibrary` |
| `LinkAnimSequence` / `ClearLinkedAnimSequences` | AnimSequence 链接管理 | `USequencerToolsFunctionLibrary` |
| `CreateEvent` / `CreateQuickBinding` | 事件和快速绑定 | `USequencerToolsFunctionLibrary` |
| `ImportFBXToControlRig` / `ExportFBXFromControlRig` | ControlRig FBX 操作 | `USequencerToolsFunctionLibrary` |

### 曲线编辑器（USequencerCurveEditorObject）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `OpenCurveEditor` / `CloseCurveEditor` / `IsCurveEditorOpen` | 曲线编辑器开关 | `USequencerCurveEditorObject` |
| `GetChannelsWithSelectedKeys` / `GetSelectedKeys` / `SelectKeys` | 关键帧选择 | `USequencerCurveEditorObject` |
| `ApplyFilter` | 应用曲线滤镜 | `USequencerCurveEditorObject` |
| `ShowCurve` / `IsCurveShown` | 曲线显示控制 | `USequencerCurveEditorObject` |
| `SetCustomColorForChannel` / `GetCustomColorForChannel` | 自定义曲线颜色 | `USequencerCurveEditorObject` |

### 使用示例（蓝图描述）

**创建一个 Level Sequence 并添加变换轨道**：

1. 使用 `Create Level Sequence` 资产节点创建序列
2. 拖拽序列引用，调用 `Add Track` 节点，Track Type 选择 `MovieScene3DTransformTrack`
3. 在返回的 Track 上调用 `Add Section` 创建 Section
4. 在 Section 上调用 `Set Range` 设置起止帧

**通过 Python 批量修改序列帧率**：

在 Python 编辑器工具中，使用 `unreal.LevelSequenceEditorBlueprintLibrary` 打开序列后，通过 `UMovieSceneSequenceExtensions` 的 ScriptMethod 形式调用 `SetDisplayRate` 修改帧率。

## C++ 用法

### 头文件引入

```cpp
#include "ExtensionLibraries/MovieSceneSequenceExtensions.h"
#include "ExtensionLibraries/MovieSceneBindingExtensions.h"
#include "ExtensionLibraries/MovieSceneTrackExtensions.h"
#include "ExtensionLibraries/MovieSceneSectionExtensions.h"
```

### 基本用法

基于源码 API 设计，展示典型的 Sequencer 脚本操作：

```cpp
// 获取 Level Sequence 的 MovieScene
UMovieScene* MovieScene = UMovieSceneSequenceExtensions::GetMovieScene(MyLevelSequence);

// 获取所有轨道
TArray<UMovieSceneTrack*> AllTracks = UMovieSceneSequenceExtensions::GetTracks(MyLevelSequence);

// 按类型查找轨道
TArray<UMovieSceneTrack*> TransformTracks = UMovieSceneSequenceExtensions::FindTracksByType(
    MyLevelSequence, UMovieScene3DTransformTrack::StaticClass());

// 获取播放范围
FSequencerScriptingRange PlaybackRange = UMovieSceneSequenceExtensions::GetPlaybackRange(MyLevelSequence);
int32 StartFrame = UMovieSceneSequenceExtensions::GetPlaybackStart(MyLevelSequence);
int32 EndFrame = UMovieSceneSequenceExtensions::GetPlaybackEnd(MyLevelSequence);

// 设置显示帧率为 30fps
UMovieSceneSequenceExtensions::SetDisplayRate(MyLevelSequence, FFrameRate(30, 1));
```

### 进阶用法

操作绑定和轨道层级：

```cpp
// 获取所有绑定
TArray<FMovieSceneBindingProxy> Bindings = UMovieSceneSequenceExtensions::GetBindings(MyLevelSequence);

// 按名称查找绑定
FMovieSceneBindingProxy CameraBinding = UMovieSceneSequenceExtensions::FindBindingByName(
    MyLevelSequence, TEXT("CineCameraActor_0"));

// 获取绑定内的轨道
TArray<UMovieSceneTrack*> BindingTracks = UMovieSceneBindingExtensions::GetTracks(CameraBinding);

// 添加新轨道到绑定
UMovieSceneTrack* NewTrack = UMovieSceneBindingExtensions::AddTrack(
    CameraBinding, UMovieSceneFloatTrack::StaticClass());

// 创建 Section 并设置范围
UMovieSceneSection* Section = UMovieSceneTrackExtensions::AddSection(NewTrack);
UMovieSceneSectionExtensions::SetRange(Section, 0, 150);  // 帧 0-150

// 获取 Channel 并添加关键帧
TArray<UMovieSceneScriptingChannel*> Channels = UMovieSceneSectionExtensions::GetAllChannels(Section);
```

操作标记帧（Marked Frames）：

```cpp
// 添加标记帧
FMovieSceneMarkedFrame MarkedFrame;
MarkedFrame.Label = TEXT("Important");
MarkedFrame.FrameNumber = FFrameNumber(100);
int32 Index = UMovieSceneSequenceExtensions::AddMarkedFrameToSequence(
    MyLevelSequence, MarkedFrame, EMovieSceneTimeUnit::DisplayRate);

// 查找标记帧
int32 FoundIndex = UMovieSceneSequenceExtensions::FindMarkedFrameByLabel(
    MyLevelSequence, TEXT("Important"));
```

## Demo 示例

### 最小可编译示例：程序化创建序列

**Build.cs 依赖**：
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "MovieScene",
    "LevelSequence",
    "SequencerScripting"
});
```

**MySequenceCreator.h**：
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "MySequenceCreator.generated.h"

class ULevelSequence;

UCLASS()
class UMySequenceCreator : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable, Category = "MyTools")
    static ULevelSequence* CreateSimpleSequence(const FString& AssetPath, int32 NumFrames, float FrameRate);
};
```

**MySequenceCreator.cpp**：
```cpp
#include "MySequenceCreator.h"
#include "LevelSequence.h"
#include "MovieScene.h"
#include "MovieSceneTrack.h"
#include "ExtensionLibraries/MovieSceneSequenceExtensions.h"
#include "ExtensionLibraries/MovieSceneTrackExtensions.h"
#include "ExtensionLibraries/MovieSceneSectionExtensions.h"

ULevelSequence* UMySequenceCreator::CreateSimpleSequence(const FString& AssetPath, int32 NumFrames, float FrameRate)
{
    // 创建 Level Sequence 资产
    ULevelSequence* Sequence = NewObject<ULevelSequence>(GetTransientPackage(), FName(*AssetPath));
    if (!Sequence) return nullptr;

    // 设置帧率
    UMovieSceneSequenceExtensions::SetDisplayRate(Sequence, FFrameRate(FrameRate, 1));

    // 设置播放范围
    UMovieSceneSequenceExtensions::SetPlaybackStart(Sequence, 0);
    UMovieSceneSequenceExtensions::SetPlaybackEnd(Sequence, NumFrames);

    // 获取 MovieScene 并添加一个空轨道
    UMovieSceneTrack* Track = UMovieSceneSequenceExtensions::AddTrack(
        Sequence, UMovieSceneTrack::StaticClass());

    if (Track)
    {
        // 添加 Section
        UMovieSceneSection* Section = UMovieSceneTrackExtensions::AddSection(Track);
        if (Section)
        {
            UMovieSceneSectionExtensions::SetRange(Section, 0, NumFrames);
        }
    }

    return Sequence;
}
```

## 模块依赖

使用 SequencerScripting 模块时，你的 Build.cs 需要引用以下模块：

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心库 |
| `MovieScene` | Sequencer 核心数据结构（UMovieScene、Section、Channel 等） |
| `MovieSceneTracks` | 各种轨道类型（Transform、Float、Event 等） |
| `LevelSequence` | Level Sequence 资产类型 |
| `TimeManagement` | 时间管理和帧率转换 |
| `SequencerScripting` | 本插件的 Runtime 模块（蓝图函数库） |

如果需要编辑器功能（FBX 导入导出、曲线编辑器等），还需要依赖 `SequencerScriptingEditor` 模块。

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-10-01 | `b4449c583d` | Anim In Engine: Fix broken linked anim sequences | 修复 AnimSequence 和 LevelSequence 之间链接断裂的 bug |
| 2025-09-30 | `4b27f5e48b` | Add FAllSpawnableRestoreState that disables and restores all spawn tracks | 新增 spawn track 状态管理，支持在序列层级中禁用/恢复所有 spawn 轨道 |
| 2025-09-23 | `958a03a3ad` | Sequencer: UE_API all blueprint exposed functions | 将所有蓝图暴露函数标记 UE_API，确保 DLL 导出符号正确 |

### 维护评价

- **创建时间**：2018 年 5 月，已有约 8 年历史
- **最近更新**：2025 年 10 月仍有活跃更新，属于**活跃维护**状态
- **标记为 Beta**：`.uplugin` 中 `IsBetaVersion: true`，说明 Epic 仍认为此插件尚未完全稳定，API 可能发生变化
- **大量废弃标记**：5.3-5.5 期间多个函数被标记为 `UE_DEPRECATED`（如 `AddSpawnableFromInstance`、`RenderMovie`、旧版 MarkedFrame 函数等），说明 API 在持续演进
- **Python 依赖**：插件依赖 `PythonScriptPlugin`，适合 Python 自动化工作流
- **推荐使用**：✅ 推荐。这是 Sequencer 脚本化的官方方案，虽然标记为 Beta 但已是事实标准。使用时注意关注版本更新中的废弃标记。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MovieScene/SequencerScripting)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- [Sequencer 官方文档](https://docs.unrealengine.com/en-US/AnimatingObjects/Sequencer/)
