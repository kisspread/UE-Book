# Zone Graph Annotations

> Annotations for Zone Graph

| 属性 | 值 |
|---|---|
| 中文名 | 区域图标注 |
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资产、调试配置） |
| 模块 | `ZoneGraphAnnotations` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-28 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ZoneGraphAnnotations) | |

## 用途

ZoneGraphAnnotations 是 UE5 ZoneGraph 导航系统的扩展组件，用于在导航车道上动态添加"标注信息"。其核心解决的问题是：**当场景中出现危险区域或障碍物时，如何让 AI 代理感知这些危险并自动规划远离危险的逃生路径**。

该插件是 Mass AI 框架的一部分，通过事件驱动机制工作：
1. 游戏逻辑发送"危险事件"（如爆炸、火灾）到子系统
2. 子系统将事件分发给所有注册的标注组件
3. 标注组件计算受影响的车道，在其上标记标签
4. 逃生路径计算器为每条受影响车道生成逃离方向和成本
5. AI 代理在寻路时读取这些标注信息，选择更安全的路径

与 ZoneGraph 的基础车道标签不同，标注是**动态的**——可以随时间添加和移除，适用于运行时变化的场景。

## 使用场景

- 你的 AI 角色需要在爆炸发生后自动远离危险区域
- 场景中有动态生成的障碍物（如倒塌的建筑碎片），AI 需要绕行
- 你需要让 AI 在巡逻时避开特定区域（如正在燃烧的区域）
- 基于 Mass 框架构建的大量 AI 代理需要共享同一套动态危险信息

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Trigger Danger` | 在指定位置触发危险事件，影响周围车道 | `UZoneGraphDisturbanceAnnotationBPLibrary` |
| `Trigger` | 触发测试组件中配置的所有测试 | `AZoneGraphAnnotationTestingActor` |

### 触发危险事件

蓝图中最常用的节点是 `Trigger Danger`，用于在运行时创建危险区域：

```
[任意蓝图] → Trigger Danger
  ├─ Instigator: [可选] 触发源 Actor（同一触发源的多次事件会被合并）
  ├─ Position: 危险中心位置 (Vector)
  ├─ Radius: 危险影响半径 (Float)
  └─ Duration: 危险持续时间 (秒)
```

### 使用示例（蓝图描述）

**示例 1：爆炸产生危险区域**

```
[爆炸事件触发器 OnEvent]
    ↓
[Get Actor Location]
    ↓
Trigger Danger
  ├─ Instigator: Self
  ├─ Position: (爆炸位置)
  ├─ Radius: 500.0
  └─ Duration: 10.0
```

**示例 2：设置带标注的 AI 导航**

在场景中放置 `AZoneGraphAnnotationTestingActor`，在组件上配置 `UZoneGraphDisturbanceAnnotation`，设置：
- `Danger Annotation Tag`: 标记危险车道的标签
- `Affected Lane Tags`: 受影响的车道过滤器
- `Escape Lane Tags`: 可用于逃生的车道过滤器
- `Ideal Span Length`: 车道细分的理想长度（默认 500.0）

## C++ 用法

### 头文件引入

```cpp
#include "ZoneGraphAnnotationSubsystem.h"
#include "Annotations/ZoneGraphDisturbanceAnnotation.h"
#include "Annotations/ZoneGraphDisturbanceAnnotationBPLibrary.h"
```

### 基本用法

通过蓝图函数库触发危险事件：

```cpp
// 在任意位置触发危险事件
// 来源: ZoneGraphDisturbanceAnnotationBPLibrary.h
UZoneGraphDisturbanceAnnotationBPLibrary::TriggerDanger(
    GetWorld(),        // WorldContextObject
    GetOwner(),        // Instigator (可选，用于合并同源事件)
    TargetLocation,    // 危险中心
    500.0f,            // 危险半径
    10.0f              // 持续时间(秒)
);
```

查询特定车道的标注标签：

```cpp
// 来源: ZoneGraphAnnotationSubsystem.h
UZoneGraphAnnotationSubsystem* Subsystem = GetWorld()->GetSubsystem<UZoneGraphAnnotationSubsystem>();

// 获取车道上的所有标注标签
FZoneGraphTagMask Tags = Subsystem->GetAnnotationTags(LaneHandle);

// 根据标签查找对应的标注组件
UZoneGraphAnnotationComponent* Annotation = Subsystem->GetFirstAnnotationForTag(DangerTag);
```

### 进阶用法

自定义事件系统——通过模板化的 SendEvent 方法发送自定义事件：

```cpp
// 来源: ZoneGraphAnnotationSubsystem.h
UZoneGraphAnnotationSubsystem* Subsystem = GetWorld()->GetSubsystem<UZoneGraphAnnotationSubsystem>();

// 构建障碍物扰动事件
FZoneGraphObstacleDisturbanceArea ObstacleEvent;
ObstacleEvent.Position = ObstacleLocation;
ObstacleEvent.Radius = 300.0f;
ObstacleEvent.ObstacleRadius = 50.0f;
ObstacleEvent.ObstacleID = FMassLaneObstacleID::GetNextUniqueID();
ObstacleEvent.Action = EZoneGraphObstacleDisturbanceAreaAction::Add;

