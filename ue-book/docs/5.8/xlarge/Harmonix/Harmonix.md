# Harmonix

> A package of Harmonix music related audio functionality.

| 属性 | 值 |
|---|---|
| 中文名 | 音乐音频工具包 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（MetaSound 节点、MIDI 资产、音频 DSP 工具） |
| 模块 | `Harmonix` (Runtime), `HarmonixDsp` (Runtime), `HarmonixDspEditor` (Runtime), `HarmonixDspTests` (Runtime), `HarmonixEditor` (Runtime), `HarmonixMetasound` (Runtime), `HarmonixMetasoundEditor` (Runtime), `HarmonixMetasoundTests` (Runtime), `HarmonixMidi` (Runtime), `HarmonixMidiEditor` (Runtime), `HarmonixMidiTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-17 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix) | |

---

## 用途

Harmonix 插件是由 Epic Games 旗下 Harmonix GenTech 团队（Rock Band、Fortnite Festival 等音乐游戏的开发团队）开发的一套**音乐相关音频功能工具包**。它解决的核心问题是：在 UE5 中实现**专业级的音乐同步、节拍量化、MIDI 处理和音频 DSP**。

与 UE5 内置的音频系统相比，Harmonix 提供了：

- **精确的音乐时间同步**：支持多种校准时间基准（音频渲染时间、玩家感知时间、视频渲染时间），确保音频与画面完美同步
- **线程安全的音频数据代理**：通过引用计数的无锁队列系统，安全地在游戏线程和音频渲染线程之间共享设置数据
- **MetaSound 深度集成**：提供专用的 MetaSound 节点和数据代理，将音乐逻辑嵌入 MetaSound 音频图中
- **MIDI 处理**：完整的 MIDI 解析和处理能力
- **音频 DSP 处理**：专业的数字信号处理工具

简而言之，如果你在做一个**节奏游戏、音乐可视化、或任何需要精确音乐同步的项目**，Harmonix 提供了比 UE5 原生工具更专业的解决方案。

---

## 使用场景

- 你在做一个**节奏游戏**（如 Guitar Hero 风格）→ 用 Harmonix 获取精确的节拍位置和量化信息
- 你需要**音频与视频精确同步**→ 用 Harmonix 的校准时间基准系统
- 你在 MetaSound 中需要**音乐逻辑节点**→ 用 HarmonixMetasound 提供的专用节点
- 你需要**解析和播放 MIDI 文件**→ 用 HarmonixMidi 模块
- 你在做**音乐驱动的视觉效果**→ 用 Harmonix 的 DSP 分析和节拍追踪
- 你在为 Fortnite Festival 类型的**音乐会/演出系统**构建功能 → 这正是 Harmonix 设计的目标场景

---

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetMeasuredUserExperienceAndReactionToAudioRenderOffsetMs` | 设置玩家实际体验到的音频渲染偏移量（毫秒），用于校准 | `UHarmonixBlueprintUtil` |
| `GetMeasuredUserExperienceAndReactionToAudioRenderOffsetMs` | 获取当前玩家体验到的音频渲染偏移量 | `UHarmonixBlueprintUtil` |
| `SetMeasuredVideoToAudioRenderOffsetMs` | 设置视频到音频渲染的偏移量（毫秒），用于音画同步校准 | `UHarmonixBlueprintUtil` |
| `GetMeasuredVideoToAudioRenderOffsetMs` | 获取当前视频到音频渲染的偏移量 | `UHarmonixBlueprintUtil` |

所有节点位于 **Harmonix > Calibration** 分类下。

### 校准时间基准枚举

`ECalibratedMusicTimebase` 枚举提供了四种时间基准：

| 枚举值 | 用途 |
|---|---|
| `AudioRenderTime` | 音频渲染器的平滑当前位置，适合基于当前歌曲时间触发音乐事件 |
| `ExperiencedTime` | 玩家实际正在听到和看到的时间（正确校准后），适合**评分玩家输入** |
| `VideoRenderTime` | 当前应该绘制的时间点（正确校准后），适合将**动画、UI 和视觉效果**与音乐同步 |
| `RawAudioRenderTime` | 原始未平滑的音频渲染位置（有抖动），仅用于**调试** |

### 使用示例（蓝图描述）

**音频校准流程：**

1. 在游戏启动时，使用一个已知延迟的测试音频和视频来测量偏移
2. 调用 `SetMeasuredUserExperienceAndReactionToAudioRenderOffsetMs` 设置测量到的偏移值
3. 调用 `SetMeasuredVideoToAudioRenderOffsetMs` 设置视频偏移
4. 之后所有音乐同步逻辑使用 `ExperiencedTime` 或 `VideoRenderTime` 作为时间基准

---

## C++ 用法

### 头文件引入

```cpp
#include "Harmonix.h"
#include "AudioRenderableProxy.h"
#include "PropertyUtility.h"
#include "MusicalTimebase.h"
```

### 基本用法 — 校准偏移设置

```cpp
#include "Harmonix.h"

// 设置音频校准偏移
UHarmonixBlueprintUtil::SetMeasuredUserExperienceAndReactionToAudioRenderOffsetMs(50.0f);

// 设置视频校准偏移
UHarmonixBlueprintUtil::SetMeasuredVideoToAudioRenderOffsetMs(33.0f);

// 读取当前偏移值
float AudioOffset = UHarmonixBlueprintUtil::GetMeasuredUserExperienceAndReactionToAudioRenderOffsetMs();
float VideoOffset = UHarmonixBlueprintUtil::GetMeasuredVideoToAudioRenderOffsetMs();
```

### 基本用法 — 属性工具

```cpp
#include "PropertyUtility.h"

// 在 PostEditChangeChainProperty 中追踪属性变化路径
void UMyObject::PostEditChangeChainProperty(FPropertyChangedChainEvent& PropertyChangedChainEvent)
{
    // 获取变化的属性链字符串，例如 "MyBar.BazArray[3].Number = 6"
    FString PropertyPath = Harmonix::GetStructPropertyChainString(&MyStruct, PropertyChangedChainEvent);
    UE_LOG(LogTemp, Log, TEXT("Changed: %s"), *PropertyPath);
    
    // 将变化的属性复制到代理结构体（用于脏标记追踪）
    Harmonix::CopyStructProperty(&MyProxyStruct, &MyStruct, PropertyChangedChainEvent);
}
```

### 进阶用法 — 线程安全的音频数据代理系统

Harmonix 提供了一套完整的线程安全音频数据代理框架，用于在游戏线程和音频渲染线程之间安全地共享数据。

```cpp
#include "AudioRenderableProxy.h"

// 1. 定义你的音频设置结构体
USTRUCT(BlueprintType)
struct FMyAudioSettings
{
    GENERATED_BODY()
    
    // 必须添加此宏，为代理系统提供类型名
    IMPL_AUDIORENDERABLE_PROXYABLE(FMyAudioSettings)
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    float Frequency = 440.0f;
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    float Volume = 1.0f;
};

// 2. 定义代理类型
// 使用宏简写声明代理类型
USING_AUDIORENDERABLE_PROXY(FMyAudioSettings, FMyAudioSettingsProxy)

// 3. 在你的 UObject 资产中维护设置队列
UCLASS()
class UMyAudioAsset : public UObject
{
    GENERATED_BODY()

public:
    // 游戏线程到音频渲染线程的设置队列
    Harmonix::TGameThreadToAudioRenderThreadSettingQueue<FMyAudioSettings> SettingsQueue;
    
    // 更新设置（在游戏线程调用）
    void UpdateSettings(const FMyAudioSettings& NewSettings)
    {
        SettingsQueue.SetNewSettings(NewSettings);
    }
    
    // 在 MetaSound 节点或音频处理器中获取当前设置
    const FMyAudioSettings* GetCurrentSettings() const
    {
        return SettingsQueue;
    }
};
```

**代理系统的工作原理：**

1. `TGameThreadToAudioRenderThreadSettingQueue` 维护一个引用计数的设置队列尾指针
2. 当设置更新时，新设置通过 `QueueUpdate` 追加到队列
3. 音频渲染线程可以随时获取当前设置，如果检测到更新则安全地切换到新数据
4. 旧的设置数据通过引用计数自动回收，无需锁机制

---

## Demo 示例

一个完整的音频校准管理器示例：

```cpp
// MyAudioCalibrationManager.h
#pragma once

#include "CoreMinimal.h"
#include "Harmonix.h"
#include "MyAudioCalibrationManager.generated.h"

UCLASS(BlueprintType, Blueprintable)
class MYPROJECT_API UMyAudioCalibrationManager : public UObject
{
    GENERATED_BODY()

public:
    // 开始校准流程
    UFUNCTION(BlueprintCallable, Category = "Audio Calibration")
    void StartCalibration();
    
    // 校准完成后保存偏移值
    UFUNCTION(BlueprintCallable, Category = "Audio Calibration")
    void FinishCalibration(float MeasuredVideoToAudioMs, float MeasuredExperienceAndReactionMs);
    
    // 获取当前视频偏移
    UFUNCTION(BlueprintPure, Category = "Audio Calibration")
    float GetVideoOffsetMs() const;
    
    // 获取当前体验偏移
    UFUNCTION(BlueprintPure, Category = "Audio Calibration")
    float GetExperienceOffsetMs() const;

    // 获取校准后的音乐时间基准
    UFUNCTION(BlueprintCallable, Category = "Audio Calibration")
    float GetCalibratedMusicTime(ECalibratedMusicTimebase Timebase) const;
};
```

```cpp
// MyAudioCalibrationManager.cpp
#include "MyAudioCalibrationManager.h"

void UMyAudioCalibrationManager::StartCalibration()
{
    // 重置偏移值
    UHarmonixBlueprintUtil::SetMeasuredVideoToAudioRenderOffsetMs(0.0f);
    UHarmonixBlueprintUtil::SetMeasuredUserExperienceAndReactionToAudioRenderOffsetMs(0.0f);
    
    UE_LOG(LogTemp, Log, TEXT("Audio calibration started."));
}

void UMyAudioCalibrationManager::FinishCalibration(
    float MeasuredVideoToAudioMs, 
    float MeasuredExperienceAndReactionMs)
{
    // 应用测量到的偏移值
    UHarmonixBlueprintUtil::SetMeasuredVideoToAudioRenderOffsetMs(MeasuredVideoToAudioMs);
    UHarmonixBlueprintUtil::SetMeasuredUserExperienceAndReactionToAudioRenderOffsetMs(
        MeasuredExperienceAndReactionMs);
    
    UE_LOG(LogTemp, Log, 
        TEXT("Calibration complete. Video offset: %.2fms, Experience offset: %.2fms"),
        MeasuredVideoToAudioMs, MeasuredExperienceAndReactionMs);
}

float UMyAudioCalibrationManager::GetVideoOffsetMs() const
{
    return UHarmonixBlueprintUtil::GetMeasuredVideoToAudioRenderOffsetMs();
}

float UMyAudioCalibrationManager::GetExperienceOffsetMs() const
{
    return UHarmonixBlueprintUtil::GetMeasuredUserExperienceAndReactionToAudioRenderOffsetMs();
}

float UMyAudioCalibrationManager::GetCalibratedMusicTime(ECalibratedMusicTimebase Timebase) const
{
    // 具体的音乐时间获取依赖子模块（HarmonixMetasound）中的播放器接口
    // 此处为框架示例
    return 0.0f;
}
```

---

## 模块依赖

Harmonix 是一个大型插件，包含多个子模块。各子模块的依赖关系如下：

| 模块 | 用途 |
|---|---|
| `HarmonixDsp` | 音频 DSP 处理，依赖 AssetRegistry、UnrealEd |
| `HarmonixMetasound` | MetaSound 集成节点，依赖 AssetRegistry、UnrealEd |
| `HarmonixMidi` | MIDI 解析与处理，依赖 AssetRegistry、UnrealEd |

> **注意**：核心 `Harmonix` 模块无特殊依赖（仅标准 Core/Engine 等）。子模块依赖 AssetRegistry 和 UnrealEd 是因为需要资产类型注册和编辑器集成。使用时需在你的模块 Build.cs 中添加对相应子模块的依赖。

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `8513e7f4` | [Audio] Fix FFusionVoice::AssignIDs KeyZone ordering + add structural null defense. | 修复 Fusion 音色键区排序并添加结构空值防护 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决 FSoundWaveData API 废弃修复的合并冲突 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-05-12 | `0ae74ea8` | [Harmonix] Add user object to the FusionPatch proxy that can be used for tracking activity in associ... | 为 FusionPatch 代理添加用户对象，用于关联活动追踪 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符与参数位宽不匹配的问题 |

### 维护评价

- **创建时间**：2024-01-17，约 1.5 年前，相对较新的插件
- **活跃维护**：最近 1 个月内有多次实质性更新，包括 bug 修复、API 改进和新功能（FusionPatch 代理用户对象）
- **实验性状态**：`IsExperimentalVersion=true` 且 `EnabledByDefault=false`，API 可能在未来版本中发生变化
- **团队背书**：由 Harmonix GenTech（Epic 旗下专业音乐游戏团队）开发和维护，技术实力有保障
- **源码规模**：521 个文件，是一个功能完善的大规模插件

**⚠️ 注意**：此插件当前为实验性状态，API 不保证稳定。在生产项目中使用前，建议先评估是否能满足需求，并做好 API 变更的应对准备。考虑到 Harmonix 团队的持续维护和在 Fortnite Festival 中的实际应用，该插件的前景值得期待。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix)
- 官方文档：无（实验性插件，暂无官方文档）