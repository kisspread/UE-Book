# Dynamic Wind

> Extremely experimental dynamic wind support for Nanite foliage.

| 属性 | 值 |
|---|---|
| 中文名 | 动态风力 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（未指定） |
| 模块 | `DynamicWind` (Runtime)，`DynamicWindEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-03 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/DynamicWind) | |

## 用途

该插件为 **Nanite 植被** 提供了实验性的动态风场支持。它允许你在场景中定义并应用实时风力，使 Nanite 树叶、草等植被元素产生逼真的风吹变形效果。通过结合全局风向和每实例旋转数据，实现更自然的动态交互。

## 模块概览

| 模块 | 类型 | 一句话总结 |
|------|------|------------|
| `DynamicWind` | Runtime | 核心运行时，负责风场模拟、数据传递及线程安全同步，驱动 Nanite 植被变形。 |
| `DynamicWindEditor` | Editor | 编辑器扩展，提供风场数据设置、编辑及与骨骼网格体等组件的集成工具。 |

详细信息请参阅各模块文档：[DynamicWind](DynamicWind.md)，[DynamicWindEditor](DynamicWindEditor.md)

## 使用场景

- 你在使用 **Nanite** 渲染技术制作开放世界或自然环境时，需要为植被添加动态风效果。
- 需要精细控制局部风向、风力强度及每实例旋转对风的影响（如不同方向的风导致草/树枝不同弯曲）。
- 使用程序化放置的植被（如 `ProceduralVegetationEditor` 放置的实例），并希望风场数据能自动传递到渲染层。

## 相关链接

- [插件根目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/DynamicWind)
- [运行时模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/DynamicWind/Source/DynamicWind)
- [编辑器模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/DynamicWind/Source/DynamicWindEditor)
- 官方文档：暂无（实验性插件）