# AJA Media Player

> Implements input and output using AJA Capture cards.

| 属性 | 值 |
|---|---|
| 中文名 | AJA 媒体采集 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（媒体源资产、媒体输出资产） |
| 模块 | `AjaCore` (Runtime), `AjaMedia` (Runtime), `AjaMediaEditor` (Runtime), `AjaMediaFactory` (Runtime), `AjaMediaOutput` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-05-09 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AjaMedia) | |

## 用途

AJA Media Player 插件在 Unreal Engine 和 AJA 专业视频采集卡之间建立桥梁，实现 SDI/HDMI 信号的实时输入和输出。AJA 是广播级/影视级视频 I/O 硬件的主流厂商之一，该插件解决的核心问题是：

1. **实时视频采集**：从 AJA 采集卡的 SDI/HDMI 输入端口捕获视频帧，作为 Media Player 使用
2. **帧同步与时间码**：通过 AJA 硬件实现引擎时钟与外部信号源的精确同步（Genlock），以及从 SDI 流中读取 LTC/VITC 时间码
3. **自定义时间步**：用外部视频信号源驱动引擎的 Tick 节奏，确保虚拟制片场景中渲染与外部摄像机/LED 墙的帧精确对齐
4. **音频/辅助数据采集**：同时采集嵌入音频通道和辅助数据（ANC）

该插件仅支持 Win64 平台，且**默认关闭**（`EnabledByDefault=false`），需要在项目设置中手动启用。这是因为依赖外部硬件驱动，仅在需要 AJA 卡的专业虚拟制片/广播场景中使用。

## 使用场景

- 你在做**虚拟制片（Virtual Production）**，需要将摄像机的 SDI 信号实时输入到引擎 → 使用 `UAjaMediaSource` 作为视频输入源
- 你需要引擎帧率与外部视频设备**精确同步**（Genlock） → 使用 `UAjaCustomTimeStep` 替代引擎默认时间步
- 你需要从 SDI 流中读取**时间码**，用于多设备录制同步 → 使用 `UAjaTimecodeProvider`
- 你需要将引擎渲染结果输出到 LED 墙或外部显示器 → 使用 `AjaMediaOutput` 模块（单独文档）

## 蓝图用法

### 核心资产

| 资产类型 | 说明 | 所在类 |
|---|---|---|
| `UAjaMediaSource` | 配置 AJA 采集卡输入源（设备、端口、格式、音频、辅助数据等） | `UAjaMediaSource` |
| `UAjaCustomTimeStep` | 通过 AJA 卡的 Genlock 信号控制引擎时钟步进 | `UAjaCustomTimeStep` |
| `UAjaTimecodeProvider` | 从 AJA 卡读取时间码（支持 LTC 引脚或 SDI 内嵌） | `UAjaTimecodeProvider` |
| `UAjaMediaSettings` | 插件全局设置（配置类） | `UAjaMediaSettings` |

### UAjaMediaSource 关键属性

| 属性 | 类型 | 说明 |
|---|---|---|
| `MediaConfiguration` | `FMediaIOConfiguration` | 设备、端口和视频设置 |
| `AutoDetectableTimecodeFormat` | `EMediaIOAutoDetectableTimecodeFormat` | 时间码格式（默认 Auto） |
| `bCaptureWithAutoCirculating` | `bool` | 使用环形缓冲区捕获，降低延迟 |
| `bCaptureVideo` | `bool` | 是否采集视频 |
| `bCaptureAudio` | `bool` | 是否采集音频 |
| `bCaptureAncillary` | `bool` | 是否采集辅助数据（影响性能） |
| `ColorFormat` | `EAjaMediaSourceColorFormat` | YUV2 8bit 或 YUV 10bit |
| `AudioChannel` | `EAjaMediaAudioChannel` | 6 通道或 8 通道 |
| `bStopInputOnCardTimeout` | `bool` | 超时时是否停止输入 |
| `bEncodeTimecodeInTexel` | `bool` | 将时间码烧录到纹理像素中 |
| `bLogDropFrame` | `bool` | 丢帧时记录警告日志 |

### UAjaCustomTimeStep 关键属性

| 属性 | 类型 | 说明 |
|---|---|---|
| `bUseReferenceIn` | `bool` | 使用参考输入引脚的 Genlock 信号 |
| `MediaConfiguration` | `FMediaIOConfiguration` | Genlock 信号的设备和端口配置 |
| `bWaitForFrameToBeReady` | `bool` | 等待帧读取完成（增加延迟但提高同步精度） |
| `TimecodeFormat` | `EMediaIOTimecodeFormat` | 从 SDI 流读取的时间码类型 |
| `bStopOnCardTimeout` | `bool` | 采集卡超时时是否停止（编辑器外） |
| `bEnableOverrunDetection` | `bool` | 检测引擎循环是否超出源信号频率 |

