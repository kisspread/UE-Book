# Mesh Painting

> System for painting data onto meshes.

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `MeshPaintEditorMode` (Editor), `MeshPaintingToolset` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2019-11-18 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MeshPainting) | |

## 用途

MeshPainting 是 UE5 的编辑器内网格绘制系统，允许美术和开发者直接在 3D 网格表面上绘制数据。它支持两大类绘制模式：

1. **顶点绘制（Vertex Painting）**：将颜色或混合权重写入网格的顶点数据。适用于控制风化程度、材质混合、植被着色等效果。
2. **纹理绘制（Texture Painting）**：直接在纹理资产或组件专属纹理上绘制颜色。对于 Nanite 等超高密度网格，纹理绘制比顶点绘制更合适，因为顶点数量过于庞大。

该插件通过 Editor Mode（编辑器模式）框架集成到编辑器中，提供完整的笔刷工具、LOD 管理、撤销/重做、复制/粘贴等工作流。

## 使用场景

- 你需要为静态网格的顶点着色，控制材质实例中的风化/污渍效果 → 使用 **Vertex Color Painting**
- 你需要在骨骼网格上绘制顶点颜色来驱动布料模拟权重 → 使用 **Vertex Weight Painting**
- 你有一个 Nanite 超高面数网格，顶点绘制不现实 → 使用 **Texture Color Painting**（组件专属纹理）
- 你需要直接在网格上绘制纹理资产（如贴花蒙版） → 使用 **Texture Asset Painting**
- 你需要从纹理图片导入顶点颜色（如从烘焙好的 AO 图导入） → 使用 Import Vertex Colors 功能

## 架构概览

插件由两个模块组成：

### MeshPaintEditorMode（编辑器模式）

负责 UI 集成，包括：
- `UMeshPaintMode`：核心编辑器模式，管理工具切换、命令绑定、选区更新
- `UMeshPaintModeSettings`：用户配置（颜色可视化模式、默认面板等）
- `FMeshPaintEditorModeCommands`：所有 UI 快捷键命令的注册
- `UMeshPaintModeSubsystem`：编辑器子系统，提供视口颜色模式切换、顶点颜色导入等辅助功能

### MeshPaintingToolset（工具集）

负责实际绘制逻辑，包括：
- 绘制工具（`UMeshVertexPaintingTool`、`UMeshTexturePaintingTool` 及其子类）
- 网格适配器（Adapter）架构，为不同网格类型提供统一的绘制接口
- 八叉树空间索引（`TMeshPaintOctree`），加速笔刷与三角形/顶点的相交检测
- 纹理绘制渲染工具（`UTexturePaintToolset`）

### 适配器架构

插件使用 **Adapter 模式** 为不同网格类型提供统一的绘制接口：

| 适配器类 | 支持的组件类型 | 顶点绘制 | 纹理绘制 | 纹理颜色绘制 |
|---|---|---|---|---|
| `FMeshPaintStaticMeshComponentAdapter` | `UStaticMeshComponent` | ✅ | ✅ | ✅ |
| `FMeshPaintSplineMeshComponentAdapter` | `USplineMeshComponent` | ✅ | ✅ | ✅ |
| `FMeshPaintSkeletalMeshComponentAdapter` | `USkeletalMeshComponent` | ✅ | ✅ | ❌ |
| `FMeshPaintGeometryCollectionComponentAdapter` | `UGeometryCollectionComponent` | ✅ | ✅ | ❌ |

通过 `IMeshPaintComponentAdapterFactory` 工厂模式注册，`FMeshPaintComponentAdapterFactory::CreateAdapterForMesh()` 根据组件类型自动选择合适的适配器。

## 编辑器模式使用方式

1. 在编辑器工具栏中选择 **Mesh Paint** 编辑器模式
2. 选择要绘制的 Actor/组件
3. 选择绘制子模式（通过面板标签页切换）：
   - **Vertex Color**：顶点颜色绘制
   - **Vertex Weights**：顶点混合权重绘制
   - **Texture Color**：组件纹理颜色绘制
   - **Texture Asset**：纹理资产绘制
4. 使用鼠标左键拖拽绘制，右键擦除

### 支持的快捷键命令

