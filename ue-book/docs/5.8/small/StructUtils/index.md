# Struct Utils

> Experimental Struct Utilities supplying InstancedStruct type

| 属性 | 值 |
|---|---|
| 中文名 | 结构体工具集 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `StructUtils` (Runtime), `StructUtilsEngine` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-04-20 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/StructUtils) | |

## 用途

StructUtils 插件提供了一套用于在运行时安全、灵活地存储和操作任意 `UScriptStruct` 实例的工具。其核心是 `FInstancedStruct` 类型，它允许开发者在不丢失类型信息的前提下，以一种类似 `TArray<uint8>` 的方式存储任意结构体数据，但提供了类型安全的访问接口。这解决了需要在容器或变量中动态存储不同类型数据结构（例如从数据表或配置文件读取）的场景，避免了直接使用 `UObject*` 引用或原始数据指针的复杂性和风险。

## 使用场景

- 你需要在一个蓝图或C++变量中，根据条件存储不同的配置结构体（例如 `FWeaponData` 或 `FArmorData`）。
- 你在构建一个数据驱动的系统，数据结构（如怪物属性、技能参数）可能在未来扩展或变化，需要一个统一的容器来承载。
- 你需要将自定义的结构体数据进行序列化、复制（如网络复制），同时希望保持其底层类型的完整性。

## 蓝图用法

本插件的核心功能主要面向 C++ 开发，未提供直接的蓝图节点。其 `FInstancedStruct` 类型主要用于 C++ 层面的数据封装。在蓝图中，通常通过引擎其他系统（如自定义蓝图函数库或资产管理器）间接使用其功能。

## C++ 用法

### 头文件引入

```cpp
#include "InstancedStruct.h"
```

### 基本用法

以下示例展示了如何创建、设置和获取 `FInstancedStruct` 中的数据。

```cpp
// 定义一个示例结构体
USTRUCT(BlueprintType)
struct FMyData
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    float Value = 0.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FString Name;
};

// 使用 FInstancedStruct
void Example()
{
    // 1. 创建一个空的 FInstancedStruct
    FInstancedStruct InstancedStruct;

    // 2. 使其初始化为指定的结构体类型（可选，通常在从数据源初始化时使用）
    InstancedStruct.InitializeAs<FMyData>();

    // 3. 获取结构体的可写引用并修改数据
    if (FMyData* DataPtr = InstancedStruct.GetMutablePtr<FMyData>())
    {
        DataPtr->Value = 3.14f;
        DataPtr->Name = TEXT("Test");
    }

    // 4. 获取结构体的只读引用以读取数据
    if (const FMyData* DataConstPtr = InstancedStruct.GetPtr<FMyData>())
    {
        UE_LOG(LogTemp, Log, TEXT("Value: %f, Name: %s"), DataConstPtr->Value, *DataConstPtr->Name);
    }

    // 5. 检查类型
    if (InstancedStruct.GetScriptStruct() == FMyData::StaticStruct())
    {
        // 是 FMyData 类型
    }
}
```

### 进阶用法

`FInstancedStruct` 可以像普通值一样在容器（如 `TArray`）中使用，并且支持序列化。

```cpp
// 存储多种类型的结构体在数组中
TArray<FInstancedStruct> DataArray;

// 添加不同类型的数据
FInstancedStruct StructA;
StructA.InitializeAs<FMyData>();
// ... 填充 StructA
DataArray.Add(StructA);

FInstancedStruct StructB;
StructB.InitializeAs<FAnotherData>(); // 假设存在另一个结构体
// ... 填充 StructB
DataArray.Add(StructB);

// 遍历时，需要先判断类型
for (const FInstancedStruct& Struct : DataArray)
{
    if (const FMyData* MyData = Struct.GetPtr<FMyData>())
    {
        // 处理 FMyData
    }
    else if (const FAnotherData* AnotherData = Struct.GetPtr<FAnotherData>())
    {
        // 处理 FAnotherData
    }
}
```

## Demo 示例

