# Mesh Resizing

> Mesh Resizing

| 属性 | 值 |
|---|---|
| 中文名 | 网格缩放 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、数据流节点） |
| 模块 | `MeshResizingCore` (Runtime), `MeshResizingEditorTools` (Runtime), `MeshResizingEngine` (Runtime), `MeshResizingDataflowNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-12-09 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshResizing) | |

## 用途

Mesh Resizing 插件提供基于 Dataflow 框架的网格缩放与变形功能。该插件并非简单的均匀缩放工具，而是专注于对网格进行**可控的、基于区域的变形操作**，用户可以通过绘制蒙版（Paint Mask）来定义影响区域，然后对选中区域进行拉伸、压缩等操作。

该插件与 UE5 的 Dataflow 系统深度集成，通过可视化节点图的方式构建网格变形工作流，适合需要精细控制网格形态的美术和工具开发场景。

## 使用场景

- 你需要对角色模型的特定部位（如手臂、腿部）进行长度调整，而不影响整体比例
- 你需要通过绘制蒙版来精确控制网格变形的影响区域和强度
- 你需要构建可复用的网格处理工作流（Dataflow 节点图）
- 你需要在编辑器中交互式地预览网格变形效果

## 蓝图用法

> ⚠️ 该插件为实验性状态，公开的蓝图 API 较少。主要通过 Dataflow 节点图进行操作。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `PaintTool` | 使用画笔工具在网格上绘制变形蒙版 | Dataflow 节点 |
| `LassoTool` | 使用套索工具选取网格区域 | Dataflow 节点 |
| `Resize` | 执行网格缩放操作 | Dataflow 节点 |

### 使用示例（蓝图描述）

1. 在编辑器中创建 Dataflow Asset
2. 添加网格输入节点（如 Skeletal Mesh 或 Static Mesh 源）
3. 连接 PaintTool 或 LassoTool 节点，定义影响区域
4. 在视口中交互式绘制蒙版权重
5. 连接 Resize 节点，设置缩放参数
6. 将结果输出到目标网格

## C++ 用法

> ⚠️ 该插件为实验性状态，大量接口可能在后续版本中变更。

### 头文件引入

```cpp
#include "MeshResizingEngine.h"
```

### 基本用法

```cpp
// 引入 Dataflow 相关头文件
#include "Dataflow/DataflowConnection.h"

// MeshResizing 的主要操作通过 Dataflow 节点系统进行，
// C++ 端主要涉及自定义节点的扩展
```

### 进阶用法

扩展自定义 Dataflow 节点以集成到网格缩放工作流中。参考 `MeshResizingDataflowNodes` 模块中的节点实现模式。

## Demo 示例

> ⚠️ 当前插件为实验性状态，公开 API 有限。建议通过 Dataflow 编辑器界面体验功能。

最小使用流程：

1. 在 `Plugins` 面板中启用 `Mesh Resizing`（需手动启用）
2. 创建 Dataflow Asset
3. 在 Dataflow 编辑器中添加 Mesh Resizing 相关节点
4. 连接节点并进行交互式编辑

## 模块依赖

该插件各模块的主要依赖如下（基于模块命名推断，实验性插件依赖可能随版本变更）：

| 模块 | 用途 |
|---|---|
| `GeometryCore` | 几何数据结构与算法基础 |
| `GeometryFramework` | 几何处理框架 |
| `Dataflow` | Dataflow 节点图系统 |
| `DataflowCore` | Dataflow 核心类型定义 |
| `MeshResizingCore` | 本插件核心数据类型（内部依赖） |
| `MeshResizingEngine` | 本插件引擎逻辑（内部依赖） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-05-12 | `a7802337` | Dataflow: | Dataflow 相关更新（信息不完整） |
| 2026-03-16 | `1f05dc85` | Adding includes before upcoming header cleanup. | 头文件清理前补充 include，预防编译问题 |
| 2026-01-30 | `7b60de76` | Dataflow : add support to lasso to the paint tool by leveraging the newly added feature in the mesh | 为绘制工具添加套索选择支持 |
| 2025-12-19 | `f86e1e20` | Dataflow : update a lot of nodes to use the new rendering system | 大量 Dataflow 节点迁移到新渲染系统 |

### 维护评价

- **创建时间**：2024-12-09，约 2 年历史
- **维护状态**：活跃维护中，最近一次更新在 2026 年 5 月，持续有功能迭代
- **实验性标记**：`IsExperimentalVersion=true`，`EnabledByDefault=false`，需手动启用
- **已知限制**：
  - API 可能随版本大幅变更
  - 插件初始提交（2024-12-09）仅为样板代码，功能逐步迭代中
  - 文档 URL 为空，官方文档暂未公开
- **推荐程度**：适合早期探索和原型开发，不建议用于生产环境。如果你需要在生产项目中使用网格变形功能，建议关注该插件的后续正式发布。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshResizing)
- 官方文档：暂无
- 测试用例：暂未发现公开测试用例