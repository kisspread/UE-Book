# WMF Media Player

> Implements a media player using the Windows Media Foundation framework.

| 属性 | 值 |
|---|---|
| 中文名 | WMF 媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `WmfMedia` (Runtime), `WmfMediaEditor` (Runtime), `WmfMediaFactory` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2014-07-31 |
| 年龄标签 | 🏛️ 文物（约 12 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/WmfMedia) | |

## 用途

`WmfMedia` 插件是一个 **Windows 平台专用**的媒体播放解决方案。它封装了微软的 Windows Media Foundation (WMF) 框架，为 Unreal Engine 提供在 Windows 上播放视频和音频文件的核心能力。其存在意义在于为 Windows 平台的项目提供一种高效、原生的媒体播放后端。

## 使用场景

- 你需要在 Windows 平台的 PC 游戏或应用中播放过场动画、剧情视频。
- 你需要在 UI 界面或 3D 空间中播放广告、教程视频等流媒体内容。
- 你的项目主要面向 Windows 平台，并希望使用系统原生的媒体解码能力以获得良好的性能和兼容性。

## 蓝图用法

`WmfMedia` 主要作为媒体播放系统的后端实现，其具体功能通过 Unreal Engine 通用的 `Media Framework` 蓝图接口暴露。你需要结合 `MediaPlayer` 和 `MediaSource` 等资产来使用。

### 核心节点

由于该插件是 Media Framework 的一个具体实现，其核心函数体现在通用的 `UMediaPlayer` 类中。以下是通过该插件播放媒体时通常会使用到的核心蓝图节点：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open Source` | 打开一个媒体源（如 `FileMediaSource`）进行播放 | `UMediaPlayer` |
| `Play` | 开始播放当前媒体 | `UMediaPlayer` |
| `Pause` | 暂停播放 | `UMediaPlayer` |
| `Close` | 关闭媒体源，释放资源 | `UMediaPlayer` |
| `Seek` | 跳转到指定时间点 | `UMediaPlayer` |
| `Set Looping` | 设置是否循环播放 | `UMediaPlayer` |

### 使用示例（蓝图描述）

1.  在你的内容浏览器中，创建一个 `File Media Source` 资产，并将其 `FilePath` 设置为你的视频文件路径（如 `C:/Videos/MyVideo.mp4`）。
2.  创建一个 `Media Player` 资产，确保其 `Player Name` 设置为 `WmfMedia`（或留空由系统自动选择）。
3.  在蓝图中，对你的 `Media Player` 资产调用 `Open Source` 节点，并传入之前创建的 `File Media Source`。
4.  连接 `Open Source` 的返回值到一个 `Play` 节点，即可开始播放。
5.  可以通过 `Media Texture` 和 `Media Sound Component` 将视频画面输出到 UI 或 3D 物体上，并输出音频。

## C++ 用法

在 C++ 中，主要通过 Unreal Engine 的媒体模块接口进行操作，`WmfMedia` 作为底层实现。

### 头文件引入

```cpp
#include "MediaPlayer.h"
#include "FileMediaSource.h"
#include "MediaTexture.h"
#include "MediaSoundComponent.h"
```

### 基本用法

以下是创建一个媒体播放器并播放本地文件的基本步骤。

```cpp
// 假设你已经在类中声明了以下成员变量
// UPROPERTY() UMediaPlayer* MediaPlayer;
// UPROPERTY() UFileMediaSource* MediaSource;
// UPROPERTY() UMediaTexture* MediaTexture;
// UPROPERTY() UMediaSoundComponent* MediaSoundComp;

void AMyActor::SetupMediaPlayer()
{
    // 1. 创建媒体播放器，可显式指定或留空让引擎选择
    MediaPlayer = NewObject<UMediaPlayer>(this);
    MediaPlayer->SetPlayerName(TEXT("WmfMediaPlayer"));

    // 2. 创建媒体源并设置文件路径
    MediaSource = NewObject<UFileMediaSource>(this);
    MediaSource->SetFilePath(FPaths::ProjectContentDir() / TEXT("Movies/MyVideo.mp4"));

    // 3. 打开媒体源
    if (MediaPlayer->OpenSource(MediaSource))
    {
        // 4. 绑定输出到媒体纹理和声音组件
        MediaTexture = NewObject<UMediaTexture>(this);
        MediaTexture->SetMediaPlayer(MediaPlayer);
        MediaTexture->UpdateResource();

        MediaSoundComp = NewObject<UMediaSoundComponent>(this);
        MediaSoundComp->SetMediaPlayer(MediaPlayer);
        MediaSoundComp->RegisterComponent();

        // 5. 开始播放
        MediaPlayer->Play();
    }
}
```

### 进阶用法

可以监听媒体播放事件来获得更精细的控制。

```cpp
// 绑定播放结束事件
MediaPlayer->OnMediaClosed.AddDynamic(this, &AMyActor::OnMediaClosed);
MediaPlayer->OnPlaybackResumed.AddDynamic(this, &AMyActor::OnPlaybackResumed);

