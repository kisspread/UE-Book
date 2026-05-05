# InstancedActors

> （.uplugin Description 为空，无官方描述）

| 属性 | 值 |
|---|---|
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容插件资产） |
| 模块 | `InstancedActors` (Runtime), `InstancedActorsTestSuite` (UncookedOnly), `InstancedActorsEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-10 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/InstancedActors) | |

## 用途

InstancedActors 是一个基于 **Mass Entity Framework** 的大规模静态物体实例化系统。它的核心目标是：将世界中大量重复出现的 Actor（树木、岩石、草地、建筑装饰物等）从传统的独立 Actor 转换为轻量级的 Mass Entity，从而实现极高数量级的渲染与逻辑管理。

系统的工作原理分为三个阶段：

1. **离线烘焙阶段**：在编辑器中，使用 `UInstancedActorsSubsystem::InstanceActor` 将 Actor 转换为实例数据（`UInstancedActorsData`），存储在空间分区的 `AInstancedActorsManager` 中。实例的 Transform 以离线方式填充，确保客户端和服务端使用完全相同的稳定索引。
2. **Mass Entity 运行时**：游戏启动后，Manager 将所有实例转换为 Mass Entity，利用 Mass 框架的 ECS 架构进行高效的 LOD 管理、批量渲染（通过 ISMC）和逻辑处理。
3. **按需 Actor 水合（Hydration）**：当玩家靠近某个实例时，系统可以将 Mass Entity "水合"为真实的 Actor 实例（服务端权威），实现物理交互、蓝图逻辑等。远离时再"脱水"回 Mass Entity。

这个插件依赖 **MassGameplay**（Mass 实体框架）、**DataRegistry**（数据注册表，用于 per-class 设置）和 **GameFeatures**（游戏特性系统集成）。

## 使用场景

- 你的世界有成千上万棵树、岩石、灌木等静态装饰物 → 用 InstancedActors 替代独立 Actor，获得 Mass ECS 的批量处理性能优势
- 你需要远处的物体以 ISMC 渲染，近处才生成真实 Actor 进行交互 → InstancedActors 的 Bulk LOD + 水合机制自动处理这个过渡
- 你需要对大面积区域的实例进行批量修改（如清除某区域的树木）→ 使用 ModifierVolume 系统
- 你在做多人游戏，需要客户端/服务端对实例状态保持同步 → 内置的 `FInstancedActorsDeltaList` + FastArray 复制机制处理破坏、生命周期等增量同步
- 你需要实例的持久化存储（如被砍掉的树不再重生）→ 内置 SaveGame 序列化支持

## 架构概览

```
UInstancedActorsSubsystem (世界子系统，管理所有 Manager)
    └── AInstancedActorsManager (空间分区 Actor，每格一个)
            └── UInstancedActorsData (每个 ActorClass 一份实例数据)
                    ├── InstanceTransforms[] (离线烘焙的 Transform 数组)
                    ├── Entities[] (运行时 Mass Entity Handle)
                    └── InstanceVisualizations[] (ISMC 可视化集合)
