# Chaos Cloth Asset

> Pattern based cloth asset using the Chaos Cloth simulation.

| 属性 | 值 |
|---|---|
| 中文名 | 混沌布料资产 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、Dataflow 节点） |
| 模块 | `ChaosClothAsset` (Runtime), `ChaosClothAssetEngine` (Runtime), `ChaosClothAssetTools` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-03-22 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAsset) | |

---

## 用途

ChaosClothAsset 是 UE5 新一代基于裁片（Pattern）的布料模拟资产系统，替代了旧版 ApexCloth 工作流。它将布料的几何数据、模拟参数和渲染数据统一存储在 `UChaosClothAsset` / `UChaosOutfitAsset` 资产中，通过 Dataflow 图驱动整个布料资产的构建流程。

核心解决的问题：
- **裁片驱动布料**：支持从 2D 裁片图案（Pattern）构建 3D 布料网格，更贴近真实服装生产流程
- **Dataflow 集成**：用可视化节点图处理布料数据的导入、修改、合并和优化
- **Outfit 系统**：一套完整的服装可以包含多块独立布料（上衣、裙子、袖子等），各自有独立的模拟参数和 LOD
- **与 Skeletal Mesh 无缝集成**：通过 `UChaosClothAssetSKMClothingAsset` 作为传统 Clothing Data 的桥梁，使布料资产可直接挂载到骨骼网格体上模拟
- **运行时属性交互**：通过 `UChaosClothAssetInteractor` 在运行时动态修改布料模拟参数（如风力、重力、刚度等）

## 使用场景

- 你在做一个需要角色服装模拟的游戏（如 RPG、换装系统）→ 用 ChaosClothAsset + OutfitAsset
- 你需要基于 2D 裁片图案制作布料 → 用 Dataflow 图编辑裁片 → 构建 ClothAsset
- 你需要在运行时根据游戏状态调整布料参数（如风吹、浸水效果）→ 用 ClothAssetInteractor
- 你需要让多个布件（袖子、裙摆）共享同一套骨骼模拟 → 用 OutfitAsset 组合多个 ClothSimulationModel
- 你需要将布料模拟缓存用于回放 → 用 Chaos Cache + ClothComponentCacheAdapter

---

## 架构概览

```
┌─────────────────────────────────────────────────────────────────┐
│                      UChaosClothAssetBase                       │
│  (USkinnedAsset 子类，公共基类)                                  │
├──────────────────────┬──────────────────────────────────────────┤
│   UChaosClothAsset   │     UChaosOutfitAsset (Outfit插件)       │
│   (单块布料)          │     (多块布料组合)                        │
└──────────┬───────────┴──────────────────────────────────────────┘
           │
           ▼
┌──────────────────────┐     ┌──────────────────────────────────┐
│ FChaosClothSimModel  │────▶│  FClothSimulationMesh (内部)      │
│ (LOD数据+蒙皮信息)   │     │  (Chaos求解器适配)                │
└──────────────────────┘     └──────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   UChaosClothComponent                           │
│  (USkinnedMeshComponent 子类，驱动模拟)                          │
│  ┌────────────────────┐  ┌──────────────────────────────────┐  │
│  │ FClothSimProxy     │  │ UChaosClothAssetInteractor       │  │
│  │ (并行模拟代理)      │  │ (运行时属性交互器)               │  │
│  └────────────────────┘  └──────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

**模块职责**：
| 模块 | 职责 |
|---|---|
| **ChaosClothAssetEngine** | 资产定义（ClothAssetBase/ClothAsset）、组件（ClothComponent）、交互器（Interactor）、模拟模型 |
| **ChaosClothAsset** | Chaos 求解器适配层（SimulationProxy/Mesh/Context）、碰撞源、缓存适配器 |
| **ChaosClothAssetTools** | Dataflow 节点、编辑器工具（仅 Win64/Mac/Linux） |

---

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetAsset` | 设置布料组件使用的资产（ClothAsset 或 OutfitAsset） | `UChaosClothComponent` |
| `GetAsset` | 获取当前绑定的布料资产 | `UChaosClothComponent` |
| `ForceNextUpdateTeleport` | 强制下一帧传送布料到新骨骼位置（保留姿态和速度） | `UChaosClothComponent` |
| `ForceNextUpdateTeleportAndReset` | 强制传送并重置布料姿态和速度 | `UChaosClothComponent` |
| `SuspendSimulation` | 暂停模拟，保持当前姿态 | `UChaosClothComponent` |
| `ResumeSimulation` | 恢复已暂停的模拟 | `UChaosClothComponent` |
| `SetEnableSimulation` | 启用/禁用模拟 | `UChaosClothComponent` |
| `IsSimulationEnabled` | 查询模拟是否启用 | `UChaosClothComponent` |
| `IsSimulationSuspended` | 查询模拟是否暂停 | `UChaosClothComponent` |
| `ResetConfigProperties` | 重置所有配置属性为资产原始值 | `UChaosClothComponent` |
| `RecreateClothSimulationProxy` | 硬重置：重新创建模拟代理 | `UChaosClothComponent` |
| `GetClothOutfitInteractor` | 获取布料交互器（用于运行时修改属性） | `UChaosClothComponent` |
| `AddCollisionSource` | 添加外部碰撞源（物理资产 + 骨骼网格体组件） | `UChaosClothComponent` |
| `RemoveCollisionSource` | 移除指定碰撞源 | `UChaosClothComponent` |
| `ResetCollisionSources` | 移除所有碰撞源 | `UChaosClothComponent` |
| `SetCollideWithEnvironment` | 设置是否与环境碰撞 | `UChaosClothComponent` |
| `SetSimulateInEditor` | 在编辑器中启用模拟（仅编辑器） | `UChaosClothComponent` |
| `SetOverlayMaterial` | 设置默认覆盖材质 | `UChaosClothAssetBase` |
| `SetOverlayMaterialMaxDrawDistance` | 设置覆盖材质最大绘制距离 | `UChaosClothAssetBase` |

