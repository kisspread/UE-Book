# WebM Video Player

> Implements the WebM media player using the libvpx and libwebm libraries.

| 属性 | 值 |
|---|---|
| 中文名 | WebM 视频播放器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `WebMMedia` (Runtime), `WebMMediaEditor` (Runtime), `WebMMediaFactory` (Runtime), `libwebm` (External) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-02 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/WebMMedia) | |

## 用途

此插件提供对 WebM 容器格式的原生媒体播放支持，包括 VP8 / VP9 视频编码和 Vorbis / Opus 音频编码。它实现了 `IMediaPlayer` 接口，可以无缝集成到 UE5 的媒体框架中，与 `Media Player` 资产、`File Media Source` 等配合使用。其核心由一个基于 `libwebm`（容器解析）和 `libvpx`（视频解码）的解码管线构成，支持在编辑器和运行时播放 `.webm` 文件。

**为什么存在？**  
标准 UE 媒体框架不原生支持 WebM 格式。此插件弥补了这一空白，允许项目使用开源、高质量的视频格式，而无需依赖第三方平台解码器（如 Windows Media Foundation 对 VP9 支持有限）。

## 使用场景

- **游戏过场动画**：使用 WebM（VP9 编码）播放高清过场，体积比 H.264 更小，且无需额外授权费用。
- **UI 视频背景**：在 HUD 或 3D 场景中渲染 WebM 视频作为动态背景或材质贴花。
- **跨平台回放**：WebM 格式已广泛支持，适合需要一致行为的多平台项目（Win64、Linux、macOS）。
- **自定义媒体管线**：需要直接访问解码后的音频/视频帧数据，用于实时处理或分析。

## 蓝图用法

由于该插件完全通过 UE 媒体框架暴露功能，**没有暴露任何自定义蓝图节点**。所有操作均通过标准的媒体相关蓝图节点完成。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `创建媒体播放器` | 创建并初始化一个 WebM 媒体播放器（需指定媒体源） | `MediaPlayer` |
| `打开源` | 将媒体播放器连接到文件 URL 或媒体源资产 | `MediaPlayer` |
| `播放` | 开始播放 | `MediaPlayer` |
| `暂停` | 暂停播放 | `MediaPlayer` |
| `设置循环` | 切换循环模式 | `MediaPlayer` |
| `获取时间` | 获取当前播放进度 | `MediaPlayer` |
| `获取轨道信息` | 获取音频/视频轨道列表 | `MediaPlayer` |
| `选择轨道` | 按索引选择活动的音频/视频轨道 | `MediaPlayer` |

### 使用示例（蓝图描述）

1. 在关卡蓝图中放置一个 `MediaPlayer` 对象实例。
2. 创建一个 `FileMediaSource` 资产，将其 `FilePath` 设置为 `.webm` 文件（位于 `/Game/Movies/` 下）。
3. 使用 **Open Source** 节点连接到该 `MediaFileSource`，并指定之前创建的 `MediaPlayer`。
4. 播放时调用 `Play` 节点。
5. （可选）通过 `OnMediaOpened` 事件获取轨道列表，并使用 `Select Track` 手动选择音视频轨。
6. 将 `MediaTexture` 绑定到一个材质，该材质赋予给 3D 平面或 UMG 图像，即可实时渲染视频。

## C++ 用法

### 头文件引入

```cpp
#include "IWebMMediaModule.h"
#include "IMediaPlayer.h"
#include "IMediaEventSink.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"
```

### 基本用法

通过模块接口创建播放器并播放文件（简化版，完整实现需处理事件）。

```cpp
// 获取模块实例
IWebMMediaModule* WebMMediaModule = FModuleManager::LoadModulePtr<IWebMMediaModule>("WebMMedia");
if (WebMMediaModule)
{
    // 创建播放器（需传入事件接收器，此处用 FMediaPlayerFacade 简写）
    TSharedPtr<IMediaPlayer, ESPMode::ThreadSafe> Player = WebMMediaModule->CreatePlayer(EventSink);

    // 打开文件
    FString FilePath = FPaths::ProjectContentDir() / TEXT("Movies/Intro.webm");
    if (Player->Open(FilePath, nullptr))
    {
        // 播放器已就绪，可通过 IMediaControls 控制播放
    }
}
```

来源：`Engine/Plugins/Media/WebMMedia/Source/WebMMedia/Public/IWebMMediaModule.h`

### 进阶用法：直接访问解码后的帧数据

使用 `FWebMContainer` 手动解析 WebM 容器，获取原始帧并进行自定义处理（绕过标准媒体管线）。

```cpp
#include "WebMContainer.h"
#include "WebMMediaFrame.h"

FWebMContainer Container;
if (Container.Open(TEXT("/Game/Movies/Clip.webm")))
{
    TArray<TSharedPtr<FWebMFrame>> AudioFrames, VideoFrames;
    FTimespan ReadDuration = FTimespan::FromSeconds(0.1); // 每次读取 100ms 数据
    Container.ReadFrames(ReadDuration, AudioFrames, VideoFrames);

    // 处理视频帧（原始 VPX 数据，位于 FWebMFrame::Data）
    for (auto& Frame : VideoFrames)
    {
        // 传递给自己的解码器或分析
        ProcessRawFrame(Frame->Data, Frame->Time);
    }
}
```

