# Electra Player

> Cross platform media player for local files and internet streaming.
> Also provides optimized local mp4 file only player (Protron) for desktop machines.

| 属性 | 值 |
|---|---|
| 中文名 | 电磁播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ElectraPlayerFactory` (Runtime), `ElectraPlayerPlugin` (Runtime), `ElectraPlayerPluginHandler` (Runtime), `ElectraPlayerRuntime` (Runtime), `ElectraProtron` (Runtime), `ElectraProtronFactory` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-01-06 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraPlayer) | |

---

> **杯型：xlarge（175 文件）** — 本文档为汇总页。该插件包含 6 个 Runtime 模块，建议按子模块拆分阅读。

---

## 用途

ElectraPlayer 是 Epic Games 为 UE5 开发的**跨平台媒体播放器**，是 Unreal 媒体框架（MediaFramework）的核心后端实现之一。它解决了以下问题：

1. **跨平台流媒体播放**：支持通过互联网播放 HLS、DASH 等自适应流媒体协议的视频和音频内容，也支持本地文件播放。
2. **桌面端高性能本地播放（Protron）**：提供一个名为 Protron 的优化路径，专门用于桌面平台（Windows）的本地 MP4 文件播放，绕过完整的流媒体处理管道，获得更低延迟和更高性能。
3. **工厂模式自动选择**：通过 `ElectraPlayerFactory` 和 `ElectraProtronFactory` 两个工厂模块，引擎可根据媒体源类型和平台自动选择最优的播放器实现。
4. **MediaFramework 集成**：通过 `ElectraPlayerPlugin` 和 `ElectraPlayerPluginHandler` 模块无缝接入 UE 的 Media Framework 体系，提供标准的 `IMediaPlayer` 接口。

简单来说，**ElectraPlayer 是 UE5 默认的视频/音频播放引擎**，替代了早期基于平台原生播放器的方案，提供了统一的跨平台媒体播放能力。

## 使用场景

- 你在游戏内需要播放过场动画视频 → 使用 ElectraPlayer 加载本地 MP4 文件渲染到 MediaTexture
- 你需要播放来自互联网的 HLS 自适应码率直播流 → ElectraPlayer 作为后端播放器
- 你在 Windows 桌面项目中需要低延迟播放本地 MP4 → 启用 Protron 优化路径
- 你需要在 UI 中嵌入视频播放 → 通过 Media Framework 的 `UMediaPlayer` + `UMediaTexture` + `UMaterial` 组合实现
- 你需要播放带字幕的流媒体内容 → ElectraPlayer 内置字幕媒体段预取支持

## 蓝图用法

ElectraPlayer 本身作为 Media Framework 的后端实现，不直接暴露大量蓝图节点。用户通过标准的 `UMediaPlayer` 蓝图接口使用它。但通过 **Project Settings** 可配置播放器选择策略。

### 核心配置（Project Settings → Plugins → Electra Protron Factory）

| 设置项 | 说明 | 类型 |
|---|---|---|
| `bPreferProtronInEditor` | 当媒体源选择"自动"时，编辑器环境是否优先使用 Protron 代替 Electra | `bool` |
| `bPreferProtronInGame` | 当媒体源选择"自动"时，游戏运行时是否优先使用 Protron 代替 Electra | `bool` |

### 标准 MediaFramework 蓝图流程

```
[Open Source (URL/File)] → [UMediaPlayer] → [UMediaTexture] → [UMaterial] → [UMaterialInstanceDynamic] → [Set Material on Mesh]
```

在蓝图中使用 ElectraPlayer 无需特殊节点——创建 `UMediaPlayer` 资产时，引擎会自动发现并使用 ElectraPlayer 作为可用的媒体播放器后端。

## C++ 用法

### 头文件引入

```cpp
// 引用 ElectraProtronFactory 模块（用于自定义 Protron 选择逻辑）
#include "ElectraProtronFactorySettings.h"

// 引用 MediaFramework 标准头文件（通常通过 UMediaPlayer 使用）
#include "MediaPlayer.h"
#include "MediaTexture.h"
```

### 基本用法：通过 UMediaPlayer 使用 ElectraPlayer

```cpp
// 创建 MediaSource 并打开
// 来源：标准 MediaFramework 用法，ElectraPlayer 作为后端自动加载
UMediaSource* MediaSource = /* 你的媒体源 */;
UMediaPlayer* MediaPlayer = /* 你的媒体播放器 */;

// OpenSource 内部会通过 PluginHandler 选择 ElectraPlayer 或 Protron
if (MediaPlayer->OpenSource(MediaSource))
{
    // 开始播放
    MediaPlayer->Play();
    
    // 检查播放状态
    if (MediaPlayer->IsPlaying())
    {
        UE_LOG(LogTemp, Log, TEXT("媒体正在播放"));
    }
}
```

### 进阶用法：自定义 Protron 偏好设置

```cpp
// 获取 Protron 工厂设置
// 来源：Source/ElectraProtronFactory/Private/ElectraProtronFactorySettings.h
UElectraProtronFactorySettings* Settings = GetMutableDefault<UElectraProtronFactorySettings>();

