# WebAPI

> Automated generation of web based APIs

| 属性 | 值 |
|---|---|
| 中文名 | Web API 自动生成 |
| 分类 | Web |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（代码生成模板） |
| 模块 | `WebAPI` (Runtime), `WebAPIBlueprintGraph` (Runtime), `WebAPIEditor` (Runtime), `WebAPILiquidJS` (Runtime), `WebAPIOpenAPI` (Runtime), `PLUGIN_NAMEGenerated` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-07-11 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Web/WebAPI) | |

## 用途

WebAPI 插件是一套**基于 OpenAPI/Swagger 规范自动生成 REST API 客户端代码**的框架。它解决的核心问题是：当后端团队提供了 OpenAPI 规范文件时，UE5 项目需要手动编写大量重复的 HTTP 请求、序列化、反序列化、认证等样板代码——这个插件将这些工作自动化。

插件的实际能力包括：

- **HTTP 请求封装**：提供模板化的 `TRequest<PayloadType>` 类，自动将 UStruct 序列化为 JSON 并发送请求
- **操作对象池**：`UWebAPISubsystem` 实现了 `UWebAPIOperationObject` 的对象池，避免频繁 GC
- **批量请求**：通过 `BatchRequests` 将多个同类型请求合并为单个数组 JSON 请求
- **OAuth 认证**：内置 OAuth 认证流程，自动处理 Token 获取和刷新
- **代码生成模板**：集成 LiquidJS 模板引擎，从 OpenAPI 规范生成 C++ 代码和蓝图节点
- **蓝图集成**：通过 `WebAPIBlueprintGraph` 模块提供自定义蓝图节点图支持

本插件处于实验阶段（`IsExperimentalVersion=true`，`EnabledByDefault=false`），需要手动启用。

## 使用场景

- 你的后端团队提供了 OpenAPI/Swagger JSON 规范文件，需要在 UE5 中快速生成对应的 API 客户端代码
- 你需要在蓝图中直接调用 REST API，而不想手写 C++ HTTP 请求代码
- 你的项目需要 OAuth 2.0 认证流程，希望有开箱即用的 Token 管理
- 你需要发送批量 API 请求（将多个操作合并为单个 HTTP 请求）
- 你需要对所有 HTTP 请求/响应进行统一的拦截和自定义处理（认证注入、日志记录等）

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetResponseMessage` | 从 API 响应中提取消息文本 | `UWebAPIUtilities` |
| `GetHostFromUrl` | 从完整 URL 中提取主机名 | `UWebAPIUtilities` |

### 使用示例（蓝图描述）

**从 URL 提取主机名：**
1. 拖入 `GetHostFromUrl` 节点
2. 将包含完整 URL 的字符串变量连接到 `InUrl` 引脚
3. 输出引脚返回纯主机名（如 `api.example.com`）

**获取 API 响应消息：**
1. 拖入 `GetResponseMessage` 节点
2. 将 `FWebAPIMessageResponse` 类型变量连接到输入引脚
3. 输出引脚返回 `FText` 类型的消息文本

> **注意**：由于插件处于实验阶段，且核心功能以 C++ 模板和代码生成为主，蓝图可用节点较少。生成的 API 子类通常会暴露更多蓝图可用的操作节点。

## C++ 用法

### 头文件引入

```cpp
#include "IWebAPIModule.h"
#include "WebAPIHttpRequest.h"
#include "WebAPISubsystem.h"
#include "WebAPIDeveloperSettings.h"
#include "WebAPITypes.h"
```

### 基本用法：创建和发送 HTTP 请求

从 `IWebAPIModuleInterface::CreateRequest` 模板函数提取。

```cpp
#include "IWebAPIModule.h"
#include "WebAPIHttpRequest.h"

// 定义请求载荷结构体（必须是 UStruct）
USTRUCT()
struct FMyRequestPayload
{
    GENERATED_BODY()

    UPROPERTY()
    FString Name;

    UPROPERTY()
    int32 Count;
};

// 创建 POST 请求
TSharedRequest<FMyRequestPayload> Request = IWebAPIModuleInterface::CreateRequest<FMyRequestPayload>(
    TEXT("https://api.example.com/v1/items"),
    UE::WebAPI::HttpVerb::NAME_Post.ToString(),  // "POST"
    TEXT("application/json")
);

// 设置载荷并绑定完成回调
FMyRequestPayload Payload;
Payload.Name = TEXT("TestItem");
Payload.Count = 42;

