# Editor DataflowGraph

> Editor Dataflow Graph

| 属性 | 值 |
|---|---|
| 中文名 | 编辑器数据流图 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（资产） |
| 模块 | `DataflowEditor` (Runtime), `DataflowEnginePlugin` (Runtime), `DataflowNodes` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2026-04-17 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Dataflow) | |

## 用途

Dataflow 插件提供了一个在 Unreal Engine 编辑器中创建和执行数据流图（Dataflow Graph）的框架。它是一个可视化脚本系统，专门用于处理数据转换、几何体操作（如骨骼网格体变形）以及资产处理等任务。该插件从实验状态迁移至稳定版本，解决了复杂数据处理管线（例如角色皮肤权重编辑、网格体生成等）的可视化构建与调试需求。

## 使用场景

- 你需要为骨骼网格体创建复杂的变形器（Deformer）或蒙皮权重编辑工具 → 使用 Dataflow 图构建逻辑。
- 你正在开发需要可视化调试数据处理流程（例如几何体生成、资产导入/转换管线）的工具 → 使用 Dataflow 节点编辑器。
- 你希望为美术或技术美术提供一个直观的界面来调整参数并实时预览结果 → 使用 Dataflow 图形界面。

## 模块列表

本插件包含以下三个模块：

| 模块 | 类型 | 简述 |
|---|---|---|
| `DataflowEditor` | Runtime | 提供 Dataflow 图的编辑器界面和交互逻辑。 |
| `DataflowEnginePlugin` | Runtime | 连接 Dataflow 图与引擎运行时，负责图的执行和计算。 |
| `DataflowNodes` | Runtime | 包含所有可用的 Dataflow 节点（如数据处理、几何体操作节点）。 |

详细的 API 文档请参见各子模块文档：
- [DataflowEditor](DataflowEditor.md)
- [DataflowEnginePlugin](DataflowEnginePlugin.md)
- [DataflowNodes](DataflowNodes.md)

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Dataflow)
- [DataflowEditor 模块文档](DataflowEditor.md)
- [DataflowEnginePlugin 模块文档](DataflowEnginePlugin.md)
- [DataflowNodes 模块文档](DataflowNodes.md)

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `ee85ff45` | Dataflow : remove sections from rendering settings since they are half broken | 移除了渲染设置中部分损坏的章节。 |
| 2026-05-25 | `25af8e6f` | Dataflow : add extra checks on the edit skin weight tool to inform user about why the node may not s | 为编辑皮肤权重工具添加额外检查，以告知用户节点可能无法工作的原因。 |
| 2026-05-22 | `9a062c29` | [Dataflow Editor] Fixed container mutation during tick evaluation. | 修复了在图的 Tick 评估期间容器被意外修改的问题。 |
| 2026-05-22 | `8dc486bc` | Dataflow Editor : Fix crash happening when using a tool with another Dataflow editor opened | 修复了在另一个 Dataflow 编辑器打开时使用工具导致的崩溃问题。 |
| 2026-05-22 | `8cfadbd3` | Dataflow Editor : fix Undo / redo issues with comment nodes | 修复了与注释节点相关的撤销/重做问题。 |

### 维护评价

**活跃维护**。该插件于 2026 年 4 月从实验阶段迁移至稳定版本，并于 2026 年 5 月持续进行了功能增强和 bug 修复。近期的提交集中在提升工具的稳定性和用户体验上。作为 Epic Games 官方维护的核心编辑器工具，预计将持续更新和完善。