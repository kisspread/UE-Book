# Media Profile

> This plugin contains the Media Profile asset and related entities, which help manage media sources and outputs

| 属性 | 值 |
|---|---|
| 中文名 | 媒体配置 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（媒体配置资产、代理资产） |
| 模块 | `MediaProfile` (Runtime), `MediaProfileEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-23 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaProfile) | |

## 用途

Media Profile 插件提供了一种**将多个媒体输入源和输出目标组织为统一配置资产**的机制。它解决的核心问题是：在涉及多路视频输入/输出的项目中（如广播级虚拟制片、实时合成、现场直播），你需要一套中央化的配置来管理所有媒体源（Media Sources）、媒体输出（Media Outputs）、时间码提供器（Timecode Provider）和同步时钟（Genlock/Custom Time Step），而不是在项目各处散落这些配置。

本质上，Media Profile 是一个**媒体管线的"总控配置文件"**：
- 定义项目使用哪些媒体输入（如摄像机信号、视频文件）
- 定义输出目标（如外部显示器、录制设备）
- 统一管理时间码和帧同步设置
- 通过代理（Proxy）机制实现运行时动态切换媒体源/输出，而无需修改引用它们的蓝图或组件
- 自动管理媒体播放器的创建、复用和销毁，以及媒体捕获的生命周期

该插件最初从 MediaFrameworkUtilities 中拆分出来，目的是避免对 OpenCVDistortion 模块的不必要依赖。

## 使用场景

- 你正在搭建虚拟制片管线，需要同时管理多路 SDI 摄像机输入和外部显示器输出 → 用 Media Profile 集中配置所有输入输出
- 你的项目需要在不同环境（开发、测试、现场直播）之间快速切换整套媒体配置 → 为每个环境创建不同的 Media Profile 资产
- 你需要统一管理时间码提供器和 Genlock 同步，且希望能在运行时/编辑器中切换 → Media Profile 的 Apply/Reset 机制支持一键切换
- 你希望在蓝图中引用媒体源/输出，但又需要在不修改蓝图的情况下动态替换实际的媒体设备 → 使用 ProxyMediaSource / ProxyMediaOutput 代理机制
- 你使用 Composure 或其他实时合成框架，需要将渲染画面捕获到外部设备 → Media Profile 的 PlaybackManager 管理视口捕获和媒体输出生命周期

## 蓝图用法

Media Profile 插件的蓝图 API 主要集中在代理资产的查询和媒体配置的运行时管理。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsProxyValid` | 检查媒体源代理是否指向有效的媒体源 | `UProxyMediaSource` |
| `IsProxyValid` | 检查媒体输出代理是否指向有效的媒体输出 | `UProxyMediaOutput` |

### 可蓝图访问的属性

由于 `UMediaProfile`、`UMediaProfileSettings`、`UMediaProfileEditorSettings` 均标记为 `BlueprintType`，以下属性可在蓝图中读取：

| 属性 | 类型 | 说明 | 所在类 |
|---|---|---|---|
| `MediaSources` | `TArray<UMediaSource*>` | 配置的媒体输入源列表 | `UMediaProfile` |
| `MediaOutputs` | `TArray<UMediaOutput*>` | 配置的媒体输出目标列表 | `UMediaProfile` |
| `bOverrideTimecodeProvider` | `bool` | 是否覆盖项目设置中的时间码提供器 | `UMediaProfile` |
| `TimecodeProvider` | `UTimecodeProvider*` | 自定义时间码提供器 | `UMediaProfile` |
| `bOverrideCustomTimeStep` | `bool` | 是否覆盖项目设置中的自定义时间步长 | `UMediaProfile` |
| `CustomTimeStep` | `UEngineCustomTimeStep*` | 自定义时间步长（Genlock） | `UMediaProfile` |
| `bApplyInCommandlet` | `bool` | 是否在 Commandlet 中也应用启动配置 | `UMediaProfileSettings` |
| `StartupMediaProfile` | `TSoftObjectPtr<UMediaProfile>` | 项目启动时使用的 Media Profile | `UMediaProfileSettings` |

### 使用示例（蓝图描述）

**在蓝图中查询当前 Media Profile 的媒体源数量：**

