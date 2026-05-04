# Level Snapshots

> 

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `LevelSnapshots` (UncookedOnly), `LevelSnapshotFilters` (UncookedOnly), `LevelSnapshotsEditor` (UncookedOnly), `FoliageSupport` (UncookedOnly), `nDisplaySupport` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-02-03 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/LevelSnapshots) | |

## 用途

Level Snapshots 是一个关卡状态快照系统，用于在编辑器中捕获关卡的完整状态并有选择地恢复。它解决的核心问题是：**在虚拟制片等复杂工作流中，关卡会经历大量修改，需要一种机制来保存"检查点"并在之后选择性地回滚特定属性**。

与 UE 内置的撤销系统不同，Level Snapshots：
- 将状态持久化到磁盘资产（`ULevelSnapshot`），跨会话可用
- 使用哈希（CRC32/MD5）快速检测 Actor 是否变化，避免不必要的加载
- 只序列化与 CDO（类默认对象）不同的属性，大幅节省空间
- 支持 Oodle 压缩，进一步减小文件体积
- 提供精细的过滤系统，允许用户选择性恢复特定属性
- 支持自定义序列化器处理非标准子对象（如 Foliage、nDisplay）

## 使用场景

- 你在虚拟制片中需要保存关卡的"黄金状态"，以便在实验性修改后快速回滚 → 用 Level Snapshots 拍摄快照
- 你需要对比当前关卡与某个历史版本的差异，但只想恢复部分 Actor 的部分属性 → 用过滤系统选择性应用
- 你的 Actor 包含自定义子对象（非标准 UPROPERTY 暴露的），需要正确快照和恢复 → 实现 `ICustomObjectSnapshotSerializer`
- 你需要在快照拍摄/应用前后执行自定义逻辑（如清理临时数据） → 实现 `IRestorationListener` 或 `ITakeSnapshotListener`
- 你需要控制哪些 Actor/Component 参与快照 → 实现 `ISnapshotRestorabilityOverrider` 或 `IActorSnapshotFilter`

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `TakeLevelSnapshot` | 拍摄当前世界的快照，返回 `ULevelSnapshot` 资产 | `ULevelSnapshotsFunctionLibrary` |
| `ApplySnapshotToWorld` | 将快照应用到世界，可选传入过滤器 | `ULevelSnapshotsFunctionLibrary` |
| `DiffAndFilterSnapshot` | 对比快照与当前世界，返回通过过滤器的变更集 | `ULevelSnapshotsFilteringLibrary` |
| `SetSnapshotName` | 设置快照名称 | `ULevelSnapshot` |
| `SetSnapshotDescription` | 设置快照描述 | `ULevelSnapshot` |
| `GetMapPath` | 获取快照对应的关卡路径 | `ULevelSnapshot` |
| `GetCaptureTime` | 获取快照拍摄时间 | `ULevelSnapshot` |
| `GetSnapshotName` | 获取快照名称 | `ULevelSnapshot` |
| `GetSnapshotDescription` | 获取快照描述 | `ULevelSnapshot` |

### 事件委托（蓝图可绑定）

| 事件 | 说明 | 所在类 |
|---|---|---|
| `OnPreTakeSnapshot` | 快照拍摄前触发 | `ULevelSnapshotsEngineSubsystem` |
| `OnPostTakeSnapshot` | 快照拍摄后触发 | `ULevelSnapshotsEngineSubsystem` |
| `OnPreApplySnapshot` | 快照应用前触发 | `ULevelSnapshotsEngineSubsystem` |
| `OnPostApplySnapshot` | 快照应用后触发 | `ULevelSnapshotsEngineSubsystem` |

### 使用示例（蓝图描述）

**拍摄并应用快照：**

1. 获取当前 World Context → 调用 `TakeLevelSnapshot`，传入名称和描述 → 获得 `ULevelSnapshot` 引用
2. 对关卡进行修改
3. 调用 `ApplySnapshotToWorld`，传入之前获得的快照对象 → 关卡恢复到快照状态

**带过滤器的选择性恢复：**

1. 拍摄快照后修改关卡
2. 调用 `DiffAndFilterSnapshot`，传入 World、Snapshot 和自定义 Filter → 获得 `FPropertySelectionMap`
3. 将 `FPropertySelectionMap` 传给 `ApplySnapshotToWorld` → 只恢复选中的属性

**监听快照事件：**

1. 获取 `ULevelSnapshotsEngineSubsystem`（通过 `GetEngineSubsystem`）
2. 绑定 `OnPreApplySnapshot` / `OnPostApplySnapshot` 委托
3. 在委托中执行自定义逻辑（如清理临时数据、记录日志等）

## C++ 用法

### 头文件引入

```cpp
#include "ILevelSnapshotsModule.h"
#include "LevelSnapshot.h"
#include "LevelSnapshotsFunctionLibrary.h"
#include "Filtering/PropertySelectionMap.h"
```

### 基本用法：拍摄和应用快照

