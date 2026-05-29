# Virtual Scouting

> Virtual Scouting lets filmmakers scout a digital environment in virtual reality.

| 属性 | 值 |
|---|---|
| 中文名 | 虚拟勘察 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（场景数据资产） |
| 模块 | `VirtualScouting` (Runtime), `VirtualScoutingEditor` (Runtime), `VirtualScoutingOpenXR` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-09-19 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/VirtualScouting) | |

## 用途

该插件是虚幻引擎虚拟制作管线的关键工具之一。它提供了一个完整的框架，让电影制作者、摄影师和场景设计师能够直接在虚拟现实环境中，对构建好的数字场景进行沉浸式勘察、预览和规划。

**核心功能包括**：
*   **沉浸式勘景**：用户佩戴 VR 头显，以第一人称视角进入虚拟场景，感受空间尺度、光照和氛围，其体验远比在传统监视器上观看更加真实。
*   **摄像机位规划**：在 VR 中直接放置和调整虚拟摄像机，规划拍摄路径和构图，并实时查看最终画面效果。
*   **标注与协作**：允许用户在虚拟场景中添加标记、笔记或简单形状，用于记录想法、标注问题点或与团队成员进行远程协同勘察。
*   **与虚拟制片流程集成**：生成的勘察数据（如摄像机位、标注）可以被导出或集成到后续的虚拟制片环节，如实时渲染、最终渲染或现场 LED 墙拍摄中。

该插件的目的是**缩短从创意到拍摄的决策周期**，减少实地勘景的成本和限制，并在项目早期就获得对最终视觉效果的直观把握。

## 使用场景

*   你正在为一部电影或剧集搭建一个大型虚拟环境（如城市、外星景观），需要导演和摄影指导在投入大量渲染资源前，提前“进入”这个环境进行艺术和摄影方向的决策。
*   你需要为一场复杂的虚拟制片镜头规划精确的摄像机运动路径和角度，以确保与虚拟场景的互动和最终画面符合预期。
*   你的团队分布在不同地点，需要通过 VR 进行远程“现场”勘察和创意会议。
*   你正在使用虚幻引擎的虚拟制片工具集（如 nDisplay、虚拟摄像机），并需要一个专门的 VR 工具来前置规划工作。

## 蓝图用法

*（基于模块概述推断，具体节点需查阅源码）*

该插件主要通过编辑器工具和运行时交互界面提供功能。`VirtualScoutingEditor` 模块提供了编辑器内的勘察管理工具，而 `VirtualScouting` 运行时模块则处理核心的 VR 交互逻辑。在蓝图层面，更可能通过触发编辑器工具或与专门的勘察会话控制器交互来使用，而非直接调用底层函数。

## C++ 用法

该插件主要为设计师和艺术家提供终端用户界面，其 C++ API 主要服务于插件内部模块（如 OpenXR 支持）的扩展。典型用法是继承或使用 `VirtualScouting` 模块中定义的基类和管理器来创建自定义的 VR 交互或工具。具体示例需参考各子模块文档。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `VREditor` | 提供虚幻编辑器内置的 VR 编辑框架，是 `VirtualScoutingOpenXR` 模块的依赖项，用于集成到编辑器的 VR 会话中。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下，双精度常量截断为浮点数所产生的编译警告。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正格式化字符串，确保32位与64位格式说明符与对应参数类型匹配。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将传统 `UE_LOG` 宏迁移至新的 `UE_LOGF` 格式化宏。 |
| 2026-03-13 | `b1da5d8f` | [Gizmos] Remove GizmoEdMode from areas not covered by preflight checks | 移除了在预检未覆盖区域中的 GizmoEdMode 代码。 |
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 将插件配置文件从 `Base<Plugin>.ini` 重命名为 `Default<Plugin>.ini`。 |

### 维护评价

该插件创建于 2024 年 9 月，相对年轻。从 git 历史看，**近期的提交（2025年底至2026年中）均为代码质量改进和引擎平台适配**，例如修复编译警告、适配新的日志格式、进行代码重构等，**没有添加新功能或进行重大架构调整**。

**综合评价**：
*   **状态**：处于**稳定维护期**。插件功能已基本完善，团队正专注于保持其代码的健壮性、可维护性以及与引擎新版本的兼容性。
*   **活跃度**：更新频率稳定，但内容以维护性更新为主。
*   **推荐度**：**推荐使用**。对于需要进行沉浸式 VR 勘景和规划的虚拟制片项目，这是一个由 Epic 官方维护的专用且可靠的解决方案。它默认未启用 (`EnabledByDefault: false`)，需要用户在项目设置中手动开启。
*   **注意**：作为一项相对新且专业的功能，其文档和社区示例可能不如一些老牌插件丰富，深入使用可能需要一定的探索。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/VirtualScouting)