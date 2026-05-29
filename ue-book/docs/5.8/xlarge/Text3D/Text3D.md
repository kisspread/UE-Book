# Text 3D

> Tool to create 3D Text with advanced options

| 属性 | 值 |
|---|---|
| 中文名 | 三维文本 |
| 分类 | Text |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质模板、样式集、字体相关资产） |
| 模块 | `Text3D` (Runtime), `Text3DEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-09-03 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Text3D) | |

## 用途

Text3D 插件为虚幻引擎提供了一个高性能、功能丰富的3D文本生成与渲染系统。它不仅仅是将文字变成3D网格，而是一个完整的文本渲染管线，专为虚拟制作（Virtual Production）、动态设计（Motion Design）和高级UI等场景设计。其主要解决以下问题：

1.  **高质量的3D文字生成**：使用 FreeType 和 HarfBuzz 进行字形解析和文本整形，支持复杂的 Unicode 文本、连字、双向文本等。
2.  **高效的性能与内存管理**：通过 `UText3DEngineSubsystem` 实现字形网格的缓存与复用，并支持多线程构建，避免每帧重复计算。
3.  **可扩展的模块化架构**：采用“扩展（Extension）”系统，将文本的渲染、布局、材质、样式、几何形状等功能解耦为独立组件。用户可以轻松替换或组合这些扩展来实现高度定制化的效果。
4.  **支持丰富的视觉效果**：内置了多种材质风格（纯色、渐变、纹理）、几何效果（挤出、斜角、描边）以及逐字符动画效果（位置、旋转、缩放、延迟）。

## 使用场景

-   **虚拟制作与LED墙**：在XR虚拟制作场景中，为LED墙创建动态的、高保真的3D文字元素。
-   **动态设计与包装**：为电视节目、电影片头或广告制作具有复杂动画效果的3D文字。
-   **游戏UI与HUD**：在需要立体感或特殊视觉效果的游戏界面中使用3D文本。
-   **产品可视化与标注**：在3D产品模型或建筑场景中添加信息性的3D文字标注。
-   **任何需要高性能、可定制3D文本的UE项目**：该插件默认关闭（`Installed=false`），适合对3D文本有高级需求的项目主动启用。

## 蓝图用法

所有核心功能通过 `UText3DComponent` 及其关联的扩展对象暴露给蓝图。

### 核心节点

**文本与字体控制 (UText3DComponent)**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Text` | 设置要显示的文本内容 | `UText3DComponent` |
| `Set Font` | 设置文本使用的字体 | `UText3DComponent` |
| `Set Typeface` | 设置字体的字面（如 Bold, Italic） | `UText3DComponent` |
| `Set Font Size` | 设置字体大小 | `UText3DComponent` |
| `Set Enforce Upper Case` | 强制所有字母大写 | `UText3DComponent` |

**几何形状控制 (UText3DDefaultGeometryExtension)**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Extrude` | 设置文本的挤出深度 | `UText3DDefaultGeometryExtension` |
| `Set Bevel` / `Set Bevel Type` / `Set Bevel Segments` | 设置斜角大小、形状和细分 | `UText3DDefaultGeometryExtension` |
| `Set Use Outline` / `Set Outline` / `Set Outline Type` | 启用/禁用描边，设置描边宽度和类型 | `UText3DDefaultGeometryExtension` |
| `Set Collision Enabled` | 设置文本碰撞体的类型 | `UText3DDefaultGeometryExtension` |

**材质控制 (UText3DDefaultMaterialExtension)**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Style` | 设置材质风格（实色、渐变、纹理、自定义） | `UText3DDefaultMaterialExtension` |
| `Set Front Color` / `Set Back Color` 等 | 设置文本各面（正面、背面、挤出面、斜角面）的颜色 | `UText3DDefaultMaterialExtension` |
| `Set Gradient Color A` / `Set Gradient Color B` 等 | 设置渐变材质的颜色、平滑度、偏移和旋转 | `UText3DDefaultMaterialExtension` |
| `Set Texture Asset` / `Set Texture Tiling` | 设置纹理材质使用的纹理资产和平铺 | `UText3DDefaultMaterialExtension` |
| `Set Blend Mode` / `Set Opacity` / `Set Is Unlit` | 设置混合模式、不透明度和是否无光照 | `UText3DDefaultMaterialExtension` |
| `Set Front Material` / `Set Back Material` 等 | 为文本各面指定完全自定义的材质实例 | `UText3DDefaultMaterialExtension` |

