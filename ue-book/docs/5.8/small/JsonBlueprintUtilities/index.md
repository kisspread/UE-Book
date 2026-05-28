# Json Blueprint Utilities

> Json functionality for Blueprint.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | JSON 蓝图工具 |
| 分类 | Blueprints |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `JsonBlueprintUtilities` (Runtime), `JsonBlueprintGraph` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-11-08 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/JsonBlueprintUtilities) | |

## 用途

这个插件解决了在蓝图中处理 JSON 数据的需求。它并非简单地将 JSON 解析为内部对象，而是提供了一个**可视化的蓝图工作流**，让开发者能够在编辑器中直接以节点图的方式构建、读取和操作 JSON 结构。其核心目标是将 JSON 的键值对操作转化为直观的蓝图节点，简化在游戏逻辑、配置文件加载和网络数据序列化中涉及 JSON 的工作。`JsonBlueprintGraph` 模块专门负责在蓝图编辑器中创建和管理这些 JSON 相关的节点。

## 使用场景

- 你需要**在蓝图中动态生成或解析 JSON 字符串**，用于与外部服务通信或读写配置文件。
- 你希望**在编辑器中以可视化方式定义 JSON 数据结构**，然后将其直接用于游戏逻辑。
- 你在开发一个需要复杂数据交换（如保存系统、任务配置）的游戏，希望避免手动拼写 JSON 字符串带来的错误。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Make Json Object` | 创建一个新的、空的 JSON 对象蓝图节点。 | `UJsonBlueprintObjectLibrary` |
| `Set Value` | 向 JSON 对象中设置一个指定键名的值（支持多种类型）。 | `UJsonBlueprintObjectLibrary` |
| `Get Value` | 从 JSON对象中获取一个指定键名的值（支持多种类型）。 | `UJsonBlueprintObjectLibrary` |
| `To Json String` | 将 JSON 对象序列化为格式化或紧凑的 JSON 字符串。 | `UJsonBlueprintObjectLibrary` |
| `From Json String` | 将 JSON 字符串反序列化为 JSON 对象。 | `UJsonBlueprintObjectLibrary` |

### 使用示例（蓝图描述）

1.  **创建与填充 JSON**：
    - 使用 `Make Json Object` 节点创建一个 JSON 对象。
    - 将其输出连接到一系列 `Set Value` 节点的 `Target` 引脚，为不同的键（如 “Name”, “Level”, “Items”）赋予字符串、整数和数组值。
2.  **序列化与解析**：
    - 将最终的 JSON 对象连接到 `To Json String` 节点，即可在输出引脚获得对应的 JSON 字符串。
    - 反之，将一个 JSON 字符串连接到 `From Json String` 节点，即可获得其对应的 JSON 对象，随后用 `Get Value` 提取数据。

## C++ 用法

### 头文件引入

```cpp
#include “JsonBlueprintUtilities.h”
```

### 基本用法

从插件源码推断的典型用法，用于在 C++ 中解析和操作 JSON 字符串。

```cpp
// 假设 JsonString 是一个包含 JSON 数据的 FString
FString JsonString = TEXT(‘{“Player”: {“Name”: “Hero”, “HP”: 100}}’);

// 1. 解析 JSON 字符串
TSharedPtr<FJsonObject> JsonObject;
TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(JsonString);
if (FJsonSerializer::Deserialize(Reader, JsonObject))
{
    // 2. 获取嵌套的 JSON 对象
    const TSharedPtr<FJsonObject>* PlayerObject;
    if (JsonObject->TryGetObjectField(TEXT(“Player”), PlayerObject))
    {
        // 3. 读取字段值
        FString PlayerName;
        if ((*PlayerObject)->TryGetStringField(TEXT(“Name”), PlayerName))
        {
            UE_LOG(LogTemp, Log, TEXT(“Player Name: %s”), *PlayerName);
        }
        
        int64 PlayerHP;
        if ((*PlayerObject)->TryGetNumberField(TEXT(“HP”), PlayerHP))
        {
            UE_LOG(LogTemp, Log, TEXT(“Player HP: %lld”), PlayerHP);
        }
    }
}
```

### 进阶用法

组合使用以创建复杂的 JSON 结构，并在 C++ 与蓝图间传递。

```cpp
// 1. 构建一个 JSON 对象
TSharedPtr<FJsonObject> RootObject = MakeShareable(new FJsonObject);
TSharedPtr<FJsonObject> StatsObject = MakeShareable(new FJsonObject);
StatsObject->SetNumberField(TEXT(“Strength”), 15);
StatsObject->SetNumberField(TEXT(“Dexterity”), 12);
RootObject->SetObjectField(TEXT(“Stats”), StatsObject);
RootObject->SetStringField(TEXT(“Class”), TEXT(“Warrior”));

