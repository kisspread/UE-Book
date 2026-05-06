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
| 创建时间 | 2024-06-19 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/StructUtils) | |

## 用途

本插件在 Unreal Engine 5.5 及之前版本中实验性地提供了 `FInstancedStruct` 类型，允许在运行时**动态存储任意结构体（USTRUCT）的实例**，而无需预先知道具体类型。其核心用途是支持**类型安全的运行时多态数据容器**，广泛用于 Mass、SmartObjects、GameplayAbility 等系统需要携带可变数据的场景。

> ⚠️ **该插件已废弃**：从 UE 5.5 开始，`FInstancedStruct` 的核心功能被直接纳入 `CoreUObject` 模块（作为引擎内置类型），本插件不再需要。后续开发应直接使用 `CoreUObject` 中的 `FInstancedStruct`，避免依赖此实验性插件。

## 使用场景

- **动态配置数据**：如任务编辑器中允许用户选择任意结构体作为任务参数。
- **运行时状态存储**：行为树、状态机等系统需要携带多种不相关的数据结构。
- **网络复制**：曾借助本插件的 `FInstancedStructNetSerializer` 实现 InstancedStruct 的复制（该序列化器现已移至 IrisCore 模块）。

## 蓝图用法

本插件不提供直接暴露给蓝图的函数/节点（其核心类型 `FInstancedStruct` 为 C++ 类，蓝图只能通过包装后的对象使用 `Instanced Struct` 相关节点——这些节点已在引擎核心中实现）。在已启用本插件的旧项目中，可以通过以下方式使用：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Make Instanced Struct` | 从结构体变量创建 InstancedStruct 实例 | `UKismetSystemLibrary` |
| `Break Instanced Struct` | 将 InstancedStruct 解包为原结构体（需指定类型） | `UKismetSystemLibrary` |
| `Set Instanced Struct Value` | 设置 InstancedStruct 内部的值 | `UKismetSystemLibrary` |
| `Get Instanced Struct Value` | 获取 InstancedStruct 内部的值（按类型） | `UKismetSystemLibrary` |

*注：这些蓝图节点位于引擎内置的 `KismetSystemLibrary`，无需额外依赖本插件即可使用（引擎已内置）。*

## C++ 用法

### 头文件引入

```cpp
// 当插件启用时，可通过以下头文件使用 FInstancedStruct
#include "StructUtils/InstancedStruct.h"
// 推荐：直接使用引擎核心版本（插件废弃后无需额外包含）
#include "InstancedStruct.h"  // CoreUObject 版本
```

### 基本用法

```cpp
// 创建一个 InstancedStruct 来存储自定义结构体
USTRUCT(BlueprintType)
struct FMyData
{
    GENERATED_BODY()
    UPROPERTY()
    int32 Value = 42;
    UPROPERTY()
    FString Name = TEXT("Default");
};

// 用法示例（摘自旧版测试用例）
FInstancedStruct MyStruct;
MyStruct.InitializeAs<FMyData>();
FMyData& Data = MyStruct.GetMutable<FMyData>();
Data.Value = 100;

// 反序列化读取
const FMyData& ReadData = MyStruct.Get<FMyData>();
UE_LOG(LogTemp, Log, TEXT("Value: %d"), ReadData.Value);
```

*来源：`Engine/Plugins/Experimental/StructUtils/Source/StructUtils/Private/Tests/InstancedStructTests.cpp`*

### 进阶用法

```cpp
// 动态切换存储类型
FInstancedStruct Container;
Container.InitializeAs<FMyData>();
// ... 使用后重置为另一类型
Container.Reset();
Container.InitializeAs<FMyOtherData>();

// 数组形式的 InstancedStruct
TArray<FInstancedStruct> InstancedArray;
InstancedArray.Emplace(FInstancedStruct::Make<FMyData>());
InstancedArray.Emplace(FInstancedStruct::Make<FMyOtherData>());
```

## Demo 示例

一个完整的最小示例（基于引擎已内置的 `FInstancedStruct`，无需启用本插件）：

```cpp
// MyActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "InstancedStruct.h"
#include "MyActor.generated.h"

USTRUCT(BlueprintType)
struct FHealthData
{
    GENERATED_BODY()
    UPROPERTY()
    float Health = 100.0f;
    UPROPERTY()
    float MaxHealth = 100.0f;
};

UCLASS()
class AMyActor : public AActor
{
    GENERATED_BODY()
public:
    UPROPERTY()
    FInstancedStruct Stats;
    
    virtual void BeginPlay() override
    {
        Super::BeginPlay();
        Stats.InitializeAs<FHealthData>();
        Stats.GetMutable<FHealthData>().Health = 50.0f;
    }
};
```

```cpp
// MyActor.cpp
#include "MyActor.h"
// 无需额外依赖，CoreUObject 已内置
```

## 模块依赖

本插件的模块在 `Build.cs` 中声明了以下依赖（仅列出非常见项）：

| 模块 | 用途 |
|---|---|
| `IrisCore` | 早期的 InstancedStruct 网络序列化器（已移入 IrisCore） |

>*标准依赖（Core, CoreUObject, Engine）已省略。*

## 维护状态

### 近期更新

```
- 2024-08-05 5bf7f335 Iris - Move InstancedStructNetSerializer to IrisCore.
- 2024-08-01 0e320e33 Iris - Crash fix for removing InstancedStruct from a replicated array and adding the same struct type.
- 2024-06-28 8083cf8c Iris - Adjust includes due to StructUtils moving.
- 2024-06-28 3680fd08 Iris - Initial naive but working version of FInstancedStructNetSerializer to be able to replicate FInstancedStruct.
- 2024-06-19 e6d36d75 Remove references to deprecated plugin StructUtils (now part of CoreUObject)
```

### 维护评价

- **创建时间**：2024-06-19（约1年前）
- **维护状态**：**已废弃**（自 UE 5.5 起被替代，插件元数据标记 `DeprecatedEngineVersion=5.5`）
- **原因**：插件提供的 `FInstancedStruct` 功能被直接合入 `CoreUObject` 模块，成为引擎核心类型。后续所有更新（网络序列化器修复）均发生在 `IrisCore` 中，而非本插件。
- **建议**：**强烈不推荐新项目启用此插件**。应直接使用引擎内置的 `FInstancedStruct`（位于 `CoreUObject`）。如果项目已使用此插件，请尽快迁移：移除插件依赖，并替换 `#include "StructUtils/InstancedStruct.h"` 为 `#include "InstancedStruct.h"`。

## 相关链接

- [源码（5.7 分支）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/StructUtils)
- [引擎内置 InstancedStruct 文档](https://docs.unrealengine.com/5.5/en-US/API/Runtime/CoreUObject/InstancedStruct/)