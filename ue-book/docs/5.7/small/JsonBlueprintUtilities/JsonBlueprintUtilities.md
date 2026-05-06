# Json Blueprint Utilities

> Json functionality for Blueprint.

| 属性 | 值 |
|---|---|
| 中文名 | JSON 蓝图工具 |
| 分类 | Blueprints |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图节点） |
| 模块 | `JsonBlueprintUtilities` (Runtime), `JsonBlueprintGraph` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-10-21 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/JsonBlueprintUtilities) | |

## 用途

Json Blueprint Utilities 是一个轻量级插件，旨在为蓝图提供直接、友好的 JSON 数据读写能力。它解决了以下痛点：

- 原生蓝图缺乏对 JSON 对象（`FJsonObjectWrapper`）的直接操作节点。
- 需要序列化/反序列化配置数据、服务端响应或本地存档时，通常需要编写 C++ 代码或使用复杂的外部库。
- 通过封装 `JsonObjectWrapper` 和对 `FJsonObject` 的操作，让蓝图开发者可以不写一行 C++ 就完成从文件/字符串创建、读取字段、写入字段、以及将结构体导出为 JSON 字符串等常见任务。

## 使用场景

- **读取配置文件**：将游戏设置、关卡数据等存储为 `.json` 文件，并通过蓝图加载。
- **处理 Web API 响应**：蓝图调用 HTTP 请求后，将返回的 JSON 字符串解析为对象，并提取特定字段。
- **保存/载入游戏存档**：使用 `Save Json to File` 和 `Load Json from File` 节点，序列化复杂存档数据。
- **调试与日志**：将关键结构体转换为 JSON 字符串并打印到屏幕上，方便可视化调试。

## 蓝图用法

插件提供了一组以 `Json` 为分类的蓝图可调用节点，主要分为：文件/字符串操作、字段访问与修改、结构体与 JSON 互转、字段检查与枚举四大类。

### 核心节点

#### 📂 文件与字符串操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Load Json from String` | 从源字符串创建 `FJsonObjectWrapper` | `UJsonBlueprintFunctionLibrary` |
| `Load Json from File` | 从指定文件路径创建 `FJsonObjectWrapper` | `UJsonBlueprintFunctionLibrary` |
| `Get Json String` | 将 `FJsonObjectWrapper` 序列化为格式化 JSON 字符串 | `UJsonBlueprintFunctionLibrary` |
| `Save Json to File` | 将 `FJsonObjectWrapper` 写入磁盘文件 | `UJsonBlueprintFunctionLibrary` |

#### 🔍 字段访问与修改

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetField` | 获取指定字段的值（支持 int/bool/float/string/Struct 等类型，通过 `CustomStructureParam` 动态匹配） | `UJsonBlueprintFunctionLibrary` |
| `SetField` | 设置（或新增）指定字段的值（同样支持动态类型匹配） | `UJsonBlueprintFunctionLibrary` |

#### 🔄 结构体与 JSON 互转

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Convert Struct To Json String` | 将任意 UStruct 转换为 JSON 字符串，无需手动拼字段 | `UJsonBlueprintFunctionLibrary` |

#### ✅ 字段检查与枚举

| 节点 | 说明 | 所在类 |
|---|---|---|
| `HasField` | 检查 JSON 对象中是否存在指定字段 | `UJsonBlueprintFunctionLibrary` |
| `GetFieldNames` | 获取 JSON 对象中所有字段的名称数组 | `UJsonBlueprintFunctionLibrary` |

### 使用示例（蓝图描述）

**场景：从字符串加载 JSON，然后读取某个字段**

1. 将一个字符串常量（例如 `{"name":"Alice","age":25}`）连接到 `Load Json from String` 的 `JsonString` 输入。
2. 从 `Load Json from String` 成功执行后的 `JsonObject` 引脚引出 `GetField` 节点。
3. 设置 `GetField` 的 `FieldName` 为 `"age"`，并将 `Value` 引脚的类型改为 `Integer`（默认是 Integer，也可以改成其他类型，节点会自动适配）。
4. 若成功，`Value` 输出即为 `25`。

**场景：将角色属性结构体转换为 JSON 并保存到文件**

1. 创建一个结构体变量（例如 `FInventoryData`），填充数据。
2. 调用 `Convert Struct To Json String`，将结构体变量连接到 `Struct` 输入。
3. 将输出的 JSON 字符串连接到一个 `Load Json from String` 节点，得到 `FJsonObjectWrapper`。
4. 调用 `Save Json to File`，指定文件路径（`FFilePath`）即可。

## C++ 用法

本插件主要面向蓝图用户，但 C++ 开发者也可直接调用其静态函数库。

### 头文件引入

```cpp
#include "JsonBlueprintFunctionLibrary.h"
```

### 基本用法

