# PropertyBindingUtils

> Utility code for implementing property bindings

| 属性 | 值 |
|---|---|
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PropertyBindingUtils` (Runtime), `PropertyBindingUtilsEditor` (Editor), `PropertyBindingUtilsTestSuite` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-15 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/PropertyBindingUtils) | |

## 用途

PropertyBindingUtils 是一个底层运行时框架，用于在 Unreal Engine 中实现**属性绑定（Property Binding）**机制。它解决的核心问题是：如何在两个不同的结构体/UObject 之间，通过**属性路径（Property Path）**描述源属性到目标属性的映射关系，并在运行时高效地执行属性值的拷贝。

这个 plugin 并不直接面向终端用户，而是作为 **State Tree** 和其他 Virtual Production 系统的基础设施层存在。它提供了：

1. **属性路径解析**：将字符串形式的路径（如 `StructB.B`、`ArrayOfInts[1]`、`InstancedObject.A`）解析为可高效遍历的中间表示
2. **属性绑定管理**：以 Source → Target 的方式管理绑定关系，支持绑定的增删查改
3. **属性拷贝执行**：根据绑定关系，在运行时将源属性值拷贝到目标属性，支持类型提升（Promotion）
4. **编辑器集成**：提供 Property Handle 扩展和 Slate Widget，使属性绑定可以在 Details Panel 中可视化操作

State Tree 的 Data Binding 功能就是基于此 plugin 构建的——State Tree 节点的输入/输出属性绑定的编译和执行，全部依赖 PropertyBindingUtils 提供的基础设施。

## 使用场景

- 你在做 **State Tree** 系统，需要在节点之间传递属性值 → 使用 PropertyBindingUtils 的绑定集合和路径解析
- 你需要在编辑器中为任意结构体属性提供**绑定 UI**（类似 Property Access 那样的下拉选择器）→ 继承 `FPropertyBindingExtension`
- 你需要实现一个自定义的**属性驱动系统**，让数据源的属性自动拷贝到消费者 → 使用 `FPropertyBindingBindingCollection` 管理绑定，`ResolvePaths()` 解析路径，`CopyProperty()` 执行拷贝
- 你需要处理**动态类型结构体**（如 `FInstancedStruct`、`FSharedStruct`）中的属性访问 → `FPropertyBindingPath` 原生支持这些间接引用

## 蓝图用法

PropertyBindingUtils 是纯 C++ 框架，没有暴露 BlueprintCallable 节点。它的使用场景主要在 State Tree 等上层系统的编辑器 UI 中。

如果需要在蓝图中实现类似功能，应该使用 State Tree 的蓝图集成，或者自行通过 C++ 暴露封装接口。

## C++ 用法

### 头文件引入

```cpp
// 核心类型
#include "PropertyBindingPath.h"
#include "PropertyBindingBinding.h"
#include "PropertyBindingBindingCollection.h"
#include "PropertyBindingBindingCollectionOwner.h"
#include "PropertyBindingDataView.h"
#include "PropertyBindingTypes.h"
#include "PropertyBindingBindableStructDescriptor.h"

// 编辑器扩展（仅 Editor 模块）
#include "PropertyBindingExtension.h"
```

### 基本用法：解析属性路径

属性路径是整个系统的核心。路径格式为 `Foo.Bar[1].Baz`，用 `.` 分隔属性名，`[N]` 表示数组索引。

```cpp
// 来源: PropertyBindingUtilsTest.cpp
#include "PropertyBindingPath.h"

// 1. 从字符串解析路径
FPropertyBindingPath Path;
bool bSuccess = Path.FromString(TEXT("StructB.B"));
// bSuccess == true, Path.NumSegments() == 2

// 2. 对已知类型解析路径的间接引用（Indirection）
TArray<FPropertyBindingPathIndirection> Indirections;
FString Error;
bool bResolved = Path.ResolveIndirections(
    FMyStruct::StaticStruct(),  // 基础结构体类型
    Indirections,               // 输出：解析后的间接引用链
    &Error                      // 输出：错误信息
);

