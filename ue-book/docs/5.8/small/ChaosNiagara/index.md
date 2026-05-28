# Chaos Niagara

> Import destruction data from Chaos into Niagara to generate secondary destruction effects.

| 属性 | 值 |
|---|---|
| 中文名 | 物理破坏Niagara |
| 分类 | （未指定） |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `ChaosNiagara` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-12-12 |
| 年龄标签 | 🏛️ 文物（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosNiagara) | |

## 用途

ChaosNiagara 是 Chaos 物理破坏系统与 Niagara 粒子系统之间的桥梁插件。它解决了"如何在物体被物理破坏时自动生成视觉特效粒子"这个问题。

核心机制：当 Chaos 物理引擎产生破坏事件（碰撞、断裂、拖尾）时，这个插件将事件数据（位置、速度、法线、质量等）传递给 Niagara 系统，让 Niagara 能够在破坏发生的位置生成二次视觉效果，如碎片飞溅、灰尘、火花等。

插件提供三个 Niagara 数据接口（Data Interface）：

1. **ChaosDestruction**：核心接口，监听 Chaos 物理求解器的碰撞/断裂/拖尾事件，驱动粒子生成
2. **GeometryCollection**：读取 Geometry Collection（几何体集合）的变形数据，用于跟随破坏物体的变换
3. **PhysicsField**：采样物理场（向量场、标量场、整数场），用于物理驱动的粒子效果

## 使用场景

- 你在做一个需要物理破坏的游戏（如建筑坍塌、车辆碰撞）→ 用 ChaosDestruction 在破坏点生成灰尘/碎片粒子
- 你需要粒子跟随 Geometry Collection 碎片运动 → 用 GeometryCollection 数据接口
- 你需要根据物理场强度驱动粒子行为 → 用 PhysicsField 采样物理场数据

## 蓝图用法

ChaosNiagara 的三个数据接口都继承自 `UNiagaraDataInterface`，主要用于 Niagara 系统内部的数据采样，而非蓝图中的直接调用。主要通过 Niagara 编辑器中的数据接口面板进行配置。

### 核心数据接口

| 数据接口 | 显示名称 | 说明 | 所在类 |
|---|---|---|---|
| Chaos Destruction Data | Chaos Destruction Data | 从 Chaos 求解器采样破坏事件，驱动粒子生成 | `UNiagaraDataInterfaceChaosDestruction` |
| Geometry Collection | Geometry Collection | 采样 Geometry Collection 的变换和包围盒数据 | `UNiagaraDataInterfaceGeometryCollection` |
| Physics Field | Physics Field | 采样物理场的向量、标量、整数值 | `UNiagaraDataInterfacePhysicsField` |

### ChaosDestruction 关键配置属性

| 属性 | 说明 |
|---|---|
| `ChaosSolverActorSet` | 关联的 Chaos 求解器 Actor 集合 |
| `DataSourceType` | 数据源类型：碰撞(Collision)/断裂(Breaking)/拖尾(Trailing) |
| `DoSpawn` | 是否启用粒子生成 |
| `SpawnMultiplierMinMax` | 每次事件生成粒子数量范围 |
| `SpawnChance` | 生成概率 (0-1) |
| `InheritedVelocityMultiplier` | 继承物理速度的倍率 |
| `RandomVelocityGenerationType` | 随机速度生成模式 |

### GeometryCollection 可用函数节点

在 Niagara 模块脚本中可使用以下函数：

| 函数 | 说明 | 所在类 |
|---|---|---|
| `GetNumGeometryElements` | 获取几何体元素数量 | `UNiagaraDataInterfaceGeometryCollection` |
| `GetElementBounds` | 获取元素包围盒 | `UNiagaraDataInterfaceGeometryCollection` |
| `GetElementTransformCS` | 获取元素组件空间变换 | `UNiagaraDataInterfaceGeometryCollection` |
| `SetElementTransformCS` | 设置元素组件空间变换 | `UNiagaraDataInterfaceGeometryCollection` |
| `SetElementTransformWS` | 设置元素世界空间变换 | `UNiagaraDataInterfaceGeometryCollection` |
| `GetActorTransform` | 获取 Actor 变换 | `UNiagaraDataInterfaceGeometryCollection` |

