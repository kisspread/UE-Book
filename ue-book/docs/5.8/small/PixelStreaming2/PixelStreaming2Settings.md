# Pixel Streaming 2 Settings

> Streaming of Unreal Engine audio and rendering to WebRTC-compatible media players such as a web browsers.

| 属性 | 值 |
|---|---|
| 中文名 | 像素流设置 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PixelStreaming2Settings` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-09-04 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming2) | |

## 用途

PixelStreaming2Settings 是 Pixel Streaming 2 插件的配置管理模块，负责将所有像素流相关设置集中管理并通过 Unreal Engine 的控制台变量（CVar）和 UDeveloperSettings 框架暴露出来。

该模块解决的核心问题是：Pixel Streaming 2 涉及大量可配置参数（编码器、WebRTC、输入、HMD、信令服务器等），需要一个统一的设置中心来管理这些配置，并支持：
- 通过编辑器项目设置界面进行可视化配置
- 通过控制台变量（CVar）进行运行时调整
- 通过命令行参数进行部署时覆盖
- 配置变更时自动触发委托通知其他模块

## 使用场景

- 你需要调整像素流的视频编码质量/比特率 → 通过编辑器设置页或 CVar 修改编码器参数
- 你需要配置 WebRTC 连接参数（端口范围、码率范围等） → 修改 WebRtcSettings 分类下的设置
- 你需要限制输入控制器模式（所有人可控制 vs 仅主机可控制） → 设置 InputControllerMode
- 你需要在编辑器中进行像素流预览 → 配置 EditorStreaming 分类
- 你需要支持 XR 头显流式传输 → 启用 HMD 相关设置
- 你需要自定义光标样式以适配像素流 → 配置 Cursor 分类

## 编辑器设置用法

### 设置入口

在 Unreal Editor 中，通过 **编辑 → 项目设置 → 插件 → Pixel Streaming 2** 访问所有配置项。

也可以直接在 `DefaultGame.ini` 中写入配置：

```ini
[/Script/PixelStreaming2Settings.PixelStreaming2PluginSettings]
EnablePixelStreamingToolbar=true
ConnectionURL=ws://127.0.0.1:80
WebRTCFps=60
WebRTCMaxBitrate=40000000
```

### 核心设置分类

#### 基本设置

| 设置项 | CVar | 说明 | 默认值 |
|---|---|---|---|
| Enable Pixel Streaming 2 Toolbar | — | 启用主视口工具栏中的像素流按钮 | `true` |
| Log Pixel Streaming Stats | `CVarLogStats` | 在日志中输出像素流统计信息 | `false` |
| Default Connection URL | `CVarConnectionURL` | 信令服务器连接地址，格式 `(protocol)://(host):(port)` | 空 |
| Initialize Default Streamer | `CVarInitializeDefaultStreamer` | 是否初始化默认流发送器 | `true` |
| Automatically Start Streaming | `CVarAutoStartStream` | 加载插件后自动开始流式传输（非编辑器模式） | `true` |

#### 编码器设置

| 设置项 | CVar | 说明 | 默认值 |
|---|---|---|---|
| Target Bitrate | `CVarEncoderTargetBitrate` | 目标比特率（bps），-1 表示使用 WebRTC 自动调整 | `-1` |
| Encoder Minimum Quality | `CVarEncoderMinQuality` | 最低编码质量（0-100） | `0` |
| Encoder Maximum Quality | `CVarEncoderMaxQuality` | 最高编码质量（0-100） | `100` |
| Quality Preset | `CVarEncoderQualityPreset` | 编码质量预设：`ULTRA_LOW_QUALITY` / `LOW_QUALITY` / `DEFAULT` / `HIGH_QUALITY` / `LOSSLESS` | `Default` |
| Latency Mode | `CVarEncoderLatencyMode` | 延迟模式：`ULTRA_LOW_LATENCY` / `LOW_LATENCY` / `DEFAULT` | `UltraLowLatency` |
| Preferred Encoder Codec | `CVarEncoderCodec` | 首选编码器：`H264` / `VP8` / `VP9` / `AV1` | `H264` |
| Keyframe Interval | `CVarEncoderKeyframeInterval` | 关键帧间隔（帧数），-1 表示禁用周期性关键帧 | `-1` |
| Max Encoding Sessions | `CVarEncoderMaxSessions` | 最大并发编码会话数，-1 表示无限制。注意 GeForce GPU 最多支持 8 个 | `-1` |
| Enable Simulcast | `CVarEncoderEnableSimulcast` | 启用联播（同时编码全分辨率、1/2、1/4） | `false` |
| Scalability Mode | `CVarEncoderScalabilityMode` | 可伸缩性模式，如 `L1T1` | `L1T1` |
| H264 Profile | `CVarEncoderH264Profile` | H264 配置文件：`AUTO` / `BASELINE` / `MAIN` / `HIGH` 等 | `Baseline` |

