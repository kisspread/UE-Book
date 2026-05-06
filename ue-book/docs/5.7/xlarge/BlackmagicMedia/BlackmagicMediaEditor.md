# Blackmagic Media Player

> Implements input and output using Blackmagic Capture cards.

| 属性 | 值 |
|---|---|
| 中文名 | Blackmagic媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `BlackmagicCore` (Runtime), `BlackmagicMedia` (Runtime), `BlackmagicMediaEditor` (Runtime), `BlackmagicMediaFactory` (Runtime), `BlackmagicMediaOutput` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-06-18 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/BlackmagicMedia) | |

## 用途

Blackmagic Media Player 插件提供了与 Blackmagic Design 视频采集/输出设备（如 DeckLink、UltraStudio 系列）的集成能力。它允许 Unreal Engine 5 通过 SDI、HDMI 等专业视频接口接收和发送视频/音频信号，实现：

- **实时视频输入**：从外部设备（摄像机、切换台、播放服务器）采集实时视频流，作为 UE5 中的 Media Source 使用。
- **实时视频输出**：将 UE5 渲染的画面（如虚拟制片、实时合成、图文包装）通过采集卡输出到外部显示设备或广播系统。
- **专业广播级工作流**：支持高帧率、高分辨率（最高 4K 60fps）、时间码、信号检测等广播级特性。

这个插件解决了 UE5 原生不支持专业视频 I/O 硬件的问题，是实现虚拟制片、广电图文包装、现场视频回放等应用场景的基础组件。

## 使用场景

- **虚拟制片**：在 LED 虚拟制片中，需要将 UE5 渲染的画面同步输出到 LED 屏幕控制器（通过 SDI），同时从摄像机采集实时视频用于合成。
- **广电图文包装**：制作体育赛事、新闻节目中的实时图文包装，UE5 输出信号通过采集卡接入切换台。
- **视频回放服务器**：将 UE5 作为视频回放服务器，从硬盘加载视频素材并通过 SDI 输出到演播室系统。
- **实时视频合成**：采集外部摄像机信号，在 UE5 中与 3D 场景混合，再输出给下游设备。
- **系统集成测试**：在自动化测试中模拟视频信号的输入/输出，验证系统的端到端延迟和信号完整性。

## 蓝图用法

本模块（`BlackmagicMediaEditor`）不直接暴露 BlueprintCallable 函数，它主要负责编辑器的资产工厂逻辑。蓝图可用的功能集中在 `BlackmagicMedia` 模块的 Media Source 和 Media Output 类中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open Source` | 打开指定的 Blackmagic Media Source，开始接收视频信号 | `UBlackmagicMediaPlayer` (Media Assets 统一接口) |
| `Close Source` | 关闭当前打开的 Media Source | `UBlackmagicMediaPlayer` |
| `Get Video Track Format` | 获取当前 Media Source 的视频格式（分辨率、帧率等） | `UBlackmagicMediaPlayer` |
| `Set Audio Track Enabled` | 启用/禁用音频轨道 | `UBlackmagicMediaPlayer` |
| `Send Media Output` | 将纹理或渲染目标发送到 Blackmagic 输出设备 | `UBlackmagicMediaOutput` |

**使用示例（蓝图描述）**：

创建一个 Blackmagic Media Source 资产，在关卡蓝图或 GameMode 中获取该资产并调用 `Open Source` 节点，连接到 `Media Player` 组件或 `Media Texture` 上，即可在场景中显示采集的实时视频。

## C++ 用法

### 头文件引入

```cpp
#include "BlackmagicMediaSource.h"
#include "BlackmagicMediaOutput.h"
#include "MediaPlayer.h"
```

### 基本用法

**创建 Blackmagic Media Source 资产**：

```cpp
// 通过工厂类在 Content Browser 中创建
// 或在代码中创建：
UBlackmagicMediaSource* MediaSource = NewObject<UBlackmagicMediaSource>();
MediaSource->DeviceProvider = EMediaIODeviceType::DeckLink;
MediaSource->DeviceIndex = 0;
MediaSource->VideoModeIndex = 0; // 根据设备支持的格式选择
MediaSource->PixelFormat = EBlackmagicMediaSourcePixelFormat::_8BitYUV;
```

**打开并播放 Media Source**:

```cpp
// 路径: Source/BlackmagicMedia/Private/BlackmagicMediaPlayer.cpp
#include "MediaPlayer.h"

