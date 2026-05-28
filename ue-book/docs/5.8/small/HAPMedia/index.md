# HAP Media

> Implements video playback of the HAP Codec. HAP is a high performance, high resolution codec that runs on the GPU.

| 属性 | 值 |
|---|---|
| 中文名 | HAP 媒体解码器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `HAPMedia` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-06-20 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/HAPMedia) | |

## 用途

HAP Media 插件为 Unreal Engine 提供了一种高性能、高分辨率的视频解码方案。HAP 是一种基于 GPU 的编解码器，它将解码工作从 CPU 卸载到显卡，从而能够流畅播放极高分辨率（例如 4K 或 8K）的视频文件，非常适合用于大型媒体墙、沉浸式体验、虚拟制作（Virtual Production）和需要同步播放多个高分辨率视频流的场景。该插件是 Windows Media Foundation (WMF) 解码器的一个扩展，专门处理 HAP 编码的视频流。

## 使用场景

- 你需要在场景中播放超高分辨率（4K/8K+）的视频素材，且对 CPU 性能敏感 → 使用 HAP 编码视频并配合此插件。
- 你正在构建一个基于 LED 墙或投影融合的虚拟制作环境，需要多路高分辨率视频同步输出 → HAP 的 GPU 解码特性可以减轻系统负担。
- 你的项目运行在 Windows 平台（Win64），且需要播放 HAP 编码的媒体文件。

## 蓝图用法

此插件主要作为底层解码器工作，不直接暴露蓝图节点。其功能通过 Unreal 的 `UMediaPlayer` 和 `UMediaTexture` 等标准媒体播放类间接使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| *无直接节点* | 作为 WMF 解码器自动注册 | `WmfMediaHAPDecoder` |

### 使用示例（蓝图描述）

1.  **启用插件**：在项目设置的“插件”选项卡中，搜索并启用 `HAPMedia` 插件。
2.  **创建媒体播放器**：在内容浏览器中右键，选择“媒体” > “媒体播放器”，创建一个新的 `MediaPlayer` 资产。
3.  **打开视频文件**：将一个 `.hap` 或使用 HAP 编码的 `.avi` 文件拖拽到 `MediaPlayer` 资产的“源 URL”属性上，或通过 `Open File` 蓝图节点加载。
4.  **连接到纹理**：创建一个 `MediaTexture` 资产，并将其“媒体播放器”属性设置为上一步创建的 `MediaPlayer`。
5.  **应用到材质**：将 `MediaTexture` 用作材质的纹理输入，再将该材质应用到物体（如静态网格体）上，即可播放视频。

## C++ 用法

该插件主要作为内部解码器模块，不提供直接对外的 C++ API。开发者通常通过标准的媒体播放模块（如 `MediaPlayer`）来使用它。以下示例展示了如何在 C++ 中启动媒体播放，底层会自动调用合适的解码器（包括 HAP）。

### 头文件引入

```cpp
#include "MediaPlayer.h"
#include "MediaTexture.h"
```

### 基本用法

以下代码片段展示了如何通过 `MediaPlayer` 打开一个媒体文件。如果该文件是 HAP 编码且插件已启用，系统将自动使用 `WmfMediaHAPDecoder` 进行解码。
（来源：UE5 媒体播放标准用法，非此插件特有）

```cpp
// 创建并初始化一个媒体播放器
UMediaPlayer* MediaPlayer = NewObject<UMediaPlayer>();
FString VideoPath = TEXT("C:/MyVideos/HighResVideo.hap");
if (MediaPlayer->OpenFile(VideoPath))
{
    // 播放成功，连接到 MediaTexture 或进行其他操作
    UE_LOG(LogTemp, Log, TEXT("Media file opened successfully."));
}
else
{
    UE_LOG(LogTemp, Warning, TEXT("Failed to open media file."));
}
```

## Demo 示例

此插件不提供独立的 Demo，但 Epic Games 的官方示例项目（如 Virtual Production 或 Media Playback 示例）中可能会演示其用法。

## 模块依赖

从插件元数据（`.uplugin`）和模块构建文件（`HAPMedia.Build.cs`）分析，该插件依赖于 WmfMedia 插件。

| 模块 | 用途 |
|---|---|
| `WmfMedia` | 提供 Windows Media Foundation 基础解码框架，HAP 解码器是其扩展 |

*注：使用此插件时，WmfMedia 插件会被自动启用。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式日志宏迁移至新的 `UE_LOGF` 格式。 |
| 2023-04-03 | `ebabab67` | Electra: Copy-up from codec refactor task stream | 来自编解码器重构任务分支的代码同步。 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新内置插件的供应商链接为安全协议（https）。 |
| 2022-08-15 | `a2d38616` | Fixing up DX12 playback with WMFmediaPlayer (H264/5, HAP, ProRes) | 修复了 DX12 下 WMF 媒体播放器对 H264/5、HAP、ProRes 编码的播放问题。 |
| 2021-11-29 | `9e51a331` | WmfMedia: HAP now uses external buffers. | HAP 解码现在开始使用外部缓冲区。 |

### 维护评价

**维护不活跃**。该插件创建于约 7 年前，主要功能已经稳定。最近的更新集中在 2022 年，主要进行了 bug 修复（如 DX12 兼容性）和基础设施维护（日志宏更新、链接更新），而非新功能开发。由于其功能高度专业化（仅限 Win64 平台的 HAP 解码），且作为 WmfMedia 插件的补充，一旦稳定后更新频率较低是正常的。

**结论**：插件功能稳定，适用于需要在 Win64 上使用 HAP 编解码器的项目。由于已超过 2 年没有重大功能更新，使用时应以官方当前支持的媒体播放功能为准，并注意在最新的引擎版本中进行测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/HAPMedia)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/Media/)（无专属文档，参考通用媒体播放文档）