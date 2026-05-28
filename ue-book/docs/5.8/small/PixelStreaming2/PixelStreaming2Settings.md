# Pixel Streaming 2

> Streaming of Unreal Engine audio and rendering to WebRTC-compatible media players such as a web browsers.

| 属性 | 值 |
|---|---|
| 中文名 | 像素流 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PixelStreaming2` (Runtime), `PixelStreaming2Core` (Runtime), `PixelStreaming2Editor` (Runtime), `PixelStreaming2HMD` (Runtime), `PixelStreaming2Input` (Runtime), `PixelStreaming2RTC` (Runtime), `PixelStreaming2Servers` (Runtime), `PixelStreaming2Settings` (Runtime), `EpicRtc` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-09-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming2) | |

## 用途

Pixel Streaming 2 是 Epic Games 推出的第二代像素流技术，用于将 Unreal Engine 的实时画面和音频通过 WebRTC 协议传输到浏览器或其他兼容的媒体播放器。与第一代相比，PS2 采用模块化架构设计，集成了自研的 EpicRtc 替代原生 WebRTC 库，并提供了更灵活的配置系统。

该插件解决的核心问题：**让用户无需安装客户端即可在浏览器中体验 UE 应用**，适用于云游戏、远程渲染、数字孪生、XR 流式传输等场景。

**主要特性**：
- 基于 EpicRtc 的 WebRTC 实现，支持 H264、VP8、VP9、AV1 编解码器
- 支持 Simulcast（多分辨率同时编码）
- 内置编辑器内流式预览功能
- 支持 HMD/XR 流式传输
- 内置信令服务器，支持远程部署
- 丰富的编码器和 WebRTC 配置选项

## 使用场景

- **云游戏平台**：将 UE 游戏画面流式传输到玩家浏览器，无需下载客户端
- **远程渲染**：在高性能服务器上运行 UE，通过浏览器远程访问渲染结果
- **数字孪生**：将工业仿真场景通过浏览器展示给多方协作
- **XR 流式传输**：将 VR/AR 内容流式传输到轻量级 XR 设备
- **编辑器预览**：在编辑器中直接启动流式服务，快速测试像素流效果
- **演示展示**：无需部署完整客户端即可向客户展示 UE 项目

## 蓝图用法

本模块（PixelStreaming2Settings）主要提供配置管理功能，蓝图 API 较少。像素流的核心蓝图功能分布在其他模块中。

### 核心节点

本模块不暴露蓝图可调用函数，但提供大量编辑器可配置属性，可通过 **项目设置 → Pixel Streaming 2** 访问。

| 属性 | 说明 | 所在类 |
|---|---|---|
| `EnablePixelStreamingToolbar` | 启用/禁用像素流工具栏 | `UPixelStreaming2PluginSettings` |
| `AutoStartStream` | 自动开始流式传输 | `UPixelStreaming2PluginSettings` |
| `ConnectionURL` | 信令服务器连接地址 | `UPixelStreaming2PluginSettings` |
| `WebRTCFps` | WebRTC 编码帧率 | `UPixelStreaming2PluginSettings` |
| `Codec` | 首选编码器（H264/VP8/VP9/AV1） | `UPixelStreaming2PluginSettings` |

### 配置方式

1. **编辑器配置**：在 `项目设置 → Plugins → Pixel Streaming 2` 中修改
2. **配置文件**：修改 `DefaultGame.ini` 中 `[PixelStreaming]` 段
3. **命令行参数**：通过 `-PixelStreaming` 开头的参数覆盖
4. **控制台变量**：运行时通过 CVar 动态调整

## C++ 用法

### 头文件引入

```cpp
#include "PixelStreaming2Settings/Internal/PixelStreaming2PluginSettings.h"
#include "PixelStreaming2Settings/Public/PixelStreaming2SettingsEnums.h"
```

### 基本用法 - 访问设置

```cpp
// 获取 Pixel Streaming 2 设置实例
UPixelStreaming2PluginSettings* Settings = GetMutableDefault<UPixelStreaming2PluginSettings>();

// 读取当前编码器配置
int32 TargetBitrate = Settings->EncoderTargetBitrate;
int32 MaxQuality = Settings->EncoderMaxQuality;
EAVPreset Preset = Settings->QualityPreset;

