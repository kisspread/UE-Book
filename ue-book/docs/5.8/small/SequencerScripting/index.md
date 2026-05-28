# Sequencer Scripting

> Python and editor utility scripting extensions for sequencer and movie scenes（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | Sequencer 脚本 |
| 分类 | Scripting |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产/材质模板） |
| 模块 | `SequencerScripting` (Runtime), `SequencerScriptingEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-05-09 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/SequencerScripting) | |

## 用途

该插件为 Unreal Engine 的 **Sequencer**（过场动画和动画序列编辑器）提供了全面的脚本接口，主要通过 **Python** 和 **蓝图（Editor Utility）** 实现。它解决了在 Sequencer 中进行自动化、批处理和自定义扩展的需求。

**核心解决问题**：Sequencer 的标准 UI 操作难以应对大规模、重复性或需要与外部管线集成的工作。例如，需要批量创建动画轨道、程序化生成动画数据、或通过脚本精确控制动画混合与播放时，手动操作效率极低且容易出错。此插件将 Sequencer 的绝大部分功能（如绑定、轨道、区段、曲线、键帧等）暴露给脚本系统，使得自动化成为可能。

## 使用场景

- **动画/过场自动化管线**：你需要为大量角色或场景创建类似的动画序列，或从外部数据源（如动作捕捉数据、表格数据）自动生成和更新 Sequencer 资产。
- **程序化动画生成**：你需要通过算法实时生成或修改动画数据（如镜头运动、相机摇臂、程序化摆动等），并将结果直接应用到 Sequencer 中。
- **自定义 Sequencer 工具与编辑器扩展**：作为技术美术或工具程序员，你希望开发自定义的 Sequencer 工具面板、快捷操作或工作流，集成到编辑器中。
- **批处理与资产处理**：你需要编写脚本来检查、清理或转换大量的 `LevelSequence` 资产，例如修复缺失的绑定、统一轨道参数或导出动画数据。
- **教学与原型开发**：快速通过 Python 脚本实验和演示 Sequencer 的各种高级功能，无需在蓝图中搭建复杂逻辑。

## 蓝图用法

该插件主要通过 `Editor Utility Blueprint` 和暴露给蓝图系统的类来工作。核心蓝图节点来自插件运行时模块（`SequencerScripting`），允许在游戏逻辑或编辑器工具中通过蓝图脚本操作 Sequencer。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Add Track` / `Find Track` | 在指定的 Sequencer 绑定上查找或添加一个新轨道（如变换、动画、事件等）。 | `USequenceLibrary` |
| `Add Section` / `Get Section` | 在轨道上查找或添加一个区段，并获取或设置其起始/结束时间。 | `USequenceLibrary` |
| `Set Range` | 设置一个 Sequencer 区段或整个序列的播放范围。 | `USequenceLibrary` |
| `Get Bindings` / `Add Possessable` | 获取序列中所有对象绑定，或添加一个新的可控制对象（Possessable）。 | `USequenceLibrary` |
| `Evaluate Sequence` | 在特定时间点强制评估序列，常用于预览或获取动画结果。 | `USequenceLibrary` |

### 使用示例（蓝图描述）

在 Editor Utility Blueprint 中，你可以创建一个函数来自动化创建镜头序列：
1.  使用 `Load Asset` 节点加载一个目标 `LevelSequence` 资产。
2.  通过 `Get Master Tracks` 获取序列的主轨道。
3.  使用 `Add Track` 添加一个 `MovieScene3DTransformTrack`（变换轨道）。
4.  在该变换轨道上使用 `Add Section` 添加一个变换区段。
5.  使用 `Set Start Frame` 和 `Set End Frame` 节点设置区段的时长。
6.  最后，使用 `Set Range` 确保序列的播放范围覆盖新添加的内容。

## C++ 用法

对于更复杂或高性能的需求，可以通过 C++ 直接使用插件提供的 API。以下示例基于插件测试用例中的典型用法。

### 头文件引入

```cpp
// 核心 Sequencer 脚本 API
#include "SequenceLibrary.h"

// 包含编辑器工具（如果在编辑器中使用）
#include "SequencerScriptingEditor.h"
```

### 基本用法

**创建和操作一个简单的 Level Sequence（来自测试用例）**
```cpp
// 来源: Engine/Plugins/MovieScene/SequencerScripting/Tests/SequenceTestBase.cpp
void AMyActor::CreateSimpleSequence()
{
    // 1. 创建一个新的 Level Sequence 资产
    ULevelSequence* MySequence = USequenceLibrary::CreateLevelSequence(GetWorld(), TEXT("MyNewSequence"));

    // 2. 获取并操作其 MovieScene
    UMovieScene* MovieScene = MySequence->GetMovieScene();

    // 3. 添加一个包含 Spawnable 的对象绑定
    FGuid BindingGuid = MovieScene->AddSpawnable(TEXT("MySpawnable"), UStaticMesh::StaticClass());

    // 4. 在该绑定上添加一个变换轨道
    UMovieScene3DTransformTrack* TransformTrack = USequenceLibrary::AddTrack<UMovieScene3DTransformTrack>(MySequence, BindingGuid);

    // 5. 在变换轨道上添加一个区段并设置关键帧
    UMovieScene3DTransformSection* Section = Cast<UMovieScene3DTransformSection>(TransformTrack->AddSection());
    Section->SetRange(TRange<FFrameNumber>(0, 100)); // 设置0到100帧的范围
    Section->SetTransformAtFrame(0, FTransform(FVector(0, 0, 0))); // 设置起始关键帧
    Section->SetTransformAtFrame(100, FTransform(FVector(0, 1000, 0))); // 设置结束关键帧
}
```

### 进阶用法

**通过 Python 脚本调用（集成测试中的典型场景）**
该插件大量功能通过 Python 暴露。以下展示了在编辑器中通过 Python 命令控制 Sequencer 的典型流程。
```python
# 来源: Engine/Plugins/MovieScene/SequencerScripting/Tests/PythonIntegrationTest.py
import unreal

# 加载一个已存在的序列
sequence = unreal.load_asset('/Game/MySequences/Cutscene_01')

# 查找其中的角色变换轨道
bindings = unreal.SequenceLibrary.get_bindings(sequence)
for binding in bindings:
    if 'MainCharacter' in binding.get_display_name():
        transform_track = unreal.SequenceLibrary.find_track(unreal.MovieScene3DTransformTrack, sequence, binding.get_id())
        if transform_track:
            # 获取第一个区段
            sections = transform_track.get_sections()
            if sections:
                section = sections[0]
                # 修改区段的时长
                section.set_start_frame_bounded(24)  # 从第24帧开始
                section.set_end_frame_bounded(120)    # 到第120帧结束
                # 在中间添加一个新的关键帧
                section.add_key(72, unreal.Transform(location=unreal.Vector(0, 500, 0)))
```

## 模块依赖

要使用 `SequencerScripting` 插件，你的项目模块需要在 `Build.cs` 文件中添加对以下模块的依赖。已省略 `Core`，`CoreUObject`，`Engine`，`Slate`，`SlateCore`，`InputCore`，`UnrealEd` 等常见依赖。

| 模块 | 用途 |
|---|---|
| `MovieScene` | Sequencer 的核心运行时库，提供序列、轨道、区段等基础类。 |
| `LevelSequence` | 高层 Level Sequence 资产和播放逻辑。 |
| `MovieSceneTools` | Sequencer 的编辑器工具集。 |
| `SequencerScripting` | **本插件的核心运行时模块**，包含用于 Python 和蓝图操作 Sequencer 的 API。 |
| `SequencerScriptingEditor` | **本插件的编辑器扩展模块**，包含编辑器专用的 Sequencer 脚本工具。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `b209798d` | Anim In Engine: Add bRemoveExcludedCurves option to animation recording so we can remove curves alre | 为动画录制添加了排除曲线选项，允许自动移除未包含的曲线数据。 |
| 2026-04-24 | `8b8110b4` | [EDA] Add Sequencer tool wrappers + fix sequencer toolset tests | 新增 Sequencer 工具包装器，并修复了相关工具集的测试用例。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志调用从 UE_LOG 迁移到性能更优的 UE_LOGF。 |
| 2026-04-10 | `77af3950` | [EDA] Add SequencerTools toolset with Anim Mixer split into separate plugin | 添加了 SequencerTools 工具集，并将动画混合器拆分为独立插件。 |
| 2026-04-10 | `8bd8f719` | [Backout] - CL52569948 | 撤销了一次之前的提交。 |

### 维护评价

**综合评价：活跃维护的实验性核心插件。**
- **年龄**：该插件自2018年存在，是 Unreal Engine 动画和过场脚本化体系的关键组成部分。
- **活跃度**：从提交历史看，**最近一次更新在2026年5月**，并且2026年4月有多次实质性功能更新（如新增工具封装、模块拆分）。这表明 Epic 团队仍在积极维护和发展此插件。
- **状态**：`.uplugin` 中 `IsBetaVersion: true`，明确标识为**实验性**。这意味着其 API 可能在未来版本中发生变化，但鉴于其长期存在和持续更新，其核心功能已相当稳定。
- **推荐**：**强烈推荐**在需要深度控制 Sequencer 的自动化管线和编辑器扩展中使用。尽管是实验状态，但它是官方提供的、功能最全面的 Sequencer 脚本方案，是许多复杂工作流的首选。使用时请关注版本更新日志，以适应可能的 API 变动。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/SequencerScripting)
- [官方文档](https://docs.unrealengine.com) （通常，具体的 Sequencer Scripting 文档会整合在引擎的 Sequencer 和 Python 脚本文档中）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/SequencerScripting/Tests)