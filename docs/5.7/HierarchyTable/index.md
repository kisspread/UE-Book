# Hierarchy Table

> （.uplugin Description 为空）

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画资产） |
| 模块 | `HierarchyTableRuntime` (Runtime), `HierarchyTableEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-07-30 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Animation/HierarchyTable) | |

## 用途

HierarchyTable 是一个**通用的层级数据容器插件**，用于存储具有父子继承关系的结构化数据。它的核心设计思路是：以树形结构组织条目，每个条目可以附加任意类型的载荷（Payload），并且子条目可以选择性地**覆盖**或**继承**父条目的值。

这个插件解决的核心问题是：在动画系统中，需要按骨骼层级定义每根骨骼的参数（如混合权重、遮罩值等），并且希望子骨骼能自动继承父骨骼的设置，同时允许对个别骨骼做局部覆盖。虽然插件被放在 Animation 分类下，但其运行时核心（`UHierarchyTable`）是完全通用的，不限于动画场景。

插件本身没有 Description，从源码推断其主要用途包括：
- 为动画骨骼层级提供可继承的参数表（Float 值、Mask 值等）
- 作为 BlendProfile 的底层数据存储，驱动分层混合动画
- 通过可扩展的 TableType 和 ElementType 系统支持自定义数据类型

## 使用场景

- 你需要按骨骼层级定义每根骨骼的混合权重，且希望子骨骼自动继承父骨骼的设置 → 用 HierarchyTable + HierarchyTableAnimation
- 你需要创建一个分层遮罩（Blend Mask），控制动画层叠时哪些骨骼参与混合 → 用 HierarchyTable 的 Mask 类型
- 你需要一个通用的树形数据资产，存储任何具有层级继承关系的参数 → 用 HierarchyTable 的默认类型

## 蓝图用法

HierarchyTable 运行时模块不暴露 BlueprintCallable 函数。它的主要使用方式是作为数据资产在 C++ 中读取，或通过 HierarchyTableAnimation 插件的动画节点间接使用。

### 动画蓝图节点

HierarchyTableAnimation 插件提供了一个动画蓝图节点：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Blend Profile Layered Blend` | 使用 HierarchyTable 驱动的 BlendProfile 进行分层姿态混合 | `FAnimNode_BlendProfileLayeredBlend` |

在动画蓝图中使用时：
1. 创建一个 `BlendProfileStandalone` 资产（基于 Skeleton 类型的 HierarchyTable）
2. 在 AnimGraph 中添加 "Blend Profile Layered Blend" 节点
3. 连接 BasePose（基础姿态）和 BlendPose（混合姿态）
4. 指定 BlendProfileAsset 为步骤 1 创建的资产
5. 通过 BlendWeight pin 控制混合强度

## C++ 用法

### 头文件引入

```cpp
#include "HierarchyTable.h"
#include "HierarchyTableType.h"
```

### 基本用法 — 查询 HierarchyTable 数据

`UHierarchyTable` 是核心资产类，存储树形结构的条目数据。每个条目（`FHierarchyTableEntryData`）包含标识符、父索引、可选载荷和元数据。

```cpp
// 获取资产（假设已经通过 AssetManager 或 LoadObject 加载）
UHierarchyTable* Table = LoadObject<UHierarchyTable>(nullptr, TEXT("/Game/MyTable"));

// 按名称查找条目
const FHierarchyTableEntryData* Entry = Table->GetTableEntry(FName("spine_01"));
if (Entry)
{
    // 获取实际值（会自动向上查找最近的被覆盖祖先）
    const float* Value = Entry->GetValue<FHierarchyTable_ElementType_Float>();
    if (Value)
    {
        float Weight = *Value;
    }
}

// 检查条目是否覆盖了父条目的值
bool bOverridden = Entry->IsOverridden();

// 获取子条目
TArray<const FHierarchyTableEntryData*> Children = Table->GetChildren(*Entry);

// 检查表的类型
if (Table->IsTableType<FHierarchyTable_TableType_Default>())
{
    // 默认类型
}
```

来源：`Source/Runtime/Public/HierarchyTable.h`、`Source/Runtime/Private/HierarchyTable.cpp`

