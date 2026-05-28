# Json Blueprint Utilities

> Json functionality for Blueprint.

| 属性 | 值 |
|---|---|
| 中文名 | JSON蓝图工具 |
| 分类 | Blueprints |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `JsonBlueprintUtilities` (Runtime), `JsonBlueprintGraph` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-11-08 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/JsonBlueprintUtilities) | |

## 用途

`JsonBlueprintUtilities` 插件为 Unreal Engine 的蓝图系统提供了原生、便捷的 JSON 数据处理能力。它主要解决了蓝图中缺乏原生 JSON 解析和操作功能的问题。该插件通过提供一个名为 `FJsonObjectWrapper` 的包装器和一系列静态函数库节点，使得蓝图开发者能够轻松地将 JSON 字符串解析为可操作的对象，读取、修改其字段值，以及将蓝图中的结构体或对象数据序列化为 JSON 字符串或写入文件。它简化了蓝图与外部系统（如Web API、配置文件）之间的数据交换流程。

## 使用场景

- 你需要在蓝图中动态读取和解析游戏配置文件（.json）。
- 你需要蓝图与 RESTful API 交互，发送或接收 JSON 格式的数据。
- 你需要将蓝图中定义的结构体数据序列化为 JSON 字符串，用于网络通信或存档。
- 你需要在编辑器工具或运行时游戏中，以可视化的方式检查或构建 JSON 数据结构。

## 蓝图用法

此插件的所有功能都通过 `UJsonBlueprintFunctionLibrary` 类的静态蓝图节点暴露。所有节点均归类于 “Json” 分类下。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Load Json from String` | 将 JSON 字符串解析为 `FJsonObjectWrapper` 对象。 | `UJsonBlueprintFunctionLibrary` |
| `Load Json from File` | 从指定文件路径加载 JSON 并解析为 `FJsonObjectWrapper` 对象。 | `UJsonBlueprintFunctionLibrary` |
| `Get Json String` | 将 `FJsonObjectWrapper` 对象序列化为 JSON 格式的字符串。 | `UJsonBlueprintFunctionLibrary` |
| `Save Json to File` | 将 `FJsonObjectWrapper` 对象序列化并保存到指定文件。 | `UJsonBlueprintFunctionLibrary` |
| `Get Field` | 从 JSON 对象中获取指定字段的值（支持多种基本类型和结构体）。 | `UJsonBlueprintFunctionLibrary` |
| `Set Field` | 向 JSON 对象添加新字段或更新已有字段的值（支持多种基本类型和结构体）。 | `UJsonBlueprintFunctionLibrary` |
| `Convert Struct To Json String` | 将蓝图中定义的任意结构体直接转换为 JSON 字符串。 | `UJsonBlueprintFunctionLibrary` |
| `Has Field` | 检查 JSON 对象中是否存在指定名称的字段。 | `UJsonBlueprintFunctionLibrary` |
| `Get Field Names` | 获取 JSON 对象中所有顶层字段的名称列表。 | `UJsonBlueprintFunctionLibrary` |

### 使用示例（蓝图描述）

1.  **从文件加载并查询数据**：
    *   拖入 `Load Json from File` 节点，选择一个 `.json` 文件。将其 “JsonObject” 输出引脚连接到一个变量。
    *   使用 `Has Field` 节点检查该对象中是否存在名为 `”PlayerName”` 的字段。
    *   如果存在，连接 `Get Field` 节点，字段名填 `”PlayerName”`，并将 “Value” 输出引脚连接到一个 String 变量或 Print String 节点。

2.  **创建并保存新的 JSON 数据**：
    *   使用 `Set Field` 节点（首次调用会自动创建根对象）。为字段 `”Level”` 设置一个整数值（例如 `5`）。
    *   继续使用 `Set Field` 为同一对象添加字段 `”Score”`，值为浮点数 `1000.5`。
    *   最后使用 `Save Json to File` 节点，将构建好的对象保存为 `.json` 文件。

3.  **结构体转换**：
    *   拖入 `Convert Struct To Json String` 节点，将一个自定义结构体变量连接到 “Struct” 输入引脚。其 “String” 输出引脚将直接得到该结构体的 JSON 字符串表示。

## C++ 用法

此插件主要面向蓝图设计，但其 `UJsonBlueprintFunctionLibrary` 和 `FJsonObjectWrapper` 类同样可以在 C++ 中使用，以实现更底层或性能敏感的操作。

### 头文件引入

```cpp
#include "JsonBlueprintUtilities/JsonBlueprintFunctionLibrary.h"
// FJsonObjectWrapper 通常定义在 Engine/Source/Runtime/Json/ 下，但使用此插件时会自动包含
```

### 基本用法

从字符串解析 JSON 并获取字段值。

```cpp
// 假设已有一个 JSON 字符串
FString JsonString = TEXT("{\"Name\":\"UE5\",\"Version\":5.5}");

FJsonObjectWrapper JsonObject;
bool bSuccess = UJsonBlueprintFunctionLibrary::FromString(JsonString, JsonObject);

