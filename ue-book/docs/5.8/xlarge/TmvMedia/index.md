# Tiled Mipmap Video Player

> Framework for tiled-mipmap video (TMV) playback, includes transcoding tools. Implemented using Advanced Professional Video (APV) codec.

| 属性 | 值 |
|---|---|
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ApvMedia` (Runtime), `TmvMedia` (Runtime), `TmvMediaEditor` (Runtime), `TmvMediaMp4Utils` (Runtime), `TmvMediaShaders` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-18 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/TmvMedia) | |

## 用途

TmvMedia 插件为 Unreal Engine 引入了 **Tiled Mipmap Video (TMV)** 格式的播放与处理能力。TMV 是一种专为高性能视频播放优化的格式，其核心思想是将视频帧分割成多个“平铺”（Tile），并为每个平铺生成多级渐远纹理（Mipmap）。这种结构特别适用于需要超高清分辨率（如虚拟制片中的 LED 墙）或需要动态调整视频质量的场景，因为它允许引擎只加载和解码当前视口可见的平铺及其合适的 Mipmap 层级，从而大幅降低内存占用和带宽需求。

该插件基于 **Advanced Professional Video (APV)** 编解码器实现，并提供了一套完整的工具链，包括播放器、编辑器集成以及将标准视频（如 MP4）转码为 TMV 格式的工具。

## 使用场景

- **虚拟制片 (Virtual Production)**：在 LED 墙上播放超高分辨率（如 8K+）的背景视频时，使用 TMV 格式可以确保流畅播放，避免因一次性加载整个视频帧而导致的内存溢出或卡顿。
- **实时合成与预览**：在编辑器或运行时，需要动态加载和播放大型视频素材进行合成或预览时，TMV 的平铺和 Mipmap 特性可以按需加载，提升交互性能。
- **离线转码工具链**：使用插件提供的转码工具，将项目中的标准视频资产预先转换为 TMV 格式，以优化最终产品的运行时性能。

## 蓝图用法

蓝图功能主要分布在 `TmvMedia` 和 `TmvMediaEditor` 模块中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open Source` | 打开一个 TMV 文件或 URL 进行播放。 | `UTmvMediaPlayer` |
| `Close` | 关闭当前播放的媒体。 | `UTmvMediaPlayer` |
| `Play` | 开始或恢复播放。 | `UTmvMediaPlayer` |
| `Pause` | 暂停播放。 | `UTmvMediaPlayer` |
| `Seek` | 跳转到指定时间点。 | `UTmvMediaPlayer` |
| `Get Duration` | 获取视频总时长。 | `UTmvMediaPlayer` |
| `Get Time` | 获取当前播放时间。 | `UTmvMediaPlayer` |
| `Is Playing` | 检查是否正在播放。 | `UTmvMediaPlayer` |
| `Transcode To Tmv` | 将源视频文件转码为 TMV 格式。 | `UTmvMediaTranscodeLibrary` |

### 使用示例（蓝图描述）

1.  **创建播放器**：在蓝图中创建一个 `UTmvMediaPlayer` 对象。
2.  **打开媒体**：调用 `Open Source` 节点，传入 TMV 文件的路径。
3.  **控制播放**：连接 `Play`、`Pause`、`Seek` 等节点到用户输入事件（如按钮点击）。
4.  **获取状态**：使用 `Get Time`、`Is Playing` 等节点更新 UI 或驱动其他逻辑。
5.  **转码**：在编辑器工具或构建脚本中，使用 `Transcode To Tmv` 节点批量转换视频资产。

## C++ 用法

### 头文件引入

```cpp
#include "TmvMediaPlayer.h"
#include "TmvMediaTranscodeLibrary.h"
```

### 基本用法

以下示例展示了如何在 C++ 中创建和控制一个 TMV 播放器。

```cpp
// 创建播放器实例
UTmvMediaPlayer* TmvPlayer = NewObject<UTmvMediaPlayer>();

// 打开媒体源
FString TmvFilePath = FPaths::ProjectContentDir() / TEXT("Videos/MyScene.tmv");
TmvPlayer->OpenSource(TmvFilePath);

// 绑定媒体事件
TmvPlayer->OnMediaOpened.AddDynamic(this, &AMyActor::HandleMediaOpened);
TmvPlayer->OnPlaybackEnd.AddDynamic(this, &AMyActor::HandlePlaybackEnd);

// 开始播放
TmvPlayer->Play();

// 在 Tick 或其他地方获取当前时间
float CurrentTime = TmvPlayer->GetTime().GetSeconds();
```

