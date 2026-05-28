# Chaos Cloth Asset

> Pattern based cloth asset using the Chaos Cloth simulation.

| 属性 | 值 |
|---|---|
| 中文名 | 混沌布料资产 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、数据流节点） |
| 模块 | `ChaosClothAsset` (Runtime), `ChaosClothAssetEngine` (Runtime), `ChaosClothAssetTools` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-03-22 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAsset) | |

## 用途

ChaosClothAsset 是 UE5 中基于**图案（Pattern）**的布料资产系统，建立在 Chaos 布料物理引擎之上。与传统将整个网格作为布料模拟不同，该插件采用**2D 裁片 → 3D 缝合 → 物理模拟**的工作流程：

1. **2D 图案设计**：定义布料的 2D 裁片形状（类似真实服装打版）
2. **3D 缝合**：将 2D 裁片通过缝线（Seam）缝合到 3D 空间
3. **物理模拟**：使用 Chaos 引擎进行布料物理仿真
4. **渲染映射**：通过 Proxy Deformer 将模拟结果映射到高精度渲染网格

该插件解决了以下问题：
- 传统布料模拟需要手动设置每个顶点的约束，图案方式更符合实际制衣流程
- 将布料数据存储在 `FManagedArrayCollection`（Chaos 的结构化数据容器）中，便于 Dataflow 节点化处理
- 支持独立的模拟网格和渲染网格，模拟用低分辨率提高性能，渲染用高分辨率保证视觉质量
- 支持 Morph Target、Accessory Mesh、Fabric 材质系统等高级布料特性

**注意**：该插件默认未启用（`EnabledByDefault: false`），需要在项目设置中手动启用。

## 使用场景

- 你需要制作角色服装并进行实时布料模拟 → 使用 ChaosClothAsset
- 你要在 Dataflow 编辑器中以节点化方式设计布料 → 该插件提供完整的 Dataflow 节点支持
- 你需要对布料的不同区域使用不同的材质属性（弯曲刚度、拉伸刚度等）→ 使用 Fabric 系统
- 你需要布料与骨骼动画绑定（蒙皮）→ 支持骨骼权重和 Tether 约束
- 你需要自定义布料区域的调整大小（Resizing）行为 → 支持 Custom Resizing Regions

## 蓝图用法

该插件的核心功能以 C++ 库形式提供，主要通过 Dataflow 节点在编辑器中使用。由于 `ChaosClothAsset` 模块主要提供底层数据结构和 Facade 访问接口，蓝图可直接调用的公开节点较少。实际布料资产的创建和配置主要通过 ChaosClothAssetEngine 和 ChaosClothAssetTools 模块完成。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| Dataflow 节点 | 通过 Dataflow 编辑器进行布料图案设计和模拟配置 | ChaosClothAssetEngine / ChaosClothAssetTools |

### 使用示例（蓝图描述）

该插件的典型工作流不依赖传统蓝图节点连接，而是通过以下路径使用：

1. **启用插件**：项目设置 → Plugins → 搜索 "Chaos Cloth Asset" → 启用
2. **创建布料资产**：Content Browser → 右键 → Chaos → Cloth Asset
3. **编辑布料**：打开 Dataflow 编辑器，使用节点定义 2D 图案、缝线、材质参数
4. **应用到角色**：在 SkeletalMesh 的 Clothing 面板中引用创建的布料资产
5. **运行时模拟**：ChaosClothComponent 自动使用该资产进行物理模拟

## C++ 用法

### 头文件引入

```cpp
#include "ChaosClothAsset/CollectionClothFacade.h"
#include "ChaosClothAsset/ClothGeometryTools.h"
#include "ChaosClothAsset/CollectionClothSelectionFacade.h"
```

### 基本用法 — 创建和查询布料数据

以下代码展示如何使用 Facade 模式访问和操作布料集合数据。

来源：`Public/ChaosClothAsset/CollectionClothFacade.h`

