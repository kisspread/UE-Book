# Android Camera Player

> Implements camera preview using the Android Camera library.

| 属性 | 值 |
|---|---|
| 中文名 | Android 相机播放器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AndroidCamera` (RuntimeNoCommandlet), `AndroidCameraEditor` (Editor), `AndroidCameraFactory` (Editor), `AndroidCameraFactory` (RuntimeNoCommandlet) |
| 实验性 | 否 |
| 创建时间 | 2025-06-26 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AndroidCamera) | |

## 用途

Android Camera Player 利用 Android 原生 Camera API 实现设备相机的实时预览，并将其作为标准 `UMediaPlayer` 源集成到 Unreal Engine 的媒体框架中。它解决了在 Android 平台上获取相机画面并用于实时渲染管线的问题（例如用作 UI 背景、材质贴图或进行后续处理）。插件自动处理 Android 清单（`AndroidManifest.xml`）中的相机权限声明，并支持前后摄像头选择与配置。

## 使用场景

- 开发需要实时相机预览的 Android 应用（如 AR、视频通话、自拍滤镜）。
- 希望将相机画面作为纹理动态渲染到场景对象上的游戏或交互媒体。
- 需要在前台和后置摄像头之间切换，并控制 Android 平台级权限的应用。

## 蓝图用法

本插件**不提供任何可直接由蓝图调用的函数或可读写属性**。所有运行时功能通过 Unreal Engine 的媒体框架蓝图节点实现。

要使用 Android Camera Player，请在蓝图中按以下步骤操作：

1. 创建 `Media Player` 资源（`Content Browser` → 右键 → `Media` → `Media Player`），勾选“Create Media Source”一同创建关联的 `Media Source` 资产。
2. 将 `Media Source` 的 `Player` 属性设置为 `AndroidCameraPlayer`（插件注册的播放器类型）。
3. 在蓝图中使用“打开媒体源”节点，指定上述 `Media Player` 和 `Media Source`。
4. 将 `Media Player` 与 `Media Texture` 或 `Media Sound` 组件连接以输出画面与声音。

相机权限和首选摄像头（前置/后置）可在**项目设置** → `Android Camera Runtime Settings` 中配置（通过 `UAndroidCameraRuntimeSettings` 类暴露的 `EditAnywhere` 属性）。

## C++ 用法

### 头文件引入

```cpp
#include "AndroidCameraRuntimeSettings.h"
#include "MediaPlayer.h"
#include "MediaSource.h"
```

### 基本用法

从项目配置中读取权限设置：

```cpp
#include "AndroidCameraRuntimeSettings.h"

void UMyCustomGameInstance::Init()
{
    const UAndroidCameraRuntimeSettings* Settings = GetDefault<UAndroidCameraRuntimeSettings>();
    if (Settings)
    {
        bool bHasPermission = Settings->bEnablePermission;
        bool bRequiresAnyCamera = Settings->bRequiresAnyCamera;
        // ... 根据配置自行决定逻辑
    }
}
```

### 进阶用法

动态创建 `AndroidCameraPlayer` 媒体源并打开：

```cpp
// 创建一个媒体播放器对象
UMediaPlayer* MediaPlayer = NewObject<UMediaPlayer>();
if (MediaPlayer)
{
    // 通过播放器打开相机（需要先设置相应的媒体源，通常由 C++ 构造）
    // AndroidCameraPlayer 内部通过 FName "AndroidCamera" 注册，可直接用播放器打开 URL 格式
    // 例如: "androidcam://" 或格式化的 URL
    // 更常用的方法是使用预设的 UMediaSource 子类：UAndroidCameraMediaSource  (由 AndroidCameraFactory 模块提供)
    // 此处仅示意
    MediaPlayer->OpenSource("androidcam://");
}
```

> **注意**：`AndroidCameraFactory` 模块提供了 `UAndroidCameraMediaSource` 派生类，建议通过 `LoadObject` 或 `CreateDefaultSubobject` 创建并使用，以实现更稳定的设备选择。

## Demo 示例

以下是一个简单的 `AActor` 子类，在 `BeginPlay` 时打印当前相机权限配置。

```cpp
// MyAndroidCameraActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyAndroidCameraActor.generated.h"

UCLASS()
class AMyAndroidCameraActor : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
};
```

```cpp
// MyAndroidCameraActor.cpp
#include "MyAndroidCameraActor.h"
#include "AndroidCameraRuntimeSettings.h"
#include "HAL/PlatformProcess.h"

void AMyAndroidCameraActor::BeginPlay()
{
    Super::BeginPlay();

    const UAndroidCameraRuntimeSettings* Settings = GetDefault<UAndroidCameraRuntimeSettings>();
    if (Settings)
    {
        UE_LOG(LogTemp, Log, TEXT("Camera Permission Enabled: %s"),
            Settings->bEnablePermission ? TEXT("true") : TEXT("false"));
        UE_LOG(LogTemp, Log, TEXT("Requires Any Camera: %s"),
            Settings->bRequiresAnyCamera ? TEXT("true") : TEXT("false"));
        UE_LOG(LogTemp, Log, TEXT("Requires Back Camera: %s"),
            Settings->bRequiresBackFacingCamera ? TEXT("true") : TEXT("false"));
        UE_LOG(LogTemp, Log, TEXT("Requires Front Camera: %s"),
            Settings->bRequiresFrontFacingCamera ? TEXT("true") : TEXT("false"));
    }
}
```

将此 Actor 拖入关卡并运行于 Android 设备上，可在日志中看到设置值。

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。实际运行时需要 Android 平台支持以及 Media 框架（`MediaAssets` 等默认包含）。

| 模块 | 用途 |
|---|---|
| `AndroidCamera` | 运行时相机播放器核心实现 |
| `AndroidCameraEditor` | 编辑器配置界面（含 `UAndroidCameraRuntimeSettings`） |
| `AndroidCameraFactory` | 注册 `AndroidCameraPlayer` 为可用 `UMediaPlayer` 源 |

## 维护状态

### 近期更新

- 2025-09-11 `6312e16d` Fix crash from pending JNI exception in non-Shipping builds  
- 2025-08-29 `32884de4` Changing more uses of RHICreateTexture to RHICmdList.CreateTexture.  
- 2025-08-12 `f5866ce3` Fixed the timing of firing MediaOpened in AndroidCameraPlayer.  
- 2025-08-08 `d7c83195` Fixed a Java exception when closing the CameraDevice during its initialization.  
- 2025-06-26 `9294da93` Remove two imports not used.

### 维护评价

插件近期更新频繁，修复了多个潜在崩溃和初始化时序问题，表明其处于**活跃维护**状态。由于创建时间不足半年，暂无大规模功能变更，但作为 Android 相机预览的唯一官方方案，在 5.5+ 版本中表现稳定。推荐在需要 Android 相机输入的项目中使用。

## 相关链接

- [源码（插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AndroidCamera)
- [官方媒体框架文档（UE 4.5 时代）](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AndroidCamera/Source)（同源码目录，无独立测试目录）