### PhysicsField 可用函数节点

| 函数 | 说明 | 所在类 |
|---|---|---|
| `SamplePhysicsVectorField` | 采样物理向量场 | `UNiagaraDataInterfacePhysicsField` |
| `SamplePhysicsScalarField` | 采样物理标量场 | `UNiagaraDataInterfacePhysicsField` |
| `SamplePhysicsIntegerField` | 采样物理整数场 | `UNiagaraDataInterfacePhysicsField` |
| `GetPhysicsFieldResolution` | 获取物理场分辨率 | `UNiagaraDataInterfacePhysicsField` |
| `GetPhysicsFieldBounds` | 获取物理场边界 | `UNiagaraDataInterfacePhysicsField` |

### 使用示例（蓝图描述）

**在 Niagara 系统中使用 ChaosDestruction**：

1. 创建一个新的 Niagara System
2. 在 System 的 Emitters 中添加一个新的 Emitter
3. 在 Emitter 的 "Emitter Properties" 中，找到 Data Interface 面板
4. 添加 "Chaos Destruction Data" 数据接口
5. 在 Spawn Burst Instantaneous 或 Spawn Rate 模块中，引用该数据接口作为数据源
6. 配置 Chaos Solver Actor Set 指向场景中的 ChaosSolverActor
7. 设置 DataSourceType（Collision/Breaking/Trailing）
8. 调整 SpawnMultiplierMinMax、SpawnChance 等参数控制粒子生成

**在 Niagara 中使用 GeometryCollection**：

1. 添加 "Geometry Collection" 数据接口到 Niagara Emitter
2. 设置 SourceMode（Default/Source/AttachParent/DefaultCollectionOnly/ParameterBinding）
3. 在模块脚本中调用 GetElementTransformCS 获取碎片变换数据
4. 使用变换数据驱动粒子位置

## C++ 用法

### 头文件引入

```cpp
#include "NiagaraDataInterfaceChaosDestruction.h"
#include "NiagaraDataInterfaceGeometryCollection.h"
#include "NiagaraDataInterfacePhysicsField.h"
```

### 基本用法

创建 ChaosDestruction 数据接口并配置参数：

```cpp
#include "NiagaraDataInterfaceChaosDestruction.h"

// 在 Niagara Component 上创建并配置 Chaos Destruction 数据接口
UNiagaraDataInterfaceChaosDestruction* ChaosDI = NewObject<UNiagaraDataInterfaceChaosDestruction>();

// 配置数据源类型（碰撞/断裂/拖尾）
ChaosDI->DataSourceType = EDataSourceTypeEnum::ChaosNiagara_DataSourceType_Collision;

// 启用粒子生成
ChaosDI->DoSpawn = true;

// 设置生成数量范围
ChaosDI->SpawnMultiplierMinMax = FVector2D(1.0f, 5.0f);

// 设置生成概率
ChaosDI->SpawnChance = 0.5f;

// 设置继承速度倍率
ChaosDI->InheritedVelocityMultiplier = 1.0f;

// 设置数据处理频率
ChaosDI->DataProcessFrequency = 30;

// 最大数据条目数
ChaosDI->MaxNumberOfDataEntriesToSpawn = 50;
```

来源：`Source/ChaosNiagara/Classes/NiagaraDataInterfaceChaosDestruction.h`

### 进阶用法

配置 ChaosDestruction 的高级过滤和空间哈希：

```cpp
// 启用空间哈希优化
ChaosDI->DoSpatialHash = true;
ChaosDI->SpatialHashVolumeMin = FVector(-1000.0f);
ChaosDI->SpatialHashVolumeMax = FVector(1000.0f);
ChaosDI->SpatialHashVolumeCellSize = FVector(100.0f);
ChaosDI->MaxDataPerCell = 10;

// 配置位置过滤
ChaosDI->LocationFilteringMode = ELocationFilteringModeEnum::ChaosNiagara_LocationFilteringMode_Inclusive;
ChaosDI->LocationXToSpawn = ELocationXToSpawnEnum::ChaosNiagara_LocationXToSpawn_MinMax;
ChaosDI->LocationXToSpawnMinMax = FVector2D(-500.0f, 500.0f);

// 配置速度生成模式
ChaosDI->RandomVelocityGenerationType = ERandomVelocityGenerationTypeEnum::ChaosNiagara_RandomVelocityGenerationType_CollisionNormalBased;
ChaosDI->SpreadAngleMax = 45.0f;

// 配置材质过滤
ChaosDI->bApplyMaterialsFilter = true;
// ChaosDI->ChaosBreakingMaterialSet.Add(SomePhysicalMaterial);

// 配置数据排序
ChaosDI->DataSortingType = EDataSortTypeEnum::ChaosNiagara_DataSortType_SortByMassMaxToMin;

// 配置阈值过滤
ChaosDI->ImpulseToSpawnMinMax = FVector2D(100.0f, 10000.0f);
ChaosDI->SpeedToSpawnMinMax = FVector2D(50.0f, 10000.0f);
ChaosDI->MassToSpawnMinMax = FVector2D(0.1f, 1000.0f);
```

来源：`Source/ChaosNiagara/Classes/NiagaraDataInterfaceChaosDestruction.h`

配置 GeometryCollection 数据接口的源模式：

```cpp
#include "NiagaraDataInterfaceGeometryCollection.h"

UNiagaraDataInterfaceGeometryCollection* GCDI = NewObject<UNiagaraDataInterfaceGeometryCollection>();

// 设置源模式
GCDI->SourceMode = ENDIGeometryCollection_SourceMode::Default;

// 设置默认 Geometry Collection 资产
GCDI->DefaultGeometryCollection = MyGeometryCollectionAsset;

// 是否包含中间骨骼/几何体（非仅叶节点）
GCDI->bIncludeIntermediateBones = true;

// 在蓝图中通过 Set 节点绑定源 Actor
// GCDI->GeometryCollectionActor = SoftReferenceToActor;
```

来源：`Source/ChaosNiagara/Public/NiagaraDataInterfaceGeometryCollection.h`

## Demo 示例

以下是一个最小的 C++ 示例，展示如何在运行时通过代码创建一个使用 ChaosDestruction 数据接口的 Niagara 系统。

### MyChaosNiagaraDemo.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MyChaosNiagaraDemo.generated.h"

class UNiagaraComponent;
class UNiagaraSystem;
class AChaosSolverActor;

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyChaosNiagaraDemo : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyChaosNiagaraDemo();

    virtual void BeginPlay() override;

    /** 要使用的 Niagara 系统 */
    UPROPERTY(EditAnywhere, Category = "Chaos Niagara")
    TObjectPtr<UNiagaraSystem> DestructionNiagaraSystem;

    /** 关联的 Chaos 求解器 */
    UPROPERTY(EditAnywhere, Category = "Chaos Niagara")
    TObjectPtr<AChaosSolverActor> ChaosSolver;

private:
    UPROPERTY()
    TObjectPtr<UNiagaraComponent> NiagaraComp;
};
```

### MyChaosNiagaraDemo.cpp

```cpp
#include "MyChaosNiagaraDemo.h"
#include "NiagaraFunctionLibrary.h"
#include "NiagaraComponent.h"
#include "NiagaraDataInterfaceChaosDestruction.h"
#include "ChaosSolverActor.h"

