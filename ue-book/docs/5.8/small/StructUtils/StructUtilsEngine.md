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

StructUtils 插件的核心目的是提供 `FInstancedStruct` 类型。`FInstancedStruct` 是一个包装器，它允许在蓝图和 C++ 中安全地持有任何 UE 结构体的实例，同时保留其类型信息。这解决了在蓝图中传递“结构体变量”时丢失具体类型、无法安全地进行向下转型（Cast）或在容器（如数组）中存储不同类型结构体的核心痛点。该插件是实验性的，并且从提交记录看，其核心功能正被整合进 `CoreUObject` 模块。

## 使用场景

- 你需要在蓝图中创建一个变量，它可以存储任意类型的结构体，并且后续能够安全地获取其原始类型进行操作。
- 你需要一个数组，其中每个元素都可以是不同类型的结构体。
- 你在编写数据驱动的游戏系统，例如一个“属性”或“状态效果”系统，每种效果都用不同的结构体表示，但需要一个统一的容器来管理它们。

## 蓝图用法

基于提供的模块源码分析，`StructUtilsEngine` 模块的公开头文件极为简洁，表明其核心的 `FInstancedStruct` 类及其蓝图 API（如 `MakeInstancedStruct`， `BreakInstancedStruct`， `Equal (InstancedStruct)`， `NotEqual (InstancedStruct)`）主要定义在 `StructUtils` 模块或已迁移至 `CoreUObject`。**由于当前提供的插件源码未包含蓝图节点的定义头文件，无法列出具体的 `BlueprintCallable` 节点。** 通常，使用 `FInstancedStruct` 时，蓝图节点围绕构造、拆解和比较展开。

### 核心概念（蓝图描述）

1.  **创建 (Make)**：使用类似 `Make Instanced Struct` 的节点，将任意结构体值“装入”一个 `InstancedStruct` 变量。
2.  **拆解 (Break)**：使用类似 `Break Instanced Struct` 的节点，并指定一个“目标结构体类型”，从 `InstancedStruct` 变量中取出原始值。如果类型不匹配，可能会导致错误。
3.  **比较**：提供比较节点判断两个 `InstancedStruct` 是否相等。

## C++ 用法

### 头文件引入

要使用 `FInstancedStruct`，通常需要包含以下头文件（注意：具体头文件可能随 UE 版本演进）：

```cpp
#include "StructUtils/InstancedStruct.h"
```

### 基本用法

```cpp
// 假设有一个自定义结构体
USTRUCT(BlueprintType)
struct FMyData
{
    GENERATED_BODY()

    UPROPERTY()
    int32 Value;
};

// 创建一个 FInstancedStruct 并持有 FMyData 实例
FMyData MyData;
MyData.Value = 42;

// 方法1：通过构造函数
FInstancedStruct StructInstance(FMyData::StaticStruct(), reinterpret_cast<const uint8*>(&MyData));

// 方法2：使用静态 Make 函数（推荐）
FInstancedStruct StructInstance2 = FInstancedStruct::Make(MyData);

// 从 FInstancedStruct 中获取数据
if (StructInstance2.GetScriptStruct() == FMyData::StaticStruct())
{
    // 安全地获取指针
    const FMyData* RetrievedData = StructInstance2.GetPtr<const FMyData>();
    if (RetrievedData)
    {
        UE_LOG(LogTemp, Log, TEXT("Value: %d"), RetrievedData->Value);
    }
    
    // 或者直接获取引用（在已知类型安全时使用）
    const FMyData& RetrievedDataRef = StructInstance2.Get<const FMyData>();
}
```

### 进阶用法

`FInstancedStruct` 可以作为容器（如 `TArray`）的元素类型，实现异构集合。

```cpp
TArray<FInstancedStruct> StructArray;

// 添加不同类型的结构体
StructArray.Add(FInstancedStruct::Make(FMyData{1}));
StructArray.Add(FInstancedStruct::Make(FVector(1.f, 2.f, 3.f)));

// 遍历并处理
for (FInstancedStruct& Struct : StructArray)
{
    if (Struct.GetScriptStruct() == FMyData::StaticStruct())
    {
        const FMyData* Data = Struct.GetPtr<FMyData>();
        // 处理 FMyData...
    }
    else if (Struct.GetScriptStruct() == TBaseStructure<FVector>::Get())
    {
        const FVector* Vec = Struct.GetPtr<FVector>();
        // 处理 FVector...
    }
}
```