1. 获取 `IMediaProfileManager` 单例 → 调用 `GetCurrentMediaProfile()`
2. 对返回的 `UMediaProfile` 调用 `NumMediaSources()` 获取输入源数量
3. 使用 `GetMediaSource(Index)` 遍历每个媒体源

**在蓝图中验证代理媒体源是否可用：**

1. 持有 `UProxyMediaSource` 引用
2. 调用 `IsProxyValid()` 节点
3. 如果返回 `true`，可安全使用该代理作为媒体源传入 MediaPlayer 组件

> 注意：大部分核心管理功能（Apply/Reset、播放管理）是 C++ 接口，蓝图中的直接操作较为有限。推荐通过 C++ 或 Editor Utility Widget 进行高级管理。

## C++ 用法

### 头文件引入

```cpp
#include "IMediaProfileModule.h"
#include "IMediaProfileManager.h"
#include "Profile/MediaProfile.h"
#include "Profile/MediaProfilePlaybackManager.h"
#include "MediaAssets/ProxyMediaSource.h"
#include "MediaAssets/ProxyMediaOutput.h"
```

### 基本用法

**获取当前 Media Profile 并查询配置**

```cpp
// 获取 Media Profile 模块
IMediaProfileModule& MediaProfileModule = FModuleManager::GetModuleChecked<IMediaProfileModule>("MediaProfile");

// 获取全局 Profile Manager
IMediaProfileManager& ProfileManager = MediaProfileModule.GetProfileManager();

// 获取当前激活的 Media Profile（可能为 null）
UMediaProfile* CurrentProfile = ProfileManager.GetCurrentMediaProfile();

if (CurrentProfile)
{
    // 查询媒体源数量
    int32 NumSources = CurrentProfile->NumMediaSources();
    
    // 获取第一个媒体源
    UMediaSource* FirstSource = CurrentProfile->GetMediaSource(0);
    
    // 查询是否覆盖了时间码设置
    UTimecodeProvider* TimecodeProvider = CurrentProfile->GetTimecodeProvider();
}
```

**监听 Media Profile 切换事件**

```cpp
IMediaProfileManager& ProfileManager = IMediaProfileManager::Get();

// 绑定配置切换回调：Previous 为旧配置，New 为新配置
ProfileManager.OnMediaProfileChanged().AddLambda(
    [](UMediaProfile* Previous, UMediaProfile* New)
    {
        UE_LOG(LogTemp, Log, TEXT("Media Profile changed from %s to %s"),
            Previous ? *Previous->GetName() : TEXT("None"),
            New ? *New->GetName() : TEXT("None"));
    }
);
```

### 进阶用法

**使用 Playback Manager 管理媒体输入播放**

```cpp
UMediaProfile* Profile = IMediaProfileManager::Get().GetCurrentMediaProfile();
if (!Profile) return;

UMediaProfilePlaybackManager* PlaybackManager = Profile->GetPlaybackManager();
if (!PlaybackManager) return;

// 按索引打开媒体源，获取对应的 MediaTexture 用于渲染
UMediaTexture* Texture = PlaybackManager->OpenSourceFromIndex(0);
if (Texture)
{
    // 可将 Texture 应用到材质或 UI 上显示
}

// 检查媒体源是否已打开（带消费者引用计数）
bool bIsOpen = PlaybackManager->IsSourceOpenFromIndex(0);

// 关闭媒体源，可选是否销毁 MediaPlayer
UMediaProfilePlaybackManager::FCloseSourceArgs CloseArgs;
CloseArgs.bDestroyMediaPlayer = true;
PlaybackManager->CloseSourceFromIndex(0, CloseArgs);
```

**使用 Playback Manager 管理媒体输出捕获**