> 注意：直接使用容器类需要额外注意线程安全，推荐在单独线程中读取。

来源：`Engine/Plugins/Media/WebMMedia/Source/WebMMedia/Public/WebMContainer.h`

## Demo 示例

以下是一个完整的 C++ Actor 组件示例，使用插件播放 WebM 视频并渲染到材质。

### VideoPlayerComponent.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"
#include "VideoPlayerComponent.generated.h"

UCLASS(ClassGroup=(Media), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UVideoPlayerComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UVideoPlayerComponent();

    // 开始播放指定路径的 .webm 文件
    UFUNCTION(BlueprintCallable, Category = "Video")
    void PlayWebM(const FString& FilePath);

    // 暂停/继续
    UFUNCTION(BlueprintCallable, Category = "Video")
    void Pause();
    UFUNCTION(BlueprintCallable, Category = "Video")
    void Resume();

    // 获取关联的 MediaTexture（用于材质）
    UFUNCTION(BlueprintCallable, Category = "Video")
    UMediaTexture* GetMediaTexture() const { return MediaTexture; }

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    UPROPERTY()
    UMediaPlayer* MediaPlayer;

    UPROPERTY()
    UMediaTexture* MediaTexture;
};
```

### VideoPlayerComponent.cpp

```cpp
#include "VideoPlayerComponent.h"
#include "MediaSource.h"
#include "FileMediaSource.h"
#include "IMediaControls.h"

UVideoPlayerComponent::UVideoPlayerComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
    MediaPlayer = CreateDefaultSubobject<UMediaPlayer>(TEXT("MediaPlayer"));
    MediaTexture = CreateDefaultSubobject<UMediaTexture>(TEXT("MediaTexture"));
    MediaTexture->SetMediaPlayer(MediaPlayer);
}

void UVideoPlayerComponent::PlayWebM(const FString& FilePath)
{
    UFileMediaSource* MediaSource = NewObject<UFileMediaSource>();
    MediaSource->SetFilePath(FilePath);

    if (MediaPlayer->OpenSource(MediaSource))
    {
        MediaPlayer->Play();
    }
}

void UVideoPlayerComponent::Pause()
{
    if (MediaPlayer->CanPause())
    {
        MediaPlayer->Pause();
    }
}

void UVideoPlayerComponent::Resume()
{
    if (MediaPlayer->CanPlay())
    {
        MediaPlayer->Play();
    }
}

void UVideoPlayerComponent::BeginPlay()
{
    Super::BeginPlay();
}

void UVideoPlayerComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (MediaPlayer)
    {
        MediaPlayer->Close();
    }
    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

以下为使用 WebM Video Player 时必须添加的依赖项（常见模块如 `Core`, `Engine` 已省略）。

| 模块 | 用途 |
|---|---|
| `Media` | UE 媒体框架核心接口（`IMediaPlayer`, `IMediaControls` 等） |
| `MediaAssets` | `UMediaPlayer`, `UMediaTexture` 等蓝图媒体资产 |
| `MediaUtils` | 媒体采样队列与对象池支持 |
| `RenderCore` | 解码后视频帧的 RHI 纹理创建与转换 |
| `RHI` | 图形资源抽象（`FRHITexture`, `FRHICommandList`） |
| `LibVpx` | VP8/VP9 视频解码器库 |
| `libwebm` | WebM 容器格式解析（第三方库，由插件内置） |

> **注意**：`WebMMediaEditor` 模块（用于编辑器快捷键等）仅运行时加载，无额外依赖；`WebMMediaFactory` 模块注册 `FileMediaSource` 工厂，依赖 `MediaAssets`。

## 维护状态

### 近期更新

- 2025-09-12 `828f0392` — WebMMedia: 在 `Close()` 时清除所有成员，移除在检测到错误之前添加的轨道
- 2025-08-29 `32884de4` — 将更多 `RHICreateTexture` 调用改为 `RHICmdList.CreateTexture`
- 2025-07-10 `abb369e2` — 为包含相应 .gen.cpp 的源文件添加 `UE_INLINE_GENERATED_CPP_BY_NAME`
- 2025-06-02 `3643a063` — 移除旧的 libwebm Linux 构建文件
- 2025-06-02 `8e5bc4b0` — 更新 libwebm 的 Linux 构建

### 维护评价

此插件相对较新（2025年6月创建），属于实验性（`IsBetaVersion=true`）。近期更新主要修复了 `Close()` 的资源清理问题，并适配新的 RHI 纹理创建 API。未发现废弃标记或明显缺陷。由于仍标记为 Beta，且缺少大规模功能迭代（如 seek precision、side-by-side 3D 支持等），建议在需要 WebM 回放的项目中谨慎使用，并关注后续版本稳定性更新。推荐用于测试和非关键功流程。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/WebMMedia)
- [官方文档](https://docs.unrealengine.com/5.4/zh-CN/media-framework-in-unreal-engine/)（媒体框架通用文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/WebMMedia/Tests)（若存在，否则查看 Engine 内部测试）