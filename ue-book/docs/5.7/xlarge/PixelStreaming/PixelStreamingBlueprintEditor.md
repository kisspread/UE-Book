# Pixel Streaming

> Streaming of Unreal Engine audio and rendering to WebRTC-compatible media players such as a web browsers.

| 属性 | 值 |
|---|---|
| 中文名 | 像素流送 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PixelStreaming` (Runtime), `PixelStreamingBlueprint` (Runtime), `PixelStreamingBlueprintEditor` (Runtime), `PixelStreamingEditor` (Runtime), `PixelStreamingHMD` (Runtime), `PixelStreamingInput` (Runtime), `PixelStreamingServers` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-08-29 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming) | |

## 用途

Pixel Streaming 插件允许 Unreal Engine 将渲染后的画面（含音频）通过 WebRTC 协议实时推送到浏览器或其他支持 WebRTC 的客户端。它解决了传统 UE 应用受限于本地硬件、无法远程访问的问题，广泛应用于云游戏、虚拟展厅、远程协作、工业仿真展示等场景。

本模块 `PixelStreamingBlueprintEditor` 是编辑器扩展，为 Pixel Streaming 的视频输入资产（`UPixelStreamingStreamerVideoInput`）提供内容浏览器的创建工厂与资产类型动作，使用户可以在编辑器中通过右键菜单快速创建以下三种视频输入方式：

- 后台缓冲区（BackBuffer）——直接抓取主视口
- MediaCapture——通过自定义 MediaCapture 捕获渲染
- RenderTarget——使用指定的渲染目标（TextureRenderTarget2D）

## 使用场景

- 你需要在 Web 浏览器中嵌入实时 UE 场景，例如产品展示、建筑可视化。
- 你希望将 UE 作为远程渲染引擎，客户端只需浏览器即可交互。
- 你需要自定义视频源的输入方式（例如不抓取主视口，而是抓取某个 Render Target）。

## 蓝图用法

> 以下节点由 `PixelStreamingBlueprint` 模块提供，可通过蓝图调用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Streamer` | 创建一个新的像素流送器（Streamer）实例 | `UPixelStreamingBlueprint` |
| `Start Streaming` | 启动指定 Streamer，开始推送视频流 | `UPixelStreamingBlueprint` |
| `Stop Streaming` | 停止指定 Streamer | `UPixelStreamingBlueprint` |
| `Set Video Input` | 设置 Streamer 的视频输入来源（如 RenderTarget） | `UPixelStreamingBlueprint` |
| `Get Streamer` | 通过 Streamer ID 获取已创建的 Streamer | `UPixelStreamingBlueprint` |

### 使用示例

1. **创建并启动流送**
   - `Create Streamer` → 输出 `Streamer`（类型为 `UPixelStreamingStreamer`）
   - `Set Video Input` 连接刚创建的 `Streamer`，并指定 `Video Input` 为 `BackBuffer`（预设资产）
   - `Start Streaming` 传入该 `Streamer`

2. **使用 RenderTarget 作为视频源**
   - 在内容浏览器中右键创建 "Streamer Video Input" → 选择 "Render Target Input"，生成一个 `UPixelStreamingStreamerVideoInputRenderTarget` 资产
   - 蓝图内将该资产赋值给 `Set Video Input` 的 `Video Input` 引脚

## C++ 用法

### 头文件引入

```cpp
#include "PixelStreamingBlueprint.h"
#include "PixelStreamingStreamer.h"
#include "PixelStreamingStreamerVideoInput.h"
#include "PixelStreamingStreamerVideoInputRenderTarget.h"
```

### 基本用法

创建并启动一个 Streamer，使用 RenderTarget 作为输入：

```cpp
// 假设已有 UTextureRenderTarget2D* MyRenderTarget

// 1. 创建视频输入对象
UPixelStreamingStreamerVideoInputRenderTarget* VideoInput = NewObject<UPixelStreamingStreamerVideoInputRenderTarget>();
VideoInput->TargetRenderTarget = MyRenderTarget;

// 2. 创建 Streamer
UPixelStreamingStreamer* Streamer = UPixelStreamingBlueprint::CreateStreamer(TEXT("MyStreamer"));

// 3. 设置输入源
Streamer->SetVideoInput(VideoInput);

// 4. 启动流送（可选配置分辨率和帧率）
Streamer->SetStreamingResolution(1920, 1080);
Streamer->SetStreamingFPS(30);
Streamer->StartStreaming();
```