// 3. 使用解析后的间接引用读取属性值
if (bResolved)
{
    // Indirections[0] -> StructB 属性 (Offset 访问)
    // Indirections[1] -> B 属性 (Offset 访问)
    const int32 Value = *reinterpret_cast<const int32*>(
        Indirections.Last().GetPropertyAddress()
    );
}
```

### 进阶用法：带值解析与动态类型

当路径中包含 `FInstancedStruct` 或 `UObject*` 引用时，需要使用带值解析来获取运行时实际类型：

```cpp
// 来源: PropertyBindingUtilsTest.cpp

// InstancedStruct 路径解析
FPropertyBindingPath Path;
Path.FromString(TEXT("ArrayOfInstancedStructs[0].B"));

UPropertyBindingUtilsTest_PropertyObject* Object = NewObject<...>();
// ... 填充 Object->ArrayOfInstancedStructs ...

// UpdateSegmentsFromValue 会写入实际的实例类型到路径段中
Path.UpdateSegmentsFromValue(FPropertyBindingDataView(Object));

// 之后可以不带值进行解析（因为类型已缓存在路径段中）
TArray<FPropertyBindingPathIndirection> Indirections;
Path.ResolveIndirections(
    UPropertyBindingUtilsTest_PropertyObject::StaticClass(),
    Indirections
);
// Indirections: [IndexArray, StructInstance, Offset]
// StructInstance 表示进入了 FInstancedStruct 的运行时类型
```

**支持的访问类型**（`EPropertyBindingPropertyAccessType`）：

| 类型 | 说明 |
|---|---|
| `Offset` | 简单偏移量访问（basePtr + offset） |
| `Object` | 解引用 UObject 指针 |
| `ObjectInstance` | 解引用特定类型的 UObject（Instanced） |
| `StructInstance` | 解引用 FInstancedStruct |
| `SharedStruct` | 解引用 FSharedStruct |
| `StructInstanceContainer` | 解引用 FInstancedStructContainer |
| `IndexArray` | 索引访问动态数组 |

### 进阶用法：绑定集合（Binding Collection）

```cpp
#include "PropertyBindingBindingCollection.h"
#include "PropertyBindingBindingCollectionOwner.h"

// 绑定集合是绑定的容器，需要继承 FPropertyBindingBindingCollection
// 并实现纯虚函数
class FMyBindingCollection : public FPropertyBindingBindingCollection
{
    // 实现 ForEachBinding, ForEachMutableBinding 等纯虚函数
    // 管理绑定的存储
};

// 在 Owner 中使用
// 1. 创建绑定（Editor-only，用于 UI 操作）
#if WITH_EDITOR
BindingCollection->AddBinding(SourcePath, TargetPath);
#endif

// 2. 解析路径（将路径转换为可执行的间接引用）
bool bResolved = BindingCollection->ResolvePaths();

// 3. 执行属性拷贝（运行时）
FPropertyBindingDataView SourceView(SourceStruct, SourceMemory);
FPropertyBindingDataView TargetView(TargetStruct, TargetMemory);
BindingCollection->CopyProperty(CopyInfo, SourceView, TargetView);
```

### 属性兼容性检查

```cpp
#include "PropertyBindingTypes.h"

const FProperty* SourceProp = ...;
const FProperty* TargetProp = ...;

auto Compat = UE::PropertyBinding::GetPropertyCompatibility(SourceProp, TargetProp);
// EPropertyCompatibility::Compatible    - 直接兼容
// EPropertyCompatibility::Promotable    - 可通过类型提升兼容（如 int→float）
// EPropertyCompatibility::Incompatible  - 不兼容
```

## Demo 示例

### 最小属性路径解析示例

```cpp
// MyPropertyBindingDemo.h
#pragma once
#include "PropertyBindingPath.h"
#include "PropertyBindingDataView.h"

