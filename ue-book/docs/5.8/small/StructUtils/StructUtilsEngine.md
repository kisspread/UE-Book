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

> ⚠️ **已废弃（Deprecated）**：该插件已在 UE 5.5 中被废弃，其核心功能（`FInstancedStruct`、`FStructView`、`FConstStructView`）已迁移至 **CoreUObject** 模块。如果你使用 UE 5.5+，请直接使用 CoreUObject 中的类型，无需启用此插件。本文档仅作历史参考。

## 用途

StructUtils 提供了一套**类型擦除的结构体容器**，核心解决的问题是：**在运行时以统一的方式持有任意 UStruct 实例，而无需预先知道具体类型**。

传统的 `USTRUCT` 使用需要在编译期确定类型，而 `FInstancedStruct` 允许你在运行时动态存储任意结构体，类似于 `TArray<uint8>` + 类型元信息的安全封装。这在以下场景中非常有用：

- 需要定义**异构数据容器**（同一容器可存储不同类型的结构体）
- 需要**延迟决定数据类型**的序列化/反序列化场景
- 构建通用的**数据驱动系统**（如 Mass Entity、Gameplay Ability System 中的上下文数据）

插件提供两个模块：
- **StructUtils**：核心类型定义（`FInstancedStruct`、`FStructView` 等）
- **StructUtilsEngine**：引擎层集成（网络序列化等）

## 使用场景

- 你在构建一个**事件系统**，不同事件携带不同结构体载荷 → 用 `FInstancedStruct` 作为事件数据载体
- 你需要一个**通用属性/标签系统**，允许存储任意结构体作为值 → 用 `FInstancedStruct` 作为属性值类型
- 你需要在**网络复制**中传递动态类型的结构体 → 用 `FInstancedStructNetSerializer`（已迁移至 Iris）
- 你需要对已有结构体数据做**零拷贝视图**访问 → 用 `FStructView` / `FConstStructView`

## 蓝图用法

> ⚠️ 该插件主要为 C++ 设计，蓝图暴露的节点有限。以下为 `FInstancedStruct` 在蓝图中可用的操作。

### 核心节点

由于 `FInstancedStruct` 是 `USTRUCT`，它可以在蓝图中作为变量使用，但创建和类型操作主要在 C++ 中完成。

| 节点 | 说明 | 所在类 |
|---|---|---|
| Break InstancedStruct | 拆解 FInstancedStruct 获取内部数据 | `FInstancedStruct` |
| Make InstancedStruct | 从具体结构体创建 FInstancedStruct | `FInstancedStruct` |

### 使用示例（蓝图描述）

在蓝图中，你可以将 `FInstancedStruct` 作为变量类型声明，然后通过 Make/Break 节点与具体结构体类型互相转换。

## C++ 用法

### 头文件引入

```cpp
#include "InstancedStruct.h"
```

### 基本用法

```cpp
// 创建一个 FInstancedStruct，内部持有 FHitResult
FInstancedStruct InstancedStruct;
InstancedStruct.InitializeAs(FHitResult::StaticStruct());

// 从具体结构体实例创建
FHitResult HitResult;
HitResult.bBlockingHit = true;
FInstancedStruct FromValue = FInstancedStruct::Make(HitResult);

// 获取内部结构体的类型
const UScriptStruct* StructType = FromValue.GetScriptStruct();

// 安全获取内部数据
if (const FHitResult* HitPtr = FromValue.GetPtr<FHitResult>())
{
    UE_LOG(LogTemp, Log, TEXT("Blocking hit: %s"), HitPtr->bBlockingHit ? TEXT("true") : TEXT("false"));
}

// 获取可变引用
FHitResult& HitRef = FromValue.GetMutable<FHitResult>();
HitRef.bBlockingHit = false;
```

### 进阶用法：StructView（零拷贝视图）

```cpp
// FConstStructView：只读视图，不拥有数据
FHitResult HitResult;
FConstStructView View = FConstStructView::Make(HitResult);

// FStructView：可变视图，不拥有数据
FStructView MutableView = FStructView::Make(HitResult);
MutableView.GetMutable<FHitResult>().bBlockingHit = true;

// 函数参数中使用 View 代替具体类型，实现泛型接口
void ProcessStruct(FConstStructView InStruct)
{
    if (InStruct.GetScriptStruct() == FHitResult::StaticStruct())
    {
        const FHitResult& Hit = InStruct.Get<FHitResult>();
        // 处理 HitResult...
    }
}
```

### 进阶用法：类型安全的容器