### UAjaTimecodeProvider 关键属性

| 属性 | 类型 | 说明 |
|---|---|---|
| `bUseDedicatedPin` | `bool` | 使用专用 LTC 引脚还是 SDI 输入读取时间码 |
| `bUseReferenceIn` | `bool` | 从参考输入引脚读取 LTC |
| `LTCConfiguration` | `FAjaMediaTimecodeReference` | LTC 引脚设备和帧率配置 |
| `TimecodeConfiguration` | `FMediaIOVideoTimecodeConfiguration` | 视频信号中的时间码配置 |

### 使用示例（蓝图描述）

**视频采集**：
1. 创建 `UAjaMediaSource` 资产 → 设置 `MediaConfiguration` 选择 AJA 设备和端口
2. 设置 `bCaptureVideo = true`，选择 `ColorFormat`
3. 在 Media Player 组件中打开该 MediaSource 进行播放

**Genlock 同步**：
1. 在项目设置 → Engine → General Settings → Custom Time Step 中选择 `UAjaCustomTimeStep`
2. 配置 `bUseReferenceIn` 和 `MediaConfiguration`
3. 启用后引擎时钟将与 AJA 卡的参考信号同步

**时间码读取**：
1. 在 World Settings → Timecode → TimecodeProvider 中选择 `UAjaTimecodeProvider`
2. 配置 `bUseDedicatedPin` 和对应的 LTC 或视频时间码配置
3. 引擎时间码将自动与 AJA 卡读取的时间码同步

## C++ 用法

### 头文件引入

```cpp
#include "AjaMediaSource.h"
#include "AjaCustomTimeStep.h"
#include "AjaTimecodeProvider.h"
#include "AjaDeviceProvider.h"
#include "AjaMediaDefinitions.h"
#include "IAjaMediaModule.h"
```

### 基本用法：创建媒体播放器

```cpp
// 通过模块接口创建 AJA 媒体播放器
// 来源: Public/IAjaMediaModule.h

#include "IAjaMediaModule.h"

// 检查 AJA 模块是否可用
if (IAjaMediaModule::Get().IsInitialized() && IAjaMediaModule::Get().CanBeUsed())
{
    // 创建播放器实例
    TSharedPtr<IMediaPlayer, ESPMode::ThreadSafe> Player = 
        IAjaMediaModule::Get().CreatePlayer(EventSink);
    
    if (Player.IsValid())
    {
        // 打开 AJA 输入源
        UAjaMediaSource* MediaSource = NewObject<UAjaMediaSource>();
        Player->Open(MediaSource->GetUrl(), MediaSource);
    }
}
```

### 基本用法：配置媒体源

```cpp
// 以编程方式配置 AJA 媒体源
// 来源: Public/AjaMediaSource.h

UAjaMediaSource* AjaSource = NewObject<UAjaMediaSource>();

// 配置输入设备（需通过 FAjaDeviceProvider 获取可用配置）
AjaSource->MediaConfiguration.Device.DeviceIdentifier = TEXT("Corvid88 0");
AjaSource->MediaConfiguration.Port.PortIdentifier = TEXT("Single1");
AjaSource->MediaConfiguration.TransportType = EMediaIOTransportType::Single;

// 启用视频和音频采集
AjaSource->bCaptureVideo = true;
AjaSource->bCaptureAudio = true;
AjaSource->ColorFormat = EAjaMediaSourceColorFormat::YUV2_8bit;
AjaSource->AudioChannel = EAjaMediaAudioChannel::Channel8;

// 启用时间码自动检测
AjaSource->AutoDetectableTimecodeFormat = EMediaIOAutoDetectableTimecodeFormat::Auto;

// 配置缓冲区大小
AjaSource->MaxNumVideoFrameBuffer = 4;
AjaSource->MaxNumAudioFrameBuffer = 4;
```

### 基本用法：查询设备信息

