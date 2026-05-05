# MCP Client Toolset

> An adapter that allows toolset registry customers (like the EDA) to connect to local/private MCP servers.

| 属性 | 值 |
|---|---|
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MCPClientToolset` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-03 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/MCPClientToolset) | |

## 用途

MCPClientToolset 是一个**编辑器工具集适配器**，用于将 Unreal Engine 的 Toolset Registry 系统连接到外部的 MCP（Model Context Protocol）服务器。

MCP 是一种让 AI 模型与外部工具交互的标准化协议。这个插件的核心作用是：**让 UE 编辑器内的 AI 助手（如 EDA）能够调用运行在本地或私有网络上的 MCP 服务器提供的工具**。

插件支持三种连接方式：
- **Legacy SSE（HTTP+SSE）**：MCP 2025-03-26 之前的旧协议，通过 GET `/sse` 建立长连接事件流，POST `/message` 发送请求
- **Streamable HTTP**：MCP 2025-03-26 新协议，单一 POST 端点，响应为 JSON 或 SSE
- **OAuth 2.0 + PKCE**：在上述传输之上叠加 OAuth 认证，支持动态客户端注册（RFC 7591）

## 使用场景

- 你在使用 UE 编辑器的 AI 助手（EDA），需要它能调用本地运行的 MCP 工具服务器 → 配置此插件
- 你有一个私有部署的 MCP 服务器，提供自定义工具（如资产搜索、代码生成等）→ 通过此插件将其注册到 Toolset Registry
- 你需要通过 OAuth 2.0 认证连接到需要身份验证的 MCP 服务器 → 使用 OAuth 配置模式

## 蓝图用法

此插件主要通过**编辑器设置面板**配置，不提供蓝图可调用节点。配置路径：

**Editor Preferences → Plugins → MCP Toolset Servers**

### 配置项

| 配置项 | 类型 | 说明 |
|---|---|---|
| `Name` | `FString` | 工具集显示名称，在 Registry 中使用 |
| `Description` | `FString` | 人类可读描述，供 AI 作为上下文使用 |
| `ServerUrl` | `FString` | MCP 服务器基础 URL，如 `http://localhost:3000` |
| `ApiKey` | `FString` | 可选 API 密钥，以 Bearer Token 方式发送 |
| `bEnabled` | `bool` | 是否启用此服务器配置 |
| `Transport` | `EMCPTransport` | 传输协议：`SSE` 或 `StreamableHTTP` |
| `Auth` | `EMCPAuth` | 认证方式：`None`、`BearerToken` 或 `OAuth2` |
| `OAuthClientId` | `FString` | OAuth 客户端 ID（留空则使用动态注册） |
| `OAuthScope` | `FString` | OAuth 作用域，如 `"read:me offline_access"` |

### 枚举类型

**EMCPTransport** — 传输协议选择：
- `SSE`：Legacy SSE（HTTP+SSE），兼容 MCP 2025-03-26 之前的服务器
- `StreamableHTTP`：Streamable HTTP，MCP 2025-03-26 新规范

**EMCPAuth** — 认证方式选择：
- `None`：无认证
- `BearerToken`：Bearer Token（API Key）
- `OAuth2`：OAuth 2.0 Authorization Code + PKCE

## C++ 用法

### 头文件引入

```cpp
#include "MCPClientToolset/MCPClientToolset.h"
#include "MCPClientToolset/MCPClientToolsetSubsystem.h"
#include "MCPClientToolset/MCPToolsetSettings.h"
```

### 基本用法

通过异步工厂方法创建 MCP 客户端工具集实例：

```cpp
#include "MCPClientToolset/MCPClientToolset.h"

using namespace UE::ToolsetRegistry;

// 配置 MCP 服务器连接
FMCPClientToolset::FConfig Config;
Config.Name = TEXT("MyLocalTools");
Config.Description = TEXT("本地 MCP 工具服务器");
Config.ServerUrl = TEXT("http://localhost:3000");
Config.ApiKey = TEXT("my-secret-key");
Config.bStreamableHTTP = false;  // 使用 Legacy SSE
Config.bOAuth = false;           // 使用 API Key 认证

// 异步创建工具集实例
TFuture<TValueOrError<TSharedPtr<FMCPClientToolset>, FString>> Future =
    FMCPClientToolset::Create(Config);

Future.Next([](TValueOrError<TSharedPtr<FMCPClientToolset>, FString> Result)
{
    if (Result.HasValue())
    {
        TSharedPtr<FMCPClientToolset> Toolset = Result.GetValue();
        // 工具集已就绪，已自动注册到 Toolset Registry
    }
    else
    {
        UE_LOG(LogMCPClientToolset, Error, TEXT("Failed to create MCP toolset: %s"),
            *Result.GetError());
    }
});
```

