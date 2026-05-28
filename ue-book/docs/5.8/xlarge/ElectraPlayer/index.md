# Electra Player

> Cross platform media player for local files and internet streaming. Also provides optimized local mp4 file only player (Protron) for desktop machines.

| 属性 | 值 |
|---|---|
| 中文名 | 伊莱克特拉播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ElectraPlayerFactory` (Runtime), `ElectraPlayerPlugin` (Runtime), `ElectraPlayerPluginHandler` (Runtime), `ElectraPlayerRuntime` (Runtime), `ElectraProtron` (Runtime), `ElectraProtronFactory` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-01-06 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraPlayer) | |

## 用途

ElectraPlayer 是 Epic 为 UE5 开发的核心跨平台媒体播放框架，旨在替代旧的媒体播放器。它主要解决以下问题：
1.  **统一跨平台播放**：为不同平台（桌面、主机、移动）提供一致的媒体播放能力。
2.  **支持网络流媒体**：内置 HTTP 流媒体引擎，支持 HLS 和 MPEG-DASH 等协议，是游戏内嵌入直播、过场动画流或用户生成内容 (UGC) 的理想选择。
3.  **高性能本地播放**：除了通用播放器，还包含 **Protron** 这个专门优化的组件，用于在桌面平台上高效、低延迟地播放本地 MP4 文件（如游戏内的预渲染过场动画）。

## 使用场景

-   你需要在你的游戏中播放一段来自网络的预告片或直播流。
-   你想在游戏内无缝播放一段高保真的本地 MP4 过场动画，且要求占用资源少、启动快。
-   你的应用需要支持多种视频格式和流媒体协议，并希望底层 API 统一。
-   你正在开发多平台（PC、主机、移动端）项目，需要一个可靠、由 Epic 官方维护的媒体播放方案。

## 模块概览

插件采用模块化设计，各模块职责清晰：

| 模块 | 用途 |
|---|---|
| **ElectraPlayerPlugin** | 插件入口和模块注册，将 Electra 播放器注册为引擎的媒体播放器工厂。 |
| **ElectraPlayerFactory** | 负责创建和管理通用的 Electra 播放器实例。 |
| **ElectraPlayerRuntime** | 核心运行时，包含解复用、解码、同步、渲染等所有播放逻辑。 |
| **ElectraPlayerPluginHandler** | 插件处理器，协调播放器插件和运行时之间的交互。 |
| **ElectraProtron** | **Protron** 的具体实现，针对桌面平台优化的本地 MP4 播放器。 |
| **ElectraProtronFactory** | 负责创建 Protron 播放器实例的工厂。 |

## 蓝图用法

ElectraPlayer 主要通过引擎标准的媒体播放 API 在蓝图中使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open Source` (Media Texture/Media Player) | 打开并播放一个本地文件或 URL。 | `UMediaPlayer` |
| `Play` | 开始播放媒体。 | `UMediaPlayer` |
| `Pause` | 暂停播放。 | `UMediaPlayer` |
| `Close` | 关闭当前媒体源。 | `UMediaPlayer` |
| `Is Playing` | 获取当前是否正在播放。 | `UMediaPlayer` |
| `Set Loop` | 设置是否循环播放。 | `UMediaPlayer` |
| `Seek` | 跳转到指定时间点。 | `UMediaPlayer` |

**说明**：在蓝图中使用媒体播放功能时，通常会将一个 `UMediaPlayer` 资产与一个 `UMediaTexture` 或 `UMediaSoundComponent` 连接。在 `UMediaPlayer` 的细节面板中，可以选择“Player”下拉菜单，选择 `ElectraPlayer` 或 `ElectraProtron` 作为后端播放器。

## C++ 用法

在 C++ 中，你可以使用标准的 `FMediaPlayer`、`UMediaPlayer` 等引擎类。ElectraPlayer 作为这些接口的一个实现，对使用者来说通常是透明的。

### 头文件引入

```cpp
#include "MediaPlayer.h"
#include "MediaTexture.h"
// 其他媒体相关头文件
```

### 基本用法

```cpp
// 创建一个 Media Player 对象并使用 Electra 后端打开源
void AMyActor::PlayMedia(const FString& URL)
{
    if (MediaPlayer)
    {
        // 打开源。UMediaPlayer 内部会根据插件优先级选择 ElectraPlayer。
        bool bOpened = MediaPlayer->OpenUrl(URL);
        if (bOpened)
        {
            // 成功打开，可以开始播放
            MediaPlayer->Play();
        }
    }
}
```

### 进阶用法

对于需要更精细控制（例如选择特定播放器后端）或使用 Protron 的场景，可能需要通过工厂类或模块接口，但这通常只在引擎内部或开发自定义媒体源时使用。

## 模块依赖

使用 ElectraPlayer 插件，你的模块通常无需额外依赖。该插件作为媒体播放器的后端，由引擎核心媒体模块调用。如果你需要在 C++ 中直接访问其内部类（非常规情况），则可能需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `MediaAssets` | 引擎的媒体资产（MediaPlayer， MediaTexture）模块，是使用的前提。 |
| `MediaUtils` | 媒体工具模块，提供基础媒体功能。 |
| `ElectraPlayerRuntime` | （仅当需要直接访问播放器内部时）核心播放器运行时。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-21 | `ff9996e8` | Media Profile: Fixed issue where ElectraProtron issue would not play a new video after it had alread | 修复了 Protron 播放器在播放完一个视频后无法播放新视频的问题。 |
| 2026-05-14 | `d15b78b3` | ElectraPlayer: Fixed streamed album metadata | 修复了流媒体中专辑元数据（如标题、艺术家）解析错误的问题。 |
| 2026-05-13 | `4340cfa6` | ElectraPlayer: Added configuration and cvars to control if decoders need to be suspended during play | 新增配置选项，允许控制播放期间是否需要暂停解码器。 |
| 2026-05-12 | `a6372743` | ElectraPlayer: changed an assertion to an if() condition to handle cases where .ts internal timestam | 将一处断言改为 if 条件判断，以处理 .ts 流内部时间戳异常的边缘情况，提高了稳定性。 |
| 2026-05-12 | `e3746831` | ElectraPlayer: Checking for sequence index when prefetching subtitle media segments to reduce unnece | 在预取字幕媒体分段时检查序列索引，以减少不必要的网络请求。 |

### 维护评价

-   **活跃维护**：插件仍在持续更新中，最近一个月内有多次功能优化和重要 Bug 修复提交。
-   **核心组件**：作为 UE5 官方的默认媒体播放解决方案，其稳定性和持续维护有基本保障。
-   **推荐使用**：对于新的 UE5 项目，特别是涉及流媒体或需要高性能跨平台视频播放的项目，**强烈推荐使用 ElectraPlayer**。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraPlayer)
-   [官方文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraPlayer/Tests)