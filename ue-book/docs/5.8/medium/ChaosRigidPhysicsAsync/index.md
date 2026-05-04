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

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosRigidPhysicsAsync)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosRigidPhysicsAsync/Tests)