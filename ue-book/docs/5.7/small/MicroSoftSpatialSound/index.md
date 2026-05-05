# MicrosoftSpatialSound

> Audio spatialization plugin using Microsoft's SASAPI service.

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | 是 |
| 包含内容 | 否 |
| 模块 | MicrosoftSpatialSound (Runtime, PreDefault) |
| 创建时间 | 2019-06-10 |
| 年龄标签 | 👴 老古董(>5年) |
| 支持平台 | Win64 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MicrosoftSpatialAudio) | |

## 用途

MicrosoftSpatialSound 是 UE5 的空间音频插件，将 Unreal 的音频空间化处理接入 Microsoft 的 **Spatial Audio Client API (SASAPI)**。该 API 是 Windows 10 (1809+) 内置的空间音频框架，支持 **Windows Sonic for Headphones**、**Dolby Atmos for Headphones** 等空间音频输出方案。

插件的核心作用是：当 UE 的音频系统需要渲染 3D 空间化音源时，不使用引擎自带的 HRTF 处理，而是将音频数据通过 Microsoft Spatial Audio Client 交由 Windows 系统层进行空间化渲染。音频对象的 3D 位置会被映射到 SASAPI 坐标系，由系统在耳机或扬声器上生成沉浸式空间声场。

与 UE 内置空间化不同，该插件使用 **外部渲染管线 (IsExternalSend=true)**，在独立线程 (`MicrosoftSpatialAudioThread`) 上驱动 SASAPI 渲染循环，通过环形缓冲区将音频数据从引擎音频线程传递到 SASAPI 渲染线程。

## 使用场景

- 你在开发 **Windows 平台游戏**，希望利用 Windows Sonic / Dolby Atmos 等系统级空间音频方案
- 你的目标是 **HoloLens / MR 设备** 的空间音频渲染（尽管 HoloLens 支持已在 2025 年移除）
- 你想为 Windows 平台提供开箱即用的耳机空间音频体验，无需额外授权费用（Windows Sonic 免费）

## 蓝图用法

该插件不暴露任何 BlueprintCallable 函数。它是纯底层音频空间化实现，通过 UE 的音频插件系统自动注册和使用。

### 启用方式

1. 进入 **Edit → Project Settings → Platforms → Windows → Audio**
2. 将 **Spatialization Plugin** 设置为 **Microsoft Spatial Sound**

或者通过 `DefaultEngine.ini`：

```ini
[Audio]
SpatializationPlugin=MicrosoftSpatialSound
```

### 注意事项

- 必须在 Windows 系统设置中启用 **Windows Sonic for Headphones**（或其他空间音频方案），否则 `MaxDynamicObjects` 为 0，无法播放任何空间化音源
- 插件会在日志中输出警告：`Microsoft Spatial Sound has zero MaxDynamicObjects`
- 插件仅支持 **Win64** 平台，在其他平台上不可用

## C++ 用法

该插件是纯运行时模块，不需要在项目代码中直接调用。其接口通过 UE 的 `IAudioSpatialization` / `IAudioSpatializationFactory` 系统自动集成。

### 头文件引入

```cpp
// 仅当需要引用插件内部类型时才需要
#include "MicrosoftSpatialSoundPlugin.h"
```

### 插件注册机制

插件通过 `IModularFeatures` 注册空间化工厂：

```cpp
// 模块启动时自动注册
IModularFeatures::Get().RegisterModularFeature(
    FMicrosoftSpatialSoundPluginFactory::GetModularFeatureName(), 
    &PluginFactory
);
```

工厂类 `FMicrosoftSpatialSoundPluginFactory` 提供以下特性：
- **GetDisplayName()**: 返回 `"Microsoft Spatial Sound"`
- **SupportsPlatform()**: 支持 `Windows` 和 `XboxOne`
- **IsExternalSend()**: 返回 `true`（音频数据在外部线程渲染）

### 数据流架构

```
Audio Thread → ProcessAudio() → 环形缓冲区 → SASAPI 渲染线程
                                               ↓
                               SpatialAudioClient::BeginUpdating()
                               遍历所有活动音源对象
                               从环形缓冲区读取音频
                               设置位置（带线性插值）
                               SpatialAudioClient::EndUpdating()
```

### 坐标系转换

插件自动将 Unreal 坐标转换为 SASAPI 坐标：

```cpp
// Unreal (X=Forward, Y=Right, Z=Up) → SASAPI (X=Right, Y=Forward, Z=Down)
static FVector UnrealToMicrosoftSpatialSoundCoordinates(
    const FVector& Input, float InDistance)
{
    return { 
        0.01f * Input.Y * InDistance,   // SASAPI X = Unreal Y (scaled to meters)
        0.01f * Input.X * InDistance,   // SASAPI Y = Unreal X
        -0.01f * Input.Z * InDistance   // SASAPI Z = -Unreal Z
    };
}
```

单位从 Unreal 单位（厘米）转换为米（×0.01）。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `AudioExtensions` | UE 音频插件扩展框架（IAudioSpatialization 接口） |
| `CoreUObject` | UObject 系统（私有依赖） |
| `Engine` | 引擎核心（私有依赖） |

### 第三方依赖

| 库 | 用途 |
|---|---|
| `SpatialAudioClientInterop` | Microsoft Spatial Audio Client 的 C++ 封装层，位于 `Engine/Binaries/ThirdParty/SpatialAudioClientInterop/` |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-05-23 | `46329b5` | Abstracting _M_ARM64 and _M_ARM64EC | 将 ARM64 架构检测逻辑抽象化，支持 ARM64 和 ARM64EC 两种变体 |
| 2025-05-02 | `c12702d` | Fix TARGET_ARCH for arm64ec | 修复 ARM64EC 平台的架构字符串，确保正确加载对应的第三方 DLL |
| 2025-04-01 | `e441fd6` | Hololens removal | 移除 HoloLens 平台相关的遗留代码和条件编译宏 |

### 维护评价

- **创建时间**: 2019 年 6 月，已存在约 7 年
- **最近更新**: 2025 年 5 月，近期有活跃更新
- **更新性质**: 近期更新主要是平台适配（ARM64EC）和代码清理（HoloLens 移除），无功能增强
- **代码规模**: 极小（2 个源文件），实现简洁直接
- **稳定性**: 代码成熟，接口稳定，无需频繁改动

**综合评价**: 插件处于 **维护中** 状态。代码虽小但功能完整，近期有平台适配更新说明仍在维护范围内。作为 Windows 平台的空间音频方案，它提供了开箱即用的系统级空间化支持，适合 Windows 平台项目使用。但需注意：

1. 仅支持 Win64，跨平台项目需要备用方案
2. 依赖 Windows 系统的空间音频设置（Windows Sonic 等）
3. HoloLens 支持已被移除

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MicrosoftSpatialAudio)
- [SpatialAudioClientInterop 第三方库](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/ThirdParty/SpatialAudioClientInterop)
- [IAudioSpatialization 接口文档](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Source/Runtime/AudioExtensions/Public/IAudioExtensionPlugin.h)
