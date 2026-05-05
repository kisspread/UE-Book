# Chaos Cloth Asset

> Pattern based cloth asset using the Chaos Cloth simulation.

| 属性 | 值 |
|---|---|
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Dataflow 蓝图资产、Cloth Collection 数据结构） |
| 模块 | `ChaosClothAsset` (Runtime), `ChaosClothAssetEngine` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-10-06 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/ChaosClothAsset) | |

---

## 用途

ChaosClothAsset 是 UE5 基于 Chaos 物理引擎的**新一代布料模拟系统**，替代旧版 UE4 的 Clothing System。它通过 **Dataflow 图形化工作流** 和 **Cloth Collection 数据结构**（基于 `FManagedArrayCollection`）来定义布料的 2D 裁片（Pattern）、3D 模拟网格、缝合线（Seam）、材质属性（Fabric）以及渲染网格。

与旧版布料系统的核心区别：
- **Dataflow 驱动**：布料资产通过 Dataflow 图进行评估和构建，支持可视化节点编辑
- **Pattern-based**：基于服装裁片概念，2D 图案 → 3D 模拟的工作流
- **多 LOD 支持**：每个 Cloth Collection 对应一个 LOD，支持 LOD 过渡
- **ISPC 加速**：模拟数据变换使用 Intel ISPC 并行化（SSE4/AVX/AVX2/AVX512）
- **Outfit 支持**：通过 `UChaosClothAssetBase` 基类支持单件布料和多件套装（Outfit）

### 需要手动启用

此插件 `EnabledByDefault: false`，需要在项目设置中手动启用。同时依赖以下插件：
- **ChaosCloth** — Chaos 布料物理求解器
- **GeometryCache** — 几何缓存支持
- **Dataflow** — 数据流图系统

---

## 使用场景

- 你需要为角色制作逼真的衣服、斗篷、裙子等布料模拟 → 使用 ChaosClothAsset
- 你需要基于 2D 裁片模式制作布料，然后缝合为 3D 服装 → 使用 ChaosClothAsset 的 Pattern + Seam 系统
- 你需要在运行时动态修改布料参数（如风力、重力、材质弹性） → 使用 `UChaosClothAssetInteractor`
- 你需要布料与骨骼网格体碰撞（如衣服与身体的碰撞） → 使用 `AddCollisionSource`
- 你需要布料与环境碰撞（如衣服碰到墙壁） → 使用 `SetCollideWithEnvironment`

