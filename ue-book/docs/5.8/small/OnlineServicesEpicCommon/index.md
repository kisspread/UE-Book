# Online Services Epic Common

> Common Online Services implementation with shared funcionality between Epic Account Services and Epic Game Services.

| 属性 | 值 |
|---|---|
| 中文名 | 史诗服务通用 |
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `OnlineServicesEpicCommon` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-01-17 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineServicesEpicCommon) | |

## 用途

该插件是 Epic 在线服务（EOS）集成架构重构的产物。它的主要目的是提取并封装 Epic Account Services (EAS) 和 Epic Game Services (EGS) 共享的底层功能，避免在 `OnlineServicesEOS` 和 `OnlineServicesEOSGS`（以及未来的新服务实现）中重复编写相同的代码。

具体来说，它解决的核心问题是 **EOS 集成中的代码复用**。在引入此插件之前，处理认证、账户 ID 解析、错误映射等通用 EOS SDK 交互逻辑分别存在于多个插件中。`OnlineServicesEpicCommon` 将这些公共逻辑集中到一个地方，为所有基于 EOS 的在线服务实现提供了一个稳固的基础层。

## 使用场景

- 当你正在开发或维护一个需要与 Epic 在线服务（如 EOS， EAS， EGS）集成的 UE5 项目时，这个插件会作为基础依赖。
- 当你需要构建一个自定义的在线服务实现，并且该实现需要与 EOS SDK 进行交互时，可以基于此类 `FOnlineServicesEpicCommon` 构建，以复用其平台句柄管理、异步操作快速 Tick 和通用错误处理机制。
- 当你的项目需要同时支持 Epic 账户和游戏账户，并且希望共享底层认证和 ID 解析逻辑时。

## 蓝图用法

该插件主要为 C++ 服务层提供基础架构，**不直接暴露蓝图节点**。其功能通过继承它的子服务类（如 `OnlineServicesEOS`， `OnlineServicesEpicAccount` 等）间接影响蓝图可用的在线功能。

## C++ 用法

### 头文件引入

```cpp
#include "Online/OnlineServicesEpicCommon.h"
#include "Online/EOSAuthLoginOptionsCommon.h"
#include "Online/OnlineErrorEpicCommon.h"
#include "Online/EpicAccountIdResolver.h"
#include "Online/EpicProductUserIdResolver.h"
```

### 基本用法

此插件的核心类 `FOnlineServicesEpicCommon` 通常不会被直接实例化，而是作为其他具体服务实现的基类。

**示例：创建一个继承自 `FOnlineServicesEpicCommon` 的新服务类**

```cpp
// MyOnlineServicesEpic.h
#pragma once

#include "Online/OnlineServicesEpicCommon.h"

namespace UE::Online
{

class FMyOnlineServicesEpic : public FOnlineServicesEpicCommon
{
public:
    using Super = FOnlineServicesEpicCommon;

    FMyOnlineServicesEpic(const FString& InServiceConfigName, FName InInstanceName, FName InInstanceConfigName);
    virtual ~FMyOnlineServicesEpic() = default;

    virtual void Initialize() override;
};

} // namespace UE::Online
```

```cpp
// MyOnlineServicesEpic.cpp
#include "MyOnlineServicesEpic.h"

namespace UE::Online
{

FMyOnlineServicesEpic::FMyOnlineServicesEpic(const FString& InServiceConfigName, FName InInstanceName, FName InInstanceConfigName)
    : Super(InServiceConfigName, InInstanceName, InInstanceConfigName)
{
}

void FMyOnlineServicesEpic::Initialize()
{
    // 调用父类的初始化
    Super::Initialize();
    
    // 在这里初始化你自己的服务特有组件
    UE_LOG(LogOnline, Log, TEXT("MyOnlineServicesEpic Initialized"));
}

} // namespace UE::Online
```
*来源：`OnlineServicesEpicCommon/Public/Online/OnlineServicesEpicCommon.h`*

### 进阶用法

**1. 使用 EOS 错误处理系统**

该插件提供了将 `EOS_EResult` 映射到 UE 统一在线错误 (`FOnlineError`) 的工具。

```cpp
// 调用 EOS SDK 函数后处理结果
EOS_EResult EosResult = SomeEOSSDKFunction();
if (EosResult != EOS_EResult::EOS_Success)
{
    // 将 EOS 错误转换为 UE Online 错误
    FOnlineError OnlineError = UE::Online::Errors::FromEOSResult(EosResult);
    
    // 你可以直接比较 FOnlineError 和 EOS_EResult
    if (OnlineError == EOS_EResult::EOS_InvalidAuth)
    {
        // 处理特定的认证错误
    }
    
    UE_LOG(LogOnline, Error, TEXT("EOS Operation Failed: %s"), *OnlineError.GetErrorMessage());
}
```
*来源：`OnlineServicesEpicCommon/Public/Online/OnlineErrorEpicCommon.h`*

**2. 解析 EOS 账户 ID**

通过提供的解析器接口，可以将 EOS 特有的 `EpicAccountId` 或 `ProductUserId` 转换为 UE 通用的 `FAccountId`。

```cpp
// 假设你有一个实现了 IEpicAccountIdResolver 的服务实例
// 通常由 OnlineServicesEOS 或 OnlineServicesEpicAccount 实现
TSharedPtr<IEpicAccountIdResolver> AccountIdResolver = /* ... */;

// 解析单个 EpicAccountId
EOS_EpicAccountId EpicId = /* ... */;
TFuture<FAccountId> AccountIdFuture = AccountIdResolver->ResolveAccountId(MyLocalAccountId, EpicId);
AccountIdFuture.Next([](FAccountId ResolvedId)
{
    if (ResolvedId.IsValid())
    {
        // 成功解析
    }
});

// 批量解析
TArray<EOS_EpicAccountId> EpicIds = /* ... */;
TFuture<TArray<FAccountId>> AccountIdsFuture = AccountIdResolver->ResolveAccountIds(MyLocalAccountId, EpicIds);
AccountIdsFuture.Next([](const TArray<FAccountId>& ResolvedIds)
{
    // 处理所有已解析的ID
});
```
*来源：`OnlineServicesEpicCommon/Public/Online/EpicAccountIdResolver.h`， `EpicProductUserIdResolver.h`*

## Demo 示例

一个展示如何从 `FOnlineServicesEpicCommon` 派生并添加自定义功能的最小示例。

**MyCustomEOSService.h**
```cpp
#pragma once

#include "Online/OnlineServicesEpicCommon.h"

namespace UE::Online
{

/**
 * 一个自定义的 EOS 服务实现，演示如何扩展 EpicCommon 基类。
 */
class FMyCustomEOSService : public FOnlineServicesEpicCommon
{
public:
    using Super = FOnlineServicesEpicCommon;

    ONLINESERVICESEPICCOMMON_API FMyCustomEOSService(const FString& InServiceConfigName, FName InInstanceName, FName InInstanceConfigName);
    ONLINESERVICESEPICCOMMON_API virtual ~FMyCustomEOSService() = default;

    // 重写 FlushTick 以添加自定义逻辑
    ONLINESERVICESEPICCOMMON_API virtual void FlushTick(float DeltaSeconds) override;

    // 自定义函数：检查当前 EOS 平台句柄状态
    ONLINESERVICESEPICCOMMON_API bool IsPlatformHandleValid() const;
};

} // namespace UE::Online
```

**MyCustomEOSService.cpp**
```cpp
#include "MyCustomEOSService.h"
#include "Online/OnlineServicesEpicCommonModule.h" // 用于日志类别

namespace UE::Online
{

FMyCustomEOSService::FMyCustomEOSService(const FString& InServiceConfigName, FName InInstanceName, FName InInstanceConfigName)
    : Super(InServiceConfigName, InInstanceName, InInstanceConfigName)
{
    UE_LOG(LogOnlineServicesEpicCommon, Log, TEXT("Custom EOS Service created."));
}

void FMyCustomEOSService::FlushTick(float DeltaSeconds)
{
    // 执行父类的 FlushTick (包括 EOS SDK 处理)
    Super::FlushTick(DeltaSeconds);
    
    // 在这里添加你自己的每帧更新逻辑
    // 例如：轮询某些自定义状态
}

bool FMyCustomEOSService::IsPlatformHandleValid() const
{
    return EOSPlatformHandle.IsValid();
}

} // namespace UE::Online
```
*来源：基于 `OnlineServicesEpicCommon/Public/Online/OnlineServicesEpicCommon.h` 和 `OnlineServicesEpicCommon/Private/Online/OnlineServicesEpicCommonModule.h` 的示例结构*

## 模块依赖

要使用 `OnlineServicesEpicCommon` 模块，你的模块的 `.Build.cs` 文件需要添加以下依赖：

| 模块 | 用途 |
|---|---|
| `OnlineServicesEpicCommon` | 本插件的核心模块 |
| `OnlineServices` | UE 统一在线服务框架基类 |
| `EOSShared` | Epic Online Services SDK 的共享类型和定义 |
| `EOSSDK` | Epic Online Services SDK 核心库 |

*注：`OnlineServicesEpicCommon` 模块自身会链接这些库，你的模块只需在其 `.Build.cs` 的 `PublicDependencyModuleNames` 或 `PrivateDependencyModuleNames` 中添加 `OnlineServicesEpicCommon`，传递依赖会处理其余部分。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移为 UE_LOGF 以提高日志性能。 |
| 2025-10-30 | `374bc354` | Increase ApiVersion for EOS_Auth_LoginOptions from 2 to 3 | 将认证登录选项的 API 版本从 2 提升至 3，适配 EOS SDK 更新。 |
| 2025-08-20 | `3540ed79` | Missing platform include in OnlineServicesEpicCommon.h | 修复头文件中缺失的平台包含，解决编译问题。 |
| 2025-08-20 | `7e11055c` | Created UserInfoEpicAccount to cover errors in functionality UserInfoEOS has when using split plugin | 创建 UserInfoEpicAccount 组件，解决在使用分离插件时 UserInfoEOS 功能出现的错误。 |
| 2025-07-21 | `0df8450d` | - Factor resolve APIs out of FAuthEOS[GS] into IEpicAccountIdResolver/IEpicProductUserIdResolver API | 将账户 ID 解析接口从具体认证类重构为独立的 `IEpicAccountIdResolver` 和 `IEpicProductUserIdResolver` 接口，提升复用性。 |

### 维护评价

`OnlineServicesEpicCommon` 是一个相对较新（创建于 2025 年 1 月）且处于 **活跃维护** 状态的插件。它是由 Epic Games 官方维护的，用于支撑其在线服务集成架构。

- **最近更新**：最后一次更新（日志迁移）在 2026 年 4 月，表明它仍在跟随引擎和 EOS SDK 的更新而演进。
- **功能发展**：从 git 历史看，插件在创建后的几个月内进行了重要的架构优化（如重构 ID 解析接口），说明其设计仍在细化中。
- **稳定性**：作为基础设施组件，其更新主要涉及 API 版本升级、平台兼容性修复和代码重构，旨在提升稳定性和可维护性。
- **推荐度**：**推荐使用**。如果你正在开发需要深度集成 Epic 在线服务的项目，这个插件提供了必要且经过官方维护的基础。由于它是 `EnabledByDefault=false`，你需要在项目插件设置中手动启用它，或者在你自己的依赖它的插件中声明对它的依赖。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineServicesEpicCommon)
- [官方文档](https://docs.unrealengine.com/en-US/InteractiveExperiences/Online/) (UE 在线子系统/服务总文档，可能不专门涵盖此插件)
- [相关插件: OnlineServicesEOS](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineServicesEOS)
- [相关插件: OnlineServicesEOSGS](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineServicesEOSGS)