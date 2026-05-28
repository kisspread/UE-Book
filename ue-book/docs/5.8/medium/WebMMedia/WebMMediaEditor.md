# WebM Video Player

> A simulated cable component.

| 属性 | 值 |
|---|---|
| 中文名 | WebM视频播放器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `WebMMedia` (Runtime), `WebMMediaEditor` (Runtime), `WebMMediaFactory` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-09-12 |
| 年龄标签 | 🏛️ 文物（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/WebMMedia) | |

## 用途

WebMMedia 为 Unreal Engine 提供 **WebM（VP8/VP9）视频格式**的原生播放能力。它基于 Google 的 libvpx 解码库和 libwebm 容器解析库，作为 UE Media Framework 的一个媒体播放器插件实现，让用户可以通过标准的 `UMediaPlayer` 接口播放 `.webm` 格式的视频文件。

该插件解决的核心问题是：UE 内置的媒体播放器不支持 WebM 格式，而 WebM 是一种广泛用于网络视频的开放、免版税格式。插件同时支持 Windows 和 Linux 平台。

> **注意**：此插件默认未启用（`EnabledByDefault: false`），且标记为实验性（`IsBetaVersion: true`）。需要在项目设置中手动启用。

## 使用场景

- 你需要在项目中播放 `.webm` 格式的过场动画或背景视频
- 你在 Linux 平台上开发，需要一种跨平台的视频播放方案
- 你需要播放 VP9 编码的 10bit 高质量视频素材（2026 年新增支持）
- 你有大量网络来源的 WebM 视频需要在引擎中直接使用，不想转码

## 蓝图用法

WebMMedia 作为 Media Framework 的底层播放器实现，不暴露独立的蓝图节点。所有操作通过标准的 `UMediaPlayer`、`UMediaSource` 和 `UMediaTexture` 完成。

### 核心节点

此插件通过 Media Framework 自动注册，无需专用蓝图节点。使用标准媒体播放蓝图即可：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open Source` | 打开一个媒体源（支持 .webm 文件） | `UMediaPlayer` |
| `Open File` | 通过文件路径打开媒体 | `UMediaPlayer` |
| `Play` | 播放已打开的媒体 | `UMediaPlayer` |
| `Set Looping` | 设置循环播放 | `UMediaPlayer` |

### 使用示例（蓝图描述）

1. 在 Content Browser 中右键 → **Media** → **Media Player**，创建一个 MediaPlayer 资产
2. 创建一个 **File Media Source** 资产，设置文件路径指向 `.webm` 文件
3. 创建一个 **Media Texture** 资产并关联到 MediaPlayer
4. 在蓝图中：
   - 拖入 `MediaPlayer` 变量 → 调用 `Open Source` 节点，传入 FileMediaSource
   - 设置 `Set Looping` 为 `true`（如需循环）
   - 拖入 `MediaTexture` 变量 → 赋值给材质的纹理参数或直接用于 UI

## C++ 用法

### 头文件引入

```cpp
#include "MediaPlayer.h"
#include "FileMediaSource.h"
#include "MediaTexture.h"
#include "MediaSource.h"
```

### 基本用法

WebMMedia 插件通过 Media Framework 的工厂模式自动注册。在 C++ 中使用标准的媒体播放 API 即可：

```cpp
// 创建媒体播放器
UMediaPlayer* MediaPlayer = NewObject<UMediaPlayer>();

// 创建文件媒体源，指向 .webm 文件
UFileMediaSource* MediaSource = NewObject<UFileMediaSource>();
MediaSource->SetFilePath(TEXT("/Game/Movies/MyVideo.webm"));

// 打开媒体源
MediaPlayer->OpenSource(MediaSource);

// 启用循环播放（WebMMedia 插件实现了循环支持）
MediaPlayer->SetLooping(true);
```

### 进阶用法

WebMMedia 在编辑器中注册了一个文件工厂（`UWebMPlatFileMediaSourceFactory`），允许直接将 `.webm` 文件拖入 Content Browser 自动创建 `UFileMediaSource` 资产。在 C++ 中可通过工厂 API 手动触发：

```cpp
#include "WebMFileMediaSourceFactory.h"