---

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetAsset` | 设置布料组件使用的资产（布料资产或套装资产） | `UChaosClothComponent` |
| `GetAsset` | 获取当前布料资产 | `UChaosClothComponent` |
| `ForceNextUpdateTeleport` | 强制下一帧传送布料粒子到新骨骼位置（保持姿态和速度） | `UChaosClothComponent` |
| `ForceNextUpdateTeleportAndReset` | 强制传送并重置姿态和速度 | `UChaosClothComponent` |
| `ResetTeleportMode` | 重置传送模式 | `UChaosClothComponent` |
| `SuspendSimulation` | 暂停布料模拟，保持最后姿态 | `UChaosClothComponent` |
| `ResumeSimulation` | 恢复已暂停的模拟 | `UChaosClothComponent` |
| `IsSimulationSuspended` | 查询模拟是否已暂停 | `UChaosClothComponent` |
| `SetEnableSimulation` | 启用/禁用模拟 | `UChaosClothComponent` |
| `IsSimulationEnabled` | 查询模拟是否已启用 | `UChaosClothComponent` |
| `RecreateClothSimulationProxy` | 硬重置布料模拟（重建代理） | `UChaosClothComponent` |
| `ResetConfigProperties` | 重置所有模拟属性为资产原始值 | `UChaosClothComponent` |
| `GetClothOutfitInteractor` | 获取布料交互器（用于运行时修改参数） | `UChaosClothComponent` |
| `AddCollisionSource` | 添加碰撞源（物理资产 + 骨骼组件） | `UChaosClothComponent` |
| `RemoveCollisionSource` | 移除指定碰撞源 | `UChaosClothComponent` |
| `RemoveCollisionSources` | 移除指定组件的所有碰撞源 | `UChaosClothComponent` |
| `ResetCollisionSources` | 移除所有碰撞源 | `UChaosClothComponent` |
| `SetCollideWithEnvironment` | 启用/禁用环境碰撞 | `UChaosClothComponent` |
| `GetCollideWithEnvironment` | 查询环境碰撞状态 | `UChaosClothComponent` |
| `SetSimulateInEditor` | 设置是否在编辑器中模拟 | `UChaosClothComponent` |
| `ResetRestLengthsWithMorphTarget` | 使用 Morph Target 重置布料静止长度 | `UChaosClothComponent` |

### 布料参数交互器（UChaosClothAssetInteractor）

| 节点 | 说明 |
|---|---|
| `GetAllPropertyNames` | 获取所有属性名称列表 |
| `GetFloatPropertyValue` | 获取浮点属性值 |
| `SetFloatPropertyValue` | 设置浮点属性值（LODIndex=-1 设置所有 LOD） |
| `GetWeightedFloatPropertyValue` | 获取带权重的浮点值（低值+高值） |
| `SetWeightedFloatPropertyValue` | 设置带权重的浮点值 |
| `GetIntPropertyValue` | 获取整数属性值 |
| `SetIntPropertyValue` | 设置整数属性值 |
| `GetVectorPropertyValue` | 获取向量属性值 |
| `SetVectorPropertyValue` | 设置向量属性值 |
| `GetStringPropertyValue` | 获取字符串属性值 |
| `SetStringPropertyValue` | 设置字符串属性值 |

### 使用示例

**设置布料资产并启动模拟：**

1. 在 Actor 上添加 `UChaosClothComponent`
2. 调用 `SetAsset` 节点，传入你的 `UChaosClothAsset` 资产
3. 布料模拟会自动在 Tick 中运行

**运行时修改布料参数（如风力效果）：**

1. 调用 `GetClothOutfitInteractor` 获取交互器
2. 使用交互器的 `SetFloatPropertyValue` 修改参数，如 `SetFloatPropertyValue("WindDragCoefficient", -1, 0.5)`

**布料与角色身体碰撞：**

1. 获取角色的 `USkeletalMeshComponent` 和 `UPhysicsAsset`
2. 调用 `AddCollisionSource(SkeletalMeshComponent, PhysicsAsset, true)` 添加为碰撞源

---

## C++ 用法

### 头文件引入

```cpp
// 布料资产和组件
#include "ChaosClothAsset/ClothAsset.h"
#include "ChaosClothAsset/ClothComponent.h"
#include "ChaosClothAsset/ClothAssetBase.h"

// 布料交互器（运行时参数修改）
#include "ChaosClothAsset/ClothAssetInteractor.h"

// Cloth Collection 数据结构和 Facade
#include "ChaosClothAsset/CollectionClothFacade.h"
#include "ChaosClothAsset/ClothGeometryTools.h"
#include "ChaosClothAsset/ClothEngineTools.h"

// 模拟模型和代理
#include "ChaosClothAsset/ClothSimulationModel.h"
#include "ChaosClothAsset/ClothSimulationProxy.h"
```

### 基本用法：创建和构建 Cloth Asset

从 Cloth Collection 构建布料资产。`FManagedArrayCollection` 是核心数据容器，通过 `FCollectionClothFacade` 进行类型安全的读写。

```cpp
// 来源: ChaosClothAssetEngine/Private/ChaosClothAsset/ClothAsset.cpp
#include "ChaosClothAsset/ClothAsset.h"
#include "ChaosClothAsset/CollectionClothFacade.h"

// 创建 Cloth Collection（每个 LOD 一个）
TSharedRef<FManagedArrayCollection> ClothCollection = MakeShared<FManagedArrayCollection>();

// 使用 Facade 定义 schema 并填充数据
UE::Chaos::ClothAsset::FCollectionClothFacade ClothFacade(ClothCollection);
ClothFacade.DefineSchema();

