# UAF State Tree

> StateTree integration for UAF.

| 属性 | 值 |
|---|---|
| 中文名 | UAF状态树集成 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UAFStateTree` (Runtime), `UAFStateTreeEditor` (Runtime), `UAFStateTreeUncookedOnly` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-07-30 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFStateTree) | |

## 总体用途

UAF State Tree 插件将 Unreal 的 StateTree 状态树系统与 UAF（Unreal Animation Framework / 用户动画框架？）集成，使 UAF 的动画逻辑可以通过 StateTree 进行声明式设计和管理。插件提供运行时执行、编辑器编辑以及未烘焙场景下的支持，允许开发者利用 StateTree 的灵活性和可视化能力来驱动 UAF 动画控制流程。

## 模块列表

| 模块 | 类型 | 一句话说明 |
|---|---|---|
| `UAFStateTree` | Runtime | 核心运行时模块，负责 StateTree 任务的执行、变量读写与回调传播。 |
| `UAFStateTreeEditor` | Editor | 编辑器集成模块，提供 UAF 状态树节点的细节面板、自动完成和图形时间线支持。 |
| `UAFStateTreeUncookedOnly` | UncookedOnly | 未烘焙场景下的处理模块，处理状态树选择和 IUpdate 传播等编译时逻辑。 |

详细 API 请参阅各模块文档：
- [UAFStateTree 模块文档](UAFStateTree.md)
- [UAFStateTreeEditor 模块文档](UAFStateTreeEditor.md)
- [UAFStateTreeUncookedOnly 模块文档](UAFStateTreeUncookedOnly.md)

## 使用场景

- **动画状态树**：当你需要为 UAF 动画系统设计复杂的条件驱动行为，但又不愿意编写大量 C++ 或蓝图逻辑时，可以使用 StateTree 的可视化编辑器来编排状态转换与任务。
- **动画变量读写**：利用 StateTree 的变量系统在动画节点间传递数据，并结合 UAF 的回调机制实现响应式动画更新。
- **编辑器效率提升**：提供自动完成和图形时间线，方便开发者在 UAF 上下文中快速创建和调试 StateTree 任务。

## 维护状态

该插件创建于 2025-07-30，属于全新的实验性插件。近期提交包括修复回调泄漏、添加 IUpdate 传播、自动完成等功能，更新频率较高，处于活跃开发阶段。但由于仍标注为实验性（`IsExperimentalVersion=true`），不推荐用于生产环境，仅适合评估或预研用途。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFStateTree)