# Audio Gameplay Volume

> Audio Gameplay Volume Plugin

| 属性 | 值 |
|---|---|
| 中文名 | 音频游戏音量 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AudioGameplayVolume` (Runtime), `AudioGameplayVolumeEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-10-27 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AudioGameplayVolume) | |

## 用途
这个插件提供了一种基于空间体积（Volume）的音频效果控制系统。它允许开发者在场景中放置特殊的体积（Actor），当玩家的音频监听器（Listener）进入这些体积时，会自动触发预设的音频效果变化（如应用特定的 Sound Effect Submix Override）。其核心目的是**简化复杂的音频环境交互逻辑**，让音频设计师能够以可视化的体积方式，直观地定义不同游戏区域（如室内、室外、水下、特定房间）的音频特性，而无需编写大量手动检测代码。

## 使用场景
- 你正在开发一个开放世界游戏，希望玩家进入山洞时自动增加回声，走到瀑布边时水声变大 → 使用 `AudioGameplayVolume` 定义山洞和瀑布的音频影响区域。
- 你在制作一个恐怖游戏，需要在特定房间（如地下室）应用压抑、混响大的音效 → 使用该插件为地下室房间放置一个体积，关联一个压抑的音效 Submix。
- 你有多人游戏，需要为某个区域（如竞技场）内的玩家语音添加特殊的通信效果（如低质量无线电效果） → 在该区域放置体积，配置相应的语音效果 Submix。
- 你的音频设计需要根据玩家与特定声源的相对位置动态改变音效（如靠近火炉时声音变暖） → 结合 `AudioGameplay` 插件和本插件的体积，实现基于位置的音频效果切换。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| [`AudioGameplayVolume`](AudioGameplayVolume.md) | Runtime | 核心运行时模块，包含音频体积 Actor、子系统（Subsystem）和优先级系统，负责监听器检测和音频效果应用。 |
| [`AudioGameplayVolumeEditor`](AudioGameplayVolumeEditor.md) | Editor | 编辑器工具模块，为 `AudioGameplayVolume` Actor 提供编辑器支持和自定义细节面板。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 更新日志宏，从 UE_LOG 迁移到 UE_LOGF。 |
| 2026-03-30 | `ffed0384` | [AudioGameplayVolumes] Fix priority system for listener-based mutators (e.g. SubmixOverride) | 修复基于监听器的音频修饰器（如子混音覆盖）的优先级系统。 |
| 2026-01-12 | `0ab2481d` | Fixed dynamic delegate bindings to non-const member functions with const pointers. This is a const- | 修复将动态委托绑定到常量指针的非 const 成员函数时的问题。 |
| 2026-01-05 | `0d4c00d1` | Fix race condition in AudioGameplayVolumeSubsystem | 修复 AudioGameplayVolumeSubsystem 中的竞态条件。 |
| 2025-12-17 | `34b66ba1` | [AGV] Fix early distance culling not working for beam-like primitives: now uses bounding box rather | 修复了对类似光束的图元进行早期距离剔除失效的问题，现在使用包围盒而非... |

### 维护评价
该插件创建于2021年，**处于活跃维护状态**。从近期提交记录（最近5次提交集中在2025年12月至2026年4月）可以看出，开发团队仍在积极修复bug和进行优化，例如修复优先级系统、竞态条件和距离剔除等核心功能问题。考虑到其仍标记为 `IsBetaVersion` (实验性)，表明它可能尚未完全稳定，但持续的更新表明 Epic Games 正在推进其成熟度。**推荐在实验性或需要此功能的新项目中使用**，但需注意其“实验性”状态可能意味着未来API会有变动。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AudioGameplayVolume)
- [关联插件：AudioGameplay](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AudioGameplay)（核心功能依赖此插件）