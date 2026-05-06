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

StructUtils 是一个实验性插件，最初用于提供 `FInstancedStruct` 类型（动态多态结构体容器）。  
但该功能**已在 UE 5.5 中被迁移到 CoreUObject 模块**，本插件已被标记为“已弃用”（`DeprecatedEngineVersion: "5.5"`）。  
**目前不需要启用此插件**：直接使用 `CoreUObject` 中的 `FInstancedStruct` 即可。

> 该插件存在的唯一历史意义是作为过渡，当前版本只是一个空壳（仅包含模块注册），实际代码已内置于引擎核心。

## 使用场景

- ❌ **不再需要此插件**。过去如果你需要动态存储不同类型（通过 UStruct 反射）的结构体，会依赖此插件。现在直接使用 `CoreUObject` 中的 `FInstancedStruct`。
- 其他工具（如 Mass、GameplayAbilities）直接引用 `CoreUObject` 中的 `FInstancedStruct`，无需额外插件。

## 蓝图用法

该插件不暴露任何蓝图可调用函数。`FInstancedStruct` 的蓝图节点位于 `CoreUObject` 中（如 `Make Instanced Struct`、`Break Instanced Struct`）。

### 相关节点（来自 CoreUObject）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Instanced Struct` | 创建一个空的 InstancedStruct 实例 | `UKismetSystemLibrary` |
| `Set Instanced Struct Value` | 设置 InstancedStruct 内部的数据 | 同上 |
| `Get Instanced Struct Value` | 获取 InstancedStruct 内部的数据（需指定类型） | 同上 |

> 若想使用蓝图中的 InstancedStruct，请确保项目使用的是 UE 5.5+ 且 **不启用** StructUtils 插件。

## C++ 用法

该插件本身不包含任何 C++ API（除一个空模块类）。实际使用 `FInstancedStruct` 的代码应在 `CoreUObject` 中寻找。

### 头文件引入

```cpp
#include "StructUtils/InstancedStruct.h"   // 已迁移至 CoreUObject
// 实际上现在推荐使用：
#include "InstancedStruct.h"               // UE 5.5+ 默认路径
```

### 基本用法

```cpp
// 创建一个包含 FVector 的 InstancedStruct
FInstancedStruct MyStruct;
MyStruct.InitializeAs<FVector>(FVector(100, 200, 300));

// 读取内部数据
const FVector* Vec = MyStruct.GetPtr<FVector>();
if (Vec)
{
    // ...
}
```

## Demo 示例

由于插件本身已废弃，不提供独立示例。可直接使用 Engine 内置功能。

### 最小代码片段（无需插件）

```cpp
// 在任意模块中（依赖 CoreUObject）
#include "InstancedStruct.h"

struct FMyCustomStruct
{
    FString Name;
    int32 Value;
};

void TestInstancedStruct()
{
    FInstancedStruct Instanced;
    Instanced.InitializeAs<FMyCustomStruct>({TEXT("Test"), 42});

    const FMyCustomStruct* Data = Instanced.GetPtr<FMyCustomStruct>();
    check(Data && Data->Value == 42);
}
```

## 模块依赖

该插件包含两个运行时模块，但均无实际代码。若需使用 `FInstancedStruct`，你的模块只需依赖 `CoreUObject` 即可（该模块是引擎核心依赖，不需要特别列出）。

| 模块 | 用途 |
|---|---|
| `StructUtils` | 空壳模块，仅用于兼容旧代码 |
| `StructUtilsEngine` | 空壳模块，同上 |

**实际使用时不需依赖任何该插件的模块**。

## 维护状态

### 近期更新

```
- 2024-08-05 5bf7f33 Iris - 将 InstancedStructNetSerializer 移至 IrisCore
- 2024-08-01 0e320e33 Iris - 修复从复制数组中移除 InstancedStruct 并添加相同结构体类型时的崩溃
- 2024-06-28 8083cf8c Iris - 因 StructUtils 移动调整包含路径
- 2024-06-28 3680fd08 Iris - FInstancedStructNetSerializer 的初始版本（实验性）
- 2024-06-19 e6d36d75 移除对已弃用的 StructUtils 插件的引用（现为 CoreUObject 的一部分）
```

### 维护评价

- **已废弃**：插件在 UE 5.5 被标记为弃用，所有功能已合并到 CoreUObject。
- **不再维护**：后续版本只会因兼容性原因保留空模块，但不会添加新功能。
- **不推荐使用**：新项目应直接使用 CoreUObject 中的 `FInstancedStruct`，无需启用此插件。
- 若你在旧版 UE 5.4 及以下仍需要此功能，可临时启用，但强烈建议升级。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/StructUtils)
- [InstancedStruct 官方文档（CoreUObject）](https://docs.unrealengine.com/5.7/en-US/API/Runtime/CoreUObject/InstancedStruct/)
- [迁移说明](https://github.com/EpicGames/UnrealEngine/commit/e6d36d75)