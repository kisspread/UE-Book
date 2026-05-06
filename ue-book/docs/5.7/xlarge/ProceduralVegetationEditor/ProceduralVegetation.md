# Procedural Vegetation Editor

> Node Graph based Editor that allows users to create Nanite Foliage ready vegetation directly in the engine. Users can load Procedural Vegetation Presets that contain prebuilt data for a species, and customize/create variations using the node graph.

| 属性 | 值 |
|---|---|
| 中文名 | 程序化植被编辑器 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ProceduralVegetation` (Runtime), `ProceduralVegetationEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-12-18 |
| 年龄标签 | 🆕（约0年） |
| [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/ProceduralVegetationEditor) | |

## 用途

Procedural Vegetation Editor 是 UE5 引擎内建的程序化植被创建工具。它允许用户通过节点图（Node Graph）直接生成、编辑和导出 Nanite 就绪（Nanite-ready）的植被资源，而无需依赖外部 DCC 软件（如 Blender、SpeedTree）。插件底层使用 `FManagedArrayCollection` 来存储植物的拓扑、骨架、叶序、材质等结构化数据，并通过一系列 PCG 节点（如 PresetLoader、Gravity、Carve、FoliageDistributor 等）组合出不同的植物形态。

本插件解决了以下问题：
- **传统工作流繁琐**：外部建模 → 导入 → 调整 → 重新导入，迭代周期长。
- **缺乏程序化控制**：难以批量生成变体，难以根据环境条件（光照、坡度、重力）动态调整植物形状。
- **Nanite 优化困难**：生成的几何体需要匹配 Nanite 要求（三角面高密度、正确 UV 等），手动创建工作量极大。

插件提供了完整的程序化管线：从 Preset 加载物种数据 → 应用生长模拟（重力、坡度、修剪）→ 放置叶/花实例 → 构建网格体（骨骼、材质、UV）→ 导出用于场景放置。

## 使用场景

- **开放世界植被填充**：在大型场景中快速生成成千上万棵不同年龄、不同姿态的树木，每棵树都是独立的程序化实例。
- **概念艺术迭代**：美术师在引擎内调整树干曲率、叶序类型、分布密度等参数，即时预览效果，无需等待外部渲染。
- **Nanite 资产生产**：直接输出高质量、符合 Nanite 管线要求的静态网格体（包含骨骼用于风吹动画），可直接用于关卡放置或 Nanite 虚拟几何体。
- **生态模拟研究**：通过 Light、Health、UpAlignment 等条件属性模拟植物对光照、土壤、竞争的反应，生成更自然的植被分布。

## 蓝图用法

本插件主要面向编辑器节点图（PCG）工作流，不提供运行时蓝图节点。以下列出可在蓝图中访问的配置类和枚举，用于节点属性的赋值和获取。

### 核心节点设置类（UObject）

| 类名 | 节点名称 | 说明 |
|---|---|---|
| `UPVPresetLoaderSettings` | ProceduralVegetationPresetLoader | 加载植物 Preset（`.uasset`） |
| `UPVImporterSettings` | ProceduralVegetationImporter | 从 `.json` 骨架文件导入基础结构 |
| `UPVGravitySettings` | ProceduralVegetationGravity | 应用重力/向光性弯曲 |
| `UPVSlopeSettings` | ProceduralVegetationSlope | 根据地形坡度调整植物弯曲 |
| `UPVCarveSettings` | ProceduralVegetationCarve | 从顶部或底部修剪植物 |
| `UPVRemoveBranchesSettings` | ProceduralVegetationRemoveBranches | 按长度/半径/光照等条件移除枝条 |
| `UPVScaleSettings` | ProceduralVegetationScale | 统一缩放植物 |
| `UPVFoliagePaletteSettings` | ProceduralVegetationFoliage | 设置叶/花实例的网格体列表 |
| `UPVFoliageDistributorSettings` | ProceduralVegetationFoliageDistributor | 控制叶/花的分布参数（密度、角度、叶序） |
| `UPVMeshBuilderSettings` | ProceduralVegetationMesher | 生成最终网格体（骨骼、材质、UV） |
| `UPVBoneReductionSettings` | ProceduralVegetationBoneReduction | 简化骨骼数量，优化风吹模拟性能 |

以上类均派生自 `UPVBaseSettings`，且标记为 `BlueprintType`，可在蓝图构造脚本或函数中创建、赋值。例如，在 PCG 节点属性面板中可直接编辑这些设置。

### 主要枚举（UENUM）

| 枚举 | 值含义 |
|---|---|
| `ECarveBasis` | LengthFromRoot / FromBottom / ZPosition / Radius |
| `EGravityMode` | Gravity / Phototropic |
| `EPVSlopeTrunkPivotPoint` | Origin / Trunk |
| `ERemoveBranchesBasis` | Length / Radius / Light / Age / Generation |
| `EPhyllotaxyType` | Alternate / Opposite / Decussate / Whorled / Spiral |
| `EPhyllotaxyFormation` | Distichous / Tristichous / Pentastichous / Octastichous / Parastichous |
| `EFoliageDistributionCondition` | Light / Scale / UpAlignment / Tip / Health / None |
| `EGenerationOffsetMethod` | Clamped / Refit |
| `EMaterialDistributionMethod` | Repeat / Fit |
| `EYTextureMode` | Default / Fit0_1 |
| `EUVMaterialMode` | Generation / Age / Radius |
| `EPVRenderType` | None / PointData / Mesh / Foliage / Bones / FoliageGrid |

### 使用示例（蓝图描述）

1. **创建一棵标准橡树**  
   - 放置 `ProceduralVegetationPresetLoader` 节点，在其属性面板中设置 `Preset` 为已导入的橡树 Preset 资产。  
   - 连接 `ProceduralVegetationMesher` 节点，调整 `PointRemoval`、`SegmentReduction` 等参数控制网格细节。  
   - 最终节点的输出端（`UPVMeshData`）可直接用于生成静态网格体或关卡放置。

2. **模拟山坡扭曲树木**  
   - 在 PresetLoader 之后添加 `ProceduralVegetationSlope` 节点，设置 `SlopeAngle=30°`、`BendStrength=2.0`。  
   输出可继续连接 `ProceduralVegetationGravity` 节点，设置 `Mode=Gravity`、`Gravity=0.5` 增加下垂感。

3. **控制叶序分布**  
   - 在 FoliagePalette 节点中指定多个叶网格体，并设置 `OverridePhyllotaxy=true`，选择 `PhyllotaxyType=Whorled`、`MinNodeBuds=3`、`MaxNodeBuds=5`。  
   - 再连接 FoliageDistributor 节点调整 `InstanceSpacing` 和 `AxilAngle`，实现不同密度和角度。

## C++ 用法

### 头文件引入

```cpp
#include "ProceduralVegetationModule.h"              // 模块入口
#include "Facades/PVBranchFacade.h"                  // 枝条操作
#include "Facades/PVPointFacade.h"                   // 生长点操作
#include "Facades/PVFoliageFacade.h"                 // 叶/花实例操作
#include "Implementations/PVGravity.h"               // 应用重力
#include "Implementations/PVCarve.h"                 // 修剪
#include "Helpers/PVFoliageJSONHelper.h"             // JSON 加载
```

### 基本用法

以下示例展示如何从 Preset JSON 文件加载一棵植物的骨架数据，然后应用重力并输出网格体。来源：`PVJSONHelper.h`、`PVGravity.h`。

