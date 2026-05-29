# Online Services

> Shared code for interacting with online services implementations.

| 属性 | 值 |
|---|---|
| 中文名 | 在线服务 |
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `OnlineServicesInterface` (Runtime), `OnlineServicesCommon` (Runtime), `OnlineServicesCommonEngineUtils` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-09-30 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineServices) | |

## 用途

该插件为 Unreal Engine 提供了与在线服务（如会话、好友、排行榜、成就等）交互的**核心抽象层和通用实现框架**。它的主要目的是**隔离平台特定的在线服务后端**（如 EOS、Steam、PlayStation Network 等），让游戏逻辑和上层系统可以基于一套统一的接口进行开发，而无需直接依赖任何特定的第三方 SDK 或平台原生 API。这极大地简化了跨平台游戏的在线功能开发与维护。

## 使用场景

- 你的游戏需要支持多个在线平台（如 PC、Xbox、PlayStation），且希望用一套代码处理会话、匹配、好友列表等核心在线功能。
- 你正在开发一个需要稳定、可扩展在线架构的项目，希望将平台特定的实现细节与游戏逻辑解耦。
- 你需要利用 Epic 的通用在线服务工具（如 `OnlineServicesCommonEngineUtils` 提供的引擎集成），快速实现标准的在线功能。

## 模块列表

| 模块 | 说明 |
|---|---|
| `OnlineServicesInterface` | 定义了所有在线服务（账户、会话、好友、成就等）的纯虚接口。是其他在线服务实现的契约基础。 |
| `OnlineServicesCommon` | 提供基于 `OnlineServicesInterface` 的通用功能框架和共享工具，用于简化具体平台后端的实现。 |
| `OnlineServicesCommonEngineUtils` | 将在线服务与 UE 引擎系统（如 `GameInstance`、`World`）进行集成的工具集，简化游戏逻辑对在线服务的调用。 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineServices)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/OnlineServices) (可能存在)

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量截断为浮点数引发的编译警告。 |
| 2026-05-12 | `4ad1dbcc` | [OnlineSubsystem][OnlineServices] Guard SetPort callers against bogus port values from EOS | 为 EOS 的 `SetPort` 调用增加保护，防止接收到无效的端口值。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了格式化字符串说明符与参数位宽不匹配的问题（32位/64位）。 |
| 2026-04-14 | `2c013d6c` | Online Services EOS Presence Refactor | 对 EOS 的“在线状态”（Presence）功能进行了重构。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移到 `UE_LOGF`。 |

### 维护评价

该插件自 2022 年从 Experimental 迁出后，一直保持**活跃维护**。从近期提交记录看，更新非常频繁（几乎每周），内容涉及**新功能开发（如 EOS Presence 重构）、Bug 修复（端口值保护、格式说明符）和代码质量改进（编译警告、日志迁移）**。作为 Epic 官方力推的在线服务统一框架，它替代了旧的 `OnlineSubsystem` 体系，是 UE 在线功能未来的标准，**强烈推荐用于新项目**。