### 进阶用法

自定义 MediaCapture 视频输入（与 MediaFramework 集成）：

```cpp
UPixelStreamingStreamerVideoInputMediaCapture* MediaCaptureInput = NewObject<UPixelStreamingStreamerVideoInputMediaCapture>();
MediaCaptureInput->MediaCapture = CreateMediaCaptureFromSomewhere(); // 使用 UMediaCapture 对象

Streamer->SetVideoInput(MediaCaptureInput);
```

## Demo 示例

### 最小启动示例（C++）

```cpp
// MyPixelStreamingActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyPixelStreamingActor.generated.h"

UCLASS()
class AMyPixelStreamingActor : public AActor
{
    GENERATED_BODY()
public:
    virtual void BeginPlay() override;
};

// MyPixelStreamingActor.cpp
#include "MyPixelStreamingActor.h"
#include "PixelStreamingBlueprint.h"
#include "PixelStreamingStreamer.h"

void AMyPixelStreamingActor::BeginPlay()
{
    Super::BeginPlay();
    
    // 创建并启动默认 Streamer（使用 BackBuffer 输入）
    UPixelStreamingStreamer* Streamer = UPixelStreamingBlueprint::CreateStreamer(TEXT("DemoStreamer"));
    if (Streamer)
    {
        Streamer->SetSignallingServerURL(TEXT("ws://localhost:8888"));
        Streamer->StartStreaming();
    }
}
```

### 编辑器内创建自定义视频输入资产

1. 在内容浏览器右键菜单选择 "PixelStreaming" → "Streamer Video Input (BackBuffer)" 创建一个资产。
2. 双击该资产，可在细节面板设置相关属性（若有）。
3. 在蓝图或 C++ 中引用该资产作为 Streamer 的输入。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PixelStreamingBlueprint` | 提供蓝图可调用函数（CreateStreamer、StartStreaming 等） |
| `PixelStreaming` | 核心流送运行时（WebRTC 会话管理、编码器） |
| `PixelStreamingInput` | 处理玩家输入（鼠标、键盘、触控）转发到 UE |
| `PixelStreamingServers` | 内置信令服务器的启动与管理 |
| `PixelStreamingHMD` | 支持 VR HMD 流送时头部跟踪的兼容模块 |
| `MediaAssets` | MediaCapture 相关功能（用于自定义视频输入） |
| `UMG` | 支持 UI 交互流送所需控件 |

> 本模块 (`PixelStreamingBlueprintEditor`) 自身依赖 `UnrealEd`、`AssetTools`、`Factory` 等编辑框架模块，这些属于常见依赖，不单独列出。

## 维护状态

### 近期更新

- 2025-09-30 (`4bfe7f55`) 更新基础设施脚本指向新 release 分支
- 2025-09-25 (`1fdac7d5`) 修复：MediaCapture 因队列和祈祷导致进入错误状态
- 2025-09-23 (`30db91bd`) 修复：内部信令服务器创建时因 FTickableGameObject 导致 ensure
- 2025-09-23 (`cc062cea`) 修复：在编辑器命令行设置 streamID 时崩溃
- 2025-08-29 (`32884de4`) 将 RHICreateTexture 替换为 RHICmdList.CreateTexture

### 维护评价

插件发布时间较新（2025年8月底），近期有多个功能性修复和基础架构更新，开发团队保持频繁提交。所有修复针对实际运行时和编辑器问题，说明插件处于积极维护状态。鉴于其属于 Epic 官方插件，代码质量和稳定性有保障，推荐在生产项目中使用。

**注意**：Pixel Streaming 需要 WebRTC 服务端和信令服务器配合，部署复杂度较高，建议仔细阅读官方文档配置网络环境。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming/Source/PixelStreaming/Tests)（部分测试存放于 Engine 主目录下）