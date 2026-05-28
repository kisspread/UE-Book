# Mesh Painting

> System for painting data onto meshes.

| 属性 | 值 |
|---|---|
| 中文名 | 网格绘制 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `MeshPaintEditorMode` (Editor), `MeshPaintingToolset` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2019-12-19 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MeshPainting) | |

## 用途

MeshPainting 插件为 UE5 编辑器提供了一套完整的网格数据绘制系统。它的核心功能是允许开发者或美术在编辑器内，通过笔刷工具直接将颜色（顶点颜色或纹理颜色）或混合权重数据“绘制”到静态网格、骨骼网格、样条网格和几何体集合（Geometry Collection）等网格资产上。

该插件解决了以下问题：
1.  **视觉效果调整**：用于调整材质实例之间的混合权重（如地形材质层、多纹理混合），实现精细的表面过渡效果。
2.  **调试与标记**：利用顶点颜色或特定纹理通道，在网格上可视化地标记区域、覆盖范围或其他调试信息，便于开发和分析。
3.  **Nanite 兼容绘制**：对于 Nanite 高密度网格，传统顶点颜色绘制效率低下。此插件支持直接绘制纹理颜色（Texture Color Painting），将数据存储在组件专属的纹理上，为这类网格提供了高效的绘制方案。

## 使用场景

-   **美术制作**：美术人员需要为游戏场景中的岩石、地形或建筑表面绘制复杂的材质混合效果（例如，控制石头、草地、泥土材质的覆盖区域）。
-   **技术美术/开发调试**：开发者需要在角色或道具网格上可视化一些非渲染数据，如布料模拟影响区域、物理碰撞权重或音频区域。
-   **处理 Nanite 网格**：当项目使用 Nanite 技术，并且需要对网格进行逐像素（而非逐顶点）的材质层控制时，应使用此插件的纹理绘制功能。

## 蓝图用法

该插件主要在编辑器工具模式下使用，提供的蓝图可调用 API 主要集中在管理绘制状态和数据的子系统上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `HasPaintableMesh` | 检查给定组件是否支持网格绘制 | `UMeshPaintingSubsystem` |
| `CreateComponentMeshPaintTexture` | 为网格组件创建并关联用于纹理绘制的画布纹理 | `UMeshPaintingSubsystem` |
| `RemoveComponentInstanceVertexColors` | 移除指定静态网格组件上的所有实例顶点颜色 | `UMeshPaintingSubsystem` |
| `PropagateColorsToRawMesh` | 将组件上存储的逐实例顶点颜色应用到底层网格资产的原始数据中 | `UMeshPaintingSubsystem` |
| `ApplyVertexColorsToAllLODs` | 将 LOD 0 上绘制的顶点颜色同步到所有更低的 LOD 层级 | `UMeshPaintingSubsystem` |
| `GetVerticesForLOD` | 获取指定 LOD 层级网格的所有顶点位置 | `UMeshPaintingSubsystem` |
| `GetColorDataForLOD` | 获取指定 LOD 层级网格的顶点颜色数据 | `UMeshPaintingSubsystem` |
| `ForceRenderMeshLOD` | 强制网格组件在视口渲染时显示指定的 LOD 层级，便于绘制 | `UMeshPaintingSubsystem` |
| `GetAdapterForComponent` | 获取与指定网格组件关联的绘制适配器，可用于查询绘制能力 | `UMeshPaintingSubsystem` |

### 使用示例（蓝图描述）

1.  **准备绘制**：在进入网格绘制模式后，插件会自动为选中的组件创建或获取适配器。你可以通过 `GetAdapterForComponent` 节点查询该组件支持哪种绘制（`SupportsVertexPaint`, `SupportsTexturePaint`）。
2.  **清理数据**：如果需要重置一个组件的绘制数据，可以按顺序调用：
    -   `RemoveComponentInstanceVertexColors` (清除顶点颜色)
    -   `RemoveComponentMeshPaintTexture` (清除纹理颜色)
3.  **应用绘制**：当在一个 LOD（通常是 LOD 0）上完成绘制后，调用 `ApplyVertexColorsToAllLODs` 可以确保所有 LOD 的顶点颜色保持一致。对于纹理颜色，数据通常保存在组件上，无需额外同步。

## C++ 用法

