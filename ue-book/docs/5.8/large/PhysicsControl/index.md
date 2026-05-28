# PhysicsControl

> Physically control static and skeletal meshes through the Physics Control Component and the Rigid Body With Control animation graph node.

| 属性 | 值 |
|---|---|
| 中文名 | 物理控制 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、动画图表节点） |
| 模块 | `PhysicsControl` (Runtime), `PhysicsControlUncookedOnly` (UncookedOnly), `PhysicsControlEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2026-05-12 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/PhysicsControl) | |

## 用途

PhysicsControl 提供了一套基于物理的角色/物体控制系统。它通过 **PhysicsControlComponent**（运行时组件）和 **Rigid Body With Control**（动画图表节点）让你能够用物理力驱动骨骼网格体和静态网格体的运动，而非纯粹依赖动画关键帧。

核心解决的问题：**物理模拟与动画控制的混合**。在需要角色受物理力影响但仍保持一定动画姿态的场景（如布娃娃、物理交互、冲击反应）中，传统方案需要在物理模拟和动画之间手动切换，而 PhysicsControl 提供了内置的控制力（control forces）机制，让物理体在模拟过程中"趋向"目标动画姿态，实现平滑的物理-动画融合。

该插件刚刚从 **Experimental** 迁移至正式目录，标志着 Epic 认为其已具备生产可用性。

## 使用场景

- 你正在做需要 **布娃娃物理** 的游戏，但希望角色在受击后能自然地"恢复"到站立动画 → 用 PhysicsControlComponent 驱动骨骼恢复
- 你需要角色在 **物理模拟状态下** 仍保持部分动画姿态（如攀爬时四肢受物理影响） → 用 Rigid Body With Control 节点
- 你需要 **精确控制** 物理体之间的碰撞启停（如抓取物体时禁用手部与物体的碰撞） → 用 Enable/DisableCollisionBetweenBodies
- 你需要对多个物理体施加 **力/加速度模式** 的控制 → 用 acceleration/force mode 切换
- 你通过 **Control Rig** 进行物理动画，需要额外的物理控制能力 → PhysicsControl 与 Control Rig 协同使用

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| [PhysicsControl](PhysicsControl.md) | Runtime | 核心运行时模块：PhysicsControlComponent、PhysicsControlData、骨骼/静态网格体物理控制逻辑 |
| [PhysicsControlUncookedOnly](PhysicsControlUncookedOnly.md) | UncookedOnly | 动画图表节点（Rigid Body With Control），仅编辑器/未打包时可用 |
| [PhysicsControlEditor](PhysicsControlEditor.md) | Editor | 编辑器扩展：自定义细节面板、资产编辑器等编辑器端支持 |

## 蓝图核心节点

详见各子模块文档。核心功能概览：

| 节点 | 说明 | 所在类/模块 |
|---|---|---|
| `EnableCollisionBetweenBodies` / `DisableCollisionBetweenBodies` | 启用/禁用指定 Body 之间的碰撞 | `PhysicsControl` |
| `SetControlMultiplier` / `SetControlMultiplierArray` | 设置物理控制乘数（力/加速度） | `PhysicsControl` |
| `SetControlTarget` / `SetControlTargetArray` | 设置物理控制目标姿态 | `PhysicsControl` |
| 力/加速度模式切换 | 在 force 和 acceleration 模式间切换 | `PhysicsControl` |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-21 | `6df5417c` | PhysicsControl: Clamp skeletal animation drive targets to joint limits to prevent spurious forces an | 骨骼动画驱动目标值钳制到关节限制范围内，防止异常力产生 |
| 2026-05-14 | `99441775` | Physics Control - Fix for Enable/DiableDisableCollisionBetweenBody when called on the same frame as | 修复同帧调用 Enable/DisableCollisionBetweenBody 的问题 |
| 2026-05-13 | `78406e38` | Control rig physics and Physics Control - clamp strength so that value < 0 don't cause unwanted beha | 钳制 strength 值，防止负值导致异常行为 |
| 2026-05-12 | `d5ffc351` | Add simple array versions of the Blueprint Enable/DisableCollisionBetweenBodies in PhysicsControl | 新增 Blueprint 数组版本的碰撞启停函数 |
| 2026-05-12 | `647e07c7` | Add support for acceleration/force mode (a simple toggle) in physics control - control rig physics, | 新增加速度/力模式切换支持 |

### 维护评价

PhysicsControl 是一个 **全新上线** 的插件（2026-05-12 从 Experimental 迁移），目前处于**积极维护期**。

- 🟢 **活跃开发**：创建后短短 9 天内已有 5 次提交，包含 bug 修复和功能新增
- 🟢 **Epic 官方维护**：由 Epic Games 直接开发和维护
- 🟢 **刚脱离实验阶段**：已通过内部 review（首次提交提到 "minor changes from review"），具备生产可用性
- ⚠️ **注意**：作为新迁出 Experimental 的插件，API 可能在后续版本中仍有调整

**推荐使用**：如果你需要物理-动画混合控制，推荐使用此插件替代自行实现。作为 Epic 官方方案，它与 Control Rig 和动画系统有深度集成。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/PhysicsControl)
- [PhysicsControl 运行时模块](PhysicsControl.md)
- [PhysicsControlUncookedOnly 动画图表模块](PhysicsControlUncookedOnly.md)
- [PhysicsControlEditor 编辑器模块](PhysicsControlEditor.md)