```cpp
// 从字符串加载 JSON
FJsonObjectWrapper JsonObject;
FString JsonString = TEXT("{\"key\":\"value\"}");
bool bSuccess = UJsonBlueprintFunctionLibrary::FromString(JsonString, JsonObject);

// 检查字段是否存在
bool bHasKey = UJsonBlueprintFunctionLibrary::HasField(JsonObject, TEXT("key"));

// 获取字段值（这里以 int32 为例，实际可用 Property 动态处理）
int32 Value = 0;
UJsonBlueprintFunctionLibrary::GetField(JsonObject, TEXT("some_int"), Value);

// 序列化为字符串
FString OutString;
UJsonBlueprintFunctionLibrary::ToString(JsonObject, OutString);
```

### 进阶用法

```cpp
// 将自定义结构体转为 JSON 字符串
FMyStruct MyStruct;
FString JsonString;
UJsonBlueprintFunctionLibrary::StructToJsonString(MyStruct, JsonString);

// 从文件加载并保存
FFilePath FilePath;
FilePath.FilePath = TEXT("C:/Game/config.json");
UJsonBlueprintFunctionLibrary::FromFile(FilePath, JsonObject);
// ... 修改 JsonObject ...
UJsonBlueprintFunctionLibrary::ToFile(JsonObject, FilePath);
```

## Demo 示例

以下是一个完整的最小示例，演示如何从字符串加载 JSON 并获取字段。

**MyJsonActor.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyJsonActor.generated.h"

UCLASS()
class AMyJsonActor : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable, Category = "Demo")
    void LoadAndPrintJson();
};
```

**MyJsonActor.cpp**

```cpp
#include "MyJsonActor.h"
#include "JsonBlueprintFunctionLibrary.h"
#include "JsonObjectWrapper.h"

void AMyJsonActor::BeginPlay()
{
    Super::BeginPlay();
    LoadAndPrintJson();
}

void AMyJsonActor::LoadAndPrintJson()
{
    // 模拟从网络或文件获取的 JSON 字符串
    const FString JsonString = TEXT("{\"character_name\":\"Hero\",\"level\":10,\"is_alive\":true}");

    FJsonObjectWrapper JsonObject;
    if (!UJsonBlueprintFunctionLibrary::FromString(JsonString, JsonObject))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to parse JSON"));
        return;
    }

    // 检查并获取字段
    if (UJsonBlueprintFunctionLibrary::HasField(JsonObject, TEXT("character_name")))
    {
        FString Name;
        // 注意：GetField 使用 CustomThunk，需要手动指定目标属性
        UJsonBlueprintFunctionLibrary::GetField(JsonObject, TEXT("character_name"), Name);
        UE_LOG(LogTemp, Log, TEXT("Character Name: %s"), *Name);
    }

    // 将整个对象转回字符串打印
    FString OutString;
    UJsonBlueprintFunctionLibrary::ToString(JsonObject, OutString);
    UE_LOG(LogTemp, Log, TEXT("Full JSON: %s"), *OutString);
}
```

## 模块依赖

本插件比较轻量，依赖项很少，且不公开给外部使用。以下为内部 Build.cs 中记载的特殊依赖（常见模块已省略）：

| 模块 | 用途 |
|---|---|
| `JsonUtilities` | 提供 `FJsonObjectWrapper` 类型 |

**结论**：外部模块若要使用 `JsonBlueprintUtilities`，只需在 `PublicDependencyModuleNames` 中添加 `"JsonBlueprintUtilities"` 即可，无需额外依赖。

## 维护状态

### 近期更新

- 2024-01-22 `7192b9d0` 从 script.h 移除 text.h（降低构建影响）
- 2023-12-21 `f39df392` 移除两个 Json 加载函数中未使用的 World Context 参数
- 2023-03-11 `d3cf046a` 为避免单节点修改后刷新整个 SGraphPanel 做基础铺垫
- 2023-01-16 `bbc37aa2` 引擎/插件常规更新
- 2022-10-21 `610c4676` 更新内置插件供应商链接为安全协议（插件创建初始 commit）

### 维护评价

- **创建时间**：2022 年 10 月，约 3 年历史，属于 UE5 早期引入的插件。
- **最近更新**：最后一次实质性功能修改在 2023 年 12 月（移除世界上下文参数），后续仅有编译优化调整。最近一年没有新增功能。
- **活跃度**：当前处于**维护不活跃**状态，但作为轻量工具库，其功能已基本稳定（读/写/查字段）。
- **已知问题**：无公开已知 bug。由于使用 `CustomThunk` 进行动态属性绑定，在蓝图节点上类型匹配可能不如标准节点直观，但这是设计权衡。
- **是否推荐**：推荐使用。对于需要简单 JSON 处理的蓝图项目，这是最轻量、官方支持的方案。但若需要复杂的 JSONPath 查询或大规模文档操作，建议考虑 C++ 直接使用 `FJsonObject` 或第三方库。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/JsonBlueprintUtilities)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/JsonBlueprintUtilities/Tests)