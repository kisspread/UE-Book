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
| 创建时间 | 2017-08-30 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AndroidCamera) | |

## 用途

该插件在 Android 平台上集成了原生 Android Camera API，允许 Unreal Engine 应用程序直接访问设备摄像头，获取实时视频帧。它不仅是一个简单的媒体播放器，更重要的是，它实现了 **OES 外部纹理 (External Texture)** 支持，能够将摄像头捕获的画面直接作为 GPU 纹理使用，避免了 CPU 到 GPU 的拷贝开销，是实现高性能 AR 应用、实时相机滤镜或视频处理的基石。

## 使用场景

- 你在开发一个 Android 平台的 **AR（增强现实）应用**，需要将相机实时画面作为背景或识别目标。
- 你需要制作一个 **实时相机滤镜应用**，需要高效地将摄像头帧数据传入材质或后处理管线。
- 你正在开发一个基于 **Android 设备的视频监控或远程视图系统**。

## 蓝图用法

该插件本身不直接暴露高级蓝图节点，而是作为媒体播放器插件集成在 **媒体框架 (Media Framework)** 中。通过配置媒体播放器资产来使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Media Player` | 创建一个媒体播放器实例，可选择使用 Android Camera 播放器 | `UMediaPlayer` (引擎内置) |
| `Open Source` | 使用 `FileMediaSource` 或 `UrlMediaSource` 打开摄像头源 | `UMediaPlayer` |
| `Get Video Texture` | 获取由摄像头画面更新的媒体纹理资源 | `UMediaTexture` |

### 使用示例（蓝图描述）

1.  **创建资产**:
    *   在内容浏览器中，右键创建 **媒体 -> 媒体播放器 (Media Player)**，命名为 `MP_AndroidCamera`。
    *   右键创建 **媒体 -> 媒体纹理 (Media Texture)**，命名为 `MT_CameraFeed`。
2.  **关联资产**:
    *   打开 `MT_CameraFeed`，在 **媒体播放器** 属性中选择 `MP_AndroidCamera`。
3.  **在 Actor 中使用**:
    *   将 `MT_CameraFeed` 拖拽到场景中的物体（如平面）上，作为材质的基础颜色纹理。
    *   在蓝图中，引用 `MP_AndroidCamera`，使用 `Open Source` 节点。
    *   `Open Source` 的 **媒体源 (Media Source)** 参数应设置为一个 `FileMediaSource` 资产，其 **文件路径 (File Path)** 设置为 `camera://0`（后置摄像头）或 `camera://1`（前置摄像头）。
4.  **流程控制**:
    *   使用 `Play`, `Pause`, `Stop` 等节点控制摄像头画面的开始和停止。

## C++ 用法

### 头文件引入

```cpp
#include “IAndroidCameraModule.h”
#include “MediaPlayer.h”
#include “MediaTexture.h”
```

### 基本用法

以下代码演示如何通过 C++ 模块接口创建一个 Android 相机播放器实例。
```cpp
// 获取 AndroidCamera 模块接口
IAndroidCameraModule* AndroidCameraModule = FModuleManager::LoadModulePtr<IAndroidCameraModule>(“AndroidCamera”);

if (AndroidCameraModule)
{
    // 创建一个媒体事件接收器（通常你的播放器类或自定义类需要实现此接口）
    IMediaEventSink* MyEventSink = /* ... */;
    // 创建播放器实例
    TSharedPtr<IMediaPlayer, ESPMode::ThreadSafe> CameraPlayer = AndroidCameraModule->CreatePlayer(*MyEventSink);

    if (CameraPlayer.IsValid())
    {
        // 通常你会将这个实例赋给 UMediaPlayer 的 NativePlayer。
        // 然后通过 UMediaPlayer 的蓝图或 C++ API 来控制打开、播放等。
    }
}
```
*（基于 `IAndroidCameraModule.h` 接口）*

### 进阶用法

直接操作播放器内部的纹理样本（Texture Sample）以实现自定义处理。
```cpp
// 假设我们有一个对 FAndroidCameraPlayer 的引用 TSharedPtr<FAndroidCameraPlayer> Player
// 或通过 IMediaPlayer 接口获取 IMediaSamples 来访问最新的样本

IMediaSamples& Samples = Player->GetSamples();
const FMediaTextureSample* TextureSample = Samples.GetVideoSample();

if (TextureSample)
{
    // TextureSample->GetTexture() 可以获取到 FRHITexture*，这是一个指向外部纹理（OES Texture）的句柄
    FRHITexture* OESTexture = TextureSample->GetTexture();

    // 在渲染线程（Render Thread）中，你可以将此纹理绑定到自定义的着色器参数上。
    // 同时，可以通过 TextureSample->GetScaleRotation() 和 TextureSample->GetOffset()
    // 获取纹理变换矩阵，用于正确采样。
}
```
*（基于 `AndroidCameraTextureSample.h` 和媒体框架采样接口）*

