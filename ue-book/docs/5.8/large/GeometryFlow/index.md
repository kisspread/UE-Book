# GeometryFlow

> Geometry DataFlow Graph（几何数据流图）

| 属性 | 值 |
|---|---|
| 中文名 | 几何数据流图 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（几何处理数据流节点与资产） |
| 模块 | `GeometryFlowCore` (Runtime), `GeometryFlowMeshProcessing` (Runtime), `GeometryFlowMeshProcessingEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-11-24 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GeometryFlow) | |

## 用途

GeometryFlow 是一个**节点图式的几何数据处理框架**，用于实现昂贵（高计算开销）的几何处理操作。它将几何处理流程抽象为数据流图（DataFlow Graph），每个节点代表一个处理步骤，节点之间通过数据管线连接，形成可组合、可复用的处理管线。

其核心应用场景是**高精度资产的游戏化处理**：将高分辨率源网格体 + 材质，通过数据流图处理为游戏可用的静态网格体资产 + 材质实例 + 碰撞几何体。`GenerateStaticMeshLODAssetTool` 将这个流程暴露为 Modeling Mode 中的工具，供用户在编辑器中直接使用。

该插件本身是**实验性原型**（Hidden、未默认安装），依赖 GeometryProcessing 和 MeshModelingToolsetExp 插件提供底层几何算法。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `GeometryFlowCore` | Runtime | 核心数据流图引擎，定义节点、数据管线、图执行等基础架构 |
| `GeometryFlowMeshProcessing` | Runtime | 网格体处理节点实现，包含 LOD 生成、网格简化、碰撞体生成等几何操作节点 |
| `GeometryFlowMeshProcessingEditor` | Editor | 编辑器集成，将数据流图处理流程暴露为 Modeling Mode 工具（如 GenerateStaticMeshLODAssetTool） |

## 使用场景

- 你需要将高精度雕刻模型转换为游戏可用的 LOD 静态网格体
- 你需要可视化地组合多个几何处理步骤（减面、UV 重投影、碰撞体生成等），形成可复用的处理管线
- 你在开发 Modeling Mode 工具，需要一个可配置的几何处理后端
- 你需要批量处理大量高精度资产，使其适配游戏引擎的性能要求

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到新 API |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 析构函数统一改为 `= default` |
| 2025-10-23 | `3acea6cd` | add geometric tolerance to mesh->convex hull simplification path, to allow simplification below the [threshold] | 为网格体到凸包简化路径添加几何容差参数 |
| 2025-07-10 | `9803c443` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. | 添加内联生成宏优化编译 |
| 2025-05-31 | `52e3dac1` | Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of ty | 修正 DLL 导出声明位置 |

### 维护评价

- **实验性状态**：插件标记为 `IsExperimentalVersion=true`，且 `Hidden=true`、`Installed=false`，属于 Epic 内部原型，从未正式公开发布
- **活跃度**：近期 commit 均为全引擎范围的代码规范化批量修改（UE_LOG 迁移、析构函数标准化、DLL 导出修正等），非该插件自身的功能性更新
- **实质性更新**：2025-10-23 的凸包简化容差变更是最近一次针对该插件实际功能的改动
- **风险**：作为隐藏的实验性插件，API 可能随时发生变化或被移除，不建议在正式项目中依赖

⚠️ **注意**：此插件为实验性原型，Hidden 且未默认安装，启用需手动操作。不推荐用于生产环境。

## 模块依赖

从 Build.cs 提取（需手动启用 `GeometryProcessing` 和 `MeshModelingToolsetExp` 插件）：

| 模块 | 用途 |
|---|---|
| `GeometryProcessing` | 底层几何算法（网格体处理、布尔运算、体素化等） |
| `MeshModelingToolsetExp` | 实验性建模工具集，提供 Modeling Mode 工具框架 |
| `MeshConversion` | 网格体格式转换 |
| `DynamicMesh` | 动态网格体数据结构 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GeometryFlow)
- [GeometryProcessing 插件文档](../GeometryProcessing/index.md)
- [MeshModelingToolsetExp 插件文档](../MeshModelingToolsetExp/index.md)