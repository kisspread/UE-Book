# MotoSynth

> An experimental granular vehicle engine. Intended to explore and demonstrate potential capabilities. Not supported.

| 属性 | 值 |
|---|---|
| 中文名 | 引擎音效合成 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、示例音频数据） |
| 模块 | `MotoSynth` (Runtime), `MotoSynthEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-11-24 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MotoSynth) | |

## 用途

MotoSynth 是一个实验性的音频合成系统，专用于实时生成可交互的车辆引擎声音。它并非采用传统的录制采样方式，而是通过“颗粒化合成”技术，动态地合成引擎的轰鸣、加速、减速等音效。这使得声音能够无缝、连续地响应游戏中的输入（如油门开度、转速），为赛车、载具模拟等游戏提供高度动态且可控的引擎音效。

## 使用场景

- 你正在开发一款赛车游戏，需要引擎声音能根据玩家的油门输入实时、平滑地变化。
- 你需要一个轻量级、无需庞大音频采样文件库的车辆引擎音效解决方案。
- 你想探索或实验游戏音频的实时合成技术，用于原型开发或技术演示。

## 蓝图用法

蓝图功能主要通过 `MotoSynthEditor` 模块集成到编辑器中。核心用法是将 MotoSynth 作为 Sound Cue 节点或音频资产组件使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `MotoSynth Node` | 作为 Sound Cue 节点，用于在音频图表中调用 MotoSynth 合成器。 | `UMotoSynthSoundCueNode` |

### 使用示例（蓝图描述）

1.  在内容浏览器中创建或找到一个 **MotoSynth** 资产（例如 `MotoSynthSampleData` 或一个预制的 MotoSynth Sound Cue）。
2.  在音频混合器（Sound Cue）图表中，添加一个 **MotoSynth** 节点。
3.  将该节点连接到最终输出，并为其设置合成器参数。
4.  在游戏逻辑蓝图中，通过车辆的转速（RPM）或油门输入来动态控制 MotoSynth 资产的播放参数（如音高、音量）。

## C++ 用法

运行时功能主要由 `MotoSynth` 模块提供，用于在游戏代码中集成和控制引擎音效。

### 头文件引入

```cpp
#include "MotoSynth.h"
```

### 基本用法

在车辆 Pawn 或 Actor 中，创建一个 `UAudioComponent` 并设置其 Sound 为一个使用了 MotoSynth 节点的 `USoundCue` 或 `USoundWave`。然后通过 `SetFloatParameter` 等函数来更新音效参数。

```cpp
// 在车辆类中
// 1. 创建并设置音频组件
AudioComponent = CreateDefaultSubobject<UAudioComponent>(TEXT("EngineSound"));
AudioComponent->SetupAttachment(RootComponent);
AudioComponent->SetSound(EngineSoundCue); // EngineSoundCue 是一个配置了MotoSynth的Sound资产

// 2. 在 Tick 或 Input 事件中更新参数
void AMyVehicle::UpdateEngineSound(float ThrottleInput, float RPM)
{
    if (AudioComponent)
    {
        // 将油门和转速传递给音频组件，驱动MotoSynth合成器
        AudioComponent->SetFloatParameter(FName("Throttle"), ThrottleInput);
        AudioComponent->SetFloatParameter(FName("RPM"), RPM);
    }
}
```

*(注：具体参数名取决于 MotoSynth 资产的配置)*

## 模块列表

- **MotoSynth**：运行时模块，包含颗粒化声音合成器的核心算法、音频资产类型（如 `UMotoSynthPreset`）和与音频引擎的交互逻辑。
- **MotoSynthEditor**：编辑器模块，提供在内容浏览器中创建和编辑 MotoSynth 预设的工具，以及将 MotoSynth 节点集成到 Sound Cue 编辑器的 UI 与功能。

## 模块依赖

要使用此插件，你的模块需要依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `AudioMixer` | 底层音频混合与处理框架 |
| `SignalProcessing` | 提供音频信号处理的数学工具库 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量截断为浮点数导致的编译器警告。 |
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | 内容浏览器“添加”菜单中的音频子菜单更新。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式的 `UE_LOG` 宏迁移至新的 `UE_LOGF` 格式化日志宏。 |
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 将插件配置文件命名规范从 `Base` 改为 `Default`。 |
| 2025-08-28 | `08e89bc9` | fixup ISoundGenerator::GetNextBuffer() implementers (don't assume zero'd buffer) | 修复声音生成器接口实现，不再假设缓冲区已清零。 |

### 维护评价

MotoSynth 是一个**实验性**插件，自2020年创建以来，保持着**定期但非重大功能**的维护。近期更新集中在编译器警告修复、宏迁移和代码规范化上，而非功能迭代。由于它被标记为“Experimental”且默认禁用，Epic 明确表示其“不受支持”。**它适合作为音频合成的技术参考或原型工具，但不推荐在需要长期稳定支持的商业项目中作为核心功能依赖。** 过去一年内仍有更新，表明代码库仍被维护以适应引擎的编译和基础架构变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MotoSynth)
- (无官方文档链接)