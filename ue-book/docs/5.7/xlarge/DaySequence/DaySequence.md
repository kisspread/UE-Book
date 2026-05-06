# DaySequence

> （无描述）

| 属性 | 值 |
|---|---|
| 中文名 | 昼夜序列 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、示例Actor） |
| 模块 | `DaySequence` (Runtime), `DaySequenceEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-08 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/DaySequence) | |

## 用途

DaySequence 是一个基于 Sequencer 的昼夜循环系统。它利用 Level Sequence 的核心架构，针对“时间驱动动画”这一特殊场景进行了定制和优化。

与传统的 Level Sequence 不同，DaySequence 专注于解决以下问题：

1.  **时间驱动**：它不是由用户交互（如播放/暂停）驱动，而是由游戏内时间（Time of Day）驱动。系统会根据当前时间自动计算并播放对应的 Sequence 片段。
2.  **混合与过渡**：支持多个 DaySequence 资产（或程序化生成的序列）同时激活，并根据特定的权重（如距离、优先级）进行混合，实现平滑的过渡效果。例如，从晴朗天气过渡到暴风雨天气。
3.  **条件激活**：通过 `UDaySequenceConditionTag` 系统，可以根据游戏状态（如玩家是否在室内、是否触发特定事件）来决定哪些 DaySequence 应该被激活。
4.  **程序化生成**：提供了 `FProceduralDaySequence` 基类和 `UProceduralDaySequenceBuilder`，允许开发者通过 C++ 或蓝图代码动态生成序列曲线，例如根据地理位置计算太阳位置、创建正弦波驱动的动画等。
5.  **性能优化**：内置了“静态时间”系统，允许外部系统（如灯光更新系统）在序列不播放时，直接读取当前时间对应的动画值，避免了不必要的序列寻址和求值开销。

它是替代手动制作数百个不同时间段 Sequence 的现代化方案，特别适用于开放世界、沙盒游戏等需要动态变化的环境系统。

## 使用场景

- **开放世界昼夜循环**：你需要让游戏世界根据真实或游戏内时间，平滑地经历日出、正午、日落、夜晚等不同光照和天气状态。
- **动态天气系统**：根据玩家位置或游戏事件，在不同区域播放不同的天气序列（如下雨、起雾）。
- **时间驱动的游戏机制**：某些敌人、NPC 或环境交互只在特定时间激活。
- **精确的天文模拟**：根据纬度、经度和日期，精确计算太阳（和月亮）在天空中的位置，并驱动光照。
- **性能敏感的动画**：灯光、天空球等需要每帧更新的属性，可以通过“静态时间”系统直接采样，避免全局序列寻址的开销。

## 蓝图用法

DaySequence 提供了丰富的蓝图节点，用于控制时间、条件切换和序列生成。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Day Sequence Actor` | 获取当前世界的 DaySequence Actor。 | `UDaySequenceSubsystem` |
| `Set Day Sequence Actor` | 设置当前世界的 DaySequence Actor。 | `UDaySequenceSubsystem` |
| `Bind To Day Sequence Actor` | 将一个 `UDaySequenceStaticTimeContributor` 绑定到指定的 DaySequence Actor 上，用于贡献静态时间。 | `UDaySequenceStaticTimeContributor` |
| `Unbind` | 解除该 Contributor 与 DaySequence Actor 的绑定。 | `UDaySequenceStaticTimeContributor` |
| `Evaluate` | 由 `UDaySequenceConditionTag` 的子类实现，用于评估条件是否满足。 | `UDaySequenceConditionTag` |
| `Broadcast On Condition Value Changed` | 当条件值可能发生变化时调用，触发系统重新评估条件。 | `UDaySequenceConditionTag` |
| `On Day Sequence Actor Set` | 事件，当系统活动的 DaySequence Actor 发生变化时触发。 | `UDaySequenceSubsystem` |
| `Add Scalar Key` | 为当前绑定的 Actor 的某个 float 属性添加关键帧。 | `UProceduralDaySequenceBuilder` |
| `Add Bool Key` | 为当前绑定的 Actor 的某个 bool 属性添加关键帧。 | `UProceduralDaySequenceBuilder` |
| `Add Vector Key` | 为当前绑定的 Actor 的某个 Vector 属性添加关键帧。 | `UProceduralDaySequenceBuilder` |

