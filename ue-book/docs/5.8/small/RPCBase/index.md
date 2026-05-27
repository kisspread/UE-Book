# Remote Procedure Calls Base

> RPC base framework that client applications can use to implement RPC libraries.

| 属性 | 值 |
|---|---|
| 中文名 | RPC 基础 |
| 分类 | Runtime |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RPCBase` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2026-02-18 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/RPCBase) | |

## 用途

RPCBase 插件提供了一个基础框架，用于在 Unreal Engine 中实现基于 HTTP 的远程过程调用（RPC）。它允许游戏或服务器应用将 UObject 的方法（函数）暴露为可通过标准 HTTP 请求调用的端点（Endpoints）。其核心功能是将 `UObject` 的 `UFUNCTION` 映射到 HTTP 路由，并处理请求的序列化、反序列化和响应构建。

这个框架主要面向需要远程调试、管理或监控游戏服务器的场景，例如通过外部工具（如网页管理界面）调用游戏内函数。

## 使用场景

- 你需要从一个外部的 Web 界面或脚本远程调用 Unreal 服务器或游戏中的特定功能（例如，触发一个游戏事件、查询服务器状态）。
- 你正在为 Unreal 服务器开发一个管理面板（Admin Panel），需要通过 HTTP API 与游戏逻辑交互。
- 你需要为游戏服务器创建一套监控 API，用于获取运行时数据或执行维护操作。

## 蓝图用法

由于 `RPCBase` 是一个用于扩展的基础模块，其主要功能通过 C++ 继承和重写来实现。蓝图层面的直接使用较少，主要集中在通过 `UFUNCTION(BlueprintCallable)` 暴露的、由子类实现的业务逻辑函数。框架本身提供的核心节点（如注册路由）在 `URPCLibraryBase` 基类中是 `protected` 的，通常由 C++ 子类在 `Initialize` 中调用。

### 核心函数

在你的派生类中，需要重写 `Initialize` 函数来注册你的 RPC 端点。

| 函数 | 说明 | 所在类 |
|---|---|---|
| `Initialize()` | 框架初始化时调用，应在此函数中调用 `RegisterRPC` 来注册你的端点。 | `URPCLibraryBase` (需子类重写) |
| `RegisterRPC(...)` | 将一个 HTTP 路由（如 `/game/spawn_actor`）与一个 `FHttpRequestHandler`（C++ 函数）绑定。这是将蓝图/游戏逻辑暴露为 API 的核心。 | `URPCLibraryBase` |

## C++ 用法

`RPCBase` 的设计模式是提供一个基类 `URPCLibraryBase`，用户通过继承它并实现特定的虚函数来创建自己的 RPC 库。

### 头文件引入

```cpp
#include "RPCLibraryBase.h"
```

### 基本用法

创建一个继承自 `URPCLibraryBase` 的类，并重写 `Initialize` 和 `StartListening` 函数。

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
	virtual void StartListening() override;
};

// MyRPCLibrary.cpp
#include "MyRPCLibrary.h"

void UMyRPCLibrary::Initialize()
{
	Super::Initialize();

#if WITH_RPC_REGISTRY
	// 注册一个示例 RPC 路由
	RegisterRPC(
		TEXT("HelloWorld"), // 路由名称
		FHttpPath(TEXT("/api/hello")), // HTTP 路径
		EHttpServerRequestVerbs::VERB_GET, // HTTP 方法
		FHttpRequestHandler::CreateUObject(this, &UMyRPCLibrary::HandleHelloRequest) // 处理函数
	);
#endif
}

void UMyRPCLibrary::StartListening()
{
	Super::StartListening();
}

#if WITH_RPC_REGISTRY
TUniquePtr<FHttpServerResponse> UMyRPCLibrary::HandleHelloRequest(const FHttpServerRequest& Request, const FHttpResultCallback& OnComplete)
{
	// 处理请求逻辑
	return CreateSimpleResponse(true, TEXT("Hello from UE5!"));
}
#endif
```

### 进阶用法

可以处理带参数的 JSON 请求，并返回结构化的 JSON 响应。使用 `DeserializeRequest` 和 `GetStringField` 等辅助函数简化 JSON 处理。