插件的核心逻辑位于 `MeshPaintingToolset` 模块，通过 `UMeshPaintingSubsystem` 引擎子系统和一系列适配器类提供服务。

### 头文件引入

```cpp
#include "MeshPaintHelpers.h" // 包含 UMeshPaintingSubsystem 和主要工具函数
#include "IMeshPaintComponentAdapter.h" // 适配器接口
#include "MeshPaintStaticMeshAdapter.h" // 静态网格适配器示例
```

### 基本用法

获取子系统并查询网格的绘制能力（基于 `Engine/Plugins/MeshPainting/Source/MeshPaintingToolset/Tests/MeshPaintTests.cpp` 推断）。

```cpp
// 获取 MeshPainting 子系统
UMeshPaintingSubsystem* PaintSubsystem = GEngine->GetEngineSubsystem<UMeshPaintingSubsystem>();
if (!PaintSubsystem) return;

// 假设 MyMeshComponent 是一个 UStaticMeshComponent*
UStaticMeshComponent* MyMeshComponent = ...;

// 1. 检查是否可绘制
bool bCanPaint = PaintSubsystem->HasPaintableMesh(MyMeshComponent);

// 2. 获取适配器以查询详细信息
TSharedPtr<IMeshPaintComponentAdapter> Adapter = PaintSubsystem->GetAdapterForComponent(MyMeshComponent);
if (Adapter.IsValid())
{
    bool bSupportsVertexPaint = Adapter->SupportsVertexPaint();
    bool bSupportsTexturePaint = Adapter->SupportsTexturePaint();
    // 根据支持情况决定后续操作
}

// 3. 填充顶点颜色（例如，将整个 LOD 0 设为红色）
PaintSubsystem->FillStaticMeshVertexColors(MyMeshComponent, /*LODIndex=*/ 0, FColor::Red, FColor::Black);
```

### 进阶用法

创建一个简单的绘制操作，使用笔刷参数影响单个顶点（基于 `MeshPaintHelpers.h` 中的 `ApplyBrushToVertex` 模板逻辑推断）。

```cpp
// 定义绘制参数（通常由 UI 工具设置）
FMeshPaintParameters PaintParams;
PaintParams.PaintAction = EMeshPaintModeAction::Paint;
PaintParams.BrushColor = FLinearColor::Green;
PaintParams.SquaredBrushRadius = 10000.0f; // 笔刷半径平方
PaintParams.BrushStrength = 0.5f;
// ... 设置其他参数，如 BrushPosition, BrushNormal, 矩阵等

// 假设我们要修改顶点索引 VertexIndex 的颜色
int32 VertexIndex = 42;
FColor CurrentColor = FColor::Black; // 从适配器获取
FVector VertexPosition = ...; // 从适配器获取

// 检查顶点是否在笔刷影响范围内
float SquaredDistance;
float VertexDepth;
if (PaintSubsystem->IsPointInfluencedByBrush(VertexPosition, PaintParams, SquaredDistance, VertexDepth))
{
    // 应用绘制
    bool bPainted = PaintSubsystem->PaintVertex(VertexPosition, PaintParams, CurrentColor);
    if (bPainted)
    {
        // 将新颜色写回适配器/组件
        Adapter->SetVertexColor(VertexIndex, CurrentColor, /*bInstance=*/true);
    }
}
```

## Demo 示例

下面展示如何创建一个自定义的网格绘制适配器工厂，用于支持一种假设的 `UMyCustomMeshComponent`。

### MyCustomMeshPaintAdapter.h
```cpp
#pragma once

#include "BaseMeshPaintComponentAdapter.h"
#include "MeshPaintAdapterFactory.h"

class UMyCustomMeshComponent;

class FMyCustomMeshPaintAdapter : public FBaseMeshPaintComponentAdapter
{
public:
    FMyCustomMeshPaintAdapter(UMyCustomMeshComponent* InComponent);

    // IMeshPaintComponentAdapter 接口实现
    virtual bool Construct(UMeshComponent* InComponent, int32 InMeshLODIndex) override;
    virtual bool SupportsTexturePaint() const override { return true; }
    virtual bool SupportsTextureColorPaint() const override { return false; }
    virtual bool SupportsVertexPaint() const override { return true; }
    // ... 实现其他纯虚函数，如 GetNumUVChannels, LineTraceComponent, GetVertexColor 等

protected:
    virtual bool InitializeVertexData() override; // 在 FBaseMeshPaintComponentAdapter 中初始化 MeshVertices 和 MeshIndices

private:
    TWeakObjectPtr<UMyCustomMeshComponent> CustomMeshComponent;
};

class FMyCustomMeshPaintAdapterFactory : public IMeshPaintComponentAdapterFactory
{
public:
    virtual TSharedPtr<IMeshPaintComponentAdapter> Construct(UMeshComponent* InComponent, int32 InMeshLODIndex) const override;
    virtual void InitializeAdapterGlobals() override {} // 通常为空
    virtual void AddReferencedObjectsGlobals(FReferenceCollector& Collector) override {}
    virtual void CleanupGlobals() override {} // 通常为空
};
```

