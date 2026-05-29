# EOS Shared

> Responsible for init/shutdown of the EOSSDK runtime library.

| 属性 | 值 |
|---|---|
| 中文名 | EOS 运行时管理 |
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `EOSShared` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-04-29 |
| 年龄标签 | 🏛️ 文物（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/EOSShared) | |

## 用途

EOSShared 是所有 EOS（Epic Online Services）在线功能插件的**基础设施层**。它本身不提供玩家可感知的在线功能（如匹配、成就、好友列表等），而是负责：

1. **EOSSDK 运行时生命周期管理**：在合适的时机加载 EOSSDK 动态库、调用 `EOS_Initialize` / `EOS_Shutdown`，确保 SDK 正确初始化和清理。
2. **多平台适配**：为 Windows、Android、iOS、Linux、Mac 提供平台特定的初始化逻辑（如 Steam 集成、移动端前后台切换、缓存目录差异等）。
3. **Platform Handle 管理**：管理多个 EOS Platform 实例的创建、Tick 轮询和生命周期（支持多配置多实例场景）。
4. **回调安全包装**：提供 RAII 风格的 EOS 回调包装器（`TEOSCallback`、`TEOSGlobalCallback`），确保回调触发时对象仍然存活，避免悬挂指针。
5. **EOS 类型工具**：提供 `LexToString` / `LexFromString` 等序列化工具函数，方便 EOS 枚举和 ID 类型在 UE 中的字符串转换。

简单来说，任何需要使用 EOS SDK 的插件（如 EOS Online Subsystem、EOS Voice Chat 等）都隐式依赖此插件。

## 使用场景

- 你使用 Epic Online Services 作为游戏的后端服务（账号、匹配、成就等）→ 所有 EOS 功能插件的基础依赖
- 你需要自定义 EOS SDK 的初始化参数（产品 ID、沙盒 ID、加密密钥等）→ 通过 `FEOSSDKPlatformConfig` 配置
- 你需要在 EOS 回调中安全地操作 UE 对象，避免对象被提前销毁 → 使用 `TEOSCallback` / `TEOSGlobalCallback` 包装器
- 你需要管理 EOS Platform 的 Tick 频率（如 Overlay 可见时需要更高频率）→ 使用 `IEOSFastTickLock`
- 你开发自定义 EOS 组件并需要注册事件通知 → 使用 `EOS_RegisterComponentEventHandler` 的 RAII 事件注册

## 蓝图用法

此插件为纯 C++ 基础设施层，**不包含任何蓝图可调用函数**。所有 API 均为 C++ 接口。

## C++ 用法

### 头文件引入

```cpp
#include "IEOSSDKManager.h"
#include "EOSSharedTypes.h"
#include "EOSShared.h"
```

### 基本用法

获取 SDK Manager 单例并检查初始化状态：

```cpp
// 来源: Source/EOSShared/Public/IEOSSDKManager.h
// 通过 IModularFeatures 获取 SDK Manager（单例模式）
IEOSSDKManager* SDKManager = IEOSSDKManager::Get();

if (SDKManager && SDKManager->IsInitialized())
{
    FString Version = SDKManager->GetSDKVersion();
    UE_LOG(LogEOSShared, Log, TEXT("EOS SDK Version: %s"), *Version);
}
```

### 配置和创建 Platform Handle

```cpp
// 来源: Source/EOSShared/Public/IEOSSDKManager.h
IEOSSDKManager* SDKManager = IEOSSDKManager::Get();
if (!SDKManager) return;

// 方式 1：通过配置名称创建（从 .ini 加载配置）
IEOSPlatformHandlePtr Platform = SDKManager->CreatePlatform(TEXT("Default"));

// 方式 2：手动添加配置后创建
FEOSSDKPlatformConfig Config;
Config.Name = TEXT("MyGame");
Config.ProductId = TEXT("your-product-id");
Config.SandboxId = TEXT("your-sandbox-id");
Config.ClientId = TEXT("your-client-id");
Config.ClientSecret = TEXT("your-client-secret");
Config.DeploymentId = TEXT("your-deployment-id");
Config.EncryptionKey = TEXT("your-encryption-key");
Config.bEnableRTC = true;
Config.TickBudgetInMilliseconds = 2;

SDKManager->AddPlatformConfig(Config);
IEOSPlatformHandlePtr MyPlatform = SDKManager->CreatePlatform(TEXT("MyGame"));

// 获取所有活跃 Platform
TArray<IEOSPlatformHandlePtr> AllPlatforms = SDKManager->GetActivePlatforms();
```

### 使用回调安全包装器

