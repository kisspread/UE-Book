# Blackmagic Media Player

> Implements input and output using Blackmagic Capture cards.

| 属性 | 值 |
|---|---|
| 中文名 | 黑魔法媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `BlackmagicCore` (Runtime), `BlackmagicMedia` (Runtime), `BlackmagicMediaEditor` (Runtime), `BlackmagicMediaFactory` (Runtime), `BlackmagicMediaOutput` (Runtime), `BlackmagicSDK` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-09-04 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/BlackmagicMedia) | |

## 用途

BlackmagicMedia 插件是 Epic Games 为集成 Blackmagic Design 公司的 PCIe 采集卡/输出卡而开发的 Media Framework 实现。其核心价值在于**将专业级广播设备与 Unreal Engine 的渲染管线进行硬件级同步**。它不仅仅是一个简单的视频捕获工具，而是为**虚拟制片（Virtual Production）** 和 **nDisplay 集群渲染** 等高级场景提供的关键底层支撑。

它解决了以下几个核心问题：
1.  **硬件同步（Genlock）**：通过 `UBlackmagicCustomTimeStep`，允许引擎的游戏循环和渲染节奏与外部视频信号源（如同步锁相发生器）精确同步，避免了画面撕裂和帧不一致。
2.  **时间码（Timecode）同步**：通过 `UBlackmagicTimecodeProvider`，可以直接从 Blackmagic 硬件输入的视频流中读取嵌入的时间码（LTC 或 VITC），并将其提供给引擎的时间同步系统，确保多个设备（如多台渲染机器、LED 墙、摄影机）的时间码完全一致。
3.  **高质量实时 I/O**：作为 Media Framework 的 `IMediaPlayer` 实现，提供了通过 Blackmagic 卡进行高分辨率、高比特率（如 10-bit YUV）的视频输入和输出的通道，支持 HDR 元数据传递。
4.  **与 MediaProfile 深度集成**：设备配置（连接、格式、时间码）可以保存为 Media Profile，方便在不同项目或场景间快速切换专业 I/O 设置。

简单来说，如果您的项目需要与 Blackmagic 硬件进行专业、精确的音频/视频交互，尤其是涉及多设备时间同步，那么这个插件就是必需的。

## 使用场景

-   **虚拟制片（Virtual Production）**：在 LED Volume（LED 墙）设置中，将 Unreal Engine 的实时渲染输出通过 Blackmagic 输出卡发送到 LED 控制器，同时从 Blackmagic 输入卡捕获真实摄影机的画面进行合成。需要引擎与 LED 控制系统严格同步。
-   **广播与直播**：将 Unreal Engine 的渲染画面（如虚拟演播室、天气图、体育数据可视化）通过 Blackmagic 输出卡接入专业的广播切换台或编码器。
-   **nDisplay 多机渲染**：在由多台 PC 驱动的大型显示系统中，使用 Blackmagic 的 Genlock 功能确保所有渲染节点同步刷新，避免画面错位。
-   **高质量视频采集与分析**：需要从专业摄影机或医疗/工业设备中采集高码率、高色彩深度的视频流进行实时处理或记录。

## 蓝图用法

此插件的主要蓝图接口集中在配置相关的资产（Media Source, Timecode Provider, Custom Time Step）上，而非运行时调用节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Media Option` | 根据传入的 Key（如 `DeviceIndex`, `CaptureVideo`）获取媒体源的配置值。 | `UBlackmagicMediaSource` |
| `Validate` | 验证当前媒体源的配置是否有效（设备是否存在，格式是否支持）。 | `UBlackmagicMediaSource` |
| `Fetch Timecode` | 手动从关联的 Blackmagic 设备获取当前时间码。通常由时间同步系统内部调用。 | `UBlackmagicTimecodeProvider` |
| `Initialize` | 初始化自定义时间步长，开始与硬件同步信号连接。 | `UBlackmagicCustomTimeStep` |
| `Shutdown` | 关闭连接并释放硬件资源。 | `UBlackmagicCustomTimeStep` |

### 使用示例（蓝图描述）

1.  **创建媒体源资产**：
    -   在内容浏览器右键，选择 `媒体` -> `Blackmagic 媒体源`。
    -   在该资产的详情面板中，通过下拉菜单选择 `设备`、`端口` 和 `视频模式`（如 1080p 30fps）。
    -   勾选 `捕获视频` 和 `捕获音频`。
    -   （可选）设置 `时间码格式` 为 `自动` 或 `LTC`。
    -   将此资产拖拽到场景中的 `媒体播放器` 组件或 `媒体纹理` 资产上作为源。

2.  **配置引擎同步（蓝图设置）**：
    -   打开 `项目设置` -> `引擎` -> `通用设置`。
    -   在 `自定义时间步长` 类中，选择 `Blackmagic SDI Input`。
    -   在 `时间码提供者` 类中，选择 `Blackmagic SDI Input`。
    -   点击下方出现的“创建”按钮来实例化它们，并分别配置其 `媒体配置` 属性，指向你的 Blackmagic 设备。

3.  **运行时监控**：
    -   可以使用 `Get Synchronization State` 节点来查询 `UBlackmagicCustomTimeStep` 或 `UBlackmagicTimecodeProvider` 的当前同步状态（如 `同步`、`未同步`、`错误`）。
    -   使用 `Is Hardware Ready` 节点（来自 `UBlackmagicMediaSource` 对应的播放器）检查硬件是否就绪。

## C++ 用法

核心用法是通过 Media Framework 创建和使用 Blackmagic 播放器，并可能集成自定义时间步长和时间码。

### 头文件引入

```cpp
#include "BlackmagicMediaModule.h"
#include "BlackmagicMediaSource.h"
#include "BlackmagicCustomTimeStep.h"
#include "BlackmagicTimecodeProvider.h"
```

### 基本用法：创建和使用媒体播放器

此示例展示如何通过 C++ 代码创建一个使用 Blackmagic 输入的媒体播放器。

```cpp
// 来源于: 基于 IBlackmagicMediaModule.h 和 FBlackmagicMediaPlayer 推断的用法
#include "BlackmagicMediaModule.h"
#include "IMediaEventSink.h"

