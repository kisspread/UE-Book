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

StructUtils 提供了 `FInstancedStruct` 类型——一种可以在运行时安全存储任意 UStruct 实例的容器。它解决了 UE 中常见的一个问题：需要在不暴露具体类型的情况下传递和存储结构体数据。

**⚠️ 重要提示：此插件已在 UE 5.5 中被废弃（DeprecatedEngineVersion: 5.5）。其核心功能已迁移至 CoreUObject 模块。** 2024 年 6 月的 commit 明确记录了"Remove references to deprecated plugin StructUtils (now part of CoreUObject)"。

## 使用场景

> ⚠️ 以下场景请直接使用 CoreUObject 中的 FInstancedStruct，而非此插件。

- 你需要一个类型安全的"万能结构体容器"，可以在不知道具体类型的情况下存储和传递不同的 UStruct
- 你在实现事件系统，需要让事件携带不同类型的数据负载
- 你需要序列化/网络复制包含多态结构体的数据

## 蓝图用法

此插件的 StructUtilsEngine 模块非常精简（仅约 4 个源文件），主要用于提供 FInstancedStruct 的网络序列化支持（InstancedStructNetSerializer），未暴露独立的蓝图节点。

在当前 UE5 版本中，FInstancedStruct 的蓝图支持已随功能迁移至 CoreUObject。

## C++ 用法

### 头文件引入

```cpp
#include "StructUtilsEngineModule.h"
```

### 基本用法

由于此插件已废弃，以下代码展示的是迁移后在 CoreUObject 中的正确用法：

```cpp
#include "InstancedStruct.h"

// 创建一个 FInstancedStruct 实例
FInstancedStruct InstancedStruct = FInstancedStruct::Make<FMyStruct>();

// 获取底层类型信息
const UScriptStruct* StructType = InstancedStruct.GetScriptStruct();

// 安全地获取数据引用
if (FMyStruct* Data = InstancedStruct.GetMutablePtr<FMyStruct>())
{
    Data->SomeField = 42;
}
```

### 进阶用法

```cpp
// 从已有结构体实例创建
FMyStruct OriginalData;
FInstancedStruct Copy = FInstancedStruct::Make(OriginalData);

// 拷贝/移动语义
FInstancedStruct Copy2 = Copy;       // 拷贝构造
FInstancedStruct Moved = MoveTemp(Copy); // 移动构造

// 重置
InstancedStruct.Reset();

// 判断是否为空
if (InstancedStruct.IsValid())
{
    // 有有效数据
}
```

## Demo 示例

由于此插件已废弃且功能已迁移，建议直接在 CoreUObject 中使用 FInstancedStruct：

```cpp
// MyComponent.h
#pragma once
#include "Components/ActorComponent.h"
#include "InstancedStruct.h"
#include "MyComponent.generated.h"

UCLASS()
class UMyComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    // 存储任意结构体的属性
    UPROPERTY(EditAnywhere, Category = "Data")
    FInstancedStruct PayloadData;

    // 动态设置不同类型的数据
    template<typename T>
    void SetPayload(const T& InData)
    {
        PayloadData = FInstancedStruct::Make(InData);
    }

    // 获取数据
    template<typename T>
    const T* GetPayload() const
    {
        return PayloadData.GetPtr<T>();
    }
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Engine` | StructUtils 模块依赖 |

无特殊依赖（StructUtilsEngine 模块无额外依赖）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-08-05 | `5bf7f335` | Iris - Move InstancedStructNetSerializer to IrisCore. | 将网络序列化器迁移至 IrisCore 模块 |
| 2024-08-01 | `0e320e33` | Iris - Crash fix for removing InstancedStruct from a replicated array and adding the same struct typ | 修复从复制数组中移除并重新添加同类型结构体的崩溃 |
| 2024-06-28 | `8083cf8c` | Iris - Adjust includes due to StructUtils moving. | 因 StructUtils 迁移调整头文件引用 |
| 2024-06-28 | `3680fd08` | Iris - Initial naive but working version of FInstancedStructNetSerializer to be able to replicate FI | 添加 FInstancedStructNetSerializer 初步实现以支持网络复制 |
| 2024-06-19 | `e6d36d75` | Remove references to deprecated plugin StructUtils (now part of CoreUObject) | 移除对已废弃插件的引用，功能已迁移至 CoreUObject |

### 维护评价

**🚫 已废弃，不推荐使用**

- 此插件在 UE 5.5 中已被标记废弃（DeprecatedEngineVersion: "5.5"）
- 2024 年 6 月的 commit 明确确认功能已迁移至 CoreUObject
- 当前目录中的剩余代码仅保留用于 Iris 网络复制的迁移过渡
- 近期的 commit 都是在"清理"和"迁移"，而非开发新功能
- **请直接使用 CoreUObject 模块中的 `FInstancedStruct`**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/StructUtils)
- 官方文档：无
- [迁移后的位置 - CoreUObject/InstancedStruct](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Source/Runtime/CoreUObject/Public/StructUtils/InstancedStruct.h)