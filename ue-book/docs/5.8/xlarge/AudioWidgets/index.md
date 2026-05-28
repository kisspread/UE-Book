# AudioWidgets

> Collection of widgets tailored to interacting with audio-related data and systems.

| 属性 | 值 |
|---|---|
| 中文名 | 音频控件 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（样式资产、材质模板） |
| 模块 | `AudioWidgetsCore` (Runtime), `AudioWidgets` (Runtime), `AudioWidgetsEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-12-10 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AudioWidgets) | |

## 用途

AudioWidgets 提供一套专为音频可视化和交互设计的 UMG 控件集合。与普通 UI 控件不同，这些控件内置了音频领域的专业逻辑——例如响度计量、削波检测、频率分析可视化、分贝刻度映射等，开发者无需从零实现音频数据到视觉表现的桥接。

该插件同时为 Unreal Insights 的音频分析面板提供底层控件支持，通过 `AudioWidgetsCore` 模块实现了与特定程序（Program）绑定的轻量运行时，使音频分析工具能在 Insights 等独立程序中使用。

插件依赖 `AudioSynesthesia` 插件进行底层音频特征提取（响度、频谱等），而 AudioWidgets 负责将这些数据以专业音频 UI 的形式呈现。

## 使用场景

- 你需要在编辑器或游戏中构建专业音频混音界面 → 用 Audio Knob、Audio Fader、Audio Button 等控件
- 你需要实时监控音频响度和峰值 → 用 Loudness Meter、Audio Meter 控件
- 你在开发 Unreal Insights 的音频分析插件 → 依赖 AudioWidgetsCore 提供计量控件
- 你需要按钮矩阵来快速切换音频通道或效果 → 用 Audio Button Matrix 控件

## 模块列表

| 模块 | 类型 | 说明 | 文档 |
|---|---|---|---|
| `AudioWidgetsCore` | RuntimeAndProgram | 核心计量逻辑与 Slate 底层控件，可独立于 UMG 在 Unreal Insights 中运行 | [AudioWidgetsCore.md](AudioWidgetsCore.md) |
| `AudioWidgets` | Runtime | UMG 封装层，提供蓝图可用的音频控件（旋钮、推子、按钮、响度计等） | [AudioWidgets.md](AudioWidgets.md) |
| `AudioWidgetsEditor` | Editor | 编辑器扩展，提供自定义控件的详情面板和预览支持 | [AudioWidgetsEditor.md](AudioWidgetsEditor.md) |

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AudioSynesthesia` | 底层音频特征分析（响度、频谱等数据源） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 转 float 的截断警告 |
| 2026-05-12 | `fcaaf385` | [AudioWidgets] Loudness Meters: context menu polish. Reorganize settings into Loudness Scale, Refere | 响度计上下文菜单优化，重新组织设置分类 |
| 2026-05-12 | `d2e95dfd` | [AudioWidgets] Loudness Meter: add max value indicator line on meters that support max value. | 为支持最大值的响度计添加最大值指示线 |
| 2026-05-12 | `ba019a16` | [AudioWidgets] Audio Meter: implemented ClippingValue draw in SAudioMeterWidget. | 实现音频表 Slate 控件的削波值绘制 |
| 2026-05-12 | `bd1d2d5c` | [AudioWidgets] [Audio Insights] Loudness Meters: set different default colors for Range and True Pea | 为范围和真峰值设置不同的默认颜色 |

### 维护评价

- **活跃维护**：2026 年 5 月仍有密集的功能更新和 bug 修复，说明该插件处于活跃开发状态
- 插件从 2020 年末创建，最初为实验性项目，已稳定成长为成熟模块
- 近期更新集中在响度计量器的功能完善（最大值指示、削波绘制、颜色区分），表明 Epic 正在打磨音频分析可视化体验
- `Installed: false` 表示需要手动启用，适用于有音频 UI 需求的项目
- 推荐用于需要专业音频计量 UI 的场景

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AudioWidgets)
- 依赖插件：[AudioSynesthesia](../AudioSynesthesia/)