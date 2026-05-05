# Mesh Modeling Toolset

> A set of modules implementing 3D mesh creation and editing based on the Interactive Tools Framework

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（材质、工具预设资产） |
| 模块 | `MeshModelingTools` (Runtime), `MeshModelingToolsEditorOnly` (Runtime), `ModelingComponents` (Runtime), `ModelingComponentsEditorOnly` (Runtime), `ModelingOperators` (Runtime), `ModelingOperatorsEditorOnly` (Runtime), `SkeletalMeshModifiers` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-10-01 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MeshModelingToolset) | |

---

## 用途

Mesh Modeling Toolset 是 UE5 编辑器中 **建模模式（Modeling Mode）** 的核心实现。它基于 Interactive Tools Framework 构建了一整套 3D 网格创建与编辑工具，涵盖多边形建模、体素布尔运算、UV 编辑、网格修复等功能。

本文档聚焦于 **ModelingComponents** 模块——它是整个工具集的 **基础设施层**，提供：

- **基类工具**：单选/多选/体素网格编辑工具的抽象基类
- **目标接口**：抽象网格数据源（DynamicMesh 提供者、提交者、持久化源）
- **选择机制**：边界选择、多边形组选择、点击选择等交互机制
- **转换工具**：StaticMesh / SkeletalMesh / GeometryCache / Volume / Spline → DynamicMesh 的转换
- **撤销/重做系统**：网格修改、选择变更、多边形组变更的可逆变更记录
- **属性集**：轴过滤、颜色通道过滤、体素参数、权重图、多边形组层等通用属性
- **吸附与变换**：射线空间吸附求解器、快速变换器
- **可视化辅助**：体积笔刷指示器、几何选择可视化

简而言之，ModelingComponents 解决的问题是：**Interactive Tools Framework 是通用的，不懂网格；而所有网格建模工具都需要相同的基础设施**。这个模块就是那个基础设施。

## 使用场景

- 你要 **开发自定义网格编辑工具** → 继承 `USingleSelectionMeshEditingTool` 或 `UMultiSelectionMeshEditingTool`
- 你需要 **在运行时转换网格格式**（如 Volume → DynamicMesh）→ 使用 `UE::Conversion` 命名空间的工具函数
- 你要实现 **网格操作的撤销/重做** → 使用 `FMeshSelectionChange`、`FMeshPolygroupChange` 等变更类
- 你需要 **交互式边界/多边形组选择** → 使用 `UBoundarySelectionMechanic` 或 `UMeshTopologySelectionMechanic`
- 你要构建 **体素布尔运算工具** → 继承 `UBaseVoxelTool`
- 你需要 **射线空间吸附**（如顶点吸附、边吸附）→ 使用 `FRaySpatialSnapSolver`
- 你要 **将骨骼网格体转换为可编辑网格** → 使用 `SkinnedMeshComponentToDynamicMesh`

## 模块架构

```
MeshModelingToolset/
├── ModelingComponents          ← 基础设施层（本文档重点）
├── ModelingComponentsEditorOnly ← 编辑器专用基础设施
├── ModelingOperators           ← 网格操作算子（布尔、简化、细分等）
├── ModelingOperatorsEditorOnly ← 编辑器专用算子
├── MeshModelingTools           ← 具体工具实现（雕刻、UV、修复等）
├── MeshModelingToolsEditorOnly ← 编辑器专用工具
└── SkeletalMeshModifiers       ← 骨骼网格修改器
```

依赖关系：`MeshModelingTools` → `ModelingOperators` → `ModelingComponents`

---

## 蓝图用法

ModelingComponents 主要是 C++ 基础设施层，蓝图可直接使用的 API 有限，主要集中在 **属性结构体** 和 **属性集** 上。

### 可蓝图使用的结构体