UMediaPlayer* MediaPlayer = NewObject<UMediaPlayer>();
// 需先有 MediaSource
UBlackmagicMediaSource* MySource = LoadObject<UBlackmagicMediaSource>(nullptr, TEXT("/Game/MyBlackmagicSource"));
if (MySource && MediaPlayer)
{
    MediaPlayer->OpenSource(MySource);
    // 成功后，MediaTexture 等组件可以开始渲染视频帧
}
```

### 进阶用法

**设置 Blackmagic Media Output 并发送渲染内容**：

```cpp
// 路径: Source/BlackmagicMediaOutput/Private/BlackmagicMediaOutput.cpp
#include "BlackmagicMediaOutput.h"
#include "Engine/TextureRenderTarget2D.h"

UBlackmagicMediaOutput* MediaOutput = NewObject<UBlackmagicMediaOutput>();
MediaOutput->OutputConfiguration.Device.DeviceType = EMediaIODeviceType::DeckLink;
MediaOutput->OutputConfiguration.Device.DeviceIndex = 0;
MediaOutput->OutputConfiguration.OutputType = EMediaIOOutputType::Fill;
MediaOutput->OutputConfiguration.Reference = EMediaIOReferenceType::External;
MediaOutput->VideoConfiguration.Mode = EMediaIOTransportType::SingleLink;

// 设置要输出的 RenderTarget
UTextureRenderTarget2D* RenderTarget = Cast<UTextureRenderTarget2D>(...);
MediaOutput->SetRenderTarget(RenderTarget);

// 开始输出
MediaOutput->SendTexture();
```

**检测设备信号状态**：

```cpp
// 通过 BlackmagicMediaSource 的 OnStateChanged 事件
// 或在 UBlackmagicMediaPlayer 中查询
if (UBlackmagicMediaPlayer* BMMediaPlayer = Cast<UBlackmagicMediaPlayer>(MediaPlayer->GetPlayerFacade()->GetPlayer()))
{
    EMediaState State = BMMediaPlayer->GetState();
    if (State == EMediaState::Playing)
    {
        // 信号已锁定
    }
}
```

## Demo 示例

以下是一个最小可编译的 C++ 示例，演示如何从代码创建 Blackmagic Media Source 并播放：

**MyBlackmagicActor.h**:
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MediaPlayer.h"
#include "BlackmagicMediaSource.h"
#include "MyBlackmagicActor.generated.h"

UCLASS()
class AMyBlackmagicActor : public AActor
{
    GENERATED_BODY()

public:
    AMyBlackmagicActor();

    UFUNCTION(BlueprintCallable, Category = "Blackmagic")
    void StartBlackmagicCapture();

    virtual void Tick(float DeltaTime) override;

private:
    UPROPERTY()
    UMediaPlayer* MediaPlayer;

    UPROPERTY()
    UBlackmagicMediaSource* MediaSource;
};
```

