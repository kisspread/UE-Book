# Alembic Importer

> Support importing Alembic files（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | Alembic导入器 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AlembicImporter` (Editor), `AlembicLibrary` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2022-01-26 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/AlembicImporter) | |

## 用途

该插件的核心功能是将 Alembic (.abc) 格式的文件导入到 Unreal Engine 5 中。Alembic 是一种开放的行业标准格式，专门用于在不同数字内容创建 (DCC) 软件之间交换复杂的几何体和动画数据。该插件解决了从 Maya、Houdini、Blender 等软件导出流体、布料、粒子、刚体模拟结果以及角色动画缓存并将其无缝集成到 UE5 场景中的问题，主要服务于影视和游戏制作流程。

## 模块列表

- **AlembicImporter**: 主要导入模块，负责处理文件解析、网格体构建、动画和几何缓存序列化等核心编码逻辑。
- **AlembicLibrary**: 底层 Alembic 库模块，封装了官方 Alembic SDK，为上层的 `AlembicImporter` 模块提供稳定的数据读取接口。

## 使用场景

- 你需要从 Houdini 中导出复杂的流体或粒子模拟结果，并将其作为可播放的几何缓存导入到 UE5 中。
- 你在 Maya 中制作了角色动画，并希望以缓存的形式（而非骨骼）导入到 UE5 用于过场动画或实时演示。
- 你需要导入高精度的 3D 扫描数据（如 .abc 格式），用于影视虚拟制片或游戏环境制作。
- 你正在使用其他 DCC 工具制作刚体破碎动画，并希望将其结果导入 UE5 作为动画序列播放。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/AlembicImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/AlembicImporter/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/AlembicImporter/Tests)