```cpp
// 存储不同类型的结构体到同一容器
TArray<FInstancedStruct> StructArray;

StructArray.Add(FInstancedStruct::Make(FHitResult()));
StructArray.Add(FInstancedStruct::Make(FVector_NetQuantize(1, 2, 3)));

// 遍历时根据类型分别处理
for (const FInstancedStruct& Item : StructArray)
{
    if (Item.GetScriptStruct() == FHitResult::StaticStruct())
    {
        const FHitResult& Hit = Item.Get<FHitResult>();
        // ...
    }
}
```

## Demo 示例

以下为一个完整的最小示例，演示 `FInstancedStruct` 的基本创建和访问：

```cpp
// MyStructUtilsExample.h
#pragma once

#include "CoreMinimal.h"
#include "InstancedStruct.h"
#include "MyStructUtilsExample.generated.h"

USTRUCT(BlueprintType)
struct FMyDataA
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere)
    float Value = 0.f;
};

USTRUCT(BlueprintType)
struct FMyDataB
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere)
    FString Name;
};

UCLASS()
class UMyStructUtilsExample : public UObject
{
    GENERATED_BODY()

public:
    // 接受任意结构体的泛型处理函数
    void ProcessData(FConstStructView Data);

    // 演示用法
    void RunExample();
};
```

```cpp
// MyStructUtilsExample.cpp
#include "MyStructUtilsExample.h"

void UMyStructUtilsExample::ProcessData(FConstStructView Data)
{
    if (Data.GetScriptStruct() == FMyDataA::StaticStruct())
    {
        const FMyDataA& A = Data.Get<FMyDataA>();
        UE_LOG(LogTemp, Log, TEXT("DataA Value: %f"), A.Value);
    }
    else if (Data.GetScriptStruct() == FMyDataB::StaticStruct())
    {
        const FMyDataB& B = Data.Get<FMyDataB>();
        UE_LOG(LogTemp, Log, TEXT("DataB Name: %s"), *B.Name);
    }
}

void UMyStructUtilsExample::RunExample()
{
    // 创建不同类型的 FInstancedStruct
    FMyDataA DataA;
    DataA.Value = 42.f;
    FInstancedStruct InstA = FInstancedStruct::Make(DataA);

    FMyDataB DataB;
    DataB.Name = TEXT("Hello");
    FInstancedStruct InstB = FInstancedStruct::Make(DataB);

    // 通过零拷贝视图传递给泛型函数
    ProcessData(FConstStructView::Make(InstA));  // 输出: DataA Value: 42.000000
    ProcessData(FConstStructView::Make(InstB));  // 输出: DataB Name: Hello
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine 等）。

StructUtils 模块依赖 `Engine`，StructUtilsEngine 无额外外部依赖。使用者无需在 Build.cs 中添加特殊依赖——由于插件标记为 `Installed: false`，需要手动在 `.uproject` 中启用该插件后使用。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-08-05 | `5bf7f335` | Iris - Move InstancedStructNetSerializer to IrisCore. | 将网络序列化器迁移至 Iris 核心模块 |
| 2024-08-01 | `0e320e33` | Iris - Crash fix for removing InstancedStruct from a replicated array and adding the same struct typ | 修复从复制数组移除后再添加同类结构体的崩溃 |
| 2024-06-28 | `8083cf8c` | Iris - Adjust includes due to StructUtils moving. | 适配 StructUtils 迁移后的头文件引用 |
| 2024-06-28 | `3680fd08` | Iris - Initial naive but working version of FInstancedStructNetSerializer to be able to replicate FI | 初步实现 FInstancedStruct 的网络复制支持 |
| 2024-06-19 | `e6d36d75` | Remove references to deprecated plugin StructUtils (now part of CoreUObject) | 移除对已废弃插件的引用，功能已并入 CoreUObject |

### 维护评价

**⛔ 已废弃，不建议使用。**

- 插件于 2021 年创建，作为实验性功能提供 `FInstancedStruct` 类型
- 核心功能已在 **UE 5.5** 中正式迁移至 **CoreUObject** 模块（`DeprecatedEngineVersion: 5.5`）
- 最近的 commit（2024-06 至 2024-08）全部是关于 **迁移和清理**，而非功能更新
- 距最近更新已超过 **1 年**，无新功能开发计划
- **推荐**：如果你使用 UE 5.5+，直接 `#include "InstancedStruct.h"`（来自 CoreUObject），无需启用此插件
- 如果你维护 UE 5.4 或更早版本的项目，此插件仍是获取 `FInstancedStruct` 功能的唯一途径

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/StructUtils)
- 官方文档：无
- [CoreUObject 中的 FInstancedStruct（迁移后）](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Source/Runtime/CoreUObject/Public/StructUtils/InstancedStruct.h)