# Chaos Cloth Asset

> Pattern based cloth asset using the Chaos Cloth simulation.

| 属性 | 值 |
|---|---|
| 中文名 | 混沌布料资产 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（布料资产蓝图、数据流图资产） |
| 模块 | `ChaosClothAsset` (Runtime), `ChaosClothAssetEngine` (Runtime), `ChaosClothAssetTools` (Editor) |
| 实验性 | ⚠️ 是（Beta 版本） |
| 创建时间 | 2024-03-22 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAsset) | |

## 用途

ChaosClothAsset 插件提供了一套**基于图案（Pattern）的布料资产系统**，用于驱动 Chaos 布料物理模拟。与传统基于骨骼网格体的布料工作流不同，该插件引入了独立的布料资产（`UChaosClothAsset`）和服装资产（Outfit Asset）概念，通过 Dataflow 节点图实现从 2D 裁片图案到 3D 布料模拟的完整流程。

核心解决的问题：
- **传统布料工作流的局限**：旧系统将布料数据绑定在骨骼网格体上，难以独立编辑和复用
- **图案化建模**：支持基于 2D 图案（裁片）的布料建模，更贴近真实服装设计流程
- **Dataflow 驱动**：布料的几何构建、属性设置均可通过 Dataflow 节点图完成，实现非破坏性编辑
- **多 LOD 模拟**：每个布料资产可包含多级 LOD 的模拟数据，支持运行时自适应
- **复杂服装编排**：通过 Outfit Asset 可将多个布料部件组合成完整服装

## 使用场景

- 你在开发需要真实布料模拟的角色服装 → 使用 `UChaosClothAsset` 创建独立布料资产
- 你需要将多件布料组合成完整服装（如外套+衬衫+裤子） → 使用 Outfit Asset 管理多个布料模型
- 你希望通过 Dataflow 节点图非破坏性地构建布料 → 为布料资产分配 Dataflow 图资产
- 你需要在运行时动态修改布料属性（如风力、重力、刚度） → 使用 `UChaosClothAssetInteractor` 读写属性
- 你需要将布料挂在骨骼网格体上使用 → 使用 `UChaosClothAssetSKMClothingAsset` 将布料资产绑定到骨骼网格体
- 你需要为布料添加外部碰撞源（如角色躯干与布料的碰撞） → 使用 `AddCollisionSource` API
- 你需要将布料模拟结果缓存用于回放 → 集成 Chaos Cache 系统（`FClothComponentCacheAdapter`）

## 蓝图用法

### 核心节点

#### 布料组件（UChaosClothComponent）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetAsset` | 设置组件使用的布料/服装资产 | `UChaosClothComponent` |
| `GetAsset` | 获取当前使用的布料/服装资产 | `UChaosClothComponent` |
| `ForceNextUpdateTeleport` | 下次更新时传送布料粒子到新骨骼位置（保持姿态） | `UChaosClothComponent` |
| `ForceNextUpdateTeleportAndReset` | 下次更新时传送并重置布料粒子 | `UChaosClothComponent` |
| `ResetRestLengthsWithMorphTarget` | 用指定 MorphTarget 重置布料静止长度 | `UChaosClothComponent` |
| `SuspendSimulation` | 暂停模拟，保持布料在最后的姿态 | `UChaosClothComponent` |
| `ResumeSimulation` | 恢复已暂停的模拟 | `UChaosClothComponent` |
| `IsSimulationSuspended` | 查询模拟是否已暂停 | `UChaosClothComponent` |
| `SetEnableSimulation` | 启用/禁用模拟 | `UChaosClothComponent` |
| `IsSimulationEnabled` | 查询模拟是否启用 | `UChaosClothComponent` |
| `ResetConfigProperties` | 将所有布料配置属性重置为资产原始值 | `UChaosClothComponent` |
| `RecreateClothSimulationProxy` | 硬重置布料模拟（重建代理） | `UChaosClothComponent` |
| `GetClothOutfitInteractor` | 获取布料交互器（用于运行时修改属性） | `UChaosClothComponent` |
| `AddCollisionSource` | 添加碰撞源（其他骨骼网格体的物理资产碰撞体） | `UChaosClothComponent` |
| `RemoveCollisionSource` | 移除指定碰撞源 | `UChaosClothComponent` |
| `SetCollideWithEnvironment` | 启用/禁用与环境碰撞 | `UChaosClothComponent` |
| `SetSimulateInEditor` | 设置是否在编辑器中模拟（仅编辑器） | `UChaosClothComponent` |
| `GetTeleportDistanceThreshold` / `SetTeleportDistanceThreshold` | 获取/设置传送距离阈值 | `UChaosClothComponent` |
| `GetTeleportRotationThreshold` / `SetTeleportRotationThreshold` | 获取/设置传送旋转阈值 | `UChaosClothComponent` |

