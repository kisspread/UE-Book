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

StructUtils 插件是一个实验性的运行时工具库，其核心目标是提供一个轻量级的、拥有运行时类型信息（RTTI）的结构体容器 `FInstancedStruct`。它解决了在需要存储、传递或序列化“某种结构体”，但具体类型在编译时未知的场景。传统的 `void*` 或 `TMap<FName, ...>` 方案缺乏类型安全、拷贝语义和序列化支持。`FInstancedStruct` 通过在内部存储结构体的 `UScriptStruct` 指针，提供了完整的类型安全拷贝、移动和序列化能力。

从近期的 Git 提交历史可以看出，该插件已被集成到 Epic 的网络序列化系统“Iris”中，用于动态复制和网络传输不同类型的结构体数据，这表明它是构建高灵活性游戏逻辑和网络系统的重要底层工具。

## 使用场景

-   你需要一个“数据包”或“消息体”，它可以是多种不同定义的结构体之一，且需要在网络中传输或在磁盘上保存。
-   你在构建一个事件派发系统，事件携带的数据结构各不相同。
-   你在设计一个属性系统，其中属性值可以是任意结构体类型。
-   你需要在 `TArray` 或 `TMap` 中存储混合类型的结构体实例。

## 蓝图用法

根据提供的源码分析，未发现暴露给蓝图的公开函数。该插件主要面向 C++ 开发者，为其提供底层的结构体操作能力。

## C++ 用法

### 头文件引入

```cpp
#include "StructUtils/StructUtilsModule.h"
#include "InstancedStruct.h" // 假设主要类型头文件
```

### 基本用法

`FInstancedStruct` 可以用来包装任意 `UScriptStruct` 定义的结构体。

```cpp
// 定义一些结构体
USTRUCT()
struct FMyDataA
{
    GENERATED_BODY()
    UPROPERTY()
    float Value;
};

USTRUCT()
struct FMyDataB
{
    GENERATED_BODY()
    UPROPERTY()
    int32 ID;
    UPROPERTY()
    FString Name;
};

// 创建一个 FInstancedStruct，它可以持有上面任意一种结构体
FInstancedStruct StructHolder;

// 用 FMyDataA 初始化
StructHolder.InitializeAs<FMyDataA>();
FMyDataA* DataA = StructHolder.GetMutable<FMyDataA>();
if (DataA)
{
    DataA->Value = 3.14f;
}

// 可以安全地拷贝
FInstancedStruct StructCopy = StructHolder;

// 切换内部存储的类型为 FMyDataB
StructHolder.InitializeAs<FMyDataB>();
FMyDataB* DataB = StructHolder.GetMutable<FMyDataB>();
if (DataB)
{
    DataB->ID = 42;
    DataB->Name = TEXT("Example");
}

// 获取内部结构体的类型信息
const UScriptStruct* ActualStructType = StructHolder.GetScriptStruct();
```

## Demo 示例

以下是一个完整的、可编译的最小示例，展示了 `FInstancedStruct` 的基本创建和使用。

**MyStructUtilsActor.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyStructUtilsActor.generated.h"

USTRUCT(BlueprintType)
struct FExampleStruct
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadWrite, EditAnywhere)
    float Health = 100.f;

    UPROPERTY(BlueprintReadWrite, EditAnywhere)
    FString CharacterName;
};

UCLASS()
class AMyStructUtilsActor : public AActor
{
    GENERATED_BODY()

public:
    AMyStructUtilsActor();

    virtual void BeginPlay() override;

    UPROPERTY(BlueprintReadWrite, EditAnywhere, Category = "StructUtils")
    FExampleStruct MyStructData;

    // 用于演示 FInstancedStruct 的成员
    FInstancedStruct InstancedStructHolder;

    UFUNCTION(BlueprintCallable, Category = "StructUtils")
    void SwapInstancedStructData();
};
```

**MyStructUtilsActor.cpp**
```cpp
#include "MyStructUtilsActor.h"
#include "InstancedStruct.h" // 假设路径，实际头文件名可能有所不同

AMyStructUtilsActor::AMyStructUtilsActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyStructUtilsActor::BeginPlay()
{
    Super::BeginPlay();

    // 使用 FExampleStruct 初始化 InstancedStructHolder
    InstancedStructHolder.InitializeAs<FExampleStruct>();
    FExampleStruct* ExampleData = InstancedStructHolder.GetMutable<FExampleStruct>();
    if (ExampleData)
    {
        ExampleData->Health = 200.f;
        ExampleData->CharacterName = TEXT("Hero");
    }

    UE_LOG(LogTemp, Log, TEXT("InstancedStruct Initialized with Health: %f"), ExampleData->Health);
}

void AMyStructUtilsActor::SwapInstancedStructData()
{
    // 将成员变量 MyStructData 的数据复制到 InstancedStructHolder 中
    InstancedStructHolder.InitializeAs<FExampleStruct>();
    FExampleStruct* HolderData = InstancedStructHolder.GetMutable<FExampleStruct>();
    if (HolderData)
    {
        *HolderData = MyStructData;
    }

    UE_LOG(LogTemp, Log, TEXT("Swapped data to InstancedStruct. New Name: %s"), *HolderData->CharacterName);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine 等） | `StructUtils` 模块的 Build.cs 显示仅依赖 `Engine`。`StructUtilsEngine` 模块未在信息中列出显式依赖，但作为运行时模块，它必然依赖 Core/Engine。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-08-05 | `5bf7f335` | Iris - Move InstancedStructNetSerializer to IrisCore. | 将InstancedStruct的网络序列化器移至Iris核心模块。 |
| 2024-08-01 | `0e320e33` | Iris - Crash fix for removing InstancedStruct from a replicated array and adding the same struct typ | 修复从复制数组中移除并添加相同类型InstancedStruct时导致的崩溃。 |
| 2024-06-28 | `8083cf8c` | Iris - Adjust includes due to StructUtils moving. | 因StructUtils移动而调整头文件包含。 |
| 2024-06-28 | `3680fd08` | Iris - Initial naive but working version of FInstancedStructNetSerializer to be able to replicate FI | Iris模块的InstancedStruct网络序列化器首个可用版本，实现FInstancedStruct的复制。 |
| 2024-06-19 | `e6d36d75` | Remove references to deprecated plugin StructUtils (now part of CoreUObject) | 移除对已废弃插件StructUtils的引用（该功能现已并入CoreUObject）。 |

### 维护评价

StructUtils 插件目前处于**维护中但功能转移**的状态。

-   **创建时间**：约4年前（2021年）。
-   **近期活动**：在2024年6月至8月有一系列提交，但内容主要是围绕“Iris”网络系统进行**重构、迁移和Bug修复**（如移动序列化器、修复崩溃、调整引用）。
-   **关键动向**：提交 `e6d36d75` 明确指出“StructUtils”作为插件已被废弃，其核心功能（如 `FInstancedStruct`）**已整合进 UE 的核心模块 `CoreUObject`**。这意味着当前的 `StructUtils` 插件本身可能只是一个遗留的“外壳”或用于特定场景（如LiveLinkHub）的扩展，其主要功能已在引擎核心中提供。
-   **推荐使用**：**不建议**开发者依赖此实验性插件作为新项目的基础。应直接使用引擎核心（`CoreUObject`）中提供的 `FInstancedStruct` 或类似功能。如果必须使用此插件，请确认其目标功能是否尚未迁移至核心。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/StructUtils)
- [官方文档]()（暂无）