**MyBlackmagicActor.cpp**:
```cpp
#include "MyBlackmagicActor.h"
#include "MediaTexture.h"
#include "Components/MediaTextureComponent.h"

AMyBlackmagicActor::AMyBlackmagicActor()
{
    PrimaryActorTick.bCanEverTick = true;

    // 创建一个 Media Player
    MediaPlayer = CreateDefaultSubobject<UMediaPlayer>(TEXT("MediaPlayer"));
    MediaPlayer->SetLooping(false);

    // 创建 Media Source 并设置参数
    MediaSource = CreateDefaultSubobject<UBlackmagicMediaSource>(TEXT("BlackmagicSource"));
    MediaSource->DeviceProvider = EMediaIODeviceType::DeckLink;
    MediaSource->DeviceIndex = 0;
    MediaSource->VideoModeIndex = 0;  // 使用设备支持的第一个格式
}

void AMyBlackmagicActor::StartBlackmagicCapture()
{
    if (MediaPlayer && MediaSource)
    {
        // 创建 Media Texture 并挂载到组件
        UMediaTexture* MediaTexture = NewObject<UMediaTexture>(this);
        MediaTexture->SetMediaPlayer(MediaPlayer);
        MediaTexture->UpdateResource();

        // 将 MediaTexture 应用到某个 Material 或 UMG 上
        // 此处仅为示例，实际应用中需要保留 MediaTexture 引用
        MediaPlayer->OpenSource(MediaSource);
    }
}

void AMyBlackmagicActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    // 可在此检测播放状态
}
```

**注意**：
- 需要目标平台已安装 Blackmagic Desktop Video SDK 并连接了相应设备。
- `MediaSource->DeviceIndex` 和 `VideoModeIndex` 应根据设备实际情况设置，可通过 `UBlackmagicMediaDevice` 枚举查询可用设备。

## 模块依赖

本模块（`BlackmagicMediaEditor`）的依赖已在其 `Build.cs` 中声明。使用时你的模块需要添加以下依赖：

| 模块 | 用途 |
|---|---|
| `BlackmagicMedia` | 核心媒体播放与媒体源逻辑 |
| `BlackmagicMediaFactory` | 资产工厂基础类（被 Editor 模块重用） |
| `MediaAssets` | UE5 媒体框架资产类型（`UMediaPlayer`, `UMediaTexture` 等） |
| `MediaUtils` | 媒体播放器实现辅助工具 |
| `MediaIOCore` | 媒体 I/O 通用核心（设备配置、传输协议等） |
| `ImageWriteQueue` | 图像写入队列（用于输出帧到内存或文件） |

**注意**：`BlackmagicMediaEditor` 是 Runtime 模块，因为它同时提供编辑器资产工厂和运行时所需的编辑辅助功能。它的依赖主要集中在运行时和媒体框架层，不强制依赖 `UnrealEd`。

## 维护状态

### 近期更新

- 2025-09-23 `9d85dc0e` Blackmagic - Fix Blackmagic source assigning default configuration despite having a valid one.
- 2025-08-21 `8143139e` Add missing #include
- 2025-08-20 `2f0476a2` Add missing include
- 2025-07-22 `d0ba5722` Media Profile: Specified category display order for AJA, Blackmagic, and NDI media sources and outputs.
- 2025-06-18 `60a45027` Disable BlackmagicMedia plugin on Windows Arm64

### 维护评价

Blackmagic Media Player 插件是 UE5 中相对新的插件（2025年6月创建），目前维护状态良好。从 commit 历史来看：

- **更新频率**：自创建以来几乎每个月都有更新，最近一次更新在 2025年9月（约1个月前）。
- **更新内容**：包括 Bug 修复（如配置默认值的修复）、编译修复（缺少 include）、功能增强（Media Profile 支持）等。
- **平台支持**：明确不支持 Windows Arm64，支持 Win64 和 Linux。
- **成熟度**：虽然创建时间短，但更新内容丰富，Bug 修复及时，可以看出是正在积极开发的成熟插件。

**建议**：推荐使用。该插件由 Epic 官方团队维护，覆盖专业视频 I/O 的核心需求，且最近更新活跃。如果你的项目需要 Blackmagic 设备集成，这是 UE5 中的标准方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/BlackmagicMedia)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/media-framework-in-unreal-engine/)（通用媒体框架文档，包含 Blackmagic 部分）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/BlackmagicMedia/Source/BlackmagicMedia/Private/Tests)（若有）