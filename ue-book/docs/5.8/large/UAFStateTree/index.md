# UAF State Tree

> StateTree integration for UAF.

| 属性 | 值 |
|---|---|
| 中文名 | UAF状态树集成 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画资产、测试资源） |
| 模块 | `UAFStateTree` (Runtime), `UAFStateTreeEditor` (Runtime), `UAFStateTreeUncookedOnly` (Runtime), `UAFStateTreeTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFStateTree) | |

## 用途

这个插件为 **Universal Animation Framework (UAF)** 提供了与 **状态树 (State Tree)** 系统的集成。其核心价值在于将 UAF 的动画资产播放能力与 State Tree 的强大、可视化状态机管理能力相结合。这使得动画师或开发者能够使用 State Tree 编辑器来构建、管理和驱动复杂的 UAF 动画播放逻辑，而无需编写大量的蓝图或 C++ 状态切换代码。它解决了在复杂动画流程（如蒙太奇、多段动画、响应游戏事件）中，状态管理与动画播放逻辑分离和管理的难题。

## 使用场景

- **你的动画师需要直观地控制复杂的动画流程**：使用 State Tree 编辑器，以可视化的方式连接、配置和调试 UAF 动画资产的播放状态、过渡条件和事件响应。
- **项目已集成 UAF 框架，需要更灵活的状态机**：通过此插件，将现有的 UAF 动画资产作为状态树中的节点或任务，实现更高级的动画行为编排。
- **团队希望分离动画逻辑与游戏逻辑**：动画师在 State Tree 中负责动画状态的流转和表现，程序员通过事件和黑板值驱动状态树，实现关注点分离。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `UAFStateTree` | Runtime | 核心运行时模块，提供 UAF 与 State Tree 集成的核心逻辑、任务和模式。 |
| `UAFStateTreeEditor` | Runtime | 编辑器扩展模块，提供用于编辑 State Tree 的节点、自定义资产类型和编辑器工具。 |
| `UAFStateTreeUncookedOnly` | Runtime | 仅开发期模块，处理编辑器内和未打包构建状态下的资产转换和预览逻辑。 |
| `UAFStateTreeTests` | Runtime | 自动化测试模块，包含针对 UAF 与 State Tree 集成功能的测试用例。 |

## 文档导航

本文档为大型插件的汇总页。以下是各子模块的详细文档：

- [UAFStateTree.md](UAFStateTree.md)：运行时核心逻辑、公开的类与API。
- [UAFStateTreeEditor.md](UAFStateTreeEditor.md)：编辑器扩展、自定义节点与工具。
- [UAFStateTreeUncookedOnly.md](UAFStateTreeUncookedOnly.md)：未打包构建时的特殊逻辑。
- [UAFStateTreeTests.md](UAFStateTreeTests.md)：测试用例与验证示例。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移至新的统一格式。 |
| 2026-04-13 | `6f1ea925` | State Tree: Updated state tree reference struct details to show the display name of the struct rathe | 优化状态树引用结构体的显示名称，增强可读性。 |
| 2026-04-13 | `5078d880` | Add UAFSharedAssets plugin for content we want to provide that references UAF assets defined in sepa | 新增共享资产插件，用于管理跨模块引用的UAF资产。 |
| 2026-04-10 | `797a6da6` | Rename GetComponent to GetOrAddComponent to match functionality | 将组件获取函数重命名为`GetOrAddComponent`，更准确反映其功能。 |
| 2026-03-31 | `4e41a45f` | Fix crash attempting to manually create UAF ST by hiding UAF ST Schema | 修复了手动创建UAF状态树资产时可能导致的崩溃问题。 |

### 维护评价

- **状态**：**实验性**且**活跃维护**。
- **分析**：该插件于2025年6月创建，标记为实验性且默认未启用。从近期的Git历史看，在2026年3月至4月期间有多次实质性更新，包括功能优化（如函数重命名）、Bug修复和架构调整（新增共享资产插件），表明其处于积极的开发和迭代阶段。
- **建议**：由于其处于实验阶段且默认未启用，适合用于技术预览、原型开发或内部工具链集成。在生产环境中使用需要谨慎评估其稳定性和未来API变化的可能性。推荐对UAF和StateTree有集成需求的团队关注和试用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFStateTree)
- [官方文档]() （暂无）