### 交互器节点（ClothAssetInteractor）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetAllPropertyNames` | 获取所有属性名称列表 | `UChaosClothAssetInteractor` |
| `GetFloatPropertyValue` | 获取浮点属性值 | `UChaosClothAssetInteractor` |
| `GetWeightedFloatPropertyValue` | 获取带权重浮点属性（低/高值） | `UChaosClothAssetInteractor` |
| `GetIntPropertyValue` | 获取整数属性值 | `UChaosClothAssetInteractor` |
| `GetVectorPropertyValue` | 获取向量属性值 | `UChaosClothAssetInteractor` |
| `GetStringPropertyValue` | 获取字符串属性值 | `UChaosClothAssetInteractor` |
| `SetFloatPropertyValue` | 设置浮点属性值（所有 LOD） | `UChaosClothAssetInteractor` |
| `SetWeightedFloatPropertyValue` | 设置带权重浮点属性 | `UChaosClothAssetInteractor` |
| `SetIntPropertyValue` | 设置整数属性值 | `UChaosClothAssetInteractor` |
| `SetVectorPropertyValue` | 设置向量属性值 | `UChaosClothAssetInteractor` |
| `SetStringPropertyValue` | 设置字符串属性值 | `UChaosClothAssetInteractor` |
| `SetPropertySet` | 从数据资产批量设置属性组 | `UChaosClothAssetInteractor` |

### 使用示例

**基本布料组件设置**：
1. 在 Actor 上添加 `Chaos Cloth Component`
2. 调用 `SetAsset` 节点，传入已创建的 `ChaosClothAsset`
3. 组件会在 `OnRegister` 时自动创建模拟代理并开始模拟

**运行时修改布料参数**：
1. 通过 `GetClothOutfitInteractor` 获取交互器对象
2. 交互器内部已绑定到当前资产的属性集合
3. 调用 `SetFloatPropertyValue` 修改具体属性（如 `WindDragCoefficient`）
4. 属性修改会在下一帧同步到模拟线程

**添加外部碰撞**：
1. 获取角色的 `PhysicsAsset`（如胶囊体碰撞）
2. 获取角色的 `SkeletalMeshComponent`
3. 调用 `AddCollisionSource`，传入源组件和物理资产
4. 布料模拟会自动将这些碰撞形状纳入计算

**传送与重置**：
1. 角色瞬移时调用 `ForceNextUpdateTeleportAndReset`
2. 布料粒子会被传送至新骨骼位置并重置速度
3. 或设置 `TeleportDistanceThreshold` / `TeleportRotationThreshold` 让组件自动检测传送

---

## C++ 用法

