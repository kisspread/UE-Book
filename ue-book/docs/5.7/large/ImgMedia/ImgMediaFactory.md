# Image Sequence Media Player

> Implements a media player for image sequences in EXR and other formats.

| 属性 | 值 |
|---|---|
| 中文名 | 图像序列媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ImgMediaFactory` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-08-15 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ImgMedia) | |

## 用途

该模块是图像序列媒体播放器的**工厂模块**与**全局配置组件**。它负责向 Unreal Engine 的媒体框架注册“图像序列”这一媒体源类型，并提供一个集中的 `UImgMediaSettings` 配置对象，用于控制运行时行为，包括：

- 默认帧率设定
- 缓存策略（本地缓存与全局缓存的大小、线程数、栈大小）
- 带宽节流（低带宽时跳过帧）
- EXR 解码线程数
- 默认代理（Proxy）标签

通过该模块，用户可以在项目设置中调整图像序列播放的性能与质量平衡，无需修改代码。

## 使用场景

- 需要播放 **EXR、PNG、JPG 等图像序列** 作为视频源，例如电影级过场、虚拟制片（Virtual Production）、时间线渲染输出。
- 希望利用**代理机制**（Proxy）切换不同分辨率序列，用于预览低分辨率素材，最终渲染时替换为全分辨率版本。
- 在性能敏感环节（如 VR、实时预览）中，通过**带宽节流**和**缓存优化**保证播放流畅性。
- 使用**全局缓存**跨多个播放器共享已加载的帧，减少内存占用。

## 蓝图用法

`UImgMediaSettings` 类通过 `config=Engine` 自动暴露到 **Project Settings → Image Sequence Media Player** 页面，可在编辑器中直接修改，无需蓝图节点。

其属性均为 `EditAnywhere` 但**未标记 `BlueprintReadWrite`**，因此不能在蓝图中直接读写。若需要在蓝图中获取当前设置，可以通过 `GetDefault<UImgMediaSettings>()`（C++ 函数封装后暴露给蓝图），但引擎并未提供原生蓝图节点。建议通过 C++ 或控制台命令修改。

### 核心配置属性（可在设置页面修改）

| 属性 | 说明 | 范围 |
|---|---|---|
| `DefaultFrameRate` | 图像序列未指定帧率时的默认值 | 24fps |
| `BandwidthThrottlingEnabled` | 带宽不足时是否自动降帧 | true/false |
| `CacheBehindPercentage` | 播放头后方缓存占总缓存百分比 | 0–100（默认25%） |
| `CacheSizeGB` | 本地缓存大小（GB） | ≥0（默认1GB） |
| `CacheThreads` | 缓存线程数，0=自动（默认2） | ≥0 |
| `CacheThreadStackSizeKB` | 缓存线程栈大小（KB） | ≥128（默认128） |
| `GlobalCacheSizeGB` | 全局缓存大小（GB） | ≥0（默认1GB） |
| `UseGlobalCache` | 是否启用全局缓存 | true/false |
| `ExrDecoderThreads` | EXR解码线程数，0=自动 | ≥0 |
| `DefaultProxy` | 默认代理标签（字符串） | 任意文本 |
| `UseDefaultProxy` | 是否使用默认代理 | true/false |

### 在蓝图中使用建议

通常你不需要直接操作设置对象。只需在编辑器配置好参数，然后使用媒体播放器创建图像序列媒体源（`ImgMediaSource` 或 `FileMediaSource` 配合图像序列文件夹）即可。

## C++ 用法

### 头文件引入

```cpp
#include "ImgMediaSettings.h"
```

### 基本用法

读取当前设置（直接访问默认对象）：

```cpp
const UImgMediaSettings& Settings = *GetDefault<UImgMediaSettings>();

// 获取默认帧率
FFrameRate DefaultRate = Settings.DefaultFrameRate;

