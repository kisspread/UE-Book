# Instanced Actors

> （描述为空）

| 属性 | 值 |
|---|---|
| 中文名 | 实例化演员 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源） |
| 模块 | `InstancedActors` (Runtime), `InstancedActorsEditor` (Editor), `InstancedActorsTestSuite` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-10 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/InstancedActors) | |

## 用途

`InstancedActors` 是一个为超大规模开放世界设计的高性能实体管理系统。它**并非**简单的静态网格实例化工具，而是一个**运行时对象池与动态渲染管理系统**。其核心解决的问题是：在拥有成千上万相似静态物体（如树木、灌木、石头、建筑部件）的庞大开放世界中，如何以极低的CPU和内存开销进行管理、渲染、交互和数据持久化。

它通过以下方式实现：
1.  **离线构建与数据驱动**：在编辑器中（“离线”状态）将Actor的位置等数据预处理并存储在`UInstancedActorsData`中，确保客户端和服务器加载完全相同的稳定数据集。
2.  **Mass ECS集成**：在运行时，利用Mass实体系统来管理这些实例。对于远离玩家的实例，它们仅作为静态网格实例（ISM）进行高效渲染；当玩家靠近时，系统会“水合”（Hydrate）这些实例，将其转换为完全功能的Actor（如可交互、有AI）。
3.  **动态LOD与表示切换**：系统根据距离自动在“详细Actor表示”和“轻量ISM表示”之间无缝切换，并提供多级LOD控制。
4.  **区域化与复制**：通过`AInstancedActorsManager`以World Partition网格单元进行区域化管理，并集成网络复制与数据持久化系统。

## 使用场景

-   你正在开发一个大型开放世界游戏，需要在广阔区域内放置数百万个树木、岩石、植被等静态物体，并需要它们在玩家靠近时能交互（如树木被砍伐、岩石可拾取）。
-   你需要一种高效的方式来管理这些物体的生命周期，包括在客户端/服务器间同步状态变化（如被破坏）、保存与加载游戏进度。
-   你希望利用UE5的Mass实体框架来最大化处理数百万对象时的性能。
-   你需要对实例化物体应用动态修改，例如通过“修改器体积”批量移除某个区域内的树木来为城市建筑腾出空间。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Instance Actor` | 在指定位置创建一个“实例化演员”。如果附近已有`Manager`，则添加实例；否则创建新的`Manager`。这是一个仅编辑器可用的操作。 | `UInstancedActorsSubsystem` |
| `Remove Actor Instance` | 移除一个“实例化演员”。如果这是`Manager`中的最后一个实例，可以选择销毁该`Manager`。 | `UInstancedActorsSubsystem` |
| `Has Mass Entity` | 查询一个Actor是否是由实例化演员系统生成的，并且当前正在使用Mass实体。 | `UInstancedActorsComponent` |

### 使用示例（蓝图描述）

1.  **编辑器实例化**：在编辑器中，通过调用`UInstancedActorsSubsystem::InstanceActor`（或编辑器工具中的类似按钮），为选定的Actor类在场景中的点击位置创建一个实例。这会自动处理`Manager`的创建和数据存储。
2.  **运行时查询**：在运行时，对于任何可能被实例化的Actor，你可以添加一个`UInstancedActorsComponent`。然后，在任何其他逻辑中，使用`Has Mass Entity`节点来检查它当前是否是“轻量”的实例（返回false）还是一个完全“水合”的Actor（返回true）。
3.  **使用修改器体积**：在场景中放置一个`AInstancedActorsRemovalModifierVolume`或包含`UInstancedActorsModifierVolumeComponent`的Actor。在它的`Modifiers`数组中添加`URemoveInstancedActorsModifier`。游戏运行时，该体积内的所有实例化物体将被移除。

## C++ 用法

### 头文件引入

```cpp
#include "InstancedActorsSubsystem.h"
#include "InstancedActorsManager.h"
#include "InstancedActorsComponent.h"
```

### 基本用法

以下示例展示了如何在运行时查询和操作实例化演员系统。
*（来源：`Public/InstancedActorsSubsystem.h`, `Public/InstancedActorsComponent.h`）*

```cpp
// 获取实例化演员子系统
UInstancedActorsSubsystem* IA_Subsystem = UInstancedActorsSubsystem::Get(GetWorld());
if (IA_Subsystem)
{
    // 在一个区域内查询是否存在任何表示特定类的实例化演员
    FBox QueryBounds = FBox(FVector(-1000, -1000, -100), FVector(1000, 1000, 100));
    bool bHasTrees = IA_Subsystem->HasInstancesOfClass(QueryBounds, ATree::StaticClass());
}

// 对于一个已知的、可能由IA系统管理的Actor
if (UInstancedActorsComponent* IAComp = Actor->FindComponentByClass<UInstancedActorsComponent>())
{
    if (IAComp->HasMassEntity())
    {
        // 该Actor当前是Mass实体，可能处于ISM表示状态
        FMassEntityHandle EntityHandle = IAComp->GetMassEntityHandle();
        // 可以进一步操作Mass实体，例如获取其Fragment
        // const FSomeFragment* Frag = IAComp->GetVolatileFragment<FSomeFragment>();
    }
}
```

### 进阶用法

以下示例展示了如何自定义实例化行为，例如为实体添加额外的Mass Fragment。
*（来源：`Public/InstancedActorsComponent.h`中的模板函数）*

```cpp
// 假设我们有一个自定义的Fragment来存储树木的生命值
USTRUCT()
struct FTreeHealthFragment : public FMassFragment
{
    GENERATED_BODY()
    float Health = 100.f;
};

