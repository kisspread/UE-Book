# Animation Locomotion Library

> Collection of techniques for driving locomotion animations

| 属性 | 值 |
|---|---|
| 中文名 | 动画运动学库 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画资产） |
| 模块 | `AnimationLocomotionLibraryRuntime` (Runtime), `AnimationLocomotionLibraryEditor` (UncookedOnly) |
| 实验性 | ⚦ 是 |
| 创建时间 | 2021-09-17 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/AnimationLocomotionLibrary) | |

## 用途

Animation Locomotion Library (ALL) 是一个用于驱动基于运动学的动画的技术集合。它解决了传统基于时间线的动画混合方式在处理复杂、动态的角色运动（如急停、转向、精确的脚步放置）时，容易出现脚部滑动、动画不自然的问题。

其核心思想是：**使用运动学数据（如速度、移动距离、到目标的距离）而非时间来驱动和同步动画**。它提供了一套模板化的动画蓝图节点和底层函数，使开发者能够构建出物理驱动、高度精确的角色运动表现。此外，它还包含将胶囊体旋转与角色姿态分离的原地转向功能，避免了角色在旋转时整个姿态跟着转，从而实现更自然的“原地转动身体”效果。

## 使用场景

- 你在制作一个第三人称动作游戏（如动作RPG、格斗游戏），需要角色动画根据移动速度、加速度进行平滑且物理准确的混合。
- 你需要实现角色快速冲刺后精确滑行到某个位置停下，并且动画的脚步落地位置需要与最终停止位置完美匹配（距离匹配）。
- 你的角色需要在小范围内（如原地）进行大幅度的身体转向观察，而不影响其运动胶囊体的朝向。
- 你需要分析并修正基于根运动的动画距离，确保动画播放的位移与逻辑移动距离一致。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Locomotion Snapshot` | 获取一个包含当前角色运动信息（速度、加速度等）的快照，用于驱动动画。 | `ULocomotionComponent` |
| `Get Character Movement Component Stop Location` | 获取角色执行急停后，基于当前速度预测将要停止的位置。 | `UCharacterMovementComponentStopLocation` |
| `Apply Turn in Place Offset` | 应用原地转向的旋转偏移，使角色的视觉姿态与胶囊体旋转分离。 | `UAnimationFunctionLibrary` |
| `Turn In Place` | 处理原地转向逻辑，返回用于动画蓝图的旋转目标值。 | `UTurnInPlaceAnimInstance` |
| `Distance Matching to Target` | 节点，用于根据到目标的距离来驱动动画播放。 | `UAnimDistanceMatchingLibrary` |

### 使用示例（蓝图描述）

1.  **获取运动快照**：在角色的事件图表中，每帧调用 `Get Locomotion Snapshot`，将返回的快照结构体输出到动画蓝图的变量中。
2.  **使用距离匹配节点**：在动画蓝图中，将一个普通的播放动画节点替换为 `Template Anim Node Advance by Distance` 或 `Template Anim Node Advance by Distance to Target` 节点。将快照中的速度或距离信息作为这些节点的驱动输入。
3.  **原地转向**：在动画蓝图的 `Turn In Place` 状态机或逻辑中，调用 `Apply Turn in Place Offset` 并传入从 `Turn In Place` 逻辑计算出的旋转偏移，将其应用到角色的网格体组件上。

## C++ 用法

### 头文件引入

```cpp
#include "LocomotionComponent.h"
#include "AnimationFunctionLibrary.h"
```

### 基本用法

从运行时模块的核心功能提取，用于在角色移动组件中获取运动快照并传递给动画系统。

```cpp
// 在你的自定义角色类中
#pragma once
#include "GameFramework/Character.h"
#include "LocomotionComponent.h"
#include "YourCharacter.generated.h"

UCLASS()
class AYourCharacter : public ACharacter
{
    GENERATED_BODY()
public:
    AYourCharacter();
    
    // 声明一个Locomotion组件指针
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Animation")
    ULocomotionComponent* LocomotionComponent;

    // 重写Tick，更新运动快照
    virtual void Tick(float DeltaTime) override;
};
```

```cpp
// .cpp 文件
#include "YourCharacter.h"

AYourCharacter::AYourCharacter()
{
    LocomotionComponent = CreateDefaultSubobject<ULocomotionComponent>(TEXT("LocomotionComponent"));
}

