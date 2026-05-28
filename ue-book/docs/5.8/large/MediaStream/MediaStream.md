# Media Stream

> Content/type agnostic chainable media proxy with media player integration.

| 属性 | 值 |
|---|---|
| 中文名 | 媒体流 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `MediaStream` (Runtime), `MediaStreamEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-10 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MediaStream) | |

## 用途

MediaStream 插件旨在为虚幻引擎提供一个统一、可扩展的媒体处理框架。它解决了从多种不同来源（如本地文件、资产、子对象、托管流）播放媒体时，需要编写大量重复且与特定媒体类型耦合的代码的问题。通过引入 **Scheme (方案)** 和 **Object (对象)** 处理器的链式代理机制，该插件将媒体的“来源解析”与“播放创建”分离开来。开发者只需通过一个统一的 `UMediaStream` 对象设置媒体源（如 `file://path` 或 `asset://path`），插件会自动根据 scheme 和路径找到合适的处理器来创建对应的媒体播放器。这使得游戏或应用中的过场动画、多媒体播放器、实时监控画面等功能能够轻松支持多种媒体格式和来源，而无需修改核心逻辑。

## 使用场景

-   **游戏内过场动画系统**：需要从本地文件、项目资产库或实时编码流中加载视频。使用 MediaStream 可以统一设置流程，通过改变 scheme（如 `file`、`asset`、`rtsp`）即可切换来源。
-   **多媒体播放器应用**：支持打开本地文件、浏览资产库中的媒体、甚至连接到直播流。MediaStream 提供了统一的接口来创建和控制这些播放实例。
-   **需要代理或镜像媒体流的场景**：例如，一个 UI 元素需要显示另一个 3D 世界中屏幕的实时画面。可以通过 `UMediaStreamProxyPlayer` 将一个 MediaStream 的输出代理给另一个，实现画面的“镜像”或“分发”。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Make Media Source From File` | 从一个文件路径创建媒体源。 | `UMediaStreamSourceBlueprintLibrary` |
| `Make Media Source From Asset` | 从一个软引用资产（如 UMediaSource）创建媒体源。 | `UMediaStreamSourceBlueprintLibrary` |
| `Make Media Source From Subobject` | 从一个 UObject 创建媒体源。 | `UMediaStreamSourceBlueprintLibrary` |
| `Set Source` | 设置 MediaStream 的媒体源，开始加载和创建播放器。 | `UMediaStream` |
| `Play` / `Pause` | 控制当前关联的媒体播放器的播放状态。 | `IMediaStreamPlayer` |
| `Set Playback State` | 通过枚举状态（Play/Pause）控制播放。 | `IMediaStreamPlayer` |
| `Get Media Texture` | 获取用于渲染媒体的纹理对象。 | `IMediaStreamPlayer` |
| `Create Source (Scheme)` | 通过 Scheme Handler 子系统，根据 scheme 和 path 创建媒体源。 | `UMediaStreamSchemeHandlerSubsystem` |

### 使用示例（蓝图描述）

1.  **从文件播放视频**：
    *   创建一个 `UMediaStream` 对象。
    *   调用 `Make Media Source From File` 节点，输入视频文件的绝对路径（如 `C:\Video.mp4`），得到一个 `FMediaStreamSource` 结构体。
    *   调用 MediaStream 的 `Set Source` 节点，传入上一步得到的源。
    *   可以通过 `Play` 节点开始播放，并使用 `Get Media Texture` 获取的纹理赋给一个 `UMedia` 材质参数来显示画面。

2.  **从资产库中的 MediaSource 资产播放**：
    *   创建一个 `UMediaStream` 对象。
    *   通过资产引用获取一个 `TSoftObjectPtr<UMediaSource>`。
    *   调用 `Make Media Source From Asset` 节点，传入该资产软引用，得到源。
    *   调用 MediaStream 的 `Set Source` 节点设置源。

## C++ 用法

### 头文件引入

```cpp
#include "MediaStream.h"
#include "MediaStreamSourceBlueprintLibrary.h"
```

### 基本用法

以下示例展示了如何在 C++ 中创建和使用 MediaStream 播放本地文件。

```cpp
// (Source: 基于公共 API 推断)
void UMyClass::PlayVideoWithMediaStream()
{
    // 1. 创建一个 MediaStream 对象
    UMediaStream* MediaStream = NewObject<UMediaStream>(this);

    // 2. 创建一个媒体源（这里使用文件 scheme）
    FMediaStreamSource Source = UMediaStreamSourceBlueprintLibrary::MakeMediaSourceFromFile(
        MediaStream, 
        TEXT("C:/Content/MyVideo.mp4")
    );

    // 3. 设置源并开始播放
    if (MediaStream->SetSource(Source))
    {
        // 获取播放器接口并控制播放
        TScriptInterface<IMediaStreamPlayer> Player = MediaStream->GetPlayer();
        if (Player)
        {
            Player->Play();
        }

        // 获取媒体纹理用于渲染
        UMediaTexture* Texture = Player->GetMediaTexture();
        // ... 将 Texture 设置给材质等。
    }
}
```

### 进阶用法：注册自定义 Scheme Handler

你可以创建自定义的 Scheme Handler 来支持新的媒体来源协议（如 `rtmp://`）。

