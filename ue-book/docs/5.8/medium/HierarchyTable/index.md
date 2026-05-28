# Hierarchy Table

> 

| 属性 | 值 |
|---|---|
| 中文名 | 层级表 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（数据资产） |
| 模块 | `HierarchyTableRuntime` (Runtime), `HierarchyTableEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-07-30 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/HierarchyTable) | |

## 用途

HierarchyTable 提供一种**表格化的层级数据存储结构**，用于将树状层级关系（如骨骼层级、Blend Profile 等）以扁平表格的形式存储和编辑。核心场景是动画系统中的**混合配置管理**——例如为不同骨骼分支设置独立的 Blend Mask 权重，并支持在运行时动态更新。

该插件解决的关键问题：动画混合配置（Blend Profile / Blend Mask）通常需要按骨骼层级结构逐节点设置参数，HierarchyTable 将这种层级数据以可编辑表格的形式暴露给工具链，方便批量管理和可视化。

## 模块列表

| 模块 | 说明 |
|---|---|
| [HierarchyTableRuntime](HierarchyTableRuntime.md) | 运行时模块，提供层级表数据结构、资产类型和核心读写接口 |
| [HierarchyTableEditor](HierarchyTableEditor.md) | 编辑器工具模块，提供层级表的自定义资产编辑器、表格视图和属性自定义界面 |

## 使用场景

- 你需要为动画蓝图中的 **Profile Blend 节点** 配置分骨骼的混合权重 → 用 HierarchyTable 存储 Blend Mask
- 你需要**可视化编辑**骨骼层级上的逐节点属性（如物理权重、LOD 权重等） → 用 HierarchyTableEditor 的表格视图
- 你需要在运行时**动态更新**混合权重（如基于游戏状态的渐进混合） → 通过 Runtime 模块的 API 读写层级表数据

## 蓝图用法

蓝图 API 以数据资产读取为主，具体函数详见各子模块文档。

## C++ 用法

C++ API 详见各子模块文档，核心用法围绕层级表数据结构的创建、遍历和资产序列化。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AnimGraphRuntime` | 动画图运行时支持（Profile Blend 节点集成） |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `c19c7e83` | [ContentBrowser] New Add Menu Misc Menu | 内容浏览器新增菜单分类调整 |
| 2026-03-18 | `50b37fba` | [iOS/macOS] Fixes for Clang 21 implicit conversion warnings. | 修复 Clang 21 隐式转换警告 |
| 2026-03-04 | `d9a06590` | Update UAF blend profiles | 更新 UAF 混合配置数据 |
| 2025-11-06 | `e75a5dce` | Move hierarchy table from animation category to misc. | 将层级表资产类别从 Animation 迁移至 Misc |
| 2025-09-08 | `7c9e306e` | Add live updating blend mask weights in the Profile Blend node | Profile Blend 节点支持实时更新混合权重 |

### 维护评价

- **活跃维护**：2026 年 4 月仍有功能性更新和编译修复，持续迭代中
- **实验性状态**：`IsExperimentalVersion=true`，尚未正式发布，API 可能变动
- **近期趋势**：功能持续完善（实时混合权重更新、分类整理），属于动画系统核心工具链的一部分
- **推荐程度**：如果你的项目需要自定义混合配置，可以关注；正式生产环境建议等待移除实验性标记

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/HierarchyTable)
- [Runtime 模块文档](HierarchyTableRuntime.md)
- [Editor 模块文档](HierarchyTableEditor.md)