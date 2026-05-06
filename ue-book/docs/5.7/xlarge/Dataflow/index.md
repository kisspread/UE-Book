# Editor DataflowGraph

> Editor Dataflow Graph

| 属性 | 值 |
|---|---|
| 中文名 | 数据流图编辑器 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（数据流节点资源） |
| 模块 | `DataflowAssetTools` (Runtime), `DataflowEditor` (Runtime), `DataflowEnginePlugin` (Runtime), `DataflowNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-10-02 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Dataflow) | |

## 总体用途

Dataflow 是一个基于节点的可视化编程框架，专为编辑器内的几何体、动画等数据处理而设计。它允许艺术家和技术美术通过拖拽连接节点来构建数据流管道，实现程序化建模、几何体变形、属性传递等复杂操作，无需编写 C++ 代码。该插件处于实验阶段，目前集中用于几何体处理领域，未来可能扩展至更多数据类型。

## 模块列表

| 模块 | 一句话总结 |
|---|---|
| `DataflowAssetTools` | 提供数据流资产的导入、导出、管理等工具函数。 |
| `DataflowEditor` | 集成数据流编辑器的 UI、交互、节点编辑功能，负责编辑体验。 |
| `DataflowEnginePlugin` | 允许在运行时（Runtime）环境中解析并执行数据流图，支持动态结果。 |
| `DataflowNodes` | 内置各种基础节点（几何体创建、变换、布尔运算、属性处理等），构成节点库。 |

各模块详细文档：  
- [DataflowAssetTools.md](DataflowAssetTools.md)  
- [DataflowEditor.md](DataflowEditor.md)  
- [DataflowEnginePlugin.md](DataflowEnginePlugin.md)  
- [DataflowNodes.md](DataflowNodes.md)

## 使用场景

- **程序化建模**：通过节点组合生成复杂几何体（如楼梯、管道、建筑物框架），提高迭代效率。
- **几何体处理流水线**：对导入的静态网格体执行自动化操作，如顶点变形、UV 映射、法线调整。
- **属性传递**：将自定义数据（顶点颜色、材质 ID）从源网格体传递到目标网格体。
- **编辑器内即时预览**：在编辑器中拖动节点或修改参数时，实时看到几何体变化，快速调试。
- **运行时动态生成**：利用 `DataflowEnginePlugin` 在游戏运行时动态生成或变形几何体（需额外配置）。

## 相关链接

- [源码 (5.7)](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Dataflow)
- 官方文档：暂无（实验性插件，文档未公开发布）

> **注意**：该插件标记为`IsExperimentalVersion=true`，API 和行为可能在后续版本中发生非向后兼容的变更，请谨慎用于生产项目。