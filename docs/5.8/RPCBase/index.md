# Remote Procedure Calls Base

> RPC base framework that client applications can use to implement RPC libraries.

| 属性 | 值 |
|---|---|
| 分类 | Runtime |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RPCBase` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2026-02-18 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/RPCBase) | |

## 用途

RPCBase 插件提供了一个用于构建基于 HTTP 的远程过程调用（RPC）服务的基础框架。它封装了底层的 HTTP 服务器和 RPC 注册机制，允许开发者通过继承其核心类 `URPCLibraryBase`，快速创建和注册自定义的 HTTP API 端点。该插件解决的核心问题是：为 Unreal Engine 应用程序提供一种标准化的方式，以暴露可被外部系统（如网页、其他服务或测试工具）通过 HTTP 请求调用的功能接口。

## 使用场景

- 你需要为你的 UE 应用程序创建一个简单的 HTTP API，以便从外部网页或脚本进行远程控制或状态查询。
- 你在开发一个需要与外部微服务或工具进行集成的系统，希望通过标准的 HTTP 请求来调用 UE 内部的功能。
- 你在编写自动化测试或构建工具，需要通过网络向运行中的 UE 实例发送指令并获取结果。

## 蓝图用法

该插件的核心类 `URPCLibraryBase` 及其提供的功能主要面向 C++ 开发者，用于构建底层的 RPC 服务库。在提供的源码中，没有发现任何标记为 `BlueprintCallable` 或 `BlueprintReadWrite` 的函数或属性。因此，**该插件不直接提供蓝图节点**。其使用方式是通过 C++ 继承和重写来实现具体的 RPC 逻辑。

## C++ 用法

### 头文件引入

```cpp
#include "RPCLibraryBase.h"
```

### 基本用法

核心用法是创建一个继承自 `URPCLibraryBase` 的子类，并在 `Initialize` 函数中注册你的 RPC 路由。

```cpp
// MyRPCLibrary.h
#pragma once
#include "RPCLibraryBase.h"
#include "MyRPCLibrary.generated.h"

UCLASS()
class UMyRPCLibrary : public URPCLibraryBase
{
    GENERATED_BODY()
protected:
    virtual void Initialize() override;
private:
    // 处理函数
    TUniquePtr<FHttpServerResponse> HandleHelloWorld(const FHttpServerRequest& Request, const FHttpResultCallback& OnComplete);
};
```

```cpp
// MyRPCLibrary.cpp
#include "MyRPCLibrary.h"

void UMyRPCLibrary::Initialize()
{
    // 必须调用基类的 Initialize
    Super::Initialize();

    // 注册一个简单的 GET 请求路由
    RegisterRPC(
        FName(TEXT("HelloWorld")), // 路由名称
        FHttpPath(TEXT("/api/hello")), // HTTP 路径
        EHttpServerRequestVerbs::VERB_GET, // 请求方法
        FHttpRequestHandler::CreateUObject(this, &UMyRPCLibrary::HandleHelloWorld) // 处理函数
    );
}

TUniquePtr<FHttpServerResponse> UMyRPCLibrary::HandleHelloWorld(const FHttpServerRequest& Request, const FHttpResultCallback& OnComplete)
{
    // 创建一个简单的成功响应
    return CreateSimpleResponse(true, TEXT("Hello from UE!"));
}
```

### 进阶用法

可以注册更复杂的路由，处理 POST 请求的 JSON 数据，并返回结构化的响应。

```cpp
void UMyRPCLibrary::Initialize()
{
    Super::Initialize();

    // 注册一个处理 JSON 数据的 POST 请求
    TArray<FExternalRpcArgumentDesc> InArgs;
    InArgs.Add(FExternalRpcArgumentDesc{TEXT("name"), TEXT("string"), TEXT("The name to greet")});

    RegisterRPC(
        FName(TEXT("GreetUser")),
        FHttpPath(TEXT("/api/greet")),
        EHttpServerRequestVerbs::VERB_POST,
        FHttpRequestHandler::CreateUObject(this, &UMyRPCLibrary::HandleGreetUser),
        false, // 不覆盖已绑定的路由
        TEXT("User"), // 可选分类
        TEXT("application/json"), // 可选内容类型
        InArgs // 输入参数描述
    );
}

