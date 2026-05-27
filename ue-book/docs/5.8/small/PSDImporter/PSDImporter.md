# PSD Importer

> 用于在 Unreal Engine 中导入 Adobe Photoshop PSD 文件的插件

| 属性 | 值 |
|---|---|
| 中文名 | PSD 导入器 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `PSDImporter` (Runtime), `PSDImporterCore` (Runtime), `PSDImporterEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-28 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PSDImporter) | |

## 用途

PSDImporter 解决了将 Adobe Photoshop 的 PSD 分层文件直接导入 Unreal Engine 并在场景中还原图层结构的问题。传统做法是将 PSD 手动拆分为多个单独的 PNG/TGA 再逐一导入，丢失了图层层级、混合模式、蒙版等信息。该插件通过内置的 PsdSDK（第三方 PSD 解析库）直接读取 PSD 文件，自动为每个图层生成纹理资产，并可选择性地在场景中以分层四边形（Quad Mesh）的方式重建 PSD 的图层堆叠关系，支持：

- **图层解析**：识别图层类型（普通图层/图层组）、混合模式、不透明度、可见性、剪切图层等
- **蒙版支持**：导入图层的 Alpha 蒙版作为独立纹理
- **图层裁剪**：自动检测并裁剪非全尺寸图层，节省纹理内存
- **3D 场景重建**：将 PSD 图层以带有深度偏移的四边形网格排列在场景中，可用于 2.5D 美术效果、UI 布局预览等
- **图层组支持**：识别 PSD 中的 Group 图层并维护父子关系

插件依赖 GeometryMask 插件，仅支持 Win64 平台。

## 使用场景

- 你是一名技术美术，需要将 Photoshop 中设计好的多层 UI 布局快速导入到 UE5 中预览 → 使用 PSD Importer
- 你需要在 3D 场景中还原 2D 美术的图层深度关系（如前景/背景分层） → 导入后自动创建带深度偏移的四边形网格
- 你需要为每个 PSD 图层单独生成纹理资产用于运行时动态组合 → 导入时自动为每个图层创建 UTexture2D
- 你需要保留 PSD 中的蒙版信息用于运行时效果 → 插件会将蒙版作为独立纹理导入

## 蓝图用法

### 核心节点

#### 文档信息（UPSDDocument）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Document Name` | 获取 PSD 文档的原始文件名 | `UPSDDocument` |
| `Get Size` | 获取文档分辨率（像素宽高） | `UPSDDocument` |
| `Get Layers` | 获取文档中所有图层的数组 | `UPSDDocument` |
| `Were Layers Resized On Import` | 图层在导入时是否被缩放至文档尺寸 | `UPSDDocument` |

#### 图层操作（APSDQuadMeshActor）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Reset All` | 重置图层四边形的所有属性（位置、大小、深度、纹理、排序优先级） | `APSDQuadMeshActor` |
| `Reset Depth` | 仅重置图层深度 | `APSDQuadMeshActor` |
| `Reset Position` | 仅重置图层位置 | `APSDQuadMeshActor` |
| `Reset Size` | 仅重置图层大小 | `APSDQuadMeshActor` |
| `Reset Texture` | 仅重置图层纹理 | `APSDQuadMeshActor` |
| `Reset Translucent Sort Priority` | 仅重置半透明排序优先级 | `APSDQuadMeshActor` |

> 注：Reset 系列节点标记为 `CallInEditor`，通常在编辑器细节面板中使用，但也可在蓝图中调用。

### 使用示例（蓝图描述）

1. **获取 PSD 文档信息**：拖入一个已导入的 `PSDDocument` 资产引用 → 连接 `Get Document Name` / `Get Size` / `Get Layers` 节点获取文档信息
2. **遍历图层并处理**：从 `Get Layers` 输出的数组，使用 `ForEachLoop` 遍历 → 通过 `FPSDFileLayer` 结构体的 `Id.Name`、`Type`、`Opacity`、`BlendMode` 等属性进行条件过滤和逻辑处理
3. **重置图层四边形**：获取 `APSDQuadMeshActor` 引用 → 调用 `Reset Quad`（或其细分变体）恢复默认状态

## C++ 用法

### 头文件引入

```cpp
#include "PSDFile.h"
#include "PSDDocument.h"
#include "PSDQuadActor.h"
#include "PSDQuadMeshActor.h"
```