// 读取 WebRTC 配置
int32 Fps = Settings->WebRTCFps;
int32 MinBitrate = Settings->WebRTCMinBitrate;
int32 MaxBitrate = Settings->WebRTCMaxBitrate;
```

### 进阶用法 - 监听设置变更

```cpp
// 监听编码器设置变更
UPixelStreaming2PluginSettings::Delegates()->OnScalabilityModeChanged.AddLambda(
    [](IConsoleVariable* CVar)
    {
        UE_LOG(LogTemp, Log, TEXT("Scalability mode changed: %s"), *CVar->GetString());
    }
);

// 监听比特率变更
UPixelStreaming2PluginSettings::Delegates()->OnWebRTCBitrateChanged.AddLambda(
    [](IConsoleVariable* CVar)
    {
        UE_LOG(LogTemp, Log, TEXT("Bitrate changed: %d"), CVar->GetInt());
    }
);
```

### 进阶用法 - 自定义编码器设置

```cpp
// 运行时修改编码器设置
IConsoleVariable* CodecCVar = IConsoleManager::Get().FindConsoleVariable(TEXT("PixelStreaming2.EncoderCodec"));
if (CodecCVar)
{
    CodecCVar->Set(TEXT("H264"));
}

// 配置 Simulcast（需要 SFU 支持）
IConsoleVariable* SimulcastCVar = IConsoleManager::Get().FindConsoleVariable(TEXT("PixelStreaming2.EncoderEnableSimulcast"));
if (SimulcastCVar)
{
    SimulcastCVar->Set(true);
}

// 设置 H264 Profile
IConsoleVariable* ProfileCVar = IConsoleManager::Get().FindConsoleVariable(TEXT("PixelStreaming2.EncoderH264Profile"));
if (ProfileCVar)
{
    ProfileCVar->Set(TEXT("Main"));
}
```

### 进阶用法 - WebRTC Field Trials

```cpp
// 配置 WebRTC Field Trials 以优化性能
IConsoleVariable* FieldTrialsCVar = IConsoleManager::Get().FindConsoleVariable(TEXT("PixelStreaming2.WebRTCFieldTrials"));
if (FieldTrialsCVar)
{
    // 禁用帧丢弃器
    FieldTrialsCVar->Set(TEXT("WebRTC-FrameDropper/Disabled/"));
}

// 或者通过专用 CVar
IConsoleVariable* DisableFrameDropper = IConsoleManager::Get().FindConsoleVariable(TEXT("PixelStreaming2.WebRTCDisableFrameDropper"));
if (DisableFrameDropper)
{
    DisableFrameDropper->Set(true);
}
```

## Demo 示例

### 自定义像素流启动器

```cpp
// MyPixelStreamingStarter.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyPixelStreamingStarter.generated.h"

UCLASS()
class AMyPixelStreamingStarter : public AActor
{
    GENERATED_BODY()

public:
    AMyPixelStreamingStarter();

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    // 动态调整流参数
    UFUNCTION(BlueprintCallable, Category = "Pixel Streaming")
    void SetBitrate(int32 NewBitrate);

    UFUNCTION(BlueprintCallable, Category = "Pixel Streaming")
    void SetCodec(const FString& NewCodec);

protected:
    // 监听流事件
    void OnStatsUpdated();
    void OnConnectionStateChanged(bool bConnected);

private:
    FDelegateHandle StatsDelegateHandle;
    FDelegateHandle ConnectionDelegateHandle;
};
```

```cpp
// MyPixelStreamingStarter.cpp
#include "MyPixelStreamingStarter.h"
#include "PixelStreaming2Settings/Internal/PixelStreaming2PluginSettings.h"

AMyPixelStreamingStarter::AMyPixelStreamingStarter()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyPixelStreamingStarter::BeginPlay()
{
    Super::BeginPlay();

    // 获取设置并配置
    UPixelStreaming2PluginSettings* Settings = GetMutableDefault<UPixelStreaming2PluginSettings>();
    if (Settings)
    {
        // 设置编码参数
        Settings->WebRTCFps = 60;
        Settings->WebRTCMinBitrate = 500000;
        Settings->WebRTCMaxBitrate = 20000000;
        Settings->QualityPreset = EAVPreset::HighQuality;
        Settings->LatencyMode = EAVLatencyMode::LowLatency;
        
        UE_LOG(LogTemp, Log, TEXT("Pixel Streaming configured: %d FPS, Quality: HighQuality"), Settings->WebRTCFps);
    }

    // 监听性能统计更新
    StatsDelegateHandle = UPixelStreaming2PluginSettings::Delegates()->OnLogStatsChanged.AddLambda(
        [this](IConsoleVariable* CVar)
        {
            OnStatsUpdated();
        }
    );
}

void AMyPixelStreamingStarter::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    // 清理委托
    if (StatsDelegateHandle.IsValid())
    {
        UPixelStreaming2PluginSettings::Delegates()->OnLogStatsChanged.Remove(StatsDelegateHandle);
    }

    Super::EndPlay(EndPlayReason);
}

void AMyPixelStreamingStarter::SetBitrate(int32 NewBitrate)
{
    IConsoleVariable* BitrateCVar = IConsoleManager::Get().FindConsoleVariable(
        TEXT("PixelStreaming2.WebRTCMaxBitrate")
    );
    if (BitrateCVar)
    {
        BitrateCVar->Set(NewBitrate);
        UE_LOG(LogTemp, Log, TEXT("Pixel Streaming bitrate set to: %d"), NewBitrate);
    }
}

void AMyPixelStreamingStarter::SetCodec(const FString& NewCodec)
{
    IConsoleVariable* CodecCVar = IConsoleManager::Get().FindConsoleVariable(
        TEXT("PixelStreaming2.EncoderCodec")
    );
    if (CodecCVar)
    {
        CodecCVar->Set(NewCodec);
        UE_LOG(LogTemp, Log, TEXT("Pixel Streaming codec set to: %s"), *NewCodec);
    }
}

void AMyPixelStreamingStarter::OnStatsUpdated()
{
    UE_LOG(LogTemp, Log, TEXT("Pixel Streaming stats updated"));
}

void AMyPixelStreamingStarter::OnConnectionStateChanged(bool bConnected)
{
    UE_LOG(LogTemp, Log, TEXT("Pixel Streaming connection state: %s"), 
        bConnected ? TEXT("Connected") : TEXT("Disconnected"));
}
```

### 构建配置（Build.cs）

```csharp
// YourModule.Build.cs
using UnrealBuildTool;

public class YourModule : ModuleRules
{
    public YourModule(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        
        PublicDependencyModuleNames.AddRange(new string[]
        {
            "Core",
            "CoreUObject",
            "Engine",
            "PixelStreaming2Settings"
        });
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PixelStreaming2Core` | 像素流核心框架，提供基础类型和接口 |
| `PixelStreaming2RTC` | WebRTC 通信层，基于 EpicRtc |
| `PixelStreaming2Input` | 输入处理，将浏览器输入转发到 UE |
| `PixelStreaming2Servers` | 内置信令和转发服务器 |
| `PixelStreaming2HMD` | HMD/XR 流式传输支持 |
| `PixelStreaming2Editor` | 编辑器内流式预览功能 |
| `EpicRtc` | Epic 自研 WebRTC 实现 |
| `VulkanRHI` | Vulkan 渲染后端支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `c1dab3e1` | [PixelStreaming2] Fix: Input handler obtaining default target window from wrong method | 修复输入处理器从错误方法获取默认目标窗口的问题 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 产生的警告 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 虚拟制作：将 VP 资源迁移至不同资产分类 |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 FJsonObject 以同时支持 FString 和 UE::FSharedString |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复格式化函数中作用域枚举可能导致的乱码输出 |

### 维护评价

**活跃维护** ⭐⭐⭐⭐⭐

- **创建时间**：2024-09-04，约 1 年历史，是较新的插件
- **更新频率**：最近 1 个月内有多次实质性更新，维护非常活跃
- **更新质量**：包含功能改进、bug 修复、代码重构，迭代质量高
- **开发者**：Epic Games 官方维护，有长期支持保障
- **架构优势**：模块化设计清晰，9 个独立模块职责分明
- **默认启用**：否，需要手动启用，说明仍在完善中
- **推荐使用**：✅ 推荐用于生产环境，特别是需要 WebRTC 流式传输的项目

**注意事项**：
- 这是 Pixel Streaming 的第二代实现，与第一代 PS 不完全兼容
- 使用了 EpicRtc 替代原生 WebRTC，可能与第三方 WebRTC 工具不兼容
- 编辑器内流式传输需要额外配置

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming2)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming2/Tests)