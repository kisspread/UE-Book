# Motion Design Data Link OAuth

> Motion Design Data Link functionality for OAuth 2.0（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 数据链路认证 |
| 分类 | Other |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（子系统、节点、设置、令牌） |
| 模块 | `DataLinkOAuth` (Runtime), `DataLinkOAuthEditor` (Editor) |
| 实验性 | ⚦ 是 |
| 创建时间 | 2025-08-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DataLinkOAuth) | |

## 用途

本插件为 UE5 的 **Motion Design** 工具链中的 **DataLink** (数据链接) 功能提供 **OAuth 2.0 授权流程** 的标准化实现。它解决的核心问题是：在虚拟制片流程中，当需要通过 DataLink 节点访问外部需要用户授权的服务（如在线表格、云存储、特定API等）时，如何安全、标准化地获取并管理访问令牌（Access Token）。

插件内置了一个本地 HTTP 回调服务器来接收 OAuth 提供商的授权码，并处理令牌交换逻辑。它将复杂的 OAuth 流程封装成易于在蓝图数据链接图表中使用的节点，并为开发者提供了扩展基类 (`UDataLinkOAuthSettings`) 来适配不同的 OAuth 提供商（如 Google， GitHub 等）。

## 使用场景

-   你在 **Motion Design** 中配置一个数据链接节点，目标是获取来自 **Google Sheets** 或 **Azure Blob Storage** 的实时数据，而该服务要求使用 OAuth 2.0 进行身份验证。
-   你希望为自定义的、需要用户授权的 Web API 创建一个标准化的数据链接输入源。
-   你需要在运行时安全地管理多个不同服务的 OAuth 令牌生命周期，包括缓存和过期清理。

## 蓝图用法

本插件的核心蓝图功能通过 DataLink 图表中的节点暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `OAuth` (Data Link Node) | 在数据链接图表中添加一个 OAuth 授权节点。这是启动整个认证流程的入口点。 | `UDataLinkNodeOAuth` |
| `FDataLinkOAuthSettingsWrapper` | 一个结构体包装器，用于在 `OAuth` 节点的属性中引用具体的 OAuth 设置资产。 | `FDataLinkOAuthSettingsWrapper` |

### 使用示例（蓝图描述）

1.  **创建设置资产**：在内容浏览器中，右键 → `杂项` → `数据资产`，选择一个 `UDataLinkOAuthSettings` 的子类（如内置的 `OAuth Default Settings`）来创建资产。在此资产中配置客户端ID、客户端密钥、授权URL、作用域等参数。
2.  **配置图表**：在 Motion Design 的 DataLink 图表中，添加一个 **`OAuth`** 节点。
3.  **连接设置**：选中 `OAuth` 节点，在其细节面板中，将上一步创建的 OAuth 设置资产拖拽到 `OAuth Settings` 属性槽中。
4.  **连接流程**：`OAuth` 节点有两个输出引脚：一个用于输出最终获取的 **访问令牌 (Access Token)**，另一个用于输出错误信息。将令牌引脚连接到后续需要授权的数据处理节点（例如，一个执行 HTTP 请求的节点）。
5.  **运行触发**：当图表执行到该节点时，系统会自动在本地（127.0.0.1）启动一个临时监听服务器，并在默认浏览器中打开对应的 OAuth 服务授权页面。用户完成授权后，浏览器会重定向回本地服务器，节点自动完成令牌交换，并将结果输出。

## C++ 用法

### 头文件引入

```cpp
#include "DataLinkOAuthSubsystem.h"
#include "DataLinkOAuthSettings.h"
#include "DataLinkNodeOAuth.h"
#include "DataLinkOAuthToken.h"
```

### 基本用法

创建一个自定义的 OAuth 设置类，以适配特定的 OAuth 提供商。

```cpp
// MyGoogleOAuthSettings.h
#pragma once
#include "DataLinkOAuthSettings.h"
#include "MyGoogleOAuthSettings.generated.h"

UCLASS(DisplayName = "Google OAuth Settings")
class UMyGoogleOAuthSettings : public UDataLinkOAuthSettings
{
    GENERATED_BODY()

public:
    UMyGoogleOAuthSettings();

    // 构建 Google 特定的授权请求 URL
    virtual bool BuildAuthRequestUrl(FUrlBuilder& OutRequestUrl, FDataLinkNodeOAuthInstance& InOAuthInstance) const override;

    // 构建 Google 特定的令牌交换请求 URL
    virtual bool BuildExchangeCodeTokenUrl(FUrlBuilder& OutRequestUrl, FDataLinkNodeOAuthInstance& InOAuthInstance, FStringView InAuthCode) const override;

private:
    // Google API 的授权端点
    UPROPERTY(EditAnywhere, Category = "Google")
    FString AuthEndpoint = TEXT("https://accounts.google.com/o/oauth2/v2/auth");

    // Google API 的令牌端点
    UPROPERTY(EditAnywhere, Category = "Google")
    FString TokenEndpoint = TEXT("https://oauth2.googleapis.com/token");
};
```

