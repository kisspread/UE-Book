# Day Sequence

> （无）

| 属性 | 值 |
|---|---|
| 中文名 | 昼夜序列 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产/蓝图） |
| 模块 | `DaySequence` (Runtime), `DaySequenceEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-06-11 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/DaySequence) | |

## 用途

DaySequence 插件是一个专为管理游戏内**昼夜循环**和**时间驱动环境变化**而设计的系统。它不同于用于创建过场动画的 Level Sequence，其核心目的是在大型开放世界中，高效、可预测地控制随时间（游戏内的一天）推移而发生的**环境、光照、天空、天气**等元素的变化。

该插件解决了以下问题：
1.  **长时间轴管理**：传统的 Level Sequence 时间轴以秒为单位，管理长达24小时（或更长）的游戏内时间变化非常繁琐。DaySequence 将“一天”抽象为一个循环单位（例如 0.0 - 1.0 或 0-24 小时），简化了周期性事件的编辑。
2.  **环境驱动系统**：它提供了一个统一的框架，让美术和设计师能够定义在特定时间点（如中午、黄昏、夜晚）触发的环境变化，而无需编写复杂的时钟逻辑或轮询。
3.  **状态条件化**：通过“条件集”系统，可以根据游戏状态（如是否下雨、是否在某个区域、是否完成任务）动态启用或禁用特定的环境变化，实现复杂的情景化表现。
4.  **编辑器集成与预览**：提供了完整的编辑器工具集，允许开发者在编辑器内直观地预览任意时间点的游戏世界状态，而无需进入运行时。

简而言之，它是为**管理游戏世界随着时间流逝而产生沉浸式变化**（而非播放过场动画）而存在的专用工具。

## 使用场景

-   你正在开发一个**开放世界游戏**，需要实现逼真的24小时昼夜循环，包括太阳位置、天空盒颜色、环境光照、室内外灯光开关等随时间平滑过渡。
-   你的游戏世界中有基于时间的**动态事件**，例如商店在特定时间营业/打烊、NPC 在夜间回家、路灯在黄昏时自动点亮。
-   你需要根据**游戏状态**（如下雨、下雪、沙尘暴）来修改环境表现，例如下雨时天色变暗、雾气增加。
-   你希望美术和关卡设计师能够**直观地在编辑器中预览和调整**不同时间点的世界效果，而无需反复进入游戏运行。

## 蓝图用法

核心功能通过 `ADaySequenceActor` 和 `UDaySequence` 类暴露给蓝图。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Day Length` | 设置一个完整游戏日的时长（以小时为单位）。 | `ADaySequenceActor` |
| `Set Current Time of Day` | 直接设置当前的游戏内时间（以小时为单位）。 | `ADaySequenceActor` |
| `Get Current Time of Day` | 获取当前的游戏内时间（以小时为单位）。 | `ADaySequenceActor` |
| `Set Active Conditions` | 设置一个条件集，用于决定哪些 Day Sequence 片段生效。 | `ADaySequenceActor` |
| `Create Root Sequence` | 为此 DaySequenceActor 创建一个新的根 Day Sequence 资产。 | `ADaySequenceActor` |
| `Get Root Sequence` | 获取此 DaySequenceActor 关联的根 Day Sequence 资产。 | `ADaySequenceActor` |
| `Set Run Day Cycle` | 启用或禁用此 Actor 的游戏内时间自动推进。 | `ADaySequenceActor` |

### 使用示例（蓝图描述）

1.  **设置昼夜循环**：在场景中放置一个 `DaySequenceActor`。在它的细节面板或通过蓝图，设置 `Day Length`（例如24小时），并勾选 `Run Day Cycle`。时间将在游戏运行时自动流逝。
2.  **编辑环境变化**：右键点击 `DaySequenceActor`，选择“Create Root Sequence”来创建并打开 DaySequence 编辑器。在此编辑器中，你可以像编辑 Level Sequence 一样，为时间轴上的不同时间点（如0.5代表中午）添加关键帧，控制关联的灯光、天空球、后处理体积等组件的属性。
3.  **使用条件集**：创建基于 `UDaySequenceConditionTag` 的蓝图子类（例如 `BPIsRaining`）。在 DaySequence 编辑器中，可以为某些序列片段指定需要激活的“条件集”。然后，在游戏运行时，通过 `Set Active Conditions` 节点动态传递当前激活的条件标签，以启用或禁用相应的环境变化。

## C++ 用法

### 头文件引入

```cpp
#include "DaySequenceActor.h"
#include "DaySequence.h"
#include "DaySequenceConditionTag.h"
```

### 基本用法

在 C++ 中获取和管理 DaySequence 的控制权。以下代码展示了如何在游戏代码中驱动昼夜循环。

```cpp
// 来源: 基于 Public/DaySequenceActor.h 中的 API 推断。
// 假设你已经通过某种方式（如 SpawnActor 或 GetActorOfClass）获取了 ADaySequenceActor 的指针。

// 1. 获取当前世界中的 DaySequence Actor
ADaySequenceActor* DayActor = ...; // 例如从 GameMode 或通过 FindObject 获取

if (DayActor)
{
    // 2. 设置一天的游戏时长为 24 小时
    DayActor->SetDayLength(24.0f);

    // 3. 启动时间自动推进（昼夜循环）
    DayActor->SetRunDayCycle(true);

    // 4. 直接跳转到下午 2 点 (14:00)
    DayActor->SetCurrentTimeOfDay(14.0f);

    // 5. 获取当前时间用于逻辑判断
    float CurrentHour = DayActor->GetCurrentTimeOfDay();
    UE_LOG(LogTemp, Log, TEXT("Current game time: %.2f hours"), CurrentHour);
}
```

