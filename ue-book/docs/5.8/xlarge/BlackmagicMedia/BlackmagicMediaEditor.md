# Blackmagic Media Player

> Implements input and output using Blackmagic Capture cards.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 黑魔法媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `BlackmagicCore` (Runtime), `BlackmagicMedia` (Runtime), `BlackmagicMediaEditor` (Runtime), `BlackmagicMediaFactory` (Runtime), `BlackmagicMediaOutput` (Runtime), `BlackmagicSDK` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-09-04 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/BlackmagicMedia) | |

## 用途
该插件为虚幻引擎提供了与 Blackmagic Design 专业视频采集卡（如 DeckLink 系列）的深度集成。它解决了在虚拟制片、广播和实时合成工作流中，将外部专业视频设备与虚幻引擎进行低延迟、高带宽、带时间码同步的视频输入输出问题。通过此插件，用户可以将 Blackmagic 采集卡捕获的实拍视频作为媒体源输入到引擎中，也可以将引擎渲染的视频画面通过采集卡实时输出到外部设备。

## 使用场景
- **虚拟制片**：在 LED 墙或绿幕拍摄现场，将摄像机信号通过 Blackmagic 采集卡输入 UE，进行实时合成与渲染预览。
- **现场广播与活动**：在电视直播或大型活动中，使用 UE 生成图形和动画，并通过 Blackmagic 采集卡将画面输出到转播车或播出设备。
- **后期制作预览**：在调色或特效制作流程中，将 UE 内容输出到专业监视器进行准确的色彩和质量评估。
- **多系统同步**：利用插件支持的时间码和自定义时间步进，与多个摄像机或其他设备保持帧精确同步。

## 蓝图用法
此插件主要通过资产定义（Asset Definition）在编辑器中创建配置资产，而不是直接暴露大量的蓝图节点。核心操作是配置和使用 `UBlackmagicMediaSource` 和 `UBlackmagicMediaOutput` 资产。

### 核心资产
| 资产类型 | 说明 | 所在类 |
|---|---|---|
| `Blackmagic Media Source` | 配置从 Blackmagic 采集卡输入的视频源（设备、模式等） | `UBlackmagicMediaSource` |
| `Blackmagic Media Output` | 配置通过 Blackmagic 采集卡输出的视频目标（设备、模式等） | `UBlackmagicMediaOutput` |

### 使用示例（蓝图描述）
1.  在内容浏览器中右键，选择“媒体” -> “媒体源+输出” -> “Blackmagic Media Source”，创建并配置一个媒体源资产。
2.  在资产编辑器中，设置设备、视频模式、像素格式、时间码源等参数。
3.  在场景中放置一个“媒体纹理”组件，将其媒体源引用设为刚创建的 Blackmagic Media Source 资产，即可显示输入画面。
4.  要输出画面，创建“Blackmagic Media Output”资产并配置，然后使用“媒体捕获”相关的蓝图节点将其与渲染目标或场景视口关联。

## C++ 用法

### 头文件引入
```cpp
#include "BlackmagicMediaSource.h"
#include "BlackmagicMediaOutput.h"
// 通常还需要包含媒体框架的基础头文件
#include "MediaIOCoreDefinitions.h"
```

### 基本用法
创建和配置一个 Blackmagic 媒体源（来自 `BlackmagicMedia` 模块的配置逻辑）：
```cpp
// 假设您已获取了 FMediaIOConfiguration 或相关配置信息
UBlackmagicMediaSource* MediaSource = NewObject<UBlackmagicMediaSource>();
MediaSource->SetMediaConfiguration(MediaConfiguration); // FMediaIOConfiguration 结构体，定义了设备、模式等
MediaSource->SetTimecodeFormat(EMediaIOTimecodeFormat::LTC); // 例如，设置时间码格式为 LTC
MediaSource->UpdateConfiguration();
```

### 进阶用法
使用媒体框架基础设施打开并读取媒体源（此为通用媒体框架用法，`BlackmagicMedia` 模块为此提供后端）：
```cpp
// 获取全局媒体播放器单例
IMediaModule* MediaModule = FModuleManager::LoadModulePtr<IMediaModule>(“Media”);
if (MediaModule)
{
    // 创建一个播放器实例，MediaSource 是 UBlackmagicMediaSource 资产
    IMediaPlayer* MediaPlayer = MediaModule->CreatePlayer(TEXT(“Blackmagic”));
    if (MediaPlayer->Open(MediaSource->GetMediaSourceURL(), MediaSource->GetMediaOptions()))
    {
        // 播放器已连接到 Blackmagic 采集卡输入
        // 可以通过 MediaPlayer 获取视频样本、时间码等信息
    }
}
```

