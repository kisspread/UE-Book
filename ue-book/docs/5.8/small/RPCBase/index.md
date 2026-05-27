# Remote Procedure Calls Base

> RPC base framework that client applications can use to implement RPC libraries.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 远程过程调用基座 |
| 分类 | Runtime |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RPCBase` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2026-02-18 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/RPCBase) | |

## 用途

RPCBase 是一个用于构建自定义 HTTP 远程过程调用 (RPC) 服务的**基础框架**。它并非提供具体的 RPC 实现，而是提供一个基类 (`URPCLibraryBase`) 和基础模块，供客户端应用程序（如内部工具、编辑器扩展或独立服务）**继承和扩展**，以实现符合自己业务逻辑的 RPC 库。

该插件的核心价值在于：
1.  **标准化流程**：封装了基于 HTTP 的 RPC 端点注册、请求处理和响应创建的通用流程。
2.  **与引擎集成**：依赖于 `ExternalRpcRegistry` 模块，使得注册的 RPC 端点能被引擎的 HTTP 服务发现和调用。
3.  **简化开发**：开发者无需从零开始处理 HTTP 请求解析、JSON 序列化/反序列化、路由注册等底层细节，只需专注于业务逻辑。

## 使用场景

-   **开发内部工具或调试接口**：为你的游戏项目创建一套 HTTP API，用于查询游戏状态、修改运行时参数或触发特定事件。
-   **构建编辑器扩展的通信后端**：为自定义的编辑器工具或面板提供与编辑器会话通信的 HTTP 端点。
-   **实现自定义的 RPC 微服务**：作为更大系统中的一个组件，处理特定的、轻量级的远程调用请求。

## 蓝图用法

`URPCLibraryBase` 中所有标记为 `BlueprintCallable` 的函数都位于 `#if WITH_RPC_REGISTRY` 预编译宏保护下，因此只有在启用相关模块时才可用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RegisterRPC` | 注册一个新的 RPC 端点。需指定路由名、HTTP 路径、请求方法 (GET/POST等) 和处理函数。 | `URPCLibraryBase` |
| `StartListening` | 在初始化并注册所有端点后调用，启动 RPC 服务监听。 | `URPCLibraryBase` |
| `CreateSimpleResponse` | 辅助函数，用于快速创建一个包含成功/失败状态和可选值的简单 HTTP 响应。 | `URPCLibraryBase` |
| `DeserializeRequest` | 辅助函数，用于将 HTTP 请求体反序列化为 JSON 对象。 | `URPCLibraryBase` |
| `GetStringField` | 辅助函数，用于从 JSON 对象中安全地提取字符串字段。 | `URPCLibraryBase` |

### 使用示例（蓝图描述）

1.  创建一个新的蓝图类，选择 `URPCLibraryBase` 作为父类。
2.  在蓝图的 `BeginPlay` 事件中（或一个自定义的初始化函数），调用 `Initialize`。
3.  使用 `RegisterRPC` 节点注册你自己的 RPC 端点。例如，注册一个名为 `GetPlayerStatus` 的 GET 请求到路径 `/myapi/playerstatus`，并将其处理函数连接到一个自定义事件。
4.  在所有端点注册完毕后，调用 `StartListening`。
5.  在 `GetPlayerStatus` 的自定义事件中，使用 `CreateSimpleResponse` 节点构建并返回响应。

## C++ 用法

### 头文件引入

```cpp
#include "RPCBaseModule.h"
#include "RPCLibraryBase.h"
```

### 基本用法

创建一个 `URPCLibraryBase` 的子类来实现你自己的 RPC 库。

```cpp
// MyCustomRPCLibrary.h
#pragma once
#include "RPCLibraryBase.h"
#include "MyCustomRPCLibrary.generated.h"

UCLASS()
class UMyCustomRPCLibrary : public URPCLibraryBase
{
    GENERATED_BODY()

public:
    UMyCustomRPCLibrary();
    void RegisterRPCs();
};
```

```cpp
// MyCustomRPCLibrary.cpp
#include "MyCustomRPCLibrary.h"
#include "HttpServerModule.h"
#include "HttpServerRequest.h"
#include "HttpResultCallback.h"

UMyCustomRPCLibrary::UMyCustomRPCLibrary()
{
    // 基类构造函数中会调用 Initialize
}

void UMyCustomRPCLibrary::RegisterRPCs()
{
#if WITH_RPC_REGISTRY
    // 注册一个 GET 端点
    RegisterRPC(
        FName(TEXT("GetHelloWorld")),
        FHttpPath(TEXT("/customrpc/hello")),
        EHttpServerRequestVerbs::VERB_GET,
        FHttpRequestHandler::CreateLambda(
            [this](const FHttpServerRequest& Request, const FHttpResultCallback& OnComplete)
            {
                // 处理请求，构建响应
                TUniquePtr<FHttpServerResponse> Response = CreateSimpleResponse(true, TEXT("Hello from Custom RPC!"));
                OnComplete(MoveTemp(Response));
                return true;
            })
    );
    // 注册一个 POST 端点
    RegisterRPC(
        FName(TEXT("PostEcho")),
        FHttpPath(TEXT("/customrpc/echo")),
        EHttpServerRequestVerbs::VERB_POST,
        FHttpRequestHandler::CreateLambda(
            [this](const FHttpServerRequest& Request, const FHttpResultCallback& OnComplete)
            {
                // 反序列化请求体
                TSharedPtr<FJsonObject> JsonObject;
                TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Request.Body);
                if (DeserializeRequest(JsonObject, Reader, /*JsonWriter - 可传入现有或临时的*/))
                {
                    // 从 JSON 中提取数据
                    FString Message;
                    if (GetStringField(JsonObject, TEXT("message"), Message, /*JsonWriter*/))
                    {
                        // 回显消息
                        TUniquePtr<FHttpServerResponse> Response = CreateSimpleResponse(true, Message);
                        OnComplete(MoveTemp(Response));
                    }
                }
                return true;
            })
    );
#endif
}
```

