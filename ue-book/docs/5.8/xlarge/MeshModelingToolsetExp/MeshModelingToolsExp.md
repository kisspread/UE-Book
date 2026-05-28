# Experimental Mesh Modeling Toolset

> A set of experimental modules implementing 3D mesh creation and editing based on the Interactive Tools Framework

| 属性 | 值 |
|---|---|
| 中文名 | 实验性网格建模工具集 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质资产、工具蓝图） |
| 模块 | `GeometryProcessingAdapters` (Runtime), `MeshModelingToolsEditorOnlyExp` (Runtime), `MeshModelingToolsExp` (Runtime), `ModelingEditorUI` (Runtime), `ModelingUI` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-07-30 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshModelingToolsetExp) | |

## 用途

本插件是从主 `MeshModelingToolset` 拆分出的**实验性**分支，包含尚在开发和测试阶段的 3D 网格创建与编辑工具。这些工具均基于 UE5 的 **Interactive Tools Framework** 构建，提供统一的交互式编辑体验。

该插件主要解决以下问题：
- **高质量网格烘焙**：将高模细节（法线、环境光遮蔽、曲率、高度等）烘焙到低模纹理或顶点颜色上
- **程序化网格生成**：从样条线、边界、多边形路径等几何体生成网格
- **网格拓扑编辑**：选择、删除、分离、翻转法线、创建 PolyGroup 等操作
- **碰撞体生成**：自动拟合简单碰撞几何体（凸包、包围盒、胶囊体等）
- **体素操作**：基于体素的平滑布尔运算和实体化
- **物理/UV/枢轴点编辑**：UV 岛编辑、枢轴点变换、UV 传输等

**重要**：这是实验性插件，默认禁用且隐藏。许多工具在成熟后会迁移到主 `MeshModelingToolset`。在生产环境中使用需谨慎。

## 使用场景

- 你需要将高模细节烘焙到低模 → 使用 `BakeMeshAttributeMaps` 系列工具
- 你需要从样条线快速生成拉伸/旋转网格 → 使用 `TriangulateSplines` 或 `RevolveSpline` 工具
- 你需要为复杂网格自动生成碰撞体 → 使用 `SetCollisionGeometry` 工具
- 你需要快速进行体素级别的布尔运算 → 使用 `VoxelBlendMeshes` 或 `SelfUnionMeshes`
- 你需要在 3D 视口中绘制多边形路径并挤出 → 使用 `DrawPolyPath` 工具
- 你需要检查网格的法线、边界、UV 接缝等问题 → 使用 `MeshInspector` 工具
- 你需要进行交互式 UV 岛编辑 → 使用 `EditUVIslands` 工具
- 你需要编辑枢轴点位置 → 使用 `EditPivot` 工具

## 蓝图用法

本插件的工具主要通过编辑器工具模式（Editor Mode / Modeling Tools 面板）使用，而非直接在蓝图中调用。核心功能通过 `UInteractiveTool` 派生类和关联的 `UInteractiveToolPropertySet` 属性集暴露。

### 核心节点（可配置属性集）

| 节点 | 说明 | 所在类 |
|---|---|---|
| 设置碰撞几何类型 | 选择包围盒/凸包/胶囊体等拟合方式 | `USetCollisionGeometryToolProperties` |
| 配置烘焙输出类型 | 设置法线/AO/曲率/高度等贴图类型 | `UBakeMeshAttributeMapsToolProperties` |
| 配置挤出参数 | 设置挤出距离、细分、折角等 | `UExtrudeMeshSelectionToolProperties` |
| 配置镜像操作 | 设置镜像平面、焊接选项等 | `UMirrorToolProperties` |
| 配置平面切割 | 设置保留两侧、填充孔洞等 | `UPlaneCutToolProperties` |
| 配置图案排列 | 设置线性/网格/径向图案参数 | `UPatternToolSettings` |
| 配置体素混合 | 设置混合强度、衰减等 | `UVoxelBlendMeshesToolProperties` |

### 使用示例（编辑器工具面板描述）

