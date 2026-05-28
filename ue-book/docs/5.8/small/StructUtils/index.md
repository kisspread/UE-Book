# Struct Utils

> Experimental Struct Utilities supplying InstancedStruct type

| 属性 | 值 |
|---|---|
| 中文名 | 结构体工具 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `StructUtils` (Runtime), `StructUtilsEngine` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-04-20 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/StructUtils) | |

## 用途

该插件提供了一个名为 `FInstancedStruct` 的核心类型，用于解决 `UObject` 指针的局限性。`FInstancedStruct` 允许在运行时持有任意 `UScriptStruct` 派生类型的实例，并提供值语义（拷贝、移动）和类型安全的访问。它常用于需要灵活、类型安全的多态数据容器的场景，例如游戏框架中的动态数据传递、需要序列化的灵活数据结构等。

## 使用场景

-   你需要在运行时存储和传递一组不同类型的结构体数据，且不想使用 `UObject*` 指针（避免GC管理、引用问题）→ 使用 `FInstancedStruct`。
-   你在构建一个需要序列化/反序列化不同数据格式的系统（如游戏存档、网络消息），且希望数据结构是类型安全的 → 使用 `FInstancedStruct`。
-   你需要一个比 `USTRUCT` 更灵活、支持运行时多态的数据容器，用于游戏逻辑（如状态机、行为树数据、任务系统参数）→ 使用 `FInstancedStruct`。

## 蓝图用法

蓝图主要通过 `StructUtilsEngine` 模块中的 `UBlueprintInstancedStructHelper` 类和 `UInstancedStructLibrary` 类暴露功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Make Instanced Struct` | 从指定的 `UScriptStruct` 和值构造一个 `FInstancedStruct` | `UBlueprintInstancedStructHelper` |
| `Break Instanced Struct` | 将 `FInstancedStruct` 分解为其底层的 `UScriptStruct` 和数据值 | `UBlueprintInstancedStructHelper` |
| `Get Script Struct` | 获取 `FInstancedStruct` 中持有的结构体类型 | `UBlueprintInstancedStructHelper` |
| `Get Value` | 以“通配符”方式获取 `FInstancedStruct` 中的值（输出为 Wildcard） | `UBlueprintInstancedStructHelper` |
| `Set Value` | 以“通配符”方式设置 `FInstancedStruct` 中的值（输入为 Wildcard） | `UBlueprintInstancedStructHelper` |
| `To Instanced Struct` | 将任意 `USTRUCT` 蓝图变量转换为 `FInstancedStruct` | `UInstancedStructLibrary` |
| `From Instanced Struct` | 将 `FInstancedStruct` 转换回其原始的 `USTRUCT` 类型（输出为 Wildcard） | `UInstancedStructLibrary` |
| `Equal (Instanced Struct)` | 比较两个 `FInstancedStruct` 是否相等（结构体类型和值） | `UInstancedStructLibrary` |
| `Not Equal (Instanced Struct)` | 比较两个 `FInstancedStruct` 是否不等 | `UInstancedStructLibrary` |
| `Reset` | 重置 `FInstancedStruct`，使其为空（不持有任何类型和数据） | `UInstancedStructLibrary` |
| `Is Valid` | 检查 `FInstancedStruct` 是否有效（是否持有类型） | `UInstancedStructLibrary` |

### 使用示例（蓝图描述）

1.  **构造与分解**：使用 `Make Instanced Struct` 节点，输入一个具体的结构体类型（如 `FMyData`）和一个该类型的值，即可创建一个 `FInstancedStruct`。使用 `Break Instanced Struct` 节点，输入一个 `FInstancedStruct`，可以输出其 `Script Struct` 和一个 `Wildcard` 类型的值。你可以将 `Wildcard` 值引脚连接到需要具体类型的节点上，实现类型安全的访问。
2.  **类型转换**：如果你有一个 `FTransform` 变量，可以通过 `To Instanced Struct` 节点将其转换为 `FInstancedStruct`。反之，对于一个已知其内部存储类型的 `FInstancedStruct`，可以使用 `From Instanced Struct` 节点将其转换回具体的 `FTransform`。

## C++ 用法

### 头文件引入

```cpp
// 基本类型和核心功能
#include "StructUtils/StructUtils.h" // (StructUtils 模块)

