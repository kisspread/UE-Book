# Harmonix

> A package of Harmonix music related audio functionality.

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（音乐资产、MetaSound 节点、MIDI 资产） |
| 模块 | `Harmonix` (Runtime), `HarmonixDsp` (Runtime), `HarmonixDspEditor` (Runtime), `HarmonixDspTests` (Runtime), `HarmonixEditor` (Runtime), `HarmonixMetasound` (Runtime), `HarmonixMetasoundEditor` (Runtime), `HarmonixMetasoundTests` (Runtime), `HarmonixMidi` (Runtime), `HarmonixMidiEditor` (Runtime), `HarmonixMidiTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-17 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Harmonix) | |

## 用途

Harmonix 是 Epic Games 旗下 Harmonix GenTech 团队（原 Harmonix Music Systems，知名音乐游戏《Rock Band》《Guitar Hero》的开发商）开发的一套**音乐驱动音频功能包**。它不是简单的音频播放器，而是一套完整的**音乐感知音频处理框架**，解决以下核心问题：

1. **音乐同步处理**：提供节拍同步（Beat Sync）、BPM 跟踪、音乐时间线管理，让游戏音频能精确跟随音乐节拍
2. **DSP 音频处理**：内置专业级数字信号处理模块，包括滤波器、延迟、失真、压缩等效果器
3. **MIDI 处理**：完整的 MIDI 文件解析、序列化和回放能力，支持 MIDI 步进序列（Step Sequence）编辑
4. **MetaSound 集成**：将上述所有功能封装为 MetaSound 节点，可在 MetaSound 编辑器中可视化地构建音乐交互逻辑
5. **Stutter/节奏效果**：支持 Stutter Edit（音频切片重复）效果和 Stutter Sequencer 节点，用于创造节奏性音频效果
6. **Wave 音乐资产**：支持 Wave Music Asset 格式，用于管理带音乐元数据的音频文件

**为什么存在**：UE5 内置的音频系统（Sound Cue、MetaSound）虽然强大，但缺乏专业音乐游戏和音乐交互应用所需的**音乐理论感知能力**。Harmonix 填补了这一空白，让开发者能在 MetaSound 中直接使用节拍同步、MIDI 序列、DSP 效果等专业音乐功能。

## 使用场景

- 你在做**音乐节奏游戏**（类似 Beat Saber、Rock Band）→ 用 Harmonix 的节拍同步和 MIDI 处理
- 你需要**音乐驱动的视觉/游戏效果**（节拍触发事件、BPM 同步动画）→ 用 Harmonix 的音乐时间线
- 你要在 MetaSound 中构建**复杂的音乐交互逻辑** → 用 HarmonixMetasound 提供的节点
- 你需要**实时音频效果处理**（滤波、延迟、失真、压缩）→ 用 HarmonixDsp 的效果器
- 你要处理 **MIDI 文件**并将其用于游戏逻辑 → 用 HarmonixMidi 的解析和序列化
- 你要创建**节奏性音频切片效果**（Glitch/Stutter 风格）→ 用 Stutter Sequencer 节点
- 你需要管理**带音乐元数据的音频文件**（BPM、拍号、时间签名）→ 用 Wave Music Asset

## 模块架构

```
Harmonix (插件根)
├── Harmonix                    ← 核心运行时模块（基础类型、音乐时间线）
├── HarmonixDsp                 ← DSP 音频处理（滤波器、效果器、音频分析）
├── HarmonixMidi                ← MIDI 处理（文件解析、序列化、步进序列）
├── HarmonixMetasound           ← MetaSound 集成（自定义节点、数据类型）
├── HarmonixEditor              ← 编辑器支持（核心）
├── HarmonixDspEditor           ← 编辑器支持（DSP）
├── HarmonixMidiEditor          ← 编辑器支持（MIDI）
├── HarmonixMetasoundEditor     ← 编辑器支持（MetaSound）
├── HarmonixDspTests            ← DSP 模块测试
├── HarmonixMidiTests           ← MIDI 模块测试
└── HarmonixMetasoundTests      ← MetaSound 模块测试
```

### 子模块文档

| 模块 | 说明 | 文档 |
|---|---|---|
| Harmonix | 核心运行时，基础类型定义和音乐时间线 | [Harmonix](Harmonix.md) |
| HarmonixDsp | DSP 音频处理引擎 | [HarmonixDsp](HarmonixDsp.md) |
| HarmonixMidi | MIDI 文件解析与序列化 | [HarmonixMidi](HarmonixMidi.md) |
| HarmonixMetasound | MetaSound 自定义节点和数据类型 | [HarmonixMetasound](HarmonixMetasound.md) |

## 蓝图用法

Harmonix 的蓝图 API 主要通过 MetaSound 节点暴露，而非传统的蓝图函数节点。核心交互方式是在 **MetaSound 编辑器**中使用 Harmonix 提供的自定义节点。

### 核心 MetaSound 节点

| 节点类型 | 说明 | 所在模块 |
|---|---|---|
| Stutter Sequencer | 音频切片重复序列器，创造节奏性 Glitch 效果 | HarmonixMetasound |
| Simple Sampler | 简单采样器节点 | HarmonixMetasound |
| Stutter Edit Effect | Stutter 编辑效果器 | HarmonixMetasound |
| Midi Stutter Sequence | MIDI 驱动的 Stutter 序列数据类型 | HarmonixMetasound |

### MIDI 步进序列编辑器

HarmonixMetasoundEditor 模块注册了 `UAssetDefinition_MidiStepSequence`，提供 MIDI 步进序列资产的编辑器支持。可在内容浏览器中创建和编辑 MIDI 步进序列资产。

## C++ 用法

### 头文件引入

```cpp
// 核心模块
#include "HarmonixModule.h"

// DSP 处理
#include "HarmonixDspModule.h"

// MIDI 处理
#include "HarmonixMidiModule.h"

// MetaSound 集成
#include "HarmonixMetasoundModule.h"
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MetasoundEngine` | MetaSound 引擎集成，用于注册自定义节点 |
| `MetasoundFrontend` | MetaSound 前端框架，节点定义和图编辑 |
| `AudioMixer` | UE5 音频混合器，底层音频处理 |
| `SignalProcessing` | UE5 信号处理库，DSP 基础设施 |
| `AssetRegistry` | 资产注册表，用于资产类型定义 |
| `Harmonix` | 核心模块，被其他所有 Harmonix 模块依赖 |

## 维护状态

### 近期更新

```
- 9803c43 Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied using UnrealCodeFixup)
- 887ca3a Stutter Edit Effect for Metasound - New Simple Sampler Node - New Stutter Sequencer Node - New Midi Stutter Sequence data type
- b8eed2e Harmonix Wave Music Assets
```

### 维护评价

- **创建时间**：2024-01-17，约 1 年前，属于较新的插件
- **活跃度**：近期有实质性功能更新（Stutter 效果、新节点、Wave Music Assets），表明正在积极开发
- **实验性状态**：标记为 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`，API 可能在未来版本中发生变化
- **团队背景**：由 Epic Games 旗下 Harmonix GenTech 团队维护，有专业音乐游戏开发背景
- **代码规模**：722 个源文件，属于大型插件，功能覆盖面广

**⚠️ 注意**：此插件为实验性功能，API 不稳定，不建议在生产环境中依赖。建议关注后续版本的稳定性改进。适合用于原型开发和功能探索。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Harmonix)
- [MetaSound 文档](https://docs.unrealengine.com/5.7/en-US/overview-of-metasound-in-unreal-engine/)（Harmonix 依赖的底层系统）