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
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ModelContextProtocol) | |

## 用途

该插件实现了 Anthropic 的模型上下文协议（MCP）服务器，使 Unreal Engine 能够作为 MCP 服务器运行。其核心目的是让外部 AI 助手（如 Claude）能够通过标准化的 JSON-RPC 协议与 Unreal Engine 编辑器和运行时进行交互。它解决了 AI 助手无法直接理解或操作 UE 项目资产、蓝图、关卡等复杂数据结构的问题，为 AI 驱动的自动化工作流、资产查询、编辑器操作提供了标准化的接口。

## 使用场景

-   **AI 辅助开发**：你正在使用 Claude 等 AI 助手，并希望它能够直接查询你的 UE 项目中的资产信息（如材质参数、蓝图节点）、执行编辑器命令（如打开资产、修改属性）或获取运行时游戏状态。
-   **自动化测试与集成**：你需要编写脚本或测试用例，通过一个标准化的协议远程控制 UE 编辑器或游戏实例，进行自动化测试或集成到 CI/CD 流程中。
-   **自定义工具链**：你希望将 UE 的功能暴露给其他支持 MCP 协议的工具或服务，构建自定义的开发工具链。

## 蓝图用法

当前提供的测试模块主要包含 C++ 接口和 Mock 类，未发现直接暴露给蓝图的 `BlueprintCallable` 函数。蓝图交互通常通过 `ModelContextProtocolEditor` 或 `ModelContextProtocolEngine` 模块提供的编辑器工具或运行时组件间接实现。核心交互逻辑基于 JSON-RPC 请求/响应。

## C++ 用法

### 头文件引入

```cpp
#include "ModelContextProtocol.h"
#include "IModelContextProtocolTool.h"
#include "IModelContextProtocolResourceProvider.h"
```

### 基本用法

以下示例展示了如何创建一个模拟的 MCP 工具和资源提供者，用于测试或理解接口。

**创建一个自定义工具（Mock 示例）**：
```cpp
// 来源: Source/ModelContextProtocolTests/Private/Mocks/MockModelContextProtocolTool.h
struct FMyCustomTool : IModelContextProtocolTool
{
    virtual FString GetName() const override { return TEXT("my_custom_tool"); }
    virtual FString GetDescription() const override { return TEXT("A custom tool that does something."); }
    virtual TSharedPtr<FJsonObject> GetInputJsonSchema() const override
    {
        // 定义工具的输入参数 JSON Schema
        return FMockModelContextProtocolTool::MakeTestInputSchema(
            {{TEXT("param1"), TEXT("string")}, {TEXT("param2"), TEXT("number")}},
            {TEXT("param1")} // param1 是必需的
        );
    }

    virtual FModelContextProtocolToolResult Run(const TSharedPtr<FJsonObject>& Params) override
    {
        // 从 Params 中获取参数
        FString Param1 = Params->GetStringField(TEXT("param1"));
        double Param2 = Params->GetNumberField(TEXT("param2"));

        // 执行你的逻辑...
        FString ResultText = FString::Printf(TEXT("Processed: %s with %f"), *Param1, Param2);

        // 返回结果
        return UE::ModelContextProtocol::MakeTextResult(ResultText);
    }
};
```

**创建一个资源提供者（Mock 示例）**：
```cpp
// 来源: Source/ModelContextProtocolTests/Private/Mocks/MockModelContextProtocolResourceProvider.h
struct FMyResourceProvider : IModelContextProtocolResourceProvider
{
    virtual void ListResources(FModelContextProtocolResourceDescriptorList& OutResourceDescriptors) const override
    {
        // 列出你提供的资源
        OutResourceDescriptors.Add(
            FModelContextProtocolResourceDescriptor(
                TEXT("ue://project/settings"),
                TEXT("Project Settings"),
                TEXT("Current project settings"),
                TEXT("application/json")
            ),
            this->AsShared()
        );
    }

    virtual TValueOrError<FModelContextProtocolResource, FString> ReadResource(const FString& Uri) const override
    {
        if (Uri == TEXT("ue://project/settings"))
        {
            // 生成或获取资源内容
            TSharedRef<FJsonObject> SettingsJson = MakeShared<FJsonObject>();
            SettingsJson->SetStringField(TEXT("projectName"), TEXT("MyGame"));
            // ... 添加更多设置

            return MakeValue(FModelContextProtocolResource(Uri, SettingsJson));
        }
        return MakeError(TEXT("Resource not found"));
    }
};
```

### 进阶用法

测试用例展示了如何通过 HTTP 发送 JSON-RPC 请求来与 MCP 服务器交互。