TUniquePtr<FHttpServerResponse> UMyRPCLibrary::HandleGreetUser(const FHttpServerRequest& Request, const FHttpResultCallback& OnComplete)
{
    // 解析请求中的 JSON
    TSharedPtr<FJsonObject> RootObject;
    TSharedRef<TJsonReader<>> JsonReader = TJsonReaderFactory<>::Create(Request.Body);
    TSharedRef<TJsonWriter<>> JsonWriter = TJsonWriterFactory<>::Create(&ResponseString);

    if (DeserializeRequest(RootObject, JsonReader, JsonWriter))
    {
        FString Name;
        if (GetStringField(RootObject, TEXT("name"), Name, JsonWriter))
        {
            FString Greeting = FString::Printf(TEXT("Hello, %s!"), *Name);
            return CreateSimpleResponse(true, Greeting);
        }
    }

    // 如果解析失败，返回错误响应
    return CreateSimpleResponse(false, TEXT("Invalid request body."), true);
}
```

## Demo 示例

一个完整的、可编译的最小 RPC 服务库示例。

```cpp
// SimpleRPCLibrary.h
#pragma once
#include "RPCLibraryBase.h"
#include "SimpleRPCLibrary.generated.h"

UCLASS()
class USimpleRPCLibrary : public URPCLibraryBase
{
    GENERATED_BODY()
protected:
    virtual void Initialize() override;
private:
    TUniquePtr<FHttpServerResponse> HandleGetStatus(const FHttpServerRequest& Request, const FHttpResultCallback& OnComplete);
    TUniquePtr<FHttpServerResponse> HandlePostCommand(const FHttpServerRequest& Request, const FHttpResultCallback& OnComplete);
};
```

```cpp
// SimpleRPCLibrary.cpp
#include "SimpleRPCLibrary.h"

void USimpleRPCLibrary::Initialize()
{
    Super::Initialize();

    // 1. 注册一个 GET /status 端点，返回应用状态
    RegisterRPC(
        FName(TEXT("GetStatus")),
        FHttpPath(TEXT("/status")),
        EHttpServerRequestVerbs::VERB_GET,
        FHttpRequestHandler::CreateUObject(this, &USimpleRPCLibrary::HandleGetStatus)
    );

    // 2. 注册一个 POST /command 端点，执行简单命令
    RegisterRPC(
        FName(TEXT("PostCommand")),
        FHttpPath(TEXT("/command")),
        EHttpServerRequestVerbs::VERB_POST,
        FHttpRequestHandler::CreateUObject(this, &USimpleRPCLibrary::HandlePostCommand)
    );
}

TUniquePtr<FHttpServerResponse> USimpleRPCLibrary::HandleGetStatus(const FHttpServerRequest& Request, const FHttpResultCallback& OnComplete)
{
    // 返回一个包含当前时间的状态信息
    FString Status = FString::Printf(TEXT("{\"status\": \"running\", \"time\": \"%s\"}"), *FDateTime::Now().ToString());
    return CreateSimpleResponse(true, Status);
}

TUniquePtr<FHttpServerResponse> USimpleRPCLibrary::HandlePostCommand(const FHttpServerRequest& Request, const FHttpResultCallback& OnComplete)
{
    // 简单地回显收到的命令
    FString Command = Request.Body;
    FString Response = FString::Printf(TEXT("{\"command_received\": \"%s\"}"), *Command);
    return CreateSimpleResponse(true, Response);
}
```

## 模块依赖

从 `RPCBase.Build.cs` 分析，使用该插件需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `ExternalRpcRegistry` | 提供外部 RPC 注册的核心组件和管理器。 |
| `HTTPServer` | 提供底层的 HTTP 服务器功能，用于监听和处理 HTTP 请求。 |

## 维护状态

### 近期更新

```
- 2026-04-14 35e60df1 将日志宏从 UE_LOG 迁移至 UE_LOGF。
- 2026-02-19 5b2a374b RPCBase - 模块初始化。
- 2026-02-18 5634e958 SubmitTool RPC 测试 + 定时构建。
```

### 维护评价

该插件创建于 2026 年 2 月，是一个非常新的插件。从提交历史看，它在创建后不久（2026年4月）就有一次代码质量改进（日志宏迁移），表明它处于**活跃维护**状态。作为 Epic Games 官方提供的基础框架，其稳定性和可靠性有保障。插件默认禁用，表明它可能是一个面向特定需求或高级用户的工具。**推荐使用**，特别是对于需要快速搭建基于 HTTP 的 RPC 服务的项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/RPCBase)