# Android Camera Player

> Implements camera preview using the Android Camera library.

| 属性 | 值 |
|---|---|
| 中文名 | 安卓摄像头播放器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AndroidCamera` (RuntimeNoCommandlet), `AndroidCameraEditor` (Editor), `AndroidCameraFactory` (Editor), `AndroidCameraFactory` (RuntimeNoCommandlet) |
| 实验性 | 否 |
| 创建时间 | 2017-08-30 |
| 年龄标签 | 🏛️ 文物（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AndroidCamera) | |

## 用途

该插件是 Unreal Engine 媒体框架的一部分，专门用于在 Android 设备上访问和预览设备的物理摄像头。它实现了基于 Android Camera 库（可能是 Camera1 或 Camera2 API）的媒体播放器，允许开发者将 Android 设备的前置或后置摄像头作为视频流源集成到游戏中。

其核心价值在于为 Android 平台提供了统一的、符合 UE 媒体框架标准的摄像头访问方式，使得开发者可以通过标准的 `UMediaPlayer` 和 `UMediaTexture` 蓝图资产来使用摄像头画面，而无需处理复杂的平台原生代码。这通常用于实现增强现实（AR）功能、摄像头预览、二维码扫描等需要实时摄像头输入的应用场景。

## 使用场景

- 你在开发一个 Android 平台的 AR 游戏或应用，需要实时访问设备摄像头画面作为背景或纹理。
- 你需要在游戏内实现一个“拍照”或“录像”功能，通过 UI 实时显示摄像头预览。
- 你的项目需要进行二维码或图像识别，需要从摄像头捕获视频帧进行分析。
- 你需要将 Android 设备的摄像头视频流通过 UE 的媒体管线进行处理（例如，作为纹理应用到 3D 模型上）。

## 蓝图用法

该插件本身不直接暴露大量可供蓝图调用的函数，而是作为媒体播放器的一个平台后端实现。因此，其使用方式与使用其他媒体源（如视频文件）类似。

### 核心节点

该插件的主要功能通过 Unreal Engine 的媒体框架 (`MediaFramework`) 间接提供。

| 节点 | 说明 | 所在类 |
|---|---|---|
| **Open Source** | `UMediaPlayer` 的函数。用于打开一个媒体源。对于摄像头，源通常是 `UAndroidCameraMediaSource` 的实例。 | `UMediaPlayer` |
| **Open URL** | `UMediaPlayer` 的函数。也可以用于打开媒体源，对于摄像头，使用特定的 URL 格式（例如 `androidcamera://`）。 | `UMediaPlayer` |
| **Set Video Texture** | `UMediaTexture` 的函数。用于将一个 `UMediaPlayer` 的视频输出链接到纹理，以便在材质或 UI 中使用。 | `UMediaTexture` |

### 使用示例（蓝图描述）

1. **创建资产**：
   - 在内容浏览器中，右键创建一个 `MediaPlayer` 资产。
   - 创建一个 `MediaTexture` 资产。

2. **配置和连接**：
   - 打开 `MediaPlayer` 资产的编辑器。
   - 在“平台”设置中，确保选中了“Android”。
   - 在 `MediaPlayer` 的详细信息面板中，找到 `Media Source` 属性。你可以通过下拉菜单选择一个预定义的 Android 摄像头源，或者通过 `Open URL` 节点动态打开一个摄像头源。
   - 将创建的 `MediaTexture` 资产拖拽到 `MediaPlayer` 的 `Video Output Texture` 属性上，建立链接。

3. **在场景中使用**：
   - 在你的关卡中，放置一个 `Media Sound` Actor（如果需要音频）。
   - 在场景中创建一个静态网格体或UI图像。
   - 创建一个材质，将 `MediaTexture` 作为纹理样本节点的输入，并将该材质应用到网格体或UI图像上。
   - 当游戏在 Android 设备上运行时，摄像头画面就会实时显示在应用了该材质的物体上。

## C++ 用法

C++ 用法主要涉及对底层媒体播放器和设置的配置。

### 头文件引入

```cpp
#include "AndroidCamera/AndroidCameraSettings.h"
```

### 基本用法

访问和配置 Android 摄像头媒体播放器的全局设置。这些设置可以通过 `UAndroidCameraSettings` 类在项目的引擎配置文件（`DefaultEngine.ini`）或通过 C++ 代码修改。

```cpp
// 获取 AndroidCamera 插件的设置对象
UAndroidCameraSettings* CameraSettings = GetMutableDefault<UAndroidCameraSettings>();

// 检查并修改是否缓存视频采样缓冲区（默认为 false）
// 注意：这个设置会严重影响性能，仅当需要访问单独的帧数据时才开启
if (CameraSettings)
{
    CameraSettings->CacheableVideoSampleBuffers = true;
    CameraSettings->SaveConfig(); // 保存配置到文件
}
```

### 进阶用法

直接操作媒体播放器以编程方式控制摄像头。这通常在更复杂的场景中使用，例如需要在不同摄像头之间切换。

