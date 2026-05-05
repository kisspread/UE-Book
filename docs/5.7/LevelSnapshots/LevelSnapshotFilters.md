# Level Snapshots

> （Description 为空）

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、过滤器模板） |
| 模块 | `LevelSnapshots` (UncookedOnly), `LevelSnapshotFilters` (UncookedOnly), `LevelSnapshotsEditor` (UncookedOnly), `FoliageSupport` (UncookedOnly), `nDisplaySupport` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-02-03 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/LevelSnapshots) | |

## 用途

Level Snapshots 是一个关卡状态快照与恢复系统，用于在虚拟制片和关卡编辑工作流中保存和恢复关卡的特定状态。

**核心问题**：在大型关卡编辑过程中，开发者经常需要：
- 在进行大规模修改前保存当前关卡状态作为"检查点"
- 对比快照与当前关卡的差异（哪些 Actor 被修改、添加或删除）
- 选择性地恢复部分关卡状态（例如只恢复位置，不恢复旋转）
- 按条件过滤哪些 Actor/属性需要被恢复

**为什么存在**：UE5 内置的撤销系统只能线性回退，无法跨会话保存状态，也无法进行细粒度的选择性恢复。Level Snapshots 填补了这一空白，特别适合虚拟制片中需要反复调整场景布局的工作流。

**模块职责划分**：
- **LevelSnapshots**：核心快照逻辑，负责序列化/反序列化关卡状态
- **LevelSnapshotFilters**：过滤器系统，定义哪些 Actor/属性参与快照操作
- **LevelSnapshotsEditor**：编辑器 UI，提供快照管理面板
- **FoliageSupport**：植被系统支持
- **nDisplaySupport**：nDisplay 多屏渲染支持

## 使用场景

- 你在虚拟制片中需要反复调整场景灯光和道具位置 → 用 Level Snapshots 保存多个检查点，随时回退
- 你需要对比两个版本的关卡差异 → 用快照对比功能查看哪些 Actor 被修改/添加/删除
- 你只想恢复某些 Actor 的位置而不影响其他属性 → 用 `UTransformPropertyFilter` 精确控制
- 你需要按标签或所属关卡批量过滤 Actor → 用 `UActorHasTagFilter` 或 `UActorInMapFilter`
- 你需要在 C++ 中快速定义自定义过滤逻辑 → 用 `ULambdaFilter`

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateFilterByClass` | 按类创建过滤器实例 | `UFilterBlueprintFunctionLibrary` |
| `GetPropertyOriginPath` | 获取属性声明所在的类路径 | `UPropertyBlueprintFunctionLibrary` |
| `GetPropertyName` | 获取属性名称 | `UPropertyBlueprintFunctionLibrary` |
| `LoadSnapshotActor` | 加载快照中已删除的 Actor | `UPropertyBlueprintFunctionLibrary` |
| `GetActorClassFromDeletedParams` | 从删除参数获取 Actor 类 | `UPropertyBlueprintFunctionLibrary` |
| `AddChild` | 向父过滤器添加子过滤器 | `UParentFilter` |
| `CreateChild` | 创建并添加子过滤器（可保存） | `UParentFilter` |
| `RemovedChild` | 移除子过滤器 | `UParentFilter` |
| `GetChildren` | 获取所有子过滤器 | `UParentFilter` |
| `CreateChild` (Negation) | 创建取反过滤器的子项 | `UNegationFilter` |
| `SetExternalChild` | 设置外部过滤器作为子项 | `UNegationFilter` |
| `GetChild` | 获取取反过滤器的子项 | `UNegationFilter` |

### 内置过滤器

| 过滤器 | 说明 |
|---|---|
| `UConstantFilter` | 对所有 Actor/属性返回固定结果 |
| `UActorHasTagFilter` | 按 Actor 标签过滤（支持全部匹配/任一匹配） |
| `UActorInMapFilter` | 按所属关卡过滤 |
| `UActorChangedTransformFilter` | 按 Transform 是否变化过滤 |
| `UPropertyHasNameFilter` | 按属性名称过滤（支持精确/模糊匹配） |
| `UPropertyTypeFilter` | 按属性类型过滤（Int、Float、Bool 等） |
| `UTransformPropertyFilter` | 精确控制 Location/Rotation/Scale 的恢复 |
| `UActorDependentPropertyFilter` | 根据 Actor 过滤结果选择不同的属性过滤器 |
| `UAndFilter` | AND 逻辑组合多个过滤器 |
| `UOrFilter` | OR 逻辑组合多个过滤器 |
| `UNegationFilter` | 取反过滤器结果 |

### 使用示例（蓝图描述）

**示例 1：只恢复特定标签 Actor 的位置**

1. 创建 `UActorHasTagFilter`，设置 `AllowedTags` 为 `{"Furniture"}`，`TagCheckingBehavior` 为 `HasAnyTag`
2. 创建 `UTransformPropertyFilter`，设置 `Location` 为 `Include`，`Rotation` 和 `Scale` 为 `DoNotCare`
3. 创建 `UAndFilter`，调用 `CreateChild` 添加上述两个过滤器
4. 将 `UAndFilter` 传入快照应用函数

**示例 2：排除已删除的 Actor，只恢复修改过的**

1. 创建 `UConstantFilter`，设置 `IsDeletedActorValidResult` 为 `Exclude`，其余为 `Include`
2. 直接传入快照应用函数

## C++ 用法

### 头文件引入

```cpp
#include "LevelSnapshotFilters.h"
#include "LevelSnapshotFilterParams.h"
#include "LambdaFilter.h"
```

### 基本用法

创建自定义 C++ 过滤器（继承 `ULevelSnapshotFilter`）：

```cpp
// MyCustomFilter.h
#pragma once

