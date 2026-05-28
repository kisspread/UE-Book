# Chaos Cloth Asset

> Pattern based cloth asset using the Chaos Cloth simulation.

| 属性 | 值 |
|---|---|
| 中文名 | 布料资产 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（布料资产类型、蓝图交互接口） |
| 模块 | `ChaosClothAsset` (Runtime), `ChaosClothAssetEngine` (Runtime), `ChaosClothAssetTools` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-03-22 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAsset) | |

## 用途

ChaosClothAsset 是 UE5 基于 Chaos 物理引擎的**新一代布料资产系统**，采用基于裁片图案（Pattern-based）的布料模拟方式。它替代了旧版 Cloth 系统中直接在 SkeletalMesh 上标记布料区域的方式，转而引入独立的布料资产（`UChaosClothAsset`）和布料组件（`UChaosClothComponent`），将布料模拟与角色骨骼动画解耦。

该插件的核心价值在于：

1. **资产化管理布料**：布料几何、模拟参数、LOD 数据封装为独立资产，可在多个角色间共享和复用
2. **Dataflow 工作流**：通过 Dataflow 图表驱动布料资产的创建和编辑，支持节点化、非破坏性的布料建模
3. **独立模拟组件**：`UChaosClothComponent` 可独立于 SkeletalMeshComponent 运行布料模拟，支持更灵活的组合方式
4. **Outfit 支持**：基类 `UChaosClothAssetBase` 同时支持单件布料资产和套装资产（Outfit Asset），适用于复杂的多件服装系统
5. **运行时属性修改**：通过 `UChaosClothAssetInteractor` 在蓝图中动态修改模拟参数（风力、重力、阻尼等），无需重建资产

该插件从 Experimental 文件夹迁出并标记为 Beta（首次提交即说明），标志着 Epic 将其视为 Chaos 布料系统的主要发展方向。

## 使用场景

- 你在制作角色服装（衬衫、裙子、斗篷等）需要物理模拟 → 用 ChaosClothAsset 创建独立的布料资产
- 你需要用 Dataflow 节点图编辑布料裁片和缝合关系 → 用该插件的 Dataflow 集成工作流
- 你需要在同一角色身上穿多件独立模拟的衣服（上衣+裙子+围巾）→ 用多个 ChaosClothComponent 或 Outfit 资产
- 你需要在运行时动态调整布料的物理参数（如进入室内时减少风力影响）→ 用 UChaosClothAssetInteractor
- 你需要布料与外部骨骼网格体碰撞（如武器碰撞衣服）→ 用 CollisionSource 系统

## 蓝图用法

### 核心节点 — 布料组件 (`UChaosClothComponent`)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetAsset` | 设置布料/套装资产 | `UChaosClothComponent` |
| `GetAsset` | 获取当前使用的布料资产 | `UChaosClothComponent` |
| `ForceNextUpdateTeleport` | 下一帧传送布料到新位置，保持当前姿态 | `UChaosClothComponent` |
| `ForceNextUpdateTeleportAndReset` | 下一帧传送并重置布料姿态和速度 | `UChaosClothComponent` |
| `SuspendSimulation` | 暂停模拟，保持当前姿态 | `UChaosClothComponent` |
| `ResumeSimulation` | 恢复已暂停的模拟 | `UChaosClothComponent` |
| `SetEnableSimulation` | 启用/禁用模拟 | `UChaosClothComponent` |
| `IsSimulationEnabled` | 查询模拟是否启用 | `UChaosClothComponent` |
| `IsSimulationSuspended` | 查询模拟是否已暂停 | `UChaosClothComponent` |
| `ResetRestLengthsWithMorphTarget` | 用 MorphTarget 重置布料静止长度 | `UChaosClothComponent` |
| `RecreateClothSimulationProxy` | 硬重置模拟（重建代理对象） | `UChaosClothComponent` |
| `ResetConfigProperties` | 将模拟参数重置为资产原始值 | `UChaosClothComponent` |
| `GetClothOutfitInteractor` | 获取布料属性交互器 | `UChaosClothComponent` |
| `AddCollisionSource` | 添加外部碰撞源 | `UChaosClothComponent` |
| `RemoveCollisionSource` | 移除指定碰撞源 | `UChaosClothComponent` |
| `ResetCollisionSources` | 清除所有碰撞源 | `UChaosClothComponent` |
| `SetCollideWithEnvironment` | 设置是否与环境碰撞 | `UChaosClothComponent` |
| `SetSimulateInEditor` | 编辑器中启用/禁用模拟 | `UChaosClothComponent` |

