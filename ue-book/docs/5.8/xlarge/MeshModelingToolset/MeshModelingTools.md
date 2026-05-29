# Mesh Modeling Toolset

> A set of modules implementing 3D mesh creation and editing based on the Interactive Tools Framework

| 属性 | 值 |
|---|---|
| 中文名 | 网格建模工具集 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质模板、蓝图资产） |
| 模块 | `MeshModelingTools` (Runtime), `MeshModelingToolsEditorOnly` (Runtime), `ModelingComponents` (Runtime), `ModelingComponentsEditorOnly` (Runtime), `ModelingOperators` (Runtime), `ModelingOperatorsEditorOnly` (Runtime), `SkeletalMeshModifiers` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-07-30 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MeshModelingToolset) | |

## 用途

Mesh Modeling Toolset 是 UE5 中核心的程序化网格建模工具集，基于 Interactive Tools Framework 实现。它提供了一整套在引擎内直接创建、编辑和雕刻 3D 网格的工具，无需离开编辑器切换到外部 DCC 软件。

该插件解决的核心问题是：**在 Unreal Engine 内完成从基础体素创建、多边形编辑、雕刻、UV 展开到网格优化的完整建模工作流**。与传统的 StaticMesh 编辑不同，它提供了类似 Blender/Maya 级别的编辑能力，直接操作 DynamicMesh。

插件默认隐藏（`Hidden: true`）且默认不启用（`IsBetaVersion: true`），需要在项目设置中手动启用后通过 Modeling Tools Editor Mode 插件的工具栏使用。

## 使用场景

- 你需要在引擎内快速创建基础几何体（方块、球体、圆柱等）→ 使用 `UAddPrimitiveTool`
- 你需要对已有网格进行自由形状雕刻 → 使用 `UDynamicMeshSculptTool` 或 `UMeshVertexSculptTool`
- 你需要进行多边形级别的网格编辑（挤出、内插、倒角等）→ 使用 `UEditMeshPolygonsTool`
- 你需要对网格进行布尔运算（并集、差集、交集）→ 使用 `UCSGMeshesTool`
- 你需要对网格进行重拓扑以获得均匀三角形分布 → 使用 `URemeshMeshTool`
- 你需要对网格进行 UV 展开和投影 → 使用 `UUVProjectionTool`
- 你需要对网格进行空间变形（弯曲、扭曲、膨胀）→ 使用 `UMeshSpaceDeformerTool`
- 你需要对网格进行平滑或偏移处理 → 使用 `USmoothMeshTool` / `UOffsetMeshTool`
- 你需要对网格顶点进行颜色绘制 → 使用 `UMeshVertexPaintTool`
- 你需要绘制并旋转生成网格 → 使用 `UDrawAndRevolveTool`
- 你需要填充网格孔洞 → 使用 `UHoleFillTool`
- 你需要通过格栅变形器变形网格 → 使用 `ULatticeDeformerTool`
- 你需要移除被遮挡的三角形 → 使用 `URemoveOccludedTrianglesTool`
- 你需要焊接网格断裂边 → 使用 `UWeldMeshEdgesTool`
- 你需要将三角面转换为多边形组 → 使用 `UConvertToPolygonsTool`

## 蓝图用法

此插件主要面向编辑器模式使用，通过 Interactive Tools Framework 在 Modeling Tools Editor Mode 中激活。以下列出核心工具及其属性类：

### 核心工具

