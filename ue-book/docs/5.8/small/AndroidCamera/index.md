# Android Camera Player

> Implements camera preview using the Android Camera library.

| 属性 | 值 |
|---|---|
| 中文名 | 安卓相机 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AndroidCamera` (Runtime), `AndroidCameraEditor` (Editor), `AndroidCameraFactory` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2017-08-30 |
| 年龄标签 | 🏛️ 文物（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AndroidCamera) | |

## 用途

此插件为 UE5 的 Media Framework 提供了一个基于 Android 平台原生 Camera API 的媒体播放器实现。它主要解决了在 Android 设备上实时访问摄像头画面的问题，允许开发者将设备的前后摄像头作为媒体源，在引擎内进行预览和处理。这是构建 Android AR 应用、实时视频聊天、或任何需要调用设备摄像头功能的项目的基础模块。

## 使用场景

- 你在开发一款 Android AR 应用，需要实时将设备摄像头画面作为纹理显示在游戏世界中
- 你需要实现一个 Android 平台的视频聊天或直播推流功能，需要获取摄像头画面
- 你正在制作一个需要扫描二维码或进行图像识别的移动应用，并希望直接在 UE 中集成预览

## 模块列表

该插件包含三个模块，共同协作以在编辑器和运行时提供 Android 摄像头支持：

| 模块 | 类型 | 说明 |
|---|---|---|
| `AndroidCamera` | Runtime | 核心运行时模块，负责实际调用 Android Camera API 获取摄像头画面、处理媒体样本。 |
| `AndroidCameraEditor` | Editor | 编辑器支持模块，提供在编辑器中预览 Android 摄像头的能力（通过目标设备服务）。 |
| `AndroidCameraFactory` | Editor | 媒体工厂模块，负责在编辑器和运行时创建和管理 `AndroidCameraMediaPlayer` 实例。 |

## 使用说明

此插件默认不启用 (`EnabledByDefault: false`)。要使用它，你必须在项目的插件设置中手动启用，并且项目必须针对 Android 平台进行打包和部署。

### 蓝图用法

主要通过媒体工厂类进行操作。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Android Camera Media Source` | 创建一个指向 Android 设备特定摄像头的媒体源资产。 | `UAndroidCameraMediaFactory` |

**示例流程**：
1.  在蓝图中，通过 `Create Android Camera Media Source` 节点创建媒体源，选择前置或后置摄像头。
2.  将创建的媒体源资产设置给一个 `MediaPlayer` 的 `Open Source` 节点。
3.  将 `MediaPlayer` 输出的纹理连接到 `MediaTexture` 或材质中，即可在场景中显示摄像头画面。

### C++ 用法

此插件的 C++ 使用主要通过 Media Framework 的标准接口 `IMediaPlayer` 和 `IMediaCaptureDevice` 进行，核心类是 `FAndroidCameraMediaPlayer`。

**头文件引入**:
```cpp
#include "IMediaCaptureDevice.h"
#include "IMediaPlayer.h"
```

**基本用法（获取摄像头设备列表）**:
```cpp
// 获取媒体设备支持接口
TArray<IMediaCaptureDevice*> CaptureDevices;
if (FModuleManager::Get().LoadModule<IMediaCaptureDeviceSupport>(“AndroidCamera”))
{
    // 枚举所有可用的 Android 摄像头设备
    // 具体的枚举逻辑封装在 AndroidCamera 模块内部
}
```

### Demo 示例

一个最小的可编译示例，展示如何在 C++ Actor 中初始化并使用 Android 摄像头播放器。

**AndroidCameraTestActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MediaPlayer.h"
#include "AndroidCameraTestActor.generated.h"

UCLASS()
class AAndroidCameraTestActor : public AActor
{
    GENERATED_BODY()

public:
    AAndroidCameraTestActor();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    UPROPERTY()
    TObjectPtr<UMediaPlayer> MediaPlayer;

