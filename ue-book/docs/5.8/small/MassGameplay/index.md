# Mass Gameplay

> Implementation of large-scale agent simulation based on MassEntity

| 属性 | 值 |
|---|---|
| 中文名 | 大规模游戏玩法 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资产（模型、材质、动画等）） |
| 模块 | `MassActors` (Runtime), `MassCharacterTrajectory` (Runtime), `MassCommon` (Runtime), `MassEQS` (Runtime), `MassGameplayDebug` (Runtime), `MassGameplayEditor` (Runtime), `MassGameplayExternalTraits` (Runtime), `MassGameplayTestSuite` (Runtime), `MassLOD` (Runtime), `MassMovement` (Runtime), `MassMovementEditor` (Runtime), `MassReplication` (Runtime), `MassRepresentation` (Runtime), `MassSimulation` (Runtime), `MassSmartObjects` (Runtime), `MassSpawner` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay) | |

## 用途

MassGameplay 是构建在 **MassEntity** 框架之上的游戏玩法实现层。MassEntity 提供了一套高性能的 ECS（实体组件系统）架构，而 MassGameplay 则利用这套架构，为大规模实体（成千上万甚至数十万）的模拟和交互提供了具体的游戏功能模块。

它的存在是为了解决在 UE 中模拟海量 AI 代理（Agent）、人群、动态物体等场景时，传统 Actor 模型性能不足的问题。通过数据驱动和并行处理的方式，MassGameplay 能够高效地管理这些实体的行为、移动、表示、网络同步和 LOD 等。

## 使用场景

- 你需要创建一个拥有成千上万 NPC 的大型城市或战场场景
- 你需要模拟密集的野生动物群体或复杂的人群行为
- 你需要高效地处理大量动态、可交互的物体（如飞鸟、粒子、破坏体）
- 你的项目需要极致的性能，并愿意采用新的 ECS 数据驱动架构

## 模块列表

以下是 MassGameplay 插件包含的所有模块及其简要功能说明。更详细的 API 和用法请参阅各子模块的文档。

| 模块 | 说明 |
|---|---|
| `MassActors` | 提供 MassEntity 与 Unreal Actor 之间的桥接，允许实体被表示为 Actor |
| `MassCharacterTrajectory` | 基于角色移动组件，计算并预测角色的移动轨迹 |
| `MassCommon` | 包含 MassEntity 框架所需的核心数据类型、片段（Fragment）和标签（Tag） |
| `MassEQS` | 将 Unreal 的环境查询系统（EQS）与 MassEntity 集成，用于大规模 AI 决策 |
| `MassGameplayDebug` | 提供用于调试和可视化 MassEntity 世界状态的编辑器工具和运行时调试功能 |
| `MassGameplayEditor` | 包含支持 MassGameplay 运行的编辑器特定功能和资产类型 |
| `MassGameplayExternalTraits` | 定义可应用于 MassEntity 的通用特征（Traits），如碰撞、导航等 |
| `MassGameplayTestSuite` | 包含 MassGameplay 的自动化测试用例 |
| `MassLOD` | 实现基于距离和视角的实体 LOD 系统，决定实体的表示细节（如网格、动画） |
| `MassMovement` | 提供实体的大规模移动系统，包括路径跟随、群体避障、物理移动等 |
| `MassMovementEditor` | 提供 MassMovement 相关的编辑器工具和可视化 |
| `MassReplication` | 处理 MassEntity 的网络同步和复制，适用于多人游戏 |
| `MassRepresentation` | 管理实体的视觉表示，如静态网格、骨骼网格体、布料等，并负责实例化渲染 |
| `MassSimulation` | 提供 MassEntity 世界的核心模拟运行框架，驱动整个 ECS 系统的更新 |
| `MassSmartObjects` | 将 MassEntity 与 SmartObject 系统集成，让实体能够与场景中的交互点互动 |
| `MassSpawner` | 提供实体生成、销毁和生命周期管理的功能 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay/Source/MassGameplayTestSuite)