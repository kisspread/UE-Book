# Multi-Server Replication

> Code to help facilitate connecting multiple UE server processes to each other.

| 属性 | 值 |
|---|---|
| 中文名 | 多服务器复制 |
| 分类 | Networking |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MultiServerReplication` (Runtime), `MultiServerConfiguration` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-08-15 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MultiServerReplication) | |

## 用途

本插件旨在为需要将游戏世界分布到多个独立运行的 Unreal 服务器进程（例如，用于承载超大规模地图或海量玩家）的项目，提供底层的通信框架。它通过在线信标（Online Beacons）建立服务器进程间的点对点连接，使得不同服务器实例上运行的游戏对象（如角色、实体）的状态能够相互同步，从而实现无缝的跨服务器交互。

## 使用场景

-   **超大型开放世界游戏**：将无缝地图划分为多个区域，每个区域由一个独立的服务器进程承载，玩家跨区域移动时，需要服务器间传递玩家和实体状态。
-   **大规模多人在线游戏 (MMO)**：当单个服务器无法容纳全部玩家时，将玩家分配到多个服务器，需要这些服务器协同处理全局事件和玩家间互动。
-   **需要服务器间直接通信的自定义架构**：任何需要超越传统客户端-服务器模型、让多个服务器进程作为对等节点直接通信的场景。

## 模块列表

本插件包含两个运行时模块，具体功能和 API 请参阅各自的详细文档。

-   **MultiServerReplication**：插件的核心模块，提供了跨服务器进程连接、状态同步和通信的基础框架与主要接口。
    -   详细文档：[MultiServerReplication.md](MultiServerReplication.md)
-   **MultiServerConfiguration**：辅助模块，可能负责管理服务器的连接配置、地址解析或相关设置。
    -   详细文档：[MultiServerConfiguration.md](MultiServerConfiguration.md)

## 蓝图用法

暂无公开的蓝图节点。此插件为底层网络模块，主要通过 C++ API 进行使用和扩展。

## C++ 用法

详细用法请参考上方模块文档。核心思路是通过插件提供的 API 在多个服务器进程间建立连接和发送/接收复制数据。

### 模块依赖

要使用此插件，你的项目或模块需要依赖以下插件/模块：

| 模块/插件 | 用途 |
|---|---|
| `OnlineSubsystemUtils` | 提供在线子系统的基础工具和信标功能，是建立服务器间连接的基础依赖 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了格式化函数中使用的枚举作用域问题，该问题曾导致输出错误。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了格式化说明符与参数位数（32/64位）不匹配的问题，提升数据类型兼容性。 |
| 2026-04-15 | `025454a5` | static analysis fix: using alloca in a loop | 修复了静态代码分析警告：禁止在循环中使用 alloca 函数，提升了代码安全性。 |
| 2026-04-15 | `f0b565cd` | FMultiServerTransport | 添加或更新了 FMultiServerTransport 类，是插件网络传输层的核心组件。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移至 UE_LOGF，统一日志输出格式。 |

### 维护评价

-   **状态**：**活跃维护中**。该插件于 2024 年 8 月创建，且从近期（2026年4月）的提交记录看，Epic Games 正在持续进行功能开发和代码修复。
-   **实验性**：插件当前标记为 `IsExperimentalVersion`，且默认未启用 (`EnabledByDefault=false`)。这表明 API 可能不稳定，且可能在未来版本中发生重大变更。建议仅用于原型开发和研究。
-   **推荐度**：对于需要探索多服务器架构的早期项目，可以尝试集成和学习。但不建议在追求稳定性的商业项目中直接依赖，需密切关注其版本更新和状态变化。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MultiServerReplication)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MultiServerReplication/Tests)