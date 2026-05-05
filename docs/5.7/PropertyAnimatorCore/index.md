# Property Animator Core

> Re-usable behaviors to control properties at runtime and in editor

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `PropertyAnimatorCore` (Runtime), `PropertyAnimatorCoreEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2024-01-28 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/PropertyAnimatorCore) | |

## 用途

Property Animator Core 插件提供了一套可复用的行为（Behavior）系统，用于在运行时和编辑器中动态控制物体的属性。它并非一个具体的动画工具，而是一个底层框架，允许开发者通过组合不同的“行为”来驱动物体的变换、材质参数、灯光属性等。其核心价值在于将属性动画的逻辑抽象化、组件化，使得在虚拟制作（Virtual Production）场景中，可以快速、灵活地为场景中的物体添加复杂的动态效果，而无需编写重复的蓝图或 C++ 代码。

## 使用场景

- **虚拟制片 (Virtual Production)**：在 LED 墙或绿幕前，需要实时控制场景中道具、灯光或虚拟摄像机的属性（如位置、旋转、颜色、强度）以配合演员表演或实拍画面。
- **动态场景布置**：在编辑器或运行时，通过预设的行为快速让场景中的物体产生规律性或随机性的运动、闪烁、缩放等效果。
- **创建可配置的动画组件**：开发一个通用的“摇摆”、“呼吸”或“环绕”组件，该组件可以附加到任何 Actor 上，并通过行为系统控制其任意属性。

## 模块列表

- **PropertyAnimatorCore** (Runtime)：核心运行时模块，定义了行为系统的基础框架、核心类（如行为、行为修饰符）以及用于驱动属性变化的底层逻辑。
- **PropertyAnimatorCoreEditor** (Editor)：编辑器扩展模块，提供了在编辑器中创建、配置和预览属性动画行为的工具和界面。

## 蓝图用法

详细的蓝图节点和用法，请参阅各子模块文档。
- 核心运行时 API：[PropertyAnimatorCore.md](PropertyAnimatorCore.md)
- 编辑器工具 API：[PropertyAnimatorCoreEditor.md](PropertyAnimatorCoreEditor.md)

## C++ 用法

详细的 C++ 集成方法和示例，请参阅各子模块文档。
- 核心运行时集成：[PropertyAnimatorCore.md](PropertyAnimatorCore.md)
- 编辑器扩展开发：[PropertyAnimatorCoreEditor.md](PropertyAnimatorCoreEditor.md)

## 模块依赖

| 模块 | 用途 |
|---|---|
| `OperatorStack` | 为行为系统提供底层的操作符栈（Operator Stack）支持，用于组合和执行属性操作。 |

## 维护状态

### 近期更新

（请查看各子模块文档以获取详细的 Git 提交历史）

### 维护评价

该插件创建于 2024 年初，是一个相对较新的模块。作为 Epic Games 官方维护的虚拟制作工具链的一部分，它预计会得到持续的维护和更新，以匹配虚拟制片工作流的发展。目前处于活跃开发阶段，推荐在需要标准化、可复用属性动画逻辑的虚拟制作项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/PropertyAnimatorCore)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/PropertyAnimatorCore/Tests)