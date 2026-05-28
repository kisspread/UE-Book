# Json Blueprint Utilities

> Json functionality for Blueprint.

| 属性 | 值 |
|---|---|
| 中文名 | JSON蓝图工具 |
| 分类 | Blueprints |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `JsonBlueprintGraph` (Runtime), `JsonBlueprintUtilities` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-11-08 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/JsonBlueprintUtilities) | |

## 用途

本插件旨在为蓝图（Blueprint）提供一组无需编写C++代码即可操作JSON数据的节点。它解决了蓝图中缺乏原生、便捷的JSON处理能力的问题，让策划和设计师能够在蓝图中直接解析JSON字符串、读取和设置JSON对象的字段，从而轻松实现数据配置导入、网络协议解析、存档数据处理等功能。

插件主要包含两个部分：
1.  **核心运行时库 (`JsonBlueprintGraph`)**：封装了与`JsonObject`交互的核心蓝图函数。
2.  **编辑器图表节点 (`JsonBlueprintGraph` 模块中的 K2Node)**：提供了三个重要的蓝图节点（`Struct To Json String`， `Get Json Field`， `Set Json Field`），这些节点在蓝图编辑器中以友好的方式暴露了JSON操作功能。

**注意**：此插件目前处于测试阶段 (`IsBetaVersion: true`)，且默认未启用 (`EnabledByDefault: false`)，需要在项目中手动启用。

## 使用场景

- 你在蓝图中接收到来自服务器或配置文件的JSON字符串，需要将其解析为蓝图可用的数据。
- 你需要将蓝图中的结构化数据（如自定义结构体）序列化为JSON字符串，用于网络传输或保存到文件。
- 你想要在蓝图中动态修改一个JSON对象内的某个特定字段的值。

## 蓝图用法

本插件的核心价值在于提供了三个直观的蓝图节点，它们都位于 `Json` 类别下。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Struct To Json String` | 一个纯函数（Pure）节点。接受任意结构体输入，并输出其对应的JSON字符串表示。 | `UK2Node_StructToJsonString` |
| `Get Json Field` | 一个纯函数节点。从一个 `JsonObject` 引用中，根据字段名（`Field Name`）提取对应的值。输出值类型可以是 `String`, `Number`, `Boolean` 等，节点会根据字段类型自动适配。 | `UK2Node_GetJsonField` |
| `Set Json Field` | 一个非纯函数节点。向一个 `JsonObject` 引用中，设置指定字段名（`Field Name`）的值。输入值类型同样可以自动适配。 | `UK2Node_SetJsonField` |

### 使用示例（蓝图描述）

**场景：解析配置JSON**

1.  **解析**：使用 `JsonUtilities` 模块中的 `JsonObjectFromJsonString` 节点，将输入的 `Json String` 解析为一个 `JsonObject` 对象。
2.  **提取字段**：连接 `JsonObject` 到 `Get Json Field` 节点的 `Object` 引脚。在 `Field Name` 引脚输入你要读取的字段名，例如 `"playerName"`。
3.  **使用数据**：`Get Json Field` 节点的 `Value` 输出引脚会输出该字段的值（例如一个字符串），你可以将其连接到其他逻辑或变量。

**场景：构建JSON请求**

1.  **创建对象**：使用 `Construct Object from Class` 节点创建一个空的 `JsonObject` 对象。
2.  **设置字段**：将这个 `JsonObject` 对象连接到多个 `Set Json Field` 节点。为每个节点设置不同的 `Field Name` 和要填入的 `Value`。
3.  **序列化**：最后，使用 `JsonUtilities` 模块中的 `JsonStringFromJsonObject` 节点，将这个被填充的 `JsonObject` 转换回JSON字符串。

## C++ 用法

虽然本插件主要为蓝图设计，但其底层依赖于 `JsonUtilities` 模块，你可以在C++中直接使用这些功能。

### 头文件引入

```cpp
#include "Serialization/JsonSerializer.h"
#include "Dom/JsonObject.h"
#include "Policies/CompactJsonStringPolicy.h" // 用于紧凑的JSON输出
```

### 基本用法

以下示例展示了如何在C++中创建、操作和序列化一个 `JsonObject`。这些操作与蓝图节点 `Struct To Json String`、`Set Json Field` 和 `Get Json Field` 的底层实现原理相同。

```cpp
// 来源：基本的JSON创建与序列化（非直接来自测试用例，但演示了核心API用法）

// 1. 创建一个JSON对象
TSharedPtr<FJsonObject> JsonObject = MakeShareable(new FJsonObject());

// 2. 添加不同类型的字段
JsonObject->SetStringField(TEXT("PlayerName"), TEXT("Hero"));
JsonObject->SetNumberField(TEXT("Level"), 15.5f);
JsonObject->SetBoolField(TEXT("IsOnline"), true);

// 3. 将JSON对象序列化为字符串
FString OutputString;
TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&OutputString);
FJsonSerializer::Serialize(JsonObject.ToSharedRef(), Writer);
Writer->Close();

// OutputString 现在是: {"PlayerName":"Hero","Level":15.5,"IsOnline":true}
```

### 进阶用法

以下示例展示了如何从JSON字符串中提取特定字段，这对应蓝图中的 `Get Json Field` 节点功能。

```cpp
// 来源：从字符串解析并读取字段（演示了蓝图节点的底层逻辑）

FString JsonString = TEXT("{\"config\": {\"width\": 1920, \"height\": 1080}}");