```cpp
// 创建一个 ManagedArrayCollection 作为布料数据的底层存储
TSharedRef<FManagedArrayCollection> ManagedArrayCollection = MakeShared<FManagedArrayCollection>();

// 创建可写 Facade 并定义 Schema（初始化所有布料数据组）
FCollectionClothFacade ClothFacade(ManagedArrayCollection);
ClothFacade.DefineSchema();

// 设置物理资产和骨骼网格引用
ClothFacade.SetPhysicsAssetSoftObjectPathName(FSoftObjectPath("/Game/Characters/PhysicsAsset"));
ClothFacade.SetSkeletalMeshSoftObjectPathName(FSoftObjectPath("/Game/Characters/SkeletalMesh"));
ClothFacade.SetReferenceBoneName(FName("pelvis"));

// 配置求解器参数
ClothFacade.SetSolverGravity(FVector3f(0.0f, 0.0f, -980.665f));
ClothFacade.SetSolverAirDamping(0.035f);
ClothFacade.SetSolverSubSteps(1);
ClothFacade.SetSolverTimeStep(0.033f);
```

### 基本用法 — 添加图案和缝线

```cpp
// 添加一个模拟图案
int32 PatternIndex = ClothFacade.AddSimPattern();
FCollectionClothSimPatternFacade SimPattern = ClothFacade.GetSimPattern(PatternIndex);

// 初始化图案：2D 位置、3D 位置、三角形索引
TArray<FVector2f> Positions2D = { FVector2f(0,0), FVector2f(100,0), FVector2f(50,100) };
TArray<FVector3f> Positions3D = { FVector3f(0,0,0), FVector3f(1,0,0), FVector3f(0.5f,1,0) };
TArray<FIntVector3> Indices = { FIntVector3(0, 1, 2) };
SimPattern.Initialize(Positions2D, Positions3D, Indices);

// 添加一个渲染图案
int32 RenderPatternIndex = ClothFacade.AddRenderPattern();
FCollectionClothRenderPatternFacade RenderPattern = ClothFacade.GetRenderPattern(RenderPatternIndex);

// 设置渲染材质
RenderPattern.SetRenderMaterialSoftObjectPathName(
    FSoftObjectPath("/Game/Materials/M_Cloth"));
```

### 基本用法 — 布料材质（Fabric）

```cpp
// 添加一个 Fabric（材质参数组）
int32 FabricIndex = ClothFacade.AddFabric();
FCollectionClothFabricFacade Fabric = ClothFacade.GetFabric(FabricIndex);

// Fabric 使用各向异性参数：(Weft经向, Warp纬向, Bias斜向)
FCollectionClothFabricConstFacade::FAnisotropicData BendingStiffness(50.0f, 100.0f, 75.0f);
FCollectionClothFabricConstFacade::FAnisotropicData StretchStiffness(100.0f, 100.0f, 100.0f);
FCollectionClothFabricConstFacade::FAnisotropicData BucklingStiffness(25.0f, 50.0f, 35.0f);

Fabric.Initialize(
    BendingStiffness,   // 弯曲刚度
    0.5f,               // 屈曲比
    BucklingStiffness,  // 屈曲刚度
    StretchStiffness,   // 拉伸刚度
    0.35f,              // 密度
    0.8f,               // 摩擦力
    0.1f,               // 阻尼
    0.0f,               // 压力
    INDEX_NONE,         // 层级
    1.0f                // 碰撞厚度
);

// 将 Fabric 关联到模拟图案
SimPattern.SetFabricIndex(FabricIndex);
```

### 进阶用法 — 几何工具