1. 在编辑器中选择一个或多个 StaticMesh Actor
2. 打开 **Modeling** 工具模式或 **Modeling Tools** 面板
3. 在工具列表中选择需要的工具（如 Extrude、Mirror、Bake 等）
4. 在右侧面板调整工具属性
5. 点击 **Accept** 应用结果或 **Cancel** 取消

## C++ 用法

本插件的工具通过 `UInteractiveToolBuilder` 创建，适用于需要扩展建模工具管线的场景。

### 头文件引入

```cpp
// 主要工具头文件
#include "MeshModelingToolsExp.h"

// 烘焙工具
#include "BakeMeshAttributeMapsTool.h"
#include "BakeMeshAttributeVertexTool.h"

// 碰撞工具
#include "Physics/SetCollisionGeometryTool.h"

// 样条线工具
#include "Spline/BaseMeshFromSplinesTool.h"
#include "TriangulateSplinesTool.h"
```

### 基本用法 — 程序化触发烘焙工具

以下示例展示了如何在 C++ 中以编程方式构建烘焙工具（来源：`BakeMeshAttributeMapsTool.h`）：

```cpp
#include "BakeMeshAttributeMapsTool.h"

// 获取工具构建器
UBakeMeshAttributeMapsToolBuilder* Builder = NewObject<UBakeMeshAttributeMapsToolBuilder>();

// 检查是否可以构建（需要至少两个选择的网格）
FToolBuilderState SceneState;
if (Builder->CanBuildTool(SceneState))
{
    // 构建工具实例
    UMultiSelectionMeshEditingTool* Tool = Builder->CreateNewTool(SceneState);
    // 工具会自动注册到 ToolManager
}
```

### 进阶用法 — 自定义烘焙参数

```cpp
#include "BakeMeshAttributeMapsTool.h"
#include "BakeMeshAttributeTool.h"

// 配置烘焙输出类型（使用位标记组合）
int32 MapTypes = static_cast<int32>(EBakeMapType::TangentSpaceNormal)
               | static_cast<int32>(EBakeMapType::AmbientOcclusion)
               | static_cast<int32>(EBakeMapType::Curvature);

// 设置纹理分辨率
EBakeTextureResolution Resolution = EBakeTextureResolution::Resolution1024;

// 设置位深度
EBakeTextureBitDepth BitDepth = EBakeTextureBitDepth::ChannelBits8;

// 烘焙结果类型枚举
// EBakeMapType::TangentSpaceNormal   - 切线空间法线
// EBakeMapType::ObjectSpaceNormal    - 物体空间法线
// EBakeMapType::BentNormal           - 弯曲法线
// EBakeMapType::Curvature            - 曲率
// EBakeMapType::AmbientOcclusion     - 环境光遮蔽
// EBakeMapType::Height               - 高度图
// EBakeMapType::Texture              - 纹理转移
// EBakeMapType::VertexColor          - 顶点颜色
// EBakeMapType::MaterialID           - 材质 ID
// EBakeMapType::PolyGroupID          - PolyGroup ID
```

### 自定义样条线网格生成工具

基于 `UBaseMeshFromSplinesTool` 扩展自定义工具（来源：`BaseMeshFromSplinesTool.h`）：

```cpp
#include "Spline/BaseMeshFromSplinesTool.h"

UCLASS()
class UMyCustomSplineTool : public UBaseMeshFromSplinesTool
{
    GENERATED_BODY()

public:
    // 自定义资产名称
    virtual FString GeneratedAssetBaseName() const override
    {
        return FString(TEXT("MyCustomSplineMesh"));
    }

    // 自定义事务名称
    virtual FText TransactionName() const override
    {
        return NSLOCTEXT("MyTools", "SplineRevolve", "Revolve Spline");
    }

    // 响应样条线更新
    virtual void OnSplineUpdate() override
    {
        // 在样条线变更时自定义逻辑
        // 例如：重新采样点、更新预览等
    }

    // 自定义资产生成中的变换处理
    virtual FTransform3d HandleOperatorTransform(
        const FDynamicMeshOpResult& OpResult) override
    {
        // 自定义变换逻辑
        return OpResult.Transform;
    }
};
```

## Demo 示例

### 最小可编译示例 — 自定义样条线旋转工具