// 1. 将字符串解析为JSON对象
TSharedPtr<FJsonObject> RootObject;
TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(JsonString);
if (FJsonSerializer::Deserialize(Reader, RootObject))
{
    // 2. 获取嵌套的 "config" 对象（对应 Get Json Field 的第一个层级）
    const TSharedPtr<FJsonObject>* ConfigObjectPtr;
    if (RootObject->TryGetObjectField(TEXT("config"), ConfigObjectPtr))
    {
        // 3. 从配置对象中获取 "width" 字段的值（对应 Get Json Field 的第二个层级）
        int32 Width;
        if ((*ConfigObjectPtr)->TryGetNumberField(TEXT("width"), Width))
        {
            UE_LOG(LogTemp, Log, TEXT("Screen Width: %d"), Width); // 输出：Screen Width: 1920
        }
    }
}
```

## Demo 示例

一个展示如何使用 `FJsonObject` 的最小 C++ 类。虽然插件本身是蓝图工具，但这是其底层功能的核心。

```cpp
// MyJsonActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "MyJsonActor.generated.h"

UCLASS()
class AMyJsonActor : public AActor
{
	GENERATED_BODY()

public:
	AMyJsonActor();
	virtual void BeginPlay() override;

	// 一个简单的函数，演示创建和打印JSON
	UFUNCTION(BlueprintCallable, Category = "JSON Demo")
	void PrintDemoJson();
};

// MyJsonActor.cpp
#include "MyJsonActor.h"
#include "Serialization/JsonSerializer.h"
#include "Dom/JsonObject.h"

AMyJsonActor::AMyJsonActor()
{
	PrimaryActorTick.bCanEverTick = false;
}

void AMyJsonActor::BeginPlay()
{
	Super::BeginPlay();
	PrintDemoJson();
}

void AMyJsonActor::PrintDemoJson()
{
	// 创建JSON对象
	TSharedPtr<FJsonObject> JsonObject = MakeShareable(new FJsonObject());

	// 设置字段
	JsonObject->SetStringField(TEXT("Message"), TEXT("Hello from Blueprint Utilities"));
	JsonObject->SetNumberField(TEXT("Timestamp"), GetWorld()->GetTimeSeconds());

	// 创建一个嵌套的数组对象
	TArray<TSharedPtr<FJsonValue>> ArrayValues;
	ArrayValues.Add(MakeShareable(new FJsonValueString(TEXT("Item1"))));
	ArrayValues.Add(MakeShareable(new FJsonValueString(TEXT("Item2"))));
	JsonObject->SetArrayField(TEXT("Items"), ArrayValues);

	// 序列化为字符串
	FString OutputString;
	TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&OutputString);
	FJsonSerializer::Serialize(JsonObject.ToSharedRef(), Writer);
	Writer->Close();

	// 打印结果
	UE_LOG(LogTemp, Log, TEXT("Generated JSON:\n%s"), *OutputString);
}
```

## 模块依赖

要使用此插件的功能，你的模块需要添加以下依赖：

| 模块 | 用途 |
|---|---|
| `JsonUtilities` | `JsonBlueprintUtilities` 和 `JsonBlueprintGraph` 模块的核心依赖，提供了 `FJsonObject` 等基础JSON操作类。 |
| `JsonBlueprintGraph` | 提供了蓝图图表节点（K2Nodes），如果你需要扩展或引用这些节点，需要依赖此模块。 |
| `JsonBlueprintUtilities` | 包含对蓝图暴露的核心运行时函数。如果你在蓝图中直接使用本插件的功能，你的项目（或打包后的插件）需要此模块。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构FJsonObject以同时支持FString和UE::FSharedString |
| 2026-03-02 | `9758fa58` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 移除FJsonObject中的字符串重复以释放内存 |
| 2026-02-25 | `ec13ba36` | [Backout] - CL51209244 | 撤销了之前的一次提交 |
| 2026-02-25 | `af0dfacf` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 移除FJsonObject中的字符串重复以释放内存 |
| 2024-01-22 | `7192b9d0` | Remove text.h from script.h (script.h is included by object.h) | 从script.h中移除text.h的包含（script.h被object.h包含） |

### 维护评价

**综合评价**：此插件创建于2021年底，至今约4年。从git日志看，**对插件本身功能的直接维护和更新非常少**。近期的提交（2026年）主要集中在对底层 `FJsonObject` 类的重构和内存优化，这属于引擎核心JSON模块的改动，并非为蓝图工具本身添加新功能或修复问题。

**状态判断**：**维护不活跃，且可能接近废弃**。插件本身处于测试版（Beta），且默认禁用。近一年内没有任何针对蓝图节点功能本身的实质性更新（如修复BUG、增加节点类型、提升易用性）。

**推荐使用**：**谨慎使用**。对于原型开发或内部工具，如果现有功能满足需求，可以启用并使用。但对于生产项目，需考虑以下风险：
1.  **功能固定**：未来获得功能增强或BUG修复的可能性较低。
2.  **API稳定性**：虽然近期的修改是底层重构，但插件的公共API可能在未来版本中未经通知即发生变化。
3.  **替代方案**：引擎核心的 `JsonUtilities` 模块在C++中非常成熟稳定。在蓝图中，也可以考虑通过包装简单的C++库函数来实现类似功能，这样拥有更高的可控性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/JsonBlueprintUtilities)
- [官方文档]() (暂无)
- [测试用例]() (未在提供的信息中找到明确的测试文件路径)