| 命令 | 功能 |
|---|---|
| SwapColor | 交换绘制/擦除颜色 |
| FillVertex / FillTexture | 填充整个网格 |
| PropagateMesh | 将顶点颜色传播到原始网格资产 |
| PropagateLODs | 将 LOD 0 的顶点颜色传播到所有 LOD |
| SaveVertex / SaveTexture | 保存顶点颜色到资产 / 保存纹理包 |
| Add | 添加 MeshPaint 纹理 |
| RemoveVertex / RemoveTexture | 移除实例顶点颜色 / 移除 MeshPaint 纹理 |
| Copy / Paste | 复制/粘贴顶点颜色或纹理 |
| Import | 从文件导入顶点颜色 |
| GetTextureColors / GetVertexColors | 从纹理导入顶点颜色 / 从 MeshPaint 纹理导入顶点颜色 |
| FixVertex / FixTexture | 修复顶点颜色 / 修复纹理颜色 |
| PreviousLOD / NextLOD | 切换 LOD 级别 |
| PreviousTexture / NextTexture | 切换绘制纹理 |
| IncreaseBrushRadius / DecreaseBrushRadius | 调整笔刷半径 |
| IncreaseBrushStrength / DecreaseBrushStrength | 调整笔刷强度 |
| IncreaseBrushFalloff / DecreaseBrushFalloff | 调整笔刷衰减 |

## 蓝图用法

该插件 **不暴露任何 BlueprintCallable 函数**。它是一个纯编辑器工具，所有交互通过编辑器 Mode 面板和快捷键完成，不提供运行时蓝图接口。

## C++ 用法

### 核心子系统 `UMeshPaintingSubsystem`

这是最重要的 C++ 入口点，作为 `UEngineSubsystem` 存在，可以在任何编辑器代码中访问：

```cpp
#include "MeshPaintHelpers.h"

UMeshPaintingSubsystem* Subsystem = GEngine->GetEngineSubsystem<UMeshPaintingSubsystem>();
```

### 头文件引入

```cpp
// 绘制子系统和辅助函数
#include "MeshPaintHelpers.h"

// 适配器接口
#include "IMeshPaintComponentAdapter.h"

// 适配器工厂
#include "MeshPaintAdapterFactory.h"

// 纹理绘制工具集
#include "TexturePaintToolset.h"

// 类型定义
#include "MeshPaintingToolsetTypes.h"

// 交互机制
#include "MeshPaintInteractions.h"
```

### 检查组件是否可绘制

```cpp
UMeshPaintingSubsystem* Subsystem = GEngine->GetEngineSubsystem<UMeshPaintingSubsystem>();

if (Subsystem->HasPaintableMesh(MyComponent))
{
    // 该组件支持某种形式的网格绘制
}
```

### 获取和设置顶点颜色数据

```cpp
UMeshPaintingSubsystem* Subsystem = GEngine->GetEngineSubsystem<UMeshPaintingSubsystem>();

// 获取指定 LOD 的顶点颜色
TArray<FColor> Colors = Subsystem->GetColorDataForLOD(StaticMesh, 0);

// 获取实例顶点颜色（组件级别，不影响原始资产）
TArray<FColor> InstanceColors = Subsystem->GetInstanceColorDataForLOD(StaticMeshComponent, 0);

// 设置实例顶点颜色
TArray<FColor> NewColors;
// ... 填充颜色数据
Subsystem->SetInstanceColorDataForLOD(StaticMeshComponent, 0, NewColors);

// 用单一颜色填充
Subsystem->FillStaticMeshVertexColors(StaticMeshComponent, 0, FColor::White, FColor::White);
```

### 将顶点颜色传播到所有 LOD

```cpp
// 创建适配器
TSharedPtr<IMeshPaintComponentAdapter> Adapter = Subsystem->GetAdapterForComponent(MeshComponent);

// 将 LOD 0 的顶点颜色传播到所有 LOD
Subsystem->ApplyVertexColorsToAllLODs(*Adapter, MeshComponent);
```

### 创建和管理 MeshPaint 纹理

```cpp
UMeshPaintingSubsystem* Subsystem = GEngine->GetEngineSubsystem<UMeshPaintingSubsystem>();

// 为组件创建 MeshPaint 纹理
Subsystem->CreateComponentMeshPaintTexture(StaticMeshComponent);

// 创建独立的 MeshPaint 纹理（不绑定到组件）
UTexture* Texture = Subsystem->CreateMeshPaintTexture(Outer, 512);

// 移除组件的 MeshPaint 纹理
Subsystem->RemoveComponentMeshPaintTexture(StaticMeshComponent);
```

