# TextToSpeech

> A text to speech system that can be used to make auditory speech announcements given input strings.

| 属性 | 值 |
|---|---|
| 中文名 | 文本转语音系统 |
| 分类 | Accessibility |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `TextToSpeech` (Runtime), `Flite` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-12-16 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/TextToSpeech) | |

## 总体用途

TextToSpeech 插件提供了一套完整的文本转语音系统，允许开发者在游戏或应用中通过编程方式将文本字符串合成为语音并播放。插件底层集成了开源语音合成引擎 **Flite**，屏蔽了不同平台（Windows、macOS、Android、iOS、Linux）的音频输出差异，提供统一且易于使用的 API。适用于辅助功能（Accessibility）、语音导航、错误播报、游戏内语音提示等需要听觉反馈的场景。

## 模块概览

| 模块 | 类型 | 一句话说明 |
|---|---|---|
| `TextToSpeech` | Runtime | 核心模块，提供蓝图和 C++ 接口：创建和管理语音实例、设置语言/语速/音量、异步合成与播放。 |
| `Flite` | Runtime | 第三方库集成模块，封装了 CMU Flite 语音合成引擎，实现底层文本分析、波形生成和平台音频输出。 |

各模块详细文档请见：
- [TextToSpeech 模块文档](TextToSpeech.md)
- [Flite 模块文档](Flite.md)

## 使用场景

- **辅助功能**: 为视障玩家朗读菜单、对话或重要通知，提升游戏可访问性。
- **语音导航**: 在虚拟现实或导航应用中，通过语音提示指导用户操作或移动。
- **动态播报**: 实时播报游戏内事件（如击杀、任务更新、聊天消息），减少对 HUD 的依赖。
- **教育和儿童应用**: 为语言学习软件或儿童故事书提供朗读能力。
- **自动化测试**: 在自动化测试中通过音频输出验证系统响应。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/TextToSpeech)