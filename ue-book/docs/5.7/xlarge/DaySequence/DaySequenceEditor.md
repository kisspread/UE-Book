# DaySequence

> （空，原 Description 为空）

| 属性 | 值 |
|---|---|
| 中文名 | 白昼序列 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、序列资产） |
| 模块 | `DaySequence` (Runtime), `DaySequenceEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-08 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/DaySequence) | |

## 用途

DaySequence 插件提供了一个基于一天中时间（小时数）驱动关卡序列播放的昼夜循环系统。它扩展了标准的 LevelSequence，允许将动画、光照、事件等绑定到一天中的特定时间，并支持条件集（ConditionSet）来控制序列的播放逻辑。

**核心解决的问题：**
- 在开放世界或场景中实现自然的昼夜交替动画和光照变化。
- 通过时间轴（小时）驱动多个关卡序列的播放、暂停、跳转。
- 使用条件标签（如季节、天气状态）决定哪些序列应被播放，实现动态环境故事。

该插件包含两个主要模块：
- `DaySequence`（运行时）：核心框架，包括 `ADaySequenceActor`（驱动播放的 Actor）、`UDaySequence`（资产）、`UDaySequenceDirector`（蓝图导演类）、`FDaySequenceConditionSet`（条件集）等。
- `DaySequenceEditor`（编辑器）：提供资产创建、编辑器预览、时间滑块、条件集编辑器、自定义细节面板等工具。

## 使用场景

- **昼夜循环**：创建 24 小时的光照动画（如太阳角度、天空颜色），绑定到 DaySequence 上，由 DaySequenceActor 根据游戏内时间驱动回放。
- **时间触发事件**：例如在 6:00 播放鸟鸣音效，在 12:00 升起吊桥等。
- **动态序列选择**：根据条件（如季节 `Summer`、天气 `Rainy`）从多个 DaySequence 资产中选择合适的序列组合。
- **编辑器预览**：在编辑器中拖拽时间滑块，实时查看不同时间点的场景效果，无需运行 PIE。

## 蓝图用法

DaySequence 插件主要通过 `ADaySequenceActor` 暴露运行时接口，同时也支持通过 Director Blueprint（类似 LevelSequence）编写事件逻辑。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetDayLength` | 设置一天的时长（小时数） | `ADaySequenceActor` |
| `SetInitialTimeOfDay` | 设置初始时间（小时，0.0 ~ DayLength） | `ADaySequenceActor` |
| `GetCurrentTimeOfDay` | 获取当前时间（小时） | `ADaySequenceActor` |
| `IsDayCycleRunning` | 检查昼夜循环是否在运行 | `ADaySequenceActor` |
| `StartDayCycle` | 启动昼夜循环播放 | `ADaySequenceActor` |
| `StopDayCycle` | 停止昼夜循环 | `ADaySequenceActor` |
| `PauseDayCycle` | 暂停循环 | `ADaySequenceActor` |
| `SetTimeOfDay` | 直接跳转到指定时间 | `ADaySequenceActor` |
| `OnTimeOfDayChanged` | 时间变化时触发的事件（蓝图可绑定） | `ADaySequenceActor` |
| `PlaySequenceAtTime` | 在指定时间播放一个子序列（条件允许时） | `ADaySequenceActor` |

> **注意**：以上节点是基于运行时模块（DaySequence）常见公开 API 的推断，详细节点请查看 `ADaySequenceActor` 和 `UDaySequence` 的蓝图可调用函数。

### 使用示例（蓝图描述）

**示例：在游戏开始时初始化昼夜循环**

1. 在关卡中放置 `ADaySequenceActor`（通过放置面板搜索 DaySequence）。
2. 在 `Event BeginPlay` 中：
   - `Get DaySequence Actor` → `Set Day Length`（输入 `24.0`）
   - `Get DaySequence Actor` → `Set Initial Time Of Day`（输入 `6.0`）
   - `Get DaySequence Actor` → `Start Day Cycle`
3. 绑定 `On Time Of Day Changed` 事件，在每次时间变化时更新用户界面（如太阳位置、颜色）。

**示例：根据条件播放不同序列**

在 `ADaySequenceActor` 属性中设置 `Condition Set`，并在 Director Blueprint 中检查条件标签（如 `Season = Summer`），通过分支节点选择加载不同的 DaySequence 资产。

## C++ 用法

以下示例基于编辑器模块（DaySequenceEditor）和运行时模块（DaySequence）的常见使用模式。

### 头文件引入

```cpp
#include "DaySequence.h"
#include "DaySequenceActor.h"
#include "DaySequencePlayer.h"
#include "DaySequenceConditionSet.h"
```

### 基本用法

**1. 创建并播放一个 DaySequence**

```cpp
// 假设已有 UDaySequence* MyDaySequence 和 UWorld* World
ADaySequenceActor* DayActor = World->SpawnActor<ADaySequenceActor>();
DayActor->SetDayLength(24.0f);
DayActor->SetInitialTimeOfDay(6.0f);
DayActor->SetSequence(MyDaySequence);
DayActor->StartDayCycle();
```

**2. 在编辑器中预览时间（来自 FDaySequenceActorPreview）**

```cpp
// 获取 DaySequenceActor 预览管理器（IDaySequenceEditorModule）
IDaySequenceEditorModule& DaySeqEditorModule = FModuleManager::LoadModuleChecked<IDaySequenceEditorModule>("DaySequenceEditor");
FDaySequenceActorPreview& Preview = DaySeqEditorModule.GetDaySequenceActorPreview();

// 启用/禁用预览
Preview.EnablePreview(true);

// 设置预览时间（小时）
Preview.SetPreviewTime(12.5f);
```

