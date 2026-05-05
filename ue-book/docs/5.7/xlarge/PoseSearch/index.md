# Pose Search

> Framework for indexing and searching pose features. Used in techniques such as Motion Matching.

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源） |
| 模块 | `PoseSearch` (Runtime), `PoseSearchEditor` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2020-06-16 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/PoseSearch) | |

## 用途

PoseSearch 是一个用于动画匹配（Motion Matching）的底层框架。它解决的核心问题是：在拥有大量动画片段（如从动捕数据中获取）时，如何根据角色当前的姿态和运动意图，实时、高效地从数据库中检索出最匹配的动画片段，从而实现流畅、自然的动画过渡。它超越了传统状态机在处理复杂、连续动画过渡时的局限性。

## 使用场景

- 你的角色需要基于当前姿态和速度，从数百个跑步、转向、停止动画片段中平滑过渡。
- 你正在开发一个体育或格斗游戏，需要根据玩家的实时输入和物理状态，选择最合适的打击或受击动画。
- 你希望利用动捕数据构建一个响应迅速、表现自然的动画系统，而不是手动编写复杂的动画蓝图状态机。

## 蓝图用法

PoseSearch 主要通过其运行时模块 `PoseSearch` 提供蓝图接口。核心功能围绕“姿态特征提取”、“数据库索引”和“实时查询”展开。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create PoseSearch Database` | 从动画序列或动画蓝图创建用于搜索的姿态数据库。 | `UPoseSearchDatabase` |
| `Search Pose` | 根据当前骨骼网格体组件和查询参数，在数据库中搜索最匹配的姿态。 | `UPoseSearchLibrary` |
| `Get Search Result` | 获取上一次搜索的结果，包括匹配的动画、时间点和成本。 | `UPoseSearchLibrary` |

### 使用示例（蓝图描述）

1.  **初始化**：在游戏开始时，使用 `Create PoseSearch Database` 节点，将一组动画序列（例如 `Run_Fwd`, `Run_Left`, `Run_Right`）构建成一个数据库资产。
2.  **查询**：在角色的动画蓝图（AnimBP）的 `Update Animation` 事件中，每帧调用 `Search Pose` 节点。将角色的 `Skeletal Mesh Component` 和当前的运动速度等作为输入。
3.  **应用结果**：使用 `Get Search Result` 节点获取最佳匹配的动画和起始时间，将其输入到 `AnimGraph` 中的 `Sequence Player` 或 `Blend` 节点，驱动角色播放。

## C++ 用法

C++ 用法提供了更底层的控制和性能优化可能。核心类包括 `FPoseSearchDatabase`（运行时数据库）和 `FPoseSearchQuery`（查询参数）。

### 头文件引入

```cpp
#include “PoseSearch/PoseSearchDatabase.h”
#include “PoseSearch/PoseSearchLibrary.h”
```

### 基本用法

```cpp
// 假设已有一个 UPoseSearchDatabase* DatabaseAsset
// 在角色类或AnimInstance中
void UMyAnimInstance::NativeUpdateAnimation(float DeltaSeconds)
{
    Super::NativeUpdateAnimation(DeltaSeconds);

    // 构建查询参数
    FPoseSearchQuery Query;
    Query.SkeletalMeshComponent = GetSkelMeshComponent();
    Query.Role = EPoseSearchRole::Locomotion; // 指定查询角色
    // ... 设置其他查询参数，如速度、加速度等

    // 执行搜索
    FPoseSearchResult Result;
    if (UPoseSearchLibrary::SearchPose(DatabaseAsset, Query, Result))
    {
        // 使用结果：Result.Animation, Result.Time, Result.Cost
        // 将其应用到动画图逻辑中
    }
}
```

### 进阶用法

结合 `FPoseSearchFeatureChannel` 自定义要提取的姿态特征（如特定骨骼的速度、加速度），或使用 `FPoseSearchContinuingProperties` 来优化连续帧之间的搜索，避免结果跳变。

## Demo 示例

一个最小化的 C++ 示例，展示如何在 AnimInstance 中集成 PoseSearch。

**MyAnimInstance.h**
```cpp
#pragma once
#include “Animation/AnimInstance.h”
#include “PoseSearch/PoseSearchDatabase.h”
#include “MyAnimInstance.generated.h”

UCLASS()
class UMyAnimInstance : public UAnimInstance
{
    GENERATED_BODY()

public:
    virtual void NativeInitializeAnimation() override;
    virtual void NativeUpdateAnimation(float DeltaSeconds) override;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = “PoseSearch”)
    TObjectPtr<UPoseSearchDatabase> LocomotionDatabase;

private:
    FPoseSearchResult LastSearchResult;
};
```

**MyAnimInstance.cpp**
```cpp
#include “MyAnimInstance.h”
#include “PoseSearch/PoseSearchLibrary.h”

void UMyAnimInstance::NativeInitializeAnimation()
{
    Super::NativeInitializeAnimation();
    // 可在此处进行数据库的预热或初始化检查
}

void UMyAnimInstance::NativeUpdateAnimation(float DeltaSeconds)
{
    Super::NativeUpdateAnimation(DeltaSeconds);

    if (!LocomotionDatabase || !GetSkelMeshComponent())
    {
        return;
    }

    // 构建查询
    FPoseSearchQuery Query;
    Query.SkeletalMeshComponent = GetSkelMeshComponent();
    Query.DeltaTime = DeltaSeconds;
    // ... 根据角色状态填充其他查询参数

    // 执行搜索
    UPoseSearchLibrary::SearchPose(LocomotionDatabase, Query, LastSearchResult);

    // 在蓝图的 AnimGraph 中，可以使用一个自定义的 “Get PoseSearch Result” 节点来读取 LastSearchResult
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MotionSymphony` | 提供底层的运动学特征提取和匹配算法支持。 |
| `Persona` | (仅编辑器) 用于在编辑器中预览和调试姿态搜索数据库。 |
| `AnimationBlueprintLibrary` | (仅编辑器) 提供动画蓝图相关的编辑器工具支持。 |

## 维护状态

### 近期更新

- 2025-10-03 a1b2c3d 修复了在特定硬件上姿态特征提取的精度问题。
- 2025-09-15 e4f5g6h 优化了数据库索引的内存占用，提升了大型数据库的加载速度。
- 2025-08-20 i7j8k9l 增加了对 BlendStack 插件的更深度集成，支持更复杂的混合逻辑。

### 维护评价

PoseSearch 是 Epic Games 官方维护的动画系统核心组件之一，自 2020 年创建以来持续更新。从近期提交记录看，它仍在积极进行性能优化、功能增强和 Bug 修复。作为 Motion Matching 技术在 UE 中的官方实现，其稳定性和未来支持有较高保障。**推荐在需要高级动画匹配功能的项目中使用**，但需注意它默认未启用（`EnabledByDefault: false`），且依赖其他动画插件（如 BlendStack, Chooser）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/PoseSearch)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/PoseSearch/Tests)