// 设置 LOD 元数据
ClothFacade.SetPhysicsAssetSoftObjectPathName(PhysicsAssetPath);
ClothFacade.SetSkeletalMeshSoftObjectPathName(SkeletalMeshPath);
ClothFacade.SetReferenceBoneName(FName("pelvis"));

// 设置模拟网格（2D 裁片 + 3D 顶点）
// ... 通过 SimPattern Facade 添加裁片和顶点

// 构建布料资产
TArray<TSharedRef<const FManagedArrayCollection>> ClothCollections;
ClothCollections.Add(ClothCollection);

UChaosClothAsset* ClothAsset = NewObject<UChaosClothAsset>();
ClothAsset->Build(ClothCollections);
```

### 使用 ClothGeometryTools 构建模拟网格

```cpp
// 来源: ChaosClothAsset/Private/ChaosClothAsset/ClothGeometryTools.cpp
#include "ChaosClothAsset/ClothGeometryTools.h"

// 从 DynamicMesh 构建模拟网格
UE::Chaos::ClothAsset::FClothGeometryTools::BuildSimMeshFromDynamicMesh(
    ClothCollection,
    DynamicMesh,
    UVChannelIndex,
    UVScale,
    bAppend,       // 是否追加到现有数据
    bImportNormals,
    &OutSim2DToSourceIndex
);

// 将模拟网格复制为渲染网格
UE::Chaos::ClothAsset::FClothGeometryTools::CopySimMeshToRenderMesh(
    ClothCollection,
    RenderMaterialPath,
    bSingleRenderPattern
);

// 清理和压缩网格数据
UE::Chaos::ClothAsset::FClothGeometryTools::CleanupAndCompactMesh(ClothCollection);
```

### 运行时修改布料参数

```cpp
// 来源: ChaosClothAssetEngine/Private/ChaosClothAsset/ClothAssetInteractor.cpp
#include "ChaosClothAsset/ClothAssetInteractor.h"

// 获取交互器
UChaosClothAssetInteractor* Interactor = ClothComponent->GetClothOutfitInteractor();

// 读取参数
float GravityScale = Interactor->GetFloatPropertyValue(FName("GravityScale"), 0);

// 修改参数（LODIndex=-1 表示所有 LOD）
Interactor->SetFloatPropertyValue(FName("GravityScale"), -1, 0.5f);
Interactor->SetFloatPropertyValue(FName("DragCoefficient"), -1, 0.1f);

// 带权重的浮点值（低值+高值，用于质量加权）
FVector2D Stiffness = Interactor->GetWeightedFloatPropertyValue(FName("EdgeStiffness"), 0);
Interactor->SetWeightedFloatPropertyValue(FName("EdgeStiffness"), -1, FVector2D(0.5f, 1.0f));
```

### 进阶用法：模拟代理和数据流

```cpp
// 来源: ChaosClothAssetEngine/Private/ChaosClothAsset/ClothSimulationProxy.cpp
// FClothSimulationProxy 是布料模拟的核心运行时对象

// 在组件注册时创建模拟代理
// UChaosClothComponent::OnRegister → CreateClothSimulationProxyImpl()

// 模拟 Tick（游戏线程）
// Tick_GameThread → 启动并行模拟任务
// CompleteParallelSimulation_GameThread → 等待完成并读取结果

// 获取模拟结果用于渲染
const TMap<int32, FClothSimulData>& SimData = Proxy->GetCurrentSimulationData_AnyThread();

// 获取模拟统计信息
int32 NumCloths = Proxy->GetNumCloths();
int32 NumDynamicParticles = Proxy->GetNumDynamicParticles();
int32 NumIterations = Proxy->GetNumIterations();
float SimTime = Proxy->GetSimulationTime();
```

### 进阶用法：Cloth Simulation Model

```cpp
// 来源: ChaosClothAssetEngine/Public/ChaosClothAsset/ClothSimulationModel.h
// FChaosClothSimulationModel 包含 LOD 模型数据，传递给求解器创建约束

