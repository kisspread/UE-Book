# ZoneGraph Annotations

> Annotations for Zone Graph

| 属性 | 值 |
|---|---|
| 分类 | AI |
| 默认启用 | ❌ 需手动启用 |
| 包含内容 | ✅ |
| 模块 | ZoneGraphAnnotations (Runtime) |
| 创建时间 | 2021-09-28 |
| 年龄标签 | 🆕 (≤5年) |
| 实验性版本 | ✅ IsExperimentalVersion |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ZoneGraphAnnotations) | |

## 用途

ZoneGraph Annotations 是 ZoneGraph 的**运行时动态标签系统**。ZoneGraph 本身只存储静态的车道标签（例如"人行道"、"车道"），而这个 plugin 允许你在运行时给车道附加**动态变化的标签**——比如"这里很危险"、"这里有障碍物"。

核心解决的问题：**让 Mass AI 代理能够感知并规避运行时出现的危险区域**。

工作原理是：通过事件系统报告危险区域（位置+半径+持续时间），Annotation 组件会计算哪些车道受到影响，为每条受影响的车道计算**逃生成本**（escape cost），然后给这些车道打上动态标签。其他系统（如 Mass 代理的寻路逻辑）可以通过查询这些标签来决定是否避开某条车道。

### 架构概览

```
UZoneGraphAnnotationSubsystem (WorldSubsystem)
  ├── 管理所有 Annotation 组件
  ├── 维护每条车道的动态标签位掩码
  ├── 双缓冲事件分发
  └── 每帧 Tick 驱动 Annotation 更新

UZoneGraphAnnotationComponent (抽象基类)
  └── UZoneGraphDisturbanceAnnotation (具体实现)
        ├── 接收 FZoneGraphDisturbanceArea 事件 (危险区域)
        ├── 接收 FZoneGraphObstacleDisturbanceArea 事件 (障碍物)
        ├── 计算逃生图 (Escape Graph)
        └── 给受影响车道打 Danger/Obstacle 标签
```

## 使用场景

- 你的游戏中有爆炸、火灾等区域效果，需要让 NPC 绕行 → 用 Disturbance Annotation
- 你用 Mass Entity 做大量 AI 代理的交通模拟，需要动态标记拥堵/事故区域 → 用这个 plugin 的事件系统
- 你需要在运行时给 ZoneGraph 车道附加"危险"标签，让寻路系统感知并规避 → 用这个 plugin

> ⚠️ 这个 plugin 是**实验性**的 (`IsExperimentalVersion: true`)，且**默认不启用**。需要在 Plugins 面板手动启用，且依赖 [ZoneGraph](../ZoneGraph/index.md) plugin。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Trigger Danger` | 在指定位置触发一个危险区域事件 | `UZoneGraphDisturbanceAnnotationBPLibrary` |

### Trigger Danger 节点详情

```
Trigger Danger (WorldContextObject, Instigator, Position, Radius, Duration)
```

| 参数 | 类型 | 说明 |
|---|---|---|
| WorldContextObject | Object | 世界上下文（自动连接） |
| Instigator | Actor | 触发者（可选），相同 Instigator 的事件会被合并 |
| Position | Vector | 危险区域中心位置 |
| Radius | Float | 危险区域半径（厘米） |
| Duration | Float | 危险持续时间（秒） |

### 使用示例（蓝图描述）

**在爆炸发生时触发危险区域：**

1. 在你的爆炸 Actor 的蓝图中，添加一个 `Event AnyDamage` 或自定义爆炸事件
2. 连接 `Trigger Danger` 节点
3. `Position` → 连接到爆炸位置（`GetActorLocation`）
4. `Radius` → 设置爆炸影响半径，例如 `500`
5. `Duration` → 设置危险持续时间，例如 `10.0`（秒）
6. `Instigator` → 连接到 `Self`

**在场景中放置 Disturbance Annotation 组件：**

1. 创建一个 Actor（或使用已有 Actor）
2. 添加 `ZoneGraphDisturbanceAnnotation` 组件
3. 在 Details 面板中配置：
   - `Danger Annotation Tag` → 选择一个 ZoneGraph Tag（如 Tag 5）用于标记危险车道
   - `Obstacle Annotation Tag` → 选择另一个 Tag（如 Tag 6）用于标记障碍物车道
   - `Affected Lane Tags` → 设置哪些类型的车道会被影响（如只影响机动车道）
   - `Escape Lane Tags` → 设置哪些类型的车道可以作为逃生路线
   - `Ideal Span Length` → 车道分段的理想长度（默认 500 厘米）
4. 勾选 `Enable Debug Drawing` 可在编辑器中可视化效果

## C++ 用法

### 头文件引入

```cpp
#include "ZoneGraphAnnotationSubsystem.h"
#include "ZoneGraphDisturbanceAnnotation.h"
#include "ZoneGraphDisturbanceAnnotationBPLibrary.h"
```

### 基本用法：发送危险事件

通过 Subsystem 的 `SendEvent()` 模板方法发送事件（来源：`ZoneGraphAnnotationSubsystem.h` L86-93）：

```cpp
// 获取 Annotation Subsystem
UZoneGraphAnnotationSubsystem* AnnotationSubsystem = GetWorld()->GetSubsystem<UZoneGraphAnnotationSubsystem>();

