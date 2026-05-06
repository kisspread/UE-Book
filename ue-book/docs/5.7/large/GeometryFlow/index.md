# GeometryFlow

> Geometry DataFlow Graph

| 属性 | 值 |
|---|---|
| 中文名 | 几何流程图 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资源） |
| 模块 | `GeometryFlowCore` (Runtime), `GeometryFlowMeshProcessing` (Runtime), `GeometryFlowMeshProcessingEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-11-10 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GeometryFlow) | |

## 总体用途

GeometryFlow 是一个基于 DataFlow 图架构的几何处理框架。它允许用户通过**节点化流程图（Graph）**的方式，组合和编排几何处理步骤（如网格简化、重拓扑、布尔运算、参数化等），实现可视化、可复用的几何处理管线。

该插件构建在 `GeometryProcessing` 库和 `MeshModelingToolsetExp` 工具集之上，将底层几何算法封装为可连接的节点，使得美术和技术美术不需要编写代码即可快速原型化和执行复杂的几何变换。

## 模块列表

| 模块 | 类型 | 一句话描述 |
|---|---|---|
| [GeometryFlowCore](GeometryFlowCore.md) | Runtime | 核心框架：定义节点系统、数据类型、执行引擎和基础节点 |
| [GeometryFlowMeshProcessing](GeometryFlowMeshProcessing.md) | Runtime | 网格处理节点库：封装常用网格算法（简化、平滑、布尔等）为 DataFlow 节点 |
| [GeometryFlowMeshProcessingEditor](GeometryFlowMeshProcessingEditor.md) | Editor | 编辑器扩展：提供可视化图编辑器、节点调色板、资产创建与调试工具 |

## 使用场景

- 你需要在 UE 中实现程序化建模或自动化几何处理管线，但希望避免编写 C++ 代码。
- 你想将多个几何处理步骤（如先重拓扑再 UV 展开）串联成可复用的模板。
- 你在开发自定义建模工具，希望利用 DataFlow 的输入/输出节点系统快速迭代算法组合。
- 适合技术美术、关卡美术快速原型几何变形、修复或优化网格。

## 维护状态

### 近期更新

- 2025-07-10 `9803c443` — 添加 UE_INLINE_GENERATED_CPP_BY_NAME 到对应 .gen.cpp 的源文件（编译维护）
- 2025-05-31 `52e3dac1` — 更新头文件，将 DLL 存储从类型移到方法/静态变量（编译兼容）
- 2024-12-16 `dbb51bc5` — GeometryFlow: 清理节点注册逻辑
- 2024-12-13 `1d69cf7b` — 几何处理单元测试：消除警告和其他问题以准备启用测试
- 2024-11-10 `66e9bb39` — 移除代码库中所有 UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 作用域

### 维护评价

GeometryFlow 是一个实验性插件（版本 0.1），创建于 2024 年 11 月，至今约 8 个月。近期更新集中在编译兼容性修复和内部清理上，没有添加新功能或公开新节点。由于尚处于早期开发阶段，API 和架构可能发生较大变化，**不建议在生产项目中直接依赖**。对于想了解 UE 中 DataFlow 架构与几何处理结合的技术探索，值得研究。

## 相关链接

- [源码（插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GeometryFlow)
- [GeometryFlowCore 模块文档](GeometryFlowCore.md)
- [GeometryFlowMeshProcessing 模块文档](GeometryFlowMeshProcessing.md)
- [GeometryFlowMeshProcessingEditor 模块文档](GeometryFlowMeshProcessingEditor.md)