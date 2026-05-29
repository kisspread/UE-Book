# Nanite Displaced Mesh

> Asset and component types that provide a basic pre-displacement pipeline for Nanite meshes

| 属性 | 值 |
|---|---|
| 中文名 | Nanite置换网格 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产类型） |
| 模块 | `NaniteDisplacedMesh` (Runtime), `NaniteDisplacedMeshEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-05-06 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NaniteDisplacedMesh) | |

## 用途

这是一个**实验性插件**，专门为 **Nanite 网格**提供**预置换（Pre-Displacement）** 处理管线。它解决的核心问题是：Nanite（UE5的虚拟化微多边形几何系统）本身不支持运行时置换贴图（Displacement Map）驱动的几何形变。此插件通过提供一套离线预处理工具和资产类型，允许开发者将置换效果**烘焙**到Nanite网格中，从而在运行时获得具有高精度表面细节的Nanite资产。

简单来说，它填补了Nanite在置换效果方面的空白，但代价是置换过程发生在编辑器/构建阶段，而非游戏运行时。

## 使用场景

- 你需要在Nanite资产（如高精度建筑、地形岩石、产品模型）上应用基于高度图的**几何细节**，但Nanite本身不支持运行时置换。
- 你希望在保持Nanite海量几何细节优势的同时，为静态网格添加额外的、由纹理驱动的表面起伏和深度。
- 你的美术管线或技术美术流程允许在资产导入或准备阶段进行预计算。
- **典型用例**：建筑可视化中的砖墙/瓦片纹理、地形中的岩石表面细节、产品渲染中的雕刻或磨损效果。

## 模块列表

本插件包含两个模块，分别负责运行时数据和编辑器工具：

- **`NaniteDisplacedMesh`** (Runtime)：提供核心的运行时资产类型（`UNaniteDisplacedMesh`）和组件类型（`UNaniteDisplacedMeshComponent`），用于在游戏或应用中加载和渲染经过预置换处理的Nanite网格。
- **`NaniteDisplacedMeshEditor`** (Editor)：提供在UE编辑器中创建、编辑和导入`UNaniteDisplacedMesh`资产所需的工具、工厂类和编辑器扩展。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NaniteDisplacedMesh)
- [官方文档]()（暂无）
- [测试用例]()（未发现独立测试用例）