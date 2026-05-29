# Modeling Components

> A set of modules implementing 3D mesh creation and editing based on the Interactive Tools Framework（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 网格建模工具集 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（工具框架组件、选择系统、交互机制、吸附系统、预览几何体） |
| 模块 | `MeshModelingTools` (Runtime), `MeshModelingToolsEditorOnly` (Runtime), `ModelingComponents` (Runtime), `ModelingComponentsEditorOnly` (Runtime), `ModelingOperators` (Runtime), `ModelingOperatorsEditorOnly` (Runtime), `SkeletalMeshModifiers` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-07-30 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MeshModelingToolset) | |

## 用途

MeshModelingToolset 是 Unreal Engine 内部网格建模工具的**基础设施插件**，为 UE5 的 Interactive Tools Framework（交互工具框架）提供 3D 网格创建和编辑的底层组件。本插件**不直接提供用户可见的建模工具**，而是为 `ModelingToolsEditorOnly`（编辑器内建模工具集）等上层插件提供构建工具所需的基类、交互机制、选择系统、吸附系统和预览渲染组件。

**核心问题**：UE5 的建模工具需要在编辑器中实时预览网格修改、支持撤销/重做、处理复杂的元素选择、以及将操作结果烘焙回 StaticMesh 等资产。本插件将这些通用能力抽象为可复用的模块。

**文档聚焦模块**：本文档聚焦于 `ModelingComponents`（Runtime 模块），它是整个插件中最核心的基础模块，提供约 112 个头文件的工具框架基础设施。

## 使用场景

- 你在开发一个需要**实时网格预览**的建模工具 → 使用 `UMeshOpPreviewWithBackgroundCompute`
- 你需要实现**网格元素选择**（顶点/边/面/多边形组）→ 使用 `UGeometrySelectionManager` + `UMeshTopologySelectionMechanic`
- 你要在工具中添加**场景吸附**功能 → 使用 `UModelingSceneSnappingManager`
- 你需要创建**临时预览几何体**（线段集、三角形集、点集）→ 使用 `UPreviewGeometry`
- 你要从多个网格**布尔运算创建新网格** → 使用 `UBaseCreateFromSelectedTool`
- 你需要实现**矩形/套索框选**交互 → 使用 `URectangleMarqueeMechanic` / `UPolyLassoMarqueeMechanic`
- 你在做一个需要**曲线控制点编辑**的工具 → 使用 `UCurveControlPointsMechanic`
- 你要从场景渲染捕获中**烘焙纹理** → 使用 `FSceneCapturePhotoSet` + `RenderCaptureFunctions`

## 蓝图用法

ModelingComponents 主要是 C++ 基础设施模块，大部分 API 通过 C++ 继承使用。以下列出少数暴露到蓝图的接口：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateMeshObject` | 根据参数创建网格对象（StaticMesh/Volume/DynamicMeshActor） | `UModelingObjectsCreationAPI` |
| `CreateTextureObject` | 根据参数创建纹理资产 | `UModelingObjectsCreationAPI` |
| `CreateMaterialObject` | 根据参数创建材质资产 | `UModelingObjectsCreationAPI` |
| `CreateNewActor` | 在世界中创建新 Actor | `UModelingObjectsCreationAPI` |
| `AddTriangleSet` | 在预览几何体中添加三角形集 | `UPreviewGeometry` |
| `AddLineSet` | 在预览几何体中添加线段集 | `UPreviewGeometry` |
| `AddPointSet` | 在预览几何体中添加点集 | `UPreviewGeometry` |
| `InvertSelection` | 反转当前网格拓扑选择 | `UMeshTopologySelectionMechanicProperties` |
| `SelectAll` | 全选网格元素 | `UMeshTopologySelectionMechanicProperties` |

### 使用示例（蓝图描述）

**创建网格对象**：
1. 获取 `UModelingObjectsCreationAPI` 实例（通过 ContextObjectStore）
2. 构造 `FCreateMeshObjectParams`，设置 Transform、Materials、Mesh 数据等
3. 调用 `CreateMeshObject` 获取 `FCreateMeshObjectResult`
4. 检查 `ResultCode == Ok`，访问 `NewActor` / `NewComponent` / `NewAsset`

**管理预览几何体**：
1. 在工具中创建 `UPreviewGeometry` 实例
2. 调用 `CreateInWorld` 将其添加到世界
3. 调用 `AddLineSet("Wireframe")` 添加线段集
4. 通过 `FindLineSet("Wireframe")` 获取并更新线段数据
5. 工具关闭时调用 `Disconnect` 清理

## C++ 用法

### 头文件引入

```cpp
#include "MeshOpPreviewHelpers.h"           // UMeshOpPreviewWithBackgroundCompute
#include "ModelingObjectsCreationAPI.h"      // UModelingObjectsCreationAPI
#include "PreviewMesh.h"                     // UPreviewMesh
#include "Drawing/PreviewGeometryActor.h"    // UPreviewGeometry
#include "Selection/GeometrySelectionManager.h" // UGeometrySelectionManager
#include "Snapping/ModelingSceneSnappingManager.h" // UModelingSceneSnappingManager
#include "ToolSetupUtil.h"                  // 材质工具函数
#include "ModelingToolTargetUtil.h"         // ToolTarget 工具函数
```

### 基本用法：预览网格操作

```cpp
// 来源：Public/MeshOpPreviewHelpers.h, Public/BaseTools/BaseMeshProcessingTool.h
// UMeshOpPreviewWithBackgroundCompute 的典型使用模式

// 1. 创建预览对象
UMeshOpPreviewWithBackgroundCompute* Preview = NewObject<UMeshOpPreviewWithBackgroundCompute>();
Preview->Setup(GetWorld(), this);  // this 实现 IDynamicMeshOperatorFactory

// 2. 配置材质
UMaterialInterface* StandardMat = ToolSetupUtil::GetDefaultMaterial(ToolManager);
UMaterialInterface* WorkingMat = ToolSetupUtil::GetDefaultWorkingMaterial(ToolManager);
Preview->ConfigureMaterials(StandardMat, WorkingMat);

// 3. 当参数改变时，通知预览需要更新
Preview->InvalidateResult();

// 4. 在 Tick 中更新预览
void OnTick(float DeltaTime)
{
    Preview->Tick(DeltaTime);
    if (Preview->HaveValidResult())
    {
        // 预览已更新，用户可以查看结果
    }
}

// 5. 接受工具时获取结果
FDynamicMeshOpResult Result = Preview->Shutdown();
// Result.Mesh 即为最终网格
```

### 基本用法：场景吸附

```cpp
// 来源：Public/Snapping/ModelingSceneSnappingManager.h

// 1. 注册吸附管理器
UE::Geometry::RegisterSceneSnappingManager(ToolsContext);

// 2. 查找吸附管理器
UModelingSceneSnappingManager* SnapManager = 
    UE::Geometry::FindModelingSceneSnappingManager(ToolManager);

// 3. 添加场景几何体到吸附缓存
SnapManager->OnActorAdded(MyActor, [](UPrimitiveComponent* Comp) { return true; });

// 4. 执行吸附查询
FSceneSnapQueryRequest SnapRequest;
SnapRequest.Position = WorldPoint;
SnapRequest.SnapTypes = static_cast<uint8>(ESceneSnapQueryType::Position);

TArray<FSceneSnapQueryResult> Results;
if (SnapManager->ExecuteSceneSnapQuery(SnapRequest, Results))
{
    // 使用吸附结果
    FVector SnappedPosition = Results[0].Position;
}

// 5. 工具关闭时清理
UE::Geometry::DeregisterSceneSnappingManager(ToolsContext);
```

### 进阶用法：创建新网格对象

```cpp
// 来源：Public/ModelingObjectsCreationAPI.h

// 1. 获取 Creation API
UModelingObjectsCreationAPI* CreationAPI = nullptr;
// 通常从 ToolsContext 的 ContextObjectStore 获取

// 2. 构造网格创建参数
FCreateMeshObjectParams MeshParams;
MeshParams.TargetWorld = GetWorld();
MeshParams.Transform = FTransform::Identity;
MeshParams.BaseName = TEXT("MyNewMesh");
MeshParams.bEnableCollision = true;
MeshParams.bEnableNanite = false;
MeshParams.Materials.Add(DefaultMaterial);

// 设置网格数据（二选一）
// 方式 A: 使用 FMeshDescription
MeshParams.SetMesh(MoveTemp(MyMeshDescription));

// 方式 B: 使用 FDynamicMesh3
MeshParams.SetMesh(&MyDynamicMesh);

// 3. 创建网格对象
FCreateMeshObjectResult Result = CreationAPI->CreateMeshObject(MeshParams);
if (Result.IsOK())
{
    AActor* NewActor = Result.NewActor;
    UPrimitiveComponent* NewComponent = Result.NewComponent;
    UObject* NewAsset = Result.NewAsset;
}
```

### 进阶用法：几何体元素选择

```cpp
// 来源：Public/Selection/GeometrySelectionManager.h

// 1. 初始化选择管理器
UGeometrySelectionManager* SelectionManager = NewObject<UGeometrySelectionManager>();
SelectionManager->Initialize(ToolsContext, TransactionsAPI);

