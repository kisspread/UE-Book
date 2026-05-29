# Paper2D

> Paper2D adds tools and assets to help create 2D games including animated sprite assets, tilesets (experimental), 2D level editing tools, and more.

| 属性 | 值 |
|---|---|
| 中文名 | 二维引擎 |
| 分类 | 2D |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（二维游戏资源） |
| 模块 | `Paper2D` (Runtime), `Paper2DEditor` (Editor), `PaperSpriteSheetImporter` (Editor), `PaperTiledImporter` (Editor), `SmartSnapping` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2014-09-16 |
| 年龄标签 | 🏛️ 文物（约 12 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/2D/Paper2D) | |

## 用途

Paper2D 是 Unreal Engine 中用于开发 2D 游戏的核心插件。它解决了 UE 原生为 3D 游戏引擎优化的架构下，高效进行 2D 内容创作、关卡编辑和运行时渲染的问题。它提供了一整套工具链，包括：
- **运行时组件**：用于显示和交互 2D 精灵（`UPaperSprite`）、瓦片地图（`UPaperTileMap`）及它们的动画。
- **编辑器工具**：提供可视化的 2D 关卡编辑模式、资产创建向导和属性自定义。
- **导入工具**：支持从第三方工具（如 TexturePacker 的精灵表、Tiled 地图编辑器、Spriter 动画）导入素材。

其核心目的是让开发者能够在 UE 生态中无缝地进行 2D 游戏原型开发和正式项目制作。

## 使用场景

- 你正在开发一款 **2D 平台跳跃游戏** → 使用 Paper2D 的 `UPaperCharacter` 和 `UPaperFlipbook` 来实现角色动画和操控。
- 你需要基于 **瓦片地图（Tile Map）** 快速搭建关卡 → 使用 `UPaperTileMap` 及其编辑器进行可视化绘制。
- 你使用 **TexturePacker** 等工具打包了精灵表 → 使用 `PaperSpriteSheetImporter` 模块将其导入为 UE 资产。
- 你使用 **Tiled** 或 **Spriter** 等工具制作了地图或动画 → 使用对应的导入器模块将内容引入引擎。
- 你需要在 3D 世界中放置 2D 元素（如 UI 面板、广告牌） → 使用 `UPaperSpriteComponent` 和 `UPaperFlipbookComponent`。

## 模块列表

| 模块 | 说明 |
|---|---|
| `Paper2D` (Runtime) | 核心运行时模块，包含所有 2D 组件、资产和游戏逻辑。 |
| `Paper2DEditor` (Editor) | 编辑器模块，提供 2D 内容创作工具、自定义资产编辑器和关卡编辑模式。 |
| `PaperSpriteSheetImporter` (Editor) | 编辑器模块，负责导入 TexturePacker 格式的精灵表（Sprite Sheet）。 |
| `PaperTiledImporter` (Editor) | 编辑器模块，负责导入 Tiled 地图编辑器创建的地图文件。 |
| `SmartSnapping` (Editor) | 编辑器模块，提供智能的 Actor 和组件对齐与吸附功能。 |
| `SpriterImporter` (Editor) | 独立编辑器模块，用于导入 Spriter 格式的 2D 骨骼动画。（*注：此模块未在主插件 .uplugin 中声明，可能为独立或遗留模块*） |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/2D/Paper2D)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/2D/Paper2D/Tests)