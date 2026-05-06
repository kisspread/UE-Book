# Android Media Player

> Implements a media player using the Android Media library.

| 属性 | 值 |
|---|---|
| 中文名 | Android 媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AndroidMedia` (Runtime), `AndroidMediaEditor` (Editor), `AndroidMediaFactory` (Runtime), `AndroidMediaFactory` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-03-28 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AndroidMedia) | |

## 用途

AndroidMedia 插件利用 Android 原生媒体库（如 MediaPlayer、Camera2 API）在 Android 平台上实现视频、音频的播放与控制。它提供了与 UE 媒体框架（Media Framework）无缝集成的播放器实例，支持本地文件、网络流媒体等常见媒体源。

本插件解决的核心问题：
- 在 Android 设备上高效播放媒体，使用硬件加速解码。
- 通过 UE 的统一媒体接口（`UMediaPlayer`、`UMediaTexture`、`UMediaSoundComponent`）暴露 Android 原生功能。
- 提供可配置的缓存选项（`UAndroidMediaSettings`），优化非引擎应用的帧缓冲行为。

## 使用场景

- 开发 Android 游戏，需要播放视频过场动画、背景视频、广告、UI 视频。
- 构建 Android 互动应用（如多媒体展示、教学软件）中嵌入媒体播放。
- 需要从网络流媒体（HLS、DASH）播放视频，并利用 Android 原生解码器。

## 蓝图用法

本插件以模块形式提供底层实现，不直接暴露大量蓝图节点。主要可通过标准媒体框架的蓝图节点进行操作，同时插件提供了一个设置类 `UAndroidMediaSettings` 用于调整视频帧缓存行为。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CacheableVideoSampleBuffers` (属性) | 控制视频样本缓冲区是否可缓存。启用后将复制帧缓冲区，便于单独帧访问；禁用则复用缓冲区以提升性能。可读写在项目设置中。 | `UAndroidMediaSettings` |

**使用示例**：
1. 打开项目设置 → 插件 → Android Media Player → Video → Cacheable Video Sample Buffers，勾选或取消。
2. 在蓝图中可通过 `Get Class Defaults` 节点获取 `AndroidMediaSettings` 并读取/修改该属性（需启用开发者设置）。

## C++ 用法

### 头文件引入

```cpp
#include "AndroidMediaSettings.h"
```

### 基本用法

获取并修改插件设置（常用于自定义媒体播放器逻辑）：

```cpp
#include "AndroidMediaSettings.h"
#include "HAL/Platform.h"

void ConfigureMediaCache()
{
    // 获取默认设置对象（单例，配置在 Engine.ini）
    UAndroidMediaSettings* Settings = GetMutableDefault<UAndroidMediaSettings>();
    if (Settings)
    {
        // 启用缓存（注意：仅在不编译引擎的应用中有实际作用）
        Settings->CacheableVideoSampleBuffers = true;
        Settings->SaveConfig(); // 保存到配置文件
    }
}
```

*来源：`Engine/Plugins/Media/AndroidMedia/Source/AndroidMediaFactory/Public/AndroidMediaSettings.h`*

### 进阶用法

将媒体播放器与 Android Media Player 创建器结合：

```cpp
#include "MediaPlayer.h"
#include "MediaSource.h"
#include "AndroidMediaPlayer.h" // 实际播放器类（位于 AndroidMedia 模块）

// 创建媒体播放器并打开 Android 原生源
UMediaPlayer* Player = NewObject<UMediaPlayer>();
if (Player)
{
    // 使用 Android 媒体源（如本地文件）
    UMediaSource* Source = UMediaSource::CreateFromFilePath(TEXT("/Game/Movies/Intro.mp4"));
    Player->OpenSource(Source);
}
```

*注意：`UAndroidMediaPlayer` 类未在提供的头文件中暴露，但可通过 `UMediaPlayer` 的 `GetPlayerFacade()->GetPlayer()` 获取平台播放器。*

## Demo 示例

以下是一个完整的模块示例，展示如何通过 `UAndroidMediaSettings` 设置帧缓冲缓存。

**AndroidMediaDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "AndroidMediaDemo.generated.h"

/**
 * 演示 Android Media Player 设置的用法
 */
UCLASS(BlueprintType)
class ANDROIDMEDIADEMO_API UAndroidMediaDemo : public UObject
{
    GENERATED_BODY()

public:
    /** 启用或禁用视频帧缓存 */
    UFUNCTION(BlueprintCallable, Category = "AndroidMedia|Demo")
    static void SetCacheableVideoSampleBuffers(bool bEnable);
};
```

**AndroidMediaDemo.cpp**
```cpp
#include "AndroidMediaDemo.h"
#include "AndroidMediaSettings.h"
#include "HAL/Platform.h"

void UAndroidMediaDemo::SetCacheableVideoSampleBuffers(bool bEnable)
{
    // 获取默认设置对象
    UAndroidMediaSettings* Settings = GetMutableDefault<UAndroidMediaSettings>();
    if (Settings)
    {
        Settings->CacheableVideoSampleBuffers = bEnable;
        Settings->SaveConfig(); // 持久化到 Config/DefaultEngine.ini
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MediaUtils` | 媒体框架工具类 |
| `MediaAssets` | 媒体资产（媒体源、纹理、音效组件） |

**常见依赖**：Core, CoreUObject, Engine, Slate, SlateCore, UMG, InputCore – 已省略。

本插件是 Android 平台专属，无需额外外部库（Android NDK 集成由引擎负责）。

## 维护状态

### 近期更新

- 2025-08-29 `32884de4` — 将多处 `RHICreateTexture` 调用替换为 `RHICmdList.CreateTexture`（渲染线程改进）
- 2025-06-18 `79ad0f74` — 更新 CameraPlayer14 至 Camera2 API（摄像头支持升级）
- 2025-05-31 `52e3dac1` — 使用 UnrealCodeFixup 更新头文件，确保 DLL 存储特性正确放置
- 2025-04-10 `ea97db60` — 电影渲染队列：高分辨率平铺支持，用于分页场景视图状态持久数据
- 2025-03-28 `b892a182` — 新增用于 MediaPlayer14 的 BitmapRenderer（新渲染器）

### 维护评价

- **创建时间**：2025-03-28，至今约 1 年（实际不足一年标签已标记）。
- **近期频率**：每 1~2 月有实质性更新，涉及渲染改进、摄像头 API 迁移、渲染器扩展。
- **活跃度**：活跃维护中，无废弃迹象。
- **限制**：仅适用于 Android 平台；非引擎应用下的帧缓冲行为需根据 `CacheableVideoSampleBuffers` 调整性能。
- **推荐使用**：是，尤其是使用 UE 媒体框架的 Android 项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AndroidMedia)
- [官方文档](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview)（较旧，但媒体框架概念通用）
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Media/AndroidMedia/Tests/)（如存在，目录可能包含自动化测试）