```

### 核心类关系

| 类 | 职责 |
|---|---|
| `UInstancedActorsSubsystem` | 世界子系统，管理所有 Manager 的注册、空间索引、延迟实体生成、设置编译 |
| `AInstancedActorsManager` | 继承 `APartitionActor`，按空间网格分区管理实例，负责实体生成/销毁、序列化、迭代 |
| `UInstancedActorsData` | 每个 ActorClass 的实例数据容器，管理 Transform 列表、Mass Entity 模板、可视化、Delta 同步 |
| `UInstancedActorsComponent` | 添加到被水合的 Actor 上，提供 Mass Entity 引用和 Fragment 操作接口 |
| `FInstancedActorsInstanceHandle` | 实例句柄，包含 `UInstancedActorsData` 引用 + `FInstancedActorsInstanceIndex` |
| `FInstancedActorsInstanceIndex` | 稳定的实例索引（uint16），客户端/服务端一致 |
| `FInstancedActorsManagerHandle` | Manager 句柄，用于空间索引查找 |

### Bulk LOD 系统

实例使用批量 LOD（`EInstancedActorsBulkLOD`）来控制整体表现：

| LOD 级别 | 说明 |
|---|---|
| `Detailed` | Mass 对每个实体单独计算 LOD，可产生 Actor（水合） |
| `Medium` | 批量渲染，使用较低质量的 ISMC |
| `Low` | 最低质量渲染 |
| `Off` | 完全不渲染 |

LOD 切换由 `UInstancedActorsStationaryLODBatchProcessor` 处理，根据距离和 `FInstancedActorsSettings` 中的阈值进行批量切换。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `InstanceActor` | 将 ActorClass 的实例添加到指定位置的 Manager | `UInstancedActorsSubsystem` |
| `RemoveActorInstance` | 移除指定实例（加入 FreeList） | `UInstancedActorsSubsystem` |
| `HasMassEntity` | 检查 Actor 是否由 InstancedActors 系统生成 | `UInstancedActorsComponent` |
| `GetManager` | 获取实例所属的 Manager | `UInstancedActorsData` |

### 设置配置

InstancedActors 的运行时行为通过 `FInstancedActorsSettings` 控制，支持多层覆盖：

1. 默认构造的 `FInstancedActorsSettings`
2. `DefaultBaseSettingsName`（命名基础设置）
3. ActorClass 继承链上的 `BaseSettings[]` + `OverrideSettings`
4. `EnforcedSettingsName`（强制覆盖设置）

关键设置项：

| 设置 | 类型 | 说明 |
|---|---|---|
| `MaxActorDistance` | double | 距玩家多近才生成真实 Actor（默认 1000 cm） |
| `MaxInstanceDistances` | TArray\<double\> | 按质量级别的最大绘制距离 |
| `LODDistanceScales` | TArray\<float\> | 按质量级别的 LOD 距离缩放 |
| `DetailedRepresentationLODDistance` | double | Detailed LOD 距离阈值（默认 7000 cm） |
| `ForceLowRepresentationLODDistance` | double | 强制 Low LOD 距离阈值（默认 27500 cm） |
| `bEjectOnActorMoved` | bool | Actor 被移动后是否弹出管理器 |
| `ActorEjectionMovementThreshold` | float | 弹出的移动阈值 |
| `bCanBeDamaged` | bool | 是否可被伤害 |
| `bIgnoreModifierVolumes` | bool | 是否忽略修改器体积 |
| `ScaleEntityCount` | float | 实体数量缩放（0.0-1.0） |

## C++ 用法

### 头文件引入

```cpp
#include "InstancedActorsSubsystem.h"
#include "InstancedActorsManager.h"
#include "InstancedActorsData.h"
#include "InstancedActorsComponent.h"
#include "InstancedActorsTypes.h"
```

### 基本用法：查询实例

```cpp
// 获取子系统
UInstancedActorsSubsystem* IASubsystem = UInstancedActorsSubsystem::Get(GetWorld());

// 查询指定区域内是否有某类型的实例
FBox QueryBounds = FBox(ActorLocation - FVector(1000), ActorLocation + FVector(1000));
bool bHasInstances = IASubsystem->HasInstancesOfClass(
    QueryBounds,
    ATreeActor::StaticClass(),
    /*bTestActorsIfSpawned=*/false,
    EInstancedActorsBulkLODMask::All
);

