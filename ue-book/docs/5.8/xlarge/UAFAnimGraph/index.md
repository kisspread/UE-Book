# UAF Anim Graph

> Framework for defining animation graphs.

| 属性 | 值 |
|---|---|
| 中文名 | UAF动画图表 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画图表资产、蓝图） |
| 模块 | `UAFAnimGraph` (Runtime), `UAFAnimGraphEditor` (Editor), `UAFAnimGraphUncookedOnly` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-26 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFAnimGraph) | |

## 用途

UAFAnimGraph 是 UAF（Unified Animation Framework）框架的动画图表子系统，提供用于定义动画图表的基础设施。该插件是 Epic 从早期 AnimNextAnimGraph 重命名迁移而来，属于 UE5 新一代动画系统的实验性组件。

该插件解决的核心问题：提供一套基于 RigVM 的动画图表定义框架，让开发者能够以节点图方式构建复杂的动画逻辑，支持动画混合、状态机、动画蒙太奇等高级动画功能。它取代了传统 AnimGraph 的部分职责，与 UAF 框架深度集成。

## 使用场景

- 你需要构建复杂的程序化动画逻辑 → 使用 UAFAnimGraph 节点图系统
- 你在开发需要高级动画混合的角色系统 → 集成 UAFAnimGraph 的动画蒙太奇和混合层功能
- 你希望将动画逻辑可视化、可调试 → 使用 UAFAnimGraphEditor 的图表编辑器
- 你正在使用 UAF 框架进行动画开发 → 这是 UAF 的图表子系统，必须配合使用

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `UAFAnimGraph` | Runtime | 核心运行时模块，提供动画图表的底层数据结构、求值器和运行时执行逻辑 |
| `UAFAnimGraphEditor` | Editor | 编辑器模块，提供动画图表的节点编辑器、调试工具和资产编辑界面 |
| `UAFAnimGraphUncookedOnly` | UncookedOnly | 仅未打包时使用的模块，负责图表的编译、优化和烘焙转换逻辑 |
| `UAFAnimGraphTests` | Runtime | 测试模块，包含自动化测试用例验证动画图表功能 |

## 插件依赖

| 插件 | 用途 |
|---|---|
| [UAF](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAF) | 统一动画框架主体，提供动画系统基础架构 |
| [RigVM](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/RigVM) | 虚拟机框架，为动画图表提供节点执行引擎 |

## 使用注意事项

⚠️ **实验性插件**：此插件标记为 `IsExperimentalVersion=true` 且 `EnabledByDefault=false`，需要手动在项目设置中启用。API 可能随版本发生重大变更，不建议在生产项目中使用。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `43658976` | Sequencer: Anim Mixer: Fix crash when scrubbing a level sequence after changing a Mix Layer transiti | 修复动画混合器在切换混合层后拖动时间轴崩溃的问题 |
| 2026-05-12 | `61c7c092` | [UEMHC] - Fix Geometry Export crash and material issues on re-export | 修复几何体导出崩溃和重新导出时的材质问题 |
| 2026-05-12 | `14c22336` | UAF: Add tick order dependecy between the UAF Montage Tick and CMC Tick to ensure the movement compo | 添加 UAF 蒙太奇 Tick 与角色移动组件的执行顺序依赖 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式化说明符不匹配问题 |
| 2026-04-22 | `287203b9` | UE 5.8 Animation deprecation clean up (CL 9/10): UAF | UE 5.8 动画系统废弃 API 清理 |

### 维护评价

UAFAnimGraph 处于**活跃维护**状态。最近更新集中在 2026 年 4-5 月，持续进行 bug 修复和 API 整理工作。作为 UAF 框架的核心组件，Epic 正在积极开发迭代。但该插件仍为实验性，建议关注后续版本更新，谨慎在正式项目中采用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFAnimGraph)
- [UAF 主框架](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAF)
- [RigVM 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/RigVM)