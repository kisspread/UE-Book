# Variant Manager Content

> Data classes and assets for the Variant Manager plugin

| 属性 | 值 |
|---|---|
| 中文名 | 变体管理内容 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `VariantManagerContent` (Runtime), `VariantManagerContentEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-09-04 |
| 年龄标签 | 🏛️ 文物（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/VariantManagerContent) | |

## 用途

VariantManagerContent 为 Variant Manager（变体管理器）插件提供**数据模型和核心类**。变体管理器是 Datasmith 工作流中的关键组件，用于管理和切换产品的不同配置状态。

**解决的问题**：在工业可视化、建筑可视化、产品展示等场景中，同一个 3D 模型可能有多种变体（颜色、材质、部件组合等）。该插件提供底层数据结构，让 Variant Manager 能够：
- 定义变体集（Variant Sets）和变体（Variants）
- 管理变体之间的属性差异（材质、变换、可见性等）
- 在运行时和编辑器中切换不同的产品配置

## 使用场景

- 你在做**产品配置器**（如汽车、家具的在线定制）→ 使用 Variant Manager 切换不同配置
- 你需要在**建筑可视化**中快速切换装修方案 → 用变体管理器管理不同设计
- 你导入了 **Datasmith** 场景需要管理多种展示状态 → 此插件提供底层数据支持
- 你需要在运行时通过蓝图切换场景中物体的属性组合 → 通过变体系统实现

## 模块说明

| 模块 | 类型 | 说明 |
|---|---|---|
| [VariantManagerContent](VariantManagerContent.md) | Runtime | 核心数据类：变体、变体集、变体绑定等运行时数据结构 |
| [VariantManagerContentEditor](VariantManagerContentEditor.md) | Editor | 编辑器扩展：变体管理器 UI 面板、资产编辑器、蓝图节点注册 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/VariantManagerContent)
- [官方文档（Datasmith）](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)