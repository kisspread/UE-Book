# Android Media Player

> Implements a media player using the Android Media library.

| 属性 | 值 |
|---|---|
| 中文名 | 安卓媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AndroidMedia` (Runtime), `AndroidMediaEditor` (Editor), `AndroidMediaFactory` (Runtime/Editor) |
| 实验性 | 否 |
| 创建时间 | 2014-11-17 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AndroidMedia) | |

## 用途

AndroidMedia 插件通过对接 Android 原生的 `android.media` API（API 14 及以上），在 Android 设备上提供视频和音频的播放能力。它是 UE Media Framework 在 Android 平台的底层实现，将 Java 层的 MediaCodec / MediaPlayer 与 UE 的纹理渲染管线连接起来，使开发者可以通过统一的 Media Framework 接口在 Android 上播放视频文件。

插件的核心价值在于：

- **平台桥接**：通过 JNI 调用 Java 层的 Android Media API，将解码后的视频帧传回 C++ 侧渲染
- **纹理集成**：将解码后的视频帧数据转换为 UE 可用的纹理资源，支持在 UMG / 材质中显示视频
- **可缓存帧缓冲**：通过 `CacheableVideoSampleBuffers` 设置控制视频帧是否独立缓存，适配不同使用场景

## 使用场景

- 你在 Android 上需要播放过场视频或加载画面 → 使用 Media Framework 的标准流程，底层自动走 AndroidMedia
- 你需要在 Android 应用中逐帧处理视频画面（如截图、AI 分析） → 启用 `CacheableVideoSampleBuffers` 确保帧数据可独立访问
- 你的 Android 应用需要从 OBB 包中直接读取视频文件 → AndroidMedia 支持从 ZIP 格式的 OBB 中直接访问视频内容

## 蓝图用法

AndroidMedia 插件本身不直接暴露蓝图节点。它作为 Media Framework 的底层实现，通过 `UMediaPlayer`、`UMediaTexture` 等上层资产间接使用。以下设置可通过 Project Settings 访问：

### 核心设置

| 设置 | 说明 | 所在类 |
|---|---|---|
| `CacheableVideoSampleBuffers` | 是否缓存视频帧缓冲（默认关闭） | `UAndroidMediaSettings` |

### 使用示例（蓝图描述）

1. 在 **Project Settings → Plugins → Android Media** 中，根据需求决定是否启用 `CacheableVideoSampleBuffers`
2. 创建 **Media Player** 资产（右键 → Media → Media Player），选择 Android 平台源
3. 创建 **Media Texture** 资产，关联到该 Media Player
4. 在 **UMG Widget** 中使用 Image 组件引用该 Media Texture，或在材质中使用 Texture Sample 节点
5. 通过蓝图调用 `Media Player → Open Source` 播放视频

## C++ 用法

### 头文件引入

```cpp
#include "AndroidMediaSettings.h"
```

### 基本用法

访问 AndroidMedia 设置（来源：`Public/AndroidMediaSettings.h`）：

```cpp
#include "AndroidMediaSettings.h"

// 获取 AndroidMedia 设置单例
const UAndroidMediaSettings* Settings = GetDefault<UAndroidMediaSettings>();

// 检查视频帧缓冲是否可缓存
// 默认为 false：视频样本复用同一帧缓冲区以避免内存拷贝，提升性能
// 设为 true：每个视频样本独立拷贝帧数据，允许后续独立访问（如截图），但可能降低性能
if (Settings->CacheableVideoSampleBuffers)
{
    // 视频帧将被独立缓存，适合逐帧分析、截图等场景
}
```

### 进阶用法

通过 Media Framework API 播放视频（AndroidMedia 在底层自动工作）：

```cpp
#include "MediaPlayer.h"
#include "MediaTexture.h"
#include "FileMediaSource.h"

// 创建 Media Player
UMediaPlayer* MediaPlayer = NewObject<UMediaPlayer>();

// 创建媒体源（可指向 APK 内或 OBB 内的视频文件）
UFileMediaSource* MediaSource = NewObject<UFileMediaSource>();
MediaSource->SetFilePath(TEXT("Movies/MyVideo.mp4"));

// 打开媒体源，底层会通过 AndroidMediaFactory 创建 Android 平台的播放器实例
bool bOpened = MediaPlayer->OpenSource(MediaSource);

// 关联 Media Texture 用于渲染
UMediaTexture* MediaTexture = NewObject<UMediaTexture>();
MediaTexture->SetMediaPlayer(MediaPlayer);
MediaTexture->UpdateResource();
```

## Demo 示例

### AndroidMediaSettings 自定义配置

```cpp
// MyGameSettings.h
#pragma once

#include "CoreMinimal.h"
#include "AndroidMediaSettings.h"
#include "MyGameSettings.generated.h"

UCLASS()
class UMyGameSettings : public UObject
{
    GENERATED_BODY()

public:
    /** 确保 AndroidMedia 在需要时启用帧缓存 */
    static void ConfigureMediaForAnalysis()
    {
        UAndroidMediaSettings* Settings = GetMutableDefault<UAndroidMediaSettings>();
        // 启用缓存，允许后续独立访问视频帧
        Settings->CacheableVideoSampleBuffers = true;
        Settings->SaveConfig();
    }
};
```

## 模块依赖

由于插件的 Build.cs 未直接提供完整内容，基于其 Media Player 的定位推断依赖如下：

| 模块 | 用途 |
|---|---|
| `MediaUtils` | Media Framework 底层工具 |
| `MediaAssets` | MediaPlayer / MediaTexture 等资产类型 |
| `Media` | Media Framework 核心接口（IMediaPlayer 等） |
| `Launch` | Android JNI 和启动层支持 |

> 无特殊依赖（仅标准 Core/Engine/Slate 等 + Media Framework）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏统一迁移为 UE_LOGF 新格式 |
| 2026-02-05 | `d5be7e14` | Fixed printfs. | 修复遗留的 printf 调用 |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 全局代码清理，将析构函数体改为 = default |
| 2025-08-29 | `32884de4` | Changing more uses of RHICreateTexture to RHICmdList.CreateTexture. | 迁移纹理创建 API 至命令列表新接口 |
| 2025-06-18 | `79ad0f74` | Updated CameraPlayer14 to Camera2 API. | 将摄像头播放器从已废弃的 Camera1 API 迁移至 Camera2 API |

### 维护评价

AndroidMedia 作为 2014 年创建的"文物级"插件，已经历 11 年的 UE 版本迭代。从近期提交来看，该插件仍在持续维护中——2025-2026 年有多次更新，涵盖 API 迁移（Camera2）、RHI 接口适配、日志系统统一等。

**优势**：
- 作为 UE Media Framework 在 Android 平台的标准实现，地位不可替代
- 持续跟进引擎 API 变化，保持与最新 UE 版本兼容
- 功能成熟稳定，多年来未出现重大功能缺陷

**注意事项**：
- `CacheableVideoSampleBuffers` 默认关闭以优化性能，仅在需要逐帧访问时开启
- 仅在 Android 平台生效（`PlatformAllowList: Android`），其他平台会使用其他 Media 实现
- 历史代码中存在一些针对旧版 Android API（API 14）的兼容逻辑

**推荐使用**：✅ 如果你的项目需要在 Android 上播放视频，这是 UE 官方推荐的标准方案，放心使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AndroidMedia)
- [官方文档](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview)