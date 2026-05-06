# Mesh Resizing

> Mesh Resizing

| 属性 | 值 |
|---|---|
| 中文名 | 网格尺寸调整 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（数据流节点、编辑器工具资源） |
| 模块 | `MeshResizingCore` (Runtime), `MeshResizingEditorTools` (Runtime), `MeshResizingEngine` (Runtime), `MeshResizingDataflowNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-15 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MeshResizing) | |

## 总体用途

Mesh Resizing 插件提供了一组用于网格尺寸调整（重采样、重拓扑、细分）的工具链。它包含核心算法库、编辑器交互工具、运行时引擎集成以及 Dataflow 节点，允许用户在编辑器蓝图、运行时脚本及数据流图中对静态网格体进行分辨率/大小的程序化修改。该插件处于实验阶段，旨在探索高效、动态的网格自适应方案。

## 模块列表

| 模块 | 类型 | 一句话说明 |
|---|---|---|
| [MeshResizingCore](MeshResizingCore.md) | Runtime | 核心数据结构和算法，负责网格细分、重采样及 RBF 插值等底层计算 |
| [MeshResizingEditorTools](MeshResizingEditorTools.md) | Runtime | 编辑器工具集成，提供交互操作面板、Landmark 工具及自定义操作入口 |
| [MeshResizingEngine](MeshResizingEngine.md) | Runtime | 运行时引擎集成，允许在游戏或模拟过程中动态调整网格参数 |
| [MeshResizingDataflowNodes](MeshResizingDataflowNodes.md) | Runtime | 数据流节点集合，可在 Dataflow 图表中组合使用以构建网格大小调整管线 |

> 各模块的详细 API、依赖关系及用法请参阅对应模块文档。

## 使用场景

- **程序化建筑**：在运行时根据玩家距离或性能预算动态调整建筑模型的面数。
- **动态 LOD 生成**：使用细分算法为角色或道具生成多级 LOD，而非预烘焙静态 LOD。
- **雕刻/建模工具**：在编辑器中通过 Landmark 工具对特定区域进行局部细分或简化。
- **数据流自动化**：在 Dataflow 图表中组合网格调整节点，实现批量处理或条件化修改。

## 维护状态

### 近期更新
- 2025-09-29 `92ddeeb8` — [MeshResizing] Fixed vertices per task alocation bug（修复每个任务分配的顶点数 bug）
- 2025-09-23 `ca2d126b` — Dataflow Editor: make the tool add node buttons work for tools that don't operate on ManagedArrayCol（使 Dataflow 编辑器中的工具添加节点按钮对非 ManagedArray 工具生效）
- 2025-08-19 `d66ea4c2` — Dataflow landmark tool : fix some pointer checks（修复 Dataflow Landmark 工具中的指针检查）
- 2025-08-19 `a5c868d7` — Dataflow Landmark tool : fix the tool marking the node invalid even when no changes were made（修复 Landmark 工具在无改动时误报节点无效的问题）
- 2025-08-15 `e79d88de` — Fix possible divide by zero in RBFInterpolation when the mesh is empty（修复空网格时 RBF 插值的除零问题）

### 维护评价
该插件创建于 2025‑08‑15，仍处于实验阶段。从活跃的 commit 日志看（至今不到两个月已有多次功能修复与改进），团队正在积极迭代。目前所有更新均围绕核心算法稳固性和 Dataflow 工具集成，未发现废弃标记或长期停滞。**推荐用于原型验证和测试环境**，生产项目使用前应充分评估其稳定性和性能。

## 相关链接

- [源码主目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MeshResizing)
- [MeshResizingCore 模块文档](MeshResizingCore.md)
- [MeshResizingEditorTools 模块文档](MeshResizingEditorTools.md)
- [MeshResizingEngine 模块文档](MeshResizingEngine.md)
- [MeshResizingDataflowNodes 模块文档](MeshResizingDataflowNodes.md)