```cpp
// 来源: LevelSnapshotsFunctionLibrary.h

#include "ILevelSnapshotsModule.h"
#include "LevelSnapshot.h"
#include "LevelSnapshotsFunctionLibrary.h"

// 拍摄快照
ULevelSnapshot* Snapshot = ULevelSnapshotsFunctionLibrary::TakeLevelSnapshot(
    WorldContextObject,
    FName("MySnapshot"),
    TEXT("Before lighting changes")
);

// 应用快照（无过滤器，恢复全部）
ULevelSnapshotsFunctionLibrary::ApplySnapshotToWorld(
    WorldContextObject,
    Snapshot,
    nullptr  // 无过滤器 = 恢复全部
);
```

### 进阶用法：注册自定义属性比较器

```cpp
// 来源: IPropertyComparer.h, ILevelSnapshotsModule.h

#include "ILevelSnapshotsModule.h"
#include "Restorability/Interfaces/IPropertyComparer.h"

class FMyPropertyComparer : public UE::LevelSnapshots::IPropertyComparer
{
public:
    virtual EPropertyComparison ShouldConsiderPropertyEqual(
        const UE::LevelSnapshots::FPropertyComparisonParams& Params) const override
    {
        // 自定义逻辑：例如忽略某些被其他属性控制的属性
        if (Params.LeafProperty->GetName() == TEXT("bSomeDependentProperty"))
        {
            return EPropertyComparison::TreatEqual;
        }
        return EPropertyComparison::CheckNormally;
    }
};

// 注册
auto& Module = UE::LevelSnapshots::ILevelSnapshotsModule::Get();
Module.RegisterPropertyComparer(
    UMyActor::StaticClass(),
    MakeShared<FMyPropertyComparer>()
);
```

### 进阶用法：注册自定义子对象序列化器

```cpp
// 来源: ICustomObjectSnapshotSerializer.h, ILevelSnapshotsModule.h

#include "ILevelSnapshots.h"
#include "Restorability/Interfaces/ICustomObjectSnapshotSerializer.h"

class FMyCustomSerializer : public UE::LevelSnapshots::ICustomObjectSnapshotSerializer
{
public:
    virtual void OnTakeSnapshot(UObject* EditorObject,
        UE::LevelSnapshots::ICustomSnapshotSerializationData& DataStorage) override
    {
        // 保存自定义子对象
        UMyObject* MyObj = Cast<UMyObject>(EditorObject);
        if (UObject* SubObj = MyObj->GetCustomSubobject())
        {
            DataStorage.AddSubobjectSnapshot(SubObj);
        }
    }

    virtual UObject* FindOrRecreateSubobjectInSnapshotWorld(
        UObject* SnapshotObject,
        const UE::LevelSnapshots::ISnapshotSubobjectMetaData& ObjectData,
        const UE::LevelSnapshots::ICustomSnapshotSerializationData& DataStorage) override
    {
        // 在快照世界中查找或重建子对象
        return FindOrCreateEquivalentSubobject(SnapshotObject);
    }

    virtual UObject* FindOrRecreateSubobjectInEditorWorld(
        UObject* EditorObject,
        const UE::LevelSnapshots::ISnapshotSubobjectMetaData& ObjectData,
        const UE::LevelSnapshots::ICustomSnapshotSerializationData& DataStorage) override
    {
        // 在编辑器世界中查找或重建子对象
        return FindOrCreateEquivalentSubobject(EditorObject);
    }
};

// 注册（仅限原生类）
Module.RegisterCustomObjectSerializer(
    UMyObject::StaticClass(),
    MakeShared<FMyCustomSerializer>(),
    true  // 包含蓝图子类
);
```

### 进阶用法：注册全局 Actor 过滤器

```cpp
// 来源: IActorSnapshotFilter.h, ILevelSnapshotsModule.h

#include "ILevelSnapshotsModule.h"
#include "Restorability/Interfaces/IActorSnapshotFilter.h"

class FMyActorFilter : public UE::LevelSnapshots::IActorSnapshotFilter
{
public:
    virtual FFilterResultData CanModifyMatchedActor(
        const UE::LevelSnapshots::FCanModifyMatchedActorParams& Params) override
    {
        // 不允许修改世界设置 Actor
        if (Params.MatchedEditorWorldActor->IsA<AWorldSettings>())
        {
            return FFilterResultData(
                EFilterResult::Disallow,
                NSLOCTEXT("MyFilter", "NoWorldSettings", "World Settings cannot be restored")
            );
        }
        return EFilterResult::DoNotCare;
    }

    virtual FFilterResultData CanDeleteNewActor(const AActor* EditorActor) override
    {
        // 不允许删除玩家出生点
        if (EditorActor->IsA<APlayerStart>())
        {
            return FFilterResultData(EFilterResult::Disallow);
        }
        return EFilterResult::DoNotCare;
    }
};

Module.RegisterGlobalActorFilter(MakeShared<FMyActorFilter>());
```

