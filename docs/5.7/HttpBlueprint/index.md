# HttpBlueprint

> Allows for sending and receiving HTTP requests in Blueprint

| 属性 | 值 |
|---|---|
| 分类 | Web |
| 默认启用 | false |
| 包含内容 | true |
| 模块 | HttpBlueprint (Runtime), HttpBlueprintGraph (UncookedOnly) |
| 创建时间 | 2022-03-14 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Web/HttpBlueprint) | |

## 用途

HttpBlueprint 是 Epic 官方提供的**纯蓝图 HTTP 请求插件**。它将 UE 的 `HTTP` 模块封装为自定义 K2 蓝图节点，让开发者无需编写 C++ 代码即可在蓝图中发起 HTTP/REST 请求并处理响应。

该插件的核心价值在于：

1. **一体化蓝图节点** — 一个 `Http Request` 节点同时处理请求发送、成功/失败分支和响应解析，比传统的 `Http Request` + `Process Request` + `On Complete` 多节点流程更简洁
2. **内置 Header 预设** — 提供 Json / Http / Url Encoded / Custom 四种预设，自动填充 `Content-Type`、`Accept-Encoding` 等常用请求头
3. **与 JsonBlueprintUtilities 联动** — 响应体（Wildcard 类型）可直接连接 JSON 解析节点

⚠️ **注意**：该插件标记为 `IsExperimentalVersion: true`，`EnabledByDefault: false`，需要在项目设置中手动启用。

## 使用场景

- 你在蓝图中需要调用 REST API（如获取排行榜数据、提交玩家成绩）
- 你需要向后端服务器发送 JSON 请求并解析响应
- 你想在不写 C++ 的情况下完成 HTTP 通信
- 你需要快速原型验证某个 API 的集成

## 蓝图用法

### 核心节点

| 节点 | 类型 | 说明 | 所在类 |
|---|---|---|---|
| `Http Request` | 异步执行节点 | 发送 HTTP 请求，提供成功/失败双分支输出 | `UHttpRequestProxyObject` |
| `Make Request Header` | 纯函数节点 | 创建带预设的 HTTP Header（支持动态增删 Key/Value 对） | `UK2Node_MakeRequestHeader` |
| `Async Make Request Header` | 异步节点 | 异步版本的 Header 构建节点 | `UK2Node_AsyncMakeRequestHeader` |

### Http Request 节点详解

这是插件的核心节点，节点标题会根据所选 Verb 动态变化（如 "Http Post Request"、"Http Get Request"）。

**输入引脚：**

| 引脚 | 类型 | 说明 |
|---|---|---|
| Execute | Exec | 触发请求 |
| Url | String | 请求的 URL 地址 |
| Verb | EHttpVerbs | HTTP 方法：Post / Put / Delete / Patch / Get |
| Header | FHttpHeader | 由 Make Request Header 创建的请求头结构体 |
| Body | String/Wildcard | 请求体（**仅 Post / Put / Delete / Patch 显示**，Get 不显示） |

**输出引脚：**

| 引脚 | 类型 | 说明 |
|---|---|---|
| Request Processing | Exec | 请求发出后立即触发（不等待响应） |
| On Success | Exec | 请求成功时触发 |
| On Error | Exec | 请求失败时触发 |
| Result Body | Wildcard | 响应内容（成功时为响应体，失败时为错误信息） |
| OutHeader | FHttpHeader | 原样返回传入的 Header（可用于链式操作） |

> **重要**：Body 引脚的类型是 Wildcard，会自动与连接的目标引脚同步类型。连接 String 时传递文本，连接 JSON Object 时传递 JSON 对象。

### EHttpVerbs 枚举

| 值 | 说明 |
|---|---|
| Post (0) | 创建资源，显示 Body 引脚 |
| Put (1) | 更新资源，显示 Body 引脚 |
| Delete (2) | 删除资源，显示 Body 引脚 |
| Patch (3) | 部分更新资源，显示 Body 引脚 |
| Get (4) | 获取资源，**不显示** Body 引脚 |

### Make Request Header 节点详解

这是一个纯函数节点（无执行引脚），用于构建 `FHttpHeader` 结构体。

**预设模式（ERequestPresets）：**

| 预设 | Content-Type | Accept |
|---|---|---|
| Json Request | `application/json` | `application/json` |
| Http Request | `text/html` | `text/html` |
| Url Encoded Request | `application/x-www-form-urlencoded` | `application/x-www-form-urlencoded` |
| Custom Request | 无自动填充 | 无自动填充 |