// 线程安全地发送事件（支持多线程调用）
Subsystem->SendEvent(ObstacleEvent);

// 移除障碍物时
FZoneGraphObstacleDisturbanceArea RemoveEvent;
RemoveEvent.ObstacleID = ObstacleEvent.ObstacleID;
RemoveEvent.Action = EZoneGraphObstacleDisturbanceAreaAction::Remove;
Subsystem->SendEvent(RemoveEvent);
```

查询逃生路径信息：

```cpp
// 来源: ZoneGraphDisturbanceAnnotation.h
// 获取 Disturbance 注解组件
UZoneGraphDisturbanceAnnotation* DisturbanceAnnotation = Cast<UZoneGraphDisturbanceAnnotation>(Annotation);

// 查询特定车道的逃生动作
const FZoneGraphEscapeLaneAction* EscapeAction = DisturbanceAnnotation->GetEscapeAction(LaneHandle);
if (EscapeAction)
{
    // 车道被分成了多个 Span，根据当前位置找到对应的 Span
    uint8 SpanIndex = EscapeAction->FindSpanIndex(CurrentDistanceAlongLane);
    const FZoneGraphEscapeLaneSpan& Span = EscapeAction->Spans[SpanIndex];
    
    // 获取逃生方向和出口信息
    if (Span.bLeadsToExit)
    {
        // 该段车道的逃离方向指向出口车道
        int32 ExitLane = Span.ExitLaneIndex;
        EZoneLaneLinkType LinkType = Span.ExitLinkType;
    }
    else if (Span.bReverseLaneDirection)
    {
        // 需要沿当前车道反向行驶
        FVector ReverseDirection = -Span.Direction;
    }
}
```

## Demo 示例

自定义一个触发危险的 Actor 组件：

**DangerTriggerComponent.h**
```cpp
#pragma once

#include "Components/ActorComponent.h"
#include "DangerTriggerComponent.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UDangerTriggerComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UDangerTriggerComponent();

    // 蓝图可调用：在当前位置触发危险
    UFUNCTION(BlueprintCallable, Category = "Danger")
    void TriggerLocalDanger(float Radius = 500.0f, float Duration = 10.0f);

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Danger")
    float DefaultRadius = 500.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Danger")
    float DefaultDuration = 10.0f;
};
```

**DangerTriggerComponent.cpp**
```cpp
#include "DangerTriggerComponent.h"
#include "Annotations/ZoneGraphDisturbanceAnnotationBPLibrary.h"

UDangerTriggerComponent::UDangerTriggerComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UDangerTriggerComponent::TriggerLocalDanger(float Radius, float Duration)
{
    AActor* Owner = GetOwner();
    if (!Owner) return;

    FVector Location = Owner->GetActorLocation();
    UZoneGraphDisturbanceAnnotationBPLibrary::TriggerDanger(
        GetWorld(),
        Owner,
        Location,
        Radius > 0.0f ? Radius : DefaultRadius,
        Duration > 0.0f ? Duration : DefaultDuration
    );
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `EditorFramework` | 编辑器框架支持（调试绘制等） |
| `UnrealEd` | 编辑器功能（编辑器内标签重注册等） |

注：该插件还隐式依赖 `ZoneGraph` 和 `MassEntity` 相关模块（通过 `FMassLaneObstacleID` 和 `ZoneGraphSubsystem` 等类型可见），但这些未在 Build.cs 中显式声明，可能通过间接依赖链引入。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移到 UE_LOGF 新格式 |
| 2026-04-01 | `58888966` | [MassCore] Move headers to Public/Mass/ subdirectory, strip Mass prefix from filenames | MassCore 头文件迁移，重构目录结构 |
| 2026-03-30 | `161605b0` | [Mass] Extract MassCore module from MassEntity | 从 MassEntity 中抽取 MassCore 模块，影响依赖结构 |
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 配置文件重命名，规范化命名 |
| 2025-06-26 | `ec900998` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. | 为源文件添加内联生成宏，优化编译 |

### 维护评价

该插件标记为**实验性**（`IsExperimentalVersion: true`）且**默认未启用**（`EnabledByDefault: false`），表明 Epic 尚未将其视为稳定 API。

**积极方面**：
- 最近更新（2026 年 4 月）仍在跟随 Mass 框架的重构进行适配，说明仍被 Epic 内部使用
- 代码结构清晰，有完善的调试绘制支持和测试框架
- 作为 ZoneGraph/Mass AI 生态的关键组件，不太可能被废弃

**注意事项**：
- API 可能随时发生变化（实验性标签）
- 版本号 0.5，尚未达到 1.0 正式版
- 依赖链中包含 Editor 模块（EditorFramework, UnrealEd），但在 Runtime 模块中使用，需注意打包兼容性
- 源文件较少（14 个），功能聚焦但覆盖面有限

**推荐**：如果你在使用 ZoneGraph + Mass AI 框架构建 AI 系统，这个插件值得启用和尝试，但需要做好 API 变更的心理准备。不建议在追求稳定性的生产项目中大量依赖。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ZoneGraphAnnotations)
- [官方文档]()（暂无）