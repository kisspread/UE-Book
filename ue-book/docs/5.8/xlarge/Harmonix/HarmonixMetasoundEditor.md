# Harmonix

> A package of Harmonix music related audio functionality.

| 属性 | 值 |
|---|---|
| 中文名 | 音乐音频套件 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（音乐资产、音序器模板） |
| 模块 | `Harmonix` (Runtime), `HarmonixDsp` (Runtime), `HarmonixDspEditor` (Runtime), `HarmonixDspTests` (Runtime), `HarmonixEditor` (Runtime), `HarmonixMetasound` (Runtime), `HarmonixMetasoundEditor` (Runtime), `HarmonixMetasoundTests` (Runtime), `HarmonixMidi` (Runtime), `HarmonixMidiEditor` (Runtime), `HarmonixMidiTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-17 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix) | |

## 用途

Harmonix 是由 Epic Games 的 Harmonix GenTech 团队开发的**音乐驱动音频处理套件**。Harmonix 团队以《Guitar Hero》《Rock Band》等音乐游戏闻名，本插件将他们在音乐同步、节奏量化、DSP 处理方面的专业技术带入 Unreal Engine。

该插件解决以下核心问题：

- **MIDI 数据解析与处理**：提供完整的 MIDI 文件解析、Step Sequencer（步进音序器）、Stutter Sequencer（卡顿音序器）等工具，支持在运行时驱动音乐事件
- **音频 DSP 处理**：提供音乐相关的数字信号处理能力，包括采样精确的音频调度和处理
- **MetaSound 集成**：将 Harmonix 的音乐处理能力作为 MetaSound 节点暴露，实现与 UE5 音频系统的深度集成
- **音乐驱动的游戏机制**：为节奏游戏、音乐可视化、节拍同步动画等场景提供基础设施

**注意**：此插件默认禁用（`EnabledByDefault: false`），且标记为实验性（`IsExperimentalVersion: true`），需要手动在项目设置中启用。

## 使用场景

- 你在开发一款**节奏音乐游戏**（如《Fortnite Festival》模式）→ 用 HarmonixMidi + HarmonixMetasound 实现节拍同步
- 你需要一个**步进音序器**来编排音乐模式 → 用 MidiStepSequence 资产和编辑器自定义 UI
- 你想要在 **MetaSound 图中使用 MIDI 数据**驱动音频节点 → 用 HarmonixMetasound 的 MetaSound 节点
- 你需要对音频流进行**实时 DSP 处理**（滤波、混响、频率分析等）→ 用 HarmonixDsp
- 你正在实现**音乐可视化或节拍驱动的视觉效果** → 用 Harmonix 的时间同步功能

## 子模块文档

| 模块 | 说明 |
|---|---|
| [Harmonix (核心)](./HarmonixCore.md) | 核心模块，提供基础音乐处理框架 |
| [HarmonixDsp](./HarmonixDsp.md) | DSP 音频处理模块 |
| [HarmonixMetasound](./HarmonixMetasound.md) | MetaSound 集成模块 |
| [HarmonixMidi](./HarmonixMidi.md) | MIDI 解析与处理模块 |
| [HarmonixMetasoundEditor](./HarmonixMetasoundEditor.md) | MetaSound 编辑器集成（当前模块） |
| [HarmonixDspEditor](./HarmonixDspEditor.md) | DSP 编辑器工具 |
| [HarmonixMidiEditor](./HarmonixMidiEditor.md) | MIDI 编辑器工具 |
| [HarmonixEditor](./HarmonixEditor.md) | 通用编辑器模块 |

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

> 注：虽然部分模块的 Build.cs 中包含 AssetRegistry 和 UnrealEd，这些属于常见的编辑器依赖，无需特别声明。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `8513e7f4` | [Audio] Fix FFusionVoice::AssignIDs KeyZone ordering + add structural null defense. | 修复 Fusion 语音 KeyZone 排序问题并增加空值防御 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决 FSoundWaveData API 废弃修复的合并冲突 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的警告 |
| 2026-05-12 | `0ae74ea8` | [Harmonix] Add user object to the FusionPatch proxy that can be used for tracking activity in associ | 为 FusionPatch 代理添加用户对象用于活动跟踪 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符不匹配问题 |

### 维护评价

**🟢 活跃维护中**

- 插件于 2024 年 1 月引入 UE5（对应 UE 5.4），从内部项目迁移到公开可用的 Runtime 插件
- 最近一次更新在 2026 年 5 月，持续有功能性修复和优化
- 大量源码文件（521 个），包含完整的测试模块（DspTests、MidiTests、MetasoundTests），说明项目质量标准较高
- 作为《Fortnite Festival》等产品的技术基础，有明确的商业使用场景支撑
- **注意**：目前仍标记为实验性（IsExperimentalVersion: true）且默认禁用，API 可能在未来版本中发生变化
- **推荐使用**：适合需要音乐驱动功能的项目，但需注意实验性状态，做好 API 变更的准备

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix)

---

# HarmonixMetasoundEditor 子模块文档

> Harmonix MetaSound 编辑器集成模块

## 模块信息

| 属性 | 值 |
|---|---|
| 模块名 | HarmonixMetasoundEditor |
| 类型 | Runtime |
| 源码路径 | `Source/HarmonixMetasoundEditor/` |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix/Source/HarmonixMetasoundEditor) | |

## 用途

HarmonixMetasoundEditor 模块负责将 Harmonix 的音乐资产（MIDI Step Sequencer、MIDI Stutter Sequence、Metasound Music、Wave Music）集成到 Unreal Editor 中。具体功能包括：

1. **自定义资产定义**：为 Harmonix 专有的资产类型注册编辑器中的显示名称、颜色、图标和分类
2. **资产工厂**：提供创建新 Harmonix 音乐资产的工厂类
3. **Step Sequencer 细节自定义**：为 MIDI Step Sequencer 提供可视化网格编辑器，支持多页浏览、单元格启用/禁用、延续状态等
4. **MetaSound 引脚样式**：为 Harmonix MetaSound 节点提供自定义引脚颜色和图标样式

## 蓝图用法

本模块主要是编辑器扩展，不直接暴露蓝图 API。

### 编辑器功能

本模块在编辑器中提供以下功能：

| 功能 | 说明 | 所在类 |
|---|---|---|
| 创建 MetaSound Music 资产 | 右键菜单 → Audio → MetaSound Music | `UHarmonixMetasoundMusicFactory` |
| 创建 Wave Music 资产 | 右键菜单 → Audio → Wave Music | `UHarmonixWaveMusicFactory` |
| 创建 MIDI Step Sequence 资产 | 右键菜单 → Audio → MIDI Step Sequence | `UMidiStepSequenceFactory` |
| 创建 MIDI Stutter Sequence 资产 | 右键菜单 → Audio → MIDI Stutter Sequence | `UMidiStutterSequenceFactory` |
| Step Sequencer 网格编辑器 | 在细节面板中可视化编辑步进音序器 | `FMidiStepSequenceDetailCustomization` |

### Step Sequencer 编辑器说明

MIDI Step Sequencer 的细节面板提供了一个网格状的可视化编辑器：

- **灰色单元格**：禁用状态
- **绿色单元格**：启用状态（播放音符）
- **黄色单元格**：延续状态（持续前一个音符）
- **分页支持**：支持多页浏览，通过 `CurrentPageNumber` 控制
- **点击切换**：点击单元格可切换启用/禁用/延续状态

## C++ 用法

### 模块启动/关闭

```cpp
#include "HarmonixMetasoundEditorModule.h"

