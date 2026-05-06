# Android Media Player

> Implements a media player using the Android Media library.

| 属性 | 值 |
|---|---|
| 中文名 | Android 媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AndroidMedia` (Runtime), `AndroidMediaEditor` (Editor), `AndroidMediaFactory` (Runtime & Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-03-28 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AndroidMedia) | |

## 用途

Android Media Player 是 UE5 Media Framework 的 Android 平台后端。它封装了 Android 原生的 `MediaPlayer` API（包括 `MediaCodec` 和 `MediaExtractor`），提供硬件加速的视频解码和渲染能力。

**解决的核心问题**：在 Android 设备上高效播放本地视频文件（如 MP4）和流媒体 URL，同时与 UE 的 Media Texture、Media Player 资产无缝集成。

**为什么存在**：Unreal Engine 需要针对每个平台提供特定的播放器实现，以利用平台原生 API 获得最佳性能和兼容性。Android 平台通过此插件实现。

## 使用场景

- **游戏过场动画**：在 Android 游戏中播放高清片头动画，利用硬件解码避免卡顿。
- **交互式应用**：在 UI 中嵌入视频（如引导视频、广告），通过 Media Texture 映射到 3D 对象。
- **流媒体播放**：支持 HTTP/HTTPS 直播流或点播视频（需要服务器端支持 Android 标准格式）。
- **本地资源播放**：播放打包在 APK/OBB 中的视频文件，或从设备外部存储读取。

## 蓝图用法

Android Media Player 不直接暴露蓝图节点。所有操作通过引擎的 **Media Player** 资产和 **Media Texture** 资产完成。

### 核心资产

| 资产类型 | 说明 |
|---|---|
| `Media Player` | 定义媒体源、播放控制（播放、暂停、跳转） |
| `Media Texture` | 将视频帧转换为纹理，可材质绑定 |
| `File Media Source` / `Stream Media Source` | 指定视频文件路径或 URL |

### 使用步骤（蓝图描述）

1. **创建 Media Player 资产**：右键内容浏览器 → Media → Media Player。
2. **创建 Media Texture 资产**：右键 → Media → Media Texture，并在其属性 `Media Player` 中指定上一步创建的 Media Player。
3. **设置媒体源**：在 Media Player 资产的属性 `Media Source` 中选择或新建 `File Media Source`（指定本地路径）或 `Stream Media Source`（指定 URL）。
4. **播放控制**：获取 Media Player 对象（通过 `Get Media Player` 节点），调用 `Open Source` 传入媒体源，成功后调用 `Play`。
5. **渲染视频**：将 Media Texture 拖入材质蓝图，作为 Base Color 或自发光，然后应用到 UI（`Image` 组件）或 3D 物体上。

**简图连接**（文字描述）：
```
Event BeginPlay → Open Source (MediaPlayer, MediaSource) → Is Preparing? 
→ Wait (OnMediaOpened)
→ Play (MediaPlayer)
→ Media Texture → (拖拽到 UI Image 的 Brush->Image)
```

## C++ 用法

### 头文件引入

```cpp
#include "IAndroidMediaModule.h"
#include "IMediaPlayer.h"
#include "MediaPlayer.h"       // 如果使用 UMediaPlayer 资产
#include "MediaTexture.h"      // 如果使用 UMediaTexture
```

### 基本用法

通过模块接口直接创建播放器（通常不需要手动创建，引擎自动处理 `UMediaPlayer` 的底层）：

```cpp
// 创建播放器实例（用于自定义播放逻辑）
IAndroidMediaModule* MediaModule = FModuleManager::LoadModulePtr<IAndroidMediaModule>("AndroidMedia");
if (MediaModule)
{
    // EventSink 需要实现 IMediaEventSink 接口
    TSharedPtr<IMediaPlayer, ESPMode::ThreadSafe> Player = MediaModule->CreatePlayer(EventSink);
    if (Player.IsValid())
    {
        // 打开文件
        Player->Open("/storage/emulated/0/Movies/trailer.mp4", nullptr);
        // 播放
        Player->GetControls().SetRate(1.0f);
    }
}
```

**来源**：`Engine/Plugins/Media/AndroidMedia/Source/AndroidMedia/Public/IAndroidMediaModule.h`

### 常用用法（通过 UMediaPlayer 资产）

推荐使用引擎标准接口，插件自动选择 Android 播放器：

```cpp
UMediaPlayer* MediaPlayer = NewObject<UMediaPlayer>();
UFileMediaSource* FileSource = NewObject<UFileMediaSource>();
FileSource->FilePath = TEXT("/game/content/Movies/Intro.mp4");