USTRUCT()
struct FMyData
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere)
    float Health = 100.0f;

    UPROPERTY(EditAnywhere)
    int32 Score = 0;
};

// MyPropertyBindingDemo.cpp
#include "MyPropertyBindingDemo.h"

void DemoPropertyPath()
{
    // 解析路径
    FPropertyBindingPath Path;
    Path.FromString(TEXT("Health"));

    // 解析间接引用
    TArray<FPropertyBindingPathIndirection> Indirections;
    if (Path.ResolveIndirections(FMyData::StaticStruct(), Indirections))
    {
        // 读取值
        FMyData Data;
        Data.Health = 42.0f;

        // 使用带值解析获取属性地址
        TArray<FPropertyBindingPathIndirection> ValueIndirections;
        Path.ResolveIndirectionsWithValue(
            FPropertyBindingDataView(FMyData::StaticStruct(), &Data),
            ValueIndirections
        );

        const float Value = *reinterpret_cast<const float*>(
            ValueIndirections.Last().GetPropertyAddress()
        );
        // Value == 42.0f
    }
}
```

**Build.cs 依赖**：
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "PropertyBindingUtils"
});
```

## 模块依赖

### PropertyBindingUtils（Runtime 模块）

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、日志、数学 |
| `CoreUObject` | UObject 系统、反射、序列化 |
| `Engine` | 引擎核心类型 |
| `RenderCore` | 渲染核心（Private） |
| `InputCore` | 输入核心（Private） |
| `UnrealEd` | 编辑器支持（仅 Editor 构建，Public） |
| `BlueprintGraph` | 蓝图图表支持（仅 Editor 构建，Public） |

### PropertyBindingUtilsEditor（Editor 模块）

| 模块 | 用途 |
|---|---|
| `PropertyBindingUtils` | 运行时核心 |
| `Slate` / `SlateCore` | UI 框架 |
| `UnrealEd` | 编辑器框架 |
| `EditorFramework` | 编辑器框架 |
| `BlueprintGraph` | 蓝图属性系统集成 |
| `StructUtilsEditor` | 结构体工具编辑器支持（Private） |

### PropertyBindingUtilsTestSuite（UncookedOnly 模块）

| 模块 | 用途 |
|---|---|
| `PropertyBindingUtils` | 被测试的模块 |
| `AITestSuite` | 测试框架 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-10-22 | `e9320294` | [State Tree] fixed behavior of removing duplicate bindings | 修复了去重绑定时的行为 bug，现在保留一条而非全部删除 |
| 2025-10-02 | `44d2e9a4` | [State Tree][Property Binding] Introduced output binding feature | 引入**反向绑定（Output Binding）**功能：目标属性可反向写回源属性，在节点处理范围结束时执行 |
| 2025-09-26 | `2e6d0afe` | [State Tree] Added copy and paste binding option | 在 Details 视图中右键支持复制/粘贴绑定 |

### 维护评价

- **创建时间**：2024-01-15，约 2 年前
- **维护状态**：**活跃维护** — 最近一次更新在 2025 年 10 月，更新频繁（近 1 个月有 3 次更新），且都是功能性更新而非简单的编译修复
- **活跃程度**：非常高，作为 State Tree 的核心基础设施，Epic 持续投入开发
- **实验性标记**：`IsBetaVersion=true`，`EnabledByDefault=false` — 虽然 API 稳定且已被 State Tree 大量使用，但 Epic 尚未正式标记为稳定版本
- **推荐使用**：如果你在开发 State Tree 相关功能或自定义属性驱动系统，推荐使用。但注意 API 仍在演进中（如 5.6 中 `EPropertyAccessType` 被废弃改为 `EPropertyBindingPropertyAccessType`，5.7 中 `ResolveCopyType` 被废弃改为 `ResolveBindingCopyInfo`）

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/PropertyBindingUtils)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Runtime/PropertyBindingUtils/Source/PropertyBindingUtilsTestSuite/Private/PropertyBindingUtilsTest.cpp)
