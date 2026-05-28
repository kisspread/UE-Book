# Online Framework Plugin

> Shared code for interacting with online gameplay services.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 在线框架 |
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Hotfix` (Runtime), `Lobby` (Runtime), `LoginFlow` (Runtime), `Party` (Runtime), `PatchCheck` (Runtime), `PlayTimeLimit` (Runtime), `Qos` (Runtime), `Rejoin` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2016-07-13 |
| 年龄标签 | 🏛️ 文物（约 10 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineFramework) | |

## 用途

OnlineFramework 是 Epic 为多人在线游戏提供的**通用在线服务基础设施层**。它不直接对接任何特定平台（如 Steam、PlayStation），而是封装了多个平台无关的在线功能模块：热更新推送、大厅匹配、队伍社交、网络质量检测、补丁检查、游玩时间限制、登录流程、重新加入等。

这个插件存在的意义是：将这些通用的在线功能从具体的 OnlineSubsystem 实现中解耦出来，使得游戏项目可以复用这些能力，而无需关心底层平台差异。它默认不启用（`EnabledByDefault=false`），需要在项目中手动启用。

## 模块总览

| 模块 | 说明 |
|---|---|
| **Hotfix** | 远程热修复管理器，支持在不发版的情况下通过后端推送配置/代码修补 |
| **Lobby** | 大厅系统抽象层，提供创建/加入/管理游戏大厅的接口 |
| **LoginFlow** | 平台登录流程管理，处理用户认证和登录状态流转 |
| **Party** | 社交队伍系统，支持组队、邀请、队伍状态同步（依赖 OnlineSubsystemGDK） |
| **PatchCheck** | 补丁版本检查，在游戏启动时校验是否需要更新 |
| **PlayTimeLimit** | 游玩时长限制，用于合规性场景（如未成年人保护） |
| **Qos** | 网络服务质量（Quality of Service）检测，测量延迟和选择最优服务器区域 |
| **Rejoin** | 重新加入机制，处理断线后重连到之前的游戏会话 |

## 使用场景

- 你需要在不更新客户端的情况下远程推送配置修复 → 用 **Hotfix** 模块
- 你需要跨平台的组队和邀请功能 → 用 **Party** 模块
- 你需要为玩家匹配最优的游戏服务器（按延迟排序）→ 用 **Qos** 模块
- 你需要在游戏启动时检查是否有强制更新 → 用 **PatchCheck** 模块
- 你需要实现大厅制的多人匹配（而非纯匹配池）→ 用 **Lobby** 模块
- 你需要实现断线重连功能 → 用 **Rejoin** 模块
- 你的游戏需要遵守未成年人游玩时长法规 → 用 **PlayTimeLimit** 模块
- 你需要管理多平台登录流程 → 用 **LoginFlow** 模块

## 子模块文档

每个子模块的详细 API 用法请参阅对应的文档页：

- [Hotfix](Hotfix.md) — 远程热修复
- [Lobby](Lobby.md) — 大厅系统
- [LoginFlow](LoginFlow.md) — 登录流程
- [Party](Party.md) — 社交队伍
- [PatchCheck](PatchCheck.md) — 补丁检查
- [PlayTimeLimit](PlayTimeLimit.md) — 游玩时长限制
- [Qos](Qos.md) — 网络质量检测
- [Rejoin](Rejoin.md) — 重新加入

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `09a2dfc6` | [Hotfix on Load] Fix issue where certain baked hotfixes will not apply when no backend hotfixes exist | 修复内置热修复在无后端配置时不生效的问题 |
| 2026-05-12 | `0b9170a8` | Guard Invite and RTJ social party calls when epic parties mirroring is enabled. | 队伍镜像启用时保护邀请和加入的社交调用 |
| 2026-04-30 | `fe1eaff2` | Add a hook for PartyPlatformSessionMonitor to allow the game party to add a special key to the platform session | 为 PartyPlatformSessionMonitor 添加钩子以支持自定义平台会话标识 |
| 2026-04-29 | `0badc43f` | Restore LogHotfixManager summary logs for hotfix on load | 恢复热修复管理器在加载时的日志摘要输出 |
| 2026-04-28 | `85cae1c6` | Broadcast party initialization after we've processed our first update | 修复队伍初始化广播时机，在首次更新处理完成后再广播 |

### 维护评价

**活跃维护** ✅

OnlineFramework 是 Epic 的核心在线基础设施，自 2016 年创建以来持续维护。最近的 commit 集中在 2026 年 4-5 月，更新频率约每周数次，内容涵盖 Bug 修复、功能增强和平台兼容性改进。作为 `EnabledByDefault=false` 的插件，它面向有特定在线需求的多人游戏项目。

**推荐使用**：如果你的项目需要上述任一在线功能（热更新、组队、大厅、QoS 等），这些模块经过了多年迭代和大量游戏项目的验证，是可靠的基础设施。但需要注意这是 Epic 内部基础设施，部分模块可能依赖特定平台子系统（如 Party 依赖 OnlineSubsystemGDK），实际使用时需评估与你项目技术栈的兼容性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineFramework)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/online-subsystem-in-unreal-engine)