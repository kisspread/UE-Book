# Chaos Flesh

> Chaos Flesh Simulation

| 属性 | 值 |
|---|---|
| 中文名 | 柔体物理仿真 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、几何体数据资产） |
| 模块 | `ChaosFlesh` (Runtime), `ChaosFleshDeprecatedNodes` (Runtime), `ChaosFleshEditor` (Runtime), `ChaosFleshEngine` (Runtime), `ChaosFleshNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-03-26 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosFlesh) | |

## 用途

ChaosFlesh 是基于 Chaos 物理引擎的**柔体（Flesh）仿真系统**，用于模拟肌肉、软组织等可变形体的物理行为。它通过 `FFleshCollection` 数据结构管理柔体几何体（包括顶点、四面体网格、肌纤维方向等），并利用 Dataflow 图进行可变形体的预处理与仿真计算。

该插件的核心能力包括：
- **柔体资产系统**：`UFleshAsset` 存储柔体几何数据，支持四面体网格（Tetrahedral Mesh）表示
- **纤维场生成**：自动生成肌纤维方向场，用于驱动各向异性材质和物理行为
- **Dataflow 集成**：通过 Dataflow 图节点系统对柔体进行从网格细分、切割到纤维生成的完整预处理流水线
- **Chaos 物理集成**：将柔体几何数据注入 Chaos 物理求解器，实现形变仿真
- **Render Collection**：将仿真结果转换为可渲染的几何数据

简而言之：这是一个让角色拥有"软软的、会晃动的肉体"效果的技术方案。

## 使用场景

- 你在制作写实角色，需要胸肌、腹部等部位有**物理驱动的软组织形变**效果
- 你需要模拟**肌肉收缩与松弛**的物理行为（如过场动画中的肌肉绷紧效果）
- 你正在开发格斗/运动类游戏，需要角色受到冲击时**肉体凹陷变形**
- 你需要对四面体网格进行预处理（细分、切割、纤维方向生成）后再送入物理引擎
- 你希望通过 Dataflow 图形化地构建柔体仿真预处理流水线

## 模块概览

| 模块 | 类型 | 说明 |
|---|---|---|
| **ChaosFlesh** | Runtime | 核心数据结构（FFleshCollection、FFleshCollectionComponent）、柔体资产与场景代理 |
| **ChaosFleshEngine** | Runtime | 物理引擎集成层，将柔体几何注入 Chaos 求解器，驱动形变仿真 |
| **ChaosFleshNodes** | Runtime | Dataflow 节点库：网格细分、四面体生成、纤维场、切割、Collection 构建等 |
| **ChaosFleshDeprecatedNodes** | Runtime | 已废弃的 Dataflow 节点，保留向后兼容性 |
| **ChaosFleshEditor** | Runtime | 编辑器集成：资产类型注册、资产编辑器、细节面板自定义 |

> 各模块详细 API 文档请参阅对应的子页面。

## 子模块文档

- [ChaosFlesh.md](ChaosFlesh.md) — 核心数据结构与组件
- [ChaosFleshEngine.md](ChaosFleshEngine.md) — 物理引擎集成与场景代理
- [ChaosFleshNodes.md](ChaosFleshNodes.md) — Dataflow 节点库
- [ChaosFleshDeprecatedNodes.md](ChaosFleshDeprecatedNodes.md) — 废弃节点
- [ChaosFleshEditor.md](ChaosFleshEditor.md) — 编辑器集成

## 典型工作流

```
FleshAsset (四面体网格输入)
       │
       ▼
  Dataflow 图预处理
  ┌─ SubdivideTetrahedralMesh（网格细分）
  ├─ Tetrahedralize（表面→四面体）
  ├─ BuildFleshCollection（构建 Collection）
  ├─ GenerateFiberField（生成纤维方向）
  └─ CutTetrahedralMesh（网格切割）
       │
       ▼
  FFleshCollectionComponent（场景组件）
       │
       ▼
  Chaos 物理求解器（形变仿真）
       │
       ▼
  Render Collection（渲染输出）
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Chaos` | Chaos 物理引擎核心 |
| `ChaosSolverEngine` | Chaos 求解器运行时 |
| `DataflowEngine` | Dataflow 图执行引擎 |
| `Dataflow` | Dataflow 节点与图框架 |
| `DataflowNodes` | 通用 Dataflow 节点 |
| `GeometryCollectionEngine` | 几何体集合引擎（与破碎系统共享基础设施） |
| `GeometryFramework` | 几何体渲染框架 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度截断警告 |
| 2026-05-12 | `981bc9da` | Dataflow: | Dataflow 相关改动 |
| 2026-05-12 | `4bb4d4eb` | Flesh : fiber field generation node clean up | 纤维场生成节点代码清理 |
| 2026-05-12 | `3ee54b1a` | PR #13147: Fix NumMaskBuffer assignment from OffsetsBuffer to MaskBuffer | 修复遮罩缓冲区赋值逻辑错误 |
| 2026-05-12 | `563a0190` | Flesh : deprecate StaticMesh property from the flesh asset | 废弃柔体资产中的 StaticMesh 属性 |

### 维护评价

- **活跃维护**：最近一次更新距今不到 1 周，2026 年 5 月有多次密集提交
- **实验性质**：标记为 `IsExperimentalVersion=true` 且 `EnabledByDefault=false`，API 不稳定，存在废弃节点（ChaosFleshDeprecatedNodes 模块的存在已证实）
- **持续演进**：从 2022 年创建至今持续开发，近期活跃地进行节点清理、属性废弃和 bug 修复，表明 Epic 仍在积极迭代
- **注意事项**：
  - 插件仍处于实验阶段，API 和数据结构可能随版本变化
  - `StaticMesh` 属性已被废弃，新项目应使用 `FFleshCollection` 的四面体网格数据
  - 依赖 Chaos 物理引擎，需要正确配置项目物理设置
- **推荐程度**：如果你需要柔体仿真效果，这是目前 UE5 中唯一官方的解决方案。虽然实验性，但有持续维护，可以谨慎使用。生产环境使用需关注版本升级时的 API 变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosFlesh)
- 测试用例：未发现独立测试目录