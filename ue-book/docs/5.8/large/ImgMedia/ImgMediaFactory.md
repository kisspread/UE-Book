# Image Sequence Media Player

> Implements a media player for image sequences in EXR and other formats.

| 属性 | 值 |
|---|---|
| 中文名 | 图像序列播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ImgMedia` (Runtime), `ImgMediaEditor` (Runtime), `ImgMediaEngine` (Runtime), `ImgMediaFactory` (Runtime), `OpenExrWrapper` (Runtime), `ExrReaderGpu` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-08-30 |
| 年龄标签 | 🏛️ 文物（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ImgMedia) | |

## 用途

ImgMedia 是 UE 的媒体播放框架（Media Framework）的一个后端实现，专门用于将**图像序列当作视频**来播放。它解决的核心问题是：影视级特效制作（VFX）和虚拟制片（Virtual Production）中，美术团队通常将渲染输出保存为 EXR 等逐帧图像序列，而不是传统视频文件。这个插件让引擎能像播放视频一样播放这些图像序列，支持正播、倒播、循环、逐帧拖动等操作。

为什么需要单独一个插件？因为图像序列与传统视频流（MP4/MOV 等）有本质区别：
- 图像序列是**独立文件**的集合，而非编码压缩的流
- 每帧可能非常大（EXR 通常是未压缩的 HDR 数据）
- 需要不同的**预缓存策略**（在播放头前后预加载帧）
- 支持 **GPU 加速解码** EXR（通过 ExrReaderGpu 模块）

支持的格式：**EXR**（主推，GPU 加速）、BMP、JPG、PNG。

## 使用场景

- 你在做**影视级渲染回放**：渲染农场输出了数百张 EXR 帧，需要在引擎内实时预览 → 用 ImgMedia
- 你在做 **Virtual Production**：LED 墙上需要播放预先渲染好的高质量图像序列作为背景 → 用 ImgMedia
- 你需要在 **Sequencer** 中精确同步图像序列与角色动画 → 用 ImgMedia（天然支持帧精确播放）
- 你想在开发阶段用**低分辨率代理**快速迭代，最终用高分辨率原图 → 用 ImgMedia 的 Proxy 系统
- 你需要**倒放**图像序列（传统视频编解码器倒放困难）→ 用 ImgMedia（原生支持）

## 蓝图用法

ImgMedia 本身作为 Media Framework 的后端，通过标准的 `UMediaPlayer`、`UMediaTexture`、`UMediaSource` 接口使用。它提供的独特蓝图功能主要集中在设置层面。

### 核心设置类

通过 **Project Settings → Plugins → ImgMedia** 或访问 `UImgMediaSettings` 配置播放行为：

| 设置 | 说明 | 默认值 |
|---|---|---|
| `DefaultFrameRate` | 未指定帧率时的默认帧率 | 24fps |
| `BandwidthThrottlingEnabled` | 带宽不足时自动跳帧 | - |
| `CacheBehindPercentage` | 播放头后方缓存占比（%） | 25% |
| `CacheSizeGB` | 预缓存滑动窗口最大内存（GB） | 1 GB |
| `GlobalCacheSizeGB` | 全局前瞻缓存大小（GB） | 1 GB |
| `UseGlobalCache` | 是否启用全局缓存 | - |
| `CacheThreads` | 缓存线程数（0=核心数） | 2 |
| `ExrDecoderThreads` | EXR 解码线程数（0=自动） | 0 |

### 使用示例（蓝图描述）

**基础用法**：
1. 在场景中放置一个 `MediaPlayer` 资产，将 Output Format 设为 Desired
2. 创建一个 `ImgMediaSource` 资产，设置 `SequencePath` 指向图像序列目录（如 `D:/Render/frame_%04d.exr`）
3. 创建一个 `MediaTexture` 资产，将其 Source 设为上面的 `MediaPlayer`
4. 将 `MediaTexture` 作为材质的纹理参数，或直接赋给 Static Mesh 的材质
5. 调用 `MediaPlayer → Open Source`（传入 ImgMediaSource），开始播放

**与 Sequencer 集成**：
1. 在 Sequencer 中添加 `MediaTrack`
2. 关联 MediaPlayer
3. 图像序列会自动与 Sequencer 时间轴同步

## C++ 用法

### 头文件引入

```cpp
#include "ImgMediaSettings.h"
```

### 基本用法：访问 ImgMedia 设置

```cpp
// 获取 ImgMedia 设置单例
const UImgMediaSettings* Settings = GetDefault<UImgMediaSettings>();

// 读取配置
FFrameRate DefaultRate = Settings->DefaultFrameRate;
bool bBandwidth = Settings->BandwidthThrottlingEnabled;
float CacheBehind = Settings->CacheBehindPercentage;
int32 Threads = Settings->CacheThreads;

