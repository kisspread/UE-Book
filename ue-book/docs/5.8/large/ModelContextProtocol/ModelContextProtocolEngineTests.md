# Unreal MCP

> Anthropic MCP (Model Context Protocol) server implementation for Unreal Engine.

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ModelContextProtocol` (Runtime), `ModelContextProtocolEditor` (Runtime), `ModelContextProtocolEngine` (Runtime), `ModelContextProtocolEditorTests` (Runtime), `ModelContextProtocolEngineTests` (Runtime), `ModelContextProtocolTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-18 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ModelContextProtocol) | |

## 用途

ModelContextProtocol 插件在 Unreal Engine 中实现了 Anthropic 的 MCP（Model Context Protocol）服务器。MCP 是一种开放协议，允许 AI 助手（如 Claude）与外部工具和数据源进行标准化通信。

该插件解决的核心问题是：**让 AI 模型能够直接与 Unreal Engine 编辑器交互**。通过 MCP 协议，外部 AI 客户端可以：

- 查询和操作编辑器中的资产（Assets）
- 执行引擎命令和蓝图操作
- 获取项目结构和场景信息
- 自动化编辑器工作流

插件采用模块化架构，分为核心协议层（`ModelContextProtocol`）、编辑器集成层（`ModelContextProtocolEditor`）、引擎集成层（`ModelContextProtocolEngine`），以及对应的测试模块。

## 使用场景

- 你正在开发 AI 辅助工具，需要让 AI 助手能够读取和操作 UE 项目内容 → 使用此插件作为 MCP 服务器端点
- 你需要通过 Claude Desktop 或其他 MCP 客户端自动化编辑器操作 → 启用此插件并配置 MCP 客户端连接
- 你在构建 AI 驱动的内容生成管线，需要程序化控制编辑器 → 通过 MCP 协议暴露引擎功能给 AI

## 蓝图用法

本插件主要作为 MCP 服务器运行，对外暴露编辑器和引擎功能。核心交互通过 MCP 协议完成，而非直接的蓝图节点。插件运行后会启动一个 MCP 服务器，外部客户端通过标准 MCP 协议与之通信。

### 核心概念

| 概念 | 说明 |
|---|---|
| MCP Server | 插件启动的协议服务器，监听外部 AI 客户端的请求 |
| Tools | 暴露给 AI 的可执行操作（如创建资产、修改属性） |
| Resources | 暴露给 AI 的可读数据（如项目结构、场景信息） |

## C++ 用法

### 头文件引入

```cpp
#include "ModelContextProtocol.h"
```

### 基本用法

MCP 服务器通常由插件自动管理生命周期。开发者主要关注的是扩展 MCP 的 Tools 和 Resources：

```cpp
// MCP 服务器在插件启动时自动初始化
// 外部客户端通过标准 MCP 协议连接
// 具体的 Tool/Resource 注册请参考各子模块实现
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ModelContextProtocol` | 核心 MCP 协议实现，提供服务器框架和协议处理 |
| `ModelContextProtocolEditor` | 编辑器集成，暴露编辑器相关功能给 MCP |
| `ModelContextProtocolEngine` | 引擎集成，暴露运行时引擎功能给 MCP |

## 维护状态

### 近期更新

- 2026-04-24 `626f7a76` [ModelContextProtocol] Strict-type check for `isError` field in `IsToolResultSuccess`.
- 2026-04-22 `8be45e82` [ModelContextProtocol] Log tool call results at *VeryVerbose* for symmetry with input logging.
- 2026-04-22 `b103f5fa` [ModelContextProtocol] Add analytics instrumentation for tool calls and sessions.
- 2026-04-19 `f4f92133` [ModelContextProtocol] Fix flaky `ToolsetRegistry.Deferred` tests by dropping `bConnected` assertion
- 2026-04-18 `6471b168` [AIAssistant] Change how UToolsetDefinitions determine which UFunctions are tools,.

### 维护评价

- **状态**：实验性插件，刚创建不久
- **IsExperimentalVersion = true**：Epic 将其标记为实验性，API 可能发生重大变化
- **EnabledByDefault = false**：需要手动启用
- **测试覆盖**：包含 3 个独立测试模块（`ModelContextProtocolTests`、`ModelContextProtocolEditorTests`、`ModelContextProtocolEngineTests`），表明 Epic 对质量有一定重视
- **推荐**：适合早期探索和实验，不建议在生产环境中使用。关注后续版本更新，MCP 协议生态正在快速发展

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ModelContextProtocol)
- [MCP 协议规范](https://modelcontextprotocol.io/)