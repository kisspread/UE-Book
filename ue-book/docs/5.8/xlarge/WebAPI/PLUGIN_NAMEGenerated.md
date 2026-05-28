# WebAPI

> Automated generation of web based APIs

| 属性 | 值 |
|---|---|
| 中文名 | 网络 API 生成器 |
| 分类 | Web |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（模板资产、代码生成模板） |
| 模块 | `WebAPI` (Runtime), `WebAPIBlueprintGraph` (Runtime), `WebAPIEditor` (Runtime), `WebAPILiquidJS` (Runtime), `WebAPIOpenAPI` (Runtime), `PLUGIN_NAMEGenerated` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-07-11 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Web/WebAPI) | |

## 用途

WebAPI 插件提供了一套自动化的 Web API 代码生成框架，用于在 Unreal Engine 5 中快速构建基于 HTTP 的 RESTful API 服务端点。

该插件解决的核心问题是：**将 UE5 中的 C++ 函数和蓝图逻辑自动转换为可通过 HTTP 调用的 Web API**。它通过以下机制实现：

1. **注解驱动的 API 定义**：开发者在 C++ 类或蓝图函数上添加特定标记，插件自动生成对应的 HTTP 端点处理代码
2. **LiquidJS 模板引擎**（`WebAPILiquidJS` 模块）：使用 LiquidJS 模板语言生成 API 代码，支持灵活的代码生成格式定制
3. **OpenAPI 规范支持**（`WebAPIOpenAPI` 模块）：自动生成符合 OpenAPI/Swagger 规范的 API 文档，方便前后端对接
4. **蓝图图节点集成**（`WebAPIBlueprintGraph` 模块）：允许在蓝图编辑器中直接定义和管理 Web API 端点
5. **模板化代码输出**：`PLUGIN_NAMEGenerated` 模块作为生成代码的模板骨架，生成的 API 代码会被放置在以此为蓝本的独立模块中

简而言之，这是一个**服务器端 API 代码生成工具**，适用于需要在 UE5 Dedicated Server 或独立服务器中暴露 HTTP API 的场景。

## 使用场景

- 你需要在 UE5 Dedicated Server 中对外暴露 RESTful API，供 Web 前端或移动端调用
- 你正在开发一个带有 Web 管理后台的游戏服务器，需要自动生成 API 端点
- 你希望基于 OpenAPI 规范自动生成客户端 SDK 或 API 文档
- 你需要通过蓝图快速定义 HTTP 端点，而不想手写 C++ HTTP 处理代码
- 你希望将游戏服务器的业务逻辑以标准化的 Web API 形式暴露给第三方服务

## 蓝图用法

由于 `PLUGIN_NAMEGenerated` 模块仅为代码生成模板骨架，实际的蓝图 API 定义功能位于 `WebAPIBlueprintGraph` 模块中。基于模块结构推断，蓝图用法主要包括：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| API 端点定义节点 | 在蓝图图表中定义 HTTP 端点（路径、方法、参数） | `WebAPIBlueprintGraph` 模块提供 |
| 请求/响应数据处理 | 解析 HTTP 请求参数并构造响应 | `WebAPI` 核心模块提供 |

> **注意**：本插件为实验性插件（IsExperimentalVersion: true），蓝图图节点功能可能随版本变化。建议查看 `WebAPIBlueprintGraph` 模块源码确认最新可用节点。

### 使用示例（蓝图描述）

1. 在蓝图编辑器中，通过 `WebAPIBlueprintGraph` 提供的自定义节点定义一个新的 API 端点
2. 指定 HTTP 路径（如 `/api/v1/players`）和 HTTP 方法（GET/POST/PUT/DELETE）
3. 定义请求参数和响应数据结构
4. 编写处理逻辑，连接业务蓝图节点
5. 构建时，`WebAPIEditor` 和 `WebAPILiquidJS` 模块自动将蓝图定义转换为可编译的 C++ API 处理代码

## C++ 用法

### 头文件引入

```cpp
// 主 API 框架
#include "WebAPI.h"

// OpenAPI 规范支持（如需生成文档）
#include "WebAPIOpenAPI.h"

// 模板引擎（如需自定义代码生成）
#include "WebAPILiquidJS.h"
```

### 基本用法

基于插件结构推断的典型用法模式——在 C++ 类中通过标记定义 API 端点：

```cpp
// 在 C++ 类上使用特定的 UCLASS 宏标记，定义为 API 控制器
// 生成的代码会自动将其注册为 HTTP 端点处理程序

// 示例：定义一个简单的 API 控制器（基于插件结构推断）
UCLASS()
class UMyGameAPIController : public UObject
{
    GENERATED_BODY()

public:
    // 定义一个 GET /api/players 端点
    // 具体的标记宏和函数签名请参考 WebAPI 核心模块的头文件
    UFUNCTION()
    void GetPlayers(/* 请求参数 */);

    // 定义一个 POST /api/players 端点
    UFUNCTION()
    void CreatePlayer(/* 请求参数 */);
};
```

> **注意**：由于 `PLUGIN_NAMEGenerated` 模块仅包含日志类别声明，实际的 API 定义宏和基类需要参考 `WebAPI` 核心模块（`Engine/Plugins/Experimental/Web/WebAPI/Source/WebAPI/`）的公共头文件。

### 进阶用法

插件的代码生成流程涉及多个模块协作：

1. **定义阶段**：在 C++ 中使用 API 宏标记类和函数
2. **生成阶段**：`WebAPIEditor` 模块在编辑器中分析标记，通过 `WebAPILiquidJS` 模板引擎生成代码
3. **输出阶段**：生成的代码以 `PLUGIN_NAMEGenerated` 模块为模板骨架，输出为独立的运行时模块
4. **文档阶段**：`WebAPIOpenAPI` 模块同时生成 OpenAPI 规范文件（JSON/YAML），可用于 Swagger UI 等工具展示

## Demo 示例

由于 `PLUGIN_NAMEGenerated` 模块是代码生成的模板骨架，以下展示其基本结构：

### Private/PLUGIN_NAMEGenerated.h

```cpp
// 这是生成代码的模板头文件
// 生成时，PLUGIN_NAME 会被替换为实际的模块名

DECLARE_LOG_CATEGORY_EXTERN(LogFPLUGIN_NAMEGenerated, Log, All);
```

实际生成的模块会包含完整的 API 端点处理代码、HTTP 路由注册、请求/响应序列化等功能。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `WebAPI` | 核心 API 框架，提供端点定义、HTTP 路由和请求处理基础设施 |
| `WebAPIBlueprintGraph` | 蓝图图节点支持，允许在蓝图编辑器中定义 API 端点 |
| `WebAPIEditor` | 编辑器集成，提供代码生成的编辑器工具和 UI |
| `WebAPILiquidJS` | LiquidJS 模板引擎集成，用于灵活的代码生成模板 |
| `WebAPIOpenAPI` | OpenAPI/Swagger 规范支持，自动生成 API 文档 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 FJsonObject 支持 FString 和 FSharedString 两种字符串类型 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移到新的 UE_LOGF 宏 |
| 2026-03-02 | `9758fa58` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 移除 FJsonObject 中的字符串重复以释放内存 |
| 2026-02-18 | `516817d0` | PR #13954: fix(deps): on-headers is vulnerable to http response header manipulation | 修复依赖库 on-headers 的 HTTP 响应头操作漏洞 |

### 维护评价

- **创建时间**：2022 年 7 月，至今约 3 年
- **最近更新**：截至 2026 年 5 月仍有活跃更新，最近的 commit 主要集中在编译警告修复、JSON 序列化重构和日志宏迁移等基础设施维护
- **维护状态**：活跃维护中，但更新多为底层基础设施改进而非功能增强
- **实验性标记**：`IsExperimentalVersion: true`，`EnabledByDefault: false`，说明 Epic 将其定位为实验性功能，API 和行为可能发生变化
- **已知限制**：
  - 实验性状态意味着生产环境使用存在风险
  - 官方文档（DocsURL）为空，缺乏官方使用指南
  - `Installed: false` 表示默认不随引擎安装，需手动启用
- **推荐**：适合探索性项目和原型开发，不建议在生产环境中作为核心依赖。如果你的需求是快速生成 RESTful API 端点且愿意接受实验性 API 变更，此插件值得一试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Web/WebAPI)
- 官方文档（暂无）