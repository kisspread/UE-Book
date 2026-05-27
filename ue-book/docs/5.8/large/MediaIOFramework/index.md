# Media IO Framework

> Media Framework classes to support Professional Media IO used by the Virtual Production industry.

| 属性 | 值 |
|---|---|
| 中文名 | 媒体IO框架 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MediaIOCore` (Runtime), `MediaIOEditor` (Editor), `GPUTextureTransfer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-10-02 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaIOFramework) | |

## 用途

MediaIOFramework 是 UE5 虚拟制片（Virtual Production）工作流的核心底层媒体IO框架。它为专业级的视频输入/输出（I/O）提供了统一的基础设施，主要解决以下问题：

1.  **专业采集卡支持**：为 AJA、Blackmagic Design 等专业视频采集卡提供标准化的硬件抽象层，使引擎能以帧同步、低延迟的方式接收和发送 SDI、HDMI 等信号。
2.  **网络视频标准支持**：支持 SMPTE 2110 等专业网络视频传输协议，适用于广播和大型虚拟制片设施。
3.  **GPU 纹理直传**：通过 `GPUTextureTransfer` 模块，实现 GPU 纹理在媒体设备与引擎渲染管线之间的高效传输，避免不必要的 CPU 拷贝，是实时合成的关键。
4.  **媒体配置管理**：提供媒体配置文件（Media Profile）系统，允许用户保存和加载复杂的硬件配置、色彩空间映射（通过集成的 OpenColorIO 插件）等设置。

该插件不直接面向终端用户创作内容，而是作为 AJA Media、Blackmagic Media 等具体媒体输入输出插件的共同基础，确保它们的行为和接口保持一致。

## 使用场景

-   **LED 虚拟棚**：需要实时将游戏引擎画面输出到 LED 墙幕，并同时从真实摄像机采集视频流进行合成时。
-   **广播与直播**：在体育直播或新闻播报中，需要将 UE5 的实时渲染内容（如图形、数据）以符合广播标准（如 SMPTE 2110）的方式输出到切换台。
-   **后期制作与合成**：在后期流程中，需要将渲染好的视频帧以专业编码格式（如 ProRes）通过硬件卡输出到监视器或录制设备。
-   **自定义媒体硬件集成**：开发团队需要为新的、非标准的媒体硬件（如特种摄影机、医疗影像设备）编写引擎驱动时，可以基于此框架快速开发。

## 蓝图用法

此插件的蓝图暴露 API 集中在 `MediaIOCore` 模块中，主要用于创建和控制媒体捕获（输入）与输出实例。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Media Capture` | 创建一个用于从外部设备（如采集卡）捕获视频流的实例。 | `UMediaIOSubsystem` |
| `Create Media Output` | 创建一个用于将引擎渲染画面发送到外部设备的实例。 | `UMediaIOSubsystem` |
| `Open Media` | 打开媒体捕获或输出设备的连接，开始数据传输。 | `UMediaCapture` / `UMediaOutput` |
| `Close Media` | 关闭连接，停止数据传输。 | `UMediaCapture` / `UMediaOutput` |
| `Get Supported Video Modes` | 查询当前连接设备支持的所有视频格式（分辨率、帧率等）。 | `UMediaCapture` / `UMediaOutput` |
| `Set Media Profile` | 根据预设的媒体配置文件，快速应用一套完整的硬件和色彩配置。 | `UMediaIOSubsystem` |

### 使用示例（蓝图描述）

1.  **捕获外部视频**：
    *   在 BeginPlay 中，使用 `Create Media Capture` 节点创建捕获实例。
    *   调用 `Get Supported Video Modes` 获取可用模式，并选择一个合适的模式（如 1080p60）。
    *   调用 `Open Media` 开始捕获。捕获到的视频流会自动成为引擎内的 `UTexture2D` 资源，可用于材质或 UMG。
2.  **输出到外部设备**：
    *   使用 `Create Media Output` 创建输出实例。
    *   指定一个 `UTextureRenderTarget2D` 作为输出源（例如，一个包含了最终合成画面的渲染目标）。
    *   调用 `Open Media`，该渲染目标的内容将被实时发送到配置的外部设备（如监视器或采集卡输出端口）。

## C++ 用法

### 头文件引入

```cpp
#include "MediaIOCoreModule.h"
#include "MediaCapture.h"
#include "MediaOutput.h"
#include "MediaIOCoreSubsystem.h"
```

### 基本用法

创建一个媒体输出实例并开始输出。此代码展示了最核心的 API 调用流程（参考了 `MediaIOCore` 的测试用例逻辑）。

```cpp
// 获取媒体IO子系统
UMediaIOSubsystem* MediaIOSubsystem = GEngine->GetEngineSubsystem<UMediaIOSubsystem>();

