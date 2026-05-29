# Data Link Http

> Motion Design Data Link（HTTP 数据源模块，提供 HTTP 请求能力）

| 属性 | 值 |
|---|---|
| 中文名 | 数据链路 HTTP 模块 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DataLink` (Runtime), `DataLinkEdGraph` (Runtime), `DataLinkDataTable` (Runtime), `DataLinkEditor` (Runtime), `DataLinkHttp` (Runtime), `DataLinkJson` (Runtime), `DataLinkJsonEditor` (Runtime), `DataLinkWebSocket` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DataLink) | |

## 用途

DataLinkHttp 是 Motion Design Data Link 插件的 HTTP 数据源模块。DataLink 是一套节点图式的数据链接系统，用于在虚拟制片（Virtual Production）场景中将外部数据源（HTTP、WebSocket、JSON、DataTable 等）接入 Motion Design 工作流。

DataLinkHttp 模块专门负责 HTTP 协议的数据获取，提供两个核心能力：

1. **HTTP 请求执行**：通过 `UDataLinkHttpSource` 节点发送 HTTP 请求（GET/POST 等），获取远程 API 数据
2. **HTTP 设置构建**：通过 `UDataLinkNodeHttpSettingsBuilder` 节点，利用 URL 模板和 Token 替换机制灵活构建 HTTP 请求参数

该系统将 HTTP 请求抽象为数据流图中的节点，允许用户在编辑器中可视化地配置数据获取逻辑，而无需编写代码。

## 使用场景

- 你需要从远程 REST API 获取数据并驱动 Motion Design 动画参数
- 你在虚拟制片中需要实时拉取外部数据（如天气、比分板、股票行情）显示在虚拟屏幕上
- 你需要构建带 Token 替换的动态 URL（如 `https://api.example.com/users/{UserId}`），根据上游节点输出自动填充
- 你需要将多个 HTTP 请求参数（URL、Headers、Body）分层组装，复用基础配置

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Http Settings Builder` | 构建 HTTP 设置，支持 URL 模板 Token 替换，设置 Verb、Headers、Body | `UDataLinkNodeHttpSettingsBuilder` |
| `Http Request` | 执行 HTTP 请求，输入 `Http Settings`，输出响应数据 | `UDataLinkHttpSource` |

### 数据结构

| 结构体 | 说明 |
|---|---|
| `FDataLinkHttpSettings` | HTTP 请求配置结构体，包含 URL、Verb、Headers、Body |

### 使用示例

典型的节点图连接方式：

1. 创建一个 **Http Settings Builder** 节点
   - 在 `URL Segments` 数组中配置 URL 路径段，Token 用 `{Token Name}` 格式定义在独立数组元素中
   - 设置 `Verb`（默认 `GET`）
   - 可选配置 `Headers` 和 `Body`

2. 将 Http Settings Builder 的输出连接到 **Http Request** 节点的 `InputHttpSettings` 输入

3. Http Request 节点执行后输出响应数据，可连接到下游数据处理节点

**URL Segments 配置示例**：

```
URL Segments:
  [0] "https://api.example.com/users/"
  [1] "{UserId}"
  [2] "/profile"
```

系统会自动检测 `{UserId}` 作为 Token，并将其暴露为可连接的输入 Pin，上游节点可动态提供该值。

## C++ 用法

### 头文件引入

```cpp
#include "DataLinkHttpSettings.h"
#include "DataLinkHttpSource.h"
#include "DataLinkNodeHttpSettingsBuilder.h"
```

### 基本用法

**使用 `FDataLinkHttpSettings` 结构体构造 HTTP 请求配置**：

```cpp
#include "DataLinkHttpSettings.h"

// 构建 HTTP 设置
FDataLinkHttpSettings Settings;
Settings.URL = TEXT("https://api.example.com/data");
Settings.Verb = TEXT("GET");
Settings.Headers.Add(TEXT("Content-Type"), TEXT("application/json"));
Settings.Headers.Add(TEXT("Authorization"), TEXT("Bearer your-token"));
Settings.Body = TEXT("");
```

*来源：Public/DataLinkHttpSettings.h*

### 进阶用法

**理解节点执行流程**（基于源码分析）：

```cpp
// DataLink 节点系统的执行模型：
// 1. UDataLinkNode::OnBuildPins() 定义输入输出 Pin
// 2. UDataLinkNode::OnExecute() 在数据流图中被调度执行
// 3. 通过 FDataLinkExecutor 管理执行上下文和数据传递

// Http Settings Builder 节点的工作原理：
// - URL Segments 中的 {Token} 会被解析为 FDataLinkStringBuilderToken
// - Token 暴露为输入 Pin，运行时由上游节点填充
// - PostEditChangeProperty 中会重新解析 Token 列表
// - 最终组合为完整的 FDataLinkHttpSettings 输出

// Http Source 节点的工作原理：
// - 输入：接收 FDataLinkHttpSettings（通常来自 Settings Builder）
// - 执行：发送 HTTP 请求
// - 输出：响应数据（传递给下游节点）
```

## Demo 示例

以下展示如何自定义一个继承自 `UDataLinkNode` 的 HTTP 数据处理节点：

```cpp
// MyDataLinkNodeWeather.h
#pragma once

#include "DataLinkNode.h"
#include "DataLinkHttpSettings.h"
#include "MyDataLinkNodeWeather.generated.h"

/**
 * 自定义节点：从天气 API 获取数据
 * 在 DataLink 节点图中作为可拖放的节点使用
 */
UCLASS(MinimalAPI, DisplayName="Weather Data Fetcher", Category="Custom")
class UMyDataLinkNodeWeather : public UDataLinkNode
{
	GENERATED_BODY()

protected:
	//~ Begin UDataLinkNode
	virtual void OnBuildPins(FDataLinkPinBuilder& Inputs, FDataLinkPinBuilder& Outputs) const override;
	virtual EDataLinkExecutionReply OnExecute(FDataLinkExecutor& InExecutor) const override;
	//~ End UDataLinkNode

private:
	/** 城市名称输入，用于构建查询 URL */
	UPROPERTY(EditAnywhere, Category="Weather")
	FString CityName = TEXT("Beijing");
};
```

```cpp
// MyDataLinkNodeWeather.cpp
#include "MyDataLinkNodeWeather.h"
#include "DataLinkPinBuilder.h"
#include "DataLinkExecutor.h"

void UMyDataLinkNodeWeather::OnBuildPins(FDataLinkPinBuilder& Inputs, FDataLinkPinBuilder& Outputs) const
{
	// 定义输出 Pin：传递 HTTP Settings 给下游的 Http Request 节点
	// FDataLinkHttpSettings 结构体会自动被识别为输出类型
	Inputs.Add(TEXT("CityName")).AsString();
	Outputs.Add(TEXT("HttpSettings")).AsStruct<FDataLinkHttpSettings>();
}

EDataLinkExecutionReply UMyDataLinkNodeWeather::OnExecute(FDataLinkExecutor& InExecutor) const
{
	// 获取输入
	FString City;
	InExecutor.GetInput(TEXT("CityName"), City);

	// 构建 HTTP 设置
	FDataLinkHttpSettings Settings;
Settings.URL = FString::Printf(TEXT("https://api.weatherapi.com/v1/current.json?q=%s"), *City);
	Settings.Verb = TEXT("GET");
	Settings.Headers.Add(TEXT("Accept"), TEXT("application/json"));

	// 输出到下游节点
	InExecutor.SetOutput(TEXT("HttpSettings"), Settings);

	return EDataLinkExecutionReply::Continue;
}
```

## 模块依赖

### DataLinkHttp 模块的依赖

从 Build.cs 及源码推断，DataLinkHttp 依赖以下模块：

| 模块 | 用途 |
|---|---|
| `DataLink` | 核心数据链路框架，提供 `UDataLinkNode`、`FDataLinkExecutor`、`FDataLinkPinBuilder` 基础类 |
| `Json` | HTTP 响应的 JSON 解析支持 |
| `HTTP` | UE 原生 HTTP 请求库（提供 `FHttpModule`） |

*注：标准依赖（Core, CoreUObject, Engine 等）已省略*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 JSON 对象以支持共享字符串，减少内存分配 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移为 UE_LOGF 新格式 |
| 2026-03-02 | `e97b93d4` | Fixes for CL 51336460 - Remove string duplication in FJsonObject to free memory | 修复字符串重复问题，优化 FJsonObject 内存占用 |
| 2026-03-02 | `9758fa58` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 去除 FJsonObject 中的字符串重复以释放内存 |
| 2026-02-25 | `ec13ba36` | [Backout] - CL51209244 | 回退提交 CL51209244 |

### 维护评价

- **状态**：活跃维护中
- **创建时间**：2025 年 8 月，约 1 年前
- **更新频率**：每月均有更新，最近一次在 2026 年 4 月底
- **更新内容**：主要是性能优化（内存占用减少）、编译适配（日志宏迁移）和 bug 修复，属于持续迭代阶段
- **实验性标记**：`IsBetaVersion=true`，API 可能发生变化
- **推荐程度**：适合在虚拟制片项目中试用，但注意 Beta 状态意味着接口可能不稳定。如果是生产环境，建议关注后续正式版本发布

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DataLink/Source/DataLinkHttp)