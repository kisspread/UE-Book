# ChaosCaching

> Chaos Cache asset support for recording and playing back physics simulations

| 属性 | 值 |
|---|---|
| 中文名 | 混沌缓存 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `ChaosCaching` (Runtime), `ChaosCachingEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-01 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosCaching) | |

## 总体用途

ChaosCaching 插件提供了一套用于录制和回放 Chaos 物理模拟的缓存资产系统。它允许开发者将复杂的物理模拟（如布料、刚体碰撞、破碎等）记录为缓存数据，并在运行时以极低的性能开销进行回放。这解决了物理模拟不可预测、性能开销大的问题，常用于电影级预渲染、游戏中的固定物理表演（如过场动画、爆炸效果）、以及需要精确重现物理交互的场景（如重放系统、测试验证）。插件依赖 `Takes` 模块来驱动录制流程。

## 模块列表

| 模块 | 类型 | 文档 | 一句话总结 |
|---|---|---|---|
| `ChaosCaching` | Runtime | [ChaosCaching.md](ChaosCaching.md) | 运行时核心，负责缓存数据的定义、录制与回放逻辑及蓝图暴露接口 |
| `ChaosCachingEditor` | Editor | [ChaosCachingEditor.md](ChaosCachingEditor.md) | 编辑器工具，提供在编辑视口中录制物理模拟并产出缓存资产的工作流与 UI |

## 使用场景

- **过场动画与电影序列**：录制复杂或随机的物理效果（如建筑物倒塌、布料飘动），确保每次播放完全一致，且性能开销极低。
- **游戏内重放系统**：将玩家造成的物理交互（如车辆撞击、物体破碎）记录下来，用于击杀回放或精彩镜头。
- **性能优化**：对于多体交互或高精度模拟，预先录制缓存，避免运行时重复计算物理，尤其适用于移动端或低端硬件。
- **物理测试与调试**：固定物理模拟结果，便于进行视觉调整和 Bug 复现。
- **增量录制**：支持在多次录制中逐步向同一个缓存资产添加新片段，便于迭代制作长序列物理表演。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosCaching)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosCaching/Tests)