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

此插件是实验性的结构体工具集，核心目标是提供一个安全、类型擦除的容器类型 `FInstancedStruct`，用于在运行时存储任意结构体（USTRUCT）的实例。这解决了在需要持有类型未知的结构体数据（例如从网络接收或从数据表加载）时，直接使用 `FStructOnScope` 或 `TArray<uint8>` 带来的不安全性和复杂性问题。它允许在蓝图和 C++ 中安全地操作这些“未知类型”的结构体数据，并支持在数据驱动的游戏逻辑（如 Gameplay Ability System 的 Effect Context、AI 行为树的黑板值）中传递复杂、异构的数据。该插件的 `SupportedPrograms` 设置为 `LiveLinkHub`，表明其最初设计与 LiveLink 系统有紧密关联，用于处理动态的、类型多变的属性数据。

## 使用场景

- 你需要在运行时存储一个结构体，但其具体类型在代码编写时未知（例如，根据配置文件或网络数据动态决定）。
- 你在实现一个数据驱动的系统，该系统需要能够处理多种不同类型的结构体数据（例如，自定义的 GamePlay Effect Context、AI 黑板条目）。
- 你需要在网络中同步或序列化一个类型可能变化的结构体实例。
- 你正在为 LiveLink 或其他动态属性系统开发自定义功能。

## 蓝图用法

此插件主要通过其核心类型 `FInstancedStruct` 在蓝图中工作。`FInstancedStruct` 本身是一个 `UStruct`，因此可以在蓝图中作为变量类型使用，并通过标准的结构体节点进行操作。其关键操作通常通过蓝图函数库（如果存在）或通过泛型接口暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Make Struct` | 根据提供的 `UScriptStruct*`（例如通过 `Find Struct` 获取）创建一个新的、空的 `FInstancedStruct` 实例。 | `UBlueprintFunctionLibrary` (推测) |
| `Set Struct Value` | 将一个已存在的、类型匹配的结构体值写入到 `FInstancedStruct` 中。 | `FInstancedStruct` |
| `Get Struct Value` | 从 `FInstancedStruct` 中读取结构体值，输出到指定的结构体引脚（需要在运行时知道目标类型）。 | `FInstancedStruct` |

### 使用示例（蓝图描述）

1.  **创建和初始化**：使用 `Find Struct` 节点查找一个结构体类型（例如 “MyCustomData”），然后将其作为输入连接到 `Make Struct` 节点，输出一个 `FInstancedStruct` 变量。
2.  **设置值**：将一个具体的 “MyCustomData” 结构体变量连接到 `Set Struct Value` 节点的 “Value” 引脚，并将步骤1中创建的 `FInstancedStruct` 变量连接到 “Target” 引脚。
3.  **获取值**：将包含数据的 `FInstancedStruct` 变量连接到 `Get Struct Value` 节点的 “Target” 引脚，并将一个 “MyCustomData” 类型的变量连接到 “Value” 输出引脚。确保在运行时，`FInstancedStruct` 内存储的确实是 “MyCustomData” 类型，否则会失败。

## C++ 用法

核心类型 `FInstancedStruct` 定义在 `StructUtilsEngine` 模块中。使用前需要包含相应的头文件。

### 头文件引入

```cpp
#include "InstancedStruct.h"
```

### 基本用法

以下示例展示了 `FInstancedStruct` 的基本创建和访问操作。

```cpp
// 来源：引擎内部通用用法，基于 FInstancedStruct 公共接口
#include "InstancedStruct.h"

// 1. 从已知的 UScriptStruct* 创建一个空的实例
UScriptStruct* MyStructType = FMyData::StaticStruct();
FInstancedStruct InstancedStruct(MyStructType);

// 2. 设置值
FMyData Data;
Data.SomeValue = 42;
InstancedStruct.Set<FMyData>(Data);
// 或者使用赋值
// InstancedStruct = FInstancedStruct::Make<FMyData>(Data);

// 3. 获取值 (需要确保类型安全)
if (InstancedStruct.GetScriptStruct() == FMyData::StaticStruct())
{
    const FMyData& RetrievedData = InstancedStruct.Get<FMyData>();
    // 使用 RetrievedData.SomeValue
}

// 4. 检查是否包含值
if (InstancedStruct.IsValid())
{
    // 结构体有效
}

// 5. 重置
InstancedStruct.Reset();
```

### 进阶用法

`FInstancedStruct` 与 UE 的反射系统结合，可用于数据序列化和网络同步。

```cpp
// 网络序列化示例概念 (基于 git log 中的 InstancedStructNetSerializer)
// 假设在一个 Actor 的属性中
UPROPERTY()
FInstancedStruct ReplicatedContext;

