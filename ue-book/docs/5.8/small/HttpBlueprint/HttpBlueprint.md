# HttpBlueprint

> Allows for sending and receiving HTTP requests in Blueprint

| 属性 | 值 |
|---|---|
| 中文名 | 蓝图 HTTP 请求 |
| 分类 | Web |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图节点图资产） |
| 模块 | `HttpBlueprint` (Runtime), `HttpBlueprintGraph` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-03-15 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Web/HttpBlueprint) | |

## 用途

HttpBlueprint 为蓝图系统提供了一套**可视化 HTTP 请求构建和执行框架**。它解决了在蓝图中直接发送 HTTP 请求的痛点：

- **请求构建**：通过自定义蓝图节点，以可视化方式构造 HTTP 请求（选择方法、设置 Header、填写 Body）
- **请求预设**：内置 Json / Http / Url Encoded 三种常用 Content-Type 预设，减少手动配置
- **Header 管理**：提供 `FHttpHeader` 结构体，方便在蓝图中存储和操作 HTTP 头信息
- **节点图扩展**：通过 `HttpBlueprintGraph` 模块实现自定义蓝图节点外观（如根据 HTTP 动词动态显示/隐藏 Body 引脚）

与直接在 C++ 中使用 `FHttpModule` 不同，此插件将 HTTP 请求封装为**代理对象**（Proxy Object），通过蓝图事件驱动方式获取响应结果。

## 使用场景

- 你需要在蓝图中调用 RESTful API（如获取用户数据、提交表单）
- 你在制作原型或快速验证，不想写 C++ 网络代码
- 你需要在蓝图中处理 Json 格式的 HTTP 请求/响应
- 你需要自定义请求预设（如不同的 Content-Type）

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateHttpRequestProxyObject` | 创建并发送 HTTP 请求代理对象 | `UHttpRequestProxyObject` |
| `MakeRequestHeader` | 从 TMap 创建 FHttpHeader 结构体 | `UHttpBlueprintFunctionLibrary` |
| `GetHeaderValue` | 获取指定 Header 的值 | `UHttpBlueprintFunctionLibrary` |
| `GetAllHeaders` | 获取所有 Header（字符串数组格式） | `UHttpBlueprintFunctionLibrary` |
| `GetAllHeadersAsMap` | 获取所有 Header（Map 格式） | `UHttpBlueprintFunctionLibrary` |
| `AddHeader` | 添加一个 Header 键值对 | `UHttpBlueprintFunctionLibrary` |
| `RemoveHeader` | 移除指定 Header | `UHttpBlueprintFunctionLibrary` |

### 请求方法枚举（EHttpVerbs）

| 枚举值 | 说明 |
|---|---|
| `Post` (0) | POST 请求，显示 Body 输入引脚 |
| `Put` (1) | PUT 请求，显示 Body 输入引脚 |
| `Delete` (2) | DELETE 请求，显示 Body 输入引脚 |
| `Patch` (3) | PATCH 请求，显示 Body 输入引脚 |
| `Get` (4) | GET 请求，**不显示** Body 输入引脚 |

### 请求预设枚举（ERequestPresets）

| 枚举值 | 显示名称 | Content-Type |
|---|---|---|
| `Json` | Json Request | `application/json` |
| `Http` | Http Request | `text/html` |
| `Url` | Url Encoded Request | `application/x-www-form-urlencoded` |
| `Custom` | Custom Request | 自定义 |

### 使用示例（蓝图描述）

**发送一个 GET 请求：**

1. 拖出 `Create HttpRequest Proxy Object` 节点
2. `InUrl` 连接一个字符串节点（如 `"https://api.example.com/users"`）
3. `InVerb` 选择 `Get`（此时不会显示 Body 引脚）
4. `InHeader` 连接 `Make Request Header` 节点，构造请求头
5. 将 `On Request Complete` 事件绑定到后续逻辑
6. 在事件回调中，`InResponse` 即为服务器返回的内容

**构造自定义 Header：**

1. 拖出 `Make Request Header` 节点
2. 创建一个 `TMap`，添加键值对如 `{"Authorization": "Bearer xxx"}`
3. 输出的 `FHttpHeader` 可传入请求或用于后续读取

**读取响应 Header：**

1. 在 `On Request Complete` 回调中，通过 `Get Header Value` 节点读取指定 Header
2. 或使用 `Get All Headers As Map` 获取完整的 Header Map

## C++ 用法

### 头文件引入

```cpp
#include "HttpBlueprintTypes.h"
#include "HttpHeader.h"
#include "HttpBlueprintFunctionLibrary.h"
#include "HttpRequestProxyObject.h"
```

### 基本用法

**创建和管理 HTTP Header（C++ 端）：**

```cpp
#include "HttpHeader.h"

