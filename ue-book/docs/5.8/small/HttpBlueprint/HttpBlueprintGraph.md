# Http Blueprint

> Allows for sending and receiving HTTP requests in Blueprint

| 属性 | 值 |
|---|---|
| 中文名 | 蓝图HTTP请求 |
| 分类 | Web |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `HttpBlueprint` (Runtime), `HttpBlueprintGraph` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-03-15 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Web/HttpBlueprint) | |

## 用途

此插件通过提供蓝图友好的异步节点，解决了蓝图用户无法直接进行网络 HTTP 通信的问题。它封装了底层的 `FHttpModule`，允许开发者在蓝图中轻松发送 GET、POST、PUT、DELETE 等 HTTP 请求，并异步处理响应数据，而无需编写 C++ 代码。它特别提供了预设头部（如 JSON、HTML）的功能，简化了常见的 API 调用配置。

## 使用场景

- 你需要在蓝图中从 Web API 获取数据（如游戏配置、排行榜）。
- 你需要向服务器发送玩家统计数据或游戏事件。
- 你需要与基于 REST 的 Web 服务进行交互，但不想编写 C++ 网络代码。
- 你希望使用预设的 HTTP 头部（如 `application/json`）来简化 API 请求的设置。

## 蓝图用法

插件提供了几个核心的蓝图节点来构造和发送 HTTP 请求。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `HttpRequest` | 发起一个 HTTP 请求的核心异步节点，可指定动词（GET/POST等）、URL、头部和请求体。 | `UK2Node_HttpRequest` |
| `Make Request Header` | 用于手动构建一个 HTTP 头部（键值对集合）的节点，支持添加多个键值对。 | `UK2Node_MakeRequestHeader` |
| `Async Make Request Header` | 异步版本的头部构建节点，可能用于更复杂的头部生成逻辑。 | `UK2Node_AsyncMakeRequestHeader` |
| JSON/HTML/URL 预设 | 在 `Make Request Header` 节点中，可选择预置方案（如 JSON），自动生成对应的 Accept 和 Content-Type 头部。 | `UK2Node_MakeRequestHeader` |

### 使用示例（蓝图描述）

**示例1：发送一个简单的 GET 请求**
1. 从蓝图添加 `HttpRequest` 节点。
2. 在 `Verb` 引脚选择 “GET”。
3. 将 URL 字符串连接到 `URL` 引脚。
4. 连接 `Success` 和 `Error` 执行引脚到后续逻辑。`Out Body` 引脚将返回响应体。

**示例2：发送带 JSON 头部的 POST 请求**
1. 使用 `Make Request Header` 节点，从预设下拉菜单中选择 “Json”。
2. 将其输出连接到 `HttpRequest` 节点的 `Header` 引脚。
3. 设置 `Verb` 为 “POST”。
4. 将你的 JSON 字符串连接到 `Body` 引脚。
5. 连接其他必要引脚。

## C++ 用法

虽然插件主要面向蓝图，但其底层结构（如 `FOptionalPin`、`FBasePreset`）和自定义 `K2Node` 的实现方式，对于需要扩展或理解其工作原理的 C++ 开发者很有参考价值。

### 头文件引入

```cpp
// 了解请求头预设结构
#include "HttpRequestHeaderPresets.h"

// 了解自定义K2Node的实现模式（若需创建类似节点）
#include "K2Node_MakeRequestHeader.h"
```

### 基本用法

从提供的代码片段中，我们可以看到 HTTP 请求头是如何被预设和使用的。
**来源：** `Private/HttpRequestHeaderPresets.h`

```cpp
// 创建一个包含标准头部的 JSON 请求头实例
UE::HttpBlueprint::HeaderPresets::FJsonPreset JsonHeaderPreset;

// 获取预设的头部Map，可用于初始化 FHttpRequestHeader
TMap<FString, FString>& Headers = JsonHeaderPreset.HeaderPresets;
// Headers 现在包含:
// {"Accept-Encoding": "identity", "User-Agent": "X-UnrealEngine-Agent", "Accepts": "application/json", "Content-Type": "application/json"}

// 你可以在此基础上继续添加或修改自定义头部
Headers.Add(TEXT("X-Custom-Header"), TEXT("MyValue"));
```

### 进阶用法

插件的核心是 `UK2Node_HttpRequest` 这类自定义蓝图节点。了解其结构有助于扩展或调试。
**来源：** `Private/K2Node_HttpRequest.h`

