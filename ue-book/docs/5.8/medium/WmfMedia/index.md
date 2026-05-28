# WMF Media Player

> Implements a media player using the Windows Media Foundation framework.

| 属性 | 值 |
|---|---|
| 中文名 | Windows媒体基础播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `WmfMedia` (Runtime), `WmfMediaEditor` (Editor), `WmfMediaFactory` (Editor), `WmfMediaFactory` (RuntimeNoCommandlet) |
| 实验性 | 否 |
| 创建时间 | 2014-07-31 |
| 年龄标签 | 🏛️ 文物（约 12 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/WmfMedia) | |

## 用途

WmfMedia 插件在 Windows 平台上实现了基于微软 **Windows Media Foundation (WMF)** 框架的媒体播放器。它为 Unreal Engine 的媒体框架 (`MediaPlayer`) 提供了一个具体的、高性能的底层实现。该插件的核心价值在于：
1.  **利用系统原生能力**：直接调用 Windows 系统级别的媒体解码和渲染组件，无需引擎内置庞大的第三方解码库。
2.  **硬件加速与格式支持**：能够利用系统已有的硬件解码器和广泛的媒体格式支持（如 H.264, HEVC, WMV 等），并能处理受 **DRM 保护的内容**。
3.  **平台特性整合**：支持 Windows 特有的功能，如与头戴显示器 (`HeadMountedDisplay`) 集成以实现 VR 视频播放。

简单来说，当你需要在 Windows 平台的 UE5 项目中播放视频或音频时，WMF 是一个稳定、高效且兼容性极佳的选择。

## 使用场景

-   你正在为 **Windows 平台**开发一个需要播放过场动画、背景视频或实况流媒体的游戏。
-   你需要播放 **MP4, AVI, WMV** 等常见格式的视频文件。
-   你的视频内容受 **Windows Media DRM** 保护，需要系统级解密支持。
-   你希望利用系统的 **GPU 硬件解码**来降低 CPU 负载，提高播放性能和电池续航（尤其适用于笔记本电脑）。
-   你需要在 **VR 应用**中播放 360 度或立体视频。

## 蓝图用法

核心的播放功能通过标准的媒体框架蓝图节点实现，这些节点属于 `UMediaPlayer` 类，与具体的媒体播放器插件实现解耦。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open URL` | 使用提供的字符串URL打开一个媒体资源进行播放 | `UMediaPlayer` |
| `Play` | 开始播放已打开的媒体资源 | `UMediaPlayer` |
| `Pause` | 暂停当前播放 | `UMediaPlayer` |
| `Close` | 关闭当前媒体源，释放资源 | `UMediaPlayer` |

### 使用示例（蓝图描述）

1.  在蓝图中添加一个 `Media Player` 变量（类型为 `Media Player` 资产的引用）。
2.  调用 `Open URL` 节点，将视频文件的路径（如文件路径 `D:\video.mp4` 或 HTTP/RTSP 流地址）作为 `URL` 输入。该节点会返回一个 `Media Source` 对象。
3.  将 `Open URL` 节点的 `Opened` 执行输出连接到 `Play` 节点，即可开始播放。
4.  可以通过 `Media Player` 变量上的其他函数（如 `Get Duration`, `Get Time`, `Is Playing`）来查询播放状态。

## C++ 用法

C++ 中的使用同样基于媒体框架的通用接口，但需要通过插件提供的工厂类进行实例化。

### 头文件引入

```cpp
#include "IMediaPlayer.h"
#include "MediaPlayer.h"
```

### 基本用法

通过 `FMediaPlayerFactory` 创建媒体播放器实例。

```cpp
// 来自：对 WmfMediaFactory 模块功能的描述
// 获取 WMF 工厂类
IMediaPlayerFactory* WmfFactory = FModuleManager::GetModulePtr<IMediaPlayerFactory>(“WmfMediaFactory”);
if (WmfFactory)
{
    // 通过工厂创建媒体播放器实例
    TSharedPtr<IMediaPlayer, ESPMode::ThreadSafe> Player = WmfFactory->CreatePlayer();
    
    // 使用通用的 IMediaPlayer 接口操作
    Player->OpenUrl(TEXT(“file:///D:/Video/test.mp4”));
    Player->Play();
}
```

## Demo 示例

```cpp
// MediaPlayerDemo.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MediaPlayerDemo.generated.h"

class UMediaPlayer;
class UMediaSource;

UCLASS()
class AMediaPlayerDemo : public AActor
{
    GENERATED_BODY()

public:
    AMediaPlayerDemo();

    UPROPERTY(EditAnywhere, Category = “Media”)
    UMediaPlayer* MediaPlayer;

    UPROPERTY(EditAnywhere, Category = “Media”)
    UMediaSource* MediaSource;

    virtual void BeginPlay() override;
};

// MediaPlayerDemo.cpp
#include “MediaPlayerDemo.h”
#include “MediaPlayer.h”
#include “MediaSource.h”

AMediaPlayerDemo::AMediaPlayerDemo()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMediaPlayerDemo::BeginPlay()
{
    Super::BeginPlay();

    if (MediaPlayer && MediaSource)
    {
        // 打开指定的媒体源并开始播放
        MediaPlayer->OpenSource(MediaSource);
        MediaPlayer->Play();
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `D3D11RHI` | 用于与Direct3D 11渲染硬件接口交互，是实现视频帧硬件解码和渲染的关键 |
| `HeadMountedDisplay` | 为VR头显提供立体视频播放支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移到新的 UE_LOGF 格式 |
| 2026-02-24 | `13c44482` | Media Profile: Added media player options to media profile editor details panels for stream media so | 媒体配置文件编辑器为流媒体添加了播放器选项 |
| 2026-02-04 | `80b637db` | Fixed printf format specifiers. | 修复了 printf 格式说明符错误 |
| 2026-01-07 | `57ff2f55` | Deprecate legacy GPU profiler related macros. | 废弃了旧的 GPU 性能分析相关宏 |
| 2025-10-30 | `0990a715` | Ran UnrealCodeFixup on Fortnite to change all ~Type() {} to instead be ~Type() = default | 代码格式化，将析构函数体改为 = default |

### 维护评价

-   **年龄**：创建于 2014 年，是一个非常成熟的插件。
-   **活跃度**：最近一次更新在 2026 年 4 月，内容涉及代码现代化和功能增强，表明插件仍在**积极维护**中。
-   **稳定性**：作为 UE 官方维护的 Windows 平台核心媒体播放器实现，其稳定性和兼容性经过了长期验证。
-   **推荐**：**强烈推荐**在 Windows 平台项目中使用，它是实现视频播放功能最可靠、集成度最高的方案。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/WmfMedia)
-   [官方文档](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview)
-   子模块文档：[WmfMedia.md](WmfMedia.md)， [WmfMediaEditor.md](WmfMediaEditor.md)， [WmfMediaFactory.md](WmfMediaFactory.md)