```cpp
#include "ChaosClothAsset/ClothGeometryTools.h"

using namespace UE::Chaos::ClothAsset;

// 检查布料集合是否包含有效的模拟/渲染网格
bool bHasSim = FClothGeometryTools::HasSimMesh(ManagedArrayCollection);
bool bHasRender = FClothGeometryTools::HasRenderMesh(ManagedArrayCollection);

// 从 DynamicMesh 构建模拟网格
UE::Geometry::FDynamicMesh3 DynamicMesh;
// ... 加载或构建 DynamicMesh ...
TMap<int, int32> VertexMap;
FClothGeometryTools::BuildSimMeshFromDynamicMesh(
    ManagedArrayCollection,
    DynamicMesh,
    0,              // UV 通道索引
    FVector2f(1.0f, 1.0f),  // UV 缩放
    false,          // 是否追加到现有数据
    true,           // 是否导入法线
    &VertexMap      // 输出：源顶点到布料顶点的映射
);

// 清理和压缩网格（移除退化三角形、无引用顶点等）
FClothGeometryTools::CleanupAndCompactMesh(ManagedArrayCollection);

// 反转网格法线和绕序
FClothGeometryTools::ReverseMesh(
    ManagedArrayCollection,
    true,   // 反转模拟网格法线
    true,   // 反转模拟网格绕序
    true,   // 反转渲染网格法线
    true,   // 反转渲染网格绕序
    {},     // 模拟图案选择（空=全部）
    {}      // 渲染图案选择（空=全部）
);

// 应用 Proxy Deformer（将模拟结果映射到渲染网格）
FClothGeometryTools::ApplyProxyDeformer(ManagedArrayCollection, false);
```

### 进阶用法 — 选择集管理

```cpp
#include "ChaosClothAsset/CollectionClothSelectionFacade.h"

// 创建选择集 Facade
FCollectionClothSelectionFacade SelectionFacade(ManagedArrayCollection);
SelectionFacade.DefineSchema();

// 创建一个顶点选择集
TSet<int32>& VertexSelection = SelectionFacade.FindOrAddSelectionSet(
    FName("MySelection"),
    ClothCollectionGroup::SimVertices3D  // 选择集依赖的组
);
VertexSelection.Add(0);
VertexSelection.Add(5);
VertexSelection.Add(10);

// 查询选择集
if (SelectionFacade.HasSelection(FName("MySelection")))
{
    const TSet<int32>& Selection = SelectionFacade.GetSelectionSet(FName("MySelection"));
    FName GroupName = SelectionFacade.GetSelectionGroup(FName("MySelection"));
}

// 合并选择集
FCollectionClothSelectionFacade OtherSelectionFacade(OtherCollection);
SelectionFacade.Append(OtherSelectionFacade, false);
```

### 进阶用法 — Morph Target

```cpp
// 添加模拟 Morph Target
int32 MorphTargetIndex = ClothFacade.AddSimMorphTarget();
FCollectionClothSimMorphTargetFacade MorphTarget = ClothFacade.GetSimMorphTarget(MorphTargetIndex);

// 初始化 Morph Target
TArray<FVector3f> PositionDeltas = { FVector3f(0.1f, 0, 0), FVector3f(-0.1f, 0, 0) };
TArray<FVector3f> TangentZDeltas = { FVector3f::ZeroVector, FVector3f::ZeroVector };
TArray<int32> VertexIndices = { 0, 1 };
MorphTarget.Initialize(FString("WindBend"), PositionDeltas, TangentZDeltas, VertexIndices);

// 按名称查找 Morph Target
int32 FoundIndex = ClothFacade.FindSimMorphTargetIndexByName(FString("WindBend"));
```

## Demo 示例

以下示例展示如何以编程方式创建一个完整的布料资产，包含图案、缝线和材质参数。

```cpp
// ClothAssetDemo.h
#pragma once

#include "CoreMinimal.h"

namespace UE::Chaos::ClothAsset
{
    class FCollectionClothFacade;
}

class FClothAssetDemo
{
public:
    /** 创建一个包含单个三角形图案的布料集合 */
    static TSharedRef<FManagedArrayCollection> CreateSimpleClothCollection();

    /** 查询布料信息并打印到日志 */
    static void LogClothInfo(const TSharedRef<const FManagedArrayCollection>& ClothCollection);
};
```

