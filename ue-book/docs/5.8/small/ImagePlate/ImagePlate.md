# Image Plate

> Actor and component types that provide a camera-aligned image plate

| 属性 | 值 |
|---|---|
| 中文名 | 图像板 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ImagePlate` (Runtime), `ImagePlateEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2017-07-13 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ImagePlate) | |

## 用途

Image Plate 插件旨在为 Unreal Engine 提供一个**始终面向相机的 2D 图像显示板**，其主要用途是**在 3D 场景中实时合成 2D 图像或图像序列**。这与传统的“摄像机映射”或“动态遮罩”技术类似，但该插件提供了更集成、更适合影视后期和虚拟制片的工作流程。核心功能是将一个 2D 图像（或一系列图像）作为一个图层无缝地叠加在 3D 场景的特定深度位置上，并能根据相机的镜头参数（如焦距、胶片背）自动缩放以匹配视口。它是为了解决**虚拟制片、影视后期合成以及需要在 3D 世界中动态呈现渲染图像或背景板**的问题而存在的。

## 使用场景

- **虚拟制片 (Virtual Production)**：在 LED 墙上显示实时渲染的 CG 背景，或者在 3D 场景中插入一个预先渲染好的背景板。
- **影视后期合成**：在场景中放置一个“动态遮罩”（Holdout Matte），用于在渲染时正确遮挡前景物体，简化合成流程。
- **CG 合成与预览**：在视口中实时预览渲染好的图像序列与当前 3D 场景的结合效果。
- **创建始终面向摄影机的 UI 或信息板**：在 3D 空间中展示需要一直正对相机的 2D 图像信息。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Image Plate` | 为组件设置图像板参数（材质、尺寸模式等） | `UImagePlateComponent` |
| `Get Plate` | 获取当前组件设置的图像板参数 | `UImagePlateComponent` |
| `Find View Target` | 查找此图像板组件所面向的目标视图 Actor | `UImagePlateComponent` |

### 使用示例（蓝图描述）

1.  **创建与基本设置**：
    *   在蓝图中，从“组件”面板添加一个 `Image Plate Component` 到你的 Actor（或直接使用 `AImagePlate` Actor）。
    *   在组件的“细节”面板中，设置 `Image Plate` 类别的属性。通常先勾选 `Fill Screen`，让图像板自动匹配视口大小。
    *   通过 `Set Image Plate` 节点，可以动态地更改图像板的材质 (`Material`)、填充量 (`FillScreenAmount`) 或固定尺寸 (`FixedSize`)。

2.  **与媒体源配合**：
    *   使用媒体框架（Media Framework）加载图像序列或视频。
    *   将媒体纹理输出连接到 `Set Image Plate` 节点的 `Plate` 参数中对应的纹理输入，或者通过材质实例 (`DynamicMaterial`) 将媒体纹理参数化传递给图像板材质。

## C++ 用法

### 头文件引入

```cpp
#include "ImagePlateComponent.h"
// 如果需要使用文件序列功能
#include "ImagePlateFileSequence.h"
```

### 基本用法

以下代码演示如何在 C++ 中为一个 Actor 创建并配置一个 Image Plate 组件。

```cpp
// 假设在你的 AMyActor::BeginPlay() 或类似初始化函数中
// 添加组件
UImagePlateComponent* ImagePlateComp = NewObject<UImagePlateComponent>(this);
ImagePlateComp->SetupAttachment(RootComponent);
ImagePlateComp->RegisterComponent();

// 创建并设置图像板参数
FImagePlateParameters PlateParams;
PlateParams.bFillScreen = true; // 让板子填充屏幕
PlateParams.FillScreenAmount = FVector2D(1.0f, 1.0f); // 完全填充

// 设置一个材质 (需要在编辑器中预先准备一个接受纹理参数的材质资产)
static ConstructorHelpers::FObjectFinder<UMaterialInterface> PlateMatFinder(
    TEXT("/Game/Materials/M_ImagePlate"));
if (PlateMatFinder.Succeeded())
{
    PlateParams.Material = PlateMatFinder.Object;
    PlateParams.TextureParameterName = TEXT("RenderTexture"); // 材质中纹理参数的名称
}

// 应用参数
ImagePlateComp->SetImagePlate(PlateParams);
```

### 进阶用法

结合 `UImagePlateFileSequence` 和异步缓存 (`FImagePlateAsyncCache`) 来加载和播放一个图像序列。

```cpp
// 创建一个文件序列对象
UImagePlateFileSequence* Sequence = NewObject<UImagePlateFileSequence>();
Sequence->SequencePath.Path = TEXT("/Game/ImageSequences/BG_Sequence"); // 图像序列目录
Sequence->FileWildcard = TEXT("*.exr"); // 图像文件通配符
Sequence->Framerate = 24.0f; // 播放帧率