```cpp
// UK2Node_HttpRequest 在编译蓝图时会展开为实际的 HTTP 调用逻辑。
// 其关键引脚包括：Verb, URL, Header, Body, Success, Error, Out Body, Out Header。
// 通过重写 ExpandNode，它将这些高层引脚连接到引擎内置的异步 HTTP 功能上。

// 在开发类似功能的自定义 K2Node 时，可以参考其模式：
// 1. 在 AllocateDefaultPins 中创建输入输出引脚。
// 2. 在 ExpandNode 中，使用 FBlueprintCompiledStatement 和 FKismetCompilerContext 将节点逻辑替换为更底层的蓝图节点序列。
```

## Demo 示例

这是一个最小的 C++ 示例，展示如何在代码中构造一个使用预设头部的 HTTP 请求。此示例不直接调用插件的蓝图节点，而是使用其底层的预设结构。

**MyHttpDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "HttpRequestHeaderPresets.h"
#include "HttpModule.h"
#include "Interfaces/IHttpRequest.h"
#include "MyHttpDemo.generated.h"

UCLASS(Blueprintable)
class UMyHttpDemo : public UObject
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "Demo")
    void SendJsonPostRequest(const FString& URL, const FString& JsonBody);
};
```

**MyHttpDemo.cpp**
```cpp
#include "MyHttpDemo.h"
#include "Interfaces/IHttpResponse.h"

void UMyHttpDemo::SendJsonPostRequest(const FString& URL, const FString& JsonBody)
{
    // 1. 获取预设的JSON头部
    UE::HttpBlueprint::HeaderPresets::FJsonPreset JsonPreset;
    const TMap<FString, FString>& PresetHeaders = JsonPreset.HeaderPresets;

    // 2. 创建HTTP请求
    TSharedRef<IHttpRequest, ESPMode::ThreadSafe> HttpRequest = FHttpModule::Get().CreateRequest();
    HttpRequest->SetURL(URL);
    HttpRequest->SetVerb(TEXT("POST"));
    HttpRequest->SetContentAsString(JsonBody);

    // 3. 应用预设头部
    for (const TPair<FString, FString>& Header : PresetHeaders)
    {
        HttpRequest->SetHeader(Header.Key, Header.Value);
    }

    // 4. 设置完成回调
    HttpRequest->OnProcessRequestComplete().BindLambda(
        [](FHttpRequestPtr Request, FHttpResponsePtr Response, bool bWasSuccessful)
        {
            if (bWasSuccessful && Response.IsValid())
            {
                UE_LOG(LogTemp, Log, TEXT("Request Success. Response Code: %d"), Response->GetResponseCode());
                UE_LOG(LogTemp, Log, TEXT("Response Body: %s"), *Response->GetContentAsString());
            }
            else
            {
                UE_LOG(LogTemp, Error, TEXT("Request Failed"));
            }
        }
    );

    // 5. 发送请求
    HttpRequest->ProcessRequest();
}
```

## 模块依赖

从 `HttpBlueprintGraph` 模块的 `Build.cs` 分析，以下是使用者需要注意的独特依赖：

| 模块 | 用途 |
|---|---|
| `JsonUtilities` | 插件依赖此插件（见 .uplugin），用于处理 JSON 数据的序列化与反序列化，是发送和接收 JSON 请求体的基础。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移到新的UE_LOGF格式。 |
| 2025-05-28 | `7e9f0fe3` | Fix blueprint compilation crash due to mismatching pin names | 修复了因引脚名称不匹配导致的蓝图编译崩溃问题。 |
| 2025-05-22 | `275c11fa` | #JIRA UE-273929 | 针对特定JIRA问题的修复或改进。 |
| 2024-08-23 | `64ae24ec` | Removed extraneous GetSelfPin implementations. | 移除了多余的 GetSelfPin 函数实现，进行了代码清理。 |
| 2024-01-12 | `7da84c1d` | Replaced UE_NODISCARD with [[nodiscard]]. | 使用 C++ 标准属性 `[[nodiscard]]` 替换了 UE 的宏。 |

### 维护评价

- **创建时间**：约3年前（2022年）。
- **最近更新**：近期（2025、2026年）仍有活跃提交，主要是 Bug 修复和代码现代化。
- **维护状态**：**实验性但仍在维护中**。虽然标记为 `IsExperimentalVersion=true` 且 `EnabledByDefault=false`，但 Epic 持续修复关键问题（如崩溃），表明其仍在积极开发中。
- **已知问题/限制**：作为实验性功能，其 API 稳定性可能不如正式功能。需要手动启用插件。
- **推荐使用**：**适用于原型开发或对实验性功能接受度高的项目**。如果你的项目需要稳定且完整的 HTTP 蓝图功能，建议关注其后续版本或考虑社区方案。对于快速验证想法，这是一个非常有用的工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Web/HttpBlueprint)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Web/HttpBlueprint/Tests) (路径待确认，建议在源码仓库中搜索)