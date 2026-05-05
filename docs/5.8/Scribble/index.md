# Scribble

> A user interface plugin providing scribble capabilities.

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（具体内容未指定） |
| 模块 | `Scribble` (Runtime), `ScribbleEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-10-29 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/Scribble) | |

## 用途

Scribble 是一个实验性的 UI 插件，旨在为 Unreal Engine 的用户界面系统提供“涂鸦”或“手绘”能力。它允许开发者在运行时或编辑器中，在 UI 元素上绘制自由形式的线条、形状或注释，可能用于实现游戏内的绘图工具、草图功能或艺术化 UI 效果。

## 使用场景

- 你需要在游戏内创建一个简单的绘画板或签名功能。
- 你正在开发一个教育类应用，需要学生在 UI 上进行手写或绘图。
- 你希望为 UI 原型或调试界面添加临时的、手绘风格的标注。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| `Scribble` | Runtime | 提供核心的涂鸦绘制功能、数据模型和运行时 API。 |
| `ScribbleEditor` | Editor | 提供在 Unreal Editor 中创建、编辑和预览涂鸦资产的工具和界面。 |

## 蓝图用法

由于插件处于实验阶段且未默认启用，具体的蓝图节点需参考模块文档。核心功能预计围绕 `Scribble` 运行时模块提供的类和函数展开，用于在 Widget 或 Viewport 上进行绘制操作。

## C++ 用法

详细的 C++ API 和使用示例请参阅各模块文档。
- **运行时模块 (`Scribble`)**: 用于在游戏逻辑中控制涂鸦的创建、更新和渲染。
- **编辑器模块 (`ScribbleEditor`)**: 用于扩展编辑器功能，集成自定义资产编辑器。

## Demo 示例

一个完整的最小示例应包含创建涂鸦组件、设置绘制参数并将其添加到 UI 层级中。具体代码结构请参考 `Scribble` 模块文档中的示例。

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。具体依赖关系请查阅各模块的 `Build.cs` 文件。

## 维护状态

### 近期更新

该插件创建于 2025 年 10 月底，属于非常新的实验性功能。目前没有可供查询的近期更新历史。

### 维护评价

- **状态**: **实验性新功能**。插件创建时间极短，且位于 `Experimental` 目录下，`EnabledByDefault` 为 `false`。
- **评价**: 这是一个全新的、处于早期开发阶段的插件。其 API 和功能可能会发生重大变化。目前不建议在生产项目中使用，但非常适合用于技术预研和原型开发。请密切关注后续版本的更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/Scribble)
- [Scribble 模块文档](Scribble.md)
- [ScribbleEditor 模块文档](ScribbleEditor.md)