# Bink Media

> Implements a media player using Bink.

| 属性 | 值 |
|---|---|
| 中文名 | Bink 媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `BinkMediaPlayer` (Runtime), `BinkMediaPlayerEditor` (Editor), `BinkMediaPlayerSDK` (External) |
| 实验性 | 否 |
| 创建时间 | 2021-06-08 |
| 年龄标签 | 🀄 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/BinkMedia) | |

## 用途
该插件为 Unreal Engine 5 提供了基于 Bink 视频解码器的媒体播放器实现。Bink 是一种专为游戏设计的高性能、跨平台视频格式，此插件解决了在 UE5 项目中直接集成和播放 Bink 格式视频的需求，特别适用于游戏过场动画、加载画面等需要高效视频解码的场景。

## 使用场景
- 你需要为游戏的过场动画或剧情片段播放高质量、高压缩比的 Bink 视频。
- 你的游戏需要一个可跨多平台（主机、PC）稳定运行的视频播放解决方案。
- 你正在开发一款对视频播放启动速度和解码性能有高要求的游戏。
- **注意**：该插件默认未启用 (`EnabledByDefault: false`)，需要在项目设置中手动启用后才能使用。

## 蓝图用法
BinkMedia 插件的核心功能通过 Unreal Engine 的标准媒体播放框架暴露。在蓝图中，你主要使用通用的媒体播放器接口，并指定使用 Bink 作为后端。

### 核心节点
| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open Source` | 使用给定的媒体源地址打开一个 Bink 视频。 | `UBinkMediaPlayerFactory` |
| `Play` | 开始播放已打开的 Bink 视频。 | `UMediaPlayer` |
| `Close` | 关闭当前正在播放的媒体。 | `UMediaPlayer` |
| `Set Looping` | 设置视频是否循环播放。 | `UMediaPlayer` |

### 使用示例（蓝图描述）
1. 在内容浏览器中右键创建 `MediaPlayer` 资产，在媒体播放器详情面板中，将 `Media Player Class` 选择为 `BinkMediaPlayer`。
2. 在你的游戏逻辑蓝图（如关卡蓝图或Actor蓝图）中，创建该 `MediaPlayer` 资产的引用。
3. 使用 `Open Source` 节点，传入 Bink 视频文件的路径（例如 `file:///D:/GameMovies/Intro.bik`）。
4. 将 `Open Source` 的 `Success` 执行引脚连接到 `Play` 节点。
5. 可以在 `Media Texture` 资产中使用该 `MediaPlayer`，以将视频渲染到游戏中的屏幕或UI上。

## C++ 用法
在 C++ 中，BinkMedia 插件同样通过标准的 `UMediaPlayer` 和 `UMediaSource` 接口进行操作。你需要确保模块依赖正确。

### 头文件引入
```cpp
#include "MediaPlayer.h"
#include "MediaSource.h"
#include "BinkMediaPlayerModule.h" // 用于获取模块接口
```

### 基本用法
```cpp
// 假设你已经有一个指向 UMediaPlayer 对象的指针 MediaPlayer
// 和一个指向 UMediaSource 对象的指针 MediaSource

// 打开媒体源
MediaPlayer->OpenSource(MediaSource);

// 监听打开完成的事件
FOnMediaPlayerMediaEvent OnOpenedEvent;
OnOpenedEvent.AddLambda([this]() {
    // 媒体打开成功，可以开始播放
    MediaPlayer->Play();
});
MediaPlayer->OnMediaOpened.Add(OnOpenedEvent);
```
**注意**：具体的 Bink 媒体播放器工厂类 (`UBinkMediaPlayerFactory`) 的创建和选择通常由引擎的媒体框架自动完成。

## Demo 示例
由于 Bink 是商业中间件，其 SDK 库（BinkMediaPlayerSDK）不包含在公开的源码中。因此，无法提供完整的、可自行编译的最小示例。官方的测试用例（如 `BinkTestBed`）依赖于预编译的 Bink SDK，无法从源码直接构建。

## 模块依赖
使用 BinkMediaPlayer 模块，你的项目或插件模块需要在 `.Build.cs` 文件中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `MoviePlayer` | 提供电影播放器接口和基础类。 |
| `RHI` | 提供渲染硬件接口，用于视频解码后纹理的上传。 |
| `Renderer` | 提供渲染相关的功能。 |
| `Slate` / `SlateCore` | 用于在编辑器或UI中显示媒体控制界面。 |
| `BinkMediaPlayer` | 核心运行时模块，提供 Bink 播放器实现。 |

## 维护状态

### 近期更新
| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移至新的 UE_LOGF 格式。 |
| 2026-04-01 | `2f26bbfa` | Bink: Fixed BinkTestBed | 修复了 Bink 测试平台。 |
| 2026-04-01 | `8a338576` | Bink: Fixed foward def mismatch, just include PixelFormat.h | 修复前向声明不匹配问题。 |
| 2026-04-01 | `9f45180e` | Bink: update for new BinkHL interface | 适配新的 BinkHL 接口。 |
| 2026-02-19 | `3e97632c` | Refactored FSceneViewport / FViewport to remove the ViewportRHI field | 重构视口类以移除 ViewportRHI 字段。 |

### 维护评价
该插件仍在积极维护中。从最近的提交记录看，开发团队正在持续跟进底层 Bink SDK 的更新（如适配 `BinkHL` 接口）、修复问题并适配引擎自身的重构（如 `ViewportRHI` 的移除、日志系统升级）。创建时间约为 5 年，属于成熟期的插件。由于默认未启用，使用时需注意手动启用。总体而言，这是一个稳定且仍在更新的官方插件，推荐需要集成 Bink 视频的项目使用。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/BinkMedia)
- 无官方文档链接（`.uplugin` 中 DocsURL 为空）