// 2. 注册选择器工厂
SelectionManager->RegisterSelectorFactory(MakeUnique<FMySelectorFactory>());

// 3. 设置选择模式
SelectionManager->SetMeshTopologyMode(
    UGeometrySelectionManager::EMeshTopologyMode::Triangle);
SelectionManager->SetSelectionElementType(EGeometryElementType::Face);

// 4. 添加选择目标
SelectionManager->AddActiveTarget(MyGeometryIdentifier);

// 5. 通过射线更新选择
FGeometrySelectionUpdateConfig UpdateConfig;
UpdateConfig.Mode = EGeometrySelectionUpdateMode::Add;
FGeometrySelectionUpdateResult UpdateResult;
SelectionManager->UpdateSelectionViaRaycast(WorldRay, UpdateConfig, UpdateResult);

// 6. 获取选择信息
if (SelectionManager->HasSelection())
{
    FGeometrySelectionBounds Bounds;
    SelectionManager->GetSelectionBounds(Bounds);
    
    FFrame3d SelectionFrame;
    SelectionManager->GetSelectionWorldFrame(SelectionFrame);
}
```

## Demo 示例

### 自定义网格处理工具

一个最小的网格处理工具示例，继承自 `UBaseMeshProcessingTool`，实现简单的网格平滑操作：

**MySmoothMeshTool.h**
```cpp
#pragma once

#include "BaseTools/BaseMeshProcessingTool.h"
#include "MySmoothMeshTool.generated.h"

UCLASS()
class UMySmoothMeshToolProperties : public UInteractiveToolPropertySet
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere, Category = Options, meta = (UIMin = "0", UIMax = "1"))
    float SmoothStrength = 0.5f;

    UPROPERTY(EditAnywhere, Category = Options, meta = (UIMin = "1", UIMax = "20"))
    int32 Iterations = 3;
};

UCLASS()
class UMySmoothMeshTool : public UBaseMeshProcessingTool
{
    GENERATED_BODY()
public:
    virtual void Setup() override;
    
protected:
    virtual void InitializeProperties() override;
    virtual TUniquePtr<UE::Geometry::FDynamicMeshOperator> MakeNewOperator() override;
    virtual bool HasMeshTopologyChanged() const override { return false; }

    UPROPERTY()
    TObjectPtr<UMySmoothMeshToolProperties> SmoothProps;
};
```

**MySmoothMeshTool.cpp**
```cpp
#include "MySmoothMeshTool.h"

void UMySmoothMeshTool::Setup()
{
    Super::Setup();
    SmoothProps = NewObject<UMySmoothMeshToolProperties>(this);
    AddOptionalPropertySet<UMySmoothMeshToolProperties>(
        []() { return true; },
        true  // changes invalidate result
    );
    SmoothProps = GetPropertySet<UMySmoothMeshToolProperties>();
}

void UMySmoothMeshTool::InitializeProperties()
{
    // 初始化属性集
}

TUniquePtr<UE::Geometry::FDynamicMeshOperator> UMySmoothMeshTool::MakeNewOperator()
{
    // 创建并返回自定义的平滑运算符
    // 运算符会接收 GetInitialMesh() 的拷贝，在后台线程执行
    auto Op = MakeUnique<FMySmoothMeshOperator>();
    Op->SourceMesh = GetInitialMesh();
    Op->Strength = SmoothProps->SmoothStrength;
    Op->NumIterations = SmoothProps->Iterations;
    return Op;
}
```

### 自定义选择器工具

一个使用 `UMeshTopologySelectionMechanic` 实现网格元素选择的最小示例：

```cpp
#include "Selection/MeshTopologySelectionMechanic.h"

UCLASS()
class UMySelectionTool : public UInteractiveTool
{
    GENERATED_BODY()
public:
    virtual void Setup() override
    {
        Super::Setup();
        
        // 创建选择机制
        SelectionMechanic = NewObject<UMySelectionMechanicSubclass>(this);
        SelectionMechanic->Initialize(
            MyDynamicMesh,
            TargetTransform,
            GetWorld(),
            [this]() -> FDynamicMeshAABBTree3* { return &MyAABBTree; }
        );
        SelectionMechanic->Setup(this);
    }
    
    virtual void Shutdown(EToolShutdownType ShutdownType) override
    {
        SelectionMechanic->Shutdown();
        Super::Shutdown(ShutdownType);
    }
    
    virtual void Render(IToolsContextRenderAPI* RenderAPI) override
    {
        SelectionMechanic->Render(RenderAPI);
    }

private:
    UPROPERTY()
    TObjectPtr<UMySelectionMechanicSubclass> SelectionMechanic;
};
```

### 预览几何体使用

```cpp
#include "Drawing/PreviewGeometryActor.h"

// 在工具 Setup 中
void UMyTool::Setup()
{
    Super::Setup();
    
    // 创建预览几何体
    PreviewGeometry = NewObject<UPreviewGeometry>(this);
    PreviewGeometry->CreateInWorld(GetWorld(), FTransform::Identity);
    
    // 添加线段集用于绘制网格边框
    ULineSetComponent* BorderLines = PreviewGeometry->AddLineSet(TEXT("Borders"));
    BorderLines->SetMaterial(ToolSetupUtil::GetDefaultLineComponentMaterial(ToolManager));
    
    // 添加三角形集用于高亮选中面
    PreviewGeometry->AddTriangleSet(TEXT("HighlightedFaces"));
    
    // 更新线段数据
    PreviewGeometry->UpdateLineSet(TEXT("Borders"), [](ULineSetComponent* Lines) {
        Lines->Clear();
        for (const FEdge3d& Edge : MyBorderEdges)
        {
            Lines->AddLine(FRenderableLine(Edge.V0, Edge.V1, FColor::Red, 2.0f));
        }
    });
}

// 在工具 Shutdown 中
void UMyTool::Shutdown(EToolShutdownType ShutdownType)
{
    PreviewGeometry->Disconnect();
    Super::Shutdown(ShutdownType);
}
```

## 模块依赖

从 `ModelingComponents.Build.cs` 的依赖关系分析（省略常见依赖）：

| 模块 | 用途 |
|---|---|
| `GeometryCore` | FDynamicMesh3、AABBTree、网格几何算法等核心几何类型 |
| `GeometryFramework` | UDynamicMeshComponent 等动态网格组件 |
| `GeometryAlgorithms` | 几何算法（三角剖分、空间查询等） |
| `DynamicMesh` | FDynamicMesh3 的运行时动态网格库 |
| `Spatial` | 空间数据结构（八叉树等） |
| `MeshConversion` | FMeshDescription 与 FDynamicMesh3 之间的转换 |
| `PhysicsCore` | 碰撞几何体类型（FKAggregateGeom 等） |

注：`ModelingComponents` 也依赖 Core、CoreUObject、Engine、Slate、SlateCore、UMG、InputCore 等标准模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-27 | `2cd4fab7` | SReferenceSkeletonTree: preserve selection across RefreshTreeView so unrelated | 骨骼树视图刷新时保持选择状态 |
| 2026-05-27 | `32bb5ca4` | [ModelingTools] MeshVertexAttributePaintTool + SkinWeightsPaintTool: added bSyncBrushRadiusAcrossMod | 顶点属性绘制和蒙皮权重绘制工具添加画笔半径同步选项 |
| 2026-05-26 | `1b791587` | [SkeletalMeshModelingTools] Edit Skeleton tool: route deleted-bone weights to root instead of droppi | 编辑骨骼工具：删除骨骼的权重转移到根骨骼而非丢失 |
| 2026-05-26 | `cf0257a2` | MeshVertexAttributePaintTool: refactor FStrokeAccumulator to support accumulating relax brush + fix | 顶点属性绘制工具重构笔触累加器，支持松弛画笔累积 |
| 2026-05-22 | `27bc20e6` | [GeometrySelection] Skip GroupTopology rebuild on vertex-only edits | 选择系统优化：仅顶点编辑时跳过多边形组拓扑重建 |

### 维护评价

**活跃维护**。该插件持续受到 Epic Games 工程团队的积极维护：

- **年龄**：创建于 2021 年 7 月，约 4 年历史
- **更新频率**：最近一次提交在 2026 年 5 月，近期内有多次实质性功能更新
- **功能演进**：从源码可见，近期新增了 Skeletal Mesh 建模工具支持（骨骼编辑、蒙皮权重绘制）、选择系统性能优化、软选择（Soft Selection）实验性 API 等
- **实验性标记**：`.uplugin` 中 `IsBetaVersion: true`，且多个 API 使用 `UE_EXPERIMENTAL` 宏标记
- **Hidden 插件**：`Hidden: true`，不作为独立功能暴露给用户
- **推荐使用**：作为 UE5 建模工具的基础设施，如果你要开发自定义建模工具，本插件提供了成熟的基类和组件。但需注意这是一个**内部实现细节**，API 可能在版本间变化

⚠️ **注意**：本插件标记为 `IsBetaVersion=true`，且 `Installed=false`（非默认启用）。多个核心 API 标记为实验性（5.7/5.8），可能在未来版本中发生变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MeshModelingToolset)
- 官方文档：无（DocsURL 为空）
- 相关插件：[ModelingToolsEditorOnly](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MeshModelingToolset)（使用本模块的编辑器建模工具集）