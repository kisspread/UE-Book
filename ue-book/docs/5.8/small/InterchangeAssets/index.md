# Interchange Framework Assets

> The Interchange Framework Assets plugin exposes the assets used by the Interchange import framework.

| 属性 | 值 |
|---|---|
| 中文名 | 交换框架资产 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（材质、网格体等基础资产） |
| 模块 | `InterchangeAssets` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-03-25 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Assets) | |

## 用途

本插件是 **Interchange 导入框架** 的**资产供应包**。它的主要功能不是提供 C++ 类或蓝图节点，而是**打包并暴露 Interchange 框架在运行时依赖的核心资产**。这些资产包括默认材质、默认网格体等，确保在 Interchange 框架处理资产导入和转换时，拥有一套标准的后备或默认资源。

简而言之，它解决了 Interchange 框架的“资源依赖”问题，确保框架功能在不依赖其他项目特定资产的情况下能够独立运行。

## 使用场景

- 当你的项目启用了 **Interchange 插件** 进行资产导入（如从 FBX、USD、glTF 等格式导入）时，你需要此插件来提供框架必需的默认资源。
- 任何基于或扩展了 Interchange 导入框架的自定义工作流，都需要依赖此插件提供的资产来保证功能的完整性。

## 蓝图用法

本插件主要提供资产内容，未暴露特定的蓝图可调用函数。在蓝图中，你可能会**间接使用**其提供的资产，例如在材质或网格体引用中。

### 使用示例

假设你正在制作一个自定义的资产导入器，并在过程中需要为导入的网格体指定一个默认材质，这个默认材质可能就来自 `InterchangeAssets` 插件。在蓝图中，你会通过资产浏览器（Content Browser）找到并引用它，而不是通过特定的函数节点。

## C++ 用法

本插件无公开的 C++ 类接口。其核心是资产内容。在 C++ 代码中，你可能会通过路径引用这些资产，或在使用 Interchange 框架的其他模块中，该框架会内部引用这些资产。

### 基本用法

虽然本插件没有直接的头文件，但理解其存在有助于调试。如果 Interchange 导入过程中报告缺失某个默认材质或网格体，检查此插件是否已正确启用和安装。

### 进阶用法

如果你正在扩展 Interchange 框架，需要在导入流程中提供自己的默认资源，你可以参考本插件的资产结构和内容，确保你的扩展与框架兼容。

## Demo 示例

本插件不提供可编译的 C++ 示例。其价值在于内容资产。一个典型的使用场景是：确保在打包项目时，`InterchangeAssets` 插件及其资产被包含在内，以避免运行时出现资源缺失错误。

## 模块依赖

根据插件的定位，它主要依赖 Interchange 框架的核心模块来定义资产的用途。

| 模块 | 用途 |
|---|---|
| `InterchangeCore` | Interchange 框架核心，定义资产导入的基础结构和接口 |
| `InterchangeImport` | Interchange 框架的实际导入逻辑模块 |

*注：`.uplugin` 还声明了对 `BaseMaterial` 插件的依赖，表明其资产可能基于该基础材质插件。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-03-16 | `1f05dc85` | Adding includes before upcoming header cleanup. | 在头文件清理前添加必要的包含，属于维护性工作 |
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 将配置文件命名规范从 `Base` 更新为 `Default` |
| 2025-09-09 | `add9671d` | PR #13720: Fix Interchange PackageRedirects | 修复了 Interchange 包重定向问题 |
| 2025-09-01 | `2d41229b` | InterchangeAssets: | 对插件本身进行维护或重构 |
| 2025-03-25 | `612836d4` | Interchange Shaders: | 可能与着色器资产相关的更新或初始提交 |

### 维护评价

- **创建时间**: 2025年3月，是一个相对较新的插件。
- **近期活动**: 最近一次提交在2026年3月，表明仍在维护中。更新内容以**维护性工作、规范调整和Bug修复**为主，没有重大的新功能引入。
- **活跃度**: 作为框架的资产插件，其更新频率通常与 Interchange 框架核心的更新同步，属于**稳定维护**状态。
- **推荐使用**: **是**。如果你的项目使用了 Interchange 框架进行资产导入，此插件是必选的配套插件，以确保框架功能正常。由于其仅包含资产且默认启用，对项目性能影响极小。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Assets)
- [Interchange 框架概览](https://docs.unrealengine.com/5.8/en-US/interchange-framework-in-unreal-engine/) （官方文档中关于整个框架的介绍）