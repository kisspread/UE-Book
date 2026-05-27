# Sequencer Scripting

> Python and editor utility scripting extensions for sequencer and movie scenes

| 属性 | 值 |
|---|---|
| 中文名 | Sequencer 脚本化 |
| 分类 | Scripting |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `SequencerScripting` (Runtime), `SequencerScriptingEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-05-09 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/SequencerScripting) | |

## 用途

SequencerScripting 是 Unreal Engine 的 Sequencer（序列器）系统与 Python/蓝图脚本之间的桥梁。它将 Sequencer 的核心概念——LevelSequence、Bindings（对象绑定）、Tracks（轨道）、Sections（片段）、Channels（通道）等——全部通过 `BlueprintCallable` 和 Python 绑定暴露出来，使开发者能够以编程方式创建、修改和查询 Sequencer 数据。

这个插件存在的根本原因是：**Sequencer 编辑器的 UI 操作无法满足批量处理和自动化需求**。当你需要通过脚本批量创建过场动画、从外部数据源导入动画关键帧、自动化序列录制流程，或在运行时通过蓝图控制 Sequencer 时，就必须依赖此插件提供的脚本化 API。

⚠️ **注意**：该插件标记为 Beta（`IsBetaVersion: true`），且默认未启用（`Installed: false`）。使用前需要在项目设置中手动启用。

## 模块概览

| 模块 | 类型 | 文档 | 说明 |
|---|---|---|---|
| `SequencerScripting` | Runtime | [SequencerScripting.md](./SequencerScripting.md) | 运行时 Sequencer 脚本化 API，包括 LevelSequence 操作、Binding/Track/Section/Channel 管理 |
| `SequencerScriptingEditor` | Runtime | [SequencerScriptingEditor.md](./SequencerScriptingEditor.md) | 编辑器专用脚本化工具，包括序列编辑器操作、工具集包装器 |

## 使用场景

- **自动化过场动画制作** → 你有一批角色动画需要组装成过场序列 → 用 Python 脚本批量创建 LevelSequence，添加 Binding、Track 和 Section
- **外部数据驱动动画** → 动捕数据或外部工具输出关键帧数据 → 用脚本化 API 将关键帧批量写入 Sequencer Channel
- **批量导出/修改序列** → 需要对大量已有序列执行相同的属性修改 → 用 Python 遍历并批量调整 Section 范围、混合模式等
- **运行时 Sequencer 控制** → 游戏中需要通过蓝图动态操控序列播放 → 用蓝图节点控制 LevelSequence 的播放、暂停、跳转
- **序列录制自动化** → 需要程序化触发 Sequence Recorder → 通过脚本接口控制录制流程和录制组

## 蓝图用法

SequencerScripting 提供了大量 `BlueprintCallable` 函数，按功能可分为以下几组：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateLevelSequence` | 创建新的 LevelSequence 资产 | `ULevelSequenceEditorBlueprintLibrary` |
| `GetBoundObjects` | 获取绑定到指定 Binding 的运行时对象 | `ULevelSequencePlayer` |
| `AddTrack` | 向指定 Binding 添加新轨道 | `UMovieSceneBindingExtensions` |
| `AddSection` | 向轨道添加新片段 | `UMovieSceneTrackExtensions` |
| `SetRange` | 设置 Section 的时间范围 | `UMovieSceneSectionExtensions` |
| `GetChannels` | 获取 Section 下的所有通道 | `UMovieSceneSectionExtensions` |
| `SetDefault` | 设置通道的默认值 | `UMovieSceneChannelExtensions` |
| `GetKeys` / `AddKey` | 读取/添加通道关键帧 | `UMovieSceneChannelExtensions` |

### 使用示例（蓝图描述）

**创建序列并添加动画轨道：**
1. 使用 `Create Level Sequence` 节点创建新序列资产
2. 调用 `Add Possessable` 将场景中的 Actor 绑定到序列
3. 使用 `Add Track` 为该 Binding 添加动画轨道（Animation Track）
4. 调用 `Add Section` 在轨道上创建新的动画片段
5. 设置 Section 的 `Start Frame` 和 `End Frame` 定义时间范围
6. 为 Section 指定动画资产

