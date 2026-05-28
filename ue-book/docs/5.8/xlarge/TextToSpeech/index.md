# TextToSpeech

> A text to speech system that can be used to make auditory speech announcements given input strings.

| 属性 | 值 |
|---|---|
| 中文名 | 文本转语音 |
| 分类 | Accessibility |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `TextToSpeech` (Runtime), `Flite` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-03-11 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TextToSpeech) | |

## 用途

这是一个为游戏提供**文本转语音（TTS）**能力的运行时插件。它基于开源的 **Flite** 语音合成引擎，能够将输入的文本字符串转换为语音音频输出。

该插件存在的主要目的是支持**无障碍（Accessibility）**场景——例如为视力障碍玩家朗读 UI 文本、菜单选项、游戏内提示信息等，使游戏内容可以被听觉方式获取。同时也可以用于需要动态语音播报的游戏场景（如实时解说、语音导航等）。

插件支持 Windows、Mac、iOS、Android 和 Linux 平台，但不支持服务器目标（Server）。

## 使用场景

- 你在做一个需要无障碍支持的游戏 → 用 TextToSpeech 为屏幕阅读器用户朗读 UI 文本
- 你需要动态生成语音播报（如体育解说、实时提示）→ 用 TextToSpeech 将字符串转为语音
- 你需要跨平台的 TTS 能力（Windows/Mac/Mobile/Linux）→ 用 TextToSpeech 统一封装
- 你在开发面向视障用户的交互应用 → 用 TextToSpeech 集成语音反馈

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| [`TextToSpeech`](TextToSpeech.md) | Runtime | 核心 TTS 功能模块，提供文本转语音 API、平台抽象层和蓝图接口 |
| [`Flite`](Flite.md) | Runtime | 第三方 Flite 语音合成引擎封装，提供底层语音合成能力 |

## 蓝图用法

详细蓝图 API 请参考 [TextToSpeech 模块文档](TextToSpeech.md)。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Speak` | 输入文本字符串，启动语音合成与播放 | `UTextToSpeechEngine` |
| `StopSpeaking` | 立即停止当前正在播放的语音 | `UTextToSpeechEngine` |
| `IsSpeaking` | 查询当前是否正在播放语音 | `UTextToSpeechEngine` |
| `GetTextToSpeechEngine` | 获取全局 TextToSpeech 引擎实例 | `UTextToSpeechEngine` |

## C++ 用法

详细 C++ API 和代码示例请参考 [TextToSpeech 模块文档](TextToSpeech.md)。

### 头文件引入

```cpp
#include "TextToSpeechEngine.h"
```

### 基本用法

```cpp
// 获取 TTS 引擎实例并播放语音
UTextToSpeechEngine* TTSEngine = UTextToSpeechEngine::GetTextToSpeechEngine();
if (TTSEngine)
{
    TTSEngine->Speak(TEXT("Hello, welcome to the game!"));
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine 等）。

插件内置了第三方 Flite 库的源码，无需额外外部依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移到新 API |
| 2026-01-28 | `5f766aee` | Fixed modules that does not support portable toolchain | 修复便携工具链兼容性问题 |
| 2026-01-13 | `4c04edd1` | [IOS/Mac] Initial pass to remove iOS/macOS sdk headers from Engine platform header files where possi | 清理 iOS/Mac 平台头文件依赖 |
| 2025-02-19 | `392e7feb` | TTS: Wrapping other maincall correctly for iOS | 修复 iOS 平台初始化调用封装 |
| 2025-02-19 | `623d8d9d` | TTS: Fixing up iOS issues. | 修复 iOS 平台相关问题 |

### 维护评价

该插件自 2021 年创建以来已有约 5 年历史，最近的更新集中在**平台兼容性修复**和**引擎代码风格迁移**，而非功能增强。近一年内的更新主要是编译修复和日志 API 迁移，没有实质性新功能添加。

**仍处于实验阶段**（`IsExperimental=true`，`EnabledByDefault=false`），表明 Epic 尚未将其视为稳定特性。需要注意的是，该插件的核心 TTS 能力依赖 Flite 这个较老的开源语音合成库，语音质量可能不及现代 TTS 方案。

⚠️ **使用建议**：适合对语音质量要求不高的无障碍场景和原型开发。如需高质量语音合成，建议考虑集成外部 TTS 服务（如 Azure Speech、Google Cloud TTS）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TextToSpeech)
- [TextToSpeech 模块文档](TextToSpeech.md)
- [Flite 模块文档](Flite.md)
- 官方文档：无
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TextToSpeech/Tests)