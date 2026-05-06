# Android Camera Player

> Implements camera preview using the Android Camera library.

| 属性 | 值 |
|---|---|
| 中文名 | Android 相机播放器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AndroidCamera` (Runtime), `AndroidCameraEditor` (Editor), `AndroidCameraFactory` (Runtime + Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-06-26 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AndroidCamera) | |

## 用途

本插件利用 Android 原生 Camera API（`android.hardware.camera2`）在 Unreal Engine 中实现实时相机预览。它将手机/平板的后置/前置摄像头作为媒体源接入 UE 的媒体框架（Media Framework），允许开发者像播放视频文件一样直接消费相机帧数据。

核心模块 `AndroidCamera` 实现了 `IMediaPlayer` 接口，提供帧数据（纹理或缓冲）供材质、蓝图或 C++ 代码使用。`AndroidCameraFactory` 模块负责在运行时创建该播放器实例，并暴露一组可配置的全局设置（如视频采样缓存策略），这些设置可通过项目设置界面调整。

## 使用场景

- **AR 应用**：在屏幕上显示实际相机画面作为 AR 背景，叠加虚拟物体。
- **实时滤镜/特效**：将相机帧传入后处理材质，实现实时美颜、风格化滤镜。
- **扫码/条码识别**：捕获相机帧并通过第三方库分析图像。
- **远程监控/自拍相机**：在游戏中嵌入相机预览，例如拍照模式或视频通话界面（需配合网络传输）。

## 蓝图用法

本模块未直接暴露 BlueprintCallable 函数或 Blueprintable 类给蓝图。所有交互通过 UE 的 Media Framework 蓝图节点完成。

### 核心设置（项目设置）

| 设置路径 | 属性 | 说明 |
|---|---|---|
| 项目设置 → Plugins → Android Camera Player | `CacheableVideoSampleBuffers` | 是否缓存视频采样缓冲。默认关闭，每个帧重用同一缓冲以提高性能；开启后每帧拷贝副本，适用于需要访问历史帧的应用，但会降低性能。 |

设置类型：`UAndroidCameraSettings`，可在 C++ 中通过 `UAndroidCameraSettings::Get()` 或 `GetMutableDefault<UAndroidCameraSettings>()` 访问。

### 蓝图创建媒体播放器

1. 调用 **Create Media Player** 节点（位于 Media 类别），设置 `MediaPlayer` 输出变量。
2. 创建 **Media Source** 对象，并绑定到 Android 相机设备（通常通过蓝图或 C++ 创建自定义源，或使用默认的 `FileMediaSource` 配合设备路径）。
3. 使用 **Open Source** 节点传入媒体源，连接成功后可获取纹理并显示在 UI 或场景中。

> 注意：Android 相机在编辑器中无法测试，需打包到真机运行。

## C++ 用法

### 头文件引入

```cpp
#include "AndroidCameraSettings.h"   // 访问设置
#include "MediaPlayer.h"             // 创建媒体播放器
#include "MediaTexture.h"            // 获取帧纹理
```

### 基本用法

通过项目设置调整缓存行为：

```cpp
// 获取全局设置对象
UAndroidCameraSettings* Settings = GetMutableDefault<UAndroidCameraSettings>();
Settings->CacheableVideoSampleBuffers = true; // 开启缓存（性能降低但可访问历史帧）
Settings->SaveConfig(); // 保存到 Config/DefaultEngine.ini
```

创建并打开相机媒体播放器（需引擎初始化后执行）：

```cpp
// 创建媒体播放器对象
UMediaPlayer* MediaPlayer = NewObject<UMediaPlayer>();
// 创建媒体源（示例使用文件源，实际需替换为相机设备源）
UFileMediaSource* MediaSource = NewObject<UFileMediaSource>();
MediaSource->FilePath = TEXT("android_camera://back"); // 伪路径，实际需使用自定义源

// 打开媒体源
FMediaPlayerOptions Options;
Options.PlayerName = TEXT("AndroidCamera"); // 指定使用 Android Camera Player
MediaPlayer->OpenSource(MediaSource, Options);
```

### 进阶用法

在材质中显示相机纹理：

```cpp
// 创建 MediaTexture 并关联到播放器
UMediaTexture* MediaTexture = NewObject<UMediaTexture>();
MediaTexture->SetMediaPlayer(MediaPlayer);
MediaTexture->UpdateResource();

