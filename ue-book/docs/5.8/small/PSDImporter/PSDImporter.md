# PSD Importer

> Import Adobe Photoshop (PSD) files as Unreal Engine assets.

| 属性 | 值 |
|---|---|
| 中文名 | PSD 导入器 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（PSD资产、蓝图角色） |
| 模块 | `PSDImporter` (Runtime), `PSDImporterCore` (Runtime), `PSDImporterEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-28 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PSDImporter) | |

## 用途

这个插件用于将 Adobe Photoshop (PSD) 文件导入到 Unreal Engine 中。它的核心功能是解析 PSD 文件的文档结构、图层信息（包括图层顺序、可见性、混合模式、不透明度等），并将其转换为 UE 内部可管理的资产（`UPSDDocument`）。更重要的是，它能将每个 PSD 图层（或合并后的图层）导入为独立的纹理资产，并进一步将其组合为一个由多个四边形网格（`APSDQuadMeshActor`）组成的场景 Actor（`APSDQuadActor`）。这些四边形网格会保留原始 PSD 图层的层次结构，使得在 UE 中可以像操作原始设计稿一样，独立调整每个图层（元素）的位置、深度、材质等属性，从而实现了设计文件与游戏引擎资产之间的高保真转换和可编辑性。

## 使用场景

- 你正在为一个 2D 风格的游戏或 UI 界面制作资源，美术同事提供的是 Photoshop 的分层源文件（.psd），你希望快速将这些 UI 元素（按钮、背景、图标等）导入 UE 并保持其独立性，以便后续进行交互绑定或动画。
- 你需要将一张复杂的、分层的概念设计图导入场景作为背景或装饰，并希望每个图层（如前景树、中景建筑、背景山）在 UE 中能够单独设置深度和渲染参数以获得视差效果。
- 你正在原型阶段，需要快速将美术设计稿转化为可交互的原型，直接使用设计图中的元素进行游戏逻辑测试。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Document Name` | 获取导入的 PSD 文档原始名称 | `UPSDDocument` |
| `Get Size` | 获取 PSD 文档的宽度和高度（像素） | `UPSDDocument` |
| `Get Layers` | 获取文档内包含的所有图层信息数组 | `UPSDDocument` |
| `Were Layers Resized On Import` | 检查图层在导入时是否被调整大小以匹配文档尺寸 | `UPSDDocument` |
| `Reset All` | 重置对应 PSD 图层 Actor 的所有属性（深度、位置、大小、纹理等）到初始状态 | `APSDQuadMeshActor` |
| `Reset Depth` | 仅重置图层 Actor 的深度（Z轴位置） | `APSDQuadMeshActor` |
| `Reset Position` | 仅重置图层 Actor 的位置（X, Y） | `APSDQuadMeshActor` |
| `Reset Size` | 仅重置图层 Actor 的大小（缩放） | `APSDQuadMeshActor` |
| `Reset Texture` | 重新应用原始导入的纹理材质 | `APSDQuadMeshActor` |
| `Reset Translucent Sort Priority` | 重置图层 Actor 的半透明排序优先级 | `APSDQuadMeshActor` |

### 使用示例（蓝图描述）

1.  **查询文档信息**：从场景中拖拽一个 `PSD Layer Root Actor`（`APSDQuadActor`）到蓝图，调用 `Get PSD Document` 节点获取其关联的 `UPSDDocument` 对象。然后，即可连接到 `Get Document Name`、`Get Size`、`Get Layers` 等节点来读取元数据。
2.  **操作单个图层**：通过 `APSDQuadActor` 的 `Get Quad Meshes` 函数获取其包含的所有 `APSDQuadMeshActor` 数组。通过数组索引或遍历获取特定图层的 Actor。例如，获取第一个图层（通常是背景），然后可以调用 `Reset Quad Position` 或 `Reset Quad Depth` 等 `CallInEditor` 节点（在编辑器内使用）来重置其状态，或者直接通过标准 Actor 节点（如 `Set Actor Location`）修改其位置。
3.  **调整图层间距**：在 `PSD Layer Root Actor` 上设置 `Layer Depth Offset` 属性，这会影响所有子图层四边形之间的深度间隔，用于创建视差效果。

## C++ 用法

### 头文件引入

