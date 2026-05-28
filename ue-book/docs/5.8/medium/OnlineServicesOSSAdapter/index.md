# Online Services OSS Adapter

> Online Services adapter for Online Subsystem implementations.

| 属性 | 值 |
|---|---|
| 中文名 | 在线服务适配器 |
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `OnlineServicesOSSAdapter` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-09-30 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineServicesOSSAdapter) | |

## 用途

UE5 引入了全新的 **Online Services（OSSv2）** API 来替代传统的 **Online Subsystem（OSSv1）** 接口。然而，大量已有的平台后端（如 Steam、PlayStation、Xbox 等）仍然基于 OSSv1 实现。这个插件充当**桥接适配器**，将 OSSv2 的调用自动转发到对应的 OSSv1 接口上，使得游戏可以使用新的 Online Services API 时，底层仍然复用已有的 OSSv1 平台实现。

具体来说，它解决了以下问题：

- **API 迁移过渡**：允许开发者逐步从 OSSv1 迁移到 OSSv2，无需等待所有平台后端都重写为 OSSv2
- **统一接口**：游戏代码只使用 OSSv2 的统一接口（`FAuth`, `FSessions`, `FSocial` 等），适配器负责翻译到对应的 OSSv1 接口（`IOnlineIdentity`, `IOnlineSession`, `IOnlineFriends` 等）
- **数据格式转换**：在 V1 和 V2 的数据结构之间双向转换，包括账号 ID、会话信息、好友关系、成就定义等
- **委托绑定辅助**：提供 `DelegateAdapter` 和 `MulticastAdapter` 模板工具，简化 V1 风格委托与 V2 风格回调之间的绑定

## 使用场景

- 你的项目已使用 Steam、EOS、PlayStation Network 等平台的 OSSv1 实现，但想开始使用新的 Online Services API
- 你正在从 Online Subsystem 架构迁移到 Online Services 架构，需要一个过渡方案
- 你需要通过 `IOnlineSubsystem::Get()` 获取的 OSSv1 后端来驱动 OSSv2 的在线服务调用
- 你在编写平台适配层代码，需要在 V1 和 V2 数据类型之间进行转换

## 蓝图用法

❌ 本插件没有暴露任何蓝图接口。这是一个纯 C++ 适配层，不包含 `UFUNCTION(BlueprintCallable)` 或 `BlueprintReadWrite` 属性。所有在线服务的功能通过 `OnlineServices` 插件暴露给蓝图。

## C++ 用法

### 头文件引入

```cpp
#include "Online/OnlineServicesOSSAdapter.h"
#include "Online/AuthOSSAdapter.h"
#include "Online/SessionsOSSAdapter.h"
#include "Online/DelegateAdapter.h"
#include "Online/MulticastAdapter.h"
#include "Online/OnlineIdOSSAdapter.h"
```

### 基本用法 — 创建并初始化适配器

适配器通常由框架自动创建，但在某些场景下你可能需要手动创建：

```cpp
#include "Online/OnlineServicesOSSAdapter.h"
#include "OnlineSubsystem.h"

using namespace UE::Online;

// 获取已注册的 OSS 后端
IOnlineSubsystem* OSS = IOnlineSubsystem::Get();
if (OSS)
{
    // 创建适配器实例，将 OSSv2 类型映射到 OSSv1 子系统
    TSharedRef<FOnlineServicesOSSAdapter> Adapter = MakeShared<FOnlineServicesOSSAdapter>(
        EOnlineServices::Null,      // 服务提供商标识
        TEXT("Default"),            // 配置名
        NAME_None,                  // 实例名
        OSS                         // 指向已有的 OSSv1 子系统
    );
    
    Adapter->RegisterComponents();
    Adapter->Initialize();
}
```

### 基本用法 — 通过模块获取所有适配器实例

```cpp
#include "Online/OnlineServicesOSSAdapterModule.h"

using namespace UE::Online;

FOnlineServicesOSSAdapterModule& Module = FModuleManager::GetModuleChecked<FOnlineServicesOSSAdapterModule>(
    TEXT("OnlineServicesOSSAdapter")
);

TArray<TSharedPtr<FOnlineServicesOSSAdapter>> AllAdapters;
Module.GetAllAdapters(AllAdapters);

for (auto& AdapterPtr : AllAdapters)
{
    // 检查每个适配器的底层 OSS 后端
    IOnlineSubsystem& Subsystem = AdapterPtr->GetSubsystem();
    UE_LOG(LogTemp, Log, TEXT("Adapter for OSS: %s"), *Subsystem.GetSubsystemName().ToString());
}
```