### 基本用法：查询 PSD 文档信息

```cpp
// 假设已有 UPSDDocument* PSDDocument
UPSDDocument* Doc = /* 从资产或工厂获取 */;

// 获取文档基本信息
const FString& Name = Doc->GetDocumentName();
const FIntPoint& DocSize = Doc->GetSize();
UE_LOG(LogTemp, Log, TEXT("PSD Document: %s, Size: %dx%d"), *Name, DocSize.X, DocSize.Y);

// 遍历图层
const TArray<FPSDFileLayer>& Layers = Doc->GetLayers();
for (const FPSDFileLayer& Layer : Layers)
{
    UE_LOG(LogTemp, Log, TEXT("  Layer[%d]: %s, Visible: %d, Opacity: %.2f"),
        Layer.Id.Index, *Layer.Id.Name, Layer.bIsVisible, Layer.Opacity);
    
    // 检查图层类型
    if (Layer.Type == EPSDFileLayerType::Group)
    {
        UE_LOG(LogTemp, Log, TEXT("    (Group Layer)"));
    }
    
    // 检查是否有蒙版
    if (Layer.HasMask())
    {
        UE_LOG(LogTemp, Log, TEXT("    Has mask, MaskDefault: %.2f"), Layer.MaskDefaultValue);
    }
}
```

### 基本用法：操作场景中的四边形网格

```cpp
// 假设已有 APSDQuadActor* QuadActor
APSDQuadActor* QuadRoot = /* 从场景获取 */;

// 获取关联的文档
UPSDDocument* Doc = QuadRoot->GetPSDDocument();

// 获取所有子四边形网格
TArray<APSDQuadMeshActor*> Meshes = QuadRoot->GetQuadMeshes();

// 调整图层间距
QuadRoot->SetLayerDepthOffset(2.0f);  // 每层间距 2 个单位

// 设置基础半透明排序优先级
QuadRoot->SetBaseTranslucentSortPriority(1);
```

### 进阶用法：自定义图层导入

```cpp
// 获取图层并检查是否需要裁剪
const TArray<FPSDFileLayer>& Layers = Doc->GetLayers();
const FIntPoint DocSize = Doc->GetSize();

for (const FPSDFileLayer& Layer : Layers)
{
    // 判断图层是否为非全尺寸（需要裁剪）
    if (Layer.NeedsCrop(DocSize))
    {
        UE_LOG(LogTemp, Log, TEXT("Layer '%s' needs crop: Bounds=[%d,%d - %d,%d]"),
            *Layer.Id.Name,
            Layer.Bounds.Min.X, Layer.Bounds.Min.Y,
            Layer.Bounds.Max.X, Layer.Bounds.Max.Y);
    }
    
    // 获取图层的裁剪信息
    if (Layer.Clipping != 0)
    {
        UE_LOG(LogTemp, Log, TEXT("Layer '%s' is a clipping layer"), *Layer.Id.Name);
    }
    
    // 检查图层支持状态
    if (!Layer.bIsSupportedLayerType)
    {
        UE_LOG(LogTemp, Warning, TEXT("Layer '%s' has unsupported type"), *Layer.Id.Name);
    }
}
```

### 进阶用法：访问纹理的图层元数据

```cpp
// 导入的纹理上附带有 UPSDLayerTextureUserData
UTexture2D* Texture = /* 从 Layer.Texture 加载 */;

if (UPSDLayerTextureUserData* UserData = Texture->GetAssetUserData<UPSDLayerTextureUserData>())
{
    UE_LOG(LogTemp, Log, TEXT("Texture layer: %s [%d]"),
        *UserData->LayerId.Name, UserData->LayerId.Index);
    UE_LOG(LogTemp, Log, TEXT("  Normalized Bounds: %s"),
        *UserData->NormalizedBounds.ToString());
    UE_LOG(LogTemp, Log, TEXT("  Pixel Bounds: [%d,%d - %d,%d]"),
        UserData->PixelBounds.Min.X, UserData->PixelBounds.Min.Y,
        UserData->PixelBounds.Max.X, UserData->PixelBounds.Max.Y);
}
```

## Demo 示例

### 创建 PSD 四边形网格并配置深度

