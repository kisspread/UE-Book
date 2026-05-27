# Chaos Cloth Asset

> Pattern based cloth asset using the Chaos Cloth simulation.

| 属性 | 值 |
|---|---|
| 中文名 | 混沌布料资产 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（布料资产数据、Dataflow 节点） |
| 模块 | `ChaosClothAsset` (Runtime), `ChaosClothAssetEngine` (Runtime), `ChaosClothAssetTools` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-03-22 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAsset) | |

## 用途

ChaosClothAsset 是 UE5 新一代基于**布料裁片（Pattern）** 的布料资产系统，取代了旧版 Cloth 驱动方式。它基于 Chaos 物理引擎进行布料模拟，将布料数据组织为一个结构化的 `FManagedArrayCollection`，包含：

- **2D 裁片（Sim Pattern）**：定义布料在平面上的展开形状，用于物理模拟
- **3D 模拟网格（Sim Vertices/Faces 3D）**：在 3D 空间中对应的模拟拓扑
- **渲染网格（Render Mesh）**：最终显示的高精度渲染网格，通过 Proxy Deformer 映射到模拟结果
- **缝合线（Seams）**：连接不同裁片的 2D 顶点对
- **面料材质（Fabric）**：弯曲刚度、拉伸刚度、密度、摩擦力等物理参数
- **变形目标（Morph Targets）**：模拟网格的变形目标支持
- **配属网格（Accessory Meshes）**：附加的模拟网格
- **权重图（Weight Maps）**：MaxDistance、Backstop 等控制约束的权重
- **自定义区域缩放（Resizing）**：针对不同身体部位的缩放控制

这个插件解决的核心问题是：**让布料资产从"绑定到骨骼网格的单一数据"升级为"包含完整裁片信息、可独立编辑、支持 Dataflow 工作流的结构化资产"**。它从 5.4 的 Experimental 目录迁移出来，标记为 Beta，表明 Epic 正在将其作为官方布料解决方案推进。

## 使用场景

- 你需要制作角色服装的物理模拟 → 使用 ChaosClothAsset 定义裁片和面料属性
- 你需要将布料数据通过 Dataflow 节点管线进行程序化生成/修改 → 依赖 Dataflow 插件
- 你需要在编辑器中通过 ChaosClothAssetTools 模块编辑布料资产 → 该模块仅限 Win64/Mac/Linux
- 你需要将布料模拟结果映射到高精度渲染网格 → 使用 Proxy Deformer 机制

## 蓝图用法

本插件主要面向 C++ 和编辑器工具层，公开的蓝图 API 有限。大部分核心功能通过 Dataflow 节点和编辑器工具暴露。

### 核心节点

本插件的核心 API 以 C++ Facade 类为主，不直接暴露大量 `BlueprintCallable` 函数。蓝图层面的布料资产操作主要通过 ChaosClothAssetTools（编辑器模块）和 Dataflow 节点实现。

## C++ 用法

### 头文件引入

```cpp
#include "ChaosClothAsset/CollectionClothFacade.h"
#include "ChaosClothAsset/ClothGeometryTools.h"
#include "ChaosClothAsset/CollectionClothSelectionFacade.h"
```

### 基本用法

**创建和初始化布料集合 Facade**

```cpp
// 来源: Public/ChaosClothAsset/CollectionClothFacade.h
using namespace UE::Chaos::ClothAsset;

// 创建一个 ManagedArrayCollection（通常来自 UChaosClothAsset 的数据）
TSharedRef<FManagedArrayCollection> ManagedArrayCollection = MakeShared<FManagedArrayCollection>();

// 创建可写的布料 Facade
FCollectionClothFacade ClothFacade(ManagedArrayCollection);

// 定义布料数据的 Schema（初始化所有必要的属性和组）
ClothFacade.DefineSchema();

// 设置全局物理资产和骨骼网格引用
ClothFacade.SetPhysicsAssetSoftObjectPathName(FSoftObjectPath(TEXT("/Game/Characters/PhysicsAsset.PhysicsAsset")));
ClothFacade.SetSkeletalMeshSoftObjectPathName(FSoftObjectPath(TEXT("/Game/Characters/SK_Character.SK_Character")));
ClothFacade.SetReferenceBoneName(FName("pelvis"));

// 设置求解器参数
ClothFacade.SetSolverGravity(FVector3f(0.0f, 0.0f, -980.665f));
ClothFacade.SetSolverAirDamping(0.035f);
ClothFacade.SetSolverSubSteps(1);
ClothFacade.SetSolverTimeStep(0.033f);
```

**添加面料材质（Fabric）**

```cpp
// 来源: Public/ChaosClothAsset/CollectionClothFabricFacade.h
// 添加面料并设置物理参数
int32 FabricIndex = ClothFacade.AddFabric();
FCollectionClothFabricFacade FabricFacade = ClothFacade.GetFabric(FabricIndex);

// 使用各向异性数据初始化面料
FCollectionClothFabricConstFacade::FAnisotropicData BendingStiffness(100.0f, 100.0f, 100.0f);
FCollectionClothFabricConstFacade::FAnisotropicData BucklingStiffness(50.0f, 50.0f, 50.0f);
FCollectionClothFabricConstFacade::FAnisotropicData StretchStiffness(100.0f, 100.0f, 100.0f);

FabricFacade.Initialize(
    BendingStiffness, 0.5f /*BucklingRatio*/, BucklingStiffness,
    StretchStiffness, 0.35f /*Density*/, 0.8f /*Friction*/, 0.1f /*Damping*/,
    0.0f /*Pressure*/, INDEX_NONE /*Layer*/, 1.0f /*CollisionThickness*/
);
```

**添加模拟裁片（Sim Pattern）**

```cpp
// 来源: Public/ChaosClothAsset/CollectionClothSimPatternFacade.h
int32 PatternIndex = ClothFacade.AddSimPattern();
FCollectionClothSimPatternFacade PatternFacade = ClothFacade.GetSimPattern(PatternIndex);

// 使用 2D 位置、3D 位置和三角形索引初始化裁片
TArray<FVector2f> Positions2D = { FVector2f(0, 0), FVector2f(1, 0), FVector2f(0, 1) };
TArray<FVector3f> Positions3D = { FVector3f(0, 0, 0), FVector3f(1, 0, 0), FVector3f(0, 0, 1) };
TArray<FIntVector3> Indices = { FIntVector3(0, 1, 2) };

PatternFacade.Initialize(Positions2D, Positions3D, Indices, FabricIndex);

// 为该裁片设置对应的面料索引
PatternFacade.SetFabricIndex(FabricIndex);
```

**添加缝合线（Seam）**

```cpp
// 来源: Public/ChaosClothAsset/CollectionClothSeamFacade.h
int32 SeamIndex = ClothFacade.AddSeam();
FCollectionClothSeamFacade SeamFacade = ClothFacade.GetSeam(SeamIndex);

// 初始化缝合线：每对索引 (A, B) 表示两个 2D 顶点被缝合
TArray<FIntVector2> Stitches = { FIntVector2(0, 5), FIntVector2(1, 4), FIntVector2(2, 3) };
SeamFacade.Initialize(Stitches);
```

### 进阶用法

**使用 ClothGeometryTools 进行网格操作**