| 工具 | 说明 | 所在类 |
|---|---|---|
| `AddPrimitiveTool` | 创建基础几何体（Box、Sphere、Cylinder 等 10 种） | `UAddPrimitiveTool` |
| `DrawPolygonTool` | 绘制多边形并挤出生成网格 | `UDrawPolygonTool` |
| `DrawAndRevolveTool` | 绘制轮廓曲线并旋转生成网格 | `UDrawAndRevolveTool` |
| `DynamicMeshSculptTool` | 基于三角形的自由形状雕刻工具 | `UDynamicMeshSculptTool` |
| `MeshVertexSculptTool` | 基于顶点的雕刻工具，支持对称 | `UMeshVertexSculptTool` |
| `EditMeshPolygonsTool` | 多边形编辑（挤出、内插、倒角等） | `UEditMeshPolygonsTool` |
| `DeformMeshPolygonsTool` | 基于多边形组拓扑的变形工具 | `UDeformMeshPolygonsTool` |
| `CSGMeshesTool` | 网格布尔运算（并集、差集、交集） | `UCSGMeshesTool` |
| `RemeshMeshTool` | 网格重拓扑 | `URemeshMeshTool` |
| `SmoothMeshTool` | 网格平滑 | `USmoothMeshTool` |
| `OffsetMeshTool` | 网格偏移/壳化 | `UOffsetMeshTool` |
| `HoleFillTool` | 孔洞填充 | `UHoleFillTool` |
| `WeldMeshEdgesTool` | 断裂边焊接 | `UWeldMeshEdgesTool` |
| `UVProjectionTool` | UV 展开投影 | `UUVProjectionTool` |
| `MeshSpaceDeformerTool` | 空间非线性变形（弯曲、扭曲、膨胀） | `UMeshSpaceDeformerTool` |
| `LatticeDeformerTool` | 格栅变形器 | `ULatticeDeformerTool` |
| `DisplaceMeshTool` | 网格位移（噪声、纹理、正弦波等） | `UDisplaceMeshTool` |
| `RemoveOccludedTrianglesTool` | 移除被遮挡三角形 | `URemoveOccludedTrianglesTool` |
| `ConvertToPolygonsTool` | 三角面转换为多边形组 | `UConvertToPolygonsTool` |
| `MeshVertexPaintTool` | 顶点颜色绘制 | `UMeshVertexPaintTool` |
| `MeshGroupPaintTool` | 多边形组绘制 | `UMeshGroupPaintTool` |
| `MeshAttributePaintTool` | 属性权重绘制 | `UMeshAttributePaintTool` |

### 雕刻刷类型

`UDynamicMeshSculptTool` 支持以下刷子类型：

| 刷子类型 | 说明 |
|---|---|
| `Move` | 沿视图平面移动顶点 |
| `PullKelvin` | Kelvin 抓取（平滑） |
| `PullSharpKelvin` | Kelvin 锐利抓取 |
| `Smooth` | 平滑顶点 |
| `Offset` | 沿法线方向偏移 |
| `SculptView` | 朝向视点方向偏移 |
| `SculptMax` | 法线方向最大高度偏移 |
| `Inflate` | 沿顶点法线膨胀 |
| `ScaleKelvin` | Kelvin 缩放 |
| `Pinch` | 向中心收缩 |
| `TwistKelvin` | Kelvin 扭曲 |
| `Flatten` | 平整到刷子区域平均平面 |
| `Plane` | 平整到初始位置平面 |
| `PlaneViewAligned` | 平整到视图对齐平面 |
| `FixedPlane` | 平整到固定世界空间平面 |
| `Resample` | 重新采样刷子区域 |

### 基础体素创建

`UAddPrimitiveTool` 及其子类支持以下体素类型：

| 体素类型 | 创建类 | 属性类 |
|---|---|---|
| Box | `UAddBoxPrimitiveTool` | `UProceduralBoxToolProperties` |
| Cylinder | `UAddCylinderPrimitiveTool` | `UProceduralCylinderToolProperties` |
| Cone | `UAddConePrimitiveTool` | `UProceduralConeToolProperties` |
| Arrow | `UAddArrowPrimitiveTool` | `UProceduralArrowToolProperties` |
| Rectangle | `UAddRectanglePrimitiveTool` | `UProceduralRectangleToolProperties` |
| Disc | `UAddDiscPrimitiveTool` | `UProceduralDiscToolProperties` |
| Torus | `UAddTorusPrimitiveTool` | `UProceduralTorusToolProperties` |
| Sphere | `UAddSpherePrimitiveTool` | `UProceduralSphereToolProperties` |
| Stairs | `UAddStairsPrimitiveTool` | `UProceduralStairsToolProperties` |
| Capsule | `UAddCapsulePrimitiveTool` | `UProceduralCapsuleToolProperties` |

## C++ 用法

### 头文件引入