### 头文件引入

```cpp
// 引擎核心模块
#include "ChaosClothAsset/ClothAsset.h"
#include "ChaosClothAsset/ClothAssetBase.h"
#include "ChaosClothAsset/ClothComponent.h"
#include "ChaosClothAsset/ClothAssetInteractor.h"
#include "ChaosClothAsset/ClothSimulationModel.h"
#include "ChaosClothAsset/ClothEngineTools.h"

// 模拟代理（内部/高级用法）
#include "ChaosClothAsset/ClothSimulationProxy.h"
```

### 基本用法

**获取布料模拟模型数据**（来源：`ClothAsset.h` 中 `GetClothSimulationModel`）

```cpp
// 获取 ClothAsset 并查询其模拟模型
UChaosClothAsset* ClothAsset = /* 从资产加载 */;

if (ClothAsset->HasValidClothSimulationModels())
{
    TSharedPtr<const FChaosClothSimulationModel> SimModel = ClothAsset->GetClothSimulationModel(0);
    
    // 查询 LOD 数量
    int32 NumLods = SimModel->GetNumLods();
    
    // 获取 LOD 0 的顶点数据
    int32 NumVertices = SimModel->GetNumVertices(0);
    TConstArrayView<FVector3f> Positions = SimModel->GetPositions(0);
    TConstArrayView<FVector3f> Normals = SimModel->GetNormals(0);
    TConstArrayView<uint32> Indices = SimModel->GetIndices(0);
}
```

**运行时通过交互器修改布料属性**（来源：`ClothAssetInteractor.h`）

```cpp
// 获取组件
UChaosClothComponent* ClothComp = /* 从 Actor 获取 */;

// 获取交互器
UChaosClothAssetInteractor* Interactor = ClothComp->GetClothOutfitInteractor(0);

if (Interactor)
{
    // 获取所有可修改属性名
    TArray<FName> PropertyNames = Interactor->GetAllPropertyNames(0);
    
    // 读取当前风阻系数
    float WindDrag = Interactor->GetFloatPropertyValue(
        FName("WindDragCoefficient"),  /* LODIndex */ 0, /* Default */ 0.f);
    
    // 修改风阻系数（LODIndex=-1 表示设置所有 LOD）
    Interactor->SetFloatPropertyValue(
        FName("WindDragCoefficient"), /* LODIndex */ -1, /* Value */ 1.5f);
    
    // 设置带权重的属性（低值/高值范围）
    Interactor->SetWeightedFloatPropertyValue(
        FName("GravityScale"), -1, FVector2D(0.8f, 1.2f));
    
    // 批量设置属性（从数据资产）
    // UClothAssetInteractorDataAsset* DataAsset = ...;
    // Interactor->SetPropertySet(DataAsset->GetPropertySet("Windy"), 0);
}
```

**编程式创建和注册布料组件**（来源：`ClothComponent.h`）

```cpp
// 在 Actor 中创建布料组件
UChaosClothComponent* ClothComp = NewObject<UChaosClothComponent>(MyActor);
ClothComp->SetAsset(MyClothAsset);

// 配置模拟参数
ClothComp->SetClothGeometryScale(1.0f);  // 布料几何缩放
ClothComp->SetEnableSimulation(true);     // 启用模拟
ClothComp->SetCollideWithEnvironment(true); // 与环境碰撞

// 传送阈值设置
ClothComp->SetTeleportDistanceThreshold(200.f);  // 位移超过 200 自动传送
ClothComp->SetTeleportRotationThreshold(90.f);   // 旋转超过 90° 自动传送

// 注册组件使其开始模拟
ClothComp->RegisterComponent();
```

### 进阶用法

**添加跨组件碰撞**（来源：`ClothComponent.h` 的 `AddCollisionSource`）

```cpp
// 布料需要与角色躯干碰撞
UChaosClothComponent* ClothComp = GetClothComponent();
USkeletalMeshComponent* BodyComp = GetBodySkeletalMeshComponent();
UPhysicsAsset* BodyPhysicsAsset = BodyComp->GetSkinnedAsset()->GetPhysicsAsset();

// 添加碰撞源（使用球体和胶囊体）
ClothComp->AddCollisionSource(BodyComp, BodyPhysicsAsset, /* bUseSphylsOnly */ true);

// 清除所有碰撞源
ClothComp->ResetCollisionSources();
```

