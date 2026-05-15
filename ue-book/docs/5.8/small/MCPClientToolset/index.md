# MCP Client Toolset

> An adapter that allows toolset registry customers (like the EDA) to connect to local/private MCP servers.

| 属性 | 值 |
|---|---|
| 中文名 | MCP 客户端工具集 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MCPClientToolset` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-01 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/MCPClientToolset) | |

## 用途

MCPClientToolset 是一个 UE5 编辑器插件，它实现了 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) 的客户端。其主要功能是作为 UE5 工具注册系统（Toolset Registry）与外部 MCP 服务器之间的桥梁。

这个插件解决的核心问题是：**让 UE5 编辑器能够发现并调用部署在本地或私有网络中的 AI 服务（MCP 服务器）所提供的工具**。它处理了与 MCP 服务器通信的复杂细节，包括多种传输协议（Legacy SSE 和 Streamable HTTP）和认证方式（静态 API Key 或 OAuth 2.0），使得编辑器内的其他系统（如 EDA）可以透明地使用这些远程 AI 工具，就像使用本地工具一样。

## 使用场景

-   **集成外部 AI 服务**：你已经部署了一个 MCP 服务器（例如，用于代码生成、资产创建或场景分析的 AI 服务），并希望直接在 UE5 编辑器的工具链（如编辑器中的某个面板或自动化脚本）中调用它。
-   **扩展编辑器功能**：你希望将 UE5 编辑器不具备的功能（如调用外部 API 进行翻译、数据检索或特定领域的 AI 推理）作为“工具”暴露给编辑器内的 AI 代理或用户界面。
-   **开发 AI 辅助工作流**：你正在构建一个基于 AI 的编辑器扩展，需要一种标准化的方式（MCP）来连接不同的 AI 后端服务。

## 蓝图用法

该插件的核心功能（连接管理、工具执行）主要由 C++ 类 `FMCPClientToolset` 驱动，由编辑器子系统 `UMCPClientToolsetSubsystem` 管理。蓝图主要用于**配置**，而非直接调用核心功能。

### 核心配置节点

配置通过 **编辑器偏好设置（Editor Preferences）** 进行，路径为：`Plugins > MCP Toolset Servers`。

| 配置项 | 说明 | 所在类/结构 |
|---|---|---|
| `MCPServers` | MCP 服务器配置列表，每个条目定义了一个连接。 | `UMCPToolsetSettings` |
| `Name` | 该工具集在注册系统中的显示名称。 | `FMCPServerConfig` |
| `Description` | 工具集描述，会提供给 AI 作为上下文。 | `FMCPServerConfig` |
| `ServerUrl` | MCP 服务器的基础 URL (例如 `http://localhost:3000`)。 | `FMCPServerConfig` |
| `bEnabled` | 是否启用该配置。 | `FMCPServerConfig` |
| `Transport` | 选择传输协议：`Legacy SSE` 或 `Streamable HTTP`。 | `FMCPServerConfig` |
| `Auth` | 选择认证方式：`None`, `Bearer Token` 或 `OAuth 2.0`。 | `FMCPServerConfig` |
| `ApiKey` | 当认证方式为 `Bearer Token` 时使用的 API 密钥。 | `FMCPServerConfig` |
| `OAuthClientId` | 当认证方式为 `OAuth 2.0` 时的客户端 ID。留空则使用动态注册。 | `FMCPServerConfig` |
| `OAuthScope` | OAuth 2.0 的 Scope 字符串。 | `FMCPServerConfig` |

## C++ 用法

### 头文件引入

```cpp
#include "MCPClientToolset/MCPClientToolset.h"
```

### 基本用法：创建并执行一个工具

此示例展示了如何手动创建一个 `FMCPClientToolset` 实例并调用一个远程工具。通常，这些实例已由 `UMCPClientToolsetSubsystem` 根据配置自动创建并注册。

