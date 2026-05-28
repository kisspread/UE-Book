# Motion Trajectory

> Generate predictions and track history of character motion.

| 属性 | 值 |
|---|---|
| 中文名 | 运动轨迹 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MotionTrajectory` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-17 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/MotionTrajectory) | |

## 用途

Motion Trajectory 是 **Motion Matching（运动匹配）动画系统的底层基础设施**，专门解决角色运动轨迹数据的采集和预测问题。

在 Motion Matching 系统中，动画数据库需要知道角色"从哪来"和"往哪去"，才能从数据库中匹配到最合适的动画片段。这个插件提供：

1. **历史轨迹采集**：以帧率无关的方式记录角色过去一段时间的运动轨迹，支持在移动平台上正确工作（只记录角色意图产生的位移，不包含平台运动）
2. **未来轨迹预测**：模拟 UCharacterMovementComponent 的地面移动物理，预测角色未来的运动轨迹
3. **轨迹采样配置**：统一的采样率、时间域配置结构体，供 Motion Matching、Pose Search 等系统共用

该插件从 PoseSearch 中拆分而来，将"过去轨迹采样"和"预测轨迹生成"独立为通用组件，使得轨迹数据可以在不同动画系统间复用。

## 使用场景

- 你正在使用 **Motion Matching** 系统，需要为角色生成过去+未来的运动轨迹 → 用 `UCharacterTrajectoryComponent`
- 你的角色在**移动平台**上战斗，需要正确记录不含平台位移的运动历史 → 该组件原生支持
- 你需要对轨迹做 **2D 展平**或**方向离散化**（如投影到 8 方向）→ 使用蓝图库函数
- 你的游戏有**非标准重力**（如墙壁行走、天花板）→ `bEnableNonStandardGravity` 支持
- 你想在 `UAnimInstance` 中手动计算轨迹，不依赖组件 → 直接使用 `FMotionTrajectoryLibrary` 静态函数

## 蓝图用法

`UCharacterTrajectoryComponent` 本身是 `Blueprintable` 的组件，可以像普通组件一样添加到角色上。其内部数据通过 `BlueprintReadOnly` 暴露给蓝图。

### 核心节点

| 属性 | 说明 | 所在类 |
|---|---|---|
| `Trajectory` | 世界空间下的完整轨迹数据（历史+预测），可直接传给 Motion Matching | `UCharacterTrajectoryComponent` |
| `SamplingData` | 采样配置（历史/预测时长、采样率） | `UCharacterTrajectoryComponent` |
| `CharacterTrajectoryData` | 角色移动参数和轨迹预测配置 | `UCharacterTrajectoryComponent` |

### 使用示例（蓝图描述）

**基础用法**：
1. 在角色蓝图中添加 `UCharacterTrajectoryComponent`
2. 组件自动监听 `OnMovementUpdated`，每帧更新轨迹数据
3. 在动画蓝图中，通过 `Get Trajectory` 节点读取 `Trajectory` 属性
4. 将轨迹数据传入 Motion Matching 节点或 Pose Search 节点

**自定义采样配置**：
- 在组件实例上覆盖 `SamplingData` 的属性：
  - `HistoryLengthSeconds`：历史时长（默认 1.5 秒）
  - `PredictionLengthSeconds`：预测时长（默认 1.5 秒）
  - `HistorySamplesPerSecond`：历史采样率（默认 5，范围 1-120）
  - `PredictionSamplesPerSecond`：预测采样率（默认 5，范围 1-120）

**调整预测行为**：
- `RotateTowardsMovementSpeed`：朝向运动方向的旋转速度（默认 10）
- `MaxControllerYawRate`：控制器偏航率上限（默认 70°/秒，负值禁用限制）
- `BendVelocityTowardsAcceleration`：将速度方向向加速度方向弯曲的程度（0-1），值越大转弯越尖锐
- `SpeedRemappingCurve`：速度重映射曲线（可选）
- `AccelerationRemappingCurve`：加速度重映射曲线（可选）
- `bEnableNonStandardGravity`：启用非标准重力支持（墙壁/天花板行走）

## C++ 用法

### 头文件引入

```cpp
#include "MotionTrajectoryLibrary.h"
#include "CharacterTrajectoryComponent.h"
```

### 基本用法

使用组件自动管理轨迹（最简单的方式）：

```cpp
// 在角色构造函数或 BeginPlay 中
UCharacterTrajectoryComponent* TrajectoryComp = 
    NewObject<UCharacterTrajectoryComponent>(this);