**使用 ClothSimulationModel 进行骨骼重映射**（来源：`ClothSimulationModel.h`）

```cpp
// 当多个布料资产需要合并使用不同骨骼时
FChaosClothSimulationModel* SimModel = /* 获取 */;

// 计算两个布料是否骨骼兼容
FCollectionClothConstFacade Cloth1Facade = /* ... */;
FCollectionClothConstFacade Cloth2Facade = /* ... */;
FSoftObjectPath MergedSkeletalMeshPath;
TArray<int32> Remap1, Remap2;

bool bCompatible = FClothEngineTools::CalculateRemappedBoneIndicesIfCompatible(
    Cloth1Facade, Cloth2Facade,
    MergedSkeletalMeshPath, Remap1, Remap2);

if (bCompatible)
{
    // 重映射骨骼索引
    FCollectionClothFacade TargetCloth = /* ... */;
    FClothEngineTools::RemapBoneIndices(TargetCloth, Remap2);
    
    // 或在模型级别重映射
    SimModel->RemapBoneIndices(Remap1);
}
```

**直接操作模拟代理（高级）**（来源：`ClothSimulationProxy.h`）

```cpp
// 在自定义 Tick 逻辑中分步控制模拟
FClothSimulationProxy* Proxy = ClothComp->GetClothSimulationProxy();

if (Proxy && Proxy->IsParallelSimulationTaskValid())
{
    // 等待并行模拟完成
    Proxy->CompleteParallelSimulation_GameThread();
    
    // 获取模拟结果
    const TMap<int32, FClothSimulData>& SimData = 
        Proxy->GetCurrentSimulationData_AnyThread();
    
    // 查询模拟统计信息
    int32 NumCloths = Proxy->GetNumCloths();
    int32 NumDynamicParticles = Proxy->GetNumDynamicParticles();
    float SimTime = Proxy->GetSimulationTime();
}
```

**Skeletal Mesh 路径集成**（来源：`ClothAssetSKMClothingAsset.h`）

```cpp
// 通过传统 Clothing 系统使用 Chaos Cloth Asset
// (在编辑器中自动完成，以下展示编程方式)
UChaosClothAssetSKMClothingAsset* ClothingAsset = /* 从 SkeletalMesh 的 clothing data 获取 */;
const UChaosClothAssetBase* ClothBase = ClothingAsset->GetAsset();
int32 ModelIndex = ClothingAsset->GetClothSimulationModelIndex();

// 检查是否有有效的模拟数据
bool bHasData = ClothingAsset->HasAnySimulationMeshData(/* LODIndex */ 0);
```

---

## Demo 示例

### 最小可运行的布料组件 Actor

```cpp
// ClothDemoActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "ClothDemoActor.generated.h"

class UChaosClothComponent;
class UChaosClothAsset;

UCLASS(BlueprintType)
class AClothDemoActor : public AActor
{
    GENERATED_BODY()
    
public:
    AClothDemoActor();
    
    virtual void BeginPlay() override;
    
    /** 布料资产（在编辑器中设置） */
    UPROPERTY(EditAnywhere, Category = "Cloth Demo")
    TObjectPtr<UChaosClothAsset> ClothAsset;
    
    /** 布料组件 */
    UPROPERTY(VisibleAnywhere, Category = "Cloth Demo")
    TObjectPtr<UChaosClothComponent> ClothComponent;
    
    /** 风力大小 */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Cloth Demo|Wind")
    float WindStrength = 50.f;
    
    /** 应用风力设置到布料 */
    UFUNCTION(BlueprintCallable, Category = "Cloth Demo")
    void ApplyWindSettings();
};
```

