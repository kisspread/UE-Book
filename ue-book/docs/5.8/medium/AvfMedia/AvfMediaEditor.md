# AVF Media Player

> Implements a media player using Apple AV Foundation.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | AVF 媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AvfMedia` (Runtime), `AvfMediaEditor` (Editor), `AvfMediaFactory` (Editor/Runtime), `AvfMediaCapture` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2014-09-16 |
| 年龄标签 | 🏛️ 文物（约 12 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AvfMedia) | |

## 用途

该插件是 Unreal Engine 媒体框架在 Apple 生态系统（iOS, macOS, tvOS）下的**底层媒体播放后端**。它通过集成苹果原生的 AV Foundation 框架，为引擎在这些平台上提供高性能、高兼容性的媒体文件（如 H.264, HEVC 视频）解码和播放能力。其存在是为了解决引擎原生媒体播放器在苹果平台上兼容性或性能不佳的问题。

## 使用场景

- 你的项目需要部署到 iOS 或 macOS 并播放游戏内过场视频（CG）或背景视频 → 本插件会自动作为默认媒体播放器。
- 你需要在苹果设备上播放网络流媒体（RTMP/HLS）或高分辨率本地视频文件。
- 你在 macOS 编辑器中预览或编辑媒体资产。

## 蓝图用法

作为底层媒体后端，本插件主要通过引擎的媒体播放器接口和编辑器资产（如 `MediaPlayer`、`MediaTexture`）进行交互，通常没有独立的公开蓝图节点。您可以通过“媒体播放器”蓝图组件和资产来加载和播放媒体。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| （通过 `MediaPlayer` 蓝图资产控制） | 使用标准的 `Open Source`、`Play`、`Pause`、`Seek` 等节点操作媒体播放器，底层会由本插件提供支持。 | `UMediaPlayer` |

### 使用示例（蓝图描述）

1. 在内容浏览器中创建一个 `MediaPlayer` 资产和一个 `MediaTexture` 资产。
2. 创建一个 `MediaPlayer` 蓝图组件，或直接在 Material 中使用 `MediaTexture` 节点采样视频纹理。
3. 在蓝图中，通过 `Create Media Player` 节点获取 `MediaPlayer` 对象的引用。
4. 调用 `Open Source` 节点，并将 `Media Source` 设置为一个 `FileMediaSource` 资产（该资产指向您的视频文件）。此时，引擎会使用 `AvfMediaFactory` 在苹果平台创建 `AvfMedia` 播放器实例。
5. 调用 `Play` 节点开始播放。

## C++ 用法

直接使用本插件 C++ API 的场景较少，通常是媒体框架底层开发者。普通开发者应使用 `UMediaPlayer` 等通用接口。以下是查看解码后媒体纹理的底层用法示例。

### 头文件引入

```cpp
// 对于直接使用媒体纹理
#include "MediaTexture.h"
// 对于平台特定捕获（如果使用 AvfMediaCapture）
#include "IMediaCaptureSupport.h"
```

### 基本用法

创建并关联媒体播放器和纹理（遵循引擎标准流程）。

```cpp
// .cpp
// 1. 创建媒体播放器
UMediaPlayer* MediaPlayer = NewObject<UMediaPlayer>();

// 2. 创建媒体纹理，并设置播放器
UMediaTexture* MediaTexture = NewObject<UMediaTexture>();
MediaTexture->SetMediaPlayer(MediaPlayer);

// 3. 打开媒体源（此处为文件源）
UFileMediaSource* FileSource = NewObject<UFileMediaSource>();
FileSource->FilePath = TEXT("/Game/Movies/MyVideo.mp4");
MediaPlayer->OpenSource(FileSource);

// 4. 播放
if (MediaPlayer->IsReady())
{
    MediaPlayer->Play();
}

// 此时，MediaTexture 将包含来自 AvfMedia 解码后的视频帧数据。
// 可以将 MediaTexture 用于材质参数或进一步处理。
```

## Demo 示例

一个最小的、可运行的媒体播放器 Actor，它会在开始游戏时自动播放一个指定的本地视频文件。

```cpp
// MyMediaActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyMediaActor.generated.h"