// 在 GetLifetimeReplicatedProps 中注册
DOREPLIFETIME(ThisClass, ReplicatedContext);

// 序列化由引擎提供的 FInstancedStructNetSerializer 处理，可正确复制类型信息和结构体数据。
```

## Demo 示例

这是一个演示 `FInstancedStruct` 基本用法的 Actor 类。

**MyDataActor.h**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "InstancedStruct.h"
#include "MyDataActor.generated.h"

USTRUCT(BlueprintType)
struct FSimpleData
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FString Name;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    int32 Score;
};

UCLASS()
class AMyDataActor : public AActor
{
    GENERATED_BODY()

public:
    AMyDataActor();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(BlueprintReadWrite, EditAnywhere, Category = "Data")
    FInstancedStruct DynamicData;

    UFUNCTION(BlueprintCallable, Category = "Data")
    void SetDynamicDataAsSimpleData(const FString& InName, int32 InScore);

    UFUNCTION(BlueprintCallable, Category = "Data")
    void PrintDynamicData() const;
};
```

**MyDataActor.cpp**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.
#include "MyDataActor.h"

AMyDataActor::AMyDataActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyDataActor::BeginPlay()
{
    Super::BeginPlay();

    // 初始设置一个 FSimpleData
    SetDynamicDataAsSimpleData(TEXT("Player1"), 100);
    PrintDynamicData();
}

void AMyDataActor::SetDynamicDataAsSimpleData(const FString& InName, int32 InScore)
{
    // 通过模板函数设置数据，类型安全且简洁
    FSimpleData NewData;
    NewData.Name = InName;
    NewData.Score = InScore;
    DynamicData = FInstancedStruct::Make<FSimpleData>(NewData);
}

void AMyDataActor::PrintDynamicData() const
{
    // 检查并获取数据
    if (DynamicData.IsValid())
    {
        if (const UScriptStruct* StructType = DynamicData.GetScriptStruct())
        {
            UE_LOG(LogTemp, Warning, TEXT("DynamicData holds struct type: %s"), *StructType->GetName());

            // 假设我们知道它是 FSimpleData
            if (StructType == FSimpleData::StaticStruct())
            {
                const FSimpleData& Data = DynamicData.Get<FSimpleData>();
                UE_LOG(LogTemp, Warning, TEXT("Name: %s, Score: %d"), *Data.Name, Data.Score);
            }
        }
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("DynamicData is not valid."));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `StructUtilsEngine` | 提供核心的 `FInstancedStruct` 类型和相关序列化支持。依赖此模块是使用此插件功能的主要方式。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-08-05 | `5bf7f335` | Iris - Move InstancedStructNetSerializer to IrisCore. | 将网络序列化器迁移到 IrisCore 模块。 |
| 2024-08-01 | `0e320e33` | Iris - Crash fix for removing InstancedStruct from a replicated array and adding the same struct typ | 修复了从复制数组中移除并重新添加相同类型实例结构体时的崩溃问题。 |
| 2024-06-28 | `8083cf8c` | Iris - Adjust includes due to StructUtils moving. | 调整因 StructUtils 移动而更改的头文件包含。 |
| 2024-06-28 | `3680fd08` | Iris - Initial naive but working version of FInstancedStructNetSerializer to be able to replicate FI | 实现了 `FInstancedStruct` 的初始网络序列化器版本。 |
| 2024-06-19 | `e6d36d75` | Remove references to deprecated plugin StructUtils (now part of CoreUObject) | 移除对已弃用插件 StructUtils 的引用（暗示该插件可能并入 CoreUObject 或被替代）。 |

### 维护评价

- **实验性状态**：插件自创建起就标记为实验性 (`IsExperimentalVersion=true`)，且 `EnabledByDefault=false`。`DeprecatedEngineVersion` 为 5.5，强烈暗示该插件的功能可能已在 5.5 版本后整合到引擎核心（如 CoreUObject）或被其他方案取代。
- **近期活动**：2024年有多次提交，但主要集中在 Iris 相关功能的修复和网络序列化器的迁移上，表明其核心仍在被维护和用于特定系统（如 Iris/网络复制）。
- **综合评价**：该插件是 Epic 用于内部开发（特别是 LiveLinkHub 和网络复制）的实验性工具。虽然有近期更新，但其“实验性”标签和 5.5 的废弃引擎版本警告表明，普通项目**不推荐**将其作为长期依赖。建议查阅最新引擎版本（如 5.4+）的官方文档，确认 `FInstancedStruct` 是否已成为 `CoreUObject` 的一部分。如果是，则应直接使用引擎内置类型。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/StructUtils)
- [官方文档]()（无）