```cpp
#include "PSDFile.h" // 提供 PSD 文件相关的数据结构，如 FPSDFileLayer, FPSDFileDocument
#include "PSDDocument.h" // 提供 UPSDDocument 类
#include "PSDQuadActor.h" // 提供 APSDQuadActor 类
#include "PSDQuadMeshActor.h" // 提供 APSDQuadMeshActor 类
```

### 基本用法

此示例展示了如何通过 C++ 代码访问一个已导入场景的 `APSDQuadActor`，获取其关联的 `UPSDDocument`，并遍历其图层。

```cpp
// 假设你已经通过某种方式（例如 SpawnActor 或在编辑器中获取引用）得到了一个 APSDQuadActor 指针
APSDQuadActor* MyPSDActor = ...;

if (MyPSDActor)
{
    // 1. 获取 PSD 文档对象
    UPSDDocument* PSDDoc = MyPSDActor->GetPSDDocument();
    if (PSDDoc)
    {
        // 2. 打印文档基本信息
        UE_LOG(LogTemp, Log, TEXT("PSD Document Name: %s, Size: %dx%d"),
            *PSDDoc->GetDocumentName(),
            PSDDoc->GetSize().X,
            PSDDoc->GetSize().Y);

        // 3. 遍历文档图层
        const TArray<FPSDFileLayer>& AllLayers = PSDDoc->GetLayers();
        for (const FPSDFileLayer& Layer : AllLayers)
        {
            // 打印每个图层的 ID 和可见性
            UE_LOG(LogTemp, Log, TEXT("Layer '%s' (Index: %d), Visible: %s"),
                *Layer.Id.Name,
                Layer.Id.Index,
                Layer.bIsVisible ? TEXT("Yes") : TEXT("No"));
        }

        // 4. 获取所有有效的（非完全透明、有尺寸、可见）图层
        TArray<const FPSDFileLayer*> ValidLayers = PSDDoc->GetValidLayers();
        UE_LOG(LogTemp, Log, TEXT("Number of valid layers for import: %d"), ValidLayers.Num());
    }

    // 5. 获取该 PSD Actor 下所有的图层网格 Actor
    TArray<APSDQuadMeshActor*> MeshActors = MyPSDActor->GetQuadMeshes();
    for (APSDQuadMeshActor* MeshActor : MeshActors)
    {
        if (MeshActor)
        {
            // 获取该网格 Actor 对应的图层信息
            const FPSDFileLayer* LayerInfo = MeshActor->GetLayer();
            if (LayerInfo)
            {
                // 这里可以对单个图层 Actor 进行操作
                // 例如，重置其深度
                // MeshActor->ResetQuadDepth(); // 注意：此函数通常用于编辑器操作
            }
        }
    }
}
```

### 进阶用法

更复杂的用法可能涉及在导入流程中进行干预或自定义处理，这需要深入研究 `PSDImporterCore` 和 `PSDImporterEditor` 模块的工厂类和导入逻辑，以及 `PsdSDK` 的底层接口。通常，基本的资产查询和 Actor 操作使用上述 `UPSDDocument` 和 `APSDQuad*` 类的接口即可完成。

## Demo 示例

这是一个最小化的 C++ 示例，展示了如何编写一个简单的 Actor 组件，该组件可以在 BeginPlay 时查找场景中指定的 `APSDQuadActor`，并打印出其文档信息和图层列表。

**PSDInfoPrinterComponent.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "PSDInfoPrinterComponent.generated.h"

class APSDQuadActor;
class UPSDDocument;

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class YOURPROJECT_API UPSDInfoPrinterComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UPSDInfoPrinterComponent();

    // 要查找的 PSD Actor 的标签
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "PSD Printer")
    FName TargetPSDActorTag = "PSDLayerRoot";

protected:
    virtual void BeginPlay() override;

private:
    void FindAndPrintPSDInfo();
};
```

**PSDInfoPrinterComponent.cpp**
```cpp
#include "PSDInfoPrinterComponent.h"
#include "Kismet/GameplayStatics.h"
#include "PSDQuadActor.h"
#include "PSDDocument.h"
#include "PSDFile.h"

UPSDInfoPrinterComponent::UPSDInfoPrinterComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UPSDInfoPrinterComponent::BeginPlay()
{
    Super::BeginPlay();
    FindAndPrintPSDInfo();
}