### 进阶用法

可以在一个管理类中实例化并运行你的自定义 RPC 库。

```cpp
// RPCManager.h
UCLASS()
class URPCManager : public UObject
{
    GENERATED_BODY()
public:
    void StartServices();
private:
    UPROPERTY()
    TObjectPtr<UMyCustomRPCLibrary> MyRPCLibrary;
};
```

```cpp
// RPCManager.cpp
void URPCManager::StartServices()
{
    MyRPCLibrary = NewObject<UMyCustomRPCLibrary>();
    MyRPCLibrary->RegisterRPCs();
    MyRPCLibrary->StartListening();
    UE_LOG(LogTemp, Log, TEXT("Custom RPC Service Started."));
}
```

## Demo 示例

一个最小的可运行自定义 RPC 库实现。

```cpp
// DemoRPCLibrary.h
#pragma once
#include "RPCLibraryBase.h"
#include "DemoRPCLibrary.generated.h"

UCLASS()
class UDemoRPCLibrary : public URPCLibraryBase
{
    GENERATED_BODY()
public:
    UDemoRPCLibrary();
    /** 注册所有演示用的 RPC 端点。 */
    void SetupEndpoints();
};
```

```cpp
// DemoRPCLibrary.cpp
#include "DemoRPCLibrary.h"

UDemoRPCLibrary::UDemoRPCLibrary()
{
    // 构造函数中可进行简单初始化
}

void UDemoRPCLibrary::SetupEndpoints()
{
#if WITH_RPC_REGISTRY
    // 端点 1: GET /demo/ping
    RegisterRPC(
        FName("DemoPing"),
        FHttpPath("/demo/ping"),
        EHttpServerRequestVerbs::VERB_GET,
        FHttpRequestHandler::CreateUObject(this, &UDemoRPCLibrary::HandlePingRequest)
    );

    // 端点 2: POST /demo/echo
    RegisterRPC(
        FName("DemoEcho"),
        FHttpPath("/demo/echo"),
        EHttpServerRequestVerbs::VERB_POST,
        FHttpRequestHandler::CreateUObject(this, &UDemoRPCLibrary::HandleEchoRequest)
    );

    // 所有端点注册完毕，开始监听
    StartListening();
#endif
}

#if WITH_RPC_REGISTRY
bool UDemoRPCLibrary::HandlePingRequest(const FHttpServerRequest& Request, const FHttpResultCallback& OnComplete)
{
    // 简单回复 pong
    OnComplete(CreateSimpleResponse(true, TEXT("pong")));
    return true;
}

bool UDemoRPCLibrary::HandleEchoRequest(const FHttpServerRequest& Request, const FHttpResultCallback& OnComplete)
{
    TSharedPtr<FJsonObject> JsonObj;
    TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Request.Body);
    // 此处为演示，实际应检查 DeserializeRequest 的返回值
    DeserializeRequest(JsonObj, Reader, /* 需要一个 JsonWriter 实例，或忽略 */);

    FString EchoMessage;
    if (GetStringField(JsonObj, TEXT("data"), EchoMessage, /* 需要一个 JsonWriter 实例，或忽略 */))
    {
        OnComplete(CreateSimpleResponse(true, EchoMessage));
    }
    else
    {
        OnComplete(CreateSimpleResponse(false, TEXT("Invalid request: missing 'data' field."), true));
    }
    return true;
}
#endif
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ExternalRpcRegistry` | 提供外部（HTTP）RPC 端点的注册表和发现机制。 |
| `HTTPServer` | 提供底层的 HTTP 服务器功能，用于监听和处理请求。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移至新的 `UE_LOGF` 格式，属代码现代化更新。 |
| 2026-02-19 | `5b2a374b` | RPCBase - module | 添加 RPCBase 模块核心文件，标志着插件基础结构的建立。 |
| 2026-02-18 | `5634e958` | SubmitTool RPC tests + scheduled build | 提交工具 RPC 测试并配置计划构建，为开发流程做准备。 |
| 2026-02-18 | `2cb65968` | Undo //Fortnite/Main/... changelist 50971911 | 撤销了与 Fortnite 主分支的特定集成更改。 |
| 2026-02-18 | `0b772971` | SubmitTool RPC test | 提交工具 RPC 测试的初始提交。 |

### 维护评价

-   **创建时间**：插件非常新，创建于 2026 年初。
-   **更新频率**：创建后有几次早期提交，最近一次更新（迁移日志宏）在 2026 年 4 月，表明仍有维护活动。
-   **活跃状态**：处于**早期活跃开发**阶段。从提交历史看，它从一个测试概念发展为一个基础模块，并持续进行小的改进。
-   **已知限制**：插件默认未启用 (`EnabledByDefault: false`)，且所有核心功能被 `WITH_RPC_REGISTRY` 宏包裹，意味着需要相应的外部模块支持。目前公开的源码仅包含基础类，具体实现依赖外部或未来更新。
-   **推荐**：**推荐**给需要在 Unreal Engine 中快速构建自定义、标准 HTTP RPC 服务的开发者。它提供了一个良好的起点，但使用者需准备好基于该框架进行扩展，并关注其后续发展。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/RPCBase)