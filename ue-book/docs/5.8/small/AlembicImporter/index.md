# Alembic Importer

> Support importing Alembic files

| 属性 | 值 |
|---|---|
| 中文名 | Alembic 导入器 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AlembicImporter` (Editor), `AlembicLibrary` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2022-01-26 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/AlembicImporter) | |

## 用途

AlembicImporter 插件提供了将 `.abc` 格式的 Alembic 文件导入到 Unreal Engine 5 的能力。Alembic 是三维动画行业广泛使用的开放格式标准，主要用于存储和交换几何体、动画（如顶点动画、变形）、粒子和相机数据。该插件解决了在 DCC 软件（如 Maya, Houdini, Blender）中制作的高质量动画、特效模拟和复杂资产，与 UE5 引擎进行数据互通的需求，是影视、虚拟制片和高级游戏开发中重要的流程环节。

## 使用场景

-   你从 Houdini 中导出了复杂的流体、布料或刚体模拟的缓存动画序列，希望导入 UE5 中用于最终渲染或实时预览。
-   你从 Maya 或 Blender 中为角色制作了复杂的骨骼绑定或 Blend Shape 动画，并希望以 Alembic 格式导入 UE5 以保持最高保真度。
-   你需要导入包含复杂拓扑变化或顶点动画（如生长、形变）的模型资产，而骨骼或 Morph Target 方案无法完美支持。

## 模块列表

| 模块 | 说明 |
|---|---|
| `AlembicImporter` | **核心导入模块**，负责 `.abc` 文件的解析、资产创建和任务调度。 |
| `AlembicLibrary` | **底层库模块**，封装了 Alembic SDK 的核心功能，提供网格、动画数据的读写接口。 |

*详细的 API 和函数说明请参考各子模块文档。*

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/AlembicImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/AlembicImporter/)
- [AlembicImporter 模块文档](AlembicImporter.md)
- [AlembicLibrary 模块文档](AlembicLibrary.md)

---
*本文档基于源码自动生成，更详细的用法和 API 参考请查看子模块文档。*