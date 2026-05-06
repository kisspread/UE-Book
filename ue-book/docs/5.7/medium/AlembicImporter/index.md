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
| 创建时间 | 2025-07-14 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Importers/AlembicImporter) | |

## 总体用途

Alembic Importer 插件用于将 Alembic（.abc）缓存文件导入 Unreal Engine，支持几何缓存（Geometry Cache）和动画数据。它是制作电影级过场动画、演算动画或动态变形物体的核心工具，允许艺术家从 DCC 工具（如 Maya、Houdini）导出复杂的变形网格，并在 UE 中直接回放，而无需依赖骨骼绑定或蒙皮。

## 模块列表

| 模块 | 一句话说明 | 详细文档 |
|---|---|---|
| `AlembicImporter` (Editor) | 导入 UI、资产工厂、线程管理等编辑器侧逻辑 | [AlembicImporter.md](./AlembicImporter.md) |
| `AlembicLibrary` (Editor) | 底层 Alembic 库封装、数据烘焙和读取实现 | [AlembicLibrary.md](./AlembicLibrary.md) |

## 使用场景

- **电影级过场动画**：使用第三方软件模拟的布料、流体、爆炸效果，导出为 Alembic 后直接在 UE 中重放。
- **建筑可视化**：导入由 BIM 或 CAD 工具导出的动态组件动画。
- **角色特效**：导入毛发、肌肉等非骨骼驱动的变形动画。
- **工业展示**：展示机械零件的拆解动画或变形过程。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Importers/AlembicImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/AlembicImporter/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Importers/AlembicImporter/Tests)（需自行确认路径）