# Mesh Resizing

> Mesh Resizing（网格调整大小）

| 属性 | 值 |
|---|---|
| 中文名 | 网格调整 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、示例场景） |
| 模块 | `MeshResizingCore` (Runtime), `MeshResizingEditorTools` (Runtime), `MeshResizingEngine` (Runtime), `MeshResizingDataflowNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-12-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshResizing) | |

## 用途

`MeshResizing` 是一个实验性编辑器插件，旨在为用户提供在编辑器中对静态网格（Static Mesh）或骨骼网格（Skeletal Mesh）进行非均匀、交互式尺寸调整的功能。它超越了简单的等比缩放，允许用户通过类似“捏脸”或塑形的方式，对网格的特定区域进行变形和调整。其核心是提供一套基于 Dataflow 的节点和相应的编辑器工具，使得复杂的网格调整操作可以在可视化的节点图中完成，结果可以记录并应用到资产上。

该插件主要解决的问题是：在角色定制、物体适配或需要对网格进行局部形态调整时，传统的建模软件流程冗长。`MeshResizing` 希望在 UE 编辑器内提供一个直接的、可迭代的解决方案。

## 使用场景

- 你正在开发一个需要角色高度自定义系统的游戏（如捏脸、换装体型调整）→ 使用 MeshResizing 创建自定义调整工具和数据流。
- 你需要快速调整一系列静态网格资产（如家具、建筑部件）以适应不同的场景需求，而不想回到DCC软件中重复建模 → 在编辑器内使用 MeshResizing 工具进行交互式调整。
- 你正在制作一个需要程序化调整网格形态的工具（例如，根据碰撞体自动调整物体形状） → 使用 MeshResizing 的 Dataflow 节点构建自定义逻辑。

## 蓝图用法

此插件的核心功能主要通过 **Dataflow 节点** 和 **编辑器工具** 暴露，传统的蓝图函数较少。主要的可编程接口集中在 `MeshResizingDataflowNodes` 模块中。

### 核心节点 (Dataflow Nodes)

Dataflow 节点通常通过编辑器中的“资产编辑器”或自定义的 Dataflow 图表来使用。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FMeshResizingDataflowNodes` | 静态工具类，包含所有注册的 Dataflow 节点工厂方法。 | `MeshResizingDataflowNodes` 模块 |

具体节点（如输入网格、应用变形、设置锚点等）需要通过编辑器中的 Dataflow 图形界面搜索添加。

### 使用示例 (蓝图/编辑器描述)

1.  **创建 Dataflow 资产**: 在内容浏览器中右键创建“Dataflow”资产。
2.  **添加节点**: 在打开的 Dataflow 图表编辑器中，右键搜索“Mesh Resizing”类别，添加如“获取网格数据”、“应用调整”等节点。
3.  **连接逻辑**: 将节点按照数据输入->处理->输出的逻辑连接起来，形成一个调整工作流。
4.  **应用结果**: 通过节点图最终输出调整后的网格数据，可以保存到新的资产或覆盖原资产。

## C++ 用法

此插件的 C++ API 主要面向工具和 Dataflow 节点的开发者，用于扩展其功能。

### 头文件引入

```cpp
#include "MeshResizingEngine/MeshResizingEngine.h" // 核心引擎功能
```

### 基本用法

（由于未提供具体的测试用例文件路径，以下为根据模块功能的推测示例）

```cpp
// 假设在某个工具或节点的实现中
#include "MeshResizingEngine/MeshResizingUtils.h"

void AdjustMeshRegion(UStaticMesh* Mesh, const FVector& RegionCenter, float ScaleFactor)
{
    // 使用引擎模块提供的工具函数
    MeshResizingUtils::ScaleMeshRegion(Mesh, RegionCenter, ScaleFactor);
}
```

### 进阶用法

结合多个模块（如 `MeshResizingCore` 的数据结构和 `MeshResizingEngine` 的处理逻辑）来实现复杂的调整算法。

## Demo 示例

由于这是一个实验性插件，且没有提供具体的测试文件路径，一个完整的最小 C++ 示例目前难以准确构建。建议参考插件自带的蓝图资产或编辑器工具来学习其使用模式。通常，您可以在引擎的 `Content/Experimental/MeshResizing` 或类似路径下找到示例场景和图表。

## 模块依赖

`MeshResizingEngine` 模块的依赖通常包括其他 MeshResizing 内部模块，以及一些图形和几何处理相关的模块。

| 模块 | 用途 |
|---|---|
| `MeshResizingCore` | 提供核心数据类型、接口和基础功能 |
| `GeometryCore`, `GeometryFramework` | 提供几何计算和几何体表示的基础框架 |
| `MeshResizingDataflowNodes` | (若依赖) 用于 Dataflow 节点的交互 |

*注意：具体依赖项请参考 `MeshResizingEngine.Build.cs` 文件中的 `PublicDependencyModuleNames` 和 `PrivateDependencyModuleNames`。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点数导致的代码警告。 |
| 2026-05-12 | `a7802337` | Dataflow: (Commit message incomplete in provided data) | 数据流相关更新（具体内容不完整）。 |
| 2026-03-16 | `1f05dc85` | Adding includes before upcoming header cleanup. | 在即将到来的头文件清理前，预先添加必要的头文件引用。 |
| 2026-01-30 | `7b60de76` | Dataflow : add support to lasso to the paint tool by leveraging the newly added feature in the mesh | 数据流：为画笔工具增加套索选择支持，利用了网格模块新增的特性。 |
| 2025-12-19 | `f86e1e20` | Dataflow : update a lot of nodes to use the new rendering system | 数据流：更新大量节点以使用新的渲染系统。 |

### 维护评价

- **活跃维护**: 是。自2024年12月创建以来，持续有功能更新和修复，最近的提交在2026年5月，表明项目仍在积极开发中。
- **实验性**: 是。`.uplugin` 中明确标记为实验性版本，且默认未启用。
- **风险提示**: 作为实验性插件，API 和功能可能在未来版本中发生重大变化或被移除。不建议在追求稳定性的正式项目中深度依赖。
- **推荐使用**: 推荐用于**原型开发、内部工具制作或技术预研**，以探索编辑器内网格程序化调整的可能性。在用于生产环境前，需充分评估其稳定性和长期维护承诺。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshResizing)
- 官方文档: 暂无
- 测试用例: 暂未在提供信息中指定路径，可在源码目录内查找 `Tests` 文件夹或搜索相关自动化测试文件。