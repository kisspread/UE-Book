# Media Foundation Media Player

> Implements a media player using the Microsoft Media Foundation framework. Requires Xbox One or Windows 7 and higher.

| 属性 | 值 |
|---|---|
| 中文名 | 媒体基础播放器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MfMedia` (Runtime), `MfMediaEditor` (Editor), `MfMediaFactory` (Editor + Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-01-25 |
| 年龄标签 | 🏛️ 文物（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MfMedia) | |

## 用途

MfMedia 是 UE5 媒体框架（Media Framework）的 Windows 平台后端实现之一，基于 Microsoft Media Foundation (MF) API。它解决了在 Windows 7+ 和 Xbox One 平台上播放视频、音频流媒体的需求。

**与 WmfMedia 的区别**：UE 引擎同时提供 WmfMedia（基于旧版 Windows Media Format SDK）和本插件。MfMedia 使用更现代的 Media Foundation 框架，支持更多编解码器格式，但早期版本在 Windows 10 上存在兼容性问题（从 git 历史可见曾被临时禁用）。当前版本已修复这些问题。

插件本身默认关闭（`EnabledByDefault: false`），需要用户在项目设置中手动启用。启用后，引擎会通过 Media Foundation API 解码和渲染媒体文件，支持常见的视频格式（如 H.264、WMV 等）和音频流。

## 使用场景

- 你需要在 Windows 平台的游戏中播放视频文件（过场动画、片头等）
- 你需要在 UI 中嵌入实时视频流
- 你需要在 Xbox One 上播放媒体内容
- 你希望使用比旧版 WmfMedia 更现代的媒体解码后端

## 蓝图用法

MfMedia 作为媒体播放器后端，不直接暴露蓝图节点。它通过 UE 媒体框架的统一接口工作。用户在蓝图中使用 `Media Player` 组件，引擎会自动选择合适的后端（如 MfMedia）。

### 核心交互方式

在蓝图中使用媒体播放功能时，实际操作对象是 `UMediaPlayer`，而非 MfMedia 模块本身：

| 操作 | 说明 | 所在类 |
|---|---|---|
| `Open Source` | 打开媒体源文件，MfMedia 负责底层解码 | `UMediaPlayer` |
| `Play` | 开始播放媒体 | `UMediaPlayer` |
| Media Texture | 将视频帧渲染到材质/纹理 | `UMediaTexture` |

### 使用示例（蓝图描述）

1. 在内容浏览器中创建 **Media Player** 资产，确保勾选 "Video Output" 选项
2. 创建 **Media Texture** 资产，关联到上一步创建的 Media Player
3. 在材质编辑器中使用 Media Texture 作为纹理输入
4. 在蓝图中：
   - 添加 `Media Player` 变量引用
   - 使用 `Open Source` 节点打开 `FileMediaSource` 资产（指定视频文件路径）
   - MfMedia 后端会在运行时自动接管解码和播放

## C++ 用法

### 头文件引入

```cpp
#include "IMfMediaModule.h"      // MfMedia 核心模块
#include "MediaPlayer.h"         // UE 媒体播放器统一接口
#include "FileMediaSource.h"     // 文件媒体源
```

### 基本用法

MfMedia 作为后端插件，开发者通常不直接调用其 API，而是通过 UE 的媒体框架统一接口使用。以下示例展示如何在 C++ 中使用媒体播放器（底层会自动选择 MfMedia）：

```cpp
// 创建媒体源
UFileMediaSource* MediaSource = NewObject<UFileMediaSource>();
MediaSource->SetFilePath(TEXT("C:/Videos/MyVideo.mp4"));

// 获取或创建 MediaPlayer
UMediaPlayer* MediaPlayer = NewObject<UMediaPlayer>();

// 打开媒体源（MfMedia 后端会自动处理解码）
if (MediaPlayer->OpenSource(MediaSource))
{
    UE_LOG(LogTemp, Log, TEXT("媒体文件已打开，使用 MfMedia 后端播放"));
    MediaPlayer->Play();
}

// 检查播放状态
if (MediaPlayer->IsPlaying())
{
    FTimespan Duration = MediaPlayer->GetDuration();
    FTimespan Position = MediaPlayer->GetTime();
    UE_LOG(LogTemp, Log, TEXT("播放进度: %s / %s"), 
        *Position.ToString(), *Duration.ToString());
}
```

### 进阶用法

通过自定义媒体源工厂（MfMediaFactory 模块）进行文件导入和格式处理：

```cpp
// MfMediaFactory 提供了文件媒体源的工厂类
// 可以通过 UFactory 机制导入媒体文件

// 注册自定义的媒体源工厂（MfMediaEditor 模块中已实现）
UFactory* Factory = NewObject<UMfFileMediaSourceFactory>();

// 检查工厂是否支持特定文件格式
FString FilePath = TEXT("C:/Videos/MyVideo.mp4");
bool bCanImport = Factory->FactoryCanImport(FilePath);