### 值继承机制

HierarchyTable 的核心特性是值继承。条目的 `Payload` 字段是 `TOptional<FInstancedStruct>`：
- 如果 `Payload.IsSet()` 为 true，表示该条目**覆盖**了父条目的值
- 如果 `Payload.IsSet()` 为 false，表示该条目**继承**父条目的值
- 调用 `GetValue<T>()` 时，系统会自动沿父链向上查找，直到找到第一个被覆盖的祖先
- 根条目（`Parent == INDEX_NONE`）的 Payload 必须被设置

```cpp
// 切换覆盖状态：覆盖→继承，继承→覆盖（从最近祖先复制值）
Entry->ToggleOverridden();

// 获取最近的被覆盖祖先
const FHierarchyTableEntryData* Ancestor = Entry->GetClosestAncestor();
```

来源：`Source/Runtime/Private/HierarchyTable.cpp`

### 类型系统

HierarchyTable 使用三层类型标记：

```cpp
// 表类型：定义表格的元数据结构
FHierarchyTable_TableType              // 基类
FHierarchyTable_TableType_Default      // 默认类型（无额外元数据）
FHierarchyTable_TableType_Skeleton     // 骨骼类型（绑定 USkeleton）

// 表载荷类型：定义每个条目的只读元数据
FHierarchyTable_TablePayloadType       // 基类
FHierarchyTable_TablePayloadType_Skeleton  // 骨骼条目类型（Bone/Curve/Attribute）

// 元素类型：定义每个条目的用户数据
FHierarchyTable_ElementType            // 基类
FHierarchyTable_ElementType_Float      // 浮点值（默认内置）
FHierarchyTable_ElementType_Mask       // 遮罩值（HierarchyTableAnimation 提供）
```

来源：`Source/Runtime/Public/HierarchyTableType.h`、`HierarchyTableDefaultTypes.h`

### 进阶用法 — 创建和操作 HierarchyTable

```cpp
// 创建 HierarchyTable 实例（通常由 Factory 处理，但也可手动创建）
UHierarchyTable* NewTable = NewObject<UHierarchyTable>();

// 初始化：设置表类型和元素类型
FInstancedStruct TableMetadata;
TableMetadata.InitializeAs(FHierarchyTable_TableType_Default::StaticStruct());
NewTable->Initialize(TableMetadata, FHierarchyTable_ElementType_Float::StaticStruct());

// 添加根条目
FHierarchyTableEntryData RootEntry;
RootEntry.Identifier = FName("root");
RootEntry.Parent = INDEX_NONE;
FInstancedStruct RootPayload;
RootPayload.InitializeAs<FHierarchyTable_ElementType_Float>();
RootPayload.GetMutable<FHierarchyTable_ElementType_Float>().Value = 1.0f;
RootEntry.Payload = RootPayload;
int32 RootIndex = NewTable->AddEntry(RootEntry);

// 添加子条目（继承父值）
FHierarchyTableEntryData ChildEntry;
ChildEntry.Identifier = FName("child_01");
ChildEntry.Parent = RootIndex;
// 不设置 Payload，表示继承
int32 ChildIndex = NewTable->AddEntry(ChildEntry);

// 批量添加
TArray<FHierarchyTableEntryData> BulkEntries;
// ... 填充数据 ...
NewTable->AddBulkEntries(BulkEntries);

// 按索引获取并修改条目
FHierarchyTableEntryData* MutableEntry = NewTable->GetMutableTableEntry(ChildIndex);
```

来源：`Source/Runtime/Private/HierarchyTable.cpp`

### 使用 BlendProfile（HierarchyTableAnimation）

```cpp
#include "BlendProfileStandalone.h"
#include "HierarchyTableBlendProfile.h"

// 从 BlendProfileStandalone 获取运行时混合配置
UBlendProfileStandalone* BlendProfile = LoadObject<UBlendProfileStandalone>(nullptr, TEXT("/Game/MyBlendProfile"));

// 获取缓存的混合数据
const FBlendProfileStandaloneCachedData& CachedData = BlendProfile->CachedBlendProfileData;

// 获取骨骼混合权重
const TArray<float>& BoneWeights = CachedData.GetBoneBlendWeights();

// 获取曲线混合权重
const auto& CurveWeights = CachedData.GetCurveBlendWeights();

// 获取属性混合权重
const auto& AttributeWeights = CachedData.GetAttributeBlendWeights();
```

