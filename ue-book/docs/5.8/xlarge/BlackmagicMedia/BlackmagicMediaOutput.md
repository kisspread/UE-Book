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
| 年龄标签 | 🏛️ 文物（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/BlackmagicMedia) | |

## 用途

这个插件为虚幻引擎提供了与Blackmagic Design硬件采集卡集成的媒体输入和输出功能。它实现了Blackmagic SDK与虚幻引擎媒体框架之间的桥梁，使得用户可以从Blackmagic采集卡捕获实时视频和音频信号（输入），也可以将引擎中的内容输出到Blackmagic设备上。

插件的核心价值在于：
1. **专业视频采集**：支持从Blackmagic DeckLink、UltraStudio等专业设备捕获高质量的视频信号
2. **视频输出**：允许将虚幻引擎渲染的内容（包括视口、渲染目标）输出到Blackmagic设备，用于监看、录制或直播
3. **时间码同步**：支持嵌入和读取时间码（Timecode），确保多设备同步
4. **音频集成**：支持捕获和输出音频信号

插件默认未启用（`EnabledByDefault: false`），因为需要硬件支持和相应的驱动程序。

## 使用场景

- **虚拟制片**：在LED墙或摄影棚中，将虚幻引擎的实时渲染输出到Blackmagic设备，用于最终输出或监看
- **直播制作**：将游戏画面或虚拟场景通过Blackmagic采集卡输出到OBS、vMix等直播软件
- **专业视频录制**：将引擎渲染的高分辨率内容直接录制到Blackmagic支持的存储设备
- **多机同步**：使用Blackmagic设备的时间码功能，同步多个摄像机或设备的时序
- **实时合成**：在绿幕拍摄中，将演员与虚幻引擎的虚拟场景实时合成

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Media Output` | 创建Blackmagic媒体输出实例 | `UBlackmagicMediaOutput` |
| `Start Capture` | 开始从Blackmagic设备捕获视频 | `UBlackmagicMediaCapture` |
| `Stop Capture` | 停止捕获 | `UBlackmagicMediaCapture` |
| `Set Output Configuration` | 设置输出配置（设备、端口、分辨率等） | `UBlackmagicMediaOutput` |

### 使用示例（蓝图描述）

1. **创建媒体输出**：
   - 在内容浏览器中右键 → Media → Blackmagic Media Output
   - 设置设备、端口、分辨率、帧率等配置

2. **开始捕获**：
   - 获取媒体输出资产的引用
   - 调用"Start Capture"节点，传入视口或渲染目标
   - 捕获会自动开始将引擎内容发送到Blackmagic设备

3. **蓝图控制**：
   - 可以通过蓝图动态创建媒体输出
   - 可以在运行时更改输出配置（如分辨率）
   - 可以监听捕获状态变化（如丢帧警告）

4. **音频输出**：
   - 在媒体输出设置中启用"Output Audio"
   - 设置音频采样率、通道数和位深度
   - 引擎的音频会自动路由到Blackmagic设备

## C++ 用法

### 头文件引入

```cpp
#include "BlackmagicMediaOutput.h"
#include "BlackmagicMediaCapture.h"
```

### 基本用法

创建Blackmagic媒体输出（来源：`BlackmagicMediaOutput.h`）：

```cpp
// 创建Blackmagic媒体输出对象
UBlackmagicMediaOutput* MediaOutput = NewObject<UBlackmagicMediaOutput>();

// 配置输出设置
FMediaIOOutputConfiguration OutputConfig;
OutputConfig.Device.DeviceName = "DeckLink Mini Monitor 4K";
OutputConfig.Device.PortIdentifier = "1";
OutputConfig.VideoMode.Width = 1920;
OutputConfig.VideoMode.Height = 1080;
OutputConfig.VideoMode.FrameRate = FFrameRate(30, 1);
OutputConfig.VideoMode.bInterlaced = false;
MediaOutput->OutputConfiguration = OutputConfig;

// 设置音频参数
MediaOutput->bOutputAudio = true;
MediaOutput->AudioSampleRate = EBlackmagicMediaOutputAudioSampleRate::SR_48k;
MediaOutput->OutputChannelCount = EBlackmagicMediaAudioOutputChannelCount::CH_2;