### MyCustomMeshPaintAdapter.cpp
```cpp
#include "MyCustomMeshPaintAdapter.h"
#include "MyCustomMeshComponent.h" // 你的自定义组件头文件

FMyCustomMeshPaintAdapter::FMyCustomMeshPaintAdapter(UMyCustomMeshComponent* InComponent)
    : CustomMeshComponent(InComponent)
{
}

bool FMyCustomMeshPaintAdapter::Construct(UMeshComponent* InComponent, int32 InMeshLODIndex)
{
    CustomMeshComponent = Cast<UMyCustomMeshComponent>(InComponent);
    MeshLODIndex = InMeshLODIndex;
    return CustomMeshComponent.IsValid();
}

bool FMyCustomMeshPaintAdapter::InitializeVertexData()
{
    if (!CustomMeshComponent.IsValid()) return false;

    // 从你的自定义网格组件获取顶点和索引数据
    // MeshVertices = CustomMeshComponent->GetVertices(MeshLODIndex);
    // MeshIndices = CustomMeshComponent->GetIndices(MeshLODIndex);
    
    // 构建八叉树以加速空间查询
    return BuildOctree();
}

TSharedPtr<IMeshPaintComponentAdapter> FMyCustomMeshPaintAdapterFactory::Construct(UMeshComponent* InComponent, int32 InMeshLODIndex) const
{
    return MakeShareable(new FMyCustomMeshPaintAdapter(Cast<UMyCustomMeshComponent>(InComponent)));
}

// 在模块启动时注册工厂
void RegisterCustomMeshPaintAdapter()
{
    FMeshPaintComponentAdapterFactory::FactoryList.Add(MakeShareable(new FMyCustomMeshPaintAdapterFactory()));
}
```

## 模块依赖

要使用此插件的功能，你的模块通常需要在 `.Build.cs` 文件中添加对 `MeshPaintingToolset` 模块的依赖。

| 模块 | 用途 |
|---|---|
| `MeshPaintingToolset` | 提供核心的绘制子系统 (`UMeshPaintingSubsystem`)、适配器接口和工具函数。 |
| `GeometryProcessing` | （插件依赖）提供几何处理功能，可能被用于网格分析或空间查询。 |

## 维护状态

该插件自 2019 年创建，是引擎的核心编辑器工具之一。根据近期提交记录，它仍在接受维护和改进，包括渲染优化和日志系统迁移。

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏，提升日志系统一致性。 |
| 2026-03-06 | `02b005a0` | make the mesh paint mode render geometry collections w/ the native render, so it does not show any p | 优化几何体集合在绘制模式下的渲染，避免视觉瑕疵。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复上一次提交中错误的查找替换操作。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退导致问题的代码变更。 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 修复引擎初始化委托的注册问题，确保绘制系统正确初始化。 |

### 维护评价

-   **维护状态**：**活跃维护中**。最近一年内有多次功能性更新和问题修复。
-   **推荐使用**：是。作为引擎内置的网格数据绘制方案，它成熟、稳定，且与编辑器深度集成。对于需要顶点颜色或纹理颜色绘制的项目（特别是涉及 Nanite），是标准选择。
-   **注意**：此插件为编辑器专用 (`Editor` 类型)，不可用于运行时。其绘制的数据（顶点颜色、纹理）会存储在资产或组件中，打包后生效。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MeshPainting)
-   [官方文档](https://docs.unrealengine.com) (无特定文档链接，请在官方文档中搜索 “Mesh Painting” 或 “Vertex Painting”)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/MeshPainting/Source/MeshPaintingToolset/Tests/MeshPaintTests.cpp)