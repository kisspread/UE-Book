# docs/xlarge/DataLink/index.md

# Motion Design Data Link

> Motion Design Data Link

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DataLink` (Runtime), `DataLinkDataTable` (Runtime), `DataLinkEdGraph` (UncookedOnly), `DataLinkEditor` (Runtime), `DataLinkHttp` (Runtime), `DataLinkJson` (Runtime), `DataLinkJsonEditor` (Runtime), `DataLinkWebSocket` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DataLink) | |

## 用途

Motion Design Data Link 是面向虚拟制片（Virtual Production）中 Motion Design 工作流的可视化数据管道插件。它提供了一套基于节点图的数据流系统，允许用户在编辑器中以可视化方式定义数据管道，将外部数据源的数据经过获取、解析、转换后，驱动 Motion Design 中的图形元素。

核心解决的问题：在直播、广播等场景中，需要将实时数据（体育比分、股票行情、选举结果、新闻滚动等）动态显示在屏幕上。DataLink 提供了从数据获取到最终呈现的完整可视化管道，用户无需编写代码即可配置复杂的数据流。

架构上，插件采用 **Template Node 模式**：编辑器节点（`UDataLinkEdNode`）内部持有一个运行时节点实例（`UDataLinkNode`），编辑器节点负责可视化表示，运行时节点负责实际的数据处理逻辑。图编译后生成运行时可执行的数据管道。

## 使用场景

- 你需要在直播画面中显示实时体育比分 → 用 DataLink + DataLinkHttp + DataLinkJson
- 你需要通过 WebSocket 接收实时数据流并更新屏幕图形 → 用 DataLink + DataLinkWebSocket
- 你需要从 DataTable 中读取配置数据并驱动 Motion Design 元素 → 用 DataLink + DataLinkDataTable
- 你需要在蓝图中发起数据链接请求 → 用 DataLinkEdGraph 中的 K2Node（已废弃，推荐使用 Data Link Executor Object）

## 模块概览

| 模块 | 类型 | 说明 |
|---|---|---|
| `DataLink` | Runtime | 核心模块，定义数据节点基类（`UDataLinkNode`）、数据图运行时逻辑、引脚定义等 |
| `DataLinkDataTable` | Runtime | DataTable 数据源集成，支持从 UE DataTable 读取数据 |
| `DataLinkEdGraph` | UncookedOnly | 可视化节点图编辑器，定义图结构、节点表示、Schema 规则和蓝图集成 |
| `DataLinkEditor` | Runtime | 编辑器工具和 UI 集成 |
| `DataLinkHttp` | Runtime | HTTP 数据源，支持从 REST API 获取数据 |
| `DataLinkJson` | Runtime | JSON 数据解析模块 |
| `DataLinkJsonEditor` | Runtime | JSON 相关的编辑器工具 |
| `DataLinkWebSocket` | Runtime | WebSocket 数据源，支持实时双向数据流 |

## 维护状态

### 近期更新

```
- f4b892b3a62d Motion Design Data Link: fix issue with pin corruption when undoing/redoing operations involving node creation/deletion and pin linking
- 94f961385e8e Motion Design: Moved scene state and data link plugins out of experimental into virtualproduction
```

- `f4b892b3a62d`: 修复了撤销/重做操作中涉及节点创建/删除和引脚连接时的引脚损坏问题，这是编辑器稳定性的关键修复
- `94f961385e8e`: 将插件从 Experimental 目录迁移到 VirtualProduction 目录，标志着从实验阶段正式进入 Virtual Production 工具链

### 维护评价

- **创建时间**: 2025-04-22，非常新的插件（不到 1 年）
- **版本状态**: Beta（`IsBetaVersion=true`），仍在积极开发中
- **最近活动**: 有实质性更新——包括 bug 修复和正式目录迁移
- **API 稳定性**: ⚠️ `UK2Node_DataLinkRequest` 已在 5.7 中标记废弃，推荐使用 Data Link Executor Object 替代，说明 API 仍在演进中
- **推荐**: 适合在 Virtual Production 项目中尝试使用，但需注意 Beta 状态可能带来 API 变更。不建议在生产环境中作为关键依赖使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DataLink)
- [DataLinkEdGraph 模块文档](./DataLinkEdGraph.md)

---

# docs/xlarge/DataLink/DataLinkEdGraph.md

# DataLinkEdGraph

> DataLink 可视化节点图编辑器模块

[← 返回插件总览](./index.md)

## 用途

DataLinkEdGraph 是 DataLink 插件的可视化编辑器表示层模块，负责将运行时数据管道以节点图的形式呈现在编辑器中。它不包含实际的数据处理逻辑（那些在 `DataLink` 核心模块中），而是专注于：

1. **图结构管理**（`UDataLinkEdGraph`）：管理节点图的整体结构，通过 ChangeId 机制跟踪变更状态，判断是否需要重新编译
2. **节点可视化**（`UDataLinkEdNode`）：将运行时数据节点（`UDataLinkNode`）包装为编辑器可操作的可视化节点，自动同步引脚结构
3. **输出标记**（`UDataLinkEdOutputNode`）：装饰性输出节点，标记图的输出端，编译器通过它遍历需要编译的节点
4. **编辑规则**（`UDataLinkEdGraphSchema`）：定义引脚类型（统一的 `PC_Data` 类型）、连接兼容性规则、循环检测、右键菜单等
5. **蓝图集成**（`UK2Node_DataLinkRequest`）：提供蓝图中的数据请求节点（已在 5.7 废弃）

该模块类型为 UncookedOnly，仅在编辑器和 PIE（Play In Editor）环境中加载，不会包含在打包产物中。

## 核心类

### UDataLinkEdGraph

继承自 `UEdGraph`，是 DataLink 数据图的编辑器表示。

| 方法 | 说明 |
|---|---|
| `FindOutputNode()` | 查找图中的装饰性输出节点 |
| `InitializeNodes()` | 初始化所有节点，重建过时节点的引脚以匹配其模板 |
| `DirtyGraph()` | 标记图已修改，触发 ChangeId 更新 |
| `IsCompiledGraphUpToDate()` | 检查编译后的图是否与当前编辑状态一致 |

**变更跟踪机制**：内部维护 `ChangeId` 和 `LastCompiledChangeId` 两个 GUID。当图发生修改时，`DirtyGraph()` 会重新生成 `ChangeId`；编译完成后，`LastCompiledChangeId` 被更新为当前 `ChangeId`。两者不匹配时 `IsCompiledGraphUpToDate()` 返回 false。

### UDataLinkEdNode

继承自 `UEdGraphNode`，是所有 DataLink 编辑器节点的基类。

| 方法 | 说明 |
|---|---|
| `SetTemplateNodeClass(InNodeClass, bReconstruct)` | 设置底层运行时节点类，可选自动重建节点 |
| `GetTemplateNode()` | 获取底层运行时节点实例 |
| `ForEachPinConnection(Function)` | 遍历所有引脚连接，回调接收当前引脚、连接的节点和连接的引脚 |
| `RefreshPins()` | 销毁并重建引脚，尽可能保留已有的连接关系 |
| `RequiresPinRecreation()` | 检查当前引脚结构是否与模板节点不匹配，需要重建 |
| `NotifyNodeChanged()` | 通知节点已变更 |
| `UpdateMetadata()` | 从模板节点更新缓存的元数据 |

**关键属性**：
- `TemplateNode`（`UPROPERTY(VisibleAnywhere, Instanced)`）：底层运行时数据节点实例，通过 `Instanced` 说明符确保每个编辑器节点拥有独立的模板节点副本

**引脚同步**：`SyncPins()` 私有方法负责将编辑器节点的引脚与模板节点的 `FDataLinkPin` 定义同步，支持输入和输出两个方向。

### UDataLinkEdOutputNode

继承自 `UDataLinkEdNode`，是一个装饰性输出