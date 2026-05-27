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
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosCloth) | |

## 用途

Chaos Cloth 是 UE5 基于 Chaos 物理引擎的布料模拟系统。它取代了旧版的 NvCloth 实现，提供了更现代化、与 Chaos 引擎深度集成的布料模拟方案。该插件支持布料组件（ChaosClothComponent）的运行时物理模拟，以及编辑器中的布料资产编辑器（ChaosClothEditor），允许美术和开发者在编辑器中配置布料材质参数、碰撞、约束等属性。

该插件从 Experimental 阶段正式迁移到稳定版，同时将原先独立的 Chaos Cloth Editor 插件合并到本插件中，简化了依赖关系。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| [`ChaosCloth`](ChaosCloth.md) | Runtime | 布料物理模拟核心模块，包含布料组件、材质、约束、求解器等运行时逻辑 |
| [`ChaosClothEditor`](ChaosClothEditor.md) | Editor | 布料编辑器模块，提供编辑器内布料资产的可视化编辑和配置界面 |

## 使用场景

- 你正在制作角色服装、旗帜、窗帘等需要实时布料物理效果的项目 → 使用 ChaosCloth
- 你需要在编辑器中可视化配置布料材质参数（拉伸、弯曲、阻尼等）→ 使用 ChaosClothEditor 模块
- 你的项目需要布料与水体、浮力系统交互（依赖 Water 和 Buoyancy 插件）→ ChaosCloth 已内置支持
- 你从旧版 NvCloth 布料系统迁移 → ChaosCloth 是官方推荐的替代方案

## 模块依赖

本插件依赖以下其他插件：

| 插件 | 用途 |
|---|---|
| `ChaosCaching` | Chaos 物理缓存系统，布料模拟结果的缓存支持 |
| `Buoyancy` | 浮力模拟，支持布料与浮力体交互 |
| `Water` | 水体系统，支持布料与水体的交互模拟 |

无特殊模块依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点的编译警告 |
| 2026-04-23 | `85f3a947` | [Chaos Cloth] Clamp SolverLOD in ChaosClothingSimulationSolver to prevent out of bound crash when so | 限制求解器 LOD 值范围，防止越界崩溃 |
| 2026-04-21 | `9322be91` | Minor cloth debug draw improvements: | 布料调试绘制功能小幅改进 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移至 UE_LOGF 新日志宏 |
| 2026-03-31 | `0d36bcd0` | Chaos Cloth : | 布料相关改动（commit message 不完整） |

### 维护评价

- **状态**：活跃维护中
- 最近更新频繁（2026 年 3-5 月持续有提交），涵盖 bug 修复、崩溃防护、代码质量改进
- 2024 年 3 月从 Experimental 迁移到正式版，表明 Epic 认为该系统已达到生产就绪状态
- 仍在持续修复问题和改进，整体质量在稳步提升
- **推荐使用**：✅ 作为 UE5 官方布料方案，推荐在新项目中使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosCloth)
- 官方文档：暂无
- [ChaosCloth 模块文档](ChaosCloth.md)
- [ChaosClothEditor 模块文档](ChaosClothEditor.md)