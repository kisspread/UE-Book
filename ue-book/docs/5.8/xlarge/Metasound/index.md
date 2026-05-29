# MetaSound

> A high-performance audio system that enables sound designers to have complete control over audio DSP graph generation of sound sources, via sample-accurate control and modulation of sound using audio parameters and audio events from game data and Blueprints

| 属性 | 值 |
|---|---|
| 中文名 | MetaSound 音频系统 |
| 分类 | Audio |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `MetasoundEditor` (Runtime), `MetasoundEngine` (Runtime), `MetasoundEngineTest` (Runtime), `MetasoundFrontend` (Runtime), `MetasoundGenerator` (Runtime), `MetasoundGraphCore` (Runtime), `MetasoundStandardNodes` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-05-23 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Metasound) | |

## 用途

MetaSound 是一个完全基于节点图的高性能音频系统。它取代了传统的基于资产的音频播放方式，允许声音设计师像搭建蓝图一样，通过连接各种音频处理节点（振荡器、滤波器、包络、混音器等）来程序化地生成和处理声音。其核心优势在于：
1.  **样本精确控制**：所有参数的调制和变化都与音频采样率同步，实现极其精准的声音控制。
2.  **参数化与事件驱动**：可以将游戏数据（如角色速度、生命值）或蓝图事件（如按键、碰撞）作为音频参数和事件输入，动态改变声音的生成逻辑。
3.  **运行时生成**：音频 DSP（数字信号处理）图形在运行时编译并执行，灵活性远超预烘焙的音频资产。

它解决了传统音频系统在灵活性、实时控制和性能上的局限性，适用于需要高度动态、交互式音频的游戏和应用。

## 使用场景

-   **程序化音频**：需要根据游戏状态（速度、高度、环境）实时变化音乐、环境音效或引擎声音。
-   **交互式音效**：玩家输入（如不同力度的按键、连击）需要产生完全不同且连贯的音效反馈。
-   **动态混音与音频可视化**：需要根据音频频谱数据驱动游戏内视觉元素（如灯光、UI动画）。
-   **海量音效变体**：通过参数变化，从一个 MetaSound 资产生成无数种声音变体，减少资产管理负担。

## 蓝图用法

MetaSound 的蓝图 API 核心在于创建、播放和参数化 MetaSound 源。详细函数请参阅各子模块文档（如 `MetasoundEngine`）。

### 核心概念

| 概念 | 说明 | 关键类 |
|---|---|---|
| MetaSound 资产 | 在编辑器中创建的节点图音频资产，定义声音的生成逻辑。 | `UAssetDefinition_MetaSound` (编辑器) |
| MetaSound 播放 | 在世界中播放一个 MetaSound 实例。 | `UAudioComponent` |
| 参数输入 | 向正在播放的 MetaSound 实例发送浮点、整型、布尔等参数。 | `UAudioComponent` |
| 事件触发 | 向 MetaSound 发送事件以触发特定逻辑分支。 | `UAudioComponent` |

### 使用示例（蓝图描述）
1.  在内容浏览器中右键 -> 音频 -> MetaSound，创建一个新资产并进入节点编辑器。
2.  添加音频节点（如 `Sine Oscillator`, `ADSR Envelope`）并连接它们。
3.  添加一个输入节点（如 `FloatInput`）并命名为 “Pitch”，连接到振荡器的频率引脚。
4.  在角色蓝图中，添加一个 `Audio Component`，其 `Sound` 属性设置为刚创建的 MetaSound 资产。
5.  通过蓝图脚本，使用 `Set Float Parameter` 节点，设置参数名 “Pitch” 为变量值（如角色的移动速度），即可实现速度驱动音高的效果。

## C++ 用法

C++ 用法主要涉及在运行时创建、播放 MetaSound 实例并控制其参数。详细 API 请参阅 `MetasoundEngine` 模块文档。

### 头文件引入

```cpp
#include "MetasoundWave.h"
#include "MetasoundAssetBase.h"
```