| 结构体 | 说明 | 头文件 |
|---|---|---|
| `FModelingToolsAxisFilter` | 轴过滤（X/Y/Z 开关），用于限制变换操作的轴向 | `AxisFilterPropertyType.h` |
| `FModelingToolsColorChannelFilter` | 颜色通道过滤（R/G/B/A 开关），用于颜色操作 | `ColorChannelFilterPropertyType.h` |

### 可蓝图使用的枚举

| 枚举 | 说明 | 头文件 |
|---|---|---|
| `EBakeTextureResolution` | 烘焙纹理分辨率（16~8192） | `BakingTypes.h` |
| `EBakeTextureBitDepth` | 烘焙纹理位深（8/16 bit） | `BakingTypes.h` |
| `EBakeTextureSamplesPerPixel` | 烘焙每像素采样数（1~256） | `BakingTypes.h` |
| `ELatticeInterpolationType` | 晶格插值类型（线性/三次） | `LatticeManager.h` |

### 属性集（Tool Property Sets）

这些属性集可被蓝图工具引用，在细节面板中显示：

| 属性集 | 说明 | 头文件 |
|---|---|---|
| `UPolygroupLayersProperties` | 多边形组层选择器，提供下拉列表选择活动组层 | `PolygroupLayersProperties.h` |
| `UWeightMapSetProperties` | 权重图选择器，支持从 MeshDescription 自动发现权重图 | `WeightMapSetProperties.h` |
| `UVoxelProperties` | 体素参数（体素数量、自动简化、移除内部表面等） | `VoxelProperties.h` |

### 使用示例（蓝图描述）

在蓝图中使用 `FModelingToolsAxisFilter`：

1. 创建一个 `FModelingToolsAxisFilter` 变量
2. 在细节面板中勾选/取消 X、Y、Z 轴
3. 调用 `AnyAxisFiltered()` 检查是否有轴被过滤
4. 将过滤结果传递给变换操作，限制操作只在未过滤的轴上执行

---

## C++ 用法

### 头文件引入

```cpp
// 基础设施
#include "ModelingComponents.h"

// 具体功能头文件
#include "BaseTools/SingleSelectionMeshEditingTool.h"
#include "BaseTools/MultiSelectionMeshEditingTool.h"
#include "BaseTools/BaseVoxelTool.h"
#include "TargetInterfaces/DynamicMeshProvider.h"
#include "TargetInterfaces/DynamicMeshCommitter.h"
#include "ConversionUtils/VolumeToDynamicMesh.h"
#include "ConversionUtils/SkinnedMeshToDynamicMesh.h"
#include "Selection/BoundarySelectionMechanic.h"
#include "Snapping/RaySpatialSnapSolver.h"
#include "Changes/MeshSelectionChange.h"
```

### 核心接口

#### IDynamicMeshProvider — 获取网格数据

```cpp
// 从工具目标获取 DynamicMesh 副本
IDynamicMeshProvider* MeshProvider = /* 从 ToolTarget 获取 */;
UE::Geometry::FDynamicMesh3 Mesh = MeshProvider->GetDynamicMesh();

// 请求带切线的网格（5.5+ 推荐用 FGetMeshParameters）
FGetMeshParameters Params;
Params.bWantMeshTangents = true;
UE::Geometry::FDynamicMesh3 MeshWithTangents = MeshProvider->GetDynamicMesh(Params);
```

#### IDynamicMeshCommitter — 提交网格修改

```cpp
// 提交修改后的网格
IDynamicMeshCommitter* MeshCommitter = /* 从 ToolTarget 获取 */;

IDynamicMeshCommitter::FDynamicMeshCommitInfo CommitInfo;
CommitInfo.bPositionsChanged = true;
CommitInfo.bTopologyChanged = false;  // 优化：拓扑没变就跳过
CommitInfo.bNormalsChanged = true;

MeshCommitter->CommitDynamicMesh(ModifiedMesh, CommitInfo);
```

#### IPersistentDynamicMeshSource — 持久化网格源（带撤销支持）