### 核心节点 — 属性交互器 (`UChaosClothAssetInteractor`)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetAllPropertyNames` | 获取所有可修改的属性名称 | `UChaosClothAssetInteractor` |
| `GetFloatPropertyValue` | 读取浮点属性值 | `UChaosClothAssetInteractor` |
| `SetFloatPropertyValue` | 设置浮点属性值 | `UChaosClothAssetInteractor` |
| `GetIntPropertyValue` | 读取整数属性值 | `UChaosClothAssetInteractor` |
| `SetIntPropertyValue` | 设置整数属性值 | `UChaosClothAssetInteractor` |
| `GetVectorPropertyValue` | 读取向量属性值 | `UChaosClothAssetInteractor` |
| `SetVectorPropertyValue` | 设置向量属性值 | `UChaosClothAssetInteractor` |
| `GetWeightedFloatPropertyValue` | 读取加权浮点属性（高低值） | `UChaosClothAssetInteractor` |
| `SetWeightedFloatPropertyValue` | 设置加权浮点属性 | `UChaosClothAssetInteractor` |
| `SetPropertySet` | 批量设置一组属性 | `UChaosClothAssetInteractor` |

### 核心节点 — 资产基类 (`UChaosClothAssetBase`)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetOverlayMaterial` | 获取覆盖材质 | `UChaosClothAssetBase` |
| `SetOverlayMaterial` | 设置覆盖材质 | `UChaosClothAssetBase` |
| `GetOverlayMaterialMaxDrawDistance` | 获取覆盖材质最大绘制距离 | `UChaosClothAssetBase` |
| `SetOverlayMaterialMaxDrawDistance` | 设置覆盖材质最大绘制距离 | `UChaosClothAssetBase` |

### 使用示例（蓝图描述）

**示例 1：设置布料资产并开始模拟**
1. 创建一个 Actor，添加 `UChaosClothComponent`
2. 调用 `SetAsset` 节点，连接你的 `UChaosClothAsset` 资产引用
3. 布料组件会自动注册并开始模拟

**示例 2：运行时修改布料参数**
1. 获取 `UChaosClothComponent` 引用
2. 调用 `GetClothOutfitInteractor(0)` 获取交互器
3. 调用 `SetFloatPropertyValue("WindSpeed", -1, 5.0)` 修改风速
4. LODIndex 传 -1 表示对所有 LOD 生效

**示例 3：布料与外部角色碰撞**
1. 获取目标角色的 `SkeletalMeshComponent` 引用
2. 获取该角色的 `PhysicsAsset` 引用
3. 调用 `AddCollisionSource(TargetSkeletalMesh, PhysicsAsset)` 添加碰撞

## C++ 用法

### 头文件引入

```cpp
#include "ChaosClothAsset/ClothAsset.h"
#include "ChaosClothAsset/ClothComponent.h"
#include "ChaosClothAsset/ClothAssetInteractor.h"
#include "ChaosClothAsset/ClothSimulationModel.h"
#include "ChaosClothAsset/ClothEngineTools.h"
```

### 基本用法

**获取布料模拟模型数据**（来源：`ClothAssetBase.h`）

```cpp
// 获取布料资产的模拟模型
UChaosClothAsset* ClothAsset = /* 从资产库或组件获取 */;
TSharedPtr<const FChaosClothSimulationModel> SimModel = ClothAsset->GetClothSimulationModel(0);

if (SimModel.IsValid())
{
    int32 NumLods = SimModel->GetNumLods();
    int32 NumVertices = SimModel->GetNumVertices(0); // LOD 0 的顶点数
    int32 NumTriangles = SimModel->GetNumTriangles(0); // LOD 0 的三角形数
    
    // 获取模拟网格位置数据
    TConstArrayView<FVector3f> Positions = SimModel->GetPositions(0);
    TConstArrayView<FVector3f> Normals = SimModel->GetNormals(0);
    TConstArrayView<uint32> Indices = SimModel->GetIndices(0);
}
```