来源：`Source/Runtime/Public/HierarchyTableBlendProfile.h`、`BlendProfileStandalone.h`

## Demo 示例

### Build.cs 依赖

```csharp
// 使用 HierarchyTable 运行时
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "HierarchyTableRuntime"
});

// 如果需要动画相关功能（BlendProfile 等）
PublicDependencyModuleNames.Add("HierarchyTableAnimationRuntime");
```

### 遍历 HierarchyTable 并读取所有覆盖值

```cpp
// MyAnimComponent.h
#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MyAnimComponent.generated.h"

class UHierarchyTable;

UCLASS()
class UMyAnimComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere)
    TObjectPtr<UHierarchyTable> BlendWeightTable;

    void PrintAllOverriddenWeights();
};
```

```cpp
// MyAnimComponent.cpp
#include "MyAnimComponent.h"
#include "HierarchyTable.h"
#include "HierarchyTableDefaultTypes.h"

void UMyAnimComponent::PrintAllOverriddenWeights()
{
    if (!BlendWeightTable || !BlendWeightTable->IsElementType<FHierarchyTable_ElementType_Float>())
    {
        return;
    }

    for (const FHierarchyTableEntryData& Entry : BlendWeightTable->GetTableData())
    {
        // GetValue 会自动沿父链查找实际值
        const float* Value = Entry.GetValue<FHierarchyTable_ElementType_Float>();
        if (Value)
        {
            UE_LOG(LogTemp, Log, TEXT("Bone: %s, Weight: %.2f, Overridden: %s"),
                *Entry.Identifier.ToString(),
                *Value,
                Entry.IsOverridden() ? TEXT("Yes") : TEXT("No (inherited)"));
        }
    }
}
```

## 模块依赖

### HierarchyTable（核心插件）

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心（USkeleton 等） |

### HierarchyTableAnimation（动画扩展插件）

| 模块 | 用途 |
|---|---|
| `HierarchyTableRuntime` | HierarchyTable 运行时核心 |
| `AnimationCore` | 动画骨骼系统 |
| `AnimGraphRuntime` | 动画蓝图运行时节点 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-09-08 | `147942822490` | Add live updating blend mask weights in the Profile Blend node | 编辑器中修改 BlendProfile 资产后，AnimGraph 节点会立即更新，无需重新编译。同时添加了编辑撤销支持。 |
| 2025-07-10 | `9803c443cfab` | Added UE_INLINE_GENERATED_CPP_BY_NAME | 自动化工具批量添加内联生成代码宏，减少编译时间。非功能性改动。 |
| 2025-06-26 | `ec9009980d52` | Added UE_INLINE_GENERATED_CPP_BY_NAME | 同上，另一个批次的自动修复。 |

### 维护评价

- **创建时间**：2024 年 7 月，约 2 年前
- **最近更新**：2025 年 9 月有功能性更新（实时编辑器预览），说明仍在活跃开发
- **实验性状态**：`IsExperimentalVersion=true`，API 可能在未来版本中发生变化
- **无测试用例**：插件目录和 Engine/Tests 下均未找到自动化测试
- **已知限制**：`FHierarchyTableEntryData::GetActualValue()` 在每次调用时会沿父链向上遍历，源码注释中标注了 TODO——需要缓存优化，当前在高频调用场景下可能有性能问题
- **推荐**：适合在动画系统中使用，但注意其**实验性**状态。如果你需要骨骼级别的混合权重控制，这是目前 UE5 推荐的方式（替代旧的 UBlendProfile 内嵌方式）。不建议在非动画场景中依赖此插件，因为 API 可能变动。

## 相关链接

- [源码 — HierarchyTable](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Animation/HierarchyTable)
- [源码 — HierarchyTableAnimation](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Animation/HierarchyTableAnimation)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- 测试用例：无