### 使用示例（蓝图描述）

**示例 1：获取并设置主角色的 DaySequence Actor**

1.  在 Game Mode 或 Player Controller 的 BeginPlay 事件中。
2.  调用 `Get Day Sequence Actor` 节点，从 `DaySequenceSubsystem` 获取。
3.  将返回的 `Return Value` 连接到 `Set Day Sequence Actor` 节点，设置该 Actor 为活动 Actor。
4.  后续所有与时间相关的查询和播放都将基于此 Actor。

**示例 2：使用 StaticTimeContributor 控制灯光**

1.  创建一个 `UDaySequenceStaticTimeContributor` 变量。
2.  在 BeginPlay 中，使用 `Construct Object from Class` 创建该 Contributor。
3.  调用 `Bind To Day Sequence Actor`，传入创建的 Contributor 和一个优先级。
4.  在游戏的 Tick 或其他逻辑中，设置 Contributor 的 `BlendWeight` 和 `StaticTime`。
5.  DaySequence Actor 会将此静态时间与其他来源（如正常播放）混合，最终驱动相关属性的动画。

## C++ 用法

### 头文件引入

```cpp
#include "DaySequenceActor.h"
#include "DaySequenceSubsystem.h"
#include "DaySequencePlayer.h"
#include "DaySequenceStaticTime.h"
```

### 基本用法

**获取 DaySequence Actor 并播放**

```cpp
// 获取当前世界的 DaySequenceSubsystem
if (UWorld* World = GetWorld())
{
    if (UDaySequenceSubsystem* Subsystem = World->GetSubsystem<UDaySequenceSubsystem>())
    {
        // 获取活动的 DaySequence Actor
        ADaySequenceActor* DaySeqActor = Subsystem->GetDaySequenceActor();
        if (DaySeqActor)
        {
            // 获取其 Player 并开始播放
            if (IDaySequencePlayer* Player = DaySeqActor->GetSequencePlayer())
            {
                Player->Play();
            }
        }
    }
}
```

**使用静态时间系统贡献时间**

```cpp
// 创建一个静态时间贡献者
UDaySequenceStaticTimeContributor* MyContributor = NewObject<UDaySequenceStaticTimeContributor>();

// 绑定到指定的 DaySequence Actor，优先级为 500
MyContributor->BindToDaySequenceActor(DaySeqActor, 500);

// 设置属性
MyContributor->BlendWeight = 0.5f;
MyContributor->StaticTime = 0.25f;  // 对应序列的 25% 位置
MyContributor->bWantsStaticTime = true;

// ... 稍后可以解绑
MyContributor->Unbind();
```

### 进阶用法

**创建自定义条件标签**

继承 `UDaySequenceConditionTag`，并实现 `Evaluate` 和 `SetupOnConditionValueChanged`：

```cpp
// MyCustomCondition.h
UCLASS()
class UMyCustomCondition : public UDaySequenceConditionTag
{
    GENERATED_BODY()

public:
    virtual bool Evaluate_Implementation() const override
    {
        // 自定义逻辑，例如检查玩家是否在某个区域内
        return bIsPlayerInZone;
    }

protected:
    virtual void SetupOnConditionValueChanged_Implementation() const override
    {
        // 绑定到改变此条件值的外部事件
        SomeDelegate.BindUObject(this, &UMyCustomCondition::BroadcastOnConditionValueChanged);
    }

private:
    bool bIsPlayerInZone = false;
};
```

**创建程序化序列**

继承 `FProceduralDaySequence`，并重写 `BuildSequence`：

```cpp
// MyProceduralSequence.h
USTRUCT()
struct FMyProceduralSequence : public FProceduralDaySequence
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere)
    FName PropertyName = "Intensity";

private:
    virtual void BuildSequence(UProceduralDaySequenceBuilder* InBuilder) override
    {
        // 1. 绑定目标 Actor（例如 BaseDaySequenceActor）
        UDaySequence* Seq = InBuilder->Initialize(CastChecked<ADaySequenceActor>(WeakTargetActor.Get()));
        
        // 2. 设置要动画化的对象
        InBuilder->SetActiveBoundObject(WeakTargetActor.Get());

        // 3. 添加关键帧
        InBuilder->AddScalarKey(PropertyName, 0.0f, 1.0f);
        InBuilder->AddScalarKey(PropertyName, 0.3f, 0.5f);
        InBuilder->AddScalarKey(PropertyName, 0.5f, 0.0f);
        InBuilder->AddScalarKey(PropertyName, 0.8f, 0.5f);
        InBuilder->AddScalarKey(PropertyName, 1.0f, 1.0f);
    }
};
```

## Demo 示例

以下是一个完整的 C++ 类，展示了如何在游戏世界中创建一个简单的 DaySequence Actor 并驱动其播放。

### DaySequenceManager.h
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DaySequenceManager.generated.h"

class ADaySequenceActor;

UCLASS()
class ADaySequenceManager : public AActor
{
    GENERATED_BODY()

public:
    ADaySequenceManager();

protected:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

private:
    UPROPERTY()
    TObjectPtr<ADaySequenceActor> DaySequenceActor;

    float CurrentTimeOfDay = 0.0f;
};
```

### DaySequenceManager.cpp
```cpp
#include "DaySequenceManager.h"
#include "DaySequenceActor.h"
#include "DaySequencePlayer.h"
#include "DaySequenceSubsystem.h"
#include "DaySequence.h"

ADaySequenceManager::ADaySequenceManager()
{
    PrimaryActorTick.bCanEverTick = true;
}

void ADaySequenceManager::BeginPlay()
{
    Super::BeginPlay();

    // 1. 尝试在世界中查找或创建 DaySequenceActor
    DaySequenceActor = Cast<ADaySequenceActor>(
        UGameplayStatics::GetActorOfClass(GetWorld(), ADaySequenceActor::StaticClass()));

    if (!DaySequenceActor)
    {
        // 如果没有，则创建一个新的
        FActorSpawnParameters SpawnParams;
        DaySequenceActor = GetWorld()->SpawnActor<ADaySequenceActor>(ADaySequenceActor::StaticClass(), SpawnParams);
    }

    // 2. 将其设置为系统的活动 Actor
    if (UDaySequenceSubsystem* Subsystem = GetWorld()->GetSubsystem<UDaySequenceSubsystem>())
    {
        Subsystem->SetDaySequenceActor(DaySequenceActor);
    }

    // 3. 设置序列并开始播放
    if (DaySequenceActor)
    {
        UDaySequence* Sequence = LoadObject<UDaySequence>(nullptr, TEXT("/Game/MyDaySequence.MyDaySequence"));
        if (Sequence)
        {
            FMovieSceneSequencePlaybackSettings Settings;
            DaySequenceActor->SetSequence(Sequence, Settings);
        }

        if (IDaySequencePlayer* Player = DaySequenceActor->GetSequencePlayer())
        {
            Player->Play();
        }
    }
}

void ADaySequenceManager::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    // 每帧更新游戏内时间
    CurrentTimeOfDay += DeltaTime * 0.1f; // 速度因子
    if (CurrentTimeOfDay > 86400.0f) CurrentTimeOfDay = 0.0f;

    if (DaySequenceActor)
    {
        DaySequenceActor->SetTimeOfDay(CurrentTimeOfDay);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LevelSequenceEditor` | 编辑器模式下，提供 Level Sequence 的编辑器和 UI 支持。 |
| `SequencerScripting` | 提供 Sequencer 的蓝图脚本化接口，用于创建和编辑序列。 |
| `MovieScene` | 核心电影场景系统。 |
| `PropertyAccess` | 高速属性访问支持。 |
| `StructUtils` | 对 `TInstancedStruct` 的支持，用于存储不同类型的程序化序列。 |