#include "CoreMinimal.h"
#include "LevelSnapshotFilters.h"
#include "MyCustomFilter.generated.h"

UCLASS()
class UMyCustomFilter : public ULevelSnapshotFilter
{
    GENERATED_BODY()
public:
    // 只允许包含 "Furniture" 标签的 Actor
    virtual EFilterResult::Type IsActorValid(const FIsActorValidParams& Params) const override
    {
        if (Params.LevelActor && Params.LevelActor->ActorHasTag(FName("Furniture")))
        {
            return EFilterResult::Include;
        }
        return EFilterResult::Exclude;
    }

    // 只恢复 Transform 属性
    virtual EFilterResult::Type IsPropertyValid(const FIsPropertyValidParams& Params) const override
    {
        // PropertyPath 包含属性路径信息
        if (Params.PropertyPath.Num() > 0 && Params.PropertyPath[0] == TEXT("RootComponent"))
        {
            return EFilterResult::Include;
        }
        return EFilterResult::DoNotCare;
    }
};
```

### 进阶用法

使用 `ULambdaFilter` 快速定义临时过滤逻辑：

```cpp
#include "LambdaFilter.h"

void ApplySnapshotWithCustomFilter()
{
    // 使用 Lambda 快速创建过滤器
    ULambdaFilter* Filter = ULambdaFilter::Create(
        // IsActorValid: 只处理 StaticMeshActor
        [](const FIsActorValidParams& Params) -> EFilterResult::Type
        {
            if (Params.LevelActor && Params.LevelActor->IsA<AStaticMeshActor>())
            {
                return EFilterResult::Include;
            }
            return EFilterResult::Exclude;
        },
        // IsPropertyValid: 默认包含所有属性
        [](const FIsPropertyValidParams& Params) -> EFilterResult::Type
        {
            return EFilterResult::Include;
        },
        // IsDeletedActorValid: 不关心已删除的 Actor
        [](const FIsDeletedActorValidParams& Params) -> EFilterResult::Type
        {
            return EFilterResult::DoNotCare;
        },
        // IsAddedActorValid: 不关心新增的 Actor
        [](const FIsAddedActorValidParams& Params) -> EFilterResult::Type
        {
            return EFilterResult::DoNotCare;
        }
    );

    // 使用 Filter 应用快照...
}
```

使用 `UAndFilter` / `UOrFilter` 组合多个过滤器：

```cpp
#include "Builtin/BlueprintOnly/AndFilter.h"
#include "Builtin/BlueprintOnly/OrFilter.h"
#include "Builtin/ActorHasTagFilter.h"
#include "Builtin/PropertyHasNameFilter.h"