Request->Post(MoveTemp(Payload),
    [](FHttpRequestPtr HttpRequest, FHttpResponsePtr HttpResponse, bool bSucceeded)
    {
        if (bSucceeded && HttpResponse.IsValid())
        {
            // 处理成功响应
            UE_LOG(LogTemp, Log, TEXT("Response: %s"), *HttpResponse->GetContentAsString());
        }
    }
);
```

**来源**：`Public/IWebAPIModule.h`、`Public/WebAPIHttpRequest.h`

### 基本用法：使用 GET 请求

```cpp
TSharedRequest<FMyResponsePayload> GetRequest = IWebAPIModuleInterface::CreateRequest<FMyResponsePayload>(
    TEXT("https://api.example.com/v1/items/123"),
    UE::WebAPI::HttpVerb::NAME_Get.ToString()
);

GetRequest->BindCompletionCallback(
    [](FHttpRequestPtr Request, FHttpResponsePtr Response, bool bSuccess)
    {
        if (bSuccess)
        {
            // 反序列化响应 JSON
            FString JsonString = Response->GetContentAsString();
            FMyResponsePayload Result;
            FJsonObjectConverter::JsonObjectStringToUStruct(JsonString, &Result);
        }
    }
);

GetRequest->Get();
```

**来源**：`Public/WebAPIHttpRequest.h`

### 进阶用法：批量请求

从 `IWebAPIModuleInterface::BatchRequests` 提取——将多个同类请求合并为单个 JSON 数组请求。

```cpp
TArray<TSharedRequest<FMyRequestPayload>> Requests;

for (int32 i = 0; i < 5; ++i)
{
    auto Req = IWebAPIModuleInterface::CreateRequest<FMyRequestPayload>(
        TEXT("https://api.example.com/v1/batch-items"),
        UE::WebAPI::HttpVerb::NAME_Post.ToString()
    );

    FMyRequestPayload Payload;
    Payload.Name = FString::Printf(TEXT("Item_%d"), i);
    Payload.Count = i * 10;
    Req->SetPayloadData(MoveTemp(Payload));

    Requests.Add(Req);
}

// 合并为单个 [payload1, payload2, ...] 格式的请求
TSharedRequest<FMyRequestPayload> BatchedRequest = IWebAPIModuleInterface::BatchRequests<FMyRequestPayload>(
    MoveTemp(Requests)
);

BatchedRequest->BindCompletionCallback(
    [](FHttpRequestPtr Req, FHttpResponsePtr Resp, bool bSuccess)
    {
        // 处理批量响应
    }
);

BatchedRequest->Post();
```

**来源**：`Public/IWebAPIModule.h`（`BatchRequests` 实现）

### 进阶用法：操作对象池

从 `UWebAPISubsystem` 提取——复用操作对象避免 GC 开销。

```cpp
// 获取子系统
UWebAPISubsystem* Subsystem = GEngine->GetEngineSubsystem<UWebAPISubsystem>();

// 从对象池获取操作对象
UWebAPIDeveloperSettings* Settings = GetDefault<UMyAPIDeveloperSettings>();
TObjectPtr<UMyOperationObject> Operation = Subsystem->MakeOperation<UMyOperationObject>(Settings);

// 使用操作对象发起请求...
// Operation->RequestInternal(...)

// 使用完毕后归还到池中
Subsystem->ReleaseOperation<UMyOperationObject>(Operation);
```

**来源**：`Public/WebAPISubsystem.h`

### 进阶用法：自定义请求/响应拦截器

从 `FWebAPIHttpRequestHandlerInterface` 和 `FWebAPIHttpResponseHandlerInterface` 提取。

```cpp
// 实现自定义请求处理器（例如添加自定义认证头）
class FMyCustomAuthHandler : public FWebAPIHttpRequestHandlerInterface
{
public:
    virtual bool HandleHttpRequest(TSharedPtr<IHttpRequest> InRequest, UWebAPIDeveloperSettings* InSettings) override
    {
        // 添加自定义头部
        InRequest->SetHeader(TEXT("X-Custom-Auth"), TEXT("my-token-123"));
        return false; // 返回 false 让后续处理器继续处理
    }
};

