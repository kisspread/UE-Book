# WebAPI

> Automated generation of web based APIs

| 属性 | 值 |
|---|---|
| 中文名 | WebAPI 运行时 |
| 分类 | Web |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容模板、蓝图资产） |
| 模块 | `WebAPI` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-11-15 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Web/WebAPI) | |

## 用途

WebAPI 插件为 Unreal Engine 提供了一整套用于构建和消费 Web API（如 REST、OpenAPI）的基础设施。它不仅包含运行时 HTTP 请求/响应处理的类型安全封装，还提供了代码生成框架（通过 WebAPIEditor 等子模块）和认证支持。核心 `WebAPI` 模块（Runtime）解决了以下问题：

- 封装了原始 `FHttpModule` 并提供了强类型 `TRequest<T>` 模板，方便发送带类型负载的请求。
- 支持自动化的批量请求合并（BatchRequests）。
- 通过 `UWebAPIOperationObject` 提供异步操作的基类，支持对象池化，复用操作对象。
- 集成了 OAuth 等认证方案，通过 `UWebAPIDeveloperSettings` 统一配置。
- 提供了 `FWebAPIAuthenticationSchemeHandler` 接口，允许自定义请求/响应的拦截处理。

总之，该插件旨在 **简化 Unreal Engine 中 Web API 的调用，并支持从 API 定义自动生成 C++ 和蓝图代码**。

## 使用场景

- **游戏需要与后端 RESTful API 通信**：例如登录、排行榜、商店、云存档等。
- **工具或编辑器插件需要调用外部 JSON API**：比如自动更新内容、获取远程资源列表。
- **需要 OAuth 2.0 认证**：如使用 Bearer Token 访问受保护的 API 端点。
- **批量发送相同类型的请求**：合并多个 POST 请求以提高性能。
- **希望利用对象池减少频繁创建 `UObject` 的开销**：对高频 API 调用做性能优化。
- **使用 OpenAPI/Swagger 规范自动生成 API 客户端**：通过编辑器的代码生成功能（需启用 WebAPIEditor 等模块）。

## 蓝图用法

本模块提供了少量可直接在蓝图中使用的节点和可配置的数据结构。

### UWebAPIUtilities（蓝图函数库）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetResponseMessage` | 从 `FWebAPIMessageResponse` 结构体中提取消息文本。 | `UWebAPIUtilities` |
| `GetHostFromUrl` | 从完整 URL 中提取主机部分（例如 `"https://api.example.com/path"` → `"api.example.com"`）。 | `UWebAPIUtilities` |

### UWebAPIOAuthSettings（配置对象）

可在项目设置或蓝图编辑器中配置 OAuth 认证参数：

| 属性 | 说明 |
|---|---|
| `SchemeName` | 认证方案名称（蓝图只读） |
| `ClientId` | OAuth 客户端标识 |
| `ClientSecret` | OAuth 客户端密钥 |
| `TokenType` | Token 类型，默认 `"Bearer"` |
| `AccessToken` | 服务器返回的访问令牌（蓝图只读） |
| `ExpiresOn` | 令牌过期时间（蓝图只读） |
| `AuthenticationServer` | 认证服务器地址 |
| `AdditionalRequestQueryParameters` | 附加的 URL 查询参数 |
| `AdditionalRequestBodyParameters` | 附加的请求体参数 |

### UWebAPIDeveloperSettings（API 设置）

在项目设置中可以为每个 API 定义主机、基础路径、User-Agent、日期格式、URI 方案等信息。这些设置在 C++ 或蓝图中均可读写。

### 使用示例（蓝图）

1. **获取 URL 的主机名**：调用 `GetHostFromUrl`，输入字符串 `"https://myapi.com/v1/users"`，输出 `"myapi.com"`。
2. **读取 API 响应消息**：当通过操作对象收到响应后，将 `FWebAPIMessageResponse` 传入 `GetResponseMessage` 节点即可显示纯文本消息。

> **注意**：核心的 `CreateRequest`、`BatchRequests` 等函数是 C++ 模板函数，无法直接暴露给蓝图。蓝图用户应使用自动生成的 API 操作对象（通过 WebAPIEditor），或通过 C++ 扩展暴露自定义蓝图节点。

## C++ 用法

### 头文件引入

```cpp
#include "IWebAPIModule.h"
#include "WebAPIHttpRequest.h"
#include "WebAPISubsystem.h"
#include "WebAPIDeveloperSettings.h"
#include "Security/WebAPIAuthentication.h"
```

### 基本用法：类型化 JSON 请求

创建并发送一个带 JSON 负载的 POST 请求，负载类型为自定义结构体 `FMyPayload`。

