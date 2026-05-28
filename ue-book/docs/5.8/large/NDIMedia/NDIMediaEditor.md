# NDI Media

> Implements media source and media output using NDI protocol

| 属性 | 值 |
|---|---|
| 中文名 | NDI媒体插件 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（媒体资产） |
| 模块 | `NDIMedia` (Runtime), `NDIMediaEditor` (Editor), `NDIMediaRendering` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-03-14 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/NDIMedia) | |

## 用途
该插件实现了基于 NDI（Network Device Interface）协议的 `MediaSource` 和 `MediaOutput`。它为 UE5 应用提供了通过局域网（LAN）使用 NDI 标准进行视频输入和输出的能力。NDI 是一种广泛应用于专业视频制作、直播和虚拟制作领域的 IP 视频协议，允许设备之间以低延迟传输高质量的音视频流。此插件存在的目的是将 NDI 的强大功能无缝集成到虚幻引擎中，使其能与其他支持 NDI 的软件和硬件（如导播台、摄像机、采集卡等）协同工作。

## 使用场景
- **虚拟制作（Virtual Production）**：在 LED 墙拍摄或绿幕合成中，将摄影机信号作为 NDI 源接入虚幻引擎，或将引擎渲染结果通过 NDI 输出给监视器或导播系统。
- **多机位直播/推流**：将虚拟摄像机视图或其他引擎画面通过 NDI 输出，供 OBS、vMix 等推流软件作为输入源使用。
- **远程监控与审查**：团队成员可以通过支持 NDI 的播放器远程实时查看虚幻引擎内的画面。
- **多应用协作**：与其他支持 NDI 的图形或视频软件（如 TouchDesigner, Adobe Premiere）交换实时视频流。

## 蓝图用法
该插件的核心功能（媒体源和媒体输出）通过标准的 `MediaSource` 和 `MediaOutput` 蓝图资产暴露。在编辑器中创建这些资产后，可以在蓝图中通过媒体播放器节点进行控制。

### 核心资产
| 资产类型 | 说明 | 所在类 |
|---|---|---|
| `NDI Media Source` | 用于定义一个 NDI 视频输入源 | `UNDIMediaSource` |
| `NDI Media Output` | 用于定义一个 NDI 视频输出目标 | `UNDIMediaOutput` |

### 使用示例（蓝图描述）
1.  **接收 NDI 流**：
    - 在内容浏览器中右键 -> `Media` -> `Media Sources + Outputs` -> `NDI Media Source`，创建源资产。
    - 在源资产详情中，填写要接收的 NDI 源名称。
    - 在蓝图中，使用 `Media Player` 的 `Open Source` 节点，连接创建的 `NDI Media Source` 资产。
    - 将 `Media Player` 的输出连接到 `Media Texture`，然后通过 `Material` 或 `Media Profile` 显示在 Actor 上。
2.  **发送 NDI 流**：
    - 在内容浏览器中右键 -> `Media` -> `Media Sources + Outputs` -> `NDI Media Output`，创建输出资产。
    - 在蓝图中，使用 `Scene Capture Component 2D` 或 `Media Bundle` 捕获画面。
    - 使用 `Media Output` 的 `Capture Scene` 节点，将 `Scene Capture Component 2D` 的输出发送到 `NDI Media Output` 资产。

## C++ 用法
核心类位于 `NDIMedia` 运行时模块中。

### 头文件引入
```cpp
#include "NDIMediaSource.h"
#include "NDIMediaOutput.h"
```

### 基本用法
创建和配置媒体源与输出。
```cpp
// 创建NDI媒体源
UNDIMediaSource* NDISource = NewObject<UNDIMediaSource>();
NDISource->SetNDISourceName(TEXT("MyNDISource"));
// 使用MediaPlayer打开该源
MediaPlayer->OpenSource(NDISource);

// 创建NDI媒体输出
UNDIMediaOutput* NDIOutput = NewObject<UNDIMediaOutput>();
NDIOutput->SetNDIOutputName(TEXT("UE5_NDI_Output"));
// 使用MediaCapture开始输出
UMediaCapture* MediaCapture = UMediaCapture::CreateMediaCapture();
MediaCapture->CaptureScene(SceneCaptureComponent2D, NDIOutput);
```