```cpp
// 获取持久化网格容器
IPersistentDynamicMeshSource* Source = /* ... */;
UDynamicMesh* MeshContainer = Source->GetDynamicMeshContainer();

// 修改网格后，提交变更（自动进入撤销系统）
auto Change = MakeUnique<FMeshReplacementChange>(/* ... */);
Source->CommitDynamicMeshChange(MoveTemp(Change), NSLOCTEXT("MyTool", "Edit", "Edit Mesh"));
```

### 转换工具

```cpp
// Volume → DynamicMesh
#include "ConversionUtils/VolumeToDynamicMesh.h"

AVolume* Volume = /* ... */;
UE::Geometry::FDynamicMesh3 Mesh;
UE::Conversion::FVolumeToMeshOptions Options;
Options.bInWorldSpace = true;
Options.bSetGroups = true;
Options.bGenerateNormals = true;
UE::Conversion::VolumeToDynamicMesh(Volume, Mesh, Options);

// SkinnedMeshComponent → DynamicMesh
#include "ConversionUtils/SkinnedMeshToDynamicMesh.h"

USkinnedMeshComponent* SkinnedComp = /* ... */;
UE::Geometry::FDynamicMesh3 SkinnedMesh;
UE::Conversion::SkinnedMeshComponentToDynamicMesh(*SkinnedComp, SkinnedMesh, /*LOD=*/0, /*bWantTangents=*/true);

// GeometryCache → DynamicMesh
#include "ConversionUtils/GeometryCacheToDynamicMesh.h"

UGeometryCache* Cache = /* ... */;
UE::Geometry::FDynamicMesh3 CacheMesh;
UE::Conversion::FGeometryCacheToDynamicMeshOptions CacheOpts;
CacheOpts.Time = 0.0f;
UE::Conversion::GeometryCacheToDynamicMesh(*Cache, CacheMesh, CacheOpts);
```

### 撤销/重做系统

```cpp
// 选择变更
#include "Changes/MeshSelectionChange.h"

// 构建一个"添加面选择"的变更
FMeshSelectionChangeBuilder Builder(EMeshSelectionElementType::Face, /*bAdding=*/true);
Builder.Add(TriangleID);
Builder.Add(TArray<int32>{10, 20, 30});
TUniquePtr<FMeshSelectionChange> Change = MoveTemp(Builder.Change);

// 应用变更
Change->Apply(SelectionSet);

// 撤销变更
Change->Revert(SelectionSet);

// 多边形组变更
#include "Changes/MeshPolygroupChange.h"

FDynamicMeshGroupEditBuilder GroupBuilder(Mesh);
GroupBuilder.SaveTriangle(TriangleID);  // 自动记录旧/新组ID
GroupBuilder.SaveTriangle(AnotherTriID, OldGroup, NewGroup);
TUniquePtr<FDynamicMeshGroupEdit> GroupEdit = GroupBuilder.ExtractResult();
```

### 选择机制

```cpp
// 边界选择
#include "Selection/BoundarySelectionMechanic.h"

UBoundarySelectionMechanic* BoundaryMechanic = NewObject<UBoundarySelectionMechanic>();
BoundaryMechanic->Initialize(
    Mesh,                          // FDynamicMesh3*
    TargetTransform,               // FTransform3d
    World,                         // UWorld*
    BoundaryLoops,                 // FMeshBoundaryLoops*
    [this]() { return Spatial; },  // 获取空间查询树的函数
    UBoundarySelectionMechanic::EBoundarySelectionType::Loops
);

// 在工具的 OnMouseMove 中更新高亮
BoundaryMechanic->UpdateHighlight(WorldRay);

// 在工具的 OnClicked 中更新选择
FVector3d HitPos, HitNormal;
BoundaryMechanic->UpdateSelection(WorldRay, HitPos, HitNormal);
```

### 吸附系统