// 在一个由IA系统管理的树木Actor的自定义Component中
void UMyTreeComponent::InitializeComponent()
{
    Super::InitializeComponent();

    // 获取InstancedActorsComponent
    UInstancedActorsComponent* IAComp = GetOwner()->FindComponentByClass<UInstancedActorsComponent>();
    if (IAComp && IAComp->HasMassEntity())
    {
        // 安全地延迟添加自定义Fragment到该实体的Mass数据中
        IAComp->AddFragmentDeferred<FTreeHealthFragment>();

        // 或者，添加一个需要更新并持久化的Fragment
        // FTreeHealthFragment NewFrag;
        // NewFrag.Health = 50.f;
        // IAComp->AddOrUpdatePersistentFragmentsDeferred(NewFrag);
    }
}
```

## Demo 示例

一个最小的自定义组件示例，演示了如何与实例化演员的Mass实体交互。
*（注意：此示例假设已正确设置项目依赖，并且组件被添加到了一个将被实例化的Actor类上）*

```cpp
// MyTreeComponent.h
#pragma once
#include "Components/ActorComponent.h"
#include "InstancedActorsComponent.h" // 假设IA插件已启用
#include "MyTreeComponent.generated.h"

USTRUCT(BlueprintType)
struct FTreeDataFragment : public FMassFragment
{
    GENERATED_BODY()

    UPROPERTY()
    float GrowthStage = 0.f;
};

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYGAME_API UMyTreeComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyTreeComponent();

protected:
    virtual void InitializeComponent() override;
    virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;
};
```

```cpp
// MyTreeComponent.cpp
#include "MyTreeComponent.h"
#include "MassEntityHandle.h"
#include "MassEntityManager.h"

UMyTreeComponent::UMyTreeComponent()
{
    PrimaryComponentTick.bCanEverTick = true;
}

void UMyTreeComponent::InitializeComponent()
{
    Super::InitializeComponent();

    // 尝试在初始化时将自定义数据片段添加到关联的Mass实体
    if (UInstancedActorsComponent* IAComp = GetOwner()->FindComponentByClass<UInstancedActorsComponent>())
    {
        if (IAComp->HasMassEntity())
        {
            IAComp->AddFragmentDeferred<FTreeDataFragment>();
        }
    }
}

void UMyTreeComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    // 读取自定义数据片段（注意线程安全）
    if (UInstancedActorsComponent* IAComp = GetOwner()->FindComponentByClass<UInstancedActorsComponent>())
    {
        if (const FTreeDataFragment* TreeData = IAComp->GetVolatileFragment<FTreeDataFragment>())
        {
            // 使用 TreeData->GrowthStage 来驱动视觉效果等
            // 注意：Mass实体可能正在并行处理，直接读取时需要确保数据安全（或仅在游戏线程处理的片段）
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MassGameplay` | 本插件的核心基础，用于实体的管理和更新 |
| `DataRegistry` | 用于查找和应用按类别的实例化设置（`FInstancedActorsClassSettingsBase`） |
| `GameFeatures` | 用于实现 `UGameFeatureAction_ConfigureInstancedActors`，支持在GFA中配置覆盖设置 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `16c20541` | Update Intel OneAPI supported version to 2026.0.0 | 更新Intel编译器支持版本。 |
| 2026-05-12 | `865421ee` | [Mass] PR #12790: InstancedActors: Use Correct Collision CVar In All Net Modes | 修复了在所有网络模式下碰撞CVar使用不正确的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从`UE_LOG`迁移到`UE_LOGF`。 |
| 2026-04-01 | `58888966` | [MassCore] Move headers to Public/Mass/ subdirectory, strip Mass prefix from filenames | 重构了Mass核心模块的头文件结构。 |
| 2026-03-30 | `161605b0` | [Mass] Extract MassCore module from MassEntity | 从MassEntity中提取出MassCore模块。 |

### 维护评价

`InstancedActors`插件标记为**实验性**（`IsExperimentalVersion=true`）且**默认未启用**。它创建于2024年初，距今约2.5年，属于相对较新的技术。

**近期更新分析**：最近的提交主要集中在**底层重构和编译修复**上（如Mass模块结构调整、日志宏迁移），而非功能性的重大更新。这表明该插件可能处于一个相对稳定的“等待成熟”阶段，或者正在等待上游Mass框架的进一步稳定。

**综合评价**：
- **活跃度**：维护不活跃。过去6个月内的更新均为基础性维护，无新功能添加。
- **成熟度**：实验性。虽然架构设计先进，但作为大规模开放世界的解决方案，其稳定性和易用性可能尚未经过充分验证。
- **推荐使用**：**谨慎推荐**。适用于对极致性能有要求、且有能力处理实验性API潜在变化的大型项目。不建议在需要高度稳定性的生产项目中直接使用，除非你有团队能够深入理解并跟进其源码变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/InstancedActors)
- [官方文档]()（无）
- [测试用例]()（插件内含测试模块 `InstancedActorsTestSuite`）