```cpp
// 来源: Source/EOSShared/Public/EOSSharedTypes.h
// TEOSCallback：一次性异步回调，自动在回调完成后释放

class FMyOnlineSubsystem
{
    void Login()
    {
        EOS_Auth_LoginOptions LoginOptions = {};
        LoginOptions.ApiVersion = EOS_AUTH_LOGIN_API_LATEST;
        // ... 设置 Credentials ...

        // 创建安全回调包装器，绑定到当前对象的弱引用
        auto* Callback = new TEOSCallback<
            EOS_Auth_LoginCallback,
            EOS_Auth_LoginCallbackInfo,
            FMyOnlineSubsystem>(AsWeak());

        Callback->CallbackLambda = [this](const EOS_Auth_LoginCallbackInfo* Data)
        {
            if (Data->ResultCode == EOS_EResult::EOS_Success)
            {
                UE_LOG(LogEOSShared, Log, TEXT("Login succeeded"));
            }
        };

        EOS_Auth_Login(AuthHandle, &LoginOptions, Callback, Callback->GetCallbackPtr());
    }
};
```

### 使用 EOS_Async 辅助函数

```cpp
// 来源: Source/EOSShared/Public/EOSSharedTypes.h (UE::Online 命名空间)
// 适用于使用 Promise 模式的异步操作链

TPromise<const EOS_Auth_LoginCallbackInfo*> Promise;
TFuture<const EOS_Auth_LoginCallbackInfo*> Future = Promise.GetFuture();

EOS_Auth_LoginOptions LoginOptions = {};
// ... 配置 ...

// EOS_Async 管理回调对象的生命周期
EOS_Async(EOS_Auth_Login, AuthHandle, LoginOptions, MoveTemp(Promise));

// 绑定后续处理
Future.Next([](const EOS_Auth_LoginCallbackInfo* Data)
{
    if (Data->ResultCode == EOS_EResult::EOS_Success)
    {
        // 登录成功处理
    }
});
```

### 使用 RAII 事件注册

```cpp
// 来源: Source/EOSShared/Public/EOSSharedTypes.h
// 用于订阅 EOS 通知事件，作用域结束时自动反注册

class FLobbiesEOS
{
    // 事件注册句柄（RAII）
    FEOSEventRegistrationPtr OnLobbyUpdatedRegistration;

    void SubscribeToLobbyUpdates(EOS_HLobby LobbyHandle)
    {
        // EOS_RegisterComponentEventHandler 自动管理注册/反注册
        OnLobbyUpdatedRegistration = UE::Online::EOS_RegisterComponentEventHandler(
            this,                                // 处理对象
            LobbyHandle,                         // EOS 句柄
            EOS_LOBBY_ADDNOTIFYLOBBYUPDATERECEIVED_API_LATEST,  // API 版本
            &EOS_Lobby_AddNotifyLobbyUpdateReceived,            // 注册函数
            &EOS_Lobby_RemoveNotifyLobbyUpdateReceived,         // 反注册函数
            &FLobbiesEOS::HandleLobbyUpdated);                  // 处理函数
    }

    void HandleLobbyUpdated(const EOS_Lobby_UpdateLobbyCallbackInfo* Data)
    {
        // 处理大厅更新通知
    }

    // OnLobbyUpdatedRegistration 析构时自动调用 RemoveNotifyLobbyUpdateReceived
};
```

### 使用 FastTickLock

```cpp
// 来源: Source/EOSShared/Public/IEOSSDKManager.h
// 当需要 SDK 高频 Tick 时（如 Overlay 可见期间），获取 RAII 锁

IEOSSDKManager* SDKManager = IEOSSDKManager::Get();

// 从 Platform Handle 获取
IEOSPlatformHandlePtr Platform = SDKManager->CreatePlatform(TEXT("Default"));
TSharedRef<IEOSFastTickLock> FastLock = Platform->GetFastTickLock();

// 或直接从 Manager 获取
TSharedRef<IEOSFastTickLock> FastLock2 = SDKManager->GetFastTickLock();

// 锁在作用域内有效，SDK 以最高频率 Tick
// 离开作用域后恢复配置的 Tick 频率
```

### EOS 类型序列化

```cpp
// 来源: Source/EOSShared/Public/EOSShared.h

// EOS Result 转字符串
FString ResultStr = LexToString(EOS_EResult::EOS_Success);

// ProductUserId 转换
EOS_ProductUserId UserId = ...;
FString UserIdStr = LexToString(UserId);

// 字符串转 ProductUserId
EOS_ProductUserId ParsedId;
LexFromString(ParsedId, TEXT("some-user-id-string"));

// 便捷函数
EOS_ProductUserId QuickId = EOSProductUserIdFromString(TEXT("some-user-id-string"));

// EpicAccountId 转换
EOS_EpicAccountId AccountId = ...;
FString AccountStr = LexToString(AccountId);

// 枚举类型转换
FString StatusStr = LexToString(EOS_EApplicationStatus::EOS_AS_Foreground);
FString NetworkStr = LexToString(EOS_ENetworkStatus::EOS_NS_Online);
```