```cpp
// 来源: Public/ChaosClothAsset/ClothGeometryTools.h
using namespace UE::Chaos::ClothAsset;

// 检查是否有模拟/渲染网格
bool bHasSim = FClothGeometryTools::HasSimMesh(ManagedArrayCollection);
bool bHasRender = FClothGeometryTools::HasRenderMesh(ManagedArrayCollection);

// 将模拟网格复制为渲染网格
FClothGeometryTools::CopySimMeshToRenderMesh(
    ManagedArrayCollection,
    FSoftObjectPath(TEXT("/Game/Materials/M_Cloth.M_Cloth")),
    false /*bSingleRenderPattern*/);

// 清理退化三角形和无效数据
FClothGeometryTools::CleanupAndCompactMesh(ManagedArrayCollection);

// 应用 Proxy Deformer 将模拟结果映射到渲染网格
FClothGeometryTools::ApplyProxyDeformer(ManagedArrayCollection, false /*bIgnoreSkinningBlend*/);
```

**使用 Facade 读取布料数据（只读模式）**

```cpp
// 来源: Public/ChaosClothAsset/CollectionClothFacade.h
// 创建只读 Facade
FCollectionClothConstFacade ConstClothFacade(ManagedArrayCollection);

// 获取模拟数据概况
int32 NumSimVertices2D = ConstClothFacade.GetNumSimVertices2D();
int32 NumSimVertices3D = ConstClothFacade.GetNumSimVertices3D();
int32 NumSimFaces = ConstClothFacade.GetNumSimFaces();
int32 NumRenderVertices = ConstClothFacade.GetNumRenderVertices();

// 获取模拟顶点数据
TConstArrayView<FVector3f> SimPositions = ConstClothFacade.GetSimPosition3D();
TConstArrayView<FVector3f> SimNormals = ConstClothFacade.GetSimNormal();
TConstArrayView<TArray<int32>> SimBoneIndices = ConstClothFacade.GetSimBoneIndices();
TConstArrayView<TArray<float>> SimBoneWeights = ConstClothFacade.GetSimBoneWeights();

// 获取渲染网格数据
TConstArrayView<FVector3f> RenderPositions = ConstClothFacade.GetRenderPosition();
TConstArrayView<FVector3f> RenderNormals = ConstClothFacade.GetRenderNormal();
TConstArrayView<TArray<FVector2f>> RenderUVs = ConstClothFacade.GetRenderUVs();

// 遍历裁片
for (int32 i = 0; i < ConstClothFacade.GetNumSimPatterns(); ++i)
{
    FCollectionClothSimPatternConstFacade Pattern = ConstClothFacade.GetSimPattern(i);
    int32 NumVertices = Pattern.GetNumSimVertices2D();
    int32 NumFaces = Pattern.GetNumSimFaces();
    TConstArrayView<FVector2f> UV2D = Pattern.GetSimPosition2D();
    // ...处理裁片数据
}

// 遍历面料
for (int32 i = 0; i < ConstClothFacade.GetNumFabrics(); ++i)
{
    FCollectionClothFabricConstFacade Fabric = ConstClothFacade.GetFabric(i);
    float Density = Fabric.GetDensity();
    float Friction = Fabric.GetFriction();
    float Bending = Fabric.GetBendingStiffness().Weft;
    // ...处理面料参数
}
```

**使用 Selection Facade 管理选择集**

```cpp
// 来源: Public/ChaosClothAsset/CollectionClothSelectionFacade.h
FCollectionClothSelectionFacade SelectionFacade(ManagedArrayCollection);
SelectionFacade.DefineSchema();

// 创建选择集
TSet<int32>& KinematicVertices = SelectionFacade.FindOrAddSelectionSet(
    FName("KinematicVertices"), 
    ClothCollectionGroup::SimVertices3D);
KinematicVertices.Add(0);
KinematicVertices.Add(1);
KinematicVertices.Add(2);

// 查询选择集
bool bHasSelection = SelectionFacade.HasSelection(FName("KinematicVertices"));
TArray<FName> AllSelections = SelectionFacade.GetNames();
```

## Demo 示例

以下是一个完整的最小示例，演示如何创建一个带有裁片、面料和缝合线的布料资产数据。

**ChaosClothAssetDemo.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "ChaosClothAsset/CollectionClothFacade.h"

