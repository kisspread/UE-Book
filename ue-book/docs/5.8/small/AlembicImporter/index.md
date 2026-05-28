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
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/AlembicImporter) | |

## 用途

此插件提供了将 Alembic (.abc) 文件格式导入 Unreal Engine 的功能。Alembic 是影视和游戏行业广泛使用的开放标准格式，用于交换复杂的 3D 几何体（如角色动画、流体模拟、布料解算等）缓存数据。该插件解决的核心问题是让 Unreal Engine 能够无缝接入基于 Alembic 的生产流程，使美术人员可以直接将在 Maya、Houdini、Blender 等 DCC 软件中生成的动态资产导入引擎，用于实时动画、过场动画或特效场景。

## 使用场景

-   你在制作一个需要复杂角色动画的游戏或影视项目，动画是在 Maya 中使用关键帧或动力学解算完成的，你希望将最终动画缓存作为 Alembic 文件导入 UE 用于实时播放或过场动画。
-   你是一名技术美术，在 Houdini 中制作了程序化的破坏或流体模拟，需要将结果以 Alembic 文件的形式导入 UE 场景中。
-   你的团队工作流程要求从其他 DCC 软件导入高精度动态模型（如面部表情捕捉数据），并希望保留其逐帧的顶点动画信息。

## 模块列表

| 模块 | 说明 |
|---|---|
| `AlembicLibrary` | 底层库模块，封装了 Alembic SDK 的核心读取功能，负责解析 .abc 文件并提取几何体、动画数据。 |
| `AlembicImporter` | 上层导入器模块，负责与虚幻编辑器的资产系统交互，处理导入设置、任务调度并将其转化为引擎可识别的资源（如 GeometryCache、StaticMesh）。 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/AlembicImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/AlembicImporter/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/AlembicImporter/Tests)