# Day Sequence

> 

| 属性 | 值 |
|---|---|
| 中文名 | 日循环序列 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `DaySequence` (Runtime), `DaySequenceEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-06-11 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/DaySequence) | |

## 用途

DaySequence 插件是 Unreal Engine Sequencer（序列器）的一个强大扩展，专门用于管理和驱动游戏世界中的“日循环”（Day Cycle）。它解决了在大型开放世界或需要精细时间控制的游戏中，实现昼夜变化、环境光照、天气系统等复杂时间驱动动画的痛点。

**核心问题**：传统的昼夜循环实现通常需要开发者手动编写大量代码来同步时间、管理多个组件（如太阳、天空球、灯光）的变化，并处理诸如序列融合、区域化时间流速、条件触发等高级需求。这导致开发困难、维护成本高且难以进行设计迭代。

**解决方案**：DaySequence 允许开发者利用 Sequencer 可视化编辑器，在一条时间轴上设计“一天”的视觉效果和事件。通过 `ADaySequenceActor` 这个核心Actor，可以在游戏世界中回放这个“日序列”，并提供了以下关键能力：
1.  **时间轴驱动**：将昼夜循环作为序列资产进行设计，便于美工和设计人员迭代。
2.  **序列融合**：支持多个日序列（如基础昼夜、室内、雨天）根据条件（玩家位置、游戏事件）进行混合。
3.  **区域化时间**：允许特定区域（如室内）拥有不同的时间流速或固定的白天/夜晚状态。
4.  **程序化生成**：提供 API 在运行时基于参数（如地理位置）动态生成日序列。
5.  **网络同步**：内置对日循环播放状态的网络复制支持。

简而言之，DaySequence 将复杂的昼夜循环系统抽象为可在 Sequencer 中编辑的资产，极大地简化了开发流程，并提供了高度的灵活性和可控性。

## 使用场景

-   **开放世界游戏**：你需要一个动态的、可预测的昼夜循环，影响光照、阴影、天空盒、天气和NPC行为 → 使用 `ABaseDaySequenceActor` 或 `ASunMoonDaySequenceActor`，并为其设计包含太阳运动、天空颜色变化、后处理效果等的 `UDaySequence` 资产。
-   **特定区域时间效果**：你希望玩家进入某个山洞时，游戏世界的时间暂停或变为固定的夜晚 → 使用 `UDaySequenceModifierComponent`，将其配置为 `Volume` 模式并附加一个触发体积。
-   **基于条件的序列切换**：你的游戏有晴天和雨天系统，需要根据游戏状态切换不同的日序列 → 使用 `UDaySequenceConditionTag` 定义条件，并将其应用在 `UDaySequenceCollectionAsset` 中的不同序列条目上。
-   **程序化日循环**：你希望基于真实的地理位置数据（经纬度、日期）来驱动太阳位置 → 使用 `FSunPositionSequence` 这一程序化序列。
-   **调试与测试**：你需要快速跳转到一天的特定时间来检查光照或触发事件 → 通过蓝图节点或 `ADaySequenceActor` 的 `SetTimeOfDay` 函数进行控制。

## 蓝图用法

DaySequence 为蓝图提供了丰富的接口，主要集中在时间控制、播放管理和条件逻辑上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| **时间查询与设置** | | |
| `Get Time Of Day` | 获取当前时间（小时） | `ADaySequenceActor` |
| `Set Time Of Day` | 设置当前时间（服务器端） | `ADaySequenceActor` |
| `Get Apparent Time Of Day` | 获取受静态时间影响的当前“表观”时间 | `ADaySequenceActor` |
| `Get Initial Time Of Day` | 获取初始设定时间 | `ADaySequenceActor` |
| **播放控制** | | |
| `Play` | 恢复播放 | `ADaySequenceActor` |
| `Pause` | 暂停播放 | `ADaySequenceActor` |
| `Is Playing` | 检查是否正在播放 | `ADaySequenceActor` |
| `Set Play Rate` | 设置播放速率（2.0 表示加速一倍） | `ADaySequenceActor` |
| **播放器控制** | | |
| `Play` | 从当前位置开始播放 | `UDaySequencePlayer` |
| `Stop` | 停止播放 | `UDaySequencePlayer` |
| `Set Play Rate` | 设置播放速率 | `UDaySequencePlayer` |
| `Get Current Time` | 获取当前帧时间 | `UDaySequencePlayer` |
| **修改器与子系统** | | |
| `Bind To Day Sequence Actor` | 将修改器组件绑定到指定的日序列Actor | `UDaySequenceModifierComponent` |
| `Enable Component` | 启用修改器 | `UDaySequenceModifierComponent` |
| `Get Day Sequence Actor` | 获取当前世界中的日序列Actor（通过子系统） | `UDaySequenceSubsystem` |
| **程序化构建器** | | |
| `Initialize` | 初始化程序化序列构建器 | `UProceduralDaySequenceBuilder` |
| `Set Active Bound Object` | 设置要动画的目标对象 | `UProceduralDaySequenceBuilder` |
| `Add Scalar Key` | 添加浮点属性关键帧 | `UProceduralDaySequenceBuilder` |
| `Add Vector Key` | 添加向量属性关键帧 | `UProceduralDaySequenceBuilder` |

### 使用示例（蓝图描述）

**1. 快速获取并控制日循环时间：**
- 从任意蓝图中，使用 `Get Game World` -> `Get Subsystem` -> `Day Sequence Subsystem` -> `Get Day Sequence Actor` 获取场景中的 `ADaySequenceActor` 引用。
- 使用 `Get Time Of Day` 读取当前时间。
- 使用 `Set Time Of Day` 强制设置时间。
- 使用 `Set Play Rate` 动态调整时间流速（例如玩家加速移动时）。

**2. 创建区域化时间修改器：**
- 在 Actor 蓝图上添加 `Day Sequence Modifier Component`。
- 在 BeginPlay 中，使用 `Bind To Day Sequence Actor` 节点将其绑定到子系统中的 `DaySequenceActor`。
- 配置修改器的 `Mode` 为 `Volume`，并关联一个 `Box Component` 作为触发区域。
- 设置 `Day Night Cycle` 为 `Fixed Time` 或 `LocalFixed Time` 来控制区域内的时间行为。

**3. 运行时生成动画序列：**
- 创建 `UProceduralDaySequenceBuilder` 变量。
- 调用 `Initialize`，传入目标 `DaySequenceActor`。
- 调用 `Set Active Bound Object`，传入你想要动画的灯光组件。
- 使用 `Add Scalar Key` 节点，在 0.0 和 1.0（代表从午夜到午夜）的时间点上，设置灯光 `Intensity` 属性的值，从而创建一个简单的昼夜亮度变化曲线。

## C++ 用法

### 头文件引入

```cpp
#include "DaySequence.h"
#include "DaySequenceActor.h"
#include "DaySequenceSubsystem.h"
#include "ProceduralDaySequenceBuilder.h"
#include "DaySequenceConditionTag.h"
```

### 基本用法

**获取日序列Actor并查询时间：**
```cpp
// 来源: Private/DaySequenceModule.h, Public/DaySequenceSubsystem.h
// 在任何可以获取 UWorld 的地方
if (UWorld* World = GetWorld())
{
    if (UDaySequenceSubsystem* Subsystem = World->GetSubsystem<UDaySequenceSubsystem>())
    {
        if (ADaySequenceActor* DaySequenceActor = Subsystem->GetDaySequenceActor())
        {
            float CurrentTimeHours = DaySequenceActor->GetTimeOfDay();
            UE_LOG(LogDaySequence, Log, TEXT("Current Time: %.2f hours"), CurrentTimeHours);
            
            // 设置时间（通常在服务器端调用）
            DaySequenceActor->SetTimeOfDay(14.0f); // 设置为下午2点
            
            // 调整时间流速
            DaySequenceActor->SetPlayRate(2.0f); // 时间流速加倍
        }
    }
}
```

### 进阶用法

**1. 程序化生成日序列：**
```cpp
// 来源: Public/ProceduralDaySequenceBuilder.h, Public/ProceduralSequences/SunPositionSequence.h
#include "ProceduralDaySequenceBuilder.h"
#include "ProceduralSequences/SunPositionSequence.h"

// 假设你有一个 ADaySequenceActor* Actor;
UProceduralDaySequenceBuilder* Builder = NewObject<UProceduralDaySequenceBuilder>();
Builder->Initialize(Actor);

// 构建一个基于地理位置的太阳运动序列
FSunPositionSequence SunPosSequence;
SunPosSequence.Latitude = 40.7128;  // 纽约纬度
SunPosSequence.Longitude = -74.0060; // 纽约经度
SunPosSequence.Time = FDateTime(2024, 6, 21); // 夏至日

// UDaySequence* GeneratedSequence = SunPosSequence.GetSequence(Actor);
// 此时 GeneratedSequence 已包含了基于物理计算的太阳旋转关键帧
```

**2. 创建自定义条件标签：**
```cpp
// 来源: Public/DaySequenceConditionTag.h
UCLASS(Blueprintable)
class UMyWeatherConditionTag : public UDaySequenceConditionTag
{
    GENERATED_BODY()
public:
    UMyWeatherConditionTag()
    {
        ConditionName = TEXT("Is Raining");
        // 可以在此绑定到真正的天气系统变化委托
    }

    virtual bool Evaluate_Implementation() const override
    {
        // 此处应查询你的游戏天气系统状态
        // return AMyWeatherManager::Get()->IsCurrentlyRaining();
        return false;
    }

protected:
    // 如果条件依赖外部事件，重写此函数绑定委托
    virtual void SetupOnConditionValueChanged_Implementation() const override
    {
        // AMyWeatherManager::Get()->OnWeatherChanged.AddDynamic(this, &UMyWeatherConditionTag::BroadcastOnConditionValueChanged);
    }
};
```

## Demo 示例

以下示例展示如何创建一个自定义的晴天/雨天条件标签，并将其应用到日序列集合资产中。

**1. 自定义条件标签 (`UMyRainCondition.h`)**
```cpp
// MyRainCondition.h
#pragma once
#include "DaySequenceConditionTag.h"
#include "MyRainCondition.generated.h"