```cpp
UMediaProfilePlaybackManager* PlaybackManager = Profile->GetPlaybackManager();

// 开始捕获到媒体输出（如 SDI 输出）
FMediaCaptureOptions CaptureOptions;
CaptureOptions.bAutoRestartCaptures = true;

// 捕获现有编辑器视口到媒体输出
UMediaCapture* Capture = PlaybackManager->OpenActiveViewportOutputFromIndex(0, CaptureOptions, true);

// 捕获渲染目标到媒体输出
UTextureRenderTarget2D* RenderTarget = /* 你的渲染目标 */;
UMediaCapture* RT_Capture = PlaybackManager->OpenRenderTargetOutputFromIndex(0, RenderTarget, CaptureOptions);

// 检查输出是否正在捕获
bool bCapturing = PlaybackManager->IsOutputCapturingFromIndex(0);

// 获取捕获状态
bool bHasError = false;
TOptional<EMediaCaptureState> State = PlaybackManager->GetOutputCaptureStateFromIndex(0, bHasError);

// 关闭输出捕获
UMediaProfilePlaybackManager::FCloseOutputArgs CloseOutputArgs;
CloseOutputArgs.bDestroyCaptureObjects = true;
CloseOutputArgs.Callback = FSimpleDelegate::CreateLambda([]() {
    UE_LOG(LogTemp, Log, TEXT("Capture fully stopped"));
});
PlaybackManager->CloseOutputFromIndex(0, CloseOutputArgs);
```

**使用 Proxy 代理机制动态切换媒体源**

```cpp
UProxyMediaSource* ProxySource = /* 从配置或资产中获取 */;

// 检查代理是否有效
if (ProxySource->IsProxyValid())
{
    // 获取代理指向的实际媒体源
    UMediaSource* ActualSource = ProxySource->GetMediaSource();
    
    // 获取代理链中最终的非代理媒体源（叶子节点）
    UMediaSource* LeafSource = ProxySource->GetLeafMediaSource();
}

// 运行时动态设置代理指向
ProxySource->SetDynamicMediaSource(NewMediaSource);
```

## Demo 示例

```cpp
// MediaProfileExample.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MediaProfileExample.generated.h"

class UMediaProfile;
class UMediaProfilePlaybackManager;
class UMediaTexture;
class UMediaCapture;

UCLASS()
class AMediaProfileExample : public AActor
{
    GENERATED_BODY()

public:
    AMediaProfileExample();

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    /** 开始播放所有配置的媒体源 */
    UFUNCTION(BlueprintCallable)
    void StartAllMediaSources();

    /** 停止所有媒体源 */
    UFUNCTION(BlueprintCallable)
    void StopAllMediaSources();

    /** 获取指定索引的媒体纹理 */
    UFUNCTION(BlueprintCallable)
    UMediaTexture* GetMediaTextureForSource(int32 SourceIndex) const;

protected:
    /** 监听 Media Profile 切换 */
    void OnMediaProfileChanged(UMediaProfile* Previous, UMediaProfile* New);

    UPROPERTY(Transient)
    TObjectPtr<UMediaProfile> ActiveProfile;

    UPROPERTY(Transient)
    TObjectPtr<UMediaProfilePlaybackManager> PlaybackManager;

    TArray<TObjectPtr<UMediaTexture>> ActiveTextures;
};
```

```cpp
// MediaProfileExample.cpp
#include "MediaProfileExample.h"
#include "IMediaProfileModule.h"
#include "IMediaProfileManager.h"
#include "Profile/MediaProfile.h"
#include "Profile/MediaProfilePlaybackManager.h"
#include "MediaTexture.h"
#include "MediaSource.h"

AMediaProfileExample::AMediaProfileExample()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMediaProfileExample::BeginPlay()
{
    Super::BeginPlay();

    // 绑定配置切换事件
    IMediaProfileManager& ProfileManager = IMediaProfileManager::Get();
    ProfileManager.OnMediaProfileChanged().AddUObject(this, &AMediaProfileExample::OnMediaProfileChanged);

    // 获取当前配置
    ActiveProfile = ProfileManager.GetCurrentMediaProfile();
    if (ActiveProfile)
    {
        PlaybackManager = ActiveProfile->GetPlaybackManager();
    }
}

void AMediaProfileExample::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    StopAllMediaSources();

    IMediaProfileManager& ProfileManager = IMediaProfileManager::Get();
    ProfileManager.OnMediaProfileChanged().RemoveAll(this);

    Super::EndPlay(EndPlayReason);
}

void AMediaProfileExample::StartAllMediaSources()
{
    if (!ActiveProfile || !PlaybackManager) return;

    ActiveTextures.Reset();
    int32 NumSources = ActiveProfile->NumMediaSources();

    for (int32 i = 0; i < NumSources; ++i)
    {
        UMediaTexture* Texture = PlaybackManager->OpenSourceFromIndex(i);
        if (Texture)
        {
            ActiveTextures.Add(Texture);
            UE_LOG(LogTemp, Log, TEXT("Opened media source %d, texture: %s"), i, *Texture->GetName());
        }
    }
}

void AMediaProfileExample::StopAllMediaSources()
{
    if (!ActiveProfile || !PlaybackManager) return;

    int32 NumSources = ActiveProfile->NumMediaSources();
    for (int32 i = 0; i < NumSources; ++i)
    {
        UMediaProfilePlaybackManager::FCloseSourceArgs Args;
        Args.bDestroyMediaPlayer = true;
        Args.bForceClose = true;
        PlaybackManager->CloseSourceFromIndex(i, Args);
    }

    ActiveTextures.Reset();
}

UMediaTexture* AMediaProfileExample::GetMediaTextureForSource(int32 SourceIndex) const
{
    if (!PlaybackManager) return nullptr;
    return PlaybackManager->GetSourceMediaTextureFromIndex(SourceIndex);
}

void AMediaProfileExample::OnMediaProfileChanged(UMediaProfile* Previous, UMediaProfile* New)
{
    // 配置切换时，停止旧配置的播放
    StopAllMediaSources();

    ActiveProfile = New;
    if (ActiveProfile)
    {
        PlaybackManager = ActiveProfile->GetPlaybackManager();
    }
    else
    {
        PlaybackManager = nullptr;
    }
}
```

