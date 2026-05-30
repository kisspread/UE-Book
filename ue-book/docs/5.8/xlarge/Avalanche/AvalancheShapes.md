# Avalanche

> Compositing, designer and broadcasting tool.
>
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 运动设计 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产， 测试资源） |
| 模块 | `Avalanche` (Runtime), `AvalancheAttribute` (Runtime), `AvalancheCamera` (Runtime), `AvalancheComponentVisualizers` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheEditorCore` (Runtime), `AvalancheEffectors` (Runtime), `AvalancheEffectorsEditor` (Runtime), `AvalancheFunctionalTest` (Runtime), `AvalancheInteractiveTools` (Runtime), `AvalancheInteractiveToolsRuntime` (Runtime), `AvalancheLevelViewport` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheMRQEditor` (Runtime), `AvalancheMask` (Runtime), `AvalancheMaskEditor` (Runtime), `AvalancheMaterial` (Runtime), `AvalancheMedia` (Runtime), `AvalancheMediaEditor` (Runtime), `AvalancheModifiers` (Runtime), `AvalancheModifiersEditor` (Runtime), `AvalancheOutliner` (Runtime), `AvalanchePropertyAnimator` (Runtime), `AvalanchePropertyAnimatorEditor` (Runtime), `AvalancheRemoteControl` (Runtime), `AvalancheRemoteControlEditor` (Runtime), `AvalancheSVGEditor` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheSceneRigEditor` (Runtime), `AvalancheSceneTree` (Runtime), `AvalancheSequence` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheShapes` (Runtime), `AvalancheShapesEditor` (Runtime), `AvalancheTag` (Runtime), `AvalancheTagEditor` (Runtime), `AvalancheText` (Runtime), `AvalancheTextEditor` (Runtime), `AvalancheTransition` (Runtime), `AvalancheTransitionEditor` (Runtime), `AvalancheViewport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Avalanche（内部代号，对外称为 Motion Design）是一个面向虚拟制作（Virtual Production）的综合性工具集。它旨在提供一套完整的工具，用于在 UE5 中创建、合成、动画化和广播实时图形元素。这个插件的核心目标是解决虚拟演播室、直播和赛事制播中对高效、动态图形设计和播放流程的需求。

其实际功能远超一个简单的图形工具，它更像是一个集成在 Unreal Engine 中的“虚拟制播引擎”，集成了形状创建、材质编辑、属性动画、远程控制、场景管理和播放队列等能力。

## 使用场景

-   你需要为虚拟演播室的主持人创建动态的背景板、名字条和信息图表 → 使用 `AvalancheShapes` 和 `AvalancheText` 模块创建和操控2D/3D图形。
-   你需要制作复杂的、可被实时远程控制的舞台视觉特效 → 使用 `AvalancheRemoteControl` 和 `AvalancheSequencer` 模块。
-   你需要管理一个虚拟场景中大量的图形元素（如上百个广告牌）的排列、动画和生命周期 → 使用 `AvalancheOutliner`、`AvalanchePropertyAnimator` 和 `AvalancheTransition` 模块。
-   你需要使用 Media Render Queue (MRQ) 来离线渲染你的实时图形设计 → 使用 `AvalancheMRQ` 模块。

## 蓝图用法

由于插件规模巨大（40+个模块），本章节将聚焦于 **AvalancheShapes** 模块的核心蓝图节点。

### 核心节点

以下节点主要存在于形状基类 `UAvaShapeDynamicMeshBase` 及其子类中。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetSize2D` / `GetSize2D` | 设置或获取2D形状的尺寸（如矩形、椭圆） | `UAvaShapeDynamicMeshBase` |
| `SetSize3D` / `GetSize3D` | 设置或获取3D形状的尺寸（如立方体、球体） | `UAvaShapeDynamicMeshBase` |
| `SetMaterial` | 为形状的指定网格索引设置材质资产 | `UAvaShapeDynamicMeshBase` |
| `SetParametricMaterial` | 为形状设置参数化材质（支持纯色、渐变、纹理） | `UAvaShapeDynamicMeshBase` |
| `SetMaterialUVParams` | 设置形状网格的UV参数（缩放、偏移、旋转等） | `UAvaShapeDynamicMeshBase` |
| `GetMeshSectionNames` | 获取构成形状的所有网格分段的名称列表 | `UAvaShapeDynamicMeshBase` |
| `SetRectangle` (静态) | **工厂函数**：将一个 `AvaShapeActor` 的形状设置为矩形并指定尺寸和变换 | `UAvaShapeMeshFunctions` |
| `RefreshParametricMaterial` | 手动触发刷新形状的参数化材质 | `AAvaShapeActor` |