// 检查是否启用了带宽节流
if (Settings.BandwidthThrottlingEnabled)
{
    // 处理降帧逻辑
}
```

### 设置运行时覆盖

`UImgMediaSettings` 不是单例，但引擎通过配置文件管理其持久化。若需要在运行时临时修改（例如根据设备性能），可构造临时对象或通过控制台变量（`cvars`）实现。部分设置（如 `CacheSizeGB`）支持在编辑器中生效；运行时修改需调用 `PostEditChangeProperty` 等效方法：

```cpp
UImgMediaSettings* Settings = const_cast<UImgMediaSettings*>(GetDefault<UImgMediaSettings>());
Settings->CacheSizeGB = 2.0f; // 修改本地缓存为2GB
// 注意：修改默认对象可能影响所有引用，请谨慎。推荐使用控制台变量。
```

### 监听设置变更

`OnSettingsChanged` 静态多播委托让你可以在设置变更时获得通知（仅在 Editor 模式下启用）：

```cpp
#include "ImgMediaSettings.h"

#if WITH_EDITOR
UImgMediaSettings::OnSettingsChanged().AddLambda([](const UImgMediaSettings* NewSettings)
{
    // 响应设置变化，例如重新初始化缓存
});
#endif
```

### 获取默认代理名称

```cpp
FString Proxy = GetDefault<UImgMediaSettings>()->GetDefaultProxy();
// If UseDefaultProxy == false, returns empty string.
```

## Demo 示例

以下代码演示如何通过 `GetDefault` 读取配置并应用于自定义播放逻辑。

**MyMediaPlayer.cpp** (假设已有 media player 引用)

```cpp
// Copyright Epic Games, Inc. All Rights Reserved.

#include "MyMediaPlayer.h"
#include "ImgMediaSettings.h"

void UMyMediaPlayer::UpdateCacheSettings()
{
    const UImgMediaSettings* Settings = GetDefault<UImgMediaSettings>();
    if (!Settings) return;

    // 设置本地缓存大小
    SetLocalCacheSize(Settings->CacheSizeGB * 1024.0f * 1024.0f * 1024.0f); // GB to bytes

    // 设置缓存线程数
    SetCacheThreads(Settings->CacheThreads > 0 ? Settings->CacheThreads : FPlatformMisc::NumberOfCores());

    // 使用全局缓存
    if (Settings->UseGlobalCache)
    {
        EnableGlobalCache(Settings->GlobalCacheSizeGB);
    }
    else
    {
        DisableGlobalCache();
    }
}
```

## 模块依赖

该模块依赖较少，主要为引擎媒体框架基础模块。

| 模块 | 用途 |
|---|---|
| `Media` | 媒体框架核心接口 |
| `MediaAssets` | 媒体播放器、媒体源等资产类 |
| `MediaUtils` | 媒体工具函数 |

**省略常见依赖**：Core, CoreUObject, Engine, Slate 等已包含在标准模板中。

## 维护状态

### 近期更新

```
- 2025-10-17 f81b388d [ImgMedia] Fix out of memory crash caused by unprotected large frame gaps.
- 2025-10-10 ebdf8ce6 [ImgMedia] Handle global cache frame eviction while scrubbing.
- 2025-09-29 f131b1dc [ImgMedia] Fixing non-safe game tickable created in async load.
- 2025-08-21 2c158c4d Change GetUsedTextures MaterialInterface to use TOptional parameters instead of Enum+bool pairs
- 2025-08-15 ae8bb436  ImgMedia: Setting frame duration as per the sequence frame rate instead of the value from the global
```

### 维护评价

- **创建时间**：2025年8月（约2个月前）
- **更新频率**：频繁，几乎每1-2周有修复或功能更新
- **活跃度**：非常活跃，持续有核心开发者维护
- **已知问题**：近期集中修复了内存溢出、全局缓存竞态、异步加载线程安全等问题，说明正在积极解决稳定性问题
- **推荐使用**：适合用于生产环境，但因较新，建议关注后续更新。`ImgMediaFactory` 模块本身稳定，主要维护点集中在其他运行时模块。

## 相关链接

- [源码（插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ImgMedia)
- [官方文档（Media Framework）](https://docs.unrealengine.com/5.7/en-US/media-framework-in-unreal-engine/)
- [测试用例（插件内 Tests 文件夹）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ImgMedia/Source/ImgMedia/Tests)