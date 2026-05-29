# Landmass

> （无描述信息）

| 属性 | 值 |
|---|---|
| 中文名 | 地形生成 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（可能包含材质、函数等） |
| 模块 | `Landmass` (Runtime), `LandmassEditor` (Editor) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2019-10-02 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Landmass) | |

## 用途

Landmass 是一个**实验性**插件，提供了一套用于程序化生成和管理大型地貌的工具。它解决了在开放世界等大型项目中，通过传统手工方式绘制地形效率低下、难以迭代和扩展的问题。该插件的核心目标是利用噪声函数、规则和分层技术，在运行时或编辑器中动态生成连续、逼真的地形资产。

## 使用场景

- 你需要为一个大型开放世界游戏快速生成基础地形，再进行细节雕刻。
- 你希望基于规则（如高度、坡度、生物群系）自动分布草地、岩石等地表材质。
- 你的项目需要支持无限或动态扩展的地形，而非一次性加载的固定地图。
- 你希望测试不同的地形参数和生成算法，以找到最适合项目的外观。

## 模块列表

-   **`Landmass`**：核心运行时模块。包含地形生成算法、噪声函数、图层混合等底层逻辑。
-   **`LandmassEditor`**：编辑器集成模块。提供用于在编辑器中预览、配置和管理生成地貌的界面与工具。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移旧版日志宏至新版，代码维护性更新。 |
| 2025-08-27 | `5ac9e159` | Landscape - Deprecating non-edit layer based landscapes | 废弃基于非编辑图层的旧式地貌工作流，推动新架构。 |
| 2025-05-29 | `8bd3e004` | Fix blutility module not guaranteed to be loaded when Landmass engine plugin compiles its content de | 修复编辑器工具模块加载依赖问题。 |
| 2025-05-01 | `0faa16c2` | Landscape Editor - Making BPBrushBase non placeable to ensure brushes are only added from Landscape | 确保笔刷仅通过地形编辑器正确添加。 |
| 2025-03-07 | `1a599460` | Remove codepaths related to HasNormalCaptureBPBrushLayer. No longer required with new landscape bor | 清理旧版笔刷图层代码。 |

### 维护评价

Landmass 是一个创建于2019年的**实验性**插件，且从未默认启用（`Installed: false`）。从提交历史看，截至2026年4月仍有维护性更新（如日志宏迁移），表明 Epic 仍在内部对其进行维护和兼容性适配。

然而，需要注意：
1.  **实验性状态**：插件明确标记为 `IsBetaVersion: true`，其API和功能未来可能发生重大变更甚至被移除。
2.  **功能演变**：近年来的提交多围绕着与新的地形编辑层（Edit Layers）工作流集成以及废弃旧有路径，说明其底层架构仍在随UE5地形系统演进。
3.  **推荐性**：鉴于其实验性状态和依赖于可能变动的内部API，**不建议在商业或长期维护项目的生产环境中直接深度依赖**。更适合作为技术研究、原型验证或学习地形生成原理的参考。对于生产环境，建议使用更稳定、文档完善的Landscape工具或第三方市场解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Landmass)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests) (Landmass相关测试可能位于此通用测试目录下)