#### 布料资产基类（UChaosClothAssetBase）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetOverlayMaterial` | 获取覆盖材质 | `UChaosClothAssetBase` |
| `SetOverlayMaterial` | 设置覆盖材质 | `UChaosClothAssetBase` |
| `GetOverlayMaterialMaxDrawDistance` | 获取覆盖材质最大绘制距离 | `UChaosClothAssetBase` |
| `SetOverlayMaterialMaxDrawDistance` | 设置覆盖材质最大绘制距离 | `UChaosClothAssetBase` |

#### 布料属性交互器（UChaosClothAssetInteractor）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetAllPropertyNames` | 获取所有属性名称列表 | `UChaosClothAssetInteractor` |
| `GetFloatPropertyValue` | 获取浮点属性值 | `UChaosClothAssetInteractor` |
| `GetWeightedFloatPropertyValue` | 获取加权浮点属性值（Low/High） | `UChaosClothAssetInteractor` |
| `GetIntPropertyValue` | 获取整数属性值 | `UChaosClothAssetInteractor` |
| `GetVectorPropertyValue` | 获取向量属性值 | `UChaosClothAssetInteractor` |
| `GetStringPropertyValue` | 获取字符串属性值 | `UChaosClothAssetInteractor` |
| `SetFloatPropertyValue` | 设置浮点属性值（LODIndex=-1 设置所有 LOD） | `UChaosClothAssetInteractor` |
| `SetWeightedFloatPropertyValue` | 设置加权浮点属性值 | `UChaosClothAssetInteractor` |
| `SetIntPropertyValue` | 设置整数属性值 | `UChaosClothAssetInteractor` |
| `SetVectorPropertyValue` | 设置向量属性值 | `UChaosClothAssetInteractor` |
| `SetStringPropertyValue` | 设置字符串属性值 | `UChaosClothAssetInteractor` |
| `SetPropertySet` | 从属性集合批量设置属性 | `UChaosClothAssetInteractor` |

### 使用示例（蓝图描述）

**场景：为角色添加布料组件并运行时调整属性**

1. 在角色蓝图中添加 `UChaosClothComponent` 组件
2. 调用 `SetAsset` 节点，将布料资产（或服装资产）连接到 `InAsset` 参数
3. 布料组件会自动从资产中读取模拟数据并开始模拟
4. 如需运行时调整属性，先调用 `GetClothOutfitInteractor` 获取交互器
5. 使用交互器的 `SetFloatPropertyValue` 设置属性，如 `"Drag"`, 值 `0.5`
6. 交互器设置的属性会覆盖资产中的默认值，仅影响当前组件实例

**场景：添加外部碰撞**

1. 获取角色的骨骼网格体组件引用
2. 获取角色的物理资产（PhysicsAsset）
3. 调用 `AddCollisionSource`，传入骨骼网格体组件和物理资产
4. 每个布料 tick，来自该物理资产的碰撞体（由骨骼变换驱动）将应用于布料模拟

## C++ 用法

### 头文件引入

```cpp
#include "ChaosClothAsset/ClothAsset.h"
#include "ChaosClothAsset/ClothAssetBase.h"
#include "ChaosClothAsset/ClothComponent.h"
#include "ChaosClothAsset/ClothAssetInteractor.h"
#include "ChaosClothAsset/ClothSimulationModel.h"
#include "ChaosClothAsset/ClothEngineTools.h"
```

### 基本用法

**创建和配置布料组件**

```cpp
// 在 Actor 的构造函数或 BeginPlay 中
UChaosClothComponent* ClothComp = NewObject<UChaosClothComponent>(this);
ClothComp->SetAsset(MyClothAsset);  // 设置布料资产
ClothComp->SetEnableSimulation(true);
ClothComp->RegisterComponent();

// 来源：Public/ChaosClothAsset/ClothComponent.h - SetAsset/UChaosClothComponent
```

**运行时修改布料属性**

