# Electra Player

> Cross platform media player for local files and internet streaming.  
> Also provides optimized local mp4 file only player (Protron) for desktop machines.

| 属性 | 值 |
|---|---|
| 中文名 | Electra 播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ElectraPlayerFactory` (Runtime), `ElectraPlayerPlugin` (Runtime), `ElectraPlayerPluginHandler` (Runtime), `ElectraPlayerRuntime` (Runtime), `ElectraProtron` (Runtime), `ElectraProtronFactory` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-09-11 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ElectraPlayer) | |

## 用途

Electra Player 是虚幻引擎内置的跨平台媒体播放器解决方案，专门用于播放本地媒体文件（如 MP4）和网络流媒体（HLS、DASH 等）。它解决了传统媒体播放组件在跨平台一致性、流媒体自适应码率、以及低延迟直播方面的局限性。该插件还包含 **Protron** 模块，为桌面平台提供一个专门针对 MP4 文件优化、内存占用更低、启动更快的“轻量”播放通道，适合需要高帧率、低开销的本地视频回放场景。

## 使用场景

- 在游戏中播放过场动画或实时加载的视频广告 → 使用 Media Player 资产配合 Electra Player。
- 流媒体直播功能：需要支持 HLS/DASH 协议，自动切换码率以适应网络波动 → 利用 Electra 的流式播放能力。
- 桌面应用中的高清 MP4 播放：通过 Protron 模块可获得比通用播放器更好的性能。
- 视频会议或访谈类应用：Electra 对低延迟直播的支持（通过调整 Live edge latency 参数）可降低端到端延迟。

## 蓝图用法

Electra Player 通过引擎的 Media Framework 暴露给蓝图，所有操作均通过 **MediaPlayer** 和 **MediaSource** 蓝图节点进行，无需直接调用插件接口。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open Source` | 打开一个媒体源（MediaSource 资产或 URL） | `MediaPlayer` |
| `Play` | 开始播放当前媒体 | `MediaPlayer` |
| `Pause` | 暂停播放 | `MediaPlayer` |
| `Close` | 关闭当前媒体并释放资源 | `MediaPlayer` |
| `OnMediaOpened` | 媒体打开成功时触发的事件 | `MediaPlayer` |
| `OnMediaOpenFailed` | 打开失败时触发的事件 | `MediaPlayer` |
| `OnEndReached` | 播放到末尾时触发的事件 | `MediaPlayer` |
| `Get Time` | 获取当前播放时间位置 | `MediaPlayer` |
| `Set Rate` | 设置播放速率（快放、慢放、倒放） | `MediaPlayer` |

### 使用示例（蓝图描述）

1. 在关卡蓝图中，创建一个 **MediaPlayer** 对象变量（从 "Media" 类别创建）。
2. 创建 **FileMediaSource** 或 **StreamMediaSource** 资产，指定本地文件路径或流 URL。
3. 将 MediaPlayer 变量与 MediaSource 连接至 **Open Source** 节点的对应引脚。
4. 等待 **OnMediaOpened** 事件触发，然后调用 **Play** 节点开始播放。
5. 使用 **Get Time** 节点读取当前播放进度，连接至 UI 的进度条。

## C++ 用法

### 头文件引入

```cpp
#include "IElectraPlayerPluginModule.h"
#include "MediaPlayer.h"
#include "MediaSource.h"
```

### 基本用法

插件通过 `IElectraPlayerPluginModule` 模块接口创建 `IMediaPlayer` 实例，并配合 `IMediaEventSink` 接收事件。不过常规使用中，更推荐直接使用 `UMediaPlayer` 对象。

```cpp
// 使用 UMediaPlayer 和 UMediaSource 播放本地文件
UMediaPlayer* MediaPlayer = NewObject<UMediaPlayer>();
UMediaSource* MediaSource = UMediaSource::CreateFromFilePath(TEXT("C:/Videos/movie.mp4"));

// 打开资源
MediaPlayer->OpenSource(MediaSource);

// 播放（通常等待 OnMediaOpened 事件）
MediaPlayer->Play();
// 来源：Engine/Plugins/Media/ElectraPlayer/Source/ElectraPlayerPlugin/Private/ElectraPlayerPlugin.cpp (简化)
```

### 进阶用法：定制播放器创建

当需要直接控制播放器创建逻辑（如注入自定义事件接收器）时，可以使用模块接口：