// 工厂会自动判断文件是否为支持的 .webm 格式
// 当用户在编辑器中导入 .webm 文件时，工厂自动创建对应的媒体源资产
```

## Demo 示例

一个最小的 WebM 视频播放组件：

```cpp
// MyWebMPlayer.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MediaPlayer.h"
#include "FileMediaSource.h"
#include "MediaTexture.h"
#include "MyWebMPlayer.generated.h"

UCLASS(ClassGroup=(Media), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyWebMPlayer : public UActorComponent
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="WebM")
    UMediaPlayer* MediaPlayer;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="WebM")
    UFileMediaSource* MediaSource;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="WebM")
    UMediaTexture* MediaTexture;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="WebM")
    bool bLoop = true;

    UFUNCTION(BlueprintCallable, Category="WebM")
    bool PlayWebMVideo(const FString& FilePath);

    UFUNCTION(BlueprintCallable, Category="WebM")
    void Stop();
};
```

```cpp
// MyWebMPlayer.cpp
#include "MyWebMPlayer.h"

bool UMyWebMPlayer::PlayWebMVideo(const FString& FilePath)
{
    if (!MediaPlayer || !MediaSource)
    {
        UE_LOG(LogTemp, Error, TEXT("MediaPlayer or MediaSource is null"));
        return false;
    }

    // 设置文件路径
    MediaSource->SetFilePath(FilePath);

    // 设置循环
    MediaPlayer->SetLooping(bLoop);

    // 绑定纹理
    if (MediaTexture)
    {
        MediaTexture->SetMediaPlayer(MediaPlayer);
    }

    // 打开并播放
    return MediaPlayer->OpenSource(MediaSource);
}

void UMyWebMPlayer::Stop()
{
    if (MediaPlayer)
    {
        MediaPlayer->Close();
    }
}
```

## 模块依赖

本插件包含以下模块：

| 模块 | 用途 |
|---|---|
| `LibVpx` | Google 的 VP8/VP9 视频编解码库（第三方依赖） |
| `MediaUtils` | UE 媒体框架工具模块 |

无其他特殊依赖（仅标准 Core/Engine 等）。

> 使用此插件时，你的模块需要在 Build.cs 中添加对 `MediaAssets`、`MediaUtils` 和 `Media` 模块的依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-22 | `6fa2f4c5` | WebMMedia: Fixed video full range yuv offsets | 修复视频全范围 YUV 偏移量问题 |
| 2026-04-21 | `f9163c8f` | WebMMedia: Added support for 10 bit VP9 files; fixed an issue where images were overwritten before t | 新增 10bit VP9 文件支持，修复图像被覆盖问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 日志宏迁移到 UE_LOGF 新格式 |
| 2026-02-11 | `2639e40b` | Updated libvpx to 1.15.1, did not copy the duplicated headers layout from 1.14.1 | 升级 libvpx 到 1.15.1 版本 |
| 2026-01-22 | `0bfe789b` | WebMMedia: Rewrite of the plugin | 对整个插件进行了重写 |

### 维护评价

**活跃维护中。** 该插件在 2026 年初经历了一次完整的重写（`0bfe789b`），随后在 1-4 月间持续有功能性更新，包括升级 libvpx 到最新版本、新增 10bit VP9 支持、修复色彩空间问题等。这表明该插件正在经历积极的现代化改造。

不过需要注意：
- 插件从 2018 年创建以来仍标记为**实验性**（`IsBetaVersion: true`）
- **默认未启用**（`EnabledByDefault: false`），需要手动在项目设置中开启
- 平台支持限于 Win64 和 Linux，不支持主机平台和移动端
- 作为实验性插件，API 和行为可能在后续版本中发生变化

尽管标记为实验性，但 2026 年的密集更新说明 Epic 仍在积极维护此插件，适合对 WebM 格式有硬性需求的项目使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/WebMMedia)
- [Media Framework 文档](https://docs.unrealengine.com/en-US/WorkingWithMedia/MediaFramework/)