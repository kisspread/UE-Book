# Media Plate

> Actor that can play media.

| 属性 | 值 |
|---|---|
| 中文名 | 媒体板 |
| 分类 | Media |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（材质、Actor 蓝图） |
| 模块 | `MediaPlate` (Runtime), `MediaPlateEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-01-27 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaPlate) | |

## 用途

MediaPlate 是一个**面向世界的媒体播放 Actor 组件**，解决了在 UE5 场景中直接播放视频/图片序列的完整工作流问题。

与底层 `UMediaPlayer` + `UMediaTexture` 的裸用法不同，MediaPlate 提供了**开箱即用的 Actor**，集成了：

1. **媒体播放管理**：支持播放列表、外部文件路径、UMediaSource 资产三种资源选择方式
2. **自适应网格显示**：内置 StaticMeshComponent，可自动根据媒体宽高比调整网格尺寸
3. **Letterbox 支持**：当媒体与屏幕宽高比不一致时自动添加黑边
4. **可见性优化**：`bPlayOnlyWhenVisible` 可在 Actor 不可见时停止播放以节省性能
5. **EXR 瓦片/Mip 支持**：针对高分辨率 EXR 图片序列的分层加载和 Mip 偏置优化（球面投影场景）
6. **Sequencer 集成**：通过 `IMediaPlayerProxyInterface` 支持 Sequencer 的代理模式
7. **Holdout Composite**：支持将网格作为 holdout 合成单独渲染（绕过 TAA）

**为什么存在**：原始 Media Framework API 需要手动管理 Player、Texture、Sound Component、材质参数等大量对象。MediaPlate 将这一切封装为一个拖放到场景中即可工作的 Actor，大幅降低了在关卡中放置视频屏幕的门槛。

## 使用场景

- 你在做一个虚拟制片场景，需要在 LED 墙上播放实时视频 → 用 MediaPlate
- 你需要在关卡中放置一块播放广告视频的屏幕 → 用 MediaPlate
- 你正在做建筑可视化项目，需要播放循环的环境视频 → 用 MediaPlate
- 你使用 EXR 图片序列作为球幕投影源 → 用 MediaPlate 的 Mip/Tiles 功能
- 你需要在 Sequencer 中精确控制视频播放时间线 → 用 MediaPlate 的 Proxy 模式
- 你需要在后期合成中将视频区域单独渲染（Holdout Composite）→ 用 MediaPlate

## 蓝图用法

### 核心节点 — 播放控制

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open` | 打开当前选定的媒体源 | `UMediaPlateComponent` |
| `OpenLatent` | 异步打开媒体，可等待纹理就绪 | `UMediaPlateComponent` |
| `Play` | 以正常速度正向播放 | `UMediaPlateComponent` |
| `PlayReverse` | 以正常速度反向播放 | `UMediaPlateComponent` |
| `Pause` | 暂停播放 | `UMediaPlateComponent` |
| `Close` | 关闭媒体 | `UMediaPlateComponent` |
| `Rewind` | 回到媒体开头 | `UMediaPlateComponent` |
| `Seek` | 跳转到指定时间 | `UMediaPlateComponent` |
| `Next` | 播放列表中下一个 | `UMediaPlateComponent` |
| `Previous` | 播放列表中上一个 | `UMediaPlateComponent` |
| `SwitchStates` | 切换事件状态（Play/Open/Pause 等） | `UMediaPlateComponent` |

### 核心节点 — 资源选择

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SelectExternalMedia` | 选择外部文件路径作为媒体源 | `UMediaPlateComponent` |
| `SelectMediaSourceAsset` | 选择 UMediaSource 资产 | `UMediaPlateComponent` |
| `SelectMediaPlaylistAsset` | 选择 UMediaPlaylist 资产 | `UMediaPlateComponent` |
| `GetSelectedMediaSource` | 获取当前选中的 MediaSource | `UMediaPlateComponent` |
| `GetMediaPlaylist` | 获取当前播放列表 | `UMediaPlateComponent` |

### 核心节点 — 查询与设置

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetMediaPlayer` | 获取内部 UMediaPlayer | `UMediaPlateComponent` |
| `GetMediaTexture` | 获取内部 UMediaTexture | `UMediaPlateComponent` |
| `IsMediaPlatePlaying` | 是否正在播放 | `UMediaPlateComponent` |
| `IsEventStateChangeAllowed` | 检查能否切换到指定状态 | `UMediaPlateComponent` |
| `GetLoop` / `SetLoop` | 获取/设置循环播放 | `UMediaPlateComponent` |
| `SetEnableAudio` | 启用/禁用音频 | `UMediaPlateComponent` |
| `SetPlayOnlyWhenVisible` | 仅可见时播放 | `UMediaPlateComponent` |
| `SetIsAspectRatioAuto` | 自动宽高比 | `UMediaPlateComponent` |
| `SetLetterboxAspectRatio` | 设置信箱宽高比 | `UMediaPlateComponent` |
| `SetMeshRange` / `GetMeshRange` | 设置球面网格弧度范围 | `UMediaPlateComponent` |

