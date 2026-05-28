# WMF Media Player

> Implements a media player using the Windows Media Foundation framework.

| 属性 | 值 |
|---|---|
| 中文名 | WMF 媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `WmfMedia` (Runtime), `WmfMediaEditor` (Editor), `WmfMediaFactory` (Editor), `WmfMediaFactory` (RuntimeNoCommandlet) |
| 实验性 | 否 |
| 创建时间 | 2014-07-31 |
| 年龄标签 | 🏛️ 文物（约 12 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/WmfMedia) | |

## 用途

WmfMedia 插件为 Unreal Engine 在 Windows 平台上提供了一套完整的、基于 Microsoft Windows Media Foundation (WMF) 框架的媒体播放实现。它并非一个独立的媒体播放器界面，而是作为 UE Media Framework 的一个后端“驱动程序”。其核心作用是将 UE 通用的媒体接口（如 `IMediaPlayer`、`IMediaTracks`）映射到 Windows 平台原生的 WMF API 上，从而实现对各种音频、视频、流媒体格式的播放支持，并能利用硬件（GPU）加速进行视频解码。

简单来说，它解决了在 Windows 上播放媒体文件的底层实现问题，让开发者无需关心 Windows 复杂的媒体 API 细节，只需通过 UE 统一的 Media Framework 进行操作。

## 使用场景

-   **开发 PC 平台游戏**：当你的游戏需要播放过场动画（CG）、动态背景或任何视频文件时，在 Windows 平台上会默认使用此插件进行解码和播放。
-   **使用 Media Framework 进行跨平台媒体开发**：如果你使用 `UMediaPlayer`、`UMediaTexture` 等蓝图资产，且目标平台包含 Windows，那么在 Windows 上的播放会由 WmfMedia 负责。
-   **需要硬件加速视频解码**：对于高分辨率（如 4K）视频，启用硬件解码（DXVA）可以显著降低 CPU 占用，提升性能。此插件支持此特性。
-   **需要访问摄像头或麦克风**：虽然更常用于播放，但 WMF 也支持音视频采集设备（如摄像头、麦克风），此插件提供了枚举和使用这些设备的基础。
-   **在蓝图中简单控制媒体播放**：虽然此插件不提供独特的蓝图节点，但通过标准的 `UMediaPlayer` 资产和 Media Framework 蓝图库，你可以实现播放、暂停、跳转等所有操作。

## 蓝图用法

WmfMedia 插件本身**不直接暴露任何 `BlueprintCallable` 函数或蓝图节点**。它的所有功能都通过 UE 的 **Media Framework** 这一通用抽象层提供。

因此，你在蓝图中操作媒体时，使用的是与任何其他媒体播放器插件（如 AvfMedia, MediaFoundation 等）相同的接口：

1.  创建一个 `UMediaPlayer` 资产。
2.  将其 `PlayerName` 设置为 `"WmfMedia"`（或在编辑器默认设置中自动选择）。
3.  使用 `Open Source`, `Play`, `Pause`, `Seek`, `Close` 等蓝图节点。
4.  通过 `UMediaTexture` 资产将视频渲染到场景中的 `UTexture` 或 `UMaterialInstanceDynamic`。

### 核心节点 (来自 Media Framework)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open Source` | 打开指定的媒体源（URL、文件路径等） | `UMediaPlayer` |
| `Play` | 开始播放媒体 | `UMediaPlayer` |
| `Pause` | 暂停播放 | `UMediaPlayer` |
| `Close` | 关闭当前媒体源 | `UMediaPlayer` |
| `Seek` | 跳转到指定时间点 | `UMediaPlayer` |
| `Set Looping` | 设置是否循环播放 | `UMediaPlayer` |
| `Get Duration` | 获取媒体总时长 | `UMediaPlayer` |

### 使用示例 (蓝图描述)

假设你有一个视频文件 `C:\Video\Intro.mp4`。

1.  **创建资产**：在内容浏览器中右键 -> **Media** -> **Media Player**，命名为 `MyMediaPlayer`。同样创建一个 **Media Texture**，命名为 `MyMediaTexture`。
2.  **配置纹理**：打开 `MyMediaTexture` 资产，在其详情面板中，将 `Media Player` 属性设置为 `MyMediaPlayer`。
3.  **在角色蓝图中使用**：
    *   添加一个 `Media Sound Component`（用于音频）和一个 `Plane` 或使用 `Render Target` 的 `Material`（用于视频）。
    *   在事件图表中：
        *   添加一个 `BeginPlay` 节点。
        *   连接到 `Open Source (MyMediaPlayer)` 节点，`Media Source` 引脚选择 **File**，路径填入 `C:\Video\Intro.mp4`。
        *   从 `MyMediaPlayer` 的输出引脚拉出 `Play` 节点。