// 构造危险区域事件
FZoneGraphDisturbanceArea DangerEvent;
DangerEvent.Position = GetActorLocation();
DangerEvent.Radius = 500.0f;
DangerEvent.Duration = 10.0f;
DangerEvent.InstigatorID = GetUniqueID(); // 可选，用于合并同一来源的事件

// 发送事件
AnnotationSubsystem->SendEvent(DangerEvent);
```

### 基本用法：发送障碍物事件

```cpp
FZoneGraphObstacleDisturbanceArea ObstacleEvent;
ObstacleEvent.Position = ObstacleLocation;
ObstacleEvent.Radius = 300.0f;       // 干扰半径
ObstacleEvent.ObstacleRadius = 50.0f; // 障碍物本身半径
ObstacleEvent.ObstacleID = FMassLaneObstacleID::GetNextUniqueID();
ObstacleEvent.Action = EZoneGraphObstacleDisturbanceAreaAction::Add;

AnnotationSubsystem->SendEvent(ObstacleEvent);

// 移除障碍物时
FZoneGraphObstacleDisturbanceArea RemoveEvent;
RemoveEvent.ObstacleID = ObstacleEvent.ObstacleID; // 使用相同的 ID
RemoveEvent.Action = EZoneGraphObstacleDisturbanceAreaAction::Remove;

AnnotationSubsystem->SendEvent(RemoveEvent);
```

### 查询车道的动态标签

```cpp
// 获取某条车道当前的动态标签
FZoneGraphTagMask Tags = AnnotationSubsystem->GetAnnotationTags(LaneHandle);

// 检查是否被标记为危险
FZoneGraphTag DangerTag(5); // 假设 Tag 5 是 Danger 标签
if (Tags.Contains(DangerTag))
{
    // 这条车道目前是危险的，应该避开
}
```

### 查询逃生动作

```cpp
// 假设你有指向 UZoneGraphDisturbanceAnnotation 的指针
const FZoneGraphEscapeLaneAction* EscapeAction = DisturbanceAnnotation->GetEscapeAction(LaneHandle);

if (EscapeAction)
{
    // 找到当前距离对应的 span
    uint8 SpanIndex = EscapeAction->FindSpanIndex(CurrentDistanceAlongLane);
    const FZoneGraphEscapeLaneSpan& Span = EscapeAction->Spans[SpanIndex];

    // 检查是否有逃生方向
    if (Span.bLeadsToExit)
    {
        // 沿着 Span 指示的方向逃离
        bool bShouldReverse = Span.bReverseLaneDirection;
        int32 ExitLane = Span.ExitLaneIndex;
        float Cost = Span.EscapeCost; // 越低越安全
    }
}
```

### 进阶用法：自定义 Annotation 组件

继承 `UZoneGraphAnnotationComponent` 创建自己的 Annotation：

```cpp
UCLASS()
class UMyCustomAnnotation : public UZoneGraphAnnotationComponent
{
    GENERATED_BODY()

public:
    // 声明这个 Annotation 使用哪些标签
    virtual FZoneGraphTagMask GetAnnotationTags() const override
    {
        return FZoneGraphTagMask(FZoneGraphTag(10)); // 使用 Tag 10
    }

    // 每帧更新逻辑
    virtual void TickAnnotation(const float DeltaTime, FZoneGraphAnnotationTagContainer& AnnotationTagContainer) override
    {
        // 在这里修改 AnnotationTagContainer 中的标签
        // AnnotationTagContainer.GetMutableAnnotationTagsForData(DataHandle) 返回每条车道的标签数组
    }

