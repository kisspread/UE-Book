# Windows DualShock

> InputDevice plugin for the PS4 DualShock controller in Windows

| 属性 | 值 |
|---|---|
| 中文名 | PS4 手柄支持 |
| 分类 | Input Devices |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `WinDualShock` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-06-23 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Windows/WinDualShock) | |

## 用途

在 Windows 平台上提供 Sony PS4 DualShock 4 手柄的完整支持，包括：

1. **手柄输入**：通过 Sony 原生 SDK（`<pad.h>`）读取 DualShock 4 的按键、摇杆输入
2. **手柄音频输出**：将游戏音频路由到 DualShock 4 手柄的内置扬声器或耳机插孔
3. **空间音频**：支持通过手柄进行空间音频渲染（包含 Spread、Priority 等控制）
4. **力反馈（振动）**：支持手柄振动马达的力反馈控制

该插件通过 `#ifdef DUALSHOCK4_SUPPORT` 条件编译守卫，仅在编译环境具备 Sony SDK 时才生效。由于依赖 Sony 专有 SDK，需要在项目设置中**手动启用**。

## 使用场景

- 你在 PC 上开发 PS4/PS5 游戏，需要测试 DualShock 4 手柄的完整功能 → 启用 WinDualShock
- 你希望游戏音频通过 DualShock 4 手柄内置扬声器播放（如语音提示、特殊音效）→ 使用本插件的音频端点
- 你需要在 Windows 上精确控制 DualShock 4 手柄的振动反馈 → 使用本插件的力反馈通道
- 你正在做手柄支持的游戏，需要同时支持 Xbox 和 DualShock → 在 Xbox 输入的基础上叠加本插件

## 蓝图用法

本插件主要在引擎层面运行，蓝图暴露的 API 较少。核心暴露内容为音频端点的**设置属性**，用于在音频混合器中配置 DualShock 手柄作为音频输出设备。

### 核心设置类

| 类名 | 用途 |
|---|---|
| `UDualShockExternalEndpointSettings` | 配置将音频输出到手柄扬声器/耳机 |
| `UDualShockSoundfieldEndpointSettings` | 配置手柄的声场端点（支持空间音频） |
| `UDualShockSpatializationSettings` | 配置手柄空间音频参数 |

### 音频端点设置（属性）

| 属性 | 类型 | 说明 | 所在类 |
|---|---|---|---|
| `ControllerIndex` | `int32` | 目标手柄的控制器索引 | `UDualShockExternalEndpointSettings` / `UDualShockSoundfieldEndpointSettings` |
| `Spread` | `float` | 空间音频扩散角度（0 ~ 2π） | `UDualShockSpatializationSettings` |
| `Priority` | `int32` | 空间音频渲染优先级（0 ~ 1000） | `UDualShockSpatializationSettings` |
| `Passthrough` | `bool` | 是否透传（跳过空间化处理） | `UDualShockSpatializationSettings` |

### 使用示例（蓝图描述）

在编辑器中使用 DualShock 手柄作为音频输出：

1. 打开 **Project Settings → Platforms → Windows → Audio**
2. 在音频输出设备配置中，选择 DualShock 相关的 Endpoint 类型
3. 创建 `UDualShockExternalEndpointSettings` 实例，设置 `ControllerIndex` 为 `0`（第一个手柄）
4. 在音频混合器子混音（Submix）中将输出路由到该端点
5. 游戏音频将通过 DualShock 4 手柄的内置扬声器或已连接的耳机播放

## C++ 用法

### 头文件引入

```cpp
// 公共设置类
#include "WinDualShockSettings.h"
```

### 基本用法：配置手柄音频输出设置

```cpp
// 创建 DualShock 外部音频端点设置
UDualShockExternalEndpointSettings* EndpointSettings = NewObject<UDualShockExternalEndpointSettings>();
EndpointSettings->ControllerIndex = 0; // 第一个 DualShock 手柄

// 获取代理设置（用于运行时音频管线）
TUniquePtr<IAudioEndpointSettingsProxy> Proxy = EndpointSettings->GetProxy();
```

### 基本用法：配置空间音频

```cpp
// 创建 DualShock 空间音频设置
UDualShockSpatializationSettings* SpatialSettings = NewObject<UDualShockSpatializationSettings>();
SpatialSettings->Spread = 3.14f;    // 半圆扩散（弧度）
SpatialSettings->Priority = 100;     // 高优先级
SpatialSettings->Passthrough = false; // 启用空间化

// 获取编码设置代理
TUniquePtr<ISoundfieldEncodingSettingsProxy> EncodingProxy = SpatialSettings->GetProxy();
```

### 进阶用法：自定义音频端点访问内部设备

该插件的内部音频设备接口 `IWinDualShockAudioDevice` 使用端点引用计数管理音频会话：