void AMyActor::OnMediaClosed()
{
    UE_LOG(LogTemp, Log, TEXT("Media Closed"));
}

void AMyActor::OnPlaybackResumed()
{
    UE_LOG(LogTemp, Log, TEXT("Media Playback Resumed"));
}
```

## Demo 示例

一个完整的、可编译的最小示例，用于在 Actor 中播放视频。

### MyMediaActor.h
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MediaPlayer.h"
#include "FileMediaSource.h"
#include "MediaTexture.h"
#include "MediaSoundComponent.h"
#include "MyMediaActor.generated.h"

UCLASS()
class AMyMediaActor : public AActor
{
    GENERATED_BODY()

public:
    AMyMediaActor();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere, Category = "Media")
    UMediaPlayer* MediaPlayer;

    UPROPERTY(EditAnywhere, Category = "Media")
    UFileMediaSource* MediaSource;

    UPROPERTY(VisibleAnywhere, Category = "Media")
    UMediaTexture* MediaTexture;

    UPROPERTY(VisibleAnywhere, Category = "Media")
    UMediaSoundComponent* MediaSoundComp;

    UPROPERTY(VisibleAnywhere, Category = "Media")
    UStaticMeshComponent* ScreenMesh;
};
```

### MyMediaActor.cpp
```cpp
#include "MyMediaActor.h"
#include "UObject/ConstructorHelpers.h"

AMyMediaActor::AMyMediaActor()
{
    PrimaryActorTick.bCanEverTick = false;

    // 创建网格体作为屏幕
    ScreenMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("ScreenMesh"));
    RootComponent = ScreenMesh;
    static ConstructorHelpers::FObjectFinder<UStaticMesh> ScreenMeshAsset(TEXT("/Engine/BasicShapes/Plane"));
    if (ScreenMeshAsset.Succeeded())
    {
        ScreenMesh->SetStaticMesh(ScreenMeshAsset.Object);
    }

    // 初始化媒体组件
    MediaPlayer = CreateDefaultSubobject<UMediaPlayer>(TEXT("MediaPlayer"));
    MediaTexture = CreateDefaultSubobject<UMediaTexture>(TEXT("MediaTexture"));
    MediaSoundComp = CreateDefaultSubobject<UMediaSoundComponent>(TEXT("MediaSoundComp"));
    MediaSoundComp->SetupAttachment(RootComponent);
}

void AMyMediaActor::BeginPlay()
{
    Super::BeginPlay();

    // 设置媒体播放器的输出
    MediaTexture->SetMediaPlayer(MediaPlayer);
    // 你可能需要动态创建材质实例并设置 MediaTexture 作为参数
    // ScreenMesh->CreateDynamicMaterialInstance(0)->SetTextureParameterValue(TEXT("MediaTextureParam"), MediaTexture);

    // 打开并播放媒体源
    if (MediaSource && MediaPlayer->OpenSource(MediaSource))
    {
        MediaPlayer->Play();
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `HeadMountedDisplay` | 用于支持在 VR 环境中播放媒体（依赖关系可能源于早期架构）。 |
| `D3D11RHI` | 提供 DirectX 11 渲染硬件接口，用于 WMF 视频帧的 GPU 解码与显示。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到新的 UE_LOGF。 |
| 2026-02-24 | `13c44482` | Media Profile: Added media player options to media profile editor details panels for stream media so | 为媒体配置编辑器添加了流媒体播放器选项面板。 |
| 2026-02-04 | `80b637db` | Fixed printf format specifiers. | 修复了 printf 格式说明符。 |
| 2026-01-07 | `57ff2f55` | Deprecate legacy GPU profiler related macros. | 废弃了旧的 GPU 性能分析相关宏。 |
| 2025-10-30 | `0990a715` | Ran UnrealCodeFixup on Fortnite to change all ~Type() {} to instead be ~Type() = default | 执行了代码修复，将析构函数体改为 `= default`。 |

### 维护评价

`WmfMedia` 是一个历史悠久的插件，创建于 **2014 年**。从近期提交记录看，它仍在被 Epic Games 维护，但更新内容主要是全局性的代码风格迁移、编译修复和对其他子系统（如媒体配置）的兼容性适配，而非功能性的增强或重构。

它是一个**稳定、成熟**的插件，作为 Windows 平台上 `Media Framework` 的基石后端之一被默认启用。只要你的项目需要支持 Windows 平台的媒体播放，它就是一个可靠的选择。然而，由于其设计较早，且主要针对 Windows 平台，如果你需要跨平台（如 Mac/Linux/iOS/Android）的媒体播放，需要结合 `AvfMedia`、`AndroidMedia` 等其他插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/WmfMedia)
- [官方文档](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/WmfMedia/Tests)