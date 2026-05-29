# Image Plate

> Actor and component types that provide a camera-aligned image plate

| 属性 | 值 |
|---|---|
| 中文名 | 图像板 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产工厂） |
| 模块 | `ImagePlate` (Runtime), `ImagePlateEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2017-07-13 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ImagePlate) | |

## 用途
Image Plate 插件提供了一种在虚幻引擎场景中显示 2D 图像或图像序列的方法，该图像板能够自动对齐并跟随摄像机，使其始终面向观众。这主要用于电影虚拟制作和后期合成领域，例如将渲染出的虚拟背景、特效素材或特定参考图像作为场景中的一个平面对象，由摄像机视角驱动其位置和朝向，为虚拟摄影棚提供动态背景或合成元素。

## 使用场景
- **电影虚拟制作**：在 LED 墙或绿幕前，将预先渲染好的 3D 环境作为动态背景板，跟随摄像机移动，创造无缝的虚拟拍摄效果。
- **建筑可视化**：快速渲染一个项目的特定视角作为 2D 图像，然后将其放入更大的场景中进行灯光和氛围测试，而无需完整建模。
- **2D 背景替换**：在游戏中或实时渲染中，需要展示一个固定视角的 2D 背景（如海报、监控屏幕画面）时，可以使用此组件并保持它在屏幕上正确的位置。

## 蓝图用法
该插件的核心功能通过 `UImagePlateComponent` 提供，它继承自 `UMeshComponent`，允许你在场景中创建一个与摄像机对齐的平面。

### 核心节点
| 节点 | 说明 | 所在类 |
|---|---|---|
| `Image Plate Component` | 创建一个图像板组件，用于显示材质。 | `UImagePlateComponent` |

### 使用示例（蓝图描述）
1.  **创建与配置**：在 Actor（如 `AImagePlate` 或任何其他 Actor）上添加一个 `Image Plate Component` 组件。
2.  **设置材质**：为该组件指定一个材质实例。该材质通常需要将 `Texture` 参数设置为你想要显示的图像或纹理。
3.  **调整属性**：在组件的细节面板中，你可以调整：
    - `Material`: 用于渲染图像板的材质。
    - `Size`: 图像板的物理尺寸（宽度和高度）。
    - `UV Range`: 控制材质在图像板上的映射范围。
4.  **运行时**：当场景中有摄像机时，图像板会自动面向并跟随摄像机，实现“摄像机对齐”的效果。

## C++ 用法
### 头文件引入
```cpp
#include "ImagePlateComponent.h"
```

### 基本用法
通过代码创建并配置一个 `UImagePlateComponent`。
（基于对组件头文件 `UImagePlateComponent` 中暴露的 `UPROPERTY` 的分析）
```cpp
// 假设你在一个 Actor 的构造函数或初始化函数中
AMyActor::AMyActor()
{
    // 创建图像板组件
    UImagePlateComponent* PlateComp = CreateDefaultSubobject<UImagePlateComponent>(TEXT("ImagePlate"));

    // 设置材质（需要在材质编辑器中创建合适的材质资产）
    static ConstructorHelpers::FObjectFinder<UMaterial> MaterialAsset(TEXT("/Game/Materials/M_ImagePlate"));
    if (MaterialAsset.Succeeded())
    {
        PlateComp->SetMaterial(0, MaterialAsset.Object);
    }

    // 设置图像板尺寸 (宽度， 高度)
    PlateComp->SetSize(FVector2D(1000.0f, 500.0f));

    // 可选：设置UV范围
    PlateComp->SetUVRange(FBox2D(FVector2D(0.0f, 0.0f), FVector2D(1.0f, 1.0f)));
}
```

### 进阶用法
结合 `UImagePlateFileSequence` 资产（通过 `ImagePlateEditor` 模块提供的工厂创建）来播放图像序列。
```cpp
// 假设你有一个 UImagePlateFileSequence 资产
UImagePlateFileSequence* FileSequence = ...;

// 创建动态材质实例以便运行时修改
UMaterialInstanceDynamic* DynamicMaterial = UMaterialInstanceDynamic::Create(PlateComp->GetMaterial(0), this);
PlateComp->SetMaterial(0, DynamicMaterial);

