# Motion Design Data Link OAuth

> Motion Design Data Link functionality for OAuth 2.0

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产定义、资产工厂） |
| 模块 | `DataLinkOAuth` (Runtime), `DataLinkOAuthEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-23 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DataLinkOAuth) | |

## 用途

DataLinkOAuth 是 UE5 [DataLink](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DataLink) 的扩展插件，实现了 **OAuth 2.0 Authorization Code 流程**。它让 DataLink 图中的节点能够自动完成浏览器授权 → 获取授权码 → 交换 Access Token → 注入 HTTP 请求头 的完整流程，主要用于 Motion Design（虚拟制作）场景中需要调用需要 OAuth 认证的第三方 REST API。

核心解决的问题：在 UE 内部启动本地 HTTP 服务器监听回调、自动打开浏览器让用户登录授权、解析回调中的授权码、用授权码换取 Access Token、缓存 Token 以便复用，最终将 `Authorization: <token_type> <access_token>` 头注入到 DataLink HTTP 请求中。

## 使用场景

- 你在 Motion Design 中需要从 Google、Spotify、GitHub 等 OAuth 2.0 服务拉取数据 → 使用此插件的 OAuth 节点
- 你需要在 DataLink 图中添加一个需要 OAuth 认证的 API 数据源 → 在图中插入 OAuth 节点，输入 HTTP Settings 和 OAuth Settings 即可
- 你需要自定义 OAuth 提供商（如企业内部 SSO）→ 继承 `UDataLinkOAuthSettings` 实现自定义逻辑

## 蓝图用法

此插件主要面向 C++ 扩展，蓝图可直接使用的是通过资产工厂创建 OAuth Settings 资产。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| OAuth 节点（DataLink 图中） | DataLink 图节点，执行 OAuth 2.0 Authorization Code 流程并输出带 Authorization 头的 Http Settings | `UDataLinkNodeOAuth` |

### 使用示例（蓝图描述）

1. 在内容浏览器中右键 → Miscellaneous → Data Link OAuth Settings，选择一个 `UDataLinkOAuthSettings` 子类（如 `UDataLinkOAuthDefaultSettings`）创建资产
2. 在资产中配置 ClientId、ClientSecret、AuthorizationURL、TokenExchangeEndpoint、Scopes 等参数
3. 在 DataLink 图中添加 OAuth 节点（分类：Authorization）
4. 将 Http Settings（包含目标 API URL 等）连接到 OAuth 节点的 `InputHttp` 引脚
5. 将创建的 OAuth Settings 资产包装为 `FDataLinkOAuthSettingsWrapper` 连接到 `InputOAuth` 引脚
6. OAuth 节点的输出是带 Authorization 头的 Http Settings，可连接到后续的 HTTP 请求节点

## C++ 用法

### 头文件引入

```cpp
#include "DataLinkOAuthSubsystem.h"
#include "DataLinkOAuthSettings.h"
#include "DataLinkNodeOAuth.h"
#include "DataLinkOAuthToken.h"
```

### 基本用法

**自定义 OAuth Settings**

要支持自定义 OAuth 提供商，需要继承 `UDataLinkOAuthSettings` 并重写关键虚函数：

```cpp
// MyOAuthSettings.h
#pragma once

#include "DataLinkOAuthSettings.h"
#include "MyOAuthSettings.generated.h"

UCLASS(DisplayName="My Custom OAuth Settings")
class UMyOAuthSettings : public UDataLinkOAuthSettings
{
    GENERATED_BODY()

public:
    // 构建授权 URL（用户浏览器跳转的目标地址）
    virtual bool BuildAuthRequestUrl(FUrlBuilder& OutRequestUrl,
        FDataLinkNodeOAuthInstance& InOAuthInstance) const override;

    // 验证回调请求是否属于当前 OAuth 实例
    virtual bool ValidateRequest(const FHttpServerRequest& InRequest,
        FDataLinkNodeOAuthInstance& InOAuthInstance) const override;

    // 从回调请求中提取授权码
    virtual bool FindAuthCode(const FHttpServerRequest& InRequest,
        FDataLinkNodeOAuthInstance& InOAuthInstance,
        FStringView& OutAuthCodeView) const override;

    // 构建用授权码交换 Access Token 的请求 URL
    virtual bool BuildExchangeCodeTokenUrl(FUrlBuilder& OutRequestUrl,
        FDataLinkNodeOAuthInstance& InOAuthInstance,
        FStringView InAuthCode) const override;

    // 从 Token 响应 JSON 构建 FDataLinkOAuthToken（如需自定义解析）
    virtual bool BuildAuthToken(FStringView InAccessResponse,
        FDataLinkOAuthToken& OutAuthToken) const override;

