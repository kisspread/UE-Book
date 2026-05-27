# Chaos Flesh

> Chaos Flesh Simulation

| 属性 | 值 |
|---|---|
| 中文名 | Chaos 软体仿真 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、Dataflow 图） |
| 模块 | `ChaosFlesh` (Runtime), `ChaosFleshDeprecatedNodes` (Runtime), `ChaosFleshEditor` (Runtime), `ChaosFleshEngine` (Runtime), `ChaosFleshNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-03-26 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosFlesh) | |

## 用途

ChaosFlesh 基于 Chaos 物理引擎，提供**软体（Flesh）有限元仿真**能力。与刚体碰撞不同，软体仿真允许物体在受力后发生**形变、撕裂、断裂**等效果，适用于肉体、果冻、内脏等需要弹塑性变形的物体。

核心资产类型为 `FleshCollection`，以四面体网格（Tetrahedral Mesh）作为体积表示，通过 Dataflow 图进行资产预处理和仿真节点编排。插件还集成了纤维场（Fiber Field）生成、蒙皮权重、破碎掩码等功能，属于 UE5 物理系统的高级扩展。

## 使用场景

- 你在做一个需要**肉体/软组织变形**效果的游戏（如格斗、手术模拟）→ 用 ChaosFlesh 配合 GeometryCollection 实现撞击形变
- 你需要对可变形物体做**撕裂和断裂**仿真 → ChaosFlesh 的有限元方法支持大变形和拓扑变化
- 你正在用 Dataflow 做程序化资产管线 → 用 ChaosFleshNodes 中的节点在 Dataflow 图中构建 Flesh 资产
- 你需要自定义纤维方向来控制肌肉收缩动画 → 利用纤维场（Fiber Field）节点生成方向数据

## 模块概览

| 模块 | 类型 | 说明 |
|---|---|---|
| [ChaosFlesh](ChaosFlesh.md) | Runtime | 核心运行时模块，包含 FleshCollection 数据结构、Chaos 仿真求解器集成、Dataflow 节点和组件接口 |
| [ChaosFleshEngine](ChaosFleshEngine.md) | Runtime | 引擎层扩展，提供 UFleshSimulationSystem、SimulationSpace、物理资产集成和场景管理 |
| [ChaosFleshNodes](ChaosFleshNodes.md) | Runtime | Dataflow 节点库，包含网格生成、纤维场、蒙皮、破碎掩码、位置偏移等预处理节点 |
| [ChaosFleshDeprecatedNodes](ChaosFleshDeprecatedNodes.md) | Runtime | 已废弃节点的临时保留，包含旧版 Dataflow 节点供向后兼容 |
| [ChaosFleshEditor](ChaosFleshEditor.md) | Runtime | 编辑器支持模块，提供资产编辑器、上下文菜单、工具栏集成和可视化辅助 |

## 蓝图用法

> ⚠️ ChaosFlesh 主要通过 C++ 和 Dataflow 图操作，蓝图支持有限。核心交互通过 `UFleshComponent` 和 `AFleshActor` 完成。

### 核心接口

| 接口 | 说明 | 所在类 |
|---|---|---|
| `FleshComponent` | 挂载 FleshCollection 资产并驱动仿真的组件 | `UFleshComponent` |
| `FleshActor` | 包含 FleshComponent 的 Actor 壳 | `AFleshActor` |
| `FleshSimulationSystem` | 场景级仿真系统，管理所有活跃的 Flesh 仿真实例 | `UFleshSimulationSystem` |

## C++ 用法

### 头文件引入

```cpp
#include "ChaosFlesh/FleshCollection.h"
#include "ChaosFleshEngine/FleshComponent.h"
```

### 基本用法

```cpp
// 创建 FleshCollection 并设置四面体网格
TSharedRef<FFleshCollection> FleshCollection = MakeShared<FFleshCollection>();

// 获取组件并绑定资产
UFleshComponent* FleshComp = NewObject<UFleshComponent>(OwnerActor);
FleshComp->SetFleshAsset(FleshAsset);
```

> 详细 API 请参考各子模块文档。

## 模块依赖

从各模块 Build.cs 提取的独特依赖：

| 模块 | 用途 |
|---|---|
| `Chaos` | Chaos 物理引擎核心 |
| `ChaosSolverEngine` | Chaos 求解器集成 |
| `GeometryCollectionEngine` | GeometryCollection 破碎系统集成 |
| `Dataflow` | Dataflow 节点图框架 |
| `DataflowNodes` | Dataflow 通用节点库 |
| `GeometryCollectionSimulationCore` | 几何集合仿真核心 |
| `FleshCollectionSimulationCore` | FleshCollection 仿真核心逻辑 |
| `AnimGraph` / `AnimGraphRuntime` | 动画图集成（骨骼绑定） |
| `PropertyAccess` / `PropertyEditor` | 属性系统和编辑器属性面板 |
| `MeshDescription` / `MeshConversion` | 网格数据处理和格式转换 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度到单精度截断的编译警告 |
| 2026-05-12 | `981bc9da` | Dataflow: | Dataflow 相关改动（信息不完整） |
| 2026-05-12 | `4bb4d4eb` | Flesh : fiber field generation node clean up | 清理纤维场生成节点的代码 |
| 2026-05-12 | `3ee54b1a` | PR #13147: Fix NumMaskBuffer assignment from OffsetsBuffer to MaskBuffer | 修复蒙版缓冲区的赋值错误 |
| 2026-05-12 | `563a0190` | Flesh : deprecate StaticMesh property from the flesh asset | 废弃 Flesh 资产上的 StaticMesh 属性，改用新管线 |

### 维护评价

- **创建时间**：2022 年 3 月，至今约 4 年
- **近期活跃度**：2026 年 5 月仍有密集提交，属于**活跃维护**状态
- **版本状态**：v0.1 + `IsExperimentalVersion=true` + `EnabledByDefault=false`，明确标注为实验性功能
- **迭代方向**：近期集中在 Dataflow 节点整理、缓冲区 bug 修复和废弃旧 API，表明正在从早期原型向稳定 API 过渡
- **风险提示**：作为实验性插件，API 可能随时发生 breaking change（如 StaticMesh 属性被废弃）。`ChaosFleshDeprecatedNodes` 模块的存在本身说明仍在处理旧版本迁移
- **推荐程度**：适合用于**技术预研和原型验证**，不建议直接用于生产环境。如需软体仿真能力，可密切关注其稳定化进展

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosFlesh)
- [官方文档]()（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosFlesh/Tests)（如有）