**通过组件交互器修改运行时属性**（来源：`ClothComponent.h`、`ClothAssetInteractor.h`）

```cpp
UChaosClothComponent* ClothComp = /* 获取组件引用 */;

// 获取交互器（ModelIndex=0, NAME_None 表示默认模型）
UChaosClothAssetInteractor* Interactor = ClothComp->GetClothOutfitInteractor(0, NAME_None);

if (Interactor)
{
    // 读取当前风速
    float WindSpeed = Interactor->GetFloatPropertyValue(FName("WindSpeed"), 0, 0.f);
    
    // 设置新的风速（LODIndex=-1 表示所有 LOD）
    Interactor->SetFloatPropertyValue(FName("WindSpeed"), -1, 10.0f);
    
    // 批量设置属性
    Interactor->SetVectorPropertyValue(FName("WindDirection"), -1, FVector(1, 0, 0));
}
```

### 进阶用法

**构建布料资产并设置碰撞**（来源：`ClothAsset.h`、`ClothComponent.h`）

```cpp
// 构建布料资产（从 ClothCollection 数据）
UChaosClothAsset* ClothAsset = NewObject<UChaosClothAsset>();

TArray<TSharedRef<const FManagedArrayCollection>> ClothCollections;
// ... 填充 ClothCollections 数据 ...

FText ErrorText, VerboseText;
ClothAsset->Build(ClothCollections, nullptr, &ErrorText, &VerboseText);

if (!ErrorText.IsEmpty())
{
    UE_LOG(LogChaosClothAsset, Error, TEXT("Build failed: %s"), *ErrorText.ToString());
}

// 设置物理碰撞资产
UPhysicsAsset* PhysicsAsset = LoadObject<UPhysicsAsset>(nullptr, TEXT("/Game/Character/Physics/BodyPhysics"));
ClothAsset->SetPhysicsAsset(PhysicsAsset);

// 在组件上添加外部碰撞源
UChaosClothComponent* ClothComp = /* 获取组件 */;
USkinnedMeshComponent* EnemyMesh = /* 获取敌方骨骼组件 */;
UPhysicsAsset* EnemyPhysics = /* 获取敌方物理资产 */;

ClothComp->AddCollisionSource(EnemyMesh, EnemyPhysics, /* bUseSphylsOnly = */ false);
ClothComp->SetCollideWithEnvironment(true);

// 使用引擎工具生成 Tether 数据（用于约束布料模拟）
TSharedRef<FManagedArrayCollection> Collection = /* 获取 ClothCollection */;
FName WeightMap = FName("MaxDistance");
FClothEngineTools::GenerateTethers(Collection, WeightMap, /* bGeodesicTethers = */ true);
```

**设置外部碰撞并控制模拟生命周期**（来源：`ClothComponent.h`、`ClothSimulationProxy.h`）

```cpp
UChaosClothComponent* ClothComp = /* 获取组件 */;

// 暂停模拟
ClothComp->SuspendSimulation();

// 恢复模拟
ClothComp->ResumeSimulation();

// 强制传送布料（角色瞬移时使用）
ClothComp->ForceNextUpdateTeleportAndReset();

// 硬重置（配置更改后完全重建模拟代理）
ClothComp->RecreateClothSimulationProxy();

// 将模拟参数重置为资产原始值
ClothComp->ResetConfigProperties();
```

## Demo 示例

```cpp
// ChaosClothDemoActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ChaosClothDemoActor.generated.h"

class UChaosClothComponent;
class UChaosClothAssetInteractor;

UCLASS()
class AChaosClothDemoActor : public AActor
{
    GENERATED_BODY()

public:
    AChaosClothDemoActor();

    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

    /** 设置布料资产 */
    UFUNCTION(BlueprintCallable, Category = "Cloth Demo")
    void SetClothAsset(class UChaosClothAssetBase* InAsset);

    /** 修改风速 */
    UFUNCTION(BlueprintCallable, Category = "Cloth Demo")
    void SetWindSpeed(float Speed);

private:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, meta = (AllowPrivateAccess = "true"))
    TObjectPtr<UChaosClothComponent> ClothComponent;

    UPROPERTY()
    float CurrentWindSpeed = 0.f;
};
```

```cpp
// ChaosClothDemoActor.cpp
#include "ChaosClothDemoActor.h"
#include "ChaosClothAsset/ClothComponent.h"
#include "ChaosClothAsset/ClothAsset.h"
#include "ChaosClothAsset/ClothAssetInteractor.h"

AChaosClothDemoActor::AChaosClothDemoActor()
{
    PrimaryActorTick.bCanEverTick = true;

    ClothComponent = CreateDefaultSubobject<UChaosClothComponent>(TEXT("ClothComponent"));
    RootComponent = ClothComponent;
}

void AChaosClothDemoActor::BeginPlay()
{
    Super::BeginPlay();

    // 编辑器中启用模拟以便预览
#if WITH_EDITOR
    ClothComponent->SetSimulateInEditor(true);
#endif
}

void AChaosClothDemoActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    // 运行时动态调整布料参数
    if (UChaosClothAssetInteractor* Interactor = ClothComponent->GetClothOutfitInteractor())
    {
        Interactor->SetFloatPropertyValue(FName("WindSpeed"), -1, CurrentWindSpeed);
    }
}

void AChaosClothDemoActor::SetClothAsset(UChaosClothAssetBase* InAsset)
{
    ClothComponent->SetAsset(InAsset);
}

void AChaosClothDemoActor::SetWindSpeed(float Speed)
{
    CurrentWindSpeed = Speed;
}
```

## 模块依赖

从 `.uplugin` 的 Plugins 字段和源码引用分析，以下是该插件的独特依赖：

| 模块 | 用途 |
|---|---|
| `ChaosCloth` | Chaos 布料物理求解器核心，提供底层模拟引擎 |
| `GeometryCache` | 几何缓存系统，用于存储和回放缓布料几何数据 |
| `Dataflow` | Dataflow 图表系统，用于节点化编辑布料资产 |
| `ClothingSystemRuntimeCommon` | 运行时衣物系统通用框架，提供 `UClothingAssetBase`、`UClothingInteractor` 等基类 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `89e20f15` | [ChaosClothAsset] Preserve the Cloth Component bSimulateInEditor and Asset properties across Bluepri | 蓝图构造脚本重运行时保留布料组件的编辑器模拟和资产属性 |
| 2026-05-26 | `8953a713` | [Cloth] Move parallel cloth simulation wait from EOF to TG_LastDemotable. | 将并行布料模拟等待从帧末移至 TG_LastDemotable 阶段，优化调度 |
| 2026-05-25 | `1db5232a` | [ChaosCloth] Implement RefershBoneMapping for ClothAssetSKMClothingAsset. | 为骨骼网格衣物资产实现骨骼映射刷新功能 |
| 2026-05-22 | `e98c5896` | [Chaos Cloth Asset] Refresh the editor-only Asset alias after a duplicate or paste of an actor. | 复制/粘贴 Actor 后刷新编辑器专用的资产别名 |
| 2026-05-20 | `b9a938ae` | Cleanup Chaos Cloth Asset converter | 清理布料资产转换器代码 |

### 维护评价

- **活跃维护**：最近的提交集中在 2026 年 5 月下旬，更新频率很高（几乎每天都有提交），属于活跃开发状态
- **功能仍在完善**：近期更新涵盖了 Bug 修复（蓝图属性保留）、性能优化（并行模拟调度）和新功能（骨骼映射刷新），说明该插件仍在积极迭代
- **Beta 阶段**：虽然从 Experimental 迁出，但仍标记为 Beta，API 可能会有变化（多个函数和属性已标记 `UE_DEPRECATED`，计划在 5.9 移除旧接口）
- **EnabledByDefault = false**：需要在项目设置中手动启用该插件
- **推荐使用**：如果你的项目需要基于物理的布料模拟，这是 Epic 官方推荐的 Chaos 布料方案。但需注意 API 仍在演进，建议关注版本更新中的废弃标记。截至当前时间（约 2 年历史），插件已从实验阶段进入 Beta，适合在生产项目中评估使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAsset)
- 官方文档（暂无）
- 测试用例（未在插件目录内发现独立测试文件）