# PhysicsControl

> Physically control static and skeletal meshes through the Physics Control Component and the Rigid Body With Control animation graph node.

| 属性 | 值 |
|---|---|
| 中文名 | 物理控制 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资源） |
| 模块 | `PhysicsControl` (Runtime), `PhysicsControlUncookedOnly` (UncookedOnly), `PhysicsControlEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-23 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PhysicsControl) | |

## 总体用途

PhysicsControl 插件提供了一套完整的物理控制解决方案，用于通过 **Physics Control Component** 和 **Rigid Body With Control** 动画图节点，对静态网格体（Static Mesh）和骨骼网格体（Skeletal Mesh）进行直接物理驱动。它允许开发者精确控制刚体的位置、旋转、速度以及施加的力，从而实现程序化动画、物理交互、混合动画与物理效果（例如布娃娃、基于物理的武器摆动、角色肢体的动态响应等）。该插件弥补了标准物理约束系统在动画管线中难以灵活集成的缺陷，为需要精细物理控制的游戏机制提供了模块化的数据驱动框架。

## 模块列表

| 模块 | 一句话总结 | 详细文档 |
|---|---|---|
| `PhysicsControl` (Runtime) | 核心运行时模块，提供所有物理控制逻辑、数据结构以及用于在 C++/蓝图中调用的主要 API。 | [PhysicsControl.md](PhysicsControl.md) |
| `PhysicsControlEditor` (Editor) | 编辑器模块，提供自定义 Details 面板、Control 预设编辑器和可视化调试工具。 | [PhysicsControlEditor.md](PhysicsControlEditor.md) |
| `PhysicsControlUncookedOnly` (UncookedOnly) | 仅在未打包（编辑器/Cook）过程中使用的模块，包含数据验证、预计算和构建辅助功能。 | [PhysicsControlUncookedOnly.md](PhysicsControlUncookedOnly.md) |

## 使用场景

- **程序化物理动画** — 当需要让角色肢体完全由物理模拟驱动（如布娃娃、死亡动画）时，借助 Physics Control Component 可以精细调节每个刚体的阻尼、刚度、外力等参数，实现更自然的物理表现。
- **物理交互式游戏对象** — 例如门、铰链、可破坏的物体，通过配置控制参数来模拟真实的物理响应。
- **混合动画与物理** — 使用 Rigid Body With Control 动画图节点，将动画播放与物理控制混合，使角色在播放动画的同时受物理碰撞影响（如推开障碍物时手臂的偏移）。
- **测试与调试** — 开发者可在编辑器中实时调整物理控制参数，并观察刚性约束的变化，快速迭代物理效果。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PhysicsControl)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PhysicsControl/Tests)