## 模块依赖

Media Profile 插件的 Build.cs 未提供完整内容，但根据源码中引用的类型可推断以下特有依赖：

| 模块 | 用途 |
|---|---|
| `MediaAssets` | `UMediaSource`、`UMediaOutput`、`UMediaTexture`、`UMediaPlayer`、`UMediaCapture` 等核心媒体资产类型 |
| `MediaFrameworkUtils` | 媒体框架工具函数（原拆分来源模块） |
| `TimeManagement` | `UTimecodeProvider`、`UEngineCustomTimeStep` 时间码和同步时钟 |
| `MediaUtils` | `FMediaCaptureOptions`、`FMediaCaptureTransform`、`EMediaCaptureState` 等媒体捕获选项和状态枚举 |
| `RenderCore` | `FViewportClient`、`FSceneViewport` 等视口捕获相关类型 |

> 注：MediaProfileEditor 模块虽标记为 Runtime 类型，但从命名和功能推断应包含编辑器 UI 相关代码（如工具栏集成、配置面板），可能依赖 `UnrealEd` 和 `Slate` 等编辑器模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-21 | `ff9996e8` | Media Profile: Fixed issue where ElectraProtron issue would not play a new video after it had alread | 修复 ElectraProtron 播放器在已播放过视频后无法播放新视频的问题 |
| 2026-05-20 | `54cbb9f8` | Ensure a transient MediaProfile always exists from startup | 确保启动时始终存在一个临时 Media Profile 实例 |
| 2026-05-20 | `de6434f1` | Composure: Add final new icons for composite actors, layers, and passes, and minor tweaks to menu co | Composure 相关图标和菜单更新（跨插件提交，非直接 MediaProfile 改动） |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口客户端关联/断开通知机制（影响 MediaProfile 的视口捕获功能） |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回滚一次之前的提交 |

### 维护评价

Media Profile 是一个**全新创建的实验性插件**（2026 年 4 月从 MediaFrameworkUtilities 拆分），目前仍在**活跃开发**中。近期更新集中在修复播放器兼容性（ElectraProtron）和确保启动稳定性，表明 Epic 正在积极打磨该插件。

**注意事项：**
- ⚠️ 标记为 **Experimental**（`IsExperimentalVersion=true`），API 可能在后续版本中发生变化
- ⚠️ **默认未启用**（`EnabledByDefault=false`），需要在项目设置中手动启用
- 该插件面向虚拟制片和广播级应用场景，普通游戏项目通常不需要使用
- 代码结构清晰，PlaybackManager 的消费者引用计数机制设计合理，支持多组件共享同一媒体源

**推荐程度：** 如果你的项目涉及多路视频 I/O 管理，推荐在 5.8+ 版本中评估使用，但需注意实验性标记意味着尚不建议用于生产环境的关键路径。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaProfile)
- [测试用例]（未在插件目录中发现独立测试文件）