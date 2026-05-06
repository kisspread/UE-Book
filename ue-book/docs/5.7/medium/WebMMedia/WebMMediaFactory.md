# WebM Video Player

> Description from .uplugin (partial): *No description field available in provided data, but based on functionality:* Provides playback of WebM media files (VP8/VP9 video, Vorbis/Opus audio) using the libwebm and libvpx libraries.

| 属性 | 值 |
|---|---|
| 中文名 | WebM 视频播放器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `WebMMedia` (RuntimeNoCommandlet), `WebMMediaEditor` (Runtime), `WebMMediaFactory` (Runtime), `libwebm` (External) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-02 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/WebMMedia) | |

## 用途

WebMMedia 插件扩展了 UE 的媒体框架（`IMediaPlayer` 接口），使其能够播放 **WebM 格式**的媒体文件。WebM 是一种开放的媒体文件格式，通常使用 VP8 或 VP9 视频编码以及 Vorbis 或 Opus 音频编码。该插件通过集成第三方库 `libwebm`（解码 WebM 容器）和 `libvpx`（解码 VP8/VP9 视频）来实现。

**解决的问题：** 标准 UE 媒体播放器（如 Windows 上的 WmfMedia）通常不支持 WebM 格式。如果你需要播放 WebM 视频（例如从浏览器录制或来自开源视频源），此插件是必要的。

**为什么存在：** 满足对开放格式媒体播放的需求，特别是跨平台场景（虽然当前插件仅在 Win64 及部分平台启用）。

## 使用场景

- 在你的游戏中播放 **VP8/VP9 编码的视频**（例如过场动画、广告、教学内容）。
- 需要处理 **低延迟流媒体** 或点播 WebM 资源。
- 使用 **Media Plate** 或 **Media Texture** 组件渲染来自 WebM 文件的视频。
- 在编辑器中对 WebM 文件进行 **预览和播放**（通过媒体播放器资产）。

## 蓝图用法

WebMMedia 插件在蓝图层面不暴露专属节点，而是通过 UE 标准的 **Media Player** 和 **Media Texture** 蓝图节点工作。当你正确启用插件后，创建一个 **Media Player** 资产，将“文件/URL”媒体源指向一个 `.webm` 文件，然后使用标准节点进行播放控制。

### 核心节点（Media Player 通用）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open Source` | 打开指定媒体源（支持文件路径或 URL） | `MediaPlayer` |
| `Play` | 开始播放 | `MediaPlayer` |
| `Pause` | 暂停播放 | `MediaPlayer` |
| `Set Loop` | 设置是否循环播放 | `MediaPlayer` |
| `Get Duration` | 获取媒体总时长（秒） | `MediaPlayer` |
| `Is Playing` | 检查是否正在播放 | `MediaPlayer` |
| `On Media Opened` | 媒体成功打开时触发的委托 | `MediaPlayer` |
| `On Media Failed` | 媒体打开或播放失败时触发的委托 | `MediaPlayer` |

### 使用示例（蓝图描述）

1. **加载并播放 WebM 文件**
   - 在关卡中放置一个 **Media Player** 变量（类型为 `MediaPlayer` 资产）。
   - 在 Event BeginPlay 中调用 `Open Source`，节点输入选择“文件”，并填入 `.webm` 文件的绝对路径或打包后的相对路径（如 `/Game/Videos/Intro.webm`）。
   - 连接 `Play` 节点（使用 `Open Source` 的输出执行线）即可开始播放。
   - 可选：创建一个 **Media Texture** 资产，将其关联到同一个 Media Player，然后将纹理拖入材质，在 3D 控件（如平面）上显示视频。

2. **播放失败处理**
   - 使用 `On Media Failed` 事件绑定到 Media Player，当打开失败时打印警告日志或显示 UI 提示。

> **注意：** WebMMedia 是一个**实验性**插件，必须先在“插件”设置中手动启用（默认禁用）。

## C++ 用法

### 头文件引入

```cpp
// 媒体播放器相关
#include "MediaPlayer.h"
#include "MediaSource.h"
#include "MediaPlayerOptions.h"
#include "IMediaPlayer.h"
#include "IMediaTracks.h"

// WebM 工厂模块可能需要的日志
#include "WebMMediaFactoryPrivate.h"
```

### 基本用法

**通过工厂创建并播放 WebM 源：** （使用文件路径）

```cpp
// 从文件路径创建媒体源
UMediaSource* MediaSource = UMediaSource::CreateFromFilePath(TEXT("/Game/Videos/Intro.webm"));

// 获取全局 MediaPlayer 实例（假设已创建 UMediaPlayer 子对象）
UMediaPlayer* MediaPlayer = CreateDefaultSubobject<UMediaPlayer>(TEXT("WebMPlayer"));

// 打开媒体源
bool bOpened = MediaPlayer->OpenSource(MediaSource);
if (bOpened)
{
    MediaPlayer->Play();
}
else
{
    UE_LOG(LogWebMMediaFactory, Warning, TEXT("Failed to open WebM media source."));
}
```

*来源：基于常见媒体播放模式，且 WebMMedia 遵循标准 IMediaPlayer 接口。*

**低层级创建播放器并检测格式：** （使用 `IMediaPlayerFactory`）