// 在游戏中强制使用 Protron（本地 MP4 高性能路径）
Settings->bPreferProtronInGame = true;
Settings->SaveConfig();

// 注意：此设置控制的是当媒体源未明确指定播放器时的行为
// 若媒体源已指定播放器类型，则此设置不生效
```

### 进阶用法：监听媒体事件

```cpp
// 通过委托监听播放结束等事件
// 来源：标准 MediaFramework 事件体系
MediaPlayer->OnEndReached.AddDynamic(this, &AMyActor::OnVideoFinished);
MediaPlayer->OnMediaOpened.AddDynamic(this, &AMyActor::OnVideoOpened);

void AMyActor::OnVideoFinished()
{
    UE_LOG(LogTemp, Log, TEXT("视频播放完毕"));
}

void AMyActor::OnVideoOpened(FString OpenedUrl)
{
    UE_LOG(LogTemp, Log, TEXT("视频已打开: %s"), *OpenedUrl);
}
```

## Demo 示例

### 在 Actor 中播放本地视频到 Mesh

```cpp
// MyVideoActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"
#include "MediaSource.h"
#include "MyVideoActor.generated.h"

UCLASS()
class AMyVideoActor : public AActor
{
    GENERATED_BODY()

public:
    AMyVideoActor();

    UPROPERTY(EditAnywhere, Category = "Video")
    UMediaPlayer* MediaPlayer;

    UPROPERTY(EditAnywhere, Category = "Video")
    UMediaSource* MediaSource;

    UPROPERTY(EditAnywhere, Category = "Video")
    UMediaTexture* MediaTexture;

    UPROPERTY(VisibleAnywhere)
    UStaticMeshComponent* ScreenMesh;

    UFUNCTION(BlueprintCallable, Category = "Video")
    void PlayVideo();

    UFUNCTION(BlueprintCallable, Category = "Video")
    void StopVideo();

    UFUNCTION()
    void OnVideoOpened(FString OpenedUrl);

    UFUNCTION()
    void OnVideoEndReached();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
};
```

```cpp
// MyVideoActor.cpp
#include "MyVideoActor.h"
#include "Materials/MaterialInstanceDynamic.h"

AMyVideoActor::AMyVideoActor()
{
    PrimaryActorTick.bCanEverTick = false;

    ScreenMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("ScreenMesh"));
    RootComponent = ScreenMesh;

    // 使用引擎默认的平面网格作为屏幕
    static ConstructorHelpers::FObjectFinder<UStaticMesh> PlaneMesh(
        TEXT("/Engine/BasicShapes/Plane.Plane"));
    if (PlaneMesh.Succeeded())
    {
        ScreenMesh->SetStaticMesh(PlaneMesh.Object);
        ScreenMesh->SetWorldScale3D(FVector(2.0f, 1.6f, 1.0f)); // 16:10 比例
    }
}

void AMyVideoActor::BeginPlay()
{
    Super::BeginPlay();

    if (MediaPlayer && MediaSource)
    {
        MediaPlayer->OnMediaOpened.AddDynamic(this, &AMyVideoActor::OnVideoOpened);
        MediaPlayer->OnEndReached.AddDynamic(this, &AMyVideoActor::OnVideoEndReached);
    }
}

void AMyVideoActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    StopVideo();
    Super::EndPlay(EndPlayReason);
}

void AMyVideoActor::PlayVideo()
{
    if (!MediaPlayer || !MediaSource)
    {
        UE_LOG(LogTemp, Warning, TEXT("MediaPlayer 或 MediaSource 未设置"));
        return;
    }

    // 将 MediaTexture 绑定到材质
    if (MediaTexture && ScreenMesh)
    {
        UMaterialInstanceDynamic* DynMaterial = ScreenMesh->CreateAndSetMaterialInstanceDynamic(0);
        if (DynMaterial)
        {
            // "VideoTexture" 是材质中纹理参数的名称
            DynMaterial->SetTextureParameterValue(TEXT("VideoTexture"), MediaTexture);
        }
    }

    // 打开媒体源 —— ElectraPlayer 会自动被选为后端
    if (MediaPlayer->OpenSource(MediaSource))
    {
        MediaPlayer->Play();
    }
}

void AMyVideoActor::StopVideo()
{
    if (MediaPlayer)
    {
        MediaPlayer->Close();
    }
}

void AMyVideoActor::OnVideoOpened(FString OpenedUrl)
{
    UE_LOG(LogTemp, Log, TEXT("视频已打开: %s，时长: %.2f 秒"),
        *OpenedUrl, MediaPlayer->GetDuration().GetTotalSeconds());
}

