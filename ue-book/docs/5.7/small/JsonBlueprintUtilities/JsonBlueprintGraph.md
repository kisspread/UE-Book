# Json Blueprint Utilities

> Json functionality for Blueprint.

| 属性 | 值 |
|---|---|
| 中文名 | JSON 蓝图工具 |
| 分类 | Blueprints |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `JsonBlueprintUtilities` (Runtime), `JsonBlueprintGraph` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-10-21 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/JsonBlueprintUtilities) | |

## 用途

**Json Blueprint Utilities** 是一套为蓝图提供 JSON 读写能力的轻量级插件。它解决了蓝图中直接操作 JSON 数据的不便性，通过预定义的自定义蓝图节点（`K2Node_GetJsonField`、`K2Node_SetJsonField`、`K2Node_StructToJsonString`），让开发者无需编写 C++ 就能快速完成 JSON 字符串与 UStruct 的双向转换以及 JSON 对象字段的增、删、改、查。

该插件将底层 C++ 函数（位于 `JsonBlueprintUtilities` 模块）包装为更直观的纯蓝图节点（位于 `JsonBlueprintGraph` 模块），简化了：

- 从 JSON 字符串解析并提取字段值
- 修改或新增 JSON 对象字段
- 将任意 UStruct 结构体序列化为 JSON 字符串
- 在运行时与外部 REST API、配置文件或网络数据交互

## 使用场景

- **游戏配置**：将游戏设置、关卡数据等存为 JSON 文件，在蓝图中读写。
- **网络数据交换**：与后端或第三方服务通信时，将响应 JSON 解析为结构体，或将请求体序列化为 JSON。
- **数据驱动设计**：用 JSON 作为设计数据源，在编辑器或运行时动态加载。
- **调试与测试**：快速打印结构体内容或构造测试数据。

## 蓝图用法

> 以下节点由 `JsonBlueprintGraph` 模块提供，位于蓝图编辑器的 **Json Blueprint Utilities** 分类下。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Json Field` | 从指定 `JsonObject` 中按路径获取字段值，输出为 `String`、`Number`、`Bool`、`Object` 或 `Array`（需手动转换） | `UK2Node_GetJsonField` |
| `Set Json Field` | 设置 `JsonObject` 中指定路径的字段值（支持基础类型及嵌套对象/数组） | `UK2Node_SetJsonField` |
| `Struct To Json String` | 将任意 `UStruct`（如自定义蓝图结构体）序列化为格式化的 JSON 字符串 | `UK2Node_StructToJsonString` |

> **注意**：以上节点均为 **纯节点（Pure Node）**，无执行引脚，可在任意表达式中直接连线。执行顺序由数据流决定。

### 使用示例（蓝图描述）

**示例 1：从 JSON 字符串获取字段值**

1. 使用 `ParseJSONString` 节点（需要额外导入或自己实现）或手动构造 `JsonObject`
2. 将得到的 `JsonObject` 连接至 `Get Json Field` 节点的 `Target` 引脚
3. 在 `FieldName` 引脚输入路径（如 `"data.name"`），支持点号分隔的嵌套路径
4. 输出引脚 `Value` 即为 `String`、`Number` 等基础类型（需通过 `String` 转 `EPropertyAccess` 等转换）

**示例 2：将自定义结构体保存为 JSON**

1. 定义一个包含 `Name`（Text）、`Score`（Float）、`Items`（Array of Name）的自定义蓝图结构体 `PlayerData`
2. 拖出 `Struct To Json String` 节点
3. 将 `PlayerData` 变量连到 `Struct` 输入引脚
4. 运行后输出引脚 `Result` 即为格式化的 JSON 字符串，可用于写入文件或发送给服务器

**示例 3：修改 JSON 对象字段**

1. 使用 `Get Json Field` 获取某个字段的 `JsonObject`（子对象）
2. 连接 `Set Json Field` 节点，输入新的字段值
3. 修改后的 `JsonObject` 可通过 `ToJsonString`（若有）或直接输出

> 以上节点均依赖 `JsonObject` 数据类型（蓝图中的 `JsonObject` 变量类型通常由 `JsonBlueprintUtilities` 模块提供，需确保已启用该插件）。

## C++ 用法

> 以下 API 由 `JsonBlueprintUtilities` 运行时模块提供，可直接在 C++ 中调用，也作为蓝图节点的底层实现。

### 头文件引入

```cpp
#include "JsonBlueprintUtilities.h"
```

### 基本用法

**1. 解析 JSON 字符串并获取字段**  
来源：`Source/JsonBlueprintUtilities/Private/...`（路径示例）

```cpp
#include "Dom/JsonObject.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"

FString JsonString = R"({"name":"Alice","score":95.5})";

// 解析为 FJsonObject
TSharedPtr<FJsonObject> JsonObject;
TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(JsonString);
if (FJsonSerializer::Deserialize(Reader, JsonObject) && JsonObject.IsValid())
{
	double Score = JsonObject->GetNumberField("score");
	FString Name = JsonObject->GetStringField("name");
}
```

**2. 结构体序列化（使用 `UJsonBlueprintFunctionLibrary`）**

```cpp
// 自定义结构体
USTRUCT(BlueprintType)
struct FTestData
{
	GENERATED_BODY()
	UPROPERTY() FString Name;
	UPROPERTY() float Score;
};

