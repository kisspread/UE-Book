# Landmass

> （Description from .uplugin 为空）

| 属性 | 值 |
|---|---|
| 中文名 | 地形编辑器 |
| 分类 | Landscape |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `Landmass` (Runtime), `LandmassEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-10-02 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Landmass) | |

## 用途

Landmass 是一个用于 UE5 编辑器的程序化地形编辑框架。它提供了一套基于蓝图的、基于图层的地形画刷系统，允许开发者通过放置和配置 Actor 来非破坏性地编辑地形的高度图和权重图。

其核心思想是管理一个“画刷”（Brush）的四叉树（Quadtree），该树高效地组织和处理多个相互重叠的程序化地形修改器。每个画刷可以是一个简单的形状，也可以是一个复杂的效果（如侵蚀），并通过材质定义其行为。系统负责将这些画刷的渲染结果混合到地形的最终表现上。

## 使用场景

- 你需要一个非破坏性的工作流来编辑大型世界地图 → 使用 Landmass 的画刷系统来程序化生成和调整地形特征。
- 你希望利用材质图来定义复杂的地形修改逻辑（如侵蚀、沉积、河流生成）→ 使用 `ALandmassActor` 或继承它，并将材质赋给其 `HeightMaterial` 或 `WeightmapMaterial`。
- 你需要管理大量重叠的地形修改器，并希望它们高效地混合 → Landmass 的四叉树管理器 (`ALandmassManagerBase`) 会自动处理空间划分和优化。

## 蓝图用法

### 核心节点

**ALandmassManagerBase (管理器)**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Target Landscape` | 将管理器绑定到指定的地形 Actor | `ALandmassManagerBase` |
| `Add Brush To Tree` | 将一个画刷 Actor 添加到四叉树中，并返回受影响的区域和画刷 | `ALandmassManagerBase` |
| `Remove Brush From Tree` | 从四叉树中移除一个画刷 Actor | `ALandmassManagerBase` |
| `Draw Brush Material` | 使用指定材质渲染画刷（用于预览或调试） | `ALandmassManagerBase` |
| `Get Actors Within Modified Nodes` | 获取四叉树中特定节点内的所有画刷 Actor | `ALandmassManagerBase` |
| `Request Update From Brush` | 请求一个画刷更新其输出（例如参数改变后） | `ALandmassManagerBase` |

**ALandmassActor (画刷)**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Fast Preview Mode` | 快速进入地形编辑预览模式 | `ALandmassActor` |
| `Restore Landscape Editing` | 恢复正常的地形编辑状态 | `ALandmassActor` |
| `Render Layer` | 核心函数，由系统调用以生成画刷的效果（重写此函数以实现自定义逻辑） | `ALandmassActor` |
| `Move Brush Up/Down` | 在画刷堆栈顺序中上移或下移 | `ALandmassActor` |
| `Update Brush Extents` | 根据 BrushSize 更新画刷的边界 | `ALandmassActor` |
| `Draw Brush Material` | 使用指定材质渲染该画刷 | `ALandmassActor` |

**ALandmassErosionBrushBase (侵蚀刷基类)**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Target Landscape` | 将侵蚀刷绑定到指定地形 | `ALandmassErosionBrushBase` |
| `Find And Assign Landscape` | 自动查找并分配场景中的地形 | `ALandmassErosionBrushBase` |

**ULandmassBlueprintFunctionLibrary (工具库)**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Cursor World Ray` | 获取编辑器中鼠标光标在世界空间中的射线（起点和方向） | `ULandmassBlueprintFunctionLibrary` |
| `Combine World Extents` | 合并两个世界空间边界（FVector4） | `ULandmassBlueprintFunctionLibrary` |
| `World Extents To Canvas Coordinates` | 将世界边界转换为画布坐标（用于 UI 绘制） | `ULandmassBlueprintFunctionLibrary` |
| `Force Update Texture` | 强制更新一个纹理（用于调试） | `ULandmassBlueprintFunctionLibrary` |

### 使用示例（蓝图描述）

1.  **创建管理器**：在场景中放置一个 `ALandmassManagerBase` Actor。在它的细节面板中，点击 `Set Target Landscape` 按钮并选择你场景中的地形。
2.  **创建画刷**：在场景中放置一个 `ALandmassActor`（或继承自它的自定义画刷）。在画刷的细节面板中：
    - 设置 `Height Material` 和/或 `Weightmap Material` 为你希望使用的材质。
    - 调整 `Brush Size`。
    - 设置 `Affects Heightmap` 或 `Affects Weightmaps` 为 true。
3.  **连接画刷与管理器**：在画刷的细节面板中，找到 `BrushManager` 属性并指向你之前创建的管理器。
4.  **预览**：选中画刷 Actor，然后在画刷的细节面板中点击 `Fast Preview Mode` 按钮，即可看到它对地形的实时影响。完成后，点击 `Restore Landscape Editing` 退出预览。
5.  **调整顺序**：选中画刷后，点击 `Move Brush Up` 或 `Move Brush Down` 来调整它与其他画刷的混合顺序。

## C++ 用法

### 头文件引入

```cpp
#include "LandmassManagerBase.h"
#include "LandmassActor.h"
#include "LandmassBPEditorExtension.h"
```

### 基本用法

创建一个自定义的地形画刷 Actor，重写 `RenderLayer` 函数来定义其行为。

```cpp
// 来源: 公共 API 设计
// MyErosionBrush.h
#pragma once
#include "LandmassActor.h"
#include "MyErosionBrush.generated.h"

UCLASS()
class AMyErosionBrush : public ALandmassActor
{
    GENERATED_BODY()

public:
    AMyErosionBrush();