UMyChaosNiagaraDemo::UMyChaosNiagaraDemo()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UMyChaosNiagaraDemo::BeginPlay()
{
    Super::BeginPlay();

    if (!DestructionNiagaraSystem)
    {
        UE_LOG(LogTemp, Warning, TEXT("ChaosNiagaraDemo: DestructionNiagaraSystem 未设置"));
        return;
    }

    // 创建 Niagara 组件
    NiagaraComp = UNiagaraFunctionLibrary::SpawnSystemAttached(
        DestructionNiagaraSystem,
        GetOwner()->GetRootComponent(),
        NAME_None,
        FVector::ZeroVector,
        FRotator::ZeroRotator,
        EAttachLocation::SnapToTarget,
        true,
        true,
        ENCPoolMethod::None,
        true
    );

    if (NiagaraComp && ChaosSolver)
    {
        // 通过用户参数传递 Chaos 求解器引用给 Niagara
        // 注意：通常 ChaosDestruction 数据接口直接在 Niagara 资产中配置
        // 这里展示的是运行时动态创建数据接口的思路
        UNiagaraDataInterfaceChaosDestruction* ChaosDI = NewObject<UNiagaraDataInterfaceChaosDestruction>();
        
        ChaosDI->DataSourceType = EDataSourceTypeEnum::ChaosNiagara_DataSourceType_Breaking;
        ChaosDI->DoSpawn = true;
        ChaosDI->SpawnMultiplierMinMax = FVector2D(1.0f, 3.0f);
        ChaosDI->SpawnChance = 1.0f;
        ChaosDI->InheritedVelocityMultiplier = 0.5f;
        ChaosDI->DataProcessFrequency = 60;
        ChaosDI->MaxNumberOfDataEntriesToSpawn = 20;
        ChaosDI->RandomVelocityGenerationType = ERandomVelocityGenerationTypeEnum::ChaosNiagara_RandomVelocityGenerationType_RandomDistribution;
        ChaosDI->RandomVelocityMagnitudeMinMax = FVector2D(50.0f, 200.0f);

        // 将求解器添加到数据接口的求解器集合
        ChaosDI->ChaosSolverActorSet.Add(ChaosSolver);

        UE_LOG(LogTemp, Log, TEXT("ChaosNiagaraDemo: 已配置破坏粒子系统"));
    }
}
```

## 模块依赖

从 `.uplugin` 的 Plugins 依赖关系提取（Build.cs 中的具体模块名需查阅源码，此处列出插件级依赖）：

| 模块/插件 | 用途 |
|---|---|
| `Niagara` | Niagara 粒子系统框架，提供数据接口基础 |
| `ChaosSolverPlugin` | Chaos 物理求解器，提供破坏事件数据源 |
| `GeometryCollectionEngine` | Geometry Collection 运行时，提供几何体集合数据访问 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移到 UE_LOGF 新格式 |
| 2026-03-31 | `2694af3a` | Enable physics field on mobile only for CPU | 移动端仅启用 CPU 模式的物理场 |
| 2026-03-18 | `b5a4f07a` | Fix debug transient physics field accumulation | 修复调试用瞬态物理场累积问题 |
| 2026-02-17 | `07e506eb` | Physics field direct evaluation in materials | 支持在材质中直接采样物理场 |
| 2025-10-31 | `351270e5` | Fix wrong indexing in Niagara Destruction Data interface causing some particles to spawn at the origin | 修复破坏数据接口索引错误导致粒子在原点生成的 Bug |

### 维护评价

**活跃维护**。尽管该插件从 2018 年创建至今已有约 7 年，但仍保持持续更新：

- 最近一次更新（2026-04-14）距今不到 1 个月，属于代码现代化维护
- Physics Field 子系统在 2026 年有密集的功能增强（材质直接采样、移动端支持、Bug 修复）
- 插件仍标记为 `IsBetaVersion = true`（实验性），说明 API 可能存在变动
- `EnabledByDefault = true` 意味着引擎默认启用，但 `Installed = false` 表示未随引擎安装
- 作为 Chaos 物理系统与 Niagara 的关键桥梁，该插件在破坏效果工作流中不可替代
- **推荐使用**，但需注意实验性状态，建议密切关注 API 变化

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosNiagara)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosNiagara)（未发现独立测试文件）