# Media Foundation Media Player

> Implements a media player using the Microsoft Media Foundation framework. Requires Xbox One or Windows 7 and higher.

| 属性 | 值 |
|---|---|
| 中文名 | 媒体基础播放器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MfMedia` (RuntimeNoCommandlet), `MfMediaEditor` (Editor), `MfMediaFactory` (Editor, RuntimeNoCommandlet) |
| 实验性 | 否 |
| 创建时间 | 2017-01-25 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MfMedia) | |

## 用途
该插件是 Unreal Engine Media Framework 的一个后端实现，它利用 Windows 原生的 Microsoft Media Foundation (MF) 框架来播放媒体文件。其存在意义是为在 Windows 和 Xbox One 平台上运行的项目提供一个可靠的、利用操作系统底层能力的媒体播放方案，可以处理多种视频和音频格式。

## 使用场景
- 你的项目主要面向 **Windows 平台**（Windows 7 及以上）或 **Xbox One**，需要播放游戏内的过场动画、广告、UI 背景视频或音频。
- 你希望利用操作系统自带的解码器，而不是引擎内置的 FFmpeg 解码器，以确保格式兼容性或性能。
- 你需要一个不同于默认“WmfMedia”播放器的备选方案。

## 蓝图用法
此插件本身不直接暴露大量额外的蓝图节点。媒体播放的核心逻辑仍通过 `UMediaPlayer` 和 `UMediaSoundComponent` 等标准媒体框架类进行。此插件的作用是为这些标准类提供一个名为 “MfMedia” 的底层播放器实现。

### 核心节点
你通常在创建或获取 `UMediaPlayer` 实例后，将其 “Player Name” 设置为 `"MfMedia"` 来指定使用此插件进行播放。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Media Player` | 创建一个新的媒体播放器对象，可在Details面板中指定使用“MfMedia” | `UMediaPlayer` |
| `Open Source` / `Open URL` | 使用已配置好的播放器打开一个媒体源 | `UMediaPlayer` |

### 使用示例（蓝图描述）
1.  在内容浏览器中右键创建一个 **Media Player** 资源。
2.  在该资源的 Details 面板中，找到 “Player” 部分，将 “Player Name” 从默认值改为 `MfMedia`。
3.  在蓝图中，使用 `Create Media Player` 节点，选择你刚刚创建的资产作为模板。
4.  将 `Open Source` 或 `Open URL` 节点连接到创建出的播放器引用，传入你要播放的媒体文件路径或流媒体地址。
5.  将播放器连接到 `Media Sound Component` 或 `Media Texture` 以输出音频和图像。

## C++ 用法
在 C++ 中，你通常不会直接与 `MfMedia` 模块交互，而是继续使用标准的 `MediaPlayer` API。插件的注册是自动完成的。

### 头文件引入
使用媒体框架的标准头文件即可。
```cpp
#include "MediaPlayer.h"
#include "MediaSource.h"
```

### 基本用法
创建并配置一个使用 `MfMedia` 播放器的 `MediaPlayer` 实例。
```cpp
// 创建一个新的 UMediaPlayer 资产或获取一个现有的
UMediaPlayer* MyMediaPlayer = NewObject<UMediaPlayer>();
// 设置播放器名称为 “MfMedia” 以使用本插件
MyMediaPlayer->SetPlayerName(FName(“MfMedia”));

// 创建一个媒体源
UMediaSource* MediaSource = ... // 例如 FFileMediaSource 或 FStreamMediaSource

// 打开媒体源
MyMediaPlayer->OpenSource(MediaSource);

// 绑定事件
MyMediaPlayer->OnMediaOpened.AddDynamic(this, &AMyActor::OnMediaOpened);
```

### 进阶用法
可以查询可用的媒体播放器插件列表，并确保 MfMedia 已注册。
```cpp
// 获取所有可用的媒体播放器工厂
TArray<IMediaPlayerFactory*> PlayerFactories = IMediaModule::Get().GetPlayerFactories();
for (IMediaPlayerFactory* Factory : PlayerFactories)
{
    if (Factory->GetName() == FName(“MfMedia”))
    {
        UE_LOG(LogTemp, Log, TEXT(“MfMedia player plugin is available.”));
        break;
    }
}
```
*（代码逻辑基于通用 Media Framework API 推断）*

