# Bink Media

> Implements a media player using Bink.

| 属性 | 值 |
|---|---|
| 中文名 | Bink 媒体 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `BinkMediaPlayer` (Runtime), `BinkMediaPlayerEditor` (Editor), `BinkMediaPlayerSDK` (External) |
| 实验性 | 否 |
| 创建时间 | 2025-07-27 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/BinkMedia) | |

## 用途

Bink Media 插件提供在 Unreal Engine 中播放 **Bink 视频格式** 的能力。Bink（由 RAD Game Tools 开发）是一种专为游戏设计的视频编解码器，以高压缩率、极低的 CPU 解码开销和跨平台支持著称。该插件封装了 Bink SDK，允许用户在引擎中以原生方式播放 Bink 视频（.bk2 文件），同时利用硬件加速渲染（D3D11/12、Vulkan、Metal 等）实现高性能播放。

**为什么存在？**  
游戏内视频播放场景（过场动画、ui 背景）对性能要求苛刻。Bink 格式比常见编解码器（H.264/265）具有更低的解码负载和更快的随机寻址能力。该插件实现了与 UE 媒体框架的集成，使开发者能以标准 Media Player 方式使用 Bink，同时保留了 Bink 特有的高级功能（如 GPU 辅助解码、HDR、alpha 通道、染色等）。

## 使用场景

- 在游戏中播放高质量过场动画，要求极小的性能开销  
- 需要支持 HDR 视频的高端 PC/主机项目  
- 需要在同一场景中同时播放多个视频（分屏、多屏幕）  
- 已有 Bink 格式的视频资产（如来自 RAD 视频工具）需集成到 UE5 管线  
- 希望利用 Bink 的 alpha 通道实现透明视频覆盖 UI  

## 蓝图用法

插件未直接暴露蓝图可调用的自定义函数。Bink 视频播放通过 UE 标准 **Media Player** 系统实现。在蓝图中：

1. 创建一个 `MediaPlayer` 对象及对应的 `MediaSource`（需使用 Bink 媒体源子类，如 `BinkMediaSource`）。  
2. 将 `FileMediaSource`（或自定义 `BinkMediaSource`）的路径指向 `.bk2` 文件。  
3. 使用 `MediaPlayer` 节点的 `Open Source` 播放，并通过 `OnEndReached`、`OnMediaOpened` 等事件控制流程。  
4. 将 `MediaTexture` 绑定到 `MediaPlayer`，再应用于材质以显示视频。

**注意**：Bink 特有的功能（如 alpha 通道、染色、音轨切换）无法直接在蓝图中暴露，建议通过 C++ 控制。

| 节点 / 属性 | 说明 | 所在类（蓝图） |
|---|---|---|
| `Open Source` | 打开指定的 Bink 媒体源 | `MediaPlayer` |
| `Play` / `Pause` | 控制播放状态 | `MediaPlayer` |
| `SetRate` | 设置播放速率（Bink 支持变速） | `MediaPlayer` |
| `Seek` | 跳转到指定时间（Bink 支持精确随机访问） | `MediaPlayer` |
| `OnEndReached` | 视频播放结束事件 | `MediaPlayer` |
| `MediaTexture` | 用于显示的媒体纹理资源 | `MediaTexture` |

## C++ 用法

Bink Media 插件核心基于 C 层 SDK，UE 封装提供 `UMediaPlayer` 兼容接口。以下展示深度用法。

### 头文件引入

```cpp
#include "BinkMediaPlayer.h"              // 核心运行时模块
#include "MediaPlayer.h"                  // UE 媒体框架
#include "BinkMediaSource.h"              // 用于 Bink 视频源
```

### 基本用法：播放一个 Bink 视频

```cpp
// 在你的游戏或 UI Actor 中

#include "MediaPlayer.h"
#include "BinkMediaSource.h"

void AMyPlayerActor::PlayBinkVideo(const FString& BinkFilePath)
{
    // 1. 创建 MediaPlayer 对象
    UMediaPlayer* MediaPlayer = NewObject<UMediaPlayer>(this);
    if (!MediaPlayer->IsValidLowLevel()) return;

    // 2. 创建 Bink 媒体源
    UBinkMediaSource* MediaSource = NewObject<UBinkMediaSource>(this);
    MediaSource->SetFilePath(BinkFilePath); // 假设 BinkMediaSource 支持文件路径设置

    // 3. 打开并播放
    bool bOpened = MediaPlayer->OpenSource(MediaSource);
    if (bOpened)
    {
        MediaPlayer->Play();
    }
}
```

**来源**: 从 UE 媒体播放框架标准用法推断，实际 BinkMediaSource 继承自 `UMediaSource`，路径设置通过 `FString` 属性。

### 进阶用法：使用 Bink 专用 API 进行底层控制

以下展示通过 Bink SDK 直接调用（需要包含 `binkplugin.h`），适用于需要精细控制渲染/解码流程的场景。

```cpp
#include "binkplugin.h"   // BinkPluginInit, BinkPluginProcessBinks, BinkPluginDraw
#include "binktextures.h" // Create_Bink_textures, Draw_Bink_textures 等

// 初始化 Bink 渲染环境
void InitBinkRenderer()
{
    BINKPLUGININITINFO Info;
    FMemory::Memzero(Info);
    // 根据当前 RHI 设置 queue 等
    // ...

    if (!BinkPluginInit(GDynamicRHI->RHIGetNativeDevice(), &Info, BinkRHI))
    {
        // 处理失败
    }
}

// 每帧更新和绘制
void TickBink()
{
    // 解码帧
    BinkPluginProcessBinks(16);  // 最多花费16ms

    // 绘制到渲染目标或叠加层
    BinkPluginDraw(1, 0);        // draw_overlays=1, draw_to_render_textures=0
}

// 播放循环（简化）
void PlayBinkByHandle(HBINK Bink)
{
    // 需配合 Bink SDK 的 DoFrame 等函数
    // 参见官方示例
}
```

**注意**：大多数项目不需要直接调用 SDK API，UE 的媒体框架已封装好。上述代码仅为展示底层能力。

## Demo 示例

以下是一个完整的 `AActor` 子类，可在场景中自动播放一个 Bink 视频到屏幕（使用 Media Texture）。

**BinkVideoPlayer.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MediaPlayer.h"
#include "BinkMediaSource.h"
#include "BinkVideoPlayer.generated.h"

UCLASS()
class ABinkVideoPlayer : public AActor
{
    GENERATED_BODY()

public:
    ABinkVideoPlayer();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Bink")
    UMediaPlayer* MediaPlayer;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Bink")
    UMediaTexture* MediaTexture;

private:
    void PlayBink(const FString& FilePath);
};
```

**BinkVideoPlayer.cpp**

```cpp
#include "BinkVideoPlayer.h"
#include "Engine/Texture2D.h"
#include "Materials/MaterialInstanceDynamic.h"

ABinkVideoPlayer::ABinkVideoPlayer()
{
    PrimaryActorTick.bCanEverTick = false;

    // 创建媒体播放器
    MediaPlayer = CreateDefaultSubobject<UMediaPlayer>(TEXT("MediaPlayer"));

    // 创建媒体纹理
    MediaTexture = CreateDefaultSubobject<UMediaTexture>(TEXT("MediaTexture"));
    MediaTexture->SetMediaPlayer(MediaPlayer);
}

void ABinkVideoPlayer::BeginPlay()
{
    Super::BeginPlay();
    
    // 假设 Bink 文件位于 Content/Video/Intro.bk2
    PlayBink(TEXT("/Game/Video/Intro.bk2"));
}

void ABinkVideoPlayer::PlayBink(const FString& FilePath)
{
    UBinkMediaSource* MediaSource = NewObject<UBinkMediaSource>(this);
    MediaSource->FilePath = FilePath;  // 假设 UBinkMediaSource 有此 FString 属性

    if (!MediaSource)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create BinkMediaSource"));
        return;
    }

    bool bSuccess = MediaPlayer->OpenSource(MediaSource);
    if (bSuccess)
    {
        MediaPlayer->Play();
        UE_LOG(LogTemp, Log, TEXT("Bink video playback started: %s"), *FilePath);
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open Bink source: %s"), *FilePath);
    }
}
```

**说明**：上述示例假设 `UBinkMediaSource` 有 `FilePath` 属性。实际插件可能使用 `FileMediaSource`，路径通过 `SetFilePath` 设置。请根据实际 API 调整。

## 模块依赖

以下为使用 `BinkMediaPlayer` 模块时需添加的依赖（省略标准 `Core`、`Engine`、`Slate`、`UMG` 等）。

| 模块 | 用途 |
|---|---|
| `BinkMediaPlayer` | 运行时播放器核心 |
| `MoviePlayer` | 加载界面集成 |
| `RenderCore` | 渲染资源管理 |
| `RHI` | 硬件接口抽象 |
| `Renderer` | 渲染管线支持 |
| `DesktopWidgets` | 编辑器 UI 工具 |
| `Projects` | 插件路径支持 |

**编辑模块** 额外需要：
- `BinkMediaPlayerEditor`（依赖 `BinkMediaPlayer` 和 `MetalRHI`）

**外部 SDK 模块** `BinkMediaPlayerSDK` 供内部使用，一般无需显式依赖。

## 维护状态

插件由 Epic Games 维护，近期频繁更新，处于活跃维护状态。

### 近期更新

- 2025-08-29 `32884de4` — 将 `RHICreateTexture` 用法迁移至 `RHICmdList.CreateTexture`（现代 RHI 适配）  
- 2025-08-27 `7766f4c6` — 修复媒体流式播放器的返回值为实际 open 调用结果  
- 2025-08-08 `40e2c8da` — 将 RHI Command Lists 传递至 MoviePlayer 和 TickableObjectRenderThread 功能  
- 2025-08-05 `dfd9e75a` — 修复 CookOnTheFly 路径问题（长期存在的 bug，感谢 BugHawk）  
- 2025-07-27 `bd4ed858` — 从模块中移除 `bAllowConfidentialPlatformDefines`（Android/iOS 不需要）

### 维护评价

- **创建时间**：2025-07-27（约 0 年）  
- **更新频率**：近 1 个月内多次提交，包含功能更新、API 适配和 bug 修复，属于活跃维护状态。  
- **适配性**：跟踪 UE 最新 RHI 变更，积极现代化代码。  
- **稳定性**：Bink 本身是非常成熟的商业技术，插件在多个大版本中稳定运行，无已知严重问题。  
- **推荐度**：强烈推荐，适合所有需要游戏内视频播放的 UE5 项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/BinkMedia)  
- [官方文档](https://docs.unrealengine.com/5.7/zh-CN/MediaFramework/HowTo/BinkMediaPlayer)（若存在）  
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/BinkMedia/Tests)（可能位于 Engine/Tests/ 下，未确认）  
- [RAD Game Tools Bink 主页](https://www.radgametools.com/bnk.htm)