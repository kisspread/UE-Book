# Android Camera Player

> Implements camera preview using the Android Camera library.

| 属性 | 值 |
|---|---|
| 中文名 | 安卓相机 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AndroidCamera` (Runtime), `AndroidCameraEditor` (Editor), `AndroidCameraFactory` (Editor, Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-08-30 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AndroidCamera) | |

## 用途

此插件为 Android 平台提供了一个基于原生 Android Camera 库的媒体播放器实现。它允许开发者在 UE 应用中访问 Android 设备的物理摄像头（前置或后置），获取实时视频流，并将其作为媒体纹理（Media Texture）输出，供引擎的 Media Framework 系统使用。其主要目的是为了在 Android 上实现摄像头预览、AR 应用或需要实时视频输入的场景。

## 使用场景

-   你在开发一个需要 Android 设备摄像头实时画面的 AR 应用。
-   你需要为 Android 平台实现一个视频通话功能，需要采集并处理摄像头画面。
-   你正在做一个需要扫描二维码或物体的 Android 应用，需要访问摄像头原始数据。
-   你希望将 Android 摄像头画面实时渲染到游戏场景中的某个表面上。

## 蓝图用法

此插件主要通过 Media Framework 的标准接口暴露功能，核心交互对象是 `MediaPlayer` 和 `MediaTexture`。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open Source` | 打开一个媒体源，对于此插件，源需要设置为 Android 摄像头设备 | `UMediaPlayer` |
| `Play` | 开始播放（获取摄像头画面） | `UMediaPlayer` |
| `Stop` | 停止播放（停止获取画面） | `UMediaPlayer` |
| `Get Video Texture` | 获取用于显示摄像头画面的 `MediaTexture` 对象 | `UMediaPlayer` |
| `Set Video Texture` | 将 `MediaTexture` 应用到材质或 UI 上 | `UMediaTexture` |

### 使用示例（蓝图描述）

1.  创建一个 `MediaPlayer` 资产。
2.  创建一个 `MediaTexture` 资产。
3.  在蓝图中，将 `MediaPlayer` 的输出连接到 `MediaTexture`。
4.  在事件图表中，调用 `MediaPlayer` 的 `Open Source` 节点，并传入一个代表 Android 摄像头的 `MediaSource`（通常由插件内部工厂创建，可在内容浏览器中找到或通过设置创建）。
5.  调用 `Play` 节点开始预览。
6.  将 `MediaTexture` 赋值给一个动态材质实例的纹理参数，或用于 `Image` 控件，即可在屏幕上显示摄像头画面。

## C++ 用法

### 头文件引入

```cpp
#include "MediaPlayer.h"
#include "MediaTexture.h"
#include "MediaSource.h"
// AndroidCamera 插件主要提供工厂和平台实现，直接使用 Media Framework 公共 API
```

### 基本用法

通过 Media Framework 的公共 API 访问摄像头。摄像头设备在 Android 上被抽象为媒体源。

```cpp
// 1. 获取或创建媒体播放器和纹理
UMediaPlayer* MediaPlayer = NewObject<UMediaPlayer>();
UMediaTexture* MediaTexture = NewObject<UMediaTexture>();
MediaTexture->SetMediaPlayer(MediaPlayer);

// 2. 打开 Android 摄像头媒体源
// “android_camera”是插件注册的媒体源协议，后面的参数可用于指定前后摄像头，如 “?device=1” 代表前置。
// 具体参数格式取决于插件实现。
FString CameraSourceURL = TEXT("android_camera://?device=0"); // device=0 通常为后置摄像头
if (MediaPlayer->OpenUrl(CameraSourceURL))
{
    UE_LOG(LogTemp, Log, TEXT("Opened Android camera source: %s"), *CameraSourceURL);
}

// 3. 播放
MediaPlayer->Play();
```

### 进阶用法

处理播放器状态事件，并动态切换摄像头。

```cpp
// 绑定播放结束或错误事件
MediaPlayer->OnMediaEvent().AddLambda([this](EMediaEvent Event)
{
    if (Event == EMediaEvent::MediaClosed || Event == EMediaEvent::MediaOpenFailed)
    {
        UE_LOG(LogTemp, Warning, TEXT("Media player encountered an event: %d"), (int32)Event);
    }
});

// 切换到前置摄像头
FString FrontCameraURL = TEXT("android_camera://?device=1");
MediaPlayer->OpenUrl(FrontCameraURL);
MediaPlayer->Play();
```

## Demo 示例

以下是一个在 Actor 中集成 Android 摄像头的最小 C++ 示例。

**AndroidCameraDemo.h**
```cpp
// AndroidCameraDemo.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "AndroidCameraDemo.generated.h"

class UMediaPlayer;
class UMediaTexture;
class UStaticMeshComponent;

UCLASS()
class AAndroidCameraDemo : public AActor
{
    GENERATED_BODY()

public:
    AAndroidCameraDemo();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    UPROPERTY(VisibleAnywhere)
    UStaticMeshComponent* PreviewPlane;

    UPROPERTY()
    UMediaPlayer* CameraPlayer;

    UPROPERTY()
    UMediaTexture* CameraTexture;

    // 材质实例，用于将 CameraTexture 赋予平面
    UPROPERTY()
    UMaterialInstanceDynamic* PreviewMaterial;
};
```

