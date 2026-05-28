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
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/StructUtils) | |

## 用途

StructUtils 插件为 Unreal Engine 提供了一个名为 `FInstancedStruct` 的核心类型。它本质上是一个**类型安全的、可序列化的容器**，可以持有任意 `USTRUCT` 的实例。

**解决的问题**：
在传统的 UE 开发中，如果你需要在蓝图或通用容器中存储不同类型的结构体数据，会面临难题：
1.  `TArray<UObject*>` 可以存储不同类型的 `UObject`，但对于值类型的 `USTRUCT` 没有等价物。
2.  使用 `void*` 或 `TMap<FName, ...>` 会丢失类型信息，导致序列化、复制和蓝图访问变得复杂且不安全。

`FInstancedStruct` 解决了这个问题。它允许你像处理 `UObject*` 一样，安全地在蓝图中创建、存储、访问和传递不同的 `USTRUCT` 数据，同时保留完整的类型信息和序列化能力。这使得构建灵活、数据驱动的系统（如 Gameplay Ability System 的上下文、AI 行为树的自定义节点数据）变得更加简单。

## 使用场景

-   **蓝图中的异构数据存储**：在蓝图数组或变量中存储不同类型的“事件”或“配置”结构体，无需为每种类型创建单独的变量。
-   **数据驱动组件**：创建一个组件，其属性可以在编辑器中配置为任意 `USTRUCT`，例如定义不同的状态效果、视觉配置或 AI 参数。
-   **Gameplay 框架**：在通用消息总线或事件系统中传递结构体数据，接收方可以根据存储的结构体类型进行安全地提取和处理。
-   **资产/数据表**：作为 `UDataTable` 行中某一列的数据类型，该列可以存储不同但已知的 `USTRUCT` 类型。

## 蓝图用法

`FInstancedStruct` 通常通过其暴露给蓝图的静态工厂函数和成员函数来使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Make Struct Instance` | 创建一个包含指定 `USTRUCT` 类型和初始化数据的 `FInstancedStruct`。 | `FInstancedStruct` (蓝图库) |
| `Set Struct Value` | 设置 `FInstancedStruct` 内部存储的值。 | `FInstancedStruct` (蓝图库) |
| `Get Struct Value` | 从 `FInstancedStruct` 中安全地提取特定类型的值。若类型不匹配则返回默认值。 | `FInstancedStruct` (蓝图库) |
| `Is Valid` | 检查 `FInstancedStruct` 是否包含有效数据（即其 `Struct` 成员是否为 `nullptr`）。 | `FInstancedStruct` (蓝图库) |
| `Get Struct` | 获取内部存储的 `USTRUCT` 的 `UScriptStruct` 类型描述符。 | `FInstancedStruct` (蓝图库) |
| `Reset` | 重置 `FInstancedStruct`，释放其持有的数据。 | `FInstancedStruct` (蓝图库) |

### 使用示例（蓝图描述）

1.  **创建**：使用 `Make Struct Instance` 节点。在“Struct Type”引脚选择你定义的 `USTRUCT`（如 `FMyCustomData`），在“Value”引脚连接该结构体的值。
2.  **存储**：将输出的 `FInstancedStruct` 变量存入数组、传递给其他函数。
3.  **访问**：在需要数据的地方，使用 `Get Struct Value` 节点。指定“Struct Type”为你期望的类型（如 `FMyCustomData`），如果存入的确实是该类型，则会输出其值；否则输出该类型的默认值。

## C++ 用法

### 头文件引入

```cpp
#include "StructUtils/InstancedStruct.h"
```

### 基本用法

```cpp
// 假设已定义 USTRUCT()
USTRUCT(BlueprintType)
struct FMyData
{
    GENERATED_BODY()

    UPROPERTY()
    float Health;

    UPROPERTY()
    FString Name;
};

// 创建一个包含 FMyData 的 FInstancedStruct
FMyData MyData;
MyData.Health = 100.0f;
MyData.Name = TEXT("Hero");
FInstancedStruct InstancedStruct = FInstancedStruct::Make(MyData);

// 从 FInstancedStruct 中取回数据
if (const FMyData* RetrievedData = InstancedStruct.GetPtr<FMyData>())
{
    UE_LOG(LogTemp, Log, TEXT("Name: %s, Health: %f"), *RetrievedData->Name, RetrievedData->Health);
}

// 重置容器
InstancedStruct.Reset();
```

### 进阶用法

```cpp
// 使用模板构造函数直接初始化
FInstancedStruct AnotherStruct(FMyData{ 50.0f, TEXT("Monster") });

// 用于容器
TArray<FInstancedStruct> StructArray;
StructArray.Add(FInstancedStruct::Make(FMyData{100, "A"}));
StructArray.Add(FInstancedStruct::Make(FVector{1,2,3})); // 可以存储不同类型