4.  **结果**：游戏开始后，`MyMediaPlayer` 会通过 WmfMedia 插件（在 Windows 上）解码视频，并将画面输出到 `MyMediaTexture`，你之前应用了该纹理的材质或平面就会显示视频画面，同时 `Media Sound Component` 会播放音频。

## C++ 用法

### 头文件引入

```cpp
// 主模块接口
#include "IWmfMediaModule.h"

// 如果你计划与媒体样本或纹理直接交互
#include "WmfMediaCommon.h"
```

### 基本用法

WmfMedia 主要作为 Media Framework 的后端，其 C++ 用法通常围绕创建和管理 `IMediaPlayer` 实例。以下是一个通过模块接口创建播放器并打开源的简单示例。

```cpp
// (示例代码，需包含必要头文件并确保在支持 WMF 的平台上调用)

// 获取 WmfMedia 模块实例
IWmfMediaModule* WmfMediaModule = FModuleManager::LoadModulePtr<IWmfMediaModule>(TEXT("WmfMedia"));

if (WmfMediaModule && WmfMediaModule->IsInitialized())
{
    // 创建一个事件接收器 (通常用于接收播放事件，如结束、错误)
    IMediaEventSink& MyEventSink = /* ... 你的事件接收器实现 ... */;

    // 创建一个 WMF 媒体播放器实例
    TSharedPtr<IMediaPlayer, ESPMode::ThreadSafe> MediaPlayer = WmfMediaModule->CreatePlayer(MyEventSink);

    if (MediaPlayer.IsValid())
    {
        // 打开一个媒体源 (例如，一个本地文件)
        FString MediaUrl = TEXT("file:///C:/Videos/MyVideo.mp4");
        MediaPlayer->Open(MediaUrl, nullptr); // 第二个参数是 IMediaOptions*，可为 nullptr

        // 控制播放
        MediaPlayer->GetControls().SetRate(1.0f); // 正常速度播放
        // MediaPlayer->GetControls().Seek(FTimespan::FromSeconds(30.0)); // 跳转到 30 秒

        // 获取样本以进行自定义渲染 (高级用法)
        IMediaSamples& Samples = MediaPlayer->GetSamples();
        TSharedPtr<IMediaTextureSample, ESPMode::ThreadSafe> VideoSample;
        if (Samples.FetchVideo(TRange<FTimespan>(), VideoSample)) // FetchVideo 需要一个时间范围
        {
            // 处理 VideoSample 中的纹理数据...
        }
    }
}
```

### 进阶用法：使用硬件解码纹理

WmfMedia 支持通过 DXVA 进行硬件加速解码，生成 D3D11 共享纹理。这通常由插件内部管理，但了解其原理有助于调试。

```cpp
// (示例概念代码，展示与硬件解码样本的潜在交互)

#include "WmfMediaHardwareVideoDecodingTextureSample.h"
#include "WmfMediaHardwareVideoDecodingRendering.h"

// 在渲染线程中...
void ProcessHardwareVideoSample(FWmfMediaHardwareVideoDecodingTextureSample* HardwareSample)
{
    if (HardwareSample && HardwareSample->GetMediaTextureSampleConverter())
    {
        // 获取或创建目标纹理（通常由渲染管线管理）
        FRHICommandListImmediate& RHICmdList = FRHICommandListExecutor::GetImmediateCommandList();
        FTextureRHIRef DestTexture = HardwareSample->GetOrCreateDestinationTexture(RHICmdList);

        // 通过样本的转换接口执行硬件解码转换
        // 注意：Convert 函数内部会调用 FWmfMediaHardwareVideoDecodingParameters::ConvertTextureFormat_RenderThread
        // 该函数会使用预定义的着色器（如 NV12 到 RGB 的转换）将硬件解码的纹理复制/转换到渲染目标纹理
        IMediaTextureSampleConverter* Converter = HardwareSample->GetMediaTextureSampleConverter();
        Converter->Convert(RHICmdList, DestTexture, FConversionHints());
    }
}
```

## Demo 示例

一个最小的、可编译的 C++ 示例，展示如何创建 WmfMedia 播放器并尝试打开一个 URL。

```cpp
// MyMediaTestActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "MyMediaTestActor.generated.h"

class IMediaPlayer;
class IMediaEventSink;
class IWmfMediaModule;

UCLASS()
class AMyMediaTestActor : public AActor
{
    GENERATED_BODY()
public:
    AMyMediaTestActor();

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    UPROPERTY(EditAnywhere, Category = "Media")
    FString MediaUrl;

    TSharedPtr<IMediaPlayer, ESPMode::ThreadSafe> MediaPlayer;
    IWmfMediaModule* WmfMediaModule;
};
```