    // 重写此函数以定义画刷如何影响地形
    virtual void RenderLayer_Implementation(const FLandscapeBrushParameters& InParameters) override;

    UPROPERTY(EditAnywhere, Category = "MyBrush")
    float ErosionStrength = 1.0f;
};

// MyErosionBrush.cpp
#include "MyErosionBrush.h"
#include "Landscape.h"

AMyErosionBrush::AMyErosionBrush()
{
    // 通常会在这里分配一个材质，例如一个计算简单噪声的材质
    // HeightMaterial = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/Materials/M_SimpleNoise"));
}

void AMyErosionBrush::RenderLayer_Implementation(const FLandscapeBrushParameters& InParameters)
{
    // InParameters 包含了渲染所需的信息，如渲染目标、区域大小等
    UTextureRenderTarget2D* RenderTarget = InParameters.CombinedResult;
    // ... 使用 RenderTarget 和 ErosionStrength 来计算并绘制侵蚀效果 ...
    // 实际实现会使用 FCanvas 或材质来向 RenderTarget 绘制
}
```

### 进阶用法

在 C++ 中与管理器交互，动态添加或移除画刷。

```cpp
// 假设你已经有了管理器的指针 AMyManager* MyManager 和画刷的指针 AMyErosionBrush* MyBrush
#include "LandmassManagerBase.h"

void AddMyBrushToLandscape(ALandmassManagerBase* Manager, ALandmassActor* Brush)
{
    if (Manager && Brush)
    {
        FVector4 ModifiedExtents;
        TArray<ALandmassActor*> InvalidatedBrushes;
        TArray<int32> ModifiedNodes;
        // 将画刷添加到管理器的四叉树中
        Manager->AddBrushToTree(Brush, Brush->BrushExtents, Brush->DrawToEntireLandscape,
                                ModifiedExtents, InvalidatedBrushes, ModifiedNodes);
    }
}
```

## Demo 示例

一个最小可编译的自定义画刷示例。

**MySimpleNoiseBrush.h**
```cpp
#pragma once
#include "LandmassActor.h"
#include "MySimpleNoiseBrush.generated.h"

UCLASS()
class AMySimpleNoiseBrush : public ALandmassActor
{
    GENERATED_BODY()

public:
    AMySimpleNoiseBrush();

    virtual void RenderLayer_Implementation(const FLandscapeBrushParameters& InParameters) override;
};
```

**MySimpleNoiseBrush.cpp**
```cpp
#include "MySimpleNoiseBrush.h"
#include "Engine/TextureRenderTarget2D.h"
#include "Kismet/KismetRenderingLibrary.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "UObject/ConstructorHelpers.h"

AMySimpleNoiseBrush::AMySimpleNoiseBrush()
{
    // 尝试加载一个简单的材质作为示例
    static ConstructorHelpers::FObjectFinder<UMaterial> MaterialFinder(TEXT("/Engine/EngineDebugMaterials/DebugVertexNormalWorldSpace"));
    if (MaterialFinder.Succeeded())
    {
        HeightMaterial = MaterialFinder.Object;
    }
}

void AMySimpleNoiseBrush::RenderLayer_Implementation(const FLandscapeBrushParameters& InParameters)
{
    // 这是一个非常简单的示例，实际的噪声生成逻辑会在这里实现
    // 例如，我们可以清空目标，然后画一个渐变
    if (InParameters.CombinedResult)
    {
        FCanvas Canvas(InParameters.CombinedResult->GameThread_GetRenderTargetResource(), nullptr, FApp::GetCurrentTime() - GStartTime, FApp::GetDeltaTime());
        // 用红色清除
        Canvas.Clear(FLinearColor::Red);
        // 在这里添加更多绘制逻辑...
        Canvas.Flush_GameThread();
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。从代码结构推断，可能依赖 `Landscape` 模块。

| 模块 | 用途 |
|---|---|
| `Landscape` | 核心地形系统，Landmass 的画刷基于 `ALandscapeBlueprintBrushBase` |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的 `UE_LOG` 宏迁移到新的 `UE_LOGF` 宏。 |
| 2025-08-27 | `5ac9e159` | Landscape - Deprecating non-edit layer based landscapes | 弃用了不基于编辑图层的旧版地形系统。 |
| 2025-05-29 | `8bd3e004` | Fix blutility module not guaranteed to be loaded when Landmass engine plugin compiles its content de | 修复了在 Landmass 插件编译其内容时，蓝图工具模块可能未加载的依赖性问题。 |
| 2025-05-01 | `0faa16c2` | Landscape Editor - Making BPBrushBase non placeable to ensure brushes are only added from Landscape | 将 `ALandscapeBlueprintBrushBase` 设为不可直接放置，确保画刷只能通过地形编辑器添加。 |
| 2025-03-07 | `1a599460` | Remove codepaths related to HasNormalCaptureBPBrushLayer. No longer required with new landscape bor | 移除了与 `HasNormalCaptureBPBrushLayer` 相关的代码路径，新版本不再需要。 |

### 维护评价

Landmass 是一个已存在超过 6 年的**实验性**插件（`IsBetaVersion=true`，且默认未安装）。从 Git 历史看，最近的更新（2025-2026年）主要是**编译修复、API 弃用和跟随主引擎地形系统的重构**，而非核心功能的增强或新特性开发。

它为复杂的程序化地形编辑提供了一个强大的框架，但作为实验性功能，其 API 可能不稳定，且 Epic 官方可能不会提供全面的支持。适合有明确需求且愿意承担一定技术风险的项目使用。不推荐作为生产环境中的核心依赖，除非你有深入研究和维护的能力。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Landmass)
- [官方文档]() (无)
- [测试用例]() (未在当前分析信息中提供)