### 使用适配器接口

```cpp
#include "IMeshPaintComponentAdapter.h"
#include "MeshPaintAdapterFactory.h"

// 为组件创建适配器
TSharedPtr<IMeshPaintComponentAdapter> Adapter = 
    FMeshPaintComponentAdapterFactory::CreateAdapterForMesh(MyMeshComponent, 0);

if (Adapter.IsValid() && Adapter->Initialize())
{
    // 查询支持的功能
    bool bSupportsVertexPaint = Adapter->SupportsVertexPaint();
    bool bSupportsTexturePaint = Adapter->SupportsTexturePaint();
    
    // 获取顶点数据
    const TArray<FVector>& Vertices = Adapter->GetMeshVertices();
    const TArray<uint32>& Indices = Adapter->GetMeshIndices();
    
    // 读写顶点颜色
    FColor Color;
    Adapter->GetVertexColor(0, Color, true); // true = instance colors
    Adapter->SetVertexColor(0, FColor::Red, true);
    
    // 球形相交检测（用于笔刷）
    TArray<uint32> HitTriangles = Adapter->SphereIntersectTriangles(
        BrushRadiusSquared, BrushPosition, CameraPosition, bOnlyFrontFacing);
}
```

### 使用纹理绘制工具集

```cpp
#include "TexturePaintToolset.h"

// 获取可绘制纹理列表
TArray<FPaintableTexture> PaintableTextures;
int32 DefaultIndex;
UTexturePaintToolset::RetrieveTexturesForComponent(
    MeshComponent, Adapter.Get(), DefaultIndex, PaintableTextures);

// 获取纹理支持的最大像素格式
int32 MaxBytesPerPixel = UTexturePaintToolset::GetMaxSupportedBytesPerPixelForPainting();

// 复制纹理到渲染目标
UTexturePaintToolset::CopyTextureToRenderTargetTexture(
    SourceTexture, RenderTargetTexture, FeatureLevel);
```

## 进阶用法

### 自定义网格类型适配器

你可以为自定义 `UMeshComponent` 子类创建适配器，扩展绘制支持：

```cpp
// 1. 实现适配器
class FMyCustomMeshComponentAdapter : public FBaseMeshPaintComponentAdapter
{
public:
    virtual bool Construct(UMeshComponent* InComponent, int32 InMeshLODIndex) override;
    virtual bool InitializeVertexData() override;
    virtual bool SupportsVertexPaint() const override { return true; }
    virtual bool SupportsTexturePaint() const override { return true; }
    virtual bool SupportsTextureColorPaint() const override { return false; }
    virtual int32 GetNumUVChannels() const override;
    virtual void QueryPaintableTextures(int32 MaterialIndex, int32& OutDefaultIndex, 
        TArray<FPaintableTexture>& InOutTextureList) override;
    // ... 其他接口实现
};

// 2. 实现工厂
class FMyCustomMeshComponentAdapterFactory : public IMeshPaintComponentAdapterFactory
{
public:
    virtual TSharedPtr<IMeshPaintComponentAdapter> Construct(
        UMeshComponent* InComponent, int32 InMeshLODIndex) const override
    {
        auto Adapter = MakeShared<FMyCustomMeshComponentAdapter>();
        if (Adapter->Construct(InComponent, InMeshLODIndex))
        {
            return Adapter;
        }
        return nullptr;
    }
    // ... 其他工厂方法
};

// 3. 在模块启动时注册
FMeshPaintComponentAdapterFactory::FactoryList.Add(
    MakeShared<FMyCustomMeshComponentAdapterFactory>());
```

### 纹理权重绘制模式

顶点权重绘制支持多种纹理混合模式（`EMeshPaintWeightTypes`）：

| 模式 | 权重数 | 说明 |
|---|---|---|
| AlphaLerp | 2 | 使用 Alpha 在两个纹理间线性插值 |
| RGB | 3 | 使用 RGB 三个通道分别控制三个纹理 |
| ARGB | 4 | 使用 ARGB 四个通道分别控制四个纹理 |
| OneMinusARGB | 5 | ARGB 四通道 + (1 - 总和) 控制五个纹理 |

## Demo 示例