#### WebRTC 设置

| 设置项 | CVar | 说明 | 默认值 |
|---|---|---|---|
| WebRtc FPS | `CVarWebRTCFps` | WebRTC 编码帧率 | `60` |
| WebRtc Start Bitrate | `CVarWebRTCStartBitrate` | 初始码率（bps） | `1000000` |
| WebRtc Minimum Bitrate | `CVarWebRTCMinBitrate` | 最低码率（bps） | `100000` |
| WebRtc Maximum Bitrate | `CVarWebRTCMaxBitrate` | 最高码率（bps） | `40000000` |
| Disable Audio Sync | `CVarWebRTCDisableAudioSync` | 禁用音视频轨道同步（低延迟场景可用） | `true` |
| Enable Flex FEC | `CVarWebRTCEnableFlexFec` | 启用弹性前向纠错 | `false` |
| Negotiate Codecs | `CVarWebRTCNegotiateCodecs` | 是否在 SDP 握手中发送所有编解码器供对端协商 | `false` |
| Port Allocator Flags | `CVarWebRTCPortAllocatorFlags` | 端口分配器标志位掩码 | `0` |
| Min/Max Port | `CVarWebRTCMinPort` / `CVarWebRTCMaxPort` | WebRTC 可用端口范围 | `49152-65535` |

#### 输入与控制

| 设置项 | CVar | 说明 | 默认值 |
|---|---|---|---|
| Input Controller Mode | `CVarInputController` | 输入控制模式：`Any`（任何人）/ `Host`（仅主机） | `Any` |

#### 光标设置

| 设置项 | 说明 |
|---|---|
| DefaultCursorClassName | 默认光标样式（软件光标，在视频流中可见） |
| TextEditBeamCursorClassName | 文本编辑光束光标样式 |
| HiddenCursorClassName | 隐藏光标样式（客户端光标模式下使用） |

#### 编辑器流式传输

| 设置项 | CVar | 说明 | 默认值 |
|---|---|---|---|
| Auto Stream PIE | `CVarAutoStreamPIE` | PIE 模式下自动开始流式传输 | `true` |
| Start On Launch | `CVarEditorStartOnLaunch` | 编辑器启动时自动开启流 | `false` |
| Editor Source | `CVarEditorSource` | 流来源：`Editor`（完整编辑器）/ `LevelEditorViewport`（仅关卡视口） | `Editor` |

#### XR 流式传输（HMD）

| 设置项 | CVar | 说明 | 默认值 |
|---|---|---|---|
| Enable HMD | `CVarHMDEnable` | 启用 HMD 功能（立体渲染与输入） | `false` |
| Match Aspect Ratio | `CVarHMDMatchAspectRatio` | 自动匹配 HMD 宽高比 | `true` |
| Apply Eye Position | `CVarHMDApplyEyePosition` | 应用 WebXR 报告的左右眼位置 | `true` |

### 端口分配器标志（EPortAllocatorFlags）

`EPortAllocatorFlags` 是位掩码枚举，用于精细控制 WebRTC 网络连接策略：

| 标志 | 说明 |
|---|---|
| `DisableUdp` | 禁用 UDP |
| `DisableStun` | 禁用 STUN |
| `DisableRelay` | 禁用 TURN 中继 |
| `DisableTcp` | 禁用 TCP |
| `EnableIPV6` | 启用 IPv6 |
| `EnableSharedSocket` | 启用共享套接字 |
| `DisableAdapterEnumeration` | 禁用网络适配器枚举 |
| `DisableCostlyNetworks` | 禁用高成本网络 |
| `EnableIPV6OnWifi` | WiFi 上启用 IPv6 |
| `DisableLinkLocalNetworks` | 禁用链路本地网络 |

### 委托通知

当 CVar 值发生变更时，`UPixelStreaming2PluginSettings::Delegates()` 提供的委托会被触发：

| 委托 | 触发条件 |
|---|---|
| `OnScalabilityModeChanged` | 可伸缩性模式变更 |
| `OnSimulcastEnabledChanged` | 联播启用状态变更 |
| `OnCaptureUseFenceChanged` | 捕获围栏设置变更 |
| `OnUseMediaCaptureChanged` | 媒体捕获模式变更 |
| `OnWebRTCFpsChanged` | WebRTC 帧率变更 |
| `OnWebRTCBitrateChanged` | WebRTC 码率变更 |
| `OnDecoupleFramerateChanged` | 帧率解耦设置变更 |
| `OnInputKeyFilterChanged` | 输入按键过滤变更 |

