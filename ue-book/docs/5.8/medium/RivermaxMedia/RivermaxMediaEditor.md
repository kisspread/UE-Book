# Rivermax Media Streaming

> Adding NVIDIA Rivermax capabilities for Media Captures and Media Players（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | Rivermax 流媒体 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RivermaxMedia` (Runtime), `RivermaxMediaEditor` (Runtime), `RivermaxMediaFactory` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-03-30 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Rivermax/RivermaxMedia) | |

## 用途

该插件为虚幻引擎集成了 NVIDIA Rivermax SDK 的功能，使引擎能够通过网络（使用 Rivermax 输入/输出流）播放和捕获媒体内容。它解决了在虚拟制作场景中，需要低延迟、高性能地通过 IP 网络进行视频流传输和接收的问题。插件的核心是提供 Rivermax Media Source（用于接收 IP 视频流）和 Rivermax Media Output（用于通过 IP 发送视频流）。

## 使用场景

- **在虚拟制作现场**：你需要从摄像机或视频服务器通过 IP 接收视频流，并将其用作场景中的实时纹理。
- **生成虚拟摄像头输出**：你需要将引擎的实时渲染画面通过 IP 发送到外部视频设备或显示器。
- **使用 nDisplay 构建大规模 LED 墙**：在集群渲染中，需要为每个节点配置 Rivermax 流来同步视频内容。

## 蓝图用法

该插件的蓝图功能主要围绕创建和使用 `URivermaxMediaSource` 和 `URivermaxMediaOutput` 资产。具体的流媒体操作（如开始/停止播放/捕获）通过标准的 Media Framework 接口（`UMediaPlayer`, `UMediaCapture`）完成，因此没有额外的自定义蓝图节点。核心交互在于配置这些媒体资产的属性。

### 核心资产

| 资产类型 | 说明 |
|---|---|
| `URivermaxMediaSource` | 配置用于通过 Rivermax 网络协议接收视频流的参数（如 IP 地址、端口、流地址等）。 |
| `URivermaxMediaOutput` | 配置用于通过 Rivermax 网络协议发送视频流的参数。 |

### 使用示例（蓝图描述）

1.  在内容浏览器中右键，选择 **Media > Rivermax Media Source** 来创建一个源资产。
2.  在资产的细节面板中配置 **Stream Address**、**Interface Address** 等网络参数。
3.  创建一个 **MediaPlayer** 资产，将其 **Source** 设置为你刚创建的 Rivermax Media Source。
4.  在蓝图中，使用 **Open Source** 节点打开该 MediaPlayer，并将其连接到媒体纹理或 UI 以显示接收的视频流。

## C++ 用法

### 头文件引入

```cpp
#include "RivermaxMediaSource.h"
#include "RivermaxMediaOutput.h"
#include "MediaPlayer.h"
#include "MediaCapture.h"
```

### 基本用法

通过代码创建和配置 Rivermax 媒体源并开始播放。

```cpp
// 创建一个 Rivermax Media Source 资产
URivermaxMediaSource* RivermaxSource = NewObject<URivermaxMediaSource>(GetTransientPackage(), FName("MyRivermaxSource"));
RivermaxSource->StreamAddress = TEXT("224.1.1.1:5000");
RivermaxSource->InterfaceAddress = TEXT("192.168.1.100"); // 使用 Rivermax 网卡的地址

// 创建一个 Media Player
UMediaPlayer* MediaPlayer = NewObject<UMediaPlayer>(GetTransientPackage(), FName("MyMediaPlayer"));

// 打开源并开始播放
if (MediaPlayer->OpenSource(RivermaxSource))
{
    MediaPlayer->Play();
}
```
*示例基于标准 Media Framework 用法，Rivermax 特有属性为 `StreamAddress` 和 `InterfaceAddress`。*

### 进阶用法

配置 Rivermax Media Output 以捕获引擎画面并发送。

```cpp
// 创建一个 Rivermax Media Output
URivermaxMediaOutput* RivermaxOutput = NewObject<URivermaxMediaOutput>(GetTransientPackage(), FName("MyRivermaxOutput"));
RivermaxOutput->StreamAddress = TEXT("224.1.1.2:5001");
RivermaxOutput->InterfaceAddress = TEXT("192.168.1.100");

