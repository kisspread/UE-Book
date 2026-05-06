# Pixel Streaming 2

> Streaming of Unreal Engine audio and rendering to WebRTC-compatible media players such as a web browsers.

| 属性 | 值 |
|---|---|
| 中文名 | 像素流 2 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（C++ 模块、蓝图函数库、编辑器设置） |
| 模块 | `PixelStreaming2` (Runtime), `PixelStreaming2Core` (Runtime), `PixelStreaming2Editor` (Runtime), `PixelStreaming2HMD` (Runtime), `PixelStreaming2Input` (Runtime), `PixelStreaming2RTC` (Runtime), `PixelStreaming2Servers` (Runtime), `PixelStreaming2Settings` (Runtime), `EpicRtc` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-10-13 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming2) | |

## 用途

Pixel Streaming 2 是虚幻引擎 5.5 引入的新一代像素流（Pixel Streaming）解决方案。它将引擎中的音频、渲染输出以及输入事件通过 **EpicRtc**（自研 WebRTC 实现）实时流式传输到浏览器等 WebRTC 兼容接收端。相比旧版 Pixel Streaming，Pixel Streaming 2 带来了更低的延迟、更高的吞吐量、更好的网络适应能力以及对 H.264/H.265 等编解码器的原生支持。

该插件由多个子模块组成：

- **PixelStreaming2** – 流式传输的核心逻辑（渲染、编码、发送）
- **PixelStreaming2Core** – 基础工具与抽象
- **PixelStreaming2Editor** – 编辑器内流式传输支持
- **PixelStreaming2HMD** – VR 头显的流式适配
- **PixelStreaming2Input** – 输入事件（键盘、鼠标、触屏）的转发
- **PixelStreaming2RTC** – WebRTC 信令与连接管理
- **PixelStreaming2Servers** – 信令服务器、SFU 等外部组件管理
- **PixelStreaming2Settings** – 全局配置与开发者设置（本项目重点）
- **EpicRtc** – 第三方 WebRTC 库包装

其中 **PixelStreaming2Settings** 模块负责提供所有可配置参数（通过控制台变量或项目设置暴露），是整个插件的配置枢纽。

## 使用场景

- **云游戏**：将高端 PC 上的游戏画面流式传输到低端设备，用户通过浏览器游玩。
- **远程渲染 / 虚拟桌面**：允许设计师、开发者远程操作 Unreal Editor，仅传输视口画面。
- **交互式 Web 应用**：将实时 3D 场景嵌入网页，用户可通过浏览器进行交互（如产品展示、建筑漫游）。
- **多用户协作**：多个终端同时观看同一场景，配合音频与输入反馈。

## 蓝图用法

`PixelStreaming2Settings` 模块本身不暴露任何蓝图可直接调用的函数或节点。所有配置通过 **Project Settings** > **Plugins** > **PixelStreaming2** 页面进行可视化编辑，或使用控制台变量动态调整。

### 核心设置（Project Settings 面板）

在编辑器菜单 **Edit → Project Settings → Plugins → PixelStreaming2** 可以看到以下常用分类：

| 分类 | 说明 |
|---|---|
| PixelStreaming | 基础开关与日志 |
| Audio | 音频传输配置（麦克风、监听等） |
| Input | 输入控制器模式、输入绑定 |
| Network | 信令服务器地址、端口、WebRTC 配置 |
| Video | 编解码器选择、码率、分辨率、帧率 |
| Logging | EpicRtc 内部日志过滤 |
| Simulcast | 多播流（不同分辨率层级） |
| WebRTC | ICE 服务器、端口分配器选项 |
| Streamer | 流 ID、是否自动启动等 |

这些属性 **可直接在编辑器中修改**，并保存至 `DefaultGame.ini`。无需编写蓝图代码即可生效。

### 控制台变量

以下是最常用的控制台变量（可在运行时通过命令行或蓝图的 `Execute Console Command` 节点修改）：