```cpp
#include "MediaPlayer.h"
#include "MediaTexture.h"

// 假设你已经有了一个 MediaPlayer 和 MediaTexture 的引用（例如，通过 UPROPERTY 暴露给蓝图）
UMediaPlayer* MyMediaPlayer;
UMediaTexture* MyMediaTexture;

// 在游戏开始或需要时打开前置摄像头
// "androidcamera://front" 表示前置摄像头，"androidcamera://back" 表示后置摄像头
bool bOpened = MyMediaPlayer->OpenUrl(TEXT("androidcamera://front"));

// 或者，通过选择预定义的 MediaSource 来打开
// UMediaSource* CameraSource = ...; // 从内容资产加载或创建
// bOpened = MyMediaPlayer->OpenSource(CameraSource);

if (bOpened)
{
    // 将 MediaPlayer 的输出链接到 MediaTexture
    MyMediaPlayer->SetVideoTexture(MyMediaTexture);
    
    // 播放
    MyMediaPlayer->Play();
}
```

## Demo 示例

一个在 Android 上显示前置摄像头预览的最小 Actor 类。

### MyCameraActor.h
```cpp
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
    AMyCameraActor();

protected:
    virtual void BeginPlay() override;

public:
    virtual void Tick(float DeltaTime) override;

    // 暴露给蓝图和编辑器，用于在编辑器中指定资产
    UPROPERTY(EditAnywhere, Category = "Camera")
    UMediaPlayer* CameraPlayer;

    UPROPERTY(EditAnywhere, Category = "Camera")
    UMediaTexture* CameraTexture;
};
```

### MyCameraActor.cpp
```cpp
#include "MyCameraActor.h"

AMyCameraActor::AMyCameraActor()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AMyCameraActor::BeginPlay()
{
    Super::BeginPlay();

    if (CameraPlayer && CameraTexture)
    {
        // 在 BeginPlay 时打开前置摄像头
        CameraPlayer->OpenUrl(TEXT("androidcamera://front"));
        
        // 设置输出纹理
        CameraPlayer->SetVideoTexture(CameraTexture);
        
        // 开始播放
        CameraPlayer->Play();
    }
}

void AMyCameraActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    // 此处可以添加每帧的更新逻辑，例如切换摄像头
}
```

**使用说明**：
1. 将上述 Actor 的头文件和源文件添加到你的项目模块中。
2. 在编辑器中放置一个该 Actor 到你的关卡。
3. 在该 Actor 的详情面板中，为其 `CameraPlayer` 属性指定一个 `MediaPlayer` 资产。
4. 为其 `CameraTexture` 属性指定一个 `MediaTexture` 资产。
5. 将 `MediaTexture` 用作场景中某个物体的材质纹理。
6. 在 Android 设备上打包并运行项目，即可看到摄像头预览。

## 模块依赖

从 `Build.cs` 文件分析，该插件没有引入任何**不常见**的模块依赖。它主要依赖于标准的 Unreal Engine 核心模块和媒体框架模块。

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

该插件自 2017 年创建以来，仍在持续维护，但更新频率较低，主要集中在 bug 修复和兼容性调整上。

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏 UE_LOG 迁移到 UE_LOGF。 |
| 2026-02-06 | `d2c0a7b4` | Fixed printf. | 修复了 printf 相关的错误。 |
| 2026-02-05 | `d5be7e14` | Fixed printfs. | 修复了多个 printf 相关的错误。 |
| 2025-09-19 | `d942b16a` | Fixed some Bughawk JNI issues | 修复了一些与 Bughawk JNI（Java Native Interface）相关的问题。 |
| 2025-09-11 | `764d5c18` | Fix crash from pending JNI exception in non-Shipping builds | 修复了在非 Shipping 版本中，由于挂起的 JNI 异常导致的崩溃问题。 |

### 维护评价

- **创建时间**：该插件于 2017 年随 Media Framework 3.0 一同引入，历史悠久。
- **维护频率**：过去几年有零星的维护性提交，主要集中在 JNI 稳定性、日志和编译错误修复上。最近一次功能性更新似乎停留在 2023 年左右（基于提交内容推断），近年来的提交均为修复性质。
- **活跃状态**：**维护不活跃**。虽然仍在接收修复，但已超过 1 年没有实质性新功能开发。插件功能相对稳定和封闭。
- **已知限制**：
    1. 仅适用于 Android 平台。
    2. 默认未启用，需要在项目设置中手动启用。
    3. 性能可能受限于 Android 设备的具体硬件和 Camera API 实现。
    4. `CacheableVideoSampleBuffers` 选项会带来显著的性能开销。
- **推荐使用**：如果你的项目**必须**在 Android 上访问物理摄像头，并且你的 UE 版本兼容（该插件存在多年，通常被支持），那么可以使用。否则，对于跨平台项目，建议考虑更现代的、平台无关的 AR 框架（如 ARFoundation），或者如果只需摄像头预览且不介意平台依赖，可以使用此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AndroidCamera)
- [官方文档](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AndroidCamera/Tests) (如果存在)