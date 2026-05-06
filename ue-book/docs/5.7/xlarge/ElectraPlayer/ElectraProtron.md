# Electra Player (ElectraProtron 子模块)

> Cross platform media player for local files and internet streaming.  
> Also provides optimized local mp4 file only player (Protron) for desktop machines.

| 属性 | 值 |
|---|---|
| 中文名 | 高效本地MP4播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ElectraPlayerFactory` (Runtime), `ElectraPlayerPlugin` (Runtime), `ElectraPlayerPluginHandler` (Runtime), `ElectraPlayerRuntime` (Runtime), `ElectraProtron` (Runtime), `ElectraProtronFactory` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-09-11 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ElectraPlayer) | |

## 用途

Electra 播放器插件是 Epic 官方提供的跨平台媒体播放解决方案，支持本地文件播放和互联网流媒体（如 HLS、DASH）。**ElectraProtron** 是其中的一个子模块，专门为桌面平台（Windows / Mac）提供**优化的本地 MP4 文件仅播放器**。它专注于高效解码并渲染容器中的视频轨道，利用 D3D12 RHI 进行硬件加速渲染，同时提供可自定义的帧缓存机制，以提高播放流畅性。

与同一插件下的 `ElectraPlayerRuntime` 不同，Protron 不处理流媒体或复杂容器结构，而是针对单一 MP4 文件做深度优化，适合需要极致本地播放性能的场景（如游戏过场动画、视频导览等）。

## 使用场景

- **游戏过场动画**：将高码率 MP4 视频作为过场，利用 Protron 获得低延迟、高帧率的播放体验。
- **视频导览/帮助系统**：在桌面游戏中嵌入本地视频教程，无需外部播放器。
- **资产预览工具**：编辑器内快速预览 MP4 文件，依赖 D3D12 RHI 实现零拷贝渲染。
- **性能敏感的应用**：需要精确控制视频帧缓存大小、预加载策略，避免因解码延迟导致的卡顿。

## 蓝图用法

ElectraProtron 模块提供了 `FElectraProtronPlayer` 类，实现了 `IMediaPlayer` 接口。它本身不暴露任何 `BlueprintCallable` 函数，而是通过媒体框架（Media Framework）的蓝图节点统一管理。用户可以在蓝图中使用标准的媒体播放器节点，选择 **Electra Protron Player** 作为播放源。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open Source` | 打开本地 MP4 文件或 URL，指定播放器选项 | `IMediaPlayer` |
| `Play` | 开始播放（速率设置为 1.0） | `IMediaControls` |
| `Pause` | 暂停播放 | `IMediaControls` |
| `Get Time` | 获取当前播放时间戳 | `IMediaControls` |
| `Seek` | 跳转到指定时间点 | `IMediaControls` |
| `Is Looping` / `Set Looping` | 查询/设置循环播放 | `IMediaControls` |

### 使用示例（蓝图描述）

1. **创建媒体播放器**：在事件图表中拖出 `Create Media Player` 节点，将返回的 `Media Player` 对象传递给后续操作。
2. **打开视频源**：使用 `Open Source` 节点，`Source` 引脚选择 `Media Source`（例如从资产浏览器拖入的 `File Media Source` 或 URL），`Player Options` 可以传入包含播放参数的结构体。
3. **播放控制**：连接 `Play`、`Pause`、`Stop` 节点；通过 `Get Time` 节点获取当前时间并显示在 UI 上。
4. **轨道选择**：Protron 默认使用第一个视频轨道和第一个音频轨道，无需额外选择。

## C++ 用法

### 头文件引入

```cpp
#include "IElectraProtronModule.h"
#include "IMediaPlayer.h"
#include "IMediaEventSink.h"
```

### 基本用法

通过插件模块的 `CreatePlayer` 创建播放器实例，然后调用 `IMediaPlayer` 接口方法。

**来源：** `Plugins/Media/ElectraPlayer/Source/ElectraProtron/Public/IElectraProtronModule.h`

```cpp
// 获取模块实例
IElectraProtronModule* ProtronModule = FModuleManager::LoadModulePtr<IElectraProtronModule>(TEXT("ElectraProtron"));
if (ProtronModule)
{
    // 创建媒体事件接收器（必须重写 OnMediaEvent）
    class FMyEventSink : public IMediaEventSink
    {
    public:
        virtual void ReceiveMediaEvent(EMediaEvent Event) override
        {
            UE_LOG(LogTemp, Log, TEXT("Media Event: %d"), static_cast<int32>(Event));
        }
    };
    TSharedRef<FMyEventSink, ESPMode::ThreadSafe> EventSink = MakeShared<FMyEventSink, ESPMode::ThreadSafe>();

    // 创建播放器
    TSharedPtr<IMediaPlayer, ESPMode::ThreadSafe> Player = ProtronModule->CreatePlayer(EventSink.Get());
    if (Player.IsValid())
    {
        // 打开本地 MP4 文件
        bool bOpened = Player->Open(TEXT("C:/MyVideo.mp4"), nullptr);
        if (bOpened)
        {
            // 获取控制接口
            IMediaControls& Controls = Player->GetControls();
            Controls.SetRate(1.0f); // 开始播放

            // 在 Tick 中更新
            // Player->TickInput(DeltaTime, Timecode);
        }
    }
}
```