```cpp
// 定义配置
UE::ToolsetRegistry::FMCPClientToolset::FConfig Config;
Config.Name = TEXT("MyAIServer");
Config.ServerUrl = TEXT("http://localhost:3000");
Config.bStreamableHTTP = true; // 或使用 Legacy SSE (默认)
Config.ApiKey = TEXT("your-api-key"); // 或通过 Auth 设置 OAuth

// 异步创建工具集实例
TFuture<TValueOrError<TSharedPtr<UE::ToolsetRegistry::FMCPClientToolset>, FString>> Future =
    UE::ToolsetRegistry::FMCPClientToolset::Create(Config);

Future.Then([](TValueOrError<TSharedPtr<UE::ToolsetRegistry::FMCPClientToolset>, FString> Result)
{
    if (Result.HasValue())
    {
        TSharedPtr<UE::ToolsetRegistry::FMCPClientToolset> Toolset = Result.GetValue();

        // 获取该服务器提供的工具 JSON Schema (用于描述可用的工具)
        FString SchemaJson = Toolset->GetJsonSchemaInternal();
        UE_LOG(LogTemp, Log, TEXT("Tool Schema: %s"), *SchemaJson);

        // 异步执行一个工具
        TFuture<TValueOrError<FString, FString>> ExecutionFuture =
            Toolset->ExecuteToolInternal(
                TEXT("generate_code"), // 工具名称
                TEXT(R"({"prompt": "Create a simple actor class"})") // JSON 格式的输入
            );

        ExecutionFuture.Then([](TValueOrError<FString, FString> ExecResult)
        {
            if (ExecResult.HasValue())
            {
                UE_LOG(LogTemp, Log, TEXT("Tool result: %s"), *ExecResult.GetValue());
            }
            else
            {
                UE_LOG(LogTemp, Error, TEXT("Tool execution failed: %s"), *ExecResult.GetError());
            }
        });
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create MCP Toolset: %s"), *Result.GetError());
    }
});
```

### 进阶用法：监听子系统的工具集注册

编辑器子系统 `UMCPClientToolsetSubsystem` 会在初始化时根据 `UMCPToolsetSettings` 自动创建和注册所有启用的 `FMCPClientToolset`。你可以监听 `UToolsetRegistrySubsystem` 的变化来知道何时有新的外部 AI 工具可用。

```cpp
#include "ToolsetRegistry/ToolsetRegistrySubsystem.h"

// 获取工具集注册子系统
UToolsetRegistrySubsystem* RegistrySubsystem = GEditor->GetEditorSubsystem<UToolsetRegistrySubsystem>();
if (RegistrySubsystem)
{
    // 可以获取所有已注册的工具集（包括其他本地工具集和 MCP 远程工具集）
    TArray<TSharedPtr<UE::ToolsetRegistry::FToolset>> AllToolsets = RegistrySubsystem->GetAllToolsets();

    for (const auto& Toolset : AllToolsets)
    {
        // 检查是否是我们关注的 MCP 工具集
        if (Toolset->GetToolsetName() == TEXT("MyAIServer"))
        {
            UE_LOG(LogTemp, Log, TEXT("Found MCP Toolset: %s - %s"),
                *Toolset->GetToolsetName(), *Toolset->GetToolsetDescription());

            // 通过注册系统执行工具（系统会处理调度）
            TFuture<TValueOrError<FString, FString>> ResultFuture =
                RegistrySubsystem->ExecuteTool(Toolset->GetToolsetName(), TEXT("tool_name"), TEXT("{}"));
            // ... 处理 Future
        }
    }
}
```

## Demo 示例

一个最小化的示例，展示如何在编辑器模块中配置和使用 MCP 工具集。

**MyMCPDemoModule.h**
```cpp
#pragma once
#include "Modules/ModuleManager.h"

class FMyMCPDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    void DemoMCPUsage();
};
```

