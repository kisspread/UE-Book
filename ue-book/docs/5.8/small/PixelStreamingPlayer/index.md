# Pixel Streaming Player

> Support for receiving a pixel streaming stream and displaying it in game.

| 属性 | 值 |
|---|---|
| 中文名 | 像素流播放器 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有 |
| 模块 | `PixelStreamingPlayer` (Runtime), `PixelStreamingPlayerEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-01-25 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PixelStreamingPlayer) | |

## 用途

本插件解决了在游戏客户端（UE 应用）内部**接收并渲染**来自 Pixel Streaming 服务器视频流的问题。它将客户端角色从“被推流的服务器”转变为“主动拉流的播放器”，允许游戏进程作为接收端，显示来自远程服务器或编码器的实时视频画面，适用于远程监控、客户端应用或需要嵌入远程渲染内容的场景。

## 使用场景

*   你需要在一个 UE 构建的游戏客户端或应用程序内，实时接收并显示来自另一个 Pixel Streaming 发送端（如云端渲染的 UE 实例）的视频画面。
*   你正在开发一个“瘦客户端”应用，其主要功能是播放来自强大云端服务器渲染的交互式内容。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Video Source` | 创建一个用于接收 Pixel Streaming 流的视频源对象。 | `UPixelStreamingVideoSource` |
| `Start Streaming` | 指定接收端信令服务器地址，开始连接并接收视频流。 | `UPixelStreamingVideoSource` |
| `Stop Streaming` | 停止接收视频流并断开连接。 | `UPixelStreamingVideoSource` |
| `Get State` | 获取当前视频流的连接与播放状态。 | `UPixelStreamingVideoSource` |

### 使用示例（蓝图描述）

1.  **初始化**：在 Actor 或 Widget 的初始化事件中，使用 `Create Video Source` 节点创建一个 `UPixelStreamingVideoSource` 对象引用。
2.  **开始播放**：当需要连接时，调用 `Start Streaming` 节点，将信令服务器的 URL（如 `ws://localhost:8888`）传入。
3.  **显示画面**：将 `Video Source` 对象的 `VideoSource` 属性绑定到 Slate 的 `SVideo` 控件或 UMG 的 `MediaPlayer` 资产，以渲染接收到的画面。
4.  **停止播放**：在需要断开时，调用 `Stop Streaming` 节点。
5.  **状态监控**：可随时调用 `Get State` 节点查询连接状态。

## C++ 用法

### 头文件引入

```cpp
#include "PixelStreamingVideoSource.h"
```

### 基本用法

```cpp
// 创建视频源实例
UPixelStreamingVideoSource* VideoSource = NewObject<UPixelStreamingVideoSource>();

// 开始接收流（需要提供信令服务器地址）
VideoSource->StartStreaming(TEXT("ws://localhost:8888"));

// 停止接收流
VideoSource->StopStreaming();
```
*示例逻辑基于插件公开的 BlueprintCallable API。*

### 进阶用法

视频源的状态可以通过 `GetState()` 方法轮询，或考虑注册到其可能提供的状态变化回调中，以实现更精细的连接管理逻辑（例如自动重连）。

## Demo 示例

以下是一个在 Actor 组件中管理视频源生命周期的最小示例：

**PixelStreamingPlayerDemoComponent.h**
```cpp
#pragma once
#include "Components/ActorComponent.h"
#include "PixelStreamingVideoSource.h"
#include "PixelStreamingPlayerDemoComponent.generated.h"

UCLASS(ClassGroup=(PixelStreaming), meta=(BlueprintSpawnableComponent))
class UPixelStreamingPlayerDemoComponent : public UActorComponent
{
    GENERATED_BODY()
public:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UPROPERTY(BlueprintReadOnly, Category = "PixelStreaming")
    UPixelStreamingVideoSource* VideoSource;
};
```

**PixelStreamingPlayerDemoComponent.cpp**
```cpp
#include "PixelStreamingPlayerDemoComponent.h"

void UPixelStreamingPlayerDemoComponent::BeginPlay()
{
    Super::BeginPlay();
    VideoSource = NewObject<UPixelStreamingVideoSource>(this);
    // 在实际项目中，信令服务器地址应可配置
    VideoSource->StartStreaming(TEXT("ws://your-signaling-server:port"));
}

void UPixelStreamingPlayerDemoComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (VideoSource)
    {
        VideoSource->StopStreaming();
    }
    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。使用者需依赖 `PixelStreaming` 插件。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移至新格式，属于引擎代码现代化。 |
| 2026-03-15 | `2caebd20` | Add more missing includes and forward declarations for various rendering headers to files that have | 补充渲染相关的头文件包含，解决编译依赖问题。 |
| 2025-08-26 | `0a8b2cd9` | Deprecating the functions RHICreateTextureReference and RHIUpdateTextureReference to force callers t | 废弃旧纹理引用API，推动使用新接口。 |
| 2025-04-10 | `ea97db60` | Movie Render Queue: High-res tiling support for paging scene view state persistent data to system s | 电影渲染队列高分辨率分页支持，与本插件无直接功能关联。 |
| 2024-09-04 | `ffe80807` | [PixelStreaming] Fix: Undeprecate as VCam is still depending on it | 取消某些函数的废弃标记，以满足虚拟相机(VCam)插件的依赖。 |

### 维护评价

该插件创建于 2023 年初，是一个较新的实验性(Beta)插件。从 Git 记录看，近期更新主要集中在底层代码现代化（日志、头文件、废弃API处理）和与其它插件（如VCam）的兼容性修复上，而非其核心功能的增强。作为 `EnabledByDefault: false` 的实验性插件，其功能可能尚未完全稳定。目前仍在维护中，但**建议仅在明确需要“游戏作为播放器”场景且愿意承担实验性API风险时使用**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PixelStreamingPlayer)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)