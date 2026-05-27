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
| 年龄标签 | 👴 老古董（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/StructUtils) | |

## 用途

StructUtils 插件的核心是提供 `FInstancedStruct` 类型，这是一个能够在运行时安全地持有、复制和实例化任意 `UScriptStruct` 类型数据的容器。它解决了在运行时动态处理不同类型结构体实例的需求，尤其是在需要序列化、复制或按类型存储/检索数据时，比传统的 `TArray<uint8>` + `UScriptStruct*` 手动管理方式更安全、更易用，并与引擎的反射和复制系统深度集成。

## 使用场景

- 你需要在一个数组或列表中存储**多种不同但相关的结构体类型**（例如，不同的游戏事件数据），并希望保留每个元素的类型信息以便正确反序列化和处理。
- 你需要将结构体实例通过网络进行复制，并希望保持其类型信息，以便在客户端正确重建。
- 你在编写一个通用的数据资产或配置系统，其中数据字段的类型在蓝图中或运行时才能确定。

## 蓝图用法

`FInstancedStruct` 本身是一个结构体，可以在蓝图中作为变量使用。其主要蓝图功能围绕其构造和类型安全的值访问。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Make InstancedStruct` | 根据提供的 `UScriptStruct` 和原始数据创建一个 `FInstancedStruct` 实例。 | `UBlueprintInstancedStructLibrary` |
| `Get Struct` | 从 `FInstancedStruct` 中安全地提取指定类型的结构体数据。如果类型不匹配，返回无效结果。 | `UBlueprintInstancedStructLibrary` |
| `IsValid` | 检查 `FInstancedStruct` 是否持有一个有效的结构体实例。 | `UBlueprintInstancedStructLibrary` |
| `Get Struct Type` | 获取 `FInstancedStruct` 当前持有的结构体类型。 | `UBlueprintInstancedStructLibrary` |

### 使用示例（蓝图描述）

1.  **创建与存储**：使用 `Make InstancedStruct` 节点，将一个结构体（如 `MyStructA`）作为输入，生成一个 `FInstancedStruct` 变量。将该变量存入一个 `TArray<FInstancedStruct>`。
2.  **读取与使用**：从数组中取出一个 `FInstancedStruct`。首先用 `Get Struct Type` 节点判断其类型。然后根据类型，使用 `Get Struct` 节点并指定对应的结构体类型（如 `MyStructA`）来安全地提取数据，后续节点即可直接使用提取出的强类型结构体。

## C++ 用法

### 头文件引入

```cpp
#include "InstancedStruct.h"
```

### 基本用法

创建、赋值和从 `FInstancedStruct` 中取回数据。
```cpp
// 假设有一个自定义结构体 FMyData
USTRUCT(BlueprintType)
struct FMyData
{
    GENERATED_BODY()
    UPROPERTY() int32 Value = 0;
};

// 创建一个 FInstancedStruct
FInstancedStruct InstancedStruct;
// 设置其内容为一个 FMyData 实例
InstancedStruct.InitializeAs<FMyData>(FMyData{42});

// 安全地获取其中的数据
if (InstancedStruct.IsValid())
{
    if (const FMyData* MyDataPtr = InstancedStruct.GetPtr<FMyData>())
    {
        UE_LOG(LogTemp, Log, TEXT("Value: %d"), MyDataPtr->Value); // 输出 42
    }
}
```

### 进阶用法

`FInstancedStruct` 的一个重要特性是支持网络复制。当它作为 `UPROPERTY(Replicated)` 成员时，其内部的类型信息和数据会被自动序列化和复制。这是通过引擎内部的 `FInstancedStructNetSerializer` 实现的（参考近期的 `Iris` 相关提交）。开发者无需手动处理复制逻辑。
```cpp
// 在某个 Actor 类中
USTRUCT()
struct FMyReplicatedData
{
    GENERATED_BODY()
    UPROPERTY(Replicated) FInstancedStruct Payload; // 此成员将被正确复制
};
```

## Demo 示例

一个展示如何在 Actor 中使用 `FInstancedStruct` 携带可复制数据的最小示例。

**MyActor.h**
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "InstancedStruct.h"
#include "MyActor.generated.h"

USTRUCT(BlueprintType)
struct FHealthData
{
    GENERATED_BODY()
    UPROPERTY() float Current = 100.f;
    UPROPERTY() float Max = 100.f;
};

USTRUCT(BlueprintType)
struct FDamageEvent
{
    GENERATED_BODY()
    UPROPERTY() float Amount = 0.f;
    UPROPERTY() FVector Origin;
};

UCLASS()
class AMyActor : public AActor
{
    GENERATED_BODY()
public:
    AMyActor();
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;

    UPROPERTY(Replicated, BlueprintReadOnly)
    FInstancedStruct CurrentGameplayEvent; // 可以存储 FHealthData 或 FDamageEvent 等

    UFUNCTION(BlueprintCallable)
    void SimulateDamageEvent(float DamageAmount);
};
```