### 进阶用法

使用 OAuth 2.0 + PKCE 认证连接到需要身份验证的 MCP 服务器：

```cpp
FMCPClientToolset::FConfig OAuthConfig;
OAuthConfig.Name = TEXT("SecureMCPTools");
OAuthConfig.Description = TEXT("需要 OAuth 认证的 MCP 服务器");
OAuthConfig.ServerUrl = TEXT("https://mcp.example.com");
OAuthConfig.bStreamableHTTP = true;  // 使用新协议
OAuthConfig.bOAuth = true;           // 启用 OAuth 2.0
OAuthConfig.OAuthClientId = TEXT("my-app-client-id");  // 留空则动态注册
OAuthConfig.OAuthScope = TEXT("read:me offline_access");

TFuture<TValueOrError<TSharedPtr<FMCPClientToolset>, FString>> Future =
    FMCPClientToolset::Create(OAuthConfig);

Future.Next([](TValueOrError<TSharedPtr<FMCPClientToolset>, FString> Result)
{
    if (Result.HasValue())
    {
        // OAuth 认证完成，工具集已就绪
        // 如果 OAuthClientId 为空，服务器会通过 RFC 7591 动态分配客户端 ID
    }
});
```

## Demo 示例

### 最小完整示例：在编辑器模块中注册 MCP 工具集

```cpp
// MyEditorModule.h
#pragma once

#include "Modules/ModuleManager.h"
#include "MCPClientToolset/MCPClientToolset.h"

class FMyEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    TSharedPtr<UE::ToolsetRegistry::FMCPClientToolset> MCPToolset;
};
```

```cpp
// MyEditorModule.cpp
#include "MyEditorModule.h"
#include "MCPClientToolset/MCPClientToolset.h"

#define LOCTEXT_NAMESPACE "MyEditorModule"

void FMyEditorModule::StartupModule()
{
    using namespace UE::ToolsetRegistry;

    FMCPClientToolset::FConfig Config;
    Config.Name = TEXT("MyMCPTools");
    Config.Description = TEXT("我的本地 MCP 工具");
    Config.ServerUrl = TEXT("http://localhost:3000");

    FMCPClientToolset::Create(Config).Next(
        [this](TValueOrError<TSharedPtr<FMCPClientToolset>, FString> Result)
        {
            if (Result.HasValue())
            {
                MCPToolset = Result.GetValue();
            }
        });
}

void FMyEditorModule::ShutdownModule()
{
    MCPToolset.Reset();
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyEditorModule, MyEditorModule)
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ToolsetRegistry` | 工具集注册系统，MCP 客户端工具集通过此模块注册到全局 Registry |

## 维护状态

### 近期更新

```
- 6605f684 2026-04-16 [MCP] Add deferred tool loading to ModelContextProtocol server
- 35e60df1 2026-04-14 Migrate UE_LOG to UE_LOGF.
- 65c955c0 2026-04-09 MCPToolsetSettings - change back to Config=DefaultPerProjectUserSettings to fix serialization issues
- 19e89d93 2026-04-06 Change MCPToolsetSettings config to Editor so that it's set at a per-user level
- aed04419 2026-04-03 [AI Toolsets]: Ensure all toolset plugins are marked as editor only.
```

### 维护评价

**活跃开发中** — 该插件创建于 2026-04-03，至今不到一个月，但已有 5 次提交，涵盖功能添加、日志迁移和配置序列化修复。

⚠️ **注意事项**：
- 标记为 `IsBetaVersion` 和 `IsExperimentalVersion`，API 可能随时变更
- `EnabledByDefault = false`，需要手动在插件管理器中启用
- 仅限编辑器使用（`EditorOnly: true`，模块 TargetAllowList 为 Editor）
- 依赖 ToolsetRegistry 插件，需确保该插件已启用
- 配置序列化仍在调整中（近期有两次关于 Config 类型的修复）

**推荐**：适合早期探索和测试 MCP 集成，不建议在生产环境中使用。如果你正在为 UE 编辑器 AI 助手开发 MCP 工具集成，可以开始试用，但需做好 API 变更的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/MCPClientToolset)
- [MCP 规范](https://modelcontextprotocol.io/)（Model Context Protocol 官方文档）