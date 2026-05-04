# Steam Shared Module

> Shared module loader for the Steam API

| 属性 | 值 |
|---|---|
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | 否 |
| 模块 | SteamShared (Runtime) |
| 创建时间 | 2019-07-16 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Steam/SteamShared) | |

## 用途

SteamShared 是 UE5 中所有 Steam 相关功能的**底层基础设施模块**。它负责动态加载 Steamworks SDK 的 DLL（`steam_api64.dll` / `libsteam_api.so` / `libsteam_api.dylib`），并提供引用计数式的 Steam API 生命周期管理。

核心价值在于：多个上层模块（OnlineSubsystemSteam、SteamSockets、SteamController 等）都需要访问 Steam API，但 Steam API 的初始化/关闭必须全局协调。SteamShared 通过 `TSharedPtr` 引用计数机制，确保只要还有任何持有者在使用 Steam API，DLL 就不会被卸载；当最后一个持有者释放句柄时，自动调用 `SteamAPI_Shutdown()` 或 `SteamGameServer_Shutdown()`。

**你通常不会直接使用这个 plugin**——它是被其他 Steam 插件间接依赖的。但理解它的工作原理有助于排查 Steam 初始化相关的问题。

## 使用场景

- 你使用了 **OnlineSubsystemSteam** 进行 Steam 网络联机 → 该 plugin 自动依赖 SteamShared
- 你使用了 **SteamSockets** 进行 Steam P2P 网络通信 → 自动依赖 SteamShared
- 你在 **Dedicated Server** 上运行 Steam Game Server API → SteamShared 管理 `SteamGameServer_Init`
- 你需要调试 Steam DLL 加载失败的问题 → 通过 `FSteamSharedModule::Get()` 检查 DLL 状态

## 蓝图用法

SteamShared 没有暴露任何 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性。这是一个纯 C++ 基础设施模块，不提供蓝图接口。

## C++ 用法

### 头文件引入

```cpp
#include "SteamSharedModule.h"
```

### 基本用法 — 获取 Steam Client 实例

```cpp
// 检查模块是否可用
if (FSteamSharedModule::IsAvailable())
{
    // 获取模块单例
    FSteamSharedModule& SteamModule = FSteamSharedModule::Get();

    // 检查 Steam DLL 是否已加载
    if (SteamModule.AreSteamDllsLoaded())
    {
        // 获取 Steam Client 实例句柄（引用计数式）
        TSharedPtr<FSteamClientInstanceHandler> ClientHandle = SteamModule.ObtainSteamClientInstanceHandle();

        if (ClientHandle.IsValid() && ClientHandle->IsInitialized())
        {
            // Steam API 已初始化，可以安全调用 Steamworks 函数
            // 例如：SteamFriends()->GetPersonaName()
        }
    }
}
```

### 获取 Steam Server 实例（Dedicated Server）

```cpp
// 仅在 Dedicated Server 环境下使用
FSteamSharedModule& SteamModule = FSteamSharedModule::Get();
TSharedPtr<FSteamServerInstanceHandler> ServerHandle = SteamModule.ObtainSteamServerInstanceHandle();

if (ServerHandle.IsValid() && ServerHandle->IsInitialized())
{
    // Steam Game Server API 已初始化
    int32 QueryPort = ServerHandle->GetQueryPort();
    int32 GamePort = ServerHandle->GetGamePort();

    // 可以调用 SteamGameServer() 相关函数
}
```

### 检查 DLL 加载路径（调试用）

```cpp
FSteamSharedModule& SteamModule = FSteamSharedModule::Get();
FString DllPath = SteamModule.GetSteamModulePath();
UE_LOG(LogTemp, Log, TEXT("Steam DLL path: %s"), *DllPath);

bool bLoaded = SteamModule.AreSteamDllsLoaded();
UE_LOG(LogTemp, Log, TEXT("Steam DLLs loaded: %s"), bLoaded ? TEXT("Yes") : TEXT("No"));
```

### 实例句柄的生命周期

```cpp
// 句柄使用 TSharedPtr 引用计数管理
// 只要至少有一个 shared ptr 存活，Steam API 就不会被关闭
{
    TSharedPtr<FSteamClientInstanceHandler> Handle1 = SteamModule.ObtainSteamClientInstanceHandle();
    TSharedPtr<FSteamClientInstanceHandler> Handle2 = SteamModule.ObtainSteamClientInstanceHandle();
    // Handle1 和 Handle2 指向同一个实例，引用计数 = 2

    // 此处可以安全使用 Steam API
}
// Handle1 和 Handle2 离开作用域，引用计数归零
// → 自动调用 SteamAPI_Shutdown()
```

