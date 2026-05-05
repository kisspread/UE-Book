# Unreal MCP

> Anthropic MCP (Model Context Protocol) server implementation for Unreal Engine.

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ModelContextProtocol` (Runtime), `ModelContextProtocolEditor` (Runtime), `ModelContextProtocolEditorTests` (Runtime), `ModelContextProtocolEngine` (Runtime), `ModelContextProtocolEngineTests` (Runtime), `ModelContextProtocolTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-18 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ModelContextProtocol) | |

## 用途

这个插件在 Unreal Engine 内部实现了一个 **Anthropic Model Context Protocol (MCP) 服务器**，允许外部 AI 客户端（如 Claude Desktop、Cursor 等支持 MCP 协议的工具）通过 HTTP + SSE（Server-Sent Events）与 Unreal Engine 进行双向通信。

核心解决的问题是：**让 AI 大语言模型能够直接操控 Unreal Engine 编辑器和运行时**。通过 MCP 协议，AI 客户端可以：

- **调用工具（Tools）**：执行 UE 内部操作，如选择 Actor、修改属性、运行控制台命令等
- **读取资源（Resources）**：访问 UE 项目中的资产信息、场景数据等结构化资源
- **接收事件通知**：通过 SSE 流接收工具列表变更等实时通知

插件采用 JSON-RPC 2.0 协议，支持 MCP 规范的多个版本（2025-11-25、2025-06-18、2024-11-05），并实现了协议版本协商机制。

## 使用场景

- 你在使用 Claude Desktop 或其他 MCP 客户端，想让 AI 直接操控 UE 编辑器 → 启用此插件并注册自定义工具
- 你需要构建 AI 辅助关卡设计工作流 → 通过 MCP 工具暴露场景操作能力给 AI
- 你想让 AI 读取项目资产信息并生成报告 → 实现 `IModelContextProtocolResourceProvider` 暴露资源
- 你在开发 AI 驱动的自动化测试系统 → 通过 MCP 工具执行测试操作并收集结果
- 你需要将 UE 编辑器能力集成到 AI Agent 工作流中 → 启动 MCP 服务器，AI 客户端即可连接

## 蓝图用法

本插件核心模块（`ModelContextProtocol`）不暴露蓝图节点，主要面向 C++ 开发者。`ModelContextProtocolEditor` 模块可能提供编辑器扩展，但当前模块本身是纯 C++ 接口。

## C++ 用法

### 头文件引入

```cpp
#include "IModelContextProtocolModule.h"
#include "IModelContextProtocolTool.h"
#include "IModelContextProtocolResourceProvider.h"
#include "ModelContextProtocolToolResults.h"
#include "ModelContextProtocolResources.h"
```

### 基本用法：注册自定义工具

实现 `IModelContextProtocolTool` 接口并注册到 MCP 模块：

```cpp
// MyMcpTool.h
#pragma once

#include "IModelContextProtocolTool.h"

class FMyMcpTool : public IModelContextProtocolTool
{
public:
    virtual FString GetName() const override { return TEXT("my_custom_tool"); }
    
    virtual FString GetDescription() const override 
    { 
        return TEXT("Performs a custom operation in the editor."); 
    }

    virtual TSharedPtr<FJsonObject> GetInputJsonSchema() const override
    {
        FJsonDomBuilder::FObject Schema;
        Schema.Set(TEXT("type"), TEXT("object"));
        FJsonDomBuilder::FObject Properties;
        Properties.Set(TEXT("actor_name"), FJsonDomBuilder::FObject().Set(TEXT("type"), TEXT("string")));
        Schema.Set(TEXT("properties"), Properties);
        FJsonDomBuilder::FArray Required;
        Required.Add(TEXT("actor_name"));
        Schema.Set(TEXT("required"), Required);
        return Schema.AsJsonObject().ToSharedPtr();
    }

    virtual FModelContextProtocolToolResult Run(const TSharedPtr<FJsonObject>& Params) override
    {
        FString ActorName;
        if (Params->TryGetStringField(TEXT("actor_name"), ActorName))
        {
            // 执行实际操作...
            return UE::ModelContextProtocol::MakeTextResult(TEXT("Success: ") + ActorName);
        }
        return UE::ModelContextProtocol::MakeErrorResult(TEXT("Missing actor_name parameter"));
    }
};
```