### 进阶用法

控制视频缓存大小、播放时间范围、音轨选择等。

**来源：** `Plugins/Media/ElectraPlayer/Source/ElectraProtron/Private/Player/ElectraProtronPlayerImpl.h` (FSampleQueueInterface)

```cpp
// 设置视频帧缓存数量（在创建播放器之前通过选项传入）
FMediaPlayerOptions Options;
Options.PlayerOptions.Add(TEXT("VideoFramesToCacheAhead"), FVariant(6));  // 预缓存6帧
Options.PlayerOptions.Add(TEXT("VideoFramesToCacheBehind"), FVariant(6)); // 保留6帧历史

Player->Open(TEXT("movie.mp4"), nullptr, &Options);

// 动态设置播放时间范围（用于剪辑部分视频）
IMediaControls& Controls = Player->GetControls();
Controls.SetPlaybackTimeRange(TRange<FTimespan>(FTimespan::FromSeconds(10), FTimespan::FromSeconds(30)));

// 查询缓存状态
const FElectraProtronPlayer::FImpl* Impl = /* 获取内部实现指针（通常需要强转） */;
if (Impl)
{
    TRangeSet<FTimespan> CachedRanges;
    Impl->GetVideoCache().QueryCacheState(CachedRanges);
}
```

## Demo 示例

一个简单的控制台应用，演示如何打开 MP4 文件并播放一段时间。

**MyMediaPlayer.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "IMediaEventSink.h"
#include "IMediaPlayer.h"

class FMyMediaApp
{
public:
    void Run();
    
private:
    class FEventSink : public IMediaEventSink
    {
    public:
        virtual void ReceiveMediaEvent(EMediaEvent Event) override
        {
            // 处理事件（可选）
        }
    };

    TSharedPtr<IMediaPlayer, ESPMode::ThreadSafe> Player;
    TSharedPtr<FEventSink, ESPMode::ThreadSafe> EventSink;
};
```

**MyMediaPlayer.cpp**
```cpp
#include "MyMediaPlayer.h"
#include "IElectraProtronModule.h"
#include "Modules/ModuleManager.h"
#include "IMediaControls.h"

void FMyMediaApp::Run()
{
    EventSink = MakeShared<FEventSink, ESPMode::ThreadSafe>();
    
    IElectraProtronModule* Module = FModuleManager::LoadModulePtr<IElectraProtronModule>(TEXT("ElectraProtron"));
    if (!Module)
    {
        UE_LOG(LogTemp, Error, TEXT("ElectraProtron module not loaded."));
        return;
    }

    Player = Module->CreatePlayer(EventSink.Get());
    if (!Player.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create player."));
        return;
    }

    const FString VideoPath = FPaths::ProjectContentDir() / TEXT("Movies/Intro.mp4");
    if (!Player->Open(VideoPath, nullptr))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open video: %s"), *VideoPath);
        return;
    }

    IMediaControls& Controls = Player->GetControls();
    Controls.SetRate(1.0f);   // 播放
    FPlatformProcess::Sleep(5.0f);  // 播放5秒
    Controls.SetRate(0.0f);   // 停止
    Player->Close();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `D3D12RHI` | 提供 D3D12 渲染硬件接口，用于视频帧的 GPU 渲染（仅 Windows） |
| `DirectX` (部分平台) | 底层 DirectX 库支持 |
| `Engine` | 提供媒体框架接口（IMediaPlayer 等） |

**说明**：ElectraProtron 是插件 `ElectraPlayer` 的一部分，使用前需要加载整个插件。在你的模块 `Build.cs` 中添加 `"ElectraProtron"` 到 `PublicDependencyModuleNames`。

## 维护状态

### 近期更新

- 2025-10-01 `31d4710d` 改进 replay 事件支持；为 HLS VoD 流增加循环播放
- 2025-09-29 `d34a730c` 仅在持续时间检查启用时发出媒体分段时间不匹配警告
- 2025-09-29 `49fa2b76` 当媒体分段时间较长时调整最大 Live 边缘延迟
- 2025-09-23 `0dc995dc` 使用 VoD 资源的同步事件现在允许通过 DAI 设置循环
- 2025-09-11 `d9f531d6` 将多行原始字符串合并为单行

以上更新均属于 `ElectraPlayer` 整体仓库，涵盖 Protron 模块的潜在影响。

### 维护评价

- **创建时间**：2025-09-11（距今约 0 年）
- **最近更新**：最新 commit 在 2025-10-01，活跃度高
- **活跃维护**：✅ 是，每周都有功能性更新和 bug 修复
- **已知问题**：暂无公开限制，但 Protron 仅支持 MP4 容器，且需要 D3D12 支持
- **推荐程度**：强烈推荐用于桌面平台本地 MP4 播放，性能优异

## 相关链接

- [源码 (ElectraProtron 子模块)](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ElectraPlayer/Source/ElectraProtron)
- [官方文档 (Media Framework)](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)
- [测试用例 (ElectraPlayer)](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ElectraPlayer/Tests)