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
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/WmfMedia) | |

## 用途

`WmfMedia` 插件基于 Windows Media Foundation（WMF）框架，为 Unreal Engine 提供高性能的本地媒体文件播放能力。支持多种音视频容器格式（如 MP4、AVI、WMV 等），并利用 Windows 平台的硬件加速（DX11/DX12）实现流畅的 4K / HDR 视频解码。

**WmfMediaFactory** 模块负责将该播放器注册到 UE 的媒体框架中，并提供全局配置选项（通过 `UWmfMediaSettings` 类），让用户在项目设置中控制非标准编解码器支持、低延迟模式、原生音频输出及硬件加速视频解码等功能。

## 使用场景

- 制作需要播放本地视频资源的游戏或交互应用，如过场动画、实时视频合成、虚拟制片。
- 在 UI 中嵌入视频播放器（通过 `MediaPlayer` + `MediaTexture` + `MediaSoundComponent`）。
- 需要低延迟预览的直播流或实时摄像机输入（启用 `LowLatency` 选项）。
- 播放需要额外编解码器支持的视频格式（开启 `AllowNonStandardCodecs`）。

## 蓝图用法

`WmfMedia` 插件主要通过标准 `MediaPlayer` 蓝图节点使用，无需自定义节点。全局设置通过项目设置界面修改，不暴露蓝图的函数调用。

### 项目设置

在 **编辑 → 项目设置 → 媒体 → WMF Media Player** 中可调整以下选项：

| 设置项 | 蓝图对应属性 | 说明 |
|---|---|---|
| Allow Non Standard Codecs | `AllowNonStandardCodecs` | 允许加载非标准编解码器的媒体 |
| Low Latency | `LowLatency` | 启用 Windows 8+ 的低延迟流水线 |
| Native Audio Out | `NativeAudioOut` | 通过操作系统原生混音器播放音频 |
| Hardware Accelerated Video Decoding (Experimental) | `HardwareAcceleratedVideoDecoding` | 启用 GPU 硬件加速视频解码（DX11 仅） |

这些设置影响该插件创建的所有媒体播放器实例。修改后需重新加载媒体资源才能生效。

## C++ 用法

### 头文件引入

```cpp
#include "WmfMediaSettings.h"
```

### 基本用法

要编程修改全局设置，可以通过 `GetMutableDefault<UWmfMediaSettings>()` 获取单例并修改。

```cpp
// 启用非标准编解码器
if (UWmfMediaSettings* Settings = GetMutableDefault<UWmfMediaSettings>())
{
    Settings->AllowNonStandardCodecs = true;
    Settings->LowLatency = true;
    Settings->NativeAudioOut = false;
    Settings->HardwareAcceleratedVideoDecoding = true;
    Settings->SaveConfig(); // 持久化到 DefaultEngine.ini
}
```

### 进阶用法

在自定义媒体播放器工厂中，可以通过 `UWmfMediaSettings` 读取当前配置并影响播放器创建参数。

```cpp
// 从媒体框架获取 WMF 播放器实例
UMediaPlayer* MediaPlayer = NewObject<UMediaPlayer>();
MediaPlayer->SetLooping(false);
MediaPlayer->PlayOnOpen = true;

// 播放前可检查设置是否支持硬件解码
const UWmfMediaSettings* Settings = GetDefault<UWmfMediaSettings>();
if (Settings->bAreHardwareAcceleratedCodecRegistered)
{
    // 已注册硬件加速编码器，可放心使用
}
```

## Demo 示例

一个最小 C++ 示例，展示如何通过 `WmfMediaFactory` 模块的设置类配置 WMF 播放器。

**MyMediaPlayerComponent.h**

```cpp
#pragma once

#include "Components/ActorComponent.h"
#include "WmfMediaSettings.h"
#include "MyMediaPlayerComponent.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyMediaPlayerComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    // 设置 WMF 播放器的全局参数
    UFUNCTION(BlueprintCallable, Category = "Media")
    void ConfigureWmfPlayer(bool bAllowNonStandard, bool bLowLatency, bool bNativeAudio, bool bHardwareDecode);
};
```

**MyMediaPlayerComponent.cpp**

```cpp
#include "MyMediaPlayerComponent.h"

void UMyMediaPlayerComponent::ConfigureWmfPlayer(bool bAllowNonStandard, bool bLowLatency, bool bNativeAudio, bool bHardwareDecode)
{
    if (UWmfMediaSettings* Settings = GetMutableDefault<UWmfMediaSettings>())
    {
        Settings->AllowNonStandardCodecs      = bAllowNonStandard;
        Settings->LowLatency                  = bLowLatency;
        Settings->NativeAudioOut              = bNativeAudio;
        Settings->HardwareAcceleratedVideoDecoding = bHardwareDecode;
        Settings->SaveConfig();
    }
}
```

## 模块依赖

使用 `WmfMediaFactory` 模块（或其提供的设置类）时，需要以下依赖项：

| 模块 | 用途 |
|---|---|
| `WmfMedia` | 核心 WMF 媒体播放器运行时逻辑 |
| `MediaUtils` | 媒体框架工具库 |
| `HeadMountedDisplay` | 可选，用于 VR 相关媒体渲染 |
| `D3D11RHI` | DX11 硬件加速视频解码支持 |

（省略常见依赖：Core, CoreUObject, Engine, Slate 等）

## 维护状态

### 近期更新

- 2025-09-03 10aed468 WmfMedia: Clamping number of inflight requests in case ProcessSample() is invoked multiple times
- 2025-08-29 32884de4 Changing more uses of RHICreateTexture to RHICmdList.CreateTexture.
- 2025-05-12 2f1f89d4 WmfMedia: Fix for incorrect dx11 decoding using the uncropped image size resulting in duplicated row
- 2025-05-12 b3cff994 WmfMedia: Fix for incorrect dx12 decoding using the uncropped image size resulting in green rows at
- 2025-04-23 6ae57335 Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar

### 维护评价

该插件仍在积极维护中，修复了 DX11/DX12 解码中的视觉问题，并优化了请求处理。硬件加速解码（实验性）功能持续改进。推荐在 Windows 平台上使用，用于播放本地媒体文件。已知限制：仅支持 Windows 平台（Win64），不支持服务器构建。低延迟模式可能影响音视频质量，需根据场景取舍。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/WmfMedia)
- [官方文档（旧版论坛）](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/WmfMedia/Tests)（如果存在）