```cpp
// 注册工具
IModelContextProtocolModule& Module = IModelContextProtocolModule::GetChecked();
Module.AddTool(MakeShared<FMyMcpTool>());

// 启动服务器（默认端口 8000，路径 /mcp）
Module.StartServer();
```

### 基本用法：注册资源提供者

```cpp
// MyResourceProvider.h
#pragma once

#include "IModelContextProtocolResourceProvider.h"
#include "ModelContextProtocolResources.h"

class FMyResourceProvider : public IModelContextProtocolResourceProvider
{
public:
    virtual void ListResources(FModelContextProtocolResourceDescriptorList& OutResourceDescriptors) const override
    {
        FModelContextProtocolResourceDescriptor Desc(
            TEXT("ue://project/info"),
            TEXT("project_info"),
            TEXT("Project Info"),
            TEXT("Current project metadata"),
            TEXT("application/json")
        );
        OutResourceDescriptors.Add(Desc, AsShared());
    }

    virtual TValueOrError<FModelContextProtocolResource, FString> ReadResource(const FString& Uri) const override
    {
        if (Uri == TEXT("ue://project/info"))
        {
            FString JsonContent = TEXT("{\"name\":\"MyProject\",\"engine\":\"5.8\"}");
            return MakeValue(FModelContextProtocolResource(Uri, MoveTemp(JsonContent)));
        }
        return MakeError(TEXT("Unknown resource URI: ") + Uri);
    }
};
```

```cpp
// 注册资源提供者
IModelContextProtocolModule& Module = IModelContextProtocolModule::GetChecked();
Module.AddResourceProvider(MakeShared<FMyResourceProvider>());
```

### 进阶用法：异步工具与结构化结果

```cpp
class FAsyncMcpTool : public IModelContextProtocolTool
{
public:
    virtual FString GetName() const override { return TEXT("async_heavy_tool"); }
    virtual FString GetDescription() const override { return TEXT("Performs a long-running operation asynchronously."); }

    // 不实现 Run，而是实现 RunAsync
    virtual void RunAsync(
        const FModelContextProtocolToolRequestId& RequestId,
        const TSharedPtr<FJsonObject>& Params,
        const FResultCallback& OnComplete) override
    {
        // 在后台线程执行耗时操作
        Async(EAsyncExecution::Thread, [OnComplete]()
        {
            // ... 长时间操作 ...
            
            // 返回结构化内容结果
            TSharedPtr<FJsonObject> StructuredData = MakeShared<FJsonObject>();
            StructuredData->SetStringField(TEXT("status"), TEXT("completed"));
            StructuredData->SetNumberField(TEXT("count"), 42);
            
            FModelContextProtocolToolResult Result = 
                UE::ModelContextProtocol::MakeStructuredContentResult(StructuredData);
            OnComplete(Result);
        });
    }

    virtual void CancelAsync(const FModelContextProtocolToolRequestId& RequestId) override
    {
        // 处理取消请求
    }
};
```

### 进阶用法：返回图片和音频结果

```cpp
// 返回图片结果
TArray<uint8> ImageData = /* ... 从渲染目标获取 ... */;
FModelContextProtocolToolResult ImageResult = 
    UE::ModelContextProtocol::MakeImageResult(TEXT("image/png"), ImageData);

// 返回音频结果
TArray<uint8> AudioData = /* ... 从音频系统获取 ... */;
FModelContextProtocolToolResult AudioResult = 
    UE::ModelContextProtocol::MakeAudioResult(TEXT("audio/ogg"), AudioData);
```

### 进阶用法：监听工具刷新事件

```cpp
IModelContextProtocolModule& Module = IModelContextProtocolModule::GetChecked();
Module.OnRefreshTools().AddLambda([&Module]()
{
    // 重新注册工具（控制台命令 ModelContextProtocol.RefreshTools 触发时）
    Module.AddTool(MakeShared<FMyMcpTool>());
});
```

### 进阶用法：分析事件集成

```cpp
IModelContextProtocolModule& Module = IModelContextProtocolModule::GetChecked();
Module.SetAnalyticsProvider(MyAnalyticsProvider);
Module.SetAnalyticsEventNamespace(TEXT("MyPlugin.MCP"));
// 之后所有 MCP 分析事件会自动以 "MyPlugin.MCP." 为前缀记录
```