### 基本用法

通过 `UAudioComponent` 播放 MetaSound 并设置参数。

```cpp
// 获取或创建 AudioComponent
UAudioComponent* AudioComp = MyActor->FindComponentByClass<UAudioComponent>();
if (!AudioComp)
{
    AudioComp = NewObject<UAudioComponent>(MyActor);
    AudioComp->RegisterComponent();
}

// 设置 MetaSound 资产
TSoftObjectPtr<UMetaSoundSource> MetaSoundAsset = ...; // 从路径或资产加载器获取
AudioComp->SetSound(MetaSoundAsset.LoadSynchronous());

// 播放
AudioComp->Play();

// 设置参数
AudioComp->SetFloatParameter(FName("MyFloatParam"), 0.5f);
AudioComp->SetBoolParameter(FName("MyBoolParam"), true);
```

### 进阶用法

使用 `FMetasoundGenerator` 直接控制音频图的输入输出，适用于需要精细控制音频缓冲区的场景（如音频可视化）。

```cpp
// 获取 MetaSound 的生成器实例
FMetasoundGenerator* Generator = AudioComp->GetMetasoundGenerator();
if (Generator)
{
    // 添加自定义输出以获取音频数据
    Generator->AddAudioOutput(FName("AudioForVisualization"));

    // 在 Tick 或定时器中读取音频缓冲
    TArray<float> AudioBuffer;
    if (Generator->GetAudioBuffer(FName("AudioForVisualization"), AudioBuffer))
    {
        // 处理 AudioBuffer，用于可视化或其他逻辑
    }
}
```

## Demo 示例

作为大型插件，MetaSound 的完整示例分散在引擎的示例项目中。子模块文档（如 `MetasoundStandardNodes.md`）中包含了各种标准节点的详细用法，是学习和构建 MetaSound 图的最佳参考。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AudioMixer` | 底层音频混音和设备管理，MetaSound 引擎在此之上运行。 |
| `SignalProcessing` | 提供 DSP 算法和数学库，用于构建音频处理节点。 |
| `MetasoundFrontend` | 定义节点图的前端表示、元数据和编译接口。 |
| `MetasoundGraphCore` | 实现节点图的核心运行时框架、数据传递和执行逻辑。 |
| `MetasoundEngine` | 集成引擎音频系统，提供资产、组件和播放接口。 |
| `MetasoundStandardNodes` | 提供一套内置的音频处理节点（振荡器、滤波器、包络等）。 |
| `MetasoundEditor` | 提供编辑器内 MetaSound 资产的编辑器、图表和预览功能。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `17643970` | Fix ensure when deleting and re-adding a MetaSound Page graph | 修复了删除并重新添加 MetaSound 页面图时的断言问题。 |
| 2026-05-14 | `278def59` | Guard MetaSound preset creation against non-Referenceable parents | 为 MetaSound 预设创建增加了对不可引用父级的防护。 |
| 2026-05-14 | `6121cd30` | Protect against mutation of target PageID in shipped builds | 防止在发布版本中目标 PageID 被意外修改。 |
| 2026-05-14 | `79768793` | Clean-up pass on prior fix for deadlock fix when entering PIE | 清理了之前修复进入 PIE 时死锁问题的代码。 |
| 2026-05-14 | `de6200e1` | Speculative fix for freeze when entering PIE | 修复了进入 PIE（Play In Editor）时可能导致冻结的潜在问题。 |

### 维护评价

MetaSound 作为 Epic Games 官方主推的现代音频系统，处于**积极维护**状态。从提交历史看，核心团队仍在频繁修复关键问题（如编辑器稳定性、运行时死锁），并优化其内部架构。尽管创建已约 6 年，但其功能和稳定性仍在持续增强，是 UE5 中音频开发的**推荐首选方案**。建议开发者使用，并关注其节点和 API 的演进。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Metasound)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/metasounds-in-unreal-engine) (外部链接)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Metasound/Source/MetasoundEngineTest)