// 创建 Header 结构体
FHttpHeader MyHeaders;

// 添加 Header
MyHeaders.AddHeader(TPair<FString, FString>("Content-Type", "application/json"));
MyHeaders.AddHeader(TPair<FString, FString>("Authorization", "Bearer my-token"));

// 获取 Header 值
FString AuthValue = MyHeaders.GetHeader(TEXT("Authorization"));
// AuthValue == "Bearer my-token"

// 获取所有 Header
TArray<FString> AllHeaders = MyHeaders.GetAllHeaders();
const TMap<FString, FString>& HeaderMap = MyHeaders.GetAllHeadersAsMap();

// 移除 Header
bool bRemoved = MyHeaders.RemoveHeader(TEXT("Authorization"));

// 检查是否有效
bool bValid = MyHeaders.IsValid(); // Headers.Num() > 0
```

**将 Header 应用到原生 HTTP 请求：**

```cpp
#include "HttpHeader.h"
#include "HttpModule.h"
#include "Interfaces/IHttpRequest.h"

// 创建原生请求
TSharedRef<IHttpRequest> Request = FHttpModule::Get().CreateRequest();
Request->SetURL(TEXT("https://api.example.com/data"));
Request->SetVerb(TEXT("GET"));

// 使用 FHttpHeader 将所有 Header 一次性设置到请求上
FHttpHeader MyHeaders;
MyHeaders.AddHeader(TPair<FString, FString>("Accept", "application/json"));
MyHeaders.AssignHeadersToRequest(Request);

Request->ProcessRequest();
```

**批量设置 Header（使用 SetHeaders）：**

```cpp
FHttpHeader Headers;
TMap<FString, FString> HeaderMap = {
    {"Content-Type", "application/json"},
    {"Cache-Control", "no-cache"},
    {"X-Custom-Header", "my-value"}
};

// SetHeaders 会覆盖已有 Header
Headers.SetHeaders(HeaderMap);
```

### 进阶用法

**构造 HTTP 请求代理对象（蓝图可用）：**

```cpp
#include "HttpRequestProxyObject.h"

// 创建请求代理（会自动发起请求）
UHttpRequestProxyObject* RequestProxy = UHttpRequestProxyObject::CreateHttpRequestProxyObject(
    TEXT("https://api.example.com/users"),   // URL
    TEXT("POST"),                             // Verb
    FHttpHeader(),                            // Headers
    TEXT("{\"name\": \"test\"}")              // Body
);

// 绑定完成回调（注意：这是蓝图事件，C++ 中需通过蓝图使用）
// RequestProxy->OnRequestComplete.AddDynamic(...)
```

## Demo 示例

**完整的 HTTP 请求 C++ 类示例：**

```cpp
// HttpDemoComponent.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "HttpHeader.h"
#include "HttpDemoComponent.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class YOURPROJECT_API UHttpDemoComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UHttpDemoComponent();

    /** 在蓝图中调用，发送一个简单的 GET 请求 */
    UFUNCTION(BlueprintCallable, Category = "Http Demo")
    void SendGetRequest(const FString& Url);

    /** 在蓝图中调用，发送一个带自定义 Header 的 POST 请求 */
    UFUNCTION(BlueprintCallable, Category = "Http Demo")
    void SendPostRequest(const FString& Url, const FString& JsonBody);