void FMyMediaManager::StartCapture()
{
    // 1. 获取 BlackmagicMedia 模块接口
    IBlackmagicMediaModule& BlackmagicModule = IBlackmagicMediaModule::Get();

    // 2. 检查硬件和模块是否可用
    if (!BlackmagicModule.IsInitialized() || !BlackmagicModule.CanBeUsed())
    {
        UE_LOG(LogTemp, Warning, TEXT("Blackmagic module or hardware not available."));
        return;
    }

    // 3. 创建媒体源 (UObject, 需要 Outer)
    UBlackmagicMediaSource* MediaSource = NewObject<UBlackmagicMediaSource>(GetTransientPackage());
    // 通常从资产加载更常见，但这里演示动态创建
    MediaSource->MediaConfiguration = /* 填充你的设备配置 */;
    MediaSource->bCaptureVideo = true;
    MediaSource->bCaptureAudio = true;

    // 4. 创建事件接收器（需实现 IMediaEventSink）
    // TSharedPtr<FMyEventSink> EventSink = MakeShared<FMyEventSink>();

    // 5. 创建播放器实例
    TSharedPtr<IMediaPlayer, ESPMode::ThreadSafe> Player = BlackmagicModule.CreatePlayer(*EventSink);
    if (Player.IsValid())
    {
        // 6. 打开媒体源
        FString Url = MediaSource->GetUrl();
        bool bOpened = Player->Open(Url, MediaSource);
        if (bOpened)
        {
            UE_LOG(LogTemp, Log, TEXT("Blackmagic media player opened successfully."));
            // 将 Player 保存起来，在 Tick 中调用 Player->TickFetch 和 Player->TickInput
        }
    }
}
```

### 进阶用法：集成自定义时间步长

此示例展示如何在引擎初始化时设置 Blackmagic 自定义时间步长。

```cpp
// 来源于: BlackmagicCustomTimeStep.h 接口
#include "BlackmagicCustomTimeStep.h"
#include "Engine/Engine.h"

bool FMyGameModule::SetupBlackmagicTimeStep()
{
    // 1. 创建自定义时间步长对象
    UBlackmagicCustomTimeStep* CustomTimeStep = NewObject<UBlackmagicCustomTimeStep>();

    // 2. 配置硬件连接（例如，用于 Genlock 的参考信号输入）
    CustomTimeStep->MediaConfiguration = /* 填充你的同步信号源设备配置 */;
    CustomTimeStep->bEnableOverrunDetection = true;

    // 3. 初始化并应用到引擎
    if (CustomTimeStep->Initialize(GEngine))
    {
        GEngine->SetCustomTimeStep(CustomTimeStep);
        UE_LOG(LogTemp, Log, TEXT("Blackmagic Custom TimeStep applied to Engine."));
        return true;
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Failed to initialize Blackmagic Custom TimeStep."));
        return false;
    }
}
```

## Demo 示例

一个最小化的，可以编译并初始化 Blackmagic 自定义时间步长的类。

```cpp
// MyBlackmagicTimeStepDemo.h
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FMyBlackmagicTimeStepDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    UPROPERTY() // UPROPERTY 防止被GC，实际使用中更常放在 GameInstance 或类似长生命周期对象中
    class UBlackmagicCustomTimeStep* CustomTimeStep = nullptr;
};