```cpp
// 雕刻工具基类
#include "MeshModelingTools/Sculpting/MeshSculptToolBase.h"

// 基础体素创建
#include "MeshModelingTools/AddPrimitiveTool.h"

// 动态网格雕刻
#include "MeshModelingTools/DynamicMeshSculptTool.h"

// 多边形编辑
#include "MeshModelingTools/EditMeshPolygonsTool.h"

// 网格平滑
#include "MeshModelingTools/SmoothMeshTool.h"

// 绘制并旋转
#include "MeshModelingTools/DrawAndRevolveTool.h"

// 雕刻刷操作
#include "MeshModelingTools/Sculpting/MeshSculptBrushOps.h"
#include "MeshModelingTools/Sculpting/MeshSmoothingBrushOps.h"
#include "MeshModelingTools/Sculpting/KelvinletBrushOp.h"
```

### 基本用法：自定义雕刻刷操作

从 `MeshSculptBrushOps.h` 中的 `FSingleNormalSculptBrushOp` 可以看到自定义雕刻刷的典型模式：

```cpp
// 自定义雕刻刷操作类
class FMyCustomBrushOp : public FMeshSculptBrushOp
{
public:
    double BrushSpeedTuning = 6.0;

    // 指定刷子在预笔画网格上操作
    virtual ESculptBrushOpTargetType GetBrushTargetType() const override
    {
        return ESculptBrushOpTargetType::TargetMesh;
    }

    // 支持多种笔画类型
    virtual bool SupportsStrokeType(EMeshSculptStrokeType StrokeType) const override
    {
        switch (StrokeType)
        {
        case EMeshSculptStrokeType::Airbrush:
        case EMeshSculptStrokeType::Dots:
        case EMeshSculptStrokeType::Spacing:
            return true;
        default:
            return false;
        }
    }

    // 使用 Alpha 遮罩
    virtual bool UsesAlpha() const override { return true; }

    // 核心：实现刷子效果
    virtual void ApplyStamp(
        const FDynamicMesh3* Mesh,
        const FSculptBrushStamp& Stamp,
        const TArray<int32>& Vertices,
        TArray<FVector3d>& NewPositionsOut) override
    {
        double UsePower = Stamp.Direction * Stamp.Power * Stamp.Radius * Stamp.DeltaTime * BrushSpeedTuning;

        bool bHaveAlpha = Stamp.HasAlpha();
        FVector3d OffsetDirection = Stamp.LocalFrame.Z();

        ParallelFor(Vertices.Num(), [&](int32 k)
        {
            int32 VertIdx = Vertices[k];
            FVector3d OrigPos = Mesh->GetVertex(VertIdx);

            double Alpha = bHaveAlpha ? Stamp.StampAlphaFunc(Stamp, OrigPos) : 1.0;

            FVector3d MoveVec = UsePower * OffsetDirection;
            double Falloff = GetFalloff().Evaluate(Stamp, OrigPos) * Alpha;
            FVector3d NewPos = OrigPos + Falloff * MoveVec;
            NewPositionsOut[k] = NewPos;
        });
    }
};
```

来源：`Engine/Plugins/Runtime/MeshModelingToolset/Source/MeshModelingTools/Public/Sculpting/MeshSculptBrushOps.h`

### 基本用法：注册自定义刷子类型

从 `UMeshSculptToolBase` 的 API 可以看到刷子注册模式：

```cpp
// 在工具的 Setup 中注册刷子
void UMySculptTool::Setup()
{
    Super::Setup();

    // 注册主刷子
    RegisterBrushType(
        1,  // Identifier
        NSLOCTEXT("MyTool", "MyBrush", "My Custom Brush"),
        MakeUnique<TBasicMeshSculptBrushOpFactory<FMyCustomBrushOp>>(),
        NewObject<UMyBrushOpProps>(this)  // 属性集
    );

    // 设置默认刷子
    SetActivePrimaryBrushType(1);
}
```

来源：`Engine/Plugins/Runtime/MeshModelingToolset/Source/MeshModelingTools/Public/Sculpting/MeshSculptToolBase.h`

### 进阶用法：使用 Kelvin 物理刷子