```cpp
// MyRevolveSplineTool.h
#pragma once

#include "CoreMinimal.h"
#include "Spline/BaseMeshFromSplinesTool.h"
#include "MyRevolveSplineTool.generated.h"

UCLASS()
class MYMODULE_API UMyRevolveSplineTool : public UBaseMeshFromSplinesTool
{
    GENERATED_BODY()

public:
    virtual void Setup() override
    {
        Super::Setup();
        // 设置完成后自定义初始化
    }

    virtual TUniquePtr<UE::Geometry::FDynamicMeshOperator> MakeNewOperator() override
    {
        // 返回自定义网格操作符
        // 可基于 ProfileCurve 生成旋转体
        return Super::MakeNewOperator();
    }

protected:
    virtual void OnSplineUpdate() override
    {
        // 当样条线变更时重新计算
        // PollSplineUpdates() 会检测样条线版本变化
    }

    virtual FString GeneratedAssetBaseName() const override
    {
        return TEXT("MyRevolve");
    }
};
```

```cpp
// MyRevolveSplineTool.cpp
#include "MyRevolveSplineTool.h"
#include "DynamicMesh/DynamicMesh3.h"

// 继承自 UBaseMeshFromSplinesTool 的核心功能已在基类实现
// 包括：轮询样条线更新、生成网格、管理预览、资产生成等
// 子类只需覆盖特定行为
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MeshModelingTools` | 主建模工具集模块（非实验性），提供基础工具类和通用属性集 |
| `GeometryFramework` | 提供 UPreviewMesh、UDynamicMeshComponent 等几何框架类 |
| `ModelingComponents` | 提供 UMeshOpPreviewWithBackgroundCompute、UConstructionPlaneMechanic 等建模组件 |
| `PhysicsCore` | 碰撞工具用于物理碰撞几何体处理 |
| `DynamicMesh` | 动态网格数据结构（FDynamicMesh3 等） |
| `MeshConversion` | 网格数据在不同格式间的转换 |
| `SkeletalMeshModelingTools` | 骨骼网格建模工具（UV 传输、烘焙等） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-27 | `32bb5ca4` | [ModelingTools] MeshVertexAttributePaintTool + SkinWeightsPaintTool: added bSyncBrushRadiusAcrossMod | 顶点属性绘制和蒙皮权重绘制工具新增跨模式同步画笔半径 |
| 2026-05-26 | `cf0257a2` | MeshVertexAttributePaintTool: refactor FStrokeAccumulator to support accumulating relax brush + fix | 重构顶点属性绘制工具的笔触累加器以支持松弛画笔累积并修复问题 |
| 2026-05-22 | `4938c498` | [SkeletalMeshModelingTools] Set AutoCalculated tangents mode on preview/sculpt meshes that lack valid | 骨骼网格建模工具为缺少有效切线的预览/雕刻网格设置自动计算切线模式 |
| 2026-05-19 | `12cf9c64` | [SkeletalMeshModelingTools] Fixed polygroup edge visualizer not updated after mesh deformation | 修复骨骼网格变形后 PolyGroup 边界可视化不更新的问题 |
| 2026-05-14 | `f6425490` | [ModelingTools] Add UMeshElementsVisualizer to skin-weights tool; default group-boundary settings ON | 为蒙皮权重工具添加网格元素可视化器；默认开启组边界设置 |

### 维护评价

- **创建时间**：2021 年 7 月，约 4 年历史
- **活跃度**：**活跃维护中**。最近一次更新在 2026 年 5 月，频率较高（几乎每周都有提交）
- **更新内容**：持续的功能增强和 Bug 修复，涉及顶点属性绘制、骨骼网格建模、可视化器等
- **实验性状态**：仍标记为 `IsExperimentalVersion=true`，`Hidden=true`，`Installed=false`
- **推荐程度**：适合需要前沿建模工具的开发者。但因为是实验性插件，API 可能随版本变化。生产环境中建议关注工具何时迁移到主 `MeshModelingToolset`

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshModelingToolsetExp)
- 官方文档：无（实验性插件无官方文档链接）
- [非实验性版本 MeshModelingToolset](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MeshModelingToolset)