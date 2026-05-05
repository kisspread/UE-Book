# Online Services Epic Common

> Common Online Services implementation with shared funcionality between Epic Account Services and Epic Game Services.

| 属性 | 值 |
|---|---|
| 分类 | Online Platform |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | OnlineServicesEpicCommon (Runtime) |
| 创建时间 | 2025-01-17 |
| 年龄标签 | 🆕 (~1.3 年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineServicesEpicCommon) | |

## 用途

这个 plugin 是 UE5 在 5.6 周期中将 EOS (Epic Online Services) 在线服务架构**拆分**后的产物。在此之前，Epic Account 和 Epic Game Services 的共用逻辑都耦合在 `OnlineServicesEOS` 和 `OnlineServicesEOSGS` 中。拆分之后，出现了多个独立 plugin：

- `OnlineServicesEOS` — Epic Account Services (玩家账户/登录)
- `OnlineServicesEOSGS` — Epic Game Services (社交/成就/排行榜等)
- `OnlineServicesEpicAccount` — 轻量版 Account Services
- `OnlineServicesEpicGame` — 轻量版 Game Services

**本 plugin（OnlineServicesEpicCommon）** 提供上述所有 plugin 的**共享基础设施**：

1. **EOS Platform Handle 管理** — 统一的 `FOnlineServicesEpicCommonPlatformFactory` 负责创建和管理 EOS SDK 的 Platform 实例，避免各 plugin 重复初始化
2. **Account ID 解析** — `IEpicAccountIdResolver` 和 `IEpicProductUserIdResolver` 接口，让不同 plugin 中的组件可以跨边界解析 Epic 用户标识
3. **Auth 登录选项公共逻辑** — `FEOSAuthLoginOptionsCommon` 封装了 EOS Auth SDK 的登录凭证构造，各 plugin 的 Auth 实现共享此逻辑
4. **错误映射** — `OnlineErrorEpicCommon` 提供 `EOS_EResult` 到 UE `FOnlineError` 的统一转换
5. **Fast Tick 机制** — 让 EOS SDK 在异步操作期间以最高频率轮询，缩短延迟

简单来说：**如果你直接使用这个 plugin，说明你正在用 UE5 的新 Online Services 框架 + Epic Online Services 后端**。你通常不会单独启用它，而是由 `OnlineServicesEOS` 或 `OnlineServicesEOSGS` 自动依赖。

## 使用场景

- 你在做一个使用 Epic Online Services 后端的多人游戏 → 这个 plugin 是 EOS 在线服务的公共基础层
- 你需要将 Epic Account ID / Product User ID 映射为 UE 的 `FAccountId` → 使用本 plugin 的 Resolver 接口
- 你在编写跨 EOS Account/Game Services 的通用组件 → 依赖本 plugin 的公共接口

## 蓝图用法

本 plugin **没有暴露任何 BlueprintCallable 函数**。它是一个纯 C++ 运行时模块，作为底层基础设施被其他 Online Services plugin 使用。

## C++ 用法

### 头文件引入

```cpp
#include "Online/OnlineServicesEpicCommon.h"
#include "Online/EpicAccountIdResolver.h"
#include "Online/EpicProductUserIdResolver.h"
#include "Online/EOSAuthLoginOptionsCommon.h"
#include "Online/OnlineErrorEpicCommon.h"
```

### 获取 EOS Platform Handle

`FOnlineServicesEpicCommon` 是所有 Epic 在线服务 plugin 的基类。通过它可以访问底层 EOS Platform Handle：

```cpp
// 来源: Online/OnlineServicesEpicCommon.h
using namespace UE::Online;

// 假设你有一个指向 FOnlineServicesEpicCommon 子类实例的指针
TSharedPtr<FOnlineServicesEpicCommon> EpicOnlineServices = /* ... */;

// 获取 EOS Platform Handle（用于直接调用 EOS C SDK）
IEOSPlatformHandlePtr PlatformHandle = EpicOnlineServices->GetEOSPlatformHandle();
```

### EOS 错误映射

将 EOS SDK 的 `EOS_EResult` 转换为 UE 在线服务框架的 `FOnlineError`：

```cpp
// 来源: Online/OnlineErrorEpicCommon.h
#include "Online/OnlineErrorEpicCommon.h"

using namespace UE::Online;

// 基本用法：将 EOS 错误码转为 FOnlineError
EOS_EResult Result = EOS_Platform_Tick(PlatformHandle);
if (Result != EOS_Success)
{
    FOnlineError OnlineError = Errors::FromEOSResult(Result);
    UE_LOG(LogTemp, Error, TEXT("EOS Error: %s"), *OnlineError.GetErrorMessage());
}

// 特定错误可以直接比较
FOnlineError SomeError = /* ... */;
if (SomeError == Errors::FromEOSResult(EOS_EResult::EOS_NoConnection))
{
    // 处理无连接情况
}
```

### Account ID 解析

在 EOS SDK 回调中，你收到的是原始的 `EOS_EpicAccountId` 或 `EOS_ProductUserId`，需要解析为 UE 的 `FAccountId`：

```cpp
// 来源: Online/EpicAccountIdResolver.h
#include "Online/EpicAccountIdResolver.h"

using namespace UE::Online;

// IEpicAccountIdResolver 由具体 plugin（如 OnlineServicesEOS）实现
// 获取 resolver 的辅助函数（绑定到特定 async op）
auto ResolveFn = Resolver->ResolveEpicAccountIdFn();

// 在异步操作中使用
FOnlineAsyncOp& MyOp = /* ... */;
EOS_EpicAccountId EpicId = /* 从 EOS 回调获得 */;

ResolveFn(MyOp, EpicId).Then([](TFuture<FAccountId> Future)
{
    FAccountId AccountId = Future.Get();
    // 使用 UE 的 AccountId 进行后续操作
});
```

