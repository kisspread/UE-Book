# ControlRigPhysics

> Support for physics simulation in control rig

| 属性 | 值 |
|---|---|
| 中文名 | 控制绑定物理 |
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `ControlRigPhysics` (Runtime), `ControlRigPhysicsEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-20 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ControlRigPhysics) | |

## 用途

ControlRigPhysics 为 Control Rig 系统引入了**运行时物理模拟能力**。它基于 PhysicsControl 插件，在 Control Rig 的求解器管线中嵌入物理碰撞检测与响应，让动画师能够在动画蓝图（Control Rig Graph）中直接驱动刚体碰撞、约束等物理行为，而无需在 Gameplay 层面额外编写物理逻辑。

该插件最初作为 PhysicsControl 的一部分存在，后独立出来成为单独插件（首个 commit 即为此次拆分）。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| [ControlRigPhysics](ControlRigPhysics.md) | Runtime | 核心运行时模块：物理碰撞节点、求解器集成、蓝图 API |
| [ControlRigPhysicsEditor](ControlRigPhysicsEditor.md) | Editor | 编辑器模块：Control Rig 图表中的物理节点自定义面板与属性细节定制 |

## 使用场景

- 你在 Control Rig 中为角色添加布料/绳索等需要物理碰撞的动画效果 → 用 ControlRigPhysics
- 你希望在动画蓝图阶段就能预览物理碰撞结果，而不是等到 Gameplay 运行时 → 用 ControlRigPhysics
- 你已经在使用 PhysicsControl 做 Gameplay 物理驱动，想在 Control Rig 管线中复用类似能力 → 用 ControlRigPhysics

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ControlRig` | Control Rig 动画系统核心 |
| `PhysicsControl` | 物理控制基础设施（碰撞检测、约束求解） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `0fc3e074` | Anim In Engine: Run CR physics collisions on game thread, if we are currently on the game thread. Th… | 修复游戏线程上的 Control Rig 物理碰撞执行问题 |
| 2026-05-26 | `81eec0eb` | Fix for missing control rig physics version - fixes assert on loading older control rigs that don't… | 修复加载旧版控制绑定时缺少物理版本号导致的断言失败 |
| 2026-05-14 | `c6a1ed72` | Control rig physics - Remove SolverSettings.WorldCollisionExpiryFrames as a value of 1 is the only… | 移除 `WorldCollisionExpiryFrames` 设置项，固定为唯一有效值 1 |
| 2026-05-14 | `15fdc3a0` | Control rig physics - more uses of the cached components | 扩大缓存组件的使用范围，提升性能 |
| 2026-05-14 | `c48042d4` | Control rig physics - use caching. Very simple change mirroring what we do in Control Rig Dynamics… | 引入组件缓存机制，与 Control Rig Dynamics 保持一致 |

### 维护评价

- **创建时间**：2025-06-20，插件非常年轻（约 1 年）
- **活跃程度**：近一个月内有多次功能性更新与性能优化，**活跃维护中**
- **状态标记**：`IsBetaVersion=true`，仍处于 Beta 阶段；位于 `Experimental` 目录
- **推荐程度**：适合早期采用者和实验性项目；生产环境使用需关注 API 变动风险（已有版本兼容修复）

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ControlRigPhysics)
- [Control Rig 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/ControlRig)
- [PhysicsControl 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PhysicsControl)