// 遍历区域内所有实例
IASubsystem->ForEachInstance(QueryBounds,
    [](const FInstancedActorsInstanceHandle& Handle, const FTransform& Transform, FInstancedActorsIterationContext& Context) -> bool
    {
        // 返回 true 继续迭代，返回 false 中断
        UE_LOG(LogTemp, Log, TEXT("Instance at %s"), *Transform.GetLocation().ToString());
        return true;
    }
);
```

> 来源：`Source/InstancedActors/Public/InstancedActorsSubsystem.h`

### 编辑器用法：实例化 Actor

```cpp
#if WITH_EDITOR
// 将一个 Actor 类型添加为实例
FInstancedActorsInstanceHandle Handle = IASubsystem->InstanceActor(
    ATreeActor::StaticClass(),
    FTransform(FRotator::ZeroRotator, SpawnLocation, FVector::OneVector),
    Level,
    FGameplayTagContainer()  // 可选附加标签
);

// 移除实例
IASubsystem->RemoveActorInstance(Handle, /*bDestroyManagerIfEmpty=*/true);
#endif
```

> 来源：`Source/InstancedActors/Public/InstancedActorsSubsystem.h`

### 进阶用法：UInstancedActorsComponent 与 Mass Entity 交互

当 Actor 被 InstancedActors 系统水合生成后，它会自动获得 `UInstancedActorsComponent`。通过该组件可以操作关联的 Mass Entity：

```cpp
// 在 Actor 中获取组件
UInstancedActorsComponent* IAComp = FindComponentByClass<UInstancedActorsComponent>();
if (IAComp && IAComp->HasMassEntity())
{
    // 添加自定义 Fragment
    IAComp->AddFragmentDeferred<FMyCustomFragment>();

    // 添加或更新 Fragment 并请求持久化保存
    IAComp->AddOrUpdatePersistentFragmentsDeferred(FMyCustomFragment{Value});

    // 读取 Fragment（注意线程安全）
    if (const FMyCustomFragment* Frag = IAComp->GetVolatileFragment<FMyCustomFragment>())
    {
        // 使用 Frag->...
    }

    // 移除 Fragment
    IAComp->RemoveFragmentDeferred<FMyCustomFragment>();
}
```

> 来源：`Source/InstancedActors/Public/InstancedActorsComponent.h`

### 进阶用法：Modifier Volume

使用修改器体积在运行时批量影响区域内的实例：

```cpp
// 创建一个修改器体积 Actor（蓝图中放置 AInstancedActorsRemovalModifierVolume）
// 或者在 C++ 中自定义 Modifier：

// 继承 UInstancedActorsModifierBase
class UMyCustomModifier : public UInstancedActorsModifierBase
{
    GENERATED_BODY()
public:
    UMyCustomModifier() { bRequiresSpawnedEntities = false; } // 可在实体生成前运行

    virtual bool ModifyInstance(
        const FInstancedActorsInstanceHandle& InstanceHandle,
        const FTransform& InstanceTransform,
        FInstancedActorsIterationContext& IterationContext) override
    {
        // 修改实例，返回 true 继续，false 中断
        IterationContext.RuntimeRemoveInstance(InstanceHandle);
        return true;
    }
};
```

> 来源：`Source/InstancedActors/Public/InstancedActorsModifiers.h`

### 进阶用法：可视化切换

实例支持多个可视化方案之间切换（例如"有果实"和"无果实"的树）：

```cpp
// 注册额外的可视化
FInstancedActorsVisualizationDesc AltVisDesc;
// ... 配置 AltVisDesc 的 ISMComponentDescriptors ...
uint8 AltVisIndex = InstanceData->AddVisualization(AltVisDesc);

// 切换某个实例的可视化
InstanceData->SwitchInstanceVisualization(InstanceIndex, AltVisIndex);
```

> 来源：`Source/InstancedActors/Public/InstancedActorsData.h`

## Demo 示例

### 自定义 InstancedActorsComponent 子类

以下示例展示如何创建一个自定义组件，在实例被水合时为其 Mass Entity 添加自定义数据：

**MyInstancedActorComponent.h**
```cpp
#pragma once

#include "InstancedActorsComponent.h"
#include "MyInstancedActorComponent.generated.h"

// 自定义 Fragment
USTRUCT()
struct FTreeHealthFragment : public FMassFragment
{
    GENERATED_BODY()
    float Health = 100.f;
};