```cpp
// 假设已有一个 HandleSpawnRequest 函数注册到了 /api/spawn_actor
TUniquePtr<FHttpServerResponse> UMyRPCLibrary::HandleSpawnRequest(const FHttpServerRequest& Request, const FHttpResultCallback& OnComplete)
{
	TSharedPtr<FJsonObject> RootObject;
	const TSharedRef<TJsonReader<>> JsonReader = TJsonReaderFactory<>::Create(Request.Body);
	TSharedRef<TJsonWriter<>> JsonWriter = TJsonWriterFactory<>::Create(&ResponseString);

	// 使用基类辅助函数反序列化请求体
	if (!DeserializeRequest(RootObject, JsonReader, JsonWriter))
	{
		return CreateSimpleResponse(false, TEXT("Invalid JSON"), true);
	}

	// 使用基类辅助函数获取字段
	FString ActorClassPath;
	if (!GetStringField(RootObject, TEXT("actor_class"), ActorClassPath, JsonWriter))
	{
		return CreateSimpleResponse(false, TEXT("Missing 'actor_class' field"), true);
	}

	// ... 根据 ActorClassPath 执行生成逻辑 ...

	return CreateSimpleResponse(true, TEXT("Actor Spawned"));
}
```

## Demo 示例

以下是一个完整的、可编译的最小 RPC 库示例，它暴露了一个 `/api/get_time` 端点来获取服务器时间。

**MyTimeRPCLibrary.h**
```cpp
// MyTimeRPCLibrary.h
#pragma once
#include "RPCLibraryBase.h"
#include "MyTimeRPCLibrary.generated.h"

UCLASS()
class UMyTimeRPCLibrary : public URPCLibraryBase
{
	GENERATED_BODY()
protected:
	virtual void Initialize() override;
	virtual void StartListening() override;

private:
#if WITH_RPC_REGISTRY
	TUniquePtr<FHttpServerResponse> HandleGetTimeRequest(const FHttpServerRequest& Request, const FHttpResultCallback& OnComplete);
#endif
};
```

**MyTimeRPCLibrary.cpp**
```cpp
// MyTimeRPCLibrary.cpp
#include "MyTimeRPCLibrary.h"
#include "JsonObjectConverter.h"

void UMyTimeRPCLibrary::Initialize()
{
	Super::Initialize();

#if WITH_RPC_REGISTRY
	RegisterRPC(
		TEXT("GetTime"),
		FHttpPath(TEXT("/api/get_time")),
		EHttpServerRequestVerbs::VERB_GET,
		FHttpRequestHandler::CreateUObject(this, &UMyTimeRPCLibrary::HandleGetTimeRequest)
	);
#endif
}

void UMyTimeRPCLibrary::StartListening()
{
	Super::StartListening();
	UE_LOG(LogTemp, Display, TEXT("Time RPC Library Started."));
}

#if WITH_RPC_REGISTRY
TUniquePtr<FHttpServerResponse> UMyTimeRPCLibrary::HandleGetTimeRequest(const FHttpServerRequest& Request, const FHttpResultCallback& OnComplete)
{
	const FString CurrentTime = FDateTime::Now().ToString();
	return CreateSimpleResponse(true, CurrentTime);
}
#endif
```

## 模块依赖

你的 `Build.cs` 文件需要依赖此插件提供的模块。

| 模块 | 用途 |
|---|---|
| `ExternalRpcRegistry` | 提供外部 HTTP 服务器注册和管理的核心功能。 |
| `HTTPServer` | 底层的 HTTP 服务器实现。 |

**示例 Build.cs 依赖添加：**
```csharp
PublicDependencyModuleNames.AddRange(new string[] { "RPCBase", "ExternalRpcRegistry", "HTTPServer" });
```

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移到 `UE_LOGF`，是 Epic 的统一日志系统更新。 |
| 2026-02-19 | `5b2a374b` | RPCBase - module | 插件模块本身的初始提交。 |
| 2026-02-18 | `5634e958` | SubmitTool RPC tests + scheduled build | 包含 RPC 测试用例和计划构建的提交。 |
| 2026-02-18 | `0b772971` | SubmitTool RPC test | RPC 功能的初始测试提交。 |

### 维护评价

RPCBase 是一个非常新的插件，首次提交于 2026 年 2 月。从提交记录看，它目前处于早期开发阶段，主要功能框架已搭建，并进行了基础的日志系统更新。

**优点**：
-   提供了清晰的 `URPCLibraryBase` 基类和设计模式，便于扩展。
-   依赖于成熟的 `ExternalRpcRegistry` 和 `HTTPServer` 模块，基础稳定。

**风险与限制**：
-   **实验性**：虽然 `IsBetaVersion` 为 `false`，但 `EnabledByDefault` 为 `false`，且处于早期阶段，API 和功能可能还不稳定，未来有较大变动风险。
-   **文档缺失**：`.uplugin` 中的 `DocsURL` 为空，缺乏官方文档。
-   **测试用例有限**：当前的测试看起来主要是为提交工具（SubmitTool）服务的，尚未发现公开的、详细的单元测试或集成测试。

**推荐**：适合早期探索和内部工具开发。**不推荐**用于对稳定性要求高的生产环境主功能。建议密切关注其更新，并做好 API 可能变化的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/RPCBase)
- 官方文档：暂无
- 测试用例：暂无（插件目录内未发现公开测试）