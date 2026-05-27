# Media Framework Utilities

> This plugin provides utility assets and actors designed to simplify the Media Framework setup. It includes access to the the Media Profile editor.

| 属性 | 值 |
|---|---|
| 中文名 | 媒体框架工具 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产模板） |
| 模块 | `MediaFrameworkUtilities` (Runtime), `MediaFrameworkUtilitiesEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaFrameworkUtilities) | |

## 用途

MediaFrameworkUtilities 的核心价值在于封装和简化了 UE 的 Media Framework 使用流程。它主要解决两个问题：

1.  **媒体资产管理复杂**：直接使用 `UMediaPlayer`、`UMediaTexture`、`UMaterial` 等组件进行配置步骤繁琐。本插件提供了 `UMediaBundle` 这个“打包资产”，将上述组件及其配置（如循环、错误重连）聚合到一个资源中，极大地简化了媒体播放的初始设置和资产管理。
2.  **缺乏统一的媒体配置与同步工具**：针对虚拟制作、广播等需要管理多路输入输出媒体（如 Blackmagic、AJA 采集卡）的场景，本插件通过集成 **Media Profiles** 功能，允许用户在不同的硬件/软件媒体配置之间快速切换。同时，提供了时间同步源，确保媒体播放与引擎其他系统（如动画、音频）的时间线对齐。

## 使用场景

-   **虚拟制作/广播**：需要在一套项目中管理多个摄像机输入（Blackmagic/AJA 卡）、不同的显示输出（LED墙、监视器），并能根据拍摄场景快速切换预设的媒体配置（Media Profile）。
-   **简化媒体播放**：你希望在场景中快速放置一个能播放视频文件的“智能”物体，而无需手动创建 Media Player、Texture、Material 并将它们连接起来。
-   **时间同步**：你需要将视频播放的时间戳与引擎的音频、动画系统精确同步，例如用于动作捕捉数据回放或现场直播。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Media Bundle` | 获取此 Actor 关联的 MediaBundle 资产 | `AMediaBundleActorBase` |
| `Request Open Media Source` | 请求打开并播放媒体源，返回是否成功 | `AMediaBundleActorBase` |
| `Request Close Media Source` | 请求关闭媒体源 | `AMediaBundleActorBase` |
| `Get Media Player` | 获取 MediaBundle 内部的媒体播放器 | `UMediaBundle` |
| `Get Media Texture` | 获取 MediaBundle 内部的媒体纹理 | `UMediaBundle` |
| `Get Material` | 获取 MediaBundle 的材质 | `UMediaBundle` |
| `Get Media Profile` | 获取当前激活的 MediaProfile 配置 | `UMediaProfileBlueprintLibrary` |
| `Set Media Profile` | 设置激活的 MediaProfile 配置 | `UMediaProfileBlueprintLibrary` |
| `Get All Media Source Proxy` | 获取所有媒体源代理 | `UMediaProfileBlueprintLibrary` |
| `Get All Media Output Proxy` | 获取所有媒体输出代理 | `UMediaProfileBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  **基本播放**：在场景中放置一个基于 `AMediaBundleActorBase` 的 Actor。在 Details 面板中，指定一个已创建的 `UMediaBundle` 资产。勾选 `bAutoPlay` 即可实现开始时自动播放。也可以在 BeginPlay 事件中调用 `Request Open Media Source` 节点手动控制。
2.  **切换配置**：在项目设置中定义好多个 `UMediaProfile`。在蓝图的某个事件（如按键输入）中，调用 `Set Media Profile` 节点并传入不同的 Profile 资产，即可运行时切换全局的媒体输入输出配置。
3.  **自定义材质**：通过 `MediaBundle` 的 `Get Material` 节点获取材质接口，可以创建动态材质实例 (`UMaterialInstanceDynamic`)，并在运行时修改其参数，例如用 `Set Texture Parameter Value` 节点将 MediaTexture 赋予材质的特定通道。

## C++ 用法

### 头文件引入

```cpp
#include "MediaBundleActorBase.h"
#include "MediaBundle.h"
#include "MediaPlayerTimeSynchronizationSource.h"
```

### 基本用法

以下代码演示了如何在 C++ 中创建和操作一个 MediaBundle Actor。
*(参考自 `Public/MediaBundleActorBase.h` 中的接口定义)*

```cpp
// 假设已经有一个 MediaBundle 资产在编辑器中创建，并指定了 MediaSource
AMediaBundleActorBase* MediaActor = GetWorld()->SpawnActor<AMediaBundleActorBase>();
MediaActor->SetMediaBundle(MyMediaBundleAsset); // 设置媒体包资产

// 请求播放
bool bSuccess = MediaActor->RequestOpenMediaSource();
if (bSuccess)
{
    UE_LOG(LogTemp, Log, TEXT("Media source opened successfully."));
}

