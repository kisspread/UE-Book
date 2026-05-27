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

ModelContextProtocol 插件在 Unreal Engine 中实现了一个 **MCP (Model Context Protocol) 服务器**，使外部 AI 编码助手（如 Claude Code、Cursor、VS Code Copilot、Gemini CLI、Codex CLI）能够通过标准化的 HTTP 协议与 Unreal Engine 编辑器进行双向通信。

核心解决的问题是：**让 AI 编码工具能够"理解"和"操控"你的 UE 项目**。通过 MCP 协议，AI 助手可以：

- 调用 UE 中注册的 **Tool**（工具函数），执行引擎操作并获取结果
- 获取函数的 **JSON Schema** 描述，理解每个工具的输入输出格式
- 接收 **图像**（UTexture2D）和 **音频**（USoundWave）类型的返回结果
- 通过自动生成的配置文件快速接入各种 AI 客户端

插件还提供了 **分析事件代理**，将 MCP 相关的使用数据转发到引擎的 FAnalytics 系统中。

> ⚠️ **注意**：此插件标记为实验性（`IsExperimentalVersion=true`），且默认不启用（`EnabledByDefault=false`）。需要在项目设置中手动启用。

## 使用场景

- 你正在使用 **Claude Code / Cursor / VS Code Copilot** 等 AI 编码工具，希望它能直接操控 UE 编辑器 → 启用此插件，AI 助手可以通过 MCP 协议调用你注册的引擎工具
- 你需要将 UE 编辑器中的 **蓝图函数** 或 **C++ 函数** 暴露给 AI 助手作为可调用工具 → 继承 `UModelContextProtocolToolLibrary` 或 `UModelContextProtocolToolAsyncAction` 注册工具
- 你需要让 AI 助手能够 **查看游戏截图、材质预览** 等视觉信息 → 使用 `MakeImageResult` 返回图像内容
- 你需要为团队快速配置 AI 编码环境 → 使用 `WriteAllClientConfigurations` 一键生成所有客户端配置文件

## 蓝图用法

### 工具注册（蓝图）

通过 **MCP Tool Library** 蓝图资产注册工具：

1. 在 Content Browser 中右键 → **Add** → **MCP Tool Library**
2. 打开蓝图，添加 **Public** 函数
3. 函数的 **Tooltip**（注释）会自动成为工具的描述
4. 函数参数会自动生成 JSON Schema

> ⚠️ `UModelContextProtocolToolLibrary` 和 `UModelContextProtocolToolAsyncAction` 已标记为 **Deprecated**，推荐使用 `UToolsetDefinition`（ToolsetRegistry 插件）。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `WriteClientConfiguration` | 为指定 AI 客户端生成 MCP 配置文件 | `UE::ModelContextProtocol` |
| `WriteAllClientConfigurations` | 为所有支持的 AI 客户端生成配置文件 | `UE::ModelContextProtocol` |
| `MakeImageResult` | 将 UTexture2D 或 FImageView 转换为 MCP 图像结果 | `UE::ModelContextProtocol` |
| `MakeAudioResult` | 将 USoundWave 转换为 MCP 音频结果 | `UE::ModelContextProtocol` |

### 使用示例（蓝图描述）

**生成客户端配置文件**：
1. 获取服务器端口号（从 `UModelContextProtocolSettings` 读取）
2. 调用 `WriteAllClientConfigurations(Port, "/mcp")` 一键生成所有配置
3. 或调用 `WriteClientConfiguration(EModelContextProtocolClient::ClaudeCode, Port, "/mcp")` 仅生成 Claude Code 配置

**返回图像结果**：
1. 获取一个 `UTexture2D` 引用
2. 调用 `MakeImageResult(Texture, TEXT("jpeg"))` 转换为 MCP 格式
3. 将返回的 `FModelContextProtocolToolResult` 作为工具输出

## C++ 用法

### 头文件引入

```cpp
#include "ModelContextProtocolClientConfig.h"
#include "ModelContextProtocolSettings.h"
#include "ModelContextProtocolEngineToolResults.h"
#include "ModelContextProtocolEngineMetaData.h"
#include "ModelContextProtocolToolUtils.h"
```