UCLASS(Blueprintable)
class MYGAME_API UMyRainCondition : public UDaySequenceConditionTag
{
    GENERATED_BODY()

public:
    UMyRainCondition();
    virtual bool Evaluate_Implementation() const override;

protected:
    virtual void SetupOnConditionValueChanged_Implementation() const override;
};
```

**2. 实现文件 (`UMyRainCondition.cpp`)**
```cpp
// MyRainCondition.cpp
#include "MyRainCondition.h"
#include "GameFramework/GameStateBase.h"
#include "MyGameState.h" // 假设的自定义GameState

UMyRainCondition::UMyRainCondition()
{
    ConditionName = TEXT("IsRaining");
}

bool UMyRainCondition::Evaluate_Implementation() const
{
    // 从游戏状态获取是否下雨
    if (UWorld* World = GetWorld())
    {
        if (AMyGameState* GameState = World->GetGameState<AMyGameState>())
        {
            return GameState->bIsRaining;
        }
    }
    return false;
}

void UMyRainCondition::SetupOnConditionValueChanged_Implementation() const
{
    // 当游戏状态中的下雨标志改变时，通知条件值变化
    if (UWorld* World = GetWorld())
    {
        if (AMyGameState* GameState = World->GetGameState<AMyGameState>())
        {
            GameState->OnRainStateChanged.AddDynamic(
                const_cast<UMyRainCondition*>(this), 
                &UMyRainCondition::BroadcastOnConditionValueChanged);
        }
    }
}
```

**3. 在 `DaySequenceCollectionAsset` 中配置：**
- 在编辑器中创建或修改一个 `UDaySequenceCollectionAsset`。
- 添加两个 `FDaySequenceCollectionEntry`。
- 第一个条目设置 `Sequence` 为你的“晴天序列”，`Conditions` 中添加 `UMyRainCondition` 并将其值设为 `false`。
- 第二个条目设置 `Sequence` 为你的“雨天序列”，`Conditions` 中添加 `UMyRainCondition` 并将其值设为 `true`。
- 将该集合资产赋给 `ADaySequenceActor` 的 `DaySequenceCollections` 属性。现在，当游戏状态中的 `bIsRaining` 改变时，播放的序列将自动切换。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LevelSequenceEditor` | 在编辑器中支持 DaySequence 资产的编辑界面。 |
| `SequencerScripting` | 提供对 Sequencer 功能的脚本访问，是 DaySequence 程序化构建器的基础。 |
| `MovieScene` | Unreal 的电影场景核心模块，DaySequence 建立于其之上。 |
| `AnimationCore` | 处理关键帧动画计算，用于序列求值。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量截断为浮点数时产生的编译警告。 |
| 2026-05-12 | `6504a9b5` | PR #14627: Check in BaseDaySequenceActor if optional components got created | 改进：在 BaseDaySequenceActor 中检查可选组件是否被成功创建。 |
| 2026-04-29 | `5f9ccdd8` | DaySequence: Unhide the Rendering, World Partition and Data Layers categories from the DaySequenceAc | 改进：取消了对 DaySequenceActor 中“Rendering”、“World Partition”等类别的隐藏，使其在细节面板中可见。 |
| 2026-04-21 | `6b47db2d` | DaySequence: Expose DaySequenceCollections property to BP | 功能更新：将 DaySequenceCollections 属性暴露给蓝图。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 维护：将日志宏 UE_LOG 迁移到新格式 UE_LOGF。 |

### 维护评价

-   **活跃维护**：插件创建于 2024 年 6 月，属于较新的模块。从 Git 历史看，在过去一个月内（截至 2026 年 5 月）有多次实质性更新，包括功能改进（暴露属性到蓝图、改进组件检查）和代码维护（修复警告、迁移日志宏）。这表明 Epic 的团队仍在积极维护和迭代此功能。
-   **实验性状态**：`.uplugin` 中 `IsExperimentalVersion` 为 `true`，且 `EnabledByDefault` 为 `false`。这意味着 API 可能尚未完全稳定，在未来版本中可能会有破坏性更改。但鉴于其在 `Engine/Plugins/Experimental/` 目录下的位置和最近的活跃更新，它很可能是一个处于实验阶段但前景良好的功能。
-   **推荐使用**：对于需要在新项目中实现复杂、可设计的昼夜循环系统，且愿意接受 API 可能变化的开发者，**推荐使用** DaySequence。它提供了传统方法无法比拟的设计便利性和灵活性。对于追求极致稳定性的生产项目，建议密切关注其 API 变化并做好封装。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/DaySequence)
- [官方文档]( )（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/DaySequence/Tests)（如果存在）