### 进阶用法

结合转码库，在编辑器工具或命令行工具中实现视频资产的自动化处理。

```cpp
#include "TmvMediaTranscodeLibrary.h"

// 设置转码参数
FTmvTranscodeSettings Settings;
Settings.SourcePath = TEXT("/Game/Videos/Raw/Background.mp4");
Settings.DestinationPath = TEXT("/Game/Videos/TMV/Background.tmv");
Settings.TileSize = FIntPoint(256, 256); // 设置平铺大小
Settings.MaxMipLevels = 5; // 设置最大 Mipmap 层级

// 执行转码（异步）
UTmvMediaTranscodeLibrary::TranscodeToTmv(Settings, FOnTmvTranscodeComplete::CreateLambda(
    [](bool bSuccess, const FString& OutputPath)
    {
        if (bSuccess)
        {
            UE_LOG(LogTemp, Log, TEXT("TMV 转码成功: %s"), *OutputPath);
        }
    }
));
```

## Demo 示例

一个最小的 Actor，用于在关卡中播放 TMV 视频。

**TmvDemoActor.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "TmvMediaPlayer.h"
#include "TmvDemoActor.generated.h"

UCLASS()
class ATmvDemoActor : public AActor
{
    GENERATED_BODY()

public:
    ATmvDemoActor();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UPROPERTY(EditAnywhere, Category = "TMV")
    FString TmvFilePath;

private:
    UPROPERTY()
    UTmvMediaPlayer* TmvPlayer;

    UFUNCTION()
    void HandleMediaOpened();
};
```

**TmvDemoActor.cpp**
```cpp
#include "TmvDemoActor.h"

ATmvDemoActor::ATmvDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void ATmvDemoActor::BeginPlay()
{
    Super::BeginPlay();

    TmvPlayer = NewObject<UTmvMediaPlayer>(this);
    TmvPlayer->OnMediaOpened.AddDynamic(this, &ATmvDemoActor::HandleMediaOpened);

    if (!TmvFilePath.IsEmpty())
    {
        TmvPlayer->OpenSource(TmvFilePath);
    }
}

void ATmvDemoActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (TmvPlayer)
    {
        TmvPlayer->Close();
    }
    Super::EndPlay(EndPlayReason);
}

void ATmvDemoActor::HandleMediaOpened()
{
    UE_LOG(LogTemp, Log, TEXT("TMV 媒体已打开，开始播放。"));
    TmvPlayer->Play();
}
```

## 模块依赖

要使用此插件，你的模块需要依赖以下特殊模块：

| 模块 | 用途 |
|---|---|
| `UEOpenAPV` | APV 编解码器的核心运行时库，由 `ApvMedia` 模块依赖。 |
| `TmvMedia` | TMV 播放器核心功能。 |
| `TmvMediaMp4Utils` | 用于 MP4 解析和转码的工具函数。 |
| `TmvMediaShaders` | 用于渲染 TMV 平铺和 Mipmap 的 GPU 着色器。 |

**注意**：`TmvMediaEditor` 模块仅用于编辑器工具，不应在运行时模块中依赖。

## 维护状态

### 近期更新

- 2026-04-24 `c7065a2f` [Tmv Media] Transcoding Commandlet
- 2026-04-23 `efcad028` HDR: Fix HDR normalization factor across media causing incorrect brightness levels going from/to the
- 2026-04-22 `323ab3ea` [TmvMediaUtils] Addressing Ux feedback for the MRG node
- 2026-04-20 `4677c750` [TmvMedia] Adding start timecode support to tmv container
- 2026-04-18 `1a28370d` [TmvMediaUtils] New version of the Movie Render Graph Tmv Encoder node.

### 维护评价

- **创建时间**：非常新，属于实验性功能。
- **维护状态**：作为 Epic Games 官方推出的、面向虚拟制片前沿技术的插件，预计在相关项目（如《曼达洛人》等使用 StageCraft 技术的项目）中会得到积极维护和更新。
- **已知限制**：作为实验性插件，API 可能不稳定，功能可能不完整。需要特定的硬件和软件环境（如支持 APV 的编解码器）。
- **推荐使用**：**仅推荐**给正在开发虚拟制片项目或需要处理超高清、高性能视频播放的专业团队。对于常规游戏开发，标准的媒体框架通常已足够。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/TmvMedia)
- [官方文档]() (暂无)
- [测试用例]() (路径待确认，可能位于 `Engine/Tests/TmvMedia/`)