# Mass AI

> AI-specific functionality extending MassGameplay（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 大规模 AI |
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（数据资产、行为配置） |
| 模块 | `MassNavigation` (Runtime), `MassNavMeshNavigation` (Runtime), `MassZoneGraphNavigation` (Runtime), `MassAIBehavior` (Runtime), `MassAIBehaviorEditor` (Runtime), `MassAIDebug` (Runtime), `MassAIReplication` (Runtime), `MassNavigationEditor` (Runtime), `MassAITestSuite` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/MassAI) | |

## 用途

MassAI 是 MassEntity（ECS 架构）在 AI 领域的扩展，专门为**大规模 AI 群体**提供高效的导航和行为系统。

与传统 UObject/行为树架构不同，MassAI 利用 MassEntity 的批量数据处理能力，将 AI 的移动、寻路、行为决策等操作以 **Fragment（组件）+ Processor（系统）** 的 ECS 模式实现。这使得单场景中同时驱动数千个 AI Agent 成为可能，而不会产生 UObject 的实例化开销。

核心解决的问题：
- **性能瓶颈**：传统 AI Controller + NavigationSystem 在大量 NPC 场景下成为性能瓶颈
- **内存占用**：每个 AI Agent 作为 UObject 的内存开销过大
- **寻路多样性**：同时支持 NavMesh、ZoneGraph 等多种导航方式，适配不同场景需求

## 模块一览

| 模块 | 说明 |
|---|---|
| **MassNavigation** | 核心导航模块，提供基于 MassEntity 的移动与避障框架 |
| **MassNavMeshNavigation** | NavMesh 寻路适配，将 MassNavigation 与 UE NavigationSystem 集成 |
| **MassZoneGraphNavigation** | ZoneGraph 寻路适配，适用于道路/走廊式线性导航场景 |
| **MassAIBehavior** | AI 行为逻辑框架，基于 MassEntity 的行为状态机 |
| **MassAIBehaviorEditor** | 行为系统编辑器支持（自定义资产编辑器、节点可视化） |
| **MassAIDebug** | 调试工具，MassEntity 调试器的 AI 扩展 |
| **MassAIReplication** | AI 网络同步支持（MassEntity Replication 扩展） |
| **MassNavigationEditor** | 导航编辑器支持（自定义资产编辑器、视觉配置） |
| **MassAITestSuite** | 自动化测试套件 |

## 使用场景

- 你需要一个开放世界场景中同时运行 **数千个 NPC**，且要求帧率稳定 → 用 MassAI + MassNavigation
- 你需要 NPC 沿道路/走廊进行 **线性巡逻导航**（而非自由寻路） → 用 MassZoneGraphNavigation
- 你需要 NPC 在复杂地形中进行 **自由避障寻路** → 用 MassNavMeshNavigation
- 你已经在用 MassGameplay 做大规模实体管理，需要为其添加 **AI 行为能力** → 用 MassAIBehavior
- 你需要在开发阶段 **可视化调试** Mass AI Agent 的状态和决策 → 用 MassAIDebug

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MassEntity` | ECS 核心框架，所有 MassAI 模块的基础 |
| `MassGameplay` | MassEntity 的 Gameplay 层扩展（MassSpawner 等） |
| `MassEntityEditor` | MassEntity 编辑器支持（MassAIDebug 依赖） |
| `ZoneGraph` | ZoneGraph 数据驱动路径系统（MassZoneGraphNavigation 依赖） |
| `NavigationSystem` | UE 原生导航系统（MassNavMeshNavigation 依赖） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `8e83e6bf` | Remove use of INFINITY to fix compile error on latest Windows SDK | 移除 INFINITY 宏用法，修复新版 Windows SDK 编译错误 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 截断为 float 的编译警告 |
| 2026-05-12 | `328c7999` | [Mass] PR #14001: Fix Mass debugger running with invalid entity | 修复 Mass 调试器在无效实体上运行导致的崩溃 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复格式化函数中 scoped enum 导致的乱码输出 |
| 2026-04-15 | `4b250a9d` | [RewindDebugger] | RewindDebugger 相关改动（MassAI 联动） |

### 维护评价

MassAI 处于**活跃维护**状态。近期更新集中在编译兼容性修复和调试工具改进，表明 Epic 持续在维护此模块。

需要注意的是：
- ⚠️ **实验性插件**：`IsExperimentalVersion=true`，API 可能在未来版本中发生破坏性变更
- ⚠️ **默认未启用**：需要在插件管理器中手动启用
- ✅ 作为 MassEntity/MassGameplay 的 AI 层扩展，与 Epic 推动的大规模实体系统发展方向一致
- ✅ 约 155 个源文件，功能覆盖完整（导航、行为、调试、同步、测试）

**推荐在以下情况下使用**：如果你的目标平台需要同时处理大量 AI Agent（>500），并且可以接受实验性 API 的风险。对于少量 NPC 场景，传统行为树 + AI Controller 方案更为成熟稳定。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/MassAI)
- 官方文档：暂无
- 子模块文档：
  - [MassNavigation](MassNavigation.md)
  - [MassNavMeshNavigation](MassNavMeshNavigation.md)
  - [MassZoneGraphNavigation](MassZoneGraphNavigation.md)
  - [MassAIBehavior](MassAIBehavior.md)
  - [MassAIBehaviorEditor](MassAIBehaviorEditor.md)
  - [MassAIDebug](MassAIDebug.md)
  - [MassAIReplication](MassAIReplication.md)
  - [MassNavigationEditor](MassNavigationEditor.md)
  - [MassAITestSuite](MassAITestSuite.md)