// 遍历容器并进行类型安全的操作
for (const FInstancedStruct& Elem : StructArray)
{
    if (const FMyData* MyDataPtr = Elem.GetPtr<FMyData>())
    {
        // 处理 FMyData
    }
    else if (const FVector* VecPtr = Elem.GetPtr<FVector>())
    {
        // 处理 FVector
    }
}
```

## Demo 示例

**MyStructUtilsActor.h**
```cpp
// MyStructUtilsActor.h
#pragma once

#include "GameFramework/Actor.h"
#include "StructUtils/InstancedStruct.h"
#include "MyStructUtilsActor.generated.h"

USTRUCT(BlueprintType)
struct FActorSpawnInfo
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere)
    TSubclassOf<AActor> ActorClass;

    UPROPERTY(EditAnywhere)
    FTransform SpawnTransform;

    UPROPERTY(EditAnywhere)
    bool bSpawnActive = true;
};

UCLASS()
class AMyStructUtilsActor : public AActor
{
    GENERATED_BODY()

public:
    AMyStructUtilsActor();

    // 蓝图可调用：从FInstancedStruct中提取并执行数据
    UFUNCTION(BlueprintCallable, Category="StructUtils")
    void ExecuteSpawnInfo(const FInstancedStruct& SpawnData);

protected:
    // 编辑器中可配置的任意结构体数据
    UPROPERTY(EditAnywhere, Category="Config")
    FInstancedStruct ConfigData;
};
```

**MyStructUtilsActor.cpp**
```cpp
// MyStructUtilsActor.cpp
#include "MyStructUtilsActor.h"
#include "Engine/World.h"

AMyStructUtilsActor::AMyStructUtilsActor()
{
    PrimaryActorTick.bCanEverTick = false;
    // 在构造函数中初始化 ConfigData 为一个示例值
    ConfigData = FInstancedStruct::Make(FActorSpawnInfo{});
}

void AMyStructUtilsActor::ExecuteSpawnInfo(const FInstancedStruct& SpawnData)
{
    // 安全地提取我们期望的结构体类型
    if (const FActorSpawnInfo* SpawnInfo = SpawnData.GetPtr<FActorSpawnInfo>())
    {
        if (SpawnInfo->ActorClass && SpawnInfo->bSpawnActive)
        {
            GetWorld()->SpawnActor<AActor>(
                SpawnInfo->ActorClass,
                &SpawnInfo->SpawnTransform
            );
        }
    }
}
```

## 模块依赖

从源码和构建脚本分析，此插件的依赖关系清晰，均为引擎常见模块。

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | |

**说明**：`StructUtils` 模块在 `Build.cs` 中明确依赖 `Engine`。`StructUtilsEngine` 模块未提供依赖列表，但根据其运行时类型和功能（涉及 `USTRUCT` 和网络序列化），它必然依赖 `CoreUObject` 和 `Engine`。这些均为引擎核心模块，无需用户额外手动添加依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-08-05 | `5bf7f335` | Iris - Move InstancedStructNetSerializer to IrisCore. | 将网络序列化器迁移到IrisCore，插件核心功能可能已稳定。 |
| 2024-08-01 | `0e320e33` | Iris - Crash fix for removing InstancedStruct from a replicated array and adding the same struct typ | 修复在复制数组中删除再添加同类型InstancedStruct时的崩溃。 |
| 2024-06-28 | `8083cf8c` | Iris - Adjust includes due to StructUtils moving. | 因StructUtils位置变动调整头文件包含路径。 |
| 2024-06-28 | `3680fd08` | Iris - Initial naive but working version of FInstancedStructNetSerializer to be able to replicate FI | 为InstancedStruct实现了初步的网络复制能力。 |
| 2024-06-19 | `e6d36d75` | Remove references to deprecated plugin StructUtils (now part of CoreUObject) | **重要：移除对已废弃的插件的引用，指出其功能已并入CoreUObject。** |

### 维护评价

**综合评价：⚠️ 请谨慎使用**

1.  **年龄与状态**：插件创建于2021年，目前仍标记为实验性 (`IsExperimentalVersion: true`) 且默认禁用。
2.  **最新动态**：最后几次提交（2024年6-8月）都与网络复制 (`NetSerializer`) 功能相关，表明核心功能（`FInstancedStruct`）早已稳定，维护工作主要在扩展其网络能力。
3.  **关键警告**：最近的提交 (`e6d36d75`) 清晰地指出 **“StructUtils now part of CoreUObject”**。这意味着 `FInstancedStruct` 这个核心类型很可能已经迁移到 `CoreUObject` 模块中，成为引擎内置功能。**继续使用这个实验性插件可能已无必要，甚至会在未来版本中移除**。
4.  **推荐建议**：
    -   对于新项目，应首先查阅 `CoreUObject` 或相关引擎模块中是否已包含 `FInstancedStruct`。
    -   如果仍在使用此插件，建议制定计划，将代码迁移到使用 `CoreUObject` 中的新版本，以避免插件被移除后出现兼容性问题。
    -   此插件目前仅对 `LiveLinkHub` 程序启用 (`SupportedPrograms`)，进一步限制了其通用性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/StructUtils)
- [官方文档](  ) （无）
- [测试用例](  ) （未提供路径）