```cpp
// 获取交互器（ModelIndex=0 表示第一个模拟模型）
UChaosClothAssetInteractor* Interactor = ClothComp->GetClothOutfitInteractor(0);
if (Interactor)
{
    // 设置浮点属性
    Interactor->SetFloatPropertyValue(FName("Wind.DragCoefficient"), -1, 0.5f);
    
    // 设置向量属性（LODIndex=-1 表示设置所有 LOD）
    Interactor->SetVectorPropertyValue(FName("Wind.WindVelocity"), -1, FVector(100.f, 0.f, 0.f));
    
    // 读取属性值
    float Value = Interactor->GetFloatPropertyValue(FName("Wind.DragCoefficient"), 0, 0.f);
}

// 来源：Public/ChaosClothAsset/ClothAssetInteractor.h
```

**查询布料模拟信息**

```cpp
// 通过基类接口查询模拟模型
UChaosClothAssetBase* Asset = ClothComp->GetAsset();
if (Asset && Asset->HasValidClothSimulationModels())
{
    int32 NumModels = Asset->GetNumClothSimulationModels();
    
    for (int32 i = 0; i < NumModels; ++i)
    {
        TSharedPtr<const FChaosClothSimulationModel> Model = Asset->GetClothSimulationModel(i);
        if (Model.IsValid())
        {
            int32 NumLods = Model->GetNumLods();
            for (int32 Lod = 0; Lod < NumLods; ++Lod)
            {
                int32 NumVerts = Model->GetNumVertices(Lod);
                int32 NumTris = Model->GetNumTriangles(Lod);
                // ... 使用模拟数据
            }
        }
    }
}

// 来源：Public/ChaosClothAsset/ClothAssetBase.h, ClothSimulationModel.h
```

### 进阶用法

**添加外部碰撞源**

```cpp
// 假设角色有一个 SkeletalMeshComponent 作为躯干
USkeletalMeshComponent* BodyMeshComp = Character->GetMesh();
UPhysicsAsset* BodyPhysicsAsset = BodyMeshComp->GetSkeletalMeshAsset()->GetPhysicsAsset();

// 为布料组件添加碰撞源
ClothComp->AddCollisionSource(BodyMeshComp, BodyPhysicsAsset, true); // true = 仅使用 Sphyls
// 来源：Public/ChaosClothAsset/ClothComponent.h - AddCollisionSource
```

**使用属性数据资产批量设置属性**

```cpp
// 从 UClothAssetInteractorDataAsset 加载属性集
UClothAssetInteractorDataAsset* PropertyDataAsset = LoadObject<UClothAssetInteractorDataAsset>(nullptr, TEXT("/Game/ClothProperties/WindPreset"));
if (PropertyDataAsset)
{
    UChaosClothAssetInteractor* Interactor = ClothComp->GetClothOutfitInteractor(0);
    const FClothAssetInteractorPropertyBag& PropertySet = PropertyDataAsset->GetPropertySet(FName("HeavyWind"));
    Interactor->SetPropertySet(PropertySet, -1);
}

// 来源：Private/ChaosClothAsset/ClothAssetInteractorDataAsset.h
```

**通过 Dataflow 构建布料资产**

```cpp
// 设置 Dataflow 图资产（通常在编辑器中完成）
UChaosClothAsset* ClothAsset = ...;
UDataflow* DataflowGraph = LoadObject<UDataflow>(nullptr, TEXT("/Game/Dataflow/MyClothGraph"));
ClothAsset->SetDataflow(DataflowGraph);

// 从 ClothCollection 构建布料
TArray<TSharedRef<const FManagedArrayCollection>> ClothCollections = ...; // 由 Dataflow 生成
ClothAsset->Build(ClothCollections);

// 来源：Public/ChaosClothAsset/ClothAssetBase.h, ClothAsset.h
```

**从 ClothCollection 工具生成 Tether 数据**

```cpp
TSharedRef<FManagedArrayCollection> ClothCollection = ...;

// 生成 geodesic tether 数据
UE::Chaos::ClothAsset::FClothEngineTools::GenerateTethers(
    ClothCollection,
    FName("MaxDistance"),     // 权重图名称
    true,                     // bGeodesicTethers
    FVector2f(0.f, 1.f)     // MaxDistance 范围
);

// 来源：Public/ChaosClothAsset/ClothEngineTools.h
```

## Demo 示例

```cpp
// MyClothActor.h
#pragma once

#include "GameFramework/Actor.h"
#include "MyClothActor.generated.h"

class UChaosClothComponent;
class UChaosClothAsset;
class UChaosClothAssetInteractor;

UCLASS()
class AMyClothActor : public AActor
{
    GENERATED_BODY()

public:
    AMyClothActor();

    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable)
    void SetWindStrength(float Strength);

protected:
    UPROPERTY(VisibleAnywhere)
    UChaosClothComponent* ClothComponent;

    UPROPERTY(EditAnywhere, Category = "Cloth")
    UChaosClothAsset* ClothAsset;

    UPROPERTY()
    UChaosClothAssetInteractor* CachedInteractor;
};
```

```cpp
// MyClothActor.cpp
#include "MyClothActor.h"
#include "ChaosClothAsset/ClothComponent.h"
#include "ChaosClothAsset/ClothAsset.h"
#include "ChaosClothAsset/ClothAssetInteractor.h"

AMyClothActor::AMyClothActor()
{
    ClothComponent = CreateDefaultSubobject<UChaosClothComponent>(TEXT("ClothComponent"));
    RootComponent = ClothComponent;
}

void AMyClothActor::BeginPlay()
{
    Super::BeginPlay();

    if (ClothAsset)
    {
        ClothComponent->SetAsset(ClothAsset);
        CachedInteractor = ClothComponent->GetClothOutfitInteractor(0);
    }
}

void AMyClothActor::SetWindStrength(float Strength)
{
    if (CachedInteractor)
    {
        CachedInteractor->SetFloatPropertyValue(FName("Wind.DragCoefficient"), -1, Strength);
    }
}
```

## 模块依赖

以下为 ChaosClothAssetEngine 模块从 Build.cs 中提取的独特依赖（省略标准 Core/Engine/Slate 依赖）：

| 模块 | 用途 |
|---|---|
| `ChaosCloth` | Chaos 布料物理求解器核心 |
| `ClothingSystemRuntimeCommon` | 通用布料系统运行时接口（`UClothingAssetBase`, `UClothingSimulationFactory`） |
| `Dataflow` | Dataflow 图执行框架（布料资产的节点图驱动） |
| `GeometryCache` | 几何缓存支持 |
| `ChaosSolverEngine` | Chaos 物理求解器引擎集成 |

插件级别依赖（.uplugin Plugins 字段）：
- `ChaosCloth` (必需)
- `GeometryCache` (必需)
- `Dataflow` (必需)

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `89e20f15` | [ChaosClothAsset] Preserve the Cloth Component bSimulateInEditor and Asset properties across Bluepri | 蓝图构造脚本重运行时保留布料组件的编辑器模拟和资产属性 |
| 2026-05-26 | `8953a713` | [Cloth] Move parallel cloth simulation wait from EOF to TG_LastDemotable. | 将并行布料模拟等待从帧末尾移到 TG_LastDemotable tick 阶段 |
| 2026-05-25 | `1db5232a` | [ChaosCloth] Implement RefershBoneMapping for ClothAssetSKMClothingAsset. | 为 SKM 布料资产实现骨骼映射刷新功能 |
| 2026-05-22 | `e98c5896` | [Chaos Cloth Asset] Refresh the editor-only Asset alias after a duplicate or paste of an actor. | 复制或粘贴 Actor 后刷新编辑器专用的资产别名 |
| 2026-05-20 | `b9a938ae` | Cleanup Chaos Cloth Asset converter | 清理布料资产转换器代码 |

### 维护评价

**活跃维护中**。ChaosClothAsset 是 Epic 正在积极开发的核心布料系统：

- **创建时间**：2024 年 3 月从 Experimental 迁移至 Beta，表明已达到一定的稳定性
- **更新频率**：最近一周内有 5 次提交，涉及 bug 修复、性能优化和功能完善，维护非常活跃
- **代码质量**：源码中大量 `UE_DEPRECATED` 标记和清晰的版本迁移路径（如 `SetClothAsset` → `SetAsset`），表明 API 在有计划地演进
- **Beta 状态**：插件仍标记为 Beta（`EnabledByDefault=false`），但核心功能已较为完整
- **架构成熟**：分离了资产（Asset）、组件（Component）、代理（Proxy）、交互器（Interactor）等层次，代码组织清晰

**推荐使用**，但需注意：
- 插件默认未启用，需在项目设置中手动启用
- API 仍在演进中，部分旧接口已标记废弃，建议使用最新 API
- 依赖 ChaosCloth、Dataflow 等插件，需确保这些插件可用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAsset)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- 测试用例：未在插件目录中发现独立测试文件