// 验证配置
FString FailureReason;
if (!MediaOutput->Validate(FailureReason))
{
    UE_LOG(LogTemp, Error, TEXT("媒体输出配置无效: %s"), *FailureReason);
}
```

### 进阶用法

捕获视口内容到Blackmagic设备（来源：`BlackmagicMediaCapture.h`）：

```cpp
// 获取或创建媒体输出
UBlackmagicMediaOutput* MediaOutput = GetOrCreateMediaOutput();

// 创建捕获实例
UBlackmagicMediaCapture* MediaCapture = Cast<UBlackmagicMediaCapture>(MediaOutput->CreateMediaCapture());

// 获取场景视口
TSharedPtr<FSceneViewport> SceneViewport = GEditor->GetActiveViewport()->GetSceneViewport();

// 开始捕获
if (MediaCapture->CaptureSceneViewport(SceneViewport))
{
    UE_LOG(LogTemp, Log, TEXT("开始Blackmagic捕获"));
    
    // 设置丢帧检测回调
    MediaCapture->OnCaptureFinished().AddLambda([](UMediaCapture* Capture, bool bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("Blackmagic捕获结束: %s"), bSuccess ? TEXT("成功") : TEXT("失败"));
    });
}
else
{
    UE_LOG(LogTemp, Error, TEXT("无法开始Blackmagic捕获"));
}

// 停止捕获
MediaCapture->StopCapture(true);
```

## Demo 示例

```cpp
// BlackmagicOutputDemo.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "BlackmagicMediaOutput.h"
#include "BlackmagicMediaCapture.h"
#include "BlackmagicOutputDemo.generated.h"

UCLASS()
class ABlackmagicOutputDemo : public AActor
{
    GENERATED_BODY()
    
public:
    ABlackmagicOutputDemo();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

public:
    UFUNCTION(BlueprintCallable, Category = "Blackmagic")
    void StartOutput();

    UFUNCTION(BlueprintCallable, Category = "Blackmagic")
    void StopOutput();

    UFUNCTION(BlueprintCallable, Category = "Blackmagic")
    void UpdateConfiguration(const FString& DeviceName, int32 Width, int32 Height, int32 FrameRate);

private:
    UPROPERTY()
    UBlackmagicMediaOutput* MediaOutput = nullptr;

    UPROPERTY()
    UBlackmagicMediaCapture* MediaCapture = nullptr;
};

// BlackmagicOutputDemo.cpp
#include "BlackmagicOutputDemo.h"
#include "Engine/Engine.h"
#include "Engine/GameViewportClient.h"

ABlackmagicOutputDemo::ABlackmagicOutputDemo()
{
    PrimaryActorTick.bCanEverTick = true;
}

void ABlackmagicOutputDemo::BeginPlay()
{
    Super::BeginPlay();
    
    // 创建媒体输出
    MediaOutput = NewObject<UBlackmagicMediaOutput>();
    
    // 默认配置
    FMediaIOOutputConfiguration Config;
    Config.Device.DeviceName = TEXT("DeckLink Mini Monitor 4K");
    Config.Device.PortIdentifier = TEXT("1");
    Config.VideoMode.Width = 1920;
    Config.VideoMode.Height = 1080;
    Config.VideoMode.FrameRate = FFrameRate(30, 1);
    MediaOutput->OutputConfiguration = Config;
    MediaOutput->bOutputAudio = true;
    
    UE_LOG(LogTemp, Log, TEXT("Blackmagic输出Actor已初始化"));
}

void ABlackmagicOutputDemo::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    StopOutput();
    
    if (MediaOutput)
    {
        MediaOutput->ConditionalBeginDestroy();
        MediaOutput = nullptr;
    }
    
    Super::EndPlay(EndPlayReason);
}