**发送一个 JSON-RPC 请求**：
```cpp
// 来源: Source/ModelContextProtocolTests/Private/ModelContextProtocolTestUtilities.h
// 构造一个调用工具的请求
TSharedRef<FJsonObject> ToolRequest = UE::ModelContextProtocol::Tests::MakeJsonRpcRequest(
    TEXT("tools/call"), // MCP 方法名
    MakeShared<FJsonValueNumber>(1), // 请求 ID
    // 构造 params 对象
    [&]() {
        TSharedRef<FJsonObject> Params = MakeShared<FJsonObject>();
        Params->SetStringField(TEXT("name"), TEXT("my_custom_tool"));
        TSharedRef<FJsonObject> Arguments = MakeShared<FJsonObject>();
        Arguments->SetStringField(TEXT("param1"), TEXT("Hello"));
        Arguments->SetNumberField(TEXT("param2"), 42.0);
        Params->SetObjectField(TEXT("arguments"), Arguments);
        return Params;
    }()
);

// 将请求对象序列化为字符串
FString RequestString = UE::ModelContextProtocol::Tests::JsonObjectToString(ToolRequest);

// 通过 HTTP POST 发送到 MCP 服务器 (通常为 http://127.0.0.1:Port/Path)
// ... 使用 FHttpModule 发送请求 ...
```

## Demo 示例

一个最小化的自定义 MCP 工具实现：

**MyMcpTool.h**
```cpp
#pragma once
#include "IModelContextProtocolTool.h"

class FMyMcpTool : public IModelContextProtocolTool
{
public:
    // IModelContextProtocolTool 接口实现
    virtual FString GetName() const override;
    virtual FString GetDescription() const override;
    virtual TSharedPtr<FJsonObject> GetInputJsonSchema() const override;
    virtual FModelContextProtocolToolResult Run(const TSharedPtr<FJsonObject>& Params) override;
};
```

**MyMcpTool.cpp**
```cpp
#include "MyMcpTool.h"
#include "ModelContextProtocolResources.h" // For MakeTextResult

FString FMyMcpTool::GetName() const
{
    return TEXT("greet_user");
}

FString FMyMcpTool::GetDescription() const
{
    return TEXT("Greets a user by name.");
}

TSharedPtr<FJsonObject> FMyMcpTool::GetInputJsonSchema() const
{
    TSharedRef<FJsonObject> Schema = MakeShared<FJsonObject>();
    Schema->SetStringField(TEXT("type"), TEXT("object"));

    TSharedRef<FJsonObject> Properties = MakeShared<FJsonObject>();
    TSharedRef<FJsonObject> NameProp = MakeShared<FJsonObject>();
    NameProp->SetStringField(TEXT("type"), TEXT("string"));
    NameProp->SetStringField(TEXT("description"), TEXT("The name of the user to greet."));
    Properties->SetObjectField(TEXT("name"), NameProp);
    Schema->SetObjectField(TEXT("properties"), Properties);

    TArray<TSharedPtr<FJsonValue>> Required;
    Required.Add(MakeShared<FJsonValueString>(TEXT("name")));
    Schema->SetArrayField(TEXT("required"), Required);

    return Schema;
}

FModelContextProtocolToolResult FMyMcpTool::Run(const TSharedPtr<FJsonObject>& Params)
{
    if (!Params.IsValid())
    {
        return UE::ModelContextProtocol::MakeErrorResult(TEXT("Missing parameters."));
    }

    const FString UserName = Params->GetStringField(TEXT("name"));
    if (UserName.IsEmpty())
    {
        return UE::ModelContextProtocol::MakeErrorResult(TEXT("'name' parameter cannot be empty."));
    }

    FString Greeting = FString::Printf(TEXT("Hello, %s! Welcome to Unreal Engine."), *UserName);
    return UE::ModelContextProtocol::MakeTextResult(Greeting);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ModelContextProtocol` | 核心协议定义、会话管理、工具/资源接口 |
| `ModelContextProtocolEngine` | 引擎运行时集成，可能包含游戏内 MCP 服务器功能 |
| `ModelContextProtocolEditor` | 编辑器集成，提供编辑器工具、资产查询等 MCP 功能 |
| `HTTP` | 用于 MCP 服务器与客户端之间的 HTTP/JSON-RPC 通信 |
| `Json` | 处理 JSON 数据的序列化与反序列化 |
| `AnalyticsET` | 用于记录 MCP 相关的分析事件（测试中可见 Mock） |

## 维护状态

### 近期更新

- 2026-04-24 `626f7a76` [ModelContextProtocol] Strict-type check for `isError` field in `IsToolResultSuccess`.
- 2026-04-22 `8be45e82` [ModelContextProtocol] Log tool call results at *VeryVerbose* for symmetry with input logging.
- 2026-04-22 `b103f5fa` [ModelContextProtocol] Add analytics instrumentation for tool calls and sessions.
- 2026-04-19 `f4f92133` [ModelContextProtocol] Fix flaky `ToolsetRegistry.Deferred` tests by dropping `bConnected` assertion
- 2026-04-18 `6471b168` [AIAssistant] Change how UToolsetDefinitions determine which UFunctions are tools,.

### 维护评价

该插件创建于 2026 年 4 月，是一个非常新的实验性插件。从提交记录看，它处于**活跃的早期开发阶段**。作为 `IsExperimentalVersion: true` 且 `EnabledByDefault: false` 的插件，其 API 和功能可能会发生重大变化。目前主要由 Epic Games 开发，用于探索 AI 与 UE 的集成。**推荐用于实验和原型开发**，但不建议在需要稳定性的生产项目中依赖它。由于其新颖性，社区资源和文档可能非常有限。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ModelContextProtocol)
-   [官方文档]() (暂无)
-   [测试用例]() (位于插件源码的 `Tests` 模块中)