// 在适当时机（如 Actor 销毁时）关闭
MediaActor->RequestCloseMediaSource();

// 获取 MediaBundle 内部组件
UMediaBundle* Bundle = MediaActor->GetMediaBundle();
if (Bundle)
{
    UMediaPlayer* Player = Bundle->GetMediaPlayer();
    UMediaTexture* Texture = Bundle->GetMediaTexture();
    // ... 进行更高级的控制
}
```

### 进阶用法

使用 `UMediaPlayerTimeSynchronizationSource` 将媒体播放与时间同步系统集成。
*(参考自 `Public/MediaPlayerTimeSynchronizationSource.h`)*

```cpp
// 创建一个时间同步源对象
UMediaPlayerTimeSynchronizationSource* SyncSource = NewObject<UMediaPlayerTimeSynchronizationSource>();
SyncSource->MediaSource = MyMediaSourceAsset;
SyncSource->MediaTexture = MyMediaTextureAsset;

// 将此同步源添加到时间同步管理器（通常需要通过蓝图或编辑器操作，此处仅为接口示意）
// FTimeSynchronization::Get().AddSource(SyncSource);

// 后续可以查询同步源状态
if (SyncSource->IsReady())
{
    FFrameTime NewestTime = SyncSource->GetNewestSampleTime();
    FFrameRate FrameRate = SyncSource->GetFrameRate();
    // 使用这些时间信息进行同步逻辑
}
```

## Demo 示例

一个最小化的 MediaBundle 播放器 Actor 实现。

**MyMediaActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "MediaBundleActorBase.h"
#include "MyMediaActor.generated.h"

UCLASS()
class AMyMediaActor : public AMediaBundleActorBase
{
	GENERATED_BODY()
	
public:
	AMyMediaActor();

protected:
	virtual void BeginPlay() override;

public:
	virtual void Tick(float DeltaTime) override;
};
```

**MyMediaActor.cpp**
```cpp
#include "MyMediaActor.h"

AMyMediaActor::AMyMediaActor()
{
	PrimaryActorTick.bCanEverTick = true;

	// 创建一个默认的 StaticMeshComponent 作为显示载体
	UStaticMeshComponent* MeshComp = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
	RootComponent = MeshComp;

	// 创建一个 MediaSoundComponent 用于播放声音
	UMediaSoundComponent* SoundComp = CreateDefaultSubobject<UMediaSoundComponent>(TEXT("MediaSound"));
	SoundComp->SetupAttachment(RootComponent);

	// 在编辑器中设置显示组件和声音组件
	SetComponent(MeshComp, SoundComp);
}

void AMyMediaActor::BeginPlay()
{
	Super::BeginPlay();

	// 如果设置了自动播放，则开始播放
	if (bAutoPlay)
	{
		RequestOpenMediaSource();
	}
}

void AMyMediaActor::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	// 这里可以添加每帧的自定义逻辑，例如基于播放状态更新UI
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MediaAssets` | 提供核心的 Media Player, Media Texture, Media Source 等资产类 |
| `MediaUtils` | 提供媒体框架的底层工具和接口 |
| `OpenCVLensDistortion` | 提供镜头畸变校正参数和渲染目标管理，用于 MediaBundle 的镜头校正功能 |
| `TimeManagement` | 提供时间同步框架 (`UTimeSynchronizationSource` 基类) |
| `MediaCompositing` | 可能用于与合成相关的媒体功能 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `36c08694` | Media IO - Populate Media Configuration when using auto for Blackmagic and Aja cards | 为 Blackmagic 和 AJA 采集卡自动填充媒体配置 |
| 2026-05-22 | `7d256b73` | [Media] Add shared Media category to the Level Editor Window menu | 在关卡编辑器的窗口菜单中新增“共享媒体”分类 |
| 2026-05-21 | `ff9996e8` | Media Profile: Fixed issue where ElectraProtron issue would not play a new video after it had alread | 修复 Media Profile 中 ElectraProtron 播放器无法播放新视频的问题 |
| 2026-05-20 | `54cbb9f8` | Ensure a transient MediaProfile always exists from startup | 确保启动时始终存在一个临时的 MediaProfile |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 通过客户端关联/取消关联通知，重构视口相关代码 |

### 维护评价

该插件目前处于 **积极维护中**。从提交历史看，近一个月内（2026年5月）有多次功能性更新和错误修复，特别是加强了对 Blackmagic、AJA 等专业采集卡的支持，并修复了媒体播放器相关的具体问题。创建时间虽早（约8年），但作为 Epic 官方媒体工作流的核心工具链之一，持续更新表明其仍被重视。插件功能完善，是虚拟制作和媒体集成项目的推荐选择。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaFrameworkUtilities)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaFrameworkUtilities/Tests)