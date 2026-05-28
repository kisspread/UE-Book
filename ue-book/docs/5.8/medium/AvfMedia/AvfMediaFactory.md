# AVF Media Player

> Implements a media player using Apple AV Foundation.

| 属性 | 值 |
|---|---|
| 中文名 | 苹果媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AvfMedia` (RuntimeNoCommandlet), `AvfMediaEditor` (Editor), `AvfMediaFactory` (Editor), `AvfMediaFactory` (RuntimeNoCommandlet), `AvfMediaCapture` (RuntimeNoCommandlet) |
| 实验性 | 否 |
| 创建时间 | 2014-09-16 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AvfMedia) | |

## 用途

AvfMedia 是 Unreal Engine 的媒体框架插件，专门用于在 **Apple 平台（iOS、Mac、tvOS）** 上提供媒体播放功能。其核心是封装了 Apple 的原生 **AV Foundation** 多媒体框架，使得开发者能够在 UE 项目中无缝播放视频和音频文件，同时充分利用苹果系统的硬件解码能力和优化。

该插件解决了在苹果生态设备上播放媒体内容的统一性问题，确保了与系统原生应用相近的播放性能和格式兼容性。

## 使用场景

- 你正在开发面向 **iPhone/iPad** 的游戏或应用，需要播放过场动画、介绍视频或用户生成内容。
- 你的 **Mac** 应用程序需要嵌入视频教程或宣传片。
- 你正在为 **Apple TV** (tvOS) 构建一个媒体中心或流媒体客户端。
- 你需要一个能在所有目标苹果设备上稳定工作、且利用系统原生解码器的媒体播放方案。

## 蓝图用法

该插件主要在底层实现媒体播放逻辑，没有提供大量面向蓝图的公开函数。其配置主要通过项目设置进行。

### 核心配置

该插件的核心配置位于 `UAvfMediaSettings` 类中。

| 属性 | 说明 | 所在类 |
|---|---|---|
| `NativeAudioOut` | 控制是否通过操作系统原生的声音混音器播放音频轨道。开启可能提升音频兼容性或性能。 | `UAvfMediaSettings` |

### 使用示例（蓝图描述）

1.  在项目设置中，找到 **插件 - AVF Media** 分类。
2.  勾选或取消勾选 **Native Audio Out** 选项，以决定音频输出方式。
3.  媒体播放的创建和控制将通过 **媒体框架** 的通用蓝图节点（如 `Open Source`、`Play`、`Close`）结合 `AvfMedia` 模块提供的内部实现来完成。

## C++ 用法

在 C++ 中，主要通过配置和调用标准的媒体框架 API 来使用该插件。

### 头文件引入

```cpp
// 引入插件设置头文件
#include "AvfMediaSettings.h"
```

### 基本用法

通过获取插件设置来查看或配置播放行为。

```cpp
// 获取 AvfMedia 的默认设置实例
const UAvfMediaSettings* Settings = GetDefault<UAvfMediaSettings>();
if (Settings)
{
    UE_LOG(LogTemp, Log, TEXT("Native Audio Out is: %s"), Settings->NativeAudioOut ? TEXT("Enabled") : TEXT("Disabled"));
}

// 实际的媒体播放器创建和操作通常通过 MediaFramework 的 UMediaPlayer 和 UMediaTexture 等通用类完成
// AvfMedia 模块在背后被框架自动调用以处理特定平台的解码
```

*（来源：`Source/AvfMediaFactory/Public/AvfMediaSettings.h`）*

## Demo 示例

以下示例展示了如何在 Actor 中创建一个使用 AvfMedia 插件的媒体播放器组件。请注意，实际的播放功能依赖于媒体框架和底层 AvfMedia 模块。

**MediaActor.h**
```cpp
// Fill out your copyright notice in the Description page of Project Settings.
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MediaActor.generated.h"

class UMediaPlayer;
class UMediaTexture;
class UMediaSource;

