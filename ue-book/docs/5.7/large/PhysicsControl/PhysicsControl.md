# PhysicsControl

> Physically control static and skeletal meshes through the Physics Control Component and the Rigid Body With Control animation graph node.

| 属性 | 值 |
|---|---|
| 中文名 | 物理控制插件 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图内容、配置数据） |
| 模块 | `PhysicsControl` (Runtime), `PhysicsControlUncookedOnly` (UncookedOnly), `PhysicsControlEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-23 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PhysicsControl) | |

> **注意**：该插件仍处于 Beta 阶段，API 可能在不兼容性警告下发生变化。

## 用途

PhysicsControl 插件提供了一套高级的物理控制框架，允许你通过 **弹簧/阻尼驱动器** 主动控制静态网格（Static Mesh）或骨骼网格（Skeletal Mesh）中物理体的运动。它包含两个核心机制：

1. **Physics Control Component** (`UPhysicsControlComponent`)：一个场景组件，可以在其所在的 Actor 上管理多个 `Control` 和 `Body Modifier`。Control 用于将一个物理体相对于另一个物理体（或世界空间）进行驱动；Body Modifier 则用于修改物理体的属性（如模拟/运动学/静态模式、重力影响等）。所有 Control 和 Modifier 都被命名，并可以组织成集合（Sets），便于批量更新。

2. **Rigid Body With Control 动画节点** (`FAnimNode_RigidBodyWithControl`)：一个动画蓝图节点，基于原有的 RigidBody 节点扩展，在模拟物理的同时允许你对每个骨骼应用独立的物理控制（类似肢体级联控制）。它支持通过 Profile 预设快速切换整套控制参数。

此插件的设计目标是解决传统物理动画中“全或无”的问题：以往要么完全由动画驱动，要么完全由物理模拟驱动，很难在两者之间平滑混合。PhysicsControl 允许你精准地指定哪些骨骼受控于动画、哪些受控于物理，以及物理驱动的强度和阻尼，从而实现类似“部分 ragdoll”、“物理辅助动画”等效果。

## 使用场景

- **角色受伤后的局部 ragdoll**：通过 Body Modifier 将受伤部位的骨骼设为 Simulated，其他部分保持动画驱动，再使用 Control 让受伤肢体跟随目标姿势（可来自动画或自定义曲线）。
- **机械臂/动态机械**：使用 Control 让机械臂的关节以物理方式驱动到指定角度，并支持碰撞响应。
- **载具悬挂系统**：使用 Body Modifier 调节车轮的模拟/运动学模式，配合 Control 实现悬挂弹簧效果。
- **角色与环境交互**：例如角色用手推动物体，可通过 Control 将手的运动作为驱动源。
- **动画与物理混合**：在动画蓝图中使用 `Rigid Body With Control` 节点，对特定骨骼使用物理控制，其他骨骼保持原有动画，实现如“随风摆动的头发”等效果。

## 蓝图用法

插件通过 `UPhysicsControlComponent` 提供大量蓝图可调用函数，同时 `UPhysicsControlBPLibrary` 提供了参数混合与转换的工具函数。

### 核心节点（UPhysicsControlComponent）

以下列出最主要的功能节点，按类别分组。

#### 创建与管理 Controls / Body Modifiers

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateControl` | 为网格组件创建一个新的 Control，返回其名称。参数包括控制数据（强度/阻尼）、目标、可选的集名称。 | `UPhysicsControlComponent` |
| `CreateControls` | 批量创建多个 Control（通常基于肢体骨骼）。 | `UPhysicsControlComponent` |
| `CreateBodyModifier` | 为某个物理体创建一个 Body Modifier。 | `UPhysicsControlComponent` |
| `CreateBodyModifiers` | 批量创建 Body Modifier（如为整个肢体所有物理体创建）。 | `UPhysicsControlComponent` |
| `DestroyControl` | 销毁指定名称的 Control。 | `UPhysicsControlComponent` |
| `DestroyBodyModifier` | 销毁指定名称的 Body Modifier。 | `UPhysicsControlComponent` |
| `GetControlNamesInSet` | 获取指定集合中所有 Control 的名称。 | `UPhysicsControlComponent` |
| `GetBodyModifierNamesInSet` | 获取指定集合中所有 Body Modifier 的名称。 | `UPhysicsControlComponent` |

#### 更新 Control 参数与目标

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetControlData` | 设置 Control 的强度/阻尼数据（支持单独设置每个轴）。 | `UPhysicsControlComponent` |
| `SetControlMultiplier` | 设置 Control 数据的乘数，允许按轴缩放强度/阻尼。 | `UPhysicsControlComponent` |
| `SetControlTarget` | 设置 Control 的位置/旋转目标（相对于父体或世界空间）。 | `UPhysicsControlComponent` |
| `SetControlTargetPosition` | 仅设置位置目标。 | `UPhysicsControlComponent` |
| `SetControlTargetOrientation` | 仅设置旋转目标。 | `UPhysicsControlComponent` |
| `SetControlEnabled` | 启用/禁用 Control。 | `UPhysicsControlComponent` |
| `ResetControl` | 重置 Control 到初始状态。 | `UPhysicsControlComponent` |

#### 更新 Body Modifier 属性

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetBodyModifier` | 一次性设置 Body Modifier 的多个属性（运动类型、重力、碰撞等）。 | `UPhysicsControlComponent` |
| `SetBodyModifierMovementType` | 设置物理体的运动类型：静态、运动学、模拟。 | `UPhysicsControlComponent` |
| `SetBodyModifierGravity` | 设置是否受重力影响。 | `UPhysicsControlComponent` |
| `SetBodyModifierCollision` | 设置碰撞启用状态。 | `UPhysicsControlComponent` |
| `SetBodyModifierKinematicTarget` | 当运动类型为运动学时，设置目标变换。 | `UPhysicsControlComponent` |
| `ResetBodyModifier` | 重置 Body Modifier 到默认状态。 | `UPhysicsControlComponent` |

#### 手动同步时间（高级）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UpdateTargetCaches` | 手动更新目标缓存（从动画空间采样），需配合禁用自动 Tick 使用。 | `UPhysicsControlComponent` |
| `UpdateControls` | 手动执行所有 Control 和 Body Modifier 的更新。 | `UPhysicsControlComponent` |

### 蓝图工具函数（UPhysicsControlBPLibrary）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ConvertToRigidBodyWithControl` | 将一个通用的 `FAnimNodeReference` 转换为 `FRigidBodyWithControlReference`，以便访问节点内部参数。 | `UPhysicsControlBPLibrary` |
| `AddControlParameters` | 向参数容器中添加单个 Control 的稀疏数据。 | `UPhysicsControlBPLibrary` |
| `AddMultipleControlParameters` | 批量添加 Control 参数（共享相同数据）。 | `UPhysicsControlBPLibrary` |
| `BlendParameters` | 线性插值两个参数集合。 | `UPhysicsControlBPLibrary` |
| `BlendControlParametersThroughSet` | 对一组 Control 名称从起始参数到结束参数进行线性混合（常用于肢体中的力递进）。 | `UPhysicsControlBPLibrary` |
| `BlendModifierParametersThroughSet` | 类似上述，但用于 Modifier。 | `UPhysicsControlBPLibrary` |

### 使用示例（蓝图描述）

**创建一个简单的世界空间 Control：**

1. 在 Actor 上添加 `Physics Control Component`（蓝图默认自动 Tick）。
2. 在 Event BeginPlay 中调用 `Create Control`：
   - ParentActor：None（世界空间）
   - ParentMeshComponentName：留空
   - ChildActor：此 Actor
   - ChildMeshComponentName：网格组件名称（如"StaticMesh0"）
   - ChildBoneName：如果骨骼网格则填写骨骼名，否则留空
   - ControlData：设置 Strength = 20, DampingRatio = 0.5, ExtraDamping = 0
   - ControlTarget：设置 TargetPosition = (0,0,0), TargetOrientation = (0,0,0)
   - Set (可选)：留空或输入自定义集合名称
3. 返回的 ControlName 存储下来，后续可用于 `Set Control Target` 动态改变目标位置。

**局部 ragdoll（模拟部分骨骼）：**

1. 使用 `Create Body Modifier` 创建腰部以上所有骨的 Body Modifier，设置 MovementType = Simulated。
2. 使用 `Create Control` 为每个模拟骨骼创建一个 WorldSpace 控制（或 ParentSpace），强度较低（如 5），使身体既有物理反应又离动画姿势不远。
3. 当需要恢复时，调用 `Set Body Modifier Movement Type` 改回 Kinematic 或 Static，同时销毁或禁用 Control。

## C++ 用法

### 头文件引入

```cpp
#include "PhysicsControlComponent.h"
#include "PhysicsControlBPLibrary.h"
// 若使用动画节点
#include "AnimNode_RigidBodyWithControl.h"
```

### 基本用法

以下示例创建一个简单的 WorldSpace Control，驱动一个骨骼网格的 `pelvis` 骨骼。

```cpp
// 获取 PhysicsControlComponent（假设它是 Actor 的子组件）
UPhysicsControlComponent* ControlComp = GetComponentByClass<UPhysicsControlComponent>();

FPhysicsControlData InitData;
InitData.Strength = FVector(20.f, 20.f, 20.f);
InitData.DampingRatio = FVector(0.5f);
InitData.ExtraDamping = FVector(0.f);

FPhysicsControlTarget InitTarget;
InitTarget.TargetPosition = FVector(0.f, 0.f, 100.f);
InitTarget.TargetOrientation = FRotator::ZeroRotator;

// 创建 Control，控制 pelvis 骨骼在世界空间中移动
FName ControlName = ControlComp->CreateControl(
    nullptr,             // 无父 Actor，世界空间
    NAME_None,           // 父组件名
    NAME_None,           // 父骨骼名
    this,                // 子 Actor
    TEXT("SkeletalMesh0"),
    TEXT("pelvis"),
    InitData,
    FPhysicsControlMultiplier(),
    InitTarget,
    TEXT("MyControls")   // 放入名为 MyControls 的集合
);

// 之后可更新目标
FPhysicsControlTarget NewTarget;
NewTarget.TargetPosition = FVector(0.f, 0.f, 200.f);
ControlComp->SetControlTarget(ControlName, NewTarget);
```

### 进阶用法

**使用肢体创建批量 Control：**

`CreateControls` 可以基于预定义的肢体骨骼数据一次性创建所有 Control。首先定义 `FPhysicsControlLimbSetupData` 数组，然后调用 `CreateControls`。

```cpp
TArray<FPhysicsControlLimbSetupData> LimbSetupData;
FPhysicsControlLimbSetupData LeftArm;
LeftArm.LimbName = TEXT("LeftArm");
LeftArm.StartBone = TEXT("clavicle_l");
LeftArm.bCreateWorldSpaceControls = true;
LeftArm.bCreateParentSpaceControls = true;
LeftArm.bCreateBodyModifiers = true;
LimbSetupData.Add(LeftArm);

ControlComp->CreateControls(
    this,
    TEXT("SkeletalMesh0"),
    LimbSetupData,
    FPhysicsControlData(),
    FPhysicsControlMultiplier(),
    FPhysicsControlTarget(),
    TEXT("DefaultWorld"),
    TEXT("DefaultParent"),
    TEXT("DefaultModifier")
);
```

**使用 RigidBodyWithControl 节点（C++ 动画蓝图）：**

在自定义 AnimInstance 中，你可以通过 `FRigidBodyWithControlReference` 访问节点参数：

```cpp
#include "PhysicsControlBPLibrary.h"

void UMyAnimInstance::NativeInitializeAnimation()
{
    Super::NativeInitializeAnimation();
    // 获取节点引用，需在动画蓝图中已放置 FAnimNode_RigidBodyWithControl
    FRigidBodyWithControlReference RBWCRef;
    // 通过 AnimInstance 的节点查找（略）
    // 然后使用 UPhysicsControlBPLibrary::SetRigidBodyWithControlParameters 等函数修改参数
}
```

## Demo 示例

以下是一个完整的 Actor 类，演示如何使用 PhysicsControlComponent 创建一个受控的静态网格物体。

**MyPhysicsControlledActor.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "PhysicsControlComponent.h"
#include "PhysicsControlData.h"
#include "MyPhysicsControlledActor.generated.h"

UCLASS()
class AMyPhysicsControlledActor : public AActor
{
    GENERATED_BODY()

public:
    AMyPhysicsControlledActor();

protected:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    UStaticMeshComponent* Mesh;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    UPhysicsControlComponent* PhysicsControlComp;

    FName ControlName;

    float ElapsedTime;
};
```

**MyPhysicsControlledActor.cpp**

```cpp
#include "MyPhysicsControlledActor.h"
#include "PhysicsControlBPLibrary.h"

AMyPhysicsControlledActor::AMyPhysicsControlledActor()
{
    PrimaryActorTick.bCanEverTick = true;

    Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
    RootComponent = Mesh;

    PhysicsControlComp = CreateDefaultSubobject<UPhysicsControlComponent>(TEXT("PhysicsControlComp"));
}