### 核心节点 — Actor 级别

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetHoldoutCompositeEnabled` | 启用 Holdout 合成模式 | `AMediaPlate` |
| `IsHoldoutCompositeEnabled` | 查询 Holdout 合成状态 | `AMediaPlate` |

### 使用示例（蓝图描述）

**场景 1：在关卡中放置一个视频屏幕**

1. 在场景中拖放 MediaPlate Actor
2. 在细节面板中，找到 `MediaPlateResource` 属性
3. 将资源类型选择为 `Asset`，然后指定一个 `UMediaSource` 资产
4. 勾选 `bAutoPlay` 和 `bPlayOnOpen`（默认已启用）
5. 运行场景，视频将自动播放并显示在 MediaPlate 的网格上

**场景 2：运行时切换媒体源**

```
[Begin Play] → [Select External Media (路径="D:/Videos/intro.mp4")] → [Open] → [Play]
```

**场景 3：异步打开并等待纹理就绪**

```
[Trigger] → [Open Latent (Timeout=15, WaitForTexture=true)] → [Branch: bOutSuccess]
                                                            → True: [Play]
                                                            → False: [Print String "Failed"]
```

**场景 4：播放列表循环**

```
[Begin Play] → [Select Media Playlist Asset (PlaylistAsset=MyPlaylist)] → [Open] → [Play]
[Button Pressed] → [Next]   // 切换到下一个视频
[Button Pressed] → [Previous] // 切换到上一个视频
```

## C++ 用法

### 头文件引入

```cpp
#include "MediaPlateComponent.h"
#include "MediaPlate.h"
#include "MediaPlateResource.h"
```

### 基本用法

以下代码展示了如何在 C++ 中程序化控制 MediaPlate 播放：

```cpp
// 假设你有一个 AMediaPlate 指针
AMediaPlate* MyMediaPlate = /* 从场景中获取 */;

// 获取组件
UMediaPlateComponent* Component = MyMediaPlate->MediaPlateComponent;

// 选择外部媒体文件并播放
Component->SelectExternalMedia(TEXT("D:/Videos/my_video.mp4"));
Component->Open();
Component->Play();
```

**来源**：`Public/MediaPlateComponent.h` 中 `SelectExternalMedia`、`Open`、`Play` 的函数声明

### 进阶用法

**异步打开媒体并等待纹理就绪**：

```cpp
// OpenLatent 是蓝图 Latent 节点，C++ 中需要手动创建 Latent Action
FLatentActionInfo LatentInfo;
LatentInfo.CallbackTarget = this;
LatentInfo.ExecutionFunction = "OnMediaReady";
LatentInfo.Linkage = 0;
LatentInfo.UUID = 1;

bool bSuccess = false;
MediaPlateComponent->OpenLatent(this, LatentInfo, 15.0f, true, bSuccess);
```

**来源**：`Public/MediaPlateComponent.h` 中 `OpenLatent` 的 UFUNCTION 声明及 `Private/MediaPlateOpenLatentAction.h`

**以播放列表方式播放**：

```cpp
// 选择一个 UMediaPlaylist 资产
UMediaPlaylist* MyPlaylist = LoadObject<UMediaPlaylist>(nullptr, TEXT("/Game/Media/MyPlaylist"));
Component->SelectMediaPlaylistAsset(MyPlaylist);
Component->Open();
Component->Play();

// 播放下一个
bool bPlayed = Component->Next();

// 播放上一个
bool bPlayedPrev = Component->Previous();
```

**来源**：`Public/MediaPlateComponent.h` 中 `SelectMediaPlaylistAsset`、`Next`、`Previous`

**通过模块接口获取 MediaPlayer**：

```cpp
#include "MediaPlateModule.h"