```cpp
// MyMediaTestActor.cpp
#include "MyMediaTestActor.h"
#include "IWmfMediaModule.h"
#include "IMediaPlayer.h"
#include "IMediaControls.h"
#include "MediaPlayer.h" // 用于 FMediaEventSink

AMyMediaTestActor::AMyMediaTestActor()
{
    PrimaryActorTick.bCanEverTick = false;
    MediaUrl = TEXT("file:///C:/test.mp4"); // 请替换为你的测试文件路径
}

void AMyMediaTestActor::BeginPlay()
{
    Super::BeginPlay();

    // 1. 加载模块
    WmfMediaModule = FModuleManager::LoadModulePtr<IWmfMediaModule>(TEXT("WmfMedia"));
    if (!WmfMediaModule || !WmfMediaModule->IsInitialized())
    {
        UE_LOG(LogTemp, Warning, TEXT("WmfMedia module is not available or initialized."));
        return;
    }

    // 2. 创建一个简单的事件接收器 (这里使用匿名 lambda 或一个简单的类)
    // 为简化，我们使用 Media Framework 提供的基础 sink
    struct FSimpleMediaEventSink : public IMediaEventSink
    {
        virtual void ReceiveMediaEvent(EMediaEvent Event) override
        {
            UE_LOG(LogTemp, Log, TEXT("Media Event: %d"), static_cast<int32>(Event));
        }
    };
    static FSimpleMediaEventSink SimpleEventSink;

    // 3. 创建播放器
    MediaPlayer = WmfMediaModule->CreatePlayer(SimpleEventSink);
    if (!MediaPlayer.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create WmfMediaPlayer."));
        return;
    }

    // 4. 打开媒体源
    if (!MediaPlayer->Open(MediaUrl, nullptr))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open media: %s"), *MediaUrl);
        return;
    }

    UE_LOG(LogTemp, Log, TEXT("Attempting to open media: %s"), *MediaUrl);

    // 5. 可选：开始播放
    // MediaPlayer->GetControls().SetRate(1.0f);
}

void AMyMediaTestActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (MediaPlayer.IsValid())
    {
        MediaPlayer->Close();
        MediaPlayer.Reset();
    }
    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

你的模块（如果使用此插件的功能）通常需要添加以下依赖。请根据实际需要选择。

| 模块 | 用途 |
|---|---|
| `WmfMedia` | 运行时核心模块，提供播放器实现 |
| `WmfMediaCodec` | 编解码器管理，如果需要注册自定义解码器 |
| `MediaAssets` | 使用 `UMediaPlayer`, `UMediaTexture` 等蓝图资产 |
| `MediaUtils` | 使用媒体框架的底层工具类 |
| `D3D11RHI` | 与硬件加速解码（DXVA）相关的纹理操作直接依赖此模块 |

**注意**：`WmfMediaEditor` 和 `WmfMediaFactory` 是编辑器相关模块，在运行时（Shipping Build）中不需要。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移到新的 `UE_LOGF` 格式。 |
| 2026-02-24 | `13c44482` | Media Profile: Added media player options to media profile editor details panels for stream media so... | 媒体配置文件编辑器现在为流媒体显示了媒体播放器选项。 |
| 2026-02-04 | `80b637db` | Fixed printf format specifiers. | 修复了格式化字符串的说明符错误。 |
| 2026-01-07 | `57ff2f55` | Deprecate legacy GPU profiler related macros. | 废弃了旧版 GPU 性能分析相关的宏。 |
| 2025-10-30 | `0990a715` | Ran UnrealCodeFixup on Fortnite to change all ~Type() {} to instead be ~Type() = default | 对代码进行了规范化，将析构函数的空实现改为 `= default`。 |

### 维护评价

WmfMedia 是一个**成熟稳定且仍在维护中**的插件。

-   **历史与成熟度**：创建于 2014 年，是 UE 在 Windows 平台媒体播放的基石之一，经过了近12年的迭代和优化。
-   **近期活动**：从 git 日志看，最近一次实质性更新在 **2026 年 2 月**（添加媒体配置文件功能），之后的提交主要是代码规范、日志系统迁移等基础设施工作。这表明其核心功能已非常稳定，近期的维护主要围绕 UE 引擎的整体现代化进行。
-   **平台支持**：仅限于 **Windows (Win64)** 平台。
-   **状态**：无已知重大问题。它是 Epic 官方维护的插件，与 UE 引擎同步更新，**推荐在 Windows 平台项目中使用**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/WmfMedia)
- [官方文档](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview) (较旧的论坛帖子，但包含基本概念)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/WmfMedia/Tests) (路径为推断，可能位于 `Media/WmfMedia/Tests/` 下)