## Demo 示例

一个完整的最小 MCP 工具实现，暴露一个 "hello_world" 工具：

```cpp
// HelloWorldMcpTool.h
#pragma once

#include "IModelContextProtocolTool.h"
#include "ModelContextProtocolToolResults.h"

class FHelloWorldMcpTool : public IModelContextProtocolTool
{
public:
    virtual FString GetName() const override
    {
        return TEXT("hello_world");
    }

    virtual FString GetDescription() const override
    {
        return TEXT("Returns a greeting message. Use this to test MCP connectivity.");
    }

    virtual TSharedPtr<FJsonObject> GetInputJsonSchema() const override
    {
        FJsonDomBuilder::FObject Schema;
        Schema.Set(TEXT("type"), TEXT("object"));
        FJsonDomBuilder::FObject Properties;
        Properties.Set(TEXT("name"), FJsonDomBuilder::FObject().Set(TEXT("type"), TEXT("string")).Set(TEXT("description"), TEXT("Name to greet")));
        Schema.Set(TEXT("properties"), Properties);
        return Schema.AsJsonObject().ToSharedPtr();
    }

    virtual FModelContextProtocolToolResult Run(const TSharedPtr<FJsonObject>& Params) override
    {
        FString Name = TEXT("World");
        Params->TryGetStringField(TEXT("name"), Name);
        return UE::ModelContextProtocol::MakeTextResult(FString::Printf(TEXT("Hello, %s! MCP server is running."), *Name));
    }
};
```

```cpp
// HelloWorldMcpTool.cpp
#include "HelloWorldMcpTool.h"
#include "IModelContextProtocolModule.h"

// 在模块 StartupModule 或合适时机注册
void RegisterHelloWorldTool()
{
    IModelContextProtocolModule& Module = IModelContextProtocolModule::GetChecked();
    Module.AddTool(MakeShared<FHelloWorldMcpTool>());
    Module.StartServer(8000, TEXT("/mcp"));
    // 现在 MCP 客户端可以连接 http://localhost:8000/mcp 并调用 hello_world 工具
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `HttpServer` | 提供 HTTP 路由和请求处理，MCP 服务器的传输层 |
| `Json` / `JsonDomBuilder` | JSON-RPC 2.0 消息的序列化与反序列化 |
| `AnalyticsET` | 遥测分析事件上报（工具调用统计等） |
| `HTTP` | HTTP 客户端/服务端基础设施 |

## 维护状态

### 近期更新

- 2026-04-24 `626f7a76` [ModelContextProtocol] Strict-type check for `isError` field in `IsToolResultSuccess`.
- 2026-04-22 `8be45e82` [ModelContextProtocol] Log tool call results at *VeryVerbose* for symmetry with input logging.
- 2026-04-22 `b103f5fa` [ModelContextProtocol] Add analytics instrumentation for tool calls and sessions.
- 2026-04-19 `f4f92133` [ModelContextProtocol] Fix flaky `ToolsetRegistry.Deferred` tests by dropping `bConnected` assertion
- 2026-04-18 `6471b168` [AIAssistant] Change how UToolsetDefinitions determine which UFunctions are tools,.

### 维护评价

- **创建时间**：2026-04-18，非常新的插件
- **实验性状态**：`IsExperimentalVersion=true`，`EnabledByDefault=false`，需要手动启用
- **协议支持**：支持 MCP 规范 2025-11-25、2025-06-18、2024-11-05 三个版本，具备版本协商能力
- **架构成熟度**：模块划分清晰（核心协议层、编辑器扩展层、引擎集成层），每层都有对应测试模块
- **已知限制**：
  - 实验性插件，API 可能在未来版本中发生变化
  - 需要手动启用，不适合直接用于生产环境
  - `NoRedist=true`，不可重新分发
- **推荐**：适合早期采用者和 AI 工具链开发者探索 UE + AI 集成。不建议在生产项目中依赖此插件，但非常适合原型开发和工作流实验。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ModelContextProtocol)
- [MCP 规范](https://modelcontextprotocol.io/specification/2025-11-25)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ModelContextProtocol/Source/ModelContextProtocolTests)