### 最小示例：获取并修改组件的顶点颜色

```cpp
// MeshPaintExample.h
#pragma once

#include "CoreMinimal.h"

class FMeshPaintExample
{
public:
    static void PaintAllVerticesRed(UStaticMeshComponent* Component);
};
```

```cpp
// MeshPaintExample.cpp
#include "MeshPaintExample.h"
#include "MeshPaintHelpers.h"

void FMeshPaintExample::PaintAllVerticesRed(UStaticMeshComponent* Component)
{
    if (!Component) return;
    
    UMeshPaintingSubsystem* Subsystem = GEngine->GetEngineSubsystem<UMeshPaintingSubsystem>();
    if (!Subsystem || !Subsystem->HasPaintableMesh(Component)) return;
    
    // 获取 LOD 0 的实例颜色
    TArray<FColor> Colors = Subsystem->GetInstanceColorDataForLOD(Component, 0);
    
    // 将所有顶点设为红色
    for (FColor& Color : Colors)
    {
        Color = FColor::Red;
    }
    
    // 写回
    Subsystem->SetInstanceColorDataForLOD(Component, 0, Colors);
}
```

**Build.cs 依赖**：

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "MeshPaintingToolset"
});
```

## 模块依赖

### MeshPaintingToolset

| 模块 | 用途 |
|---|---|
| `InteractiveToolsFramework` | 交互工具框架基类 |
| `EditorInteractiveToolsFramework` | 编辑器交互工具扩展 |
| `GeometryCore` | 几何核心（AABB 树等） |
| `Core` | 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `RenderCore` | 渲染核心 |
| `RHI` | 渲染硬件接口 |
| `MeshDescription` | 网格描述数据 |
| `StaticMeshDescription` | 静态网格描述 |
| `GeometryCollectionEngine` | 几何集合引擎（Chaos 破碎） |
| `TypedElementFramework` | 类型化元素框架 |
| `TypedElementRuntime` | 类型化元素运行时 |
| `UnrealEd` | 编辑器核心 |
| `InterchangeEngine` | 交换引擎 |
| `InterchangePipelines` | 交换管线 |
| `Chaos` | Chaos 物理 |
| `ImageCore` | 图像核心 |

### MeshPaintEditorMode

| 模块 | 用途 |
|---|---|
| `Slate` / `SlateCore` | UI 框架 |
| `EditorSubsystem` | 编辑器子系统基类 |
| `MeshPaintingToolset` | 绘制工具集（内部依赖） |
| `InteractiveToolsFramework` | 交互工具框架 |
| `EditorInteractiveToolsFramework` | 编辑器交互工具 |
| `UnrealEd` | 编辑器核心 |
| `PropertyEditor` | 属性编辑器 |
| `MainFrame` | 主窗口 |
| `DesktopPlatform` | 桌面平台（文件对话框） |
| `ToolWidgets` | 工具 UI 组件 |
| `DynamicMesh` | 动态网格 |
| `GeometryCore` | 几何核心 |
| `ImageCore` | 图像核心 |
| `MeshConversionEngineTypes` | 网格转换引擎类型 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-09-23 | `e28f503` | 优化多组件选择时的纹理覆盖性能，共享单个 FMaterialUpdateContext |
| 2025-07-10 | `9803c44` | 添加 UE_INLINE_GENERATED_CPP_BY_NAME（批量代码修复） |
| 2025-06-18 | `1fa8da6` | 修复绘制材质覆盖后的材质重缓存问题，支持 RVT 材质中的纹理绘制 |

### 维护评价

- **创建时间**：2019-11-18，从 UE4 时代迁移而来
- **最近更新**：2025 年 9 月有实质性性能优化和 bug 修复，维护活跃
- **维护状态**：**活跃维护** — 最近 6 个月内有功能性更新
- **注意事项**：
  - 部分 API 标记为 `UE_DEPRECATED(5.7)`，如 `ClearMeshTextureOverrides` 和旧版 `ApplyOrRemoveTextureOverride`
  - 纹理颜色绘制（Texture Color Paint）是较新加入的功能，专门针对 Nanite 网格
  - GeometryCollection 适配器不支持 LOD（注释中标注了 TODO）
- **推荐使用**：✅ 推荐。这是 UE5 内置的官方网格绘制方案，持续维护中

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MeshPainting)
- [官方文档]()（无 DocsURL）
