# Pixel Streaming Player

> Support for receiving a pixel streaming stream and displaying it in game.

| 属性 | 值 |
|---|---|
| 中文名 | 像素流播放器 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产工厂） |
| 模块 | `PixelStreamingPlayer` (Runtime), `PixelStreamingPlayerEditor` (Editor) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2023-01-25 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PixelStreamingPlayer) | |

## 用途

此插件使一个 UE 应用能够作为“客户端”或“播放器”，接收并实时显示另一个 UE 应用或服务通过 Pixel Streaming 技术发送的视频流。它解决了在同一个 UE 项目中集成来自另一个源的实时视频画面的需求，可以用于多人协作、监控、测试或演示等场景。

## 使用场景

- 你需要在你的游戏或应用 UI 中，实时显示另一个独立运行的 UE 项目的画面。
- 你正在开发一个远程控制或远程桌面应用，需要接收并渲染远端的 UE 渲染流。
- 你想在开发或测试中，同时观察主程序和另一个实例的渲染输出。

## 蓝图用法

此插件的公开蓝图接口较少，其主要功能集中在底层流处理和纹理创建。从源码分析，主要的可用节点与创建用于显示流的纹理资产有关。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FactoryCreateNew` | 创建一个新的 `MediaTexture` 资产，用于接收和显示 Pixel Streaming 流 | `UPixelStreamingMediaTextureFactory` |

### 使用示例（蓝图描述）

1.  在编辑器中，可以通过“创建资产”菜单，选择由 `PixelStreamingMediaTextureFactory` 提供的选项，来创建一个新的、专门用于 Pixel Streaming 播放的 `MediaTexture` 资产。
2.  创建后，将此 `MediaTexture` 拖拽到场景中的 UI 元素（如 `Image` 控件）或 `Media Player` 组件中。
3.  通过 C++ 或蓝图逻辑配置相应的 Pixel Streaming 会话信息，将流连接到这个 `MediaTexture` 上进行播放。

## C++ 用法

### 头文件引入

```cpp
#include "PixelStreamingMediaTextureFactory.h"
```

### 基本用法

从 `UPixelStreamingMediaTextureFactory` 的定义可以看出，它继承自 `UFactory`，主要用于在编辑器中创建特定资产。

```cpp
// 伪代码示例，说明工厂类的用途
// 实际使用通常在编辑器上下文中，由“创建资产”菜单触发
UObject* NewAsset = PixelStreamingMediaTextureFactory->FactoryCreateNew(
    UMediaTexture::StaticClass(),
    OuterPackage,
    AssetName,
    RF_Public | RF_Standalone,
    nullptr,
    GWarn
);
UMediaTexture* StreamingTexture = Cast<UMediaTexture>(NewAsset);
// StreamingTexture 现在可以被配置为接收 Pixel Streaming 流
```
*（来源：分析 `Private/PixelStreamingMediaTextureFactory.h`）*

### 进阶用法

集成到 Pixel Streaming 工作流中，需要结合 `PixelStreaming` 插件的 API。典型流程包括：初始化 Pixel Streaming 子系统、创建或获取流接收器、将接收的帧数据写入由工厂创建的 `MediaTexture` 中。

## Demo 示例

一个最小示例，展示如何在运行时代码中使用 `PixelStreamingMediaTextureFactory` 来创建纹理资产。

**PixelStreamingDemoActor.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "PixelStreamingDemoActor.generated.h"

class UMediaTexture;

UCLASS()
class APixelStreamingDemoActor : public AActor
{
    GENERATED_BODY()

public:
    APixelStreamingDemoActor();

    UPROPERTY(BlueprintReadOnly, Category = "Pixel Streaming")
    UMediaTexture* StreamingTexture;

    UFUNCTION(BlueprintCallable, Category = "Pixel Streaming")
    void CreateStreamingTexture();
};
```

**PixelStreamingDemoActor.cpp**
```cpp
#include "PixelStreamingDemoActor.h"
#include "PixelStreamingMediaTextureFactory.h"
#include "MediaTexture.h"

APixelStreamingDemoActor::APixelStreamingDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void APixelStreamingDemoActor::CreateStreamingTexture()
{
    // 获取工厂实例
    UPixelStreamingMediaTextureFactory* Factory = NewObject<UPixelStreamingMediaTextureFactory>();

    // 创建纹理资产（这里为示例，实际创建需要有效的 Outer 和 Name）
    UObject* NewObj = Factory->FactoryCreateNew(
        UMediaTexture::StaticClass(),
        this, // 使用Actor作为外部对象
        FName("StreamingTexture"),
        RF_NoFlags,
        nullptr,
        GWarn
    );

    StreamingTexture = Cast<UMediaTexture>(NewObj);
    if (StreamingTexture)
    {
        UE_LOG(LogTemp, Log, TEXT("Successfully created a MediaTexture for Pixel Streaming."));
        // 接下来需要配置 StreamingTexture 以连接到具体的流会话
    }
}
```

## 模块依赖

从 `.uplugin` 的 `Plugins` 部分可知，此插件依赖 `PixelStreaming` 插件。因此，使用本插件的模块通常也需要依赖 `PixelStreaming` 相关模块。

| 模块 | 用途 |
|---|---|
| `PixelStreaming` | 提供底层的像素流接收、解码和会话管理功能 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF 格式。 |
| 2026-03-15 | `2caebd20` | Add more missing includes and forward declarations for various rendering headers to files that have | 为多个渲染头文件添加缺失的包含和前向声明。 |
| 2025-08-26 | `0a8b2cd9` | Deprecating the functions RHICreateTextureReference and RHIUpdateTextureReference to force callers t | 弃用 RHICreateTextureReference 和 RHIUpdateTextureReference 函数，强制调用方更新。 |
| 2025-04-10 | `ea97db60` | Movie Render Queue: High-res tiling support for paging scene view state persistent data to system m | 电影渲染队列：为分页场景视图状态持久化数据到系统内存添加高分辨率平铺支持。 |
| 2024-09-04 | `ffe80807` | [PixelStreaming] Fix: Undeprecate as VCam is still depending on it |  [PixelStreaming] 修复：取消弃用，因为 VCam 仍在依赖此功能。 |

### 维护评价

该插件创建于 2023 年初，至今约 3 年。从最近的提交记录看，更新主要是代码维护（如头文件修复、日志迁移）和兼容性适配（跟随引擎渲染 API 变化），**没有新的功能添加**。最后一次实质性功能相关更新（关于弃用 API 的调整）在 2024 年 9 月。

**总结**：该插件处于**实验性（Beta）** 状态且默认禁用。维护活动较低，主要集中在保持代码与引擎最新版本的兼容性。它提供了一个基础的像素流接收和显示能力，但功能可能不完整或存在限制。**建议**：仅在有明确的实验或原型需求时使用，并注意其 Beta 状态和潜在的不稳定性。不建议在关键生产项目中依赖此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PixelStreamingPlayer)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PixelStreamingPlayer/Tests) *(路径基于常见结构推断)*