所有预设都会自动添加：
- `Accept-Encoding: identity`
- `User-Agent: X-UnrealEngine-Agent`

节点支持通过右键菜单 **Add Pin / Remove Pin** 动态增删 Key/Value 输入对。

### Header 操作函数（UHttpBlueprintFunctionLibrary）

| 函数 | 说明 | 纯函数 |
|---|---|---|
| `GetHeaderValue` | 根据 Header 名获取对应值 | ✅ |
| `GetAllHeaders` | 获取所有 Header 为字符串数组 | ✅ |
| `GetAllHeadersAsMap` | 获取所有 Header 为 Map | ✅ |
| `AddHeader` | 添加一个 Header 键值对 | ❌ |
| `RemoveHeader` | 移除一个 Header | ❌ |

### 使用示例（蓝图描述）

**示例 1：发送 GET 请求并解析 JSON 响应**

1. 创建一个 Event 节点（如 BeginPlay 或自定义事件）
2. 从 Exec 引脚拖出，放置 `Make Request Header` 节点，选择 **Json Request** 预设
3. 放置 `Http Request` 节点
4. 连接：`Make Request Header` 的输出 → `Http Request` 的 Header 引脚
5. 设置 Url 引脚为 `"https://api.example.com/data"`
6. Verb 引脚选择 **Get**
7. 从 `Http Request` 的 **On Success** Exec 引脚拖出，连接后续逻辑
8. 将 **Result Body** 引脚连接到 JSON 解析节点

**示例 2：发送 POST 请求提交 JSON 数据**

1. 放置 `Make Request Header` 节点，选择 **Json Request** 预设
2. 放置 `Http Request` 节点，Verb 设为 **Post**
3. 将 Header 输出连接到 `Http Request` 的 Header 引脚
4. 将 Body 引脚连接一个包含 JSON 字符串的变量（如 `"{\"name\":\"player1\",\"score\":100}"`）
5. 设置 Url 为你的 API 端点
6. 从 **On Success** 和 **On Error** 分别连接不同的后续逻辑

**示例 3：自定义 Header 并发送请求**

1. 放置 `Make Request Header` 节点，选择 **Custom Request** 预设
2. 在 Key/Value 输入对中填入自定义头，如 `Authorization` / `Bearer your-token-here`
3. 可通过右键节点 → Add Pin 添加更多自定义头
4. 连接到 `Http Request` 节点的 Header 引脚

## C++ 用法

### 头文件引入

```cpp
#include "HttpBlueprintTypes.h"       // EHttpVerbs, ERequestPresets
#include "HttpHeader.h"               // FHttpHeader
#include "HttpBlueprintFunctionLibrary.h" // 工具函数
#include "HttpRequestProxyObject.h"   // HTTP 请求代理（Internal 头文件）
```

### 基本用法

```cpp
// 创建 Header
FHttpHeader Header;
Header.AddHeader(TPair<FString, FString>(TEXT("Content-Type"), TEXT("application/json")));
Header.AddHeader(TPair<FString, FString>(TEXT("Authorization"), TEXT("Bearer my-token")));

// 通过 FHttpModule 直接发送请求（与 HttpBlueprint 底层逻辑一致）
FHttpModule& HttpModule = FHttpModule::Get();
TSharedRef<IHttpRequest> Request = HttpModule.CreateRequest();
Request->SetURL(TEXT("https://api.example.com/data"));
Request->SetVerb(TEXT("POST"));
Request->SetContentAsString(TEXT("{\"key\":\"value\"}"));
Header.AssignHeadersToRequest(Request);
Request->ProcessRequest();
Request->OnProcessRequestComplete().BindLambda(
    [](FHttpRequestPtr InRequest, FHttpResponsePtr InResponse, bool bSuccess)
    {
        if (bSuccess && InResponse.IsValid())
        {
            FString ResponseBody = InResponse->GetContentAsString();
            // 处理响应...
        }
    }
);
```

### 进阶用法

```cpp
// 使用 UHttpBlueprintFunctionLibrary 操作 Header
FHttpHeader Header;

// 通过函数库添加 Header（蓝图和 C++ 均可调用）
UHttpBlueprintFunctionLibrary::AddHeader(Header, TEXT("Accept"), TEXT("application/json"));
UHttpBlueprintFunctionLibrary::AddHeader(Header, TEXT("Content-Type"), TEXT("application/json"));

// 查询 Header
FString Value;
bool bFound = UHttpBlueprintFunctionLibrary::GetHeaderValue(Header, TEXT("Accept"), Value);
// bFound == true, Value == "application/json"

// 获取所有 Header
TArray<FString> AllHeaders = UHttpBlueprintFunctionLibrary::GetAllHeaders(Header);
// 返回格式: ["Accept: application/json", "Content-Type: application/json"]

// 以 Map 形式获取
TMap<FString, FString> HeaderMap = UHttpBlueprintFunctionLibrary::GetAllHeaders_Map(Header);

// 移除 Header
UHttpBlueprintFunctionLibrary::RemoveHeader(Header, TEXT("Accept"));
```

