# Unreal MCP

> Anthropic MCP (Model Context Protocol) server implementation for Unreal Engine.

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ModelContextProtocol` (Runtime), `ModelContextProtocolEditor` (Runtime), `ModelContextProtocolEngine` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-18 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ModelContextProtocol) | |

## 用途

该插件为 Unreal Engine 实现了 Anthropic 的模型上下文协议（MCP）服务器。它解决的核心问题是**让外部 AI 模型（如 Claude）能够通过标准化的 JSON-RPC 协议与 Unreal Engine 编辑器进行交互**。AI 可以调用编辑器中注册的“工具”（Tools），执行诸如查询资产信息、操作场景对象、甚至生成蓝图逻辑等操作，从而实现 AI 辅助的游戏开发、自动化内容生成和智能编辑器助手等功能。它本质上是一个连接 AI 与 UE 编辑器能力的桥梁。

## 使用场景

- **AI 辅助内容创作**：你正在开发一个开放世界游戏，需要 AI 助手根据自然语言描述（如“在森林区域生成100棵松树”）自动在编辑器中放置资产。
- **自动化测试与构建**：你需要一个 AI 代理来自动执行一系列编辑器操作（如打开关卡、运行测试、打包项目）以进行持续集成。
- **智能编辑器扩展**：你希望开发一个编辑器插件，允许用户通过对话框与 AI 交互来完成复杂的蓝图逻辑编写或材质调整。
- **工具链集成**：你的团队使用基于 MCP 的外部工具链，需要将 Unreal Engine 作为其中一个可编程节点集成进去。

## 蓝图用法

该插件主要通过 C++ 模块和蓝图工具库（Tool Library）资产提供功能。核心的蓝图交互点在于创建和使用 **MCP 工具库**。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create MCP Tool Library` | 在内容浏览器中通过右键菜单创建一个新的 MCP 工具库蓝图资产。 | `UModelContextProtocolToolLibraryFactory` |
| `Create MCP Editor Tool Library` | 创建一个编辑器专用的 MCP 工具库蓝图，可使用编辑器专用节点。 | `UModelContextProtocolEditorToolLibraryFactory` |

### 使用示例（蓝图描述）

1.  **创建工具库**：在内容浏览器空白处右键，选择 “Blueprints” -> “MCP Tool Library” 或 “MCP Editor Tool Library” 来创建一个新的蓝图资产。
2.  **定义工具函数**：打开该蓝图，在 “My Blueprint” 面板中添加新的 “Public” 函数。为函数添加详细的 Doxygen 风格注释（`/** ... */`），这些注释将作为该工具对 AI 的描述和参数说明。
3.  **实现函数逻辑**：在函数图表中实现具体逻辑，例如使用标准的蓝图节点查询或修改游戏世界。
4.  **注册与使用**：当插件模块启动时，会自动扫描并注册所有此类工具库中定义的公共函数，使其作为 MCP 工具对连接的 AI 客户端可用。

## C++ 用法

### 头文件引入

```cpp
// 引入编辑器模块适配器管理器
#include "ModelContextProtocolEditor.h"
// 引入工具集注册表适配器
#include "ModelContextProtocolToolsetRegistryAdapter.h"
```

### 基本用法

该模块的核心是 `FToolsetRegistryToolAdapterManager`，它负责将 UE 内部的“工具集注册表”（ToolsetRegistry）中的工具桥接到 MCP 服务器。

```cpp
// 来源: Engine/Plugins/Experimental/ModelContextProtocol/Source/ModelContextProtocolEditor/Public/ModelContextProtocolEditor.h
// 在你的编辑器模块或子系统中
class FMyEditorSubsystem
{
    FToolsetRegistryToolAdapterManager ToolsetAdapterManager;

    void Initialize()
    {
        // 注册所有来自 ToolsetRegistry 的工具到 MCP 服务器
        // 支持“急切”模式（一次性注册所有）和“延迟”模式（通过 list_toolsets 等工具按需加载）
        ToolsetAdapterManager.RegisterTools();
    }

    void Deinitialize()
    {
        // 注销所有已注册的工具
        ToolsetAdapterManager.DeregisterTools();
    }
};
```

### 进阶用法

你可以创建自定义的 MCP 工具适配器，将任何 C++ 功能暴露给 AI。