```cpp
// 使用设备提供者查询可用 AJA 设备和配置
// 来源: Public/AjaDeviceProvider.h

#include "AjaDeviceProvider.h"

FAjaDeviceProvider DeviceProvider;

// 获取所有可用设备
TArray<FMediaIODevice> Devices = DeviceProvider.GetDevices();
for (const FMediaIODevice& Device : Devices)
{
    UE_LOG(LogTemp, Log, TEXT("AJA Device: %s"), *Device.DeviceIdentifier);
    
    // 获取设备支持的模式
    TArray<FMediaIOMode> Modes = DeviceProvider.GetModes(Device, /*bInOutput=*/false);
    for (const FMediaIOMode& Mode : Modes)
    {
        UE_LOG(LogTemp, Log, TEXT("  Mode: %s"), *Mode.ToText().ToString());
    }
}

// 获取所有输入配置
TArray<FMediaIOInputConfiguration> InputConfigs = DeviceProvider.GetInputConfigurations();

// 自动检测当前正在输入的信号源
DeviceProvider.AutoDetectConfiguration(
    FAjaDeviceProvider::FOnConfigurationAutoDetected::CreateLambda(
        [](TArray<FAjaDeviceProvider::FMediaIOConfigurationWithTimecodeFormat> Configurations)
        {
            for (const auto& Config : Configurations)
            {
                UE_LOG(LogTemp, Log, TEXT("Detected: %s with TC: %d"),
                    *Config.Configuration.ToDisplayString(),
                    (int32)Config.TimecodeFormat);
            }
        }
    )
);
```

### 进阶用法：HDR 配置

```cpp
// 配置 HDR 元数据
// 来源: Public/AjaMediaDefinitions.h

#include "AjaMediaDefinitions.h"

// 构建 HDR 选项
FAjaMediaHDROptions HDROptions;
HDROptions.EOTF = EAjaHDRMetadataEOTF::PQ;       // HDR10 使用 PQ 传输函数
HDROptions.Gamut = EAjaHDRMetadataGamut::Rec2020;  // Rec.2020 色域

// 在 UE 内部结构和 AJA 库结构之间转换
AJA::FAjaHDROptions AjaHDROptions = UE::AjaMedia::MakeAjaHDROptions(HDROptions);
```

### 进阶用法：手动初始化 AJA 系统

```cpp
// 手动控制 AJA 系统的生命周期
// 来源: Private/Aja/Aja.h

#include "Aja/Aja.h"

// 初始化 AJA 系统
bool bSuccess = FAja::Initialize();

// 检查是否可用
if (FAja::IsInitialized() && FAja::CanUseAJACard())
{
    // AJA 卡可用，可以进行视频 I/O
}

// 在应用程序关闭时清理
FAja::Shutdown();

// 时间码转换辅助
AJA::FTimecode AjaTC;
FFrameRate FrameRate(30000, 1001); // 29.97fps
FTimecode UETC = FAja::ConvertAJATimecode2Timecode(AjaTC, FrameRate);
```

## Demo 示例

以下示例展示如何在 C++ 中创建一个 AJA 媒体输入源并将其打开进行视频采集：

```cpp
// AjaMediaDemo.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MediaTexture.h"
#include "AjaMediaDemo.generated.h"

class IMediaPlayer;
class UAjaMediaSource;
class UMediaTexture;

UCLASS(ClassGroup=(Media), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UAjaMediaDemoComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UAjaMediaDemoComponent();

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    /** 打开 AJA 输入 */
    UFUNCTION(BlueprintCallable, Category = "AJA Demo")
    bool OpenAjaInput();

    /** 关闭 AJA 输入 */
    UFUNCTION(BlueprintCallable, Category = "AJA Demo")
    void CloseAjaInput();

    /** 媒体纹理，用于显示采集的视频 */
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "AJA Demo")
    TObjectPtr<UMediaTexture> MediaTexture;

    /** 设备标识符 */
    UPROPERTY(EditAnywhere, Category = "AJA Demo")
    FString DeviceIdentifier = TEXT("Corvid88 0");

    /** 端口标识符 */
    UPROPERTY(EditAnywhere, Category = "AJA Demo")
    FString PortIdentifier = TEXT("Single1");

private:
    TSharedPtr<IMediaPlayer, ESPMode::ThreadSafe> Player;
    UPROPERTY()
    TObjectPtr<UAjaMediaSource> MediaSource;
};
```

