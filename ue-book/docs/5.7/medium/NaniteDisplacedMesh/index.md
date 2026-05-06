# Nanite Displaced Mesh

> Asset and component types that provide a basic pre-displacement pipeline for Nanite meshes

| 属性 | 值 |
|---|---|
| 中文名 | Nanite 置换网格 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资源与组件类型） |
| 模块 | `NaniteDisplacedMesh` (Runtime), `NaniteDisplacedMeshEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-07 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NaniteDisplacedMesh) | |

## 总体用途

Nanite Displaced Mesh 提供了 **预位移（pre-displacement）管线的资产与组件**，允许开发者对静态网格体应用高度位移贴图，并在 Nanite 渲染管线中使用。它解决传统位移贴图（如 Tessellation）与 Nanite 不兼容的问题，通过提前在编辑器或构建时生成位移后的顶点数据，实现高效、无损细节的高性能渲染。

## 模块列表

| 模块 | 类型 | 一句话总结 | 详细文档 |
|---|---|---|---|
| `NaniteDisplacedMesh` | Runtime | 核心运行时模块，定义 `UNaniteDisplacedMesh` 资产与 `UNaniteDisplacedMeshComponent` 组件，管理位移数据与渲染。 | [🔗 NaniteDisplacedMesh.md](./NaniteDisplacedMesh.md) |
| `NaniteDisplacedMeshEditor` | Editor | 提供编辑器内创建/编辑位移资产的 UI、资产工厂、细节面板等工具。 | [🔗 NaniteDisplacedMeshEditor.md](./NaniteDisplacedMeshEditor.md) |

## 使用场景

- 在 Nanite 项目中需要为静态网格体（如地形、岩石、建筑细节）添加复杂位移细节（如凹凸、裂纹）。
- 通过预烘焙位移贴图，在运行时无需额外细分，保持 Nanite 的高性能渲染优势。
- 需要资产级编-译时位移处理，而非运行时动态细分。

## 相关链接

- [源码（5.7）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NaniteDisplacedMesh)
- [NaniteDisplacedMesh 模块文档](./NaniteDisplacedMesh.md)
- [NaniteDisplacedMeshEditor 模块文档](./NaniteDisplacedMeshEditor.md)