### 进阶用法：监听快照生命周期

```cpp
// 来源: IRestorationListener.h, ITakeSnapshotListener.h

#include "Interfaces/IRestorationListener.h"
#include "Interfaces/ITakeSnapshotListener.h"

class FMyListener : public UE::LevelSnapshots::IRestorationListener,
                    public UE::LevelSnapshots::ITakeSnapshotListener
{
public:
    // 快照拍摄回调
    virtual void PreTakeSnapshot(
        const UE::LevelSnapshots::FPreTakeSnapshotEventData& Params) override
    {
        UE_LOG(LogLevelSnapshots, Log, TEXT("About to take snapshot for world: %s"),
            *Params.World->GetName());
    }

    // 快照应用回调
    virtual void PreApplySnapshot(
        const UE::LevelSnapshots::FPreApplySnapshotEventData& Params) override
    {
        // 在应用前清理临时数据
    }

    virtual void PostApplySnapshot(
        const UE::LevelSnapshots::FPostApplySnapshotEventData& Params) override
    {
        // 在应用后重建缓存
    }
};
```

## Demo 示例

### 自定义属性比较器（完整示例）

```cpp
// MyPropertyComparer.h
#pragma once

#include "Restorability/Interfaces/IPropertyComparer.h"

class FIgnoreTransientPropertyComparer : public UE::LevelSnapshots::IPropertyComparer
{
public:
    virtual EPropertyComparison ShouldConsiderPropertyEqual(
        const UE::LevelSnapshots::FPropertyComparisonParams& Params) const override;
};
```

```cpp
// MyPropertyComparer.cpp
#include "MyPropertyComparer.h"
#include "PropertyInfoHelpers.h"

using namespace UE::LevelSnapshots;

IPropertyComparer::EPropertyComparison FIgnoreTransientPropertyComparer::ShouldConsiderPropertyEqual(
    const FPropertyComparisonParams& Params) const
{
    // 忽略标记为 Transient 的属性
    if (Params.LealProperty && Params.LeafProperty->HasAnyPropertyFlags(CPF_Transient))
    {
        return EPropertyComparison::TreatEqual;
    }

    // 对浮点属性使用自定义精度
    const FNumericProperty* NumericProp = CastField<FNumericProperty>(Params.LeafProperty);
    if (NumericProp)
    {
        if (AreNumericPropertiesNearlyEqual(NumericProp, 
            Params.SnapshotContainer, Params.WorldContainer))
        {
            return EPropertyComparison::TreatEqual;
        }
    }

    return EPropertyComparison::CheckNormally;
}
```

```cpp
// 注册（在模块 StartupModule 中）
#include "ILevelSnapshotsModule.h"

void FMyGameModule::StartupModule()
{
    if (UE::LevelSnapshots::ILevelSnapshotsModule::IsAvailable())
    {
        auto& LSModule = UE::LevelSnapshots::ILevelSnapshotsModule::Get();
        LSModule.RegisterPropertyComparer(
            AActor::StaticClass(),
            MakeShared<FIgnoreTransientPropertyComparer>()
        );
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `FoliageEdit` | FoliageSupport 模块依赖，用于支持 Foliage Actor 的快照和恢复 |
| `nDisplay` | nDisplaySupport 模块依赖，用于支持 nDisplay 集群的快照和恢复 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

```
- bbc2d3772a2e Level Snapshots: Fix crash when deciding whether a property should be saved, if the property non-reflected.
- 09f88d4925c2 Cloth - Added support for the Cloth/Outfit Asset to the SkeletalMesh clothing data, and multi-simulation support to the SkeletalMeshComponent.
- 80b5e5f89274 [Core] Cleanup bad usage of begin/end on tset
```

### 维护评价

- **创建时间**：2021-02-03，约 4 年历史
- **Beta 状态**：`IsBetaVersion=true`，仍处于 Beta 阶段
- **默认未启用**：`EnabledByDefault=false`，需要手动在插件列表中启用
- **模块类型**：所有模块均为 `UncookedOnly`，仅在编辑器中可用，不会打包到发布版本
- **近期活动**：有持续的 bug 修复和功能改进
- **已知限制**：
  - 不支持 `Instanced` UPROPERTY 的递归检查
  - 自定义序列化器目前不支持蓝图类（仅限原生类）
  - nDisplaySupport 仅支持 Win64 和 Linux 平台
  - 5.1 版本的 Foliage 数据格式存在已知损坏问题（已在 5.2 修复）

**综合评价**：Level Snapshots 是一个功能完善但仍在 Beta 阶段的虚拟制片工具。它提供了完整的快照拍摄、差异对比和选择性恢复能力，API 设计良好且高度可扩展。由于仍标记为 Beta 且默认未启用，建议在生产环境中谨慎使用，但作为关卡状态管理工具已经相当成熟。**推荐在虚拟制片项目中使用**，但需注意 Beta 状态可能带来的 API 变更风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/LevelSnapshots)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/LevelSnapshots/Tests)