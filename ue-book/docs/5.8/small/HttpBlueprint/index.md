# HttpBlueprint

> Allows for sending and receiving HTTP requests in Blueprint

| 属性 | 值 |
|---|---|
| 中文名 | 蓝图HTTP |
| 分类 | Web |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图节点、K2节点） |
| 模块 | `HttpBlueprint` (Runtime), `HttpBlueprintGraph` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-03-15 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Web/HttpBlueprint) | |

## 用途

HttpBlueprint 插件将 Unreal Engine 底层的 `FHttpModule` 和 `IHttpRequest` 等 C++ HTTP 网络功能，封装成一系列可在蓝图中直接使用的节点。其核心目的是让设计师和游戏逻辑程序员无需编写 C++ 代码，即可在蓝图图表中轻松实现 HTTP 请求的发送、数据组装、响应接收和解析。这解决了蓝图中原生缺乏易用 HTTP 通信能力的痛点，特别适用于需要与后端服务器或外部 API 进行交互的场景。

## 使用场景

- 你需要在蓝图中调用 RESTful API 来获取或提交游戏数据（如玩家存档、排行榜）。
- 游戏逻辑需要根据实时从服务器获取的配置进行动态调整。
- 你正在快速原型验证一个需要网络请求的功能，希望先用蓝图实现。

## 蓝图用法

该插件的核心是提供一组蓝图节点来构建和管理 HTTP 请求。以下是主要功能分组：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create HTTP Request` | 创建一个新的 HTTP 请求对象。 | `UK2Node_MakeHttpRequest` |
| `Set Request Method` | 为请求设置方法（GET, POST, PUT, DELETE 等）。 | （封装在流程中） |
| `Set Request Header` | 为请求添加或设置 HTTP 头（如 Content-Type, Authorization）。 | （封装在流程中） |
| `Set Request Body (String)` | 设置请求体内容（适用于 JSON、XML 等文本数据）。 | （封装在流程中） |
| `Process HTTP Request` | 异步发送已配置好的请求，并输出请求句柄。 | `UK2Node_MakeHttpRequest` |
| `HTTP Request Complete` | 事件节点，当 HTTP 请求完成（成功或失败）时触发，提供响应状态码、头和体。 | `UK2Node_HttpRequestOnComplete` |

### 使用示例

1.  使用 `Create HTTP Request` 节点创建请求。
2.  将其连接到 `Set Request Method` (例如设置为 `GET`) 和 `Set Request Header` (例如 `Content-Type: application/json`)。
3.  对于 POST/PUT 请求，使用 `Set Request Body (String)` 提供 JSON 字符串。
4.  使用 `Process HTTP Request` 发送请求，并将返回的 `Future` 或句柄连接到 `HTTP Request Complete` 事件的相应输入引脚。
5.  在 `HTTP Request Complete` 事件中，根据 `Status Code` 判断成功与否，并解析 `Response Body`。

## C++ 用法

在 C++ 中，你可以直接使用本插件封装的类，这些类提供了与蓝图节点等效的面向对象接口。

### 头文件引入

```cpp
#include "HttpBlueprint/Classes/HttpBlueprintTypes.h"
#include "HttpBlueprint/Classes/HttpBlueprintRequest.h"
#include "HttpBlueprint/Classes/HttpBlueprintResponse.h"
```

### 基本用法

这是一个简单的 GET 请求示例，模拟蓝图中的 `Process HTTP Request` 和 `HTTP Request Complete` 流程。
（来源：基于 `HttpBlueprint` 模块公共头文件推断的典型用法）

```cpp
// 1. 创建一个请求对象
UHttpBlueprintRequest* MyRequest = NewObject<UHttpBlueprintRequest>();

// 2. 配置请求
MyRequest->SetVerb(EBPHttpVerb::GET);
MyRequest->SetURL(TEXT("https://api.example.com/data"));
MyRequest->SetHeader(TEXT("Accept"), TEXT("application/json"));

// 3. 绑定完成回调
MyRequest->OnRequestCompleted().AddLambda(
    [](int32 StatusCode, const FString& ResponseContent, bool bWasSuccessful) {
        if (bWasSuccessful && StatusCode == EHttpResponseCodes::Ok) {
            // 成功处理响应内容
            UE_LOG(LogTemp, Log, TEXT("Response: %s"), *ResponseContent);
        } else {
            // 处理错误
            UE_LOG(LogTemp, Error, TEXT("Request failed: %d"), StatusCode);
        }
    }
);

// 4. 发送请求（异步）
MyRequest->ProcessRequest();
```

### 进阶用法

结合 `JsonBlueprintUtilities` 插件处理 JSON 数据的典型模式：
（来源：根据插件依赖关系推断的常见组合用法）

```cpp
// 假设要发送一个包含 JSON 数据的 POST 请求
UHttpBlueprintRequest* PostRequest = NewObject<UHttpBlueprintRequest>();
PostRequest->SetVerb(EBPHttpVerb::POST);
PostRequest->SetURL(TEXT("https://api.example.com/users"));
PostRequest->SetHeader(TEXT("Content-Type"), TEXT("application/json"));