```cpp
#include "Snapping/RaySpatialSnapSolver.h"

UE::Geometry::FRaySpatialSnapSolver SnapSolver;

// 添加吸附目标
SnapSolver.AddPointTarget(FVector3d(100, 0, 0));
SnapSolver.AddLineTarget(FVector3d(0, 0, 0), FVector3d(100, 100, 0));

// 可选：设置点约束函数（如吸附到网格）
SnapSolver.PointConstraintFunc = [this](const FVector3d& Point) -> FVector3d {
    return SnapToGrid(Point, GridSize);
};

// 求解
FRay3d Ray(Origin, Direction);
SnapSolver.UpdateSnappedPoint(Ray);

// 获取结果
FVector3d SnappedPoint = SnapSolver.GetCurrentSnappedPoint();

// 可视化
SnapSolver.Draw(Renderer, LineLength);
```

### 值监视器（运行时属性轮询）

```cpp
#include "Changes/ValueWatcher.h"

// 在运行时，UProperty 不会触发 PropertyChanged 事件
// TValueWatcher 通过轮询检测变化
TValueWatcher<float> VoxelSizeWatcher;
VoxelSizeWatcher.Initialize(
    [this]() { return VoxProperties->VoxelCount; },     // 获取当前值
    [this](float NewValue) { RebuildVoxelMesh(NewValue); }, // 值变化时回调
    VoxProperties->VoxelCount                             // 初始值
);

// 在工具的 OnTick 中调用
VoxelSizeWatcher.CheckAndUpdate();
```

---

## Demo 示例

一个最小的自定义网格编辑工具，继承 `USingleSelectionMeshEditingTool`：

### MyMeshSmoothingTool.h

```cpp
#pragma once

#include "BaseTools/SingleSelectionMeshEditingTool.h"
#include "MyMeshSmoothingTool.generated.h"

UCLASS()
class UMyMeshSmoothingToolBuilder : public USingleSelectionMeshEditingToolBuilder
{
    GENERATED_BODY()
public:
    virtual USingleSelectionMeshEditingTool* CreateNewTool(
        const FToolBuilderState& SceneState) const override
    {
        return NewObject<UMyMeshSmoothingTool>();
    }
};

UCLASS()
class UMyMeshSmoothingToolProperties : public UInteractiveToolPropertySet
{
    GENERATED_BODY()
public:
    /** 平滑强度 */
    UPROPERTY(EditAnywhere, Category = "Smoothing", meta = (UIMin = "0", UIMax = "1"))
    float SmoothStrength = 0.5f;

    /** 迭代次数 */
    UPROPERTY(EditAnywhere, Category = "Smoothing", meta = (UIMin = "1", UIMax = "10"))
    int32 Iterations = 3;
};

UCLASS()
class UMyMeshSmoothingTool : public USingleSelectionMeshEditingTool
{
    GENERATED_BODY()

public:
    virtual void Setup() override;
    virtual void OnTick(float DeltaTime) override;
    virtual void OnShutdown(EToolShutdownType ShutdownType) override;

private:
    UPROPERTY()
    TObjectPtr<UMyMeshSmoothingToolProperties> Settings;

    // 原始网格备份（用于撤销）
    TSharedPtr<UE::Geometry::FDynamicMesh3, ESPMode::ThreadSafe> OriginalMesh;
};
```

### MyMeshSmoothingTool.cpp