```cpp
// MyGoogleOAuthSettings.cpp
#include "MyGoogleOAuthSettings.h"

UMyGoogleOAuthSettings::UMyGoogleOAuthSettings()
{
    // 设置 Google 所需的默认作用域（范围）
    Scopes.Add(TEXT("openid"));
    Scopes.Add(TEXT("profile"));
    Scopes.Add(TEXT("email"));
}

bool UMyGoogleOAuthSettings::BuildAuthRequestUrl(FUrlBuilder& OutRequestUrl, FDataLinkNodeOAuthInstance& InOAuthInstance) const
{
    // 构建符合 Google 规范的授权 URL
    OutRequestUrl.Appendf(TEXT("%s?client_id=%s&redirect_uri=%s:%d&response_type=code&scope=%s&access_type=offline"),
        *AuthEndpoint,
        *ClientId,
        *LoopbackAddress,
        InOAuthInstance.ListenPort,
        *FString::Join(Scopes, TEXT(" ")));
    // ... 省略 state 参数设置等细节
    return true;
}

bool UMyGoogleOAuthSettings::BuildExchangeCodeTokenUrl(FUrlBuilder& OutRequestUrl, FDataLinkNodeOAuthInstance& InOAuthInstance, FStringView InAuthCode) const
{
    // 构建用于用授权码交换访问令牌的 POST 请求 URL 和参数
    OutRequestUrl.Appendf(TEXT("%s?code=%s&client_id=%s&client_secret=%s&redirect_uri=%s:%d&grant_type=authorization_code"),
        *TokenEndpoint,
        *InAuthCode,
        *ClientId,
        *ClientSecret,
        *LoopbackAddress,
        InOAuthInstance.ListenPort);
    return true;
}
```

### 进阶用法

查询和管理子系统中的令牌缓存。

```cpp
#include "DataLinkOAuthSubsystem.h"

void CheckCachedToken(const UDataLinkOAuthSettings* MySettings)
{
    UDataLinkOAuthSubsystem* OAuthSubsystem = UDataLinkOAuthSubsystem::Get();
    if (OAuthSubsystem)
    {
        // 尝试查找与特定设置对应的缓存令牌
        const FDataLinkOAuthToken* CachedToken = OAuthSubsystem->FindToken(MySettings);
        if (CachedToken && !CachedToken->AccessToken.IsEmpty())
        {
            UE_LOG(LogTemp, Log, TEXT("Found cached token of type: %s"), *CachedToken->TokenType);
            // 使用令牌...
        }
        else
        {
            UE_LOG(LogTemp, Warning, TEXT("No valid cached token found. A new authorization flow is needed."));
        }

        // 手动清理所有过期的令牌
        OAuthSubsystem->CleanExpiredTokens();
    }
}
```

## Demo 示例

一个完整的自定义 OAuth 设置类示例。

```cpp
// GitHubOAuthSettings.h
#pragma once
#include "DataLinkOAuthSettings.h"
#include "GitHubOAuthSettings.generated.h"

UCLASS(DisplayName = "GitHub OAuth Settings")
class UGitHubOAuthSettings : public UDataLinkOAuthSettings
{
    GENERATED_BODY()

public:
    UGitHubOAuthSettings();

    virtual bool BuildAuthRequestUrl(FUrlBuilder& OutRequestUrl, FDataLinkNodeOAuthInstance& InOAuthInstance) const override;
    virtual bool ValidateRequest(const FHttpServerRequest& InRequest, FDataLinkNodeOAuthInstance& InOAuthInstance) const override;
    virtual bool BuildExchangeCodeTokenUrl(FUrlBuilder& OutRequestUrl, FDataLinkNodeOAuthInstance& InOAuthInstance, FStringView InAuthCode) const override;

private:
    UPROPERTY(EditAnywhere, Category = "GitHub")
    FString AuthorizationURL = TEXT("https://github.com/login/oauth/authorize");

    UPROPERTY(EditAnywhere, Category = "GitHub")
    FString TokenExchangeEndpoint = TEXT("https://github.com/login/oauth/access_token");

    UPROPERTY(EditAnywhere, Category = "GitHub")
    TArray<FString> Scopes = { TEXT("repo"), TEXT("user") };
};
```