// 获取模块实例
FHarmonixMetasoundEditorModule& Module = FModuleManager::GetModuleChecked<FHarmonixMetasoundEditorModule>("HarmonixMetasoundEditor");

// 模块会自动在编辑器启动时注册所有资产定义和工厂
```

### 自定义 MetaSound 引脚样式

```cpp
#include "HarmonixMetasoundSlateStyle.h"

// 获取样式实例
const HarmonixMetasoundEditor::FSlateStyle& Style = HarmonixMetasoundEditor::FSlateStyle::Get();

// 获取自定义引脚颜色
FLinearColor PinColor = Style.GetPinColor(FName("MyPinType"));

// 获取连接/断开状态的图标
const FSlateBrush* ConnectedIcon = Style.GetConnectedIcon(FName("MyPinType"));
const FSlateBrush* DisconnectedIcon = Style.GetDisconnectedIcon(FName("MyPinType"));
```

### 注册自定义 Step Sequencer 细节自定义

```cpp
#include "MidiStepSequenceDetailCustomization.h"

// 在编辑器模块启动时注册细节自定义
FPropertyEditorModule& PropertyModule = FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");
PropertyModule.RegisterCustomClassLayout(
    UMidiStepSequence::StaticClass()->GetFName(),
    FOnGetDetailCustomizationInstance::CreateStatic(&FMidiStepSequenceDetailCustomization::MakeInstance)
);
```

## 资产类型定义

本模块定义了以下资产类型在编辑器中的表现：

| 资产类型 | 显示名称 | 分类 | 用途 |
|---|---|---|---|
| `UAssetDefinition_MetasoundMusic` | MetaSound Music | Audio | 基于 MetaSound 的音乐资产 |
| `UAssetDefinition_WaveMusic` | Wave Music | Audio | 基于波形的音乐资产 |
| `UAssetDefinition_MidiStepSequence` | MIDI Step Sequence | Audio | MIDI 步进音序器 |
| `UAssetDefinition_MidiStutterSequence` | MIDI Stutter Sequence | Audio | MIDI 卡顿音序器 |

## Demo 示例

本模块作为编辑器扩展模块，不提供独立的运行时功能。使用示例请参考核心模块（HarmonixMetasound、HarmonixMidi）的文档。

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

> 注：本模块依赖 `HarmonixMetasound` 核心模块提供底层音乐资产类定义。

---

# 维护状态（汇总）

## 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `8513e7f4` | [Audio] Fix FFusionVoice::AssignIDs KeyZone ordering + add structural null defense. | 修复 Fusion 语音 KeyZone 排序问题并增加空值防御 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决 FSoundWaveData API 废弃修复的合并冲突 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的警告 |
| 2026-05-12 | `0ae74ea8` | [Harmonix] Add user object to the FusionPatch proxy that can be used for tracking activity in associ | 为 FusionPatch 代理添加用户对象用于活动跟踪 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符不匹配问题 |

## 维护评价

**🟢 活跃维护中**

- 插件于 2024 年 1 月引入 UE5（对应 UE 5.4），从 Epic Games 内部项目迁移到公开可用的 Runtime 插件
- 最近一次更新在 2026 年 5 月，持续有功能性修复和优化，维护频率较高
- 大量源码文件（521 个），包含完整的测试模块（DspTests、MidiTests、MetasoundTests），说明项目质量标准较高
- 作为《Fortnite Festival》等产品的技术基础，有明确的商业使用场景支撑
- **注意**：目前仍标记为实验性（IsExperimentalVersion: true）且默认禁用，API 可能在未来版本中发生变化
- **推荐使用**：适合需要音乐驱动功能的项目，但需注意实验性状态，做好 API 变更的准备

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix)