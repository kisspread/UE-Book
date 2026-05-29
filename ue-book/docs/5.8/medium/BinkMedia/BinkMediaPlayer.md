# Bink Media

> Implements a media player using Bink.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | Bink 媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `BinkMediaPlayer` (Runtime), `BinkMediaPlayerEditor` (Editor), `BinkMediaPlayerSDK` (External) |
| 实验性 | 否 |
| 创建时间 | 2021-06-08 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/BinkMedia) | |

## 用途
该插件将 RAD Game Tools 的 Bink 高性能视频编解码器集成到 Unreal Engine 5 中。它解决了在游戏内播放高质量、高效率预渲染视频的需求，特别适用于开场动画、过场电影、加载屏幕以及游戏中的全屏视频播放场景。与 UE 原生媒体框架不同，Bink 以其极高的解码效率、广泛的平台支持和紧凑的文件体积著称，是游戏行业播放内置视频的常用解决方案。插件通过提供 `UBinkMediaPlayer` 核心类和 `UBinkMediaTexture` 纹理资产，将 Bink 播放功能无缝融入引擎的媒体和渲染系统。

## 使用场景
- 你需要在游戏中播放开场动画或过场电影 → 使用 `UBinkMediaPlayer` 播放 `.bik` 文件
- 你需要在 UI 上动态显示视频，例如游戏内的电视屏幕 → 使用 `UBinkMediaTexture` 并通过材质系统渲染
- 你需要以不同缓冲模式（流式、预加载）优化内存和加载性能 → 配置 `BinkBufferMode`
- 你需要以叠加层模式直接渲染视频，绕过 UE 渲染管线以获得最佳性能或特定效果 → 配置 `BinkDrawStyle`
- 你需要配置 5.1/7.1 环绕声或特定语言音轨 → 配置 `BinkSoundTrack`
- 你需要播放用于加载屏幕的视频 → 使用 `FBinkMovieStreamer` 接口

## 蓝图用法
蓝图功能主要集中在 `UBinkMediaPlayer`、`UBinkMediaTexture` 和 `UBinkFunctionLibrary` 类中。

### 核心节点
| 节点 | 说明 | 所在类 |
|---|---|---|
| `OpenUrl` | 打开指定的媒体文件或 URL。 | `UBinkMediaPlayer` |
| `CloseUrl` | 关闭当前媒体并释放资源。 | `UBinkMediaPlayer` |
| `Play` | 开始或恢复媒体播放。 | `UBinkMediaPlayer` |
| `Pause` | 暂停媒体播放。 | `UBinkMediaPlayer` |
| `Stop` | 停止播放并完全卸载视频。 | `UBinkMediaPlayer` |
| `SetVolume` | 设置音量（0.0 到 1.0）。 | `UBinkMediaPlayer` |
| `SetLooping` | 设置是否循环播放。 | `UBinkMediaPlayer` |
| `Seek` | 跳转到指定的播放时间。 | `UBinkMediaPlayer` |
| `Draw` | 将当前帧绘制到指定的纹理资源上。 | `UBinkMediaPlayer` |
| `GetDuration` | 获取视频总时长。 | `UBinkMediaPlayer` |
| `GetTime` | 获取当前播放时间。 | `UBinkMediaPlayer` |
| `IsPlaying` | 检查是否正在播放。 | `UBinkMediaPlayer` |
| `SetMediaPlayer` | 为 `BinkMediaTexture` 设置关联的播放器。 | `UBinkMediaTexture` |
| `Clear` | 将媒体纹理清空为透明黑色。 | `UBinkMediaTexture` |
| `Bink_DrawOverlays` | 绘制所有待处理的 Bink 叠加层渲染。 | `UBinkFunctionLibrary` |

### 使用示例（蓝图描述）
1.  **基本播放**：创建一个 `UBinkMediaPlayer` 资产，设置其 `URL` 属性为视频路径。在关卡蓝图中，获取该资产，调用 `OpenUrl`，然后调用 `Play`。监听 `OnMediaOpened` 和 `OnMediaReachedEnd` 事件来控制流程。
2.  **UI 视频**：创建一个 `UBinkMediaTexture` 资产，并将其 `MediaPlayer` 属性链接到上面创建的 `UBinkMediaPlayer` 资产。在 UI 蓝图（UMG Widget）中，使用该 `BinkMediaTexture` 作为图片或材质的纹理输入。播放器播放时，纹理内容会自动更新。
3.  **叠加层渲染**：将 `UBinkMediaPlayer` 的 `BinkDrawStyle` 属性设置为 `Overlay Fill Screen`。在每帧的 `Event Tick` 中，或在需要绘制的时机，调用 `Draw` 节点并传入渲染目标纹理（可为 null）。之后在 `Event Tick` 的末尾调用 `Bink_DrawOverlays` 来统一绘制所有叠加层。

## C++ 用法

### 头文件引入
```cpp
#include "BinkMediaPlayer.h"
#include "BinkMediaTexture.h"
// 底层纹理管理
#include "BinkRHI.h"
```

### 基本用法
播放视频并将其渲染到纹理。
```cpp
// 来源：基于 Public/BinkMediaPlayer.h 和 Private/BinkRHI.h 的用法推断
void AMyActor::PlayBinkVideo()
{
    // 1. 创建或获取 BinkMediaPlayer 对象
    UBinkMediaPlayer* BinkPlayer = NewObject<UBinkMediaPlayer>(this);
    
    // 2. 配置播放器属性
    BinkPlayer->URL = TEXT("/Game/Movies/MyMovie.bik");
    BinkPlayer->BinkBufferMode = EBinkMediaPlayerBinkBufferModes::BMASM_Bink_Stream;
    BinkPlayer->BinkSoundTrack = EBinkMediaPlayerBinkSoundTrack::BMASM_Bink_Sound_Simple;
    BinkPlayer->Looping = false;
    BinkPlayer->StartImmediately = true;

    // 3. 初始化并打开
    BinkPlayer->InitializePlayer();
    if (BinkPlayer->OpenUrl(BinkPlayer->URL))
    {
        UE_LOG(LogTemp, Log, TEXT("Bink video opened successfully."));
    }
}

// 在渲染时，将视频绘制到纹理
void AMyActor::RenderBinkToTexture(UTexture* TargetTexture)
{
    if (UBinkMediaPlayer* BinkPlayer = GetBinkPlayer()) // 假设的获取方法
    {
        if (BinkPlayer->IsPlaying())
        {
            // 可以在这里设置 tonemap, HDR 等参数
            BinkPlayer->Draw(TargetTexture, false, 10000, 1.0f, false, false);
        }
    }
}
```

### 进阶用法
直接使用 `FBinkTextures` 进行精细的渲染控制，适用于自定义渲染管线。
```cpp
// 来源：Private/BinkRHI.h
void AMyAdvancedRenderer::RenderBinkFrameDirectly(FRHICommandListImmediate& RHICmdList, FTextureRHIRef RenderTargetRHI)
{
    if (!MyBinkTextures || !MyBinkPlayer || !MyBinkPlayer->bnk) return;

    // 1. 设置渲染目标和绘制区域
    MyBinkTextures->SetRenderTarget(RenderTargetRHI.GetReference(), ERenderTargetLoadAction::EClear);
    MyBinkTextures->SetDrawPosition(0.0f, 0.0f, 1920.0f, 1080.0f); // 全屏绘制
    MyBinkTextures->SetSourceRect(0.0f, 0.0f, 1.0f, 1.0f); // 使用整个源纹理
    MyBinkTextures->SetAlphaSettings(1.0f, 0); // 不透明，无特殊标志
    MyBinkTextures->SetHDRSettings(0, 1.0f, 0); // 无色调映射

    // 2. 在渲染线程上解码和绘制
    // 注意：Bink 解码通常在游戏线程完成，这里主要是GPU绘制
    // 确保游戏线程已解码最新一帧 (BinkDoFrame)
    MyBinkTextures->Draw();
}
```

## Demo 示例
以下是一个最小化的 C++ Actor 示例，演示如何控制 Bink 视频播放并监听事件。

**BinkMediaPlayerDemoActor.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "BinkMediaPlayerDemoActor.generated.h"

class UBinkMediaPlayer;

UCLASS()
class ABinkMediaPlayerDemoActor : public AActor
{
    GENERATED_BODY()
    
public:    
    ABinkMediaPlayerDemoActor();

protected:
    virtual void BeginPlay() override;

public:    
    virtual void Tick(float DeltaTime) override;

    UPROPERTY(EditAnywhere, Category = "Bink")
    FString VideoURL = TEXT("/Game/Movies/Startup.bik");

    UPROPERTY(VisibleAnywhere, Category = "Bink")
    TObjectPtr<UBinkMediaPlayer> BinkPlayer;

    UFUNCTION()
    void OnBinkMediaOpened(FString OpenedUrl);

    UFUNCTION()
    void OnBinkMediaReachedEnd();

private:
    bool bNeedsPlay = false;
};
```

**BinkMediaPlayerDemoActor.cpp**
```cpp
#include "BinkMediaPlayerDemoActor.h"
#include "BinkMediaPlayer.h"

ABinkMediaPlayerDemoActor::ABinkMediaPlayerDemoActor()
{
    PrimaryActorTick.bCanEverTick = true;
}

void ABinkMediaPlayerDemoActor::BeginPlay()
{
    Super::BeginPlay();

    // 创建 Bink 播放器
    BinkPlayer = NewObject<UBinkMediaPlayer>(this, TEXT("DemoBinkPlayer"));
    
    // 配置
    BinkPlayer->URL = VideoURL;
    BinkPlayer->Looping = false;
    BinkPlayer->StartImmediately = false; // 我们手动控制播放时机
    BinkPlayer->BinkBufferMode = EBinkMediaPlayerBinkBufferModes::BMASM_Bink_Stream;

    // 绑定事件
    BinkPlayer->OnMediaOpened.AddDynamic(this, &ABinkMediaPlayerDemoActor::OnBinkMediaOpened);
    BinkPlayer->OnMediaReachedEnd.AddDynamic(this, &ABinkMediaPlayerDemoActor::OnBinkMediaReachedEnd);

    // 初始化播放器
    BinkPlayer->InitializePlayer();
    
    // 打开视频文件（非阻塞）
    if (BinkPlayer->OpenUrl(BinkPlayer->URL))
    {
        UE_LOG(LogTemp, Log, TEXT("Bink Demo: Open command sent for %s"), *VideoURL);
        bNeedsPlay = true;
    }
}

void ABinkMediaPlayerDemoActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    // 当视频打开后，延迟一帧开始播放，确保一切就绪
    if (bNeedsPlay && BinkPlayer->IsInitialized())
    {
        bNeedsPlay = false;
        BinkPlayer->Play();
        UE_LOG(LogTemp, Log, TEXT("Bink Demo: Playback started."));
    }
    
    // 你可以在这里调用 BinkPlayer->Draw() 来渲染到纹理，或者使用 BinkMediaTexture 资产自动更新
}

void ABinkMediaPlayerDemoActor::OnBinkMediaOpened(FString OpenedUrl)
{
    UE_LOG(LogTemp, Log, TEXT("Bink Demo: Media opened successfully: %s"), *OpenedUrl);
}

void ABinkMediaPlayerDemoActor::OnBinkMediaReachedEnd()
{
    UE_LOG(LogTemp, Log, TEXT("Bink Demo: Media playback reached end."));
    // 可以在此处触发过场结束、加载下一个关卡等逻辑
}
```

## 模块依赖
要使用 BinkMediaPlayer 模块，你的模块需要依赖以下**独特**的模块（常见依赖如 Core, Engine, Slate 等已省略）：

| 模块 | 用途 |
|---|---|
| `BinkMediaPlayer` | 提供 `UBinkMediaPlayer`, `UBinkMediaTexture` 等核心类。 |
| `MediaAssets` | (通过 `BinkMediaPlayerSDK`) 提供与 UE 媒体系统集成的基础。 |
| `MoviePlayer` | 用于在加载屏幕等场景播放全屏视频流（`FBinkMovieStreamer`）。 |
| `RHI` | 底层渲染硬件接口，用于创建 GPU 纹理和绘制命令。 |
| `Renderer` | 用于访问渲染线程工具和资源管理。 |

**注意**：`BinkMediaPlayerSDK` 模块是外部依赖，包含了 Bink 的解码库和头文件（如 `bink.h`），链接时需要确保对应的库文件可用。通常情况下，引擎和插件已提供预编译库。

## 维护状态

### 近期更新
| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的日志宏迁移至新的 UE_LOGF 宏。 |
| 2026-04-01 | `2f26bbfa` | Bink: Fixed BinkTestBed | 修复了 Bink 测试床工具。 |
| 2026-04-01 | `8a338576` | Bink: Fixed foward def mismatch, just include PixelFormat.h | 修复了前向声明不匹配的问题，改为直接包含头文件。 |
| 2026-04-01 | `9f45180e` | Bink: update for new BinkHL interface | 更新以适配新版的 BinkHL 接口。 |
| 2026-02-19 | `3e97632c` | Refactored FSceneViewport / FViewport to remove the ViewportRHI field | 重构视口类以移除过时的 ViewportRHI 字段，此更新影响了 Bink 的叠加层渲染路径。 |

### 维护评价
该插件由 Epic Games 维护，**处于活跃开发状态**。从 Git 历史可见，自 2021 年创建以来持续更新，最近一次更新距今仅数月（2026年4月）。更新内容包括：适配引擎核心类重构（如视口系统）、更新底层 Bink SDK 接口、修复编译和运行时问题。这表明插件与 UE5 主干开发保持同步，兼容性和稳定性得到保证。插件默认禁用 (`EnabledByDefault=false`)，属于专业或特定需求组件，但代码质量和维护水平很高，**推荐在需要 Bink 格式视频的项目中使用**。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/BinkMedia)
- [官方文档]() (无)
- [测试用例]() (未在提供的信息中发现独立测试文件，可能内置于引擎测试套件)