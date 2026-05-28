# Mover

> Mover is an Unreal Engine plugin to support movement of actors with rollback networking.

| 属性 | 值 |
|---|---|
| 中文名 | 运动组件 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产和示例） |
| 模块 | `Mover` (Runtime), `MoverCVDData` (Runtime), `MoverCVDEditor` (Runtime), `MoverEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-02-02 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Mover) | |

## 用途

Mover 是 UE5 中用于实现 Actor 运动逻辑的框架，旨在取代或扩展传统的 `CharacterMovementComponent`。它主要解决两个问题：
1.  **高度可定制的运动逻辑**：通过模块化、可组合的 `Movement Mode` 和 `Layered Moves`，开发者可以轻松构建复杂且可复用的运动行为（如飞行、攀爬、滑索等），而无需继承庞大的组件类。
2.  **网络预测与回滚**：其核心设计原生支持带网络预测（Prediction）和回滚（Rollback）的运动，非常适合需要精确网络同步的多人游戏。

简而言之，Mover 提供了一套现代、灵活且网络友好的 Actor 运动基础设施。

## 使用场景

-   你的多人游戏需要高度定制化且网络同步精确的角色移动，例如包含特殊载具、攀爬或飞行状态。
-   你希望将运动逻辑（如移动模式、层移动）模块化，以便于复用和测试，而不是将所有逻辑塞进一个庞大的组件。
-   你需要替换或深度定制 `CharacterMovementComponent` 的行为，但又被其庞大的代码和复杂的继承关系所困扰。

## 模块列表

本插件由以下模块组成，详细 API 和用法请参阅各模块文档：

| 模块 | 类型 | 说明 |
|---|---|---|
| **Mover** | Runtime | 核心运行时模块。包含运动系统的主要类、接口、模式和层移动的实现。 |
| **MoverCVDData** | Runtime | 为 Chaos Visual Debugger (CVD) 提供数据支持，用于运动数据的可视化调试。 |
| **MoverCVDEditor** | Runtime | CVD 编辑器集成，提供运动数据的编辑器内可视化界面。 |
| **MoverEditor** | Runtime | 编辑器扩展模块，为 Mover 系统提供资产编辑器、自定义细节面板等工具支持。 |

## 蓝图与 C++ 用法概览

-   **蓝图**：可通过 `UMoverComponent` 组件添加到 Actor。主要工作流包括配置 `Movement Mode`、添加 `Layered Moves`，并响应运动状态事件。
-   **C++**：通过继承和实现 `INavMovementInterface`、`IMoverDebugComponentInterface` 等接口，或创建自定义的 `UMovementMode` 和 `UInstantMovementEffect` 来扩展功能。
-   **详细 API**：请参阅各模块文档（如 `Mover.md`）以获取具体的 `UCLASS`、`UFUNCTION` 和 `UPROPERTY` 列表。

## 模块依赖

要使用 Mover 插件，你的项目模块通常需要依赖以下独特模块（标准 Core/Engine 依赖已省略）：

| 模块 | 用途 |
|---|---|
| `Mover` | 核心运动功能，必须依赖。 |
| `MoverCVDData` | 如果你需要运动数据的 CVD 可视化调试功能。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `6ef46a3c` | Mover: update README for next release | 更新文档，为下个版本发布做准备 |
| 2026-05-22 | `4ea45e21` | Mover: fix bug where skipping vertical anim root motion was not being respected in all montage cases | 修复动画根运动在特定蒙太奇下跳过垂直分量的 bug |
| 2026-05-20 | `dd78e781` | Mover: fix for inconsistent behavior of mode-changed events (kinematic / NPP cases) resulting in que... | 修复模式切换事件（运动学/NPP 情况下）行为不一致导致的问题 |
| 2026-05-14 | `801be5dc` | Mover/ChaosMover: Just like moves, move instances are now using a pull mechanism so they can work in... | Move 实例改用拉取机制，以更好地适应网络回滚 |
| 2026-05-14 | `d040bc9f` | Mover: adding simulation that's specific to kinematically-moved Actors | 添加针对运动学驱动 Actor 的专属模拟 |

### 维护评价

**活跃维护中**。
-   插件于 2024 年初创建，相对较新。
-   截至 2026 年 5 月，近期更新非常频繁（几乎每日），内容集中在功能完善、Bug 修复和网络同步优化上。
-   从 commit 信息看，开发团队正在积极地为网络预测回滚、特定运动场景（如动画根运动、运动学 Actor）打补丁，表明其处于**活跃开发期**。
-   **推荐使用**：对于新项目，尤其是需要高级网络同步和模块化运动设计的多人游戏，Mover 是一个很有前途的现代解决方案。但需注意其路径在 `Experimental` 下，API 和功能仍可能发生变化。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Mover)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Mover/Tests)