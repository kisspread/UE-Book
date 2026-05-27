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

StructUtils 是一个**已废弃**的实验性插件，提供 `FInstancedStruct` 类型——一种支持类型擦除的结构体容器，允许在运行时存储任意 UScriptStruct 实例并保留其类型信息。

**该插件已在 UE 5.5 中被废弃，其核心功能已迁移至 `CoreUObject` 模块。** 如果你使用 UE 5.3 及以上版本，应直接使用 CoreUObject 中的 FInstancedStruct，无需启用此插件。

核心功能包括：
- **FInstancedStruct**：类型安全的结构体容器，可存储任意 USTRUCT 实例
- **网络序列化支持**：通过 StructUtilsEngine 提供 FInstancedStruct 的网络复制能力
- 类似于运行时的 "多态结构体"，适用于需要在容器中存储不同类型结构体的场景

## 使用场景

- 你需要一个容器能存储不同类型的结构体实例（如事件系统、数据驱动配置）→ 已迁移至 CoreUObject
- 你需要在网络复制时序列化动态类型的结构体 → 已迁移至 Iris/IrisCore

> ⚠️ **废弃警告**：此插件在 UE 5.5 已标记为废弃（`DeprecatedEngineVersion: 5.5`），功能已整合到引擎核心。请参考 [CoreUObject 中的 FInstancedStruct](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Source/Runtime/CoreUObject)。

## 蓝图用法

该插件为纯 C++ 运行时模块，不包含蓝图暴露的节点。

## C++ 用法

### 头文件引入

```cpp
#include "StructUtils/InstancedStruct.h"
```

> ⚠️ 从 UE 5.3 起，FInstancedStruct 已移至 CoreUObject，头文件路径可能已变更。

### 基本用法

FInstancedStruct 的典型使用模式：

```cpp
#include "StructUtils/InstancedStruct.h"

// 定义一些结构体
USTRUCT(BlueprintType)
struct FMyDataA
{
    GENERATED_BODY()

    UPROPERTY()
    float Value = 0.f;
};

USTRUCT(BlueprintType)
struct FMyDataB
{
    GENERATED_BODY()

    UPROPERTY()
    FString Name;
};

// 创建 FInstancedStruct 并存储不同类型
FInstancedStruct StructA = FInstancedStruct::Make<FMyDataA>();
StructA.GetMutable<FMyDataA>().Value = 42.f;

FInstancedStruct StructB = FInstancedStruct::Make<FMyDataB>();
StructB.GetMutable<FMyDataB>().Name = TEXT("Hello");

// 类型安全地读取
if (StructA.GetScriptStruct() == FMyDataA::StaticStruct())
{
    const FMyDataA& Data = StructA.Get<FMyDataA>();
    UE_LOG(LogTemp, Log, TEXT("Value: %f"), Data.Value);
}
```

### 进阶用法

作为容器存储异构结构体数组：

```cpp
TArray<FInstancedStruct> EventData;

// 存储不同类型的事件数据
EventData.Add(FInstancedStruct::Make<FMyDataA>());
EventData.Add(FInstancedStruct::Make<FMyDataB>());

// 遍历时根据类型分发
for (const FInstancedStruct& Struct : EventData)
{
    if (Struct.GetScriptStruct() == FMyDataA::StaticStruct())
    {
        // 处理 FMyDataA
    }
    else if (Struct.GetScriptStruct() == FMyDataB::StaticStruct())
    {
        // 处理 FMyDataB
    }
}
```

## Demo 示例

```cpp
// MyActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "StructUtils/InstancedStruct.h"
#include "MyActor.generated.h"

USTRUCT(BlueprintType)
struct FDamageEvent
{
    GENERATED_BODY()
    UPROPERTY()
    float Amount = 0.f;
    UPROPERTY()
    FName Type;
};

USTRUCT(BlueprintType)
struct FHealEvent
{
    GENERATED_BODY()
    UPROPERTY()
    float Amount = 0.f;
};

UCLASS()
class AMyActor : public AActor
{
    GENERATED_BODY()
public:
    void ProcessEvent(const FInstancedStruct& Event);
    void QueueEvent();
};
```

```cpp
// MyActor.cpp
#include "MyActor.h"

void AMyActor::ProcessEvent(const FInstancedStruct& Event)
{
    if (const FDamageEvent* Damage = Event.GetPtr<FDamageEvent>())
    {
        UE_LOG(LogTemp, Log, TEXT("Damage: %f %s"), Damage->Amount, *Damage->Type.ToString());
    }
    else if (const FHealEvent* Heal = Event.GetPtr<FHealEvent>())
    {
        UE_LOG(LogTemp, Log, TEXT("Heal: %f"), Heal->Amount);
    }
}

void AMyActor::QueueEvent()
{
    FInstancedStruct DamageEvent = FInstancedStruct::Make<FDamageEvent>();
    DamageEvent.GetMutable<FDamageEvent>().Amount = 50.f;
    ProcessEvent(DamageEvent);
}
```

## 模块依赖

StructUtilsEngine 模块的 Build.cs 显示为空依赖，StructUtils 模块依赖 Engine。

| 模块 | 用途 |
|---|---|
| `Engine` | StructUtils 基础模块依赖 |
| `IrisCore` | 网络序列化已迁移至此（5.8） |

无特殊依赖（仅标准 Core/Engine 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-08-05 | `5bf7f335` | Iris - Move InstancedStructNetSerializer to IrisCore. | 网络序列化器迁移至 IrisCore |
| 2024-08-01 | `0e320e33` | Iris - Crash fix for removing InstancedStruct from a replicated array and adding the same struct typ | 修复复制数组中移除再添加同类型结构体的崩溃 |
| 2024-06-28 | `8083cf8c` | Iris - Adjust includes due to StructUtils moving. | 因插件迁移调整头文件引用 |
| 2024-06-28 | `3680fd08` | Iris - Initial naive but working version of FInstancedStructNetSerializer to be able to replicate FI | 为 FInstancedStruct 添加初始网络序列化支持 |
| 2024-06-19 | `e6d36d75` | Remove references to deprecated plugin StructUtils (now part of CoreUObject) | 移除对该废弃插件的引用，功能已并入 CoreUObject |

### 维护评价

⚠️ **已废弃 — 不建议使用**

- **创建时间**：2021-04-20，约 4 年历史
- **废弃时间**：UE 5.5（2024 年中期）标记为废弃
- **当前状态**：插件本身不再维护，相关功能已迁移至 `CoreUObject` 和 `IrisCore`
- **近期活动**：所有近期提交（2024 年）均为**迁移和清理**工作，非功能增强
- **推荐**：❌ 不推荐启用此插件。如果你使用 UE 5.3+，FInstancedStruct 已作为 CoreUObject 的一部分自动可用。此插件仅作为历史存档存在。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/StructUtils)
- 官方文档：无
- [CoreUObject（FInstancedStruct 新位置）](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Source/Runtime/CoreUObject)