class FChaosClothAssetDemo
{
public:
    /** 创建一个包含完整裁片定义的布料数据 */
    static TSharedRef<FManagedArrayCollection> CreateSimpleClothAsset();

    /** 读取并打印布料资产信息 */
    static void PrintClothAssetInfo(const TSharedRef<const FManagedArrayCollection>& ClothCollection);
};
```

**ChaosClothAssetDemo.cpp**

```cpp
#include "ChaosClothAssetDemo.h"
#include "ChaosClothAsset/CollectionClothFacade.h"
#include "ChaosClothAsset/ClothGeometryTools.h"

using namespace UE::Chaos::ClothAsset;

TSharedRef<FManagedArrayCollection> FChaosClothAssetDemo::CreateSimpleClothAsset()
{
    TSharedRef<FManagedArrayCollection> Collection = MakeShared<FManagedArrayCollection>();

    // 1. 定义 Schema
    FCollectionClothFacade ClothFacade(Collection);
    ClothFacade.DefineSchema(EClothCollectionExtendedSchemas::None);

    // 2. 设置全局信息
    ClothFacade.SetSkeletalMeshSoftObjectPathName(FSoftObjectPath(TEXT("/Game/SK_Character.SK_Character")));
    ClothFacade.SetReferenceBoneName(FName("pelvis"));

    // 3. 创建面料
    int32 FabricIdx = ClothFacade.AddFabric();
    FCollectionClothFabricFacade Fabric = ClothFacade.GetFabric(FabricIdx);
    FCollectionClothFabricConstFacade::FAnisotropicData Uniform(100.0f, 100.0f, 100.0f);
    Fabric.Initialize(Uniform, 0.5f, FCollectionClothFabricConstFacade::FAnisotropicData(50.0f, 50.0f, 50.0f),
        Uniform, 0.35f, 0.8f, 0.1f, 0.0f, INDEX_NONE, 1.0f);

    // 4. 创建模拟裁片 — 一个三角形
    int32 PatternIdx = ClothFacade.AddSimPattern();
    FCollectionClothSimPatternFacade Pattern = ClothFacade.GetSimPattern(PatternIdx);

    TArray<FVector2f> Positions2D = {
        FVector2f(0.0f, 0.0f),
        FVector2f(100.0f, 0.0f),
        FVector2f(0.0f, 100.0f)
    };
    TArray<FVector3f> Positions3D = {
        FVector3f(0.0f, 0.0f, 0.0f),
        FVector3f(100.0f, 0.0f, 0.0f),
        FVector3f(0.0f, 0.0f, 100.0f)
    };
    TArray<FIntVector3> Indices = { FIntVector3(0, 1, 2) };

    Pattern.Initialize(Positions2D, Positions3D, Indices, FabricIdx);

    return Collection;
}