// 实现自定义响应处理器（例如全局错误日志）
class FMyLoggingHandler : public FWebAPIHttpResponseHandlerInterface
{
public:
    virtual bool HandleHttpResponse(EHttpResponseCodes::Type InResponseCode,
        TSharedPtr<IHttpResponse> InResponse, bool bInWasSuccessful,
        UWebAPIDeveloperSettings* InSettings) override
    {
        if (!bInWasSuccessful)
        {
            UE_LOG(LogWebAPI, Error, TEXT("API request failed: %d"), InResponseCode);
        }
        return false;
    }
};
```

**来源**：`Public/WebAPIHttpMessageHandlers.h`

## Demo 示例

### 完整的 API 设置和请求示例

```cpp
// MyAPISettings.h
#pragma once

#include "WebAPIDeveloperSettings.h"
#include "MyAPISettings.generated.h"

UCLASS(Config="Engine", DefaultConfig)
class MYGAME_API UMyAPISettings : public UWebAPIDeveloperSettings
{
    GENERATED_BODY()

public:
    UMyAPISettings()
    {
        Host = TEXT("api.mygame.com");
        BaseUrl = TEXT("/v1");
        bLogRequests = true;
    }
};
```

```cpp
// MyAPITypes.h
#pragma once

#include "MyAPITypes.generated.h"

USTRUCT(BlueprintType)
struct FGetPlayerResponse
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadWrite)
    FString PlayerName;

    UPROPERTY(BlueprintReadWrite)
    int32 Level;

    UPROPERTY(BlueprintReadWrite)
    int32 Score;
};

USTRUCT(BlueprintType)
struct FUpdateScoreRequest
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadWrite)
    FString PlayerId;

    UPROPERTY(BlueprintReadWrite)
    int32 NewScore;
};
```

```cpp
// MyAPIClient.h
#pragma once

#include "IWebAPIModule.h"
#include "WebAPIHttpRequest.h"
#include "MyAPITypes.h"
#include "MyAPISettings.h"

class FMyAPIClient
{
public:
    void GetPlayer(const FString& PlayerId, TFunction<void(const FGetPlayerResponse&)> OnComplete)
    {
        const UMyAPISettings* Settings = GetDefault<UMyAPISettings>();
        FString Url = Settings->FormatUrl(FString::Printf(TEXT("/players/%s"), *PlayerId));

        auto Request = IWebAPIModuleInterface::CreateRequest<FGetPlayerResponse>(
            Url, UE::WebAPI::HttpVerb::NAME_Get.ToString());

        Request->BindCompletionCallback(
            [OnComplete](FHttpRequestPtr Req, FHttpResponsePtr Resp, bool bSuccess)
            {
                if (bSuccess && Resp.IsValid())
                {
                    FGetPlayerResponse Result;
                    FJsonObjectConverter::JsonObjectStringToUStruct(
                        Resp->GetContentAsString(), &Result);
                    OnComplete(Result);
                }
            }
        );

        Request->Get();
    }

    void UpdateScore(const FUpdateScoreRequest& ScoreData)
    {
        const UMyAPISettings* Settings = GetDefault<UMyAPISettings>();
        FString Url = Settings->FormatUrl(TEXT("/players/score"));

        auto Request = IWebAPIModuleInterface::CreateRequest<FUpdateScoreRequest>(
            Url, UE::WebAPI::HttpVerb::NAME_Post.ToString());

        Request->Post(FUpdateScoreRequest(ScoreData));
    }
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `HTTP` | HTTP 请求/响应底层支持 |
| `Json` / `JsonUtilities` | UStruct 与 JSON 之间的序列化/反序列化 |

> 其余依赖均为标准 Core/Engine/Slate 等常见模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 FJsonObject 以同时支持 FString 和 FSharedString |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 新日志宏 |
| 2026-03-02 | `9758fa58` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 移除 FJsonObject 中的字符串重复以释放内存 |
| 2026-02-18 | `516817d0` | PR #13954: fix(deps): on-headers is vulnerable to http response header manipulation | 修复依赖库 on-headers 的 HTTP 响应头操纵安全漏洞 |

### 维护评价

**状态：活跃维护中** 🟢

- 创建于 2022 年 7 月，至今约 4 年
- 近期（2026 年）有持续的维护更新，包括编译警告修复、性能优化（内存去重）、安全漏洞修复等
- 更新以基础设施维护为主（编译器兼容性、代码质量、依赖安全），表明该插件已被纳入 UE 持续集成维护体系
- 仍处于实验阶段（`IsExperimentalVersion=true`），API 可能在未来版本发生变化
- 需手动启用（`EnabledByDefault=false`）
- **推荐在实验项目中使用**，生产环境需谨慎评估实验性 API 变更风险

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Web/WebAPI)
- [官方文档](https://epicgames.com)（未提供文档链接）