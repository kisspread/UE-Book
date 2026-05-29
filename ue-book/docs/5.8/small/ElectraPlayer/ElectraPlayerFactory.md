# Electra Player

> Cross platform media player for local files and internet streaming. Also provides optimized local mp4 file only player (Protron) for desktop machines.

| 属性 | 值 |
|---|---|
| 中文名 | 跨平台媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ElectraPlayerFactory` (Runtime), `ElectraPlayerPlugin` (Runtime), `ElectraPlayerPluginHandler` (Runtime), `ElectraPlayerRuntime` (Runtime), `ElectraProtron` (Runtime), `ElectraProtronFactory` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-01-06 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraPlayer) | |

## 用途

Electra Player 是 Epic Games 为 Unreal Engine 开发的下一代媒体播放框架。它旨在替代旧版的 Media Framework 和 Windows Media Player 插件，提供一个统一的、高性能、跨平台的媒体播放解决方案。

该插件解决了旧媒体框架在处理高分辨率、高码率视频、实时网络流媒体（如 HLS, DASH）以及复杂媒体元数据（如专辑、章节信息）时可能遇到的性能瓶颈和兼容性问题。它的核心优势在于：
1.  **跨平台支持**：提供一个统一的 API 来处理不同平台的媒体文件和流媒体协议。
2.  **高性能解码与渲染**：深度集成现代 GPU 进行硬件加速解码和渲染，降低 CPU 开销。
3.  **优化的本地播放 (Protron)**：针对桌面平台（主要是 Windows），提供一个名为 “Protron” 的优化路径，专门用于播放本地 MP4 文件，以获得极致性能和低延迟。
4.  **先进的流媒体支持**：内置对 HLS、MPEG-DASH 等现代自适应流媒体协议的支持，适用于在线视频点播和直播场景。

## 使用场景

*   你需要为游戏或应用加载并播放本地视频文件（如片头动画、过场视频）。
*   你需要播放来自网络的实时视频流或自适应码率视频流（如宣传视频、直播源）。
*   你的项目对媒体播放的性能（帧率、延迟、CPU 占用）有极高要求，尤其是在播放高分辨率（4K, 8K）内容时。
*   你在开发 Windows 桌面应用，并希望获得最佳的本地 MP4 文件播放性能。
*   你需要处理包含丰富元数据的媒体文件，如音频专辑信息（艺术家、曲目列表）或章节信息。

## 蓝图用法

Electra Player 主要作为底层媒体框架运行。通常，你不会直接在蓝图中调用其内部函数，而是通过 Unreal Engine 的标准 `Media Player` 资产和蓝图节点来使用。

### 核心节点（通过 Media Player 资产）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open Source` | 打开并准备播放一个媒体源（本地文件 URL 或网络流 URL）。 | `UMediaPlayer` |
| `Play` | 开始或恢复播放媒体。 | `UMediaPlayer` |
| `Pause` | 暂停媒体播放。 | `UMediaPlayer` |
| `Close` | 关闭当前媒体源并释放资源。 | `UMediaPlayer` |
| `Seek` | 跳转到媒体的指定时间点。 | `UMediaPlayer` |
| `Get Duration` | 获取媒体的总时长。 | `UMediaPlayer` |
| `Get Time` | 获取当前的播放时间。 | `UMediaPlayer` |
| `Is Playing` | 检查媒体是否正在播放。 | `UMediaPlayer` |
| `Set Looping` | 设置媒体是否循环播放。 | `UMediaPlayer` |

### 使用示例（蓝图描述）

1.  **创建与配置**：在内容浏览器中右键 -> `Media` -> `Media Player` 创建一个资产。在该资产的详情面板中，确保 “Media Player Class” 设置为 `ElectraMediaPlayer`。
2.  **关联纹理**：创建或找到一个 `Media Texture` 资产，在其详情面板中将 “Media Player” 指向你刚创建的 Media Player 资产。
3.  **在蓝图中控制**：在你的 Actor 蓝图中：
    *   添加一个 `Media Player` 类型的变量，并指向你的 Media Player 资产。
    *   在事件图表中，使用 `Open Source` 节点，传入媒体文件的路径或流地址。
    *   连接 `Play` 节点以开始播放。
    *   你可以使用 `Get Time` 和 `Get Duration` 节点配合进度条 UI，或使用 `Is Playing` 节点来控制播放/暂停按钮的状态。
4.  **显示视频**：将带有 Media Texture 的材质应用到网格体或 UI 组件（如 `Image` 控件）上，即可显示视频画面。

## C++ 用法

### 头文件引入

使用 Electra Player 不需要直接引入其特定模块头文件。你应使用引擎提供的通用媒体框架头文件。

```cpp
#include "MediaPlayer.h"
#include "MediaTexture.h"
#include "FileMediaSource.h"
#include "StreamMediaSource.h"
#include "MediaSource.h"
```

### 基本用法

以下代码演示如何在 C++ 中控制 Electra Player 播放本地文件。

```cpp
// 假设你已经持有 UMediaPlayer* MediaPlayer 和 UMediaTexture* MediaTexture 指针。
// 通常 MediaPlayer 是 UPROPERTY，通过 CreateDefaultSubobject 创建或从资产加载。

// 播放本地文件
void AMyActor::PlayLocalFile(const FString& FilePath)
{
    if (MediaPlayer)
    {
        // 创建一个文件媒体源
        UFileMediaSource* FileSource = NewObject<UFileMediaSource>();
        FileSource->SetFilePath(FilePath);

        // 打开源
        if (MediaPlayer->OpenSource(FileSource))
        {
            // 设置循环播放
            MediaPlayer->SetLooping(true);
            
            // 开始播放
            MediaPlayer->Play();
            
            // (可选) 将 MediaTexture 绑定到某个 UI 或网格体材质参数
            // MediaTexture 中的资源会自动更新。
        }
    }
}
```