// 构造一个 JSON 对象
TSharedPtr<FJsonObject> JsonObject = MakeShareable(new FJsonObject);
JsonObject->SetStringField(TEXT("name"), TEXT("Player1"));
JsonObject->SetNumberField(TEXT("score"), 95);

// 将 JSON 对象序列化为字符串
FString JsonString;
TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&JsonString);
FJsonSerializer::Serialize(JsonObject.ToSharedRef(), Writer);
PostRequest->SetBody(JsonString);

// 发送并处理（同上例）
PostRequest->OnRequestCompleted().AddLambda(/* ... */);
PostRequest->ProcessRequest();
```

## Demo 示例

一个可编译的最小 C++ 类，演示如何使用 HttpBlueprint 进行请求。

**HttpBlueprintDemo.h**
```cpp
// Fill out your copyright notice in the Description page of Project Settings.
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "HttpBlueprintDemo.generated.h"

UCLASS()
class AHttpBlueprintDemo : public AActor
{
    GENERATED_BODY()
public:
    AHttpBlueprintDemo();

    UFUNCTION(BlueprintCallable, Category = "HTTP Demo")
    void MakeSimpleGetRequest();

private:
    UPROPERTY()
    class UHttpBlueprintRequest* CurrentRequest;

    void OnRequestCompleted(int32 StatusCode, const FString& Content, bool bSuccess);
};
```

**HttpBlueprintDemo.cpp**
```cpp
#include "HttpBlueprintDemo.h"
#include "HttpBlueprint/Classes/HttpBlueprintRequest.h"

AHttpBlueprintDemo::AHttpBlueprintDemo()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AHttpBlueprintDemo::MakeSimpleGetRequest()
{
    if (CurrentRequest)
    {
        CurrentRequest->CancelRequest();
        CurrentRequest->ConditionalBeginDestroy();
    }

    CurrentRequest = NewObject<UHttpBlueprintRequest>(this);
    CurrentRequest->SetVerb(EBPHttpVerb::GET);
    CurrentRequest->SetURL(TEXT("https://httpbin.org/get"));

    CurrentRequest->OnRequestCompleted().AddUObject(this, &AHttpBlueprintDemo::OnRequestCompleted);
    CurrentRequest->ProcessRequest();
}

void AHttpBlueprintDemo::OnRequestCompleted(int32 StatusCode, const FString& Content, bool bSuccess)
{
    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("HTTP Request Succeeded! Status: %d\nBody: %s"), StatusCode, *Content);
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("HTTP Request Failed! Status: %d"), StatusCode);
    }
    CurrentRequest = nullptr;
}
```

## 模块依赖

使用者的模块需要依赖以下核心模块：
| 模块 | 用途 |
|---|---|
| `Http` | 提供底层的 HTTP 请求和网络接口实现，是本插件功能的基础。 |
| `Json` | 用于在 C++ 和蓝图中解析和生成 JSON 数据，与 HTTP 请求体协同工作。 |
| `JsonUtilities` | 提供高级的 JSON 对象序列化/反序列化辅助函数。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF，属于引擎日志系统适配性更新。 |
| 2025-05-28 | `7e9f0fe3` | Fix blueprint compilation crash due to mismatching pin names | 修复了因节点引脚名称不匹配导致的蓝图编译崩溃问题。 |
| 2025-05-22 | `275c11fa` | #JIRA UE-273929 | 关联的特定 JIRA 任务修复，具体改动未知。 |
| 2024-08-23 | `64ae24ec` | Removed extraneous GetSelfPin implementations. | 移除了多余的 `GetSelfPin` 实现，属于代码清理优化。 |
| 2024-01-12 | `7da84c1d` | Replaced UE_NODISCARD with [[nodiscard]]. | 使用标准 C++ 属性替换了引擎特定的宏。 |

### 维护评价

该插件创建于 2022 年 3 月，至今约 4 年。从提交历史看，它仍然在维护中，最近一次更新在 2026 年 4 月，主要目的是适配引擎宏的更新。2025 年 5 月有关键的 bug 修复，解决了蓝图编译崩溃问题，证明其仍在被使用和关注。

**评价**：这是一个处于**实验性 (Experimental)** 状态的插件，且默认未启用。尽管年龄不长，但它有实质性更新记录，特别是最近的崩溃修复表明 Epic 可能在内部或特定场景下使用或测试它。对于项目中**确实需要蓝图化 HTTP 功能的场景**，可以谨慎启用和使用，但需意识到其“实验性”标签可能意味着 API 未来可能变动或存在未发现的限制。对于新项目，如果非必需，建议评估成熟度后再引入。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Web/HttpBlueprint)
- [官方文档]()
- [测试用例]() (待补充)