// 获取代理名称
FString ProxyTag = Settings->GetDefaultProxy();
if (!ProxyTag.IsEmpty())
{
    UE_LOG(LogTemp, Log, TEXT("Using proxy: %s"), *ProxyTag);
}
```

### 进阶用法：监听设置变更（编辑器内）

```cpp
#if WITH_EDITOR
// 注册设置变更回调
UImgMediaSettings::FOnImgMediaSettingsChanged& Delegate = UImgMediaSettings::OnSettingsChanged();
Delegate.AddLambda([](const UImgMediaSettings* ChangedSettings)
{
    UE_LOG(LogTemp, Log, TEXT("ImgMedia settings changed, cache size: %.2f GB"), 
        ChangedSettings->CacheSizeGB);
});
#endif
```

## Demo 示例

### 自定义 ImgMedia 配置组件

```cpp
// ImgMediaConfigHelper.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MediaPlayer.h"
#include "MediaSource.h"
#include "ImgMediaConfigHelper.generated.h"

UCLASS(ClassGroup=(Media), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UImgMediaConfigHelper : public UActorComponent
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category="Media")
    UMediaPlayer* MediaPlayer;

    UPROPERTY(EditAnywhere, Category="Media")
    UMediaSource* ImageSequenceSource;

    UFUNCTION(BlueprintCallable, Category="Media")
    bool PlaySequence();

    UFUNCTION(BlueprintCallable, Category="Media")
    void SetBandwidthThrottling(bool bEnabled);
};
```

```cpp
// ImgMediaConfigHelper.cpp
#include "ImgMediaConfigHelper.h"
#include "ImgMediaSettings.h"

bool UImgMediaConfigHelper::PlaySequence()
{
    if (!MediaPlayer || !ImageSequenceSource)
    {
        UE_LOG(LogTemp, Warning, TEXT("MediaPlayer or ImageSequenceSource is null"));
        return false;
    }

    return MediaPlayer->OpenSource(ImageSequenceSource);
}

void UImgMediaConfigHelper::SetBandwidthThrottling(bool bEnabled)
{
    UImgMediaSettings* Settings = GetMutableDefault<UImgMediaSettings>();
    if (Settings)
    {
        Settings->BandwidthThrottlingEnabled = bEnabled;
        Settings->SaveConfig();
    }
}
```

## 模块依赖

从 Build.cs 分析，该插件有多个内部模块互相依赖。以下为**使用者**需要关注的外部依赖：

| 模块 | 用途 |
|---|---|
| `MediaAssets` | Media Framework 核心资产类（MediaPlayer、MediaTexture、MediaSource） |
| `MediaUtils` | Media Framework 工具库 |
| `ImageWrapper` | BMP/JPG/PNG 格式的图像解码支持 |
| `OpenEXR` / `Imath` | EXR 图像格式底层库（被 OpenExrWrapper 封装） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `edcd0d53` | [ImgMedia] refresh single-frame sequences on tile visibility changes | 单帧图像序列在瓦片可见性变化时自动刷新 |
| 2026-05-26 | `cf292c75` | [ImgMedia] Use AR-constrained view rect for tile mip selection | 瓦片 MIP 级别选择使用 AR 约束的视图矩形 |
| 2026-05-26 | `96b8b04b` | Media IO: Fix to recent CL 54396736 for ImgMedia and NDI players emitting incorrect SourceOpened | 修复 ImgMedia 和 NDI 播放器发送错误 SourceOpened 事件的问题 |
| 2026-05-23 | `42746f7a` | Media IO: Added additional engine analytics information to various media players and capture and pro | 为多个媒体播放器和采集设备添加引擎分析信息 |
| 2026-05-22 | `7d256b73` | [Media] Add shared Media category to the Level Editor Window menu | 在关卡编辑器窗口菜单中添加共享 Media 分类 |

### 维护评价

**活跃维护** ✅

- **创建时间**：2017 年 8 月，已有约 8 年历史，是 Media Framework 3.0 的核心组件
- **更新频率**：近期（2026 年 5 月）仍有活跃提交，包括瓦片流式加载优化、分析功能增强和 bug 修复
- **维护质量**：作为 Epic 官方维护的媒体播放后端，随引擎版本持续更新，特别是随着 **Nanite 瓦片流式加载**系统的成熟，ImgMedia 也在适配瓦片级别的图像序列播放
- **稳定性**：经过多年的 VFX/VP 生产环境验证，核心功能稳定
- **已知限制**：大型 EXR 序列的内存占用较高，需要合理配置缓存参数；移动端仅支持 BMP/JPG/PNG，不支持 EXR

**推荐使用**：如果你的工作流涉及图像序列播放（特别是 EXR），这是官方唯一推荐的解决方案，生产环境可靠。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ImgMedia)
- [官方文档](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview)