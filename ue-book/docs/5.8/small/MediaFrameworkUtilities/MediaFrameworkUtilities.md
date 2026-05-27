# Media Framework Utilities

> This plugin provides utility assets and actors designed to simplify the Media Framework setup. It includes access to the the Media Profile editor.

| 属性 | 值 |
|---|---|
| 中文名 | 媒体框架工具 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、媒体资产） |
| 模块 | `MediaFrameworkUtilities` (Runtime), `MediaFrameworkUtilitiesEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaFrameworkUtilities) | |

## 用途

MediaFrameworkUtilities 插件旨在降低媒体播放器框架的集成复杂度。它通过提供预先配置好的资产（MediaBundle）和基础 Actor（MediaBundleActorBase），将播放视频音频所需的多个资产（媒体源、媒体播放器、媒体纹理、材质）打包在一起，并管理它们的生命周期。同时，该插件还引入了 **媒体配置文件（Media Profile）** 概念和编辑器支持，允许在不同硬件或场景下快速切换媒体输入输出方案，特别适合需要处理多路媒体流、复杂媒体管线或进行镜头畸变校正的项目。

## 使用场景

- 你需要在项目中快速集成并播放一个视频，不想手动创建和连接 Media Player、Media Texture、Material 等多个资产。
- 你的项目需要管理多套媒体设备配置（如演播室、外场拍摄、直播推流），需要在开发和运行时快速切换。
- 你需要对视频流进行镜头畸变校正（Lens Distortion），并生成对应的位移贴图。
- 你使用 Blackmagic 或 AJA 等专业视频采集卡，并希望自动配置媒体输入。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Media Bundle` | 获取当前 Actor 关联的 MediaBundle 资产 | `AMediaBundleActorBase` |
| `Request Open Media Source` | 请求打开媒体源（触发播放） | `AMediaBundleActorBase` |
| `Request Close Media Source` | 请求关闭媒体源 | `AMediaBundleActorBase` |
| `Set Component` | 设置用于渲染媒体的基元组件和声音组件 | `AMediaBundleActorBase` |
| `Get Material` | 获取 MediaBundle 内的材质 | `UMediaBundle` |
| `Get Media Player` | 获取 MediaBundle 内的媒体播放器 | `UMediaBundle` |
| `Get Media Texture` | 获取 MediaBundle 内的媒体纹理 | `UMediaBundle` |
| `Get Media Source` | 获取 MediaBundle 内的媒体源 | `UMediaBundle` |
| `Get Lens Displacement Texture` | 获取镜头畸变校正生成的位移纹理 | `UMediaBundle` |
| `Get Media Profile` | 获取当前激活的媒体配置文件 | `UMediaProfileBlueprintLibrary` |
| `Set Media Profile` | 设置激活的媒体配置文件 | `UMediaProfileBlueprintLibrary` |
| `Get All Media Source Proxy` | 获取所有媒体源代理 | `UMediaProfileBlueprintLibrary` |
| `Get All Media Output Proxy` | 获取所有媒体输出代理 | `UMediaProfileBlueprintLibrary` |

### 使用示例（蓝图描述）

1. **快速播放一个视频**：
   - 将 `AMediaBundleActorBase` 拖入场景。
   - 在其细节面板中，为 `MediaBundle` 属性指定一个已创建的 `UMediaBundle` 资产。
   - 勾选 `bAutoPlay` 选项，游戏开始时将自动播放。
   - 若需通过逻辑控制，可在蓝图中使用 `Request Open Media Source` 和 `Request Close Media Source` 节点。

2. **动态切换媒体配置文件**：
   - 在游戏设置界面，通过 `Get All Media Source Proxy` 获取可用设备列表。
   - 调用 `Set Media Profile` 并传入选中的配置文件对象，即可全局切换媒体输入源。

3. **使用镜头畸变校正**：
   - 在 `UMediaBundle` 资产中，配置 `LensParameters`。
   - 通过 `Get Lens Displacement Texture` 获取生成的位移贴图，可将其用于后期处理材质中校正畸变。

## C++ 用法

### 头文件引入

```cpp
#include "MediaBundle.h"
#include "MediaBundleActorBase.h"
#include "MediaProfileBlueprintLibrary.h"
```

### 基本用法

从 `AMediaBundleActorBase` 和 `UMediaBundle` 的公开接口来看，核心用法是控制媒体播放状态。

```cpp
// 在某个 Actor 中
// 1. 获取 MediaBundle 资产
UMediaBundle* MyMediaBundle = ...; // 通过资产加载或属性引用获取

// 2. 通过 MediaBundle 控制播放
if (MyMediaBundle)
{
    // 打开媒体源
    MyMediaBundle->OpenMediaSource();
    // 检查是否正在播放
    bool bPlaying = MyMediaBundle->IsPlaying();
    // 关闭媒体源
    MyMediaBundle->CloseMediaSource();
}

// 3. 监听媒体状态变化
MyMediaBundle->OnMediaStateChanged().AddUObject(this, &AMyClass::HandleMediaStateChanged);
```

### 进阶用法

结合 `AMediaBundleActorBase` 和媒体配置文件，实现更灵活的控制。

