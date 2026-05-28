# Pixel Streaming

> Streaming of Unreal Engine audio and rendering to WebRTC-compatible media players such as a web browsers.

| 属性 | 值 |
|---|---|
| 中文名 | 像素流送 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源） |
| 模块 | `PixelStreaming` (Runtime), `PixelStreamingBlueprint` (Runtime), `PixelStreamingBlueprintEditor` (Runtime), `PixelStreamingEditor` (Runtime), `PixelStreamingHMD` (Runtime), `PixelStreamingInput` (Runtime), `PixelStreamingServers` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-31 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming) | |

## 用途

Pixel Streaming 是一个完整的端到端云端渲染和流媒体解决方案。它解决了在不依赖客户端硬件性能的情况下，将 Unreal Engine 应用程序（如游戏、数字孪生、建筑可视化）的画面和音频实时传输给轻量级客户端（如 Web 浏览器、移动设备）的需求。插件通过集成 WebRTC 协议，建立了从 UE 主机到浏览器的低延迟视频流通道，并反向支持浏览器的键盘、鼠标和触摸输入，从而在云端运行 UE 应用。

## 使用场景

- **云端游戏 (Cloud Gaming)**：玩家无需高性能PC，在手机或浏览器上就能玩3A大作。
- **数字孪生与工业可视化**：在Web端展示复杂的工厂模型或城市规划方案，用户无需安装专业软件。
- **交互式体验与广告**：创建基于浏览器的汽车配置器、房地产漫游等高质量3D交互体验。
- **VR/AR 流媒体**：通过 `PixelStreamingHMD` 模块，将高质量的VR内容流式传输到VR头显设备。
- **多用户协同**：作为后端渲染引擎，支持多个用户通过网页同时查看和交互同一场景。

## 蓝图用法

此插件提供了丰富的蓝图接口，主要集中在 `UPixelStreamingInput` 和 `UPixelStreamingSettings` 类中。核心功能包括控制流送的启停、处理输入事件和进行身份验证。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start Streaming` | 启动像素流送服务器 | `UPixelStreamingInput` |
| `Stop Streaming` | 停止像素流送 | `UPixelStreamingInput` |
| `On Connected` | 当新客户端连接时触发的委托 | `UPixelStreamingInput` |
| `On Disconnected` | 当客户端断开时触发的委托 | `UPixelStreamingInput` |
| `On Input Event` | 接收到客户端输入时触发的委托 | `UPixelStreamingInput` |
| `Send Pixel Streaming Response` | 向特定客户端发送自定义消息 | `UPixelStreamingInput` |
| `Force Keyframe` | 强制生成一个新的关键帧 | `UPixelStreamingInput` |
| `Set Authentication Enabled` | 启用或禁用连接身份验证 | `UPixelStreamingSettings` |

### 使用示例（蓝图描述）

1.  **启动流送**：在BeginPlay事件中，获取 `Pixel Streaming` 子系统，调用 `Start Streaming` 节点。
2.  **处理输入**：绑定 `On Input Event` 事件，在事件处理函数中根据输入类型（键盘、鼠标等）执行相应的游戏逻辑。
3.  **身份验证**：在项目设置或蓝图中调用 `Set Authentication Enabled`，然后绑定 `On Authentication` 委托，对连接请求进行验证。

## C++ 用法

C++ 用法主要围绕获取子系统、管理流送生命周期以及处理底层事件。

### 头文件引入

```cpp
#include "PixelStreamingModule.h"
#include "PixelStreamingInputComponent.h"
```

### 基本用法

获取 Pixel Streaming 子系统并启动流送。
```cpp
// 来自测试用例：PixelStreamingTests/Tests/PixelStreamingTest.cpp
IPixelStreamingModule* PixelStreamingModule = FModuleManager::GetModulePtr<IPixelStreamingModule>(TEXT("PixelStreaming"));
if (PixelStreamingModule)
{
    PixelStreamingModule->StartStreaming();
}
```

### 进阶用法

创建一个 `UPixelStreamingInputComponent` 来接收和处理流送输入。
```cpp
// 创建输入组件
UPixelStreamingInputComponent* InputComponent = NewObject<UPixelStreamingInputComponent>(this);
InputComponent->RegisterComponent();

// 绑定输入处理委托
InputComponent->OnInputEvent.AddLambda([](const FString& Descriptor)
{
    // 解析并处理来自浏览器的输入
    UE_LOG(LogTemp, Log, TEXT("Received input: %s"), *Descriptor);
});
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `WebRTC` | 核心的实时通信协议库，用于音视频编解码和传输 |
| `PixelStreamingHMD` | 虚拟现实头显设备支持，用于VR内容的流送 |
| `PixelStreamingServers` | 内置的信令和Web服务器，用于客户端发现和连接建立 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `c1dab3e1` | [PixelStreaming2] Fix: Input handler obtaining default target window from wrong method | 修复了输入处理器从错误方法获取默认目标窗口的问题 |
| 2026-05-14 | `876d5541` | Fix the crash with PIE/Simulate | 修复了在编辑器内播放(PIE)或模拟时发生的崩溃 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量截断为浮点数会产生警告的代码 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the ... | 虚拟制作相关资产分类调整和迁移 |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构了FJsonObject以同时支持FString和UE::FSharedString |

### 维护评价

Pixel Streaming 插件处于**积极维护**状态。它在 2019 年底从实验性阶段毕业，至今已有约 6 年历史。从近期（2026年5月）的提交记录看，开发团队仍在持续修复关键bug（如PIE崩溃、输入处理问题）并进行代码优化（如浮点数警告、JSON重构），表明该插件是 Epic Games 官方支持的核心功能之一。由于 EnabledByDefault 为 false，用户需要手动启用。该插件功能稳定，是 UE 进行云端渲染和 Web 流媒体的官方推荐方案，**推荐使用**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming/Tests)