void CreateComplexFilter()
{
    UAndFilter* RootFilter = NewObject<UAndFilter>();

    // 添加 Actor 标签过滤器
    UActorHasTagFilter* TagFilter = NewObject<UActorHasTagFilter>();
    RootFilter->AddChild(TagFilter);

    // 添加属性名称过滤器
    UPropertyHasNameFilter* NameFilter = NewObject<UPropertyHasNameFilter>();
    RootFilter->AddChild(NameFilter);

    // 使用 RootFilter...
}
```

## Demo 示例

```cpp
// MySnapshotFilter.h
#pragma once

#include "CoreMinimal.h"
#include "LevelSnapshotFilters.h"
#include "MySnapshotFilter.generated.h"

/**
 * 自定义快照过滤器：只恢复带有 "RestoreMe" 标签的 Actor 的位置属性
 */
UCLASS(BlueprintType)
class MYPROJECT_API UMySnapshotFilter : public ULevelSnapshotFilter
{
    GENERATED_BODY()

public:
    UMySnapshotFilter();

    virtual EFilterResult::Type IsActorValid(const FIsActorValidParams& Params) const override;
    virtual EFilterResult::Type IsPropertyValid(const FIsPropertyValidParams& Params) const override;
    virtual EFilterResult::Type IsDeletedActorValid(const FIsDeletedActorValidParams& Params) const override;
    virtual EFilterResult::Type IsAddedActorValid(const FIsAddedActorValidParams& Params) const override;

private:
    UPROPERTY(EditAnywhere, Category = "Config")
    FName RequiredTag;
};
```

```cpp
// MySnapshotFilter.cpp
#include "MySnapshotFilter.h"

UMySnapshotFilter::UMySnapshotFilter()
    : RequiredTag(FName("RestoreMe"))
{
}

EFilterResult::Type UMySnapshotFilter::IsActorValid(const FIsActorValidParams& Params) const
{
    if (!Params.LevelActor)
    {
        return EFilterResult::Exclude;
    }

    // 只处理带有指定标签的 Actor
    if (Params.LevelActor->ActorHasTag(RequiredTag))
    {
        return EFilterResult::Include;
    }

    return EFilterResult::Exclude;
}

EFilterResult::Type UMySnapshotFilter::IsPropertyValid(const FIsPropertyValidParams& Params) const
{
    // 只恢复 RootComponent 下的属性（通常是 Transform）
    if (Params.PropertyPath.Num() > 0 && Params.PropertyPath[0] == TEXT("RootComponent"))
    {
        return EFilterResult::Include;
    }

    return EFilterResult::DoNotCare;
}

EFilterResult::Type UMySnapshotFilter::IsDeletedActorValid(const FIsDeletedActorValidParams& Params) const
{
    // 不恢复已删除的 Actor
    return EFilterResult::Exclude;
}

EFilterResult::Type UMySnapshotFilter::IsAddedActorValid(const FIsAddedActorValidParams& Params) const
{
    // 不移除新增的 Actor
    return EFilterResult::Exclude;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `FoliageEdit` | FoliageSupport 模块依赖，用于植被系统快照支持 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

```
- a5fc97ba8900 LevelSnapshots: FilterByClass now also works in add/delete actors, not just modify.
- 0479ec364dfc LevelSnapshots: Fixed BP function not being static.
- d5a5a356b9d3 Remove unnecessary Public and Private entries for the current module being added to PublicIncludePaths or PrivateIncludePaths
```

### 维护评价

- **创建时间**：2021-02-03，约 4 年历史
- **维护状态**：活跃维护中，近期有功能性更新（FilterByClass 扩展到 add/delete actors）和 bug 修复
- **实验性标记**：`IsBetaVersion = true`，`EnabledByDefault = false`，表明 Epic 仍将其视为实验性功能
- **已知限制**：
  - 所有模块均为 `UncookedOnly` 类型，仅在编辑器中可用，打包后不可用
  - nDisplaySupport 仅支持 Win64 和 Linux 平台
  - 仍处于 Beta 阶段，API 可能发生变化
- **推荐程度**：适合在虚拟制片项目中使用，但需注意 Beta 状态，建议在生产环境中做好备份

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/LevelSnapshots)
- [LevelSnapshotFilters 源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/LevelSnapshots/Source/LevelShapshotFilters)