void FChaosClothAssetDemo::PrintClothAssetInfo(const TSharedRef<const FManagedArrayCollection>& ClothCollection)
{
    FCollectionClothConstFacade ConstFacade(ClothCollection);

    if (!ConstFacade.IsValid())
    {
        UE_LOG(LogTemp, Warning, TEXT("Invalid cloth collection"));
        return;
    }

    UE_LOG(LogTemp, Log, TEXT("=== Cloth Asset Info ==="));
    UE_LOG(LogTemp, Log, TEXT("Sim Vertices 2D: %d"), ConstFacade.GetNumSimVertices2D());
    UE_LOG(LogTemp, Log, TEXT("Sim Vertices 3D: %d"), ConstFacade.GetNumSimVertices3D());
    UE_LOG(LogTemp, Log, TEXT("Sim Faces: %d"), ConstFacade.GetNumSimFaces());
    UE_LOG(LogTemp, Log, TEXT("Render Vertices: %d"), ConstFacade.GetNumRenderVertices());
    UE_LOG(LogTemp, Log, TEXT("Render Faces: %d"), ConstFacade.GetNumRenderFaces());
    UE_LOG(LogTemp, Log, TEXT("Sim Patterns: %d"), ConstFacade.GetNumSimPatterns());
    UE_LOG(LogTemp, Log, TEXT("Render Patterns: %d"), ConstFacade.GetNumRenderPatterns());
    UE_LOG(LogTemp, Log, TEXT("Fabrics: %d"), ConstFacade.GetNumFabrics());
    UE_LOG(LogTemp, Log, TEXT("Seams: %d"), ConstFacade.GetNumSeams());

    for (int32 i = 0; i < ConstFacade.GetNumFabrics(); ++i)
    {
        FCollectionClothFabricConstFacade Fabric = ConstFacade.GetFabric(i);
        UE_LOG(LogTemp, Log, TEXT("  Fabric[%d]: Density=%.2f, Friction=%.2f, Damping=%.2f"),
            i, Fabric.GetDensity(), Fabric.GetFriction(), Fabric.GetDamping());
    }
}
```

## 模块依赖

### ChaosClothAsset (Runtime)

| 模块 | 用途 |
|---|---|
| `GeometryCore` | 动态网格（FDynamicMesh3）操作 |
| `Chaos` | Chaos 物理引擎核心数据类型 |
| `ChaosCloth` | Chaos 布料物理模拟运行时 |
| `GeometryFramework` | 几何体框架工具 |
| `Dataflow` | Dataflow 节点图框架 |

### ChaosClothAssetEngine (Runtime)

依赖关系基于 ChaosClothAsset 模块，额外引入引擎布料资产类。

### ChaosClothAssetTools (Editor)

依赖关系包括编辑器工具链和 ChaosClothAsset 模块，仅限 Win64/Mac/Linux 平台。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `89e20f15` | [ChaosClothAsset] Preserve the Cloth Component bSimulateInEditor and Asset properties across Blueprint | 蓝图操作时保留布料组件的模拟和资产属性 |
| 2026-05-26 | `8953a713` | [Cloth] Move parallel cloth simulation wait from EOF to TG_LastDemotable | 优化并行布料模拟的同步时机 |
| 2026-05-25 | `1db5232a` | [ChaosCloth] Implement RefershBoneMapping for ClothAssetSKMClothingAsset | 实现布料资产骨骼映射刷新 |
| 2026-05-22 | `e98c5896` | [Chaos Cloth Asset] Refresh the editor-only Asset alias after a duplicate or paste of an actor | 复制/粘贴 Actor 后刷新编辑器资产别名 |
| 2026-05-20 | `b9a938ae` | Cleanup Chaos Cloth Asset converter | 清理布料资产转换器代码 |

### 维护评价

ChaosClothAsset 是 Epic 正在**积极维护和推进**的核心布料资产系统：

- **创建时间**：2024-03-22，从 Experimental 迁移到 Beta，约 2 年历史
- **活跃度**：最近一周（2026-05-20 至 2026-05-26）有 5 次提交，包括功能增强、性能优化和代码清理，属于**高度活跃**
- **成熟度**：标记为 Beta（`EnabledByDefault=false`），尚未成为默认启用的正式功能，但 API 已趋于稳定（大量 UE_DEPRECATED 标记表明经历了多轮迭代）
- **代码质量**：采用了成熟的 Facade 设计模式，Const/非 Const 分离，数据访问层次分明
- **已知限制**：
  - 默认未启用，需要手动在项目设置中开启
  - 依赖 ChaosCloth、GeometryCache、Dataflow 三个插件
  - 编辑器工具仅限桌面平台（Win64/Mac/Linux）
  - 部分 API 在 5.7 版本有废弃标记（如 PathName → SoftObjectPath）
- **推荐使用**：✅ 推荐用于需要结构化布料资产工作流的项目。随着 Chaos 物理引擎的成熟，该插件有望成为官方布料解决方案的标准组件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAsset)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAsset/Tests)