```cpp
// 端点添加时的引用计数（由插件内部自动管理）
// AddEndpoint 返回 true 表示这是该端口类型的首个端点
bool bIsFirstEndpoint = AudioDevice->AddEndpoint(EWinDualShockPortType::PadSpeakers);

// 通过 PushAudio 向手柄推送音频帧
// 采样率：48000Hz，帧数：256/帧
AudioDevice->PushAudio(
    EWinDualShockPortType::PadSpeakers,
    AudioData,    // TArrayView<const float>
    NumChannels   // 2（立体声）
);

// 用完后移除端点引用
AudioDevice->RemoveEndpoint(EWinDualShockPortType::PadSpeakers);
```

**音频默认参数**（`EWinDualShockDefaults`）：

| 参数 | 值 |
|---|---|
| 采样率 | 48000 Hz |
| 每帧采样数 | 256 |
| 手柄扬声器通道数 | 2 |
| 振动通道数 | 2 |
| 队列深度 | 4 |

## Demo 示例

### 音频端点设置示例

```cpp
// DualShockAudioExample.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "DualShockAudioExample.generated.h"

UCLASS()
class UDualShockAudioExampleSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    /** 在手柄扬声器上播放测试音频 */
    UFUNCTION(BlueprintCallable, Category = "DualShock|Audio")
    void SetupDualShockSpeakerOutput(int32 ControllerIndex);

    /** 获取手柄空间音频设置 */
    UFUNCTION(BlueprintCallable, Category = "DualShock|Audio")
    UDualShockSpatializationSettings* GetSpatialSettings() const;

private:
    UPROPERTY()
    UDualShockExternalEndpointSettings* EndpointSettings = nullptr;

    UPROPERTY()
    UDualShockSpatializationSettings* SpatialSettings = nullptr;
};
```

```cpp
// DualShockAudioExample.cpp
#include "DualShockAudioExample.h"
#include "WinDualShockSettings.h"

void UDualShockAudioExampleSubsystem::SetupDualShockSpeakerOutput(int32 ControllerIndex)
{
    // 创建端点设置
    EndpointSettings = NewObject<UDualShockExternalEndpointSettings>();
    EndpointSettings->ControllerIndex = ControllerIndex;

    // 获取运行时代理（用于传递给音频混合器）
    TUniquePtr<IAudioEndpointSettingsProxy> Proxy = EndpointSettings->GetProxy();

    UE_LOG(LogTemp, Log, TEXT("DualShock speaker output configured for controller %d"), ControllerIndex);
}

UDualShockSpatializationSettings* UDualShockAudioExampleSubsystem::GetSpatialSettings() const
{
    if (!SpatialSettings)
    {
        SpatialSettings = NewObject<UDualShockSpatializationSettings>();
        SpatialSettings->Spread = 1.0f;
        SpatialSettings->Priority = 0;
        SpatialSettings->Passthrough = false;
    }
    return SpatialSettings;
}
```

## 模块依赖

Build.cs 未在提供的文件中包含，以下依赖基于源码 `#include` 推断：

| 模块 | 用途 |
|---|---|
| `AudioMixer` | 音频混合器后端（Endpoint/Soundfield 接口） |
| `AudioExtensions` | 音频端点扩展接口（`IAudioEndpointSettingsProxy` 等） |

此外，插件通过第三方头文件链接 **Sony DualShock 4 SDK**（`<pad.h>`, `<pad_audio.h>`），编译时需要 Sony SDK 可用（`DUALSHOCK4_SUPPORT` 宏）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-29 | `5697202b` | WinDualShock: dedupe XAudio2 init-failure warnings to stop log spam | 修复 XAudio2 初始化失败时日志重复刷屏 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移到新版 UE_LOGF 日志宏 |
| 2026-04-09 | `810fdfcc` | [Win Dual Shock] Only create the audio endpoint submix for the WinDualShock plugin if it is a prefer | 仅在首选时才为插件创建音频端点子混音 |
| 2026-04-01 | `1afb0871` | [Input] Add a thread affinitiy for input for IInputDevice so that we can specify which input modules | 为输入设备添加线程亲和性设置 |
| 2026-03-26 | `2cdca0c0` | [Input] FInputDeviceScope refactor and deprecation. | 输入设备作用域重构及废弃旧接口 |

### 维护评价

- **创建时间**：2020 年 6 月，约 6 年历史
- **活跃程度**：活跃维护中。2026 年有多次更新，包括日志优化、音频端点行为改进和输入系统重构适配
- **平台限制**：仅支持 Win64，依赖 Sony 专有 SDK（`DUALSHOCK4_SUPPORT` 宏），未安装 Sony SDK 时不会编译
- **启用方式**：`EnabledByDefault = false`，需要在项目设置中手动启用
- **建议**：如果你的游戏需要在 Windows 上支持 DualShock 4 手柄（特别是音频输出功能），该插件是官方推荐方案。由于依赖 Sony SDK，请确保编译环境已正确配置。在 UE 5.x 中持续得到维护，推荐使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Windows/WinDualShock)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Windows/WinDualShock)（未发现独立测试文件）