### 基本用法 — 委托适配器（Delegate Adapter）

`DelegateAdapter` 用于将 V1 风格的单次委托绑定转换为带弱指针安全检查的 `TUniqueFunction`：

```cpp
#include "Online/DelegateAdapter.h"

using namespace UE::Online;

// 传统 V1 写法（手动创建 lambda，无弱指针检查）：
// Identity->GetAuthToken(LocalUserNum, FOnAuthTokenGetComplete::CreateLambda(
//     [this](int32 UserNum, FString LoginToken) { ... }
// ));

// 使用 DelegateAdapter（自动弱指针检查，支持 move-only 捕获）：
auto Adapter = MakeDelegateAdapter(this, [this](int32 UserNum, FString LoginToken)
{
    // this 指针已通过弱指针验证是有效的
    HandleAuthToken(LoginToken);
});

// 转换为 TDelegate 使用
TDelegate<void(int32, FString)> BoundDelegate = *Adapter;
```

### 基本用法 — 多播委托适配器（Multicast Adapter）

`MulticastAdapter` 用于绑定多播委托，支持返回值控制解绑行为：

```cpp
#include "Online/MulticastAdapter.h"

using namespace UE::Online;

// void 返回值：执行一次后自动解绑
MakeMulticastAdapter(this, Identity->OnLoginCompleteDelegate,
    [this](int32 UserNum)
    {
        UE_LOG(LogTemp, Log, TEXT("User %d login complete"), UserNum);
        // 自动解绑
    }
);

// bool 返回值：返回 true 时解绑，返回 false 时继续监听
MakeMulticastAdapter(this, SessionInterface->OnSessionUserInviteAcceptedDelegate,
    [this](bool bWasSuccessful, int32 ControllerId, TSharedPtr<const FUniqueNetId> UserId,
           const FOnlineSessionSearchResult& Result) -> bool
    {
        if (bWasSuccessful)
        {
            HandleSessionJoined(Result);
            return true;  // 解绑
        }
        return false;  // 继续监听
    }
);
```

### 基本用法 — 错误转换

```cpp
#include "Online/ErrorsOSSAdapter.h"

using namespace UE::Online;

// 将 OSSv1 的 FOnlineError 转换为 OSSv2 的 FOnlineError
::FOnlineError V1Error;
V1Error.bSucceeded = false;
V1Error.ErrorCode = TEXT("STeamError_001");

FOnlineError V2Error = UE::Online::Errors::FromOssError(V1Error);
if (!V2Error.IsOk())
{
    UE_LOG(LogTemp, Warning, TEXT("Error: %s"), *V2Error.GetErrorMessage());
}

// 注册自定义平台错误处理器
UE::Online::Errors::AddOssPlatformErrorHandler(
    [](const FOnlineError& V2Error, const FOnlineErrorOss& V1Error) -> TOptional<FOnlineError>
    {
        // 自定义平台错误转换逻辑
        return TOptional<FOnlineError>();
    }
);
```

### 进阶用法 — 认证适配器（FAuthOSSAdapter）

```cpp
#include "Online/AuthOSSAdapter.h"

using namespace UE::Online;

// 获取适配器中的认证服务
TOnlineResult<FAuthLogin> LoginResult = Auth->Login(FAuthLogin::Params{
    /* PlatformUserId */ PlatformUserId,
    /* Credentials */ {}
}).Get();
```

### 进阶用法 — 会话适配器配置选项

会话适配器支持通过配置项控制行为，这些配置名定义在 `SessionsOSSAdapter.h` 中：

```cpp
#include "Online/SessionsOSSAdapter.h"

// 可配置的会话选项常量（供 OSS 配置使用）：
// OSS_ADAPTER_SESSIONS_ALLOW_SANCTIONED_PLAYERS   - 是否允许被制裁的玩家
// OSS_ADAPTER_SESSIONS_ALLOW_UNREGISTERED_PLAYERS  - 是否允许未注册玩家
// OSS_ADAPTER_SESSIONS_USE_LOBBIES_IF_AVAILABLE    - 是否优先使用 Lobby
// OSS_ADAPTER_SESSIONS_USE_LOBBIES_VOICE_CHAT_IF_AVAILABLE - Lobby 语音聊天
// OSS_ADAPTER_SESSIONS_USES_STATS                  - 会话是否使用统计
// OSS_ADAPTER_SESSIONS_SCHEMA_NAME                 - 会话 schema 名称
// OSS_ADAPTER_SESSIONS_BUILD_UNIQUE_ID             - 构建唯一 ID
// OSS_ADAPTER_SESSIONS_PING_IN_MS                  - Ping 延迟（毫秒）
```