```cpp
// ClothDemoActor.cpp
#include "ClothDemoActor.h"
#include "ChaosClothAsset/ClothAsset.h"
#include "ChaosClothAsset/ClothComponent.h"
#include "ChaosClothAsset/ClothAssetInteractor.h"

AClothDemoActor::AClothDemoActor()
{
    PrimaryActorTick.bCanEverTick = true;
    
    // 创建布料组件
    ClothComponent = CreateDefaultSubobject<UChaosClothComponent>(
        TEXT("ClothComponent"));
    RootComponent = ClothComponent;
}

void AClothDemoActor::BeginPlay()
{
    Super::BeginPlay();
    
    // 设置布料资产
    if (ClothAsset)
    {
        ClothComponent->SetAsset(ClothAsset);
    }
    
    // 启用模拟与环境碰撞
    ClothComponent->SetEnableSimulation(true);
    ClothComponent->SetCollideWithEnvironment(true);
    
    // 应用初始风力设置
    ApplyWindSettings();
}

void AClothDemoActor::ApplyWindSettings()
{
    UChaosClothAssetInteractor* Interactor = 
        ClothComponent->GetClothOutfitInteractor();
    
    if (!Interactor)
    {
        return;
    }
    
    // 设置风速（WindSpeed 是 ChaosCloth 的标准属性名）
    Interactor->SetVectorPropertyValue(
        FName("WindSpeed"), 
        /* LODIndex */ -1,  // 所有 LOD
        FVector(WindStrength, 0.f, 0.f));
    
    // 设置风阻系数
    Interactor->SetFloatPropertyValue(
        FName("WindDragCoefficient"), -1, 0.07f);
    
    // 设置风力提升系数（模拟风中飘扬效果）
    Interactor->SetFloatPropertyValue(
        FName("WindLiftCoefficient"), -1, 0.03f);
}
```

---

## 模块依赖

从 Build.cs 提取的依赖关系（省略常见依赖）：

| 模块 | 用途 |
|---|---|
| `ChaosCloth` | Chaos 布料物理模拟核心 |
| `ChaosSolverEngine` | Chaos 物理求解器 |
| `Dataflow` | Dataflow 可视化节点图框架 |
| `GeometryFramework` | 几何处理框架 |
| `PropertyBag` | 属性袋系统（用于 InteractorPropertyBag） |
| `MeshConversion` | 网格转换工具 |
| `Chaos` | Chaos 物理引擎核心 |

插件依赖：
| 插件 | 用途 |
|---|---|
| `ChaosCloth` | 底层布料求解器 |
| `GeometryCache` | 几何缓存支持 |
| `Dataflow` | Dataflow 图编辑器和运行时 |

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `89e20f15` | [ChaosClothAsset] Preserve the Cloth Component bSimulateInEditor and Asset properties across Blueprint construction script reruns | 修复蓝图构造脚本重运行时丢失布料组件的模拟和资产设置 |
| 2026-05-26 | `8953a713` | [Cloth] Move parallel cloth simulation wait from EOF to TG_LastDemotable | 将并行布料模拟等待从帧末移至 TG_LastDemotable TickGroup |
| 2026-05-25 | `1db5232a` | [ChaosCloth] Implement RefershBoneMapping for ClothAssetSKMClothingAsset | 实现 ClothAssetSKMClothingAsset 的骨骼映射刷新 |
| 2026-05-22 | `e98c5896` | [Chaos Cloth Asset] Refresh the editor-only Asset alias after a duplicate or paste of an actor | 修复复制粘贴 Actor 后编辑器中资产引用不更新的问题 |
| 2026-05-20 | `b9a938ae` | Cleanup Chaos Cloth Asset converter | 清理布料资产转换器代码 |

### 维护评价

- **状态**：⚠️ Beta（从 Experimental 迁移，标记为 Beta）
- **活跃度**：**高度活跃**。最近 5 次提交集中在 2026 年 5 月，每周都有实质性改进（bug 修复、性能优化、蓝图兼容性提升）
- **创建时间**：2024 年 3 月（约 2 年），正处于快速迭代期
- **代码质量**：代码注释完善，有清晰的接口定义（`IClothComponentAdapter`），遵循 UE 的异步构建安全模式（`WaitUntilAsyncPropertyReleased`）
- **已知限制**：
  - 需要手动启用（`EnabledByDefault = false`）
  - ChaosClothAssetTools 仅支持 Win64/Mac/Linux
  - 部分旧 API 已标记 `UE_DEPRECATED`（5.6/5.7），迁移时注意
  - OutfitAsset 在本插件文档范围之外（位于独立插件）
- **推荐使用**：**推荐用于新项目**。作为 ApexCloth 的替代方案，提供更完整的 Dataflow 工作流和运行时交互能力。但鉴于 Beta 状态，API 可能仍有变动，需关注 deprecation 警告。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAsset)
- [ChaosCloth 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosCloth)（底层求解器）
- [Dataflow 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Dataflow)（可视化节点图）