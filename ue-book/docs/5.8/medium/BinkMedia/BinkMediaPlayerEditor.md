# Bink Media

> Implements a media player using Bink.

| 属性 | 值 |
|---|---|
| 中文名 | Bink媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `BinkMediaPlayer` (Runtime), `BinkMediaPlayerEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2021-06-08 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/BinkMedia) | |

## 用途

BinkMedia 插件提供了一个基于 **Bink** 视频解码库的媒体播放器，用于在虚幻引擎中播放 Bink 2 (`.bk2`) 格式的视频文件。Bink 是一种高性能、低内存占用的视频压缩格式，广泛应用于游戏行业用于过场动画、背景视频等。此插件的核心价值在于让开发者能够在 UE5 项目中高效、无缝地集成和使用 Bink 视频内容。

## 使用场景

- **游戏过场动画**：你需要在你的 RPG 或动作游戏中播放高质量的过场动画，同时对内存和 CPU 占用有严格要求。
- **动态 UI 背景**：你想要在游戏菜单或 UI 界面中使用循环播放的视频作为背景。
- **游戏内事件触发**：当玩家完成某个任务或进入特定区域时，触发一段全屏视频。
- **跨平台部署**：你的游戏需要支持包括主机在内的多个平台，Bink 的广泛兼容性是一个优势。

## 蓝图用法

从 `BinkMediaPlayer` 运行时模块和 `BinkMediaPlayerEditor` 的源码分析，蓝图可用的 API 主要通过 `UBinkMediaPlayer` 类暴露。以下是核心的功能分组。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open Source Latent` | 异步打开指定的 Bink 文件源。 | `UBinkMediaPlayer` |
| `Play` | 开始播放媒体。 | `UBinkMediaPlayer` |
| `Pause` | 暂停媒体播放。 | `UBinkMediaPlayer` |
| `Rewind` | 将媒体倒回至开始。 | `UBinkMediaPlayer` |
| `Seek` | 将媒体跳转到指定时间点。 | `UBinkMediaPlayer` |
| `Set Rate` | 设置播放速率（0.0 暂停，1.0 正常，2.0 快进）。 | `UBinkMediaPlayer` |
| `Get Time` | 获取当前播放时间。 | `UBinkMediaPlayer` |
| `Get Duration` | 获取媒体总时长。 | `UBinkMediaPlayer` |
| `Get Rate` | 获取当前播放速率。 | `UBinkMediaPlayer` |
| `Is Playing` | 检查媒体是否正在播放。 | `UBinkMediaPlayer` |
| `Is Paused` | 检查媒体是否已暂停。 | `UBinkMediaPlayer` |
| `Supports Seeking` | 检查媒体是否支持跳转。 | `UBinkMediaPlayer` |
| `Supports Scrubbing` | 检查媒体是否支持拖动播放（Scrubbing）。 | `UBinkMediaPlayer` |
| `Can Play` | 检查是否可以执行播放操作。 | `UBinkMediaPlayer` |
| `Can Pause` | 检查是否可以执行暂停操作。 | `UBinkMediaPlayer` |

### 使用示例（蓝图描述）

1.  **创建并播放视频**：
    *   在资产浏览器中右键 -> **Media** -> **Bink Media Player** 创建一个 `UBinkMediaPlayer` 资产。
    *   在内容浏览器中创建一个 **Media Texture** 资产。
    *   打开 `UBinkMediaPlayer` 资产，在 `Source Url` 属性中指定 `.bk2` 文件路径。
    *   在材质中，使用 `Media Texture` 采样器节点，并将创建的 Media Texture 资产赋给它。
    *   在蓝图中，获取对 `UBinkMediaPlayer` 资产的引用，调用 `Open Source Latent` 节点打开视频，然后在完成（`On Success`）执行引脚后调用 `Play` 节点。

2.  **控制播放**：
    *   获取 `UBinkMediaPlayer` 引用。
    *   使用 `Play`、`Pause`、`Rewind` 节点进行基本控制。
    *   使用 `Set Rate` 节点配合浮点数实现快放、慢放和倒放。
    *   使用 `Seek` 节点配合 `FFTimespan` 输入实现精确跳转。

