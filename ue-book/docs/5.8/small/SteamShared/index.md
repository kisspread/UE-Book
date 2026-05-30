# Steam Shared Module

> Shared module loader for the Steam API（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | Steam共享模块 |
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SteamShared` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-07-16 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Steam/SteamShared) | |

## 用途

SteamShared插件是Steamworks SDK集成到虚幻引擎中的**底层基础模块**。它并非面向最终用户的功能插件，而是为上层SteamOnlineSubsystem等模块提供共享的、集中管理的Steam API加载与实例化服务。

其核心价值在于：
1.  **统一加载与卸载**：负责安全地加载和卸载Steamworks SDK的客户端 (`steamclient64.dll`) 和专用服务器 (`steam_api64.dll`) 动态链接库。
2.  **实例生命周期管理**：通过`FSteamClientInstanceHandler`和`FSteamServerInstanceHandler`以引用计数的方式管理Steam客户端和服务器API的实例。当最后一个使用者释放句柄时，才会执行API清理和DLL卸载，避免重复初始化/反初始化问题。
3.  **网络地址支持**：提供`FInternetAddrSteam`类，将Steam的网络标识（如CSteamID或IP地址）封装为UE标准的`FInternetAddr`接口，供上层SteamSockets等网络模块使用。
4.  **平台抽象**：隐藏了不同平台（Windows, Mac, Linux, Android）加载Steam DLL的差异，并处理特定平台限制（如Win64:arm64不支持）。

简而言之，它是UE中所有Steam功能的“基石”，确保了Steam API在引擎生命周期内安全、可靠地运行。

## 使用场景

-   **你的项目需要集成Steam功能（成就、大厅、用户身份等）**：本插件会被SteamOnlineSubsystem自动依赖，无需直接使用，但了解其机制有助于调试启动失败等问题。
-   **你正在开发一个多人游戏，并需要同时管理客户端和服务器模式的Steam API**：可以使用本模块的`ObtainSteamClientInstanceHandle`和`ObtainSteamServerInstanceHandle`来安全地获取实例句柄。
-   **你需要处理Steam网络连接或P2P通信**：`FInternetAddrSteam`是SteamSockets网络子系统使用的地址格式，本模块提供了其定义。

## 蓝图用法

本插件主要提供底层的C++服务，**没有暴露任何蓝图可调用的函数（BlueprintCallable）或蓝图可读写属性（BlueprintReadWrite）**。

与Steam的蓝图交互通常通过更高级的插件（如OnlineSubsystemSteam）或蓝图函数库进行，它们会在底层调用本模块提供的服务。

## C++ 用法

### 头文件引入

```cpp
#include "SteamSharedModule.h"
```

### 基本用法

获取Steam客户端实例的引用计数句柄。当句柄有效时，Steam客户端API已初始化，可以在其生命周期内安全调用相关函数。

```cpp
// 来源： FSteamSharedModule::ObtainSteamClientInstanceHandle 的典型使用模式
if (FSteamSharedModule::IsAvailable())
{
    // 获取客户端实例句柄（智能指针）
    TSharedPtr<FSteamClientInstanceHandler> ClientHandle = FSteamSharedModule::Get().ObtainSteamClientInstanceHandle();

    if (ClientHandle.IsValid())
    {
        // Steam客户端API已就绪，可以进行Steam相关操作
        // 例如: 获取当前用户信息，访问 SteamFriends() 等接口
    }
}
// 当 ClientHandle 离开作用域或被重置后，如果这是最后一个持有者，Steam客户端API将被自动清理。
```

### 进阶用法

同时获取客户端和服务器实例句柄。这在游戏同时作为客户端和大厅主机（Listen Server）时可能有用。

```cpp
// 来源： 组合使用 ObtainSteamClientInstanceHandle 和 ObtainSteamServerInstanceHandle
TSharedPtr<FSteamClientInstanceHandler> ClientHandle = FSteamSharedModule::Get().ObtainSteamClientInstanceHandle();
TSharedPtr<FSteamServerInstanceHandler> ServerHandle = FSteamSharedModule::Get().ObtainSteamServerInstanceHandle();

if (ClientHandle.IsValid() && ServerHandle.IsValid())
{
    // 客户端和服务器Steam API均已初始化
    // 客户端可用于玩家社交功能，服务器可用于大厅列表、用户认证等

    // 获取服务器查询端口（如果需要）
    int32 QueryPort = ServerHandle->GetQueryPort();
}
// 句柄管理同上，各自独立管理引用计数。
```

## Demo 示例

一个最小的示例，展示如何检查SteamShared模块并尝试获取一个客户端实例。

```cpp
// MySteamCheck.h
#pragma once

#include "CoreMinimal.h"

class FMySteamCheck
{
public:
    static void CheckSteamAvailability();
};
```

```cpp
// MySteamCheck.cpp
#include "MySteamCheck.h"
#include "SteamSharedModule.h"
#include "Misc/MessageDialog.h"

void FMySteamCheck::CheckSteamAvailability()
{
    // 检查模块是否加载
    if (!FSteamSharedModule::IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("SteamShared模块未加载。"));
        return;
    }

    // 尝试获取客户端句柄
    TSharedPtr<FSteamClientInstanceHandler> ClientHandle = FSteamSharedModule::Get().ObtainSteamClientInstanceHandle();

    if (ClientHandle.IsValid())
    {
        UE_LOG(LogTemp, Log, TEXT("Steam客户端API初始化成功！"));
        // ... 执行需要Steam客户端API的代码 ...
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("无法初始化Steam客户端API。请确保Steam客户端正在运行并且游戏已通过Steam启动。"));
        // 可以弹窗提示用户
        FMessageDialog::Open(EAppMsgType::Ok, FText::FromString(TEXT("无法连接到Steam客户端。请确保Steam已启动。")));
    }
    // ClientHandle 在此销毁，如果成功获取过，则对应的Steam API会被清理。
}
```

## 模块依赖

从`SteamShared.Build.cs`分析，该模块的依赖项均为引擎核心或网络相关基础模块，无特殊依赖。

| 模块 | 用途 |
|---|---|
| `OnlineSubsystemUtils` | 提供网络子系统相关的工具类 |
| `Networking` | 基础网络模块，为`FInternetAddr`等提供支持 |

（注：Core, CoreUObject, Engine等核心模块依赖已省略）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-22 | `f6116b00` | Updating Steamworks to 1.64 + binaries, now with arm64 android support. | 升级Steamworks SDK至1.64，并增加对Android arm64平台的支持。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从UE_LOG迁移至UE_LOGF，以支持格式化字符串。 |
| 2026-02-04 | `e596cc7a` | Disable Steam on Android | 暂时禁用Android平台的Steam功能。 |
| 2026-01-23 | `c73d4bf4` | PR #14263: Updating Steamworks to v1.63, which adds support for Android | 通过PR #14263升级Steamworks至v1.63，此版本新增Android平台支持。 |
| 2025-11-12 | `2a4530a3` | Fixed steam_appid.txt not being generated for dedicated servers and improved error logging for steam | 修复了专用服务器不生成steam_appid.txt文件的问题，并改进了Steam相关的错误日志。 |

### 维护评价

-   **创建时间**：约7年前（2019年）。
-   **维护活跃度**：**活跃维护中**。尽管作为底层模块更新频率不高，但在最近6个月内有实质性更新，包括升级底层Steamworks SDK版本、修复平台兼容性问题（Android）和改进构建系统（arm64支持）。这表明该插件随着引擎版本和Steam SDK的更新而持续维护。
-   **状态**：该插件是许多Steam相关功能的基石，虽然`EnabledByDefault`为`false`，但它会被其他插件（如`OnlineSubsystemSteam`）隐式依赖。没有迹象表明它会被废弃。
-   **推荐**：**推荐使用**。所有需要集成Steam功能的UE项目都应包含此插件。直接使用它的场景较少，主要是作为依赖项存在。开发者应关注其更新，以确保与最新Steamworks SDK的兼容性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Steam/SteamShared)