以下是一个最小化的自定义类，演示了 `FInstancedStruct` 的基本使用。

```cpp
// MyStructUtilsExample.h
#pragma once

#include "CoreMinimal.h"
#include "InstancedStruct.h"
#include "MyStructUtilsExample.generated.h"

USTRUCT(BlueprintType)
struct FSampleStruct
{
    GENERATED_BODY()

    UPROPERTY()
    int32 IntegerValue = 0;

    UPROPERTY()
    FString StringValue;
};

UCLASS()
class UMyStructUtilsExample : public UObject
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable)
    void CreateAndPopulateStruct();

    UFUNCTION(BlueprintCallable)
    void PrintStructData() const;

private:
    UPROPERTY()
    FInstancedStruct StoredStruct;
};
```

```cpp
// MyStructUtilsExample.cpp
#include "MyStructUtilsExample.h"

void UMyStructUtilsExample::CreateAndPopulateStruct()
{
    // 将 StoredStruct 初始化为 FSampleStruct 类型
    StoredStruct.InitializeAs<FSampleStruct>();

    // 修改数据
    if (FSampleStruct* SampleData = StoredStruct.GetMutablePtr<FSampleStruct>())
    {
        SampleData->IntegerValue = 42;
        SampleData->StringValue = TEXT("Hello, StructUtils!");
    }
}

void UMyStructUtilsExample::PrintStructData() const
{
    // 安全地读取数据
    if (const FSampleStruct* SampleData = StoredStruct.GetPtr<FSampleStruct>())
    {
        UE_LOG(LogTemp, Log, TEXT("Integer: %d, String: %s"),
            SampleData->IntegerValue, *SampleData->StringValue);
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("StoredStruct does not contain FSampleStruct."));
    }
}
```

## 模块依赖

本插件的模块没有特殊的外部依赖。

| 模块 | 用途 |
|---|---|
| （无） | 无特殊依赖（仅标准 Core/Engine 等） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-08-05 | `5bf7f335` | Iris - Move InstancedStructNetSerializer to IrisCore. | 将 InstancedStruct 的网络序列化器移至 IrisCore 模块。 |
| 2024-08-01 | `0e320e33` | Iris - Crash fix for removing InstancedStruct from a replicated array and adding the same struct typ | 修复从复制数组中移除 InstancedStruct 后再添加相同结构体类型时的崩溃。 |
| 2024-06-28 | `8083cf8c` | Iris - Adjust includes due to StructUtils moving. | 因 StructUtils 模块移动，调整相关头文件包含。 |
| 2024-06-28 | `3680fd08` | Iris - Initial naive but working version of FInstancedStructNetSerializer to be able to replicate FI | 为 FInstancedStruct 添加了初步可用的网络序列化器（Iris 网络系统）。 |
| 2024-06-19 | `e6d36d75` | Remove references to deprecated plugin StructUtils (now part of CoreUObject) | 移除对已废弃的独立 StructUtils 插件的引用，表明其功能已融入 CoreUObject。 |

### 维护评价

**维护评价：已整合，不推荐作为独立插件使用。**
- **年龄**：插件创建于2021年，至今约4年。
- **活跃度**：2024年仍有相关提交，但近期提交内容（如“移至CoreUObject”、“移至IrisCore”）强烈表明，`FInstancedStruct` 等核心功能已被整合进引擎更核心的模块（CoreUObject）或特定子系统（Iris网络）。此独立的 `Experimental` 插件可能仅作为遗留入口或特定版本的兼容层存在。
- **已知限制**：`.uplugin` 明确标记为 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`，需要手动启用。其 `DeprecatedEngineVersion: 5.5` 进一步暗示它可能在引擎后续版本中被彻底移除。
- **推荐**：**不推荐**在新的、长期维护的项目中依赖此实验性插件。应优先检查并使用 `CoreUObject` 中官方提供的 `FInstancedStruct`（从 UE 5.4+ 开始）。如果必须使用，请注意其生命周期可能随引擎版本更新而终结。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/StructUtils)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/StructUtils/Tests) (推断路径)