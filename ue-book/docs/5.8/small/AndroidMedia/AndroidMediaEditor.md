# Android Media Player

> Implements a media player using the Android Media library.

| 属性 | 值 |
|---|---|
| 中文名 | 安卓媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AndroidMedia` (RuntimeNoCommandlet), `AndroidMediaEditor` (Editor), `AndroidMediaFactory` (Editor, RuntimeNoCommandlet) |
| 实验性 | 否 |
| 创建时间 | 2014-11-17 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AndroidMedia) | |

## 用途

`AndroidMedia` 插件为 Unreal Engine 的 Media Framework 提供了 Android 平台的原生实现。它使用 Android 系统内置的 `MediaPlayer` 或 `MediaCodec` 等底层 API 来解码和播放视频与音频。这确保了在海量 Android 设备上拥有最佳的兼容性和性能，是 UE 在 Android 平台播放媒体文件（如本地视频、网络流媒体）的核心依赖。

## 使用场景

- 你的移动游戏需要在 Android 设备上播放过场动画或剧情视频。
- 你需要在 Android 设备的 UI 上显示来自摄像头或网络串流的实时画面。
- 你正在开发一个跨平台（PC/Android）的应用，并希望在 Android 端使用系统原生能力进行媒体播放，以获得更好的能效和兼容性。

## 蓝图用法

插件通过 Media Framework 的公共蓝图接口工作。`AndroidMediaEditor` 和 `AndroidMediaFactory` 模块主要负责编辑器内的资产导入和工厂创建，运行时媒体控制主要通过 `UMediaPlayer` 等通用类完成。

### 核心节点

该插件主要作为后端实现，其功能通过标准的 Media Framework 蓝图节点暴露。以下节点在 Android 平台上会由本插件驱动：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open Source` / `Open File` / `Open URL` | 打开一个媒体源，启动播放准备流程。 | `UMediaPlayer` |
| `Play` | 开始播放已准备好的媒体。 | `UMediaPlayer` |
| `Pause` | 暂停当前播放。 | `UMediaPlayer` |
| `Close` | 关闭媒体源，释放资源。 | `UMediaPlayer` |
| `Seek` | 跳转到指定时间点。 | `UMediaPlayer` |
| `Is Playing` / `Is Paused` | 查询播放器当前状态。 | `UMediaPlayer` |
| `Get Duration` | 获取媒体总时长。 | `UMediaPlayer` |
| `On Media Opened` / `On Media Closed` | 媒体打开/关闭的回调事件。 | `UMediaPlayer` |

### 使用示例（蓝图描述）

1.  在你的蓝图中，创建一个 `Media Player` 资产的引用变量。
2.  使用 `Create Media Player` 节点创建一个 `UMediaPlayer` 对象，并将其赋值给该变量。
3.  使用 `Open Source` 节点，并指定一个 `File Media Source` 或 `Stream Media Source` 资产。连接到媒体播放器对象。
4.  在 `On Media Opened` 事件中，调用 `Play` 节点开始播放。
5.  可以添加按钮来触发 `Pause`、`Seek` 等节点控制播放。

## C++ 用法

在 C++ 中，你可以直接使用 Media Framework 的 API。`AndroidMedia` 模块在底层自动接管，无需在应用层代码中显式引用 `AndroidMedia` 模块。

### 头文件引入

```cpp
#include "MediaPlayer.h"
#include "FileMediaSource.h"
#include "MediaSource.h"
```

### 基本用法

以下代码演示了如何创建媒体播放器并打开一个文件进行播放。在 Android 平台运行时，将由 `AndroidMedia` 模块处理实际解码。

```cpp
// 在你的 Actor 或 Widget 类中
UPROPERTY()
UMediaPlayer* MyMediaPlayer;

UPROPERTY()
UFileMediaSource* MyMediaSource;

void AMyActor::BeginPlay()
{
    Super::BeginPlay();

    // 创建媒体播放器实例
    MyMediaPlayer = NewObject<UMediaPlayer>(this);
    // 创建媒体源资产（通常从蓝图资产加载）
    MyMediaSource = LoadObject<UFileMediaSource>(nullptr, TEXT("/Game/Movies/MyVideo"));

    if (MyMediaPlayer && MyMediaSource)
    {
        // 绑定媒体打开完成委托
        MyMediaPlayer->OnMediaOpened.AddDynamic(this, &AMyActor::OnMediaPlayerOpened);
        // 打开媒体源
        MyMediaPlayer->OpenSource(MyMediaSource);
    }
}

void AMyActor::OnMediaPlayerOpened(FString OpenedUrl)
{
    // 媒体已准备好，开始播放
    if (MyMediaPlayer && MyMediaPlayer->IsReady())
    {
        MyMediaPlayer->Play();
    }
}

void AMyActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    // 重要：在 Actor 销毁前关闭媒体播放器
    if (MyMediaPlayer)
    {
        MyMediaPlayer->Close();
    }
    Super::EndPlay(EndPlayReason);
}
```

### 进阶用法

处理媒体播放事件和控制：

```cpp
// 在类的头文件中声明
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnMediaSeekCompleted, bool, bSuccess);

UPROPERTY(BlueprintAssignable, Category = "Media")
FOnMediaSeekCompleted OnMediaSeekCompleted;

void AMyActor::SetupMediaPlayerEvents()
{
    if (MyMediaPlayer)
    {
        MyMediaPlayer->OnMediaSeekCompleted.AddDynamic(this, &AMyActor::HandleSeekCompleted);
        MyMediaPlayer->OnPlaybackSuspended.AddDynamic(this, &AMyActor::HandlePlaybackSuspended);
    }
}

void AMyActor::HandleSeekCompleted(bool bSuccess)
{
    UE_LOG(LogTemp, Log, TEXT("Seek operation %s."), bSuccess ? TEXT("succeeded") : TEXT("failed"));
}

void AMyActor::HandlePlaybackSuspended()
{
    // 可能是缓冲中或系统中断
    UE_LOG(LogTemp, Warning, TEXT("Playback suspended."));
}

// 在某个函数中执行跳转
void AMyActor::SeekToMiddle()
{
    if (MyMediaPlayer && MyMediaPlayer->IsReady())
    {
        const FTimespan Duration = MyMediaPlayer->GetDuration();
        const FTimespan Middle = Duration / 2;
        MyMediaPlayer->Seek(Middle);
    }
}
```

## Demo 示例

一个完整的 C++ Actor 示例，用于在 Android 上播放视频文件。

### MyVideoPlayerActor.h

```cpp
// MyVideoPlayerActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyVideoPlayerActor.generated.h"

class UMediaPlayer;
class UFileMediaSource;
class UMediaTexture;
class UStaticMeshComponent;

UCLASS()
class AMyVideoPlayerActor : public AActor
{
    GENERATED_BODY()

public:
    AMyVideoPlayerActor();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UFUNCTION()
    void OnMediaOpened(FString OpenedUrl);

    UFUNCTION()
    void OnMediaFailedToOpen(FString FailedUrl);

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    UStaticMeshComponent* ScreenMesh;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Media")
    UMediaPlayer* VideoPlayer;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Media")
    UMediaTexture* VideoTexture;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Media")
    UFileMediaSource* VideoSource;
};
```

### MyVideoPlayerActor.cpp