### 基本用法

**生成 AI 客户端配置文件**：

```cpp
// Source/ModelContextProtocolEngine/Public/ModelContextProtocolClientConfig.h

// 为 Claude Code 生成 .mcp.json 配置
bool bSuccess = UE::ModelContextProtocol::WriteClientConfiguration(
    EModelContextProtocolClient::ClaudeCode,
    8000,           // 端口号
    TEXT("/mcp"),   // URL 路径
    FPaths::ProjectDir()  // 配置文件输出目录
);

// 一次性为所有支持的客户端生成配置
int32 FilesWritten = UE::ModelContextProtocol::WriteAllClientConfigurations(
    8000,
    TEXT("/mcp"),
    FPaths::ProjectDir()
);
// FilesWritten = 成功写入的配置文件数量
```

**读取 MCP 服务器设置**：

```cpp
// Source/ModelContextProtocolEngine/Public/ModelContextProtocolSettings.h

// 获取服务器配置（来自项目设置）
bool bAutoStart = UE::ModelContextProtocol::ShouldAutoStartServer();
uint32 Port = UE::ModelContextProtocol::GetServerPortNumber();
FString UrlPath = UE::ModelContextProtocol::GetServerUrlPath();
// 默认值: Port=8000, UrlPath="/mcp"
```

### 进阶用法

**创建图像和音频类型的工具结果**：

```cpp
// Source/ModelContextProtocolEngine/Public/ModelContextProtocolEngineToolResults.h

// 从 UTexture2D 创建图像结果（MCP Image Content）
UTexture2D* MyTexture = /* ... */;
FModelContextProtocolToolResult ImageResult = UE::ModelContextProtocol::MakeImageResult(
    MyTexture,
    TEXT("jpeg"),  // 输出格式
    EModelContextProtocolAudience::All
);

// 从 FImageView 创建图像结果
FImageView ImageView = /* ... */;
FModelContextProtocolToolResult ImageResult2 = UE::ModelContextProtocol::MakeImageResult(
    ImageView,
    TEXT("png")
);

// 从 USoundWave 创建音频结果（MCP Audio Content）
USoundWave* MySound = /* ... */;
FModelContextProtocolToolResult AudioResult = UE::ModelContextProtocol::MakeAudioResult(MySound);
```

**收集 UFunction 元数据用于 Schema 生成**：

```cpp
// Source/ModelContextProtocolEngine/Public/ModelContextProtocolEngineMetaData.h

#if WITH_EDITORONLY_DATA
// 收集函数的编辑器元数据（用于 JSON Schema 生成）
const UFunction* MyFunction = /* ... */;
FJsonSchemaPropertyFilter Filter = /* ... */;
FModelContextProtocolFunctionMetaData MetaData = 
    UE::ModelContextProtocol::CollectFunctionMetaData(MyFunction, Filter);
#endif

// 将 cookable 元数据转换为编辑器元数据
FJsonSchemaEditorMetadata EditorMeta = 
    UE::ModelContextProtocol::ConvertToCachedEditorMetadata(MetaData);
```

**获取工具结果类型和值**：

```cpp
// Source/ModelContextProtocolEngine/Public/ModelContextProtocolToolUtils.h

FProperty* ResultProperty = /* ... */;
FModelContextProtocolFunctionMetaData* MetaData = /* ... */;
TSharedPtr<FJsonObject> OutSchema;

// 判断工具结果类型
EModelContextProtocolToolResultType ResultType = 
    UE::ModelContextProtocol::GetToolResultType(ResultProperty, MetaData, OutSchema);

// 根据类型提取结果值
FModelContextProtocolToolResult Result = 
    UE::ModelContextProtocol::GetToolResultFromType(ResultType, ResultProperty, Container, ReturnValueOffset);
```

## Demo 示例

### 自定义 MCP 工具库（C++）