    UPROPERTY()
    TObjectPtr<UMediaTexture> MediaTexture;
};
```

**AndroidCameraTestActor.cpp**
```cpp
#include "AndroidCameraTestActor.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"
#include "MediaSource.h"
#include "UObject/ConstructorHelpers.h"

AAndroidCameraTestActor::AAndroidCameraTestActor()
{
    PrimaryActorTick.bCanEverTick = false;

    // 在构造函数中查找默认媒体纹理资产（可选，也可在运行时创建）
    static ConstructorHelpers::FObjectFinder<UMediaTexture> MediaTextureFinder(
        TEXT(“/Game/Media/YourMediaTexture”));
    if (MediaTextureFinder.Succeeded())
    {
        MediaTexture = MediaTextureFinder.Object;
    }
}

void AAndroidCameraTestActor::BeginPlay()
{
    Super::BeginPlay();

    // 创建 MediaPlayer
    MediaPlayer = NewObject<UMediaPlayer>(this, TEXT(“AndroidCameraPlayer”));
    if (MediaPlayer)
    {
        // 创建一个指向设备前置摄像头的媒体源 (需要 AndroidCameraMediaFactory)
        UMediaSource* CameraSource = nullptr; // 此处应通过工厂创建，示例简化

        if (CameraSource && MediaTexture)
        {
            // 将 MediaPlayer 与 MediaTexture 关联
            MediaTexture->SetMediaPlayer(MediaPlayer);
            // 打开摄像头源
            MediaPlayer->OpenSource(CameraSource);
            MediaPlayer->Play();
        }
    }
}

void AAndroidCameraTestActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (MediaPlayer)
    {
        MediaPlayer->Close();
    }
    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

要使用此插件，你的项目模块通常需要依赖以下内容：

| 模块 | 用途 |
|---|---|
| `AndroidCamera` | 提供 Android 摄像头媒体播放器的核心运行时实现 |
| `MediaAssets` | 使用 Media Framework 的基础资产（MediaPlayer， MediaTexture， MediaSource） |
| `MediaUtils` | Media Framework 的公共工具库 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF。 |
| 2026-02-06 | `d2c0a7b4` | Fixed printf. | 修复了 printf 相关问题。 |
| 2026-02-05 | `d5be7e14` | Fixed printfs. | 修复了多处 printf 调用问题。 |
| 2025-09-19 | `d942b16a` | Fixed some Bughawk JNI issues | 修复了一些 Bughawk JNI 相关问题。 |
| 2025-09-11 | `764d5c18` | Fix crash from pending JNI exception in non-Shipping builds | 修复了非 Shipping 构建中因未处理的 JNI 异常导致的崩溃。 |

### 维护评价

**综合评价：低维护，基本可用**

1.  **年龄**：创建于 2017 年，至今已有约 9 年历史，属于“文物”级别的插件。
2.  **更新频率**：近期（2025-2026年）仍有提交，但内容主要是 JNI 层的 Bug 修复和日志系统迁移，并非功能增强或重大重构。
3.  **维护状态**：处于**维护不活跃**状态。上一次实质性的功能更新可能发生在数年前（如 Media Framework 3.0 时期）。近期更新表明 Epic 仍在处理该模块的编译和平台兼容性问题，但无主动开发迹象。
4.  **已知问题**：依赖于较老的 Android Camera API (android.hardware.Camera)，该 API 在较新的 Android 版本中已被更现代的 Camera2 API 取代。这可能导致在某些新设备上出现兼容性或性能问题。
5.  **推荐使用**：**谨慎推荐**。如果你的项目必须使用 UE 内置的 Media Framework 来集成 Android 摄像头，此插件是官方提供的唯一选择。然而，它功能相对基础且接口陈旧。对于复杂的摄像头控制（如手动曝光、变焦、高性能流处理），通常建议编写自定义原生插件或使用第三方插件。如果项目只需要简单的摄像头预览，且目标 Android 版本不过于新，此插件仍然可用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AndroidCamera)
- [官方文档](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AndroidCamera/Tests)