```cpp
// 1. 创建 ManagedArrayCollection 容器
FManagedArrayCollection Collection;

// 2. 加载 Preset JSON 数据（参见 PVFoliageJSONHelper）
FString PresetPath = FPaths::ProjectContentDir() / TEXT("Vegetation/Oak_Preset.json");
PV::PVFoliageJSONHelper::LoadFoliageDataInCollection(
    Collection,
    PresetPath,
    FPVFoliageVariationData(),  // 变体数据
    ErrorMessage
);

// 3. 应用重力弯曲
FPVGravityParams GravityParams;
GravityParams.Mode = EGravityMode::Gravity;
GravityParams.Gravity = 0.3f;
GravityParams.Direction = FVector3f::DownVector;
FPVGravity::ApplyGravity(GravityParams, Collection);

// 4. 修剪顶部 20%（从 LengthFromRoot 基准）
// 使用 FPVCarve::ApplyCarve，但需要先提取枝条和点数据
// 通常通过 Facade 操作
PV::Facades::FBranchFacade BranchFacade(Collection);
PV::Facades::FPointFacade PointFacade(Collection);
// ... 构建 PointsToRemove 数组
TArray<bool> PointsToRemove;
TArray<bool> BranchesToRemove;
// 根据 Carve 逻辑填充后调用
FPVCarve::RemoveEntriesAndRecomputeAttributes(Collection, SourceCollection, PointsToRemove, BranchesToRemove, FoliageInstancesToRemove);

// 5. 构建网格体（使用 FPVMeshBuilder 的方法，需包含更详细参数）
FPVMeshBuilderParams BuilderParams;
BuilderParams.PointRemoval = 0.02f;
BuilderParams.SegmentReduction = 0.5f;
// ... 设置其他参数
FPVMeshBuilder::BuildMesh(Collection, BuilderParams);
```

### 进阶用法：自定义枝条移除逻辑

利用 `PV::Facades::FBranchFacade` 和 `IShrinkable` 接口手动剔除特定枝条。

```cpp
// 根据枝条生成代数和长度移除过细枝条
PV::Facades::FBranchFacade BranchFacade(Collection);
TArray<bool> BranchesToRemove(BranchFacade.GetElementCount(), false);

for (int32 BranchIdx = 0; BranchIdx < BranchFacade.GetElementCount(); ++BranchIdx)
{
    int32 GenNumber = BranchFacade.GetHierarchyGenerationNumber(BranchIdx);
    // 只移除第三代及以上枝条
    if (GenNumber >= 3)
    {
        // 获取该枝条所有点的尺度，判断平均粗细
        const TArray<int32>& Points = BranchFacade.GetPoints(BranchIdx);
        float TotalScale = 0.0f;
        for (int32 PtIdx : Points)
        {
            TotalScale += PointFacade.GetPointScale(PtIdx);
        }
        float AvgScale = Points.Num() > 0 ? TotalScale / Points.Num() : 0.0f;
        if (AvgScale < 0.2f)
        {
            BranchesToRemove[BranchIdx] = true;
        }
    }
}

// 执行移除并更新索引
FManagedArrayCollection OutCollection;
FPVRemoveBranches::ApplyRemoveBranches(ERemoveBranchesBasis::Generation, 0.5f, OutCollection);
```

## Demo 示例

以下是一个完整的最小 C++ 示例，演示如何从 Preset 生成一颗树并保存为静态网格体。需要依赖 ProceduralVegetation 模块。

### ProceduralVegetationDemo.h

```cpp
#pragma once
#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "ProceduralVegetationDemo.generated.h"

UCLASS()
class UProceduralVegetationDemo : public UObject
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "Demo")
    void GenerateTree(const FString& InPresetPath);
};
```

### ProceduralVegetationDemo.cpp