```cpp
// MyGameTools.h
#pragma once

#include "ModelContextProtocolToolLibrary.h"
#include "MyGameTools.generated.h"

/**
 * 游戏相关的 MCP 工具库，暴露给 AI 助手使用。
 * 每个 public UFUNCTION 都会自动注册为一个 MCP Tool。
 */
UCLASS(BlueprintType)
class UMyGameTools : public UModelContextProtocolToolLibrary
{
    GENERATED_BODY()

public:
    /**
     * 获取当前关卡中所有 Actor 的数量。
     * @return 关卡中的 Actor 总数
     */
    UFUNCTION(BlueprintCallable, Category = "MCP Tools")
    static int32 GetActorCount();

    /**
     * 设置指定 Actor 的位置。
     * @param ActorName 要移动的 Actor 名称
     * @param NewLocation 目标世界坐标位置
     * @return 是否成功移动
     */
    UFUNCTION(BlueprintCallable, Category = "MCP Tools")
    static bool SetActorLocation(const FString& ActorName, const FVector& NewLocation);
};
```

```cpp
// MyGameTools.cpp
#include "MyGameTools.h"
#include "Engine/World.h"

int32 UMyGameTools::GetActorCount()
{
    UWorld* World = GEngine->GetWorldContexts()[0].World();
    if (!World) return 0;

    int32 Count = 0;
    for (TActorIterator<AActor> It(World); It; ++It)
    {
        Count++;
    }
    return Count;
}

bool UMyGameTools::SetActorLocation(const FString& ActorName, const FVector& NewLocation)
{
    UWorld* World = GEngine->GetWorldContexts()[0].World();
    if (!World) return false;

    for (TActorIterator<AActor> It(World); It; ++It)
    {
        if (It->GetName() == ActorName)
        {
            It->SetActorLocation(NewLocation);
            return true;
        }
    }
    return false;
}
```

> 注：`UModelContextProtocolToolLibrary` 已标记为 Deprecated。新项目建议使用 `UToolsetDefinition`（ToolsetRegistry 插件）。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AnalyticsET` | 引擎分析事件系统，用于 MCP 使用数据上报 |
| `Json` | JSON 解析与生成，用于 MCP 协议通信和 Schema 定义 |
| `JsonSchema` | JSON Schema 生成，用于描述工具的输入输出格式 |
| `ToolsetRegistry` | 新一代工具注册系统（替代已废弃的 ToolLibrary/AsyncAction） |
| `HTTPServer` | HTTP 服务器，承载 MCP 协议的 HTTP 端点 |
| `ModelContextProtocol` | 核心 MCP 协议实现模块 |

## 维护状态

### 近期更新

- 2026-04-24 `626f7a76` [ModelContextProtocol] Strict-type check for `isError` field in `IsToolResultSuccess`.
- 2026-04-22 `8be45e82` [ModelContextProtocol] Log tool call results at *VeryVerbose* for symmetry with input logging.
- 2026-04-22 `b103f5fa` [ModelContextProtocol] Add analytics instrumentation for tool calls and sessions.
- 2026-04-19 `f4f92133` [ModelContextProtocol] Fix flaky `ToolsetRegistry.Deferred` tests by dropping `bConnected` assertion
- 2026-04-18 `6471b168` [AIAssistant] Change how UToolsetDefinitions determine which UFunctions are tools,.

### 维护评价

- **创建时间**：2026-04-18，全新插件
- **实验性标记**：`IsExperimentalVersion=true`，`EnabledByDefault=false`，明确标记为实验性
- **废弃警告**：`UModelContextProtocolToolLibrary` 和 `UModelContextProtocolToolAsyncAction` 已标记为 Deprecated，推荐迁移到 `UToolsetDefinition`（ToolsetRegistry 插件），说明架构仍在快速迭代
- **模块结构**：6 个模块（含 3 个测试模块），结构清晰，测试覆盖良好
- **NoRedist**：标记为 `NoRedist=true`，不可重新分发

**综合评价**：这是一个全新的实验性插件，正处于活跃开发阶段。API 可能会发生重大变化（已有废弃标记为证）。适合早期探索和实验使用，不建议在生产环境中依赖。推荐关注 ToolsetRegistry 插件作为更稳定的工具注册方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ModelContextProtocol)
- [MCP 协议规范](https://modelcontextprotocol.io/specification/2025-06-18/server/tools)