**AndroidCameraDemo.cpp**
```cpp
// AndroidCameraDemo.cpp
#include "AndroidCameraDemo.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"
#include "Engine/StaticMeshActor.h"
#include "Materials/MaterialInstanceDynamic.h"

AAndroidCameraDemo::AAndroidCameraDemo()
{
    PrimaryActorTick.bCanEverTick = false;

    // 创建一个静态网格作为预览平面
    PreviewPlane = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PreviewPlane"));
    RootComponent = PreviewPlane;
    // 假设你有一个单位平面网格
    // PreviewPlane->SetStaticMesh(ConstructorHelpers::FObjectFinder<UStaticMesh>(TEXT("/Engine/BasicShapes/Plane.Plane")).Object);

    // 创建媒体播放器和纹理
    CameraPlayer = CreateDefaultSubobject<UMediaPlayer>(TEXT("CameraPlayer"));
    CameraTexture = CreateDefaultSubobject<UMediaTexture>(TEXT("CameraTexture"));
    CameraTexture->SetMediaPlayer(CameraPlayer);
}

void AAndroidCameraDemo::BeginPlay()
{
    Super::BeginPlay();

    // 动态创建材质实例并应用媒体纹理
    if (PreviewPlane->GetMaterial(0))
    {
        PreviewMaterial = UMaterialInstanceDynamic::Create(PreviewPlane->GetMaterial(0), this);
        PreviewPlane->SetMaterial(0, PreviewMaterial);
        // 将媒体纹理设置到材质的某个参数（假设参数名为 “CameraTex”）
        PreviewMaterial->SetTextureParameterValue(FName("CameraTex"), CameraTexture);
    }

    // 打开 Android 摄像头
    FString CameraURL = TEXT("android_camera://?device=0");
    if (CameraPlayer->OpenUrl(CameraURL))
    {
        CameraPlayer->Play();
        UE_LOG(LogTemp, Log, TEXT("Android camera playback started."));
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open Android camera source."));
    }
}

void AAndroidCameraDemo::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (CameraPlayer)
    {
        CameraPlayer->Close();
    }
    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

从 `Build.cs` 文件分析得出，使用此插件时，你的项目模块可能需要依赖以下内容：

| 模块 | 用途 |
|---|---|
| `MediaUtils` | 提供媒体播放器、纹理等基础框架类（`AndroidCamera` 模块依赖） |
| `MediaAssets` | 提供 `UMediaPlayer`, `UMediaTexture` 等资产类（`AndroidCameraFactory` 模块依赖） |
| `Setting` | 用于读取编辑器或项目设置（`AndroidCameraEditor` 模块依赖） |

*注意：这些依赖关系是插件内部使用的。作为插件使用者，你通常只需在项目的 `.Build.cs` 文件中添加对 `MediaAssets` 模块的依赖即可使用 `UMediaPlayer` 等类。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧版 UE_LOG 宏迁移到新版 UE_LOGF 宏。 |
| 2026-02-06 | `d2c0a7b4` | Fixed printf. | 修复了 printf 格式化问题。 |
| 2026-02-05 | `d5be7e14` | Fixed printfs. | 修复了多个 printf 格式化问题。 |
| 2025-09-19 | `d942b16a` | Fixed some Bughawk JNI issues | 修复了部分 Bughawk JNI 接口问题。 |
| 2025-09-11 | `764d5c18` | Fix crash from pending JNI exception in non-Shipping builds | 修复了非发行版构建中因待处理JNI异常导致的崩溃。 |

### 维护评价

**维护状态：不活跃**

-   **创建时间**：插件创建于 2017 年，历史悠久。
-   **最近更新**：近几次提交（2025-2026年）均为底层代码清理（日志宏迁移）和 JNI 稳定性修复，**没有新功能或重大改进**。这表明插件已进入维护模式，主要目标是保持编译通过和基本稳定，而非功能演进。
-   **平台限制**：插件仅适用于 Android 平台，使用范围有限。
-   **已知问题**：基于早期提交历史，该插件在 Media Framework 重构期间曾存在各种播放问题（如闪烁、崩溃、音视频同步），这些问题可能已随引擎升级得到修复，但也可能遗留一些平台特定的边界情况。
-   **推荐度**：**有条件推荐**。如果你的项目 **必须** 且 **仅** 在 Android 上使用设备摄像头，并且你使用的是较新的 UE 版本（5.x），那么此插件仍然是官方提供、相对可靠的方案。但请注意，它并非现代、功能丰富的解决方案（如缺乏高级图像处理管线），且长期无功能性更新。对于跨平台或需要更复杂摄像功能的项目，可能需要考虑第三方插件或自行实现。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AndroidCamera)
-   [官方文档](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview)（来自.uplugin，内容可能较旧）