### 进阶用法：使用条件集

条件集允许根据游戏状态动态控制 Day Sequence 片段的激活。这通常与自定义的 `UDaySequenceConditionTag` 子类配合使用。

```cpp
// 来源: 基于 Public/DaySequenceConditionSet.h 和测试用例推断。

// 1. 定义一个条件标签（在 .h 文件中）
// UCLASS(BlueprintType)
// class UMyWeatherConditionTag : public UDaySequenceConditionTag
// {
//     GENERATED_BODY()
// };

// 2. 在游戏中设置活动的条件
if (DayActor)
{
    // 创建一个条件集
    FDaySequenceConditionSet ConditionSet;

    // 添加一个条件，并设置其期望值为 true（例如，表示“正在下雨”）
    // 条件集的键是 UDaySequenceConditionTag 的类，值是 bool
    ConditionSet.Add(UMyWeatherConditionTag::StaticClass(), true);

    // 将这个条件集应用到 DaySequenceActor
    DayActor->SetActiveConditions(ConditionSet);

    // 当天气变化时（例如，雨停了），更新条件
    ConditionSet.Add(UMyWeatherConditionTag::StaticClass(), false);
    DayActor->SetActiveConditions(ConditionSet);
}
```

## Demo 示例

以下是一个最小化的 `ADaySequenceActor` 子类，用于在 C++ 中创建一个预设了参数的昼夜循环 Actor。

### MyDayActor.h
```cpp
#pragma once

#include "CoreMinimal.h"
#include "DaySequenceActor.h"
#include "MyDayActor.generated.h"

UCLASS(BlueprintType)
class MYPROJECT_API AMyDayActor : public ADaySequenceActor
{
    GENERATED_BODY()

public:
    AMyDayActor();

protected:
    virtual void BeginPlay() override;
};
```

### MyDayActor.cpp
```cpp
#include "MyDayActor.h"

AMyDayActor::AMyDayActor()
{
    // 设置一天时长为 30 分钟（0.5小时）
    DayLength = 0.5f;
    // 默认启用昼夜循环
    bRunDayCycle = true;
}

void AMyDayActor::BeginPlay()
{
    Super::BeginPlay();
    // 游戏开始时，从早上 6 点开始
    SetCurrentTimeOfDay(6.0f);
}
```

使用说明：
1.  在 C++ 项目中创建上述 `AMyDayActor` 类。
2.  在场景中放置此 Actor。
3.  为它创建一个根 Day Sequence 资产（右键 -> Create Root Sequence）。
4.  在打开的 DaySequence 编辑器中编辑环境变化。
5.  运行游戏，你将看到一个以 30 分钟为周期的快速昼夜循环，并从早上 6 点开始。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LevelSequence` | DaySequence 的核心序列资产 (`UDaySequence`) 继承自 `ULevelSequence`。 |
| `MovieScene` | 提供底层的电影场景轨道、片段和评估框架。 |
| `MovieSceneTracks` | 提供用于控制 Actor 属性、变换等的具体轨道类型。 |
| `LevelSequenceEditor` | DaySequence 编辑器工具 (`FDaySequenceEditorToolkit`) 基于 Sequencer 的编辑器框架构建。 |
| `SequencerScripting` | 提供蓝图脚本支持，用于通过蓝图控制序列。 |
| `PropertyEditor` | 用于自定义 DaySequence 相关属性（如 `FDaySequenceTime`）在细节面板中的显示。 |

**无特殊依赖（仅标准 Core/Engine/Slate 等）的常见模块已省略。**

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，代码中双精度常量截断为浮点数时产生的编译警告。 |
| 2026-05-12 | `6504a9b5` | PR #14627: Check in BaseDaySequenceActor if optional components got created | PR #14627：在 BaseDaySequenceActor 中检查可选组件是否已创建。 |
| 2026-04-29 | `5f9ccdd8` | DaySequence: Unhide the Rendering, World Partition and Data Layers categories from the DaySequenceAc | 日夜序列：在 DaySequenceActor 细节面板中取消隐藏“渲染”、“世界分区”和“数据层”分类。 |
| 2026-04-21 | `6b47db2d` | DaySequence: Expose DaySequenceCollections property to BP | 日夜序列：向蓝图公开 DaySequenceCollections 属性。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 日志调用迁移到 UE_LOGF 格式化版本。 |

### 维护评价

-   **创建时间**：插件于 2024 年 6 月从内部项目（`Restricted/NFL`）迁移到实验性分支，目前约有 2 年历史。
-   **活跃度**：**非常活跃**。从 2026 年 4 月至 5 月，有连续的功能性更新和代码质量改进，包括修复编译警告、暴露新属性到蓝图、改善编辑器 UI 分类等。这表明 Epic 内部仍在积极使用和开发此插件。
-   **状态**：**实验性，但维护良好**。`.uplugin` 标记为 `IsExperimentalVersion=true` 且 `EnabledByDefault=false`，说明它尚未被视为稳定 API，不建议直接用于生产版本，但适合在原型或内部项目中评估和使用。
-   **推荐**：**推荐用于实验性项目或预研**。如果你的项目需要一个专业、集成于编辑器的昼夜循环系统，并且不介意在后续引擎版本中可能遇到 API 变动，那么这是一个非常强大且值得尝试的工具。对于生产项目，建议密切关注其从实验性分支毕业的时间点。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/DaySequence)
- [官方文档]() （暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/DaySequence/Tests) （如果存在）