```cpp
// 动态切换媒体配置文件
void AMyGameMode::SwitchToProfile(UMediaProfile* NewProfile)
{
    UMediaProfileBlueprintLibrary::SetMediaProfile(NewProfile);
    // 媒体系统将根据新配置文件重新初始化输入输出
}

// 获取当前所有可用的媒体输入源代理
TArray<UProxyMediaSource*> AvailableSources = UMediaProfileBlueprintLibrary::GetAllMediaSourceProxy();
for (UProxyMediaSource* Source : AvailableSources)
{
    // 处理每个可用设备
}
```

## Demo 示例

以下是一个最小示例，展示如何创建一个自定义的媒体播放 Actor，并通过代码控制播放。

### MyMediaActor.h
```cpp
#pragma once
#include "MediaBundleActorBase.h"
#include "MyMediaActor.generated.h"

UCLASS()
class AMyMediaActor : public AMediaBundleActorBase
{
	GENERATED_BODY()

public:
    // 可在蓝图中调用的播放函数
    UFUNCTION(BlueprintCallable, Category = "Media")
    void PlayMedia();

    UFUNCTION(BlueprintCallable, Category = "Media")
    void StopMedia();

private:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    // 处理媒体状态变化
    UFUNCTION()
    void OnMediaStatusChanged(bool bIsPlaying);
};
```

### MyMediaActor.cpp
```cpp
#include "MyMediaActor.h"
#include "MediaBundle.h"

void AMyMediaActor::BeginPlay()
{
    Super::BeginPlay();
    // 绑定状态变化事件
    if (UMediaBundle* Bundle = GetMediaBundle())
    {
        Bundle->OnMediaStateChanged().AddUObject(this, &AMyMediaActor::OnMediaStatusChanged);
    }
}

void AMyMediaActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (UMediaBundle* Bundle = GetMediaBundle())
    {
        Bundle->OnMediaStateChanged().RemoveAll(this);
    }
    Super::EndPlay(EndPlayReason);
}

void AMyMediaActor::PlayMedia()
{
    RequestOpenMediaSource();
}

void AMyMediaActor::StopMedia()
{
    RequestCloseMediaSource();
}

void AMyMediaActor::OnMediaStatusChanged(bool bIsPlaying)
{
    if (bIsPlaying)
    {
        UE_LOG(LogTemp, Log, TEXT("Media started playing."));
    }
    else
    {
        UE_LOG(LogTemp, Log, TEXT("Media stopped playing."));
    }
}
```

## 模块依赖

要使用此插件，你的模块通常无需直接依赖 `MediaFrameworkUtilities`，因为它主要提供资产和 Actor。但如果你需要在 C++ 中扩展其功能，则需添加以下依赖：

| 模块 | 用途 |
|---|---|
| `MediaFrameworkUtilities` | 访问 MediaBundle, MediaBundleActorBase 等核心类 |
| `MediaAssets` | 使用 MediaPlayer, MediaTexture, MediaSource 等媒体资产类 |
| `OpenCVLensDistortion` | 处理镜头畸变参数（FOpenCVLensDistortionParameters） |
| `TimeManagement` | 使用时间同步源（UTimeSynchronizationSource） |
| `MediaUtils` | 媒体配置文件（UMediaProfile）相关功能 |

**注意**：`MediaFrameworkUtilitiesEditor` 模块仅在编辑器环境下使用，用于提供媒体配置文件编辑器等工具，运行时代码不应依赖它。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `36c08694` | Media IO - Populate Media Configuration when using auto for Blackmagic and Aja cards | 为 Blackmagic 和 AJA 采集卡的自动模式填充媒体配置 |
| 2026-05-22 | `7d256b73` | [Media] Add shared Media category to the Level Editor Window menu | 在关卡编辑器窗口菜单中添加共享的“媒体”类别 |
| 2026-05-21 | `ff9996e8` | Media Profile: Fixed issue where ElectraProtron issue would not play a new video after it had alread | 媒体配置文件：修复 ElectraProtron 播放器在播放过一次后无法播放新视频的问题 |
| 2026-05-20 | `54cbb9f8` | Ensure a transient MediaProfile always exists from startup | 确保启动时始终存在一个临时的媒体配置文件 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口：通过通知客户端关联或取消关联来减少强制性的样板代码 |

### 维护评价

该插件由 Epic Games 维护，**仍在活跃更新**。从近期的提交记录看（截至2026年5月），团队仍在持续改进其功能，特别是针对专业视频采集卡（Blackmagic， AJA）的集成、媒体配置文件的稳定性以及编辑器用户体验。插件创建于2018年（UE4时代），已历经约7年，但其核心架构（MediaBundle）设计良好，并随着引擎媒体框架的演进不断更新。**推荐用于需要简化媒体管线集成和管理多套媒体方案的项目**。

**注意事项**：
1. 该插件默认**未启用**，需要在插件设置中手动开启。
2. 它主要提供**框架和工具**，具体功能的实现依赖于引擎内置的媒体播放器插件（如 Media Player, Media Foundation 等）。
3. 镜头畸变功能依赖 `OpenCVLensDistortion` 模块，确保该模块可用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaFrameworkUtilities)
- [官方文档] (暂无直接链接，可参考UE官方文档中“Media Framework”部分)