```cpp
// 获取媒体模块，遍历所有播放器工厂
IMediaModule* MediaModule = FModuleManager::LoadModulePtr<IMediaModule>("Media");
if (MediaModule)
{
    TArray<IMediaPlayerFactory*> Factories = MediaModule->GetPlayerFactories();
    for (IMediaPlayerFactory* Factory : Factories)
    {
        if (Factory->CanPlayUrl(TEXT("file:///game/videos/test.webm"), nullptr))
        {
            // 该工厂支持 WebM，可以创建播放器
            IMediaPlayerPtr Player = Factory->CreatePlayer();
            // ... 后续设置和播放
            break;
        }
    }
}
```

*来源：通用示例，来自其他媒体插件文档。*

### 进阶用法

**自定义媒体播放器配置：** WebMMedia 在某些情况下可能需要设置解码选项（如线程数、丢弃帧策略）。这些参数通常通过 `IMediaSink` 接口传递，或通过 `UMediaPlayer::SetDesiredPlayerName` 指定播放器名称 `FName("WebMMedia")`。

```cpp
// 强制使用 WebM 播放器
MediaPlayer->SetDesiredPlayerName(TEXT("WebMMedia"));
MediaPlayer->OpenSource(MySource);
```

## Demo 示例

以下是一个完整的 Actor 组件示例，在 C++ 中嵌入 WebM 视频播放：

**MyMediaActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"
#include "MyMediaActor.generated.h"

UCLASS()
class AMyMediaActor : public AActor
{
    GENERATED_BODY()

public:
    AMyMediaActor();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Media")
    UMediaPlayer* MediaPlayer;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Media")
    UMediaTexture* MediaTexture;
};
```

**MyMediaActor.cpp**
```cpp
#include "MyMediaActor.h"
#include "MediaSource.h"
#include "Components/StaticMeshComponent.h"

AMyMediaActor::AMyMediaActor()
{
    PrimaryActorTick.bCanEverTick = false;

    MediaPlayer = CreateDefaultSubobject<UMediaPlayer>(TEXT("WebMMediaPlayer"));
    MediaTexture = CreateDefaultSubobject<UMediaTexture>(TEXT("VideoTexture"));
    MediaTexture->SetMediaPlayer(MediaPlayer); // 关联

    // 创建一个静态网格并赋予材质，用于显示视频
    UStaticMeshComponent* Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("DisplayMesh"));
    RootComponent = Mesh;

    // 材质动态加载（假设已有一个材质使用 MediaTexture）
    static ConstructorHelpers::FObjectFinder<UMaterialInterface> MatFinder(TEXT("/Game/Materials/MediaScreenMaterial"));
    if (MatFinder.Succeeded())
    {
        // 材质需要在蓝图实例中替换媒体纹理，此处略
    }
}

void AMyMediaActor::BeginPlay()
{
    Super::BeginPlay();

    // 从 Content 目录加载 WebM 源
    UMediaSource* Source = UMediaSource::CreateFromFilePath("/Game/Videos/Intro.webm");
    if (Source && MediaPlayer->OpenSource(Source))
    {
        MediaPlayer->Play();
        UE_LOG(LogTemp, Log, TEXT("WebM video started."));
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open WebM source."));
    }
}
```

## 模块依赖

**要使用 WebMMedia 插件，你的模块需要依赖以下内容：**

| 模块 | 用途 |
|---|---|
| `Media` | 核心媒体框架，提供 `IMediaPlayer`、`IMediaPlayerFactory` 等接口 |
| `MediaAssets` | 提供了蓝图可见的 `UMediaPlayer`、`UMediaTexture` 等资产类 |
| `LibVpx` | VP8/VP9 视频解码器（通过 `WebMMedia` 模块间接依赖） |
| `libwebm` | WebM 容器解析器（外部模块，静态链接） |

**常见依赖已省略**（Core, CoreUObject, Engine 等）。

## 维护状态

### 近期更新

| 日期 | Hash | Commit 解读 |
|---|---|---|
| 2025-09-12 | `828f0392` | 修复：在 `Close()` 时清除所有成员，确保检测到无效轨道前正确移除内容 |
| 2025-08-29 | `32884de4` | 将 `RHICreateTexture` 替换为 `RHICmdList.CreateTexture`（渲染跨代改造） |
| 2025-07-10 | `abb369e2` | 为 `gen.cpp` 对应的源文件添加 `UE_INLINE_GENERATED_CPP_BY_NAME` 宏（代码规范） |
| 2025-06-02 | `3643a063` | 移除旧的 libwebm Linux 构建文件 |
| 2025-06-02 | `8e5bc4b0` | 更新 libwebm Linux 构建文件 |

### 维护评价

- **创建时间：** 2025-06-02（从提供的元数据看，实际创建可能更早，但最近进行了构建文件清理）。
- **近期更新：** 2025-09 仍有功能修复（清除轨道），说明插件**仍在维护**。
- **活跃度：** 近 3 个月有两次实质性代码更新（渲染改造、bug 修复），维护状态良好。
- **限制：** 本插件为**实验性**（IsBetaVersion=true），默认禁用，可能在未来版本中接口发生变动。已知问题可能包括：部分平台不支持（仅 Win64 列入允许列表），以及 VP8/VP9 的硬件加速有限。
- **推荐使用：** 适合需要 WebM 播放的项目，但建议在真实设备上充分测试。生产环境使用需评估稳定性和许可（libvpx 采用 BSD 许可，兼容商业项目）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/WebMMedia)
- [UPROPERTY 参考（官方文档）](https://docs.unrealengine.com/5.3/en-US/)（暂无特定 WebMMedia 文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/WebMMedia/Tests)（可能不存在公开测试）