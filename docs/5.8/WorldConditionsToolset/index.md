# World Conditions Toolset

> Toolset for WorldConditions Inspection（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `WorldConditionsToolset` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-01 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/WorldConditionsToolset) | |

## 用途

此插件是 **AI 助手工具集（Toolset）** 的一部分，专门为 `WorldConditions` 系统提供 **可检查性（Inspection）** 工具。它解决了 AI 助手（或开发者工具）无法直接理解和操作 `FWorldConditionQueryDefinition` 这类复杂结构的问题。

其核心功能是：
1.  **JSON 序列化/反序列化**：将 `FWorldConditionQueryDefinition` 转换为 JSON 格式，便于 AI 助手读取、修改和回写。
2.  **生成可读描述**：将世界条件查询或单个条件转换为人类（或 AI）可读的文本描述，便于理解和调试。

它依赖于 `WorldConditions` 和 `ToolsetRegistry` 插件，是连接底层世界条件系统与上层 AI 工具链的桥梁。

## 使用场景

-   你正在开发或使用一个 **AI 助手**，需要让 AI 能够理解、分析或修改游戏中的世界条件逻辑。
-   你需要一个 **调试工具**，能够将复杂的世界条件查询以 JSON 或文本形式导出，便于检查或版本控制。
-   你在构建一个 **可视化编辑器** 或 **脚本系统**，需要将世界条件数据在结构体和 JSON 之间进行转换。

## 蓝图用法

此插件提供的蓝图节点主要用于获取世界条件的文本描述，通常用于调试或信息展示。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetQueryDescription` | 获取一个 `FWorldConditionQueryDefinition` 的完整文本描述。 | `UWorldConditionTools` |
| `GetConditionDescription` | 获取一个包含 `FWorldConditionBase` 派生结构体的 `FInstancedStruct` 的文本描述。 | `UWorldConditionTools` |

### 使用示例（蓝图描述）

1.  **获取查询描述**：
    *   假设你有一个 `FWorldConditionQueryDefinition` 类型的变量 `MyQueryDef`。
    *   在蓝图中，拖拽 `MyQueryDef` 引脚，搜索并调用 `GetQueryDescription` 节点。
    *   节点的输出 `ReturnValue` 即为该查询包含的所有条件的文本描述，可以将其连接到 `Print String` 节点进行输出。

2.  **获取单个条件描述**：
    *   假设你有一个 `FInstancedStruct` 类型的变量 `MyConditionStruct`，其内部存储了一个 `FWorldConditionBase` 的子类（如 `FWorldConditionQuery`）。
    *   在蓝图中，调用 `GetConditionDescription` 节点，并将 `MyConditionStruct` 作为输入。
    *   输出即为该单个条件的文本描述。

## C++ 用法

C++ 用法主要涉及使用 `FWorldConditionQueryConverter` 进行 JSON 数据的转换，这通常由 `ToolsetRegistry` 系统在内部调用，但了解其原理有助于扩展。

### 头文件引入

```cpp
#include "WorldConditionsToolset.h"
#include "WorldConditionQueryConverter.h" // 如果需要直接使用转换器
```

### 基本用法

此插件的核心是注册一个 JSON 转换器。`FWorldConditionQueryConverter` 会自动处理 `FWorldConditionQueryDefinition` 类型属性的序列化。

```cpp
// 在 ToolsetRegistry 系统中，当遇到 FWorldConditionQueryDefinition 类型的属性时，
// 会自动使用 FWorldConditionQueryConverter 进行处理。
// 以下为概念性代码，展示转换器如何被调用（实际由 ToolsetRegistry 框架驱动）。

// 假设有一个包含 FWorldConditionQueryDefinition 的对象
UObject* MyObject = ...;
FProperty* QueryProperty = MyObject->GetClass()->FindPropertyByName(TEXT("MyQueryDefinition"));

// ToolsetRegistry 框架会检查属性类型，并找到对应的转换器
// FWorldConditionQueryConverter::CanConvertProperty 会返回 true

// 序列化为 JSON
TSharedPtr<FJsonObject> JsonObject = ...;
// 框架调用 PropertyToJsonData 将属性值转为 JSON
// FWorldConditionQueryConverter::PropertyToJsonData(MyProperty, ValuePtr)