void ABlackmagicOutputDemo::StartOutput()
{
    if (MediaCapture && MediaCapture->IsCapturing())
    {
        UE_LOG(LogTemp, Warning, TEXT("已经在捕获中"));
        return;
    }
    
    // 验证配置
    FString FailureReason;
    if (!MediaOutput->Validate(FailureReason))
    {
        UE_LOG(LogTemp, Error, TEXT("配置验证失败: %s"), *FailureReason);
        return;
    }
    
    // 创建捕获
    MediaCapture = Cast<UBlackmagicMediaCapture>(MediaOutput->CreateMediaCapture());
    if (!MediaCapture)
    {
        UE_LOG(LogTemp, Error, TEXT("无法创建Blackmagic捕获"));
        return;
    }
    
    // 获取主视口
    if (GEngine && GEngine->GameViewport)
    {
        TSharedPtr<FSceneViewport> SceneViewport = GEngine->GameViewport->GetGameViewportWidget()->GetSceneViewport();
        if (SceneViewport.IsValid())
        {
            if (MediaCapture->CaptureSceneViewport(SceneViewport))
            {
                UE_LOG(LogTemp, Log, TEXT("Blackmagic输出已启动"));
            }
            else
            {
                UE_LOG(LogTemp, Error, TEXT("无法启动Blackmagic输出"));
            }
        }
    }
}

void ABlackmagicOutputDemo::StopOutput()
{
    if (MediaCapture && MediaCapture->IsCapturing())
    {
        MediaCapture->StopCapture(true);
        UE_LOG(LogTemp, Log, TEXT("Blackmagic输出已停止"));
    }
    
    if (MediaCapture)
    {
        MediaCapture->ConditionalBeginDestroy();
        MediaCapture = nullptr;
    }
}

void ABlackmagicOutputDemo::UpdateConfiguration(const FString& DeviceName, int32 Width, int32 Height, int32 FrameRate)
{
    StopOutput();
    
    FMediaIOOutputConfiguration Config;
    Config.Device.DeviceName = DeviceName;
    Config.Device.PortIdentifier = TEXT("1");
    Config.VideoMode.Width = Width;
    Config.VideoMode.Height = Height;
    Config.VideoMode.FrameRate = FFrameRate(FrameRate, 1);
    MediaOutput->OutputConfiguration = Config;
    
    UE_LOG(LogTemp, Log, TEXT("Blackmagic配置已更新: %s %dx%d @ %dfps"), 
        *DeviceName, Width, Height, FrameRate);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MediaIOCore` | 媒体IO核心框架，提供基础的媒体输入输出功能 |
| `MediaUtils` | 媒体工具库，提供通用的媒体处理功能 |
| `BlackmagicSDK` | Blackmagic SDK的封装，与硬件设备通信 |
| `TimeManagement` | 时间管理模块，用于时间码同步 |
| `GPUTextureTransfer` | GPU纹理传输，用于高性能视频输出 |

无特殊依赖（仅标准 Core/Engine/Slate 等）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `fe681f84` | MediaIO: Fix Blackmagic auto-detect misinterpreting interlaced signals as progressive. | 修复Blackmagic自动检测功能将隔行信号错误识别为逐行信号 |
| 2026-05-26 | `36c08694` | Media IO - Populate Media Configuration when using auto for Blackmagic and Aja cards | 使用Blackmagic和AJA卡的自动模式时填充媒体配置 |
| 2026-05-23 | `42746f7a` | Media IO: Added additional engine analytics information to various media players and capture and pro | 为各种媒体播放器和捕获添加额外的引擎分析信息 |
| 2026-05-12 | `b7bb4354` | Media IO - Fix bob deinterlacer field samples sharing source-frame timestamp | 修复Bob反隔行处理器的场采样共享源帧时间戳问题 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 虚拟制片：将各种VP资产移动到不同的资产类别 |

### 维护评价

**活跃维护**：插件虽然创建于2018年，但最近几个月仍有持续的功能更新和bug修复。从提交记录看，开发团队在持续改进Blackmagic设备的兼容性，特别是在：
1. 隔行/逐行信号检测
2. 时间码同步
3. 性能优化（多线程调度）
4. 分析工具集成

**推荐使用**：对于需要使用Blackmagic采集卡进行专业视频制作的用户，这个插件是必要的。它提供了完整的输入输出解决方案，并且得到了官方的持续维护。

**注意事项**：
1. 插件默认未启用，需要在项目设置中手动启用
2. 需要安装Blackmagic Desktop Video驱动程序
3. 实验性功能（如多线程调度、隔行作为逐行输出）需要谨慎使用
4. 硬件兼容性很重要，建议使用Blackmagic官方推荐的设备列表中的设备

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/BlackmagicMedia)
- [Blackmagic官方文档](https://www.blackmagicdesign.com/developer/product-documentation)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/BlackmagicMedia/Tests)