```cpp
// MyVideoPlayerActor.cpp
#include "MyVideoPlayerActor.h"
#include "MediaPlayer.h"
#include "FileMediaSource.h"
#include "MediaTexture.h"
#include "Components/StaticMeshComponent.h"
#include "UObject/ConstructorHelpers.h"

AMyVideoPlayerActor::AMyVideoPlayerActor()
{
    PrimaryActorTick.bCanEverTick = false;

    ScreenMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("ScreenMesh"));
    RootComponent = ScreenMesh;

    // 创建媒体播放器和纹理
    VideoPlayer = CreateDefaultSubobject<UMediaPlayer>(TEXT("VideoPlayer"));
    VideoTexture = CreateDefaultSubobject<UMediaTexture>(TEXT("VideoTexture"));

    // 关联媒体纹理到播放器
    VideoTexture->SetMediaPlayer(VideoPlayer);

    // 加载默认媒体源（假设在 Content/Movies 下）
    static ConstructorHelpers::FObjectFinder<UFileMediaSource> SourceFinder(TEXT("/Game/Movies/DefaultVideo"));
    if (SourceFinder.Succeeded())
    {
        VideoSource = SourceFinder.Object;
    }
}

void AMyVideoPlayerActor::BeginPlay()
{
    Super::BeginPlay();

    if (VideoPlayer && VideoSource)
    {
        // 绑定委托
        VideoPlayer->OnMediaOpened.AddDynamic(this, &AMyVideoPlayerActor::OnMediaOpened);
        VideoPlayer->OnMediaOpenFailed.AddDynamic(this, &AMyVideoPlayerActor::OnMediaFailedToOpen);

        // 打开媒体源，开始准备
        VideoPlayer->OpenSource(VideoSource);
    }
}

void AMyVideoPlayerActor::OnMediaOpened(FString OpenedUrl)
{
    UE_LOG(LogTemp, Log, TEXT("Media opened: %s"), *OpenedUrl);

    // 媒体准备就绪，开始播放
    if (VideoPlayer->IsReady())
    {
        VideoPlayer->Play();
        // 你可以将 VideoTexture 应用到 ScreenMesh 的材质上
        // 例如通过动态材质实例设置纹理参数
    }
}

void AMyVideoPlayerActor::OnMediaFailedToOpen(FString FailedUrl)
{
    UE_LOG(LogTemp, Error, TEXT("Failed to open media: %s"), *FailedUrl);
}

void AMyVideoPlayerActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    // 清理：关闭播放器，释放资源
    if (VideoPlayer)
    {
        VideoPlayer->Close();
    }
    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

从插件的模块类型和用途推断，使用本插件的项目模块通常需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `MediaAssets` | 提供 `UMediaPlayer`， `UMediaSource` 等核心媒体资产类。 |
| `MediaUtils` | 提供媒体相关的工具函数和数据结构。 |
| `RenderCore` | `AndroidMedia` 运行时模块可能依赖此模块进行纹理和渲染相关的操作。 |

（注：`AndroidMediaEditor` 和 `AndroidMediaFactory` 作为编辑器模块，会依赖 `UnrealEd` 等，但这些是编辑器插件常见依赖，无需特别列出。）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移旧日志宏到新的日志格式宏。 |
| 2026-02-05 | `d5be7e14` | Fixed printfs. | 修复了遗留的 printf 语句。 |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 代码现代化，将空的析构函数体改为 `= default`。 |
| 2025-08-29 | `32884de4` | Changing more uses of RHICreateTexture to RHICmdList.CreateTexture. | 适配 RHI API 更改，使用命令列表创建纹理。 |
| 2025-06-18 | `79ad0f74` | Updated CameraPlayer14 to Camera2 API. | 将过时的 Camera1 API 调用更新为 Camera2 API。 |

### 维护评价

`AndroidMedia` 插件是一个历史悠久、功能稳定的基础平台插件。其创建时间（2014年）表明它是 UE 早期 Android 媒体支持的核心。近年来的提交（2025-2026年）**主要是底层维护性工作**，如日志系统迁移、编译警告修复、适配新的引擎 API (`RHICmdList`, `Camera2`)，**没有新的功能增强**。这表明插件功能已非常成熟和稳定，当前处于**低频率维护**状态，主要工作是确保其在新版 UE 引擎和新 Android 系统/API 上能继续正常编译和运行。对于需要在 Android 上播放媒体的项目，该插件仍然是**官方推荐且必不可少**的选择，其稳定性和兼容性值得信赖。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AndroidMedia)
- [官方文档](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview) (较早期的论坛文档链接，可参考)