```cpp
// GitHubOAuthSettings.cpp
#include "GitHubOAuthSettings.h"
#include "DataLinkOAuthInstance.h" // For FDataLinkNodeOAuthInstance

UGitHubOAuthSettings::UGitHubOAuthSettings()
{
    // 无需额外构造
}

bool UGitHubOAuthSettings::BuildAuthRequestUrl(FUrlBuilder& OutRequestUrl, FDataLinkNodeOAuthInstance& InOAuthInstance) const
{
    // 构建 GitHub 授权 URL，并生成一个随机 state 参数用于安全验证
    const FString State = FGuid::NewGuid().ToString();
    // 将 state 保存到共享数据中，供后续验证使用
    if (FDataLinkOAuthDefaultSharedData* SharedData = InOAuthInstance.SharedData.GetMutablePtr<FDataLinkOAuthDefaultSharedData>())
    {
        SharedData->State = State;
    }

    OutRequestUrl.Appendf(TEXT("%s?client_id=%s&redirect_uri=%s:%d&scope=%s&state=%s"),
        *AuthorizationURL,
        *ClientId,
        *LoopbackAddress,
        InOAuthInstance.ListenPort,
        *FString::Join(Scopes, TEXT(" ")),
        *State);
    return true;
}

bool UGitHubOAuthSettings::ValidateRequest(const FHttpServerRequest& InRequest, FDataLinkNodeOAuthInstance& InOAuthInstance) const
{
    // GitHub 会通过 state 参数回调，验证其是否与我们发送的一致
    const FString* StateValuePtr = InRequest.QueryParameters.Find(TEXT("state"));
    if (StateValuePtr && InOAuthInstance.SharedData.IsValid())
    {
        const FDataLinkOAuthDefaultSharedData* SharedData = InOAuthInstance.SharedData.GetPtr<FDataLinkOAuthDefaultSharedData>();
        return SharedData && *StateValuePtr == SharedData->State;
    }
    return false;
}

bool UGitHubOAuthSettings::BuildExchangeCodeTokenUrl(FUrlBuilder& OutRequestUrl, FDataLinkNodeOAuthInstance& InOAuthInstance, FStringView InAuthCode) const
{
    OutRequestUrl.Appendf(TEXT("%s?client_id=%s&client_secret=%s&code=%s&redirect_uri=%s:%d"),
        *TokenExchangeEndpoint,
        *ClientId,
        *ClientSecret,
        *InAuthCode,
        *LoopbackAddress,
        InOAuthInstance.ListenPort);
    return true;
}
```

## 模块依赖

本插件有一个对其他插件的依赖。

| 模块 | 用途 |
|---|---|
| `DataLink` | 核心依赖。DataLinkOAuth 为 DataLink 框架提供 OAuth 扩展节点 (`UDataLinkNodeOAuth`)。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏统一升级为新的格式化宏，属于代码维护。 |
| 2025-09-05 | `de978cf7` | Explicitly adding various missing headers to fix non-unity build errors after large CoreUObject chan | 修复因 CoreUObject 变更导致的非 Unity 构建错误，确保编译通过。 |
| 2025-08-27 | `f25e96ca` | Motion Design: set the scene state and data link plugins to beta | 将插件标记为测试版（Beta）。 |
| 2025-08-27 | `94f96138` | Motion Design: Moved scene state and data link plugins out of experimental into virtualproduction | 插件从实验性目录迁移至虚拟制片目录，标志着其正式化。 |

### 维护评价

**DataLinkOAuth** 是一个相对较新的插件（约1年），从创建之初就处于 **测试版 (Beta)** 状态，表明其API和功能可能尚未最终确定。从提交记录看，在初始合并后，主要进行了一些编译修复和日志维护工作，没有重大的功能变更。这表明它目前处于一个**稳定的测试阶段**，等待用户反馈和集成到更广泛的工作流中。

由于是测试版，不建议在追求极致稳定性的生产关键路径中直接使用。然而，对于虚拟制片和 Motion Design 的数据链接探索、原型开发以及非关键的自动化任务，该插件提供了一个完整且符合UE开发习惯的OAuth实现方案，值得尝试和评估。

**综合评价**：🆕 新兴组件（测试版），功能完整但稳定性待验证，适合在 Motion Design 相关项目中探索使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DataLinkOAuth)
- [官方文档]() (暂无)
- [测试用例]() (插件目录内未发现测试文件)