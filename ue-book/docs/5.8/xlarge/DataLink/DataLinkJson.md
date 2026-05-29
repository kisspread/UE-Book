# Data Link Json

> JSON data conversion nodes for the DataLink system.

| 属性 | 值 |
|---|---|
| 中文名 | 数据链接 JSON |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DataLinkJson` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DataLink/Source/DataLinkJson) | |

## 用途

DataLinkJson 是 Unreal Engine 虚拟制片 (Virtual Production) 中 **DataLink** 系统的一个**专用转换模块**。其核心功能是在 **JSON 数据**和 **Unreal 的结构体 (UScriptStruct) 之间进行双向转换**。

它不是一个独立的插件，而是 DataLink 插件的组成部分，通过提供专门的 **数据链接节点 (UDataLinkNode)** 来处理 JSON 数据流。它解决了在基于节点的数据链接系统中，如何标准化地将外部 API、配置文件或网络数据中的 JSON 对象映射到引擎内部可操作的数据结构（反之亦然）的问题。

## 使用场景

- **获取外部数据**：你的 Motion Design 项目需要从一个 REST API 获取 JSON 格式的设备状态或配置数据，并将其转换为引擎内的结构体以驱动蓝图逻辑或材质参数。
- **发送配置数据**：你需要将蓝图中某个结构体的当前状态（例如用户自定义的动画参数）序列化为 JSON 字符串，通过 WebSocket 发送给外部控制系统。
- **数据流水线构建**：在 DataLink 的蓝图节点编辑器中，你构建一个数据流，其中一个环节是解析收到的 JSON 消息，并提取特定字段的值到后续节点。

## 蓝图用法

本模块主要通过 DataLink 蓝图节点系统提供功能，核心节点均为 `UDataLinkNode` 的子类，可在 DataLink 图表编辑器中使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `String to JSON` | 将字符串解析为 FJsonObject 引用。 | `UDataLinkStringToJson` |
| `JSON to Struct` | 将 JSON 对象转换为指定的 UScriptStruct 实例。支持自定义映射逻辑。 | `UDataLinkJsonToStruct` |
| `Struct to JSON` | 将一个结构体实例转换为 JSON 对象。 | `UDataLinkJsonFromStruct` |

### 使用示例（蓝图描述）

在 DataLink 蓝图编辑器中，你可以这样构建一个将外部 JSON 配置应用到场景 actor 的流程：
1. 使用一个 **HTTP 请求节点** 获取 JSON 字符串。
2. 连接到 **`String to JSON`** 节点，将字符串转换为 JSON 对象。
3. 将 JSON 对象连接到 **`JSON to Struct`** 节点。在该节点的细节面板中，指定目标结构体（例如 `FMyDeviceConfig`），并可选择一个自定义映射类 (`UDataLinkJsonStructMapping`) 来处理复杂的字段对应关系。
4. 将转换后的结构体输出连接到后续的 **“设置 Actor 变量”** 或 **“设置材质参数”** 节点。

## C++ 用法

本模块的 API 主要面向扩展和定制转换逻辑。

### 头文件引入

```cpp
#include "DataLinkJsonUtils.h"      // 用于工具函数
#include "DataLinkJsonToStruct.h"   // 用于 JSON 到结构体的节点
#include "DataLinkJsonStructMapping.h" // 用于自定义映射基类
```

### 基本用法：自定义 JSON 到结构体的映射逻辑

当默认的 JSON 字段名到结构体属性名的映射不满足需求时，可以继承 `UDataLinkJsonStructMapping` 并重写 `Apply` 方法。

```cpp
// 来源: Public/DataLinkJsonStructMapping.h
// 一个自定义的映射，将 JSON 中的 "sensor_value" 字段映射到结构体的 "Value" 属性
UCLASS()
class UMyCustomSensorMapping : public UDataLinkJsonStructMapping
{
	GENERATED_BODY()

public:
	virtual bool Apply(const TSharedRef<FJsonObject>& InSourceJson, const FStructView& InTargetStructView) const override
	{
		if (const TSharedPtr<FJsonValue>* FoundValue = InSourceJson->Values.Find(TEXT("sensor_value")))
		{
			if (FProperty* ValueProp = InTargetStructView.GetProperty())
			{
				// 此处简化了类型转换逻辑，实际需处理不同类型
				float NumericValue = (*FoundValue)->AsNumber();
				ValueProp->SetValue_InContainer(InTargetStructView.GetMemory(), &NumericValue);
				return true;
			}
		}
		return false;
	}
};
```

然后，在 `FDataLinkJsonStructMappingConfig` 配置中指定此类。

### 进阶用法：使用工具函数解析嵌套 JSON

使用 `FindJsonValue` 工具函数可以方便地按路径访问嵌套的 JSON 字段。

```cpp
// 来源: Public/DataLinkJsonUtils.h
#include "DataLinkJsonUtils.h"
#include "JsonObjectConverter.h" // 假设需要进行类型转换