```cpp
// ClothAssetDemo.cpp
#include "ClothAssetDemo.h"

#include "ChaosClothAsset/CollectionClothFacade.h"
#include "ChaosClothAsset/ClothGeometryTools.h"
#include "ChaosClothAsset/CollectionClothFabricFacade.h"
#include "ChaosClothAsset/CollectionClothSelectionFacade.h"

using namespace UE::Chaos::ClothAsset;

TSharedRef<FManagedArrayCollection> FClothAssetDemo::CreateSimpleClothCollection()
{
    TSharedRef<FManagedArrayCollection> Collection = MakeShared<FManagedArrayCollection>();
    
    // 初始化 Schema
    FCollectionClothFacade ClothFacade(Collection);
    ClothFacade.DefineSchema();
    
    // 设置全局参数
    ClothFacade.SetPhysicsAssetSoftObjectPathName(FSoftObjectPath("/Game/PA_Cloth"));
    ClothFacade.SetSkeletalMeshSoftObjectPathName(FSoftObjectPath("/Game/SM_Character"));
    ClothFacade.SetReferenceBoneName(FName("spine_01"));
    
    // 添加材质
    const int32 FabricIndex = ClothFacade.AddFabric();
    auto Fabric = ClothFacade.GetFabric(FabricIndex);
    Fabric.Initialize(
        FCollectionClothFabricConstFacade::FAnisotropicData(100.f),
        0.5f,  // BucklingRatio
        FCollectionClothFabricConstFacade::FAnisotropicData(50.f),
        FCollectionClothFabricConstFacade::FAnisotropicData(100.f),
        0.35f, 0.8f, 0.1f, 0.f, INDEX_NONE, 1.f
    );
    
    // 添加模拟图案（一个简单的四边形，两个三角形）
    const int32 PatternIndex = ClothFacade.AddSimPattern();
    auto SimPattern = ClothFacade.GetSimPattern(PatternIndex);
    SimPattern.SetFabricIndex(FabricIndex);
    
    TArray<FVector2f> Pos2D = {
        FVector2f(0.f, 0.f), FVector2f(100.f, 0.f),
        FVector2f(100.f, 100.f), FVector2f(0.f, 100.f)
    };
    TArray<FVector3f> Pos3D = {
        FVector3f(0.f, 0.f, 0.f), FVector3f(1.f, 0.f, 0.f),
        FVector3f(1.f, 1.f, 0.f), FVector3f(0.f, 1.f, 0.f)
    };
    TArray<FIntVector3> Tris = {
        FIntVector3(0, 1, 2), FIntVector3(0, 2, 3)
    };
    SimPattern.Initialize(Pos2D, Pos3D, Tris);
    
    // 添加渲染图案
    const int32 RenderPatternIndex = ClothFacade.AddRenderPattern();
    auto RenderPattern = ClothFacade.GetRenderPattern(RenderPatternIndex);
    RenderPattern.SetRenderMaterialSoftObjectPathName(
        FSoftObjectPath("/Game/Materials/M_Cloth"));
    
    // 复制模拟网格到渲染网格
    FClothGeometryTools::CopySimMeshToRenderMesh(
        Collection,
        FSoftObjectPath("/Game/Materials/M_Cloth"),
        true  // 单一渲染图案
    );
    
    return Collection;
}

void FClothAssetDemo::LogClothInfo(const TSharedRef<const FManagedArrayCollection>& ClothCollection)
{
    FCollectionClothConstFacade ConstFacade(ClothCollection);
    
    if (!ConstFacade.IsValid())
    {
        UE_LOG(LogTemp, Warning, TEXT("布料集合无效"));
        return;
    }
    
    UE_LOG(LogTemp, Log, TEXT("=== 布料信息 ==="));
    UE_LOG(LogTemp, Log, TEXT("模拟顶点数 (2D): %d"), ConstFacade.GetNumSimVertices2D());
    UE_LOG(LogTemp, Log, TEXT("模拟顶点数 (3D): %d"), ConstFacade.GetNumSimVertices3D());
    UE_LOG(LogTemp, Log, TEXT("模拟面数: %d"), ConstFacade.GetNumSimFaces());
    UE_LOG(LogTemp, Log, TEXT("渲染顶点数: %d"), ConstFacade.GetNumRenderVertices());
    UE_LOG(LogTemp, Log, TEXT("渲染面数: %d"), ConstFacade.GetNumRenderFaces());
    UE_LOG(LogTemp, Log, TEXT("图案数: %d"), ConstFacade.GetNumSimPatterns());
    UE_LOG(LogTemp, Log, TEXT("缝线数: %d"), ConstFacade.GetNumSeams());
    UE_LOG(LogTemp, Log, TEXT("材质数: %d"), ConstFacade.GetNumFabrics());
    UE_LOG(LogTemp, Log, TEXT("Morph Target 数: %d"), ConstFacade.GetNumSimMorphTargets());
    
    // 输出权重图信息
    TArray<FName> WeightMapNames = ConstFacade.GetWeightMapNames();
    for (const FName& Name : WeightMapNames)
    {
        TConstArrayView<float> Weights = ConstFacade.GetWeightMap(Name);
        UE_LOG(LogTemp, Log, TEXT("权重图 '%s': %d 个值"), *Name.ToString(), Weights.Num());
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ChaosCloth` | Chaos 布料物理模拟引擎（核心依赖） |
| `GeometryCache` | 几何缓存系统 |
| `Dataflow` | 节点化数据流编辑框架 |
| `GeometryFramework` | 几何工具库（DynamicMesh 等） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `89e20f15` | [ChaosClothAsset] Preserve the Cloth Component bSimulateInEditor and Asset properties across Blueprint | 在蓝图编辑器中保留布料组件的 SimulateInEditor 和资产属性 |
| 2026-05-26 | `8953a713` | [Cloth] Move parallel cloth simulation wait from EOF to TG_LastDemotable | 优化并行布料模拟的同步点，从 EOF 移至 TG_LastDemotable |
| 2026-05-25 | `1db5232a` | [ChaosCloth] Implement RefreshBoneMapping for ClothAssetSKMClothingAsset | 为布料资产实现骨骼映射刷新功能 |
| 2026-05-22 | `e98c5896` | [Chaos Cloth Asset] Refresh the editor-only Asset alias after a duplicate or paste of an actor | 在复制或粘贴 Actor 后刷新编辑器资产别名 |
| 2026-05-20 | `b9a938ae` | Cleanup Chaos Cloth Asset converter | 清理布料资产转换器代码 |

### 维护评价

- **创建时间**：2024 年 3 月，从 Experimental 迁移为 Beta 状态，至今约 2 年
- **更新频率**：**非常活跃**。最近的提交集中在 2026 年 5 月，几乎每周都有更新
- **更新内容**：涵盖功能完善（骨骼映射刷新）、性能优化（并行模拟同步）、编辑器体验改进（蓝图属性保留、复制粘贴修复）和代码清理
- **Beta 状态**：该插件标记为 Beta，首次提交明确说明从 Experimental 迁出
- **默认未启用**：`EnabledByDefault: false`，需要手动启用

**推荐使用**：该插件正处于活跃开发阶段，功能持续完善中。作为 UE5 官方推荐的新一代布料资产系统，适合用于需要高质量布料模拟的项目。但由于仍在 Beta 阶段，API 可能在未来版本中有变动，建议关注更新日志中的废弃标记（多个 5.7 版本的 `UE_DEPRECATED` 标记已出现）。生产环境使用时需充分测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAsset)
- 官方文档（暂无）
- [ChaosCloth 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosCloth)（底层物理引擎依赖）
- [Dataflow 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Dataflow)（节点化编辑框架）