**MyMCPDemoModule.cpp**
```cpp
#include "MyMCPDemoModule.h"
#include "MCPClientToolset/MCPClientToolset.h"
#include "ToolsetRegistry/ToolsetRegistrySubsystem.h"

#define LOCTEXT_NAMESPACE "FMyMCPDemoModule"

void FMyMCPDemoModule::StartupModule()
{
    // 通常，MCP 服务器配置在 Editor Preferences 中完成。
    // 这里演示如何以编程方式（例如，在某个编辑器按钮点击后）临时创建一个连接并执行工具。
    // 注意：生产环境中推荐使用配置。
    FCoreDelegates::OnPostEngineInit.AddLambda([this]()
    {
        DemoMCPUsage();
    });
}

void FMyMCPDemoModule::ShutdownModule()
{
    // 清理资源（如果需要）
}

void FMyMCPDemoModule::DemoMCPUsage()
{
    UE_LOG(LogTemp, Log, TEXT("Starting MCP Client Toolset Demo"));

    // 配置一个临时的 MCP 服务器
    UE::ToolsetRegistry::FMCPClientToolset::FConfig Config;
    Config.Name = TEXT("DemoMCPServer");
    Config.ServerUrl = TEXT("http://localhost:8080"); // 假设你的 MCP 服务器运行在此
    Config.bStreamableHTTP = true;

    // 创建工具集
    auto CreateFuture = UE::ToolsetRegistry::FMCPClientToolset::Create(Config);
    CreateFuture.Then([Config](TValueOrError<TSharedPtr<UE::ToolsetRegistry::FMCPClientToolset>, FString> Result)
    {
        if (!Result.HasValue())
        {
            UE_LOG(LogTemp, Error, TEXT("Failed to connect to MCP server '%s': %s"),
                *Config.Name, *Result.GetError());
            return;
        }

        auto Toolset = Result.GetValue();
        UE_LOG(LogTemp, Log, TEXT("Successfully connected to MCP server '%s' (version: %s)"),
            *Toolset->GetToolsetName(), *Toolset->GetToolsetVersion());

        // 获取服务器支持的工具模式
        FString Schema = Toolset->GetJsonSchemaInternal();
        UE_LOG(LogTemp, Log, TEXT("Available Tools Schema:\n%s"), *Schema);

        // 假设服务器提供了一个名为 `summarize` 的工具，我们尝试调用它。
        FString ToolName = TEXT("summarize");
        FString InputJson = TEXT(R"({"text": "Unreal Engine is a complete suite of development tools for anyone working with real-time technology."})");

        auto ExecFuture = Toolset->ExecuteToolInternal(ToolName, InputJson);
        ExecFuture.Then([ToolName](TValueOrError<FString, FString> ExecResult)
        {
            if (ExecResult.HasValue())
            {
                UE_LOG(LogTemp, Log, TEXT("Tool '%s' executed successfully:\n%s"),
                    *ToolName, *ExecResult.GetValue());
            }
            else
            {
                UE_LOG(LogTemp, Error, TEXT("Tool '%s' failed: %s"),
                    *ToolName, *ExecResult.GetError());
            }
        });
    });
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyMCPDemoModule, MyMCPDemo)
```

## 模块依赖

从 `MCPClientToolset.Build.cs` 分析，使用该插件需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `ToolsetRegistry` | 核心依赖。提供 `FToolset` 基类和 `UToolsetRegistrySubsystem` 管理器。 |
| `HTTP`, `HTTPServer` | 用于实现与 MCP 服务器的通信（SSE, Streamable HTTP）以及处理 OAuth 回调。 |
| `Json`, `JsonUtilities` | 用于处理 MCP 协议中的 JSON-RPC 消息。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-28 | `ce5526cc` | Add support for disabling toolsets and tools by name. | 新增按名称禁用工具集和工具的功能。 |
| 2026-04-16 | `6605f684` | [MCP] Add deferred tool loading to ModelContextProtocol server | 为 MCP 服务器添加了延迟加载工具的机制。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF。 |
| 2026-04-09 | `65c955c0` | MCPToolsetSettings - change back to Config=DefaultPerProjectUserSettings to fix serialization issues | 修复了设置序列化问题，将配置存储位置改回默认。 |
| 2026-04-06 | `19e89d93` | Change MCPToolsetSettings config to Editor so that it's set at a per-user level | 将配置作用域改为编辑器，实现按用户保存设置。 |

### 维护评价

该插件**处于活跃开发的实验阶段**。

-   **年龄**：插件创建于 2026 年 4 月，非常年轻。
-   **更新频率**：从提交历史看，在创建后的第一个月内有多次更新，包括功能增强（禁用工具、延迟加载）、维护性重构（日志宏）和重要的 Bug 修复（配置序列化），表明 Epic 工程师正在积极迭代。
-   **状态**：`.uplugin` 中明确标记 `IsBetaVersion: true` 和 `IsExperimentalVersion: true`，并且默认不启用（`EnabledByDefault: false`）。这属于 UE5 的早期实验性功能。
-   **建议**：可以用于内部原型开发和技术探索，体验与外部 MCP 服务的集成。**不建议**在需要高度稳定性的生产项目中依赖此插件。API 和行为可能会在未来的版本中发生重大变更。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/MCPClientToolset)
-   [官方文档]() (无)
-   [测试用例]() (未在提供的信息中发现)