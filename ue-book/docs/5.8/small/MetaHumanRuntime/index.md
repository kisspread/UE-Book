# MetaHumanRuntime

> Deprecated plugin now redirected to MetaHumanSDK（已弃用的插件，现重定向至 MetaHumanSDK）

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 运行时（已弃用） |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | 无（纯内容插件） |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2024-06-10 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetaHuman/MetaHumanRuntime) | |

## 用途

该插件最初旨在为 Unreal Engine 提供 MetaHuman 角色的运行时组件和功能，封装并统一了 UEFN（Unreal Editor for Fortnite）中的 MetaHuman 组件代码，以支持在标准 UE 项目中使用。**然而，根据其元数据和近期提交记录，此插件已被官方弃用，其核心功能已整合并迁移至 `MetaHumanSDK` 插件。** 当前版本仅作为一个指向 `MetaHumanSDK` 的兼容性重定向入口存在。

## 使用场景

由于插件已被弃用，**不推荐在任何新项目中直接使用它**。以下是它最初设计解决的场景，但现在应通过 `MetaHumanSDK` 实现：

-   **在标准 Unreal Engine 项目中运行 MetaHuman 角色**：需要 MetaHuman 的动画、物理和交互功能时。
-   **从 UEFN 项目迁移 MetaHuman 相关逻辑**：将专用于 Fortnite 的 MetaHuman 组件代码重构为可在普通 UE 项目中复用的基础组件。

**当前正确做法：** 所有 MetaHuman 相关的运行时功能开发，均应直接使用 **[MetaHumanSDK](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetaHuman/MetaHumanSDK)** 插件。

## 蓝图用法

**无公开蓝图节点。**
该插件不包含任何源代码模块，其模块列表为空。所有蓝图功能均已迁移至 `MetaHumanSDK` 插件。请参考 `MetaHumanSDK` 的文档以获取相关蓝图节点。

## C++ 用法

**无公开 C++ API。**
该插件不包含任何源代码模块（`.cpp` 或 `.h` 文件）。所有 C++ 接口和运行时组件均已迁移至 `MetaHumanSDK` 插件。

## Demo 示例

**无直接示例。**
由于插件本身无代码内容，无法提供基于此插件的示例。所有示例代码应基于 `MetaHumanSDK` 插件创建。建议查阅 Epic Games 官方示例项目或 `MetaHumanSDK` 文档中的使用范例。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MetaHumanSDK` | 该插件的核心依赖，提供所有实际的 MetaHuman 运行时功能。 |

（其他依赖为标准引擎模块）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-09-16 | `62f8cc0c` | Unable to load plugin, missing dependency MetaHumanRuntime | 解决因插件缺失依赖导致的加载失败问题 |
| 2024-08-19 | `79003ad1` | Move MetaHumanRuntime plugin to MetaHumanSDK plugin and rename it to MetaHumanSDKRuntime | 将功能主体迁移并重命名至 MetaHumanSDK，此插件正式进入弃用状态 |
| 2024-08-08 | `ea519b5c` | [MH-12702] Unreal Editor crashes after Playing a Level with an Optimized MetaHuman with MetaHuman Co | 修复在播放关卡时，带有优化 MetaHuman 和 MetaHuman 组件的编辑器崩溃问题 |
| 2024-07-31 | `8e8004fd` | MetaHuman component for UE improvements | 改进用于 UE 的 MetaHuman 组件 |
| 2024-07-24 | `bd22b183` | Fixed issue for control rigs not running on body parts | 修复控制绑定在身体部位上不运行的问题 |

### 维护评价

**已弃用，不推荐使用。**

-   **创建时间**：约1年前（2024-06-10）。
-   **维护状态**：**已弃用**。核心功能在2024年8月已迁移至 `MetaHumanSDK`，随后仅进行过兼容性修复。
-   **活跃度**：最后一次实质性功能更新是2024年8月的迁移操作，之后仅有针对迁移后遗留问题的修复。
-   **结论**：这是一个短期存在后即被更完善的 `MetaHumanSDK` 取代的实验性插件。目前它仅作为旧版兼容性重定向存在，不应在新项目中使用。**强烈建议使用 `MetaHumanSDK`。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetaHuman/MetaHumanRuntime)
- [继任者：MetaHumanSDK](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetaHuman/MetaHumanSDK)