// 创建异步缓存
FImagePlateAsyncCache AsyncCache = Sequence->GetAsyncCache();

// 在游戏线程 Tick 或需要新帧时，请求特定时间的帧
float CurrentTimeSeconds = GetWorld()->GetTimeSeconds();
int32 LeadingFrames = 5;  // 预缓存前5帧
int32 TrailingFrames = 2; // 保留后2帧

TSharedFuture<FImagePlateSourceFrame> FutureFrame = AsyncCache.RequestFrame(
    CurrentTimeSeconds, LeadingFrames, TrailingFrames);

// 可以轮询 FutureFrame->IsReady() 或在完成后回调处理 FImagePlateSourceFrame
// 然后可以将 SourceFrame 中的纹理数据拷贝到渲染目标或材质实例上。
// 注意：这通常需要在渲染线程上完成，需谨慎处理多线程问题。
```

## Demo 示例

**ImagePlateDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ImagePlateDemo.generated.h"

class UImagePlateComponent;

UCLASS()
class AImagePlateDemo : public AActor
{
	GENERATED_BODY()

public:
	AImagePlateDemo();

protected:
	virtual void BeginPlay() override;

public:
	virtual void Tick(float DeltaTime) override;

private:
	UPROPERTY(VisibleAnywhere)
	TObjectPtr<UImagePlateComponent> ImagePlateComponent;

	// 用于动态更新的媒体纹理示例
	UPROPERTY(EditAnywhere, Category = "Demo")
	TObjectPtr<UTexture> DynamicSourceTexture;
};
```

**ImagePlateDemo.cpp**
```cpp
#include "ImagePlateDemo.h"
#include "ImagePlateComponent.h"

AImagePlateDemo::AImagePlateDemo()
{
	PrimaryActorTick.bCanEverTick = true;
	RootComponent = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));

	ImagePlateComponent = CreateDefaultSubobject<UImagePlateComponent>(TEXT("ImagePlate"));
	ImagePlateComponent->SetupAttachment(RootComponent);
}

void AImagePlateDemo::BeginPlay()
{
	Super::BeginPlay();

	if (ImagePlateComponent)
	{
		FImagePlateParameters Params = ImagePlateComponent->GetPlate();
		Params.bFillScreen = false;
		Params.FixedSize = FVector2D(1920, 1080); // 设置为 1920x1080 的固定尺寸
		// 注意：这里需要确保 Material 已经在组件的细节面板或通过蓝图设置
		ImagePlateComponent->SetImagePlate(Params);
	}
}

void AImagePlateDemo::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	// 示例：动态更换纹理源（例如，从媒体纹理更新）
	if (DynamicSourceTexture && ImagePlateComponent)
	{
		FImagePlateParameters Params = ImagePlateComponent->GetPlate();
		if (Params.DynamicMaterial && Params.RenderTexture != DynamicSourceTexture)
		{
			Params.DynamicMaterial->SetTextureParameterValue(Params.TextureParameterName, DynamicSourceTexture);
			// 注意：通常不需要手动设置 RenderTexture，它由媒体系统管理
		}
	}
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MediaUtils` | 提供媒体框架集成和图像序列异步加载功能 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `8d566979` | [ContentBrowser] New Add Menu Media Menu | 为内容浏览器添加了新的媒体菜单选项。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏 UE_LOG 迁移为新版 UE_LOGF。 |
| 2026-03-25 | `d59d85d1` | [HWRT] Fix crash when UImagePlateComponent doesn't have a valid material assigned. | 修复了硬件光线追踪模式下，当图像板组件未分配有效材质时可能导致的崩溃。 |
| 2026-02-06 | `af701dad` | [HWRT] Deprecate public FRayTracingGeometry Initializer. | 标记废弃了公开的 FRayTracingGeometry 初始化器。 |
| 2025-10-08 | `018dadd6` | Changing a number of places that use implicit command lists to instead use the one already available | 将多处使用隐式命令列表的代码改为使用已有可用的命令列表，提升代码一致性。 |

### 维护评价

该插件虽然被标记为**实验性 (Beta)** 且 **默认未启用**，但从 Git 提交记录来看，**维护状态非常活跃**。最近的更新（2025-10 至 2026-04）涉及功能扩展（内容浏览器集成）、Bug 修复（崩溃问题）和底层渲染代码优化（命令列表、光线追踪），表明 Epic 仍在积极维护并将其作为虚拟制片和高级渲染功能的一部分进行迭代。尽管它被归类在 `Experimental` 文件夹下，且已有 9 年历史，但近期实质性更新频繁，**推荐在虚拟制片或高级合成项目中评估使用**。需注意其 API 可能仍在演进中。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ImagePlate)
- [官方文档](https://docs.unrealengine.com/) (可于 Unreal Engine 官方文档中搜索 “Image Plate” 或 “Virtual Production”)