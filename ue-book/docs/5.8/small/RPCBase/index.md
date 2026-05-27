# Remote Procedure Calls Base

> RPC base framework that client applications can use to implement RPC libraries.

| 属性 | 值 |
|---|---|
| 中文名 | 远程过程调用基础框架 |
| 分类 | Runtime |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RPCBase` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2026-02-18 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/RPCBase) | |

## 用途

本插件为在 Unreal Engine 项目中实现**基于 HTTP 的远程过程调用 (RPC)** 提供了一个基础框架。它并非一个开箱即用的 RPC 库，而是一个抽象基类 `URPCLibraryBase`，供客户端应用程序（即你的项目或插件）继承，从而快速构建自定义的 RPC 服务端点。其核心功能是封装了与 `ExternalRpcRegistry` 的交互，简化了 HTTP 路由注册、请求处理和 JSON 序列化/反序列化的常见模式。

## 使用场景

- 你需要为你的 UE5 应用程序创建一套内部或外部的 HTTP API，用于调试、监控、控制游戏逻辑或与外部系统集成。
- 你正在开发一个插件或模块，需要将某些功能以 HTTP 服务的形式暴露出来，例如提供一个管理界面或数据查询接口。
- 你希望统一项目内多个 RPC 服务的实现模式和风格。

## 蓝图用法

根据当前提供的源码分析，`URPCLibraryBase` 主要设计为一个 C++ 基类，用于被继承和扩展。其核心功能（如 `RegisterRPC`）被 `#if WITH_RPC_REGISTRY` 预处理器宏包裹，并且类本身被标记为 `MinimalAPI`，这意味着它的许多成员不会自动导出给蓝图。因此，**该插件的主要使用方式是通过 C++ 继承，而非直接在蓝图中使用其节点**。

## C++ 用法

### 头文件引入

```cpp
#include "RPCLibraryBase.h"
```

### 基本用法

你需要从 `URPCLibraryBase` 派生一个子类，并在你的子类中重写或调用 `Initialize()` 和 `StartListening()` 方法来注册你的 RPC 路由。

```cpp
// MyRPCLibrary.h
#pragma once
#include "RPCLibraryBase.h"
#include "MyRPCLibrary.generated.h"

UCLASS()
class UMyRPCLibrary : public URPCLibraryBase
{
    GENERATED_BODY()
public:
    // 调用此方法来初始化并注册RPC
    void Setup();
private:
    // 覆盖初始化函数，注册自定义RPC
    virtual void Initialize();
    
    // 你的RPC处理函数示例
    bool HandleHelloWorldRPC(const FHttpServerRequest& Request, const FHttpResultCallback& OnComplete);
};
```

```cpp
// MyRPCLibrary.cpp
#include "MyRPCLibrary.h"

void UMyRPCLibrary::Setup()
{
    // 初始化基类，这将触发注册流程
    Initialize();
    // 开始监听HTTP请求
    StartListening();
}

void UMyRPCLibrary::Initialize()
{
    // 确保在 WITH_RPC_REGISTRY 环境下注册
#if WITH_RPC_REGISTRY
    // 注册一个处理GET请求的RPC，路径为 /api/hello
    RegisterRPC(
        FName(TEXT("HelloWorldRPC")),
        FHttpPath(TEXT("/api/hello")),
        EHttpServerRequestVerbs::VERB_GET,
        FHttpHandler::CreateUObject(this, &UMyRPCLibrary::HandleHelloWorldRPC),
        false,
        TEXT("Example"),
        TEXT("application/json"),
        { /* 可选的参数描述数组 */ }
    );
#endif
    // 调用基类的初始化（如果需要）
    // Super::Initialize(); // 根据实际需求决定
}

bool UMyRPCLibrary::HandleHelloWorldRPC(const FHttpServerRequest& Request, const FHttpResultCallback& OnComplete)
{
    // 使用基类的辅助函数创建响应
    auto Response = CreateSimpleResponse(true, TEXT("{\"message\": \"Hello from UE5 RPC!\"}"));
    OnComplete(MoveTemp(Response));
    return true;
}
```
*（基本用法示例基于 `URPCLibraryBase` 的公开接口推导）*

### 进阶用法

基类提供了一些辅助方法，用于处理更复杂的 JSON 请求。以下是一个处理包含 JSON Body 的 POST 请求的示例：