// 从 Cloth Collection 构建模拟模型
TSharedPtr<FChaosClothSimulationModel> Model = ClothAsset->GetClothSimulationModel();

// 查询 LOD 信息
int32 NumLods = Model->GetNumLods();
int32 NumVerts = Model->GetNumVertices(0);  // LOD 0
int32 NumTris = Model->GetNumTriangles(0);

// 获取几何数据
TConstArrayView<FVector3f> Positions = Model->GetPositions(0);
TConstArrayView<FVector3f> Normals = Model->GetNormals(0);
TConstArrayView<uint32> Indices = Model->GetIndices(0);
TConstArrayView<FVector2f> PatternPositions = Model->GetPatternPositions(0);
```

---

## 架构概览

### 模块划分

```
ChaosClothAsset (Runtime)
├── Cloth Collection 数据结构 (FManagedArrayCollection)
├── Facade 层 (FCollectionClothFacade, FCollectionClothSimPatternFacade 等)
├── ClothGeometryTools — 网格构建和操作工具
└── ClothEngineTools — 依赖 Engine 的工具（Tether 生成、骨骼重映射）

ChaosClothAssetEngine (Runtime)
├── UChaosClothAssetBase — 布料资产基类（支持 Cloth Asset 和 Outfit Asset）
├── UChaosClothAsset — 布料资产实现
├── UChaosClothComponent — 布料模拟组件
├── UChaosClothAssetInteractor — 运行时参数交互器
├── FChaosClothSimulationModel — 模拟模型（LOD 数据）
├── FChaosClothSimulationProxy — 模拟代理（线程间数据共享）
└── ClothSimulationProxy.ispc — ISPC 并行变换内核
```

### Cloth Collection Group 结构

每个 `FManagedArrayCollection` 代表一个 LOD，包含以下 Group：

| Group | 说明 |
|---|---|
| `Lods` | LOD 元数据（骨骼网格路径、物理资产路径、参考骨骼） |
| `Solvers` | 求解器参数（重力、空气阻尼、时间步长、子步数） |
| `SimVertices2D` | 2D 模拟顶点（裁片空间坐标） |
| `SimVertices3D` | 3D 模拟顶点（世界空间坐标、法线、蒙皮权重） |
| `SimFaces` | 模拟三角面（2D 和 3D 索引） |
| `SimPatterns` | 模拟裁片（引用顶点和面的范围） |
| `RenderVertices` | 渲染顶点（位置、法线、UV、颜色、蒙皮权重、Deformer 数据） |
| `RenderFaces` | 渲染三角面 |
| `RenderPatterns` | 渲染裁片（材质引用、Deformer 影响数） |
| `Seams` | 缝合线（连接不同裁片的缝合关系） |
| `SeamStitches` | 缝合点对（2D 顶点的配对关系） |
| `Fabrics` | 材质参数（弹性、阻尼等物理属性） |
| `SimMorphTargets` | 模拟 Morph Target（用于修改静止长度等） |
| `SimMorphTargetVertices` | Morph Target 顶点数据 |
| `SimAccessoryMeshes` | 附件网格（用于多件式服装组合） |
| `CustomResizingRegions` | 自定义缩放区域 |

### 类继承关系

```
USkinnedAsset
└── UChaosClothAssetBase (IDataflowContentOwner, IDataflowInstanceInterface)
    ├── UChaosClothAsset          — 单件布料资产
    └── (UChaosClothOutfitAsset)  — 套装资产（在 ChaosClothAssetOutfit 插件中）

USkinnedMeshComponent
└── UChaosClothComponent (IDataflowPhysicsSolverInterface, IClothComponentAdapter)
```

### 模拟管线

```
UChaosClothComponent::TickComponent
  ├── FClothSimulationProxy::Tick_GameThread
  │   ├── PreProcess_GameThread — 准备上下文、LOD 切换、Teleport 检测
  │   ├── PreSimulate_GameThread — 写入模拟数据
  │   ├── [并行任务] Tick() — Chaos 求解器推进模拟
  │   ├── PostSimulate_GameThread — 读取模拟结果
  │   └── PostProcess_GameThread — 更新组件
  └── UpdateComponentSpaceTransforms — 应用模拟结果到骨骼变换