```cpp
// 来源: Engine/Plugins/Experimental/ModelContextProtocol/Source/ModelContextProtocolEditor/Private/ModelContextProtocolToolsetRegistryAdapter.h
// 定义一个自定义工具
struct FMyCustomTool : IModelContextProtocolTool
{
    virtual FString GetName() const override { return TEXT("my_custom_tool"); }
    virtual FString GetDescription() const override { return TEXT("Performs a custom operation."); }
    virtual TSharedPtr<FJsonObject> GetInputJsonSchema() const override
    {
        // 定义 JSON Schema 来描述输入参数
        TSharedPtr<FJsonObject> Schema = MakeShareable(new FJsonObject);
        Schema->SetStringField(TEXT("type"), TEXT("object"));
        // ... 添加 properties 定义
        return Schema;
    }

    // 同步执行版本
    virtual FModelContextProtocolToolResult Run(const TSharedPtr<FJsonObject>& Params) override
    {
        // 解析 Params 并执行逻辑
        // ...
        return FModelContextProtocolToolResult(TEXT("Success"));
    }

    // 或者异步执行版本
    virtual void RunAsync(const FModelContextProtocolToolRequestId& RequestId, const TSharedPtr<FJsonObject>& Params, const FResultCallback& OnComplete) override
    {
        // 启动异步任务
        Async(EAsyncExecution::ThreadPool, [this, RequestId, Params, OnComplete]()
        {
            // ... 执行耗时操作
            FModelContextProtocolToolResult Result(TEXT("Async operation completed"));
            // 回调通知完成
            OnComplete.ExecuteIfBound(RequestId, Result);
        });
    }
};

// 然后，你需要将这个工具注册到 MCP 模块中（通常通过模块启动时的逻辑）。
```

## Demo 示例

以下是一个最小化的编辑器子系统示例，展示如何集成 MCP 工具集管理器。

**MyMCPSubsystem.h**
```cpp
#pragma once

#include "ModelContextProtocolToolsetRegistryAdapter.h"
#include "Subsystems/EditorSubsystem.h"
#include "MyMCPSubsystem.generated.h"

UCLASS()
class UMyMCPSubsystem : public UEditorSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

private:
    FToolsetRegistryToolAdapterManager ToolsetAdapterManager;
};
```

**MyMCPSubsystem.cpp**
```cpp
#include "MyMCPSubsystem.h"

void UMyMCPSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    // 注册所有可用的工具集到 MCP 服务器
    ToolsetAdapterManager.RegisterTools();
}

void UMyMCPSubsystem::Deinitialize()
{
    // 清理：注销所有工具
    ToolsetAdapterManager.DeregisterTools();
    Super::Deinitialize();
}
```

## 模块依赖

要使用 `ModelContextProtocolEditor` 模块，你的模块需要在 `.Build.cs` 中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `ModelContextProtocol` | MCP 协议核心实现和工具接口定义。 |
| `ToolsetRegistry` | UE 内部的工具集注册表系统，是本模块桥接的主要数据源。 |

## 维护状态

### 近期更新

- 2026-04-24 `626f7a76` [ModelContextProtocol] Strict-type check for `isError` field in `IsToolResultSuccess`.
- 2026-04-22 `8be45e82` [ModelContextProtocol] Log tool call results at *VeryVerbose* for symmetry with input logging.
- 2026-04-22 `b103f5fa` [ModelContextProtocol] Add analytics instrumentation for tool calls and sessions.
- 2026-04-19 `f4f92133` [ModelContextProtocol] Fix flaky `ToolsetRegistry.Deferred` tests by dropping `bConnected` assertion
- 2026-04-18 `6471b168` [AIAssistant] Change how UToolsetDefinitions determine which UFunctions are tools,.

### 维护评价

- **创建时间**：非常新（约 1 年），属于实验性功能。
- **状态**：**实验性** (`IsExperimentalVersion: true`)，且默认未启用 (`EnabledByDefault: false`)。这表明它仍处于早期开发或概念验证阶段。
- **推荐度**：**谨慎使用**。适合用于研究、原型开发或内部工具链集成。不建议在需要长期稳定性的生产项目中依赖此插件，因为其 API 和功能可能会发生重大变更。建议密切关注 Epic Games 的官方更新日志和路线图。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ModelContextProtocol)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ModelContextProtocol/Source/ModelContextProtocolEditorTests)