# WMF Media Player

> Implements a media player using the Windows Media Foundation framework.

| 属性 | 值 |
|---|---|
| 中文名 | WMF媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `WmfMedia` (Runtime), `WmfMediaEditor` (Editor), `WmfMediaFactory` (Runtime), `WmfMediaFactory` (RuntimeNoCommandlet) |
| 实验性 | 否 |
| 创建时间 | 2014-07-31 |
| 年龄标签 | 🏛️ 文物（约 12 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/WmfMedia) | |

## 用途

**WmfMedia** 是 Unreal Engine 媒体框架在 **Windows 平台**上的核心后端实现。它封装了微软的 Windows Media Foundation (WMF) API，为引擎提供了在 Windows 64 位系统上解码和播放音频、视频文件的能力。

这个插件的存在解决了两个关键问题：
1.  **平台抽象**：将 Windows 特有的、复杂的媒体处理 API (WMF) 封装成引擎内部统一的 `IMediaPlayer`、`IMediaTracks` 等接口，使得上层应用（如 `MediaFrameworkUtilities`、`MediaAssets`）无需关心平台细节。
2.  **功能集成**：支持硬件加速解码、低延迟流媒体等高级特性，并将这些选项通过引擎的设置系统暴露出来。

简而言之，它是引擎在 Windows 上进行所有媒体播放（如视频文件、网络流）的底层驱动之一。

## 使用场景

只要你的项目运行在 **Windows 平台**上，并且需要播放媒体内容，那么你很可能在间接或直接地使用这个插件。

*   **游戏内过场动画**：播放预制的 `.mp4`、`.wmv` 等格式的过场视频。
*   **UI 背景与装饰**：在游戏菜单或 UI 界面中播放动态视频背景。
*   **监控与安全系统模拟**：在游戏中模拟实时监控摄像头画面。
*   **流媒体**：播放网络视频流或音频流。
*   **任何需要 Windows 原生解码能力**的场景。

## 蓝图用法

此插件主要提供底层媒体能力，直接暴露给蓝图的接口集中在配置层面。

### 核心配置节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Class Settings` | 获取 `UWmfMediaSettings` 类的实例，用于读取当前配置。 | `UWmfMediaSettings` (静态) |
| `AllowNonStandardCodecs` (属性) | 允许使用非标准编解码器。开启前需确保用户系统已安装相应解码器包。 | `UWmfMediaSettings` |
| `LowLatency` (属性) | 启用低延迟处理。适用于实时应用，但可能影响音视频质量（仅 Windows 8+ 支持）。 | `UWmfMediaSettings` |
| `NativeAudioOut` (属性) | 通过操作系统原生音频混合器播放音频轨道。 | `UWmfMediaSettings` |
| `HardwareAcceleratedVideoDecoding` (属性) | 启用硬件加速视频解码（实验性）。需要 DX11 支持。 | `UWmfMediaSettings` |

### 使用示例（蓝图描述）

1.  **修改播放设置**：在你的 GameMode 或初始化逻辑中，通过 “Get Class Settings” 节点获取 `UWmfMediaSettings` 对象，然后将其属性（如 `LowLatency`）设为 `true`，以改变全局的媒体播放行为。
2.  **创建媒体播放器**：使用 `MediaFrameworkUtilities` 或 `MediaAssets` 插件中的 “Create Media Player” 等节点，其底层会自动在 Windows 上使用 WmfMedia 实现。

## C++ 用法

C++ 用法通常不直接实例化 WmfMedia 的播放器，而是通过引擎的 `FMediaModule` 来请求和使用。

### 头文件引入

```cpp
// 要操作 WmfMedia 的设置
#include "WmfMediaSettings.h"
```

### 基本用法

**修改插件配置（来自 `WmfMediaSettings.h`）**：

```cpp
// 在合适的地方（如 GameInstance 初始化后）获取设置对象
UWmfMediaSettings* Settings = GetMutableDefault<UWmfMediaSettings>();
if (Settings)
{
    // 启用低延迟模式
    Settings->LowLatency = true;
    // 允许非标准编解码器
    Settings->AllowNonStandardCodecs = true;
    // 保存到配置文件
    Settings->TryUpdateDefaultConfigFile();
}
```

**注意**：直接修改 `UObject` 默认对象并保存配置会修改 `Engine.ini` 文件。更常见的做法是使用 `UDeveloperSettings` 或 `UGameUserSettings` 来管理你的游戏特定设置，并在媒体播放前应用。

### 进阶用法

WmfMedia 的核心播放器类（如 `FWmfMediaPlayer`）通常由 `FMediaModule` 通过 `IMediaPlayerFactory` 创建。如果你需要扩展或调试媒体播放流程，可以关注 `WmfMediaFactory` 模块，它负责注册工厂并创建播放器实例。

