# Android Camera Player

> Implements camera preview using the Android Camera library.

| 属性 | 值 |
|---|---|
| 中文名 | 安卓相机播放器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AndroidCamera` (RuntimeNoCommandlet), `AndroidCameraEditor` (Editor), `AndroidCameraFactory` (Editor), `AndroidCameraFactory` (RuntimeNoCommandlet) |
| 实验性 | 否 |
| 创建时间 | 2025-06-26 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AndroidCamera) | |

## 用途

该插件通过 Android 原生 Camera API（`android.hardware.Camera` 或 `Camera2`）在 Unreal Engine 中实现摄像头画面实时预览。它是一个自定义的 **Media Player**，能够将设备相机捕捉的帧数据转换为引擎可消费的 `IMediaTextureSample`，并支持音频/视频轨道选择、截图、分辨率变化检测等。

解决的核心问题：在 Android 平台上以标准媒体框架（Media Framework）的方式获取并渲染相机画面，便于继承现有的媒体播放器接口、Actor 组件和蓝图系统。适用于需要实时相机输入的任何 UE 应用（AR、滤镜、扫描、远程协作等）。

## 使用场景

- **实时相机预览**：在 UI 或 3D 场景中直接显示后置/前置相机画面。
- **AR 辅助功能**：结合 SceneCapture2D 或后期处理实现增强现实效果。
- **拍照与录像**：利用 `TakePicture()` 截取当前帧保存为图片。
- **自定义媒体播放器**：作为 `UMediaPlayer` 的源，与其他媒体框架集成（如 `MediaTexture`、`MediaSoundComponent`）。

## 蓝图用法

Android Camera Player 没有直接暴露独立的蓝图书点；它通过标准的 **Media Player** 节点被使用。配置流程如下：

1. 创建 `UMediaPlayer` 或使用蓝图中 **Media Player** 资产。
2. 将 `Media Player` 的源选择为「Android Camera Player」（可通过 `MediaSource` 资产或代码指定 URL）。
3. 连接 `MediaTexture` 和 `MediaSoundComponent` 渲染画面与音频。

### 媒体源 URL

相机 URL 格式建议为 `"androidcam://"`（具体协议由 `IMediaOptions` 实现）。在蓝图中，通常通过创建 `UMediaSource` 的子类或直接调用 `Open Source` 节点。

### 可用操作（继承自 MediaPlayer）

| 节点（BlueprintCallable） | 说明 | 所属类 |
|---|---|---|
| `Open Source` | 打开相机媒体源 | `UMediaPlayer` |
| `Play` | 开始播放（实时流） | `UMediaPlayer` |
| `Close` | 关闭相机并释放资源 | `UMediaPlayer` |
| `Pause` | 暂停相机画面更新 | `UMediaPlayer` |
| `OnMediaOpened` | 相机成功打开时的委托 | `UMediaPlayer` |
| `OnMediaPlayerMediaClosed` | 相机关闭时的委托 | `UMediaPlayer` |

**注意**：相机控制（如切换摄像头、截图）未直接暴露为蓝图节点，需通过 C++ 扩展。

## C++ 用法

### 头文件引入

```cpp
#include "IAndroidCameraModule.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"
```

### 基本用法

通过模块接口创建相机播放器并打开相机：

```cpp
// 获取 AndroidCamera 模块
IAndroidCameraModule* CameraModule = FModuleManager::LoadModulePtr<IAndroidCameraModule>("AndroidCamera");
if (CameraModule)
{
    // 创建相机播放器
    TSharedPtr<IMediaPlayer, ESPMode::ThreadSafe> CameraPlayer = CameraModule->CreatePlayer(EventSink);

    // 设置媒体选项（可指定摄像头索引、分辨率等）
    FMediaPlayerOptions Options;
    Options.CameraDeviceIndex = 0; // 0 = 后置, 1 = 前置

    // 打开相机（URL 为 "androidcam://"）
    if (CameraPlayer->Open(TEXT("androidcam://"), &Options))
    {
        // 成功打开，此时可以从播放器获取轨道信息并选择视频轨道
        CameraPlayer->GetTracks().SelectTrack(EMediaTrackType::Video, 0);
    }
}
```

**来源**：`Private/Player/AndroidCameraPlayer.cpp`（未完整提供，但由接口推断）

### 纹理采样与渲染

渲染到材质需将播放器与 `UMediaTexture` 关联：

```cpp
UMediaTexture* MediaTexture = CreateDefaultSubobject<UMediaTexture>(TEXT("CameraTexture"));
MediaTexture->SetMediaPlayer(MediaPlayer);
// 在每帧 Tick 中，播放器自动填充采样
```

### 截取当前帧

通过 `FJavaAndroidCameraPlayer::TakePicture` 保存图片到指定路径：

```cpp
// 内部调用，需转换为 UE 路径
const FString OutputFilePath = FPaths::ProjectSavedDir() / TEXT("CameraPhoto.jpg");
// 假设已有 FJavaAndroidCameraPlayer 实例
bool bSuccess = JavaCameraPlayer->TakePicture(OutputFilePath);
```

### 进阶用法

**多轨道选择**：获取视频格式列表并切换分辨率：

```cpp
TArray<FJavaAndroidCameraPlayer::FVideoTrack> VideoTracks;
if (JavaCameraPlayer->GetVideoTracks(VideoTracks))
{
    // 选择第一个轨道
    JavaCameraPlayer->SelectTrack(VideoTracks[0].Index);
}
```

**事件驱动**：监控 `MediaOpened` 和 `MediaClosed` 委托：

```cpp
MediaPlayer->OnMediaOpened.AddLambda([](const FString& OpenedUrl)
{
    UE_LOG(LogTemp, Log, TEXT("Camera opened: %s"), *OpenedUrl);
});
```

## Demo 示例

以下是一个简化的 `AActor` 子类，在场景中显示相机预览。

### CameraActor.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"
#include "CameraActor.generated.h"

UCLASS()
class ACameraActor : public AActor
{
    GENERATED_BODY()

public:
    ACameraActor();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UPROPERTY(VisibleAnywhere, Category = "Media")
    UMediaPlayer* MediaPlayer;

    UPROPERTY(VisibleAnywhere, Category = "Media")
    UMediaTexture* MediaTexture;
};
```

