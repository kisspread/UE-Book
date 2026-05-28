# Legacy Composure

> Legacy system for real-time compositing. This plugin is no longer developed. Use Composure going forward.

| 属性 | 值 |
|---|---|
| 中文名 | 合成器插件 |
| 分类 | Compositing |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `Composure` (Runtime), `ComposureEditor` (Runtime), `ComposureLayersEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-06-27 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Compositing/Composure) | |

## 用途

Composure 是一个为虚幻引擎设计的**实时合成系统**。它提供了一套工具和框架，允许开发者在引擎内直接进行图层化的、可编程的合成操作，常用于**虚拟制片**、**实时视觉特效**和**后期制作流程**。该系统支持将 3D 渲染层、实时视频源、材质效果等进行复杂混合与处理。

**重要提示**：根据 `.uplugin` 描述，此插件已是**遗留版本**，Epic Games 已停止对其开发，并建议使用名为“Composure”的新系统。本文档基于此遗留系统代码。

## 使用场景

- **虚拟制片/绿幕抠像**：将演员实时拍摄的视频（通过色键技术）与 3D 虚拟场景无缝合成。
- **实时后期效果**：在引擎内对最终画面进行多层的颜色校正、光晕、景深等后期效果处理，无需导出到其他软件。
- **动态 UI 与广告合成**：将游戏或应用内的 UI 元素与 3D 世界进行动态合成。
- **广播与直播图形**：为实时广播、体育直播等场景叠加图形、数据可视化层。

## 模块列表

| 模块 | 类型 | 简述 |
|---|---|---|
| `Composure` | Runtime | 插件的核心运行时逻辑，包含合成图层、输入输出、后处理通道等基础架构。 |
| `ComposureEditor` | Runtime | 提供编辑器内的 UI、自定义资产编辑器和工作流，用于配置和预览合成项目。 |
| `ComposureLayersEditor` | Runtime | 提供用于管理和编辑合成图层（Compositing Elements）的专门编辑器界面。 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Compositing/Composure)

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口相关通用代码重构。 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回退了之前的提交 CL53913857。 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口相关通用代码重构。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移到新的 UE_LOGF 格式。 |
| 2026-04-13 | `efbf4c0b` | Viewport: Use managed pointer for reference to Client | 视口中对 Client 的引用改用智能指针。 |

### 维护评价

**综合评价：已废弃，不推荐用于新项目。**

此插件是一个**遗留系统**，官方已明确声明不再开发，并建议使用新版“Composure”。其最后一次功能性更新远在多年以前。近期的提交均为针对整个引擎的通用代码维护（如日志宏迁移、智能指针替换），与该插件的功能增强或缺陷修复无关。

**结论**：如果您是新的项目或正在评估合成方案，**强烈建议**寻找并使用官方推荐的“Composure”新系统，而非此遗留版本。对于维护旧有项目的团队，可以继续使用，但需意识到不会再有功能更新或官方支持。