### 进阶用法
处理媒体播放事件和错误。
```cpp
// 绑定媒体打开完成事件
MediaPlayer->OnMediaOpened.AddDynamic(this, &AMyActor::OnMediaOpened);
// 绑定媒体错误事件
MediaPlayer->OnMediaOpenFailed.AddDynamic(this, &AMyActor::OnMediaOpenFailed);

void AMyActor::OnMediaOpened(FString OpenedUrl)
{
    UE_LOG(LogTemp, Log, TEXT("NDI Media Source Opened: %s"), *OpenedUrl);
}

void AMyActor::OnMediaOpenFailed(FString FailedUrl)
{
    UE_LOG(LogTemp, Error, TEXT("Failed to open NDI Media Source: %s"), *FailedUrl);
}
```
**注意**：上述代码为概念示例，具体 API 调用请参考最新源码和头文件。

## Demo 示例
一个最小化的、用于接收并显示 NDI 流的 Actor。
```cpp
// NDIReceiverActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MediaPlayer.h"
#include "NDIReceiverActor.generated.h"

UCLASS()
class ANDIReceiverActor : public AActor
{
    GENERATED_BODY()

public:
    ANDIReceiverActor();

    virtual void BeginPlay() override;

    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UPROPERTY(EditAnywhere, Category="NDI")
    UNDIMediaSource* NDISource;

    UPROPERTY(VisibleAnywhere, Category="NDI")
    UMediaPlayer* MediaPlayer;

    UPROPERTY(VisibleAnywhere, Category="NDI")
    UMediaTexture* MediaTexture;
};

// NDIReceiverActor.cpp
#include "NDIReceiverActor.h"
#include "MediaTexture.h"
#include "NDIMediaSource.h"

ANDIReceiverActor::ANDIReceiverActor()
{
    PrimaryActorTick.bCanEverTick = false;
    // 创建媒体播放器和纹理组件
    MediaPlayer = CreateDefaultSubobject<UMediaPlayer>(TEXT("MediaPlayer"));
    MediaTexture = CreateDefaultSubobject<UMediaTexture>(TEXT("MediaTexture"));
    MediaTexture->SetMediaPlayer(MediaPlayer);
}

void ANDIReceiverActor::BeginPlay()
{
    Super::BeginPlay();
    if (NDISource && MediaPlayer)
    {
        // 打开NDI源
        MediaPlayer->OpenSource(NDISource);
    }
}

void ANDIReceiverActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (MediaPlayer)
    {
        MediaPlayer->Close();
    }
    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖
该插件本身依赖 `MediaIOFramework` 和 `MediaPlayerEditor` 插件。对于使用该插件的项目模块，在 `Build.cs` 中需要添加以下依赖（仅列出该插件特有的依赖）：

| 模块 | 用途 |
|---|---|
| `NDIMedia` | NDI 媒体源与输出的核心运行时实现 |
| `MediaIOFramework` | 提供媒体输入输出的基础框架 |
| `NDISDK` | 第三方 NDI 软件开发工具包 |

## 维护状态

### 近期更新
| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `96b8b04b` | Media IO: Fix to recent CL 54396736 for ImgMedia and NDI players emitting incorrect SourceOpened ana | 修复了 NDI 和图像媒体播放器发出错误“SourceOpened”分析事件的问题 |
| 2026-05-23 | `42746f7a` | Media IO: Added additional engine analytics information to various media players and capture and pro | 为 NDI 等多种媒体播放器和采集程序添加了额外的引擎分析信息 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 将虚拟制作资产移至新的资产类别（如 Media Sources + Outputs） |
| 2026-05-12 | `c657503b` | [Media] Add missing UAssetDefinition entries for concrete UMediaSource and UMediaOutput subclasses t | 添加了缺失的资产定义条目，支持在编辑器中创建 NDI 源和输出资产 |
| 2026-04-23 | `efcad028` | HDR: Fix HDR normalization factor across media causing incorrect brightness levels going from/to the | 修复了跨媒体 HDR 归一化导致亮度不正确的问题 |

### 维护评价
**活跃维护**。
- **年龄**：该插件于 2024 年 3 月创建，是较新的功能。
- **近期活动**：提交历史显示在 2026 年 5 月仍有**高频率**的功能性更新、Bug 修复和资产整合工作，表明它仍在被 Epic 积极维护和改进。
- **状态**：虽然 `.uplugin` 中标记为 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`，但持续的提交记录表明它已具备相当的完整性，并正在向稳定版演进。
- **推荐**：对于有明确 NDI 集成需求的虚拟制作、直播或专业视频项目，这是一个**推荐使用**的官方插件。尽管是实验性状态，但其活跃的维护状态降低了使用风险。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/NDIMedia)
- 官方文档：无
- 测试用例：未在给定信息中发现。