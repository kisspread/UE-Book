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

StructUtils 插件的核心是提供 `FInstancedStruct` 类型。它是一个**运行时多态结构体容器**，允许在同一个变量中存储不同类型（但通常是相关基类）的 USTRUCT 实例，并保留完整的类型信息和数据。这解决了在容器（如 TArray 或 TMap）中存储异构结构体、以及需要进行运行时类型擦除和还原的场景。

## 使用场景

- 你需要在一个数组中存储不同派生类型的结构体数据（例如，不同类型的伤害信息、事件数据）。
- 你需要一个能够存放任意结构体数据的通用容器，同时在读取时能够安全地检查和获取原始类型。
- 你在实现一个需要传输或保存多种数据类型“包”的系统（如游戏状态快照、技能参数包）。

## 蓝图用法

由于此插件是底层运行时类型，其蓝图节点主要通过 `StructUtilsEngine` 模块暴露。请查阅 `StructUtilsEngine` 模块的文档以获取完整的蓝图节点列表。

核心的 `FInstancedStruct` 通常在 C++ 层面进行操作和传递。

## C++ 用法

### 头文件引入

```cpp
#include "StructUtils/Public/StructUtilsModule.h"
#include “StructUtils/Public/InstancedStruct.h”
```

### 基本用法

创建、赋值和获取 `FInstancedStruct` 中的数据。

```cpp
// 包含目标结构体的头文件
#include "MyStructs.h"

// 创建一个空的实例化结构体
FInstancedStruct MyInstancedStruct;

// 从一个具体的结构体进行构造
FMyStructA StructAData;
StructAData.Value = 42;
MyInstancedStruct = FInstancedStruct::Make(StructAData);

// 检查其类型
if (MyInstancedStruct.GetScriptStruct() == FMyStructA::StaticStruct())
{
    // 安全地获取回原始数据
    const FMyStructA& RetrievedData = MyInstancedStruct.Get<FMyStructA>();
    UE_LOG(LogTemp, Log, TEXT("Value: %d"), RetrievedData.Value);
}

// 也可以使用模板函数进行类型安全的获取（如果类型不匹配会触发断言）
FMyStructA& MutableData = MyInstancedStruct.GetMutable<FMyStructA>();
MutableData.Value = 100;
```

### 进阶用法

在容器中使用，实现运行时多态。

```cpp
TArray<FInstancedStruct> StructContainer;

// 存入不同类型的结构体
FMyStructA A;
A.Value = 1;
StructContainer.Add(FInstancedStruct::Make(A));

FMyStructB B;
B.Name = TEXT("Hello");
StructContainer.Add(FInstancedStruct::Make(B));

// 遍历并处理
for (const FInstancedStruct& Instanced : StructContainer)
{
    if (const FMyStructA* AsA = Instanced.GetPtr<FMyStructA>())
    {
        // 处理 A 类型
    }
    else if (const FMyStructB* AsB = Instanced.GetPtr<FMyStructB>())
    {
        // 处理 B 类型
    }
    else
    {
        // 处理未知类型或基类
    }
}
```

## Demo 示例

一个可编译的最小示例，演示基本用法。

**MyStructs.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "MyStructs.generated.h"

USTRUCT(BlueprintType)
struct FMyBaseData
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadWrite)
    int32 BaseID = 0;
};

USTRUCT(BlueprintType)
struct FMyDamageData : public FMyBaseData
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadWrite)
    float DamageAmount = 0.f;
};

USTRUCT(BlueprintType)
struct FMyHealData : public FMyBaseData
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadWrite)
    float HealAmount = 0.f;
};
```

**MyStructUtilsExample.cpp**
```cpp
#include "MyStructs.h"
#include "StructUtils/Public/InstancedStruct.h"
#include "HAL/Platform.h"
#include "Logging/LogMacros.h"

DEFINE_LOG_CATEGORY_STATIC(LogStructUtilsExample, Log, All);

void RunExample()
{
    // 创建一个容器来存储不同类型的事件数据
    TArray<FInstancedStruct> EventBuffer;

    // 制造伤害事件
    FMyDamageData DamageEvent;
    DamageEvent.BaseID = 101;
    DamageEvent.DamageAmount = 25.0f;
    EventBuffer.Add(FInstancedStruct::Make(DamageEvent));

    // 制造治疗事件
    FMyHealData HealEvent;
    HealEvent.BaseID = 102;
    HealEvent.HealAmount = 15.0f;
    EventBuffer.Add(FInstancedStruct::Make(HealEvent));

    // 处理事件队列
    for (FInstancedStruct& Event : EventBuffer)
    {
        if (FMyDamageData* Damage = Event.GetMutablePtr<FMyDamageData>())
        {
            UE_LOG(LogStructUtilsExample, Warning, TEXT("处理伤害事件 ID: %d, 伤害: %.1f"), Damage->BaseID, Damage->DamageAmount);
            Damage->DamageAmount *= 2.0f; // 增加伤害
        }
        else if (FMyHealData* Heal = Event.GetMutablePtr<FMyHealData>())
        {
            UE_LOG(LogStructUtilsExample, Warning, TEXT("处理治疗事件 ID: %d, 治疗: %.1f"), Heal->BaseID, Heal->HealAmount);
        }
        else
        {
            UE_LOG(LogStructUtilsExample, Error, TEXT("未知的事件类型！"));
        }
    }
}
```

## 模块依赖

`StructUtils` 模块的 Build.cs 仅依赖 `Engine`。

无特殊依赖（仅标准 Core/Engine 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-08-05 | `5bf7f335` | Iris - Move InstancedStructNetSerializer to IrisCore. | 将 InstancedStruct 的网络序列化器移至 Iris 核心模块。 |
| 2024-08-01 | `0e320e33` | Iris - Crash fix for removing InstancedStruct from a replicated array and adding the same struct typ | 修复从复制数组中移除 InstancedStruct 并添加相同结构体类型时导致的崩溃。 |
| 2024-06-28 | `8083cf8c` | Iris - Adjust includes due to StructUtils moving. | 因 StructUtils 位置变动，调整相关头文件包含。 |
| 2024-06-28 | `3680fd08` | Iris - Initial naive but working version of FInstancedStructNetSerializer to be able to replicate FI | 为 FInstancedStruct 实现初始但可用的网络序列化器，以支持复制。 |
| 2024-06-19 | `e6d36d75` | Remove references to deprecated plugin StructUtils (now part of CoreUObject) | 移除对已废弃的 StructUtils 插件的引用（其功能现属于 CoreUObject）。 |

### 维护评价

- **活跃维护**：近期（2024年）有多次提交，主要围绕 **Iris 网络系统** 进行集成和修复（如网络序列化器、崩溃修复）。这表明 `InstancedStruct` 是现代 UE 网络栈（Iris）的一个重要数据类型。
- **实验性警告**：插件始终标记为 `Experimental` 且默认未启用。最新提交表明其功能正在向 `CoreUObject` 或 `IrisCore` 核心模块迁移，这可能是其长期演进方向。
- **推荐使用**：适用于需要高级运行时多态结构体功能的项目，尤其是涉及 Iris 网络复制的场景。但需注意其“实验性”状态，未来 API 可能变动。对于简单的多态需求，可考虑先评估标准的 UObject 继承或变体类型。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/StructUtils)
- [官方文档](（无）)
- [测试用例](（未在插件目录内提供，请在引擎测试目录搜索 `InstancedStruct` 相关用例）)