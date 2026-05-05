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
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ModelContextProtocol) | |

## 用途

本插件实现了 Anthropic 的模型上下文协议（MCP）服务器，使 Unreal Engine 能够作为 MCP 服务器运行。其核心目的是为 AI 模型（如 Claude）提供一个标准化的接口，使其能够与 Unreal Engine 编辑器和运行时进行交互。通过此插件，AI 可以查询引擎状态、执行编辑器操作、调用蓝图函数等，从而实现 AI 辅助的游戏开发、自动化测试和内容生成。

## 使用场景

- **AI 辅助关卡设计**：让 AI 根据自然语言描述，通过 MCP 协议在编辑器中生成或修改关卡布局。
- **自动化测试与调试**：AI 通过 MCP 协议连接到运行中的游戏实例，执行测试用例、检查游戏状态或触发特定事件。
- **智能内容生成**：AI 模型利用 MCP 协议调用引擎的资产创建和编辑功能，生成材质、蓝图或动画。
- **开发流程集成**：将 AI 助手集成到开发工作流中，通过标准协议与引擎通信，实现代码审查、问题诊断等高级功能。

## 蓝图用法

本插件主要通过 C++ 提供服务，蓝图可调用的接口有限，主要用于初始化和状态查询。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `StartMcpServer` | 启动 MCP 服务器，开始监听客户端连接 | `UMcpServerSubsystem` |
| `StopMcpServer` | 停止 MCP 服务器 | `UMcpServerSubsystem` |
| `IsMcpServerRunning` | 查询 MCP 服务器是否正在运行 | `UMcpServerSubsystem` |

### 使用示例（蓝图描述）

在游戏模式或某个管理器的 `BeginPlay` 事件中，调用 `StartMcpServer` 节点来启动服务。在需要停止服务时（如游戏结束），调用 `StopMcpServer`。可以使用 `IsMcpServerRunning` 节点来检查服务状态，并根据结果更新 UI 或执行其他逻辑。

## C++ 用法

### 头文件引入

```cpp
#include "ModelContextProtocol.h"
#include "McpServerSubsystem.h"
```

### 基本用法

以下示例展示了如何在 C++ 中启动和停止 MCP 服务器。

```cpp
// 来源: ModelContextProtocol/Tests/McpServerTest.cpp
void AMyGameMode::StartMcpService()
{
    // 获取 MCP 服务器子系统
    UMcpServerSubsystem* McpSubsystem = GEngine->GetEngineSubsystem<UMcpServerSubsystem>();
    if (McpSubsystem)
    {
        // 启动服务器，监听默认端口
        McpSubsystem->StartMcpServer();
        UE_LOG(LogTemp, Log, TEXT("MCP Server Started"));
    }
}

void AMyGameMode::StopMcpService()
{
    UMcpServerSubsystem* McpSubsystem = GEngine->GetEngineSubsystem<UMcpServerSubsystem>();
    if (McpSubsystem)
    {
        McpSubsystem->StopMcpServer();
        UE_LOG(LogTemp, Log, TEXT("MCP Server Stopped"));
    }
}
```

### 进阶用法

注册自定义工具（Tool）供 AI 调用。这是扩展 MCP 服务器功能的核心方式。

```cpp
// 来源: ModelContextProtocolEngine/Tests/McpToolTest.cpp
#include "McpToolRegistry.h"
#include "McpTool.h"

// 定义一个自定义工具类
class FMyCustomTool : public IMcpTool
{
public:
    virtual FString GetName() const override { return TEXT("MyCustomTool"); }
    virtual FString GetDescription() const override { return TEXT("A tool that does something custom."); }
    virtual TSharedPtr<FJsonObject> GetInputSchema() const override
    {
        // 定义工具的输入参数 JSON Schema
        TSharedPtr<FJsonObject> Schema = MakeShareable(new FJsonObject);
        Schema->SetStringField(TEXT("type"), TEXT("object"));
        // ... 定义 properties
        return Schema;
    }
    virtual TSharedPtr<FJsonObject> Execute(const TSharedPtr<FJsonObject>& Input) override
    {
        // 实现工具的具体逻辑
        TSharedPtr<FJsonObject> Result = MakeShareable(new FJsonObject);
        Result->SetStringField(TEXT("status"), TEXT("success"));
        return Result;
    }
};

// 在游戏初始化时注册工具
void AMyGameMode::BeginPlay()
{
    Super::BeginPlay();
    
    UMcpToolRegistry* ToolRegistry = GEngine->GetEngineSubsystem<UMcpToolRegistry>();
    if (ToolRegistry)
    {
        TSharedPtr<IMcpTool> MyTool = MakeShareable(new FMyCustomTool());
        ToolRegistry->RegisterTool(MyTool);
    }
}
```

## Demo 示例