## Demo 示例

一个最小的 C++ 示例，展示 `FInstancedStruct` 的基本创建和获取。

```cpp
// MyComponent.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "StructUtils/InstancedStruct.h"
#include "MyComponent.generated.h"

USTRUCT(BlueprintType)
struct FHealthInfo
{
    GENERATED_BODY()

    UPROPERTY()
    float CurrentHealth = 100.f;
};

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "StructUtils Demo")
    void CreateAndLogStruct();

private:
    // 持有一个 FInstancedStruct 成员
    FInstancedStruct StoredStruct;
};
```

```cpp
// MyComponent.cpp
#include "MyComponent.h"
#include "StructUtils/InstancedStruct.h"

void UMyComponent::CreateAndLogStruct()
{
    // 创建一个 FHealthInfo 实例
    FHealthInfo Health;
    Health.CurrentHealth = 75.5f;

    // 将其封装进 FInstancedStruct
    StoredStruct = FInstancedStruct::Make(Health);

    // 验证并取回数据
    if (StoredStruct.GetScriptStruct() == FHealthInfo::StaticStruct())
    {
        const FHealthInfo* RetrievedHealth = StoredStruct.GetPtr<FHealthInfo>();
        if (RetrievedHealth)
        {
            UE_LOG(LogTemp, Warning, TEXT("Retrieved Health: %.1f"), RetrievedHealth->CurrentHealth);
        }
    }
}
```

## 模块依赖

从提供的 `Build.cs` 信息分析，无特殊依赖（仅标准 Core/Engine/Slate 等）。
`StructUtilsEngine` 模块依赖 `Engine`，而 `StructUtils` 模块的依赖未在提供的片段中列出，但根据其核心功能（结构体反射），它极可能依赖 `CoreUObject`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-08-05 | `5bf7f335` | Iris - Move InstancedStructNetSerializer to IrisCore. | 将 InstancedStruct 的网络序列化器迁移到 IrisCore 模块。 |
| 2024-08-01 | `0e320e33` | Iris - Crash fix for removing InstancedStruct from a replicated array and adding the same struct typ | 修复从复制数组中移除 InstancedStruct 后添加相同类型导致的崩溃。 |
| 2024-06-28 | `8083cf8c` | Iris - Adjust includes due to StructUtils moving. | 因 StructUtils 模块迁移调整头文件包含。 |
| 2024-06-28 | `3680fd08` | Iris - Initial naive but working version of FInstancedStructNetSerializer to be able to replicate FI | 实现 FInstancedStruct 网络序列化器的初始版本，用于网络复制。 |
| 2024-06-19 | `e6d36d75` | Remove references to deprecated plugin StructUtils (now part of CoreUObject) | 移除对已废弃 StructUtils 插件的引用，因其功能已并入 CoreUObject。 |

### 维护评价

**维护不活跃/可能被整合**。
该插件创建于 2021 年，标记为实验性且默认禁用。从 2024 年的提交记录看，大部分更新与 **Iris**（UE 的下一代网络复制系统）相关，主要是为了支持 `FInstancedStruct` 的网络复制功能。关键提交 `e6d36d75` 清晰地指出“StructUtils (now part of CoreUObject)”，这表明该插件的核心价值 `FInstancedStruct` 类很可能已被整合到引擎的 `CoreUObject` 模块中。
鉴于此，该插件的当前存在形式（作为独立插件）可能仅为了兼容或包含 Iris 网络序列化相关的扩展代码。**对于新项目，建议优先检查 `CoreUObject` 模块中是否已包含 `FInstancedStruct`，而非直接依赖此实验性插件。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/StructUtils)
- 官方文档（无）
- 测试用例（未在提供的源码片段中发现，可能位于其他模块或已被迁移）