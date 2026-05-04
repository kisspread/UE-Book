# EOS Shared

> Responsible for init/shutdown of the EOSSDK runtime library.

| 属性 | 值 |
|---|---|
| 分类 | Online Platform |
| 默认启用 | ❌ No |
| 包含内容 | No |
| 模块 | EOSShared (Runtime, PostConfigInit) |
| 支持平台 | Android, IOS, Linux, LinuxArm64, Mac, Win64 |
| 创建时间 | 2021-04-29 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/EOSShared) | |

## 用途

EOSShared 是 UE5 中所有 EOS（Epic Online Services）相关插件的**基础设施层**。它负责：

1. **SDK 生命周期管理** — 在模块启动时自动加载并初始化 EOS SDK 运行时库（`EOS_Initialize`），在模块关闭时执行 `EOS_Shutdown`。
2. **Platform Handle 管理** — 创建、缓存和 tick EOS Platform Handle，支持多个命名配置（Named Platform Configs）。
3. **跨平台 SDK 加载** — 在需要运行时加载的平台上（如 Windows），自动搜索并加载 EOSSDK 动态库。
4. **内存管理** — 将 EOS SDK 的内存分配器重定向到 UE 的 `FMemory`，以便 LLM 追踪。
5. **日志桥接** — 将 EOS SDK 的日志输出转发到 UE 日志系统（`LogEOSSDK`）。
6. **Overlay 集成** — 管理 EOS Overlay 的渲染回调和输入转发。
7. **工具函数** — 提供 EOS 枚举/ID 类型与 `FString` 之间的转换（`LexToString`/`LexFromString`），以及 EOS 异步回调的安全封装模板。

简单来说，**EOSShared 是 EOS Online Subsystem 的"引擎"**——没有它，其他 EOS 插件（如 EOSPlus、OnlineSubsystemEOS）都无法工作。

## 使用场景

- 你的项目使用 Epic Online Services（好友、成就、排行榜、P2P、RTC 等）→ 必须启用 EOSShared
- 你需要在 EOS SDK 初始化前/后注入自定义逻辑 → 通过 `OnPreInitializeSDK` / `OnPostInitializeSDK` 委托
- 你需要创建多个 EOS Platform 实例（例如一个用于玩家登录，一个用于服务器）→ 使用 Named Platform Configs
- 你使用了 Steam 并希望 EOS SDK 与 Steam 原生集成 → EOSShared 在 Win64/Mac/Linux 上自动启用 Steam 集成路径

## 蓝图用法

EOSShared 没有暴露任何 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性。它是一个纯 C++ 基础设施模块，蓝图层面的 EOS 功能由上层插件（如 `OnlineSubsystemEOS`）提供。

## C++ 用法

### 头文件引入

```cpp
// SDK Manager 接口和 Platform Handle
#include "IEOSSDKManager.h"

// EOS 类型转换工具函数
#include "EOSShared.h"

// 异步回调封装、事件注册模板
#include "EOSSharedTypes.h"
```

### 获取 SDK Manager

`IEOSSDKManager` 通过 `IModularFeatures` 注册，可在任何时候获取：

```cpp
// 获取 SDK Manager 实例（可能为 nullptr）
IEOSSDKManager* SDKManager = IEOSSDKManager::Get();
if (SDKManager && SDKManager->IsInitialized())
{
    // SDK 已就绪
}
```

### 创建 Platform Handle

```cpp
// 方式 1：通过命名配置（从 Engine.ini 加载）
IEOSPlatformHandlePtr PlatformHandle = SDKManager->CreatePlatform(TEXT("MyPlatformConfig"));

// 方式 2：直接传入 EOS_Platform_Options
EOS_Platform_Options Options = {};
Options.ApiVersion = EOS_PLATFORM_OPTIONS_API_LATEST;
// ... 填充 Options ...
IEOSPlatformHandlePtr PlatformHandle = SDKManager->CreatePlatform(Options);

// Platform Handle 可隐式转换为 EOS_HPlatform
EOS_HPlatform RawHandle = *PlatformHandle;
```

### 监听 SDK 初始化事件

```cpp
// 在 SDK 初始化前修改选项
SDKManager->OnPreInitializeSDK.AddLambda([](EOS_InitializeOptions& Options)
{
    // 可修改 Options 中的字段
    Options.OverrideThreadAffinity = &MyThreadAffinity;
});

// 在 SDK 初始化后执行自定义逻辑
SDKManager->OnPostInitializeSDK.AddLambda([](EOS_EResult Result)
{
    if (Result == EOS_EResult::EOS_Success)
    {
        UE_LOG(LogTemp, Log, TEXT("EOS SDK initialized successfully"));
    }
});
```

### 安全使用 EOS 异步回调

`EOSSharedTypes.h` 提供了 `EOS_Async` 模板函数，自动管理回调对象的生命周期：

```cpp
// 方式 1：使用 TPromise（推荐用于 UE::Online 框架）
TPromise<const EOS_Auth_LoginCallbackInfo*> Promise;
EOS_Async(EOS_Auth_Login, AuthHandle, LoginOptions, MoveTemp(Promise));
// Promise 的 Future 会在回调触发时自动 fulfill

// 方式 2：使用 Lambda
EOS_Async(EOS_Connect_Login, ConnectHandle, ConnectOptions,
    [this](const EOS_Connect_LoginCallbackInfo* Data)
    {
        if (Data->ResultCode == EOS_EResult::EOS_Success)
        {
            // 登录成功
        }
    });
```

