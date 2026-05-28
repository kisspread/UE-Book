# Pixel Streaming

> Streaming of Unreal Engine audio and rendering to WebRTC-compatible media players such as a web browsers.

| 属性 | 值 |
|---|---|
| 中文名 | 像素流送 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `PixelStreaming` (Runtime), `PixelStreamingBlueprint` (Runtime), `PixelStreamingBlueprintEditor` (Runtime), `PixelStreamingEditor` (Runtime), `PixelStreamingHMD` (Runtime), `PixelStreamingInput` (Runtime), `PixelStreamingServers` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-31 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming) | |

## 用途

该插件实现了 Unreal Engine 的像素流送技术，核心功能是将引擎渲染的视频帧和音频流通过 **WebRTC** 协议实时传输到兼容的客户端（主要是现代网络浏览器）。它解决了远程访问高性能 UE 应用（如 3D 可视化、建筑漫游、云游戏）而无需在客户端部署庞大引擎或高性能硬件的需求。用户只需通过一个网页链接即可在任何设备上获得接近原生的交互体验。

## 使用场景

- **云游戏/远程体验**：将运行在云端服务器的 UE 游戏画面实时推流到玩家的浏览器中，实现“点击即玩”。
- **建筑/设计可视化**：设计师和客户可以通过浏览器审阅、交互式探索复杂的 3D 建筑模型或工业设计。
- **虚拟展览/培训**：在博物馆、展厅或企业培训中，提供基于网页的沉浸式 3D 交互内容。
- **无需安装的演示**：为 UE 项目制作可在任何网络浏览器中运行的实时演示 demo，便于分享和营销。

## 蓝图用法

本插件提供了丰富的蓝图接口，用于在运行时创建和控制流送。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Pixel Streaming Streamer` | 创建一个新的像素流送实例。 | `UPixelStreamingSubsystem` |
| `Start Streaming` | 启动已创建的流送器的流送。 | `UPixelStreamer` |
| `Stop Streaming` | 停止流送。 | `UPixelStreamer` |
| `Set Video Input` | 为流送器设置视频输入源（例如后缓冲区、渲染目标、媒体捕获）。 | `UPixelStreamer` |
| `Set Audio Input` | 为流送器设置音频输入源。 | `UPixelStreamer` |
| `Send Custom Message` | 通过数据通道向所有连接的观看者发送自定义消息。 | `UPixelStreamer` |

### 使用示例（蓝图描述）

1.  **基本流送**：
    *   在你的 GameMode 或 Actor 蓝图中，使用 `Create Pixel Streaming Streamer` 节点创建一个流送器对象。
    *   将其 `Video Input` 设置为 `Pixel Streaming Video Input Back Buffer`（捕获最终渲染画面）。
    *   调用 `Start Streaming` 节点。引擎启动后，控制台日志会输出一个用于访问的 URL。
2.  **发送自定义数据**：
    *   持有对流送器对象的引用。
    *   当需要发送数据时，调用 `Send Custom Message` 节点，输入消息类型字符串和 JSON 格式的负载数据。
    *   前端 JavaScript 代码可以通过相应的事件监听器接收到这些数据。

## C++ 用法

### 头文件引入

```cpp
#include "PixelStreamingInputComponent.h"
#include "PixelStreamingPlugin.h"
```

### 基本用法

此示例展示如何在 C++ 中创建流送器并设置视频输入。

```cpp
// 来源：引擎内部使用模式推断
#include "PixelStreamingSubsystem.h"
#include "PixelStreamingVideoInputBackBuffer.h"

// 获取子系统
UPixelStreamingSubsystem* PSSubsystem = GEngine->GetEngineSubsystem<UPixelStreamingSubsystem>();
if (PSSubsystem)
{
    // 创建一个流送器
    UPixelStreamer* Streamer = PSSubsystem->CreateStreamer(TEXT("MyCStreamer"));
    if (Streamer)
    {
        // 设置视频输入为后缓冲区（最常用）
        Streamer->SetVideoInput(UPixelStreamingVideoInputBackBuffer::Create());
        // 启动流送
        Streamer->StartStreaming();
    }
}
```

### 进阶用法

实现自定义视频输入源。你需要继承 `UPixelStreamingVideoInput` 并重写 `GetFrame` 方法。

```cpp
// 来源：参考 UPixelStreamingVideoInputRenderTarget 等实现
#include "PixelStreamingVideoInput.h"