从 `KelvinletBrushOp.h` 中可以看到基于物理的 Kelvin 刷子实现：

```cpp
// Scale Kelvin 刷子 - 基于物理的缩放变形
class FScaleKelvinletBrushOp : public FBaseKelvinletBrushOp
{
public:
    virtual void ApplyStamp(
        const FDynamicMesh3* SrcMesh,
        const FSculptBrushStamp& Stamp,
        const TArray<int32>& Vertices,
        TArray<FVector3d>& NewPositionsOut) override
    {
        // 初始化物理属性（刚度、不可压缩性等）
        SetBaseProperties(SrcMesh, Stamp);

        float Strength = GetPropertySetAs<UScaleKelvinletBrushOpProps>()->GetStrength();
        float Speed = Strength * 0.25f * FMath::Sqrt(Stamp.Radius) * Stamp.Direction;

        // 创建 Scale Kelvinlet 并应用
        FScaleKelvinlet ScaleKelvinlet(Speed, 0.35f * Size, Mu, Nu);
        ApplyKelvinlet(ScaleKelvinlet, Stamp.LocalFrame, Vertices, NewPositionsOut);

        // 应用衰减
        ApplyFalloff(Stamp, Vertices, NewPositionsOut);
    }
};
```

来源：`Engine/Plugins/Runtime/MeshModelingToolset/Source/MeshModelingTools/Public/Sculpting/KelvinletBrushOp.h`

## Demo 示例

### 自定义雕刻刷属性集

```cpp
// MyBrushOpProps.h
#pragma once

#include "InteractiveTool.h"
#include "Sculpting/MeshBrushOpBase.h"
#include "MyBrushOpProps.generated.h"

UCLASS(MinimalAPI)
class UMySculptBrushOpProps : public UMeshSculptBrushOpProps
{
    GENERATED_BODY()
public:
    /** 刷子强度 */
    UPROPERTY(EditAnywhere, Category = MyBrush, meta = (DisplayName = "Strength",
        UIMin = "0.0", UIMax = "1.0", ClampMin = "0.0", ClampMax = "1.0"))
    float Strength = 0.5f;

    /** 衰减量 */
    UPROPERTY(EditAnywhere, Category = MyBrush, meta = (DisplayName = "Falloff",
        UIMin = "0.0", UIMax = "1.0", ClampMin = "0.0", ClampMax = "1.0"))
    float Falloff = 0.5f;

    /** 自定义参数：变形速率 */
    UPROPERTY(EditAnywhere, Category = MyBrush, meta = (DisplayName = "Deform Speed",
        UIMin = "0.1", UIMax = "5.0", ClampMin = "0.01", ClampMax = "20.0"))
    float DeformSpeed = 1.0f;

    virtual float GetStrength() override { return Strength; }
    virtual void SetStrength(float NewStrength) override { Strength = FMathf::Clamp(NewStrength, 0.0f, 1.0f); }
    virtual float GetFalloff() override { return Falloff; }
    virtual bool SupportsStrengthPressure() override { return true; }
};
```