// 2. 序列化为字符串
FString OutputJsonString;
TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&OutputJsonString);
FJsonSerializer::Serialize(RootObject.ToSharedRef(), Writer);

// 此时 OutputJsonString 为：{“Stats”: {“Strength”: 15, “Dexterity”: 12}, “Class”: “Warrior”}

// 3. (演示) 在蓝图函数中，可以使用 UJsonBlueprintObjectLibrary 包装上述 C++ 对象，
//    使其能被蓝图识别和使用，实现 C++ 底层逻辑与蓝图上层设计的结合。
```

## Demo 示例

```cpp
// JsonDemoActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "JsonDemoActor.generated.h"

UCLASS()
class AJsonDemoActor : public AActor
{
    GENERATED_BODY()
    
public:
    AJsonDemoActor();

    UFUNCTION(BlueprintCallable, Category = "JsonDemo")
    FString GenerateCharacterJson(const FString& Name, int32 Level);

    UFUNCTION(BlueprintCallable, Category = "JsonDemo")
    void ParseCharacterJson(const FString& JsonString, FString& OutName, int32& OutLevel);
};

// JsonDemoActor.cpp
#include "JsonDemoActor.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonWriter.h"
#include "Serialization/JsonSerializer.h"

AJsonDemoActor::AJsonDemoActor() {}

FString AJsonDemoActor::GenerateCharacterJson(const FString& Name, int32 Level)
{
    TSharedPtr<FJsonObject> JsonObject = MakeShareable(new FJsonObject);
    JsonObject->SetStringField(TEXT("Name"), Name);
    JsonObject->SetNumberField(TEXT("Level"), Level);
    
    FString OutputString;
    TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&OutputString);
    FJsonSerializer::Serialize(JsonObject.ToSharedRef(), Writer);
    return OutputString;
}

void AJsonDemoActor::ParseCharacterJson(const FString& JsonString, FString& OutName, int32& OutLevel)
{
    TSharedPtr<FJsonObject> JsonObject;
    TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(JsonString);
    if (FJsonSerializer::Deserialize(Reader, JsonObject) && JsonObject.IsValid())
    {
        JsonObject->TryGetStringField(TEXT("Name"), OutName);
        JsonObject->TryGetNumberField(TEXT("Level"), OutLevel);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Json` | 核心 JSON 解析与序列化库。 |
| `JsonUtilities` | JSON 与 UE 结构体、UObject 之间的转换工具。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 FJsonObject 以支持共享字符串，优化内存。 |
| 2026-03-02 | `9758fa58` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 移除 FJsonObject 中的字符串重复，释放内存。 |
| 2026-02-25 | `ec13ba36` | [Backout] - CL51209244 | 回退了某个更改。 |
| 2026-02-25 | `af0dfacf` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 移除 FJsonObject 中的字符串重复，释放内存（尝试提交）。 |
| 2024-01-22 | `7192b9d0` | Remove text.h from script.h (script.h is included by object.h) | 移除不必要的头文件包含，优化编译。 |

### 维护评价

- **创建时间**：约 5 年前。
- **维护状态**：**维护中**。尽管标记为实验性（Beta）且默认禁用，但在 2026 年仍有实质性的性能优化更新（减少字符串内存拷贝），表明 Epic 在持续改进其底层实现。
- **已知限制**：作为实验性功能，其 API 和行为在未来版本中可能发生变化。
- **推荐**：对于需要在蓝图中处理 JSON 的需求，此插件提供了标准化的解决方案。由于其默认禁用且为 Beta，建议在评估后使用，并关注版本更新说明。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/JsonBlueprintUtilities)