// 蓝图辅助功能和资产
#include "StructUtils/InstancedStruct.h" // FInstancedStruct 定义 (通常包含在上面的头文件中)
#include "StructUtilsEngine/BuiltinStructs.h" // 可能包含一些内置结构体定义
```

### 基本用法

```cpp
// 创建一个 FInstancedStruct 实例
FInstancedStruct MyStruct;
// 可以从一个已有的 UScriptStruct* 和原始数据指针初始化
UScriptStruct* MyStructType = FMyData::StaticStruct();
FMyData InitialData;
MyStruct.InitializeAs(MyStructType, reinterpret_cast<const uint8*>(&InitialData));
// 或者更简单地，使用模板构造函数
FInstancedStruct AnotherStruct(FMyData{1, 2.0f, "Hello"});

// 检查类型和获取数据
if (MyStruct.IsValid())
{
    UScriptStruct* ActualType = MyStruct.GetScriptStruct();
    // 安全地获取指针（需确保类型匹配）
    if (ActualType == FMyData::StaticStruct())
    {
        const FMyData* DataPtr = MyStruct.GetPtr<FMyData>();
        if (DataPtr)
        {
            UE_LOG(LogTemp, Log, TEXT("Value: %d"), DataPtr->SomeInt);
        }
    }
}

// 重置
MyStruct.Reset();
```

*来源参考：引擎内对 FInstancedStruct 的单元测试和使用场景*

### 进阶用法

```cpp
// 复制和移动语义
FInstancedStruct StructA(FMyData{});
FInstancedStruct StructB = StructA; // 拷贝
FInstancedStruct StructC = MoveTemp(StructA); // 移动，StructA 变为空

// 比较操作
bool bAreEqual = (StructB == StructC); // 基于类型和二进制值比较

// 序列化
FMemoryWriter Writer(MemoryData);
StructB.Serialize(Writer);
FMemoryReader Reader(MemoryData);
FInstancedStruct StructD;
StructD.Serialize(Reader);

// 作为容器元素
TArray<FInstancedStruct> StructArray;
StructArray.Add(FInstancedStruct(FMyData{1}));
StructArray.Add(FInstancedStruct(FOtherData{2.0f}));
// 可以遍历数组，通过 GetScriptStruct() 判断类型并安全转换
for (const FInstancedStruct& StructElem : StructArray)
{
    if (StructElem.GetScriptStruct() == FMyData::StaticStruct())
    {
        const FMyData* Data = StructElem.GetPtr<FMyData>();
        // ... 处理 FMyData
    }
}
```

*来源参考：综合多个引擎模块对 FInstancedStruct 的使用方式*

## Demo 示例

```cpp
// MyActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "StructUtils/InstancedStruct.h"
#include "MyActor.generated.h"

UCLASS()
class AMyActor : public AActor
{
    GENERATED_BODY()

public:
    AMyActor();

    UPROPERTY(EditAnywhere, Category = "StructUtils Demo")
    FInstancedStruct RuntimeData;

    UFUNCTION(BlueprintCallable)
    void PrintRuntimeData();

private:
    void PopulateRuntimeData();
};

// MyActor.cpp
#include "MyActor.h"
#include "MyDataStruct.h" // 假设定义了 FMyData 和 FOtherData

AMyActor::AMyActor()
{
    PrimaryActorTick.bCanEverTick = false;
    // 在构造函数中，可以预设一个默认的结构体类型
    RuntimeData.InitializeAs(FMyData::StaticStruct());
}

void AMyActor::PopulateRuntimeData()
{
    // 根据某个条件动态填充不同的数据
    FMyData DataA{42, 3.14f, "StructA"};
    FOtherData DataB{true, FVector::OneVector};

    if (FMath::RandBool())
    {
        RuntimeData = FInstancedStruct(DataA);
    }
    else
    {
        RuntimeData = FInstancedStruct(DataB);
    }
}