### CameraActor.cpp

```cpp
#include "CameraActor.h"
#include "IAndroidCameraModule.h"
#include "Modules/ModuleManager.h"

ACameraActor::ACameraActor()
{
    PrimaryActorTick.bCanEverTick = false;

    MediaPlayer = CreateDefaultSubobject<UMediaPlayer>(TEXT("MediaPlayer"));
    MediaTexture = CreateDefaultSubobject<UMediaTexture>(TEXT("MediaTexture"));
    MediaTexture->SetMediaPlayer(MediaPlayer);
}

void ACameraActor::BeginPlay()
{
    Super::BeginPlay();

    // 创建原生播放器并注入到 UMediaPlayer
    IAndroidCameraModule* CameraModule = FModuleManager::LoadModulePtr<IAndroidCameraModule>("AndroidCamera");
    if (CameraModule && MediaPlayer)
    {
        TSharedPtr<IMediaPlayer, ESPMode::ThreadSafe> NativePlayer = CameraModule->CreatePlayer(MediaPlayer->GetEventSink());
        MediaPlayer->SetNativeMediaPlayer(NativePlayer);
        MediaPlayer->OpenSource(TEXT("androidcam://"));
    }
}

void ACameraActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (MediaPlayer)
    {
        MediaPlayer->Close();
    }
    Super::EndPlay(EndPlayReason);
}
```

然后在材质中引用 `MediaTexture`，并将材质应用到平面网格上即可看到相机画面。

## 模块依赖

该插件主要依赖 Android 平台模块和媒体框架，未引入特殊第三方库。

| 模块 | 用途 |
|---|---|
| `Media` | 核心媒体接口（IMediaPlayer、IMediaSamples 等） |
| `MediaUtils` | 媒体工具函数与采样池 |
| `RHI` | 渲染硬件接口，用于创建纹理 |
| `AndroidRuntime` | Android 平台支持（JNI、Java 类包装） |
| `ApplicationCore` | 应用生命周期管理 |

**注意**：使用此插件需要在项目 `.build.cs` 中添加 `"AndroidCamera"` 到 `PublicDependencyModuleNames`，并确保平台为 Android。

## 维护状态

### 近期更新

- 2025-09-11 `6312e16d` — Fix crash from pending JNI exception in non-Shipping builds（修复非 Shipping 构建中 JNI 异常导致的崩溃）
- 2025-08-29 `32884de4` — Changing more uses of RHICreateTexture to RHICmdList.CreateTexture.（RHI 纹理创建方式迁移）
- 2025-08-12 `f5866ce3` — Fixed the timing of firing MediaOpened in AndroidCameraPlayer.（修复 MediaOpened 事件触发时机）
- 2025-08-08 `d7c83195` — Fixed a Java exception when closing the CameraDevice during its initialization.（修复相机初始化过程中关闭导致的 Java 异常）
- 2025-06-26 `9294da93` — Remove two imports not used.（移除无用导入）

### 维护评价

该插件于 2025 年创建，属于全新插件。最近几个月内持续有功能性修复和适配更新（RHI 接口变更、异常处理、事件时序），表明开发团队在积极维护。目前在 UE 5.7 分支上表现稳定。由于仅支持 Android 平台，无需跨平台兼容性问题。推荐在需要实时相机预览的 Android 项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AndroidCamera)
- [官方文档（论坛讨论）](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AndroidCamera/Source/AndroidCamera/Private/Player)（位于插件内部）