    // 处理事件
    virtual void HandleEvents(const FInstancedStructContainer& Events) override
    {
        for (const FConstStructView& Event : Events)
        {
            if (const FMyCustomEvent* MyEvent = Event.GetPtr<const FMyCustomEvent>())
            {
                // 处理自定义事件
            }
        }
    }

    // ZoneGraph 数据加载/卸载回调
    virtual void PostZoneGraphDataAdded(const AZoneGraphData& ZoneGraphData) override { /* 初始化 */ }
    virtual void PreZoneGraphDataRemoved(const AZoneGraphData& ZoneGraphData) override { /* 清理 */ }
};
```

## Demo 示例

### 最小可编译示例：在 C++ 中触发危险区域

**Build.cs 依赖：**

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "ZoneGraph",
    "ZoneGraphAnnotations"
});
```

**DangerTriggerActor.h：**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DangerTriggerActor.generated.h"

UCLASS()
class ADangerTriggerActor : public AActor
{
    GENERATED_BODY()

public:
    // 蓝图可调用的触发函数
    UFUNCTION(BlueprintCallable)
    void TriggerDangerZone();

protected:
    UPROPERTY(EditAnywhere, Category = "Danger")
    float DangerRadius = 500.0f;

    UPROPERTY(EditAnywhere, Category = "Danger")
    float DangerDuration = 10.0f;
};
```

**DangerTriggerActor.cpp：**

```cpp
#include "DangerTriggerActor.h"
#include "ZoneGraphAnnotationSubsystem.h"
#include "ZoneGraphDisturbanceAnnotation.h"

void ADangerTriggerActor::TriggerDangerZone()
{
    UZoneGraphAnnotationSubsystem* Subsystem = GetWorld()->GetSubsystem<UZoneGraphAnnotationSubsystem>();
    if (!Subsystem) return;

    FZoneGraphDisturbanceArea Danger;
    Danger.Position = GetActorLocation();
    Danger.Radius = DangerRadius;
    Danger.Duration = DangerDuration;
    Danger.InstigatorID = GetUniqueID();

    Subsystem->SendEvent(Danger);
}
```

**场景设置：**

1. 在场景中放置 `ADangerTriggerActor`
2. 确保场景中有 ZoneGraph Data（通过 ZoneShape 创建）
3. 在场景中放置一个带 `UZoneGraphDisturbanceAnnotation` 组件的 Actor
4. 配置 Annotation 的 Tag 设置
5. 调用 `TriggerDangerZone()` 后，受影响车道会被打上动态标签

## 模块依赖

从 `ZoneGraphAnnotations.Build.cs` 的 `PublicDependencyModuleNames` 提取：

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 反射系统 |
| `Engine` | 引擎核心（Actor、World 等） |
| `RHI` | 渲染硬件接口 |
| `ZoneGraph` | ZoneGraph 核心模块（车道数据、查询） |
| `ZoneGraphDebug` | ZoneGraph 调试绘制 |
| `MassEntity` | Mass Entity 框架（子系统注册） |

Plugin 依赖：

| Plugin | 用途 |
|---|---|
| `ZoneGraph` | 提供 ZoneGraph 基础设施 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-06-26 | `ec900998` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files | 代码质量改进，非功能性变更 |
| 2025-06-10 | `b08804f0` | Replace some usages of FORCEINLINE with inline in AI modules | 编译器兼容性修复 |
| 2025-04-23 | `939cc6e5` | Converted files to have dllstorage on methods/staticvar | DLL 导出规范化 |

### 维护评价

- **创建时间**：2021-09-28，约 4.6 年前
- **最近更新**：2025-06-26，最近一次更新是代码质量/编译兼容性修复
- **实质性功能更新**：近期 3 次提交均为自动化代码维护，无新功能
- **实验性状态**：`.uplugin` 中 `IsExperimentalVersion: true`，`EnabledByDefault: false`
- **推荐程度**：⚠️ 实验性 plugin，功能稳定但 API 可能在未来版本变更。如果你的项目深度依赖 Mass + ZoneGraph 的 AI 寻路方案，可以使用；否则建议关注后续版本是否转为正式。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ZoneGraphAnnotations)
- [ZoneGraph plugin 文档](../ZoneGraph/index.md)