## Demo 示例

此示例展示如何在 C++ 中配置 WmfMedia 插件，并通过标准媒体接口播放一个视频文件。你需要有 `MediaAssets` 模块的依赖。

**MyMediaController.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MediaPlayer.h"
#include "MyMediaController.generated.h"

UCLASS()
class AMyMediaController : public AActor
{
    GENERATED_BODY()

public:
    AMyMediaController();

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY(EditAnywhere, Category = "Media")
    TSoftObjectPtr<UMediaSource> MediaSourceAsset;

    UPROPERTY()
    TObjectPtr<UMediaPlayer> MediaPlayer;

    void ConfigureWmfMediaSettings();
};
```

**MyMediaController.cpp**
```cpp
#include "MyMediaController.h"
#include "MediaFrameworkUtilities/Public/MediaPlayerAsset.h" // 用于创建播放器
#include "WmfMediaSettings.h" // 包含 WmfMedia 设置头文件
#include "MediaSource.h"

AMyMediaController::AMyMediaController()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyMediaController::BeginPlay()
{
    Super::BeginPlay();
    ConfigureWmfMediaSettings();

    // 1. 创建媒体播放器
    MediaPlayer = NewObject<UMediaPlayer>(this);
    if (!MediaPlayer || MediaSourceAsset.IsNull())
    {
        return;
    }

    // 2. 打开媒体源
    UMediaSource* Source = MediaSourceAsset.LoadSynchronous();
    if (Source && MediaPlayer->OpenSource(Source))
    {
        UE_LOG(LogTemp, Log, TEXT("Media opened successfully via WmfMedia backend."));
        // 3. 播放
        MediaPlayer->Play();
    }
}

void AMyMediaController::ConfigureWmfMediaSettings()
{
    // 获取并修改 WmfMedia 插件的全局设置
    UWmfMediaSettings* WmfSettings = GetMutableDefault<UWmfMediaSettings>();
    if (WmfSettings)
    {
        // 示例：针对此应用场景，我们想要低延迟
        WmfSettings->LowLatency = true;
        UE_LOG(LogTemp, Log, TEXT("WmfMedia LowLatency enabled."));
        // 注意：此处修改只影响本次运行时内存中的设置，不会持久化到配置文件。
    }
}
```

## 模块依赖

使用者通常无需直接依赖此插件的模块，而是依赖上层媒体模块。如果你需要在自己的模块中**配置** WmfMedia 的设置，可能需要依赖 `WmfMediaFactory`。标准的媒体使用流程依赖：

| 模块 | 用途 |
|---|---|
| `MediaAssets` | 提供 `UMediaPlayer`, `UMediaSource`, `UMediaTexture` 等资产类，是蓝图和 C++ 中操作媒体的主要接口。 |
| `MediaFrameworkUtilities` | 提供更高级的媒体工具函数和 UI 组件。 |
| `MediaUtils` | 提供底层的媒体工具和接口定义（如 `IMediaPlayer`）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF。 |
| 2026-02-24 | `13c44482` | Media Profile: Added media player options to media profile editor details panels for stream media so... | 在媒体配置文件编辑器中为流媒体添加了播放器选项。 |
| 2026-02-04 | `80b637db` | Fixed printf format specifiers. | 修复了 printf 格式说明符问题。 |
| 2026-01-07 | `57ff2f55` | Deprecate legacy GPU profiler related macros. | 废弃了旧的 GPU 性能分析器相关宏。 |
| 2025-10-30 | `0990a715` | Ran UnrealCodeFixup on Fortnite to change all ~Type() {} to instead be ~Type() = default | 执行代码修复，将析构函数体改为 = default。 |

### 维护评价

WmfMedia 是一个**历史久远但仍在活跃维护**的插件。

*   **创建时间**：2014年，是 UE4 早期媒体框架的核心部分。
*   **近期活跃度**：在 2025 年底至 2026 年初仍有持续的代码提交，包括功能增强（媒体配置文件支持）、代码现代化（日志宏迁移）和问题修复。
*   **状态**：**活跃维护中**。作为 Windows 平台媒体播放的基石，它显然仍在跟随引擎版本迭代。
*   **推荐使用**：**是**。如果你需要在 Windows 上进行媒体播放，这是官方提供的、经过长期测试的解决方案。注意 `HardwareAcceleratedVideoDecoding` 标记为实验性功能。

## 相关链接

*   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/WmfMedia)
*   [官方文档](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview)
*   [相关测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/WmfMedia/Tests) (如果存在)