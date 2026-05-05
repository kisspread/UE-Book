# Chaos Rigid Physics Async

> Provides the Chaos Rigid Body Physics Engine (Async Implementation)

| 属性 | 值 |
|---|---|
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ChaosRigidPhysicsAsync` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-31 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosRigidPhysicsAsync) | |

## 用途

本插件是 Unreal Engine Chaos 物理引擎的一个**实验性异步实现**。它旨在将刚体物理模拟的计算任务从游戏线程（Game Thread）分离出来，放到独立的物理线程上执行。其核心目的是**提升游戏性能**，通过异步计算避免复杂的物理模拟阻塞游戏逻辑，从而维持更高的帧率和更流畅的游戏体验。它与引擎内置的同步 Chaos 物理系统并行存在，提供了一种性能优化的替代方案。

## 使用场景

- 你正在开发一个**物理对象数量庞大**或**物理交互复杂**的游戏（如大型开放世界、物理破坏模拟、大量载具），需要避免物理计算成为性能瓶颈。
- 你的项目对**帧率稳定性**要求极高，希望物理计算不会导致游戏线程卡顿。
- 你希望在**实验性功能**中测试和评估异步物理带来的性能收益与潜在的同步问题。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `ChaosRigidPhysicsAsync` | Runtime | **核心模块**。实现了异步的 Chaos 刚体物理世界、求解器和相关组件。 |
| `ChaosRigidPhysicsAsyncTests` | Runtime | **测试模块**。包含针对核心模块功能的自动化测试用例。 |

### 近期更新

- 2026-04-14 `35e60df1` 将 UE_LOG 迁移至 UE_LOGF。
- 2026-04-13 `55407bce` Chaos API：通过将 Tick 拆分为 Start/End Tick 来更新场景 API，并新增了 WaitOnTick。
- 2026-04-09 `c63a4c15` Chaos API：更新形状实例以处理材质。
- 2026-04-08 `6d6dbc44` Chaos API：添加 PhysicsService，并移除了异步插件对 Dataflow 的依赖。
- 2026-03-31 `5f0e43c9` Chaos API：更新形状实例以处理凸体、三角网格和高度场几何类型。

### 维护评价

该插件近期处于**活跃维护**状态。在约两周内进行了五次提交，更新频率较高，内容集中于 Chaos 物理 API 的底层重构、功能解耦与接口优化，表明开发团队正在积极完善其核心架构与稳定性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosRigidPhysicsAsync)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosRigidPhysicsAsync/Tests)