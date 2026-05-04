# Text 3D

> Tool to create 3D Text with advanced options

| 属性 | 值 |
|---|---|
| 分类 | Text |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `Text3D` (Runtime), `Text3DEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Text3D) | |

## 用途

Text3D 插件提供了一套完整的工具链，用于在 Unreal Engine 中创建、渲染和操作高质量的 3D 文本。它解决了在虚拟制片、实时图形和游戏 UI 中需要动态、可定制的立体文字的需求。其核心功能包括将文本转换为 3D 网格、支持丰富的字体和材质选项、以及提供文本排版和动画控制。

## 使用场景

- **虚拟制片**：在虚拟场景中创建动态的 3D 标题、字幕或信息牌。
- **实时图形**：生成用于数据可视化或信息展示的立体文字。
- **游戏 UI**：为游戏菜单、HUD 或过场动画制作具有深度和光影效果的文字元素。
- **动态内容**：需要根据运行时数据（如玩家名称、分数）实时更新 3D 文本的场景。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| **Text3D** | Runtime | 核心运行时模块，负责 3D 文本的生成、渲染和基础功能。详见 [Text3D.md](Text3D.md)。 |
| **Text3DEditor** | Editor | 编辑器集成模块，提供资产编辑器、自定义细节面板和编辑器内预览功能。详见 [Text3DEditor.md](Text3DEditor.md)。 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Text3D)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Text3D/Tests)