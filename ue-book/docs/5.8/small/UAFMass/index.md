# UAF Mass

> Mass integration for UAF.

| 属性 | 值 |
|---|---|
| 中文名 | UAF 大规模实体集成 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UAFMass` (Runtime), `UAFMassTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-11-10 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFMass) | |

## 用途

此插件为 Unreal Animation Framework (UAF) 提供了与 Mass 大规模实体系统的集成支持。它解决了在使用 Mass 框架处理海量实体时，如何高效地进行动画驱动和更新的问题。通过定义特定的 Mass Fragment 和 Processor，该插件为 UAF 的动画更新流水线与 Mass 的批量数据处理架构之间建立了桥接，使得动画系统能够利用 Mass 的高效批处理能力来驱动大量角色的动画。

## 使用场景

-   当你的项目需要驱动成百上千个 NPC 或角色的动画，并且已经使用 Mass 框架来管理这些实体时，需要通过此插件将动画更新集成到 Mass 的处理流程中。
-   你需要为基于 Mass 的大规模人群模拟或战斗场景中的实体提供支持 UAF 的动画表现。

## 模块列表

-   **`UAFMass`** (Runtime): 核心模块，包含将 UAF 动画更新逻辑与 Mass 实体处理器和观察器集成的主要类、Fragment 和 Processor。
-   **`UAFMassTests`** (Runtime): 测试模块，包含针对 UAFMass 模块核心功能的自动化测试用例。

## 核心功能

此插件主要通过定义和实现 Mass 系统所需的组件来扩展 UAF：

-   **Trajectory Bridge**: 最新的重构将轨迹计算桥接功能集成到插件中，为 Mass 实体提供运动预测和轨迹管理。
-   **Mass Processing Integration**: 定义了动画相关的 Mass Fragment (如动画状态数据)，并实现了在 Mass 处理阶段 (Processing Phase) 中执行动画更新逻辑的 Processor。
-   **事件依赖**: 提供了在 UAF 中设置 Mass 处理阶段事件依赖的选项，确保动画更新在正确的时机执行。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-23 | `746b6abb` | Move UAF-Mass trajectory bridge into engine UAFMass plugin | 将 UAF 与 Mass 的轨迹桥接功能正式移入此插件 |
| 2026-04-01 | `58888966` | [MassCore] Move headers to Public/Mass/ subdirectory, strip Mass prefix from filenames | 配合 MassCore 模块重构，调整头文件路径 |
| 2026-03-30 | `161605b0` | [Mass] Extract MassCore module from MassEntity | 配合 Mass 架构调整，更新依赖关系 |
| 2026-03-11 | `1d291fa1` | [Mass] Multi-fragment observer support in UMassObserverProcessor | 利用 Mass 框架新特性，增强动画观察处理器的灵活性 |
| 2026-02-17 | `baf983b4` | [SubmitTool - UAF] Add validators to build and run LowLevelTests for UAF plugins | 为插件添加自动化测试提交验证 |

### 维护评价

该插件于 2025 年 11 月创建，最近一次实质性更新在 2026 年 4 月，表明它仍在被**积极维护和开发**中。近期的提交记录显示，插件的功能在不断完善（如轨迹桥接），并紧跟底层 Mass 框架的架构演进进行适配。同时，添加了测试验证，提升了代码质量。由于其标记为实验性 (`IsExperimentalVersion=true`) 且默认禁用，表明其 API 和功能可能尚未稳定，适合用于技术预研和原型开发。**推荐**在需要 UAF 与 Mass 集成的实验性项目中使用。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFMass)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFMass/Tests)