```cpp
// AjaMediaDemo.cpp
#include "AjaMediaDemo.h"

#include "IAjaMediaModule.h"
#include "AjaMediaSource.h"
#include "MediaTexture.h"
#include "IMediaEventSink.h"

UAjaMediaDemoComponent::UAjaMediaDemoComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UAjaMediaDemoComponent::BeginPlay()
{
    Super::BeginPlay();
    OpenAjaInput();
}

void UAjaMediaDemoComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    CloseAjaInput();
    Super::EndPlay(EndPlayReason);
}

bool UAjaMediaDemoComponent::OpenAjaInput()
{
    // 1. 检查模块是否就绪
    IAjaMediaModule& AjaModule = IAjaMediaModule::Get();
    if (!AjaModule.IsInitialized() || !AjaModule.CanBeUsed())
    {
        UE_LOG(LogTemp, Warning, TEXT("AJA Media module is not available."));
        return false;
    }

    // 2. 配置媒体源
    MediaSource = NewObject<UAjaMediaSource>();
    MediaSource->MediaConfiguration.Device.DeviceIdentifier = DeviceIdentifier;
    MediaSource->MediaConfiguration.Port.PortIdentifier = PortIdentifier;
    MediaSource->MediaConfiguration.TransportType = EMediaIOTransportType::Single;
    MediaSource->bCaptureVideo = true;
    MediaSource->bCaptureAudio = true;
    MediaSource->ColorFormat = EAjaMediaSourceColorFormat::YUV2_8bit;
    MediaSource->AudioChannel = EAjaMediaAudioChannel::Channel8;
    MediaSource->AutoDetectableTimecodeFormat = EMediaIOAutoDetectableTimecodeFormat::Auto;

    if (!MediaSource->Validate())
    {
        UE_LOG(LogTemp, Warning, TEXT("AJA MediaSource configuration is invalid."));
        return false;
    }

    // 3. 创建播放器
    // 使用一个简单的事件接收器（也可以继承 IMediaEventSink 来处理事件）
    Player = AjaModule.CreatePlayer(*GEngine->GetEngineSubsystem<UMediaPlayerSubsystem>()->GetDefaultEventSink());
    if (!Player.IsValid())
    {
        UE_LOG(LogTemp, Warning, TEXT("Failed to create AJA media player."));
        return false;
    }

    // 4. 打开媒体源
    FString Url = MediaSource->GetUrl();
    bool bOpened = Player->Open(Url, MediaSource);
    if (!bOpened)
    {
        UE_LOG(LogTemp, Warning, TEXT("Failed to open AJA input: %s"), *Url);
        return false;
    }

    // 5. 将媒体纹理绑定到播放器
    if (MediaTexture)
    {
        MediaTexture->SetMediaPlayer(Player.Get());
    }

    UE_LOG(LogTemp, Log, TEXT("AJA input opened successfully: %s"), *Url);
    return true;
}

void UAjaMediaDemoComponent::CloseAjaInput()
{
    if (Player.IsValid())
    {
        if (MediaTexture)
        {
            MediaTexture->SetMediaPlayer(nullptr);
        }
        Player->Close();
        Player.Reset();
    }
    MediaSource = nullptr;
}
```

## 模块依赖

该插件包含 5 个模块，以下列出各模块的关键依赖（不包含 Core/Engine/Slate 等常见依赖）：

| 模块 | 用途 |
|---|---|
| `MediaIOCore` | 媒体 I/O 核心抽象层，提供设备提供者接口和共享媒体采样基类 |
| `MediaUtils` | 媒体工具库，提供媒体播放器基类、采样池等 |
| `TimeManagement` | 时间管理，用于自定义时间步和时间码提供者的基类 |
| `AJA` | AJA 硬件 SDK 封装模块（本插件的 `AjaCore`），提供底层设备 API |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `36c08694` | Media IO - Populate Media Configuration when using auto for Blackmagic and Aja cards | 自动检测模式下正确填充媒体配置 |
| 2026-05-23 | `42746f7a` | Media IO: Added additional engine analytics information to various media players and capture and pro | 为媒体播放器和采集添加引擎分析数据 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 虚拟制片资产分类调整和迁移 |
| 2026-05-12 | `c657503b` | [Media] Add missing UAssetDefinition entries for concrete UMediaSource and UMediaOutput subclasses t | 补充媒体源/输出子类的资产定义注册 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式化说明符不匹配问题 |

### 维护评价

AJA Media Player 是一个**活跃维护**的专业级插件，最近一次更新距今仅数天。该插件：

- ✅ **持续更新**：近几个月有功能性更新（自动检测改进、分析数据添加、资产注册修复）
- ✅ **生产质量**：自 2018 年创建以来持续迭代，代码成熟稳定
- ✅ **虚拟制片核心组件**：是 Unreal Engine 虚拟制片工作流中 AJA 硬件集成的关键基础设施
- ⚠️ **仅限 Win64**：不支持其他平台
- ⚠️ **需要硬件**：必须安装 AJA 采集卡及其驱动程序才能使用
- ⚠️ **默认关闭**：`EnabledByDefault=false`，需手动在项目设置中启用

**推荐使用**：如果你的项目需要与 AJA 视频采集卡集成（虚拟制片、广播、现场制作等），该插件是官方支持的标准方案，强烈推荐使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AjaMedia)
- [官方文档](https://docs.unrealengine.com/en-US/ProductionPipelines/MediaFramework/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AjaMedia/Tests)