```cpp
#include "ProceduralVegetationDemo.h"
#include "Facades/PVBranchFacade.h"
#include "Facades/PVPointFacade.h"
#include "Facades/PVFoliageFacade.h"
#include "Facades/PVMetaInfoFacade.h"
#include "Implementations/PVGravity.h"
#include "Implementations/PVCarve.h"
#include "Implementations/PVMeshBuilder.h"
#include "Implementations/PVScale.h"
#include "Helpers/PVFoliageJSONHelper.h"
#include "GeometryCollection/GeometryCollection.h"
#include "Engine/StaticMesh.h"
#include "Engine/StaticMeshActor.h"
#include "Materials/MaterialInterface.h"
#include "UObject/StrongObjectPtr.h"

void UProceduralVegetationDemo::GenerateTree(const FString& InPresetPath)
{
    // 1. 创建 Collection
    FManagedArrayCollection Collection;

    // 2. 加载 Preset
    FString ErrorMsg;
    bool bSuccess = PV::PVFoliageJSONHelper::LoadFoliageDataInCollection(
        Collection,
        InPresetPath,
        FPVFoliageVariationData(),
        ErrorMsg
    );
    if (!bSuccess)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load preset: %s"), *ErrorMsg);
        return;
    }

    // 3. 应用小幅缩放和重力
    FPVScale::ApplyScale(0.8f, Collection);
    FPVGravityParams GravityParams;
    GravityParams.Gravity = 0.2f;
    GravityParams.Mode = EGravityMode::Gravity;
    GravityParams.Direction = FVector3f::DownVector;
    FPVGravity::ApplyGravity(GravityParams, Collection);

    // 4. 构建网格体
    FPVMeshBuilderParams BuilderParams;
    BuilderParams.PointRemoval = 0.02f;
    BuilderParams.SegmentReduction = 0.6f;
    BuilderParams.MinMeshDivisions = 6;
    BuilderParams.MaxMeshDivisions = 12;
    BuilderParams.bOverrideMaterial = false;
    // 使用预设材质
    FPVMeshBuilder::BuildMesh(Collection, BuilderParams);

    // 5. 提取最终几何体（可以是 UDynamicMesh 或 UGeometryCollection）
    // 此处简化为打印枝条数量
    PV::Facades::FBranchFacade BranchFacade(Collection);
    UE_LOG(LogTemp, Log, TEXT("Generated tree with %d branches"), BranchFacade.GetElementCount());
}
```

该示例可在任意 Actor 或工具蓝图中调用。实际生产环境中，最终几何体通常通过 `UPVMeshData` 输出到关卡或保存为资产。

## 模块依赖

本插件不依赖特殊第三方库。以下为 ProceduralVegetation（Runtime）模块的独特依赖（省略常见模块）。

| 模块 | 用途 |
|---|---|
| `PCG` | 程序化内容生成框架，用于节点图和数据类型（如 `UPCGSpatialData`、`FPCGElement`） |
| `GeometryCollectionEngine` | 提供 `FManagedArrayCollection` 及其访问器，作为植被数据的核心容器 |
| `DynamicMesh` | 用于网格构建（`UDynamicMesh`、`FMeshShapeGenerator`） |
| `Chaos` | 少量物理相关，如 `FBoneFacade` 中的风力数据（`NJORD`） |
| `JsonUtilities` | JSON 加载 Preset 和骨架数据 |

**编辑器模块（ProceduralVegetationEditor）额外依赖**：`UnrealEd`、`PropertyEditor`、`KismetCompiler` 等，以提供节点编辑器的 UI 支持。

## 维护状态

### 近期更新

根据 Git 日志（2025-12-18 集中提交）：

- 2025-12-18 `b0eaa7e8` [PVE] Foliage condition system  
- 2025-12-18 `e6d3fae0` [PVE] Added UV1 and UV2 data also added Generation data in UV0.X  
- 2025-12-18 `0565d5cc` [PVE] Fix the missing bones for some parts of the mesh.  
- 2025-12-18 `5a2cd1cc` Fixed foliage face orientation  
- 2025-12-18 `e46aff7e` Bug fixes  

从提交内容看，项目处于快速开发阶段，修复关键问题（骨骼缺失、叶面朝向）并添加新功能（条件系统、UV 数据、生成数据）。表明当前**活跃维护**。

### 维护评价

- **创建时间**：2025-12-18，极新的插件，尚未发布稳定版本。
- **近期更新**：同一日期密集提交，显示团队正在集中攻关。
- **活跃度**：极高，每天有多次功能性提交。
- **已知问题**：头文件中存在截断（如 `PVFoliage.h` 的 `EFoliageDistributionCondition` 被截断），部分功能注释不完整。建议等待后续稳定版本。
- **推荐度**：如果项目需要自定义程序化植被管线且不畏惧早期实验特性，可以试用。对于生产项目建议等待正式版。

## 相关链接

- [源码（树状目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ProceduralVegetationEditor)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/ProceduralVegetationEditor/)（尚不存在）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ProceduralVegetationEditor/Tests)（未公开）