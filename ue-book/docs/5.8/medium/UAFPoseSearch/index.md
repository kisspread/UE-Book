# UAF Pose Search

> Pose Search integration for UAF.

| 属性 | 值 |
|---|---|
| 中文名 | UAF 动作搜索 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UAFPoseSearch` (Runtime), `UAFPoseSearchUncookedOnly` (Runtime), `UAFPoseSearchTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFPoseSearch) | |

## 用途

本插件是 Unreal Animation Framework (UAF) 的扩展，将 **动作搜索 (Pose Search)** 技术集成到 UAF 高级动画系统中。它允许开发者在构建基于 UAF 的复杂动画逻辑时，利用动作搜索算法，根据当前角色状态（如速度、方向、位置等）实时查找并播放最匹配的动画片段（Pose），从而实现更平滑、更智能的动画过渡和混合效果。它解决了在 UAF 框架下高效、精确地进行上下文相关动作匹配的问题。

## 使用场景

-   你正在使用 UAF 构建一个开放世界或大型项目的高级动画系统，需要角色动画能根据复杂的游戏逻辑（如地形、战斗状态、交互目标）做出流畅、精准的反应。
-   你希望将成熟的动作搜索功能无缝整合到你已有的 UAF 动画蓝图或逻辑中，而不是手动管理复杂的动画状态机。

## 模块列表

-   `UAFPoseSearch` (Runtime): 核心运行时模块，包含在 UAF 框架内执行动作搜索所需的组件、数据结构和逻辑。
-   `UAFPoseSearchUncookedOnly` (Runtime): 仅在编辑器/未打包状态下使用的模块，可能包含用于配置、调试或预览动作搜索结果的工具。
-   `UAFPoseSearchTests` (Runtime): 包含针对该插件功能的自动化测试用例，是验证用法和了解功能细节的重要参考。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFPoseSearch)
-   [UAFPoseSearch 模块文档](UAFPoseSearch.md)
-   [UAFPoseSearchUncookedOnly 模块文档](UAFPoseSearchUncookedOnly.md)
-   [UAFPoseSearchTests 模块文档](UAFPoseSearchTests.md)