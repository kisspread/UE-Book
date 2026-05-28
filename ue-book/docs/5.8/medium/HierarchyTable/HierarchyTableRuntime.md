# Hierarchy Table

> 

| 属性 | 值 |
|---|---|
| 中文名 | 层级数据表 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `HierarchyTableRuntime` (Runtime), `HierarchyTableEditor` (UncookedOnly) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2024-07-30 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/HierarchyTable) | |

## 用途

`HierarchyTable` 是一个**通用的层次化数据容器**插件。它提供了一个资产 (`UHierarchyTable`) 来存储树状结构的数据，其中每个节点可以携带用户自定义的、类型化的数据负载 (`Payload`)。其核心特性是支持数据的**继承与覆盖**机制：子节点可以选择继承父节点的值，也可以设置自己的值进行覆盖。这使得它非常适合管理诸如骨骼动画混合权重、LOD参数、材质参数分层覆盖等需要树状继承关系的数据。

## 使用场景

- **管理骨骼蒙皮权重**：为骨骼树中的每个骨骼存储一个权重值，允许子骨骼继承或覆盖父骨骼的权重。
- **分层LOD设置**：为模型的不同部位（如头、手、身体）定义LOD距离参数，子部位可以继承父部位的设置。
- **材质参数混合**：构建一个基于骨骼树的材质参数（如颜色、粗糙度）分层系统。
- **任何需要树状层次结构并带有可继承、可覆盖数据的应用场景**。

## 蓝图用法

该插件的核心是作为数据资产使用，其本身提供的 `BlueprintCallable` 函数有限。主要的交互通常在编辑器中完成，或在C++中通过其API进行。蓝图层面主要涉及对该资产 (`UHierarchyTable`) 的引用和遍历。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Table Entry` | 根据条目名称 (`FName`) 获取层级表中的条目数据 | `UHierarchyTable` |
| `Get Children` | 获取指定条目的所有子条目 | `UHierarchyTable` |
| `Get Table Data` | 获取整个表的所有条目数据数组 | `UHierarchyTable` |
| `Is Overridden` | 判断一个条目是否有自定义覆盖值，还是继承自父级 | `FHierarchyTableEntryData` |
| `Get Value` / `Get Metadata` | 获取条目的数据负载或元数据 | `FHierarchyTableEntryData` |

### 使用示例（蓝图描述）

1.  **创建与初始化**：在内容浏览器中右键 → Animation → Hierarchy Table 创建资产。打开后，在编辑器界面中设置表的类型（`Table Metadata`）和元素类型（`Element Type`），然后添加树状节点并为每个节点设置值。
2.  **运行时访问**：在蓝图中，通过 `Load Asset` 节点或直接变量引用 `UHierarchyTable` 资产。使用 `Get Table Entry` 节点获取特定骨骼的条目，然后调用其 `GetValue` 函数（通过类型转换节点，如 `Struct Get Float`）来读取存储的 `float` 值。

## C++ 用法

### 头文件引入

```cpp
#include "HierarchyTable.h"
#include "HierarchyTableDefaultTypes.h"
```

### 基本用法

以下代码演示了如何在运行时查询一个预定义的 `HierarchyTable` 资产中某个条目的值。
*(来源: Public/HierarchyTable.h)*

```cpp
// 假设已经获得了一个指向 UHierarchyTable 资产的指针 (HierarchyTableAsset)
UHierarchyTable* HierarchyTableAsset = ...;

// 通过名称查找一个条目
const FName BoneName = TEXT("spine_01");
const FHierarchyTableEntryData* Entry = HierarchyTableAsset->GetTableEntry(BoneName);

if (Entry)
{
    // 检查该条目是否有自己的覆盖值，还是继承自父级
    bool bIsCustomValue = Entry->IsOverridden();

    // 获取实际生效的值（如果自身未覆盖，会递归查找最近的有覆盖值的祖先）
    const FHierarchyTable_ElementType_Float* FloatValue = Entry->GetValue<FHierarchyTable_ElementType_Float>();
    if (FloatValue)
    {
        float CurrentWeight = FloatValue->Value;
        // ... 使用权重值
    }

    // 获取该条目的元数据（表类型相关的只读数据）
    // const SomeMetadataType& Meta = Entry->GetMetadata<SomeMetadataType>();
}
```

### 进阶用法

以下代码展示了如何动态构建一个层级表，并使用类型安全的访问方法。
*(来源: Public/HierarchyTable.h, Public/HierarchyTableDefaultTypes.h)*

```cpp
#include "InstancedStruct.h" // 来自 StructUtils 模块

// 1. 创建并初始化一个新的层级表对象（通常在编辑器工具或特定上下文中）
UHierarchyTable* NewTable = NewObject<UHierarchyTable>();

// 设置表类型为默认类型，元素类型为浮点类型
FInstancedStruct TableMetadata = FInstancedStruct::Make<FHierarchyTable_TableType_Default>();
const UScriptStruct* ElementType = FHierarchyTable_ElementType_Float::StaticStruct();
NewTable->Initialize(TableMetadata, ElementType);