## Demo 示例

**文件: `MyCameraComponent.h`**
```cpp
#pragma once

#include “CoreMinimal.h”
#include “Components/ActorComponent.h”
#include “MediaPlayer.h”
#include “MediaTexture.h”
#include “MyCameraComponent.generated.h”

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyCameraComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = “Camera”)
    UMediaPlayer* MediaPlayer;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = “Camera”)
    UMediaTexture* MediaTexture;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = “Camera”)
    bool bUseFrontCamera = false;

    UFUNCTION(BlueprintCallable, Category = “Camera”)
    bool StartCamera();

    UFUNCTION(BlueprintCallable, Category = “Camera”)
    void StopCamera();

protected:
    virtual void BeginDestroy() override;

private:
    UPROPERTY()
    UFileMediaSource* MediaSource;
};
```

**文件: `MyCameraComponent.cpp`**
```cpp
#include “MyCameraComponent.h”
#include “MediaSource.h”

bool UMyCameraComponent::StartCamera()
{
    if (!MediaPlayer || !MediaTexture)
    {
        UE_LOG(LogTemp, Warning, TEXT(“MediaPlayer or MediaTexture is not set.”));
        return false;
    }

    // 关联媒体纹理和播放器
    MediaTexture->SetMediaPlayer(MediaPlayer);

    // 创建并配置媒体源
    MediaSource = NewObject<UFileMediaSource>();
    // ‘camera://0’ 代表后置摄像头, ‘camera://1’ 代表前置摄像头
    MediaSource->SetFilePath(bUseFrontCamera ? TEXT(“camera://1”) : TEXT(“camera://0”));

    // 打开媒体源
    bool bOpened = MediaPlayer->OpenSource(MediaSource);

    if (bOpened)
    {
        // 立即开始播放（捕获摄像头画面）
        MediaPlayer->Play();
    }

    return bOpened;
}

void UMyCameraComponent::StopCamera()
{
    if (MediaPlayer && MediaPlayer->IsPlaying())
    {
        MediaPlayer->Close();
    }
}

void UMyCameraComponent::BeginDestroy()
{
    StopCamera();
    Super::BeginDestroy();
}
```

## 模块依赖

从 Build.cs 的依赖分析，使用者需要关注以下模块：

| 模块 | 用途 |
|---|---|
| `AndroidCameraFactory` | 工厂模式的核心，负责根据平台和媒体源创建对应的播放器实例 |
| `MediaUtils` | 媒体框架的工具库，提供样本队列、采样器等通用功能 |
| `AndroidCameraEditor` | 提供编辑器支持（如媒体播放器资产的创建向导） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移到新的 UE_LOGF 格式 |
| 2026-02-06 | `d2c0a7b4` | Fixed printf. | 修复了日志格式化问题 |
| 2026-02-05 | `d5be7e14` | Fixed printfs. | 修复了多处日志格式化错误 |
| 2025-09-19 | `d942b16a` | Fixed some Bughawk JNI issues | 修复了一些与 Bughawk JNI 相关的问题 |
| 2025-09-11 | `764d5c18` | Fix crash from pending JNI exception in non-Shipping builds | 修复了非发行版本中因待处理JNI异常导致的崩溃 |

### 维护评价

**维护中，但实质性功能更新停滞。**

*   **创建时间**: 该插件创建于 2017 年，是媒体框架 3.0 时期的一部分。
*   **最近更新频率和内容**: 最近几年的提交主要是编译修复、日志改进和 JNI 稳定性修复（如 `Bughawk` 问题），没有新的功能特性或架构改动。最后一次**功能性更新**在 2017 年底左右。
*   **活跃度**: 尚处于维护状态，但仅限于保持其能在新引擎版本中编译和基本运行，没有活跃的功能开发。
*   **已知问题或限制**: 插件版本号为 2.0，但长期未更新，可能存在对新版 Android API 或摄像头硬件特性支持不全的问题。`EnabledByDefault: false` 说明它可能不适用于所有项目。
*   **推荐使用**: **推荐**。尽管更新不频繁，但它依然是 Unreal Engine 在 Android 平台上进行**高性能、低延迟相机访问**的官方和最直接的解决方案。对于 AR 等需要直接操作外部纹理的场景，它是必需的。如果只是简单录制或显示，可以考虑通用的 Media Framework 播放器。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AndroidCamera)
- [官方文档](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview) (链接指向较旧的论坛帖子，当前文档请参考引擎内置帮助)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AndroidCamera/Tests) (如果存在)