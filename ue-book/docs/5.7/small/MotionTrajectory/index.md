# Motion Trajectory

> Generate predictions and track history of character motion.

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否（需手动启用） |
| 包含内容 | ✅ 是 |
| 模块 | MotionTrajectory (Runtime, PreDefault) |
| 创建时间 | 2021-09-16 |
| 年龄标签 | 🆕 (≤5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Animation/MotionTrajectory) | |

## 用途

MotionTrajectory 插件为 Motion Matching 系统提供轨迹数据支持。它解决的核心问题是：**如何为动画匹配系统提供角色的运动历史记录和未来预测**。

具体来说，这个插件做了两件事：
1. **历史记录**：跟踪角色过去一段时间的运动轨迹（位置和朝向）
2. **运动预测**：基于当前速度、加速度和控制器输入，模拟 `UCharacterMovementComponent` 的运动逻辑来预测角色未来的位置和朝向

这些轨迹数据存储在世界空间中，可以直接传递给 PoseSearch（Motion Matching）系统进行动画匹配。

插件提供了两种使用方式：
- 通过 `UCharacterTrajectoryComponent` 组件（开箱即用）
- 通过 `FMotionTrajectoryLibrary` 静态函数（在 AnimInstance 中手动调用，避免使用组件）

## 使用场景

- 你正在使用 Motion Matching / PoseSearch 系统 → 需要这个插件提供轨迹数据
- 你的角色使用标准 `UCharacterMovementComponent` → 直接使用 `UCharacterTrajectoryComponent`
- 你的角色使用自定义移动组件 → 使用 `FMotionTrajectoryLibrary` 并自行采集运动数据
- 你需要在动画蓝图中直接计算轨迹，不希望通过组件 → 使用 `FMotionTrajectoryLibrary` 的静态函数

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Trajectory` (属性) | 只读属性，获取当前轨迹数据 `FTransformTrajectory` | `UCharacterTrajectoryComponent` |
| `SamplingData` (属性) | 采样配置（历史长度、采样率等） | `UCharacterTrajectoryComponent` |
| `CharacterTrajectoryData` (属性) | 角色运动数据（速度、加速度等） | `UCharacterTrajectoryComponent` |
| `DebugDrawTrajectory` | 绘制轨迹调试线 | `UTransformTrajectoryBlueprintLibrary` |

### 使用示例（蓝图描述）

**添加组件：**
1. 打开你的角色蓝图
2. 添加 `UCharacterTrajectoryComponent` 组件
3. 该组件会自动绑定到 `ACharacter` 的 `OnCharacterMovementUpdated` 事件

**调试显示：**
在控制台输入 `a.CharacterTrajectory.Debug 1` 可开启轨迹调试绘制（仅 Debug 构建生效）。

## C++ 用法

### 头文件引入

```cpp
#include "CharacterTrajectoryComponent.h"
#include "MotionTrajectoryLibrary.h"
```

### 基本用法（组件方式）

最简单的方式是给角色添加 `UCharacterTrajectoryComponent`：

```cpp
// 在角色构造函数中
UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Trajectory")
TObjectPtr<UCharacterTrajectoryComponent> TrajectoryComponent;

// 构造函数
AMyCharacter::AMyCharacter()
{
    TrajectoryComponent = CreateDefaultSubobject<UCharacterTrajectoryComponent>(TEXT("TrajectoryComponent"));
}
```

组件会自动：
- 在 `BeginPlay` 时初始化轨迹采样数据
- 在每次移动更新时记录历史并计算预测

### 进阶用法（静态函数方式）

如果需要在 `UAnimInstance` 中直接使用，避免组件开销：

```cpp
// 在 AnimInstance 中
void UMyAnimInstance::NativeUpdateAnimation(float DeltaSeconds)
{
    Super::NativeUpdateAnimation(DeltaSeconds);

    ACharacter* Character = Cast<ACharacter>(TryGetPawnOwner());
    if (!Character) return;

    // 更新角色运动数据
    CharacterTrajectoryData.UpdateDataFromCharacter(DeltaSeconds, Character);

    // 更新历史记录
    FMotionTrajectoryLibrary::UpdateHistory_TransformHistory(
        Trajectory, TranslationHistory, CharacterTrajectoryData, SamplingData, DeltaSeconds);

    // 更新预测
    FMotionTrajectoryLibrary::UpdatePrediction_SimulateCharacterMovement(
        Trajectory, CharacterTrajectoryData, SamplingData);
}
```

## Demo 示例

一个完整的最小示例，展示如何在自定义角色中使用轨迹组件：

**MyCharacter.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "MyCharacter.generated.h"

class UCharacterTrajectoryComponent;

UCLASS()
class AMyCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    AMyCharacter();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Trajectory")
    TObjectPtr<UCharacterTrajectoryComponent> TrajectoryComponent;
};
```

**MyCharacter.cpp**
```cpp
#include "MyCharacter.h"
#include "CharacterTrajectoryComponent.h"

AMyCharacter::AMyCharacter()
{
    TrajectoryComponent = CreateDefaultSubobject<UCharacterTrajectoryComponent>(TEXT("TrajectoryComponent"));
}
```

**Build.cs 依赖：**
```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "MotionTrajectory",
    "PoseSearch"  // Motion Matching 系统
});
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心（包含 TrajectoryTypes 等） |
| `AnimGraphRuntime` | 动画图运行时 |
| `PoseSearch` | Motion Matching 系统（插件依赖） |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-06-26 | `ec90099` | 为源文件添加 `UE_INLINE_GENERATED_CPP_BY_NAME`（代码规范化） |
| 2025-04-23 | `939cc6e` | 将所有文件转换为使用 `dllstorage`（构建系统适配） |
| 2025-02-14 | `f9bb934` | **重要更新**：弃用 PoseSearch 专有的 `FPoseSearchQueryTrajectory`，改用引擎级 `FTransformTrajectory` |

### 维护评价

- **创建时间**：2021-09-16，约 4.5 年历史
- **最近更新**：2025-06-26，仍在活跃维护
- **维护状态**：✅ 活跃维护
- **实验性状态**：⚠️ 标记为 Experimental，`EnabledByDefault = false`
- **推荐程度**：如果你在使用 Motion Matching / PoseSearch，这是必需的依赖。虽然是实验性插件，但作为 Motion Matching 系统的核心组件，会持续维护。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Animation/MotionTrajectory)
- [PoseSearch 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Animation/PoseSearch) - Motion Matching 核心系统
- [TrajectoryTypes.h](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Source/Runtime/Engine/Public/Animation/TrajectoryTypes.h) - 引擎级轨迹类型定义