## C++ 用法

### 头文件引入

```cpp
#include "Internal/PixelStreaming2PluginSettings.h"
```

### 基本用法：读取配置值

```cpp
// 获取设置单例
UPixelStreaming2PluginSettings* Settings = GetMutableDefault<UPixelStreaming2PluginSettings>();

// 读取基本配置
int32 Fps = Settings->WebRTCFps;                      // 默认 60
int32 MaxBitrate = Settings->WebRTCMaxBitrate;         // 默认 40Mbps
bool bAutoStart = Settings->AutoStartStream;           // 默认 true
FString URL = Settings->ConnectionURL;                 // 信令服务器地址

// 读取编码器配置
int32 MinQuality = Settings->EncoderMinQuality;        // 默认 0
int32 MaxQuality = Settings->EncoderMaxQuality;        // 默认 100
EAVPreset Preset = Settings->QualityPreset;            // 默认 Default
EAVLatencyMode Latency = Settings->LatencyMode;       // 默认 UltraLowLatency
```

### 基本用法：通过 CVar 运行时修改

```cpp
// 通过 CVar 修改帧率（运行时生效）
IConsoleVariable* FpsCVar = IConsoleManager::Get().FindConsoleVariable(TEXT("PixelStreaming2.WebRTCFps"));
if (FpsCVar)
{
    FpsCVar->Set(30);  // 设置为 30fps
}

// 通过 CVar 修改码率
IConsoleVariable* MaxBitrateCVar = IConsoleManager::Get().FindConsoleVariable(TEXT("PixelStreaming2.WebRTCMaxBitrate"));
if (MaxBitrateCVar)
{
    MaxBitrateCVar->Set(20000000);  // 20Mbps
}
```

### 进阶用法：监听配置变更委托

```cpp
#include "Internal/PixelStreaming2PluginSettings.h"

void UMyClass::BindToSettingsChanges()
{
    UPixelStreaming2PluginSettings::FDelegates* Delegates = UPixelStreaming2PluginSettings::Delegates();
    if (Delegates)
    {
        // 监听码率变更
        Delegates->OnWebRTCBitrateChanged.AddUObject(this, &UMyClass::OnBitrateChanged);
        
        // 监听帧率变更
        Delegates->OnWebRTCFpsChanged.AddUObject(this, &UMyClass::OnFpsChanged);
        
        // 监听解耦帧率设置变更
        Delegates->OnDecoupleFramerateChanged.AddUObject(this, &UMyClass::OnDecoupleChanged);
    }
}

void UMyClass::OnBitrateChanged(IConsoleVariable* CVar)
{
    int32 NewBitrate = CVar->GetInt();
    UE_LOG(LogTemp, Log, TEXT("Bitrate changed to: %d bps"), NewBitrate);
}

void UMyClass::OnFpsChanged(IConsoleVariable* CVar)
{
    int32 NewFps = CVar->GetInt();
    UE_LOG(LogTemp, Log, TEXT("FPS changed to: %d"), NewFps);
}

void UMyClass::OnDecoupleChanged(IConsoleVariable* CVar)
{
    bool bDecoupled = CVar->GetBool();
    UE_LOG(LogTemp, Log, TEXT("Decouple framerate: %s"), bDecoupled ? TEXT("true") : TEXT("false"));
}
```

### 进阶用法：读取端口分配器标志

```cpp
#include "Internal/PixelStreaming2PluginSettings.h"

void UMyClass::CheckPortAllocatorSettings()
{
    // 获取组合后的端口分配器标志
    EPortAllocatorFlags Flags = UPixelStreaming2PluginSettings::GetPortAllocationFlags();
    
    // 检查特定标志
    if (EnumHasAnyFlags(Flags, EPortAllocatorFlags::DisableStun))
    {
        UE_LOG(LogTemp, Log, TEXT("STUN is disabled"));
    }
    
    if (EnumHasAnyFlags(Flags, EPortAllocatorFlags::EnableIPV6))
    {
        UE_LOG(LogTemp, Log, TEXT("IPv6 is enabled"));
    }
    
    // 获取编解码器偏好列表
    TArray<EVideoCodec> CodecPreferences = UPixelStreaming2PluginSettings::GetCodecPreferences();
    for (EVideoCodec Codec : CodecPreferences)
    {
        UE_LOG(LogTemp, Log, TEXT("Codec preference: %d"), static_cast<int32>(Codec));
    }
}
```

### 进阶用法：运行时修改命令行参数覆盖