## Demo 示例

以下是一个最小的 EOS SDK 管理示例，展示初始化、创建 Platform 和安全回调：

**MyEOSManager.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "IEOSSDKManager.h"
#include "EOSSharedTypes.h"

class FMyEOSManager
{
public:
    bool Init(const FString& ProductId, const FString& SandboxId,
              const FString& ClientId, const FString& ClientSecret,
              const FString& DeploymentId, const FString& EncryptionKey);
    void Shutdown();
    void LogStatus() const;

private:
    IEOSPlatformHandlePtr PlatformHandle;
    FEOSEventRegistrationPtr NetworkStatusRegistration;
};
```

**MyEOSManager.cpp**

```cpp
#include "MyEOSManager.h"
#include "EOSShared.h"
#include "IEOSSDKManager.h"

bool FMyEOSManager::Init(const FString& ProductId, const FString& SandboxId,
                         const FString& ClientId, const FString& ClientSecret,
                         const FString& DeploymentId, const FString& EncryptionKey)
{
    IEOSSDKManager* SDKManager = IEOSSDKManager::Get();
    if (!SDKManager || !SDKManager->IsInitialized())
    {
        UE_LOG(LogEOSShared, Error, TEXT("EOS SDK Manager not available"));
        return false;
    }

    // 配置 Platform 参数
    FEOSSDKPlatformConfig Config;
    Config.Name = TEXT("MyGamePlatform");
    Config.ProductId = ProductId;
    Config.SandboxId = SandboxId;
    Config.ClientId = ClientId;
    Config.ClientSecret = ClientSecret;
    Config.DeploymentId = DeploymentId;
    Config.EncryptionKey = EncryptionKey;
    Config.bEnableRTC = true;
    Config.TickBudgetInMilliseconds = 2;

    SDKManager->AddPlatformConfig(Config);

    // 创建 Platform Handle
    PlatformHandle = SDKManager->CreatePlatform(TEXT("MyGamePlatform"));
    if (!PlatformHandle.IsValid())
    {
        UE_LOG(LogEOSShared, Error, TEXT("Failed to create EOS Platform"));
        return false;
    }

    UE_LOG(LogEOSShared, Log, TEXT("EOS Platform created, SDK Version: %s"),
           *SDKManager->GetSDKVersion());

    return true;
}

void FMyEOSManager::Shutdown()
{
    // RAII: NetworkStatusRegistration 自动反注册
    NetworkStatusRegistration.Reset();

    // 释放 Platform Handle
    PlatformHandle.Reset();
}

void FMyEOSManager::LogStatus() const
{
    IEOSSDKManager* SDKManager = IEOSSDKManager::Get();
    if (SDKManager)
    {
        SDKManager->LogInfo(0);
    }
}
```

## 模块依赖

Build.cs 中声明的依赖：`ApplicationCore`, `Slate`。

这两个都属于常见引擎模块，因此：

无特殊依赖（仅标准 Core/Engine/Slate 等及 ApplicationCore）。

> **注意**：此插件运行时依赖 EOSSDK 动态库（由 `EOSSDK_RUNTIME_LOAD_REQUIRED` 控制加载）。Windows 平台还支持可选的 Steam 集成（`UE_WITH_EOS_STEAM_INTEGRATION`），需要 `SteamShared` 插件。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-28 | `3f55a262` | Hotfix PreWarm - RAII high priority ticking lock from startup to first login | 修复启动到首次登录期间的高频 Tick 锁 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到 UE_LOGF |
| 2026-02-20 | `dbbc3925` | EOSSDK 1.19.0.3 CL 49960398 Headers Update | 升级 EOSSDK 头文件到 1.19.0.3 |
| 2026-02-19 | `3e97632c` | Refactored FSceneViewport / FViewport to remove the ViewportRHI field | 适配引擎 Viewport 重构移除 RHI 字段 |
| 2026-02-09 | `52a2dc16` | - Support EOS_P2P not being present in per-project SDK | 支持项目级 SDK 中缺少 EOS_P2P 模块的情况 |

### 维护评价

**活跃维护**。该插件在 2026 年持续收到实质性更新，包括 SDK 版本升级（1.19.0.3）、引擎 API 适配和功能修复。作为 EOS 在线功能的基础设施层，它随着 EOS SDK 的更新和引擎 API 的变化同步维护。

- 创建于 2021 年，约 5 年历史，属于 EOS 体系的核心基础设施
- 最近一次更新距今不到 1 个月，维护频率稳定
- 注意：默认未启用（`EnabledByDefault: false`），需要手动在插件配置中启用
- 推荐使用：如果你的游戏使用 Epic Online Services，此插件是必需的底层依赖

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/EOSShared)
- [EOSSDK 官方文档](https://dev.epicgames.com/docs/epic-online-services)