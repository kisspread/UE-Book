# Variant Manager Content

> Data classes and assets for the Variant Manager plugin

| 属性 | 值 |
|---|---|
| 中文名 | 变体管理器内容 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `VariantManagerContent` (Runtime), `VariantManagerContentEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-09-04 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/VariantManagerContent) | |

## 用途

此插件为 Variant Manager 插件提供核心的数据结构和资产类型。它定义了 `ULevelVariantSets`，`UVariant` 和 `UVariantSet` 等关键类，这些类是存储和管理产品变体配置（如材质、几何体、可见性等）的基础。其主要作用是为基于 Datasmith 的建筑、工程和施工（AEC）以及制造工作流提供一个标准化、可管理的产品配置数据存储层，使设计师和工程师能够在 UE 中快速切换和展示不同的设计或产品方案。

## 使用场景

- **建筑可视化与产品展示**：你从 Revit 或其他 CAD/BIM 软件通过 Datasmith 导入了整个建筑或产品模型，并希望通过一键点击来展示不同的材质方案、家具布局或设备型号。
- **产品配置器**：你为汽车、家具或工业设备创建了一个交互式的产品配置器，客户可以实时切换颜色、内饰或可选配件。
- **设计评审**：你正在向客户演示一个建筑项目的不同设计阶段或多个设计方案（如外观A vs 外观B），需要一个干净、可维护的方式来保存和切换这些状态。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `VariantManagerContent` | Runtime | 定义并序列化核心数据结构（`ULevelVariantSets`, `UVariantSet`, `UVariant`），是资产存储和运行时读取的基础。 |
| `VariantManagerContentEditor` | Editor | 处理这些数据资产在编辑器中的创建、编辑和UI集成，支持从Datasmith场景创建变体集等功能。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `0a77223b` | Fixed crash in LevelVariantSet.cpp | 修复了 `LevelVariantSet.cpp` 中的一个崩溃问题。 |
| 2026-04-16 | `0b4d09a4` | [ContentBrowser] New Add Menu Data Menu | （相关提交）内容浏览器新增了“添加”菜单的数据选项。 |
| 2026-04-14 | `50042443` | TLazyObjectPtr Deprecation: | 处理了 `TLazyObjectPtr` 的废弃标记。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移至 `UE_LOGF`。 |
| 2026-03-20 | `c5bb9adf` | [AutoViz] Minor updates to Variant Manager | （自动可视化）对变体管理器进行了小更新。 |

### 维护评价

插件仍在**活跃维护**中。最近几个月有多次更新，包括重要的崩溃修复（`0a77223b`）和与编辑器新特性的同步（`0b4d09a4`）。其核心功能（基于Datasmith的变体管理）是 Epic Games 企业解决方案（如 Twinmotion）的关键部分，因此长期维护有保障。尽管插件标记为实验性（`IsBetaVersion=true`），但鉴于其持续更新和重要性，可以认为是一个成熟、可靠的组件。**推荐使用**，特别是在 AEC/制造领域的可视化项目中。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/VariantManagerContent)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/VariantManagerContent/Tests)