## Demo 示例

一个完整的最小示例，展示如何创建适配器并注册自定义平台错误处理器：

```cpp
// MyOnlineService.h
#pragma once

#include "CoreMinimal.h"
#include "Online/OnlineServicesOSSAdapter.h"
#include "Online/ErrorsOSSAdapter.h"

class FMyOnlineService
{
public:
    void Initialize();
    void Shutdown();

private:
    UE::Online::TSharedPtr<UE::Online::FOnlineServicesOSSAdapter> OnlineServices;
    UE::Online::TOnlineAsyncOpHandle<UE::Online::FAuthLogin> LoginHandle;
};
```

```cpp
// MyOnlineService.cpp
#include "MyOnlineService.h"
#include "OnlineSubsystem.h"
#include "Online/DelegateAdapter.h"

using namespace UE::Online;

void FMyOnlineService::Initialize()
{
    // 1. 获取当前的 Online Subsystem
    IOnlineSubsystem* OSS = IOnlineSubsystem::Get();
    if (!OSS)
    {
        UE_LOG(LogTemp, Error, TEXT("No Online Subsystem found"));
        return;
    }

    // 2. 创建适配器
    OnlineServices = MakeShared<FOnlineServicesOSSAdapter>(
        EOnlineServices::Null,
        TEXT("Default"),
        NAME_None,
        OSS
    );

    // 3. 注册组件并初始化
    OnlineServices->RegisterComponents();
    OnlineServices->Initialize();

    UE_LOG(LogTemp, Log, TEXT("OnlineServicesOSSAdapter initialized for: %s"),
        *OSS->GetSubsystemName().ToString());
}

void FMyOnlineService::Shutdown()
{
    OnlineServices.Reset();
}
```

## 模块依赖

本插件本身依赖 OnlineServices 和 OnlineSubsystem 两个插件。作为适配层，它对使用者的模块没有特殊依赖要求，使用者只需依赖 `OnlineServices` 插件中的 `OnlineServices` 模块即可。

| 模块 | 用途 |
|---|---|
| `OnlineServices` | 提供 OSSv2 接口定义（作为插件依赖） |
| `OnlineSubsystem` | 提供 OSSv1 接口定义（作为插件依赖） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 批量迁移 UE_LOG 到 UE_LOGF 宏 |
| 2026-04-09 | `ce8bc99f` | UE: OSSv2 - fix mirrored session settings update never firing callback | 修复镜像会话设置更新后回调未触发的问题 |
| 2026-02-02 | `f7c9f067` | Fix client crash on shutdown when the default online subsystem is reloaded, invalidating the OSS ada | 修复关闭时默认 OSS 重载导致适配器失效而崩溃 |
| 2025-11-04 | `69504011` | UE - OSSv2 : Fix for shutdown order in OSSv2 with Adapters | 修复适配器场景下 OSSv2 关闭顺序问题 |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 自动代码修复：将空析构函数改为 `= default` |

### 维护评价

- **创建时间**：2022 年 9 月，从 Experimental 目录迁移到正式目录，标志着 OSSv2 架构进入稳定阶段
- **活跃维护**：✅ 是。最近 6 个月内有多次实质性 bug 修复（会话回调、关闭顺序、崩溃修复），说明该插件在生产环境中被广泛使用且持续维护
- **更新内容**：主要是稳定性修复和崩溃修复，没有大的功能变更，说明接口已趋于稳定
- **稳定性**：近期的 commit 集中在修复适配器与 OSS 交互的边界情况（重载、关闭顺序），表明框架已经成熟但边缘场景仍在被发现和修复
- **推荐使用**：✅ 推荐。这是从 OSSv1 迁移到 OSSv2 的官方桥梁，如果你的项目需要同时支持两种 API，这是必经之路。注意该插件**默认不启用**（`EnabledByDefault: false`），需要在项目设置中手动启用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineServicesOSSAdapter)
- [OnlineServices 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineServices)
- [OnlineSubsystem 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineSubsystem)