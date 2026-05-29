# Online Framework Plugin

> Shared code for interacting with online gameplay services.

| 属性 | 值 |
|---|---|
| 中文名 | 在线框架插件 |
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Hotfix` (Runtime), `Lobby` (Runtime), `LoginFlow` (Runtime), `Party` (Runtime), `PatchCheck` (Runtime), `PlayTimeLimit` (Runtime), `Qos` (Runtime), `Rejoin` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2016-07-13 |
| 年龄标签 | 🏛️ 文物（约 10 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineFramework) | |

## 用途

本插件是 Epic 为在线游戏服务构建的一套**通用、高级的框架层**。它基于底层 `OnlineSubsystem`，提供了一系列标准化的功能模块，旨在简化常见的在线社交与游戏准备流程的开发，例如创建大厅、管理派对、应用热修复、检查游戏更新等。开发者无需从零实现这些复杂逻辑，可以直接组合使用这些模块来快速搭建在线功能。

## 使用场景

- 你需要为多人游戏创建一个功能完整的大厅（Lobby）系统 → 使用 `Lobby` 模块。
- 你需要让玩家能组队、邀请好友一起匹配游戏 → 使用 `Party` 模块。
- 你需要在不发补丁的情况下远程修复线上游戏的bug或进行配置更新 → 使用 `Hotfix` 模块。
- 你需要确保玩家的游戏客户端是最新版本才能进入游戏 → 使用 `PatchCheck` 模块。
- 你需要评估玩家的网络连接质量（QoS）以进行匹配或服务器选择 → 使用 `Qos` 模块。

## 模块列表

| 模块 | 说明 |
|---|---|
| `Hotfix` | 运行时热修复系统，支持从后端拉取并应用修复代码或配置。 |
| `Lobby` | 大厅系统，提供游戏房间创建、管理、加入等标准化接口。 |
| `LoginFlow` | 登录流程处理，管理用户登录、认证的步骤和状态。 |
| `Party` | 派对系统，处理玩家组队、邀请、状态同步等社交功能。 |
| `PatchCheck` | 游戏版本与补丁检查，确保客户端版本符合服务器要求。 |
| `PlayTimeLimit` | 游戏时间限制功能，用于实现防沉迷或游戏时长管理。 |
| `Qos` | 网络服务质量（Quality of Service）检测，用于评估连接质量。 |
| `Rejoin` | 重连逻辑，处理游戏会话中断后的重新加入流程。 |

## 蓝图用法

本插件的核心功能主要通过其子模块暴露给蓝图。每个模块（如 `Party`、`Lobby`）都提供了独立的蓝图接口（通常是蓝图函数库或管理器类），用于创建和管理会话、处理邀请、应用热修复等。详细 API 请参阅各子模块的文档。

## C++ 用法

本插件主要作为框架库，其 C++ 接口被 `OnlineSubsystem` 及其游戏特定实现所调用。普通游戏开发者通常通过蓝图或继承自框架提供的基类来使用其功能。例如，`Party` 模块提供了 `UOnlinePartySubsystem` 等类，开发者可以继承或调用其方法来实现自定义派对逻辑。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `OnlineSubsystemGDK` | `Party` 模块的特定依赖，表明其可能集成了 GDK 平台的派对功能。 |
| `OnlineSubsystem` | 所有模块的底层基础，提供与不同在线服务通信的抽象层。 |

**说明**：除 `OnlineSubsystemGDK` 这一特定平台依赖外，其他依赖均为常见的 `OnlineSubsystem`、`Engine` 等核心模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `09a2dfc6` | [Hotfix on Load] Fix issue where certain baked hotfixes will not apply when no backend hotfixes exis | 修复离线时预置热修复无法加载的问题。 |
| 2026-05-12 | `0b9170a8` | Guard Invite and RTJ social party calls when epic parties mirroring is enabled. | 为派对邀请和加入请求添加保护，防止与 Epic 派对镜像功能冲突。 |
| 2026-04-30 | `fe1eaff2` | Add a hook for PartyPlatformSessionMonitor to allow the game party to add a special key to the platf | 为派对会话监控添加钩子，允许游戏派对在平台会话中添加特殊标识。 |
| 2026-04-29 | `0badc43f` | Restore LogHotfixManager summary logs for hotfix on load | 恢复热修复管理器在加载时的日志摘要输出。 |
| 2026-04-28 | `85cae1c6` | Broadcast party initialization after we've processed our first update | 优化派对初始化广播时机，确保在首次状态更新后进行。 |

### 维护评价

- **活跃维护**：最近的提交记录（2026年5月）表明该插件仍在**积极维护和更新**。
- **稳定性**：近期更新多为功能增强和Bug修复（如修复热修复加载问题、优化派对初始化），表明其核心功能已比较成熟稳定。
- **实验性**：该插件 `EnabledByDefault` 为 `false`，但并未标记为实验性（`IsBetaVersion`/`IsExperimentalVersion` 为 `false`）。这意味着它功能完整，但出于项目配置考虑默认关闭，需要手动启用。
- **推荐**：对于需要标准化在线社交和准备流程的多人游戏项目，**推荐使用**此插件。它提供了经过 Epic 实践检验的底层框架，能显著降低开发复杂度。请注意其依赖的 `OnlineSubsystem` 需要正确配置。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineFramework)
- （暂无官方文档链接，可通过子模块文档和源码学习）