```cpp
bool UMyRPCLibrary::HandleAddItemRPC(const FHttpServerRequest& Request, const FHttpResultCallback& OnComplete)
{
#if WITH_RPC_REGISTRY
    TSharedPtr<FJsonObject> RootObject;
    TSharedRef<TJsonWriter<>> JsonWriter = TJsonWriterFactory<>::Create(&ResponseString);
    TSharedRef<TJsonReader<>> JsonReader = TJsonReaderFactory<>::Create(Request.Body);

    // 使用基类的 DeserializeRequest 进行反序列化
    if (!DeserializeRequest(RootObject, JsonReader, JsonWriter))
    {
        OnComplete(CreateSimpleResponse(false, TEXT("{\"error\": \"Invalid JSON\"}", true));
        return false;
    }

    // 使用基类的 GetStringField 提取字段
    FString ItemName;
    if (!GetStringField(RootObject, TEXT("name"), ItemName, JsonWriter))
    {
        OnComplete(CreateSimpleResponse(false, TEXT("{\"error\": \"Missing 'name' field\"}"));
        return false;
    }

    // ... 处理业务逻辑，将ItemName添加到游戏中 ...

    OnComplete(CreateSimpleResponse(true, TEXT("{\"success\": true, \"item_added\": \"") + ItemName + TEXT("\"}")));
    return true;
#endif
    return false;
}
```
*（进阶用法展示了如何使用 `DeserializeRequest` 和 `GetStringField` 等基类方法）*

## Demo 示例

一个最小的、可编译的示例，演示如何创建一个简单的 RPC 库：

```cpp
// MinimalRPCLibrary.h
#pragma once
#include "RPCLibraryBase.h"
#include "MinimalRPCLibrary.generated.h"

UCLASS()
class UMinimalRPCLibrary : public URPCLibraryBase
{
    GENERATED_BODY()
public:
    void InitializeLibrary();
    
private:
    virtual void Initialize() override;
    bool HandlePing(const FHttpServerRequest& Request, const FHttpResultCallback& OnComplete);
};
```

```cpp
// MinimalRPCLibrary.cpp
#include "MinimalRPCLibrary.h"
#include "HttpServerResponse.h"

void UMinimalRPCLibrary::InitializeLibrary()
{
    Initialize();
    StartListening();
}

void UMinimalRPCLibrary::Initialize()
{
#if WITH_RPC_REGISTRY
    RegisterRPC(
        FName("PingRPC"),
        FHttpPath("/ping"),
        EHttpServerRequestVerbs::VERB_GET,
        FHttpHandler::CreateUObject(this, &UMinimalRPCLibrary::HandlePing),
        false,
        TEXT("System"),
        TEXT("text/plain")
    );
#endif
}

bool UMinimalRPCLibrary::HandlePing(const FHttpServerRequest& Request, const FHttpResultCallback& OnComplete)
{
    auto Response = CreateSimpleResponse(true, TEXT("Pong from UE5"));
    OnComplete(MoveTemp(Response));
    return true;
}
```

## 模块依赖

你的项目或插件如果要使用 RPCBase，需要在 `.Build.cs` 文件中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `ExternalRpcRegistry` | 提供外部 RPC 注册的核心接口和组件 |
| `HTTPServer` | 提供底层的 HTTP 服务器功能，用于处理实际的请求和响应 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志输出宏统一迁移到 UE_LOGF 格式。 |
| 2026-02-19 | `5b2a374b` | RPCBase - module | 初始化 RPCBase 模块的基本结构。 |
| 2026-02-18 | `5634e958` | SubmitTool RPC tests + scheduled build | 提交 RPC 测试工具并配置计划构建。 |
| 2026-02-18 | `2cb65968` | Undo //Fortnite/Main/... changelist 50971911 | 撤销了 Fortnite 分支的一个特定更改。 |
| 2026-02-18 | `0b772971` | SubmitTool RPC test | 初始提交，用于 SubmitTool 的 RPC 测试。 |

### 维护评价

RPCBase 是一个非常新的插件（创建于 2026 年初），目前处于早期开发阶段。从提交历史看，它在创建初期有几次密集的更新（主要用于初始化和测试），之后在 2026 年 4 月有进行维护性的日志宏迁移。由于插件历史极短，无法判断其长期维护频率。**它被标记为 `EnabledByDefault: false`，表明目前可能仍处于实验性或集成测试阶段。** 考虑到其作为基础框架的定位，预计它会随着上层 RPC 库的开发而持续演进。目前可以尝试使用，但需留意后续可能的接口变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/RPCBase)
- [RPCLibraryBase.h](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/RPCBase/Source/RPCBase/Public/RPCLibraryBase.h)
- [RPCBaseModule.h](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/RPCBase/Source/RPCBase/Public/RPCBaseModule.h)
- [测试用例] (当前提供的源码信息中未包含测试文件路径)