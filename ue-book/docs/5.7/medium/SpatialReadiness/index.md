# SpatialReadiness

> 通过跟踪物理物体的“就绪”状态（如冻结/休眠），避免不必要的物理更新，从而优化仿真性能。

| 属性 | 值 |
|---|---|
| 中文名 | 空间就绪状态管理 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无（纯代码插件） |
| 模块 | `SpatialReadiness` (Runtime), `SpatialReadinessTests` (Runtime, 测试) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-07-21 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SpatialReadiness) | |

## 总体用途

SpatialReadiness 是一套轻量级的物理优化系统，它标记物理物体的“空间就绪状态”（Spatial Readiness），允许引擎跳过对已冻结（Frozen）或非活跃物体的碰撞查询、约束求解和更新逻辑。主要目标是降低大型物理场景中因持续评估休眠物体而产生的 CPU 开销，同时保持对弹起/唤醒事件的及时响应。

该插件为 Chaos 物理引擎的 UserData 系统提供额外的状态标记，配合 `ChaosUserDataPT` 依赖，可在帧间高效地查询和修改物体的就绪等级。调试和统计功能（如周期统计、冻结体列表排序）也内置于核心模块中，便于性能分析。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| `SpatialReadiness` | Runtime | 核心模块：定义就绪状态枚举、管理冻结体列表、提供蓝图/C++ 接口，并集成调试统计。 |
| `SpatialReadinessTests` | Runtime | 测试模块：包含自动化单元测试和性能基准，验证就绪状态切换的正确性与性能收益。 |

> 各模块的详细 API 和用法请参阅：
> - [SpatialReadiness 模块文档](./SpatialReadiness.md)
> - [SpatialReadinessTests 模块文档](./SpatialReadinessTests.md)

## 使用场景

- **大型开放世界**：场景中有数千个静态或半静态物体（如石块、固定家具），它们大部分时间不运动。启用 SpatialReadiness 后，这些物体可被标记为“已冻结”，物理管线将跳过它们的碰撞检测与更新，显著降低每帧耗时。
- **物理沙箱/测试工具**：开发者需要在模拟中观察哪些物体处于活跃/冻结状态，并手动控制就绪阈值。插件提供的调试打印、统计信息和 CVar 开关非常适合此类场景。
- **性能敏感的物理模拟**：需要对物理引擎进行精细调优，避免因休眠物体反复被唤醒导致不必要的计算开销。SpatialReadiness 允许定义多级就绪状态，实现更灵活的休眠策略。
- **Juno 项目集成**：插件初期即为 Juno（可能为特定游戏/项目）提供了专用 CVar，便于在 Standalone 模式下进行测试与验证。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SpatialReadiness)
- [SpatialReadiness 模块文档](./SpatialReadiness.md)
- [SpatialReadinessTests 模块文档](./SpatialReadinessTests.md)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/SpatialReadiness/Tests/)