```cpp
// 定义结构体（需要实现 USTRUCT 的 JSON 序列化）
USTRUCT()
struct FMyPayload
{
    GENERATED_BODY()
    UPROPERTY() FString Name;
    UPROPERTY() int32 Score;
};

// 发送请求
void SendScore(const FString& PlayerName, int32 Score)
{
    FMyPayload Payload;
    Payload.Name = PlayerName;
    Payload.Score = Score;

    TSharedRef<TRequest<FMyPayload>> Request = IWebAPIModuleInterface::CreateRequest<FMyPayload>(
        TEXT("https://example.com/api/score"),
        TEXT("POST"),
        TEXT("application/json")
    );
    Request->AddHeader({TEXT("Authorization"), TEXT("Bearer mytoken")});
    Request->SetPayloadData(Payload);
    Request->BindCompletionCallback([](FHttpRequestPtr HttpRequest, FHttpResponsePtr HttpResponse, bool bSuccess)
    {
        if (bSuccess && HttpResponse.IsValid())
        {
            UE_LOG(LogTemp, Log, TEXT("Response: %s"), *HttpResponse->GetContentAsString());
        }
    });
    (*Request)(); // 发送请求
}
```

来源文件：`Engine/Plugins/Experimental/Web/WebAPI/Source/WebAPI/Public/IWebAPIModule.h`

### 基本用法：批量请求

将多个相同负载类型的请求合并为一个批处理请求（适用于支持批量 JSON 数组的服务端 API）。

```cpp
TArray<TSharedRef<TRequest<FMyPayload>>> Requests;
Requests.Add(IWebAPIModuleInterface::CreateRequest<FMyPayload>(...));
Requests.Add(IWebAPIModuleInterface::CreateRequest<FMyPayload>(...));
// 合并请求
TSharedRef<TRequest<FMyPayload>> Batch = IWebAPIModuleInterface::BatchRequests<FMyPayload>(MoveTemp(Requests));
(*Batch)();
```

来源文件：`Engine/Plugins/Experimental/Web/WebAPI/Source/WebAPI/Public/IWebAPIModule.h`

### 进阶用法：使用操作对象（UWebAPIOperationObject）

操作对象提供了完整的异步生命周期管理，并支持对象池（通过 `UWebAPISubsystem`）。

```cpp
// 在某个拥有 World 上下文的类中
UWebAPISubsystem* Subsystem = GetWorld()->GetSubsystem<UWebAPISubsystem>();
if (Subsystem)
{
    // 获取一个操作对象（假设已有 UMyOperation 子类）
    TObjectPtr<UMyOperation> Op = Subsystem->MakeOperation<UMyOperation>(Settings);
    // 使用 Op 发起请求（具体由子类实现）
    // ...
    // 完成后释放回池
    Subsystem->ReleaseOperation<UMyOperation>(Op);
}
```

来源文件：`Engine/Plugins/Experimental/Web/WebAPI/Source/WebAPI/Public/WebAPISubsystem.h`

### 进阶用法：自定义认证处理器

实现 `FWebAPIAuthenticationSchemeHandler` 并注册到开发设置中，以拦截请求和响应进行认证。

```cpp
class FMyAuthHandler : public FWebAPIAuthenticationSchemeHandler
{
public:
    virtual bool HandleHttpRequest(TSharedPtr<IHttpRequest> InRequest, UWebAPIDeveloperSettings* InSettings) override
    {
        // 在请求发送前追加认证头
        InRequest->SetHeader(TEXT("X-Api-Key"), TEXT("my-secret-key"));
        return false; // 不拦截，继续处理
    }
    virtual bool HandleHttpResponse(EHttpResponseCodes::Type InResponseCode, TSharedPtr<IHttpResponse> InResponse, bool bInWasSuccessful, UWebAPIDeveloperSettings* InSettings) override
    {
        // 检查响应是否需要重新认证等
        return false;
    }
};

// 在模块 StartupModule 时注册
TSharedPtr<FMyAuthHandler> AuthHandler = MakeShared<FMyAuthHandler>();
GetMutableDefault<UMyAPISettings>()->AuthenticationHandlers.Add(AuthHandler);
```

来源文件：`Engine/Plugins/Experimental/Web/WebAPI/Source/WebAPI/Public/Security/WebAPIAuthentication.h`

### 进阶用法：使用 UWebAPIDeveloperSettings

```cpp
UWebAPIDeveloperSettings* Settings = GetMutableDefault<UMyAPISettings>(); // 假设已有子类
Settings->Host = TEXT("api.example.com");
Settings->BaseUrl = TEXT("/v2");
Settings->bOverrideScheme = true;
Settings->URISchemeOverride = TEXT("https");
Settings->SaveConfig();
```