### 进阶用法

处理网络流媒体和播放事件。

```cpp
// 播放网络流
void AMyActor::PlayStream(const FString& StreamURL)
{
    if (MediaPlayer)
    {
        UStreamMediaSource* StreamSource = NewObject<UStreamMediaSource>();
        StreamSource->SetStreamUrl(StreamURL);

        MediaPlayer->OpenSource(StreamSource);
        
        // 绑定打开完成事件
        MediaPlayer->OnMediaOpened.AddDynamic(this, &AMyActor::OnMediaOpened);
    }
}

// 事件处理函数
void AMyActor::OnMediaOpened(const FString& OpenedUrl)
{
    UE_LOG(LogTemp, Log, TEXT("Electra Player opened media: %s"), *OpenedUrl);
    MediaPlayer->Play();
}
```

## Demo 示例

一个完整的 Actor 示例，包含播放/暂停控制。

**MyMediaActor.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyMediaActor.generated.h"

class UMediaPlayer;
class UMediaTexture;

UCLASS()
class AMyMediaActor : public AActor
{
    GENERATED_BODY()
    
public:
    AMyMediaActor();

    UPROPERTY(EditAnywhere, Category = "Media")
    UMediaPlayer* MediaPlayer;

    UPROPERTY(EditAnywhere, Category = "Media")
    UMediaTexture* MediaTexture;

    UPROPERTY(EditAnywhere, Category = "Media")
    FString LocalVideoPath = TEXT("C:/Videos/MyVideo.mp4");

    UFUNCTION(BlueprintCallable, Category = "Media")
    void TogglePlayPause();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    bool bIsPlaying = false;
};
```

**MyMediaActor.cpp**
```cpp
#include "MyMediaActor.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"
#include "FileMediaSource.h"

AMyMediaActor::AMyMediaActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyMediaActor::BeginPlay()
{
    Super::BeginPlay();

    if (MediaPlayer)
    {
        // 创建文件源并打开
        UFileMediaSource* Source = NewObject<UFileMediaSource>();
        Source->SetFilePath(LocalVideoPath);
        MediaPlayer->OpenSource(Source);
    }
}

void AMyMediaActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (MediaPlayer)
    {
        MediaPlayer->Close();
    }
    Super::EndPlay(EndPlayReason);
}

void AMyMediaActor::TogglePlayPause()
{
    if (MediaPlayer)
    {
        if (bIsPlaying)
        {
            MediaPlayer->Pause();
        }
        else
        {
            MediaPlayer->Play();
        }
        bIsPlaying = !bIsPlaying;
    }
}
```

## 模块依赖

从各模块的 Build.cs 分析，使用 Electra Player 本身不需要在你的模块中显式添加复杂依赖，因为它通过插件系统和运行时加载集成。但以下模块是其运行时独有的关键依赖，你在自己的模块中通常无需直接引用：

| 模块 | 用途 |
|---|---|
| `ElectraBase` | Electra 框架的基础库，提供通用工具和接口。 |
| `DirectX` | Windows 平台上的 DirectX 图形和媒体 API 支持。 |
| `D3D12RHI` | 为 Protron 优化的本地播放器提供 Direct3D 12 渲染硬件接口。 |

**注意**：你的项目模块通常只需要依赖 `Engine` 和标准模块。Electra Player 插件会自动被引擎加载并提供媒体播放能力。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-21 | `ff9996e8` | Media Profile: Fixed issue where ElectraProtron issue would not play a new video after it had alread | 修复了 Protron 播放器在播放完一个视频后无法播放新视频的问题。 |
| 2026-05-14 | `d15b78b3` | ElectraPlayer: Fixed streamed album metadata | 修复了流媒体音频的专辑元数据（如歌曲信息）解析问题。 |
| 2026-05-13 | `4340cfa6` | ElectraPlayer: Added configuration and cvars to control if decoders need to be suspended during play | 新增了配置选项和控制台变量，允许控制播放期间是否挂起解码器。 |
| 2026-05-12 | `a6372743` | ElectraPlayer: changed an assertion to an if() condition to handle cases where .ts internal timestam | 将一个断言改为条件判断，以更好地处理 .ts 流内部时间戳可能存在的问题。 |
| 2026-05-12 | `e3746831` | ElectraPlayer: Checking for sequence index when prefetching subtitle media segments to reduce unnece | 在预取字幕媒体段时增加了序列索引检查，以减少不必要的网络请求。 |

### 维护评价

*   **活跃维护**：插件在2026年5月仍有频繁的更新，修复了多个影响播放稳定性和功能性的问题（如元数据、新视频播放、流媒体细节），表明 Epic Games 仍在积极维护和改进此核心媒体框架。
*   **成熟稳定**：插件自2021年初引入，已有约5年历史，属于成熟组件。其设计目标是成为 UE 的默认媒体播放后端。
*   **推荐使用**：对于新的 UE 项目，**强烈推荐**使用 Electra Player 作为媒体播放方案。它代表了更现代、更强大且受官方支持的技术方向。只有在需要兼容非常旧的媒体格式或特定平台遗留播放器时，才考虑其他方案。

## 相关链接

*   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraPlayer)
*   [官方文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)
*   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Media/)

**注意**：关于 Electra Player 专用的单元测试，可能需要检查 `Engine/Tests/Media/` 目录下的相关测试文件。