## Demo 示例

**BlackmagicSimpleCapture.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include “BlackmagicSimpleCapture.generated.h”

class UBlackmagicMediaSource;
class UMediaTexture;

UCLASS()
class ABlackmagicSimpleCapture : public AActor
{
    GENERATED_BODY()

public:
    ABlackmagicSimpleCapture();

    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, Category=“Blackmagic”)
    UBlackmagicMediaSource* InputSource; // 在编辑器中指定一个已配置的 Blackmagic 媒体源资产

    UPROPERTY(VisibleAnywhere, Category=“Blackmagic”)
    UMediaTexture* MediaTexture;
};
```

**BlackmagicSimpleCapture.cpp**
```cpp
#include “BlackmagicSimpleCapture.h”
#include “BlackmagicMediaSource.h”
#include “MediaTexture.h”
#include “MediaPlayer.h”
#include “MediaSource.h”
#include “Components/StaticMeshComponent.h”

ABlackmagicSimpleCapture::ABlackmagicSimpleCapture()
{
    PrimaryActorTick.bCanEverTick = false;

    Root = CreateDefaultSubobject<USceneComponent>(TEXT(“Root”));
    RootComponent = Root;

    MediaTexture = CreateDefaultSubobject<UMediaTexture>(TEXT(“MediaTexture”));
    // 通常还需要一个网格体组件来显示这个 MediaTexture
}

void ABlackmagicSimpleCapture::BeginPlay()
{
    Super::BeginPlay();

    if (InputSource && MediaTexture)
    {
        // 创建媒体播放器
        UMediaPlayer* MediaPlayer = NewObject<UMediaPlayer>(this, TEXT(“BlackmagicPlayer”));
        // 将媒体纹理与播放器关联
        MediaTexture->SetMediaPlayer(MediaPlayer);
        // 打开媒体源，开始接收 Blackmagic 采集卡的输入
        if (MediaPlayer->OpenSource(InputSource))
        {
            UE_LOG(LogTemp, Log, TEXT(“Blackmagic media source opened successfully.”));
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MediaIOCore` | 提供媒体输入输出的核心框架和基础类（如 `FMediaIOConfiguration`） |
| `MediaAssets` | 提供 `UMediaTexture`, `UMediaPlayer` 等媒体资产相关功能 |
| `MediaUtils` | 提供媒体工具函数 |
| `BlackmagicSDK` | Blackmagic 提供的官方 SDK 库（外部依赖） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `fe681f84` | MediaIO: Fix Blackmagic auto-detect misinterpreting interlaced signals as progressive. | 修复黑魔法采集卡自动检测时误将隔行信号识别为逐行信号的问题。 |
| 2026-05-26 | `36c08694` | Media IO - Populate Media Configuration when using auto for Blackmagic and Aja cards | 为黑魔法和 AJA 采集卡的“自动”模式填充正确的媒体配置。 |
| 2026-05-23 | `42746f7a` | Media IO: Added additional engine analytics information to various media players and capture and pro | 为各类媒体播放器、采集和输出模块添加了额外的引擎分析信息。 |
| 2026-05-12 | `b7bb4354` | Media IO - Fix bob deinterlacer field samples sharing source-frame timestamp | 修复 Bob 反交错处理器中，场样本错误地共享源帧时间戳的问题。 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the … | 将多个虚拟制片资产迁移到不同的资产分类中，并将其移至新位置。 |

### 维护评价
该插件创建于 2018 年，历史较长。但根据最近的提交记录，**它在 2026 年 5 月仍有频繁的功能更新和错误修复**，特别是关于自动配置、隔行信号处理和时间码同步等关键功能。这表明 Epic Games 仍在积极维护此插件，以支持其在虚拟制片和广播等专业领域的需求。由于它默认未启用，且与特定硬件绑定，推荐在确定需要使用 Blackmagic 采集卡时再启用。整体来看，这是一个功能成熟且仍在活跃维护的专业级插件。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/BlackmagicMedia)
- [Blackmagic Design SDK 官方文档](https://www.blackmagicdesign.com/developer)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/BlackmagicMedia/Tests) (如果存在)