```cpp
// MySculptBrushOp.h
#pragma once

#include "Sculpting/MeshBrushOpBase.h"
#include "MyBrushOpProps.h"

class FMySculptBrushOp : public FMeshSculptBrushOp
{
public:
    virtual ESculptBrushOpTargetType GetBrushTargetType() const override
    {
        return ESculptBrushOpTargetType::SculptMesh;
    }

    virtual EStampAlignmentType GetStampAlignmentType() const override
    {
        return EStampAlignmentType::HitNormal;
    }

    virtual bool SupportsStrokeType(EMeshSculptStrokeType StrokeType) const override
    {
        return StrokeType == EMeshSculptStrokeType::Airbrush
            || StrokeType == EMeshSculptStrokeType::Dots
            || StrokeType == EMeshSculptStrokeType::Spacing;
    }

    virtual bool UsesAlpha() const override { return true; }

    virtual void BeginStroke(
        const FDynamicMesh3* Mesh,
        const FSculptBrushStamp& Stamp,
        const TArray<int32>& InitialVertices) override
    {
        // 记录笔画开始时的状态
    }

    virtual void ApplyStamp(
        const FDynamicMesh3* Mesh,
        const FSculptBrushStamp& Stamp,
        const TArray<int32>& Vertices,
        TArray<FVector3d>& NewPositionsOut) override
    {
        UMySculptBrushOpProps* Props = GetPropertySetAs<UMySculptBrushOpProps>();
        double Speed = Props->DeformSpeed * Stamp.Radius * Stamp.Power * Stamp.DeltaTime;
        FVector3d Direction = Stamp.LocalFrame.Z();

        ParallelFor(Vertices.Num(), [&](int32 k)
        {
            int32 VertIdx = Vertices[k];
            FVector3d OrigPos = Mesh->GetVertex(VertIdx);

            double Falloff = GetFalloff().Evaluate(Stamp, OrigPos);
            bool bHaveAlpha = Stamp.HasAlpha();
            double Alpha = bHaveAlpha ? Stamp.StampAlphaFunc(Stamp, OrigPos) : 1.0;

            FVector3d Offset = Speed * Direction * Falloff * Alpha * Stamp.Direction;
            NewPositionsOut[k] = OrigPos + Offset;
        });
    }

    virtual void EndStroke(
        const FDynamicMesh3* Mesh,
        const FSculptBrushStamp& Stamp,
        const TArray<int32>& FinalVertices) override
    {
        // 笔画结束时的清理
    }
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GeometryFramework` | DynamicMesh / DynamicMeshComponent 网格框架 |
| `ModelingOperators` | 网格操作算子（Remesh、Weld、CSG 等） |
| `ModelingComponents` | 建模工具的公共组件（预览网格、选择机制等） |
| `InteractiveToolsFramework` | 交互工具框架基类和接口 |
| `MeshDescription` | 静态网格的 MeshDescription 数据格式 |
| `DynamicMesh` | FDynamicMesh3 网格数据结构和几何算法 |
| `GeometryProcessing` | 几何处理算法（布尔运算、重拓扑、UV 等） |
| `MeshConversion` | MeshDescription 与 DynamicMesh 之间转换 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-27 | `32bb5ca4` | [ModelingTools] MeshVertexAttributePaintTool + SkinWeightsPaintTool: added bSyncBrushRadiusAcrossMod | 属性绘制工具新增跨模式刷子半径同步功能 |
| 2026-05-26 | `1b791587` | [SkeletalMeshModelingTools] Edit Skeleton tool: route deleted-bone weights to root instead of droppi | 骨骼编辑工具将删除骨骼权重路由到根骨骼 |
| 2026-05-26 | `cf0257a2` | MeshVertexAttributePaintTool: refactor FStrokeAccumulator to support accumulating relax brush + fix | 重构顶点属性绘制的笔画累加器以支持松弛刷 |
| 2026-05-22 | `27bc20e6` | [GeometrySelection] Skip GroupTopology rebuild on vertex-only edits | 仅顶点编辑时跳过 GroupTopology 重建以提升性能 |

### 维护评价

**活跃维护中。** Mesh Modeling Toolset 是 UE5 建模工具的核心插件，由 Epic Games 持续维护。

- **创建时间**：2021 年 7 月，从 Experimental 迁移而来（原 MeshModelingTools 插件更早）
- **更新频率**：每周都有实质性更新，最近一次更新在 2026 年 5 月，包含新功能和 Bug 修复
- **状态**：标记为实验性（`IsBetaVersion: true`），但功能非常成熟且广泛使用
- **代码规模**：495 个源文件，属于大型插件，包含 7 个运行时模块
- **隐藏状态**：默认隐藏（`Hidden: true`），需要通过 Modeling Tools Editor Mode 插件间接使用
- **推荐使用**：✅ 推荐。这是 Epic 官方维护的引擎内建模解决方案，功能完整且持续迭代。虽然标记为实验性，但已在大量项目中经过验证。

⚠️ **注意**：该插件标记为实验性（`IsBetaVersion: true`），API 可能在引擎版本间发生变化。建议关注版本更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MeshModelingToolset)
- 官方文档：无（`.uplugin` 中未指定 DocsURL）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MeshModelingToolset/Tests)（如有）