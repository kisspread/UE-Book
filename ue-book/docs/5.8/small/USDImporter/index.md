# USD Importer

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | USD 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质、动画等） |
| 模块 | `GeometryCacheUSD` (Runtime), `USDClassesEditor` (Runtime), `USDExporter` (Runtime), `USDSchemas` (Runtime), `USDStage` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDStageImporter` (Runtime), `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter) | |

## 用途

本插件为 Unreal Engine 提供了对 Pixar USD (Universal Scene Description) 文件格式的完整导入支持。USD 是一种开放、可扩展的文件格式，广泛用于影视、动画和游戏行业，用于交换和协作复杂的 3D 场景数据。本插件允许开发者将 USD 文件（包括几何体、材质、动画、场景层级等）直接导入到 UE 中，并提供了在编辑器内预览、编辑和进一步处理 USD 数据的工具。它解决了 UE 原生不支持 USD 格式的问题，实现了与使用 USD 工作流程（如 Maya、Houdini、Nuke 等）的资产管线的无缝对接。

## 使用场景

- 你需要将使用 Maya 或 Houdini 制作的、基于 USD 的复杂角色或场景资产导入到 UE 项目中。
- 你的美术团队使用 USD 作为主要的资产交换格式，你需要将 USD 资产集成到 UE 的实时渲染管线中。
- 你需要从 USD 文件导入包含复杂动画（如骨骼动画、变形动画）和材质的资产。
- 你需要在 UE 编辑器中实时预览和调整导入的 USD 资产的最终效果。

## 模块概述

| 模块 | 用途 |
|---|---|
| `GeometryCacheUSD` | 处理 USD 中的几何缓存（如布料模拟、粒子缓存）数据的导入。 |
| `USDClassesEditor` | 提供编辑器专用的 USD 类和数据类型，用于扩展编辑器功能。 |
| `USDExporter` | 提供将 UE 场景或资产导出为 USD 格式的能力。 |
| `USDSchemas` | 定义 UE 与 USD 之间的数据映射（Schema），是数据转换的核心。 |
| `USDStage` | 管理 USD Stage（场景描述）的加载、表示和基础操作。 |
| `USDStageEditor` | 提供在编辑器中查看和编辑 USD Stage 的 UI 面板和工具。 |
| `USDStageEditorViewModels` | 为 `USDStageEditor` 提供数据模型和视图模型支持。 |
| `USDStageImporter` | 实现将 USD Stage 数据（如网格、材质、动画）转换为 UE 资产的核心逻辑。 |
| `USDTests` | 包含针对 USD 插件功能的自动化测试用例。 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter)