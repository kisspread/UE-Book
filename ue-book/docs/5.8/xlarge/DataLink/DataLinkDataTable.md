# Motion Design Data Link

> （插件描述为空）

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计数据链接 |
| 分类 | VirtualProduction |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DataLink` (Runtime), `DataLinkDataTable` (Runtime), `DataLinkEdGraph` (Runtime), `DataLinkEditor` (Runtime), `DataLinkHttp` (Runtime), `DataLinkJson` (Runtime), `DataLinkJsonEditor` (Runtime), `DataLinkWebSocket` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DataLink) | |

## 用途

本插件为 Unreal Engine 的 Motion Design（动态设计）功能提供统一的数据链接框架。它解决的核心问题是：**如何将各种外部数据源（如数据表、HTTP API、WebSocket 服务、JSON 文件等）统一接入 Motion Design 的动态图形和工作流中**。

该插件并非单一功能模块，而是一个由多个子模块组成的生态系统，每个子模块负责连接一种特定的数据源。它为 Motion Design 提供了数据驱动的基础设施，使得设计师和开发者能够创建响应实时数据变化的动态内容。

## 使用场景

- **虚拟制作数据可视化**：在虚拟制作场景中，需要将实时数据（如财务数据、物联网传感器数据、体育比赛数据）以动态图形的形式叠加在画面上。
- **数据驱动的动画**：创建基于外部数据变化的动画效果，例如根据实时股价变化改变图标大小或颜色。
- **API 集成**：通过 `DataLinkHttp` 或 `DataLinkWebSocket` 模块，直接连接后端服务或微服务，获取数据用于动态设计。
- **数据表格驱动**：使用 `DataLinkDataTable` 模块，将 DataTable 中存储的配置或内容直接应用到 Motion Design 元素上。

## 蓝图用法

由于该插件主要由 C++ 运行时模块构成，且 `DataLinkDataTable` 模块是具体的节点实现，其蓝图用法主要体现在 Motion Design 编辑器中的节点图上。核心类 `UDataLinkNode` 及其派生类（如 `UDataLinkDataTableSource`）提供了数据节点的基类。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| （数据源节点） | 继承自 `UDataLinkNode`，代表一个具体的、可连接的数据源或数据处理单元。 | `UDataLinkNode` |
| `Data Table` | 一个具体的节点实现，用于从 DataTable 资产中读取数据并输出。 | `UDataLinkDataTableSource` |

### 使用示例（蓝图描述）

在 Motion Design 编辑器的节点图（DataLink 图）中，用户可以：
1.  **添加节点**：从节点列表中搜索并添加一个 “Data Table” 节点。
2.  **配置数据源**：在该节点的属性面板中，选择要读取的 `UDataTable` 资产。
3.  **连接节点**：将 “Data Table” 节点的输出引脚（如 “Row Value”）连接到下游需要数据的节点（如某个文本或材质参数节点）。
4.  **执行**：当图执行时，“Data Table” 节点会查询指定的 DataTable，并将数据传递给后续节点。

## C++ 用法

### 头文件引入

```cpp
#include "DataLinkNode.h"
#include "DataLinkDataTableSource.h"
```

### 基本用法

要实现一个自定义的数据源节点，通常需要继承 `UDataLinkNode`。以下示例基于 `UDataLinkDataTableSource` 的实现模式，展示如何创建一个简单的数据源。

**来源文件**: `Engine/Plugins/VirtualProduction/DataLink/Source/DataLinkDataTable/Public/DataLinkDataTableSource.h`

```cpp
// MyCustomDataSource.h
#pragma once

#include "CoreMinimal.h"
#include "DataLinkNode.h"
#include "MyCustomDataSource.generated.h"

UCLASS(MinimalAPI, Category="Custom", DisplayName="My Custom Source")
class UMyCustomDataSource : public UDataLinkNode
{
	GENERATED_BODY()

protected:
	// 定义该节点的输入和输出引脚
	virtual void OnBuildPins(FDataLinkPinBuilder& Inputs, FDataLinkPinBuilder& Out) const override
	{
		// 例如：定义一个输入字符串引脚和一个输出整数引脚
		Inputs.Add(TEXT("InputString"), EDLDataType::String);
		Outputs.Add(TEXT("OutputValue"), EDLDataType::Int);
	}

	// 执行节点的核心逻辑
	virtual EDataLinkExecutionReply OnExecute(FDataLinkExecutor& InExecutor) const override
	{
		// 1. 获取输入引脚数据
		const FString InputString = InExecutor.GetValue<FString>(TEXT("InputString"));

		// 2. 执行自定义逻辑（例如：计算字符串长度）
		const int32 Result = InputString.Len();

		// 3. 将结果写入输出引脚
		InExecutor.SetValue(TEXT("OutputValue"), Result);

		// 4. 返回执行成功
		return EDataLinkExecutionReply::Continue;
	}
};
```

### 进阶用法

更复杂的用法可以组合多个自定义节点，并处理异步操作。对于网络数据源（如 `DataLinkHttp`），`OnExecute` 可能是异步的，需要正确处理 `FDataLinkExecutor` 的完成回调。

## Demo 示例

以下是一个完整的、最小化的自定义数据链接节点示例，它实现了将两个输入数字相加的功能。

**MyDataLinkMathAddNode.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "DataLinkNode.h"
#include "MyDataLinkMathAddNode.generated.h"

UCLASS(MinimalAPI, Category="Math", DisplayName="Add Two Numbers")
class UMyDataLinkMathAddNode : public UDataLinkNode
{
	GENERATED_BODY()

protected:
	virtual void OnBuildPins(FDataLinkPinBuilder& Inputs, FDataLinkPinBuilder& Out) const override
	{
		Inputs.Add(TEXT("A"), EDLDataType::Float);
		Inputs.Add(TEXT("B"), EDLDataType::Float);
		Outputs.Add(TEXT("Result"), EDLDataType::Float);
	}

	virtual EDataLinkExecutionReply OnExecute(FDataLinkExecutor& InExecutor) const override
	{
		const float A = InExecutor.GetValue<float>(TEXT("A"));
		const float B = InExecutor.GetValue<float>(TEXT("B"));
		const float Result = A + B;
		InExecutor.SetValue(TEXT("Result"), Result);
		return EDataLinkExecutionReply::Continue;
	}
};
```

**MyDataLinkMathAddNode.cpp**
```cpp
#include "MyDataLinkMathAddNode.h"

// 通常 .cpp 文件可能只需要包含生成的头文件
// #include "MyDataLinkMathAddNode.generated.h"
// 此处无需额外实现，逻辑已在头文件的虚函数中。
```

## 模块依赖

根据 `DataLinkDataTable` 模块的 `Build.cs` 文件推断，使用者需要依赖以下模块。**注意：该插件内部模块众多，此处仅列出核心数据链接框架的依赖，具体子模块可能有自己的依赖。**

| 模块 | 用途 |
|---|---|
| `DataLink` | 提供数据链接的核心运行时框架，包括 `UDataLinkNode` 基类、引脚系统、执行器等。 |
| `DataTable` | 用于访问和查询 Unreal Engine 的 DataTable 资产。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 JSON 对象以支持两种字符串类型 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏以统一格式 |
| 2026-03-02 | `e97b93d4` | Fixes for CL 51336460 - Remove string duplication in FJsonObject to free memory | 修复内存问题：消除 JSON 对象中的字符串重复 |
| 2026-03-02 | `9758fa58` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 修复内存问题：消除 JSON 对象中的字符串重复 |
| 2026-02-25 | `ec13ba36` | [Backout] - CL51209244 | 回退之前的某次更改 |

### 维护评价

该插件**非常新**（创建于 2025 年 8 月），且仍处于 **Beta 状态** (`IsBetaVersion=true`)。从 Git 历史看，近期更新主要集中在底层优化（如内存管理、日志统一）和稳定性修复，尚未看到显著的新功能提交。

**结论**：这是一个处于早期活跃开发阶段的实验性插件。它的架构和 API 可能还不稳定，未来会有较大变动。目前适合用于内部测试和原型验证，但**不建议**在追求稳定性的生产项目中深度依赖。推荐关注其后续版本更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DataLink)
- [官方文档]() （暂无）
- [测试用例]() （暂未在常见位置发现，可能位于 `Engine/Plugins/VirtualProduction/DataLink/Tests/` 或 `Engine/Tests/`）