// 从 JSON 反序列化
TSharedPtr<FJsonValue> JsonValue = ...;
// 框架调用 JsonDataToProperty 将 JSON 值写回属性
// FWorldConditionQueryConverter::JsonDataToProperty(JsonValue, MyProperty, OutValuePtr)
```

### 进阶用法

直接使用 `UWorldConditionTools` 的静态函数来获取描述。

```cpp
#include "WorldConditionsToolset.h"
#include "WorldConditions/WorldConditionQuery.h"
#include "InstancedStruct.h"

void DescribeMyWorldCondition()
{
    // 1. 获取一个查询定义的描述
    FWorldConditionQueryDefinition QueryDef;
    // ... 假设 QueryDef 已经被正确初始化和填充了条件 ...
    FText QueryDescription = UWorldConditionTools::GetQueryDescription(QueryDef);
    UE_LOG(LogTemp, Log, TEXT("Query Description: %s"), *QueryDescription.ToString());

    // 2. 获取单个条件的描述
    // 假设我们有一个 FWorldConditionQuery 实例
    FWorldConditionQuery SingleCondition;
    // ... 初始化 SingleCondition ...
    FInstancedStruct ConditionStruct = FInstancedStruct::Make(SingleCondition);
    FText ConditionDescription = UWorldConditionTools::GetConditionDescription(ConditionStruct);
    UE_LOG(LogTemp, Log, TEXT("Condition Description: %s"), *ConditionDescription.ToString());
}
```

## Demo 示例

以下是一个最小的示例，展示如何在 C++ 中使用此插件提供的描述功能。

**MyWorldConditionActor.h**
```cpp
// MyWorldConditionActor.h
#pragma once

#include "GameFramework/Actor.h"
#include "WorldConditions/WorldConditionQuery.h"
#include "MyWorldConditionActor.generated.h"

UCLASS()
class AMyWorldConditionActor : public AActor
{
	GENERATED_BODY()

public:
	AMyWorldConditionActor();

	// 一个可以在编辑器中设置的世界条件查询定义
	UPROPERTY(EditAnywhere, Category = "World Conditions")
	FWorldConditionQueryDefinition MyQueryDefinition;

	// 在 BeginPlay 时打印其描述
	virtual void BeginPlay() override;
};
```

**MyWorldConditionActor.cpp**
```cpp
// MyWorldConditionActor.cpp
#include "MyWorldConditionActor.h"
#include "WorldConditionsToolset.h" // 引入插件头文件

AMyWorldConditionActor::AMyWorldConditionActor()
{
	PrimaryActorTick.bCanEverTick = false;
}

void AMyWorldConditionActor::BeginPlay()
{
	Super::BeginPlay();

	// 使用插件提供的工具函数获取描述
	FText Description = UWorldConditionTools::GetQueryDescription(MyQueryDefinition);
	UE_LOG(LogTemp, Warning, TEXT("World Condition Query Description:\n%s"), *Description.ToString());
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `WorldConditions` | 提供核心的世界条件系统（`FWorldConditionQueryDefinition`, `FWorldConditionBase` 等）。 |
| `ToolsetRegistry` | 提供工具集注册框架和 `FToolsetJsonConverter` 基类。 |

## 维护状态

### 近期更新

```
- 2026-04-18 6471b168 [AIAssistant] Change how UToolsetDefinitions determine which UFunctions are tools,.
- 2026-04-17 8c911af5 [Backout] - CL52878047
- 2026-04-17 9404cd3e [AIAssistant] Change how UToolsetDefinitions determine which UFunction are tools,.
```

### 维护评价

-   **创建时间**：2026年4月1日（未来日期，可能为测试数据）。
-   **最近更新**：最近一次提交在2026年4月18日，内容是关于调整 `UToolsetDefinitions` 如何确定工具函数的逻辑，属于功能性的框架调整。
-   **活跃度**：从提交记录看，该插件在创建后不久（2026年4月）有密集的提交，主要围绕 AI 助手工具集的集成和加载优化。**由于创建日期为未来时间，无法准确判断其长期维护状态。** 基于近期提交，它在创建初期是活跃维护的。
-   **已知限制**：这是一个**实验性**插件（`IsExperimentalVersion: true`），且**默认禁用**（`EnabledByDefault: false`）。这意味着它可能不稳定，API 可能发生变化，且需要用户手动启用。
-   **推荐使用**：**仅推荐给正在开发或集成 AI 助手工具集的高级用户或开发者**。对于普通的游戏逻辑开发，直接使用 `WorldConditions` 插件即可，无需此工具集。使用前请确保理解其依赖关系和实验性状态。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/WorldConditionsToolset)
-   [WorldConditions 插件源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/WorldConditions)
-   [ToolsetRegistry 插件源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ToolsetRegistry)