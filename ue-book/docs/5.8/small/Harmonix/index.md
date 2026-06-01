# Harmonix

> A package of Harmonix music related audio functionality.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 哈莫尼克斯音频套件 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `Harmonix` (Runtime), `HarmonixDsp` (Runtime), `HarmonixDspEditor` (Runtime), `HarmonixDspTests` (Runtime), `HarmonixEditor` (Runtime), `HarmonixMetasound` (Runtime), `HarmonixMetasoundEditor` (Runtime), `HarmonixMetasoundTests` (Runtime), `HarmonixMidi` (Runtime), `HarmonixMidiEditor` (Runtime), `HarmonixMidiTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-17 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix) | |

## 用途

Harmonix 插件为 Unreal Engine 5 提供了一套由 Harmonix（Epic 旗下音乐游戏技术公司）开发的专业音乐与音频工具集。它主要解决音乐游戏（如《摇滚乐队》、《Fuser》）开发中的核心问题：**精确的、基于时间轴的音乐交互**。

该插件通过底层的 MIDI 解析、数字信号处理（DSP）以及与 UE5 原生 MetaSound 音频图的深度集成，使开发者能够：
- **精确驱动游戏逻辑**：根据音乐的节拍、小节、和弦变化等实时触发游戏事件。
- **处理 MIDI 数据**：解析、修改和生成 MIDI 消息，用于控制虚拟乐器或游戏机制。
- **扩展 MetaSound**：提供专门用于音乐交互的音频处理节点。
- **实现低延迟音频合成**：包含高性能的音频合成器（Fusion），适用于实时音乐生成和效果处理。

## 使用场景

- **音乐/节奏游戏开发**：需要精确的节拍同步、输入判定和音乐驱动的视觉效果。
- **互动音乐系统**：游戏音乐能根据玩家行为或游戏状态实时变化和过渡。
- **音频可视化工具**：分析音频信号的频率、节拍等特征来驱动视觉元素。
- **专业音乐制作工具集成**：在 UE 编辑器中处理和编辑 MIDI 数据。

## 模块概览

本插件包含 11 个模块，分工如下：

| 模块 | 类型 | 用途简介 |
|---|---|---|
| **Harmonix** | Runtime | 插件的核心模块，提供基础类型、接口和音乐时钟系统。 |
| **HarmonixMidi** | Runtime | 完整的 MIDI 文件解析、数据结构和处理管线。 |
| **HarmonixMetasound** | Runtime | 为 MetaSound 提供专用于音乐交互的节点（如节拍检测、MIDI 音序器）。 |
| **HarmonixDsp** | Runtime | 数字信号处理工具库，包含 Fusion 合成器和音频分析功能。 |
| **HarmonixEditor** | Runtime | 为 Harmonix 核心功能提供编辑器内的资产预览和工具支持。 |
| **HarmonixMidiEditor** | Runtime | 为 MIDI 资产提供编辑器内的查看和编辑支持。 |
| **HarmonixMetasoundEditor** | Runtime | 为 HarmonixMetaSound 节点提供编辑器支持。 |
| **HarmonixDspEditor** | Runtime | 为 HarmonixDsp（如 Fusion Patch）提供编辑器支持。 |
| **HarmonixDspTests** | Runtime | 包含 HarmonixDsp 模块的自动化测试用例。 |
| **HarmonixMetasoundTests** | Runtime | 包含 HarmonixMetasound 模块的自动化测试用例。 |
| **HarmonixMidiTests** | Runtime | 包含 HarmonixMidi 模块的自动化测试用例。 |

## 相关链接

- [源码目录](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix)

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `8513e7f4` | [Audio] Fix FFusionVoice::AssignIDs KeyZone ordering + add structural null defense. | 修复 Fusion 合成器音区（KeyZone）排序问题并增加空指针防护。 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决与 `FSoundWaveData` API 废弃修复相关的合并冲突。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下 `double` 常量被截断为 `float` 产生警告的代码。 |
| 2026-05-12 | `0ae74ea8` | [Harmonix] Add user object to the FusionPatch proxy that can be used for tracking activity in associ... | 为 FusionPatch 代理添加用户对象，可用于关联活动跟踪。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正格式化字符串说明符，确保其与参数位宽（32/64位）匹配。 |

### 维护评价

Harmonix 是一个**活跃维护中**的实验性插件。
- **创建时间**：2024年1月随 UE 5.4 引入，历史不足2年。
- **更新频率**：从提交记录看，在2026年5月仍有密集的修复和改进提交，表明 Epic 内部仍在积极使用和维护此插件。
- **状态**：`IsExperimentalVersion=true` 且 `EnabledByDefault=false`，表明它仍处于开发和完善阶段，API 可能变动，不建议用于对稳定性要求极高的正式项目。
- **推荐度**：如果你正在开发**音乐驱动**的交互式体验或游戏，尤其是需要与 MetaSound 集成，那么这个插件是**强烈推荐**的专业工具集。建议在实验性项目或原型中先行评估。