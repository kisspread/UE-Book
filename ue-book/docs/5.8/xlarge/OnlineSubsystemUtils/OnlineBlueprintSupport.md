# Online Subsystem Utils

> Shared code for interacting online service and online subsystem implementations.

| 属性 | 值 |
|---|---|
| 中文名 | 在线子系统工具集 |
| 分类 | Online Platform |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图节点、本地化资源） |
| 模块 | `OnlineSubsystemUtils` (Runtime), `OnlineBlueprintSupport` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2016-07-13 |
| 年龄标签 | 🏛️ 文物（约 10 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineSubsystemUtils) | |

## 用途

OnlineSubsystemUtils 是 Unreal Engine 在线子系统架构的**核心工具层**，提供以下功能：

1. **蓝图异步节点（OnlineBlueprintSupport）**：将排行榜查询/刷新、应用内购买（IAP）的查询/结账/恢复等在线操作封装为蓝图可用的异步节点（K2 节点），使设计师和非 C++ 开发者也能在蓝图中使用在线服务功能。
2. **运行时工具代码（OnlineSubsystemUtils）**：提供在线子系统实现之间共享的公共工具类、辅助函数和基础设施代码，包括会话管理、网络连接工具、IP 连接处理等运行时在线服务支撑逻辑。

该插件**不直接实现**任何特定平台的在线服务（如 Steam、EOS、PlayStation），而是作为所有 OnlineSubsystem 插件的**公共依赖和工具层**，避免各平台实现之间的代码重复。

## 使用场景

- 你在蓝图中需要查询排行榜数据 → 使用 `K2Node_LeaderboardQuery` / `K2Node_LeaderboardFlush` 节点
- 你需要在蓝图中实现应用内购买流程 → 使用 `K2Node_InAppPurchase2` 等系列节点
- 你正在开发自定义的 OnlineSubsystem 插件 → 依赖本插件的共享工具代码
- 你需要在运行时处理在线会话、VOIP、网络连接等公共逻辑 → 使用 OnlineSubsystemUtils 模块

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `LeaderboardFlush` | 将本地排行榜数据刷新/上传到在线服务 | `UK2Node_LeaderboardFlush` |
| `LeaderboardQuery` | 从在线服务查询排行榜数据 | `UK2Node_LeaderboardQuery` |
| `InAppPurchase2` | 发起应用内购买请求 | `UK2Node_InAppPurchase2` |
| `InAppPurchaseQuery2` | 查询应用内可购买商品列表 | `UK2Node_InAppPurchaseQuery2` |
| `InAppPurchaseRestore2` | 恢复之前已购买的应用内商品 | `UK2Node_InAppPurchaseRestore2` |
| `InAppPurchaseCheckout` | 对应用内购买执行结账操作 | `UK2Node_InAppPurchaseCheckout` |
| `InAppPurchaseFinalize` | 完成/确认应用内购买 | `UK2Node_InAppPurchaseFinalize` |
| `InAppPurchaseQueryOwnedProducts` | 查询用户已拥有的应用内商品 | `UK2Node_InAppPurchaseQueryOwnedProducts` |
| `InAppPurchaseRestoreOwnedProducts` | 恢复用户已拥有的所有商品 | `UK2Node_InAppPurchaseRestoreOwnedProducts` |
| `InAppPurchaseGetKnownReceipts` | 获取已知的应用内购买收据 | `UK2Node_InAppPurchaseGetKnownReceipts` |
| `InAppPurchaseUnprocessed2` | 获取未处理的应用内购买 | `UK2Node_InAppPurchaseUnprocessed2` |

所有 K2 节点均继承自 `UK2Node_BaseAsyncTask`，在蓝图中表现为带有多输出执行引脚的异步节点。

### 使用示例（蓝图描述）

**查询排行榜**：
1. 在蓝图中添加 `LeaderboardQuery` 节点
2. 连接 `OnSuccess` 和 `OnFailure` 执行引脚到后续逻辑
3. 在属性面板中设置排行榜名称和查询参数
4. 成功引脚输出排行榜条目数组

**应用内购买流程**：
1. 使用 `InAppPurchaseQuery2` 查询可用商品列表
2. 成功后使用 `InAppPurchase2` 发起购买
3. 购买完成后可使用 `InAppPurchaseFinalize` 确认交易
4. 对于已购买商品，使用 `InAppPurchaseRestore2` 恢复

## C++ 用法

### 头文件引入

```cpp
// 运行时工具模块
#include "OnlineSubsystemUtils.h"

// 如需使用 K2 节点基类（编辑器模块）
#include "K2Node_LeaderboardFlush.h"
```

### 基本用法

K2 异步节点通常不直接在 C++ 中使用，而是通过子类化 `UK2Node_BaseAsyncTask` 创建新的蓝图节点：

```cpp
// 创建自定义在线操作的 K2 异步节点
// 来源: Engine/Plugins/Online/OnlineSubsystemUtils/Source/OnlineBlueprintSupport/Classes/K2Node_LeaderboardFlush.h
UCLASS(MinimalAPI)
class UK2Node_LeaderboardFlush : public UK2Node_BaseAsyncTask
{
    GENERATED_UCLASS_BODY()

    virtual FText GetTooltipText() const override;
    virtual FText GetNodeTitle(ENodeTitleType::Type TitleType) const override;
    virtual FText GetMenuCategory() const override;
};
```

### 进阶用法

在运行时 C++ 代码中使用 OnlineSubsystemUtils 模块提供的工具函数（如获取在线子系统实例、处理会话等），通常通过 `IOnlineSubsystem` 接口间接使用本模块提供的共享工具。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `OnlineSubsystem` | 在线子系统核心接口 |
| `OnlineServices` | 在线服务抽象层 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点的警告 |
| 2026-05-12 | `4ad1dbcc` | [OnlineSubsystem][OnlineServices] Guard SetPort callers against bogus port values from EOS | 防御 EOS 返回的无效端口值，保护 SetPort 调用方 |
| 2026-04-30 | `7b87ee43` | Null-check Driver->GetSocketSubsystem() in UIpConnection::LowLevelSend synchronous send-failure path | 在 IP 连接同步发送失败路径中增加空指针检查 |
| 2026-04-29 | `bef86caa` | Whitespace: followup to migrate UE_LOG to UE_LOGF: Restore newlines in multi-line format strings | 迁移 UE_LOG 到 UE_LOGF 后恢复多行格式字符串中的换行 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复格式化函数中作用域枚举导致的乱码输出 |

### 维护评价

- **活跃维护**：最近 6 个月内持续有实质性更新（Bug 修复、防御性编码、API 迁移）
- **核心基础设施**：作为所有 OnlineSubsystem 插件的公共依赖层，Epic 会持续维护以确保各平台在线服务正常工作
- **历史悠久**：2016 年从引擎内部代码抽取为独立插件，经历多年迭代，API 稳定成熟
- **推荐使用**：如果你的项目涉及任何在线功能（排行榜、IAP、会话、多人游戏），此插件作为底层依赖自动启用，无需手动操作
- ⚠️ **注意**：`OnlineBlueprintSupport` 模块类型为 `UncookedOnly`，其 K2 节点仅在编辑器和未打包版本中可用，打包后通过蓝图编译结果使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineSubsystemUtils)
- [OnlineSubsystem 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineSubsystem)（前置依赖）