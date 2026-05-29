# Electra Util

> Reusable Base Components for Electra Player Media Playback（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | Electra 播放器工具库 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ElectraBase` (RuntimeNoCommandlet), `ElectraSamples` (RuntimeNoCommandlet), `ElectraHTTPStream` (RuntimeNoCommandlet) |
| 实验性 | 否 |
| 创建时间 | 2021-01-06 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraUtil) | |

## 用途

ElectraUtil 是 Epic 自研媒体播放器 **Electra Player** 的底层工具库，提供构建 Electra 媒体播放管线所需的基础组件。它本身不是一个完整的播放器插件，而是被 Electra Player、Electra ProRes 等插件依赖的共享基础设施。

该插件包含三个子模块，分别解决媒体播放链路中的不同问题：
- **ElectraBase**：核心基础设施，提供平台抽象、缓冲区管理、同步原语、线程安全数据结构、HTTP 传输接口、MP4 解复用、时间码处理、DRM 接口等通用能力
- **ElectraHTTPStream**：HTTP 媒体流传输实现，处理 HLS/DASH 等自适应流媒体的分片下载与解析
- **ElectraSamples**：音频/视频采样帧的定义与管理，包括 I420/YUV 格式的视频帧、PCM/AAC 音频帧等媒体样本的内存布局

**需要注意**：该插件默认未启用（`EnabledByDefault=false`），仅在平台支持列表（Win64/Mac/iOS/tvOS/Android/Linux）内生效，且不支持 Server 目标。它由 Electra Player 主插件在需要时自动引入。

## 模块列表

| 模块 | 类型 | 一句话说明 |
|---|---|---|
| `ElectraBase` | Runtime | 核心基础库：平台抽象、MP4 解复用、HTTP 接口、缓冲区管理、时间码、DRM |
| `ElectraHTTPStream` | Runtime | HTTP 自适应流媒体传输实现（HLS/DASH 分片下载与解析） |
| `ElectraSamples` | Runtime | 媒体采样帧定义：I420 视频帧、PCM/AAC 音频帧等内存布局管理 |

## 使用场景

- 你正在开发**自定义媒体播放器**插件，需要复用 HTTP 流媒体下载、MP4 解复用等基础能力 → 引入 ElectraUtil 各子模块
- 你正在构建**自适应流媒体**（HLS/DASH）的客户端 → 使用 ElectraHTTPStream 的流分片管理功能
- 你需要处理**多种视频/音频格式的采样帧**，统一内存布局和格式转换 → 使用 ElectraSamples 提供的帧描述
- 你需要集成**DRM 内容保护**或**时间码**解析 → 使用 ElectraBase 提供的 DRM 许可证接口和时间码工具

> **注意**：该插件通常不会被直接引用，而是作为 Electra Player（Media Electra Player 插件）的内部依赖自动加载。除非你在构建自己的 Electra 系媒体播放器，否则不需要手动启用此插件。

## 蓝图用法

该插件不包含蓝图可调用的 API（`RuntimeNoCommandlet` 类型，无 `BlueprintCallable` 暴露）。所有功能均为 C++ 层供其他媒体插件内部使用。

## C++ 用法

### 头文件引入

```cpp
#include "ElectraBase.h"
#include "ElectraHTTPStream.h"
#include "ElectraSamples.h"
```

### 基本用法

此插件的 API 面向 Electra 媒体播放器内部开发者，不提供独立的高层使用接口。主要功能通过以下子模块协作完成：

**媒体样本帧创建与操作**（ElectraSamples）：

```cpp
// 创建一个 I420 格式的视频采样帧
// 来源：Source/ElectraSamples/
TSharedPtr<FElectraVideoFrame> VideoFrame = MakeShared<FElectraVideoFrame>();
// 配置分辨率、色彩空间等参数后传递给解码管线
```

**HTTP 流媒体请求**（ElectraHTTPStream）：

```cpp
// 通过 HTTP 流媒体管理器请求 HLS/DASH 分片
// 来源：Source/ElectraHTTPStream/
// 通常由 Electra Player 的播放器适配层内部调用
```

### 进阶用法

在构建自定义 Electra 播放器时，三个模块配合使用：

1. **ElectraBase** 提供底层平台抽象（`IPlatformMediaGenericInterface`）、线程安全容器、MP4 解复用器
2. **ElectraHTTPStream** 基于 ElectraBase 的 HTTP 接口实现流媒体分片下载
3. **ElectraSamples** 定义解码输出帧的标准内存布局，供渲染器消费

## 模块依赖

该插件供其他 Electra 系插件内部依赖，使用者通常不需要直接引入。各模块内部依赖：

| 模块 | 用途 |
|---|---|
| `ElectraBase` | 无特殊依赖（仅标准 Core/Engine/Slate 等） |
| `ElectraHTTPStream` | 依赖 `ElectraBase`（HTTP 传输接口） |
| `ElectraSamples` | 依赖 `ElectraBase`（基础类型）、`DirectX`（GPU 纹理格式） |

> **注意**：ElectraSamples 依赖 `DirectX` 模块，仅在 Win64 平台有效，其他平台通过条件编译跳过相关功能。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `bc37b7ea` | ElectraUtil: added stub methods for server builds to prevent linker errors when this class is accide | 为 Server 构建添加桩方法，防止意外引入时的链接错误 |
| 2026-04-23 | `efcad028` | HDR: Fix HDR normalization factor across media causing incorrect brightness levels going from/to the | 修复跨媒体 HDR 归一化因子导致的亮度异常问题 |
| 2026-04-20 | `3ed2062b` | ElectraDecoders: modernized the decoder factory to be more usable for other clients | 现代化解码器工厂，提升其他客户端的可用性 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到新的 UE_LOGF 格式 |
| 2026-03-25 | `2924c4cc` | [ElectraUtil] Fix timecode subframe precision loss in CreateTimecodeFromMPEGDefinition | 修复 MPEG 时间码转 UE 时间码时的亚帧精度丢失 |

### 维护评价

ElectraUtil 作为 Electra 媒体播放器的核心基础库，**持续处于活跃维护状态**。近半年内有多次实质性更新，涵盖 HDR 修复、解码器工厂重构、Server 兼容性改进等。该插件自 2021 年从 Epic 内部项目迁移至公开代码库以来，作为多个 Electra 媒体插件（Electra Player、Electra ProRes 等）的共享基础设施，得到了稳定且持续的维护。

**推荐使用**：如果你在使用或扩展 Electra 媒体播放器管线，该插件是必不可少的基础依赖。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraUtil)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)
- 子模块文档：[ElectraBase](ElectraBase.md) | [ElectraHTTPStream](ElectraHTTPStream.md) | [ElectraSamples](ElectraSamples.md)