void AMyVideoActor::OnVideoEndReached()
{
    UE_LOG(LogTemp, Log, TEXT("视频播放完毕，正在关闭..."));
    MediaPlayer->Close();
}
```

## 模块架构

该插件由 6 个 Runtime 模块组成，按职责分层：

```
┌──────────────────────────────────────────────────────┐
│                  UMediaPlayer (Engine)                │  ← 用户接口层
├──────────────────┬───────────────────────────────────┤
│ ElectraPlayer    │  ElectraProtron                   │  ← 播放器实现层
│ Plugin           │  (本地MP4优化路径)                  │
├──────────────────┴───────────────────────────────────┤
│            ElectraPlayerRuntime                      │  ← 核心运行时
│    (解码、流媒体协议、缓冲、字幕等)                    │
├──────────────────┬───────────────────────────────────┤
│ ElectraPlayer    │  ElectraProtronFactory             │  ← 工厂层
│ PluginHandler    │  (Protron创建/选择)                │
├──────────────────┴───────────────────────────────────┤
│             ElectraPlayerFactory                     │  ← 基础工厂
│             (ElectraBase)                            │
└──────────────────────────────────────────────────────┘
```

| 模块 | 类型 | 职责 | 关键依赖 |
|---|---|---|---|
| `ElectraPlayerFactory` | Runtime | 基础工厂，注册 ElectraPlayer 到 MediaFramework | ElectraBase |
| `ElectraPlayerPlugin` | Runtime | Electra 播放器的 MediaFramework 接口适配 | Engine |
| `ElectraPlayerPluginHandler` | Runtime | 管理播放器插件的生命周期和选择 | ElectraPlayerRuntime, ElectraPlayerPlugin |
| `ElectraPlayerRuntime` | Runtime | 核心解码、流媒体协议处理、缓冲管理 | Engine, DirectX |
| `ElectraProtron` | Runtime | Protron 高性能本地 MP4 播放实现 | D3D12RHI |
| `ElectraProtronFactory` | Runtime | Protron 工厂，根据设置决定是否使用 Protron | ElectraBase |

## 模块依赖

从各模块的 Build.cs 分析，以下为该插件的**独特依赖**（非常见 Core/Engine/Slate 等）：

| 模块 | 用途 |
|---|---|
| `ElectraBase` | Electra 系列插件的公共基础设施库 |
| `DirectX` | ElectraPlayerRuntime 用于硬件加速解码的 DirectX 接口 |
| `D3D12RHI` | ElectraProtron 用于 Direct3D 12 渲染硬件接口的视频纹理处理 |

> 其余为标准 Core/Engine 依赖，无需额外配置。使用该插件无需手动添加依赖——它作为 MediaFramework 后端自动注册。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-21 | `ff9996e8` | Media Profile: Fixed issue where ElectraProtron issue would not play a new video after it had already played one | 修复 Protron 播放完一个视频后无法播放新视频的问题 |
| 2026-05-14 | `d15b78b3` | ElectraPlayer: Fixed streamed album metadata | 修复流媒体专辑元数据读取问题 |
| 2026-05-13 | `4340cfa6` | ElectraPlayer: Added configuration and cvars to control if decoders need to be suspended during play | 新增 CVar 配置项控制播放期间是否暂停解码器 |
| 2026-05-12 | `a6372743` | ElectraPlayer: changed an assertion to an if() condition to handle cases where .ts internal timestamp wrap around | 将 .ts 文件内部时间戳回绕时的断言改为条件判断，避免崩溃 |
| 2026-05-12 | `e3746831` | ElectraPlayer: Checking for sequence index when prefetching subtitle media segments to reduce unnecessary requests | 字幕媒体段预取时增加序列索引检查，减少不必要的网络请求 |

### 维护评价

**活跃维护** ✅

- **创建时间**：2021 年 1 月，从 Epic 内部项目（NFL）迁移到公开代码库，已有约 5 年历史
- **更新频率**：最近一次更新在 2026 年 5 月，距本文档生成仅数天，**持续活跃**
- **更新内容**：近期集中修复了 Protron 的播放切换 bug、流媒体元数据、字幕预取优化、时间戳溢出处理等，说明在持续迭代改进
- **已知限制**：Protron 仅支持 Windows 桌面平台的本地 MP4 文件；流媒体解码依赖 DirectX，跨平台支持度因平台而异
- **推荐程度**：**强烈推荐**。这是 Epic 官方维护的默认媒体播放后端，是 UE5 MediaFramework 的核心组件，用于几乎所有视频播放场景

> ⚠️ 虽然插件本身于 2021 年创建，但最近 5 天内仍有 5 次实质性提交，说明维护非常活跃，不存在废弃风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraPlayer)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)
- [ElectraProtronFactory 设置源码](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Media/ElectraPlayer/Source/ElectraProtronFactory/Private/ElectraProtronFactorySettings.h)