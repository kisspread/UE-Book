# Web Authentication Plugin

> Access to Web Authenticated Sessions.

| 属性 | 值 |
|---|---|
| 分类 | Online Platform |
| 默认启用 | ❌ 否（需要手动启用） |
| 包含内容 | 否 |
| 模块 | WebAuth (Runtime) |
| 支持平台 | Win64, IOS, Android |
| 创建时间 | 2019-12-19 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Online/WebAuth) | |

## 用途

WebAuth 插件提供**跨平台的 Web 认证会话管理**能力。它封装了在外部浏览器中启动 OAuth/OIDC 认证流程、安全存储凭证、清理登录 Cookie 等操作，让游戏无需嵌入 WebView 即可完成 Web 端的身份验证。

核心设计思路：游戏通过 URL 打开系统浏览器完成登录，浏览器通过自定义 URL Scheme 回调回游戏，插件将回调中的 token 交给游戏代码处理。

**平台实现差异：**
- **iOS**：使用 Apple 的 `ASWebAuthenticationSession` API（iOS 12+），凭证存储在 iOS Keychain
- **Android**：使用 Chrome Custom Tabs 启动认证，凭证存储在 `SharedPreferences`
- **Win64 / 其他平台**：无实际实现（`FNullPlatformWebAuth` 返回 `nullptr`），`IsAvailable()` 返回 `false`

## 使用场景

- 你的游戏使用 OAuth 2.0 / OpenID Connect 登录（如 Epic Games、Google、Steam 等）
- 你需要在移动端打开系统浏览器完成 Web 登录流程
- 你需要安全地在设备上存储登录凭证（token），下次启动时自动登录
- 你需要在登出时清理浏览器中的登录 Cookie

## 蓝图用法

⚠️ **本插件没有暴露任何蓝图接口**（无 `UCLASS`、无 `UFUNCTION(BlueprintCallable)`）。所有 API 均为 C++ 接口，需要通过 C++ 代码调用。

## C++ 用法

### 头文件引入

```cpp
#include "WebAuthModule.h"
```

### 基本用法

#### 检查平台是否支持

```cpp
FWebAuthModule& WebAuthModule = FWebAuthModule::Get();
if (!WebAuthModule.IsAvailable())
{
    UE_LOG(LogTemp, Warning, TEXT("WebAuth is not available on this platform"));
    return;
}
```

#### 发起认证会话

```cpp
FString AuthURL = TEXT("https://your-auth-server.com/authorize?client_id=xxx&redirect_uri=mygame://callback");
FString AppScheme = TEXT("mygame");

FWebAuthModule::Get().GetWebAuth().AuthSessionWithURL(
    AuthURL,
    AppScheme,
    FWebAuthSessionCompleteDelegate::CreateLambda([](const FString& RedirectURL, bool bHasResponse)
    {
        if (bHasResponse && !RedirectURL.IsEmpty())
        {
            // 解析 RedirectURL 中的 token/authorization code
            UE_LOG(LogTemp, Log, TEXT("Auth callback received: %s"), *RedirectURL);
        }
        else
        {
            UE_LOG(LogTemp, Warning, TEXT("Auth session cancelled or failed"));
        }
    })
);
```

#### 存储凭证

```cpp
// 保存登录凭证
FWebAuthModule::Get().GetWebAuth().SaveCredentials(
    TEXT("device-id-123"),      // Id
    TEXT("refresh-token-abc"),  // Token
    TEXT("Production")          // EnvironmentName
);

// 传入空 Id 或 Token 会清除已存储的凭证
FWebAuthModule::Get().GetWebAuth().SaveCredentials(FString(), FString(), TEXT("Production"));
```

#### 加载凭证

```cpp
FString OutId, OutToken;
if (FWebAuthModule::Get().GetWebAuth().LoadCredentials(OutId, OutToken, TEXT("Production")))
{
    UE_LOG(LogTemp, Log, TEXT("Loaded credentials - Id: %s"), *OutId);
    // 使用 OutId 和 OutToken 自动登录
}
```

#### 清理登录 Cookie

```cpp
FWebAuthModule::Get().GetWebAuth().DeleteLoginCookies(
    TEXT("login_"),          // Cookie 前缀
    TEXT("https"),            // Scheme
    TEXT("your-auth-server.com"),  // Domain
    TEXT("/login")            // Path
);
```

### 进阶用法

#### Console 命令测试

在 Development 构建中，可通过控制台命令测试认证会话：

```
WebAuth Session https://your-auth-server.com/authorize mygame://callback
```

### 各平台实现细节

#### iOS

- 使用 `ASWebAuthenticationSession`（要求 iOS 12+）
- 需要在 Info.plist 中注册 `CFBundleURLTypes` 以接收回调
- 凭证存储在 iOS Keychain（`kSecClassGenericPassword`）
- 旧版凭证（基于 `identifierForVendor`）会自动迁移到新位置（基于 `bundleIdentifier`）
- 需要链接 `AuthenticationServices.framework`

#### Android

- 使用 Chrome Custom Tabs 打开认证页面
- 凭证存储在 `SharedPreferences`（键名 `MCP_DeviceId` / `MCP_DeviceToken`）
- 需要在项目 UPL.xml 中配置 URL Scheme 以接收回调
- 自动清除 `.`、`www.` 前缀域名变体的 Cookie

## Demo 示例

### 最小登录流程示例

