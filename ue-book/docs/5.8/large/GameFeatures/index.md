# Game Features

> Support for modular Game Feature Plugins

| 属性 | 值 |
|---|---|
| 中文名 | 游戏特性 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameFeatures` (Runtime), `GameFeaturesEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-31 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GameFeatures) | |

## 用途

Game Features 插件提供了一套底层框架，用于实现**模块化游戏功能 (Game Feature Plugin)** 的运行时加载、激活和生命周期管理。它解决的核心问题是：如何将游戏的核心逻辑（如新玩法、新区域、新角色能力）以插件的形式打包，并允许在运行时按需动态加载和卸载，从而支持游戏的模块化扩展、可下载内容（DLC）以及游戏模组（Mod）等场景。

## 使用场景

-   **大型开放世界游戏**：为不同区域（如不同星球、不同城市）打包独立的功能模块，并在玩家进入对应区域时动态加载，以优化内存和加载时间。
-   **可下载内容（DLC）扩展**：将新任务、新武器、新角色作为独立的游戏功能插件进行分发和安装。
-   **游戏模组（Mod）支持**：允许玩家或社区创建自定义的游戏功能包，并由主游戏在运行时安全地加载和集成。
-   **A/B 测试或功能开关**：将某个实验性玩法或UI改版打包，通过服务器指令或配置动态启用，无需重新构建游戏客户端。

## 模块概览

| 模块 | 类型 | 说明 |
|---|---|---|
| [`GameFeatures`](GameFeatures.md) | Runtime | 核心运行时框架。提供游戏特性插件的生命周期管理器、加载器、组件化激活器以及用于声明特性的数据资产（如`UGameFeatureData`）。 |
| [`GameFeaturesEditor`](GameFeaturesEditor.md) | Runtime | 编辑器扩展。提供创建和管理游戏特性插件项目的向导、资产类型以及编辑器内的状态调试工具。 |
| [`PLUGIN_NAMERuntime`](PLUGIN_NAMERuntime.md) | Runtime | 代码模板。这是一个用于创建包含 C++ 代码的新游戏特性插件的模板项目。 |

## 主要功能点

-   **特性生命周期管理**：支持游戏特性插件的完整状态流转（`Installed` -> `Registered` -> `Loaded` -> `Activated` -> `Deactivated` -> `Unloaded`）。
-   **依赖关系解析**：自动处理特性插件之间的依赖关系，确保按正确的顺序加载。
-   **组件化激活**：特性激活时可以自动向游戏世界中注入新的组件（如新的Actor、Component），实现功能的“即插即用”。
-   **代码与资产支持**：既可以创建包含蓝图和资产的内容型插件，也可以创建包含C++逻辑的代码型插件。

## 模块依赖

使用此插件的核心功能无需额外依赖非常见模块。其内部设计依赖于以下系统，这些通常已包含在基础项目中：

| 模块 | 用途 |
|---|---|
| `GameplayTags` | 用于标识和查询游戏特性的状态与类型。 |
| `GameplayAbilities` | （可选）用于集成和激活来自游戏特性的能力系统。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `f604c6dd` | CollectDepends when AddOrUpdateRef, skip dep walk for deps already counted at >= target state in thi | 优化依赖收集逻辑，避免重复遍历已计数依赖，提升性能。 |
| 2026-05-12 | `a7ff6fd5` | [GameFeatures] Added optional CVar property gating for AddWorldPartitionContent activation. | 为世界分区内容的激活新增了可选的CVar属性门控功能。 |
| 2026-04-30 | `3f194f64` | Only load verse path mapper bin in cooked non editor builds. Cooked editor still requires all plugin | 调整Verse路径映射器二进制文件的加载时机，仅在非编辑器的打包构建中加载。 |

### 维护评价

**活跃维护**。该插件于2024年初从Experimental迁移至Runtime，虽标记为Beta，但Epic Games持续为其提供更新。近期（2026年）的提交表明其仍在进行功能优化和错误修复，特别是针对大型项目（如使用世界分区）的场景。作为《堡垒之夜》创作模式等官方功能的核心支撑，其长期维护有保障。推荐在开发需要高度模块化或动态内容加载的项目时使用。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GameFeatures)
-   [GameFeatures 模块文档](GameFeatures.md)
-   [GameFeaturesEditor 模块文档](GameFeaturesEditor.md)
-   [PLUGIN_NAMERuntime 模板文档](PLUGIN_NAMERuntime.md)