void ProcessNestedJson(const TSharedRef<FJsonObject>& JsonObject)
{
	// 尝试获取一个深层嵌套的值，路径为 "response.data.items[0].id"
	TSharedPtr<FJsonValue> ItemIdValue = UE::DataLinkJson::FindJsonValue(JsonObject, TEXT("response.data.items[0].id"));
	
	if (ItemIdValue.IsValid())
	{
		int64 ItemId = ItemIdValue->AsNumber();
		UE_LOG(LogTemp, Log, TEXT("Found Item ID: %lld"), ItemId);
	}
}
```

## Demo 示例

一个最小的、展示如何创建自定义映射并用于 `UDataLinkJsonToStruct` 的 C++ 示例。

```cpp
// MyCustomJsonMapping.h
#pragma once

#include "CoreMinimal.h"
#include "DataLinkJsonStructMapping.h"
#include "MyCustomJsonMapping.generated.h"

USTRUCT(BlueprintType)
struct FMyData
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	float Temperature;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	FString SensorName;
};

UCLASS()
class UMyCustomJsonMapping : public UDataLinkJsonStructMapping
{
	GENERATED_BODY()

public:
	virtual bool Apply(const TSharedRef<FJsonObject>& InSourceJson, const FStructView& InTargetStructView) const override
	{
		if (InTargetStructView.GetScriptStruct() != FMyData::StaticStruct())
		{
			return false;
		}

		FMyData& Data = *InTargetStructView.GetPtr<FMyData>();

		// 自定义映射逻辑：JSON 字段名与结构体属性名不同，且需要类型转换
		if (const TSharedPtr<FJsonValue>* TempValue = InSourceJson->Values.Find(TEXT("temp")))
		{
			Data.Temperature = (*TempValue)->AsNumber();
		}

		if (const TSharedPtr<FJsonValue>* NameValue = InSourceJson->Values.Find(TEXT("name")))
		{
			Data.SensorName = (*NameValue)->AsString();
		}

		return true;
	}
};
```

## 模块依赖

从 `DataLinkJson.Build.cs` 推断，本模块依赖 DataLink 核心模块和 JSON 解析模块。

| 模块 | 用途 |
|---|---|
| `DataLink` | 数据链接系统的核心运行时模块，提供 `UDataLinkNode`, `FDataLinkExecutor` 等基类。 |
| `Json` | 提供 `FJsonObject`, `FJsonValue` 等 JSON 解析与序列化基础类。 |
| `JsonUtilities` | 提供 `FJsonObjectConverter`，用于标准的 JSON 与 UStruct 转换，本模块的简单映射可能基于此。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 JSON 对象以支持两种字符串类型，可能是为了性能或兼容性优化。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移到 UE_LOGF，属于日志系统的现代化重构。 |
| 2026-03-02 | `e97b93d4` | Fixes for CL 51336460 - Remove string duplication in FJsonObject to free memory | 修复内存问题，移除 JSON 对象中的字符串重复以释放内存。 |
| 2026-03-02 | `9758fa58` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 针对 Fortnite 项目的内存优化，与上一条相关。 |
| 2026-02-25 | `ec13ba36` | [Backout] - CL51209244 | 回滚了之前的某个提交，表明进行了谨慎的变更管理。 |

### 维护评价

- **活跃维护**：该模块在 2026 年初至今（2026 年 4 月）有多次提交，主要集中在**性能优化（内存管理）、代码现代化和 Bug 修复**上。这表明它正在被积极地优化和改进，而不仅仅是初始搭建。
- **实验性状态**：`.uplugin` 中标记为 `IsBetaVersion: true`，表明它是 Motion Design / Virtual Production 工具链中的较新功能，API 可能会变化，但正在稳定中。
- **推荐使用**：对于需要在虚拟制片或 Motion Design 项目中集成 JSON 数据流的开发者，**推荐使用**此模块。它作为 DataLink 系统的一部分，提供了标准化和可扩展的 JSON 处理能力，且目前维护活跃。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DataLink/Source/DataLinkJson)
- 官方文档：暂无
- 测试用例：未在提供信息中明确，可能位于 `Engine/Tests` 或插件内部