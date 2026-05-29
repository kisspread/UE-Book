# Synthesis and DSP Effects

> A variety of realtime synthesizers and DSP source and submix effects.

| 属性 | 值 |
|---|---|
| 中文名 | 音频合成与DSP效果 |
| 分类 | Audio |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（音频资产、测试蓝图） |
| 模块 | `Synthesis` (Runtime), `SynthesisEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2017-01-10 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Synthesis) | |

## 用途

Synthesis 插件为 UE5 提供了一套完整的实时音频合成和 DSP（数字信号处理）框架。它解决的核心问题是：在运行时动态生成和处理音频，而不需要预先录制或烘焙音频资产。

**主要功能包括：**
- **实时合成器**：包括 EpicSynth1 等多复音虚拟模拟合成器，可通过蓝图或 C++ 控制振荡器、滤波器、包络等参数
- **Source Effects**：可挂载在声源上的 DSP 效果链（如延迟、失真、滤波等）
- **Submix Effects**：作用于混音总线的 DSP 效果（如全局混响、EQ 等）
- **MIDI 支持**：集成 MIDI 输入，支持 MIDI 控制合成器
- **音频可视化工具**：波形显示、频谱分析等调试工具

## 使用场景

- 你需要在游戏中动态生成音效（如程序化音乐、交互式环境音）→ 使用 EpicSynth1 或自定义合成器
- 你需要对特定声源应用实时音频效果（如回声、失真、滤波）→ 使用 Source Effects
- 你需要全局混音效果（如房间混响、主输出压缩）→ 使用 Submix Effects
- 你需要接收 MIDI 输入控制游戏音频 → 使用 MIDI 组件
- 你需要音频可视化调试工具 → 使用内置的波形/频谱显示

## 模块概览

| 模块 | 类型 | 说明 |
|---|---|---|
| `Synthesis` | Runtime | 核心模块，包含所有合成器、DSP 效果和音频组件 |
| `SynthesisEditor` | Editor | 编辑器扩展，提供音频资产编辑器和可视化工具 |

## 子模块文档

由于本插件包含 101 个源文件，文档按子模块拆分：

- [Synthesis.md](Synthesis.md) — 运行时模块详细文档（合成器、DSP 效果、组件 API）
- [SynthesisEditor.md](SynthesisEditor.md) — 编辑器模块详细文档（编辑器工具、资产编辑器）

## 蓝图核心节点概览

| 功能分类 | 代表节点 | 说明 |
|---|---|---|
| 合成器控制 | `NoteOn`, `NoteOff`, `SetSynthPreset` | 控制 EpicSynth1 的音符和预设 |
| 效果链管理 | `AddSourceEffect`, `AddSubmixEffect` | 动态添加/移除音频效果 |
| MIDI | `MidiNoteOn`, `MidiNoteOff` | 处理 MIDI 输入事件 |
| 参数控制 | `SetFloatParam`, `SetModulationParam` | 实时调整合成器和效果参数 |

## C++ 核心类概览

| 类名 | 用途 |
|---|---|
| `USynthComponent` | 合成器组件基类，可挂载到 Actor 上 |
| `UEpicSynth1Component` | EpicSynth1 虚拟模拟合成器组件 |
| `USourceEffectBase` | Source Effect 效果基类 |
| `USubmixEffectBase` | Submix Effect 效果基类 |
| `USynth2DSlider` | 2D 滑块控件（用于合成器参数调节） |
| `UMIDIControllerBlueprintProxy` | MIDI 控制器蓝图代理 |

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AudioSynesthesiaCore` | 音频分析核心（用于音频特征提取） |
| `AudioSynesthesia` | 音频感知插件（作为前置插件依赖） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 截断为 float 的编译警告 |
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | 内容浏览器新增音频菜单入口 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到 UE_LOGF 新格式 |
| 2026-03-10 | `22707c32` | [Subsonic] Generator sources can be played/stopped through subsonic actions, and get cleaned up when | Subsonic 系统集成，支持通过 Subsonic 控制生成器音源的播放/停止和清理 |
| 2026-03-09 | `a5cf226b` | Rename FModulationDestination::UpdateModulators to SetModulators | 重命名调制目标的更新函数为 SetModulators |

### 维护评价

**维护状态：✅ 活跃维护中**

- 插件创建于 2017 年（约 9 年历史），是 UE4 时代引入的核心音频功能
- 2026 年仍有持续更新，最近一次修改在 2026 年 5 月
- 近期更新包括新功能集成（Subsonic）、编译兼容性修复、API 命名规范化
- 作为 Epic 官方维护的音频基础设件，稳定可靠
- **推荐使用**：适用于任何需要实时音频合成或 DSP 处理的 UE5 项目

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Synthesis)
- [AudioSynesthesia 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AudioSynesthesia)（前置依赖）