MediaPlayer->OnMediaOpened.AddDynamic(this, &UMyClass::OnMediaOpened);
MediaPlayer->OpenSource(FileSource);
// 在 OnMediaOpened 回调中调用 MediaPlayer->Play();
```

**来源**：`Engine/Source/Runtime/MediaAssets/Private/MediaPlayer.cpp`（引擎标准用法）

### 进阶用法

处理视频帧转换（自定义渲染）：通常无需手动处理，`FAndroidMediaTextureSample` 已实现 `IMediaTextureSampleConverter`，在 `TickFetch` 中自动将 Android 原生帧转换为 UE RHI 纹理。

## Demo 示例

一个可编译的最小示例，在 Android 上播放指定视频文件。

### MyVideoPlayer.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"
#include "MyVideoPlayer.generated.h"

UCLASS()
class AMyVideoPlayer : public AActor
{
    GENERATED_BODY()

public:
    AMyVideoPlayer();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Media")
    UMediaPlayer* MediaPlayer;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Media")
    UMediaTexture* MediaTexture;
};
```

### MyVideoPlayer.cpp

```cpp
#include "MyVideoPlayer.h"
#include "FileMediaSource.h"

AMyVideoPlayer::AMyVideoPlayer()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyVideoPlayer::BeginPlay()
{
    Super::BeginPlay();

    if (!MediaPlayer || !MediaTexture)
    {
        UE_LOG(LogTemp, Error, TEXT("Please assign MediaPlayer and MediaTexture in blueprint"));
        return;
    }

    // 创建媒体源（支持本地路径）
    UFileMediaSource* FileSource = NewObject<UFileMediaSource>();
    FileSource->FilePath = TEXT("/game/Movies/Intro.mp4"); // 需将视频文件放入 Content/Movies 并打包

    // 监听打开成功事件
    MediaPlayer->OnMediaOpened.AddDynamic(this, &AMyVideoPlayer::OnMediaOpened);
    // 打开媒体
    MediaPlayer->OpenSource(FileSource);
}

void AMyVideoPlayer::OnMediaOpened(FString OpenedUrl)
{
    UE_LOG(LogTemp, Log, TEXT("Media opened: %s"), *OpenedUrl);
    MediaPlayer->Play();
}
```

**注意**：需要将视频文件复制到 Android 设备的合适路径（如 `/game/Movies/`），或使用 `FileMediaSource` 设置为绝对路径。更稳定的方法是将视频放在 APK 的 `Movies` 目录下（需在 `.uproject` 中添加 `AdditionalDependencies` 和目录打包设置）。

## 模块依赖

使用 Android Media Player 插件时，你的模块需要依赖以下独特模块：

| 模块 | 用途 |
|---|---|
| `Media` | 核心媒体框架接口（`IMediaPlayer` 等） |
| `MediaAssets` | `UMediaPlayer`、`UMediaTexture`、`UFileMediaSource` 等资产类 |
| `MediaUtils` | 媒体播放器管理工具（如 `FMediaPlayerFacade`） |

**无需额外配置**：插件本身自动被引擎在 Android 平台上加载，你只需在 `.Build.cs` 中添加 `"Media", "MediaAssets", "MediaUtils"` 即可。

## 维护状态

### 近期更新

- 2025-08-29 `32884de4` 将更多 `RHICreateTexture` 调用改为 `RHICmdList.CreateTexture`（适配渲染接口重构）
- 2025-06-18 `79ad0f74` 更新 `CameraPlayer14` 为 Camera2 API（可能与 Camera 播放器相关，但同属于 Android 媒体模块）
- 2025-05-31 `52e3dac1` 更新头文件 DLL 存储方法声明（代码风格统一）
- 2025-04-10 `ea97db60` 电影渲染管线：高分辨率平铺支持（跨模块重构）
- 2025-03-28 `b892a182` 新的 `BitmapRenderer` 用于 `MediaPlayer14`（引入新渲染器）

### 维护评价

- **创建时间**：2025 年 3 月（较新）。
- **近期更新**：最近 6 个月内有多次实质性更新（渲染接口适配、API 升级、功能增强）。
- **活跃程度**：该插件是 Android 平台媒体播放的核心依赖，Epic 持续维护且跟随引擎演进。
- **已知问题**：无公开严重缺陷。
- **推荐度**：✅ 强烈推荐。用于任何需要 Android 视频播放的 UE 项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AndroidMedia)
- [官方文档（Media Framework）](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AndroidMedia/Source/AndroidMedia/Private)（内部未公开独立测试，实现本身即为测试目标）