**布局控制 (UText3DDefaultLayoutExtension)**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Horizontal Alignment` / `Set Vertical Alignment` | 设置文本的水平和垂直对齐方式 | `UText3DDefaultLayoutExtension` |
| `Set Tracking` / `Set Line Spacing` / `Set Word Spacing` | 设置字距、行距和词间距 | `UText3DDefaultLayoutExtension` |
| `Set Use Max Width` / `Set Max Width` / `Set Max Width Behavior` | 启用最大宽度限制，并设置限制值和超限行为（缩放或换行后缩放） | `UText3DDefaultLayoutExtension` |
| `Set Use Max Height` / `Set Max Height` | 启用最大高度限制 | `UText3DDefaultLayoutExtension` |

**逐字符效果 (UText3DLayoutTransformEffect)**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Location Enabled` / `Set Location Progress` / `Set Location Begin` / `Set Location End` 等 | 控制每个字符的位置动画效果 | `UText3DLayoutTransformEffect` |
| `Set Rotation Enabled` / `Set Rotation Progress` / `Set Rotation Begin` / `Set Rotation End` 等 | 控制每个字符的旋转动画效果 | `UText3DLayoutTransformEffect` |
| `Set Scale Enabled` / `Set Scale Progress` / `Set Scale Begin` / `Set Scale End` 等 | 控制每个字符的缩放动画效果 | `UText3DLayoutTransformEffect` |

### 使用示例（蓝图描述）

1.  **创建基础3D文本**：
    -   在场景中放置一个 `Text3DComponent`。
    -   通过 `Set Text` 节点设置内容为 “Hello 3D World”。
    -   通过 `Set Font` 和 `Set Typeface` 选择一个包含中文字体的字体。
    -   通过 `Set Extrude` 和 `Set Bevel` 节点赋予其3D厚度和倒角。

2.  **应用材质与效果**：
    -   获取组件的 `MaterialExtension` (类型为 `UText3DDefaultMaterialExtension`)。
    -   调用 `Set Style` 设置为 `Gradient`。
    -   调用 `Set Gradient Color A` 和 `Set Gradient Color B` 设置渐变色。
    -   获取组件的 `LayoutExtension` (类型为 `UText3DDefaultLayoutExtension`)。
    -   调用 `Set Horizontal Alignment` 设置为 `Center`。

3.  **制作打字机动画**：
    -   获取或创建组件的 `LayoutEffects`，添加一个 `UText3DLayoutTransformEffect` 实例。
    -   启用位置效果 (`Set Location Enabled`)。
    -   将 `Set Location Progress` 动画参数从0变化到100，并配合 `Set Location Order` 设置为 `Normal` (从左到右)，即可实现逐个字符出现的效果。

## C++ 用法

### 头文件引入

```cpp
#include "Text3DComponent.h"
#include "Extensions/Text3DDefaultMaterialExtension.h"
#include "Extensions/Text3DDefaultGeometryExtension.h"
#include "Extensions/Text3DDefaultLayoutExtension.h"
#include "Extensions/Text3DLayoutTransformEffect.h"
```

### 基本用法

创建和配置一个 `UText3DComponent`。
(来源：基于 `UText3DComponent` 及扩展类的公共API综合)

```cpp
// 在Actor中创建Text3DComponent
UText3DComponent* Text3DComp = NewObject<UText3DComponent>(MyActor);
Text3DComp->RegisterComponent();
Text3DComp->AttachToComponent(MyActor->GetRootComponent(), FAttachmentTransformRules::KeepRelativeTransform);

// 设置文本和字体
Text3DComp->SetText(FText::FromString(TEXT("UE5 Text3D")));
Text3DComp->SetFontSize(120.0f);

// 配置几何形状 (通过默认几何扩展)
UText3DDefaultGeometryExtension* GeometryExt = Text3DComp->GetDefaultGeometryExtension();
if (GeometryExt)
{
    GeometryExt->SetExtrude(20.0f);
    GeometryExt->SetBevel(5.0f);
    GeometryExt->SetBevelType(EText3DBevelType::Convex);
    GeometryExt->SetBevelSegments(8);
    GeometryExt->SetUseOutline(false);
}

// 配置材质 (通过默认材质扩展)
UText3DDefaultMaterialExtension* MaterialExt = Text3DComp->GetDefaultMaterialExtension();
if (MaterialExt)
{
    MaterialExt->SetStyle(EText3DMaterialStyle::Gradient);
    MaterialExt->SetGradientColorA(FLinearColor::Blue);
    MaterialExt->SetGradientColorB(FLinearColor::Cyan);
    MaterialExt->SetGradientSmoothness(0.5f);
}
```