```

---

## Demo 示例

### Build.cs 依赖配置

```csharp
// MyModule.Build.cs
public MyModule : ModuleRules
{
    public MyModule(ReadOnlyTargetRules Target) : base(Target)
    {
        PublicDependencyModuleNames.AddRange(new string[]
        {
            "Core",
            "CoreUObject",
            "Engine",
            "ChaosClothAssetEngine",  // 布料资产引擎
            "ChaosClothAsset",        // 布料数据结构
        });
    }
}
```

### 最小示例：程序化创建布料组件

```cpp
// MyClothActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "MyClothActor.generated.h"

class UChaosClothComponent;
class UChaosClothAsset;

UCLASS()
class AMyClothActor : public AActor
{
    GENERATED_BODY()
public:
    AMyClothActor();

    UPROPERTY(VisibleAnywhere)
    UChaosClothComponent* ClothComponent;

    UPROPERTY(EditAnywhere)
    UChaosClothAsset* ClothAsset;
};

// MyClothActor.cpp
#include "MyClothActor.h"
#include "ChaosClothAsset/ClothComponent.h"
#include "ChaosClothAsset/ClothAsset.h"

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
    }
}
```

---

## 模块依赖

### ChaosClothAsset 模块

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心库 |
| `CoreUObject` | UObject 系统 |
| `GeometryCore` | 几何数据结构（FDynamicMesh3） |
| `MeshConversion` | 网格格式转换 |
| `ClothingSystemRuntimeCommon` | 通用布料运行时（FClothVertBoneData 等） |
| `RenderCore` | 渲染核心 |

### ChaosClothAssetEngine 模块

| 模块 | 用途 |
|---|---|
| `DataflowCore` | Dataflow 核心框架 |
| `DataflowEngine` | Dataflow 引擎 |
| `DataflowSimulation` | Dataflow 模拟接口 |
| `ClothingSystemRuntimeCommon` | 通用布料运行时 |
| `ChaosClothAsset` | 布料数据结构模块 |
| `ChaosCloth` | Chaos 布料物理求解器 |
| `ChaosCaching` | Chaos 缓存（录制/回放） |
| `ClothingSystemRuntimeInterface` | 布料系统运行时接口 |
| `PropertyEditor` (Editor only) | 详情面板 UI 扩展 |

---

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-11-18 | `86e950b0bec0` | 修复导入模拟 Morph Target 时的崩溃 |
| 2025-10-03 | `188d475e494b` | 修复 USD 布料 Turned Sewing 导入未添加对应弹簧的问题 |
| 2025-10-02 | `7a5a0b9c6bde` | 将基于字符串的 ClothAssetInteractor 方法标记为废弃 |

### 维护评价

- **状态**：🟢 **活跃维护**
- **创建时间**：2022 年 10 月（从 Experimental 迁移到正式插件目录）
- **最近更新**：2025 年 11 月，持续有功能性更新和 Bug 修复
- **API 演进**：API 在快速演进中，大量方法在 5.4-5.7 期间被废弃并替换
- **IsBetaVersion**：仍标记为 Beta，说明 Epic 认为此系统尚未完全稳定
- **推荐**：✅ **推荐使用**。这是 Epic 官方的新一代布料系统，是 UE4 Clothing System 的正式替代。虽然 API 仍在变化，但它是唯一受支持的 Chaos 布料工作流。
- **注意事项**：
  - `EnabledByDefault: false`，需要手动启用
  - API 废弃较快，升级引擎版本时需关注 deprecation warnings
  - 与旧版 Clothing System 不兼容，不能直接迁移

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/ChaosClothAsset)
- [官方文档]()（.uplugin 中未提供 DocsURL）
- 相关插件：
  - [ChaosCloth](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosCloth) — Chaos 布物理求解器
  - [ChaosClothEditor](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/ChaosClothEditor) — 布料编辑器 UI
  - [Dataflow](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Dataflow) — 数据流图系统
