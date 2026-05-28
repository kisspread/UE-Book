# Experimental Mesh Modeling Toolset

> A set of experimental modules implementing 3D mesh creation and editing based on the Interactive Tools Framework

| 属性 | 值 |
|---|---|
| 中文名 | 实验性网格建模工具集 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器工具、材质、UI资产） |
| 模块 | `GeometryProcessingAdapters` (Runtime), `MeshModelingToolsEditorOnlyExp` (Runtime), `MeshModelingToolsExp` (Runtime), `ModelingEditorUI` (Runtime), `ModelingUI` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-07-30 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshModelingToolsetExp) | |

## 用途

MeshModelingToolsetExp 是 UE5 中基于 Interactive Tools Framework 的实验性 3D 网格建模工具集合。它从主插件 MeshModelingToolset 拆分而来，承载处于开发和验证阶段的高级网格编辑功能。

该插件解决的核心问题包括：
- **网格顶点属性绘制**：在网格表面绘制权重、颜色等逐顶点属性，支持骨骼网格和静态网格
- **纹理烘焙**：通过渲染捕获（Render Capture）将高模细节烘焙到低模 UV 纹理上
- **样条线绘制**：在场景中交互式绘制样条线，支持多种绘制模式和输出目标
- **实例化静态网格编辑**：对 ISM 组件的实例进行选择、变换、复制、替换等操作
- **网格布尔运算**：基于体素的 CSG 布尔运算和网格合并
- **BSP 转换**：将 BSP 画刷转换为静态网格
- **网格细分**：对网格执行 Catmull-Clark、Loop 等细分方案
- **其他工具**：切线编辑、材质编辑、网格转体积、实例收割等

这些工具处于实验阶段，API 和功能可能随时变更。稳定版本已迁移至 MeshModelingToolset（非实验性）插件。

## 使用场景

- 你需要在骨骼网格上绘制蒙皮权重 → 使用 `SkeletalMeshVertexAttributePaintTool`
- 你需要将高模的表面细节烘焙到低模的纹理贴图上 → 使用 `BakeRenderCaptureTool`
- 你需要在场景中交互式绘制样条线路径 → 使用 `DrawSplineTool`
- 你需要批量编辑大量重复的静态网格实例 → 使用 `ISMEditorTool`
- 你需要对两个网格执行布尔运算（并集、差集、交集）→ 使用 `VoxelCSGMeshesTool`
- 你需要将旧的 BSP 画刷关卡转换为静态网格 → 使用 `BspConversionTool`
- 你需要对网格执行 Catmull-Clark 或 Loop 细分 → 使用 `SubdividePolyTool`
- 你需要将多个网格合并为一个 → 使用 `MergeMeshesTool`
- 你需要在网格表面随机喷涂小形状 → 使用 `ShapeSprayTool`
- 你需要为一组 Actor 创建自定义枢轴点 → 使用 `AddPivotActorTool`

## 蓝图用法

本插件中的工具主要通过编辑器中的 Modeling Tools 面板激活，而非直接在蓝图中调用。以下为各工具暴露到 UI 的核心属性和操作。

### 核心工具节点

| 工具 | 说明 | 所在类 |
|---|---|---|
| `BakeRenderCaptureTool` | 渲染捕获纹理烘焙 | `UBakeRenderCaptureTool` |
| `DrawSplineTool` | 交互式样条线绘制 | `UDrawSplineTool` |
| `ISMEditorTool` | 实例化静态网格编辑 | `UISMEditorTool` |
| `MeshAttributePaintToolV2` | 静态网格顶点属性绘制 | `UMeshAttributePaintToolV2` |
| `SkeletalMeshVertexAttributePaintTool` | 骨骼网格顶点属性绘制 | `USkeletalMeshVertexAttributePaintTool` |
| `VoxelCSGMeshesTool` | 体素布尔运算 | `UVoxelCSGMeshesTool` |
| `MergeMeshesTool` | 体素网格合并 | `UMergeMeshesTool` |
| `BspConversionTool` | BSP 画刷转静态网格 | `UBspConversionTool` |
| `SubdividePolyTool` | 网格细分 | `USubdividePolyTool` |
| `MeshTangentsTool` | 切线可视化与编辑 | `UMeshTangentsTool` |
| `MeshToVolumeTool` | 网格转体积 | `UMeshToVolumeTool` |
| `EditMeshMaterialsTool` | 网格材质编辑 | `UEditMeshMaterialsTool` |
| `HarvestInstancesTool` | 实例收割 | `UHarvestInstancesTool` |
| `ShapeSprayTool` | 形状喷涂 | `UShapeSprayTool` |
| `AddPivotActorTool` | 添加枢轴 Actor | `UAddPivotActorTool` |