UCLASS()
class UMyCustomVideoInput : public UPixelStreamingVideoInput
{
    GENERATED_BODY()

public:
    // 提供一帧要编码的图像数据
    virtual FPixelStreamingFrame GetFrame() override
    {
        FPixelStreamingFrame Frame;
        // ... 从你的自定义渲染目标、纹理等获取图像数据并填充到 Frame ...
        // 通常涉及 RHI 锁定和纹理拷贝操作。
        return Frame;
    }
};
```

## Demo 示例

一个最小可运行的 C++ 示例，创建一个仅使用后缓冲区输入的像素流送器。

```cpp
// MyPixelStreamingActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyPixelStreamingActor.generated.h"

class UPixelStreamer;

UCLASS()
class AMyPixelStreamingActor : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;

private:
    UPROPERTY()
    UPixelStreamer* MyStreamer = nullptr;
};
```

```cpp
// MyPixelStreamingActor.cpp
#include "MyPixelStreamingActor.h"
#include "PixelStreamingSubsystem.h"
#include "PixelStreamingVideoInputBackBuffer.h"

void AMyPixelStreamingActor::BeginPlay()
{
    Super::BeginPlay();

    if (UPixelStreamingSubsystem* PS = GEngine->GetEngineSubsystem<UPixelStreamingSubsystem>())
    {
        MyStreamer = PS->CreateStreamer(TEXT("MinimalDemo"));
        if (MyStreamer)
        {
            MyStreamer->SetVideoInput(UPixelStreamingVideoInputBackBuffer::Create());
            MyStreamer->StartStreaming();
            UE_LOG(LogTemp, Log, TEXT("Pixel Streaming started. Check logs for viewer URL."));
        }
    }
}
```

## 模块依赖

要使用此插件的功能，你的模块需要链接以下特定模块：

| 模块 | 用途 |
|---|---|
| `PixelStreaming` | 核心流送、编解码、WebRTC 交互功能。 |
| `PixelStreamingInput` | 处理从浏览器到引擎的输入事件转发。 |
| `PixelStreamingBlueprint` | 提供蓝图可调用的流送接口。 |

**注意**：`PixelStreamingServers` 模块提供了独立的信令服务器和 Web 服务器实现，通常由插件内部或独立部署使用，应用程序模块一般不需要直接依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `c1dab3e1` | [PixelStreaming2] Fix: Input handler obtaining default target window from wrong method | 修复输入处理器获取默认目标窗口的方法错误。 |
| 2026-05-14 | `876d5541` | Fix the crash with PIE/Simulate | 修复在 PIE 和模拟模式下的崩溃问题。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下，双精度常量截断为浮点数时产生的警告。 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 虚拟制片：将多个 VP 资产移动到新的资产类别，并完成迁移。 |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 FJsonObject 以同时支持 FString 和 UE::FSharedString。 |

### 维护评价

- **活跃维护**：从 git 历史看，该插件在最近几个月内持续获得 bug 修复、兼容性改进和功能重构，维护非常活跃。
- **核心地位**：作为 Epic 官方提供的、用于云游戏和远程访问的关键技术，其代码质量和长期支持有保障。
- **推荐使用**：对于需要将 UE 应用流式传输到浏览器的项目，**强烈推荐使用**。虽然默认未启用，但设置和集成相对成熟，社区资源丰富。
- **已知限制**：性能高度依赖服务器硬件、编码器和网络带宽。对实时性要求极高的输入（如竞技 FPS）可能存在感知延迟。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming/Tests)

---

# Pixel Streaming Blueprint Editor 模块

| 属性 | 值 |
|---|---|
| 中文名 | 像素流送蓝图编辑器支持 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 (随主插件启用) |
| 包含内容 | ❌ 无 |
| 模块 | `PixelStreamingBlueprintEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-31 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming/Source/PixelStreamingBlueprintEditor) | |