### 使用示例（蓝图描述）

1.  **创建一个矩形并设置材质**：
    1.  在蓝图中使用 `Spawn Actor` 节点生成一个 `AvaShapeActor`。
    2.  将其连接到 `SetRectangle` 静态节点的 `ShapeActor` 输入，设置 `Size` 和 `Transform`。
    3.  从 `SetRectangle` 的输出 `Mesh` 引脚，调用 `SetParametricMaterial` 节点，配置 `Style` 为 `LinearGradient`，并设置 `ColorA` 和 `ColorB`。

2.  **动态修改形状的UV**：
    1.  获取到代表形状网格的 `UAvaShapeDynamicMeshBase` 对象。
    2.  调用 `SetMaterialUVParams` 节点，传入 `MeshIndex`（通常主网格为0）和一个 `FAvaShapeMaterialUVParameters` 结构体。
    3.  在该结构体中，可设置 `Scale`（缩放）、`Offset`（偏移）、`Rotation`（旋转）等参数来调整材质在形状上的表现。

## C++ 用法

### 头文件引入

```cpp
#include "AvalancheShapes/Public/AvaShapeActor.h"
#include "AvalancheShapes/Public/DynamicMeshes/AvaShapeRectangleDynMesh.h"
```

### 基本用法

以下示例展示了如何在 C++ 中创建一个矩形形状。

```cpp
// 假设在某个AActor的BeginPlay中
void AMyActor::BeginPlay()
{
    Super::BeginPlay();
    
    // 1. 生成一个AvaShapeActor
    FActorSpawnParameters SpawnParams;
    SpawnParams.Owner = this;
    AAvaShapeActor* ShapeActor = GetWorld()->SpawnActor<AAvaShapeActor>(SpawnParams);
    
    // 2. 使用工厂函数设置为矩形
    FVector2D RectangleSize(200.0f, 100.0f);
    FTransform ShapeTransform = FTransform(FRotator::ZeroRotator, FVector(0, 0, 100), FVector::OneVector);
    UAvaShapeRectangleDynamicMesh* RectMesh = UAvaShapeMeshFunctions::SetRectangle(ShapeActor, RectangleSize, ShapeTransform);
    
    // 3. (可选) 修改材质
    if (RectMesh)
    {
        RectMesh->SetPrimaryColor(FLinearColor::Red);
    }
}
```

*来源: `AvalancheShapes/Public/AvaShapePrimitiveFunctions.h`*

### 进阶用法

你可以继承 `UAvaShape2DDynMeshBase` 或 `UAvaShape3DDynMeshBase` 来创建自定义形状。核心是重写 `CreateMesh` 和 `CreateUVs` 函数来定义几何体和UV坐标。

```cpp
// MyCustomShape.h
#pragma once
#include "DynamicMeshes/AvaShape2DDynMeshBase.h"
#include "MyCustomShape.generated.h"

UCLASS(MinimalAPI, ClassGroup="Shape", BlueprintType, CustomConstructor, Within=AvaShapeActor)
class UMyCustomShapeDynamicMesh : public UAvaShape2DDynMeshBase
{
    GENERATED_BODY()
public:
    UMyCustomShapeDynamicMesh() : UAvaShape2DDynMeshBase(FVector2D(50.f, 50.f)) {}
    
    virtual const FString& GetMeshName() const override { return TEXT("MyCustomShape"); }
    
protected:
    // 重写此函数来构建三角形网格
    virtual bool CreateMesh(FAvaShapeMesh& InMesh) override;
};

// MyCustomShape.cpp
bool UMyCustomShapeDynamicMesh::CreateMesh(FAvaShapeMesh& InMesh)
{
    // 使用 CacheVertex 和 AddTriangle 函数构建顶点和三角形
    FAvaShapeCachedVertex2D V0 = CacheVertexCreate(InMesh, FVector2D(-100.f, -100.f));
    FAvaShapeCachedVertex2D V1 = CacheVertexCreate(InMesh, FVector2D(100.f, -100.f));
    FAvaShapeCachedVertex2D V2 = CacheVertexCreate(InMesh, FVector2D(100.f, 100.f));
    FAvaShapeCachedVertex2D V3 = CacheVertexCreate(InMesh, FVector2D(-100.f, 100.f));
    
    AddTriangle(InMesh, V0, V1, V2);
    AddTriangle(InMesh, V0, V2, V3);
    
    return true; // 返回true表示网格已成功创建
}
```