### 使用示例

**ISME编辑器工具（蓝图描述）**：

1. 在场景中选中一个或多个包含 `UInstancedStaticMeshComponent` 的 Actor
2. 通过 Modeling Tools 面板激活 ISM Editor 工具
3. 在属性面板中设置 TransformMode（Shared Gizmo / Multi-Gizmo）
4. 点击实例进行选择（支持 Shift+点击添加、Ctrl+点击减去）
5. 使用 Gizmo 进行变换，或通过 Action 按钮执行 Duplicate / Delete / Replace

**BakeRenderCaptureTool（蓝图描述）**：

1. 选中两个 Static Mesh Actor（源高模 + 目标低模）
2. 通过 Modeling Tools 面板激活 Bake Render Capture 工具
3. 在 RenderCaptureProperties 中勾选需要的贴图类型（BaseColor、Normal、MRS 等）
4. 设置输出分辨率和采样数
5. 点击 Accept 生成纹理资产

## C++ 用法

### 头文件引入

```cpp
// 顶点属性绘制
#include "MeshVertexAttributePaintToolBase.h"

// 渲染捕获烘焙
#include "BakeRenderCaptureTool.h"

// 样条线绘制
#include "DrawSplineTool.h"

// ISM 编辑器
#include "ISMEditorTool.h"

// 体素布尔运算
#include "VoxelCSGMeshesTool.h"

// 模块入口
#include "MeshModelingToolsEditorOnlyExp.h"
```

### 基本用法

以下示例展示了如何以编程方式使用顶点属性绘制工具的数据层。

```cpp
// 来源: Public/MeshVertexAttributePaintToolBase.h
// 使用 FMeshVertexAttributePaintToolData 进行顶点权重读写

FMeshVertexAttributePaintToolData PaintData;
PaintData.Setup(MyDynamicMesh, 0); // 0 = 初始属性索引

// 开始修改事务
PaintData.BeginChange();

// 读取当前权重值
float CurrentValue = PaintData.GetValue(VertexIndex);

// 设置新权重值
PaintData.SetValue(VertexIndex, 0.75f);

// 提交修改（生成 FMeshChange 用于撤销/重做）
TUniquePtr<FMeshChange> Change = PaintData.EndChange();

// 如果需要取消
PaintData.CancelChange();
```

### 进阶用法

以下示例展示了如何使用渲染捕获烘焙工具的属性系统来配置烘焙参数。

```cpp
// 来源: Public/BakeRenderCaptureTool.h
// 配置渲染捕获属性

URenderCaptureProperties* CaptureProps = NewObject<URenderCaptureProperties>();

// 设置烘焙分辨率
CaptureProps->Resolution = EBakeTextureResolution::Resolution2048;

// 选择要生成的贴图类型
CaptureProps->bBaseColorMap = true;
CaptureProps->bNormalMap = true;
CaptureProps->bPackedMRSMap = true;  // 打包的 Metallic/Roughness/Specular
CaptureProps->bEmissiveMap = false;
CaptureProps->bOpacityMap = false;
CaptureProps->bSubsurfaceColorMap = false;

// 采样设置
CaptureProps->bAntiAliasing = false;

// 配置输出
UBakeRenderCaptureToolProperties* OutputProps = NewObject<UBakeRenderCaptureToolProperties>();
OutputProps->SamplesPerPixel = EBakeTextureSamplesPerPixel::Sample4;
OutputProps->TextureSize = EBakeTextureResolution::Resolution2048;
OutputProps->ValidSampleDepthThreshold = 0.0f; // 跳过遮挡清理
```

## Demo 示例

以下是一个最小化的工具 Builder 实现示例，展示了如何创建自定义的网格编辑工具。

```cpp
// MyCustomMeshTool.h
#pragma once

#include "CoreMinimal.h"
#include "InteractiveToolBuilder.h"
#include "SingleSelectionTool.h"
#include "BaseTools/SingleSelectionMeshEditingTool.h"
#include "MyCustomMeshTool.generated.h"

UCLASS()
class UMyCustomMeshToolProperties : public UInteractiveToolPropertySet
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere, Category = Options)
    float Strength = 1.0f;

    UPROPERTY(EditAnywhere, Category = Options)
    bool bShowPreview = true;
};

UCLASS()
class UMyCustomMeshTool : public USingleSelectionMeshEditingTool
{
    GENERATED_BODY()
public:
    virtual void Setup() override;
    virtual void OnShutdown(EToolShutdownType ShutdownType) override;
    virtual void OnTick(float DeltaTime) override;

    virtual bool HasCancel() const override { return true; }
    virtual bool HasAccept() const override { return true; }
    virtual bool CanAccept() const override;

protected:
    UPROPERTY()
    TObjectPtr<UMyCustomMeshToolProperties> Settings;

    UPROPERTY()
    TObjectPtr<UPreviewMesh> PreviewMesh;
};
```

```cpp
// MyCustomMeshTool.cpp
#include "MyCustomMeshTool.h"

void UMyCustomMeshTool::Setup()
{
    USingleSelectionMeshEditingTool::Setup();
    
    Settings = NewObject<UMyCustomMeshToolProperties>(this);
    AddPropertySet(Settings);

    // 创建预览网格
    PreviewMesh = NewObject<UPreviewMesh>(this);
    PreviewMesh->CreateInWorld(GetTargetWorld(), FTransform::Identity);
    // ... 初始化网格数据
}

void UMyCustomMeshTool::OnShutdown(EToolShutdownType ShutdownType)
{
    if (PreviewMesh)
    {
        PreviewMesh->Disconnect();
    }
    USingleSelectionMeshEditingTool::OnShutdown(ShutdownType);
}

void UMyCustomMeshTool::OnTick(float DeltaTime)
{
    USingleSelectionMeshEditingTool::OnTick(DeltaTime);
    // ... 每帧更新逻辑
}

bool UMyCustomMeshTool::CanAccept() const
{
    return true;
}
```

## 模块依赖

以下为各子模块的独特依赖（省略常见的 Core/Engine/Slate 等）。

### MeshModelingToolsEditorOnlyExp

| 模块 | 用途 |
|---|---|
| `GeometryFramework` | DynamicMesh 相关框架 |
| `ModelingComponents` | 建模组件（PreviewMesh、TransformGizmo 等） |
| `ModelingOperators` | 网格操作算子 |
| `MeshConversion` | MeshDescription 与 DynamicMesh 互转 |
| `DynamicMesh` | 动态网格数据结构 |
| `GeometryProcessing` | 网格处理算法（细分、简化等） |
| `MeshModelingToolsExp` | 实验性建模工具基类 |
| `ModelingUI` | 建模工具 UI 框架 |

### MeshModelingToolsExp

| 模块 | 用途 |
|---|---|
| `GeometryFramework` | DynamicMesh 框架 |
| `ModelingComponents` | 建模组件 |
| `ModelingOperators` | 网格操作算子 |
| `DynamicMesh` | 动态网格 |
| `GeometryProcessing` | 网格处理算法 |
| `MeshConversion` | 网格格式转换 |

### GeometryProcessingAdapters

| 模块 | 用途 |
|---|---|
| `GeometryProcessing` | 封装几何处理接口适配 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-27 | `32bb5ca4` | [ModelingTools] MeshVertexAttributePaintTool + SkinWeightsPaintTool: added bSyncBrushRadiusAcrossMod | 顶点绘制工具新增跨模式同步笔刷半径功能 |
| 2026-05-26 | `cf0257a2` | MeshVertexAttributePaintTool: refactor FStrokeAccumulator to support accumulating relax brush + fix | 重构笔画累加器以支持松弛笔刷的累积模式 |
| 2026-05-22 | `4938c498` | [SkeletalMeshModelingTools] Set AutoCalculated tangents mode on preview/sculpt meshes that lack valid tangents | 骨骼网格建模工具在缺少有效切线时自动计算切线 |
| 2026-05-19 | `12cf9c64` | [SkeletalMeshModelingTools] Fixed polygroup edge visualizer not updated after mesh deformation | 修复骨骼网格变形后多边形组边缘可视化不更新的问题 |
| 2026-05-14 | `f6425490` | [ModelingTools] Add UMeshElementsVisualizer to skin-weights tool; default group-boundary settings ON | 为蒙皮权重工具添加网格元素可视化器并默认开启组边界显示 |

### 维护评价

- **活跃维护**：最近一个月内有多次功能性更新，集中在顶点绘制和骨骼网格工具
- **实验性插件**：`IsExperimentalVersion=true`，`Hidden=true`，默认未安装
- **从 MeshModelingToolset 拆分**：2021 年从主工具集拆分，专门承载实验性功能
- **成熟工具会迁移**：稳定的功能会迁移到非实验性的 MeshModelingToolset 插件
- **推荐使用**：适合希望使用最新建模功能的开发者，但需注意 API 可能变更。生产环境建议关注非实验性版本

⚠️ **注意**：该插件默认未安装且隐藏，需要在 Plugin 设置中手动启用。由于是实验性插件，部分工具的 API 和行为可能在后续版本中发生变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshModelingToolsetExp)
- 官方文档：无
- [非实验性版本 MeshModelingToolset](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MeshModelingToolset)