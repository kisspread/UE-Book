# Waveform Editor

> Editor tool for waveforms

| 属性 | 值 |
|---|---|
| 中文名 | 波形编辑器 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（波形资产，编辑器工具） |
| 模块 | `WaveformEditor` (Editor), `WaveformEditorWidgets` (Editor), `WaveformTransformations` (Editor), `WaveformTransformationsWidgets` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-08-18 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/WaveformEditor) | |

## 用途

WaveformEditor 是一个功能完整的音频波形编辑器插件。它为音频设计师和开发者提供了一个在编辑器内直接查看、分析、修剪、应用淡入淡出效果以及非破坏性处理音频波形资产的专用工具。其存在是为了解决音频工作流中必须依赖外部软件或复杂蓝图逻辑的痛点，将基本波形操作集成到UE编辑器内，提高迭代效率。

## 使用场景

- 你在为游戏制作环境音效，需要精确修剪循环段的开始和结束点。
- 你需要为对话或音效快速添加淡入（Fade In）和淡出（Fade Out）效果。
- 你想要可视化音频文件的波形，并检查其响度（Loudness）特征。
- 你希望通过非破坏性的方式转换音频资产（例如重采样），同时保留原始文件。

## 模块概览

| 模块 | 功能 |
|---|---|
| `WaveformEditor` | 核心编辑器模块，提供波形资产的数据模型、基本操作逻辑和编辑器主窗口。 |
| `WaveformEditorWidgets` | 提供构成波形编辑器UI的Slate控件，如波形显示、控件条、标尺等。 |
| `WaveformTransformations` | 定义和实现对波形数据的非破坏性变换操作，如修剪、淡入淡出、增益调整等。 |
| `WaveformTransformationsWidgets` | 为 `WaveformTransformations` 中定义的变换提供对应的Slate编辑控件和UI交互。 |

## 蓝图与 C++ 用法概述

本插件主要作为**编辑器工具**使用，其核心功能通过编辑器界面（Slate UI）进行交互。大部分底层逻辑（如波形数据处理、变换应用）封装在 `Runtime` 模块中，为可能的C++扩展提供支持。详细的类与API说明请参考各子模块文档。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `40a5c76a` | [Waveform] Performance regression when dragging trimfade extents | 修复拖拽修剪/淡入淡出区域时的性能下降问题。 |
| 2026-05-14 | `1f67ea84` | [Waveform editor] Remove no-op trimfade transform option | 移除了一个无效的修剪淡入选项，简化UI。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下常量类型截断产生的编译警告。 |
| 2026-04-28 | `d67c3aa3` | [Waveform editor] - Shift + space returns playhead to start, but playback does not start at beginnin | 修复了Shift+空格键将播放头归位后，播放未从头开始的问题。 |
| 2026-04-17 | `93be7d91` | [Waveform] Performance regression when dragging trimfade extents | 修复拖拽修剪/淡入淡出区域时的性能下降问题（回滚或后续修复）。 |

### 维护评价

该插件自2022年创建以来，保持着**非常活跃**的维护状态。从近期提交记录看，团队持续在修复bug、优化性能并改进用户体验。尽管标记为“实验性”（Beta）且默认未启用，但它显然是 Epic Games 正在积极开发和打磨的音频工具链的重要组成部分。**强烈推荐**音频相关工作者关注和使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/WaveformEditor)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/WaveformEditor/Tests)