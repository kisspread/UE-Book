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

StructUtils 插件提供了 `FInstancedStruct` 类型，旨在解决虚幻引擎中结构体在运行时多态性方面的限制。传统的 `USTRUCT` 是值类型，在存储到数组或容器时，其类型在声明时就已经确定，无法在运行时动态改变或存储不同但相关的结构体类型。`FInstancedStruct` 封装了结构体实例及其类型信息，允许在运行时安全地存储、复制和访问不同类型的结构体数据，实现了结构体层面的多态性。

## 使用场景

- **运行时数据容器**：当你需要一个数组或映射表来存储多种不同类型的结构体数据（如不同的游戏事件数据、不同的伤害类型参数）时，可以使用 `TArray<FInstancedStruct>` 来替代多个独立的数组。
- **可扩展的组件系统**：在实现类似“能力系统”或“状态效果”时，每个能力/状态可能有不同的参数结构体。使用 `FInstancedStruct` 可以统一管理这些参数，并根据实际存储的类型进行分派。
- **序列化与网络复制**：`FInstancedStruct` 设计时考虑了序列化支持，可以用于需要保存或在网络上传输包含动态类型结构体数据的场景。
- **插件与模块解耦**：当不同模块需要交换数据但又不希望彼此依赖具体的结构体定义时，可以通过 `FInstancedStruct` 作为接口进行传递。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Make Literal` | 根据一个结构体值创建一个新的 `FInstancedStruct`。 | `FInstancedStruct` (蓝图库) |
| `Break Struct` | 从 `FInstancedStruct` 中提取特定类型的结构体数据。需要提供目标结构体类型作为上下文。 | `FInstancedStruct` (蓝图库) |
| `Get Script Struct` | 获取 `FInstancedStruct` 内部存储的结构体类型 (`UScriptStruct*`)。 | `FInstancedStruct` (蓝图库) |
| `IsValid` | 检查 `FInstancedStruct` 是否包含有效的结构体实例。 | `FInstancedStruct` (蓝图库) |

### 使用示例

在蓝图中，你可以使用 `Make Literal` 节点将一个具体的结构体值（如 `Vector`、`HitResult` 或自定义结构体）封装到一个 `FInstancedStruct` 变量中。当需要读取数据时，将该变量连接到 `Break Struct` 节点，并在节点上指定你期望的结构体类型。如果 `FInstancedStruct` 内存储的类型与指定类型匹配，则成功提取数据；否则，输出默认值。

## C++ 用法

### 头文件引入

```cpp
#include "InstancedStruct.h"
```

### 基本用法

以下示例展示如何创建、检查和访问 `FInstancedStruct`。假设存在一个自定义结构体 `FMyStruct`。

```cpp
// 创建一个实例，并存储一个 FMyStruct 类型的值
FMyStruct MyData;
MyData.SomeValue = 42;
FInstancedStruct InstancedStruct = FInstancedStruct::Make(MyData);

// 检查其是否有效且包含期望的类型
if (InstancedStruct.IsValid() && InstancedStruct.GetScriptStruct() == FMyStruct::StaticStruct())
{
    // 安全地获取内部数据的引用（const）
    const FMyStruct& RetrievedData = InstancedStruct.Get<FMyStruct>();
    UE_LOG(LogTemp, Log, TEXT("Retrieved value: %d"), RetrievedData.SomeValue);

    // 或者获取可修改的引用（需要确保类型正确）
    // FMyStruct& MutableData = InstancedStruct.GetMutable<FMyStruct>();
}
```

### 进阶用法

`FInstancedStruct` 常用于容器中，以实现存储多种类型结构体的目的。

```cpp
TArray<FInstancedStruct> StructArray;

// 向数组中添加不同类型的结构体
StructArray.Add(FInstancedStruct::Make(FVector(1,2,3)));
StructArray.Add(FInstancedStruct::Make(FHitResult()));
StructArray.Add(FInstancedStruct::Make(FMyStruct{99}));

// 遍历并检查类型
for (const FInstancedStruct& Item : StructArray)
{
    if (const UScriptStruct* StructType = Item.GetScriptStruct())
    {
        UE_LOG(LogTemp, Log, TEXT("Array item is of type: %s"), *StructType->GetName());
        // 根据 StructType 进行特定类型的数据处理...
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-08-05 | `5bf7f335` | Iris - Move InstancedStructNetSerializer to IrisCore. | 将 `FInstancedStruct` 的网络序列化器移至 Iris 核心模块。 |
| 2024-08-01 | `0e320e33` | Iris - Crash fix for removing InstancedStruct from a replicated array and adding the same struct typ | 修复在从复制数组中移除 `FInstancedStruct` 并添加相同类型结构体时导致的崩溃。 |
| 2024-06-28 | `8083cf8c` | Iris - Adjust includes due to StructUtils moving. | 因 StructUtils 位置调整，更新相关头文件包含路径。 |
| 2024-06-28 | `3680fd08` | Iris - Initial naive but working version of FInstancedStructNetSerializer to be able to replicate FI | 初始实现 `FInstancedStruct` 的网络序列化器，使其具备网络复制能力。 |
| 2024-06-19 | `e6d36d75` | Remove references to deprecated plugin StructUtils (now part of CoreUObject) | 清理对已废弃的旧版 StructUtils 插件的引用（暗示核心功能已迁移）。 |

### 维护评价

StructUtils 仍处于 **实验性** 阶段（`IsExperimentalVersion=true`），但近期的提交记录（截至2024年8月）表明它仍在 **活跃维护** 中，特别是围绕其核心类型 `FInstancedStruct` 的 **网络序列化** 功能（与 Iris 复制系统集成）进行了重要的修复和优化。尽管创建于约4年前，且最新的commit显示其部分功能可能正在被整合到引擎核心（CoreUObject）或更稳定的模块中，但插件本身仍在更新和改进。对于需要 `FInstancedStruct` 功能的项目，它是一个可用且正在发展的解决方案。需要注意其“实验性”标签，意味着API在未来版本中可能发生变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/StructUtils)
- [官方文档]() (暂无)
- [测试用例]() (暂无)