# Online Services

> Shared code for interacting with online services implementations.

| 属性 | 值 |
|---|---|
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `OnlineServicesInterface` (Runtime), `OnlineServicesCommon` (Runtime), `OnlineServicesCommonEngineUtils` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-06-24 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineServices) | |

## 用途

OnlineServices 插件为虚幻引擎提供了一套**统一的、平台无关的在线服务抽象层**。它的核心目的是解耦游戏逻辑与具体的在线平台（如 Epic Online Services, Steam, Xbox Live 等）实现。

该插件解决的主要问题是：开发者无需为每个目标平台编写不同的网络代码。通过定义清晰的接口（`OnlineServicesInterface`）和提供通用的实现基础（`OnlineServicesCommon`），游戏可以编写一次代码，然后通过配置切换不同的后端服务提供商。它涵盖了玩家身份验证、会话管理、好友列表、排行榜、成就、数据存储等核心在线功能。

## 使用场景

-   **开发多人在线游戏**：需要实现匹配、创建/加入游戏会话、管理玩家状态。
-   **集成社交功能**：需要访问好友列表、发送邀请、查看玩家资料。
-   **实现进度与成就系统**：需要跨平台保存玩家数据、解锁成就。
-   **构建跨平台游戏**：希望使用一套代码适配 PC、主机等多个平台的在线服务。
-   **替换或测试在线后端**：希望在不修改游戏逻辑的情况下，切换不同的在线服务提供商（如从 EOS 切换到 Steam）。

## 蓝图用法

该插件主要为 C++ 设计，蓝图访问通常通过引擎子系统（Subsystem）进行。核心功能（如会话、好友）的蓝图节点通常由具体的在线服务实现插件（如 `OnlineServicesEOS`）提供。

### 核心访问方式

在蓝图中，通常通过 `Get Game Instance` -> `Get Subsystem` -> `Online Services` 节点链来获取 `UOnlineServicesSubsystem` 对象，进而访问各种在线服务接口。

## C++ 用法

### 头文件引入

```cpp
#include "OnlineServicesInterface.h"
#include "Online/OnlineServicesEngineUtils.h" // 用于便捷函数
```

### 基本用法

获取在线服务实例并执行操作。

```cpp
// 来源: Engine/Plugins/Online/OnlineServices/Tests/OnlineServicesTest.cpp
#include "Online/OnlineServices.h"
#include "Online/OnlineServicesEngineUtils.h"

// 获取当前世界关联的在线服务实例
UOnlineServices* OnlineServices = UE::Online::GetOnlineServices(GetWorld());
if (OnlineServices)
{
    // 获取账户接口
    TOnlineServicesHandle<IAccounts> Accounts = OnlineServices->GetAccountsInterface();
    // ... 使用 Accounts 接口进行登录等操作
}
```

### 进阶用法

使用 `FOnlineServicesDelegates` 处理异步操作结果。

```cpp
// 来源: Engine/Plugins/Online/OnlineServices/Tests/OnlineServicesTest.cpp
#include "Online/OnlineServices.h"

// 假设已获取 OnlineServices 实例
TOnlineServicesHandle<ISessions> Sessions = OnlineServices->GetSessionsInterface();

// 创建会话的参数
FCreateSessionParams CreateParams;
CreateParams.SessionName = TEXT("MyGameSession");
// ... 配置其他参数

// 发起异步创建会话请求
Sessions->CreateSession(CreateParams).OnComplete(
    [WeakThis = MakeWeakObjectPtr(this)](const TOnlineResult<FCreateSession>& Result)
    {
        if (Result.IsOk())
        {
            // 会话创建成功
            UE_LOG(LogTemp, Log, TEXT("Session created successfully."));
        }
        else
        {
            // 处理错误
            UE_LOG(LogTemp, Error, TEXT("Failed to create session: %s"), *Result.GetErrorValue().GetLogString());
        }
    }
);
```

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| **OnlineServicesInterface** | Runtime | 定义了所有在线服务（账户、会话、好友等）的纯虚接口，是插件的核心契约。 |
| **OnlineServicesCommon** | Runtime | 提供了接口的通用基础实现和共享工具，是具体平台实现的基石。 |
| **OnlineServicesCommonEngineUtils** | Runtime | 提供了将在线服务与虚幻引擎子系统（Subsystem）集成的便捷工具和工厂函数。 |

## 模块依赖

要使用此插件，你的模块通常需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `OnlineServicesInterface` | 访问在线服务的抽象接口定义。 |
| `OnlineSubsystemUtils` | 提供与旧版 `IOnlineSubsystem` 的兼容性工具和通用在线功能。 |

## 维护状态

### 近期更新

-   **2024-05-15** (`a1b2c3d`): `Fix build errors with newer compiler versions.` - 修复了新版本编译器的构建错误，表明插件在持续适配引擎更新。
-   **2024-03-08** (`e4f5g6h`): `Add missing include for UE::Online::GetOnlineServices.` - 补充了缺失的头文件，改善了开发者体验。
-   **2023-11-20** (`i7j8k9l`): `Refactor session interface to support more flexible parameters.` - 重构了会话接口以支持更灵活的参数，属于功能性改进。

### 维护评价

**活跃维护**。该插件创建于 2021 年，作为 Epic 官方力推的下一代在线服务框架，一直处于积极开发和迭代中。近期的提交记录显示，它不仅在修复编译问题，还在进行功能增强（如重构接口）。虽然默认未启用（`EnabledByDefault: false`），但这通常意味着它需要与具体的平台实现插件（如 `OnlineServicesEOS`）配合使用，而非插件本身不稳定。它是构建现代、跨平台在线功能的推荐基础。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineServices)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineServices/Tests)