## C++ 用法

以下示例展示了在 C++ 中如何操作 Bink 媒体播放器。

### 头文件引入

```cpp
#include "MediaPlayer.h"
#include "MediaTexture.h"
// 假设 BinkMediaPlayer 是基于 UMediaPlayer 的子类或使用相同接口
#include "BinkMediaPlayer.h"
```

### 基本用法

基于媒体播放器通用接口和 Bink 工具类的功能推断。

```cpp
// 在某个 Actor 或组件中
UPROPERTY()
UBinkMediaPlayer* MyBinkPlayer;

UPROPERTY()
UMediaTexture* MyMediaTexture;

// 初始化（通常在 BeginPlay 或构造时）
void AMyActor::SetupBinkPlayer()
{
    // 1. 加载或创建媒体播放器资产
    MyBinkPlayer = LoadObject<UBinkMediaPlayer>(nullptr, TEXT("/Game/Movies/MyBinkPlayer.BinkPlayer"));

    if (MyBinkPlayer)
    {
        // 2. 打开媒体源
        const FString MediaPath = FPaths::ProjectContentDir() + TEXT("Movies/MyVideo.bk2");
        MyBinkPlayer->OpenUrl(MediaPath);

        // 3. 播放
        MyBinkPlayer->Play();

        // 4. (可选) 将媒体纹理链接到材质等
        if (MyMediaTexture)
        {
            MyMediaTexture->SetMediaPlayer(MyBinkPlayer);
        }
    }
}
```

### 进阶用法

结合事件和查询进行更精细的控制。

```cpp
// 监听播放状态变化
void AMyActor::BindToMediaPlayerEvents()
{
    if (MyBinkPlayer)
    {
        // 当媒体打开完成时
        MyBinkPlayer->OnMediaOpened().AddUObject(this, &AMyActor::HandleMediaOpened);
        // 当媒体播放结束时
        MyBinkPlayer->OnMediaEnd().AddUObject(this, &AMyActor::HandleMediaEnd);
        // 当发生错误时
        MyBinkPlayer->OnMediaOpenFailed().AddUObject(this, &AMyActor::HandleMediaOpenFailed);
    }
}

void AMyActor::HandleMediaOpened(const FString& OpenedUrl)
{
    UE_LOG(LogTemp, Log, TEXT("Bink media opened: %s"), *OpenedUrl);
    // 可以在这里安全地查询时长等信息
    FTimespan Duration = MyBinkPlayer->GetDuration();
}

void AMyActor::HandleMediaEnd()
{
    UE_LOG(LogTemp, Log, TEXT("Bink media playback finished."));
    // 可以选择循环播放或执行其他逻辑
    MyBinkPlayer->Rewind();
    MyBinkPlayer->Play();
}

// 在 Tick 中查询当前时间（例如更新 UI 进度条）
void AMyActor::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);

    if (MyBinkPlayer && MyBinkPlayer->IsPlaying())
    {
        FTimespan CurrentTime = MyBinkPlayer->GetTime();
        FTimespan TotalDuration = MyBinkPlayer->GetDuration();
        float Progress = (TotalDuration.GetTotalSeconds() > 0) ?
            CurrentTime.GetTotalSeconds() / TotalDuration.GetTotalSeconds() : 0.0f;
        // UpdateProgressBar(Progress);
    }
}
```

## Demo 示例

一个最小的 Actor，用于在场景中播放 Bink 视频。

**BinkDemoActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "BinkDemoActor.generated.h"

class UBinkMediaPlayer;
class UMediaTexture;
class UMaterialInstanceDynamic;
class UStaticMeshComponent;

UCLASS()
class ABinkDemoActor : public AActor
{
    GENERATED_BODY()

public:
    ABinkDemoActor();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    UStaticMeshComponent* DisplayMesh;

    UPROPERTY(EditAnywhere, Category = "Bink")
    FString BinkFileUrl;

    UPROPERTY(Transient)
    UBinkMediaPlayer* BinkPlayer;

    UPROPERTY(Transient)
    UMediaTexture* MediaTexture;

    UPROPERTY(Transient)
    UMaterialInstanceDynamic* DynamicMaterial;