if (bSuccess)
{
    // 检查字段是否存在
    if (UJsonBlueprintFunctionLibrary::HasField(JsonObject, TEXT("Name")))
    {
        FString GameName;
        // 获取字符串类型的字段值
        UJsonBlueprintFunctionLibrary::GetField(JsonObject, TEXT("Name"), GameName);
        UE_LOG(LogTemp, Log, TEXT("Game Name: %s"), *GameName); // 输出: Game Name: UE5
    }

    float EngineVersion;
    // 获取数值类型的字段值
    if (UJsonBlueprintFunctionLibrary::GetField(JsonObject, TEXT("Version"), EngineVersion))
    {
        UE_LOG(LogTemp, Log, TEXT("Engine Version: %.1f"), EngineVersion); // 输出: Engine Version: 5.5
    }
}
```

### 进阶用法

动态构建一个 JSON 对象并序列化回字符串。

```cpp
FJsonObjectWrapper MyObject;

// 设置不同类型的字段
UJsonBlueprintFunctionLibrary::SetField(MyObject, TEXT("bIsActive"), true);
UJsonBlueprintFunctionLibrary::SetField(MyObject, TEXT("MaxPlayers"), 64);
TArray<FString> MapList = {TEXT("DM-Deck"), TEXT("CTF-Face")};
UJsonBlueprintFunctionLibrary::SetField(MyObject, TEXT("MapRotation"), MapList);

// 序列化为带缩进的格式化字符串
FString OutputString;
if (UJsonBlueprintFunctionLibrary::ToString(MyObject, OutputString))
{
    // 输出结果将是一个格式良好的 JSON 字符串
    UE_LOG(LogTemp, Log, TEXT("Generated JSON:\n%s"), *OutputString);
}
```

## Demo 示例

这是一个最小的 C++ 示例，演示如何使用该插件的函数库解析简单的 JSON 并提取数据。

**MyJsonDemoActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyJsonDemoActor.generated.h"

UCLASS()
class AMyJsonDemoActor : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable)
    void ParseAndPrintJson();
};
```

**MyJsonDemoActor.cpp**
```cpp
#include "MyJsonDemoActor.h"
#include "JsonBlueprintUtilities/JsonBlueprintFunctionLibrary.h"

void AMyJsonDemoActor::BeginPlay()
{
    Super::BeginPlay();
    ParseAndPrintJson();
}

void AMyJsonDemoActor::ParseAndPrintJson()
{
    const FString SampleJson = TEXT(R"({
        "weapon": {
            "name": "Pistol",
            "damage": 10.5,
            "isAutomatic": false
        }
    })");

    FJsonObjectWrapper RootObject;
    if (!UJsonBlueprintFunctionLibrary::FromString(SampleJson, RootObject))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to parse JSON string."));
        return;
    }

    // 获取嵌套的 JSON 对象
    FJsonObjectWrapper WeaponObject;
    if (UJsonBlueprintFunctionLibrary::GetField(RootObject, TEXT("weapon"), WeaponObject))
    {
        FString WeaponName;
        float Damage;
        bool bAutomatic;

        UJsonBlueprintFunctionLibrary::GetField(WeaponObject, TEXT("name"), WeaponName);
        UJsonBlueprintFunctionLibrary::GetField(WeaponObject, TEXT("damage"), Damage);
        UJsonBlueprintFunctionLibrary::GetField(WeaponObject, TEXT("isAutomatic"), bAutomatic);

        UE_LOG(LogTemp, Log, TEXT("Weapon: %s, Damage: %.1f, Automatic: %s"),
            *WeaponName, Damage, bAutomatic ? TEXT("true") : TEXT("false"));
    }
}
```

## 模块依赖

要使用 `JsonBlueprintUtilities` 模块，你的项目模块（或插件模块）的 `Build.cs` 文件需要添加以下依赖。该插件本身依赖 `Json` 模块来处理核心的 JSON 解析和生成逻辑。

| 模块 | 用途 |
|---|---|
| `Json` | 核心 JSON 解析与序列化库，`JsonBlueprintUtilities` 的基础依赖 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构底层 JSON 对象以支持两种字符串存储方式，优化内存 |
| 2026-03-02 | `9758fa58` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 移除 JSON 对象中的字符串重复存储，以释放内存 |
| 2026-02-25 | `ec13ba36` | [Backout] - CL51209244 | 回退了一次提交 |
| 2026-02-25 | `af0dfacf` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 首次尝试移除字符串重复以优化内存 |
| 2024-01-22 | `7192b9d0` | Remove text.h from script.h (script.h is included by object.h) | 清理头文件依赖，移除不必要的包含 |

### 维护评价

`JsonBlueprintUtilities` 是一个功能明确、专注于蓝图 JSON 交互的插件。虽然其创建于 2021 年，但最近的提交历史（2026 年）显示其底层（`FJsonObject`）仍在接受性能优化和内存管理的重构，表明该插件处于**活跃维护**状态。

**需要注意的是**，该插件在 `.uplugin` 中标记为 `IsBetaVersion: true` 且 `EnabledByDefault: false`。这意味着：
1.  **功能可能不完善**：作为 Beta 版本，其 API 或行为在未来版本中可能发生不兼容的更改。
2.  **需要手动启用**：在使用前，必须在项目的 `.uproject` 文件或编辑器插件管理器中显式启用该插件。

尽管存在 Beta 标签，但鉴于它是 Epic Games 官方维护且近期有实质性更新，它是一个解决蓝图 JSON 需求的可靠选择。推荐在明确了解其 Beta 状态的前提下使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/JsonBlueprintUtilities)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/JsonBlueprintUtilities)（如果存在）