```cpp
// (Source: 基于 IMediaStreamSchemeHandler 接口推断)
#include "IMediaStreamSchemeHandler.h"
#include "MediaStreamSchemeHandlerManager.h"

// 定义自定义 Handler 类
class FMediaStreamRtmpSchemeHandler : public IMediaStreamSchemeHandler
{
public:
    static const FLazyName Scheme; // e.g., "rtmp"

    virtual FMediaStreamSource CreateSource(UObject* InOuter, const FString& InPath) override
    {
        // 解析 RTMP 路径，创建一个 FMediaStreamSource
        FMediaStreamSource NewSource;
        NewSource.Scheme = Scheme;
        NewSource.Path = InPath;
        // NewSource.Object = ... (可能需要创建一个 UObject 来持有 RTMP 连接信息)
        return NewSource;
    }

    virtual UMediaPlayer* CreateOrUpdatePlayer(const FMediaStreamSchemeHandlerCreatePlayerParams& InParams) override
    {
        // 创建一个支持 RTMP 的媒体播放器并配置它
        UMediaPlayer* Player = InParams.CurrentPlayer;
        if (!Player)
        {
            Player = NewObject<UMediaPlayer>(InParams.MediaStream);
        }
        // ... 配置 Player 打开 RTMP 流
        // Player->OpenSource(...)
        return Player;
    }

#if WITH_EDITOR
    virtual void CreatePropertyCustomization(UMediaStream* InMediaStream, IMediaStreamSchemeHandler::FCustomWidgets& InOutCustomWidgets) override
    {
        // 提供自定义编辑器 UI
    }
#endif
};

// 注册 Handler (通常在模块 StartupModule 中)
void FMyModule::StartupModule()
{
    FMediaStreamSchemeHandlerManager::Get().RegisterSchemeHandler<FMediaStreamRtmpSchemeHandler>(FMediaStreamRtmpSchemeHandler::Scheme);
}
```

## Demo 示例

一个完整的、可编译的最小示例，演示在 Actor 组件中使用 MediaStream。

### MyMediaStreamActorComponent.h
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MediaStream.h"
#include "MyMediaStreamActorComponent.generated.h"

UCLASS(ClassGroup=(MediaStream), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyMediaStreamActorComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyMediaStreamActorComponent();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Media")
    TObjectPtr<UMediaStream> MediaStream;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Media")
    FString VideoFilePath;
};
```

### MyMediaStreamActorComponent.cpp
```cpp
#include "MyMediaStreamActorComponent.h"
#include "MediaStreamSourceBlueprintLibrary.h"
#include "MediaTexture.h"
#include "MediaPlayer.h"

UMyMediaStreamActorComponent::UMyMediaStreamActorComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
    MediaStream = CreateDefaultSubobject<UMediaStream>(TEXT("MediaStream"));
}

void UMyMediaStreamActorComponent::BeginPlay()
{
    Super::BeginPlay();

    if (!VideoFilePath.IsEmpty())
    {
        FMediaStreamSource Source = UMediaStreamSourceBlueprintLibrary::MakeMediaSourceFromFile(
            MediaStream,
            VideoFilePath
        );

        if (MediaStream->SetSource(Source))
        {
            // 立即播放
            TScriptInterface<IMediaStreamPlayer> Player = MediaStream->GetPlayer();
            if (Player)
            {
                Player->Play();
            }
            UE_LOG(LogTemp, Log, TEXT("MediaStream: Started playing %s"), *VideoFilePath);
        }
    }
}

void UMyMediaStreamActorComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (MediaStream)
    {
        MediaStream->Close();
    }
    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MediaCompositing` | 插件依赖项，提供媒体合成相关的基础功能。 |
| `MediaPlayerEditor` | 插件依赖项，为媒体播放器提供编辑器支持。 |
| `LevelSequenceEditor` | 插件依赖项，可能与在关卡序列中控制媒体流有关。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `6ba34f64` | [MediaStream] Revert Sample Queue approach; bind MediaTexture directly to player before opening | 回滚采样队列方案，在打开前直接将媒体纹理绑定到播放器。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，代码因双精度常量截断为浮点数而产生的警告。 |
| 2026-05-12 | `4fc7c47c` | [MediaViewer] Fix drop-target image identification | 修复了媒体查看器中拖放目标图片识别的问题。 |
| 2026-05-12 | `82b74724` | [MediaStream] Adding a cache setting override (like MediaPlate does) for using a local cache when us | 为媒体流添加缓存设置覆盖（类似 MediaPlate），以在使用本地缓存时生效。 |
| 2026-05-12 | `aa0f454d` | [MediaViewer] Implementing a Tile visibility provider for media viewer that support zooming, panning | 为媒体查看器实现了图块可见性提供程序，以支持缩放和平移。 |

### 维护评价

该插件处于**活跃维护**状态。它于 2025 年初创建，至今约一年，最近一周内（2026年5月）有多次功能性提交，包括缓存优化、绑定逻辑调整和编译问题修复。作为一个 `IsExperimentalVersion = true` 且默认禁用的实验性插件，它仍在积极开发和完善中。从提交记录看，Epic 工程师正在修复问题并增加新功能（如本地缓存支持）。目前没有发现长期无更新的迹象。**推荐**在了解其为实验性状态的前提下，在需要灵活媒体源处理的项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MediaStream)
- [官方文档]() (暂无)
- [测试用例]() (未在提供的源码路径中发现)