void AMyActor::PrintRuntimeData()
{
    if (!RuntimeData.IsValid())
    {
        UE_LOG(LogTemp, Warning, TEXT("RuntimeData is not valid."));
        return;
    }

    UScriptStruct* Type = RuntimeData.GetScriptStruct();
    UE_LOG(LogTemp, Log, TEXT("RuntimeData type: %s"), *Type->GetName());

    if (Type == FMyData::StaticStruct())
    {
        const FMyData* Data = RuntimeData.GetPtr<FMyData>();
        UE_LOG(LogTemp, Log, TEXT("FMyData - Int: %d, Float: %f, String: %s"),
            Data->SomeInt, Data->SomeFloat, *Data->SomeString);
    }
    else if (Type == FOtherData::StaticStruct())
    {
        const FOtherData* Data = RuntimeData.GetPtr<FOtherData>();
        UE_LOG(LogTemp, Log, TEXT("FOtherData - Bool: %d, Vector: %s"),
            Data->bFlag, *Data->Location.ToString());
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `StructUtils` | 提供 `FInstancedStruct` 核心类型和基础库。**使用者必须依赖此模块。** |
| `StructUtilsEngine` | 提供蓝图暴露的 `UBlueprintInstancedStructHelper` 和 `UInstancedStructLibrary` 类，以及一些引擎内置结构体。**蓝图用户通常需要依赖此模块。** |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-08-05 | `5bf7f335` | Iris - Move InstancedStructNetSerializer to IrisCore. | 将 FInstancedStruct 的网络序列化器移至 Iris 网络模块，表明与新网络系统集成。 |
| 2024-08-01 | `0e320e33` | Iris - Crash fix for removing InstancedStruct from a replicated array and adding the same struct typ | 修复从复制数组中移除再添加相同类型 FInstancedStruct 时导致的崩溃。 |
| 2024-06-28 | `8083cf8c` | Iris - Adjust includes due to StructUtils moving. | 因 StructUtils 模块位置调整而更新头文件包含路径，属于维护性修改。 |
| 2024-06-28 | `3680fd08` | Iris - Initial naive but working version of FInstancedStructNetSerializer to be able to replicate FI | 为 FInstancedStruct 实现了初步的网络序列化功能，支持其在网络间复制。 |
| 2024-06-19 | `e6d36d75` | Remove references to deprecated plugin StructUtils (now part of CoreUObject) | 清理对旧版（已废弃并合并到CoreUObject的）StructUtils插件的引用，完成迁移。 |

### 维护评价

-   **创建时间**：2021年4月，已存在约4年。
-   **近期活跃度**：在2024年6-8月有多次提交，主要与Epic的 **Iris** 新网络系统进行集成（网络序列化器）和维护（Bug修复、路径调整）。这表明插件仍在被积极使用和适配。
-   **实验状态**：尽管近期有更新，但插件在 `.uplugin` 中明确标记为 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`，说明它仍处于实验阶段，API可能未稳定。
-   **生命周期注意**：Git记录显示旧版 `StructUtils` 插件已被废弃并合并到 `CoreUObject`，当前这个 `Engine/Plugins/Experimental/StructUtils` 是作为独立的、提供更丰富功能（如蓝图节点）的实验性扩展而存在的。
-   **推荐使用**：**推荐在新项目中谨慎使用**。对于需要运行时多态结构体的核心需求，该插件提供的 `FInstancedStruct` 是目前引擎内（非官方默认启用）的优秀解决方案。但由于其**实验性标签**和**依赖Epic正在开发的新网络系统（Iris）**，使用者需要接受未来可能的API变动风险。建议仅在明确需要其功能，并准备好跟踪引擎更新和潜在迁移的情况下使用。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/StructUtils)
-   [官方文档](https://docs.unrealengine.com/)（无专属文档，参考引擎源码及测试）
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/StructUtilsTests)