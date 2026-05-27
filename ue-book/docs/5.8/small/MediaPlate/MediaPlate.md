# Media Plate

> Actor that can play media.

| 属性 | 值 |
|---|---|
| 中文名 | 媒体板 |
| 分类 | Media |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（材质模板、蓝图资产） |
| 模块 | `MediaPlate` (Runtime), `MediaPlateEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-01-27 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaPlate) | |

## 用途

Media Plate 插件提供了一个优化的、功能完备的媒体播放器Actor，用于在游戏世界中展示视频、图片序列（如EXR序列）等媒体内容。它封装了媒体播放器（MediaPlayer）、媒体纹理（MediaTexture）和材质实例的创建与管理，提供了一套完整的蓝图API，用于控制媒体的打开、播放、暂停、跳转、循环等行为。其核心优势在于对EXR等大分辨率图片序列的高效处理，支持Mip级别的平铺加载与优化渲染，特别适合需要播放高分辨率媒体内容（如全息投影、电影屏幕、环境映射球体）的交互式应用和影视虚拟制片场景。

## 使用场景

- 你需要在虚拟制片场景中播放高清视频或EXR图片序列作为屏幕内容。
- 你需要一个易于控制、支持多种媒体源（资产、外部文件、播放列表）且性能优化的媒体播放器Actor。
- 你需要在球体网格上播放全景视频或环境贴图，并支持基于视角的Mip优化加载。
- 你需要通过蓝图或Sequencer精确控制媒体的播放状态和属性。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open` | 打开媒体资源。这是播放前的必要步骤。 | `UMediaPlateComponent` |
| `Play` | 以正常速度（速率1.0）向前播放。 | `UMediaPlateComponent` |
| `PlayReverse` | 以正常速度（速率-1.0）倒放。 | `UMediaPlateComponent` |
| `Pause` | 暂停播放。 | `UMediaPlateComponent` |
| `Close` | 关闭当前打开的媒体资源。 | `UMediaPlateComponent` |
| `Seek` | 跳转到指定的播放时间点。 | `UMediaPlateComponent` |
| `Rewind` | 回到媒体的起始位置。 | `UMediaPlateComponent` |
| `Next` / `Previous` | 播放播放列表中的下一个/上一个媒体。 | `UMediaPlateComponent` |
| `GetMediaPlayer` | 获取底层的媒体播放器对象。 | `UMediaPlateComponent` |
| `GetMediaTexture` | 获取用于显示媒体的媒体纹理。 | `UMediaPlateComponent` |
| `SelectMediaSourceAsset` | 选择一个媒体源资产作为播放内容。 | `UMediaPlateComponent` |
| `SelectExternalMedia` | 选择一个外部文件路径（非UE资产）作为播放内容。 | `UMediaPlateComponent` |
| `SelectMediaPlaylistAsset` | 选择一个媒体播放列表资产。 | `UMediaPlateComponent` |
| `SetLoop` | 设置是否循环播放。 | `UMediaPlateComponent` |
| `SetEnableAudio` | 启用或禁用音频播放。 | `UMediaPlateComponent` |
| `SetPlayOnlyWhenVisible` | 设置是否仅在媒体板可见时才播放。 | `UMediaPlateComponent` |
| `SetIsAspectRatioAuto` | 设置是否自动根据媒体调整网格体的宽高比。 | `UMediaPlateComponent` |
| `IsMediaPlatePlaying` | 检查媒体板是否正在播放。 | `UMediaPlateComponent` |
| `IsEventStateChangeAllowed` | 检查是否允许切换到指定的事件状态（如播放、打开等）。 | `UMediaPlateComponent` |

### 使用示例（蓝图描述）

1.  **播放一个媒体源资产**：在蓝图中获取你的MediaPlate Actor，调用 `Select Media Source Asset` 节点并选择一个 `UMediaSource` 资产，然后依次调用 `Open` 和 `Play` 节点。
2.  **制作一个自动播放的循环视频墙**：在MediaPlate Actor的细节面板中，勾选 `Auto Play` 和 `Loop`，并为其静态网格体组件赋予正确的材质。将视频或图片序列资源赋予 `MediaPlateResource` 属性即可。
3.  **通过事件控制播放**：使用 `Is Media Plate Playing` 节点检查状态，或使用 `Is Event State Change Allowed` 节点检查能否执行某个操作（如切换到播放状态），然后根据结果调用相应节点。

## C++ 用法

### 头文件引入

```cpp
#include "MediaPlateComponent.h"
#include "MediaPlate.h"
#include "MediaPlateResource.h"
```

### 基本用法

**代码示例：获取并控制一个MediaPlate组件**

```cpp
// 假设我们已经有一个指向AMediaPlateActor的指针 MediaPlateActor
if (AMediaPlate* MediaPlateActor = /* ... */)
{
    UMediaPlateComponent* MediaPlateComp = MediaPlateActor->MediaPlateComponent;
    if (MediaPlateComp)
    {
        // 1. 打开并播放一个媒体源资产
        UMediaSource* MySource = /* ... */;
        MediaPlateComp->SelectMediaSourceAsset(MySource);
        MediaPlateComp->Open();
        MediaPlateComp->Play();

        // 2. 2秒后暂停
        FTimerHandle TimerHandle;
        GetWorld()->GetTimerManager().SetTimer(TimerHandle, [MediaPlateComp]()
        {
            MediaPlateComp->Pause();
        }, 2.0f, false);

        // 3. 检查播放状态
        if (MediaPlateComp->IsMediaPlatePlaying())
        {
            UE_LOG(LogTemp, Log, TEXT("Media Plate is playing."));
        }

        // 4. 关闭媒体
        MediaPlateComp->Close();
    }
}
```