// 在 Tick 中更新纹理参数，假设你的材质有一个名为 "SequenceTexture" 的纹理参数
if (FileSequence && DynamicMaterial)
{
    // 伪代码：根据当前帧或时间从 FileSequence 获取对应的纹理
    UTexture2D* CurrentFrameTexture = FileSequence->GetTextureForFrame(CurrentFrameIndex);
    if (CurrentFrameTexture)
    {
        DynamicMaterial->SetTextureParameterValue("SequenceTexture", CurrentFrameTexture);
    }
}
```

## Demo 示例
一个最小的可编译 Actor 示例，该 Actor 持有一个图像板组件。

**ImagePlateDemoActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ImagePlateDemoActor.generated.h"

class UImagePlateComponent;
class UMaterialInterface;

UCLASS()
class AImagePlateDemoActor : public AActor
{
    GENERATED_BODY()

public:
    AImagePlateDemoActor();

protected:
    virtual void BeginPlay() override;

public:
    // 图像板组件
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Image Plate")
    UImagePlateComponent* ImagePlateComponent;

    // 要应用的材质
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Image Plate")
    UMaterialInterface* PlateMaterial;
};
```

**ImagePlateDemoActor.cpp**
```cpp
#include "ImagePlateDemoActor.h"
#include "ImagePlateComponent.h"

AImagePlateDemoActor::AImagePlateDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;

    // 创建并附加图像板组件
    ImagePlateComponent = CreateDefaultSubobject<UImagePlateComponent>(TEXT("ImagePlate"));
    RootComponent = ImagePlateComponent;

    // 默认尺寸
    ImagePlateComponent->SetSize(FVector2D(500.f, 280.f));
}

void AImagePlateDemoActor::BeginPlay()
{
    Super::BeginPlay();

    // 如果指定了材质，则应用
    if (PlateMaterial)
    {
        ImagePlateComponent->SetMaterial(0, PlateMaterial);
    }
}
```

## 模块依赖
你的项目模块需要依赖以下模块才能使用 Image Plate 的功能：

| 模块 | 用途 |
|---|---|
| `RenderCore` | 核心渲染功能，用于处理纹理和材质。 |
| `RHI` | 渲染硬件接口，底层渲染资源管理。 |
| `MediaAssets` | 媒体资产支持，用于处理图像序列等媒体文件。 |
| `ImagePlate` | 本插件的运行时模块，提供 `UImagePlateComponent` 核心类。 |
| `ImagePlateEditor` | 本插件的编辑器模块，提供资产定义和工厂，用于创建 `UImagePlateFileSequence` 等资产。 |

## 维护状态

### 近期更新
| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `8d566979` | [ContentBrowser] New Add Menu Media Menu | 在内容浏览器的“添加”菜单中整合了“媒体”子菜单。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式日志宏 UE_LOG 迁移至新式 UE_LOGF。 |
| 2026-03-25 | `d59d85d1` | [HWRT] Fix crash when UImagePlateComponent doesn't have a valid material assigned. | 修复了当图像板组件没有有效材质时，硬件光线追踪会导致的崩溃。 |
| 2026-02-06 | `af701dad` | [HWRT] Deprecate public FRayTracingGeometry Initializer. | 废弃了公开的 FRayTracingGeometry 初始化器，可能影响与光线追踪几何体相关的底层代码。 |
| 2025-10-08 | `018dadd6` | Changing a number of places that use implicit command lists to instead use the one already available | 重构了多处代码，将使用隐式命令列表改为使用已有的命令列表。 |

### 维护评价
该插件自 2017 年创建以来已有约 7 年历史，属于**实验性**且**默认未启用**的插件。从近期 git 历史看，它**仍在维护中**，但更新主要集中在**底层渲染重构**（如光线追踪修复、日志宏迁移、命令列表优化）和**编辑器集成优化**（内容浏览器菜单），并未增加新的核心功能。考虑到其实验性状态和长期未有重大功能更新，建议在生产环境中**谨慎使用**。它适用于需要特定摄像机对齐图像板功能的项目，但需要自行承担其实验性带来的风险。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ImagePlate)
- 官方文档（无）
- [测试用例]（未在插件目录内发现标准测试文件）