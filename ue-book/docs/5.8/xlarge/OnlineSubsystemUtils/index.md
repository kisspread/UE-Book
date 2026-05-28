# Online Subsystem Utils

> Shared code for interacting online service and online subsystem implementations.

| 属性 | 值 |
|---|---|
| 中文名 | 在线子系统工具集 |
| 分类 | Online Platform |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `OnlineSubsystemUtils` (Runtime), `OnlineBlueprintSupport` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2016-07-13 |
| 年龄标签 | 🏛️ 文物（约 10 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineSubsystemUtils) | |

## 用途

OnlineSubsystemUtils 是 UE 在线子系统架构的**公共基础设施层**，为各个平台的 Online Subsystem 实现（如 Steam、EOS、PlayStation 等）提供共享的工具代码和蓝图支持。它不直接实现任何平台的在线功能，而是作为粘合层解决以下问题：

- **会话管理工具**：提供 `FOnlineSessionUtils` 等工具类，简化多人会话的创建、搜索与加入流程
- **网络连接辅助**：包含 IP 连接、套接字管理等底层网络工具（`UIpConnection`、`UIpNetDriver`）
- **蓝图可调用代理**：通过 `OnlineBlueprintSupport` 模块暴露大量在线功能到蓝图（`UOnlineBlueprintCallProxyBase` 派生类）
- **开发者调试工具**：提供 PIE 环境下的在线子系统模拟与调试能力
- **通用子系统代理/单例管理**：统一管理各平台 Online Subsystem 实例的生命周期与查询

简单来说：没有这个插件，每个平台的 Online Subsystem 实现都要重复造轮子；有了它，所有在线功能共享一套经过验证的基础工具。

## 模块概览

| 模块 | 类型 | 职责 |
|---|---|---|
| [`OnlineSubsystemUtils`](OnlineSubsystemUtils.md) | Runtime | 核心运行时工具：会话管理、网络连接、子系统代理/单例、开发者工具 |
| [`OnlineBlueprintSupport`](OnlineBlueprintSupport.md) | UncookedOnly | 蓝图层：在线功能的蓝图可调用代理节点，仅在编辑器/未打包构建中加载 |

## 使用场景

- **多人游戏开发**：需要创建/搜索/加入在线会话 → 使用会话管理工具类
- **蓝图多人逻辑**：不想写 C++ 就实现匹配和会话功能 → 使用 OnlineBlueprintSupport 提供的蓝图代理节点
- **跨平台在线功能**：项目需要支持多个在线平台（Steam、EOS、Console） → 使用统一的子系统代理接口
- **PIE 联机调试**：在同一台机器上模拟多人联机 → 使用开发者工具模块
- **自定义 Online Subsystem**：为新平台实现在线服务 → 继承并依赖此插件提供的基础类

## 模块依赖

此插件本身依赖：

| 插件/模块 | 用途 |
|---|---|
| `OnlineSubsystem` | 核心在线子系统接口定义 |
| `OnlineServices` | 新一代在线服务抽象层 |

使用者的模块通常需要依赖：

| 模块 | 用途 |
|---|---|
| `OnlineSubsystemUtils` | 访问运行时工具类和会话管理功能 |
| `OnlineSubsystem` | 访问 `IOnlineSubsystem` 等核心接口 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为 float 的编译警告 |
| 2026-05-12 | `4ad1dbcc` | [OnlineSubsystem][OnlineServices] Guard SetPort callers against bogus port values from EOS:<PUID> ad | 防御 EOS 返回异常端口值导致 SetPort 调用出错 |
| 2026-04-30 | `7b87ee43` | Null-check Driver->GetSocketSubsystem() in UIpConnection::LowLevelSend synchronous send-failure path | 修复 UIpConnection 同步发送失败路径中套接字子系统空指针问题 |
| 2026-04-29 | `bef86caa` | Whitespace: followup to migrate UE_LOG to UE_LOGF: Restore newlines in multi-line format strings tha | 日志迁移到 UE_LOGF 后恢复多行格式字符串中的换行 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复作用域枚举在格式化函数中导致乱码输出的问题 |

### 维护评价

**活跃维护**。作为 UE 在线子系统架构的核心组成部分，此插件持续获得更新：

- 创建于 2016 年，已有约 10 年历史，是 UE 多人游戏功能的基石之一
- 2026 年 4-5 月仍有密集更新，主要集中在底层网络连接稳定性和编译兼容性修复
- 作为 EnabledByDefault 的插件，Epic 持续维护其与 EOS、Steam 等平台的兼容性
- 随着 OnlineServices 架构的引入，此插件正在逐步向新架构过渡
- **推荐使用**：任何涉及多人在线功能的 UE 项目都会直接或间接依赖此插件

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineSubsystemUtils)
- [OnlineSubsystemUtils 模块文档](OnlineSubsystemUtils.md)
- [OnlineBlueprintSupport 模块文档](OnlineBlueprintSupport.md)