**MyActor.cpp**
```cpp
#include "MyActor.h"
#include "Net/UnrealNetwork.h"

AMyActor::AMyActor()
{
    bReplicates = true;
    // 初始设置为一个 FHealthData 事件
    CurrentGameplayEvent.InitializeAs<FHealthData>(FHealthData{100.f, 100.f});
}

void AMyActor::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);
    DOREPLIFETIME(AMyActor, CurrentGameplayEvent);
}

void AMyActor::SimulateDamageEvent(float DamageAmount)
{
    // 在服务器端，将事件切换为 FDamageEvent
    if (HasAuthority())
    {
        FDamageEvent DmgEvent;
        DmgEvent.Amount = DamageAmount;
        DmgEvent.Origin = GetActorLocation();
        CurrentGameplayEvent.InitializeAs<FDamageEvent>(DmgEvent);
    }
    // 当前的 CurrentGameplayEvent 将会自动复制到所有客户端
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Engine` | 核心引擎模块，提供 USTRUCT、反射、序列化等基础功能。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-08-05 | `5bf7f335` | Iris - Move InstancedStructNetSerializer to IrisCore. | 将网络序列化器移至 Iris 核心模块，优化结构。 |
| 2024-08-01 | `0e320e33` | Iris - Crash fix for removing InstancedStruct from a replicated array and adding the same struct type. | 修复从复制数组移除并添加同类型InstancedStruct时导致的崩溃。 |
| 2024-06-28 | `8083cf8c` | Iris - Adjust includes due to StructUtils moving. | 调整头文件包含路径以适配模块移动。 |
| 2024-06-28 | `3680fd08` | Iris - Initial naive but working version of FInstancedStructNetSerializer to be able to replicate FInstancedStruct. | 实现 FInstancedStruct 的初始网络复制功能。 |
| 2024-06-19 | `e6d36d75` | Remove references to deprecated plugin StructUtils (now part of CoreUObject). | 清理废弃插件引用，相关功能已集成至CoreUObject。 |

### 维护评价

**实验性状态**：该插件明确标记为实验性 (`IsExperimentalVersion=true`)，且未默认启用。它有一个 `DeprecatedEngineVersion` 为 5.5，暗示它可能在未来被移除或合并。

**活跃度**：核心功能在2024年6-8月有集中更新，主要围绕 `Iris` 网络系统对其复制功能进行集成、优化和修复。这表明 Epic 内部有实际项目（如 Iris）在使用该功能并推动其完善。

**综合评价**：StructUtils 提供了一个强大且必要的底层工具（`FInstancedStruct`）。尽管插件本身是实验性的，但其核心类型很可能已成为引擎内部某些系统（如增强输入、Iris）的基础组件。对于开发者而言，如果需要在运行时动态处理多态结构体数据，可以谨慎使用，但需要意识到它可能在未来版本中发生变化（如移入引擎其他模块）。鉴于近期有针对网络复制的活跃开发，它在需要网络同步动态结构体数据的场景中价值很高。

**风险提示**：该插件声明支持 `LiveLinkHub`，但 `DeprecatedEngineVersion` 和 `IsExperimentalVersion` 标志表明其稳定性存在风险，不建议在需要长期稳定的核心功能中依赖它。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/StructUtils)
- 官方文档：无
- 测试用例：未在插件目录中发现专用测试用例，测试可能位于其他使用该插件的模块内。