## Demo 示例

以下是一个完整的 C++ 示例，使用 `TRequest` 发送简单 GET 请求并打印结果。

**MyApiClient.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "IWebAPIModule.h"
#include "WebAPIHttpRequest.h"

class FMyApiClient
{
public:
    static void FetchUserInfo(const FString& UserId);
};
```

**MyApiClient.cpp**
```cpp
#include "MyApiClient.h"
#include "HttpModule.h"
#include "Interfaces/IHttpResponse.h"

void FMyApiClient::FetchUserInfo(const FString& UserId)
{
    // 使用 TRequest 创建 GET 请求（PayloadType 可用默认结构体 FEmptyPayload 或自定义的轻量结构）
    TSharedRef<TRequest<FString>> Request = IWebAPIModuleInterface::CreateRequest<FString>(
        FString::Printf(TEXT("https://api.example.com/users/%s"), *UserId),
        TEXT("GET"),
        TEXT("application/json")
    );
    Request->SetPayloadData(FString()); // GET 请求通常无 Body，但模板需要设置（可以为空）
    Request->BindCompletionCallback([](FHttpRequestPtr HttpRequest, FHttpResponsePtr HttpResponse, bool bSuccess)
    {
        if (bSuccess && HttpResponse.IsValid())
        {
            FString ResponseStr = HttpResponse->GetContentAsString();
            UE_LOG(LogTemp, Log, TEXT("UserInfo: %s"), *ResponseStr);
        }
        else
        {
            UE_LOG(LogTemp, Warning, TEXT("Request failed"));
        }
    });
    (*Request)(); // 触发请求
}
```

**说明**：
- 该示例使用了 `TRequest<FString>`，也可以使用自定义的 `USTRUCT` 作为负载类型。
- 需要确保 HTTP 模块已初始化（一般已由引擎自动完成）。
- 效果：发送 GET 请求，异步回调中输出服务器返回的 JSON 字符串。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `HTTP` | 底层 HTTP 请求/响应处理 |
| `Json` | JSON 序列化/反序列化（通过 `FJsonObjectConverter`） |
| `DeveloperSettings` | 支持 `UDeveloperSettings` 基类 |
| `EngineSubsystem` | 支持 `UEngineSubsystem` |
| `Async` | 异步 Future/Promise 支持 |

> 其余依赖如 `Core`, `CoreUObject`, `Engine`, `Slate`, `UMG` 等为标准引擎模块，此处省略。

## 维护状态

### 近期更新

| 日期 | Hash | Commit | 解读 |
|---|---|---|---|
| 2025-07-31 | `399ed9f8` | Make FWindowsPlatformProcess::CreateProc and FMacPlatformProcess::CreateProc specify the handles to | 跨平台进程句柄调整（间接影响 WebAPI 目录） |
| 2025-06-11 | `afdf8d75` | Replace some usages of FORCEINLINE with inline in Online modules. | 样式清理，替换 FORCEINLINE |
| 2024-11-22 | `36771d79` | Updated uplugin descriptor files marked as both Experimental and Beta. | 更新插件描述符（移除了同时标记 Beta 和 Experimental 的冲突） |
| 2024-11-20 | `e2fe1c9e` | Fixed object properties using MustImplement to now use ObjectMustImplement metadata | 修复属性元数据（全局修复） |
| 2024-11-15 | `a2c3875d` | Cleanup of FSlateFontInfo constructor across the solution that uses font paths. | 全局代码清理（影响字体构造） |

### 维护评价

- **创建时间**：2024-11-15，至今约 0.7 年。
- **近期更新**：最后一次功能性 commit 为 2025-06-11 的样式替换，其他多为全局性修复和重构，插件本身的核心功能未看到明显改进。
- **活跃度**：由于插件标记为 **实验性**，且未进入 Beta，维护频率较低。全局改动虽涉及该目录，但都不是 WebAPI 特有的功能更新。
- **已知限制**：作为实验性插件，API 可能随时变动；部分功能（如蓝图节点生成、编辑器的代码生成）依赖于其他子模块，当前 WebAPI 模块仅提供底层运行时。
- **推荐程度**：如果你的项目需要强类型 HTTP 请求封装、对象池或 OAuth 支持，且愿意承担实验性 API 不稳定的风险，可以考虑使用。否则建议直接使用标准的 `FHttpModule` 和 `FJsonObjectConverter`。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Web/WebAPI)
- [官方文档]（暂无，MarkdownURL 为空）
- [测试用例]（未公开测试文件，可能位于 Engine/Tests/ 下，暂不提供链接）