class UMediaPlayer;
class UMediaTexture;
class UMediaSource;

UCLASS()
class AMyMediaActor : public AActor
{
    GENERATED_BODY()

public:
    AMyMediaActor();

protected:
    virtual void BeginPlay() override;

    // 在编辑器中设置的媒体源资产
    UPROPERTY(EditAnywhere, Category = "Media")
    UMediaSource* MediaSource;

    // 创建的媒体播放器和纹理（仅用于演示，实际可能通过蓝图管理）
    UPROPERTY(VisibleAnywhere, Category = "Media")
    UMediaPlayer* MediaPlayer;

    UPROPERTY(VisibleAnywhere, Category = "Media")
    UMediaTexture* MediaTexture;
};
```

```cpp
// MyMediaActor.cpp
#include "MyMediaActor.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"
#include "MediaSource.h"

AMyMediaActor::AMyMediaActor()
{
    PrimaryActorTick.bCanEverTick = false;
    // 在构造函数中创建播放器和纹理对象
    MediaPlayer = CreateDefaultSubobject<UMediaPlayer>(TEXT("MediaPlayer"));
    MediaTexture = CreateDefaultSubobject<UMediaTexture>(TEXT("MediaTexture"));
    MediaTexture->SetMediaPlayer(MediaPlayer);
}

void AMyMediaActor::BeginPlay()
{
    Super::BeginPlay();

    if (MediaSource && MediaPlayer)
    {
        // 打开源并播放
        MediaPlayer->OpenSource(MediaSource);
        // 注意：实际播放需要等待 IsReady，此处简化逻辑
        if (MediaPlayer->IsReady())
        {
            MediaPlayer->Play();
            UE_LOG(LogTemp, Log, TEXT("Media playback started via AVF backend on Apple platform."));
        }
    }
}
```

## 模块依赖

从 `Build.cs` 分析，该插件依赖于媒体框架的核心模块以及苹果平台的特定框架。

| 模块 | 用途 |
|---|---|
| `Media` | 媒体框架核心接口 |
| `MediaAssets` | 提供 `MediaPlayer`, `MediaTexture` 等资产类 |
| `MediaUtils` | 媒体工具函数 |
| `AVFoundation` (苹果框架) | 插件的核心播放实现框架 |
| `CoreMedia` (苹果框架) | 苹果平台媒体时间、样本等基础数据类型 |

*注：部分依赖可能为平台特定（通过`PlatformAllowList`限定），开发者通常无需直接链接。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `1951db93` | [AvfMedia] Default H.264 file playback to BGRA decode and provide CPU accessible buffer for media fi | 优化 H.264 解码为 BGRA 格式，并提供 CPU 可访问的缓冲区。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式 `UE_LOG` 宏迁移到新的 `UE_LOGF` 格式化日志。 |
| 2026-04-13 | `b905d146` | Fix/Silence unreachable code warnings | 修复或消除“不可达代码”的编译器警告。 |
| 2026-04-01 | `39223292` | [AvfMedia] Provide CPU buffer alongside GPU texture when using FAvfMediaCapturePlayer | 在使用 `FAvfMediaCapturePlayer` 时，同时提供 CPU 缓冲区和 GPU 纹理。 |
| 2026-02-05 | `d5be7e14` | Fixed printfs. | 修复了 `printf` 风格的输出语句（可能转向使用标准 UE 日志）。 |

### 维护评价

- **活跃维护**：该插件在 2026 年仍有多次功能性更新（如解码优化、双缓冲支持）和代码质量改进。
- **状态稳定**：作为苹果平台媒体播放的基础后端，它持续适配引擎内部 API 变更（如日志宏迁移）并修复警告。
- **推荐使用**：对于需要在 iOS、macOS 或 tvOS 上播放媒体的项目，本插件是**默认且推荐**的媒体播放后端，它经过了 Epic 的持续维护和优化。
- **注意**：它是一个平台特定插件，仅在目标平台为 `IOS`, `Mac`, `TVOS` 时生效。在 Windows 或 Linux 等其他平台上，引擎会使用其他后端（如 `WmfMedia`）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AvfMedia)
- [官方文档](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AvfMedia/Tests) (通常位于插件目录或 `Engine/Tests` 下)