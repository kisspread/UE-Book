# Remote Procedure Calls Base

> RPC base framework that client applications can use to implement RPC libraries.

| 属性 | 值 |
|---|---|
| 中文名 | 远程过程调用基础 |
| 分类 | Runtime |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RPCBase` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2026-02-18 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/RPCBase) | |

## 用途

RPCBase 是一个底层的运行时框架插件，为其他插件提供构建基于 HTTP 的远程过程调用（RPC）服务端能力的基础。它本身不实现具体的业务逻辑，而是封装了 HTTP 服务器的 RPC 路由注册、请求处理、响应构建等核心功能。其他插件（如用于自动测试、状态监控或管理接口的插件）可以继承此框架提供的基类，快速开发出自己的 HTTP RPC 接口。

## 使用场景

-   你需要为编辑器或游戏进程添加一个轻量级的 HTTP 接口，以便外部工具进行通信、查询状态或执行操作。
-   你正在开发一个需要提供网络管理 API 的子系统（如自动化测试框架、性能监控系统）。
-   你希望将 UE 应用的部分功能通过 HTTP 端点暴露给其他服务调用。

## 蓝图用法

此插件主要为 C++ 开发设计，核心功能均通过 C++ 类提供，未暴露蓝图节点。

## C++ 用法

### 头文件引入

```cpp
#include "RPCLibraryBase.h"
```

### 基本用法

创建自己的 RPC 库类，继承自 `URPCLibraryBase`。在构造或初始化时，重写 `Initialize()` 函数来注册你的 RPC 路由。

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
    virtual void Initialize() override;
    
    UFUNCTION(BlueprintCallable, Category = “MyRPC”)
    void DoSomething();
};
```

```cpp
// MyRPCLibrary.cpp
#include “MyRPCLibrary.h”

void UMyRPCLibrary::Initialize()
{
    Super::Initialize();

#if WITH_RPC_REGISTRY
    // 注册一个处理 POST 请求的 RPC，路径为 /api/do-something
    RegisterRPC(
        FName(“DoSomething”),
        FHttpPath(TEXT(“/api/do-something”)),
        EHttpServerRequestVerbs::VERB_POST,
        FHttpHandler::CreateUObject(this, &UMyRPCLibrary::HandleDoSomethingRequest)
    );
#endif
}

#if WITH_RPC_REGISTRY
bool UMyRPCLibrary::HandleDoSomethingRequest(const FHttpServerRequest& Request, const FHttpResultCallback& OnComplete)
{
    // 解析请求体（JSON）
    TSharedPtr<FJsonObject> JsonObject;
    TSharedRef<TJsonReader<>> JsonReader = TJsonReader<<>::Create(Request.Body);
    TSharedRef<TJsonWriter<>> JsonWriter = TJsonWriter<>::Create(&ResponseString);

    if (DeserializeRequest(JsonObject, JsonReader, JsonWriter))
    {
        // 处理业务逻辑
        FString ActionValue;
        if (GetStringField(JsonObject, TEXT(“action”), ActionValue, JsonWriter))
        {
            // ... 执行具体操作 ...

            // 返回成功响应
            OnComplete(CreateSimpleResponse(true, TEXT(“Action performed successfully.”)));
            return true;
        }
    }

    // 返回错误响应
    OnComplete(CreateSimpleResponse(false, TEXT(“Invalid request.”), true));
    return false;
}
#endif
```

### 进阶用法

`URPCLibraryBase` 提供了几个保护级别的辅助方法，用于简化 RPC 处理：
- `RegisterRPC`: 核心方法，用于将处理函数绑定到指定的 HTTP 路径和动词。
- `HandleRegistrationFinishedRoute`: 用于处理所有 RPC 注册完成后的特殊路由查询（通常用于服务发现）。
- `CreateSimpleResponse`: 创建标准化格式的 HTTP JSON 响应。
- `DeserializeRequest`: 通用的 JSON 请求体反序列化方法。
- `GetStringField`: 从 JSON 对象中安全地获取字符串字段的辅助函数。

## Demo 示例

```cpp
// StatusCheckRPCLibrary.h
#pragma once
#include “RPCLibraryBase.h”
#include “StatusCheckRPCLibrary.generated.h”

UCLASS()
class UStatusCheckRPCLibrary : public URPCLibraryBase
{
    GENERATED_BODY()

public:
    virtual void Initialize() override;

#if WITH_RPC_REGISTRY
private:
    bool HandleStatusCheckRequest(const FHttpServerRequest& Request, const FHttpResultCallback& OnComplete);
#endif
};
```

```cpp
// StatusCheckRPCLibrary.cpp
#include “StatusCheckRPCLibrary.h”

void UStatusCheckRPCLibrary::Initialize()
{
    Super::Initialize();

#if WITH_RPC_REGISTRY
    RegisterRPC(
        FName(“StatusCheck”),
        FHttpPath(TEXT(“/api/status”)),
        EHttpServerRequestVerbs::VERB_GET,
        FHttpHandler::CreateUObject(this, &UStatusCheckRPCLibrary::HandleStatusCheckRequest),
        true, // bOverrideIfBound
        TEXT(“Monitoring”) // OptionalCategory
    );
#endif
}

#if WITH_RPC_REGISTRY
bool UStatusCheckRPCLibrary::HandleStatusCheckRequest(const FHttpServerRequest& Request, const FHttpResultCallback& OnComplete)
{
    // 简单的健康检查逻辑
    const bool bIsRunning = true; // 替换为实际状态检查
    const FString Status = bIsRunning ? TEXT(“OK”) : TEXT(“Error”);

    OnComplete(CreateSimpleResponse(bIsRunning, Status));
    return true;
}
#endif
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ExternalRpcRegistry` | 提供 HTTP 服务器的 RPC 注册管理功能 |
| `HTTPServer` | 提供底层的 HTTP 服务器实现 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志系统迁移到新的 UE_LOGF 格式 |
| 2026-02-19 | `5b2a374b` | RPCBase - module | 插件模块的初始搭建 |
| 2026-02-18 | `5634e958` | SubmitTool RPC tests + scheduled build | 包含用于提交工具的 RPC 测试和构建配置 |
| 2026-02-18 | `2cb65968` | Undo //Fortnite/Main/... changelist 50971911 | 撤销了特定分支的某个变更 |
| 2026-02-18 | `0b772971` | SubmitTool RPC test | 最初的 RPC 测试提交 |

### 维护评价

RPCBase 是一个非常新的插件（创建于 2026 年 2 月），目前处于活跃维护状态。从提交记录看，它经历了从初始提交到日志系统迁移的迭代。作为 Epic 官方维护的底层框架，其稳定性和后续更新有保障。由于是基础框架且默认禁用，它适合需要自建 HTTP RPC 服务的开发者或团队在项目初期评估和集成。目前没有已知问题或限制的公开记录。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/RPCBase)