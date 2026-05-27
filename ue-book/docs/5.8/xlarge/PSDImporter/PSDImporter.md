# PSD Importer

> 

| 属性 | 值 |
|---|---|
| 中文名 | PSD 导入器 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `PSDImporter` (Runtime), `PSDImporterCore` (Runtime), `PSDImporterEditor` (Editor), `PsdSDK` (External) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-28 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PSDImporter) | |

## 用途

PSD Importer 插件用于将 Adobe Photoshop 的 PSD 文件直接导入 Unreal Engine。它能够解析 PSD 文件的完整图层结构，将每个图层分别导入为独立的纹理资产，并创建对应的四边形网格 Actor 在场景中按图层顺序排列显示。

核心解决的问题：
- **图层保真导入**：保持 PSD 文件的图层层次结构、混合模式、透明度、可见性等属性
- **图层蒙版支持**：单独提取并导入图层的 Alpha 蒙版
- **空间化显示**：通过四边形 Actor 将 2D 图层在 3D 空间中按深度排列，支持图层间距、视距调整和半透明排序
- **裁切图层支持**：识别和处理 Photoshop 的裁切图层（Clipping Layer）

该插件目前处于实验阶段（Experimental），仅支持 Win64 平台，且依赖 GeometryMask 插件。

## 使用场景

- 你在 Photoshop 中制作了多图层的 2D 游戏 UI，需要将每个图层分别导入引擎 → 用 PSD Importer
- 你需要将概念艺术或背景图按图层深度排列到 3D 场景中 → 用 PSD Importer
- 你在做 2.5D 游戏，需要将 Photoshop 设计稿直接转换为场景中的四边形排列 → 用 PSD Importer
- 你需要保留 PSD 图层的蒙版信息用于运行时遮罩效果 → 用 PSD Importer

## 蓝图用法

### 核心节点

#### 文档访问

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Document Name` | 获取 PSD 文档原始文件名 | `UPSDDocument` |
| `Get Size` | 获取文档分辨率（宽×高像素） | `UPSDDocument` |
| `Get Layers` | 获取文档中所有图层的数组 | `UPSDDocument` |
| `Were Layers Resized On Import` | 查询导入时图层是否被调整到文档大小 | `UPSDDocument` |

#### 四边形 Actor 控制

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get PSDDocument` | 获取关联的 PSD 文档资产 | `APSDQuadActor` |
| `Get Quad Meshes` | 获取所有子图层 Actor 列表 | `APSDQuadActor` |
| `Get/Set Layer Depth Offset` | 获取/设置图层之间的 Z 轴间距 | `APSDQuadActor` |
| `Get/Set Adjust For View Distance` | 获取/设置视距补偿距离 | `APSDQuadActor` |
| `Get/Set Base Translucent Sort Priority` | 获取/设置半透明排序基础优先级 | `APSDQuadActor` |

#### 图层 Actor 操作（CallInEditor）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Reset All` | 重置图层的所有设置为默认值 | `APSDQuadMeshActor` |
| `Reset Depth` | 仅重置图层深度 | `APSDQuadMeshActor` |
| `Reset Position` | 仅重置图层位置 | `APSDQuadMeshActor` |
| `Reset Size` | 仅重置图层大小 | `APSDQuadMeshActor` |
| `Reset Texture` | 仅重置图层纹理 | `APSDQuadMeshActor` |
| `Reset Translucent Sort Priority` | 仅重置半透明排序优先级 | `APSDQuadMeshActor` |

#### 图层属性访问

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Layer` | 获取关联的图层数据 | `APSDQuadMeshActor` |
| `Get Clipping Layer` | 获取裁切到当前图层的图层数据 | `APSDQuadMeshActor` |
| `Get Quad Material` | 获取图层使用的材质 | `APSDQuadMeshActor` |
| `Get Quad Actor` | 获取所属的根四边形 Actor | `APSDQuadMeshActor` |

### 使用示例（蓝图描述）

1. **导入 PSD 文件**：在 Content Browser 中右键 → Import，选择 .psd 文件。插件会自动创建 `UPSDDocument` 资产，并可选择在场景中生成 `APSDQuadActor` 及其子 Actor
2. **在蓝图中访问图层信息**：获取 `UPSDDocument` 引用后，调用 `Get Layers` 获得所有图层，遍历数组获取每个图层的名称、透明度、混合模式等属性
3. **调整图层深度**：选中场景中的 `APSDQuadActor`，通过 Details 面板调整 `Layer Depth Offset` 属性，所有子图层会自动按指定间距重新排列

## C++ 用法

### 头文件引入

```cpp
#include "PSDFile.h"
#include "PSDDocument.h"
#include "PSDQuadActor.h"
#include "PSDQuadMeshActor.h"
```

### 基本用法

```cpp
// 获取导入的 PSD 文档
UPSDDocument* Document = /* 通过资产引用获取 */;

// 获取文档基本信息
const FString& DocName = Document->GetDocumentName();
const FIntPoint& DocSize = Document->GetSize();
bool bResized = Document->WereLayersResizedOnImport();