    UFUNCTION()
    void OnMediaOpened(const FString& OpenedUrl);
};
```

**BinkDemoActor.cpp**
```cpp
#include "BinkDemoActor.h"
#include "MediaPlayer.h" // 假设 UBinkMediaPlayer 接口类似
#include "MediaTexture.h"
#include "Components/StaticMeshComponent.h"
#include "Materials/MaterialInstanceDynamic.h"

ABinkDemoActor::ABinkDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;

    DisplayMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("DisplayMesh"));
    RootComponent = DisplayMesh;
}

void ABinkDemoActor::BeginPlay()
{
    Super::BeginPlay();

    // 创建媒体纹理
    MediaTexture = NewObject<UMediaTexture>(this, UMediaTexture::StaticClass(), TEXT("BinkMediaTexture"));

    // 创建或加载媒体播放器
    BinkPlayer = NewObject<UBinkMediaPlayer>(this, UBinkMediaPlayer::StaticClass(), TEXT("BinkPlayer"));
    if (BinkPlayer)
    {
        BinkPlayer->OnMediaOpened().AddDynamic(this, &ABinkDemoActor::OnMediaOpened);
        MediaTexture->SetMediaPlayer(BinkPlayer);

        // 应用到网格材质
        if (DisplayMesh->GetMaterial(0))
        {
            DynamicMaterial = DisplayMesh->CreateAndSetMaterialInstanceDynamic(0);
            DynamicMaterial->SetTextureParameterValue(TEXT("BaseTexture"), MediaTexture);
        }

        // 打开视频
        if (!BinkFileUrl.IsEmpty())
        {
            BinkPlayer->OpenUrl(BinkFileUrl);
        }
    }
}

void ABinkDemoActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (BinkPlayer)
    {
        BinkPlayer->Close();
    }
    Super::EndPlay(EndPlayReason);
}

void ABinkDemoActor::OnMediaOpened(const FString& OpenedUrl)
{
    UE_LOG(LogTemp, Log, TEXT("BinkDemoActor: Media opened - %s"), *OpenedUrl);
    BinkPlayer->Play();
}
```

## 模块依赖

此插件无特殊依赖（仅标准 Core/Engine/Slate 等）。其运行时模块 `BinkMediaPlayer` 依赖了 `MoviePlayer`、`RenderCore`、`RHI`、`Renderer`、`DesktopWidgets` 等引擎媒体和渲染核心模块，编辑器模块 `BinkMediaPlayerEditor` 依赖了 `MetalRHI`（用于 Apple 平台的特定编辑器预览支持）。使用者无需额外指定这些依赖，它们已包含在插件模块中。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 更新日志宏至新版 `UE_LOGF`。 |
| 2026-04-01 | `2f26bbfa` | Bink: Fixed BinkTestBed | 修复了 Bink 测试平台。 |
| 2026-04-01 | `8a338576` | Bink: Fixed foward def mismatch, just include PixelFormat.h | 修复了前向声明不匹配，改为包含头文件。 |
| 2026-04-01 | `9f45180e` | Bink: update for new BinkHL interface | 更新以适配新的 BinkHL 接口。 |
| 2026-02-19 | `3e97632c` | Refactored FSceneViewport / FViewport to remove the ViewportRHI field | 重构了视口类，移除了 ViewportRHI 字段。 |

### 维护评价

- **维护状态**: **活跃维护**
- **创建时间**: 2021年6月，插件相对成熟。
- **近期活动**: 在 **2026年4月** 仍有连续的功能更新和接口适配（如适配新 BinkHL 接口），表明 Epic 和 Bink 技术团队仍在积极维护和更新此插件。
- **已知限制**: 默认未启用 (`EnabledByDefault: false`)，需要在项目设置中手动启用。`IsBetaVersion: false` 表明其已达到生产就绪状态。
- **推荐使用**: **推荐**。对于需要播放 Bink 格式视频的项目，这是一个官方支持且维护良好的解决方案。其活跃的更新历史保证了与最新 UE 版本和底层 Bink 技术的兼容性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/BinkMedia)
- [官方文档]() （.uplugin 未提供）
- [测试用例]() （从提供的代码片段中未发现集成在插件目录内的测试用例）