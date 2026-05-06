# Gizmo Editor Mode

> Editor mode to manage InteractiveToolFramework based global TRS gizmos

| 属性 | 值 |
|---|---|
| 中文名 | Gizmo 编辑模式 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GizmoEdMode` (Editor), `LightGizmos` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-11-10 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/GizmoEdMode) | |

## 总体用途

Gizmo Editor Mode 是一个实验性的编辑器插件，它为 **InteractiveToolFramework** 提供全局的 **TRS（平移 / 旋转 / 缩放）Gizmo** 支持。该插件定义了专门的编辑器模式，允许用户通过熟悉的 Gizmo 交互方式操作场景中的物体，同时与基于 ITF 的工具链无缝集成。其核心目标是统一不同工具对变换 Gizmo 的使用方式，减少重复实现。

## 模块列表

| 模块 | 一句话总结 |
|---|---|
| `GizmoEdMode` | 提供编辑器模式入口、Gizmo 组件管理及与 ITF 的桥接层（详见 [GizmoEdMode.md](GizmoEdMode.md)）。 |
| `LightGizmos` | 针对灯光对象提供专属 Gizmo 绘制与交互支持（详见 [LightGizmos.md](LightGizmos.md)）。 |

## 使用场景

- 你正在开发或使用基于 `InteractiveToolFramework` 的自定义编辑工具，希望复用标准 TRS Gizmo 而无需从零构建。
- 你需要在一个统一的编辑器模式下切换不同变换操作（平移 / 旋转 / 缩放），并保持与其他 ITF 工具一致的交互体验。
- 你的项目涉及灯光对象的空间调整，希望获得专门优化的 Gizmo 反馈（例如强度、衰减范围的可视化）。

## 相关链接

- [源码（主目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GizmoEdMode)
- [GizmoEdMode 模块文档](GizmoEdMode.md)
- [LightGizmos 模块文档](LightGizmos.md)