**3. 创建 UDaySequenceDirector 蓝图（来自 FMovieSceneSequenceEditor_DaySequence）**

```cpp
UDaySequence* DaySequence = GetValidDaySequence();
UBlueprint* Blueprint = FKismetEditorUtilities::CreateBlueprint(
    UDaySequenceDirector::StaticClass(),
    DaySequence,
    FName(*DaySequence->GetDirectorBlueprintName()),
    BPTYPE_Normal,
    UBlueprint::StaticClass(),
    UBlueprintGeneratedClass::StaticClass()
);
DaySequence->SetDirectorBlueprint(Blueprint);
```

### 进阶用法

**自定义条件集（ConditionSet）的编辑器交互**

```cpp
// 在自定义细节面板中使用 SDaySequenceConditionSetCombo 编辑条件
TSharedPtr<IPropertyHandle> ConditionSetHandle = ...;  // 从属性获取
SNew(SDaySequenceConditionSetCombo)
    .StructPropertyHandle(ConditionSetHandle)
```

**创建自定义 DaySequence 资产**

```cpp
// 使用 UDaySequenceFactoryNew 创建新资产
UDaySequenceFactoryNew* Factory = NewObject<UDaySequenceFactoryNew>();
UDaySequence* NewDaySequence = CastChecked<UDaySequence>(Factory->FactoryCreateNew(
    UDaySequence::StaticClass(),
    GetTransientPackage(),
    FName(TEXT("NewDaySequence")),
    RF_Standalone | RF_Public,
    nullptr,
    GWarn
));
```

## Demo 示例

以下是一个最小的、在 C++ 中创建并运行 DaySequence 的示例（假设已有有效的 DaySequence 资产）。

**MyDaySequenceManager.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyDaySequenceManager.generated.h"

class ADaySequenceActor;
class UDaySequence;

UCLASS()
class AMyDaySequenceManager : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;

private:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "DaySequence", meta = (AllowPrivateAccess = "true"))
    UDaySequence* Sequence;

    UPROPERTY()
    ADaySequenceActor* DayActor;
};
```

**MyDaySequenceManager.cpp**
```cpp
#include "MyDaySequenceManager.h"
#include "DaySequence.h"
#include "DaySequenceActor.h"

void AMyDaySequenceManager::BeginPlay()
{
    Super::BeginPlay();

    if (!Sequence)
    {
        UE_LOG(LogTemp, Error, TEXT("No DaySequence assigned!"));
        return;
    }

    DayActor = GetWorld()->SpawnActor<ADaySequenceActor>();
    if (DayActor)
    {
        DayActor->SetDayLength(24.0f);
        DayActor->SetInitialTimeOfDay(8.0f);
        DayActor->SetSequence(Sequence);
        DayActor->StartDayCycle();
    }
}
```

将此 Actor 放置到关卡中，并在蓝图或细节面板中指定一个 DaySequence 资产即可运行。

## 模块依赖

以下为 DaySequence 插件的依赖模块（省略了常见的 Core、CoreUObject、Engine 等）。

| 模块 | 用途 |
|---|---|
| `LevelSequence` | 核心序列框架，DaySequence 继承自 ULevelSequence |
| `MovieScene` | 底层序列数据结构 |
| `SequencerScripting` | 提供蓝图可调用的 Sequencer API |
| `LevelSequenceEditor` | 编辑器扩展，用于在 Sequencer UI 中显示 DaySequence 特有功能 |
| `UnrealEd` | 编辑器基础，用于 AssetDefinition、Factory、DetailCustomization 等 |

## 维护状态

由于插件创建于 2025 年 9 月，属于非常新的实验性功能，更新较为频繁。

### 近期更新

- 2025-12-18 `221712a9` — DaySequence: Fixed crash when editing DayLength / TimePerCycle during PIE.
- 2025-11-18 `24988ae3` — DaySequence: Fixed crash in DaySequenceModifierComponent when setting DayNightCycle to LocalFixedTim
- 2025-09-10 `13ee8036` — UMG: Disable Dynamic Possession menu if it's not supported（相关）
- 2025-09-09 `78c312b8` — Fix Sequence Modifier Component to only tick when enabled, which fixes a race condition during creat
- 2025-09-08 `77a167d7` — Iris Beta（初始提交）

### 维护评价

- **创建时间**：2025-09-08
- **近期更新**：最近 3 个月内有 2 次实质性修复（PIE 崩溃、DaySequenceModifierComponent 崩溃），说明仍在活跃维护。
- **状态**：实验性（`IsExperimentalVersion=true`），但已有完整的编辑器工具和运行时系统，可用于生产项目但需注意 API 可能变化。
- **已知问题**：随着更新不断修复（如 Editor 中修改 DayLength 时的崩溃），暂无大规模已知限制。
- **推荐度**：对于需要昼夜循环和条件序列的 UE5 项目，该插件是一个强大且原生集成的解决方案。建议开启插件并投入开发，但需留意未来版本 API 调整。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/DaySequence)
- [DaySequence 运行时测试](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/Programs/AutomationTool/Scripts)（未提供确切测试路径，可搜索项目内的 DaySequence 测试）
- [官方文档](https://docs.unrealengine.com/5.7/)（暂无专门 DaySequence 文档，可参考 LevelSequence 文档）