// 创建一个 Media Capture
UMediaCapture* MediaCapture = NewObject<UMediaCapture>(GetTransientPackage(), FName("MyMediaCapture"));

// 开始捕获到输出
if (MediaCapture->CaptureSceneRenderTarget(RivermaxOutput, 0)) // 0 通常代表整个场景
{
    // 捕获已开始
}
```

## Demo 示例

一个最小化 C++ 示例，演示如何创建一个 Rivermax Media Source 并用于播放。

```cpp
// RivermaxMediaDemo.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "RivermaxMediaDemo.generated.h"

class UMediaPlayer;
class URivermaxMediaSource;

UCLASS()
class ARivermaxMediaDemo : public AActor
{
    GENERATED_BODY()

public:
    ARivermaxMediaDemo();

    virtual void BeginPlay() override;

private:
    UPROPERTY()
    UMediaPlayer* MediaPlayer;

    UPROPERTY()
    URivermaxMediaSource* MediaSource;
};
```

```cpp
// RivermaxMediaDemo.cpp
#include "RivermaxMediaDemo.h"
#include "RivermaxMediaSource.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"

ARivermaxMediaDemo::ARivermaxMediaDemo()
{
    PrimaryActorTick.bCanEverTick = false;
}

void ARivermaxMediaDemo::BeginPlay()
{
    Super::BeginPlay();

    // 创建媒体源
    MediaSource = NewObject<URivermaxMediaSource>(this, FName("DemoRivermaxSource"));
    MediaSource->StreamAddress = TEXT("224.1.1.1:5000");
    MediaSource->InterfaceAddress = TEXT("192.168.1.100"); // 请替换为实际的网络接口地址

    // 创建媒体播放器
    MediaPlayer = NewObject<UMediaPlayer>(this, FName("DemoMediaPlayer"));

    // (可选) 创建 MediaTexture 并设置材质，以便在场景中显示
    // UMediaTexture* MediaTexture = NewObject<UMediaTexture>(this, FName("DemoMediaTexture"));
    // MediaPlayer->SetMediaTexture(MediaTexture);

    // 打开源
    if (MediaPlayer->OpenSource(MediaSource))
    {
        UE_LOG(LogTemp, Log, TEXT("Rivermax media source opened successfully."));
        MediaPlayer->Play();
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open Rivermax media source."));
    }
}
```

## 模块依赖

从插件的功能和头文件（如 `IDisplayClusterModularFeatureMediaInitializer`）推断，它依赖于以下独特模块：

| 模块 | 用途 |
|---|---|
| `RivermaxCore` | 提供底层的 Rivermax SDK 封装和网络接口。 |
| `DisplayCluster` | 用于与 nDisplay 系统集成，支持集群化部署下的媒体流初始化和同步。 |
| `MediaUtils` | 提供媒体框架的通用工具类和接口。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-23 | `42746f7a` | Media IO: Added additional engine analytics information to various media players and capture and pro | 为媒体播放器和捕获添加了引擎分析数据。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量截断为浮点数的警告。 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the ... | 调整了虚拟制作资产的分类。 |
| 2026-05-12 | `c657503b` | [Media] Add missing UAssetDefinition entries for concrete UMediaSource and UMediaOutput subclasses t | 为具体的媒体源和输出子类添加了缺失的资产定义。 |
| 2026-04-28 | `3348026a` | Rivermax: ANC timecode input, input stream base class refactor, and pixel format unification | 添加了 ANC 时间码输入，重构了输入流基类，并统一了像素格式。 |

### 维护评价

Rivermax Media 插件是一个相对较新的功能（创建于 2022 年），标记为**实验性**（IsBetaVersion=true）。根据近期提交记录（截至 2026 年 5 月），它仍然在**积极维护**中，近期进行了功能增强（时间码、分析数据）、代码质量改进（修复警告）以及与其他系统（如虚拟制作资产分类、nDisplay）的集成优化。

**推荐使用**：如果你的虚拟制作工作流需要基于 NVIDIA Rivermax 进行 IP 视频传输，这是一个官方支持的集成方案。但请注意其“实验性”状态，意味着 API 和功能可能会在未来发生变化，且可能需要特定的硬件和网络环境支持。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Rivermax/RivermaxMedia)
- [官方文档]() (无)