```cpp
// MyPSDActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "PSDDocument.h"
#include "PSDQuadActor.h"
#include "MyPSDActor.generated.h"

UCLASS()
class AMyPSDActor : public AActor
{
    GENERATED_BODY()

public:
    AMyPSDActor();

    UPROPERTY(EditAnywhere, Category = "PSD")
    TObjectPtr<UPSDDocument> PSDDocument;

    UPROPERTY(EditAnywhere, Category = "PSD")
    float LayerSpacing = 1.5f;

    UFUNCTION(BlueprintCallable, Category = "PSD")
    void SetupDocument();
};
```

```cpp
// MyPSDActor.cpp
#include "MyPSDActor.h"
#include "PSDQuadMeshActor.h"

AMyPSDActor::AMyPSDActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyPSDActor::SetupDocument()
{
    if (!PSDDocument)
    {
        UE_LOG(LogTemp, Warning, TEXT("No PSD Document assigned"));
        return;
    }

    const FString& DocName = PSDDocument->GetDocumentName();
    const FIntPoint& DocSize = PSDDocument->GetSize();
    const TArray<FPSDFileLayer>& Layers = PSDDocument->GetLayers();

    UE_LOG(LogTemp, Log, TEXT("Setting up PSD: %s (%dx%d), %d layers"),
        *DocName, DocSize.X, DocSize.Y, Layers.Num());

    // 遍历所有图层，检查有效图层
    for (const FPSDFileLayer& Layer : Layers)
    {
        if (!Layer.bIsVisible)
        {
            UE_LOG(LogTemp, Log, TEXT("Skipping hidden layer: %s"), *Layer.Id.Name);
            continue;
        }

        // 设置图层间距
        if (Layer.NeedsCrop(DocSize))
        {
            UE_LOG(LogTemp, Log, TEXT("Layer '%s' will be cropped to [%d,%d - %d,%d]"),
                *Layer.Id.Name,
                Layer.Bounds.Min.X, Layer.Bounds.Min.Y,
                Layer.Bounds.Max.X, Layer.Bounds.Max.Y);
        }

        // 检查蒙版信息
        if (Layer.HasMask())
        {
            UE_LOG(LogTemp, Log, TEXT("Layer '%s' has mask: default=%.2f, bounds=[%d,%d - %d,%d]"),
                *Layer.Id.Name, Layer.MaskDefaultValue,
                Layer.MaskBounds.Min.X, Layer.MaskBounds.Min.Y,
                Layer.MaskBounds.Max.X, Layer.MaskBounds.Max.Y);
        }
    }

    UE_LOG(LogTemp, Log, TEXT("Total textures to generate: %d"), PSDDocument->GetTextureCount());
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GeometryMask` | 插件级依赖，用于几何蒙版功能支持 |

**外部依赖**：
- `PsdSDK`：第三方 PSD 文件解析库（位于 `Source/ThirdParty/PsdSDK/`），负责读取和解析 Photoshop 二进制格式

**模块间依赖关系**：
- `PSDImporterCore` → 核心数据类型和解析逻辑
- `PSDImporter` → 运行时模块，依赖 `PSDImporterCore`
- `PSDImporterEditor` → 编辑器导入工厂和 UI，依赖 `PSDImporter` 和 `PSDImporterCore`

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新版 UE_LOGF 格式 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复错误的批量替换操作 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退一个有问题的变更 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 修复引擎初始化委托的注册问题 |
| 2025-07-15 | `bafe5da2` | Silence incorrect V1051 warnings | 抑制静态分析工具的误报警告 |

### 维护评价

- **活跃程度**：插件创建于 2025 年 4 月，最近一次更新在 2026 年 4 月，约 1 年的生命周期内保持了持续更新
- **更新内容**：近期提交主要为代码质量维护（日志迁移、静态分析警告修复、API 重命名适配），未见重大功能变更
- **实验性状态**：标记为 `IsExperimentalVersion=true` 且 `Installed=false`，属于实验阶段，尚未默认启用
- **平台限制**：仅支持 Win64，跨平台使用受限
- **推荐度**：如果你的工作流涉及大量 PSD 文件到 UE5 的转换（尤其是技术美术和 2.5D 项目），可以尝试使用。但由于是实验性插件，API 可能在未来版本中发生变化，不建议在生产环境中深度依赖

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PSDImporter)
- [GeometryMask 依赖插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/GeometryMask)