TrajectoryComp->RegisterComponent();

// 组件会自动在 OnMovementUpdated 中更新轨迹
// 通过 Trajectory 属性获取当前轨迹数据
FTransformTrajectory& Trajectory = TrajectoryComp->GetTrajectory(); // 通过 protected 或 friend 访问
```

### 进阶用法：在 AnimInstance 中手动计算轨迹

如果你不想使用组件（例如需要在动画线程中处理），可以直接调用 `FMotionTrajectoryLibrary` 的静态函数：

```cpp
#include "MotionTrajectoryLibrary.h"

// 假设在 UAnimInstance 的某个更新函数中
void UMyAnimInstance::UpdateTrajectory()
{
    ACharacter* Character = Cast<ACharacter>(TryGetPawnOwner());
    if (!Character) return;

    // 1. 配置采样参数
    FTrajectorySamplingData SamplingData;
    SamplingData.HistoryLengthSeconds = 1.5f;
    SamplingData.HistorySamplesPerSecond = 5;
    SamplingData.PredictionLengthSeconds = 1.5f;
    SamplingData.PredictionSamplesPerSecond = 5;
    SamplingData.Init(); // 初始化计算内部缓存

    // 2. 更新角色数据
    FCharacterTrajectoryData CharacterData;
    CharacterData.UpdateDataFromCharacter(DeltaSeconds, Character);

    // 3. 初始化轨迹采样点
    FTransformTrajectory Trajectory;
    FVector Position = Character->GetActorLocation();
    FQuat Facing = Character->GetActorQuat();
    FMotionTrajectoryLibrary::InitTrajectorySamples(Trajectory, SamplingData, Position, Facing);

    // 4. 更新历史轨迹（移动平台安全）
    TArray<FVector> TranslationHistory;
    FMotionTrajectoryLibrary::UpdateHistory_TransformHistory(
        Trajectory, TranslationHistory, CharacterData, SamplingData, DeltaSeconds);

    // 5. 生成预测轨迹
    FMotionTrajectoryLibrary::UpdatePrediction_SimulateCharacterMovement(
        Trajectory, CharacterData, SamplingData);

    // 现在 Trajectory 包含完整的过去+未来轨迹，可传给 Motion Matching
}
```

**来源**：`Source/MotionTrajectory/Public/MotionTrajectoryLibrary.h`

### 进阶用法：自定义轨迹预测参数

```cpp
FCharacterTrajectoryData CharacterData;
CharacterData.UpdateDataFromCharacter(DeltaSeconds, Character);

// 调整预测行为
CharacterData.RotateTowardsMovementSpeed = 15.f;  // 更快的朝向旋转
CharacterData.MaxControllerYawRate = 90.f;         // 更高的控制器偏航率
CharacterData.BendVelocityTowardsAcceleration = 0.3f; // 轻微弯曲速度方向
CharacterData.bEnableNonStandardGravity = true;    // 支持非标准重力

// 可选：使用速度重映射曲线
CharacterData.bUseSpeedRemappingCurve = true;
CharacterData.SpeedRemappingCurve.GetRichCurve()->AddKey(0.f, 0.f);
CharacterData.SpeedRemappingCurve.GetRichCurve()->AddKey(600.f, 400.f);
```

## Demo 示例

一个最小的自定义轨迹预测组件示例，展示如何扩展轨迹计算逻辑：

```cpp
// MyCustomTrajectoryComponent.h
#pragma once

#include "CoreMinimal.h"
#include "MotionTrajectoryLibrary.h"
#include "Components/ActorComponent.h"
#include "MyCustomTrajectoryComponent.generated.h"

UCLASS(ClassGroup = (Animation), meta = (BlueprintSpawnableComponent))
class MYGAME_API UMyCustomTrajectoryComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyCustomTrajectoryComponent();

    virtual void BeginPlay() override;
    virtual void TickComponent(float DeltaTime, ELevelTick TickType,
        FActorComponentTickFunction* ThisTickFunction) override;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Trajectory")
    FTrajectorySamplingData SamplingData;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Trajectory")
    FCharacterTrajectoryData CharacterTrajectoryData;

    UPROPERTY(BlueprintReadOnly, Category = "Trajectory")
    FTransformTrajectory Trajectory;

private:
    TArray<FVector> TranslationHistory;
};
```

```cpp
// MyCustomTrajectoryComponent.cpp
#include "MyCustomTrajectoryComponent.h"
#include "GameFramework/Character.h"

UMyCustomTrajectoryComponent::UMyCustomTrajectoryComponent()
{
    PrimaryComponentTick.bCanEverTick = true;
    SamplingData.HistoryLengthSeconds = 1.5f;
    SamplingData.HistorySamplesPerSecond = 5;
    SamplingData.PredictionLengthSeconds = 1.5f;
    SamplingData.PredictionSamplesPerSecond = 5;
}

void UMyCustomTrajectoryComponent::BeginPlay()
{
    Super::BeginPlay();
    SamplingData.Init();
    CharacterTrajectoryData.Init(); // 如果存在此方法
}

void UMyCustomTrajectoryComponent::TickComponent(float DeltaTime,
    ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    ACharacter* Character = Cast<ACharacter>(GetOwner());
    if (!Character) return;

    // 更新角色数据
    CharacterTrajectoryData.UpdateDataFromCharacter(DeltaTime, Character);

    // 初始化采样点
    FMotionTrajectoryLibrary::InitTrajectorySamples(
        Trajectory, SamplingData,
        Character->GetActorLocation(),
        Character->GetActorQuat());

    // 更新历史（移动平台安全）
    FMotionTrajectoryLibrary::UpdateHistory_TransformHistory(
        Trajectory, TranslationHistory,
        CharacterTrajectoryData, SamplingData, DeltaTime);

    // 生成预测轨迹
    FMotionTrajectoryLibrary::UpdatePrediction_SimulateCharacterMovement(
        Trajectory, CharacterTrajectoryData, SamplingData);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PoseSearch` | Motion Matching 核心模块，提供 `FTransformTrajectory` 等轨迹数据结构 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-21 | `dcffc04a` | Support for non standard gravity in motion trajectory library | 支持非标准重力下的轨迹预测 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到 UE_LOGF |
| 2025-06-26 | `ec900998` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. | 添加内联生成宏优化编译 |
| 2025-04-23 | `939cc6e5` | Used FortniteClient build target to find and convert all files to have dllstorage on methods/staticv | DLL 导出标记批量转换 |
| 2025-02-14 | `f9bb934d` | Deprecated PoseSearch specific's FPoseSearchQueryTrajectory and FPoseSearchQueryTrajectorySample in ... | 废弃 PoseSearch 专有轨迹结构，迁移通用结构 |

### 维护评价

**维护状态：活跃维护中** ✅

- 2026 年 4 月仍有功能更新（非标准重力支持），说明仍在积极开发
- 近期更新包含功能增强（非标准重力）、代码现代化（UE_LOGF 迁移）和 API 统一（废弃冗余结构体）
- 作为 PoseSearch / Motion Matching 系统的关键基础设施，属于活跃开发链路
- 当前仍标记为 **Experimental**，未默认启用，API 可能会有 breaking changes
- **推荐使用**，但需注意实验性标记，未来版本可能出现接口变更

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/MotionTrajectory)
- 官方文档：无