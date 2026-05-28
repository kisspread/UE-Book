# Replay Tracks

> Sequence tracks for playing recorded gameplay（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 回放轨道 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ReplayTracks` (Runtime), `ReplayTracksEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-04-08 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/ReplayTracks) | |

## 用途

Replay Tracks 插件扩展了 UE5 的 Sequencer（定序器）系统，专门用于在 Sequencer 时间线上播放和控制预先录制好的游戏回放（Replay）内容。它解决的核心问题是：游戏设计师或电影制作人需要像编辑电影镜头一样，精确地剪辑、编排和混合游戏内的回放片段与过场动画，以创建完整的演示视频、游戏预告片或教程。

该插件将游戏回放（一种动态录制的数据）封装成 Sequencer 可以理解和操控的“轨道”和“区段”，从而让回放内容可以与其他 Sequencer 动画、镜头、音频等轨道无缝集成。

## 使用场景

- **游戏预告片制作**：你需要将游戏中的高光时刻（通过 Replay 系统录制）按照剧本顺序编排，并加入慢动作、多角度切换和电影化转场。
- **游戏内过场混合**：你希望在一个长的过场动画序列中，穿插一小段实际的游戏玩法回放，以展示角色的特定操作。
- **教程与演示**：在 Sequencer 中精确控制教学演示片段的播放节奏（快进、倒放、暂停），并与UI注解动画同步。

## 蓝图用法

该插件主要为 Sequencer 编辑器提供资产和功能，其运行时接口通常由 Sequencer 框架内部调用，直接暴露给蓝图的函数节点较少。核心用法体现在 Sequencer 编辑器界面中。

### 核心节点（Sequencer 中可用）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Replay Track` | 在 Sequencer 轨道列表中添加一个用于容纳回放区段的专用轨道。 | `UReplayTrack` |
| `Replay Section` | 表示回放数据的一个区段。可以设置其持续时间、播放速度、开始/结束时间等属性，并像剪辑视频一样在时间线上移动和分割。 | `UReplaySection` |

### 使用示例（Sequencer 编辑器描述）

1.  **创建轨道**：在 Sequencer 的轨道区域，右键点击 -> “添加新轨道” -> 选择 “Replay Track”。
2.  **添加回放**：确保你已经通过 UE 的 Replay System 录制并保存了游戏回放文件（.replay）。在 “Replay Track” 的时间线上右键，选择 “Add Replay Section”，然后从资产选择器中选择一个 `.replay` 文件。
3.  **编辑与编排**：
    - **调整时长**：拖拽 “Replay Section” 的左右边缘来调整它在最终时间线中的持续时间（可以比原回放长或短）。
    - **设置速度**：选中区段，在细节面板中设置 “Play Rate” 属性（例如 0.5 为慢动作，2.0 为快进）。
    - **混合**：将多个 “Replay Section” 拖拽到同一个 “Replay Track” 或不同 “Replay Track” 上，实现回放内容的序列或平行播放。
    - **同步**：像对齐其他 Sequencer 轨道一样，将回放区段与镜头、动画、音频轨道的关键帧对齐。

## C++ 用法

该插件的 C++ 层主要是为 Sequencer 框架实现相关的接口，供 Sequencer UI 和评估器调用。直接使用 C++ 代码创建和操控这些轨道的情况较少，通常是在扩展 Sequencer 功能时参考。

### 头文件引入

```cpp
// 用于使用核心回放轨道/区段类型
#include "ReplayTrack.h"
#include "ReplaySection.h"

// 用于在编辑器模块中扩展或检查回放轨道功能
#include "IReplayTracksEditorModule.h"
```

### 基本用法

以下代码展示了如何通过 C++ 以编程方式检查或操作一个已经存在的回放区段（需要在 Sequencer 编辑器上下文中）。

```cpp
// 假设你已经通过 Sequencer API 获取了 UMovieSceneSequence* Sequence
// 以及一个 UMovieSceneTrack* Track

// 检查轨道是否是回放轨道
if (UReplayTrack* ReplayTrack = Cast<UReplayTrack>(Track))
{
    // 遍历并查找特定回放区段
    for (UMovieSceneSection* Section : ReplayTrack->GetAllSections())
    {
        if (UReplaySection* ReplaySection = Cast<UReplaySection>(Section))
        {
            // 读取或设置区段属性（示例：调整播放速度）
            FReplaySectionParams Params = ReplaySection->GetReplaySectionParams();
            Params.PlayRate = 1.5f; // 设置1.5倍速
            ReplaySection->SetReplaySectionParams(Params);
            
            // 注意：直接修改后，需要通知 Sequencer 数据已变更
            // ReplaySection->Modify(); // 标记为已修改
            break;
        }
    }
}
```
*代码示意，需在合适的 Sequencer 编辑器操作上下文中执行。*

## Demo 示例

一个完整的、可编译的最小示例可能不适用，因为该插件主要是为 Sequencer 编辑器提供 UI 和工作流，其运行时行为依赖于 Sequencer 的整体评估系统。一个概念性的“使用示例”即上文 **“使用示例（Sequencer 编辑器描述）”** 章节所描述的步骤。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MovieScene` | Sequencer 核心数据模型和轨道基础。 |
| `MovieSceneTracks` | Sequencer 内置的标准轨道类型（如动画、镜头轨道），回放轨道与其并列。 |
| `Sequencer` (Editor) | Sequencer 编辑器 UI 框架，`ReplayTracksEditor` 模块用于在此框架中注册和显示回放轨道编辑控件。 |
| `ReplaySystem` / `DemoNetDriver` | 底层提供录制和回放游戏状态能力的模块，本插件是其在 Sequencer 中的消费者。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-06-05 | `28030cd1` | Sequencer: remove uses of IMovieScenePlayer | 清理过时接口，跟随 Sequencer 框架重构。 |
| 2024-02-21 | `33c4fac2` | [Backout] - CL31676435 and 31676432... | 回退了之前的修改，属于框架调整。 |
| 2024-02-21 | `22575fdd` | [Backout] - CL31652683 | 回退了之前的修改，属于框架调整。 |
| 2024-02-20 | `4aa3f9f3` | Sequencer: linker/runner refactor | Sequencer 链接器/执行器重构，本插件需适配。 |
| 2023-11-03 | `bb5b082f` | Sequencer: move evaluation information onto FSharedPlaybackState | Sequencer 评估信息迁移，本插件需适配底层变化。 |

### 维护评价

- **维护不活跃**：该插件自 2021 年创建以来，最近的更新（2024年）均为跟随 Sequencer 核心框架的重构而进行的适配性修改（如回退、清理过时接口），没有观察到功能性增强或新特性添加。
- **实验性状态**：插件自创建之初即标记为 `IsBetaVersion=true`，并且 `EnabledByDefault=false`，直到最近（2024年）的提交仍处于此状态，表明它尚未被 Epic 官方认定为稳定可用的功能。
- **功能定位**：它是一个非常垂直、面向特定工作流（Sequencer + Replay）的工具型插件。
- **使用建议**：可以尝试用于原型验证或个人项目中，了解 Sequencer 集成回放的可能性。但不建议用于关键或需要长期维护的生产项目，因为它功能可能不完善，且未来有被调整或移除的风险。请密切关注官方更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/ReplayTracks)
- [官方文档]()（无）
- [测试用例]()（插件目录内未包含独立测试）