// 创建媒体输出实例
UMediaOutput* MediaOutput = MediaIOSubsystem->CreateMediaOutput(/* 设备配置信息 */);
if (MediaOutput)
{
    // 配置输出参数（例如绑定一个渲染目标）
    // MediaOutput->SetRenderTarget(MyRenderTarget2D);

    // 打开连接，开始输出
    MediaOutput->Open(/* 可选的完成回调 */);

    // ... 在适当的时候关闭
    // MediaOutput->Close();
}
```

**注意**：实际使用中，`CreateMediaOutput` 需要传入一个 `FMediaIOConfiguration` 结构体，该结构体详细指定了设备标识、连接类型、视频模式等。通常这些参数由 `MediaIOEditor` 模块提供的 UI 配置界面生成。

### 进阶用法

结合 `MediaIOEditor` 模块的配置，实现从配置文件中加载媒体设置：

```cpp
// 假设已经通过编辑器UI保存了一个媒体配置文件为 UMediaProfile 资产
UMediaProfile* MediaProfile = LoadObject<UMediaProfile>(nullptr, TEXT("/Game/Config/MyProductionProfile"));
if (MediaProfile)
{
    // 应用整个媒体配置文件，这会自动配置所有相关的捕获和输出
    MediaIOSubsystem->ApplyMediaProfile(MediaProfile);
}
```

## Demo 示例

一个最小化示例，演示如何创建一个简单的视频输出到外部设备。

**MediaOutputDemo.h**
```cpp
// MediaOutputDemo.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MediaOutput.h"
#include "MediaCapture.h"
#include "MediaOutputDemo.generated.h"

UCLASS()
class MYPROJECT_API AMediaOutputDemo : public AActor
{
    GENERATED_BODY()

public:
    AMediaOutputDemo();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    UPROPERTY()
    UMediaOutput* MediaOutput;

    UPROPERTY()
    UMediaCapture* MediaCapture;
};
```

**MediaOutputDemo.cpp**
```cpp
// MediaOutputDemo.cpp
#include "MediaOutputDemo.h"
#include "MediaIOCoreSubsystem.h"
#include "Engine/TextureRenderTarget2D.h"

AMediaOutputDemo::AMediaOutputDemo()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMediaOutputDemo::BeginPlay()
{
    Super::BeginPlay();

    // 获取子系统
    UMediaIOSubsystem* Subsystem = GEngine->GetEngineSubsystem<UMediaIOSubsystem>();
    if (!Subsystem) return;

    // 创建输出实例 (此处假设使用一个默认或已知的设备配置)
    // 在实际项目中，FMediaIOConfiguration应来自设置或配置文件
    FMediaIOConfiguration Config;
    // ... 配置 Config ...

    MediaOutput = Subsystem->CreateMediaOutput(Config);
    if (MediaOutput)
    {
        // 创建一个临时渲染目标用于输出
        UTextureRenderTarget2D* RT = NewObject<UTextureRenderTarget2D>();
        RT->InitAutoFormat(1920, 1080);
        MediaOutput->SetRenderTarget(RT);

        // 创建并打开捕获，开始输出
        MediaCapture = MediaOutput->CreateMediaCapture();
        if (MediaCapture)
        {
            MediaCapture->Open(/* 可选回调 */);
        }
    }
}

void AMediaOutputDemo::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (MediaCapture)
    {
        MediaCapture->Close();
        MediaCapture->ConditionalBeginDestroy();
        MediaCapture = nullptr;
    }
    if (MediaOutput)
    {
        MediaOutput->Close();
        MediaOutput->ConditionalBeginDestroy();
        MediaOutput = nullptr;
    }
    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

使用者需要依赖以下模块来访问此插件的核心功能：

| 模块 | 用途 |
|---|---|
| `MediaIOCore` | 提供媒体IO的核心运行时类，如 `UMediaCapture`、`UMediaOutput`、`UMediaIOSubsystem`。 |
| `GPUTextureTransfer` | 提供GPU纹理高效传输功能，是实时视频输入输出的性能关键。 |
| `VulkanRHI` | `GPUTextureTransfer` 模块依赖，用于底层的 GPU 内存操作。 |

**注意**：`MediaIOEditor` 是编辑器专用模块，用于提供配置UI、资产编辑器等，打包发布时无需依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `36c08694` | Media IO - Populate Media Configuration when using auto for Blackmagic and Aja cards | 增强Blackmagic和AJA采集卡在自动配置模式下的参数填充功能。 |
| 2026-05-23 | `42746f7a` | Media IO: Added additional engine analytics information to various media players and capture and pro | 为多个媒体播放器和捕获组件增加了引擎分析埋点数据。 |
| 2026-05-14 | `a43a62b2` | Media Profile: Changed media texture capture behavior to always preserve aspect ratio of texture eve | 修改媒体纹理捕获行为，确保输出纹理始终保留原始宽高比。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点的编译警告。 |
| 2026-05-12 | `a879de69` | Fix clang warnings when compiling MediaIODeinterlacerTests | 修复编译MediaIO去隔行测试代码时的Clang警告。 |

### 维护评价

-   **维护状态**：**活跃维护中**。根据最近的 Git 记录，插件在 2026 年 5 月仍有持续的功能增强、行为改进和编译修复，表明其是虚拟制作核心基础设施的一部分，受到 Epic 和社区的持续关注。
-   **推荐程度**：**强烈推荐**用于任何涉及专业视频硬件集成的虚拟制片项目。它是连接引擎与专业设备的桥梁，功能稳定且持续更新。
-   **注意事项**：
    1.  该插件默认未启用（`EnabledByDefault: false`），需要在项目设置中手动启用。
    2.  它是一个基础框架插件，通常不直接使用，而是与 `AJAMedia`、`BlackmagicMedia` 等插件配合使用。
    3.  使用硬件功能需要对应的物理设备和驱动支持。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaIOFramework)
-   [GPUTextureTransfer 模块文档](docs/large/MediaIOFramework/GPUTextureTransfer.md)
-   [MediaIOCore 模块文档](docs/large/MediaIOFramework/MediaIOCore.md)
-   [MediaIOEditor 模块文档](docs/large/MediaIOFramework/MediaIOEditor.md)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaIOFramework/Tests)