## Demo 示例

以下是一个最小的 HTTP GET 请求示例，包含 .h 和 .cpp 文件。

### MyHttpActor.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "HttpHeader.h"
#include "MyHttpActor.generated.h"

UCLASS()
class AMyHttpActor : public AActor
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "HTTP")
    void FetchData(const FString& Url);

private:
    void OnResponse(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bSuccess);
};
```

### MyHttpActor.cpp

```cpp
#include "MyHttpActor.h"
#include "HttpBlueprintFunctionLibrary.h"
#include "HttpModule.h"
#include "Interfaces/IHttpResponse.h"

void AMyHttpActor::FetchData(const FString& Url)
{
    FHttpHeader Header;
    UHttpBlueprintFunctionLibrary::AddHeader(Header, TEXT("Accept"), TEXT("application/json"));

    FHttpModule& HttpModule = FHttpModule::Get();
    TSharedRef<IHttpRequest> Request = HttpModule.CreateRequest();
    Request->SetURL(Url);
    Request->SetVerb(TEXT("GET"));
    Header.AssignHeadersToRequest(Request);
    Request->OnProcessRequestComplete().BindUObject(this, &AMyHttpActor::OnResponse);
    Request->ProcessRequest();
}

void AMyHttpActor::OnResponse(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bSuccess)
{
    if (bSuccess && Response.IsValid())
    {
        UE_LOG(LogTemp, Log, TEXT("Response: %s"), *Response->GetContentAsString());
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Request failed"));
    }
}
```

### Build.cs 依赖

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "HttpBlueprint"  // 需要引用 HttpBlueprint 模块
});
```

## 模块依赖

### HttpBlueprint 模块（Runtime）

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心功能 |
| `HTTP` | 底层 HTTP 请求实现（Private） |

### HttpBlueprintGraph 模块（UncookedOnly）

| 模块 | 用途 |
|---|---|
| `BlueprintGraph` | 蓝图节点图系统 |
| `Kismet` | 蓝图编辑器核心 |
| `KismetCompiler` | 蓝图编译器 |
| `JsonBlueprintUtilities` | JSON 蓝图工具（插件依赖） |
| `GraphEditor` | 图形编辑器 UI |

> **使用者须知**：如果你只是在蓝图中使用 Http Request 节点，不需要额外配置 C++ 依赖——只需在项目设置中启用插件即可。只有在 C++ 中调用 `FHttpHeader` 或 `UHttpBlueprintFunctionLibrary` 时，才需要在 Build.cs 中添加 `HttpBlueprint` 依赖。

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-05-28 | `7e9f0fe3` | Fix blueprint compilation crash due to mismatching pin names | 修复蓝图编译时因引脚名称不匹配导致的崩溃，属于稳定性修复 |
| 2025-05-22 | `275c11fa` | [HttpBlueprint] Update HttpRequestProxyObject.cpp to fix crash on connection error | 修复 HTTP 连接错误时的崩溃（JIRA UE-273929），解决了网络异常场景下的稳定性问题 |
| 2024-08-23 | `64ae24ec` | Removed extraneous GetSelfPin implementations | 清理冗余的 GetSelfPin 实现，代码重构 |

### 维护评价

- **创建时间**：2022-03-14，约 4 年历史
- **实验性状态**：`IsExperimentalVersion: true`，`EnabledByDefault: false` — 仍处于实验阶段
- **活跃程度**：最近两次更新在 2025 年 5 月，均为关键的崩溃修复，说明 Epic 仍在维护
- **已知限制**：
  - 实验性插件，API 可能在未来版本中发生变化
  - Body 引脚仅在 Post/Put/Delete/Patch 时显示（Get 请求无 Body）
  - 没有内置的超时配置、重试机制或请求取消功能
  - 没有官方文档（DocsURL 为空）
- **推荐**：适合原型开发和简单场景。生产环境建议评估是否直接使用 `FHttpModule` / `FHttp` 以获得更多控制权

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Web/HttpBlueprint)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- [JsonBlueprintUtilities 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/JsonBlueprintUtilities) — HttpBlueprint 的插件依赖