类似地，`IEpicProductUserIdResolver` 用于解析 `EOS_ProductUserId`：

```cpp
// 来源: Online/EpicProductUserIdResolver.h
auto ResolveProductFn = ProductResolver->ResolveProductUserIdFn();

EOS_ProductUserId ProductUserId = /* 从 EOS 回调获得 */;
ResolveProductFn(MyOp, ProductUserId).Then([](TFuture<FAccountId> Future)
{
    FAccountId AccountId = Future.Get();
});
```

### Fast Tick 机制

当发起 EOS SDK 异步调用时，可以让 EOS 以最高频率轮询以减少延迟：

```cpp
// 来源: Online/OnlineServicesEpicCommon.cpp
// 在调用 EOS SDK 之前启用 fast tick
EpicOnlineServices->AddEOSSDKFastTick(MyAsyncOp);

// 调用 EOS SDK 函数...
EOS_Platform_Auth_Login(PlatformHandle, &LoginOptions, this, OnLoginComplete);

// 在完成回调中移除 fast tick（也可以不调用，async op 销毁时自动移除）
EpicOnlineServices->RemoveEOSSDKFastTick(MyAsyncOp);
```

Fast tick 可通过配置关闭：

```ini
; Engine.ini
[OnlineServices.EOS]
bEnableAsyncOpFastTick=false
```

### 平台类型转换

在 UE 平台类型和 EOS 平台类型之间转换：

```cpp
// 来源: Online/OnlineServicesEpicCommon.h
EOnlinePlatformType UeType = EOnlinePlatformType::Steam;
EOS_OnlinePlatformType EosType = EOnlinePlatformType_To_EOS_OnlinePlatformType(UeType);
// EosType == EOS_OPT_Steam

// 反向转换
EOnlinePlatformType BackToUe = EOS_OnlinePlatformType_To_EOnlinePlatformType(EOS_OPT_PSN);
// BackToUe == EOnlinePlatformType::PSN
```

支持的平台映射：Epic, Steam, PSN, Nintendo, XBL, Unknown。

## Demo 示例

### 在 Build.cs 中添加依赖

```csharp
// 你的模块 Build.cs
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "OnlineServicesCommon",  // 在线服务框架
});

PrivateDependencyModuleNames.AddRange(new string[] {
    "OnlineServicesEpicCommon",  // 本 plugin
    "OnlineServicesInterface",
    "EOSShared",
});
```

### 启用 Plugin

在 `.uproject` 或 Editor 的 Plugins 面板中手动启用（默认不启用）：

```json
{
    "Plugins": [
        {
            "Name": "OnlineServicesEpicCommon",
            "Enabled": true
        }
    ]
}
```

> **注意**：通常你不需要直接启用这个 plugin。启用 `OnlineServicesEOS` 或 `OnlineServicesEOSGS` 会自动将其拉入。

### EOS 平台配置

在 `Engine.ini` 中配置 EOS 连接参数（旧方式）：

```ini
[OnlineServices.EOS]
PlatformConfigName=MyPlatform

[EOSSDK.Platform.MyPlatform]
ProductId=your_product_id
SandboxId=your_sandbox_id
DeploymentId=your_deployment_id
ClientId=your_client_id
ClientSecret=your_client_secret
ClientEncryptionKey=your_encryption_key
```

推荐使用 `EOSShared` 的命名配置方式（新方式），避免重复配置。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心模块 |
| `OnlineServicesCommon` | 在线服务框架通用基类（`FOnlineServicesCommon`） |
| `EOSSDK` | Epic Online Services SDK（私有依赖） |
| `EOSShared` | EOS SDK 共享管理层（私有依赖） |
| `OnlineServicesInterface` | 在线服务接口定义（私有依赖） |

### Plugin 依赖

| Plugin | 用途 |
|---|---|
| `OnlineServices` | 在线服务框架 plugin |
| `EOSShared` | EOS SDK 共享管理 plugin |

### 支持平台

Android, IOS, Linux, LinuxArm64, Mac, Win64

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-08-20 | `3540ed79` | 修复 OnlineServicesEpicCommon.h 中缺少平台 include 的问题 |
| 2025-08-20 | `7e11055c` | 创建 UserInfoEpicAccount，修复 split plugins 场景下 UserInfoEOS 的功能错误 |
| 2025-07-21 | `0df8450d` | 将 resolve API 从 FAuthEOS/FAuthEOSGS 中提取为独立的 IEpicAccountIdResolver/IEpicProductUserIdResolver 接口 |

### 维护评价

- **年龄**：~1.3 年（2025-01 创建），🆕
- **活跃程度**：**活跃维护**。最近 1 个月内有功能性更新和重构
- **性质**：这是 UE5 在线服务架构拆分的产物（EOS Split Plugins），属于核心基础设施
- **风险**：架构仍在演进中（如 resolve API 的提取），接口可能继续调整
- **推荐**：如果你使用 EOS 后端，这个 plugin 是自动依赖的基础层，不需要直接关注。如果你在开发跨 EOS 服务的自定义组件，可以基于本 plugin 的 Resolver 接口构建

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineServicesEpicCommon)
- [OnlineServicesEOS plugin](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineServicesEOS) — Epic Account Services 实现
- [OnlineServicesEOSGS plugin](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineServicesEOSGS) — Epic Game Services 实现
- [EOSShared plugin](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/EOSShared) — EOS SDK 共享管理
