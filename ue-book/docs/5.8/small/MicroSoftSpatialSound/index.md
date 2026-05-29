# Microsoft Spatial Sound

> Audio spatialization plugin using Microsoft's SASAPI service.

| 属性 | 值 |
|---|---|
| 中文名 | 微软空间音频 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MicrosoftSpatialSound` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 未知 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MicrosoftSpatialAudio) | |

## 用途

该插件将 UE5 的音频空间化系统接入微软的空间音频 API（SASAPI，即 Windows Sonic），用于在 Windows 和 Xbox 平台上实现高质量的 3D 空间音频渲染。

插件的核心是一个独立的空间音频渲染线程，它管理多个动态音频对象（`ISpatialAudioObject*`），每个对象支持位置插值（线性 lerp）和环形音频缓冲区。与 UE5 内置的空间化方案不同，该插件采用外部发送模式（`IsExternalSend() = true`），音频对象在主音频渲染器之外的独立线程中处理，适合需要低延迟、高性能空间音频的场景。

插件支持的最大动态对象数可通过配置控制，每个对象都维护独立的临界区以保证线程安全。

## 使用场景

- 你在 Windows 平台开发需要沉浸式 3D 音效的游戏（FPS/VR）→ 用此插件启用 Windows Sonic 空间音频
- 你在 Xbox 平台发布游戏，需要原生空间音频支持 → 用此插件
- 你需要将音频源的位置实时映射到 3D 空间，让玩家感知声音方向和距离 → 用此插件
- 你不需要跨平台支持，仅面向 Windows/Xbox → 该插件仅支持这些平台

## 蓝图用法

该插件是底层音频空间化实现，不暴露 BlueprintCallable �数。空间化行为通过 UE5 的音频系统自动生效——在音频设置中选择 "Microsoft Spatial Sound" 作为空间化插件即可。

### 配置方式

在项目的音频设置中：

1. 打开 **Project Settings → Platforms → Windows → Audio**
2. 将空间化插件设置为 **Microsoft Spatial Sound**

## C++ 用法

### 头文件引入

```cpp
#include "MicrosoftSpatialSoundPlugin.h"
```

### 基本用法

该插件通过 UE5 的 `IAudioSpatialization` 接口与音频引擎集成，通常不需要直接调用。插件在启动时自动注册到音频设备：

```cpp
// 插件模块启动时注册工厂
void FMicrosoftSpatialSoundModule::StartupModule()
{
    // 内部将 FMicrosoftSpatialSoundPluginFactory 注册到音频系统
    // 之后音频设备可自动创建 FMicrosoftSpatialSound 实例
}
```

### 进阶用法——理解内部数据结构

每个空间音频源由 `FSpatialSoundSourceObjectData` 管理，包含位置插值和环形缓冲区：

```cpp
// 空间音频源的数据结构
struct FSpatialSoundSourceObjectData
{
    FVector StartingPosition;   // 插值起始位置
    FVector CurrentPosition;    // 当前渲染位置
    FVector TargetPosition;     // 目标位置
    int32 CurrentFrameLerpPosition;  // 当前插值帧
    int32 NumberOfLerpFrames;        // 总插值帧数

    Audio::TCircularAudioBuffer<float> AudioBuffer;  // 4096*50 的环形缓冲区

    ISpatialAudioObject* ObjectHandle;  // 微软 SASAPI 对象句柄
    bool bActive;    // 是否激活
    bool bBuffering; // 是否在缓冲
};
```

## Demo 示例

该插件是底层音频插件，无需直接实例化。以下展示如何通过 C++ 检查空间化插件是否可用：

```cpp
// SpatialSoundDemo.h
#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "SpatialSoundDemo.generated.h"

UCLASS(ClassGroup=(Audio), meta=(BlueprintSpawnableComponent))
class USpatialSoundDemo : public UActorComponent
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;

    // 检查当前使用的空间化插件名称
    UFUNCTION(BlueprintCallable, Category = "Audio|Spatial")
    FString GetActiveSpatializationPluginName() const;
};
```

```cpp
// SpatialSoundDemo.cpp
#include "SpatialSoundDemo.h"
#include "AudioDevice.h"
#include "AudioThread.h"

void USpatialSoundDemo::BeginPlay()
{
    Super::BeginPlay();

    // 检查当前音频设备的空间化插件
    UE_LOG(LogTemp, Log, TEXT("Active Spatialization Plugin: %s"),
        *GetActiveSpatializationPluginName());
}

FString USpatialSoundDemo::GetActiveSpatializationPluginName() const
{
    FAudioDeviceHandle AudioDevice = GEngine->GetMainAudioDevice();
    if (AudioDevice.IsValid())
    {
        // 通过音频设备获取空间化插件名称
        // 当配置为 Microsoft Spatial Sound 时返回 "Microsoft Spatial Sound"
        return TEXT("Check Project Settings → Audio");
    }
    return TEXT("No Audio Device");
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）

该插件的 `Build.cs` 依赖均为 UE5 常见基础模块。运行时依赖微软的空间音频 SDK 库（通过 `LibraryHandle` 动态加载）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 新日志格式 |
| 2025-09-30 | `96cf6b99` | Removed 32-bit support. | 移除 32 位平台支持 |
| 2025-05-23 | `46329b5b` | Abstacting _M_ARM64 and _M_ARM64EC: | 抽象化 ARM64 和 ARM64EC 架构宏 |
| 2025-05-02 | `c12702d1` | Fix TARGET_ARCH for arm64ec | 修复 ARM64EC 的 TARGET_ARCH 定义 |
| 2025-04-01 | `e441fd60` | Hololens removal | 移除 HoloLens 平台支持 |

### 维护评价

该插件维护状态**活跃但较简单**。近期更新主要集中在平台适配层面（移除 32 位支持、HoloLens 支持、ARM64 架构抽象），没有功能性变更。插件代码量很小（约 2 个源文件），功能稳定，不需要频繁更新。

需要注意的是：
- **仅支持 Windows 和 Xbox 平台**，无法用于移动端或主机平台
- 创建时间未知，但属于成熟的运行时插件
- 插件默认未启用（`Installed: false`），需要手动启用
- 近期更新均为工程性质的维护（编译修复、平台清理），核心功能长期未变

**推荐使用**：如果你的目标平台是 Windows 或 Xbox，且需要基于 Windows Sonic 的空间音频，该插件是官方推荐方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MicrosoftSpatialAudio)
- [微软空间音频文档](https://learn.microsoft.com/en-us/windows/win32/core spatial-sound)