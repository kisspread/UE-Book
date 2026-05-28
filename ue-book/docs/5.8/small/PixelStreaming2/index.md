# Pixel Streaming 2

> Streaming of Unreal Engine audio and rendering to WebRTC-compatible media players such as a web browsers.

| 属性 | 值 |
|---|---|
| 中文名 | 像素流送 2 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PixelStreaming2` (Runtime), `PixelStreaming2Core` (Runtime), `PixelStreaming2Editor` (Runtime), `PixelStreaming2HMD` (Runtime), `PixelStreaming2Input` (Runtime), `PixelStreaming2RTC` (Runtime), `PixelStreaming2Servers` (Runtime), `PixelStreaming2Settings` (Runtime), `EpicRtc` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-09-04 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming2) | |

## 用途

Pixel Streaming 2 插件是 Epic Games 推出的新一代像素流送解决方案，用于将虚幻引擎应用的实时音频与渲染画面，通过 WebRTC 协议高效地流式传输到支持 WebRTC 的客户端（例如网页浏览器）。它旨在替代旧版像素流送插件，提供更好的架构、性能和可维护性。用户可以通过远程客户端查看并与运行在服务器端的 UE 应用进行交互。

## 模块列表

本插件由多个协作模块组成，以实现清晰的功能划分。

| 模块名 | 一句话说明 |
|---|---|
| `PixelStreaming2` | 主插件模块，负责初始化、生命周期管理和对外暴露核心功能。 |
| `PixelStreaming2Core` | 核心流送引擎，处理视频/音频捕获、编码和传输的底层逻辑。 |
| `PixelStreaming2Editor` | 编辑器集成，提供编辑器内的像素流送配置、预览和控制功能。 |
| `PixelStreaming2HMD` | VR/HMD 支持，为头戴式显示设备提供立体渲染和流送支持。 |
| `PixelStreaming2Input` | 输入处理模块，将来自客户端的鼠标、键盘、触摸等输入事件转发回 UE 应用。 |
| `PixelStreaming2RTC` | WebRTC 会话管理，封装 EpicRtc 库，处理点对点连接、协商和数据传输。 |
| `PixelStreaming2Servers` | 信令与中间件服务器管理，用于协调客户端与流送实例的连接。 |
| `PixelStreaming2Settings` | 设置与配置模块，集中管理所有像素流送相关的项目设置和运行时参数。 |
| `EpicRtc` | Epic 自研的 WebRTC 实现库，作为底层通信协议栈。 |

## 使用场景

-   **云游戏 / 应用串流**：将高性能要求的 UE 游戏或应用运行在云端服务器，玩家通过低配设备（PC、手机、平板）的浏览器即可畅玩。
-   **远程协作与演示**：设计师或开发者可以远程实时查看并操控在编辑器或独立应用中运行的项目，便于团队协作和方案演示。
-   **交互式数字孪生与可视化**：在工业、建筑、城市规划等领域，为客户提供一个轻量级的网页端来交互查看复杂的 3D 场景。
-   **安全的客户端访问**：无需将完整的可执行文件分发给客户端，所有计算都在服务器完成，有效保护项目资产。

## 蓝图用法

本插件提供了丰富的蓝图接口。由于插件规模巨大，具体函数请参阅各子模块的详细文档。核心功能主要分布在 `PixelStreaming2Core` 和 `PixelStreaming2Settings` 模块中。

### 核心功能

| 功能 | 说明 |
|---|---|
| 流送会话管理 | 启动、停止流送，获取当前连接状态和会话信息。 |
| 输入转发 | 接收并处理来自网页客户端的输入事件（键盘、鼠标、触摸、游戏手柄）。 |
| 画面捕获与编码 | 控制视频捕获的分辨率、帧率、编码质量等参数。 |
| 信令连接 | 配置信令服务器地址，管理客户端与流送实例的匹配连接。 |
| HMD / 立体渲染 | 为 VR 设备配置双眼渲染模式并进行流送。 |

### 使用示例（蓝图描述）

1.  **初始化流送**：在游戏开始时，使用 `Create Streamer` 类节点创建一个流送器实例，并调用其 `Start Streaming` 方法。
2.  **配置输入**：在项目设置或通过蓝图，将玩家控制器的输入事件（如 `Input Action`）绑定到像素流送的输入转发接口，确保远程输入能生效。
3.  **动态调整质量**：根据网络条件或客户端性能，通过蓝图动态修改 `Stream Quality`、`Bitrate` 等设置节点。

## C++ 用法

详细的 C++ API 和使用示例请查阅各子模块的文档页。以下是一个简要的代码流程概述。

### 头文件引入

```cpp
#include "PixelStreaming2Core.h"
```

### 基本用法

```cpp
// 获取核心流送模块
IPixelStreaming2Core* PS2Core = IPixelStreaming2Core::Get();
if (PS2Core)
{
    // 创建一个新的流送会话（Streamer）
    TWeakPtr<IPixelStreaming2Streamer> Streamer = PS2Core->CreateStreamer();
    
    // 配置流送器参数 (通常通过设置模块)
    // ...
    
    // 启动流送
    Streamer.Pin()->StartStreaming();
}
```

（代码示例基于核心模块接口模式推断）

## Demo 示例

由于本插件通常与具体的项目游戏逻辑和服务器架构紧密结合，一个独立的最小示例意义有限。Epic Games 通常会在官方示例项目（如 Lyra）或文档中提供完整的集成范例。建议参考官方文档中的“快速入门”指南。

## 模块依赖

本插件的模块之间相互依赖，构成一个整体。作为使用者，你的项目模块主要需要依赖 `PixelStreaming2` 模块来使用其对外接口。以下是其关键的外部依赖。

| 模块 | 用途 |
|---|---|
| `VulkanRHI` | 用于高性能的 GPU 画面捕获。 |
| `MediaUtils` | 多媒体框架基础工具。 |
| `Networking` | 网络通信基础。 |
| `Json` | 处理配置和信令消息。 |
| `Slate`, `SlateCore`, `UMG` | 提供编辑器 UI 和潜在的运行时 UI 叠加层。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `c1dab3e1` | [PixelStreaming2] Fix: Input handler obtaining default target window from wrong method | 修复输入处理器从错误方法获取默认目标窗口的问题 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下 double 常量截断为 float 导致的编译警告 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the ... | 虚拟制作：调整了相关资产分类并进行迁移 |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 JSON 对象以支持多种字符串类型 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复格式化函数中作用域枚举可能导致错误输出的问题 |

### 维护评价

Pixel Streaming 2 于 2024 年 9 月引入，是一个相对较新的、现代化的插件。从近期 git 历史（截至 2026 年 5 月）来看，该插件处于**活跃维护**状态。最近的更新包括**功能性 Bug 修复**（如输入处理）、**代码质量改进**（消除警告）以及**架构重构**（JSON 对象）。这表明 Epic Games 正在持续改进和维护该插件。

**综合评价**：该插件是官方推荐的像素流送解决方案，架构清晰，模块化程度高，且目前维护活跃。对于新项目，**强烈建议使用 Pixel Streaming 2** 来构建云游戏或远程可视化应用。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming2)
-   [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)