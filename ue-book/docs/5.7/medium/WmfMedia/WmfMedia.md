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
| 创建时间 | 2025-04-23 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/WmfMedia) | |

## 用途

`WmfMedia` 是 Unreal Engine 在 Windows 平台上的核心媒体播放器实现。它基于 Windows Media Foundation (WMF) 框架，支持播放多种格式的音频和视频文件、流媒体以及直接读取内存数据。该插件提供了完整的媒体管道，包括音频、视频、字幕（文本叠加）和二进制数据轨道，并支持硬件加速视频解码（通过 DirectX 11）。

它解决了 UE 在 Windows 上需要高性能、低延迟、硬件加速的本地媒体播放问题。默认情况下，当用户在 Windows 上使用 `Media Player` 资产时，引擎会自动选择 `WmfMedia` 作为后端播放器。

## 使用场景

- 在 Windows 游戏或应用中播放本地视频文件（如 `.mp4`, `.wmv`）、音频文件
- 播放来自 URL 的流媒体内容（如 RTSP、MMS）
- 集成 Windows 采集设备（摄像头、麦克风）的实时音视频流
- 需要硬件加速解码（NV12/YCbCr 转 RGB）的高分辨率或高帧率视频播放
- 内存中解析媒体数据（通过 `FArchive`）

## 蓝图用法

`WmfMedia` 本身不暴露任何自定义蓝图函数。它作为 `Media Player` 资产的后端，自动生效。用户只需使用标准 Media Framework 蓝图节点即可。

### 核心操作流程

1. **创建 Media Player**：在蓝图编辑器中创建 `Media Player` 资产，或使用 `Create Media Player` 节点。
2. **绑定媒体源**：使用 `Open Source` 节点，指定一个 `Media Source` 资产（如 `File Media Source`、`Stream Media Source`）或直接传入 URL 字符串。
3. **播放控制**：使用 `Media Player` 对象的 `Play`、`Pause`、`Seek` 等节点。
4. **获取渲染纹理**：将 `Media Player` 的 `Video Texture` 输出连接到材质或 UMG 的 `Image` 控件，实现视频渲染。
5. **音频播放**：自动路由到音频系统，无需额外节点。
6. **字幕处理**：通过 `On Media Player Media Opened` 事件获取轨道信息，然后使用 `Get Track` 和 `Select Track` 节点选择字幕轨道。

> **注意**：由于 WMF 是 Windows 本地实现，所有媒体操作在 **Windows 64位** 平台（非服务器）上自动使用 WMF 后端。无需手动指定。

## C++ 用法

### 头文件引入

```cpp
#include "IWmfMediaModule.h"
#include "IMediaPlayer.h"
#include "IMediaEventSink.h"
#include "MediaPlayerOptions.h"
```

### 基本用法：创建并播放媒体

以下示例展示了如何通过 `IWmfMediaModule` 创建一个 WMF 媒体播放器，并打开一个本地文件。

```cpp
// 假设在某个 Actor 或 Manager 中

void UMyMediaComponent::PlayLocalFile(const FString& FilePath)
{
    // 获取 WMF 模块
    IWmfMediaModule* WmfModule = IWmfMediaModule::Get();
    if (!WmfModule || !WmfModule->IsInitialized())
    {
        UE_LOG(LogTemp, Error, TEXT("WmfMedia module not available"));
        return;
    }

    // 创建 WMF 播放器
    TSharedPtr<IMediaPlayer, ESPMode::ThreadSafe> MediaPlayer = WmfModule->CreatePlayer(EventSink);
    if (!MediaPlayer.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create WMF media player"));
        return;
    }

    // 打开文件（第二个参数 IMediaOptions 可以为 nullptr）
    bool bOpened = MediaPlayer->Open(FilePath, nullptr);
    if (bOpened)
    {
        // 成功后，可以通过 IMediaControls 控制播放
        IMediaControls& Controls = MediaPlayer->GetControls();
        Controls.Play();
    }
}
```

*来源：源码 `IWmfMediaModule.h` 中的 `CreatePlayer` 接口。*

### 进阶用法：处理媒体事件与轨道信息

```cpp
// 事件接收类示例
class FMyMediaEventSink : public IMediaEventSink
{
public:
    virtual void ReceiveMediaEvent(EMediaEvent Event) override
    {
        switch (Event)
        {
        case EMediaEvent::MediaOpened:
            UE_LOG(LogTemp, Log, TEXT("Media opened successfully"));
            break;
        case EMediaEvent::MediaClosed:
            UE_LOG(LogTemp, Log, TEXT("Media closed"));
            break;
        case EMediaEvent::PlaybackEndReached:
            UE_LOG(LogTemp, Log, TEXT("Playback ended"));
            break;
        default:
            break;
        }
    }
};

// 获取轨道信息
void UMyMediaComponent::PrintTrackInfo(IMediaPlayer& Player)
{
    IMediaTracks& Tracks = Player.GetTracks();
    for (int32 TrackType = 0; TrackType < 3; ++TrackType) // audio, video, caption
    {
        EMediaTrackType Type = static_cast<EMediaTrackType>(TrackType);
        int32 NumTracks = Tracks.GetNumTracks(Type);
        for (int32 i = 0; i < NumTracks; ++i)
        {
            FText DisplayName = Tracks.GetTrackDisplayName(Type, i);
            FString Language = Tracks.GetTrackLanguage(Type, i);
            UE_LOG(LogTemp, Log, TEXT("Track %d: %s [%s]"), i, *DisplayName.ToString(), *Language);
        }
    }
}
```

*与 WMF 集成方式：`FWmfMediaPlayer` 内部实现了 `IMediaPlayer` 并管理 `FWmfMediaTracks`。*

### 硬件加速解码

WMF 播放器默认启用硬件加速（当系统支持时）。可通过 `UWmfMediaSettings` 进行调整。在游戏线程或渲染线程中，`FWmfMediaHardwareVideoDecodingTextureSample` 负责将 GPU 解码后的 NV12 纹理转换为 RGB。通常无需手动调用。

## Demo 示例

以下是一个完整的 `UActorComponent` 示例，展示如何使用 WMF 媒体播放器播放本地文件并输出日志。

**MyWmfPlayerComponent.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "IMediaEventSink.h"
#include "MyWmfPlayerComponent.generated.h"

UCLASS(ClassGroup=(Media), meta=(BlueprintSpawnableComponent))
class UMyWmfPlayerComponent : public UActorComponent, public IMediaEventSink
{
    GENERATED_BODY()

public:
    UMyWmfPlayerComponent();

    UFUNCTION(BlueprintCallable, Category = "Media")
    void PlayFile(const FString& FilePath);

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    // IMediaEventSink interface
    virtual void ReceiveMediaEvent(EMediaEvent Event) override;

private:
    TSharedPtr<IMediaPlayer, ESPMode::ThreadSafe> MediaPlayer;
};
```

**MyWmfPlayerComponent.cpp**
```cpp
#include "MyWmfPlayerComponent.h"
#include "IWmfMediaModule.h"
#include "IMediaControls.h"

UMyWmfPlayerComponent::UMyWmfPlayerComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UMyWmfPlayerComponent::BeginPlay()
{
    Super::BeginPlay();
    // 模块初始化已在引擎启动时完成，可直接使用
}

void UMyWmfPlayerComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (MediaPlayer.IsValid())
    {
        MediaPlayer->Close();
        MediaPlayer.Reset();
    }
    Super::EndPlay(EndPlayReason);
}

void UMyWmfPlayerComponent::PlayFile(const FString& FilePath)
{
    IWmfMediaModule* WmfModule = IWmfMediaModule::Get();
    if (!WmfModule || !WmfModule->IsInitialized())
    {
        UE_LOG(LogTemp, Error, TEXT("WmfMedia module not available"));
        return;
    }

    MediaPlayer = WmfModule->CreatePlayer(*this);
    if (!MediaPlayer.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create WMF player"));
        return;
    }

    bool bOpened = MediaPlayer->Open(FilePath, nullptr);
    if (!bOpened)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open media: %s"), *FilePath);
    }
}

void UMyWmfPlayerComponent::ReceiveMediaEvent(EMediaEvent Event)
{
    switch (Event)
    {
    case EMediaEvent::MediaOpened:
        UE_LOG(LogTemp, Log, TEXT("Media opened, starting playback"));
        if (MediaPlayer.IsValid())
        {
            MediaPlayer->GetControls().Play();
        }
        break;
    case EMediaEvent::MediaClosed:
        UE_LOG(LogTemp, Log, TEXT("Media closed"));
        break;
    default:
        break;
    }
}
```

*注意：此示例不包含 `Build.cs`，因为依赖关系已在下一节说明。将上述代码添加至你的项目中即可运行。*

## 模块依赖

### WmfMedia 模块

| 模块 | 用途 |
|---|---|
| `D3D11RHI` | 硬件加速视频解码（创建共享 D3D11 纹理） |
| `HeadMountedDisplay` | VR 相关媒体播放的额外支持（如立体视频） |
| `Engine` | 标准引擎依赖 |

**其他模块**：`WmfMediaEditor` 和 `WmfMediaFactory` 依赖标准编辑器模块，无需额外配置。

若要使用 `WmfMedia` 模块，在你的模块 `Build.cs` 的 `PublicDependencyModuleNames` 中添加：

```csharp
PublicDependencyModuleNames.AddRange(
    new string[]
    {
        "WmfMedia",
        "MediaAssets",   // 常见需求：使用 MediaPlayer 资产
        "MediaUtils"     // 媒体工具库
    }
);
```

> `D3D11RHI` 是私有依赖，当你的代码直接使用 WMF 硬件解码功能时可能需要链接，一般通过 `WmfMedia` 的公有 API 即可自动处理。

## 维护状态

### 近期更新

- 2025-09-03 `10aed468` WmfMedia: Clamping number of inflight requests in case ProcessSample() is invoked multiple times
- 2025-08-29 `32884de4` Changing more uses of RHICreateTexture to RHICmdList.CreateTexture
- 2025-05-12 `2f1f89d4` WmfMedia: Fix for incorrect dx11 decoding using the uncropped image size resulting in duplicated rows
- 2025-05-12 `b3cff994` WmfMedia: Fix for incorrect dx12 decoding using the uncropped image size resulting in green rows
- 2025-04-23 `6ae57335` Used UnrealGame build target to find and convert all files to have dllstorage on methods/static vars

### 维护评价

- **活跃维护**：最近 6 个月内有多次功能性修复和代码质量改进。
- **已知问题**：硬件解码在某些极端情况（如高分辨率、高帧率）可能出现绿边或重复行，但近期已针对性修复。
- **推荐使用**：作为 Windows 平台默认媒体播放器，稳定可靠，建议在 Windows 目标上使用。可在 `UWmfMediaSettings` 中调整低延迟、硬件加速等选项。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/WmfMedia)
- [官方文档（论坛帖子）](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/WmfMedia/Source)（源码中无独立测试目录，但可通过引擎自动化测试运行 WMF 相关测试）