### 进阶用法

**代码示例：使用延迟动作（Latent Action）打开媒体并等待纹理就绪**

```cpp
// 在蓝图函数库或某个UObject中
void UMyBlueprintFunctionLibrary::OpenMediaPlateLatent(AActor* MediaPlateActor, FLatentActionInfo LatentInfo, float Timeout, bool& bSuccess)
{
    if (AMediaPlate* MediaPlate = Cast<AMediaPlate>(MediaPlateActor))
    {
        UMediaPlateComponent* Comp = MediaPlate->MediaPlateComponent;
        if (Comp)
        {
            // 调用延迟版本的Open，它会等待媒体打开并（可选）等待纹理渲染样本
            Comp->OpenLatent(MediaPlate, LatentInfo, Timeout, /*bInWaitForTexture=*/true, bSuccess);
        }
    }
}
```

## Demo 示例

**MediaPlateDemoActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MediaPlateDemoActor.generated.h"

class AMediaPlate;
class UMediaSource;

UCLASS()
class AMyMediaPlateDemoActor : public AActor
{
	GENERATED_BODY()
	
public:	
	AMyMediaPlateDemoActor();

protected:
	virtual void BeginPlay() override;

public:	
	virtual void Tick(float DeltaTime) override;

	/** 在编辑器中指定一个媒体源资产 */
	UPROPERTY(EditAnywhere, Category = "Demo")
	TObjectPtr<UMediaSource> MediaSourceToPlay;

	/** 在场景中放置的MediaPlate Actor */
	UPROPERTY(EditAnywhere, Category = "Demo")
	TObjectPtr<AMediaPlate> TargetMediaPlate;
};
```

**MediaPlateDemoActor.cpp**
```cpp
#include "MediaPlateDemoActor.h"
#include "MediaPlate.h"
#include "MediaPlateComponent.h"
#include "MediaSource.h"

AMyMediaPlateDemoActor::AMyMediaPlateDemoActor()
{
	PrimaryActorTick.bCanEverTick = true;
}

void AMyMediaPlateDemoActor::BeginPlay()
{
	Super::BeginPlay();

	// 检查目标MediaPlate是否有效
	if (TargetMediaPlate && MediaSourceToPlay)
	{
		UMediaPlateComponent* MediaComp = TargetMediaPlate->MediaPlateComponent;
		if (MediaComp)
		{
			// 选择指定的媒体源
			MediaComp->SelectMediaSourceAsset(MediaSourceToPlay);
			// 打开媒体
			MediaComp->Open();
			// 开始播放
			MediaComp->Play();
		}
	}
}

void AMyMediaPlateDemoActor::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	// 可以在这里添加逻辑，例如根据游戏事件暂停或跳转
}
```

## 模块依赖

MediaPlate 模块依赖了 `UnrealEd`，这意味着它的部分功能（如材质实例创建、资产数据处理）与编辑器紧密耦合。因此，在纯Runtime模块中使用此插件时，需要注意条件编译（`WITH_EDITOR`）宏。

| 模块 | 用途 |
|---|---|
| `MediaUtils` | 提供底层的媒体工具函数和数据结构。 |
| `MediaPlayer` | 核心的媒体播放器类。 |
| `MediaTexture` | 用于在UE中渲染媒体帧的纹理资源。 |
| `MediaAssets` | 提供 `UMediaSource`, `UMediaPlaylist` 等资产类型。 |
| `MediaSound` | 通过 `UMediaSoundComponent` 处理媒体音频。 |
| `ImageWriteQueue` | 用于EXR序列的图像写入队列。 |
| `ImageWrapper` | 用于支持多种图像格式（如EXR）的读写。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志输出宏迁移至新的UE_LOGF。 |
| 2026-04-09 | `17c8eeed` | [MediaPlateEditor] Prevent adding multiple media tracks under the same media plate binding. | 防止在同一个媒体板绑定下添加多个媒体轨道。 |
| 2026-04-08 | `786c0a7e` | [MediaPlate] Support multiple media textures in the "material instance constant" code path. | 在“材质实例常量”代码路径中支持多层媒体纹理。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复了上一次错误的查找替换后，第二次提交。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退了变更列表51314860的改动。 |

### 维护评价

- **活跃维护**：插件仍在积极维护中，最近的提交（2026年4月）显示了对日志系统、编辑器工作流和多层纹理渲染的持续改进和优化。
- **实验性状态**：`.uplugin` 中 `IsBetaVersion=true`，表明该插件仍处于Beta测试阶段，其API和功能在未来的引擎版本中可能发生变化。
- **功能成熟**：从源码规模（39个文件）和提供的API深度来看，该插件已经相当成熟，提供了完整的播放控制、资源管理、渲染优化（Mip/Tiles）功能，特别是对EXR序列的支持非常专业。
- **推荐使用**：**推荐在需要高质量、可控的媒体播放功能，尤其是虚拟制片和高端交互式场景中使用**。但由于其Beta状态，建议在项目升级引擎版本时做好充分测试，并关注更新日志以应对可能的API变动。对于要求极高稳定性的项目，可考虑等待其正式版本。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaPlate)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaPlate/Tests)