void UPSDInfoPrinterComponent::FindAndPrintPSDInfo()
{
    if (!GetWorld()) return;

    TArray<AActor*> FoundActors;
    UGameplayStatics::GetAllActorsWithTag(GetWorld(), TargetPSDActorTag, FoundActors);

    for (AActor* Actor : FoundActors)
    {
        APSDQuadActor* PSDQuadActor = Cast<APSDQuadActor>(Actor);
        if (PSDQuadActor)
        {
            UPSDDocument* Doc = PSDQuadActor->GetPSDDocument();
            if (Doc)
            {
                UE_LOG(LogTemp, Display, TEXT("=== PSD Document: %s ==="), *Doc->GetDocumentName());
                UE_LOG(LogTemp, Display, TEXT("Size: %dx%d"), Doc->GetSize().X, Doc->GetSize().Y);
                UE_LOG(LogTemp, Display, TEXT("Total Layers: %d"), Doc->GetLayers().Num());

                int32 LayerIndex = 0;
                for (const FPSDFileLayer& Layer : Doc->GetLayers())
                {
                    UE_LOG(LogTemp, Display, TEXT("  [%d] %s (Visible: %s, Opacity: %.2f)"),
                        LayerIndex,
                        *Layer.Id.Name,
                        Layer.bIsVisible ? TEXT("Yes") : TEXT("No"),
                        Layer.Opacity);
                    LayerIndex++;
                }

                UE_LOG(LogTemp, Display, TEXT("Valid layers for texture generation: %d"), Doc->GetTextureCount());
            }
        }
    }
}
```

**使用方法**：将 `UPSDInfoPrinterComponent` 添加到场景中任意一个 Actor 上（例如，关卡中的某个空 Actor），在 `TargetPSDActorTag` 属性中填写你的 `APSDQuadActor` 的标签（默认是 “PSDLayerRoot”）。运行游戏时，日志窗口将输出该 PSD 文档的详细信息。

## 模块依赖

该插件自身依赖 `GeometryMask` 插件。对于使用该插件的项目，需要根据使用目的进行模块依赖：

| 模块 | 用途 |
|---|---|
| `PSDImporterCore` | 运行时核心逻辑，用于在打包后的项目中处理 PSD 数据（如果运行时需要动态解析） |
| `PSDImporter` | 运行时资产和角色类（`UPSDDocument`, `APSDQuadActor`, `APSDQuadMeshActor`）的定义，是大多数项目需要引用的模块 |
| `GeometryMask` | 提供几何遮罩功能，插件内部依赖，使用者通常无需直接引用 |

**重要提示**：由于此插件标记为 `Installed: false`（默认未启用），你需要手动在项目的 `.uproject` 文件或编辑器插件界面中启用它。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志输出宏 `UE_LOG` 迁移至新的格式化宏 `UE_LOGF`。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复之前因错误的查找替换操作引入的问题（第二次尝试）。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退了 CL51314860 这次变更。 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 将引擎初始化委托从静态变量改为通过函数获取，以修复可能的注册丢失问题。 |
| 2025-07-15 | `bafe5da2` | Silence incorrect V1051 warnings | 抑制（Silence）静态代码分析工具 V1051 产生的不正确的警告信息。 |

### 维护评价

- **年龄与状态**：这是一个于 2025 年 4 月创建的较新插件（约 1 年），目前仍处于 **实验性**（`IsExperimentalVersion: true`）阶段，并且默认未启用（`Installed: false`）。
- **更新频率**：从提交记录看，近期（2026年）有多次维护性更新，主要是跟随 UE 引擎代码规范调整（如委托接口、日志宏）和修复内部问题。这表明插件仍被 Epic 内部维护或使用，以保持与引擎主干的兼容性。
- **功能更新**：最近的提交没有包含重大的新功能开发，主要以维护和修复为主。
- **推荐程度**：**适合实验和原型验证**。由于它是实验性插件，API 和功能可能在未来版本中发生变化或被移除。不推荐在追求稳定性的正式生产项目中深度依赖。对于需要将 PSD 文件导入 UE 并保持图层独立性的非关键路径或内部工具链，可以尝试使用。使用时需关注其随 UE 版本升级可能出现的兼容性问题。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PSDImporter)
- 官方文档：暂无
- 测试用例：暂无（用户未提供路径）