void AYourCharacter::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    // 组件会自动在内部更新其快照数据
    // 你可以在动画蓝图中通过接口获取这个快照
}
```

### 进阶用法

结合距离匹配，在自定义动画实例中驱动动画。

```cpp
// 在你的自定义动画实例中
#include "AnimationLocomotionLibraryRuntime.h"
#include "AnimDistanceMatchingLibrary.h"

void UYourAnimInstance::NativeUpdateAnimation(float DeltaSeconds)
{
    Super::NativeUpdateAnimation(DeltaSeconds);

    // 获取角色的Locomotion快照
    AActor* OwnerActor = GetOwningActor();
    if (ULocomotionComponent* LocoComp = OwnerActor->FindComponentByClass<ULocomotionComponent>())
    {
        FLocomotionSnapshot Snapshot = LocoComp->GetLocomotionSnapshot();
        // 使用快照数据，例如设置动画蓝图的速度变量
        Speed = Snapshot.GroundSpeed;
        
        // 驱动距离匹配节点
        // 这通常在动画蓝图中连接，但也可通过代码设置状态
    }
}
```

## Demo 示例

一个最小的示例，展示如何为角色添加运动快照功能。

```cpp
// SnapshotCharacter.h
#pragma once
#include "GameFramework/Character.h"
#include "LocomotionComponent.h"
#include "SnapshotCharacter.generated.h"

UCLASS()
class ASnapshotCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    ASnapshotCharacter();

    // 这个函数返回的数据可以在动画蓝图中作为输入
    UFUNCTION(BlueprintCallable, Category = "Animation")
    FAnimLocomotionSnapshot GetLocomotionSnapshot() const;

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Animation", meta = (AllowPrivateAccess = "true"))
    ULocomotionComponent* LocomotionComp;
};
```

```cpp
// SnapshotCharacter.cpp
#include "SnapshotCharacter.h"

ASnapshotCharacter::ASnapshotCharacter()
{
    LocomotionComp = CreateDefaultSubobject<ULocomotionComponent>(TEXT("LocomotionComp"));
}

void ASnapshotCharacter::BeginPlay()
{
    Super::BeginPlay();
}

FAnimLocomotionSnapshot ASnapshotCharacter::GetLocomotionSnapshot() const
{
    if (LocomotionComp)
    {
        return LocomotionComp->GetLocomotionSnapshot();
    }
    return FAnimLocomotionSnapshot();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AnimationLocomotionLibraryRuntime` | 提供核心的运行时功能，如运动快照、原地转向逻辑和距离匹配节点。 |
| `AnimationLocomotionLibraryEditor` | 提供编辑器内工具，如用于生成距离曲线的动画修改器。 |

**使用者需要依赖的模块**：`AnimationLocomotionLibraryRuntime`

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从UE_LOG迁移至UE_LOGF，是引擎范围的统一代码清理。 |
| 2025-07-10 | `9803c443` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applie... | 为源文件添加了内联生成宏，用于编译优化。 |
| 2025-06-26 | `ec900998` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applie... | 同上，为更多源文件应用了相同的编译优化宏。 |
| 2025-04-23 | `93a13080` | Used LyraGame build target to find and convert all files to have dllstorage on methods/staticvar ins... | 为方法/静态变量添加了DLL导出属性，以解决构建问题。 |
| 2025-03-13 | `b059f7b4` | Fix trivial unreachable code warnings. | 修复了简单的无法到达代码警告。 |

### 维护评价

- **创建于 2021 年 9 月**，已有约 4 年历史。
- **最近一次更新在 2026 年 4 月**，主要是代码维护和编译优化，表明该插件仍在被 Epic Games 纳入引擎主干并同步维护。
- **状态**：该插件在 .uplugin 中标记为 **Beta 版 (`IsBetaVersion: true`)** 且 **默认未启用 (`EnabledByDefault: false`)**，说明它仍处于实验性阶段，API 和功能可能在未来版本中发生变化。
- **推荐度**：如果你正在开发需要高品质运动动画的项目，特别是参考了 Epic 官方项目 Lyra 的动画方案，那么使用这个库是很好的起点。但需注意其 Beta 状态，在正式项目中应做好应对可能的 API 变更的准备，并密切关注引擎更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/AnimationLocomotionLibrary)
- 官方文档: （无）