### 进阶用法

创建一个自定义的渲染器（Renderer）或扩展（Extension）。
(来源：`UText3DRendererBase`, `UText3DExtensionBase` 的派生类结构)

```cpp
// 1. 自定义渲染器（继承 UText3DRendererBase）
UCLASS()
class UMyCustomText3DRenderer : public UText3DRendererBase
{
    GENERATED_BODY()

protected:
    virtual void OnCreate() override { /* 创建自定义渲染组件 */ }
    virtual void OnUpdate(const UE::Text3D::Renderer::FUpdateParameters& InParameters) override { /* 更新逻辑 */ }
    virtual void OnClear() override { /* 清除渲染状态 */ }
    virtual void OnDestroy() override { /* 销毁资源 */ }
    virtual EText3DMeshType GetMeshType() const override { return EText3DMeshType::Static; }
    virtual FName GetFriendlyName() const override { return TEXT("MyCustomRenderer"); }
    virtual FBox OnCalculateBounds() const override { /* 返回自定义包围盒 */ }
    // ... 其他纯虚函数实现
};

// 2. 自定义效果扩展（继承 UText3DLayoutEffectBase）
UCLASS()
class UMyCustomText3DEffect : public UText3DLayoutEffectBase
{
    GENERATED_BODY()

protected:
    // 重写效果应用逻辑
    virtual void ApplyEffect(uint32 InGlyphIndex, uint32 InGlyphCount) override
    {
        // 根据InGlyphIndex和InGlyphCount，对每个字符的变换进行自定义计算
        UText3DCharacterBase* Character = /* ... */;
        if (Character)
        {
            FVector NewLocation = /* 自定义位置计算 */;
            Character->SetRelativeLocation(NewLocation);
        }
    }
    virtual FText3DRange GetTargetRange() const override { return FText3DRange(0, 10); } // 只影响前10个字符
};
```

## Demo 示例

一个最小化的可编译示例，创建一个带有自定义动画的3D文本Actor。

### MyText3DActor.h
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "MyText3DActor.generated.h"

class UText3DComponent;
class UText3DLayoutTransformEffect;

UCLASS()
class AMyText3DActor : public AActor
{
    GENERATED_BODY()

public:
    AMyText3DActor();

protected:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

    UPROPERTY(VisibleAnywhere)
    UText3DComponent* Text3DComponent;

    UPROPERTY()
    UText3DLayoutTransformEffect* TransformEffect;

    UPROPERTY(EditAnywhere, Category="Animation")
    float AnimationSpeed = 1.0f;

    float CurrentProgress = 0.0f;
};
```

### MyText3DActor.cpp
```cpp
#include "MyText3DActor.h"
#include "Text3DComponent.h"
#include "Extensions/Text3DLayoutTransformEffect.h"
#include "Extensions/Text3DDefaultGeometryExtension.h"
#include "Extensions/Text3DDefaultMaterialExtension.h"

AMyText3DActor::AMyText3DActor()
{
    PrimaryActorTick.bCanEverTick = true;

    Text3DComponent = CreateDefaultSubobject<UText3DComponent>(TEXT("Text3D"));
    RootComponent = Text3DComponent;
}