if (bCanImport)
{
    bool bCanceled = false;
    UObject* ImportedSource = Factory->FactoryCreateFile(
        UFileMediaSource::StaticClass(),
        GetTransientPackage(),
        FName("ImportedMedia"),
        RF_NoFlags,
        FilePath,
        nullptr,
        GWarn,
        bCanceled
    );
}
```

## Demo 示例

以下展示如何在 Actor 中集成 MfMedia 视频播放：

**MediaPlaybackActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MediaPlaybackActor.h"

class UMediaPlayer;
class UMediaTexture;
class UFileMediaSource;
class UMediaSoundComponent;

UCLASS()
class AMyMediaPlaybackActor : public AActor
{
    GENERATED_BODY()

public:
    AMyMediaPlaybackActor();

    /** 开始播放指定媒体文件 */
    UFUNCTION(BlueprintCallable, Category = "Media")
    bool PlayMedia(const FString& FilePath);

    /** 停止播放 */
    UFUNCTION(BlueprintCallable, Category = "Media")
    void StopMedia();

    /** 是否正在播放 */
    UFUNCTION(BlueprintPure, Category = "Media")
    bool IsMediaPlaying() const;

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    /** 媒体播放器 */
    UPROPERTY(Transient)
    TObjectPtr<UMediaPlayer> MediaPlayer;

    /** 媒体纹理（视频画面输出） */
    UPROPERTY(Transient)
    TObjectPtr<UMediaTexture> MediaTexture;

    /** 媒体源 */
    UPROPERTY(Transient)
    TObjectPtr<UFileMediaSource> MediaSource;

    /** 静态网格体（用于显示视频） */
    UPROPERTY(VisibleAnywhere)
    TObjectPtr<UStaticMeshComponent> ScreenMesh;

    /** 媒体音效组件 */
    UPROPERTY(VisibleAnywhere)
    TObjectPtr<UMediaSoundComponent> SoundComponent;
};
```

**MediaPlaybackActor.cpp**
```cpp
#include "MyMediaPlaybackActor.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"
#include "FileMediaSource.h"
#include "MediaSoundComponent.h"
#include "Components/StaticMeshComponent.h"

AMyMediaPlaybackActor::AMyMediaPlaybackActor()
{
    PrimaryActorTick.bCanEverTick = false;

    // 创建用于显示视频的网格体
    ScreenMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("ScreenMesh"));
    RootComponent = ScreenMesh;

    // 创建媒体音效组件
    SoundComponent = CreateDefaultSubobject<UMediaSoundComponent>(TEXT("SoundComponent"));
    SoundComponent->SetupAttachment(RootComponent);
}

void AMyMediaPlaybackActor::BeginPlay()
{
    Super::BeginPlay();

    // 创建媒体播放器实例（引擎自动选择 MfMedia 后端）
    MediaPlayer = NewObject<UMediaPlayer>(this, TEXT("MediaPlayer"));

    // 创建媒体纹理用于视频输出
    MediaTexture = NewObject<UMediaTexture>(this, TEXT("MediaTexture"));
    MediaTexture->SetMediaPlayer(MediaPlayer);
    MediaTexture->UpdateResource();

    // 创建媒体源
    MediaSource = NewObject<UFileMediaSource>(this, TEXT("MediaSource"));

    // 关联音效组件到播放器
    SoundComponent->SetMediaPlayer(MediaPlayer);
}

bool AMyMediaPlaybackActor::PlayMedia(const FString& FilePath)
{
    if (!MediaPlayer || !MediaSource)
    {
        return false;
    }

    MediaSource->SetFilePath(FilePath);

    if (MediaPlayer->OpenSource(MediaSource))
    {
        MediaPlayer->Play();
        return true;
    }

    return false;
}

void AMyMediaPlaybackActor::StopMedia()
{
    if (MediaPlayer)
    {
        MediaPlayer->Close();
    }
}

bool AMyMediaPlaybackActor::IsMediaPlaying() const
{
    return MediaPlayer && MediaPlayer->IsPlaying();
}

void AMyMediaPlaybackActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    StopMedia();
    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

从 Build.cs 分析，MfMedia 模块的核心依赖为：

| 模块 | 用途 |
|---|---|
| `MediaUtils` | UE 媒体框架通用工具（时间戳、采样格式等） |
| `MediaAssets` | 媒体资产类型（MediaPlayer、MediaTexture、MediaSource 等） |
| `MediaFactory` | 媒体播放器工厂基类 |

> 无特殊依赖（仅标准 Core/Engine/Slate 等加上 Media 框架模块）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF | 将 UE_LOG 迁移为 UE_LOGF 宏（日志宏升级） |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 析构函数风格统一为 = default |
| 2025-09-25 | `94af5100` | Replaced PREPROCESSOR_TO_STRING with UE_STRINGIZE | 宏替换：PREPROCESSOR_TO_STRING 改为 UE_STRINGIZE |
| 2025-06-20 | `642aa84c` | Fix PVS warnings | 修复 PVS 静态分析警告 |
| 2025-02-18 | `0ecd6846` | Media: reworking the timestamp associated sequence index | 媒体：重构时间戳关联的序列索引机制 |

### 维护评价

**维护中（但以被动维护为主）**

- **创建时间**：2017 年（约 8 年前），随 UE 4.15 版本引入
- **更新频率**：近期更新全部为引擎级重构/代码风格修正，而非 MfMedia 自身功能更新
- **活跃度**：插件核心功能稳定，没有新特性开发，但随着引擎版本迭代被动接收代码规范更新
- **已知限制**：
  - 仅支持 Windows 7+ 和 Xbox One，不支持 Linux/macOS/移动端
  - 默认关闭（`EnabledByDefault: false`），需手动启用
  - 曾在 Windows 10 上存在兼容性问题（已修复）
- **推荐**：如果你的目标平台是 Windows 且需要媒体播放功能，这是推荐使用的后端。对于跨平台项目，建议结合其他平台特定后端（AvfMedia 用于 Apple 平台等）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MfMedia)
- [官方文档](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview)
- 相关插件：[WmfMedia](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/WmfMedia)（旧版 Windows Media Format 后端）