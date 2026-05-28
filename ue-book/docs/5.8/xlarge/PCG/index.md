# Procedural Content Generation Framework (PCG)

> Visual scripting framework for procedurally populating worlds with content in editor and/or at run-time.

| 属性 | 值 |
|---|---|
| 中文名 | 程序化内容生成框架 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、测试资源） |
| 模块 | `PCG` (Runtime), `PCGCompute` (Runtime), `PCGEditor` (Runtime), `PCGTests` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-01-30 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCG) | |

## 用途

PCG (Procedural Content Generation Framework) 是一个数据驱动、节点式的内容生成框架。其核心目的是提供一套完整的工具链，让开发者能够通过可视化图表 (Graph) 定义规则，在编辑器或运行时高效、可控地程序化生成游戏世界中的内容，如地形、植被、建筑布局、拾取物等。它解决了手动布置大型开放世界场景效率低下、难以迭代和维护的问题，是创建复杂、多样化且动态可调的游戏环境的强大工具。

## 使用场景

- **开放世界内容填充**：你需要为庞大的开放世界自动生成森林、草地、岩石分布和道路网络。
- **城市与建筑生成**：你需要程序化地布局城市街区、建筑群及其内部细节（如房间内的家具）。
- **关卡设计辅助**：你希望在关卡设计阶段快速生成并迭代原型，测试不同的布局方案。
- **动态内容**：你需要根据玩家行为或游戏状态，在运行时动态生成或修改场景内容。

## 模块列表

| 模块 | 类型 | 用途概述 |
|---|---|---|
| `PCG` | Runtime | 核心运行时库。包含框架基础、数据类型、执行环境、以及绝大多数标准的节点和工具。 |
| `PCGCompute` | Runtime | 计算模块。提供基于 GPU 的高性能计算节点（Compute Shader）支持，用于处理大规模数据。 |
| `PCGEditor` | Runtime | 编辑器集成模块。提供 PCG 图表编辑器、节点 UI、场景预览、以及与材质、地形等其他编辑器工具的集成。 |
| `PCGTests` | Runtime | 自动化测试模块。包含对 PCG 框架核心功能和节点的单元测试与功能测试。 |

## 蓝图用法（概览）

PCG 主要以资产和编辑器操作为主，但提供了一些蓝图接口。

### 核心概念

- **PCGGraph**：核心资产，是一个包含各种节点的可视化图表，定义了完整的生成逻辑。
- **PCGSubsystem**：世界子系统，负责管理和执行 PCG 图表的生成任务。
- **PCGComponent**：附加到场景 Actor 上的组件，用于将 PCG 图表（PCGGraph）与场景中的特定位置和区域关联。

### 典型工作流（蓝图描述）

1.  **创建图表资产**：在内容浏览器中右键创建 `PCGGraph` 资产。
2.  **编辑图表**：双击打开，从节点面板拖拽“表面采样器”、“过滤器”、“网格体生成器”、“点数据操作”等节点进行连接。
3.  **放置到场景**：在场景中放置一个 Actor，为其添加 `PCGComponent`。
4.  **指定图表**：在组件的详情面板中，指定你创建的 `PCGGraph` 资产。
5.  **生成与迭代**：点击组件详情面板中的“生成”按钮，或在编辑器工具栏中使用 PCG 窗口进行全局预览和生成。修改图表后，可实时或手动更新场景。

## C++ 用法（概览）

PCG 框架高度可扩展，通常通过 C++ 来创建自定义的节点、数据处理器或设置。

### 关键扩展点

- **自定义 PCG 节点**：继承 `UPCGSettings` 或 `UPCGStaticMeshSpawnerSettings` 等基类，定义输入输出端口和自定义逻辑。
- **自定义数据处理器**：实现 `IPCGDataProcessor` 接口，在数据流经节点时进行处理。
- **访问与操作数据**：在节点的 `Execute` 或 `ExecuteInternal` 函数中，使用 `FPCGContext`、`FPCGTaggedData` 和 `FPCGPoint` 等核心数据结构来读写点、属性和元数据。

### 测试用例

自动化测试位于 `Tests` 目录下（`PCGTests` 模块），采用 BDD 风格（`IMPLEMENT_SIMPLE_AUTOMATION_TEST` + `GIVEN/WHEN/THEN`）编写，是学习框架内部工作原理和用法的绝佳参考。

## Demo 示例

作为大型框架，PCG 本身即是一个功能完备的示例系统。学习的最佳方式是：
1.  查看 `Engine/Plugins/PCG/` 目录下已有的示例图表资产。
2.  在编辑器中使用 `PCGEditor` 模块提供的示例节点来构建自己的图表。
3.  研究 `PCGTests` 模块中的测试用例。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PCG` | 核心框架，包含所有基础类型和运行时逻辑。任何使用 PCG 功能的模块都必须依赖它。 |
| `PCGCompute` | 提供 GPU 计算能力，仅当需要编写或使用 Compute Shader 节点时依赖。 |
| `PCGEditor` | 编辑器扩展，仅在编辑器模块中依赖，用于提供 PCG 图表编辑和场景交互功能。 |
| `Landscape` | 地形交互，用于将 PCG 生成的点数据转化为地形层信息或从地形上采样。 |
| `ProceduralMeshComponent` | 程序化网格体，部分节点可用于动态生成程序化网格体。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `1cd8cea5` | [PCG] Fixed potential crash when building the landscape cache, when some entries can't be resolved. | 修复了在构建地形缓存时，部分条目无法解析可能导致的崩溃。 |
| 2026-05-26 | `788faf05` | [PCG] Optimize FPCGComponentVisualizer | 优化了 PCG 组件的可视化器性能。 |
| 2026-05-26 | `0532b644` | [PCG] Fix crash with null objects with accessors | 修复了当访问器遇到空对象时导致的崩溃。 |
| 2026-05-26 | `82ca98ed` | [PCG] Optimized & cached metadata size computation, but gated on a flag w/ TLS backing so the normal | 优化并缓存了元数据大小计算，并通过 TLS 标志进行控制。 |
| 2026-05-26 | `585bbecb` | [PCG] Fixed editor update performance issue related to manual edit (+ a double update) and inspection. | 修复了与手动编辑和检查相关的编辑器更新性能问题（包括双重更新）。 |

### 维护评价

**积极维护中**。PCG 框架于 2024 年初正式从实验阶段移出，是 Epic Games 近年来重点发展的核心工具之一。从近期（2026年5月）的提交记录可见，开发团队持续进行着**性能优化**和**稳定性修复**工作，提交频率高且内容具体，表明该框架仍在快速迭代和成熟过程中。它是一个**功能强大、设计现代、官方支持且推荐使用**的程序化内容生成解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCG)
- [官方文档](https://docs.unrealengine.com/latest/en-US/procedural-content-generation--framework-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCG/Tests)