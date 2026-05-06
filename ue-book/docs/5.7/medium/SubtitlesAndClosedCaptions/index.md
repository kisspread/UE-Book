# Subtitles and Closed Captions

> Standalone plugin for displaying Subtitles and Closed Captions

| 属性 | 值 |
|---|---|
| 中文名 | 字幕与隐藏式字幕 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Widget蓝图、字幕资产数据、测试资源） |
| 模块 | `SubtitlesAndClosedCaptions` (Runtime), `SubtitlesAndClosedCaptionsEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-25 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SubtitlesAndClosedCaptions) | |

## 总体用途

SubtitlesAndClosedCaptions 是一个独立插件，为游戏提供**字幕与隐藏式字幕显示系统**。它解耦了字幕显示逻辑与默认的 `DialogueWave` 播放机制，允许开发者通过蓝图或 C++ 直接管理字幕队列、热切换 Widget，并支持基于 `USubtitleAssetUserData` 的批量字幕队列。

该插件解决了以下问题：
- 默认字幕系统与音频播放器强绑定，难以独立控制。
- 缺乏插件级的可替换 UI 组件。
- 缺少对隐藏式字幕（Closed Captions）的专门支持。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| [SubtitlesAndClosedCaptions](SubtitlesAndClosedCaptions.md) | Runtime | 核心运行时模块，提供字幕子系统、字幕队列、蓝图可调用 API |
| [SubtitlesAndClosedCaptionsEditor](SubtitlesAndClosedCaptionsEditor.md) | UncookedOnly | 编辑器模块，提供字幕相关自定义资产编辑、蓝图节点注册、Cvar 控制 |

## 使用场景

- **独立字幕功能**：你需要在游戏中展示字幕或隐藏式字幕，但不希望受限于默认的 UAudioComponent 或 DialogueWave 的播放生命周期。
- **热切换字幕 UI**：游戏过程中需要动态替换字幕显示控件（例如切换语言皮肤），可使用 `USubtitlesSubsystem` 的交换 Widget 功能。
- **批量字幕队列**：通过 `USubtitleAssetUserData` 一次性排队多个字幕，并控制外部计时（External timing）与否。
- **编辑器工作流**：为音频资产附加 `USubtitleAssetUserData`，在 Blueprint 中直接调用“QueueAllSubtitlesInAsset”节点，无需 C++ 继承。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SubtitlesAndClosedCaptions)
- [Runtime 模块文档](SubtitlesAndClosedCaptions.md)
- [Editor 模块文档](SubtitlesAndClosedCaptionsEditor.md)