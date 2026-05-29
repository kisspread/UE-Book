```markdown
# MassGameplay

> Implementation of large-scale agent simulation based on MassEntity

| 属性 | 值 |
|---|---|
| 中文名 | 大规模游戏玩法 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、测试资源） |
| 模块 | `MassActors` (Runtime), `MassCharacterTrajectory` (Runtime), `MassCommon` (Runtime), `MassEQS` (Runtime), `MassGameplayDebug` (Runtime), `MassGameplayEditor` (Runtime), `MassGameplayExternalTraits` (Runtime), `MassGameplayTestSuite` (Runtime), `MassLOD` (Runtime), `MassMovement` (Runtime), `MassMovementEditor` (Runtime), `MassReplication` (Runtime), `MassRepresentation` (Runtime), `MassSimulation` (Runtime), `MassSmartObjects` (Runtime), `MassSpawner` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay) | |

## 用途

MassGameplay 是基于 MassEntity（ECS 架构）构建的大规模代理（Agent）模拟框架的上层实现。它将 MassEntity 的底层数据驱动能力转化为可直接用于游戏玩法的系统，解决**同屏成千上万个实体（NPC、载具、群组）的高效模拟**问题。

核心思路：底层 MassEntity 提供 ECS 数据布局和批量处理能力，MassGameplay 在其之上实现了运动、表示、LOD、网络复制、生成、智能对象交互等游戏层功能，使开发者能够以声明式方式定义大规模实体的行为与外观。

该插件从原 MassEntity 插件中拆分而来（MassEntity 负责核心 ECS 框架，MassAI 负责 AI 导航，MassGameplay 负责通用游戏玩法功能）。

> ⚠️ **注意**：此插件默认禁用且标记为实验性（`IsExperimentalVersion=true`），API 可能在版本间发生破坏性变更。

## 使用场景

- 你需要同屏模拟 10,000+ 个 NPC（市民、僵尸群、军队）→ 用 MassSpawner + MassRepresentation
- 你需要大规模实体的网络同步（多人游戏中的群组）→ 用 MassReplication
- 你需要根据距离对大量实体做 LOD 简化（远距离降级为点集/布告板/隐藏）→ 用 MassLOD
- 你需要大量实体平滑移动和避让 → 用 MassMovement
- 你需要大量实体与场景中的智能对象（门、掩体）交互 → 用 MassSmartObjects
- 你需要从 EQS 查询中驱动大量实体的决策 → 用 MassEQS

## 模块一览

| 模块 | 职责 |
|---|---|
| **MassActors** | Mass Entity 与 Actor 之间的桥接，提供 MassAgentComponent 等双向关联机制 |
| **MassCharacterTrajectory** | 为 Mass 实体生成角色运动轨迹数据，用于动画预测 |
| **MassCommon** | 通用片段（Fragment）和标签（Tag）定义，所有模块共享的基础数据类型 |
| **MassEQS** | 将 Mass Entity 系统与环境查询系统（EQS）集成，实现大规模环境查询 |
| **MassGameplayDebug** | 调试可视化工具，支持运行时观察 Mass 实体状态 |
| **MassGameplayEditor** | 编辑器扩展，提供 MassGameplay 相关的编辑器 UI 和资产类型 |
| **MassGameplayExternalTraits** | 外部特质定义，用于扩展 Mass 实体的外部属性接口 |
| **MassGameplayTestSuite** | 自动化测试套件，覆盖 MassGameplay 各子系统的功能验证 |
| **MassLOD** | 多级细节管理，根据观察者距离动态切换实体的表示精度 |
| **MassMovement** | 大规模移动处理器，实现批量实体的速度、转向和碰撞规避 |
| **MassMovementEditor** | MassMovement 的编辑器支持模块 |
| **MassReplication** | 大规模实体的网络复制方案，支持分布式代理同步 |
| **MassRepresentation** | 实体视觉表示管理，在 Actor、ISM（实例化静态网格）、布告板等模式间切换 |
| **MassSimulation** | 总体模拟调度，管理 Mass 实体的生命周期和系统执行顺序 |
| **MassSmartObjects** | Mass 实体与 SmartObject 系统的集成，实现大规模实体的场景交互 |
| **MassSpawner** | 实体生成器，支持按区域/点位批量生成和销毁 Mass 实体 |

## 模块依赖

该插件的大部分模块仅依赖 MassEntity 核心框架和标准 UE 模块。以下是值得关注的特殊依赖：

| 模块 | 用途 |
|---|---|
| `MassEntity` | MassGameplay 的底层 ECS 框架，所有模块的核心依赖 |
| `SmartObjects` | MassSmartObjects 模块用于集成智能对象交互系统 |
| `GameplayAbilities` | MassGameplayExternalTraits 用于集成 GAS 特质 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `07ab5d30` | Revert earlier change to MassAgentComponent. | 回滚 MassAgentComponent 的先前改动 |
| 2026-05-13 | `751e48da` | [MassRepresentation] Wait for actor readiness before switching off ISM | 关闭 ISM 前等待 Actor 就绪，修复表示切换闪烁 |
| 2026-05-13 | `022b39e0` | Fix handling of non-puppet actors in Mass crowds | 修复群组中非傀儡 Actor 的处理逻辑 |
| 2026-05-12 | `7c7f835b` | [MassRepresentation] Cluster of pre-existing bugs in `TMassLODCalculator`'s per-viewer LOD path. | 修复 LOD 计算器中逐观察者路径的一批历史遗留 Bug |
| 2026-05-12 | `f59bc340` | [Mass representation] Switched two manually calculated `bDoKeepActorExtraFrame` to use the new UE::M | 统一 Actor 帧保留逻辑为新 API |

### 维护评价

- **状态**：🟢 **活跃维护中**
- 最近一次更新在 2026 年 5 月，距今不足 1 个月，更新频率高且集中于 Representation 和 LOD 子系统
- 多个模块仍在持续修 bug 和优化，说明 Epic 内部项目（如 Fortnite）仍在使用
- 标记为实验性（`IsExperimentalVersion=true`），API 稳定性无法保证
- 默认禁用，需手动在项目设置中启用
- **推荐使用**：如果你的项目需要大规模实体模拟（>1000 个同屏代理），这是 Epic 官方唯一方案，尽管是实验性状态，但维护活跃，建议关注但谨慎用于生产环境

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay)
- [MassEntity 核心框架](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassEntity)（MassGameplay 的底层依赖）
- [MassAI 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/MassAI)（AI 导航相关，与 MassGameplay 同源拆分）
```