    // 将 Token 注入 HTTP 请求头（如需自定义 Authorization 格式）
    virtual bool AuthorizeHttpRequest(const FDataLinkOAuthToken& InAuthToken,
        FDataLinkHttpSettings& InOutHttpSettings) const override;
};
```

源码参考：`DataLinkOAuthSettings.h`

**使用默认 Settings 子类**

`UDataLinkOAuthDefaultSettings` 是一个开箱即用的实现，适用于标准 OAuth 2.0 提供商。只需配置以下属性：

```cpp
// 创建 UDataLinkOAuthDefaultSettings 资产并配置
UDataLinkOAuthDefaultSettings* Settings = GetDefault<UDataLinkOAuthDefaultSettings>();
// 在编辑器资产中设置：
// - ClientId: OAuth 客户端 ID
// - ClientSecret: OAuth 客户端密钥
// - AuthorizationURL: 授权端点（如 https://accounts.google.com/o/oauth2/auth）
// - TokenExchangeEndpoint: Token 交换端点（如 https://oauth2.googleapis.com/token）
// - Scopes: 请求的权限范围数组
```

源码参考：`DataLinkOAuthDefaultSettings.h`

**查询缓存的 Token**

```cpp
#include "DataLinkOAuthSubsystem.h"

UDataLinkOAuthSubsystem* Subsystem = UDataLinkOAuthSubsystem::Get();
if (Subsystem)
{
    if (const FDataLinkOAuthToken* Token = Subsystem->FindToken(MyOAuthSettings))
    {
        // Token 有效，可直接使用
        const FString& AccessToken = Token->AccessToken;
        const FString& TokenType = Token->TokenType; // 通常是 "Bearer"
        const FDateTime& Expiration = Token->ExpirationDate;
    }
}
```

源码参考：`DataLinkOAuthSubsystem.h`

### 进阶用法

**OAuth 流程完整架构**

DataLinkOAuth 的 OAuth 2.0 Authorization Code 流程分为以下阶段：

1. **端口发现**：通过绑定端口 0 自动找到一个未使用的本地端口
2. **启动 HTTP 监听**：在该端口上启动 `IHttpRouter`，注册请求预处理器
3. **打开浏览器**：调用 `FPlatformProcess::LaunchURL` 打开浏览器跳转到授权 URL
4. **等待回调**：用户在浏览器完成授权后，OAuth 提供商回调到 `http://127.0.0.1:<port>`
5. **验证状态**：通过 `state` 参数验证请求是否属于当前实例
6. **提取授权码**：从回调 URL 的 `code` 参数中提取授权码
7. **交换 Token**：向 Token 端点 POST 请求，用授权码换取 Access Token
8. **缓存 Token**：将 Token 注册到 `UDataLinkOAuthSubsystem` 供后续复用
9. **注入请求头**：将 `Authorization: Bearer <token>` 注入到输出的 `FDataLinkHttpSettings`

**Token 缓存机制**

Token 通过 `FDataLinkOAuthTokenHandle` 进行缓存，该 handle 基于 `UDataLinkOAuthSettings` 的属性值计算 CRC32 哈希。相同配置的 Settings 会复用同一份缓存 Token。Token 过期后会被自动清理（有 5 秒的提前量 padding）。

源码参考：`DataLinkOAuthTokenHandle.cpp`、`DataLinkOAuthSubsystem.cpp`

**SharedData 机制**

OAuth 流程的各个阶段可以通过 `FInstancedStruct` 类型的 SharedData 共享数据。`UDataLinkOAuthDefaultSettings` 使用 `FDataLinkOAuthDefaultSharedData`（包含 `State` 字段用于 CSRF 防护）。自定义 Settings 可以指定自己的 SharedData 类型。

源码参考：`DataLinkOAuthDefaultSharedData.h`

## Demo 示例

### 自定义 OAuth Settings（最小示例）

**MyOAuthSettings.Build.cs**

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "DataLinkOAuth",
});
```

**MyOAuthSettings.h**

```cpp
#pragma once

#include "DataLinkOAuthSettings.h"
#include "MyOAuthSettings.generated.h"

UCLASS(DisplayName="GitHub OAuth Settings")
class UMyOAuthSettings : public UDataLinkOAuthSettings
{
    GENERATED_BODY()

public:
    UMyOAuthSettings();

    virtual bool BuildAuthRequestUrl(FUrlBuilder& OutRequestUrl,
        FDataLinkNodeOAuthInstance& InOAuthInstance) const override;

    virtual bool ValidateRequest(const FHttpServerRequest& InRequest,
        FDataLinkNodeOAuthInstance& InOAuthInstance) const override;