*来源: `AvalancheShapes/Public/DynamicMeshes/AvaShape2DDynMeshBase.h`*

## Demo 示例

下面是一个完整的自定义形状模块示例。

```cpp
// MyTriangleShape.h
#pragma once

#include "DynamicMeshes/AvaShape2DDynMeshBase.h"
#include "MyTriangleShape.generated.h"

UCLASS(MinimalAPI, ClassGroup="Shape", BlueprintType, CustomConstructor, Within=AvaShapeActor)
class UMyTriangleShapeDynamicMesh : public UAvaShape2DDynMeshBase
{
    GENERATED_BODY()

public:
    UMyTriangleShapeDynamicMesh()
        : UAvaShape2DDynMeshBase(FVector2D(50.f, 50.f))
    {}

    virtual const FString& GetMeshName() const override
    {
        return TEXT("MyTriangle");
    }

protected:
    // 重写网格创建函数，定义一个简单的三角形
    virtual bool CreateMesh(FAvaShapeMesh& InMesh) override
    {
        // 创建三个顶点
        FAvaShapeCachedVertex2D BottomLeft = CacheVertexCreate(InMesh, FVector2D(-50.f, -50.f));
        FAvaShapeCachedVertex2D BottomRight = CacheVertexCreate(InMesh, FVector2D(50.f, -50.f));
        FAvaShapeCachedVertex2D TopCenter = CacheVertexCreate(InMesh, FVector2D(0.f, 50.f));
        
        // 添加一个三角形
        AddTriangle(InMesh, BottomLeft, BottomRight, TopCenter);
        
        return true;
    }
};
```

```cpp
// MyTriangleShape.cpp
#include "MyTriangleShape.h"
// UMyTriangleShapeDynamicMesh 的实现已内联在头文件中。
```

## 模块依赖

AvalancheShapes 模块依赖了几个独特的核心模块，用于实现其功能。

| 模块 | 用途 |
|---|---|
| `DynamicMesh` | 提供 `UDynamicMeshComponent` 和几何数据操作能力，是所有形状的网格载体。 |
| `GeometryScriptingCore` | 用于几何体的脚本化操作，可能被用于更复杂的网格处理。 |
| `AvalancheCore` | Avalanche插件的核心基础模块，提供共享的类型定义和工具函数。 |
| `MaterialDesigner` | 用于与材质设计器（Material Designer）集成，支持更复杂的材质创建。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将运动设计相关面板从关卡编辑器分离到独立窗口组 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 为使用播放列表页面设置的MRQ添加分析功能 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 在节目控制工具栏中添加页面加载选项（全部、下一个、选中） |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 新增项目设置，可强制禁用Text3D和形状的碰撞 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口：通过通知客户端其关联或解除关联来重构必需的样板代码 |

### 维护评价

**活跃维护中**。从最近的提交历史看，Avalanche（Motion Design）插件正处于密集的开发和迭代期。最近的改动集中在用户体验优化（UI面板重组）、功能扩展（新的播放选项、分析功能）以及性能与稳定性提升（碰撞管理、代码重构）。考虑到这是 Epic Games 官方维护的核心虚拟制作工具，且创建时间不到一年，可以预期它将随着 UE5 的版本更新而持续获得新功能和 bug 修复。目前没有发现明显的已知问题或废弃标记，推荐在虚拟制作和动态图形相关项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [官方文档]() （暂无公开文档链接）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheFunctionalTest)