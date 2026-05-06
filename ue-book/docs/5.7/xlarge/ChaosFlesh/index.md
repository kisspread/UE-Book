# Chaos Flesh

> Chaos Flesh Simulation

| 属性 | 值 |
|---|---|
| 中文名 | 混沌物理肉体模拟 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、数据流图表、测试资源） |
| 模块 | `ChaosFlesh` (Runtime), `ChaosFleshDeprecatedNodes` (Runtime), `ChaosFleshEditor` (Runtime), `ChaosFleshEngine` (Runtime), `ChaosFleshNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-10-01 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosFlesh) | |

## 总体用途

Chaos Flesh 是一套基于 Chaos 物理引擎的软组织模拟系统，用于在 Unreal Engine 中创建可变形体（如肌肉、脂肪、皮肤等）的真实物理效果。它提供数据流（Dataflow）驱动的可视化编程工作流，允许艺术家和设计师无需深入 C++ 即可搭建肉体仿真网络，并集成到角色动画或实时场景中。

该插件仍处于 **实验性阶段**，适用于对物理模拟有高要求的项目，如写实类游戏、医疗模拟或影视预演。

## 模块列表

| 模块 | 一句话总结 | 详细文档 |
|---|---|---|
| `ChaosFlesh` (Runtime) | 核心运行时，包含肉体模拟的物理求解器与基本数据结构 | [ChaosFlesh.md](ChaosFlesh.md) |
| `ChaosFleshDeprecatedNodes` (Runtime) | 已被取代的旧版数据流节点，用于向后兼容 | [ChaosFleshDeprecatedNodes.md](ChaosFleshDeprecatedNodes.md) |
| `ChaosFleshEditor` (Runtime) | 编辑器工具，提供资产编辑、预览与调试功能 | [ChaosFleshEditor.md](ChaosFleshEditor.md) |
| `ChaosFleshEngine` (Runtime) | 引擎集成层，将模拟结果同步到场景组件与动画管线 | [ChaosFleshEngine.md](ChaosFleshEngine.md) |
| `ChaosFleshNodes` (Runtime) | 数据流节点库，暴露给蓝图/图表编辑器的可视化编程节点 | [ChaosFleshNodes.md](ChaosFleshNodes.md) |

## 使用场景

- **角色肉体变形**：模拟角色在运动时肌肉、脂肪的自然晃动与碰撞响应。
- **生物/怪物动画**：为非人形生物添加软体部位，如蠕动的触手、鼓起的囊状物。
- **医疗手术模拟**：通过实时变形反馈模拟组织切割、挤压。
- **影视级特效**：生成衣服、道具与身体接触时的挤压/拉伸效果。
- **数据流原型验证**：使用 Dataflow 节点快速搭建物理模拟网络，无需编程。

## 相关链接

- [源码（主分支）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosFlesh)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/chaos-flesh-in-unreal-engine/)（注意：实验性功能文档可能不全）