// MyBlackmagicTimeStepDemo.cpp
#include "MyBlackmagicTimeStepDemo.h"
#include "BlackmagicCustomTimeStep.h"
#include "Engine/Engine.h"

#define LOCTEXT_NAMESPACE "FMyBlackmagicTimeStepDemoModule"

void FMyBlackmagicTimeStepDemoModule::StartupModule()
{
    // 确保在编辑器和游戏运行中都尝试初始化
    if (GEngine)
    {
        // 注意：实际配置需要根据物理硬件填写。这里使用默认配置可能失败。
        CustomTimeStep = NewObject<UBlackmagicCustomTimeStep>(GetTransientPackage(), NAME_None, RF_MarkAsNative);
        if (CustomTimeStep->Initialize(GEngine))
        {
            GEngine->SetCustomTimeStep(CustomTimeStep);
            UE_LOG(LogTemp, Log, TEXT("[BlackmagicDemo] Custom TimeStep initialized and set."));
        }
        else
        {
            UE_LOG(LogTemp, Warning, TEXT("[BlackmagicDemo] Failed to initialize Custom TimeStep. Check hardware connection and drivers."));
        }
    }
}

void FMyBlackmagicTimeStepDemoModule::ShutdownModule()
{
    if (GEngine && CustomTimeStep)
    {
        // 在模块关闭时，如果当前时间步长是我们的，就移除它
        if (GEngine->GetCustomTimeStep() == CustomTimeStep)
        {
            GEngine->SetCustomTimeStep(nullptr);
        }
        CustomTimeStep->Shutdown(GEngine);
        CustomTimeStep = nullptr;
    }
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyBlackmagicTimeStepDemoModule, MyBlackmagicTimeStepDemo)
```

## 模块依赖

从 `BlackmagicMedia.Build.cs` 可以看出，此插件深度依赖 MediaIO 框架和 Blackmagic 官方 SDK。

| 模块 | 用途 |
|---|---|
| `MediaIOCore` | 提供 `FMediaIOCorePlayerBase` 等基类和媒体 I/O 通用接口。 |
| `MediaIOCoreAssets` | 提供 `UCaptureCardMediaSource` 等资产基类。 |
| `BlackmagicSDK` | Blackmagic Design 官方的 DeckLink SDK 驱动程序库，提供硬件访问的底层 API。 |

此外，模块本身（如 `BlackmagicMedia`, `BlackmagicCore`）相互依赖。对于使用者，当在 Build.cs 中依赖 `BlackmagicMedia` 时，上述关联模块通常会自动链接。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `fe681f84` | MediaIO: Fix Blackmagic auto-detect misinterpreting interlaced signals as progressive. | 修复了 Blackmagic 自动检测功能将隔行信号误判为逐行信号的问题。 |
| 2026-05-26 | `36c08694` | Media IO - Populate Media Configuration when using auto for Blackmagic and Aja cards | 当 Blackmagic 和 Aja 卡使用“自动”模式时，自动填充媒体配置。 |
| 2026-05-23 | `42746f7a` | Media IO: Added additional engine analytics information to various media players and capture and pro... | 为多个媒体播放器和捕获组件添加了额外的引擎分析信息。 |
| 2026-05-12 | `b7bb4354` | Media IO - Fix bob deinterlacer field samples sharing source-frame timestamp | 修复了 Bob 去隔行处理中，场样本共享了源帧时间戳的问题。 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the ... | 将多个虚拟制片资产移至不同资产类别并进行了迁移。 |

### 维护评价

BlackmagicMedia 插件自 **2018 年** 创建以来，持续作为官方虚拟制片工具集的一部分得到维护。**最近一次更新发生在 2026 年 5 月**，主要针对隔行扫描信号检测和时间戳等核心底层问题进行了修复，并增加了分析功能。这表明该插件仍处于**活跃维护**状态，以适应不断更新的硬件驱动和解决新发现的集成问题。

作为连接昂贵专业硬件的桥梁，其稳定性和精确性至关重要。从提交记录看，开发团队仍在积极跟进和修复实际使用中发现的边缘案例。**强烈推荐**在任何需要使用 Blackmagic 采集卡/输出卡的 UE5 项目中启用此插件。需要注意，它默认未启用，因为并非所有项目都使用专业视频硬件。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/BlackmagicMedia)
-   [官方文档](https://docs.unrealengine.com/5.8/en-US/using-blackmagic-media-player-in-unreal-engine/) （通常位于 Media Framework 章节下）
-   [Blackmagic Design 官方网站](https://www.blackmagicdesign.com/) （获取驱动和硬件信息）