# Resonance Audio

> 3D audio spatialization and room acoustics simulation plugin by Google.

| 属性 | 值 |
|---|---|
| 中文名 | 空间音频 |
| 分类 | Audio |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（音频资产） |
| 模块 | `ResonanceAudio` (Runtime), `ResonanceAudioEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2017-12-13 |
| 年龄标签 | 🏛️ 文物（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ResonanceAudio) | |

## 用途

Resonance Audio 是 Google 提供的 3D 空间音频与室内声学模拟插件。它为 UE5 提供了基于 HRTF（头部相关传输函数）的头部追踪空间化、环境混响、房间声学模拟等功能，能在移动端和桌面端为玩家呈现逼真的 3D 听觉体验。相比 UE5 内置的空间音频方案，Resonance Audio 专注于移动端性能优化（Android/iOS）和 Google 生态集成。

## 使用场景

- 你在开发 VR/AR 应用，需要基于头部追踪的精准 3D 空间音频 → 用 Resonance Audio
- 你需要为游戏中的室内/室外环境模拟真实混响和声学反射 → 用 Resonance Audio
- 你在做 Android/iOS 移动端项目，需要高性能的空间音频方案 → 用 Resonance Audio
- 你需要为场景中的音频源添加遮挡、衍射等环境声学效果 → 用 Resonance Audio

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| **ResonanceAudio** | Runtime | 核心运行时模块，提供 HRTF 空间化、混响、房间声学模拟、蓝图 API 等功能。详见 [ResonanceAudio.md](ResonanceAudio.md) |
| **ResonanceAudioEditor** | Editor | 编辑器模块，提供 Resonance 音频设置的编辑器集成工具。详见 [ResonanceAudioEditor.md](ResonanceAudioEditor.md) |

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| 设置全局混响 | 配置 Resonance 全局混响参数 | `UResonanceAudioBlueprintFunctionLibrary` |
| 设置房间声学属性 | 配置当前房间的声学模拟参数 | `UResonanceAudioBlueprintFunctionLibrary` |

> 更多蓝图节点详见 [ResonanceAudio.md](ResonanceAudio.md) 的蓝图用法章节。

## C++ 用法

```cpp
#include "ResonanceAudioApi.h"
#include "ResonanceAudioBlueprintFunctionLibrary.h"
```

> 更多 C++ 用法和 API 详见 [ResonanceAudio.md](ResonanceAudio.md) 的 C++ 用法章节。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ProceduralMeshComponent` | 用于生成声学场景的几何网格（房间声学模拟需要） |
| `AudioMixer` | UE5 音频混音器后端集成 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 转 float 的编译警告 |
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | ContentBrowser 音频菜单更新（非插件本身改动） |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 全局日志宏迁移到 UE_LOGF（非插件本身改动） |
| 2026-01-20 | `7cfdbde4` | AudioMixerDevice - Add ref count to submixes using the register/unregister API. | 为 submix 添加引用计数机制（影响音频系统底层） |
| 2025-11-10 | `3ecbd390` | Fixed broken printf specifier strings. | 修复格式化字符串错误 |

### 维护评价

该插件创建于 2017 年（约 8 年前），由 Google 开发并贡献给 UE。虽然 `.uplugin` 中 `IsBetaVersion=true`，但实际上它已经在引擎中存在多年并被广泛使用。近期的 commit 多为编译警告修复和全局音频系统改动，并非该插件本身的功能更新。插件的核心功能已趋于稳定，但标记为实验性状态可能会影响生产环境中的采用信心。值得注意的是，Google 在 2023 年已停止对 Resonance Audio 的维护，后续由 Epic 以兼容性维护为主。

**推荐使用**：如果你的项目已经在使用 Resonance Audio 或需要 Google 生态兼容，可以继续使用；新项目建议评估 UE5 内置的空间音频方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ResonanceAudio)
- [官方文档](https://developers.google.com/resonance-audio/develop/unreal/getting-started)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ResonanceAudio/Tests)