| 控制台变量名 | 默认值 | 说明 |
|---|---|---|
| `PixelStreaming2.LogStats` | false | 是否在日志中输出 PixelStreaming 统计 |
| `PixelStreaming2.CaptureSource` | "Backbuffer" | 捕获源（Backbuffer / SceneViewport 等） |
| `PixelStreaming2.WebRTCMaxBitrate` | 20000000 | 最大视频码率，单位 bps |
| `PixelStreaming2.WebRTCMinBitrate` | 500000 | 最小视频码率，单位 bps |
| `PixelStreaming2.Codec` | "H264" | 视频编码格式（H264 / H265 / VP8 / VP9） |
| `PixelStreaming2.FPS` | 60 | 目标帧率 |
| `PixelStreaming2.AutoStartStreaming` | false | 是否自动启动流（无需信令） |
| `PixelStreaming2.PortAllocatorFlags` | 0 | ICE 端口分配器标志位（按位组合） |

## C++ 用法

### 头文件引入

```cpp
#include "PixelStreaming2PluginSettings.h"          // 设置类与控制台变量
#include "PixelStreaming2SettingsEnums.h"            // 本模块定义的枚举
```

### 基本用法

#### 1. 读取开发者设置

```cpp
#include "PixelStreaming2PluginSettings.h"

// 获取默认设置对象（线程安全）
const UPixelStreaming2PluginSettings* Settings = GetDefault<UPixelStreaming2PluginSettings>();
if (Settings)
{
    // 读取配置属性
    bool bLogStats = Settings->LogStats;
    FString SingalingIP = Settings->SignalingServerUrl;

    // 读取枚举
    ERemoteStreamerType StreamerType = Settings->StreamerType;
}
```

*来源：`PixelStreaming2PluginSettings.h`，类 `UPixelStreaming2PluginSettings`*

#### 2. 访问控制台变量（CVar）

```cpp
#include "PixelStreaming2PluginSettings.h"

// 直接读写静态 CVar
bool bCurrentLogStats = UE::PixelStreaming2::UPixelStreaming2PluginSettings::CVarLogStats.GetValueOnAnyThread();
UE::PixelStreaming2::UPixelStreaming2PluginSettings::CVarLogStats->Set(true, ECVF_SetByCode);

// 读取枚举型 CVar（例如 codec）
FString EncoderCodec = UE::PixelStreaming2::UPixelStreaming2PluginSettings::CVarEncoderCodec.GetValueOnAnyThread();
EVideoCodec CodecEnum = UE::PixelStreaming2::GetEnumFromString<EVideoCodec>(EncoderCodec);
```

*来源：`PixelStreaming2PluginSettings.h` 中的 `TAutoConsoleVariable` 静态成员及辅助模板函数*

#### 3. 使用端口分配器标志

```cpp
#include "PixelStreaming2PluginSettings.h"

// 组合标志位
EPortAllocatorFlags Flags = EPortAllocatorFlags::DisableUdp | EPortAllocatorFlags::EnableSharedSocket;

// 转换为底层值传给 EpicRtc
uint32 RawFlags = static_cast<uint32>(Flags);
```

*来源：`PixelStreaming2PluginSettings.h` 中定义的 `EPortAllocatorFlags` 枚举（与 EpicRtc 选项对应）*

### 进阶用法

#### 在使用 EpicRtc 时动态应用设置

在自定义的 EpicRtc 适配器模块中，通常需要将 PixelStreaming2Settings 中的配置传递给 `EpicRtcConnectionConfig`：

```cpp
#include "PixelStreaming2PluginSettings.h"
#include "epic_rtc/core/connection_config.h"

void BuildConnectionConfig(EpicRtcConnectionConfig& OutConfig)
{
    const UPixelStreaming2PluginSettings* Settings = GetDefault<UPixelStreaming2PluginSettings>();
    
    // 端口分配器选项
    OutConfig.portAllocatorOptions = static_cast<EpicRtcPortAllocatorOptions>(Settings->PortAllocatorFlags);
    
    // ICE 服务器列表
    for (const FICEConnectionConfig& IceCfg : Settings->ICEServers)
    {
        FString IceUrl;
        FString Username, Credential;
        // ... 解析并添加到 OutConfig
    }
    
    // 音频/视频编解码偏好
    OutConfig.videoCodecPriority = static_cast<EpicRtcVideoCodecPriority>(Settings->CodecPriorities);
}
```

*综合应用示例，非直接源码，但反映了设置模块的典型用法。*

## Demo 示例

以下是一个最小 C++ 例子，展示如何在游戏模块启动时读取 PixelStreaming2 设置并打印关键配置。

**PS2SettingsDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FPS2SettingsDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

**PS2SettingsDemo.cpp**
```cpp
#include "PS2SettingsDemo.h"
#include "PixelStreaming2PluginSettings.h"
#include "PixelStreaming2SettingsEnums.h"
#include "Engine/DeveloperSettings.h"

void FPS2SettingsDemoModule::StartupModule()
{
    const UPixelStreaming2PluginSettings* Settings = GetDefault<UPixelStreaming2PluginSettings>();
    if (Settings)
    {
        UE_LOG(LogTemp, Log, TEXT("PixelStreaming2 Settings:"));
        UE_LOG(LogTemp, Log, TEXT("  SignalingServerUrl = %s"), *Settings->SignalingServerUrl);
        UE_LOG(LogTemp, Log, TEXT("  StreamerType = %d"), static_cast<uint8>(Settings->StreamerType));
        UE_LOG(LogTemp, Log, TEXT("  LogStats = %s"), Settings->LogStats ? TEXT("true") : TEXT("false"));
    }
}

void FPS2SettingsDemoModule::ShutdownModule()
{
}

IMPLEMENT_MODULE(FPS2SettingsDemoModule, PS2SettingsDemo)
```

**注意**：需要将 `PixelStreaming2Settings` 添加到你模块的 `PublicDependencyModuleNames` 中。

## 模块依赖

使用 `PixelStreaming2Settings` 时，你只需要依赖它本身及其必要的虚幻引擎基础模块。以下列出该模块特有的（非标配）依赖：

| 模块 | 用途 |
|---|---|
| `PixelStreaming2Core` | 提供基础类型、日志、枚举定义 |
| `EpicRtc` | 提供端口分配器选项枚举（`EpicRtcPortAllocatorOptions`） |
| `AVConfig` / `Video` | 视频编解码器配置类型（`EVideoCodec` 等） |

**注意**：实际使用中无需手动引用 `PixelStreaming2Core` 或 `EpicRtc` 的头文件，因为 `PixelStreaming2PluginSettings.h` 已包含它们。

## 维护状态

### 近期更新

- 2026-01-23 `a9928676` — [NVCodecs, PixelStreaming2] Fixes:
- 2025-11-18 `d7a4d160` — [AVCodecs, PixelStreaming2] Fixes:
- 2025-10-28 `b1db9444` — [PixelStreaming2] Fix: Deadlocks in PixelStreaming2Thread
- 2025-10-17 `5c2f039d` — [PS2] Fix: Non-functional public API
- 2025-10-13 `0de4d465` — [PS2] Bug Fixes for 5.7

### 维护评价

PixelStreaming2 是 UE5.5 引入的新功能，目前处于 **活跃维护** 阶段。创建至今不足一年，最近一次更新在 2026 年 1 月（修复问题）。更新内容包括 Bug 修复、死锁处理和非功能性 API 修正，说明开发团队正在积极完善。由于该插件仍属较新，建议使用时密切关注官方更新，并在发布前进行充分的网络与兼容性测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming2)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming2/Source/PixelStreaming2Tests)（如果存在）