## 用途

本模块是 `PixelStreamingBlueprint` 模块的编辑器扩展，**仅在编辑器环境下运行**。其主要职责是为像素流送相关的蓝图可编辑资产（主要是各种“视频输入”配置资产）在编辑器中提供完整的集成支持，包括资产的创建、显示、分类和外观定制。

## 使用场景

- **在内容浏览器中创建资产**：允许用户通过“添加”菜单直接创建不同类型（后缓冲、渲染目标、媒体捕获）的像素流送视频输入配置资产。
- **资产识别与管理**：在内容浏览器和编辑器列表中，这些自定义资产拥有独特的名称、颜色和分类，便于用户识别和管理。

## 蓝图用法

本模块不直接提供蓝图节点，其功能主要体现在编辑器的用户界面和资产操作上。

### 核心资产类型

| 资产类 | 说明 | 创建方式 |
|---|---|---|
| `Pixel Streaming Video Input Back Buffer` | 配置视频输入源为引擎后缓冲区（即主视口渲染结果）。 | 在内容浏览器中右键 -> `Pixel Streaming` -> `Video Input Back Buffer` |
| `Pixel Streaming Video Input Render Target` | 配置视频输入源为特定的 UTextureRenderTarget2D。 | 在内容浏览器中右键 -> `Pixel Streaming` -> `Video Input Render Target` |
| `Pixel Streaming Video Input Media Capture` | 配置视频输入源为媒体捕获设备。 | 在内容浏览器中右键 -> `Pixel Streaming` -> `Video Input Media Capture` |

### 使用示例（蓝图描述）

1.  在内容浏览器的空白区域**右键**。
2.  在弹出菜单中找到 `Create Advanced Asset` -> `Pixel Streaming` -> `Video Input` 分类。
3.  选择你需要的类型（如 `Video Input Render Target`）。
4.  输入资产名称，即可创建一个新的配置资产。双击该资产可以打开其编辑细节面板。

## C++ 用法

本模块的 C++ 代码主要为编辑器提供服务，应用程序代码通常不会直接调用。其核心在于实现了 `UAssetDefinition` 和 `UFactory` 接口。

### 头文件引入

应用程序代码无需引入此模块的头文件。

### 基本用法（模块内部）

模块通过注册以下类来集成编辑器：

```cpp
// 1. 资产定义 - 控制资产在编辑器中的显示
UCLASS()
class UAssetDefinition_StreamerVideoInput : public UAssetDefinitionDefault
{
    GENERATED_BODY()
    // 重写 GetAssetDisplayName, GetAssetClass, GetAssetColor 等方法，为视频输入资产提供编辑器 UI 表示。
};

// 2. 工厂类 - 控制资产的创建
// 例如，针对后缓冲输入的工厂：
UCLASS()
class UPixelStreamingStreamerVideoInputBackBufferFactory : public UFactory
{
    GENERATED_UCLASS_BODY()
    // 重写 FactoryCreateNew 方法，在用户请求创建该类型资产时，实例化对应的 UObject。
};
```

## Demo 示例

本模块为编辑器扩展，没有独立的运行时示例。其效果体现在通过上述“蓝图用法”步骤创建资产的过程。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PixelStreamingBlueprint` | 提供要编辑的 `UPixelStreamingVideoInput` 资产基类。 |
| `UnrealEd` | 核心编辑器框架，提供 `UFactory`、`UAssetDefinition` 等基类。 |
| `Core` | 基础核心库。 |

## 维护状态

### 近期更新

最近更新与主 PixelStreaming 插件同步，见上方主插件的更新日志。

### 维护评价

- **稳定维护**：作为编辑器支持模块，随主插件一同维护，更新频率与主插件一致。
- **依赖关系**：依赖于主 `PixelStreaming` 和 `PixelStreamingBlueprint` 模块，其生命周期与这些核心模块绑定。
- **推荐使用**：当你的项目启用 PixelStreaming 插件并需要在编辑器中创建和管理视频输入配置资产时，此模块会自动加载，无需额外操作。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming/Source/PixelStreamingBlueprintEditor)