// 2. 创建并添加条目
FHierarchyTableEntryData RootEntry;
RootEntry.Identifier = TEXT("root");
RootEntry.Parent = INDEX_NONE; // 根节点
RootEntry.Payload = FInstancedStruct::Make<FHierarchyTable_ElementType_Float>(1.0f); // 设置覆盖值
NewTable->AddEntry(RootEntry);

FHierarchyTableEntryData ChildEntry;
ChildEntry.Identifier = TEXT("child");
ChildEntry.Parent = 0; // 父节点索引为0（即root）
// 不设置 Payload，将继承父级的值
NewTable->AddEntry(ChildEntry);

// 3. 读取数据
const FHierarchyTableEntryData* Child = NewTable->GetTableEntry(TEXT("child"));
if (Child && !Child->IsOverridden())
{
    // 将继承来自 “root” 的值
    const FHierarchyTable_ElementType_Float* InheritedValue = Child->GetValue<FHierarchyTable_ElementType_Float>();
    // InheritedValue->Value 应为 1.0f
}
```

## Demo 示例

以下是一个最小的运行时模块，演示了如何创建一个自定义的元素类型并将其存入层级表。

**MyGameTypes.h**
```cpp
#pragma once

#include "HierarchyTableType.h"
#include "MyGameTypes.generated.h"

// 自定义一个元素类型，例如“颜色权重”
USTRUCT(BlueprintType)
struct FMyElementType_ColorWeight : public FHierarchyTable_ElementType
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Data")
	FLinearColor Color = FLinearColor::White;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Data", meta = (ClampMin = "0.0", ClampMax = "1.0"))
	float Weight = 1.0f;
};
```

**MyHierarchyTableUser.cpp**
```cpp
#include "MyHierarchyTableUser.h"
#include "HierarchyTable.h"
#include "MyGameTypes.h"
#include "InstancedStruct.h"

void AMyHierarchyTableUser::ProcessHierarchyTable(UHierarchyTable* Table)
{
	if (!Table || !Table->IsElementType<FMyElementType_ColorWeight>())
	{
		return;
	}

	// 遍历所有条目
	for (const FHierarchyTableEntryData& Entry : Table->GetTableData())
	{
		// 使用模板函数安全地获取我们自定义的类型
		const FMyElementType_ColorWeight* MyData = Entry.GetValue<FMyElementType_ColorWeight>();
		if (MyData)
		{
			UE_LOG(LogTemp, Log, TEXT("Entry [%s]: Color=%s, Weight=%.2f, Inherited=%s"),
				*Entry.Identifier.ToString(),
				*MyData->Color.ToString(),
				MyData->Weight,
				Entry.IsOverridden() ? TEXT("No") : TEXT("Yes"));
		}
	}
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `StructUtils` | 提供 `FInstancedStruct`，是实现类型化、可运行时确定的 `Payload` 的核心依赖 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `c19c7e83` | [ContentBrowser] New Add Menu Misc Menu | 内容浏览器“添加”菜单中的“杂项”分类调整，可能影响本插件资产创建入口。 |
| 2026-03-18 | `50b37fba` | [iOS/macOS] Fixes for Clang 21 implicit conversion warnings. | 修复了特定平台编译器的警告，属于平台兼容性维护。 |
| 2026-03-04 | `d9a06590` | Update UAF blend profiles | 更新了动画混合配置文件功能，表明插件与动画系统仍在协同演进。 |
| 2025-11-06 | `e75a5dce` | Move hierarchy table from animation category to misc. | 将此插件资产类型从“动画”分类移至“杂项”，暗示其通用性定位。 |
| 2025-09-08 | `7c9e306e` | Add live updating blend mask weights in the Profile Blend node | 在混合节点中增加了实时更新混合遮罩权重的功能，是其核心动画应用的一个增强。 |

### 维护评价

该插件创建于 **2024年7月**，是一个相对**年轻且实验性**的插件。从提交历史看，**最近一次实质性功能相关提交在2025年9月**，之后的更新主要是编译警告修复和菜单分类调整，表明其核心功能已趋于稳定，但**没有被标记为活跃开发**。

**优点**：
- 设计清晰，解决了动画和特效中常见的层次化数据管理问题。
- 代码结构良好，提供了类型安全的访问接口。

**风险与限制**：
- 实验性 (`IsExperimentalVersion: true`) 且默认未启用，意味着API可能在未来版本中发生不兼容的更改。
- 源码中的 `TODO` 注释（如 `GetActualValue` 的缓存问题）表明存在已知的性能优化点。
- 文档和示例几乎没有，使用者需要深入研究源码。

**建议**：如果你的项目需要管理树状结构的继承数据，且可以接受实验性API的风险，那么 `HierarchyTable` 是一个值得考虑的架构选择。不建议在追求长期稳定性的项目中作为核心基础设施使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/HierarchyTable)
- [官方文档]() (无)