// 遍历所有图层
const TArray<FPSDFileLayer>& Layers = Document->GetLayers();
for (const FPSDFileLayer& Layer : Layers)
{
    // 获取图层标识
    FPSDFileLayerId LayerId = Layer.Id;
    int32 Index = LayerId.Index;
    const FString& Name = LayerId.Name;

    // 获取图层属性
    EPSDBlendMode BlendMode = Layer.BlendMode;
    double Opacity = Layer.Opacity;
    bool bVisible = Layer.bIsVisible;
    FIntRect Bounds = Layer.Bounds;

    // 检查是否有蒙版
    if (Layer.HasMask())
    {
        TSoftObjectPtr<UTexture2D> MaskTexture = Layer.Mask;
        FIntRect MaskBounds = Layer.MaskBounds;
        float MaskDefault = Layer.MaskDefaultValue;
    }

    // 设置导入操作
    // 可选: Import, ImportMerged, Rasterize, Ignore
}
```

### 进阶用法

```cpp
// 在场景中创建四边形 Actor 层级结构
APSDQuadActor* QuadActor = /* 获取或创建 */;

// 配置图层间距
QuadActor->SetLayerDepthOffset(5.0f);  // 每个图层间隔 5 个单位

// 配置视距补偿
QuadActor->SetAdjustForViewDistance(1000.0f);  // 1000 单位内减小近处四边形尺寸

// 配置半透明排序
QuadActor->SetBaseTranslucentSortPriority(10);  // 从优先级 10 开始递增

// 获取所有图层 Actor
TArray<APSDQuadMeshActor*> MeshActors = QuadActor->GetQuadMeshes();
for (APSDQuadMeshActor* MeshActor : MeshActors)
{
    const FPSDFileLayer* Layer = MeshActor->GetLayer();
    const FPSDFileLayer* ClipLayer = MeshActor->GetClippingLayer();
    UMaterialInterface* Material = MeshActor->GetQuadMaterial();
}
```

## Demo 示例

```cpp
// PSDDemoComponent.h
#pragma once

#include "Components/ActorComponent.h"
#include "PSDDemoComponent.generated.h"

class UPSDDocument;
class APSDQuadActor;

UCLASS(ClassGroup=(PSD), meta=(BlueprintSpawnableComponent))
class UPSDDemoComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category = "PSD")
    TSoftObjectPtr<UPSDDocument> Document;

    UPROPERTY(EditAnywhere, Category = "PSD")
    float LayerSpacing = 2.0f;

    UFUNCTION(BlueprintCallable, Category = "PSD")
    void PrintDocumentInfo();

    UFUNCTION(BlueprintCallable, Category = "PSD")
    void ListAllLayers();
};
```

```cpp
// PSDDemoComponent.cpp
#include "PSDDemoComponent.h"
#include "PSDDocument.h"
#include "PSDFile.h"

void UPSDDemoComponent::PrintDocumentInfo()
{
    UPSDDocument* Doc = Document.LoadSynchronous();
    if (!Doc)
    {
        UE_LOG(LogTemp, Warning, TEXT("PSD Document not loaded"));
        return;
    }

    UE_LOG(LogTemp, Log, TEXT("Document: %s"), *Doc->GetDocumentName());
    UE_LOG(LogTemp, Log, TEXT("Size: %dx%d"), Doc->GetSize().X, Doc->GetSize().Y);
    UE_LOG(LogTemp, Log, TEXT("Layer count: %d"), Doc->GetLayers().Num());
    UE_LOG(LogTemp, Log, TEXT("Texture count: %d"), Doc->GetTextureCount());
    UE_LOG(LogTemp, Log, TEXT("Layers resized: %s"), Doc->WereLayersResizedOnImport() ? TEXT("Yes") : TEXT("No"));
}

void UPSDDemoComponent::ListAllLayers()
{
    UPSDDocument* Doc = Document.LoadSynchronous();
    if (!Doc) return;

    // 获取有效图层（有有效大小、可见、非完全透明、类型受支持）
    TArray<const FPSDFileLayer*> ValidLayers = Doc->GetValidLayers();
    UE_LOG(LogTemp, Log, TEXT("Valid layers: %d"), ValidLayers.Num());

    for (const FPSDFileLayer* Layer : ValidLayers)
    {
        UE_LOG(LogTemp, Log, TEXT("  Layer [%d] '%s' | Blend: %d | Opacity: %.2f | Visible: %d | Has Mask: %d"),
            Layer->Id.Index,
            *Layer->Id.Name,
            static_cast<int32>(Layer->BlendMode),
            Layer->Opacity,
            Layer->bIsVisible,
            Layer->HasMask());

        // 检查是否需要裁切（图层或蒙版不等于文档全尺寸）
        if (Layer->NeedsCrop(Doc->GetSize()))
        {
            UE_LOG(LogTemp, Log, TEXT("    -> Layer needs crop to document size"));
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GeometryMask` | 几何遮罩功能，用于图层蒙版处理 |
| `PsdSDK` | 第三方 PSD 文件解析库 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新格式 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复上一次批量替换错误后的重试 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退有问题的变更 CL51314860 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 修复引擎初始化委托注册方式的兼容性问题 |
| 2025-07-15 | `bafe5da2` | Silence incorrect V1051 warnings | 抑制静态分析工具的误报警告 |

### 维护评价

**实验性插件，维护中但尚未成熟。**

- **创建时间**：2025 年 4 月，历史较短
- **更新频率**：2026 年有多次更新，主要为编译兼容性和 API 迁移修复，属于被动维护
- **实验状态**：`IsExperimentalVersion=true`，`Installed=false`（非默认安装），表明 Epic 尚未将其视为稳定功能
- **平台限制**：仅支持 Win64，限制了适用范围
- **依赖关系**：依赖外部 PsdSDK 第三方库和 GeometryMask 插件

**使用建议**：可以在实验项目或原型开发中使用，但不建议在生产环境中依赖。由于是实验性插件，API 可能在后续版本中发生破坏性变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PSDImporter)
- [官方文档]()（暂无）