# Web Authentication Plugin

> Access to Web Authenticated Sessions.

| 属性 | 值 |
|---|---|
| 中文名 | 网页认证插件 |
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `WebAuth` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-12-19 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/WebAuth) | |

## 用途

此插件提供了跨平台（Windows， iOS， Android）启动系统浏览器进行网页认证（如 OAuth）的能力，并管理认证后的会话凭证。它解决了在游戏内直接处理复杂网页认证流程（如登录、授权）的难题，允许游戏安全地将玩家重定向到系统浏览器完成认证，然后接收重定向回调（URL）以获取认证令牌。这避免了在游戏内嵌入 WebView 带来的安全性和维护性问题。

## 使用场景

- 你的游戏需要集成第三方服务（如 Epic Games Services、Discord、Google 等）的登录，且该服务使用标准的网页 OAuth 流程。
- 你需要为 iOS 或 Android 平台的玩家提供统一的、使用系统浏览器的登录体验。
- 你需要安全地保存、加载和删除与认证服务关联的凭证（ID 和 Token）。

## 蓝图用法

通过分析插件源码（`WebAuth.h`， `WebAuthModule.h`），该插件主要提供 C++ 接口 (`IWebAuth`)，没有发现 `UFUNCTION(BlueprintCallable)` 标记的函数。因此，**该插件不直接提供蓝图节点**。所有功能需要通过 C++ 调用。

## C++ 用法

### 头文件引入

```cpp
#include "WebAuthModule.h"
```

### 基本用法

**发起一个网页认证会话**（来源：`Source/Public/WebAuth.h`）。

```cpp
// 1. 获取 WebAuth 模块实例
FWebAuthModule& WebAuthModule = FWebAuthModule::Get();

// 2. 检查当前平台是否支持 WebAuth
if (WebAuthModule.IsAvailable())
{
    // 3. 获取 WebAuth 接口
    IWebAuth& WebAuth = WebAuthModule.GetWebAuth();

    // 4. 定义认证完成后的回调
    FWebAuthSessionCompleteDelegate AuthDelegate;
    AuthDelegate.BindLambda([](const FString& RedirectURL, bool bHasResponse)
    {
        if (bHasResponse)
        {
            // 认证成功，从 RedirectURL 中解析授权码或令牌
            UE_LOG(LogTemp, Log, TEXT("WebAuth 成功， 重定向URL: %s"), *RedirectURL);
        }
        else
        {
            // 认证失败或被取消
            UE_LOG(LogTemp, Warning, TEXT("WebAuth 失败或被取消"));
        }
    });

    // 5. 发起认证
    // UrlStr: 授权端点的 URL
    // SchemeStr: 自定义 URL 方案（用于接收回调），例如 “mygame://”
    WebAuth.AuthSessionWithURL(
        TEXT("https://provider.com/oauth2/authorize?..."),
        TEXT("mygame://callback"),
        AuthDelegate
    );
}
```

### 进阶用法

**管理认证凭证**（保存、加载、删除）（来源：`Source/Public/WebAuth.h`）。

```cpp
IWebAuth& WebAuth = FWebAuthModule::Get().GetWebAuth();

// 保存凭证（在认证成功后调用）
WebAuth.SaveCredentials(
    TEXT("user_unique_id"),       // 用户ID
    TEXT("access_token_xxxx"),    // 访问令牌
    TEXT("EpicGames")             // 环境/服务名称，用于标识凭证
);

// 加载凭证（在应用启动时尝试自动登录）
FString OutId, OutToken;
if (WebAuth.LoadCredentials(OutId, OutToken, TEXT("EpicGames")))
{
    UE_LOG(LogTemp, Log, TEXT("自动登录成功， ID: %s"), *OutId);
    // 使用 OutId 和 OutToken 进行后续 API 调用
}

// 删除凭证（用户登出时调用）
WebAuth.DeleteLoginCookies(
    TEXT("token_prefix"),   // Cookie 名称前缀
    TEXT("mygame"),         // 自定义方案
    TEXT("provider.com"),   // 域名
    TEXT("/")              // 路径
);
```

## Demo 示例

一个最小的 C++ 示例，演示如何发起一个网页认证请求。

```cpp
// MyGameWebAuth.h
#pragma once
#include "CoreMinimal.h"
#include "WebAuthModule.h"

class FMyGameWebAuth
{
public:
    static void StartLogin(const FString& LoginURL, const FString& CallbackScheme);
};
```

```cpp
// MyGameWebAuth.cpp
#include "MyGameWebAuth.h"
#include "WebAuthModule.h"

void FMyGameWebAuth::StartLogin(const FString& LoginURL, const FString& CallbackScheme)
{
    FWebAuthModule& AuthModule = FWebAuthModule::Get();
    if (!AuthModule.IsAvailable())
    {
        UE_LOG(LogTemp, Error, TEXT("WebAuth 不可用"));
        return;
    }

    IWebAuth& WebAuth = AuthModule.GetWebAuth();

    FWebAuthSessionCompleteDelegate Delegate;
    Delegate.BindLambda([](const FString& URL, bool bSuccess)
    {
        if (bSuccess)
        {
            // 处理成功登录，从 URL 中提取 token
            UE_LOG(LogTemp, Log, TEXT("登录成功， 回调URL: %s"), *URL);
            // 解析 URL 获取 token (需要根据具体 OAuth 流程实现)
        }
        else
        {
            UE_LOG(LogTemp, Warning, TEXT("登录失败"));
        }
    });

    // 发起认证， 将会打开系统浏览器
    WebAuth.AuthSessionWithURL(LoginURL, CallbackScheme, Delegate);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ApplicationCore` | 提供跨平台应用程序核心功能，可能用于系统级 URL 打开或凭证安全存储 |
| `Launch` | 包含平台启动相关的代码，用于初始化和执行 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `55d096e6` | Fix missing characterr in WebAuth_UPL.xml | 修复 Android 构建配置文件中的拼写错误。 |
| 2026-05-21 | `504de753` | Deal with startup issue on Android causing possible wrong Webview state preventing either render or | 修复 Android 上可能因启动问题导致 WebView 状态错误，进而影响渲染的 bug。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移到 `UE_LOGF`。 |
| 2026-03-12 | `737f182a` | Auto return new intent data in WebAuth if app restarted during login session | 在 Android 上，若应用在登录会话中被重启，WebAuth 会自动返回新的 Intent 数据。 |
| 2026-01-27 | `a18eb61a` | [IOS] Setting the requires platform sdk flag in multiple modules that depends on them. | 为 iOS 平台设置所需 SDK 标志。 |

### 维护评价

该插件自 2019 年创建，已有约 7 年历史。根据近期 Git 记录，插件仍在**活跃维护中**，最近几个月有多次提交，主要针对 **iOS 和 Android 平台的稳定性修复和功能增强**，例如修复启动状态、处理应用重启等场景。尽管其核心接口 `IWebAuth` 变化不大，但各平台的底层实现持续得到优化。考虑到它是处理跨平台网页认证的基础设施，且近期更新频繁，目前**推荐使用**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/WebAuth)