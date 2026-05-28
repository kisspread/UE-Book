# Dynamic Wind

> Extremely experimental dynamic wind support for Nanite foliage.

| 属性 | 值 |
|---|---|
| 中文名 | 动态风 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `DynamicWind` (Runtime), `DynamicWindEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/DynamicWind) | |

## 用途

这个插件为 UE5 的 Nanite 植被系统提供了实验性的动态风力支持。它解决了一个核心问题：在使用 Nanite 技术渲染大规模植被时，如何实现高效、逼真的动态风力动画效果。传统的植被风力模拟可能无法直接应用于 Nanite 几何体，而此插件提供了专用的运行时模拟和编辑器工具链，旨在将动态风效果与 Nanite 技术深度集成。

## 使用场景

- 你正在开发一个拥有大规模户外场景（如森林、草原）的游戏，并使用 Nanite 来渲染其植被。
- 你需要让这些 Nanite 植被（如草、树叶、树枝）能够对风产生实时、动态的物理反应，以增强场景的真实感和沉浸感。
- 你希望风力的效果可以通过游戏中的参数（如风速、风向）进行动态控制。

## 蓝图用法

插件主要通过运行时模块 `DynamicWind` 提供核心功能，编辑器模块 `DynamicWindEditor` 提供相关的编辑器集成和资产创建工具。

### 核心模块

| 模块 | 说明 |
|---|---|
| `DynamicWind` | 提供动态风力的核心运行时模拟系统。 |
| `DynamicWindEditor` | 提供编辑器扩展和相关资产（如风力场资产）的创建与编辑功能。 |

## C++ 用法

### 模块依赖

要使用此插件的功能，你的项目模块通常需要在 `Build.cs` 中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `DynamicWind` | 用于访问核心的动态风力运行时 API。 |
| `Foliage` | 通常与植被系统配合使用。 |
| `GeometryFramework` | 可能用于场景中的几何体操作。 |

### 初始化与使用

详细用法请参考 [DynamicWind](DynamicWind.md) 和 [DynamicWindEditor](DynamicWindEditor.md) 的模块文档。

## Demo 示例

由于插件包含内容资产，可以直接在编辑器中探索。一个典型的使用流程如下：
1.  启用插件。
2.  在编辑器中创建或使用一个 `Wind Field` 资产（由 `DynamicWindEditor` 提供）。
3.  配置风力场的参数（强度、湍流等）。
4.  将风力场放置到场景中，并确保你的 Nanite 植被网格体启用了动态风响应。
5.  运行时，植被将根据场景中的风力场参数产生动态摇曳效果。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `8b5eabf3` | FastGeo: Support GPU animated instanced skinned meshes. | 为 GPU 动画的实例化蒙皮网格体添加支持。 |
| 2026-04-14 | `b1c9fc96` | Fixed dynamic wind ES31 compilation error not supporting bit fields in structured buffers. | 修复了动态风系统在 ES3.1 下因不支持结构体缓冲区位域导致的编译错误。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF。 |
| 2026-04-09 | `39e82b40` | Refactored ASTP to support layers and blend spaces. Rather than use a parent / child hierarchy, ther... | 重构了 ASTP（动画状态树处理器）以支持层和混合空间，改进了原有层级结构。 |
| 2026-04-02 | `ac7816b3` | Implement dynamic wind for GPU skin and unified bone indices which both use a bone map. | 实现了针对 GPU 蒙皮和统一骨骼索引的动态风效果，两者均使用骨骼映射。 |

### 维护评价

该插件创建于 2025 年 8 月，是一个相对较新的实验性插件。从近期的 Git 历史看，它在 2026 年 4 月和 5 月仍有**持续的活跃更新**，内容包括功能增强、bug 修复和底层重构。这表明该插件处于**积极开发和维护**中。

由于其 `IsExperimentalVersion = true` 且 `EnabledByDefault = false`，这明确意味着它仍处于**实验阶段**，API 和功能可能会发生变化，不建议在正式生产项目中未经充分测试直接使用。但对于探索 Nanite 植被的前沿动态效果，这是一个非常有价值的研究和原型开发工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/DynamicWind)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/DynamicWind/Tests)