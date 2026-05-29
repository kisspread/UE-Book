# DaySequence

> 用于驱动游戏世界昼夜循环的序列化框架。

| 属性 | 值 |
|---|---|
| 中文名 | 白天序列 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `DaySequence` (Runtime), `DaySequenceEditor` (Editor) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2024-06-11 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/DaySequence) | |

## 用途

DaySequence 是一个**专门为昼夜循环设计的序列化框架**。它解决了在大型开放世界或需要动态时间变化的场景中，统一管理、驱动和同步各种视觉效果（如光照、天空、天气、材质）和游戏逻辑（如NPC行为、事件触发）随时间变化的需求。它构建在 Unreal 的 Level Sequence 系统之上，提供了更符合“一天”概念的抽象（如用 `NormalizedTime` 表示 0.0 (午夜) 到 1.0 (次日午夜) 的时间），并将编辑器中的时间轴与游戏内的昼夜系统深度集成。

## 使用场景

- **开放世界游戏**：你需要一个系统来根据游戏内时间，无缝驱动从日出到日落的全局光照、天空穹顶、雾气、环境音效等变化。
- **带有时间机制的游戏**：例如，游戏核心玩法围绕时间循环（如《死亡搁浅》的时间雨）或季节变化展开。
- **复杂的环境叙事**：希望在特定时间点触发精确的过场动画、环境事件或NPC调度。
- **美术管线优化**：美术希望使用类似Sequencer的界面来直观地“导演”整个世界的昼夜变化，而不是管理大量分散的蓝图和参数。

## 蓝图用法

核心的蓝图接口主要通过 `ABaseDaySequenceActor` 暴露。详细的蓝图函数和属性请参见子模块文档 [DaySequence](DaySequence.md)。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Time of Day` | 设置一天中的标准化时间 (0.0-1.0)。 | `ABaseDaySequenceActor` |
| `Get Time of Day` | 获取当前一天中的标准化时间。 | `ABaseDaySequenceActor` |
| `Play` | 播放关联的白天序列。 | `ABaseDaySequenceActor` |
| `Get Day Length in Minutes` | 获取一个完整昼夜循环在现实中的分钟数。 | `ADaySequenceActor` |

### 使用示例（蓝图描述）

在关卡中放置一个 `DaySequenceActor`，它会自动管理所有受时间驱动的序列。通过蓝图调用 `Set Time of Day` 节点，传入 0.25 (代表早上6点)，驱动整个世界的黎明效果。可以使用 `Get Time of Day` 节点查询当前时间，并基于此控制其他游戏逻辑（如商店开门时间）。

## C++ 用法

DaySequence 的核心是 `ABaseDaySequenceActor` 和 `UDaySequenceComponent`。C++ 扩展通常涉及创建自定义的 Actor 来整合自己的时间逻辑。

### 头文件引入

```cpp
#include "DaySequenceActor.h"
#include "DaySequenceComponent.h"
```

### 基本用法

创建一个继承自 `ABaseDaySequenceActor` 的自定义 Actor，并重写时间相关的虚拟函数。

```cpp
// MyDaySequenceActor.h
#pragma once
#include "DaySequenceActor.h"
#include "MyDaySequenceActor.generated.h"

UCLASS()
class AMyDaySequenceActor : public ABaseDaySequenceActor
{
    GENERATED_BODY()
public:
    // 重写以提供自定义的时间计算逻辑
    virtual float GetCustomTimeOfDay() const override;
    // 可以重写 OnTimeChanged 来响应时间变化
    virtual void OnTimeChanged(float NewTime) override;
};
```

```cpp
// MyDaySequenceActor.cpp
#include "MyDaySequenceActor.h"

float AMyDaySequenceActor::GetCustomTimeOfDay() const
{
    // 示例：从游戏存档系统获取时间
    return UMySaveGameSubsystem::Get()->GetSavedTimeOfDay();
}

void AMyDaySequenceActor::OnTimeChanged(float NewTime)
{
    Super::OnTimeChanged(NewTime);
    // 根据时间变化更新自定义的游戏逻辑
    if (NewTime > 0.75f) // 晚上6点后
    {
        // 启用夜间模式
    }
}
```

### 进阶用法

与 `UDaySequenceComponent` 交互，在其他 Actor 中响应时间变化。

```cpp
// 在某个 Manager Actor 中
void AMyGameManager::BeginPlay()
{
    Super::BeginPlay();
    // 查找关卡中的 DaySequenceActor
    if (ADaySequenceActor* DayActor = FindDaySequenceActor())
    {
        // 绑定到时间变化事件
        DayActor->GetDaySequenceComponent()->OnTimeOfDayChanged.AddDynamic(this, &AMyGameManager::HandleTimeChange);
    }
}

void AMyGameManager::HandleTimeChange(float NewTime)
{
    // 根据 NewTime 执行全局游戏逻辑
}
```

## 子模块概览

- **[DaySequence](DaySequence.md)** (Runtime)：核心运行时模块。包含 `ABaseDaySequenceActor`, `UDaySequenceComponent`, `UDaySequenceSubsystem` 等类，负责在游戏中管理时间、播放序列、驱动时间轴和接口。
- **[DaySequenceEditor](DaySequenceEditor.md)** (Editor)：编辑器扩展模块。提供自定义的 Sequencer 轨道（如 `DaySequenceTrack`）、细节面板自定义、资产编辑器以及工作流程工具，让美术和策划能够直观地编辑昼夜序列。

## 模块依赖

除了标准的 Core/Engine 模块外，DaySequence 特别依赖于 Unreal 的序列系统和时间管理系统。

| 模块 | 用途 |
|---|---|
| `LevelSequence` | 提供底层的序列播放引擎，DaySequence 构建于其上。 |
| `TimeManagement` | 提供时间缩放和同步等核心功能。 |
| `Niagara` | （可选）用于集成或驱动昼夜相关的粒子系统效果。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点的编译警告。 |
| 2026-05-12 | `6504a9b5` | PR #14627: Check in BaseDaySequenceActor if optional components got created | 增加检查，确保 BaseDaySequenceActor 的可选组件被正确创建。 |
| 2026-04-29 | `5f9ccdd8` | DaySequence: Unhide the Rendering, World Partition and Data Layers categories from the DaySequenceAc | 在 DaySequenceActor 细节面板中显示渲染、世界分区和数据层类别。 |
| 2026-04-21 | `6b47db2d` | DaySequence: Expose DaySequenceCollections property to BP | 将 DaySequenceCollections 属性暴露给蓝图。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移到新的 UE_LOGF 格式。 |

### 维护评价

DaySequence 插件创建于 2024 年，**仍在活跃维护中**。最近的更新记录（截至 2026 年 5 月）显示开发团队持续在进行功能增强（暴露更多蓝图属性、改善编辑器体验）、代码健壮性提升（修复组件创建问题）和工程优化（编译器警告修复）。作为 `Experimental` 标签的插件，它可能还会经历较大的 API 变动，但持续的更新表明 Epic 正在将其作为重要功能进行开发。对于需要专业昼夜循环系统的项目，这是一个值得跟踪和评估的高潜力插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/DaySequence)
- [官方文档]() （暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/DaySequence/Tests)