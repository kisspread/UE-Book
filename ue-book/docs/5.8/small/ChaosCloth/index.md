# Chaos Cloth

> Adds Chaos Cloth modules.

| 属性 | 值 |
|---|---|
| 中文名 | 混沌布料 |
| 分类 | Physics |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ChaosCloth` (Runtime), `ChaosClothEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2024-03-22 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosCloth) | |

## 用途

ChaosCloth 是 Unreal Engine 的 Chaos 物理引擎驱动的布料模拟插件，为 Skeletal Mesh 组件提供基于物理的布料动画能力。它取代了旧的 NvCloth 方案，使用 Chaos 物理求解器进行布料碰撞、约束和动力学计算，支持自碰撞、布料与水体交互、浮力模拟等高级功能。该插件从 Experimental 状态毕业后，将原本独立的 ChaosClothEditor 模块合并进来，成为 UE5 布料模拟的标准方案。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| [ChaosCloth](ChaosCloth.md) | Runtime | 布料模拟核心运行时模块，包含求解器、碰撞检测、约束系统及与 SkeletalMeshComponent 的集成 |
| [ChaosClothEditor](ChaosClothEditor.md) | Editor | 编辑器扩展模块，提供布料属性编辑器 UI、资产查看器及编辑器内预览支持 |

## 使用场景

- 你需要为角色服装、旗帜、窗帘等添加物理布料动画 → 使用 ChaosCloth 的 ClothAsset 和 ClothComponent
- 你需要模拟布料与水面的交互（如船帆、浮在水面上的布料）→ ChaosCloth 依赖 Water 和 Buoyancy 插件提供水体交互
- 你需要在编辑器中可视化调整布料权重和约束参数 → 使用 ChaosClothEditor 的编辑器工具
- 你需要支持 LOD 级别的布料模拟优化 → ChaosCloth 内置 SolverLOD 机制自动降低远处布料精度

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Chaos` | Chaos 物理引擎核心，提供物理求解器和碰撞框架 |
| `ChaosCaching` | Chaos 物理缓存系统，支持布料模拟结果的缓存与回放 |
| `ClothSolver` | 布料求解器基础设施 |
| `ClothSimData` | 布料模拟数据结构和管理 |
| `Water` | 水体系统，支持布料与水面交互 |
| `Buoyancy` | 浮力系统，支持布料在水中的浮力模拟 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-04-23 | `85f3a947` | [Chaos Cloth] Clamp SolverLOD in ChaosClothingSimulationSolver to prevent out of bound crash when so | 钳制 SolverLOD 值防止越界崩溃 |
| 2026-04-21 | `9322be91` | Minor cloth debug draw improvements: | 布料调试绘制的小幅改进 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新格式 UE_LOGF |
| 2026-03-31 | `0d36bcd0` | Chaos Cloth : | Chaos Cloth 相关改动 |

### 维护评价

✅ **活跃维护中**

该插件自 2024 年 3 月从 Experimental 毕业以来持续获得更新，最近数月内有多次实质性改进，包括 Bug 修复（越界崩溃）、代码质量提升（编译警告修复、日志宏迁移）和功能改进（调试绘制优化）。作为 UE5 官方布料模拟的标准方案，由 Epic Games 核心物理团队维护，推荐在生产项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosCloth)
- [ChaosCloth 模块文档](ChaosCloth.md)
- [ChaosClothEditor 模块文档](ChaosClothEditor.md)