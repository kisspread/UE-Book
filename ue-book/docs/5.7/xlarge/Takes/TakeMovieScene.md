# Take Recorder

> A suite of tools and interfaces designed for recording, reviewing and playing back takes in a virtual production environment.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `CacheTrackRecorder` (Runtime), `TakeMovieScene` (Runtime), `TakeRecorder` (Runtime), `TakeRecorderNamingTokens` (Runtime), `TakeRecorderSources` (Runtime), `TakesCore` (Runtime), `TakeSequencer` (Runtime), `TakeTrackRecorders` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-01-10 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Takes) | |

## 用途

Takes 插件是 Unreal Engine 虚拟制作（Virtual Production）工作流的核心组件之一，它提供了一套完整的框架，用于在 Sequencer（序列器）中录制、管理和回放“Take”（镜头）。一个 Take 通常包含特定时间段内所有参与元素（如摄像机、角色、灯光、动画等）的状态数据。

**TakeMovieScene 模块**是该插件与 Sequencer 集成的关键部分。它主要负责：
1.  **定义数据结构**：定义了用于在 Sequencer 轨道中存储 Take 元数据（如时间码、Slate 信息）的 Section 和 Track 类。
2.  **处理时间码与卡顿检测**：提供了专门的数据结构和通道，用于记录录制过程中每一帧的“目标时间码”和“实际时间码”。通过比较两者，可以精确检测引擎在录制期间是否发生了卡顿（Hitch），这对于保证虚拟制作中多设备（如 nDisplay）的同步至关重要。
3.  **提供评估接口**：允许在 Sequencer 的任意时间点评估并获取 Take 的元数据。

简而言之，该模块解决了在虚拟制作中精确记录和同步时间信息，并诊断录制过程中性能问题的需求。

## 使用场景

-   **虚拟制片（Virtual Production）**：在 LED 墙或 nDisplay 多机渲染环境中，需要精确同步所有摄像机、渲染节点和外部设备的时间码。Take Recorder 和 TakeMovieScene 模块确保录制数据的时间准确性，并能事后分析卡顿。
-   **动作捕捉与动画录制**：录制演员表演或动画数据时，需要将时间码与外部设备（如 OptiTrack）同步。该模块帮助管理录制数据在 Sequencer 中的存储。
-   **后期制作与审阅**：导演或后期团队需要在 Sequencer 中精确回放录制的 Take，并查看每一帧的元数据（如 Slate、时间码）以进行审阅和剪辑。

## 蓝图用法

TakeMovieScene 模块主要提供数据结构和 Sequencer 集成，其蓝图暴露的接口相对底层，通常由 Take Recorder 的上层蓝图逻辑调用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `HoursName`, `MinutesName`, `SecondsName`, `FramesName`, `SubFramesName`, `RateName`, `SlateName` | 可读写属性，用于配置 Take 元数据（时间码各分量、帧率、Slate）在 Sequencer 通道中的显示名称。 | `UMovieSceneTakeSettings` |
| `Evaluate` | 在指定的 `FFrameTime` 评估 Take Section 的数据，返回包含时间码、帧率和 Slate 的结构体。 | `UMovieSceneTakeSection` |

### 使用示例（蓝图描述）

1.  **配置 Take 设置**：
    -   在项目设置或通过蓝图获取 `UMovieSceneTakeSettings` 的默认对象。
    -   设置其 `HoursName`, `SlateName` 等属性，以自定义 Sequencer 中 Take 轨道的显示标签。

2.  **评估 Take 数据**：
    -   在 Sequencer 的蓝图逻辑中，获取当前播放位置的 `FFrameTime`。
    -   调用 `UMovieSceneTakeSection` 实例的 `Evaluate` 节点。
    -   从返回的 `FSectionData` 结构体中提取 `Timecode`（时间码）、`Rate`（帧率）和 `Slate`（场记板信息）用于显示或逻辑判断。

## C++ 用法

### 头文件引入

```cpp
#include "MovieSceneTakeSection.h"
#include "MovieSceneTakeSettings.h"
#include "Hitching/FrameHitchSceneDecoration.h"
```

### 基本用法

以下示例展示了如何在 C++ 中创建一个 `UMovieSceneTakeSection` 并评估其数据。

```cpp
// 假设我们已经有一个 UMovieSceneTakeSection 的实例 TakeSection
// 通常它由 Take Recorder 自动创建和管理

// 1. 评估特定时间点的 Take 数据
FFrameTime CurrentTime(100); // 第100帧
TOptional<UMovieSceneTakeSection::FSectionData> SectionData = TakeSection->Evaluate(CurrentTime);

if (SectionData.IsSet())
{
    FTimecode Timecode = SectionData.GetValue().Timecode;
    FString Slate = SectionData.GetValue().Slate;
    float FrameRate = SectionData.GetValue().Rate;
    
    UE_LOG(LogTemp, Log, TEXT("Take at frame %d: Timecode=%s, Slate=%s, Rate=%.2f"),
        CurrentTime.FrameNumber.Value,
        *Timecode.ToString(),
        *Slate,
        FrameRate);
}
```

### 进阶用法

分析录制过程中的卡顿数据。这通常由 Take Recorder 内部完成，但理解其结构有助于自定义分析。

```cpp
// 假设我们有一个 UFrameHitchSceneDecoration 对象 HitchDecoration
// 它通常附加在 ULevelSequence 资产上

// 1. 评估特定帧的卡顿信息
FFrameTime FrameToCheck(50);
TOptional<UE::TakeMovieScene::FFrameHitchData> HitchData = HitchDecoration->Evaluate(FrameToCheck);

if (HitchData.IsSet())
{
    FTimecode TargetTC = HitchData.GetValue().TargetTimecode;
    FTimecode ActualTC = HitchData.GetValue().ActualTimecode;
    
    // 比较目标时间和实际时间，判断是否卡顿
    if (TargetTC != ActualTC)
    {
        UE_LOG(LogTemp, Warning, TEXT("Hitch detected at frame %d! Target: %s, Actual: %s"),
            FrameToCheck.FrameNumber.Value,
            *TargetTC.ToString(),
            *ActualTC.ToString());
    }
}

// 2. 获取所有记录了卡顿数据的帧时间
TConstArrayView<FFrameNumber> HitchFrameTimes = HitchDecoration->TargetTimecode.GetFrameTimes();
UE_LOG(LogTemp, Log, TEXT("Total frames with hitch data: %d"), HitchFrameTimes.Num());
```

## Demo 示例

一个最小示例，展示如何创建一个 `UMovieSceneTakeSection` 并手动设置其通道数据。

**MyTakeDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "MovieSceneTakeSection.h"

class FMyTakeDemo
{
public:
    static void CreateAndPopulateTakeSection();
};
```

**MyTakeDemo.cpp**
```cpp
#include "MyTakeDemo.h"
#include "UObject/Package.h"

void FMyTakeDemo::CreateAndPopulateTakeSection()
{
    // 创建一个新的 Take Section 对象（通常在 Sequencer 编辑器上下文中由系统创建）
    UMovieSceneTakeSection* TakeSection = NewObject<UMovieSceneTakeSection>(GetTransientPackage(), NAME_None, RF_Transient);

    // 设置一些示例数据到其通道中
    // 注意：实际使用中，这些数据由 Take Recorder 在录制时自动填充
    FFrameNumber KeyTime(0);
    
    // 设置小时通道
    TakeSection->HoursCurve.AddKey(KeyTime, 10);
    // 设置分钟通道
    TakeSection->MinutesCurve.AddKey(KeyTime, 30);
    // 设置秒通道
    TakeSection->SecondsCurve.AddKey(KeyTime, 15);
    // 设置帧通道
    TakeSection->FramesCurve.AddKey(KeyTime, 5);
    // 设置 Slate 通道
    TakeSection->Slate.AddKey(KeyTime, TEXT("Slate_001"));

    // 评估这个 Section
    TOptional<UMovieSceneTakeSection::FSectionData> Data = TakeSection->Evaluate(FFrameTime(KeyTime));
    if (Data.IsSet())
    {
        UE_LOG(LogTemp, Display, TEXT("Created Take Section - Timecode: %s, Slate: %s"),
            *Data.GetValue().Timecode.ToString(),
            *Data.GetValue().Slate);
    }
}
```

## 模块依赖

`TakeMovieScene` 模块依赖于 Sequencer 的核心模块来定义轨道和通道。使用者（通常是其他 Takes 子模块或需要与 Take 数据交互的模块）需要链接这些模块。

| 模块 | 用途 |
|---|---|
| `MovieScene` | Sequencer 的核心模块，提供 `UMovieSceneSection`, `UMovieSceneTrack` 等基类。 |
| `TimeManagement` | 提供时间码（`FTimecode`）、帧率（`FFrameRate`）等时间管理相关类型。 |

## 维护状态

### 近期更新

-   2025-10-03 e96da19808f1 Take Recorder: When FPS mismatch, hitch visualization shows a warning icon in track area.
    *解读：增强了卡顿可视化功能，在帧率不匹配时会在轨道区域显示警告图标，提升了用户体验。*
-   2025-09-15 74386d312d0f Fixup API macro usage
    *解读：修复了 API 导出宏的使用，属于代码维护和规范性改进。*
-   2025-08-20 06f821a8140a Take Recorder: Save per-frame hitch information into ULevelSequence. The data is saved in a Sequencer decorator object, which is not displayed to the user.
    *解读：核心功能更新。将逐帧卡顿信息保存到关卡序列资产中，为后续的卡顿分析和可视化奠定了基础。*

### 维护评价

**活跃维护**。
-   **创建时间**：2019年，是虚拟制作工具链的早期组件之一。
-   **近期活动**：最近三个月有连续的功能性提交，特别是围绕“卡顿检测与可视化”这一核心痛点进行了重要增强。
-   **维护状态**：作为 Epic Games 官方虚拟制作套件的关键部分，该插件处于持续活跃的维护和开发中，没有废弃迹象。
-   **推荐使用**：对于任何涉及虚拟制作、需要精确时间同步和录制管理的项目，**强烈推荐使用**。它是 UE 虚拟制作工作流的基石之一。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Takes)
-   [官方文档](https://docs.unrealengine.com/5.7/en-US/take-recorder-in-unreal-engine/) (UE5 官方文档 - Take Recorder)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Takes/Tests) (如果存在)