**WebAuthDemo.Build.cs** 中添加依赖（插件本身就是 Runtime 模块，你的模块无需额外依赖它，仅需启用插件）：

```csharp
// 在 .uproject 或 DefaultEngine.ini 中启用插件即可
// 如果需要直接引用模块：
PublicDependencyModuleNames.Add("WebAuth");
```

**WebAuthDemo.h**

```cpp
#pragma once

#include "CoreMinimal.h"

DECLARE_LOG_CATEGORY_EXTERN(LogWebAuthDemo, Log, All);

class FWebAuthDemo
{
public:
    /** 发起登录 */
    static void Login();
    
    /** 检查是否有已保存的凭证 */
    static bool TryAutoLogin();
    
    /** 清除凭证并登出 */
    static void Logout();
};
```

**WebAuthDemo.cpp**

```cpp
#include "WebAuthDemo.h"
#include "WebAuthModule.h"

DEFINE_LOG_CATEGORY(LogWebAuthDemo);

void FWebAuthDemo::Login()
{
    FWebAuthModule& WebAuthModule = FWebAuthModule::Get();
    if (!WebAuthModule.IsAvailable())
    {
        UE_LOG(LogWebAuthDemo, Error, TEXT("WebAuth not available on this platform"));
        return;
    }

    const FString AuthURL = TEXT("https://accounts.example.com/authorize?client_id=mygame&response_type=token");
    const FString Scheme = TEXT("mygame");

    WebAuthModule.GetWebAuth().AuthSessionWithURL(
        AuthURL,
        Scheme,
        FWebAuthSessionCompleteDelegate::CreateLambda([](const FString& RedirectURL, bool bHasResponse)
        {
            if (bHasResponse && !RedirectURL.IsEmpty())
            {
                UE_LOG(LogWebAuthDemo, Log, TEXT("Login successful, redirect: %s"), *RedirectURL);
                // 解析 token 并保存
                FString Token = TEXT("parsed_token_from_url");
                FString UserId = TEXT("user_123");
                FWebAuthModule::Get().GetWebAuth().SaveCredentials(UserId, Token, TEXT("Production"));
            }
            else
            {
                UE_LOG(LogWebAuthDemo, Warning, TEXT("Login cancelled"));
            }
        })
    );
}

bool FWebAuthDemo::TryAutoLogin()
{
    FWebAuthModule& WebAuthModule = FWebAuthModule::Get();
    if (!WebAuthModule.IsAvailable())
    {
        return false;
    }

    FString UserId, Token;
    if (WebAuthModule.GetWebAuth().LoadCredentials(UserId, Token, TEXT("Production")))
    {
        if (!UserId.IsEmpty() && !Token.IsEmpty())
        {
            UE_LOG(LogWebAuthDemo, Log, TEXT("Auto-login with stored credentials for user: %s"), *UserId);
            // 使用凭证进行自动登录
            return true;
        }
    }
    return false;
}

void FWebAuthDemo::Logout()
{
    FWebAuthModule& WebAuthModule = FWebAuthModule::Get();
    if (!WebAuthModule.IsAvailable())
    {
        return;
    }

    // 清除存储的凭证
    WebAuthModule.GetWebAuth().SaveCredentials(FString(), FString(), TEXT("Production"));

    // 清除浏览器 Cookie
    WebAuthModule.GetWebAuth().DeleteLoginCookies(
        TEXT("login_"),
        TEXT("https"),
        TEXT("accounts.example.com"),
        TEXT("/login")
    );

    UE_LOG(LogWebAuthDemo, Log, TEXT("Logged out and cleared credentials"));
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础模块（所有平台） |
| `ApplicationCore` | 平台核心功能（仅 iOS、Android） |
| `Launch` | Android 启动相关（仅 Android） |

**附加原生依赖：**
- iOS: `AuthenticationServices.framework`
- Android: `com.android.support:customtabs:25.2.0`（通过 UPL.xml 自动添加）

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-09-02 | `5a48f72` | Registered JNI functions. Made JNI classes for Java classes. Added thread_local Ue::Jni::Env global. Various JNI bug fixes and cleanup | Android JNI 重构：迁移到新的 UE JNI 框架，修复多线程环境问题 |
| 2025-08-14 | `8e3c931` | WebAuth (IOS) - Use UE Log macros instead of NS_LOG, migrate credentials to new location | iOS 凭证迁移：用 bundleIdentifier 替代 identifierForVendor 作为 Keychain service，避免卸载后凭证失效 |
| 2025-08-01 | `c101fef` | Use a string that doesn't change after reinstalls as key for keychain to store credentials | iOS 修复：解决重装 App 后凭证丢失的问题 |

### 维护评价

- **创建时间**：2019-12-19（约 6 年前）
- **维护状态**：**活跃维护** — 2025 年 8-9 月连续有多次实质性更新，主要针对 iOS 和 Android 平台的凭证存储和 JNI 框架优化
- **实验性**：`EnabledByDefault=false`，属于可选插件，但并非标记为实验性
- **平台覆盖**：仅支持 iOS 和 Android 有实际功能，Win64 为 Null 实现
- **推荐度**：如果你的游戏需要在移动端进行 Web OAuth 登录，这是一个成熟的解决方案。注意 Win64 平台不支持，桌面端需要其他方案

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Online/WebAuth)
- [官方文档](https://docs.unrealengine.com/)（无专门页面）
- [WebAuth_UPL.xml（Android 配置）](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Online/WebAuth/Source/WebAuth_UPL.xml)