FTestData Data;
Data.Name = TEXT("Bob");
Data.Score = 88.0f;

// 转换为 JSON 字符串（类名因版本可能不同，请参考实际头文件）
FString OutJson;
bool bSuccess = UJsonBlueprintFunctionLibrary::StructToJsonString(Data, OutJson);
// OutJson: {"Name":"Bob","Score":88.0}
```

**3. 调用蓝图节点底层函数（若已暴露）**

可通过 `UKismetBlueprintLibrary` 或自定义库函数调用。具体函数可搜索 `GetJsonField`、`SetJsonField` 等。

### 进阶用法

**从文件加载 JSON 并提取多层字段**  
来源：组合多个 API

```cpp
// 读取文件
FString FileContent;
FFileHelper::LoadFileToString(FileContent, TEXT("Config.json"));

// 解析含数组的 JSON
TSharedPtr<FJsonObject> Root;
if (FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(FileContent), Root))
{
	TArray<TSharedPtr<FJsonValue>> Items = Root->GetArrayField("items");
	for (auto& Val : Items)
	{
		TSharedPtr<FJsonObject> ItemObj = Val->AsObject();
		FString ItemName = ItemObj->GetStringField("name");
		// ...
	}
}
```

## Demo 示例

以下是一个完整的最小 C++ 示例，演示结构体转 JSON 并解析返回。  
**注意**：需要项目已启用 `JsonBlueprintUtilities` 插件，并在 `Build.cs` 中添加依赖（见模块依赖）。

`MyJsonTest.h`

```cpp
#pragma once
#include "CoreMinimal.h"
#include "MyJsonTest.generated.h"

USTRUCT(BlueprintType)
struct FPlayerData
{
	GENERATED_BODY()
	UPROPERTY(EditAnywhere, BlueprintReadWrite) FString PlayerName;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) int32 Level;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) TArray<FString> Inventory;
};
```

`MyJsonTest.cpp`

```cpp
#include "MyJsonTest.h"
#include "JsonObjectConverter.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"
#include "Misc/FileHelper.h"

// 示例函数
FString ConvertPlayerDataToJson(const FPlayerData& Data)
{
	FString JsonString;
	FJsonObjectConverter::UStructToJsonObjectString(FPlayerData::StaticStruct(), &Data, JsonString, 0, 0, false);
	return JsonString;
}

void CreatePlayerFromJson(const FString& JsonString, FPlayerData& OutData)
{
	TSharedPtr<FJsonObject> JsonObject;
	TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(JsonString);
	if (FJsonSerializer::Deserialize(Reader, JsonObject) && JsonObject.IsValid())
	{
		FJsonObjectConverter::JsonObjectToUStruct(JsonObject.ToSharedRef(), FPlayerData::StaticStruct(), &OutData);
	}
}
```

> 实际项目中建议使用 `UJsonBlueprintFunctionLibrary` 封装的函数，它们已处理细节并抛出错误。

## 模块依赖

要使用此插件，您的模块需要在 `Build.cs` 中声明以下依赖（**常见依赖已省略**）：

| 模块 | 用途 |
|---|---|
| `Json` | JSON 序列化/反序列化核心 |
| `JsonUtilities` | 提供 `FJsonObjectConverter` 等便捷转换工具 |

> 如果仅使用蓝图节点，无需额外依赖，编辑器会自动加载 `JsonBlueprintGraph` 模块。

## 维护状态

### 近期更新

- 2024-01-22 `7192b9d0` — Remove text.h from script.h (script.h is included by object.h)  
- 2023-12-21 `f39df392` — [JsonBlueprint] Removed unused world context requirement from two json loading functions  
- 2023-03-11 `d3cf046a` — Lay groundwork for avoiding SGraphPanel refreshes after making a change to a single node  
- 2023-01-16 `bbc37aa2` — [Engine/Plugins]  
- 2022-10-21 `610c4676` — Update vendor links for built-in plugins to use secure protocol.

### 维护评价

- **创建时间**：2022-10-21，约 3 年  
- **更新频率**：最后一次功能性更新在 2023 年底（移除不必要的 world context），最近一次（2024 年初）仅为头文件清理  
- **活跃度**：非活跃维护，最近一年多无实质性功能更新  
- **限制**：插件标记为 **实验性（Beta）**，默认不启用，API 可能发生变化；仅提供有限的蓝图节点（Get/Set/StructToJson），缺少完整的 JSON 数组操作、遍历等高级节点  
- **推荐度**：对于需要快速在蓝图中处理简单 JSON 的场景值得启用，但复杂数据操作建议使用 C++ 直接调用 `Json`/`JsonUtilities` 模块，或等待官方完善

> **警告**：距离上次实质性功能更新已超过 1 年，未来可能被官方废弃或重构。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/JsonBlueprintUtilities)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/JsonBlueprintUtilities/Tests)（若存在）