UCLASS()
class AMediaActor : public AActor
{
    GENERATED_BODY()

public:
    AMediaActor();

    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

public:
    // 媒体播放器组件
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Media")
    UMediaPlayer* MediaPlayer;

    // 用于显示视频的纹理组件
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Media")
    UMediaTexture* MediaTexture;

    // 要播放的媒体源（例如 .mp4 文件）
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Media")
    UMediaSource* MediaSource;
};
```

**MediaActor.cpp**
```cpp
// Fill out your copyright notice in the Description page of Project Settings.
#include "MediaActor.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"
#include "MediaSource.h"
#include "Components/StaticMeshComponent.h"

AMediaActor::AMediaActor()
{
    PrimaryActorTick.bCanEverTick = true;

    // 创建媒体播放器（引擎会根据平台自动选择 AvfMedia 或其他媒体插件）
    MediaPlayer = CreateDefaultSubobject<UMediaPlayer>(TEXT("MediaPlayer"));

    // 创建媒体纹理，用于将视频帧渲染到屏幕上
    MediaTexture = CreateDefaultSubobject<UMediaTexture>(TEXT("MediaTexture"));
    MediaTexture->SetMediaPlayer(MediaPlayer);

    // 可选：创建一个静态网格体组件，将媒体纹理作为材质应用
    UStaticMeshComponent* Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("ScreenMesh"));
    RootComponent = Mesh;
    // 假设已为 Mesh 设置了一个平面静态网格体
    // 在 BeginPlay 中或通过蓝图设置材质，材质需使用一个采样 MediaTexture 的纹理参数。
}

void AMediaActor::BeginPlay()
{
    Super::BeginPlay();

    // 如果指定了媒体源，则打开并播放
    if (MediaSource && MediaPlayer)
    {
        if (MediaPlayer->OpenSource(MediaSource))
        {
            MediaPlayer->Play();
        }
    }
}

void AMediaActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    // 媒体播放器会自动更新纹理，通常不需要在此处做额外操作。
}
```

## 模块依赖

该插件的模块依赖了媒体框架的核心组件。

| 模块 | 用途 |
|---|---|
| `MediaAssets` | 提供 `UMediaPlayer`, `UMediaTexture`, `UMediaSource` 等核心媒体资产类。 |
| `MediaUtils` | 提供媒体框架的工具类和底层接口。 |
| `AppleMovieStreamer` | （平台特定）提供与 Apple 平台底层流媒体相关的支持。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `1951db93` | [AvfMedia] Default H.264 file playback to BGRA decode and provide CPU accessible buffer for media fi | 默认将H.264文件解码格式设为BGRA，并提供CPU可访问的缓冲区 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏 UE_LOG 迁移到 UE_LOGF。 |
| 2026-04-13 | `b905d146` | Fix/Silence unreachable code warnings | 修复或消除不可达代码警告。 |
| 2026-04-01 | `39223292` | [AvfMedia] Provide CPU buffer alongside GPU texture when using FAvfMediaCapturePlayer | 在使用FAvfMediaCapturePlayer时，除GPU纹理外也提供CPU缓冲区。 |
| 2026-02-05 | `d5be7e14` | Fixed printfs. | 修复了打印语句。 |

### 维护评价

- **活跃维护**：该插件自2014年创建，历史悠久，但仍在持续更新。近期（2026年内）有多次提交，主要聚焦于 **视频解码格式优化**（BGRA默认、CPU缓冲区提供）和 **代码质量维护**（日志迁移、警告修复）。
- **平台特异性**：插件明确针对 Apple 平台，在 iOS、Mac、tvOS 上运行，属于平台特定功能插件。
- **功能稳定**：作为媒体框架的平台后端实现，其核心功能（基于AVFoundation的播放）已非常成熟，近期更新主要是增强功能和提升代码健壮性。
- **推荐使用**：如果你的项目目标平台包含 Apple 设备且需要视频播放功能，此插件是 **必备且推荐** 的。它是 UE 在苹果设备上实现媒体播放的官方解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AvfMedia)
- [官方文档](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview) (历史论坛帖子，内容可能已过时，但链接存在)