private:
    void OnResponseReceived(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bSuccess);
};
```

```cpp
// HttpDemoComponent.cpp
#include "HttpDemoComponent.h"
#include "HttpModule.h"
#include "Interfaces/IHttpRequest.h"
#include "Interfaces/IHttpResponse.h"
#include "HttpHeader.h"

UHttpDemoComponent::UHttpDemoComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UHttpDemoComponent::SendGetRequest(const FString& Url)
{
    // 构建 Header
    FHttpHeader Headers;
    Headers.AddHeader(TPair<FString, FString>("Accept", "application/json"));

    // 创建请求
    TSharedRef<IHttpRequest> Request = FHttpModule::Get().CreateRequest();
    Request->SetURL(Url);
    Request->SetVerb(TEXT("GET"));
    Headers.AssignHeadersToRequest(Request);
    Request->OnProcessRequestComplete().BindUObject(this, &UHttpDemoComponent::OnResponseReceived);
    Request->ProcessRequest();
}

void UHttpDemoComponent::SendPostRequest(const FString& Url, const FString& JsonBody)
{
    FHttpHeader Headers;
    Headers.AddHeader(TPair<FString, FString>("Content-Type", "application/json"));

    TSharedRef<IHttpRequest> Request = FHttpModule::Get().CreateRequest();
    Request->SetURL(Url);
    Request->SetVerb(TEXT("POST"));
    Request->SetContentAsString(JsonBody);
    Headers.AssignHeadersToRequest(Request);
    Request->OnProcessRequestComplete().BindUObject(this, &UHttpDemoComponent::OnResponseReceived);
    Request->ProcessRequest();
}

void UHttpDemoComponent::OnResponseReceived(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bSuccess)
{
    if (bSuccess && Response.IsValid())
    {
        // 读取响应 Header
        FHttpHeader ResponseHeaders;
        for (const auto& Pair : Response->GetAllHeaders())
        {
            FString Key, Value;
            Pair.Split(TEXT(": "), &Key, &Value);
            ResponseHeaders.AddHeader(TPair<FString, FString>(Key, Value));
        }

        UE_LOG(LogTemp, Log, TEXT("Response: %s"), *Response->GetContentAsString());
        UE_LOG(LogTemp, Log, TEXT("Status: %d"), Response->GetResponseCode());
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("HTTP Request Failed"));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `JsonBlueprintUtilities` | Json 蓝图工具支持（插件依赖） |
| `Http` | 底层 HTTP 模块（FHttpModule / IHttpRequest） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新的 UE_LOGF 格式 |
| 2025-05-28 | `7e9f0fe3` | Fix blueprint compilation crash due to mismatching pin names | 修复因引脚名称不匹配导致的蓝图编译崩溃 |
| 2025-05-22 | `275c11fa` | #JIRA UE-273929 | 修复 JIRA 工单 UE-273929 相关问题 |
| 2024-08-23 | `64ae24ec` | Removed extraneous GetSelfPin implementations. | 移除多余的 GetSelfPin 实现 |
| 2024-01-12 | `7da84c1d` | Replaced UE_NODISCARD with [[nodiscard]]. | 用标准 C++ [[nodiscard]] 替换 UE_NODISCARD 宏 |

### 维护评价

- **状态**：活跃维护中。2025 年仍有实质性 bug 修复（蓝图编译崩溃），2026 年有代码规范化更新
- **实验性**：标记为 `IsExperimentalVersion = true`，且 `EnabledByDefault = false`，需要手动启用
- **代码质量**：代码规范良好，使用现代 C++ 特性（`[[nodiscard]]`），注释完整
- **风险提示**：作为实验性插件，API 可能在未来版本中发生变化
- **推荐**：适合用于原型开发和快速验证。生产环境使用需谨慎，建议关注版本更新中的 API 变化

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Web/HttpBlueprint)
- [官方文档]()（暂无）