FMediaPlateModule& MediaPlateModule = FModuleManager::GetModuleChecked<FMediaPlateModule>("MediaPlate");
UObject* PlayerProxy = nullptr;
UMediaPlayer* Player = MediaPlateModule.GetMediaPlayer(SomeObject, PlayerProxy);
```

**来源**：`Public/MediaPlateModule.h` 中 `FMediaPlateModule::GetMediaPlayer`

## Demo 示例

### MediaPlateController.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MediaPlateController.generated.h"

class UMediaPlateComponent;
class UMediaPlayer;

UCLASS()
class AMyMediaPlateController : public AActor
{
	GENERATED_BODY()

public:
	AMyMediaPlateController();

	/** 要控制的 MediaPlate Actor 引用 */
	UPROPERTY(EditAnywhere, Category = "Media")
	TObjectPtr<AActor> TargetMediaPlateActor;

	/** 要播放的外部视频路径 */
	UPROPERTY(EditAnywhere, Category = "Media")
	FString VideoFilePath;

	UFUNCTION(BlueprintCallable, Category = "Media")
	void StartPlayback();

	UFUNCTION(BlueprintCallable, Category = "Media")
	void TogglePause();

	UFUNCTION(BlueprintCallable, Category = "Media")
	void PlayNext();

	virtual void BeginPlay() override;

private:
	UPROPERTY()
	TObjectPtr<UMediaPlateComponent> CachedComponent;
};
```

### MediaPlateController.cpp

```cpp
#include "MediaPlateController.h"
#include "MediaPlateComponent.h"
#include "MediaPlate.h"

AMyMediaPlateController::AMyMediaPlateController()
{
	PrimaryActorTick.bCanEverTick = false;
}

void AMyMediaPlateController::BeginPlay()
{
	Super::BeginPlay();

	// 从目标 Actor 获取 MediaPlateComponent
	if (TargetMediaPlateActor)
	{
		AMediaPlate* MediaPlate = Cast<AMediaPlate>(TargetMediaPlateActor);
		if (MediaPlate)
		{
			CachedComponent = MediaPlate->MediaPlateComponent;
		}

		// 如果不是 AMediaPlate 类型，尝试直接查找组件
		if (!CachedComponent)
		{
			CachedComponent = TargetMediaPlateActor->FindComponentByClass<UMediaPlateComponent>();
		}
	}

	if (CachedComponent && !VideoFilePath.IsEmpty())
	{
		StartPlayback();
	}
}

void AMyMediaPlateController::StartPlayback()
{
	if (!CachedComponent)
	{
		return;
	}

	// 选择外部文件
	CachedComponent->SelectExternalMedia(VideoFilePath);
	// 打开媒体
	CachedComponent->Open();
	// 开始播放
	CachedComponent->Play();
}

void AMyMediaPlateController::TogglePause()
{
	if (!CachedComponent)
	{
		return;
	}

	if (CachedComponent->IsMediaPlatePlaying())
	{
		CachedComponent->Pause();
	}
	else
	{
		CachedComponent->Play();
	}
}

void AMyMediaPlateController::PlayNext()
{
	if (!CachedComponent)
	{
		return;
	}

	if (!CachedComponent->Next())
	{
		// 播放列表已到末尾，可选择循环或停止
		UE_LOG(LogTemp, Warning, TEXT("已到达播放列表末尾"));
	}
}
```

## 模块依赖

从 Build.cs 提取，MediaPlate 模块依赖了 `UnrealEd`（运行时模块依赖编辑器模块，用于编辑器内回调等功能）。

使用者无特殊依赖（仅标准 Core/Engine/Slate 等），但需确保项目已启用 MediaPlate 插件。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志系统迁移到新宏格式 |
| 2026-04-09 | `17c8eeed` | [MediaPlateEditor] Prevent adding multiple media tracks under the same media plate binding. | 防止同一绑定下重复添加媒体轨道 |
| 2026-04-08 | `786c0a7e` | [MediaPlate] Support multiple media textures in the "material instance constant" code path. | 支持材质实例中多纹理层 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复之前批量替换导致的错误 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退之前的提交 |

### 维护评价

**活跃维护**。MediaPlate 是 UE5 媒体框架的核心组件之一，近几个月内持续有功能性更新（多纹理支持、编辑器防重复轨道等）和维护性修复。

主要观察：
- **Beta 状态**：`.uplugin` 中 `IsBetaVersion=true`，API 可能在未来版本有 breaking changes
- **创建时间**：2022 年初，约 4 年历史，已从初始版本演化到支持 EXR 瓦片、Holdout Composite 等高级功能
- **废弃属性**：存在多个 `UE_DEPRECATED(5.5)` / `UE_DEPRECATED(5.6)` 标记的旧 API，说明 API 经历过重大重构
- **Sequencer 集成**：实现了 `IMediaPlayerProxyInterface`，表明与 Sequencer 深度集成
- **推荐使用**：如果你需要在场景中放置视频播放对象，MediaPlate 是官方推荐方案。但注意它仍是 Beta 状态，生产环境使用需关注版本兼容性

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaPlate)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)