## Demo 示例
一个最小化的 Actor 示例，用于播放本地文件。
```cpp
// MyMediaActor.h
#pragma once
#include "GameFramework/Actor.h"
#include “MyMediaActor.generated.h”

class UMediaPlayer;
class UMediaSource;
class UMediaSoundComponent;

UCLASS()
class AMyMediaActor : public AActor
{
    GENERATED_BODY()
public:
    AMyMediaActor();
    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, Category = “Media”)
    UMediaPlayer* MediaPlayer;

    UPROPERTY(EditAnywhere, Category = “Media”)
    UMediaSource* MediaSource;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = “Media”)
    UMediaSoundComponent* MediaSoundComponent;

private:
    UFUNCTION()
    void OnMediaOpened(FString OpenedUrl);
};

// MyMediaActor.cpp
#include “MyMediaActor.h”
#include “MediaPlayer.h”
#include “MediaSource.h”
#include “MediaSoundComponent.h”
#include “FileMediaSource.h”

AMyMediaActor::AMyMediaActor()
{
    PrimaryActorTick.bCanEverTick = false;
    MediaSoundComponent = CreateDefaultSubobject<UMediaSoundComponent>(TEXT(“MediaSound”));
    RootComponent = MediaSoundComponent;
}

void AMyMediaActor::BeginPlay()
{
    Super::BeginPlay();

    if (!MediaPlayer || !MediaSource)
    {
        UE_LOG(LogTemp, Warning, TEXT(“MediaPlayer or MediaSource not set.”));
        return;
    }

    // 确保使用 MfMedia 播放器
    MediaPlayer->SetPlayerName(FName(“MfMedia”));
    // 将播放器与声音组件关联
    MediaSoundComponent->SetMediaPlayer(MediaPlayer);
    // 绑定回调
    MediaPlayer->OnMediaOpened.AddDynamic(this, &AMyMediaActor::OnMediaOpened);
    // 打开源
    MediaPlayer->OpenSource(MediaSource);
}

void AMyMediaActor::OnMediaOpened(FString OpenedUrl)
{
    UE_LOG(LogTemp, Log, TEXT(“Media opened: %s, Playing...”), *OpenedUrl);
    MediaPlayer->Play();
}
```

## 模块依赖
该插件的模块依赖于 Unreal Engine 的媒体框架核心模块。

| 模块 | 用途 |
|---|---|
| `MediaUtils` | 提供媒体框架的通用工具类和接口。 |
| `MediaAssets` | 提供 `MediaPlayer`, `MediaSource` 等资产类型。 |
| `Media` | 媒体框架的核心运行时接口。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移到新的 UE_LOGF 格式，属于代码现代化重构。 |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 全局代码修正，将空析构函数改为“= default”，属于代码质量改进。 |
| 2025-09-25 | `94af5100` | Replaced PREPROCESSOR_TO_STRING with UE_STRINGIZE. | 替换宏定义，使用更标准的 UE_STRINGIZE，属于维护性更新。 |
| 2025-06-20 | `642aa84c` | Fix PVS warnings | 修复静态代码分析警告，属于编译和代码质量维护。 |
| 2025-02-18 | `0ecd6846` | Media: reworking the timestamp associated sequence index | 媒体相关改动：重新设计了时间戳关联的序列索引逻辑。 |

### 维护评价
- **创建时间**：插件创建于 2017 年初（UE 4.15 时代），是一个历史悠久的底层平台模块。
- **近期活动**：截至 2026 年仍有更新，但主要是代码现代化、宏替换和警告修复等维护性提交，没有看到新功能增加或重大问题修复。
- **活跃度**：处于**维护中**状态。作为引擎核心媒体后端之一，它仍然被支持以保证 Windows 平台的兼容性，但活跃开发重心可能已转移到其他更通用的播放器实现（如 FFmpeg）。
- **已知问题**：早期提交记录（2017年）曾提及在 Windows 10 上存在问题并被临时禁用，后续应已修复。作为默认禁用的插件，其稳定性依赖于特定平台和 Media Foundation 运行时。
- **推荐**：**推荐用于需要稳定 Windows/Xbox One 平台媒体播放的生产项目**，特别是当默认播放器遇到兼容性问题时。由于它默认禁用，启用前请确认目标平台支持。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MfMedia)
- [官方文档](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MfMedia/Tests) *(路径推断)*