**批量修改关键帧：**
1. 使用 `Get Sections` 获取轨道上的所有片段
2. 对每个 Section 调用 `Get Channels` 获取通道列表
3. 使用 `Get Keys` 读取当前关键帧
4. 遍历关键帧，使用 `Set Key Value` 修改值
5. 或使用 `Add Key` 添加新的关键帧

## C++ 用法

### 头文件引入

```cpp
#include "LevelSequence.h"
#include "LevelSequencePlayer.h"
#include "MovieScene.h"
#include "MovieSceneBinding.h"
#include "MovieSceneTrack.h"
#include "MovieSceneSection.h"
#include "MovieSceneChannel.h"
```

### 基本用法

```cpp
// 获取当前 LevelSequence
ULevelSequence* Sequence = GetMyLevelSequence();
UMovieScene* MovieScene = Sequence->GetMovieScene();

// 遍历所有绑定（Bindings）
for (const FMovieSceneBinding& Binding : MovieScene->GetBindings())
{
    FGuid ObjectBinding = Binding.GetObjectGuid();
    
    // 获取绑定上的所有轨道
    TArray<UMovieSceneTrack*> Tracks = Binding.GetTracks();
    for (UMovieSceneTrack* Track : Tracks)
    {
        // 获取轨道上的所有片段
        TArray<UMovieSceneSection*> Sections = Track->GetAllSections();
        for (UMovieSceneSection* Section : Sections)
        {
            TRange<FFrameNumber> Range = Section->GetRange();
            // 处理片段...
        }
    }
}
```

### 进阶用法

```cpp
// 通过脚本化 API 操作通道关键帧
UMovieSceneChannel* Channel = GetChannelFromSection(Section);
if (Channel)
{
    // 读取关键帧数据
    FMovieSceneChannelProxy& Proxy = Section->GetChannelProxy();
    
    // 添加新关键帧
    FFrameNumber KeyTime(100); // 第100帧
    // 使用特定通道类型的 AddKey 方法
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MovieScene` | Sequencer 核心类型定义（Binding、Track、Section、Channel） |
| `LevelSequence` | LevelSequence 资产类型 |
| `LevelSequenceEditor` | 编辑器内序列操作 |
| `SequencerCore` | Sequencer 核心工具集 |
| `PythonScriptPlugin` | Python 脚本绑定支持 |
| `ScriptPlugin` | 脚本系统基础设施 |
| `SequencerTools` | Sequencer 工具集（Anim Mixer 等） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `b209798d` | Anim In Engine: Add bRemoveExcludedCurves option to animation recording so we can remove curves alre | 动画录制新增排除曲线移除选项 |
| 2026-04-24 | `8b8110b4` | [EDA] Add Sequencer tool wrappers + fix sequencer toolset tests | 添加 Sequencer 工具包装器并修复工具集测试 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志系统迁移到 UE_LOGF 宏 |
| 2026-04-10 | `77af3950` | [EDA] Add SequencerTools toolset with Anim Mixer split into separate plugin | SequencerTools 工具集加入，Anim Mixer 拆分为独立插件 |
| 2026-04-10 | `8bd8f719` | [Backout] - CL52569948 | 回退变更 CL52569948 |

### 维护评价

- **创建时间**：2018 年 5 月，已有约 8 年历史
- **维护状态**：**活跃维护中**。2026 年 5 月仍有功能性更新（动画录制选项、工具集包装器）
- **Beta 状态**：尽管标记为 `IsBetaVersion: true`，但该插件已被广泛使用，Beta 标签可能只是历史遗留
- **默认未启用**：`Installed: false`，需要手动在项目设置中启用
- **注意事项**：支持的程序列表仅包含 `LiveLinkHub`，标准游戏项目使用时需确认兼容性
- **推荐程度**：✅ **强烈推荐**用于需要脚本化操作 Sequencer 的场景。API 覆盖全面，持续维护，是 Sequencer 自动化的唯一官方方案

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/SequencerScripting)
- [SequencerScripting 模块文档](./SequencerScripting.md)
- [SequencerScriptingEditor 模块文档](./SequencerScriptingEditor.md)