void AMyPhysicsControlledActor::BeginPlay()
{
    Super::BeginPlay();

    // 配置初始控制数据
    FPhysicsControlData InitData;
    InitData.Strength = FVector(10.f);
    InitData.DampingRatio = FVector(0.5f);
    InitData.ExtraDamping = FVector(0.f);

    FPhysicsControlTarget InitTarget;
    InitTarget.TargetPosition = GetActorLocation() + FVector(0, 0, 200);
    InitTarget.TargetOrientation = FRotator::ZeroRotator;

    // 创建世界空间控制，驱动整个 Mesh（无骨骼）
    ControlName = PhysicsControlComp->CreateControl(
        nullptr,
        NAME_None,
        NAME_None,
        this,
        TEXT("Mesh"),
        NAME_None,       // 非骨骼网格，无骨骼名
        InitData,
        FPhysicsControlMultiplier(),
        InitTarget,
        TEXT("MyDemoControl")
    );

    // 设置 Body Modifier 使物体可被物理驱动
    PhysicsControlComp->CreateBodyModifier(
        this,
        TEXT("Mesh"),
        NAME_None,
        FPhysicsControlModifierData(),
        TEXT("MyDemoModifier")
    );
    // 设置为模拟+受重力
    PhysicsControlComp->SetBodyModifierMovementType(TEXT("MyDemoModifier"), EPhysicsMovementType::Simulated);
    PhysicsControlComp->SetBodyModifierGravity(TEXT("MyDemoModifier"), true);
}

void AMyPhysicsControlledActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (!ControlName.IsNone())
    {
        ElapsedTime += DeltaTime;
        // 让目标位置做圆周运动
        FVector NewTargetPos = FVector(
            FMath::Sin(ElapsedTime) * 100.f,
            FMath::Cos(ElapsedTime) * 100.f,
            200.f
        );
        PhysicsControlComp->SetControlTargetPosition(ControlName, NewTargetPos);
    }
}
```

> **注意**：本例中我们同时创建了 Body Modifier 并设置为 Simulated，使得物体受物理模拟，同时控制会通过弹簧驱动器将其拉向目标位置，产生有趣的跟随运动。

## 模块依赖

此插件的运行时模块 `PhysicsControl` 依赖以下独特模块（标准 Core/Engine 等已省略）：

| 模块 | 用途 |
|---|---|
| `Chaos` | 底层物理求解器（用于弹簧/阻尼驱动器） |
| `AnimGraphRuntime` | 提供 `FAnimNode_SkeletalControlBase` 等基础动画节点框架 |
| `PhysicsCore` | 提供基础物理体、约束等类型 |

编辑器模块 `PhysicsControlEditor` 额外依赖 `UnrealEd`、`PropertyEditor` 等，用于自定义资产编辑器。

## 维护状态

### 近期更新

从 Git 日志获取的最近更新：

- 2025-11-18 `bfe41435` — Sets the PhysicsControl plugin to Beta
- 2025-09-26 `e040cfab` — Disable diagnostic logging in RigidBodyWithControl in test/shipping and demote level to verbose.
- 2025-09-23 `7b7ebe09` — Support using a mask when invoking control profiles
- 2025-09-23 `4e0fa71d` — Support control/modifier and set names in all the functions. Also tidies up the docs etc. No behavior change.
- 2025-09-23 `4bdb12a5` — Align RigidBodyWithControl KinematicTargetSpace with the other parts of PhysicsControl

### 维护评价

- **创建时间**：2025-09-23，距今不到 3 个月，属于新插件。
- **近期更新**：最近一次实质性更新（功能更新）在 2025-09-23，之后仅有一次设置 Beta 标签和一次日志调整。虽然 Beta 标签是在 11 月份设置的，但核心代码没有变化，可能意味着已稳定。
- **活跃度**：目前没有后续更新，但仍处于早期阶段。考虑到 Epic 通常在正式版之前不会有频繁提交，该插件的维护节奏与预期相符。
- **已知问题**：Beta 阶段可能存在未发现的缺陷或 API 变更。
- **推荐使用**：如果项目需要精细的物理控制，且可以接受一定的不稳定性，推荐使用。建议密切关注 Epic 的更新。在生产项目中，请做好充分的测试和版本锁定。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PhysicsControl)
- [官方文档](https://docs.unrealengine.com/5.7/zh-CN/physics-control-plugin) （等待 Epic 更新文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PhysicsControl/Tests) （如果存在）