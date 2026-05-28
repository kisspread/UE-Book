# Online Services

> Shared code for interacting with online services implementations.

| 属性 | 值 |
|---|---|
| 中文名 | 在线服务框架 |
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `OnlineServicesInterface` (Runtime), `OnlineServicesCommon` (Runtime), `OnlineServicesCommonEngineUtils` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-09-30 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineServices) | |

## 用途

`OnlineServices` 插件提供了一套统一的、面向未来的在线服务（如登录、会话、排行榜、好友等）API 抽象层。它的核心价值在于**解耦游戏逻辑与具体的在线平台实现**。

在传统 `OnlineSubsystem` 架构中，游戏代码需要直接与特定平台（如 Steam, EOS, 主机平台）的接口打交道，导致平台切换困难且代码混乱。`OnlineServices` 旨在解决这个问题，它定义了一套平台无关的接口（`OnlineServicesInterface` 模块），并由具体平台（如 EOS）或通用实现（如 `OnlineServicesCommon`）来提供这些接口的具体功能。

`OnlineServicesCommonEngineUtils` 模块则为这些在线服务提供了与 Unreal Engine 底层系统（如网络驱动、世界上下文）交互所需的通用工具和适配代码。

## 使用场景

- **开发跨平台游戏**：你的游戏需要同时支持 Steam、Epic Online Services (EOS)、PlayStation、Xbox 等多个在线平台，使用此框架可以编写一次核心在线功能代码，通过切换 `OnlineServices` 的实现模块来适配不同平台。
- **实现自定义在线服务**：你需要一个本地的、用于测试的或基于局域网的在线服务实现（如 `OnlineServicesNull` 或 `OnlineServicesLAN`），无需从头实现复杂的平台交互，只需基于 `OnlineServicesCommon` 进行扩展。
- **简化网络会话管理**：你需要创建、查找、加入游戏会话（房间），此插件提供了标准化的 `Sessions` 接口和会话生命周期管理。

## 蓝图用法

此插件主要为 C++ 框架，旨在为其他在线服务模块（如 EOSOnlineServices）提供基础。蓝图功能通常由最终的平台实现模块（如 EOS）或 `OnlineSubsystemBlueprints` 兼容层暴露。`OnlineServicesCommonEngineUtils` 模块本身不提供直接暴露给蓝图的节点。

核心的会话管理功能（如创建、查找、加入房间）的蓝图节点，通常会在平台具体实现（如 `EOS`）或 `OnlineSubsystem` 蓝图桥接插件中找到。

## C++ 用法

### 头文件引入

根据你要使用的模块和功能引入相应头文件。

```cpp
// 使用 LAN 会话相关功能
#include "Online/SessionsLAN.h"

// 使用引擎工具函数
#include "Online/OnlineServicesCommonEngineUtils.h"
```

### 基本用法：使用 LAN 会话

`OnlineServicesCommonEngineUtils` 提供了 `FSessionsLAN` 的基础实现，可用于创建局域网内的游戏会话。

```cpp
// 假设已有一个 FOnlineServicesCommon 实例（通常由具体平台模块提供）
FOnlineServicesCommon& OnlineServices = ...;

// 创建 LAN 会话服务实例（需要一个网络监听端口，通常为 7777）
FSessionsLAN SessionsLAN(OnlineServices);

// 创建一个 LAN 会话
FSessionsLAN::FCreateSession::Params CreateParams;
CreateParams.LocalAccountId = LocalUserAccountId;
CreateParams.SessionName = FName("MyLANGame");
// ... 设置其他参数，如最大玩家数，是否公开等 ...

TFuture<TOnlineResult<FCreateSession>> CreateFuture = SessionsLAN.CreateSession(CreateParams);
// 处理异步结果...

// 在 Tick 中驱动 LAN 会话的网络发现与更新
SessionsLAN.Tick(DeltaSeconds);
```

*来源文件*: `Engine/Plugins/Online/OnlineServices/Source/OnlineServicesCommonEngineUtils/Public/Online/SessionsLAN.h`

### 进阶用法：世界上下文对象缓存

`FWorldContextScopedObjectCache` 是一个重要的工具模板，用于管理与特定世界（PIE 实例）生命周期绑定的对象缓存，确保编辑器下多PIE实例的正确性。

```cpp
#include "Online/WorldContextScopedObjectCache.h"

// 定义一个缓存的在线服务对象
FWorldContextScopedObjectCache<FOnlineServicesCommon> ServicesCache;

// 获取或创建一个与特定世界上下文关联的服务实例
FName WorldContextName = GetWorld()->GetFName();
TSharedPtr<FOnlineServicesCommon> Services = ServicesCache.FindOrAdd(
    WorldContextName,
    [this]() -> TSharedRef<FOnlineServicesCommon> {
        // 创建并返回一个新的 FOnlineServicesCommon 实例
        return MakeShared<FOnlineServicesCommon>(/*...*/);
    }
);

if (Services.IsValid())
{
    // 使用该世界的服务实例进行操作...
}
```

*来源文件*: `Engine/Plugins/Online/OnlineServices/Source/OnlineServicesCommonEngineUtils/Public/Online/WorldContextScopedObjectCache.h`

## Demo 示例

以下是一个最小的示例，展示如何创建一个自定义的 LAN 会话子类并实现序列化。

```cpp
// MyLANSessions.h
#pragma once
#include "Online/SessionsLAN.h"

class FMyLANSessions : public UE::Online::FSessionsLAN
{
public:
    FMyLANSessions(UE::Online::FOnlineServicesCommon& InServices);

protected:
    // 实现自定义的会话数据序列化
    virtual void AppendSessionToPacket(FNboSerializeToBuffer& Packet, const UE::Online::FSessionLAN& Session) override;
    virtual void ReadSessionFromPacket(FNboSerializeFromBuffer& Packet, UE::Online::FSessionLAN& Session) override;
};
```

```cpp
// MyLANSessions.cpp
#include "MyLANSessions.h"

FMyLANSessions::FMyLANSessions(UE::Online::FOnlineServicesCommon& InServices)
    : FSessionsLAN(InServices)
{
}

void FMyLANSessions::AppendSessionToPacket(FNboSerializeToBuffer& Packet, const UE::Online::FSessionLAN& Session)
{
    // 先调用父类的标准序列化
    UE::Online::NboSerializerLANSvc::SerializeToBuffer(Packet, Session);
    // 追加你自定义的会话数据字段
    // Packet << MyCustomField;
}

void FMyLANSessions::ReadSessionFromPacket(FNboSerializeFromBuffer& Packet, UE::Online::FSessionLAN& Session)
{
    // 先调用父类的标准反序列化
    UE::Online::NboSerializerLANSvc::SerializeFromBuffer(Packet, Session);
    // 读取你自定义的会话数据字段
    // Packet >> MyCustomField;
}
```

## 模块依赖

从 `OnlineServicesCommonEngineUtils.Build.cs` 分析，除了常见的 `Core`, `Engine` 模块外，其独特的依赖为：

| 模块 | 用途 |
|---|---|
| `OnlineServicesCommon` | 基础的通用在线服务实现和接口定义，本模块的基类来源于此。 |
| `OnlineSubsystemUtils` | 提供底层的网络工具和 `FLANSession` 管理器，用于实现局域网会话的广播和发现。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量截断为浮点数的编译器警告。 |
| 2026-05-12 | `4ad1dbcc` | [OnlineSubsystem][OnlineServices] Guard SetPort callers against bogus port values from EOS:<PUID> ad | 保护 SetPort 调用方免受来自 EOS 的无效端口值的影响。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正了32位和64位格式化说明符不匹配的问题。 |
| 2026-04-14 | `2c013d6c` | Online Services EOS Presence Refactor: | 在线服务EOS Presence状态重构。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的 UE_LOG 宏迁移至新的 UE_LOGF 宏。 |

### 维护评价

该插件从 `Experimental` 阶段迁移至正式插件（`Engine/Plugins/Online`），表明其架构已趋于稳定。近期的提交历史（截至 2026 年）显示它仍在被**积极维护**。更新内容涵盖代码质量改进（修复警告）、安全性修复（防御无效输入）以及功能重构（EOS Presence），表明这是一个成熟且活跃的核心基础设施模块。

由于它是连接游戏与各平台在线服务的标准化桥梁，对于任何需要在线功能的 UE5 项目都**推荐使用**，尤其是新项目或跨平台项目。需要注意的是，它默认未启用，需要在项目设置中手动开启，并配合具体的平台实现插件（如 `OnlineServicesEOS`）使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineServices)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/OnlineServices)