```cpp
// 获取 ElectraPlayerPlugin 模块
IElectraPlayerPluginModule* ElectraModule = FModuleManager::LoadModulePtr<IElectraPlayerPluginModule>("ElectraPlayerPlugin");
if (ElectraModule && ElectraModule->IsInitialized())
{
    // 创建一个自定义事件接收器
    class FMyEventSink : public IMediaEventSink
    {
        virtual void ReceiveMediaEvent(EMediaEvent Event) override
        {
            UE_LOG(LogTemp, Log, TEXT("Media event: %d"), (int32)Event);
        }
    };
    FMyEventSink EventSink;

    // 创建播放器
    TSharedPtr<IMediaPlayer, ESPMode::ThreadSafe> Player = ElectraModule->CreatePlayer(EventSink);
    if (Player.IsValid())
    {
        // 后续可以设置媒体源并播放...
    }
}
// 来源：Engine/Plugins/Media/ElectraPlayer/Source/ElectraPlayerPlugin/Public/IElectraPlayerPluginModule.h
```

### 选择 Protron 播放器

Protron 模块专门针对 MP4 进行优化，若需要在桌面平台使用，可在 `UMediaSource` 的选项中指定播放器名称：

```cpp
UMediaSource* MediaSource = ...;
MediaSource->SetPlayerPluginName(TEXT("ElectraProtronFactory"));
MediaPlayer->OpenSource(MediaSource);
```

## Demo 示例

以下是一个最小可编译示例，在游戏启动时自动播放一个本地 MP4 文件：

**MyMediaPlayer.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MediaPlayer.h"
#include "MyMediaPlayer.generated.h"

UCLASS()
class AMyMediaPlayer : public AActor
{
    GENERATED_BODY()
public:
    virtual void BeginPlay() override;

private:
    UPROPERTY()
    UMediaPlayer* MediaPlayer;
};
```

**MyMediaPlayer.cpp**
```cpp
#include "MyMediaPlayer.h"
#include "MediaSource.h"

void AMyMediaPlayer::BeginPlay()
{
    Super::BeginPlay();

    MediaPlayer = NewObject<UMediaPlayer>(this);
    // 使用 FileMediaSource 资产（假设已创建）
    UFileMediaSource* MediaSource = NewObject<UFileMediaSource>();
    MediaSource->SetFilePath(TEXT("C:/MyGame/Content/Videos/intro.mp4"));

    MediaPlayer->OpenSource(MediaSource);
    MediaPlayer->OnMediaOpened.AddDynamic(this, &AMyMediaPlayer::OnMediaOpened);
}

void AMyMediaPlayer::OnMediaOpened(FString OpenedUrl)
{
    MediaPlayer->Play();
}
```

> **说明**：实际使用时请将文件路径替换为工程 Content 目录下的合法资源。

## 模块依赖

使用 Electra Player 插件时，你的模块通常只需要依赖 `MediaAssets` 和 `MediaUtils`（通过引擎媒体框架），ElectraPlayer 插件自身会处理内部模块加载。以下为该插件各核心模块的外部依赖（仅供了解）：

| 模块 | 用途 |
|---|---|
| `DirectX` | （ElectraPlayerRuntime）Windows 平台视频解码加速 |
| `D3D12RHI` | （ElectraProtron）桌面平台 MP4 播放的 GPU 渲染支持 |

对用户模块而言，无需显式添加 `ElectraPlayerRuntime` 等依赖，只需在 `.Build.cs` 中添加：

```csharp
PublicDependencyModuleNames.AddRange(new string[] { "MediaAssets", "MediaUtils" });
```

## 维护状态

### 近期更新

- 2025-10-01 `31d4710d` ElectraPlayer: Improved support for replay events; added ability to turn a HLS VoD stream into a replay.
- 2025-09-29 `d34a730c` ElectraPlayer: Emit warning about mismatched media segment duration only when the duration check was performed.
- 2025-09-29 `49fa2b76` ElectraPlayer: Adjusting the maximum Live edge latency in case the media segments have a larger duration.
- 2025-09-23 `0dc995dc` ElectraPlayer: Using a VoD asset for a synchronized event now allows it to loop when provided via DataAsset.
- 2025-09-11 `d9f531d6` Electra: combined multiline raw string into a single line.

### 维护评价

该插件创建于 2025 年 9 月，至今不到一年。从最近的提交记录来看，维护活跃且专注：修复了流媒体同步、延迟控制、事件循环等关键功能。提交内容属于功能性更新，而非简单的编译修复。该插件已从实验性状态转为正式插件，稳定性良好。适合用于生产项目。暂无已知重大限制或废弃标记。

## 相关链接

- [源码（ElectraPlayer 插件目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ElectraPlayer)
- [官方文档 - Media Framework](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ElectraPlayer/Tests)（若不存在，则无公开测试目录）