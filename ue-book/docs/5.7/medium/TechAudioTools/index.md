# TechAudioTools

> A collection of audio-related tools and utilities.

| 属性 | 值 |
|---|---|
| 中文名 | 技术音频工具集 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、MetaSound 预设） |
| 模块 | `TechAudioTools` (Runtime), `TechAudioToolsMetaSound` (Runtime), `TechAudioToolsMetaSoundEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-02 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/TechAudioTools) | |

## 用途

TechAudioTools 是一个处于实验阶段的音频工具集，专门为 MetaSound 和 MVVM（Model-View-ViewModel）框架集成而设计。它主要解决以下问题：

- 在 MetaSound 节点或 UI 中显示音频参数值时，需要将内部浮点值**格式化为带单位的可读文本**（例如将 440 显示为 “440 Hz”，将 0.5 显示为 “500 ms”），并支持自定义单位类型（如 `BandwidthOct`、`Tempo`）。
- 需要将 MetaSound 的字面量参数（如 `Float`、`Int`、`String` 等）**绑定到 UI 控件**，以便通过 UI 实时调节参数值。
- 在音频组件上提供**视图模型（AudioComponentViewModel）**，使蓝图或 C++ 能够更方便地驱动音频组件参数。

该插件不直接提供音频 DSP 功能，而是专注于**数据表示层**和**编辑器工具**，提升音频参数在 UI 和 MetaSound 编辑器的使用体验。

## 模块列表

| 模块 | 类型 | 一句话说明 |
|---|---|---|
| TechAudioTools | Runtime | 核心基础模块：提供单位类型定义、数值格式化与标签转换工具。 |
| TechAudioToolsMetaSound | Runtime | MetaSound 运行时扩展：为每个 MetaSound 字面量类型创建对应的 ViewModel，并增加 `BandwidthOct`、`Tempo` 等新单位类型。 |
| TechAudioToolsMetaSoundEditor | Editor | 编辑器集成模块：提供 MetaSound 编辑器 UI 支持，包括参数值格式化显示、文档辅助等。 |

各模块详细 API 请参阅对应文档：
- [TechAudioTools 模块文档](./TechAudioTools.md)
- [TechAudioToolsMetaSound 模块文档](./TechAudioToolsMetaSound.md)
- [TechAudioToolsMetaSoundEditor 模块文档](./TechAudioToolsMetaSoundEditor.md)

## 使用场景

### 场景一：在 MetaSound 编辑器中显示带单位的参数值
当你在 MetaSound 中创建了音频参数（如频率 `Frequency`、时长 `Duration`），希望编辑器节点或 UI 面板中直接显示为 “440 Hz” 或 “2.0 kHz” 等格式化文本时，可使用本插件提供的单位格式化功能。不需要手动编写字符串转换逻辑。

### 场景二：为音频参数创建可绑定的 UI 控件
如果使用 MVVM 模式构建 UI（如用户界面控件绑定到 MetaSound 参数），该插件的 ViewModel 类（如 `AudioComponentViewModel`、各类 `LiteralViewModel`）可以帮助你快速完成属性绑定，无需重复实现数据模型。

### 场景三：自定义单位类型
当标准单位（Hz, dB, seconds）无法满足需求时（例如需要带宽的 `Oct` 单位、节拍的 `BPM` 单位），该插件提供了扩展机制，允许在标签格式化器中注册新单位。

## 维护状态

### 近期更新

- 2025-09-29 `e2b39300` — TechAudioTools - Remove clamp when converting between source and display values while using Default
- 2025-09-03 `085d445f` — TechAudioTools - added BandwidthOct and Tempo as new float unit types for label formatting
- 2025-09-03 `a5101638` — TechAudioTools - Added AudioComponentViewModel
- 2025-09-03 `13481976` — TechAudioTools - fixed documentation errors
- 2025-09-02 `8eab906f` — TechAudioTools - added viewmodel classes for each MetaSound literal type

### 维护评价

**状态：实验性 - 活跃开发中**  
- 创建于 2025 年 9 月，距今不足 1 年，属于新插件。  
- 最近一个月内（截至 2025-09-29）有多次功能性更新，包括新增单位类型、添加 ViewModel、修复文档等，说明开发团队正在积极迭代。  
- 插件标记为 `IsBetaVersion=true` 和 `IsExperimentalVersion=true`，**接口和功能可能在未来版本中发生不兼容变更**，不建议用于生产项目。  
- 已知限制：未提供完整的单元测试覆盖（但从 git log 看暂未发现自动化测试内容）。  
- **推荐仅在实验性项目或原型开发中使用**，或等待正式版。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/TechAudioTools)
- [TechAudioTools 模块文档](./TechAudioTools.md)
- [TechAudioToolsMetaSound 模块文档](./TechAudioToolsMetaSound.md)
- [TechAudioToolsMetaSoundEditor 模块文档](./TechAudioToolsMetaSoundEditor.md)