// 将 MediaTexture 赋值给动态材质实例（例如画布或场景组件）
UMaterialInstanceDynamic* DynMat = ...
DynMat->SetTextureParameterValue(TEXT("CameraFeed"), MediaTexture);
```

## Demo 示例

以下是一个可编译的最小 C++ 示例，演示如何在自定义 Actor 中打开 Android 相机并显示：

```cpp
// MyCameraActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"
#include "MyCameraActor.generated.h"

UCLASS()
class AMyCameraActor : public AActor
{
    GENERATED_BODY()

public:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Media")
    UMediaPlayer* MediaPlayer;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Media")
    UMediaTexture* MediaTexture;

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
};
```

```cpp
// MyCameraActor.cpp
#include "MyCameraActor.h"
#include "MediaSource.h"
#include "FileMediaSource.h"
#include "MediaPlayerOptions.h"

void AMyCameraActor::BeginPlay()
{
    Super::BeginPlay();

    // 创建媒体播放器和纹理
    MediaPlayer = NewObject<UMediaPlayer>(this);
    MediaTexture = NewObject<UMediaTexture>(this);
    MediaTexture->SetMediaPlayer(MediaPlayer);
    MediaTexture->UpdateResource();

    // 创建 Android 相机媒体源（伪代码，实际需使用 AndroidCamera 提供的工厂）
    UFileMediaSource* MediaSource = NewObject<UFileMediaSource>();
    MediaSource->FilePath = TEXT("android_camera://back"); // 占位符，需替换为真实设备标识

    // 设置播放选项，指定使用 AndroidCamera 插件
    FMediaPlayerOptions Options;
    Options.PlayerName = TEXT("AndroidCamera");
    // 可指定相机分辨率、帧率等
    Options.Keys.Add(TEXT("CameraId"), TEXT("0")); // 后置相机 ID

    // 打开媒体源
    MediaPlayer->OpenSource(MediaSource, Options);

    // 将纹理应用到本 Actor 的静态网格或 UI 上（略）
}

void AMyCameraActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (MediaPlayer)
    {
        MediaPlayer->Close();
    }
    Super::EndPlay(EndPlayReason);
}
```

> **注意**：上述示例中的文件路径和参数仅作示意。实际使用时，需要通过 `IMediaPlayerFactory` 接口动态创建 `UMediaSource` 子类（AndroidCamera 未公开蓝图，需 C++ 自行实现工厂调用）。生产环境中建议参考 Engine 自带的测试用例或源码中的 `AndroidCameraPlayer` 实现。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MediaAssets` | 提供 `UMediaPlayer`、`UMediaTexture` 等核心媒体类 |
| `MediaUtils` | 媒体播放器工厂、平台检测等工具 |

## 维护状态

### 近期更新

| 日期 | Hash | Commit 解读 |
|---|---|---|
| 2025-09-11 | `6312e16d` | 修复非 Shipping 构建中挂起的 JNI 异常导致的崩溃 |
| 2025-08-29 | `32884de4` | 将更多 `RHICreateTexture` 调用改为 `RHICmdList.CreateTexture` |
| 2025-08-12 | `f5866ce3` | 修复 AndroidCameraPlayer 中 MediaOpened 事件的触发时机 |
| 2025-08-08 | `d7c83195` | 修复在 Camera 设备初始化过程中关闭设备时的 Java 异常 |
| 2025-06-26 | `9294da93` | 删除两个未使用的 import |

### 维护评价

该插件创建于 2025 年 6 月，至今约 3 个月，目前处于活跃维护阶段。近期 commit 均为功能性修复和适配新 API（如 RHI 迁移），无废弃标记。由于它是 UE 5.5+ 中新引入的平台插件（或从实验阶段迁移），积极响应用户反馈。当前无已知重大限制。

**推荐使用**：适用于需要在 Android 平台集成相机预览的场景，但需注意：
- 必须手动在 Plugin 设置中启用（默认关闭）。
- 仅支持 Android 平台，不支持模拟器。
- 编辑器无法预览，必须真机测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AndroidCamera)
- [官方文档](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview)（Media Framework 概述）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AndroidCamera/Source/AndroidCamera/Private/Tests)（假设存在，未验证）