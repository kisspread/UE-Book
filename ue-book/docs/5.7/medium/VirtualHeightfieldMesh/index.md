# Virtual Heightfield Mesh

> Mesh renderer for virtual texture heightfields

| 属性 | 值 |
|---|---|
| 中文名 | 虚拟高度场网格 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（运行时模块 + 编辑器模块） |
| 模块 | `VirtualHeightfieldMesh` (Runtime), `VirtualHeightfieldMeshEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-23 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/VirtualHeightfieldMesh) | |

## 总体用途

该插件为**虚拟纹理高度场**提供高性能网格渲染能力。其核心是将高度场数据（来自虚拟纹理）转化为可渲染的网格几何体，适用于大规模地形或高度场场景，利用虚拟纹理的分块、流送技术极大降低显存开销和绘制调用数量。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| [VirtualHeightfieldMesh](VirtualHeightfieldMesh.md) | Runtime | 运行时渲染模块，负责高度场网格的生成、顶点缓冲、流送及渲染管线 |
| [VirtualHeightfieldMeshEditor](VirtualHeightfieldMeshEditor.md) | Editor | 编辑器模块，提供高度场网格资产的操作工具、细节面板及预览支持 |

## 使用场景

- 你需要渲染**超大规模地形**，传统网格或 Landscape 无法满足性能需求。
- 项目已经使用了**运行时虚拟纹理（RVT）** 存储高度场数据，需要一种轻量级网格化方案来显示这些地形。
- 希望利用虚拟纹理的自动 LOD 和流送机制，减少 CPU/GPU 负担，同时保持视觉质量。

## 相关链接

- [源码（主仓库）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/VirtualHeightfieldMesh)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/)（该插件暂无独立文档页）