一个最小的可运行示例，展示如何创建并注册一个简单的 MCP 工具。

**MyMcpTool.h**
```cpp
#pragma once
#include "McpTool.h"

class FMyMcpTool : public IMcpTool
{
public:
    virtual ~FMyMcpTool() = default;
    virtual FString GetName() const override;
    virtual FString GetDescription() const override;
    virtual TSharedPtr<FJsonObject> GetInputSchema() const override;
    virtual TSharedPtr<FJsonObject> Execute(const TSharedPtr<FJsonObject>& Input) override;
};
```

**MyMcpTool.cpp**
```cpp
#include "MyMcpTool.h"
#include "JsonObjectConverter.h"

FString FMyMcpTool::GetName() const
{
    return TEXT("EchoTool");
}

FString FMyMcpTool::GetDescription() const
{
    return TEXT("A simple tool that echoes back the input message.");
}

TSharedPtr<FJsonObject> FMyMcpTool::GetInputSchema() const
{
    TSharedPtr<FJsonObject> Schema = MakeShareable(new FJsonObject);
    Schema->SetStringField(TEXT("type"), TEXT("object"));
    
    TSharedPtr<FJsonObject> Properties = MakeShareable(new FJsonObject);
    TSharedPtr<FJsonObject> MessageProp = MakeShareable(new FJsonObject);
    MessageProp->SetStringField(TEXT("type"), TEXT("string"));
    MessageProp->SetStringField(TEXT("description"), TEXT("The message to echo."));
    Properties->SetObjectField(TEXT("message"), MessageProp);
    
    Schema->SetObjectField(TEXT("properties"), Properties);
    TArray<TSharedPtr<FJsonValue>> Required;
    Required.Add(MakeShareable(new FJsonValueString(TEXT("message"))));
    Schema->SetArrayField(TEXT("required"), Required);
    
    return Schema;
}

TSharedPtr<FJsonObject> FMyMcpTool::Execute(const TSharedPtr<FJsonObject>& Input)
{
    TSharedPtr<FJsonObject> Result = MakeShareable(new FJsonObject);
    
    FString Message;
    if (Input->TryGetStringField(TEXT("message"), Message))
    {
        Result->SetStringField(TEXT("echo"), Message);
        Result->SetStringField(TEXT("status"), TEXT("success"));
    }
    else
    {
        Result->SetStringField(TEXT("error"), TEXT("Missing 'message' field."));
        Result->SetStringField(TEXT("status"), TEXT("error"));
    }
    
    return Result;
}
```

**在游戏模块中注册（例如在 GameInstance 子类中）：**
```cpp
#include "MyMcpTool.h"
#include "McpToolRegistry.h"

void UMyGameInstance::Init()
{
    Super::Init();
    
    UMcpToolRegistry* Registry = GEngine->GetEngineSubsystem<UMcpToolRegistry>();
    if (Registry)
    {
        TSharedPtr<IMcpTool> EchoTool = MakeShareable(new FMyMcpTool());
        Registry->RegisterTool(EchoTool);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Json` | 解析和生成 MCP 协议所需的 JSON 数据 |
| `JsonUtilities` | 辅助 JSON 与 UObject 之间的转换 |
| `WebSockets` | 实现 MCP 协议底层的 WebSocket 通信 |
| `Networking` | 提供底层网络支持 |
| `Sockets` | 提供套接字层支持 |

## 维护状态

### 近期更新

- 2026-04-24 `626f7a76` [ModelContextProtocol] Strict-type check for `isError` field in `IsToolResultSuccess`.
- 2026-04-22 `8be45e82` [ModelContextProtocol] Log tool call results at *VeryVerbose* for symmetry with input logging.
- 2026-04-22 `b103f5fa` [ModelContextProtocol] Add analytics instrumentation for tool calls and sessions.
- 2026-04-19 `f4f92133` [ModelContextProtocol] Fix flaky `ToolsetRegistry.Deferred` tests by dropping `bConnected` assertion
- 2026-04-18 `6471b168` [AIAssistant] Change how UToolsetDefinitions determine which UFunctions are tools,.

### 维护评价

- **创建时间**：2026年4月，非常新的插件。
- **更新频率**：创建后短期内有密集的功能性提交，表明处于积极开发阶段。
- **维护状态**：**活跃开发中**。作为实验性插件，功能正在快速迭代和完善。
- **已知限制**：目前为实验性版本（`IsExperimentalVersion=true`），API 可能不稳定，且默认未启用（`EnabledByDefault=false`）。
- **推荐使用**：适合对 AI 与游戏引擎集成有前沿探索需求的开发者。不建议用于生产环境的稳定项目，但非常适合原型开发、技术研究和实验性项目。请密切关注其 API 变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ModelContextProtocol)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ModelContextProtocol/Source/ModelContextProtocolTests)