## Demo 示例

### 最小 Steam 初始化示例

```cpp
// MySteamManager.h
#pragma once
#include "CoreMinimal.h"

class FMySteamManager
{
public:
    bool Initialize();
    void Shutdown();
    bool IsSteamAvailable() const;

private:
    TSharedPtr<class FSteamClientInstanceHandler> SteamClientHandle;
};

// MySteamManager.cpp
#include "MySteamManager.h"
#include "SteamSharedModule.h"

bool FMySteamManager::Initialize()
{
    if (!FSteamSharedModule::IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("SteamShared module not available"));
        return false;
    }

    FSteamSharedModule& SteamModule = FSteamSharedModule::Get();

    if (!SteamModule.AreSteamDllsLoaded())
    {
        UE_LOG(LogTemp, Warning, TEXT("Steam DLLs not loaded. Check Steamworks SDK installation."));
        return false;
    }

    SteamClientHandle = SteamModule.ObtainSteamClientInstanceHandle();
    if (!SteamClientHandle.IsValid() || !SteamClientHandle->IsInitialized())
    {
        UE_LOG(LogTemp, Warning, TEXT("Failed to initialize Steam Client API"));
        return false;
    }

    UE_LOG(LogTemp, Log, TEXT("Steam initialized successfully"));
    return true;
}

void FMySteamManager::Shutdown()
{
    // 释放句柄，当引用计数归零时会自动调用 SteamAPI_Shutdown()
    SteamClientHandle.Reset();
}

bool FMySteamManager::IsSteamAvailable() const
{
    return SteamClientHandle.IsValid() && SteamClientHandle->IsInitialized();
}
```

**Build.cs 依赖**：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "SteamShared"
});
```

**前提条件**：需要安装 Steamworks SDK 到 `Engine/Source/ThirdParty/Steamworks/` 目录。

## 模块依赖

SteamShared 本身的依赖（你不需要关心，仅作参考）：

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `Sockets` | 网络 Socket 子系统（用于解析服务器多宿主地址） |
| `Steamworks` | Steam 官方 SDK（第三方库，Engine 内置） |

依赖 SteamShared 的上层模块（这些才是真正面向开发者的）：

| 模块 | 用途 |
|---|---|
| `OnlineSubsystemSteam` | Steam 在线子系统（成就、排行榜、好友等） |
| `SteamSockets` | 基于 Steam 的 Socket 网络传输层 |
| `SocketSubsystemSteamIP` | Steam IP Socket 子系统 |
| `SteamController` | Steam Controller 输入支持 |
| `EOSShared` | Epic Online Services 共享模块（兼容层） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-06-11 | `afdf8d75` | Replace some usages of FORCEINLINE with inline in Online modules | 代码规范化，将 `FORCEINLINE` 替换为 `inline`，无功能变化 |
| 2025-06-03 | `0a44e4b8` | Plugin modules can be included & excluded on a per-architecture basis | 新增 `PlatformArchitectureDenyList` 支持，排除 Win64:arm64 |
| 2025-04-23 | `6ae57335` | Used UnrealGame build target to find and convert all files to have dllstorage | DLL 导出符号规范化，无功能变化 |

### 维护评价

- **创建时间**：2019-07-16，已存在约 7 年
- **更新频率**：近期更新均为工程化改进（编译规范化、架构支持），无功能性变更
- **维护状态**：**维护中** — 作为 Steam 生态的底层依赖，随引擎一起维护
- **稳定性**：非常稳定，核心逻辑多年来基本未变
- **已知限制**：
  - `EnabledByDefault = false`，需要手动启用或被其他 plugin 隐式依赖
  - 不支持动态重载（`SupportsDynamicReloading() = false`）
  - 不支持 Win64:arm64 架构
  - 要求 Steamworks SDK 已安装到 `Engine/Source/ThirdParty/Steamworks/`
- **推荐**：如果你使用任何 Steam 相关功能，这个 plugin 会被自动依赖，无需手动启用。**不要**手动禁用它，否则 OnlineSubsystemSteam 等插件将无法工作。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Steam/SteamShared)
- [OnlineSubsystemSteam 文档](../OnlineSubsystemSteam/)（主要消费者）
- [Steamworks SDK 官方文档](https://partner.steamgames.com/doc/sdk)