```cpp
#include "MyMeshSmoothingTool.h"
#include "DynamicMesh/DynamicMesh3.h"
#include "TargetInterfaces/DynamicMeshProvider.h"
#include "TargetInterfaces/DynamicMeshCommitter.h"
#include "Changes/MeshReplacementChange.h"

void UMyMeshSmoothingTool::Setup()
{
    Super::Setup();

    // 注册属性集（自动显示在细节面板中）
    Settings = NewObject<UMyMeshSmoothingToolProperties>(this);
    AddToolPropertySource(Settings);

    // 获取输入网格
    IDynamicMeshProvider* Provider = Cast<IDynamicMeshProvider>(Target);
    FDynamicMesh3 InputMesh = Provider->GetDynamicMesh();

    // 备份原始网格
    OriginalMesh = MakeShared<FDynamicMesh3, ESPMode::ThreadSafe>(MoveTemp(InputMesh));
}

void UMyMeshSmoothingTool::OnTick(float DeltaTime)
{
    // 使用 TValueWatcher 监听属性变化（运行时兼容）
    // 实际平滑逻辑在此处执行
}

void UMyMeshSmoothingTool::OnShutdown(EToolShutdownType ShutdownType)
{
    if (ShutdownType == EToolShutdownType::Accept)
    {
        // 执行平滑操作
        FDynamicMesh3 SmoothedMesh = *OriginalMesh;
        for (int32 i = 0; i < Settings->Iterations; ++i)
        {
            // LaplacianSmooth(SmoothedMesh, Settings->SmoothStrength);
        }

        // 提交修改
        IDynamicMeshCommitter* Committer = Cast<IDynamicMeshCommitter>(Target);
        Committer->CommitDynamicMesh(SmoothedMesh);
    }
    // 如果是 Cancel，则不做任何操作，原始网格保持不变

    Super::OnShutdown(ShutdownType);
}
```

---

## 模块依赖

从头文件分析，ModelingComponents 依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `GeometryCore` | FDynamicMesh3、FMeshAABBTree3、PolygroupSet 等核心几何类型 |
| `InteractiveToolsFramework` | UInteractiveTool、UInteractiveGizmo、FToolCommandChange 等工具框架 |
| `MeshDescription` | FMeshDescription 网格描述格式（引擎标准网格表示） |
| `GeometryFramework` | UDynamicMesh、UDynamicMeshComponent（运行时动态网格组件） |

> 无其他特殊依赖。标准 Core/Engine/Slate 等已省略。

---

## 维护状态

### 近期更新

```
- 52235111ca10 Merge Actor - Approximate: 修复距离剔除导致场景捕获阶段 Actor 变黑的问题
- 4a3600a63cce Merge Actor - Approximate: 修复强制 LOD 网格在场景捕获阶段不渲染的问题
- cf61855939fa PCG Editor Mode - 工作数据架构重构；PCGComponent 管理处理数据
```

> 注：以上为插件目录级别的最近提交，部分可能涉及 MeshModelingToolset 的依赖模块而非核心建模功能。

### 维护评价

- **创建时间**：2019 年 10 月，随 UE4.24 的 Modeling Tools Editor Mode 一起引入
- **维护状态**：**活跃维护中**。作为 UE5 编辑器建模模式的核心，Epic 持续投入开发
- **实验性标记**：`.uplugin` 中 `IsBetaVersion=true`，`Hidden=true`——虽然标记为 Beta，但实际上已经是 UE5 编辑器的标准功能
- **模块规模**：850+ 源文件，属于超大型插件
- **已知限制**：
  - 标记为 Beta，API 可能在版本间发生变化
  - 部分模块标记为 Hidden，不建议直接在生产项目中依赖其内部 API
  - `UE_DEPRECATED(5.5, ...)` 标记表明部分 API 正在迭代更新
- **推荐程度**：✅ **强烈推荐使用**。这是 UE5 官方建模工具的基础设施，稳定性和质量有保障。如果你要开发自定义建模工具，这是最佳起点。但注意 API 可能随版本变化，需关注废弃标记。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MeshModelingToolset)
- [ModelingComponents 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MeshModelingToolset/Source/ModelingComponents)
- 官方文档：无（`.uplugin` 中 DocsURL 为空）
- [UE5 建模模式官方文档](https://docs.unrealengine.com/5.0/en-US/modeling-tools-in-unreal-engine/)