void AMyText3DActor::BeginPlay()
{
    Super::BeginPlay();

    // 配置文本
    Text3DComponent->SetText(FText::FromString(TEXT("Dynamic Text")));
    Text3DComponent->SetFontSize(100.0f);

    // 配置几何
    auto* GeomExt = Text3DComponent->GetDefaultGeometryExtension();
    if (GeomExt)
    {
        GeomExt->SetExtrude(15.0f);
        GeomExt->SetBevel(3.0f);
    }

    // 配置材质
    auto* MatExt = Text3DComponent->GetDefaultMaterialExtension();
    if (MatExt)
    {
        MatExt->SetStyle(EText3DMaterialStyle::Solid);
        MatExt->SetFrontColor(FLinearColor::Green);
    }

    // 添加并配置动画扩展
    TransformEffect = NewObject<UText3DLayoutTransformEffect>(Text3DComponent);
    Text3DComponent->AddLayoutEffect(TransformEffect);

    TransformEffect->SetScaleEnabled(true);
    TransformEffect->SetScaleProgress(0.0f);
    TransformEffect->SetScaleBegin(FVector(0.1f));
    TransformEffect->SetScaleEnd(FVector(1.0f));
    TransformEffect->SetScaleOrder(EText3DCharacterEffectOrder::Normal);
    TransformEffect->SetScaleStagger(true); // 错开效果
}

void AMyText3DActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    // 更新动画进度
    CurrentProgress += DeltaTime * AnimationSpeed;
    if (CurrentProgress > 1.0f)
    {
        CurrentProgress -= 1.0f; // 循环动画
    }

    // 应用进度到扩展
    if (TransformEffect)
    {
        TransformEffect->SetScaleProgress(CurrentProgress * 100.0f); // Progress范围是0-100
    }
}
```

## 模块依赖

本插件依赖以下非标准核心模块：

| 模块 | 用途 |
|---|---|
| `FreeType2` | 用于解析字体文件（如 .ttf, .otf）并获取字形轮廓数据 |
| `HarfBuzz` | 用于复杂的文本整形（Text Shaping），处理连字、双向文本等 |
| `MeshMergeUtilities` | 可能用于编辑器内将多个静态网格体合并的工具 |
| `UnrealEd` | 提供编辑器专用功能（仅 Text3D 模块依赖，用于特定子系统） |
| `DirectX` | 可能用于编辑器模块（Text3DEditor）中的某些图形相关功能 |
| `GeometryProcessing` | 提供几何处理算法，可能用于字形网格的生成或优化 |
| `GeometryScripting` | 提供蓝图可用的几何操作脚本接口 |
| `GeometryMask` | 插件依赖其材质相关功能 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `660d059d` | Text3D: Text3D relies on GeometryMask for its material functions (content-only dependency). As there... | 文本3D的材质功能现在依赖于几何遮罩插件（仅内容依赖）。 |
| 2026-05-22 | `f3f717af` | Text3D: fix build errors when building with server (no free type) | 修复了在服务器构建（不含FreeType）时的编译错误。 |
| 2026-05-21 | `14da3adf` | Text3D: fixed issue where in the exact timing where preparation of Text3D only held onto new glyph h... | 修复了在特定时序下，Text3D准备阶段仅保留新字形句柄可能导致的错误。 |
| 2026-05-15 | `2f367c6e` | Text3D: fix function defined in editor-only | 修复了仅在编辑器中定义的函数。 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 动态设计：新增项目设置，可强制禁用Text3D和形状的碰撞。 |

### 维护评价

- **创建时间**：插件于2025年9月从实验性（Experimental）状态正式迁移到虚拟制作（VirtualProduction）类别，是一个相对年轻的插件。
- **近期活动**：最近一个月（2026年5月）有多次提交，集中在**bug修复、构建兼容性优化和依赖关系调整**上，表明插件正在积极维护和稳定化。
- **维护状态**：**活跃维护中**。插件已经脱离实验阶段，进入了正式的虚拟制作工具链，近期更新专注于提高稳定性和兼容性。
- **已知限制**：依赖 FreeType 和 HarfBuzz，可能增加项目包体大小；高性能场景下需注意字形缓存的内存管理。
- **推荐使用**：**推荐**。对于需要高质量、可定制化3D文本，特别是虚拟制作、动态设计领域的项目，Text3D是一个强大且设计良好的官方解决方案。由于其默认未启用，适合有明确需求的项目集成。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Text3D)
- 官方文档 (`.uplugin` 中的 `DocsURL` 为空)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Text3D/Tests) (推测路径，实际测试文件位置需根据项目结构确认)