    virtual bool BuildExchangeCodeTokenUrl(FUrlBuilder& OutRequestUrl,
        FDataLinkNodeOAuthInstance& InOAuthInstance,
        FStringView InAuthCode) const override;

private:
    UPROPERTY(EditAnywhere, Category="OAuth")
    TArray<FString> Scopes;
};
```

**MyOAuthSettings.cpp**

```cpp
#include "MyOAuthSettings.h"
#include "DataLinkOAuthDefaultSharedData.h"
#include "DataLinkOAuthInstance.h"
#include "PlatformHttp.h"

UMyOAuthSettings::UMyOAuthSettings()
{
    SharedDataType = FDataLinkOAuthDefaultSharedData::StaticStruct();
}

bool UMyOAuthSettings::BuildAuthRequestUrl(FUrlBuilder& OutRequestUrl,
    FDataLinkNodeOAuthInstance& InOAuthInstance) const
{
    FDataLinkOAuthDefaultSharedData& SharedData =
        InOAuthInstance.SharedData.GetMutable<FDataLinkOAuthDefaultSharedData>();

    const FString RedirectUri = FString::Printf(TEXT("%s:%d"),
        LoopbackAddress, InOAuthInstance.ListenPort);

    OutRequestUrl << TEXT("https://github.com/login/oauth/authorize")
        << TEXT("?response_type=code")
        << TEXT("&client_id=") << ClientId
        << TEXT("&redirect_uri=") << FPlatformHttp::UrlEncode(RedirectUri)
        << TEXT("&state=") << SharedData.State;

    if (!Scopes.IsEmpty())
    {
        OutRequestUrl << TEXT("&scope=");
        for (const FString& Scope : Scopes)
        {
            OutRequestUrl << FPlatformHttp::UrlEncode(Scope) << TEXT("+");
        }
        OutRequestUrl.RemoveAt(OutRequestUrl.Len() - 1, 1);
    }
    return true;
}

bool UMyOAuthSettings::ValidateRequest(const FHttpServerRequest& InRequest,
    FDataLinkNodeOAuthInstance& InOAuthInstance) const
{
    FDataLinkOAuthDefaultSharedData& SharedData =
        InOAuthInstance.SharedData.GetMutable<FDataLinkOAuthDefaultSharedData>();
    const FString* FoundState = InRequest.QueryParams.Find(TEXT("state"));
    return FoundState && *FoundState == SharedData.State;
}

bool UMyOAuthSettings::BuildExchangeCodeTokenUrl(FUrlBuilder& OutRequestUrl,
    FDataLinkNodeOAuthInstance& InOAuthInstance, FStringView InAuthCode) const
{
    const FString RedirectUri = FString::Printf(TEXT("%s:%d"),
        LoopbackAddress, InOAuthInstance.ListenPort);

    OutRequestUrl << TEXT("https://github.com/login/oauth/access_token")
        << TEXT("?grant_type=authorization_code")
        << TEXT("&redirect_uri=") << FPlatformHttp::UrlEncode(RedirectUri)
        << TEXT("&client_id=") << ClientId
        << TEXT("&client_secret=") << ClientSecret
        << TEXT("&code=") << InAuthCode;
    return true;
}
```

## 模块依赖

从 `DataLinkOAuth.Build.cs` 的 `PublicDependencyModuleNames` 和 `PrivateDependencyModuleNames` 提取：

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `DataLink` | DataLink 节点图框架（必需） |
| `DataLinkHttp` | DataLink HTTP 请求类型（`FDataLinkHttpSettings`） |
| `Engine` | 引擎核心（GEngine 等） |
| `HTTP` | HTTP 客户端（用于 Token 交换请求） |
| `HTTPServer` | 本地 HTTP 服务器（用于 OAuth 回调监听） |
| `Json` | JSON 解析（Token 响应解析） |
| `Sockets` | Socket 操作（用于自动端口发现） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 |
|---|---|---|
| 2025-09-12 | `8406696f` | 修复非 unity build 缺失头文件问题 |
| 2025-08-27 | `f25e96ca` | 将 DataLink 插件设置为 Beta 状态 |
| 2025-08-27 | `94f96138` | 将 DataLink 插件从 Experimental 迁移到 VirtualProduction 目录 |

### 维护评价

- **创建时间**：2025-04-23，约 1 年前
- **状态**：实验性（IsBetaVersion=true），仍在积极开发中
- **迁移历史**：最初在 `Engine/Plugins/Experimental/`，于 2025-08 迁移到 `Engine/Plugins/VirtualProduction/`
- **依赖关系**：依赖 `DataLink` 和 `DataLinkHttp`，属于 Motion Design 生态系统
- **推荐使用**：适合在 Motion Design / Virtual Production 场景中使用。作为 Beta 插件，API 可能会有变动，不建议在生产环境的关键路径中使用。如需在非 Motion Design 场景中使用 OAuth，建议自行实现或使用第三方库。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DataLinkOAuth)
- [DataLink 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DataLink)（前置依赖）
- [DataLinkHttp 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DataLinkHttp)（HTTP 请求类型）
