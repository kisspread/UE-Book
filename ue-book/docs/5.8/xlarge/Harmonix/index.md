# Harmonix

> A package of Harmonix music related audio functionality.

| 属性 | 值 |
|---|---|
| 中文名 | 音乐功能集 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（音乐资产） |
| 模块 | `Harmonix` (Runtime), `HarmonixDsp` (Runtime), `HarmonixDspEditor` (Runtime), `HarmonixDspTests` (Runtime), `HarmonixEditor` (Runtime), `HarmonixMetasound` (Runtime), `HarmonixMetasoundEditor` (Runtime), `HarmonixMetasoundTests` (Runtime), `HarmonixMidi` (Runtime), `HarmonixMidiEditor` (Runtime), `HarmonixMidiTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-17 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix) | |

## 用途

Harmonix 插件是 Epic Games 旗下 Harmonix 工作室开发的一套全面的音乐与音频功能包。其核心目标是为 UE5 项目提供专业级、高性能的音乐交互与处理能力，特别适用于音乐游戏、互动音乐体验以及需要复杂音频合成与处理的应用场景。

插件并非一个单一功能组件，而是一个**模块化工具集**，涵盖了从底层音频信号处理、MIDI 解析、到上层 MetaSound 节点集成、乐器模拟等全套解决方案。它旨在解决传统游戏音频管线（如基于波形的播放）在处理**音乐同步、动态编曲、实时音高/节奏变换**等高级音乐需求时的局限性。

## 使用场景

*   **音乐游戏开发**：需要将游戏玩法（打击、节奏检测）与音乐的精确节拍、小节、乐句同步。
*   **动态与程序化配乐**：根据游戏状态（如战斗强度、探索氛围）实时切换或混合音乐层，实现流畅的过渡。
*   **高级音频合成与设计**：利用 MetaSound 集成，在音频图谱中直接使用音乐相关的节点进行复杂的音效设计。
*   **MIDI 驱动的交互**：解析 MIDI 文件或实时 MIDI 数据，并将其转化为游戏中的事件或可视化效果。
*   **乐器与音色模拟**：创建和管理具有多层采样、动态演奏细节（如轮指、滑音）的虚拟乐器。

## 模块概览

| 模块 | 说明 |
|---|---|
| `Harmonix` | 核心运行时模块，提供插件的基础框架和通用功能。 |
| `HarmonixDsp` | **数字信号处理核心**，包含音高检测、变速、音频分析等 DSP 算法。 |
| `HarmonixMidi` | **MIDI 文件解析与处理**，提供 MIDI 序列、事件、音轨的管理能力。 |
| `HarmonixMetasound` | **MetaSound 集成层**，提供音乐相关的 MetaSound 节点（如节拍器、音乐序列器、音高跟踪器）。 |
| `HarmonixDspEditor` | HarmonixDsp 的编辑器扩展。 |
| `HarmonixMidiEditor` | HarmonixMidi 的编辑器扩展，可能包括资产导入与编辑工具。 |
| `HarmonixMetasoundEditor` | HarmonixMetasound 的编辑器扩展，用于构建音乐相关的 MetaSound 图谱。 |
| `HarmonixEditor` | 插件通用的编辑器功能。 |
| `HarmonixDspTests` | HarmonixDsp 模块的自动化测试。 |
| `HarmonixMidiTests` | HarmonixMidi 模块的自动化测试。 |
| `HarmonixMetasoundTests` | HarmonixMetasound 模块的自动化测试。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `8513e7f4` | [Audio] Fix FFusionVoice::AssignIDs KeyZone ordering + add structural null defense. | 修复 Fusion 声音分配 ID 时的键区排序问题，并增加空指针防御。 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决与 FSoundWaveData API 弃用相关的合并冲突。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 警告的代码。 |
| 2026-05-12 | `0ae74ea8` | [Harmonix] Add user object to the FusionPatch proxy that can be used for tracking activity in association | 为 FusionPatch 代理添加用户对象，用于关联活动跟踪。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正 32 位与 64 位格式化说明符不匹配的问题。 |

### 维护评价

**活跃维护中**。

该插件于 2024 年 1 月正式引入 UE5 引擎（从内部/实验路径迁移），历史不长。从近期 git 提交记录看，维护非常活跃，最近几周的提交集中在**修复 Bug、增强稳定性和改进底层实现**（如 Fusion 音频系统的优化、编译警告清理）。提交信息表明 Epic Games 和 Harmonix 团队仍在积极投入开发，解决实际使用中遇到的问题。

**注意事项**：
*   **实验性状态**：插件被标记为 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`。这意味着其 **API 和功能可能在未来版本中发生重大变更**，不建议在需要长期稳定维护的核心项目中直接使用，除非准备好跟踪更新。
*   作为大型工具集，建议根据项目具体需求，选择性地使用其中的子模块（如仅使用 `HarmonixMidi` 或 `HarmonixMetasound`），而非全部启用。

**推荐度**：对于有明确音乐交互、动态配乐、专业音频处理需求的项目，尤其是在原型开发和探索阶段，强烈推荐关注和试用。务必关注版本更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix)
- [子模块文档](./Modules.md)