UCLASS(ClassGroup="Instanced Actors", Meta=(BlueprintSpawnableComponent))
class MYGAME_API UMyInstancedActorComponent : public UInstancedActorsComponent
{
    GENERATED_BODY()

public:
    // 在实体模板创建时添加自定义 Fragment
    virtual void ModifyMassEntityTemplate(
        FMassEntityManager& InMassEntityManager,
        UInstancedActorsData* InstancedActorData,
        FMassEntityTemplateData& InOutMassEntityTemplateData) const override
    {
        InOutMassEntityTemplateData.AddFragment<FTreeHealthFragment>();
    }

    // 支持持久化
    virtual uint32 GetInstancePersistenceDataID() const override { return 0x54524545; /* 'TREE' */ }
    virtual bool ShouldSerializeInstancePersistenceData(const FArchive& Archive, UInstancedActorsData* InstanceData, int64 TimeDelta) const override { return true; }
    virtual void SerializeInstancePersistenceData(FStructuredArchive::FRecord Record, UInstancedActorsData* InstanceData, int64 TimeDelta) const override
    {
        // 保存/加载自定义数据
    }
};
```

**Build.cs 依赖**
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "InstancedActors",
    "MassEntity"
});
```

## 模块依赖

`InstancedActors.Build.cs` 中的 `PublicDependencyModuleNames`：

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `GameplayTags` | Gameplay Tag 系统，用于实例分类和 Modifier 过滤 |
| `MassEntity` | Mass Entity 框架核心 |
| `MassCommon` | Mass 通用类型 |
| `MassActors` | Mass Actor 水合/生成 |
| `MassRepresentation` | Mass 表示系统（ISMC/Actor 切换） |
| `MassSpawner` | Mass 实体生成 |
| `MassLOD` | Mass LOD 管理 |
| `MassSmartObjects` | Mass Smart Object 集成 |
| `MassSignals` | Mass 信号系统 |
| `DataRegistry` | 数据注册表，用于 per-class 设置查找 |
| `DeveloperSettings` | 开发者设置基类 |
| `NetCore` | 网络核心（FastArray 序列化） |
| `GameFeatures` | 游戏特性系统（GameFeatureAction 集成） |

编辑器额外依赖：`UnrealEd`、`InputCore`、`MassGameplayDebug`（非 Shipping 配置）

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-10-17 | `2322b67b3f51` | 修复 RemoveVisualization() 时未正确销毁实体模板的问题。实体模板中的 VisualizationTrait 将 StaticMeshDescHandle 视为不可变，移除可视化时需要重建模板 |
| 2025-10-08 | `f3b9f9a38991` | 撤销 Fortnite Release-38.00 分支的变更 |
| 2025-10-08 | `7953886d2f83` | 新增标志位处理子系统切换时的实体销毁时序问题。当新的游戏模式特定子系统创建时，IAM 会被切换，新代码防止批量 LOD 处理器在旧子系统已失效时执行检查 |

### 维护评价

- **创建时间**：2024 年 1 月，约 2 年历史
- **实验性状态**：`IsExperimentalVersion=true`，`EnabledByDefault=false`，需手动启用
- **活跃程度**：2025 年 10 月仍有实质性更新（Bug 修复和时序问题处理），属于**活跃维护**
- **已知限制**：
  - 实验性插件，API 可能在未来版本中发生变化
  - 实例索引使用 uint16，单个 Manager 中每个 ActorClass 最多 65534 个实例
  - 测试用例文件（`InstancedActorsTest.cpp`）基本为空，缺乏自动化测试覆盖
- **推荐**：如果你的项目需要大规模静态物体管理且已经使用或计划使用 Mass 框架，强烈推荐。否则需要评估引入 Mass 依赖的成本

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/InstancedActors)
- 官方文档：无（.uplugin DocsURL 为空）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/InstancedActors/Source/InstancedActorsTestSuite)（基本为空）