```cpp
// 启动时通过命令行参数覆盖设置：
// UE5Editor.exe -PixelStreaming2.ConnectionURL=ws://10.0.0.1:80
// UE5Editor.exe -PixelStreaming2.WebRTCFps=30
// UE5Editor.exe -PixelStreaming2.Codec=VP8
// UE5Editor.exe -PixelStreaming2.AutoStartStream=false
// UE5Editor.exe -PixelStreaming2.HMDEnable=true

// 编码器质量预设支持的值：
// -PixelStreaming2.EncoderQualityPreset=ULTRA_LOW_QUALITY
// -PixelStreaming2.EncoderQualityPreset=LOW_QUALITY
// -PixelStreaming2.EncoderQualityPreset=DEFAULT
// -PixelStreaming2.EncoderQualityPreset=HIGH_QUALITY
// -PixelStreaming2.EncoderQualityPreset=LOSSLESS
```

## Demo 示例

以下示例展示如何创建一个自定义模块，在运行时动态调整 Pixel Streaming 2 的设置：

**MyPixelStreamingManager.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "MyPixelStreamingManager.generated.h"

UCLASS()
class UMyPixelStreamingManager : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    /** 切换到低延迟模式 */
    UFUNCTION(BlueprintCallable, Category = "PixelStreaming")
    void SwitchToLowLatencyMode();

    /** 切换到高质量模式 */
    UFUNCTION(BlueprintCallable, Category = "PixelStreaming")
    void SwitchToHighQualityMode();

private:
    void OnBitrateChanged(IConsoleVariable* CVar);
};
```

**MyPixelStreamingManager.cpp**

```cpp
#include "MyPixelStreamingManager.h"
#include "Internal/PixelStreaming2PluginSettings.h"

void UMyPixelStreamingManager::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);

    // 绑定设置变更委托
    UPixelStreaming2PluginSettings::FDelegates* Delegates = UPixelStreaming2PluginSettings::Delegates();
    if (Delegates)
    {
        Delegates->OnWebRTCBitrateChanged.AddUObject(this, &UMyPixelStreamingManager::OnBitrateChanged);
    }
}

void UMyPixelStreamingManager::Deinitialize()
{
    Super::Deinitialize();
}

void UMyPixelStreamingManager::SwitchToLowLatencyMode()
{
    UPixelStreaming2PluginSettings* Settings = GetMutableDefault<UPixelStreaming2PluginSettings>();

    // 低延迟：高帧率、低码率上限、最低延迟模式
    Settings->WebRTCFps = 120;
    Settings->WebRTCMaxBitrate = 20000000;
    Settings->LatencyMode = EAVLatencyMode::UltraLowLatency;
    Settings->DecoupleFramerate = true;

    UE_LOG(LogTemp, Log, TEXT("Switched to low latency mode"));
}

void UMyPixelStreamingManager::SwitchToHighQualityMode()
{
    UPixelStreaming2PluginSettings* Settings = GetMutableDefault<UPixelStreaming2PluginSettings>();

    // 高质量：高码率上限、高质量预设
    Settings->WebRTCFps = 60;
    Settings->WebRTCMaxBitrate = 80000000;
    Settings->QualityPreset = EAVPreset::HighQuality;
    Settings->EncoderMinQuality = 50;
    Settings->DecoupleFramerate = false;

    UE_LOG(LogTemp, Log, TEXT("Switched to high quality mode"));
}

void UMyPixelStreamingManager::OnBitrateChanged(IConsoleVariable* CVar)
{
    UE_LOG(LogTemp, Verbose, TEXT("WebRTC bitrate updated to: %d"), CVar->GetInt());
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `EpicRtc` | Epic RTC 库，提供 `EpicRtcPortAllocatorOptions` 等端口分配器枚举映射 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `c1dab3e1` | [PixelStreaming2] Fix: Input handler obtaining default target window from wrong method | 修复输入处理器获取默认目标窗口方法错误 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 截断为 float 的编译警告 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the ... | 虚拟制作资产分类调整和迁移 |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 FJsonObject 以支持 FString 和 UE::FSharedString |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复作用域枚举在格式化函数中导致的输出错误 |

### 维护评价

- **活跃维护** ✅：最近 1 个月内有多次功能性更新和 bug 修复
- **年轻插件**：创建于 2024 年 9 月，约 2 年历史，仍处于快速迭代阶段
- **Epic 官方维护**：由 Epic Games 开发和维护，与 UE5 主分支同步
- **需注意**：`EnabledByDefault=false`，需要手动在插件管理器中启用
- **推荐使用**：作为 Pixel Streaming 2 的官方继任者，适用于所有需要 WebRTC 流式传输的场景

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming2)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)
- [WebRTC 可伸缩性模式参考](https://www.w3.org/TR/webrtc-svc/#scalabilitymodes)
- [WebRTC Field Trials 文档](https://webrtc.googlesource.com/src/+/HEAD/g3doc/field-trials.md)