### 使用 RAII 事件注册

`EOS_RegisterComponentEventHandler` 将 EOS 通知注册绑定到 RAII 对象，离开作用域时自动取消注册：

```cpp
// 声明为成员变量
FEOSEventRegistrationPtr LobbyUpdatedRegistration;

// 注册（通常在初始化时调用）
LobbyUpdatedRegistration = EOS_RegisterComponentEventHandler(
    this,
    LobbyHandle,
    EOS_LOBBY_ADDNOTIFYLOBBYUPDATERECEIVED_API_LATEST,
    &EOS_Lobby_AddNotifyLobbyUpdateReceived,
    &EOS_Lobby_RemoveNotifyLobbyUpdateReceived,
    &FLobbiesEOS::HandleLobbyUpdated);

// 当对象销毁或 Registration 被 reset 时，自动调用 RemoveNotify
```

### 类型转换工具

```cpp
// EOS_Result → FString
FString ErrorStr = LexToString(EOS_EResult::EOS_InvalidCredentials);

// ProductUserId ↔ FString
FString PuidStr = LexToString(ProductUserId);
EOS_ProductUserId Puid;
LexFromString(Puid, *PuidStr);

// EpicAccountId ↔ FString
FString AccountStr = LexToString(EpicAccountId);

// 各种枚举 → TCHAR* 字符串
const TCHAR* StatusStr = LexToString(EOS_ELoginStatus::EOS_LS_LoggedIn);
```

### INI 配置

Platform Config 从 `Engine.ini` 的 `[EOSSDK.Platform.<ConfigName>]` 节读取：

```ini
[EOSSDK]
DefaultPlatformConfigName=Default
bEnableApiVersionWarnings=true
ModulesToLoad=OnlineSubsystemEOS

[EOSSDK.Platform.Default]
ProductId=your_product_id
SandboxId=your_sandbox_id
ClientId=your_client_id
ClientSecret=your_client_secret
DeploymentId=your_deployment_id
ClientEncryptionKey=your_encryption_key
bIsServer=false
bDisableOverlay=false
bEnableRTC=true
TickBudgetInMilliseconds=1
```

## Demo 示例

### 最小 EOS 初始化示例

```cpp
// MyGame.Build.cs
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "EOSShared"
});
```

```cpp
// MyGameSubsystem.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "IEOSSDKManager.h"
#include "MyGameSubsystem.generated.h"

UCLASS()
class UMyGameSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override
    {
        // 获取 SDK Manager
        IEOSSDKManager* SDKManager = IEOSSDKManager::Get();
        if (!SDKManager || !SDKManager->IsInitialized())
        {
            UE_LOG(LogTemp, Warning, TEXT("EOS SDK not available"));
            return;
        }

        // 创建默认 Platform Handle
        const FString& ConfigName = SDKManager->GetDefaultPlatformConfigName();
        if (!ConfigName.IsEmpty())
        {
            PlatformHandle = SDKManager->CreatePlatform(ConfigName);
            if (PlatformHandle.IsValid())
            {
                UE_LOG(LogTemp, Log, TEXT("EOS Platform created: %s"), *ConfigName);
            }
        }
    }

    virtual void Deinitialize() override
    {
        // Platform Handle 通过 SharedPtr 自动管理
        PlatformHandle.Reset();
    }

private:
    IEOSPlatformHandlePtr PlatformHandle;
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心模块 |
| `EOSSDK` | Epic Online Services SDK 二进制库 |
| `ApplicationCore` | （仅 iOS）应用生命周期管理 |
| `Slate` | （仅当编译引擎时）Overlay 渲染集成 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-09-23 | `c851b86` | EOSSDK CL45343210 Release v1.18.0.4 Full update | 更新 EOS SDK 到 v1.18.0.4 版本 |
| 2025-09-23 | `14fcdb4` | [Backout] - CL45934846 回退上述更新 | 回退操作，可能是集成问题 |
| 2025-09-23 | `4c26457` | EOSSDK CL45343210 Release v1.18.0.4 Full update | 重新应用 SDK 更新 |

### 维护评价

- **活跃维护** ✅ — 最近一次更新在 2025 年 9 月，距今不到 1 年
- **创建时间** — 2021 年 4 月，约 5 年历史
- **更新模式** — 主要跟随 EOS SDK 版本升级，是 Epic 官方维护的核心基础设施
- **稳定性** — 作为 Online Subsystem 底层，接口稳定，极少有破坏性变更
- **推荐使用** ✅ — 如果你的项目使用 EOS，这是必须启用的插件。即使不直接编写代码，它也会被其他 EOS 插件自动依赖

⚠️ 注意：此插件 `EnabledByDefault = false`，需要在项目设置中手动启用，或通过其他 EOS 插件的依赖关系自动启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/EOSShared)
- [EOS SDK 官方文档](https://dev.epicgames.com/docs/epic-online-services)
- [OnlineSubsystemEOS 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineSubsystemEOS)（EOSShared 的主要消费者）
