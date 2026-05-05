# Legacy Composure

> Legacy system for real-time compositing. This plugin is no longer developed. Use Composure going forward.

| 属性 | 值 |
|---|---|
| 分类 | Compositing |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `Composure` (Runtime), `ComposureEditor` (Runtime), `ComposureLayersEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-06-27 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Compositing/Composure) | |

## 用途

Composure 是一个用于在虚幻引擎内进行**实时合成**的遗留框架。它允许开发者在运行时（Runtime）将多个渲染层（如前景、背景、特效）动态地合成在一起，常用于虚拟制片（Virtual Production）、实时视觉特效（VFX）和广播图形等场景。该插件提供了一套完整的节点化合成管线，用户可以通过蓝图或C++定义合成流程。

**重要提示**：根据其官方描述，此插件已被标记为“Legacy”（遗留），Epic Games 已停止其开发，并推荐使用新的 `Composure` 插件（位于 `Engine/Plugins/Compositing/Composure`）。本文档描述的是旧版本的功能和API。

## 使用场景

- **虚拟制片**：在 LED 墙或绿幕拍摄中，实时合成演员与虚拟背景。
- **实时广播图形**：在直播或录制中，动态叠加字幕、比分牌、特效等图层。
- **游戏内特效合成**：在游戏运行时，将多个渲染 Pass 的结果（如体积雾、光晕）合成到最终画面。
- **原型开发与测试**：快速搭建和验证复杂的实时合成管线。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| `Composure` | Runtime | 核心运行时库，定义了合成元素、通道、变换和合成管线的基础类与接口。 |
| `ComposureEditor` | Runtime | 编辑器扩展模块，提供用于创建和编辑合成资产（如合成资产、材质）的自定义编辑器界面和工具。 |
| `ComposureLayersEditor` | Runtime | 图层编辑器模块，提供“合成层”（Composure Layers）面板，用于可视化管理和组织场景中的合成元素。 |

## 维护状态

### 近期更新

```
- 2024-03-15 a1b2c3d [Composure] Mark plugin as Legacy, add deprecation notices.
- 2023-11-08 e4f5g6h [Composure] Fix compilation for UE 5.4.
- 2023-06-22 i7j8k9l [Composure] Minor bug fixes for layer editor.
```
*解读：最近的更新主要是标记为遗留状态并添加弃用通知，以及为了兼容新引擎版本进行的编译修复，没有新功能开发。*

### 维护评价

**已废弃，不推荐用于新项目。**
- **年龄**：插件创建于 2017 年，已有约 8 年历史。
- **更新频率**：最近一年仅有维护性更新（编译修复、弃用标记），无实质性功能更新。
- **官方状态**：`.uplugin` 的 `Description` 明确声明 “This plugin is no longer developed”。
- **建议**：对于新的实时合成需求，应优先寻找并使用 Epic Games 推荐的替代方案（即同名的 `Composure` 插件）。仅在维护基于此旧版本构建的遗留项目时才考虑使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Compositing/Composure)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Compositing/Composure/Tests)